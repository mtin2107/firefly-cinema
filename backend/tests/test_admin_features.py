from datetime import timedelta

from app.models import Booking, BookingSeat


def test_movie_validation_uses_vietnamese_message(client, auth_headers, movie_payload):
    invalid = dict(movie_payload, duration_min="không-phải-số")
    response = client.post("/api/admin/movies", headers=auth_headers["admin"], json=invalid)
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert "không hợp lệ" in detail
    assert "valid integer" not in detail.lower()


def test_movie_with_booking_cannot_be_deleted(client, auth_headers, showtime, users, db):
    user, _ = users
    booking = Booking(user_id=user.id, showtime_id=showtime.id, total=showtime.price)
    booking.seats = [BookingSeat(showtime_id=showtime.id, seat_code="A1")]
    db.add(booking)
    db.commit()
    response = client.delete(f"/api/admin/movies/{showtime.movie_id}", headers=auth_headers["admin"])
    assert response.status_code == 409


def test_admin_movie_crud(client, auth_headers, movie_payload):
    created = client.post("/api/admin/movies", headers=auth_headers["admin"], json=movie_payload)
    assert created.status_code == 201
    movie_id = created.json()["id"]
    updated_payload = dict(movie_payload, title="Phim đã sửa")
    updated = client.put(f"/api/admin/movies/{movie_id}", headers=auth_headers["admin"],
                         json=updated_payload)
    assert updated.status_code == 200
    assert updated.json()["title"] == "Phim đã sửa"
    assert client.delete(f"/api/admin/movies/{movie_id}",
                         headers=auth_headers["admin"]).status_code == 200


def test_showtime_overlap_same_day_but_not_different_day(client, auth_headers, showtime):
    overlap = {
        "movie_id": showtime.movie_id,
        "start_time": (showtime.start_time + timedelta(minutes=30)).isoformat(),
        "room": showtime.room,
        "price": showtime.price,
    }
    assert client.post("/api/admin/showtimes", headers=auth_headers["admin"], json=overlap).status_code == 409
    next_day = dict(overlap, start_time=(showtime.start_time + timedelta(days=1)).isoformat())
    assert client.post("/api/admin/showtimes", headers=auth_headers["admin"], json=next_day).status_code == 201


def test_showtime_with_ticket_cannot_be_updated_or_deleted(
    client, auth_headers, showtime, users, db
):
    user, _ = users
    booking = Booking(user_id=user.id, showtime_id=showtime.id, total=showtime.price)
    booking.seats = [BookingSeat(showtime_id=showtime.id, seat_code="B1")]
    db.add(booking)
    db.commit()
    payload = {
        "movie_id": showtime.movie_id,
        "start_time": (showtime.start_time + timedelta(hours=4)).isoformat(),
        "room": "Phòng 2",
        "price": showtime.price,
    }
    assert client.put(f"/api/admin/showtimes/{showtime.id}", headers=auth_headers["admin"],
                      json=payload).status_code == 409
    assert client.delete(f"/api/admin/showtimes/{showtime.id}",
                         headers=auth_headers["admin"]).status_code == 409


def test_predict_isolates_each_model_failure(client, auth_headers, fake_classifier):
    from tests.conftest import FakeModel

    fake_classifier.models = [
        FakeModel("broken", error=ValueError("private C:\\models\\broken")),
        FakeModel("healthy", result=(False, 0.12)),
    ]
    response = client.post("/api/admin/predict", headers=auth_headers["admin"], json={"text": "phim ổn"})
    assert response.status_code == 200
    assert [item["model"] for item in response.json()] == ["healthy"]
