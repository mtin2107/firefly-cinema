import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta

import pytest
from sqlalchemy import func, select

from app import config
from app.models import Booking, BookingSeat, PaymentTransaction

URL = "/api/payments/sepay-webhook"
SECRET = "t33-secret"
API_KEY = "t33-api-key"


@pytest.fixture
def hmac_mode(monkeypatch):
    monkeypatch.setattr(config, "SEPAY_WEBHOOK_SECRET", SECRET)
    monkeypatch.setattr(config, "SEPAY_API_KEY", "")


@pytest.fixture
def key_mode(monkeypatch):
    monkeypatch.setattr(config, "SEPAY_WEBHOOK_SECRET", "")
    monkeypatch.setattr(config, "SEPAY_API_KEY", API_KEY)


@pytest.fixture
def booking(client, auth_headers, showtime, db):
    response = client.post("/api/bookings", headers=auth_headers["user"],
                           json={"showtime_id": showtime.id, "seats": ["A1"]})
    assert response.status_code == 201
    return db.get(Booking, response.json()["id"])


def _payload(tx_id=1, amount=0, content="", **extra):
    body = {"id": tx_id, "gateway": "MBBank", "transactionDate": "2026-11-13 10:00:00",
            "accountNumber": "0000000000", "subAccount": None, "code": None, "content": content,
            "transferType": "in", "transferAmount": amount, "accumulated": 0,
            "referenceCode": "SB1", "description": ""}
    body.update(extra)
    return json.dumps(body).encode()


def _signed(raw, secret=SECRET, ts=None):
    ts = str(int(time.time()) if ts is None else ts)
    digest = hmac.new(secret.encode(), ts.encode() + b"." + raw, hashlib.sha256).hexdigest()
    return {"X-SePay-Timestamp": ts, "X-SePay-Signature": f"sha256={digest}",
            "Content-Type": "application/json"}


def _send_hmac(client, raw, **kw):
    return client.post(URL, content=raw, headers=_signed(raw, **kw))


def _send_key(client, raw, key=API_KEY):
    return client.post(URL, content=raw, headers={"Authorization": f"Apikey {key}",
                                                  "Content-Type": "application/json"})


def _tx_count(db):
    return db.scalar(select(func.count()).select_from(PaymentTransaction))


def _code(booking):
    return f"FF{booking.id:05d}"


# AC-01, AC-02
@pytest.mark.parametrize("status", ["held", "pending_verify"])
def test_valid_webhook_marks_booking_paid(client, db, hmac_mode, booking, status):
    booking.status = status
    db.commit()
    response = _send_hmac(client, _payload(amount=booking.total, content=f"{_code(booking)} chuyen tien"))
    assert response.status_code == 200
    assert response.json() == {"success": True}
    db.refresh(booking)
    assert booking.status == "paid"
    row = db.get(PaymentTransaction, 1)
    assert (row.result, row.booking_id, row.amount) == ("paid", booking.id, booking.total)


# AC-03
@pytest.mark.parametrize("tamper", ["bad_secret", "body_changed", "no_headers", "old_ts", "api_key_instead"])
def test_hmac_rejects_bad_requests(client, db, hmac_mode, booking, tamper):
    raw = _payload(amount=booking.total, content=_code(booking))
    if tamper == "bad_secret":
        response = _send_hmac(client, raw, secret="wrong")
    elif tamper == "body_changed":
        headers = _signed(raw)
        response = client.post(URL, content=raw.replace(b'"in"', b'"in" '), headers=headers)
    elif tamper == "no_headers":
        response = client.post(URL, content=raw, headers={"Content-Type": "application/json"})
    elif tamper == "old_ts":
        response = _send_hmac(client, raw, ts=int(time.time()) - 301)
    else:
        response = client.post(URL, content=raw, headers={"Authorization": f"Apikey {SECRET}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Webhook không hợp lệ."
    assert _tx_count(db) == 0
    db.refresh(booking)
    assert booking.status == "held"


# AC-04
def test_api_key_mode(client, db, key_mode, booking):
    raw = _payload(amount=booking.total, content=_code(booking))
    for bad in ({"Authorization": "Apikey wrong"}, {"Authorization": f"Bearer {API_KEY}"}, {}):
        assert client.post(URL, content=raw, headers=bad).status_code == 401
    assert _tx_count(db) == 0
    assert _send_key(client, raw).status_code == 200
    db.refresh(booking)
    assert booking.status == "paid"


def test_disabled_without_secret_or_key(client, db, monkeypatch, booking):
    monkeypatch.setattr(config, "SEPAY_WEBHOOK_SECRET", "")
    monkeypatch.setattr(config, "SEPAY_API_KEY", "")
    response = _send_key(client, _payload(amount=booking.total, content=_code(booking)), key="")
    assert response.status_code == 503
    assert _tx_count(db) == 0


# AC-05
def test_duplicate_id_is_processed_once(client, db, hmac_mode, booking):
    raw = _payload(tx_id=7, amount=booking.total, content=_code(booking))
    assert _send_hmac(client, raw).json() == {"success": True}
    booking.status = "held"  # nếu bị xử lý lại, vé sẽ quay về paid và sinh thêm dòng
    db.commit()
    assert _send_hmac(client, raw).json() == {"success": True}
    assert _tx_count(db) == 1
    db.refresh(booking)
    assert booking.status == "held"


# AC-06
def test_underpaid_needs_review_and_overpaid_is_paid(client, db, hmac_mode, booking):
    _send_hmac(client, _payload(tx_id=1, amount=booking.total - 1000, content=_code(booking)))
    db.refresh(booking)
    assert booking.status == "held"
    row = db.get(PaymentTransaction, 1)
    assert row.result == "needs_review" and row.note == "Thiếu 1.000 đ."

    _send_hmac(client, _payload(tx_id=2, amount=booking.total + 5000, content=_code(booking)))
    db.refresh(booking)
    assert booking.status == "paid"
    assert db.get(PaymentTransaction, 2).note == "Dư 5.000 đ."


# AC-07
@pytest.mark.parametrize("status", ["expired", "rejected", "paid"])
def test_non_pending_booking_is_not_changed(client, db, hmac_mode, booking, status):
    booking.status = status
    db.commit()
    _send_hmac(client, _payload(amount=booking.total, content=_code(booking)))
    db.refresh(booking)
    assert booking.status == status
    assert db.get(PaymentTransaction, 1).result == "needs_review"


def test_money_after_hold_expired_does_not_restore_seats(client, db, hmac_mode, booking):
    booking.created_at = datetime.now() - timedelta(minutes=20)
    db.commit()
    _send_hmac(client, _payload(amount=booking.total, content=_code(booking)))
    db.refresh(booking)
    assert booking.status == "expired"
    assert db.get(PaymentTransaction, 1).note == "Vé đã hết hạn giữ chỗ."
    assert db.scalar(select(func.count()).select_from(BookingSeat).where(
        BookingSeat.booking_id == booking.id)) == 0


# AC-08
@pytest.mark.parametrize("content,transfer_type,result", [
    ("chuyen tien an trua", "in", "needs_review"),
    ("FF99999 chuyen tien", "in", "needs_review"),
    ("FF00001", "out", "ignored"),
])
def test_unmatched_or_outgoing(client, db, hmac_mode, booking, content, transfer_type, result):
    response = _send_hmac(client, _payload(amount=booking.total, content=content, transferType=transfer_type))
    assert response.json() == {"success": True}
    assert db.get(PaymentTransaction, 1).result == result
    db.refresh(booking)
    assert booking.status == "held"


# AC-09
@pytest.mark.parametrize("field", ["code", "content"])
def test_code_from_sepay_or_bank_memo(client, db, hmac_mode, booking, field):
    extra = ({"code": _code(booking), "content": "chuyen tien"} if field == "code"
             else {"content": f"MBVCB.123.{_code(booking).lower()}.chuyen tien"})
    _send_hmac(client, _payload(amount=booking.total, **extra))
    db.refresh(booking)
    assert booking.status == "paid"


def test_invalid_body_returns_422(client, db, hmac_mode):
    raw = b'{"id": "abc"}'
    assert _send_hmac(client, raw).status_code == 422
    assert _tx_count(db) == 0


# AC-15
def test_admin_lists_and_resolves(client, db, hmac_mode, booking, auth_headers):
    _send_hmac(client, _payload(tx_id=1, amount=1000, content=_code(booking)))
    _send_hmac(client, _payload(tx_id=2, amount=1000, content="khong ma"))
    admin = auth_headers["admin"]

    assert client.get("/api/admin/payments", headers=auth_headers["user"]).status_code == 403
    assert client.post("/api/admin/payments/1/resolve", headers=auth_headers["user"]).status_code == 403

    rows = client.get("/api/admin/payments?result=needs_review", headers=admin).json()
    assert {row["id"] for row in rows} == {1, 2}
    first = next(row for row in rows if row["id"] == 1)
    assert first["booking_code"] == _code(booking) and first["amount"] == 1000

    resolved = client.post("/api/admin/payments/1/resolve", headers=admin)
    assert resolved.status_code == 200 and resolved.json()["result"] == "resolved"
    assert client.post("/api/admin/payments/1/resolve", headers=admin).status_code == 409
    assert client.post("/api/admin/payments/999/resolve", headers=admin).status_code == 404
    assert [row["id"] for row in client.get("/api/admin/payments?result=needs_review", headers=admin).json()] == [2]


def test_user_can_still_cancel_hold_with_underpaid_transaction(client, db, hmac_mode, booking, auth_headers):
    _send_hmac(client, _payload(amount=1000, content=_code(booking)))
    response = client.delete(f"/api/bookings/{booking.id}", headers=auth_headers["user"])
    assert response.status_code == 200
    assert db.get(PaymentTransaction, 1).booking_id == booking.id
