"""T19: upload poster với SQLite và thư mục upload tạm, không dùng DB thật."""
import base64
import re

import pytest

from app.main import app
from app.routers import admin_posters


JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 30
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 30
WEBP = b"RIFF\x20\x00\x00\x00WEBP" + b"\x00" * 30
POSTER_MESSAGE = "Hãy chọn ảnh poster hoặc dán đường dẫn poster."


@pytest.fixture
def posters_dir(tmp_path, monkeypatch):
    """Làm cả endpoint và StaticFiles dùng chung thư mục tạm."""
    monkeypatch.setattr(admin_posters, "UPLOAD_DIR", tmp_path)
    mount = next(route for route in app.routes if getattr(route, "path", "") == "/uploads")
    monkeypatch.setattr(mount.app, "directory", str(tmp_path))
    monkeypatch.setattr(mount.app, "all_directories", [str(tmp_path)])
    return tmp_path


def upload(client, headers, raw, filename="poster.jpg"):
    return client.post(
        "/api/admin/posters", headers=headers,
        json={"filename": filename, "data": base64.b64encode(raw).decode("ascii")},
    )


@pytest.mark.parametrize("raw,ext", [(JPEG, "jpg"), (PNG, "png"), (WEBP, "webp")])
def test_upload_and_static_get(client, auth_headers, posters_dir, raw, ext):
    result = upload(client, auth_headers["admin"], raw, "not-the-correct-extension.txt")
    assert result.status_code == 201
    assert list(result.json()) == ["poster_url"]
    url = result.json()["poster_url"]
    assert re.fullmatch(rf"/uploads/posters/[0-9a-f]{{32}}\.{ext}", url)
    assert (posters_dir / url.removeprefix("/uploads/")).read_bytes() == raw
    served = client.get(url)
    assert served.status_code == 200 and served.content == raw


def test_reject_bad_base64(client, auth_headers, posters_dir):
    result = client.post("/api/admin/posters", headers=auth_headers["admin"],
                         json={"filename": "x.jpg", "data": "!!!not base64!!!"})
    assert result.status_code == 422
    assert result.json() == {"detail": "Ảnh poster không hợp lệ."}
    assert not (posters_dir / "posters").exists()


@pytest.mark.parametrize("raw", [b"hello", b"GIF89a" + b"0" * 32, b"<svg></svg>"])
def test_reject_disguised_non_image(client, auth_headers, posters_dir, raw):
    result = upload(client, auth_headers["admin"], raw, "looks-valid.jpg")
    assert result.status_code == 422
    assert result.json() == {"detail": "Chỉ nhận ảnh JPG, PNG hoặc WebP."}
    assert not (posters_dir / "posters").exists()


def test_reject_over_2mb_without_writing(client, auth_headers, posters_dir):
    result = upload(client, auth_headers["admin"], JPEG + b"a" * (2 * 1024 * 1024))
    assert result.status_code == 422
    assert result.json() == {"detail": "Ảnh poster tối đa 2 MB."}
    assert not (posters_dir / "posters").exists()


def test_traversal_filename_ignored(client, auth_headers, posters_dir):
    response = upload(client, auth_headers["admin"], PNG, "../../../../../outside.gif")
    assert response.status_code == 201
    url = response.json()["poster_url"]
    assert re.fullmatch(r"/uploads/posters/[0-9a-f]{32}\.png", url)
    assert not (posters_dir.parent / "outside.gif").exists()


def test_upload_requires_admin(client, auth_headers, posters_dir):
    request = {"filename": "x.png", "data": base64.b64encode(PNG).decode()}
    assert client.post("/api/admin/posters", json=request).status_code == 401
    assert client.post("/api/admin/posters", json=request,
                       headers=auth_headers["user"]).status_code == 403
    assert not (posters_dir / "posters").exists()


def test_create_requires_poster_and_accepts_links(client, auth_headers, movie_payload, posters_dir):
    headers = auth_headers["admin"]
    assert client.post("/api/admin/movies", json=movie_payload, headers=headers).json() == {"detail": POSTER_MESSAGE}
    for url in ("https://example.com/poster.jpg", "/uploads/posters/" + "a" * 32 + ".jpg"):
        result = client.post("/api/admin/movies", json={**movie_payload, "poster_url": url}, headers=headers)
        assert result.status_code == 201
        assert result.json()["poster_url"] == url


def test_update_existing_movie_can_keep_poster_empty(client, auth_headers, movie_payload, movie):
    payload = dict(movie_payload, poster_url=None)
    result = client.put(f"/api/admin/movies/{movie.id}", json=payload, headers=auth_headers["admin"])
    assert result.status_code == 200
    assert result.json()["poster_url"] is None


@pytest.mark.parametrize("poster_url", ["/uploads/../x", "/etc/passwd", "javascript:alert(1)"])
def test_reject_invalid_poster_paths(client, auth_headers, movie_payload, poster_url):
    result = client.post("/api/admin/movies", json={**movie_payload, "poster_url": poster_url}, headers=auth_headers["admin"])
    assert result.status_code == 422
    assert "Đường dẫn poster" in result.json()["detail"]
