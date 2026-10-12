from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Booking, Comment, Movie, Showtime, User
from ..schemas import MovieIn, MovieOut
from ..security import require_admin

router = APIRouter(prefix="/api/admin/movies", tags=["Quản trị phim"])


def _movie_or_404(db: Session, movie_id: int) -> Movie:
    movie = db.get(Movie, movie_id)
    if movie is None:
        raise HTTPException(404, "Không tìm thấy phim.")
    return movie


def _values(body: MovieIn) -> dict:
    values = body.model_dump()
    values["genre"] = ", ".join(body.genre)
    values["formats"] = ", ".join(body.formats)
    return values


@router.get("", response_model=list[MovieOut])
def list_admin_movies(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.scalars(select(Movie).order_by(Movie.release_date.desc(), Movie.id.desc())).all()


@router.post("", response_model=MovieOut, status_code=201)
def create_movie(body: MovieIn, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    movie = Movie(**_values(body), score=0)
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


@router.put("/{movie_id}", response_model=MovieOut)
def update_movie(movie_id: int, body: MovieIn, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    movie = _movie_or_404(db, movie_id)
    for field, value in _values(body).items():
        setattr(movie, field, value)
    db.commit()
    db.refresh(movie)
    return movie


@router.delete("/{movie_id}")
def delete_movie(movie_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    movie = _movie_or_404(db, movie_id)
    has_booking = db.scalar(
        select(Booking.id)
        .join(Showtime, Booking.showtime_id == Showtime.id)
        .where(Showtime.movie_id == movie_id, Booking.status.not_in(("expired", "rejected")))
        .limit(1)
    )
    if has_booking is not None:
        raise HTTPException(409, "Phim đã có vé, không xóa được. Hãy chuyển trạng thái sang Đã chiếu xong.")

    db.execute(delete(Comment).where(Comment.movie_id == movie_id))
    db.execute(delete(Showtime).where(Showtime.movie_id == movie_id))
    db.delete(movie)
    db.commit()
    return {"detail": "Đã xóa phim."}
