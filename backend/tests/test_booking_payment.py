from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse

from sqlalchemy import func, select

from app.models import Booking, BookingSeat, Showtime, User
from app.security import create_token, hash_password


def _create(client, headers, showtime, seats=("A1",)):
    return client.post(
        "/api/bookings",
        headers=headers,
        json={"showtime_id": showtime.id, "seats": list(seats)},
    )


def test_new_booking_contract_and_one_hold_per_showtime(client, auth_headers, showtime):
    response = _create(client, auth_headers["user"], showtime, ("A1", "F1"))
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "held"
    assert body["code"] == f"FF{body['id']:05d}"
    created_at = datetime.fromisoformat(body["created_at"])
    assert datetime.fromisoformat(body["hold_expires_at"]) == min(
        created_at + timedelta(minutes=15), showtime.start_time - timedelta(minutes=30)
    )

    detail = client.get(f"/api/showtimes/{showtime.id}").json()
    assert detail["booked_seats"] == ["A1", "F1"]
    duplicate_hold = _create(client, auth_headers["user"], showtime, ("A2",))
    assert duplicate_hold.status_code == 409
    assert duplicate_hold.json()["detail"] == (
        "Bạn đang giữ chỗ cho suất này. Hãy thanh toán vé đang giữ trước khi đặt thêm."
    )


def test_expired_hold_releases_unique_seat_for_another_user(
    client, auth_headers, showtime, db
):
    first = _create(client, auth_headers["user"], showtime)
    booking_id = first.json()["id"]
    showtime.start_time = datetime.now() + timedelta(minutes=20)
    db.commit()

    detail = client.get(f"/api/showtimes/{showtime.id}")
    assert detail.status_code == 200
    assert "A1" not in detail.json()["booked_seats"]
    assert db.get(Booking, booking_id).status == "expired"
    assert db.scalar(select(func.count()).select_from(BookingSeat).where(
        BookingSeat.booking_id == booking_id
    )) == 0

    showtime.start_time = datetime.now() + timedelta(hours=2)
    db.commit()
    second = _create(client, auth_headers["admin"], showtime)
    assert second.status_code == 201


def test_pending_and_paid_are_not_expired(client, auth_headers, showtime, db, monkeypatch):
    from app import booking_rules

    monkeypatch.setattr(booking_rules, "BANK_ID", "970436")
    monkeypatch.setattr(booking_rules, "BANK_ACCOUNT", "123456789")
    monkeypatch.setattr(booking_rules, "BANK_ACCOUNT_NAME", "LE MINH TIN")
    held = _create(client, auth_headers["user"], showtime).json()
    claim = client.post(
        f"/api/bookings/{held['id']}/transfer-claim", headers=auth_headers["user"]
    )
    assert claim.status_code == 200
    assert claim.json()["status"] == "pending_verify"
    assert claim.json()["qr_url"] is None

    showtime.start_time = datetime.now() + timedelta(minutes=10)
    db.commit()
    assert "A1" in client.get(f"/api/showtimes/{showtime.id}").json()["booked_seats"]
    assert db.get(Booking, held["id"]).status == "pending_verify"

    confirm = client.post(
        f"/api/admin/bookings/{held['id']}/confirm", headers=auth_headers["admin"]
    )
    assert confirm.status_code == 200
    assert confirm.json()["status"] == "paid"
    assert "A1" in client.get(f"/api/showtimes/{showtime.id}").json()["booked_seats"]


def test_last_thirty_minutes_are_blocked(client, auth_headers, showtime, db):
    showtime.start_time = datetime.now() + timedelta(minutes=30)
    db.commit()
    response = _create(client, auth_headers["user"], showtime)
    assert response.status_code == 400
    assert response.json()["detail"] == "Suất chiếu sắp bắt đầu, vui lòng mua vé tại quầy."


def test_transfer_claim_ownership_and_invalid_state(client, auth_headers, showtime, db, monkeypatch):
    from app import booking_rules

    monkeypatch.setattr(booking_rules, "BANK_ID", "970436")
    monkeypatch.setattr(booking_rules, "BANK_ACCOUNT", "123456789")
    monkeypatch.setattr(booking_rules, "BANK_ACCOUNT_NAME", "LE MINH TIN")
    booking = _create(client, auth_headers["user"], showtime).json()
    other = User(full_name="Người khác", email="other@example.com",
                 password_hash=hash_password("secret1"), role="user")
    db.add(other)
    db.commit()
    other_headers = {"Authorization": f"Bearer {create_token(other.id)}"}
    assert client.post(
        f"/api/bookings/{booking['id']}/transfer-claim", headers=other_headers
    ).status_code == 404
    assert client.post(
        f"/api/bookings/{booking['id']}/transfer-claim", headers=auth_headers["user"]
    ).status_code == 200
    assert client.post(
        f"/api/bookings/{booking['id']}/transfer-claim", headers=auth_headers["user"]
    ).status_code == 409


def test_admin_list_security_confirm_reject_and_release(client, auth_headers, showtime, db):
    assert client.get("/api/admin/bookings").status_code == 401
    assert client.get("/api/admin/bookings", headers=auth_headers["user"]).status_code == 403

    first = _create(client, auth_headers["user"], showtime, ("A1",)).json()
    listing = client.get(
        f"/api/admin/bookings?status=held&code={first['code']}",
        headers=auth_headers["admin"],
    )
    assert listing.status_code == 200
    assert listing.json()[0]["customer_email"] == "user@example.com"
    assert client.post(
        f"/api/admin/bookings/{first['id']}/reject", headers=auth_headers["user"]
    ).status_code == 403
    rejected = client.post(
        f"/api/admin/bookings/{first['id']}/reject", headers=auth_headers["admin"]
    )
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "rejected"
    assert rejected.json()["seats"] == []
    assert db.scalar(select(func.count()).select_from(BookingSeat).where(
        BookingSeat.booking_id == first["id"]
    )) == 0
    assert client.post(
        f"/api/admin/bookings/{first['id']}/confirm", headers=auth_headers["admin"]
    ).status_code == 409


def test_qr_url_configured_and_missing(client, auth_headers, showtime, monkeypatch):
    from app import booking_rules

    monkeypatch.setattr(booking_rules, "BANK_ID", "970436")
    monkeypatch.setattr(booking_rules, "BANK_ACCOUNT", "123456789")
    monkeypatch.setattr(booking_rules, "BANK_ACCOUNT_NAME", "LE MINH TIN")
    booking = _create(client, auth_headers["user"], showtime).json()
    parsed = urlparse(booking["qr_url"])
    query = parse_qs(parsed.query)
    assert parsed.path.endswith("/970436-123456789-compact2.png")
    assert query["amount"] == [str(booking["total"])]
    assert query["addInfo"] == [booking["code"]]
    assert query["accountName"] == ["LE MINH TIN"]

    monkeypatch.setattr(booking_rules, "BANK_ACCOUNT", "")
    assert client.get("/api/bookings/me", headers=auth_headers["user"]).json()[0]["qr_url"] is None


def test_delete_movie_ignores_expired_or_rejected_bookings(
    client, auth_headers, showtime, movie, db
):
    booking = _create(client, auth_headers["user"], showtime).json()
    row = db.get(Booking, booking["id"])
    row.status = "rejected"
    for seat in list(row.seats):
        db.delete(seat)
    db.commit()
    response = client.delete(f"/api/admin/movies/{movie.id}", headers=auth_headers["admin"])
    assert response.status_code == 200
