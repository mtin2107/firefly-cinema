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
    movies = db.scalars(select(Movie).where(Movie.status == "now_showing").order_by(Movie.id)).all()
    for d in range(days):
        day = date.today() + timedelta(days=d)
        start = datetime.combine(day, time.min)
        exists = db.scalar(select(func.count()).select_from(Showtime)
                           .where(Showtime.start_time >= start, Showtime.start_time < start + timedelta(days=1)))
        if exists:
            continue
        for idx, movie in enumerate(movies):
            for i, t in enumerate(TIMES):
                if (i + idx + day.toordinal()) % 2 == 0 or i == 3:
                    h, m = map(int, t.split(":"))
                    db.add(Showtime(movie_id=movie.id, start_time=datetime.combine(day, time(h, m)),
                                    room=f"Phòng {idx % 4 + 1}", price=95000 if h >= 17 else 75000))
    db.commit()


def seed(db: Session) -> None:
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
            b = Booking(user_id=guest.id, showtime_id=st.id, created_at=now - timedelta(days=days_ago),
                        total=sum(seat_price(s, st.price) for s in seats))
            b.seats = [BookingSeat(showtime_id=st.id, seat_code=s) for s in seats]
            db.add(b)
    db.commit()
