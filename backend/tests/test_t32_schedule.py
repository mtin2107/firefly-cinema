from datetime import datetime, timedelta

from app.models import Showtime
from app.routers import movies


def test_schedule_is_public_filters_cutoff_and_date(client, db, movie, monkeypatch):
    now = datetime(2026, 11, 12, 18, 0)

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return now

    monkeypatch.setattr(movies, "datetime", Clock)
    rows = [
        Showtime(movie_id=movie.id, start_time=now + timedelta(minutes=10), room="Phòng 1", price=75_000),
        Showtime(movie_id=movie.id, start_time=now + timedelta(hours=3), room="Phòng 2", price=95_000),
        Showtime(movie_id=movie.id, start_time=now + timedelta(days=1), room="Phòng 1", price=75_000),
    ]
    db.add_all(rows)
    db.commit()

    everything = client.get("/api/showtimes")
    assert everything.status_code == 200
    body = everything.json()
    assert [s["id"] for s in body] == [rows[1].id, rows[2].id]  # suất trong mốc chặn 30 phút bị bỏ
    assert body[0]["movie"]["id"] == movie.id and body[0]["price"] == 95_000

    today = client.get("/api/showtimes", params={"date": "2026-11-12"}).json()
    assert [s["id"] for s in today] == [rows[1].id]
    tomorrow = client.get("/api/showtimes", params={"date": "2026-11-13"}).json()
    assert [s["id"] for s in tomorrow] == [rows[2].id]
    assert client.get("/api/showtimes", params={"date": "2026-11-20"}).json() == []


def test_schedule_rejects_bad_date_in_vietnamese(client):
    response = client.get("/api/showtimes", params={"date": "13-11-2026"})
    assert response.status_code == 422
    assert response.json()["detail"].startswith("Trường 'date' không hợp lệ")


def test_showtime_detail_route_still_works(client, showtime):
    assert client.get(f"/api/showtimes/{showtime.id}").status_code == 200
