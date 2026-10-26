from datetime import datetime, time, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Integer, case, cast, func, select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Booking, BookingSeat, Comment, Movie, Rating, Showtime, User
from ..security import require_admin
from ..booking_rules import expire_holds
from ..seats import ROWS, COLS

router = APIRouter(prefix="/api/admin", tags=["Tổng quan"])

@router.get("/dashboard")
def dashboard(days: int = 30, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    if days not in (7, 30, 90):
        raise HTTPException(422, "Số ngày phải là 7, 30 hoặc 90.")
    expire_holds(db)
    db.commit()
    today = datetime.now().date()
    first = today - timedelta(days=days - 1)
    start, end = datetime.combine(first, time.min), datetime.combine(today + timedelta(days=1), time.min)
    def period(column):
        return (column >= start, column < end)
    paid = Booking.status == "paid"
    revenue = func.sum(case((paid, Booking.total), else_=0))
    paid_count = func.sum(case((paid, 1), else_=0))
    row = db.execute(select(
        func.coalesce(revenue, 0), func.coalesce(paid_count, 0),
        func.coalesce(func.sum(case((Booking.status.in_(["held", "pending_verify"]), 1), else_=0)), 0),
        func.coalesce(func.sum(case((Booking.status.in_(["expired", "rejected"]), 1), else_=0)), 0),
    ).where(*period(Booking.created_at))).one()
    seats_sold = db.scalar(select(func.count(BookingSeat.id)).join(Booking).where(paid, *period(Booking.created_at)))
    rating_avg, rating_count = db.execute(select(func.coalesce(func.avg(Rating.stars), 0), func.count(Rating.id)).where(*period(Rating.created_at))).one()
    daily_rows = db.execute(select(func.date(Booking.created_at), func.coalesce(revenue, 0), paid_count)
                            .where(*period(Booking.created_at)).group_by(func.date(Booking.created_at))).all()
    daily_map = {r[0]: {"date": r[0], "revenue": r[1], "tickets": r[2]} for r in daily_rows}
    sales = db.execute(select(Showtime.movie_id, revenue, paid_count).select_from(Booking).join(Showtime)
                       .where(*period(Booking.created_at)).group_by(Showtime.movie_id)).all()
    sales_map = {r[0]: (r[1], r[2]) for r in sales}
    # Lấp ghế gồm cả suất sắp chiếu: vé bán hôm nay thường cho suất các ngày sau.
    capacities = dict(db.execute(select(Showtime.movie_id, func.count(Showtime.id) * len(ROWS) * COLS)
                                 .where(Showtime.start_time >= start).group_by(Showtime.movie_id)).all())
    occupied = dict(db.execute(select(Showtime.movie_id, func.count(BookingSeat.id)).select_from(BookingSeat)
                               .join(Booking).join(Showtime, Showtime.id == Booking.showtime_id)
                               .where(paid, Showtime.start_time >= start).group_by(Showtime.movie_id)).all())
    ratings = {r[0]: (float(r[1]), r[2]) for r in db.execute(select(Rating.movie_id, func.avg(Rating.stars), func.count(Rating.id))
               .where(*period(Rating.created_at)).group_by(Rating.movie_id))}
    effective = case((Comment.human_label.is_not(None), Comment.human_label), else_=cast(Comment.is_negative, Integer))
    negatives = {r[0]: r[1] / r[2] for r in db.execute(select(Comment.movie_id, func.sum(effective), func.count(Comment.id))
                 .where(*period(Comment.created_at)).group_by(Comment.movie_id))}
    movies = []
    for mid, title in db.execute(select(Movie.id, Movie.title).order_by(Movie.title, Movie.id)):
        amount, count = sales_map.get(mid, (0, 0))
        avg, votes = ratings.get(mid, (0, 0))
        movies.append(dict(movie_id=mid, title=title, revenue=amount, paid_tickets=count,
                           occupancy=occupied.get(mid, 0) / capacities[mid] if capacities.get(mid) else 0,
                           rating_avg=avg, rating_count=votes, negative_rate=negatives.get(mid, 0)))
    return dict(days=days, revenue=row[0], paid_tickets=row[1], pending_tickets=row[2], cancelled_tickets=row[3],
                seats_sold=seats_sold, rating_avg=float(rating_avg), rating_count=rating_count,
                daily=[daily_map.get((first + timedelta(days=i)).isoformat(),
                       dict(date=(first + timedelta(days=i)).isoformat(), revenue=0, tickets=0)) for i in range(days)], movies=movies)


@router.get("/me/summary")
def my_summary(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    today = datetime.now().date()
    comments = db.scalars(select(Comment)).all()
    bookings = db.scalars(select(Booking)).all()
    reviewed = [c for c in comments if c.reviewed_by == user.id and c.reviewed_at]
    checked = [b for b in bookings if b.checked_in_by == user.id and b.checked_in_at]
    activity = [{"kind": "review", "id": c.id, "at": c.reviewed_at, "label": "Duyệt bình luận", "movie_title": c.movie.title} for c in reviewed]
    activity += [{"kind": "checkin", "id": b.id, "at": b.checked_in_at, "label": "Soát vé", "movie_title": b.showtime.movie.title} for b in checked]
    return {
        "todo": {"comments": sum(c.is_negative and c.human_label is None and c.reviewed_at is None for c in comments),
                 "pending_verify": sum(b.status == "pending_verify" for b in bookings),
                 "showtimes_today": db.scalar(select(func.count(Showtime.id)).where(func.date(Showtime.start_time) == today.isoformat()))},
        "work": {"reviewed_today": sum(c.reviewed_at.date() == today for c in reviewed), "reviewed_total": len(reviewed),
                 "overrides": sum(c.human_label is not None and c.human_label != int(c.is_negative) for c in reviewed),
                 "checked_in_today": sum(b.checked_in_at.date() == today for b in checked)},
        "recent_activity": sorted(activity, key=lambda a: (a["at"], a["id"]), reverse=True)[:5],
    }
