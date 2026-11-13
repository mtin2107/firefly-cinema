"""T33: SePay báo tiền vào qua webhook → tự xác nhận vé; admin xem giao dịch cần xử lý tay."""
import hashlib
import hmac
import logging
import re
import time
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import config
from ..booking_rules import booking_code, expire_holds
from ..database import get_db
from ..models import Booking, PaymentTransaction, User
from ..schemas import PaymentOut, SepayWebhookIn
from ..security import require_admin

router = APIRouter(tags=["Thanh toán"])
logger = logging.getLogger(__name__)

BOOKING_CODE = re.compile(r"FF(\d{5,9})", re.IGNORECASE)
MAX_CLOCK_SKEW_SECONDS = 300
SUCCESS = {"success": True}


def _verify(request: Request, raw: bytes) -> None:
    secret, api_key = config.SEPAY_WEBHOOK_SECRET, config.SEPAY_API_KEY
    if not secret and not api_key:
        raise HTTPException(503, "Rạp chưa bật xác nhận thanh toán tự động.")
    if secret:
        timestamp = request.headers.get("X-SePay-Timestamp", "")
        signature = request.headers.get("X-SePay-Signature", "").strip().lower()
        if not timestamp.isdigit() or abs(time.time() - int(timestamp)) > MAX_CLOCK_SKEW_SECONDS:
            raise HTTPException(401, "Webhook không hợp lệ.")
        digest = hmac.new(secret.encode(), timestamp.encode() + b"." + raw, hashlib.sha256).hexdigest()
        ok = hmac.compare_digest(signature.encode(), f"sha256={digest}".encode())
    else:
        ok = hmac.compare_digest(
            request.headers.get("Authorization", "").encode(), f"Apikey {api_key}".encode()
        )
    if not ok:
        raise HTTPException(401, "Webhook không hợp lệ.")


def _decide(db: Session, body: SepayWebhookIn) -> tuple[int | None, str, str]:
    """Trả (booking_id, result, note). Chỉ đổi vé sang paid khi mọi điều kiện đều khớp."""
    if body.transferType != "in":
        return None, "ignored", "Không phải giao dịch tiền vào."
    match = BOOKING_CODE.search(body.code or "") or BOOKING_CODE.search(body.content)
    if not match:
        return None, "needs_review", "Không tìm thấy mã vé trong nội dung chuyển khoản."
    expire_holds(db)
    booking = db.get(Booking, int(match.group(1)))
    if booking is None:
        return None, "needs_review", f"Không có vé {match.group(0).upper()}."
    if booking.status not in {"held", "pending_verify"}:
        reasons = {"paid": "Vé đã thanh toán trước đó.", "expired": "Vé đã hết hạn giữ chỗ.",
                   "rejected": "Vé đã bị từ chối."}
        return booking.id, "needs_review", reasons.get(booking.status, "Vé không chờ thanh toán.")
    if body.transferAmount < booking.total:
        return booking.id, "needs_review", f"Thiếu {booking.total - body.transferAmount:,} đ.".replace(",", ".")
    booking.status = "paid"
    extra = body.transferAmount - booking.total
    return booking.id, "paid", f"Dư {extra:,} đ.".replace(",", ".") if extra else ""


@router.post("/api/payments/sepay-webhook")
async def sepay_webhook(request: Request, db: Session = Depends(get_db)):
    raw = await request.body()
    _verify(request, raw)
    try:
        body = SepayWebhookIn.model_validate_json(raw)
    except ValidationError:
        raise HTTPException(422, "Dữ liệu webhook không hợp lệ.")
    if db.get(PaymentTransaction, body.id) is not None:
        return SUCCESS
    booking_id, result, note = _decide(db, body)
    db.add(PaymentTransaction(
        id=body.id, booking_id=booking_id, amount=body.transferAmount, content=body.content[:255],
        transaction_date=body.transactionDate[:30], result=result, note=note,
    ))
    try:
        db.commit()
    except IntegrityError:  # cùng id đến song song: bản kia đã xử lý
        db.rollback()
        return SUCCESS
    logger.info("SePay %s: vé %s → %s", body.id, booking_code(booking_id) if booking_id else "-", result)
    return SUCCESS


def _payment_out(row: PaymentTransaction) -> dict:
    return {
        "id": row.id, "booking_code": booking_code(row.booking_id) if row.booking_id else None,
        "amount": row.amount, "content": row.content, "transaction_date": row.transaction_date,
        "result": row.result, "note": row.note, "received_at": row.received_at,
    }


@router.get("/api/admin/payments", response_model=list[PaymentOut])
def list_payments(
    result: Literal["paid", "needs_review", "ignored", "resolved"] | None = None,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = select(PaymentTransaction).order_by(PaymentTransaction.received_at.desc()).limit(200)
    if result:
        query = query.where(PaymentTransaction.result == result)
    return [_payment_out(row) for row in db.scalars(query).all()]


@router.post("/api/admin/payments/{payment_id}/resolve", response_model=PaymentOut)
def resolve_payment(payment_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    row = db.get(PaymentTransaction, payment_id)
    if row is None:
        raise HTTPException(404, "Không tìm thấy giao dịch.")
    if row.result != "needs_review":
        raise HTTPException(409, "Chỉ đánh dấu được giao dịch đang cần xử lý.")
    row.result = "resolved"
    db.commit()
    return _payment_out(row)
