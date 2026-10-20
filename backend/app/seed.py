import json
import logging
import os
import tempfile
from datetime import date, datetime, time, timedelta
from pathlib import Path

from sqlalchemy import select, func
from sqlalchemy.orm import Session

import secrets

from .models import User, Movie, Showtime, Comment, Booking, BookingSeat, Rating
from .seats import ROWS, COLS, seat_price
from .security import hash_password
from .classifier import classifier
from .config import ADMIN_PASSWORD
from .booking_rules import HOLD_MINUTES

logger = logging.getLogger(__name__)

DATA = Path(__file__).parent / "data" / "movies.json"
DEMO_COMMENTS = Path(__file__).parent / "data" / "demo_comments.json"
TIMES = ["09:30", "13:15", "16:00", "19:30", "22:00"]
_SEED_STATE_VERSION = 1
_SEED_STATE_SUFFIX = ".showtime-seed.json"


def _empty_seed_state() -> dict:
    return {"version": _SEED_STATE_VERSION, "days": {}}


def _seed_state_path(db: Session) -> Path | None:
    """Trả sidecar gắn với đúng file SQLite đang được session sử dụng."""
    bind = db.get_bind()
    if bind.dialect.name != "sqlite":
        raise RuntimeError("Showtime seed state chỉ hỗ trợ SQLite.")
    database = bind.url.database
    if not database or database == ":memory:":
        return None
    database_path = Path(database).resolve()
    return database_path.with_name(database_path.name + _SEED_STATE_SUFFIX)


def _read_seed_state(
    db: Session, days: list[date], movie_ids: set[int]
) -> tuple[dict, Path | None]:
    path = _seed_state_path(db)
    if path is None:
        state = db.info.setdefault(
            "showtime_seed_state", _empty_seed_state()
        )
        return state, None
    if path.exists():
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
            if state.get("version") != _SEED_STATE_VERSION or not isinstance(
                state.get("days"), dict
            ):
                raise ValueError("invalid state shape")
            for value in state["days"].values():
                if not isinstance(value, list) or any(
                    not isinstance(movie_id, int) for movie_id in value
                ):
                    raise ValueError("invalid movie ids")
            return state, path
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            raise RuntimeError(
                f"Không thể đọc showtime seed state cho database {path.name}."
            ) from exc

    # Database hiện hữu chưa có sidecar: coi các ngày từ đầu cửa sổ đến
    # ngày lịch hiện hữu xa nhất trong cửa sổ là đã được seed. Quy tắc bảo thủ
    # này giữ các thao tác xóa cũ; ngày rolling mới phía sau vẫn được bổ sung.
    state = _empty_seed_state()
    window_start = datetime.combine(days[0], time.min)
    window_end = datetime.combine(days[-1] + timedelta(days=1), time.min)
    existing_starts = db.scalars(select(Showtime.start_time).where(
        Showtime.start_time >= window_start,
        Showtime.start_time < window_end,
    )).all()
    if existing_starts:
        seeded_through = max(value.date() for value in existing_starts)
        for day in days:
            if day <= seeded_through:
                state["days"][day.isoformat()] = sorted(movie_ids)
    return state, path


def _write_seed_state(path: Path | None, state: dict) -> None:
    if path is None:
        return
    temp_path = None
    try:
        fd, temp_name = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
        )
        temp_path = Path(temp_name)
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(state, handle, ensure_ascii=False, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


def _reset_seed_state_for_new_database(db: Session) -> None:
    """Bỏ state cũ chỉ khi database chưa có phim và đang được khởi tạo mới."""
    state = _empty_seed_state()
    path = _seed_state_path(db)
    if path is None:
        db.info["showtime_seed_state"] = state
        return
    _write_seed_state(path, state)


def _ensure_showtimes(db: Session, days: int = 5) -> None:
    """Đảm bảo luôn có suất chiếu cho `days` ngày tới (chạy mỗi lần khởi động)."""
    from .showtime_rules import ROOMS, find_showtime_conflict

    movies = db.scalars(select(Movie).where(Movie.status == "now_showing").order_by(Movie.id)).all()
    window_days = [date.today() + timedelta(days=offset) for offset in range(days)]
    movie_ids = {movie.id for movie in movies}
    state, state_path = _read_seed_state(db, window_days, movie_ids)

    def add_first_available(movie: Movie, movie_idx: int, day: date, day_idx: int,
                            candidate_indexes: list[int]) -> bool:
        for time_idx in candidate_indexes:
            h, m = map(int, TIMES[time_idx].split(":"))
            start_time = datetime.combine(day, time(h, m))
            duplicate = db.scalar(
                select(Showtime.id).where(
                    Showtime.movie_id == movie.id,
                    Showtime.start_time == start_time,
                ).limit(1)
            )
            if duplicate is not None:
                continue
            room_start = (movie_idx + day_idx + time_idx) % len(ROOMS)
            for room_step in range(len(ROOMS)):
                room = ROOMS[(room_start + room_step) % len(ROOMS)]
                if find_showtime_conflict(
                    db, room=room, start_time=start_time, duration_min=movie.duration_min
                ):
                    continue
                db.add(Showtime(movie_id=movie.id, start_time=start_time, room=room,
                                price=95000 if h >= 17 else 75000))
                db.flush()
                return True
        return False

    for d, day in enumerate(window_days):
        day_start = datetime.combine(day, time.min)
        day_end = day_start + timedelta(days=1)
        handled_movie_ids = set(state["days"].get(day.isoformat(), []))
        existing_movie_ids = set(db.scalars(
            select(Showtime.movie_id).where(
                Showtime.start_time >= day_start,
                Showtime.start_time < day_end,
            )
        ).all())
        target_movies = [movie for movie in movies if movie.id not in handled_movie_ids]

        # Ưu tiên công bằng: mỗi phim mới đi vào ngày seed có ít nhất một suất.
        for idx, movie in enumerate(target_movies):
            if movie.id in existing_movie_ids:
                handled_movie_ids.add(movie.id)
                continue
            preferred = (idx + d) % len(TIMES)
            candidates = [(preferred + step) % len(TIMES) for step in range(len(TIMES))]
            if add_first_available(movie, idx, day, d, candidates):
                existing_movie_ids.add(movie.id)
                handled_movie_ids.add(movie.id)

        # Chỉ lấp lịch mẫu cho phim chưa từng được xử lý trong ngày. Các suất
        # seed đã bị admin xóa (kể cả xóa sạch ngày) sẽ không xuất hiện lại.
        for idx, movie in enumerate(target_movies):
            for i, _ in enumerate(TIMES):
                if (i + idx + d) % 2 == 0 or i == 3:
                    if add_first_available(movie, idx, day, d, [i]):
                        existing_movie_ids.add(movie.id)
            if movie.id in existing_movie_ids:
                handled_movie_ids.add(movie.id)
        state["days"][day.isoformat()] = sorted(handled_movie_ids)
    db.commit()
    _write_seed_state(state_path, state)


def seed(db: Session) -> None:
    """Tạo dữ liệu mẫu lần đầu và duy trì cửa sổ lịch chiếu 5 ngày."""
    is_new_database = not db.scalar(select(func.count()).select_from(Movie))
    if is_new_database:
        # Một database mới có thể dùng lại đúng đường dẫn của file vừa reset.
        # Làm rỗng sidecar trước mọi commit để lần khởi động kế tiếp vẫn có thể
        # hoàn tất seed an toàn nếu tiến trình bị ngắt giữa chừng.
        _reset_seed_state_for_new_database(db)
        for m in json.loads(DATA.read_text(encoding="utf-8")):
            db.add(Movie(**m))
        admin_password = ADMIN_PASSWORD or "admin123"
        if not ADMIN_PASSWORD:
            logger.warning("ADMIN_PASSWORD chưa được cấu hình; đang dùng mật khẩu admin mặc định cho máy dev.")
        admin = User(full_name="Quản trị viên", email="admin@firefly.vn", password_hash=hash_password(admin_password), role="admin")
        demo = User(full_name="Nguyễn Văn Demo", email="demo@firefly.vn", password_hash=hash_password("123456"))
        db.add_all([admin, demo])
        db.flush()
        for movie in db.scalars(select(Movie).where(Movie.status != "coming_soon")).all():
            for index, viewer in enumerate((admin, demo)):
                db.add(Rating(movie_id=movie.id, user_id=viewer.id,
                              stars=3 + ((movie.id + index) % 3)))
        samples = json.loads(DEMO_COMMENTS.read_text(encoding="utf-8"))
        now = datetime.now()
        for sample in samples:
            text = sample["content"]
            neg, score = classifier.predict(text)
            review = sample.get("review")
            human_label = None
            reviewed_by = None
            reviewed_at = None
            if review == "confirm":
                human_label = int(neg)
            elif review == "opposite":
                human_label = int(not neg)
            if human_label is not None:
                reviewed_by = admin.id
                reviewed_at = now - timedelta(
                    days=sample["days_ago"], hours=max(sample.get("hours_ago", 0) - 1, 0)
                )
            db.add(Comment(
                movie_id=sample["movie_id"], user_id=demo.id, content=text,
                is_negative=neg, negative_score=score, model_name=classifier.name,
                model_version=classifier.version, human_label=human_label,
                reviewed_by=reviewed_by, reviewed_at=reviewed_at,
                hidden=sample.get("hidden", False),
                created_at=now - timedelta(
                    days=sample["days_ago"], hours=sample.get("hours_ago", 0)
                ),
            ))
        db.commit()
        _ensure_showtimes(db)
        _seed_bookings(db)
    _ensure_showtimes(db)


# Số lượt đặt mẫu cho mỗi phim: (trong 7 ngày qua, từ 8 đến 30 ngày trước)
# để mục "Phim hot trong tuần / trong tháng" có dữ liệu khi demo
_SAMPLE_SALES = {9: (14, 16), 4: (12, 8), 10: (6, 16), 1: (5, 13), 3: (8, 7), 8: (9, 3), 2: (4, 5), 5: (2, 4), 18: (7, 1)}


def _seed_bookings(db: Session) -> None:
    guest = User(full_name="Khách mua tại quầy", email="quay@firefly.vn",
                 password_hash=hash_password(secrets.token_hex(16)))
    db.add(guest)
    db.flush()
    now = datetime.now()
    for movie_id, (week, older) in _SAMPLE_SALES.items():
        showtimes = db.scalars(select(Showtime).where(Showtime.movie_id == movie_id).order_by(Showtime.start_time)).all()
        if not showtimes:
            continue
        for i in range(week + older):
            st = showtimes[i % len(showtimes)]
            n = i // len(showtimes)  # mỗi lượt đặt 2 ghế liền nhau, lấp dần từ hàng giữa
            row = ROWS[(3 + n // (COLS // 2)) % len(ROWS)]
            col = (n % (COLS // 2)) * 2 + 1
            seats = [f"{row}{col}", f"{row}{col + 1}"]
            days_ago = (i % 6) + 1 if i < week else 8 + (i % 20)
            b = Booking(user_id=guest.id, showtime_id=st.id, status="paid", created_at=now - timedelta(days=days_ago),
                        total=sum(seat_price(s, st.price) for s in seats))
            b.seats = [BookingSeat(showtime_id=st.id, seat_code=s) for s in seats]
            db.add(b)
    demo = db.scalar(select(User).where(User.email == "demo@firefly.vn"))
    demo_showtimes = db.scalars(select(Showtime).order_by(Showtime.start_time, Showtime.id).limit(3)).all()
    if demo is not None and len(demo_showtimes) == 3:
        examples = [
            (demo_showtimes[0], "paid", ["A1", "A2"], now - timedelta(days=2)),
            (demo_showtimes[1], "pending_verify", ["A3", "A4"], now - timedelta(minutes=4)),
            # Vé hết hạn đã nhả ghế; không seed một vé held cũ rồi chờ request dọn.
            (demo_showtimes[2], "expired", [], now - timedelta(minutes=HOLD_MINUTES + 1)),
        ]
        for showtime, status, seats, created_at in examples:
            booking = Booking(
                user_id=demo.id, showtime_id=showtime.id, status=status,
                created_at=created_at,
                total=sum(seat_price(seat, showtime.price) for seat in seats),
            )
            booking.seats = [
                BookingSeat(showtime_id=showtime.id, seat_code=seat) for seat in seats
            ]
            db.add(booking)
    db.commit()
