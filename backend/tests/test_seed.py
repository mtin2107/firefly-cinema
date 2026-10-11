from datetime import date, datetime, time, timedelta

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models import Booking, BookingSeat, Movie, Showtime
from app.seed import _ensure_showtimes, seed
from app.showtime_rules import CLEANUP_MINUTES


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


def test_deleting_all_showtimes_of_a_day_is_not_reverted(db, movie, monkeypatch):
    today = date(2026, 10, 11)
    target = today + timedelta(days=2)
    freeze_today(monkeypatch, today)
    _ensure_showtimes(db, days=5)
    start = datetime.combine(target, time.min)
    db.execute(delete(Showtime).where(
        Showtime.start_time >= start,
        Showtime.start_time < start + timedelta(days=1),
    ))
    db.commit()

    with Session(bind=db.get_bind()) as restarted_db:
        seed(restarted_db)
        assert restarted_db.scalar(select(func.count()).select_from(Showtime).where(
            Showtime.start_time >= start,
            Showtime.start_time < start + timedelta(days=1),
        )) == 0


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


def test_new_rolling_day_keeps_admin_showtime_and_seeds_other_movies(
    db, movie, monkeypatch
):
    first_day = date(2026, 10, 11)
    second_movie = Movie(
        title="Phim B rolling", genre="Tâm lý", duration_min=95,
        age_rating="T13", release_date="2026-10-01", status="now_showing",
        director="Đạo diễn", cast="Diễn viên", score=0, description="Mô tả",
        poster_bg="#334455", poster_fg="#ffffff", country="Việt Nam",
        formats="Phụ đề",
    )
    db.add(second_movie)
    db.commit()
    freeze_today(monkeypatch, first_day)
    _ensure_showtimes(db, days=5)

    target = first_day + timedelta(days=5)
    admin_showtime = Showtime(
        movie_id=movie.id,
        start_time=datetime.combine(target, time(10, 0)),
        room="Phòng 1",
        price=123_000,
    )
    db.add(admin_showtime)
    db.commit()
    admin_snapshot = (
        admin_showtime.id, admin_showtime.movie_id, admin_showtime.start_time,
        admin_showtime.room, admin_showtime.price,
    )

    freeze_today(monkeypatch, first_day + timedelta(days=1))
    seed(db)

    db.refresh(admin_showtime)
    assert (
        admin_showtime.id, admin_showtime.movie_id, admin_showtime.start_time,
        admin_showtime.room, admin_showtime.price,
    ) == admin_snapshot
    day_start = datetime.combine(target, time.min)
    rows = db.scalars(select(Showtime).where(
        Showtime.start_time >= day_start,
        Showtime.start_time < day_start + timedelta(days=1),
    ).order_by(Showtime.start_time, Showtime.id)).all()
    assert {row.movie_id for row in rows} >= {movie.id, second_movie.id}
    for index, left in enumerate(rows):
        left_movie = db.get(Movie, left.movie_id)
        left_end = left.start_time + timedelta(
            minutes=left_movie.duration_min + CLEANUP_MINUTES
        )
        for right in rows[index + 1:]:
            if left.room != right.room:
                continue
            right_movie = db.get(Movie, right.movie_id)
            right_end = right.start_time + timedelta(
                minutes=right_movie.duration_min + CLEANUP_MINUTES
            )
            assert not (left.start_time < right_end and right.start_time < left_end)


def test_new_now_showing_movie_gets_schedule_on_already_seeded_days(
    db, movie, monkeypatch
):
    today = date(2026, 10, 11)
    new_movie = Movie(
        title="Phim mới đang chiếu", genre="Gia đình", duration_min=90,
        age_rating="P", release_date="2026-10-11", status="upcoming",
        director="Đạo diễn", cast="Diễn viên", score=0, description="Mô tả",
        poster_bg="#445566", poster_fg="#ffffff", country="Việt Nam",
        formats="Lồng tiếng",
    )
    db.add(new_movie)
    db.commit()
    freeze_today(monkeypatch, today)
    _ensure_showtimes(db, days=5)
    assert db.scalar(select(func.count()).select_from(Showtime).where(
        Showtime.movie_id == new_movie.id
    )) == 0

    new_movie.status = "now_showing"
    db.commit()

    seed(db)

    scheduled_days = set(db.scalars(select(Showtime.start_time).where(
        Showtime.movie_id == new_movie.id
    )).all())
    assert {value.date() for value in scheduled_days} == {
        today + timedelta(days=offset) for offset in range(5)
    }


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
