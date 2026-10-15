from datetime import datetime, timedelta
from urllib.parse import urlencode

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .config import BANK_ACCOUNT, BANK_ACCOUNT_NAME, BANK_ID
from .models import Booking, BookingSeat, Showtime

HOLD_CUTOFF_MINUTES = 30
HOLD_MINUTES = 15
BOOKING_STATUSES = {"held", "pending_verify", "paid", "expired", "rejected"}


def booking_code(booking_id: int) -> str:
    return f"FF{booking_id:05d}"


def hold_expires_at(booking: Booking) -> datetime:
    return min(
        booking.created_at + timedelta(minutes=HOLD_MINUTES),
        booking.showtime.start_time - timedelta(minutes=HOLD_CUTOFF_MINUTES),
    )


def transfer_payment_enabled() -> bool:
    return all((BANK_ID, BANK_ACCOUNT, BANK_ACCOUNT_NAME))


def qr_url(booking: Booking) -> str | None:
    if booking.status != "held" or not transfer_payment_enabled():
        return None
    query = urlencode({
        "amount": booking.total,
        "addInfo": booking_code(booking.id),
        "accountName": BANK_ACCOUNT_NAME,
    })
    return f"https://img.vietqr.io/image/{BANK_ID}-{BANK_ACCOUNT}-compact2.png?{query}"


def booking_out(booking: Booking) -> dict:
    return {
        "id": booking.id,
        "code": booking_code(booking.id),
        "status": booking.status,
        "hold_expires_at": hold_expires_at(booking),
        "qr_url": qr_url(booking),
        "seats": [seat.seat_code for seat in booking.seats],
        "total": booking.total,
        "created_at": booking.created_at,
        "showtime": booking.showtime,
        "movie": booking.showtime.movie,
    }


def release_booking_seats(db: Session, booking_id: int) -> None:
    db.execute(delete(BookingSeat).where(BookingSeat.booking_id == booking_id))


def expire_holds(db: Session, now: datetime | None = None) -> int:
    current = now or datetime.now()
    held = db.scalars(select(Booking).where(Booking.status == "held")).all()
    expired = [booking for booking in held if hold_expires_at(booking) <= current]
    for booking in expired:
        release_booking_seats(db, booking.id)
        booking.status = "expired"
    if expired:
        db.flush()
        for booking in expired:
            db.expire(booking, ["seats"])
    return len(expired)
