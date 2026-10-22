from datetime import datetime, timedelta

import pytest

from app.routers import bookings, movies


@pytest.mark.parametrize("minutes,bookable", [(-1, False), (0, False), (29, False), (30, False), (31, True)])
def test_online_cutoff(client, db, movie, showtime, auth_headers, monkeypatch, minutes, bookable):
    now = datetime(2026, 10, 22, 18, 0)

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return now

    monkeypatch.setattr(movies, "datetime", Clock)
    monkeypatch.setattr(bookings, "datetime", Clock)
    showtime.start_time = now + timedelta(minutes=minutes)
    db.commit()

    response = client.get(f"/api/movies/{movie.id}/showtimes")
    assert response.status_code == 200
    assert [s["id"] for s in response.json()] == ([showtime.id] if bookable else [])
    detail = client.get(f"/api/showtimes/{showtime.id}")
    assert detail.status_code == 200
    assert detail.json()["bookable"] is bookable
    result = client.post("/api/bookings", headers=auth_headers["user"],
                         json={"showtime_id": showtime.id, "seats": ["A1"]})
    if bookable:
        assert result.status_code == 201
    else:
        assert result.status_code == 400
        assert result.json()["detail"] == (
            "Suất chiếu đã bắt đầu, không thể đặt vé." if minutes <= 0 else
            "Suất chiếu sắp bắt đầu, vui lòng mua vé tại quầy."
        )


def test_nonexistent_showtime_and_movie(client):
    assert client.get("/api/movies/9999/showtimes").status_code == 404
    assert client.get("/api/showtimes/999999").status_code == 404
