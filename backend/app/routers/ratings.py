"""Viewer ratings; one atomic upsert per user and movie."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Movie, Rating, User
from ..schemas import RatingIn
from ..security import get_current_user
from ..rate_limit import SlidingWindowRateLimiter
from .movies import get_movie_or_404

router = APIRouter(prefix="/api/movies", tags=["Chấm sao"])
_rating_limits = SlidingWindowRateLimiter()


def require_rateable(movie):
    if movie.status == "coming_soon":
        raise HTTPException(400, "Phim sắp chiếu chưa nhận bình luận hoặc chấm sao.")


def limit_rating(user_id):
    _rating_limits.hit(user_id, limit=20, seconds=60,
                       message="Bạn chấm sao quá nhanh. Hãy thử lại sau ít phút.")


def save_rating(db, movie_id, user_id, stars):
    statement = insert(Rating).values(movie_id=movie_id, user_id=user_id, stars=stars)
    db.execute(statement.on_conflict_do_update(
        index_elements=[Rating.user_id, Rating.movie_id],
        set_={"stars": stars, "updated_at": datetime.now()},
    ))


def rating_result(db, movie_id, stars):
    avg, count = db.execute(select(func.round(func.avg(Rating.stars), 1), func.count(Rating.id))
                            .where(Rating.movie_id == movie_id)).one()
    return {"stars": stars, "rating_avg": float(avg or 0), "rating_count": count}


@router.get("/{movie_id}/my-rating")
def mine(movie_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    get_movie_or_404(db, movie_id)
    return {"stars": db.scalar(select(Rating.stars).where(
        Rating.movie_id == movie_id, Rating.user_id == user.id))}


@router.put("/{movie_id}/rating")
def set_rating(movie_id: int, body: RatingIn, user: User = Depends(get_current_user),
               db: Session = Depends(get_db)):
    require_rateable(get_movie_or_404(db, movie_id))
    limit_rating(user.id)
    save_rating(db, movie_id, user.id, body.stars)
    db.commit()
    return rating_result(db, movie_id, body.stars)


@router.delete("/{movie_id}/rating")
def remove_rating(movie_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_rateable(get_movie_or_404(db, movie_id))
    limit_rating(user.id)
    rating = db.scalar(select(Rating).where(Rating.movie_id == movie_id, Rating.user_id == user.id))
    if rating:
        db.delete(rating)
    db.commit()
    return rating_result(db, movie_id, None)
