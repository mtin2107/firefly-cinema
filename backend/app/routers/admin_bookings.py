from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..booking_rules import booking_code, booking_out, expire_holds, release_booking_seats
from ..database import get_db
from ..models import Booking, User
from ..schemas import AdminBookingOut
from ..security import require_admin

router = APIRouter(prefix="/api/admin/bookings", tags=["Quản trị vé"])


def _admin_out(booking: Booking) -> dict:
    return {
        **booking_out(booking),
        "checked_in_at": booking.checked_in_at,
        "checked_in_by_name": booking.checkin_user.full_name if booking.checkin_user else None,
        "customer_name": booking.user.full_name,
        "customer_email": booking.user.email,
    }


def _booking_or_404(db: Session, booking_id: int) -> Booking:
    booking = db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(404, "Không tìm thấy vé.")
    return booking


@router.get("", response_model=list[AdminBookingOut])
def list_bookings(
    status: Literal["held", "pending_verify", "paid", "expired", "rejected"] | None = None,
    code: str | None = None,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    expire_holds(db)
    db.commit()
    query = select(Booking).order_by(Booking.id.desc()).limit(200)
    if status:
        query = query.where(Booking.status == status)
    if code:
        value = code.strip().upper()
        if value.startswith("FF"):
            value = value[2:]
        if not value.isdigit():
            return []
        query = query.where(Booking.id == int(value))
    return [_admin_out(booking) for booking in db.scalars(query).all()]


@router.post("/{booking_id}/confirm", response_model=AdminBookingOut)
def confirm_booking(
    booking_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    expire_holds(db)
    db.commit()
    booking = _booking_or_404(db, booking_id)
    if booking.status not in {"held", "pending_verify"}:
        raise HTTPException(409, "Vé không ở trạng thái có thể xác nhận thanh toán.")
    booking.status = "paid"
    db.commit()
    db.refresh(booking)
    return _admin_out(booking)


@router.post("/{booking_id}/reject", response_model=AdminBookingOut)
def reject_booking(
    booking_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    expire_holds(db)
    db.commit()
    booking = _booking_or_404(db, booking_id)
    if booking.status not in {"held", "pending_verify"}:
        raise HTTPException(409, "Vé không ở trạng thái có thể từ chối thanh toán.")
    release_booking_seats(db, booking.id)
    booking.status = "rejected"
    db.commit()
    db.refresh(booking)
    return _admin_out(booking)
