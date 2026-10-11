import json
from datetime import date, datetime, time, timedelta
from pathlib import Path

from sqlalchemy import select, func
from sqlalchemy.orm import Session

import secrets

from .models import User, Movie, Showtime, Comment, Booking, BookingSeat
from .seats import ROWS, COLS, seat_price
from .security import hash_password
from .classifier import classifier

DATA = Path(__file__).parent / "data" / "movies.json"
TIMES = ["09:30", "13:15", "16:00", "19:30", "22:00"]


def _ensure_showtimes(db: Session, days: int = 5) -> None:
    """Đảm bảo luôn có suất chiếu cho `days` ngày tới (chạy mỗi lần khởi động)."""
    from .showtime_rules import ROOMS, find_showtime_conflict

    movies = db.scalars(select(Movie).where(Movie.status == "now_showing").order_by(Movie.id)).all()

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

    for d in range(days):
        day = date.today() + timedelta(days=d)
        day_start = datetime.combine(day, time.min)
        day_end = day_start + timedelta(days=1)

        # Ưu tiên công bằng: mỗi phim đang chiếu có ít nhất một suất trong ngày.
        existing_movie_ids = set(db.scalars(
            select(Showtime.movie_id).where(
                Showtime.start_time >= day_start,
                Showtime.start_time < day_end,
            )
        ).all())
        for idx, movie in enumerate(movies):
            if movie.id in existing_movie_ids:
                continue
            preferred = (idx + d) % len(TIMES)
            candidates = [(preferred + step) % len(TIMES) for step in range(len(TIMES))]
            if add_first_available(movie, idx, day, d, candidates):
                existing_movie_ids.add(movie.id)

        # Sau suất tối thiểu, lấp thêm lịch mẫu cũ; khi phòng ưu tiên bận thì thử phòng khác.
        for idx, movie in enumerate(movies):
            for i, _ in enumerate(TIMES):
                if (i + idx + d) % 2 == 0 or i == 3:
                    add_first_available(movie, idx, day, d, [i])
    db.commit()


def seed(db: Session) -> None:
    """Tạo dữ liệu mẫu đúng một lần khi database chưa có phim."""
    if not db.scalar(select(func.count()).select_from(Movie)):
        for m in json.loads(DATA.read_text(encoding="utf-8")):
            db.add(Movie(**m))
        admin = User(full_name="Quản trị viên", email="admin@firefly.vn", password_hash=hash_password("admin123"), role="admin")
        demo = User(full_name="Nguyễn Văn Demo", email="demo@firefly.vn", password_hash=hash_password("123456"))
        db.add_all([admin, demo])
        db.flush()
        samples = [
            (1, "Xem xong muốn gọi điện về cho mẹ liền. Cảnh cuối trên toa tàu quá đẹp."),
            (1, "Phim dài lê thê, nửa đầu buồn ngủ thật sự, phí tiền vé."),
            (4, "Con mình 6 tuổi xem cười suốt, đoạn ở chợ Bến Thành dễ thương lắm."),
            (2, "Kịch bản nhảm, hù dọa toàn tiếng động lớn, thất vọng."),
            (3, "Cảnh lũ quay rất thật, âm thanh rạp này nghe đã."),
            (9, "Nhạc phim hay muốn khóc, xem xong về nghe lại cả tối."),
            (9, "Hình ảnh đẹp, đoạn diễn cuối nổi da gà."),
            (10, "Kỹ xạo ổn nhưng kịch bản hơi kém, đoạn giữa xàm quá."),
            (8, "Không khí ngột ngạt đúng chất, coi xong không dám đi tàu đêm."),
            (12, "Phục trang đẹp, chuyện tình cảm động."),
            (5, "Hài nhạt, cười được đúng hai lần, khá thất vọng."),
            (18, "Mấy bé đá bóng dễ thương, cả rạp vỗ tay đoạn cuối."),
        ]
        for i, (movie_id, text) in enumerate(samples):
            neg, score = classifier.predict(text)
            db.add(Comment(movie_id=movie_id, user_id=demo.id, content=text, is_negative=neg,
                           negative_score=score, model_name=classifier.name,
                           created_at=datetime.now() - timedelta(hours=5 * (i + 1))))
        db.commit()
        _ensure_showtimes(db)
        _seed_bookings(db)


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
            b = Booking(user_id=guest.id, showtime_id=st.id, created_at=now - timedelta(days=days_ago),
                        total=sum(seat_price(s, st.price) for s in seats))
            b.seats = [BookingSeat(showtime_id=st.id, seat_code=s) for s in seats]
            db.add(b)
    db.commit()
