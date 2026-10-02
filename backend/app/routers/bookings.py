from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Booking, BookingSeat, Showtime, User
from ..schemas import BookingIn, BookingOut
from ..seats import is_valid_seat, seat_price, MAX_SEATS_PER_BOOKING
from ..security import get_current_user

router = APIRouter(prefix="/api/bookings", tags=["Đặt vé"])


def to_out(b: Booking) -> dict:
    return {"id": b.id, "seats": [s.seat_code for s in b.seats], "total": b.total, "created_at": b.created_at,
            "showtime": b.showtime, "movie": b.showtime.movie}


@router.post("", response_model=BookingOut, status_code=201)
def create_booking(body: BookingIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    st = db.get(Showtime, body.showtime_id)
    if not st:
        raise HTTPException(404, "Không tìm thấy suất chiếu.")
    if st.start_time <= datetime.now():
        raise HTTPException(400, "Suất chiếu này đã bắt đầu.")
    seats = sorted(set(body.seats))
    if not 1 <= len(seats) <= MAX_SEATS_PER_BOOKING:
        raise HTTPException(400, f"Chọn từ 1 đến {MAX_SEATS_PER_BOOKING} ghế.")
    invalid = [s for s in seats if not is_valid_seat(s)]
    if invalid:
        raise HTTPException(400, f"Ghế không hợp lệ: {', '.join(invalid)}.")

    taken = db.scalars(select(BookingSeat.seat_code)
                       .where(BookingSeat.showtime_id == st.id, BookingSeat.seat_code.in_(seats))).all()
    if taken:
        raise HTTPException(409, f"Ghế {', '.join(sorted(taken))} vừa có người đặt. Hãy chọn ghế khác.")

    booking = Booking(user_id=user.id, showtime_id=st.id, total=sum(seat_price(s, st.price) for s in seats))
    booking.seats = [BookingSeat(showtime_id=st.id, seat_code=s) for s in seats]
    db.add(booking)
    try:
        db.commit()
    except IntegrityError:  # 2 người bấm đặt cùng lúc
        db.rollback()
        raise HTTPException(409, "Có ghế vừa được người khác đặt. Hãy tải lại sơ đồ ghế.")
    db.refresh(booking)
    return to_out(booking)


@router.get("/me", response_model=list[BookingOut])
def my_bookings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(Booking).where(Booking.user_id == user.id).order_by(Booking.id.desc())).all()
    return [to_out(b) for b in rows]
