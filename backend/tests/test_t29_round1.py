import base64
from datetime import datetime

import pytest
from app.models import Booking, Comment


def test_avatar_rejects_large_body_before_parsing(client, auth_headers, tmp_path, monkeypatch):
    from app.routers import auth
    upload_dir = tmp_path / "uploads"
    monkeypatch.setattr(auth, "UPLOAD_DIR", upload_dir)

    def must_not_decode(*args, **kwargs):
        raise AssertionError("Body quá lớn không được giải mã/ghi ảnh")

    monkeypatch.setattr(auth, "validate_image", must_not_decode)
    # JSON không hợp lệ cũng phải bị chặn 413 trước khi đọc/parse body.
    response = client.put("/api/auth/me/avatar", headers={**auth_headers["user"], "Content-Type": "application/json"}, content=b" " * (3 * 1024 * 1024 + 1))
    assert response.status_code == 413
    assert response.json() == {"detail": "Ảnh đại diện tối đa 2 MB."}
    # Dưới giới hạn HTTP nhưng vượt độ dài chuỗi base64: schema chặn 422.
    limit = 4 * ((2 * 1024 * 1024 + 2) // 3)
    response = client.put("/api/auth/me/avatar", headers=auth_headers["user"], json={"filename": "large.png", "data": "A" * (limit + 1)})
    assert response.status_code == 422
    assert not upload_dir.exists()


def test_avatar_valid_after_body_guard(client, auth_headers, tmp_path, monkeypatch):
    from app.routers import auth
    monkeypatch.setattr(auth, "UPLOAD_DIR", tmp_path)
    image = b"\x89PNG\r\n\x1a\n"
    response = client.put("/api/auth/me/avatar", headers=auth_headers["user"], json={"filename": "small.png", "data": base64.b64encode(image).decode()})
    assert response.status_code == 200
    assert (tmp_path / "avatars" / response.json()["avatar_url"].rsplit("/", 1)[1]).read_bytes() == image


@pytest.mark.parametrize("payload", [[], None, "không phải object", {"filename": "x.png", "data": []}])
def test_avatar_invalid_json_shape_stays_422(client, auth_headers, tmp_path, monkeypatch, payload):
    from app.routers import auth
    folder = tmp_path / "uploads"
    monkeypatch.setattr(auth, "UPLOAD_DIR", folder)
    response = client.put("/api/auth/me/avatar", headers=auth_headers["user"], json=payload)
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], str)
    assert not folder.exists()


def test_avatar_rejects_non_json_media_type(client, auth_headers, tmp_path, monkeypatch):
    from app.routers import auth
    folder = tmp_path / "uploads"
    monkeypatch.setattr(auth, "UPLOAD_DIR", folder)
    response = client.put("/api/auth/me/avatar", headers={**auth_headers["user"], "Content-Type": "text/plain"}, content='{"filename":"x.png","data":"AA=="}')
    assert response.status_code == 422
    assert not folder.exists()


def test_public_comment_keys_match_before_t29(client, db, movie, users, auth_headers):
    comment = Comment(movie_id=movie.id, user_id=users[0].id, content="Bình luận đã duyệt", is_negative=True, negative_score=.9, model_name="fake", model_version="test", human_label=0, reviewed_by=users[1].id, reviewed_at=datetime.now())
    db.add(comment)
    db.commit()
    expected = {"is_anonymous", "author_stars", "can_delete", "id", "movie_id", "user_name", "content", "is_negative", "effective_negative", "reviewed", "negative_score", "created_at"}
    for headers in ({}, auth_headers["user"], auth_headers["admin"]):
        response = client.get(f"/api/movies/{movie.id}/comments", headers=headers)
        assert response.status_code == 200
        assert set(response.json()[0]) == expected
        assert response.json()[0]["is_negative"] is True
    account = client.get("/api/auth/me/summary", headers=auth_headers["user"]).json()["recent_comments"][0]
    assert account["human_label"] == 0 and account["reviewed_at"]
    admin = client.get("/api/admin/comments", headers=auth_headers["admin"]).json()["items"][0]
    assert admin["human_label"] == 0 and admin["reviewed_at"]


def test_admin_activity_contains_movie_titles(client, db, movie, users, showtime, auth_headers):
    now = datetime.now()
    db.add(Comment(movie_id=movie.id, user_id=users[0].id, content="Đã duyệt", is_negative=True, negative_score=.9, model_name="fake", model_version="test", human_label=0, reviewed_by=users[1].id, reviewed_at=now))
    db.add(Booking(user_id=users[0].id, showtime_id=showtime.id, total=80000, status="paid", checked_in_by=users[1].id, checked_in_at=now))
    db.commit()
    response = client.get("/api/admin/me/summary", headers=auth_headers["admin"])
    assert response.status_code == 200
    activities = response.json()["recent_activity"]
    assert {a["kind"] for a in activities} == {"review", "checkin"}
    assert all(a["movie_title"] == movie.title for a in activities)
    assert client.get("/api/admin/me/summary", headers=auth_headers["user"]).status_code == 403
