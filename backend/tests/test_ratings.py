"""T22: API contracts, anonymity, ownership, aggregates and DB constraints."""
import pytest
from sqlalchemy import select, func, event
from sqlalchemy.exc import IntegrityError
from app.models import Rating, Movie
from app.routers.ratings import _rating_limits


@pytest.fixture(autouse=True)
def clear_rating_limit():
    _rating_limits.clear_all()
    yield
    _rating_limits.clear_all()


def test_rating_lifecycle(client, db, movie, auth_headers):
    path = f"/api/movies/{movie.id}"
    headers = auth_headers["user"]
    assert client.get(path + "/my-rating", headers=headers).json() == {"stars": None}
    assert client.put(path + "/rating", headers=headers, json={"stars": 3}).json() == {
        "stars": 3, "rating_avg": 3.0, "rating_count": 1}
    assert client.put(path + "/rating", headers=headers, json={"stars": 5}).json()["rating_count"] == 1
    assert client.get(path + "/my-rating", headers=headers).json() == {"stars": 5}
    row = db.scalar(select(Rating))
    assert row.stars == 5 and row.updated_at >= row.created_at
    assert client.put(path + "/rating", headers=auth_headers["admin"], json={"stars": 4}).json() == {
        "stars": 4, "rating_avg": 4.5, "rating_count": 2}
    db.expire_all()
    assert client.get(path).json()["rating_avg"] == 4.5
    assert client.get("/api/movies?collection=top_rated").json()[0]["id"] == movie.id
    assert client.delete(path + "/rating", headers=headers).json() == {
        "stars": None, "rating_avg": 4.0, "rating_count": 1}
    assert client.delete(path + "/rating", headers=headers).status_code == 200
    client.delete(path + "/rating", headers=auth_headers["admin"])
    db.expire_all()
    assert client.get(path).json()["rating_count"] == 0
    assert client.get("/api/movies?collection=top_rated").json() == []


@pytest.mark.parametrize("stars", [0, 6, -1, 2.5, True, "4", None])
def test_invalid_stars(client, movie, auth_headers, stars):
    assert client.put(f"/api/movies/{movie.id}/rating", headers=auth_headers["user"],
                      json={"stars": stars}).status_code == 422


def test_auth_missing_movies_and_coming_soon(client, db, movie, auth_headers):
    path = f"/api/movies/{movie.id}"
    for method, suffix in [("get", "/my-rating"), ("put", "/rating"), ("delete", "/rating")]:
        kwargs = {"json": {"stars": 4}} if method == "put" else {}
        assert getattr(client, method)(path + suffix, **kwargs).status_code == 401
        assert getattr(client, method)("/api/movies/99999" + suffix,
                                        headers=auth_headers["user"], **kwargs).status_code == 404
    movie.status = "coming_soon"
    db.commit()
    for method, suffix, payload in [("put", "/rating", {"stars": 3}),
                                    ("post", "/comments", {"content": "Phim hay"})]:
        response = getattr(client, method)(path + suffix, headers=auth_headers["user"], json=payload)
        assert response.status_code == 400 and "sắp chiếu" in response.json()["detail"]
    assert client.delete(path + "/rating", headers=auth_headers["user"]).status_code == 400
    movie.status = "ended"
    db.commit()
    assert client.put(path + "/rating", headers=auth_headers["user"], json={"stars": 5}).status_code == 200
    assert client.post(path + "/comments", headers=auth_headers["user"], json={"content": "Phim hay"}).status_code == 201


def test_anonymous_comments_rating_and_delete(client, db, movie, users, auth_headers):
    path = f"/api/movies/{movie.id}"
    headers = auth_headers["user"]
    client.put(path + "/rating", headers=headers, json={"stars": 3})
    created = client.post(path + "/comments", headers=headers, json={
        "content": "Ko hay như quảng cáo, hơi thất vọng", "is_anonymous": True, "stars": 5})
    assert created.status_code == 201
    comment = created.json()
    assert comment["author_stars"] == 5 and comment["can_delete"]
    assert comment["effective_negative"]
    assert db.scalar(select(func.count()).select_from(Rating)) == 1
    public = client.get(path + "/comments").json()[0]
    assert public["user_name"] == "Khán giả ẩn danh" and public["is_anonymous"]
    assert not public["can_delete"]
    assert not {"user_id", "email"} & public.keys()
    assert users[0].full_name not in str(public) and users[0].email not in str(public)
    admin = client.get("/api/admin/comments", headers=auth_headers["admin"]).json()["items"][0]
    assert admin["user_name"] == users[0].full_name and admin["is_anonymous"]
    client.put(path + "/rating", headers=headers, json={"stars": 2})
    db.expire_all()
    assert client.get(path + "/comments").json()[0]["author_stars"] == 2
    client.delete(path + "/rating", headers=headers)
    db.expire_all()
    assert client.get(path + "/comments").json()[0]["author_stars"] is None
    delete_path = f"/api/comments/{comment['id']}"
    assert client.delete(delete_path).status_code == 401
    assert client.delete(delete_path, headers=auth_headers["admin"]).status_code == 404
    assert client.delete(delete_path, headers=headers).json() == {"ok": True}
    assert client.delete(delete_path, headers=headers).status_code == 404


def test_database_constraints(db, movie, users):
    db.add(Rating(movie_id=movie.id, user_id=users[0].id, stars=5))
    db.commit()
    db.add(Rating(movie_id=movie.id, user_id=users[0].id, stars=4))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
    db.add(Rating(movie_id=movie.id, user_id=users[1].id, stars=6))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_rating_limit(client, movie, auth_headers):
    path = f"/api/movies/{movie.id}/rating"
    for _ in range(20):
        assert client.put(path, headers=auth_headers["user"], json={"stars": 4}).status_code == 200
    assert client.delete(path, headers=auth_headers["user"]).status_code == 429


def test_movie_list_aggregates_one_query(client, db, movie, users):
    db.add(Rating(movie_id=movie.id, user_id=users[0].id, stars=4))
    db.commit()
    for index in range(3):
        values = {column.name: getattr(movie, column.name) for column in Movie.__table__.columns if column.name != "id"}
        values["title"] = f"Other movie {index}"
        db.add(Movie(**values))
    db.commit()
    statements = []
    def record(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)
    event.listen(db.get_bind(), "before_cursor_execute", record)
    try:
        data = client.get("/api/movies").json()
    finally:
        event.remove(db.get_bind(), "before_cursor_execute", record)
    assert len(statements) == 1
    assert len(data) == 4
    rated = next(item for item in data if item["id"] == movie.id)
    assert rated["rating_avg"] == 4.0 and rated["rating_count"] == 1
    assert all(item["rating_count"] == 0 for item in data if item["id"] != movie.id)


def test_deleting_rated_movie_cleans_ratings(client, db, movie, users, auth_headers):
    db.add(Rating(movie_id=movie.id, user_id=users[0].id, stars=4))
    db.commit()
    assert client.delete(f"/api/admin/movies/{movie.id}", headers=auth_headers["admin"]).status_code == 200
    assert db.scalar(select(func.count()).select_from(Rating)) == 0


def test_seed_ratings_deterministic_and_restart_preserves_removal(db, fake_classifier, monkeypatch):
    from app import seed as seed_module
    monkeypatch.setattr(seed_module, "classifier", fake_classifier)
    seed_module.seed(db)
    rows = db.scalars(select(Rating).order_by(Rating.movie_id, Rating.user_id)).all()
    from app.models import User, Comment
    viewers = db.scalars(select(User).where(User.email.like("khan-gia-%@firefly.vn")).order_by(User.id)).all()
    assert len(viewers) == 6
    assert all(viewer.role == "user" and viewer.password_hash for viewer in viewers)
    assert len({viewer.password_hash for viewer in viewers}) == 6
    counts = []
    for movie in db.scalars(select(Movie).order_by(Movie.id)).all():
        ratings = [row for row in rows if row.movie_id == movie.id]
        if movie.status == "coming_soon":
            assert ratings == []
            continue
        counts.append(len(ratings))
        assert len(ratings) == 2 + movie.id % 5
        for index, row in enumerate(ratings):
            assert row.user_id == viewers[index].id
            assert row.stars == 3 + ((movie.id + index) % 3)
    assert len(set(counts)) > 1
    excluded = db.scalars(select(User.id).where(User.email.in_(("admin@firefly.vn", "demo@firefly.vn")))).all()
    assert all(row.user_id not in excluded for row in rows)
    comments = db.scalars(select(Comment)).all()
    assert len(comments) == 30 and all(comment.author_stars is None for comment in comments)
    removed_id = rows[0].id
    db.delete(rows[0])
    db.commit()
    seed_module.seed(db)
    assert db.get(Rating, removed_id) is None
    assert db.scalar(select(func.count()).select_from(Rating)) == len(rows) - 1


def test_rounding_consistent_in_rating_movie_and_list(client, db, movie, users, auth_headers):
    from app.models import User
    extra = [User(full_name=f"Viewer {i}", email=f"viewer{i}@test.vn", password_hash="unused") for i in range(2)]
    db.add_all(extra)
    db.flush()
    for user in [*users, extra[0]]:
        db.add(Rating(movie_id=movie.id, user_id=user.id, stars=4))
    db.add(Rating(movie_id=movie.id, user_id=extra[1].id, stars=5))
    db.commit()
    result = client.put(f"/api/movies/{movie.id}/rating", headers=auth_headers["user"], json={"stars": 4}).json()
    db.expire_all()
    assert result["rating_avg"] == client.get(f"/api/movies/{movie.id}").json()["rating_avg"] == client.get("/api/movies").json()[0]["rating_avg"] == 4.3


def test_nested_showtime_and_booking_movie_ratings(client, db, showtime, users, auth_headers):
    db.add(Rating(movie_id=showtime.movie_id, user_id=users[0].id, stars=5))
    db.commit()
    db.expire_all()
    data = client.get(f"/api/showtimes/{showtime.id}").json()
    assert data["movie"]["rating_avg"] == 5.0 and data["movie"]["rating_count"] == 1
    booking = client.post("/api/bookings", headers=auth_headers["user"],
                          json={"showtime_id": showtime.id, "seats": ["A1", "A2"]})
    assert booking.status_code == 201
    assert booking.json()["movie"]["rating_avg"] == 5.0
    assert client.get("/api/bookings/me", headers=auth_headers["user"]).json()[0]["movie"]["rating_count"] == 1


@pytest.mark.parametrize("token_kind", ["malformed", "expired"])
def test_public_comments_invalid_token_is_guest(client, db, movie, users, auth_headers, token_kind):
    from datetime import datetime, timedelta, timezone
    import jwt
    from app.config import SECRET_KEY
    created = client.post(f"/api/movies/{movie.id}/comments", headers=auth_headers["user"],
                          json={"content": "Bình luận của tôi", "is_anonymous": True})
    assert created.status_code == 201
    token = "not-a-valid-token" if token_kind == "malformed" else jwt.encode(
        {"sub": str(users[0].id), "exp": datetime.now(timezone.utc) - timedelta(seconds=10)},
        SECRET_KEY, algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    result = client.get(f"/api/movies/{movie.id}/comments", headers=headers)
    assert result.status_code == 200
    assert result.json()[0]["can_delete"] is False
    assert result.json()[0]["user_name"] == "Khán giả ẩn danh"
    assert client.get(f"/api/movies/{movie.id}/my-rating", headers=headers).status_code == 401
    assert client.delete(f"/api/comments/{created.json()['id']}", headers=headers).status_code == 401


def test_comment_without_stars_preserves_existing_rating(client, db, movie, auth_headers):
    headers = auth_headers["user"]
    path = f"/api/movies/{movie.id}"
    client.put(path + "/rating", headers=headers, json={"stars": 2})
    created = client.post(path + "/comments", headers=headers, json={"content": "Không gửi sao mới"})
    assert created.status_code == 201 and created.json()["author_stars"] == 2
    assert client.get(path + "/my-rating", headers=headers).json() == {"stars": 2}
    assert db.scalar(select(func.count()).select_from(Rating)) == 1
