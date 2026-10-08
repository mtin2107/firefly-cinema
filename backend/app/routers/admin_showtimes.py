from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import BookingSeat, Movie, Showtime, User
from ..schemas import ShowtimeIn, ShowtimeOut
from ..security import require_admin
from ..showtime_rules import ROOMS, find_showtime_conflict

router = APIRouter(prefix="/api/admin/showtimes", tags=["Quản trị suất chiếu"])


def _showtime_or_404(db: Session, showtime_id: int) -> Showtime:
    showtime = db.get(Showtime, showtime_id)
    if showtime is None:
        raise HTTPException(404, "Không tìm thấy suất chiếu.")
    return showtime


def _movie_for_new_showtime(db: Session, movie_id: int) -> Movie:
    movie = db.get(Movie, movie_id)
    if movie is None:
        raise HTTPException(422, "Phim không tồn tại.")
    if movie.status == "ended":
        raise HTTPException(422, "Phim đã chiếu xong, không thể tạo suất mới.")
    return movie


def _validate_body(db: Session, body: ShowtimeIn, *, exclude_id: int | None = None) -> Movie:
    if body.room not in ROOMS:
        raise HTTPException(422, "Phòng chiếu không hợp lệ.")
    movie = _movie_for_new_showtime(db, body.movie_id)
    conflict = find_showtime_conflict(
        db,
        room=body.room,
        start_time=body.start_time,
        duration_min=movie.duration_min,
        exclude_showtime_id=exclude_id,
    )
    if conflict:
        showtime, conflict_movie = conflict
        raise HTTPException(
            409,
            f"Phòng {body.room.removeprefix('Phòng ')} đã có suất {conflict_movie.title} "
            f"lúc {showtime.start_time:%H:%M}. Hãy chọn giờ khác hoặc phòng khác.",
        )
    return movie


def _ticket_count(db: Session, showtime_id: int) -> int:
    return db.scalar(
        select(func.count()).select_from(BookingSeat).where(BookingSeat.showtime_id == showtime_id)
    ) or 0


def _ensure_mutable(db: Session, showtime: Showtime) -> None:
    tickets = _ticket_count(db, showtime.id)
    if tickets:
        raise HTTPException(409, f"Suất chiếu đã có {tickets} vé, không sửa hay xóa được.")


@router.get("", response_model=list[ShowtimeOut])
def list_showtimes(
    movie_id: int | None = None,
    date_filter: date | None = Query(None, alias="date"),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = select(Showtime).order_by(Showtime.start_time, Showtime.room, Showtime.id)
    if movie_id is not None:
        query = query.where(Showtime.movie_id == movie_id)
    if date_filter is not None:
        start = datetime.combine(date_filter, time.min)
        query = query.where(Showtime.start_time >= start, Showtime.start_time < start + timedelta(days=1))
    return db.scalars(query).all()


@router.post("", response_model=ShowtimeOut, status_code=201)
def create_showtime(
    body: ShowtimeIn,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    _validate_body(db, body)
    showtime = Showtime(**body.model_dump())
    db.add(showtime)
    db.commit()
    db.refresh(showtime)
    return showtime


@router.put("/{showtime_id}", response_model=ShowtimeOut)
def update_showtime(
    showtime_id: int,
    body: ShowtimeIn,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    showtime = _showtime_or_404(db, showtime_id)
    _ensure_mutable(db, showtime)
    _validate_body(db, body, exclude_id=showtime.id)
    for field, value in body.model_dump().items():
        setattr(showtime, field, value)
    db.commit()
    db.refresh(showtime)
    return showtime


@router.delete("/{showtime_id}")
def delete_showtime(
    showtime_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    showtime = _showtime_or_404(db, showtime_id)
    _ensure_mutable(db, showtime)
    db.delete(showtime)
    db.commit()
    return {"detail": "Đã xóa suất chiếu."}
