from datetime import date, datetime, time, timedelta

from sqlalchemy import delete, func, select

from app.models import Booking, BookingSeat, Movie, Showtime
from app.seed import _ensure_showtimes, seed


def freeze_today(monkeypatch, value):
    class FrozenDate(date):
        @classmethod
        def today(cls):
            return value

    monkeypatch.setattr("app.seed.date", FrozenDate)


def test_deleted_seed_showtime_is_not_recreated_on_restart(db, movie, monkeypatch):
    today = date(2026, 10, 11)
    freeze_today(monkeypatch, today)
    _ensure_showtimes(db, days=5)
    deleted = db.scalars(select(Showtime).order_by(Showtime.id)).first()
    deleted_identity = (deleted.movie_id, deleted.start_time, deleted.room)
    db.execute(delete(Showtime).where(Showtime.id == deleted.id))
    db.commit()
    seed(db)
    assert db.scalar(select(Showtime.id).where(
        Showtime.movie_id == deleted_identity[0],
        Showtime.start_time == deleted_identity[1],
        Showtime.room == deleted_identity[2],
    )) is None


def test_seed_appends_new_day_when_calendar_moves(db, movie, monkeypatch):
    first_day = date(2026, 10, 11)
    second_movie = Movie(
        title="Phim rolling", genre="Tâm lý", duration_min=100,
        age_rating="T13", release_date="2026-10-01", status="now_showing",
        director="Đạo diễn", cast="Diễn viên", score=0, description="Mô tả",
        poster_bg="#223344", poster_fg="#ffffff", country="Việt Nam",
        formats="Phụ đề",
    )
    db.add(second_movie)
    db.commit()
    freeze_today(monkeypatch, first_day)
    _ensure_showtimes(db, days=5)

    freeze_today(monkeypatch, first_day + timedelta(days=1))
    seed(db)
    rows = db.execute(select(Showtime.start_time, Showtime.movie_id)).all()
    by_day = {}
    for start_time, movie_id in rows:
        by_day.setdefault(start_time.date(), set()).add(movie_id)
    expected_movies = {movie.id, second_movie.id}
    for offset in range(1, 6):
        assert expected_movies <= by_day[first_day + timedelta(days=offset)]


def test_seed_does_not_change_admin_showtime_or_bookings(db, movie, users, monkeypatch):
    first_day = date(2026, 10, 11)
    freeze_today(monkeypatch, first_day)
    _ensure_showtimes(db, days=5)
    user, _ = users
    admin_showtime = Showtime(
        movie_id=movie.id,
        start_time=datetime.combine(first_day + timedelta(days=3), time(6, 0)),
        room="Phòng 1",
        price=123_000,
    )
    db.add(admin_showtime)
    db.flush()
    booking = Booking(user_id=user.id, showtime_id=admin_showtime.id, total=123_000)
    booking.seats = [BookingSeat(showtime_id=admin_showtime.id, seat_code="A1")]
    db.add(booking)
    db.commit()
    snapshot = (admin_showtime.movie_id, admin_showtime.start_time, admin_showtime.room, admin_showtime.price)
    booking_id = booking.id

    freeze_today(monkeypatch, first_day + timedelta(days=1))
    seed(db)
    db.refresh(admin_showtime)
    assert (admin_showtime.movie_id, admin_showtime.start_time,
            admin_showtime.room, admin_showtime.price) == snapshot
    assert db.get(Booking, booking_id) is not None
    assert db.scalar(select(func.count()).select_from(BookingSeat).where(
        BookingSeat.booking_id == booking_id
    )) == 1
