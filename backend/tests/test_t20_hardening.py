import os
import subprocess
import sys
from datetime import datetime, timedelta

import jwt
import pytest

from app import chat_assistant
from app.models import Booking, BookingSeat, Movie, Showtime, User
from app.security import verify_password


@pytest.mark.parametrize("secret", ["", "doi-chuoi-bi-mat-nay", "qua-ngan"])
def test_backend_rejects_weak_secret_key(secret):
    env = os.environ.copy()
    env["SECRET_KEY"] = secret
    env["PYTHONUTF8"] = "1"
    result = subprocess.run(
        [sys.executable, "-c", "import app.config"],
        cwd=os.path.dirname(os.path.dirname(__file__)), env=env,
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "SECRET_KEY" in result.stderr
    assert "32" in result.stderr


def test_token_signed_with_old_default_is_rejected(client, users):
    token = jwt.encode({"sub": str(users[0].id)}, "doi-chuoi-bi-mat-nay", algorithm="HS256")
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_login_sixth_failure_is_limited_and_correct_login_works_after_window(
    client, users, monkeypatch
):
    from app import rate_limit

    clock = [1000.0]
    monkeypatch.setattr(rate_limit.time, "monotonic", lambda: clock[0])
    payload = {"email": users[0].email, "password": "sai-mat-khau"}
    for _ in range(5):
        assert client.post("/api/auth/login", json=payload).status_code == 401
    limited = client.post("/api/auth/login", json=payload)
    assert limited.status_code == 429
    assert limited.json()["detail"] == "Bạn đăng nhập sai quá nhiều lần. Hãy thử lại sau 5 phút."
    clock[0] += 301
    payload["password"] = "secret1"
    assert client.post("/api/auth/login", json=payload).status_code == 200


def test_correct_password_is_blocked_during_login_lock_window(
    client, users, monkeypatch
):
    from app import rate_limit

    clock = [2000.0]
    monkeypatch.setattr(rate_limit.time, "monotonic", lambda: clock[0])
    payload = {"email": users[0].email, "password": "sai-mat-khau"}
    for _ in range(5):
        assert client.post("/api/auth/login", json=payload).status_code == 401

    payload["password"] = "secret1"
    blocked = client.post("/api/auth/login", json=payload)
    assert blocked.status_code == 429
    assert blocked.json()["detail"] == (
        "Bạn đăng nhập sai quá nhiều lần. Hãy thử lại sau 5 phút."
    )

    clock[0] += 301
    assert client.post("/api/auth/login", json=payload).status_code == 200


def test_seed_uses_admin_password_from_environment(db, monkeypatch, fake_classifier):
    from app import seed as seed_module

    monkeypatch.setattr(seed_module, "ADMIN_PASSWORD", "mat-khau-admin-rieng")
    seed_module.seed(db)
    admin = db.query(User).filter(User.email == "admin@firefly.vn").one()
    assert verify_password("mat-khau-admin-rieng", admin.password_hash)


def test_hold_expiry_uses_fifteen_minutes_and_showtime_cutoff(
    client, auth_headers, showtime, db
):
    first = client.post("/api/bookings", headers=auth_headers["user"], json={
        "showtime_id": showtime.id, "seats": ["A1"],
    }).json()
    assert datetime.fromisoformat(first["hold_expires_at"]) == datetime.fromisoformat(
        first["created_at"]
    ) + timedelta(minutes=15)

    near = Showtime(movie_id=showtime.movie_id, start_time=datetime.now() + timedelta(minutes=40),
                    room="Phòng 2", price=80_000)
    db.add(near)
    db.commit()
    second = client.post("/api/bookings", headers=auth_headers["user"], json={
        "showtime_id": near.id, "seats": ["A2"],
    }).json()
    assert datetime.fromisoformat(second["hold_expires_at"]) == near.start_time - timedelta(minutes=30)


def test_expired_fifteen_minute_hold_releases_seat(client, auth_headers, showtime, db):
    created = client.post("/api/bookings", headers=auth_headers["user"], json={
        "showtime_id": showtime.id, "seats": ["A1"],
    }).json()
    booking = db.get(Booking, created["id"])
    booking.created_at = datetime.now() - timedelta(minutes=16)
    db.commit()
    client.get(f"/api/showtimes/{showtime.id}")
    assert booking.status == "expired"
    assert db.query(BookingSeat).filter(BookingSeat.booking_id == booking.id).count() == 0


def test_third_held_booking_is_blocked(client, auth_headers, showtime, db):
    extra = [
        Showtime(movie_id=showtime.movie_id, start_time=showtime.start_time + timedelta(hours=i),
                 room=f"Phòng {i + 1}", price=80_000)
        for i in (1, 2)
    ]
    db.add_all(extra)
    db.commit()
    for index, row in enumerate([showtime, extra[0]]):
        assert client.post("/api/bookings", headers=auth_headers["user"], json={
            "showtime_id": row.id, "seats": [f"A{index + 1}"],
        }).status_code == 201
    blocked = client.post("/api/bookings", headers=auth_headers["user"], json={
        "showtime_id": extra[1].id, "seats": ["A3"],
    })
    assert blocked.status_code == 409
    assert blocked.json()["detail"] == "Bạn đang giữ 2 vé chưa thanh toán. Hãy thanh toán hoặc chờ vé hết hạn."


def test_transfer_claim_requires_qr_configuration(client, auth_headers, showtime, monkeypatch):
    from app import booking_rules

    monkeypatch.setattr(booking_rules, "BANK_ACCOUNT", "")
    booking = client.post("/api/bookings", headers=auth_headers["user"], json={
        "showtime_id": showtime.id, "seats": ["A1"],
    }).json()
    response = client.post(
        f"/api/bookings/{booking['id']}/transfer-claim", headers=auth_headers["user"]
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Rạp chưa bật thanh toán chuyển khoản."


def test_fourth_comment_is_limited_before_classifier(client, auth_headers, movie, monkeypatch):
    from app.routers import comments

    calls = []

    class CountingClassifier:
        name = "counting"
        version = "test"

        def predict(self, text):
            calls.append(text)
            return False, 0.1

    monkeypatch.setattr(comments, "classifier", CountingClassifier())
    for index in range(3):
        assert client.post(f"/api/movies/{movie.id}/comments", headers=auth_headers["user"],
                           json={"content": f"Bình luận {index}"}).status_code == 201
    limited = client.post(f"/api/movies/{movie.id}/comments", headers=auth_headers["user"],
                          json={"content": "Bình luận thứ tư"})
    assert limited.status_code == 429
    assert limited.json()["detail"] == "Bạn bình luận quá nhanh. Hãy thử lại sau ít phút."
    assert len(calls) == 3


@pytest.mark.parametrize("genre", ["Hài hước", "hài hước", "hai huoc", "Hài"])
def test_chat_genre_search_is_accent_and_case_insensitive(db, genre):
    movie = Movie(
        title="Thứ Bảy Không Ngủ", genre="Hài hước", duration_min=100,
        age_rating="T13", release_date="2026-10-01", status="now_showing",
        director="", cast="", score=0, description="", poster_bg="#112233",
        poster_fg="#ffffff", country="Việt Nam", formats="Phụ đề",
    )
    db.add(movie)
    db.commit()
    assert "Thứ Bảy Không Ngủ" in [row["title"] for row in chat_assistant.search_movies(
        db, genre=genre, status="now_showing"
    )]
