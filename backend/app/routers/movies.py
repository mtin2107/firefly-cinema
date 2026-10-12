import unicodedata
from datetime import datetime, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ..database import get_db
from ..booking_rules import expire_holds
from ..models import Movie, Showtime, Booking, BookingSeat, Comment
from ..schemas import MovieOut, ShowtimeOut, ShowtimeDetailOut

router = APIRouter(prefix="/api", tags=["Phim & suất chiếu"])


def get_movie_or_404(db: Session, movie_id: int) -> Movie:
    movie = db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(404, "Không tìm thấy phim.")
    return movie


def _split(value: str) -> list[str]:
    return [x.strip() for x in value.split(",") if x.strip()]


def _plain(text: str) -> str:
    """Bỏ dấu để tìm kiếm: "Mèo Mướp" -> "meo muop" """
    text = unicodedata.normalize("NFD", text.lower()).replace("đ", "d")
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


def _ranking(db: Session, collection: str) -> dict[int, int]:
    """Trả về {movie_id: điểm} để xếp hạng các bộ sưu tập."""
    if collection in ("hot_week", "hot_month"):
        since = datetime.now() - timedelta(days=7 if collection == "hot_week" else 30)
        rows = db.execute(
            select(Showtime.movie_id, func.count(BookingSeat.id))
            .join(BookingSeat, BookingSeat.showtime_id == Showtime.id)
            .join(Booking, Booking.id == BookingSeat.booking_id)
            .where(Booking.created_at >= since)
            .group_by(Showtime.movie_id)
        ).all()
    elif collection == "top_comments":
        rows = db.execute(select(Comment.movie_id, func.count(Comment.id)).group_by(Comment.movie_id)).all()
    else:
        return {}
    return {movie_id: count for movie_id, count in rows if count > 0}


@router.get("/movies", response_model=list[MovieOut])
def list_movies(
    status: Literal["now_showing", "coming_soon", "ended"] | None = None,
    genre: str | None = None,        # vd: Hành động
    country: str | None = None,      # vd: Hàn Quốc
    year: int | None = None,         # phát hành đúng năm này
    year_before: int | None = None,  # phát hành trước năm này
    age_rating: str | None = None,   # vd: T18
    format: str | None = None,       # "Phụ đề" | "Lồng tiếng"
    collection: Literal["hot_week", "hot_month", "top_comments", "top_rated"] | None = None,
    q: str | None = None,            # tìm theo tên phim, không cần gõ dấu
    db: Session = Depends(get_db),
):
    query = select(Movie).order_by(Movie.release_date.desc())
    if status:
        query = query.where(Movie.status == status)
    if country:
        query = query.where(Movie.country == country)
    if year:
        query = query.where(Movie.release_date.like(f"{year}-%"))
    if year_before:
        query = query.where(Movie.release_date < f"{year_before}-01-01")
    if age_rating:
        query = query.where(Movie.age_rating == age_rating)
    movies = db.scalars(query).all()

    # Các cột chứa nhiều giá trị ("Hành động, Hài hước") lọc chính xác bằng Python
    if genre:
        movies = [m for m in movies if genre in _split(m.genre)]
    if format:
        movies = [m for m in movies if format in _split(m.formats)]
    if q:
        needle = _plain(q.strip())
        movies = [m for m in movies if needle in _plain(m.title)]

    if collection == "top_rated":
        movies = sorted([m for m in movies if m.score >= 8], key=lambda m: m.score, reverse=True)
    elif collection:
        rank = _ranking(db, collection)
        movies = sorted([m for m in movies if m.id in rank], key=lambda m: rank[m.id], reverse=True)
    return movies


@router.get("/movies/{movie_id}", response_model=MovieOut)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    return get_movie_or_404(db, movie_id)


@router.get("/movies/{movie_id}/showtimes", response_model=list[ShowtimeOut])
def movie_showtimes(movie_id: int, db: Session = Depends(get_db)):
    get_movie_or_404(db, movie_id)
    return db.scalars(
        select(Showtime)
        .where(Showtime.movie_id == movie_id, Showtime.start_time > datetime.now())
        .order_by(Showtime.start_time)
    ).all()


@router.get("/showtimes/{showtime_id}", response_model=ShowtimeDetailOut)
def showtime_detail(showtime_id: int, db: Session = Depends(get_db)):
    expire_holds(db)
    db.commit()
    st = db.get(Showtime, showtime_id)
    if not st:
        raise HTTPException(404, "Không tìm thấy suất chiếu.")
    booked = db.scalars(select(BookingSeat.seat_code).where(BookingSeat.showtime_id == st.id)).all()
    return {"showtime": st, "movie": st.movie, "booked_seats": list(booked)}
