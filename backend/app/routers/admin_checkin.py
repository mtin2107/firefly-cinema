from datetime import datetime
import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Booking, User
from ..security import require_admin
from ..schemas import AdminBookingOut
from ..booking_rules import expire_holds
from .admin_bookings import _admin_out

router = APIRouter(prefix="/api/admin/checkin", tags=["Soát vé"])

def lookup(db, code):
    match = re.fullmatch(r"FF([0-9]+)", code.strip().upper())
    booking_id = int(match[1]) if match and len(match[1]) <= 12 else 0
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(404, "Không tìm thấy vé.")
    return booking

def reason(booking):
    if booking.checked_in_at:
        return f"Vé đã được soát lúc {booking.checked_in_at:%H:%M %d/%m/%Y}."
    return {"held": "Vé chưa thanh toán, đang giữ chỗ.",
            "pending_verify": "Vé chưa thanh toán, đang chờ xác nhận chuyển khoản.",
            "expired": "Vé đã hủy do quá hạn thanh toán.",
            "rejected": "Vé đã hủy do không nhận được thanh toán."}.get(booking.status, "Vé không thể soát.")

@router.get("/{code}", response_model=AdminBookingOut)
def get_ticket(code: str, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    expire_holds(db)
    db.commit()
    return _admin_out(lookup(db, code))

@router.post("/{code}", response_model=AdminBookingOut)
def checkin(code: str, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    expire_holds(db)
    db.commit()
    booking = lookup(db, code)
    result = db.execute(update(Booking).where(
        Booking.id == booking.id, Booking.status == "paid", Booking.checked_in_at.is_(None)
    ).values(checked_in_at=datetime.now(), checked_in_by=user.id).execution_options(synchronize_session=False))
    db.commit()
    db.refresh(booking)
    if result.rowcount != 1:
        raise HTTPException(409, reason(booking))
    return _admin_out(booking)
