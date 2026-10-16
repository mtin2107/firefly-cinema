from datetime import datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Integer, case, cast, func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Comment, Movie, User
from ..schemas import AdminSentimentOut
from ..security import require_admin

router = APIRouter(prefix="/api/admin", tags=["Thống kê cảm xúc"])


@router.get("/sentiment", response_model=AdminSentimentOut)
def sentiment(
    days: int = Query(30),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if not 1 <= days <= 365:
        raise HTTPException(422, "Số ngày thống kê phải từ 1 đến 365.")

    # Gồm hôm nay và days - 1 ngày trước; end là 00:00 ngày mai và không được tính.
    today = datetime.now().date()
    first_date = today - timedelta(days=days - 1)
    start = datetime.combine(first_date, time.min)
    end = datetime.combine(today + timedelta(days=1), time.min)
    in_range = (Comment.created_at >= start, Comment.created_at < end)

    effective_negative = case(
        (Comment.human_label.is_not(None), Comment.human_label),
        else_=cast(Comment.is_negative, Integer),
    )
    reviewed = case((Comment.human_label.is_not(None), 1), else_=0)
    model_agrees = case(
        (
            Comment.human_label.is_not(None),
            case((Comment.human_label == cast(Comment.is_negative, Integer), 1), else_=0),
        ),
        else_=0,
    )

    summary_row = db.execute(select(
        func.count(Comment.id),
        func.coalesce(func.sum(effective_negative), 0),
        func.coalesce(func.sum(reviewed), 0),
        func.coalesce(func.sum(model_agrees), 0),
    ).where(*in_range)).one()
    total, negative, reviewed_count, agree = (int(value) for value in summary_row)

    movie_rows = db.execute(select(
        Comment.movie_id,
        Movie.title,
        func.count(Comment.id).label("total"),
        func.coalesce(func.sum(effective_negative), 0).label("negative"),
        func.coalesce(func.avg(Comment.negative_score), 0).label("avg_negative_score"),
    ).join(Movie, Movie.id == Comment.movie_id).where(*in_range).group_by(
        Comment.movie_id, Movie.title
    )).all()
    movies = [{
        "movie_id": row.movie_id,
        "title": row.title,
        "total": row.total,
        "negative": int(row.negative),
        "negative_ratio": int(row.negative) / row.total,
        "avg_negative_score": float(row.avg_negative_score),
    } for row in movie_rows]
    movies.sort(key=lambda row: (-row["negative_ratio"], -row["total"], row["title"], row["movie_id"]))

    daily_rows = db.execute(select(
        func.date(Comment.created_at).label("date"),
        func.count(Comment.id).label("total"),
        func.coalesce(func.sum(effective_negative), 0).label("negative"),
    ).where(*in_range).group_by(func.date(Comment.created_at))).all()
    daily_by_date = {row.date: (row.total, int(row.negative)) for row in daily_rows}
    daily = []
    for offset in range(days):
        date_value = first_date + timedelta(days=offset)
        total_on_date, negative_on_date = daily_by_date.get(date_value.isoformat(), (0, 0))
        daily.append({"date": date_value.isoformat(), "total": total_on_date, "negative": negative_on_date})

    return {
        "summary": {
            "total": total,
            "negative": negative,
            "negative_ratio": negative / total if total else 0,
            "reviewed": reviewed_count,
            "model_human_accuracy": agree / reviewed_count if reviewed_count else 0,
        },
        "movies": movies,
        "daily": daily,
    }
