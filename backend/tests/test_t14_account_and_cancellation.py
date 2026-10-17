from datetime import datetime, timedelta

import pytest
from sqlalchemy import func, select

from app.models import Booking, BookingSeat, User
from app.security import verify_password


def _booking(db, showtime, user, status, seat):
    booking = Booking(
        user_id=user.id,
        showtime_id=showtime.id,
        total=showtime.price,
        status=status,
        created_at=datetime.now(),
    )
    booking.seats = [BookingSeat(showtime_id=showtime.id, seat_code=seat)]
    db.add(booking)
    db.commit()
    return booking


def test_cancel_held_booking_deletes_booking_and_releases_seat(
    client, auth_headers, showtime, users, db
):
    created = client.post(
        "/api/bookings",
        headers=auth_headers["user"],
        json={"showtime_id": showtime.id, "seats": ["A1"]},
    ).json()

    response = client.delete(
        f"/api/bookings/{created['id']}", headers=auth_headers["user"]
    )

    assert response.status_code == 200
    assert response.json() == {"detail": "Đã hủy vé."}
    assert db.get(Booking, created["id"]) is None
    assert db.scalar(select(func.count()).select_from(BookingSeat).where(
        BookingSeat.booking_id == created["id"]
    )) == 0
    detail = client.get(f"/api/showtimes/{showtime.id}").json()
    assert "A1" not in detail["booked_seats"]


def test_cancel_other_users_booking_and_missing_booking_are_hidden(
    client, auth_headers, showtime, users, db
):
    booking = _booking(db, showtime, users[1], "held", "A2")

    other = client.delete(
        f"/api/bookings/{booking.id}", headers=auth_headers["user"]
    )
    missing = client.delete("/api/bookings/999999", headers=auth_headers["user"])

    assert other.status_code == missing.status_code == 404
    assert other.json() == missing.json() == {"detail": "Không tìm thấy vé."}
    assert db.get(Booking, booking.id) is not None


@pytest.mark.parametrize("status", ["paid", "pending_verify", "expired"])
def test_cancel_non_held_booking_returns_conflict(
    client, auth_headers, showtime, users, db, status
):
    booking = _booking(db, showtime, users[0], status, "A3")

    response = client.delete(
        f"/api/bookings/{booking.id}", headers=auth_headers["user"]
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Chỉ hủy được vé đang giữ chỗ chưa thanh toán."
    }
    assert db.get(Booking, booking.id) is not None


def test_cancel_expired_held_booking_returns_conflict_and_releases_seat(
    client, auth_headers, showtime, users, db
):
    booking = _booking(db, showtime, users[0], "held", "A4")
    booking.created_at = datetime.now() - timedelta(minutes=16)
    db.commit()

    response = client.delete(
        f"/api/bookings/{booking.id}", headers=auth_headers["user"]
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Chỉ hủy được vé đang giữ chỗ chưa thanh toán."
    }
    assert booking.status == "expired"
    assert db.scalar(select(func.count()).select_from(BookingSeat).where(
        BookingSeat.booking_id == booking.id
    )) == 0


def test_change_password_accepts_new_password_and_rejects_old_one(
    client, auth_headers, users
):
    response = client.post(
        "/api/auth/change-password",
        headers=auth_headers["user"],
        json={"current_password": "secret1", "new_password": "matkhau-moi"},
    )

    assert response.status_code == 200
    assert response.json() == {"detail": "Đã đổi mật khẩu."}
    assert client.post("/api/auth/login", json={
        "email": users[0].email, "password": "matkhau-moi",
    }).status_code == 200
    assert client.post("/api/auth/login", json={
        "email": users[0].email, "password": "secret1",
    }).status_code == 401
    assert client.get("/api/auth/me", headers=auth_headers["user"]).status_code == 200


def test_change_password_rejects_wrong_current_password(client, auth_headers):
    response = client.post(
        "/api/auth/change-password",
        headers=auth_headers["user"],
        json={"current_password": "sai-mat-khau", "new_password": "matkhau-moi"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Mật khẩu hiện tại không đúng."}


def test_change_password_blocks_correct_password_after_five_failures_without_changing_it(
    client, auth_headers, users, monkeypatch
):
    from app import rate_limit
    from app.routers import auth

    clock = [3000.0]
    monkeypatch.setattr(rate_limit.time, "monotonic", lambda: clock[0])
    original_verify = auth.verify_password
    verify_calls = []

    def counting_verify(password, stored):
        verify_calls.append(password)
        return original_verify(password, stored)

    monkeypatch.setattr(auth, "verify_password", counting_verify)
    payload = {"current_password": "sai-mat-khau", "new_password": "matkhau-moi"}
    for _ in range(5):
        assert client.post(
            "/api/auth/change-password", headers=auth_headers["user"], json=payload
        ).status_code == 400

    payload["current_password"] = "secret1"
    blocked = client.post(
        "/api/auth/change-password", headers=auth_headers["user"], json=payload
    )
    assert blocked.status_code == 429
    assert blocked.json() == {
        "detail": "Bạn nhập sai mật khẩu quá nhiều lần. Hãy thử lại sau 5 phút."
    }
    assert verify_calls == ["sai-mat-khau"] * 5
    assert verify_password("secret1", users[0].password_hash)
    assert not verify_password("matkhau-moi", users[0].password_hash)


def test_change_password_failures_share_counter_with_login(
    client, auth_headers, users, monkeypatch
):
    from app import rate_limit

    clock = [4000.0]
    monkeypatch.setattr(rate_limit.time, "monotonic", lambda: clock[0])
    payload = {"current_password": "sai-mat-khau", "new_password": "matkhau-moi"}
    for _ in range(5):
        assert client.post(
            "/api/auth/change-password", headers=auth_headers["user"], json=payload
        ).status_code == 400

    login = client.post(
        "/api/auth/login",
        json={"email": users[0].email.upper(), "password": "secret1"},
    )
    assert login.status_code == 429
    assert login.json() == {
        "detail": "Bạn đăng nhập sai quá nhiều lần. Hãy thử lại sau 5 phút."
    }


def test_successful_change_password_clears_shared_failure_counter(
    client, auth_headers, monkeypatch
):
    from app import rate_limit

    clock = [5000.0]
    monkeypatch.setattr(rate_limit.time, "monotonic", lambda: clock[0])
    wrong = {"current_password": "sai-mat-khau", "new_password": "matkhau-moi"}
    for _ in range(4):
        assert client.post(
            "/api/auth/change-password", headers=auth_headers["user"], json=wrong
        ).status_code == 400

    changed = client.post(
        "/api/auth/change-password",
        headers=auth_headers["user"],
        json={"current_password": "secret1", "new_password": "matkhau-moi"},
    )
    assert changed.status_code == 200

    after_clear = client.post(
        "/api/auth/change-password", headers=auth_headers["user"], json=wrong
    )
    assert after_clear.status_code == 400
    assert after_clear.json() == {"detail": "Mật khẩu hiện tại không đúng."}


def test_account_fields_keep_registration_length_limits(client, auth_headers):
    assert client.patch(
        "/api/auth/me", headers=auth_headers["user"], json={"full_name": " A "}
    ).status_code == 422
    assert client.patch(
        "/api/auth/me", headers=auth_headers["user"], json={"full_name": "A" * 101}
    ).status_code == 422
    assert client.post(
        "/api/auth/change-password",
        headers=auth_headers["user"],
        json={"current_password": "secret1", "new_password": "12345"},
    ).status_code == 422


def test_update_full_name_is_returned_and_persisted(client, auth_headers, users, db):
    response = client.patch(
        "/api/auth/me",
        headers=auth_headers["user"],
        json={"full_name": "  Lê Minh Tín  "},
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == "Lê Minh Tín"
    assert db.get(User, users[0].id).full_name == "Lê Minh Tín"
    assert client.get("/api/auth/me", headers=auth_headers["user"]).json()["full_name"] == "Lê Minh Tín"
