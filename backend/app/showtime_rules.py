from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Movie, Showtime

CLEANUP_MINUTES = 15


def find_showtime_conflict(
    db: Session,
    *,
    room: str,
    start_time: datetime,
    duration_min: int,
    exclude_showtime_id: int | None = None,
) -> tuple[Showtime, Movie] | None:
    """Tìm suất giao với khoảng [start, start + duration + 15 phút) trong cùng phòng."""
    candidate_end = start_time + timedelta(minutes=duration_min + CLEANUP_MINUTES)
    rows = db.execute(
        select(Showtime, Movie)
        .join(Movie, Movie.id == Showtime.movie_id)
        .where(Showtime.room == room)
        .order_by(Showtime.start_time)
    ).all()
    for showtime, movie in rows:
        if exclude_showtime_id is not None and showtime.id == exclude_showtime_id:
            continue
        occupied_until = showtime.start_time + timedelta(minutes=movie.duration_min + CLEANUP_MINUTES)
        if start_time < occupied_until and showtime.start_time < candidate_end:
            return showtime, movie
    return None
