from datetime import date, timedelta

import pytest

from app import taxonomy
from app.chat_assistant import search_movies
from app.models import Movie


@pytest.mark.parametrize("offset,expected", [(-1, "now_showing"), (0, "now_showing"), (1, "coming_soon")])
def test_effective_status_all_consumers(client, db, movie, auth_headers, monkeypatch, offset, expected):
    class FrozenDate(date):
        @classmethod
        def today(cls):
            return cls(2030, 6, 15)
    # The helper imports date at call time; pin its date dependency without changing global datetime.
    real = taxonomy.effective_status
    monkeypatch.setattr(taxonomy, "effective_status", lambda m=None, today=None, **kw: real(m, today or FrozenDate.today(), **kw))
    from app.routers import movies, ratings, admin_movies
    from app import chat_assistant
    for module in (movies, ratings, admin_movies, chat_assistant):
        monkeypatch.setattr(module, "effective_status", taxonomy.effective_status)
    movie.status = "coming_soon"
    movie.release_date = (FrozenDate.today() + timedelta(days=offset)).isoformat()
    db.commit()
    assert client.get(f"/api/movies/{movie.id}").json()["status"] == expected
    assert client.get("/api/movies").json()[0]["status"] == expected
    assert [m["id"] for m in client.get("/api/movies", params={"status": expected}).json()] == [movie.id]
    other = "coming_soon" if expected == "now_showing" else "now_showing"
    assert client.get("/api/movies", params={"status": other}).json() == []
    assert search_movies(db, status=expected)[0]["status"] == expected
    assert search_movies(db, status=other) == []
    response = client.put(f"/api/movies/{movie.id}/rating", json={"stars": 8}, headers=auth_headers["user"])
    assert response.status_code == (400 if expected == "coming_soon" else 200)
    db.refresh(movie)
    assert movie.status == "coming_soon"


def test_admin_rejects_due_coming_soon(client, movie_payload, auth_headers):
    movie_payload.update(status="coming_soon", release_date=date.today().isoformat())
    response = client.post("/api/admin/movies", json=movie_payload, headers=auth_headers["admin"])
    assert response.status_code == 422
    assert response.json()["detail"] == "Phim sắp chiếu phải có ngày khởi chiếu sau hôm nay."
    movie_payload.update(release_date=(date.today() + timedelta(days=1)).isoformat(), poster_url=None)
    assert client.post("/api/admin/movies", json=movie_payload, headers=auth_headers["admin"]).status_code == 201


@pytest.mark.parametrize("status", ["now_showing", "ended"])
def test_other_statuses_stay(status):
    assert taxonomy.effective_status({"status": status, "release_date": "2099-01-01"}) == status
