"""T30 regressions; temporary SQLite and upload paths only."""
import base64
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Barrier

import pytest
from sqlalchemy import event, select, text
from sqlalchemy.orm import Session

from app.database import get_db
from app.main import app
from app.models import Booking, Comment, Rating, Showtime, User


@pytest.mark.parametrize("status", ["expired", "rejected"])
def test_bug01_delete_preserves_tickets(client, db, users, showtime, auth_headers, status):
    b = Booking(user_id=users[0].id, showtime_id=showtime.id, total=80000, status=status)
    db.add(b)
    db.commit()
    response = client.delete(f"/api/admin/movies/{showtime.movie_id}", headers=auth_headers["admin"])
    assert response.status_code == 409
    assert response.json()["detail"] == "Phim đã có vé, không xóa được. Hãy chuyển trạng thái sang Đã chiếu xong."
    assert client.get("/api/bookings/me", headers=auth_headers["user"]).status_code == 200
    for value in ["", "held", "pending_verify", "paid", "expired", "rejected"]:
        assert client.get("/api/admin/bookings" + (f"?status={value}" if value else ""), headers=auth_headers["admin"]).status_code == 200
    assert client.get(f"/api/admin/checkin/FF{b.id:05d}", headers=auth_headers["admin"]).status_code == 200
    assert db.scalar(text("SELECT COUNT(*) FROM bookings b LEFT JOIN showtimes s ON s.id=b.showtime_id WHERE s.id IS NULL")) == 0


def test_bug01_delete_without_tickets(client, db, users, showtime, auth_headers):
    mid = showtime.movie_id
    db.add(Comment(movie_id=mid, user_id=users[0].id, content="Thử", is_negative=False, negative_score=0.1, model_name="fake"))
    db.commit()
    assert client.delete(f"/api/admin/movies/{mid}", headers=auth_headers["admin"]).status_code == 200
    assert not db.scalars(select(Showtime)).all()
    assert not db.scalars(select(Comment)).all()


def test_bug02_code_never_reused(client, db, showtime, auth_headers):
    body = {"showtime_id": showtime.id, "seats": ["A1"]}
    first = client.post("/api/bookings", headers=auth_headers["user"], json=body)
    assert first.status_code == 201
    assert client.delete(f"/api/bookings/{first.json()['id']}", headers=auth_headers["user"]).status_code == 200
    second = client.post("/api/bookings", headers=auth_headers["admin"], json=body)
    assert second.status_code == 201
    assert second.json()["code"] > first.json()["code"]
    assert "AUTOINCREMENT" in db.scalar(text("SELECT sql FROM sqlite_master WHERE name='bookings'"))


@pytest.mark.parametrize("attempt", range(5))
def test_bug03_concurrent_hold_limit(client, db, users, showtime, auth_headers, attempt):
    engine = db.get_bind()
    rows = [Showtime(movie_id=showtime.movie_id, start_time=datetime.now()+timedelta(days=3), room=f"R{i}", price=80000) for i in range(4)]
    db.add_all(rows)
    db.commit()
    ids = [r.id for r in rows]
    barrier = Barrier(4)

    def sessions():
        with Session(engine) as session:
            yield session

    # Enlarge the real count/insert race window without changing the result.
    def slow_count(conn, cursor, statement, parameters, context, many):
        if statement.startswith("SELECT bookings.id") and "bookings.status" in statement and "LIMIT" not in statement:
            time.sleep(0.15)

    app.dependency_overrides[get_db] = sessions
    event.listen(engine, "after_cursor_execute", slow_count)
    try:
        def request(sid):
            barrier.wait(timeout=10)
            return client.post("/api/bookings", headers=auth_headers["user"], json={"showtime_id": sid, "seats": ["A1"]})
        with ThreadPoolExecutor(max_workers=4) as pool:
            responses = list(pool.map(request, ids))
        assert sorted(r.status_code for r in responses) == [201, 201, 409, 409]
        assert all(r.json()["detail"].startswith("Bạn đang giữ 2 vé chưa thanh toán") for r in responses if r.status_code == 409)
        db.expire_all()
        assert len(db.scalars(select(Booking).where(Booking.status == "held")).all()) == 2
    finally:
        event.remove(engine, "after_cursor_execute", slow_count)


@pytest.mark.parametrize("score,expected", [(4.5, False), (7.99, False), (8.0, True), (10, True)])
def test_bug04_top_rated_boundary(client, db, movie, users, score, expected):
    count = 100 if score == 7.99 else 2
    for i in range(count):
        user = User(full_name="R", email=f"rating{i}@example.com", password_hash="unused", role="user")
        db.add(user)
        db.flush()
        stars = (7 if i == 0 else 8) if score == 7.99 else (4+i if score == 4.5 else int(score))
        db.add(Rating(movie_id=movie.id, user_id=user.id, stars=stars))
    db.commit()
    rows = client.get("/api/movies?collection=top_rated").json()
    assert (movie.id in [r["id"] for r in rows]) is expected


def test_concurrent_same_seat_only_one_winner(client, db, showtime, auth_headers):
    engine = db.get_bind()
    sid = showtime.id
    barrier = Barrier(2)
    def sessions():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_db] = sessions
    def reserve(role):
        barrier.wait(timeout=10)
        return client.post("/api/bookings", headers=auth_headers[role], json={"showtime_id": sid, "seats": ["B1"]}).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(reserve, ["user", "admin"])) == [201, 409]


@pytest.mark.parametrize("raw", [bytes.fromhex("89504e470d0a1a0a0000000d49484452")+bytes(15), b"\xff\xd8\xff"+bytes(20), b"RIFF\x20\x00\x00\x00WEBP"+bytes(20)])
@pytest.mark.parametrize("avatar", [False, True])
def test_bug05_corrupt_image_rejected(client, auth_headers, tmp_path, monkeypatch, raw, avatar):
    from app.routers import auth, admin_posters
    folder = tmp_path / "uploads"
    monkeypatch.setattr(auth, "UPLOAD_DIR", folder)
    monkeypatch.setattr(admin_posters, "UPLOAD_DIR", folder)
    payload = {"filename": "image.png", "data": base64.b64encode(raw).decode()}
    response = client.put("/api/auth/me/avatar", headers=auth_headers["user"], json=payload) if avatar else client.post("/api/admin/posters", headers=auth_headers["admin"], json=payload)
    assert response.status_code == 422
    assert response.json()["detail"] == "Ảnh bị hỏng hoặc không đầy đủ."
    assert not folder.exists()
