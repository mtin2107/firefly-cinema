import asyncio
import json
from pathlib import Path

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.routers import admin_trailers

MP4 = b"\x00\x00\x00\x18ftypisom" + bytes(range(256)) * 8
WEBM = b"\x1a\x45\xdf\xa3" + b"webm" * 100


@pytest.fixture(autouse=True)
def temporary_uploads(tmp_path, monkeypatch):
    monkeypatch.setattr(admin_trailers, "UPLOAD_DIR", tmp_path)
    return tmp_path


@pytest.mark.parametrize("body,mime,extension", [(MP4, "video/mp4", "mp4"), (WEBM, "video/webm", "webm"), (MP4, "video/webm", "mp4")])
def test_upload_signature_and_playback(client, auth_headers, temporary_uploads, body, mime, extension):
    result = client.post("/api/admin/trailers", content=body, headers={**auth_headers["admin"], "Content-Type": mime})
    assert result.status_code == 201
    assert set(result.json()) == {"trailer_url"}
    url = result.json()["trailer_url"]
    assert url.endswith("." + extension)
    response = client.get(url)
    assert response.status_code == 200
    assert response.content == body
    assert response.headers["accept-ranges"] == "bytes"
    assert response.headers["content-type"] == f"video/{extension}"
    assert int(response.headers["content-length"]) == len(body)
    assert not list(temporary_uploads.rglob("*.tmp"))


@pytest.mark.parametrize("role,status", [(None, 401), ("user", 403)])
def test_upload_requires_admin(client, auth_headers, role, status):
    headers = auth_headers[role] if role else {}
    assert client.post("/api/admin/trailers", content=MP4, headers={**headers, "Content-Type": "video/mp4"}).status_code == status


@pytest.mark.parametrize("body,mime", [(b"", "video/mp4"), (b"fake.mp4", "video/mp4"), (b"\x89PNG\r\n", "video/webm"), (MP4, "application/json")])
def test_bad_upload_cleanup(client, auth_headers, temporary_uploads, body, mime):
    result = client.post("/api/admin/trailers", content=body, headers={**auth_headers["admin"], "Content-Type": mime})
    assert result.status_code == 422
    assert result.json()["detail"] == "Chỉ nhận video MP4 hoặc WebM."
    assert not list((temporary_uploads / "trailers").glob("*"))


def test_upload_oversize_and_stream_cleanup(client, auth_headers, temporary_uploads, monkeypatch):
    result = client.post("/api/admin/trailers", content=b"", headers={**auth_headers["admin"], "Content-Type": "video/mp4", "Content-Length": str(100 * 1024 * 1024 + 1)})
    assert result.status_code == 413
    monkeypatch.setattr(admin_trailers, "MAX_VIDEO_BYTES", 16)
    result = client.post("/api/admin/trailers", content=iter([MP4[:12], MP4[12:20]]), headers={**auth_headers["admin"], "Content-Type": "video/mp4"})
    assert result.status_code == 413
    assert result.json()["detail"] == "Video trailer tối đa 100 MB."
    assert not list(temporary_uploads.rglob("*.tmp"))


def test_stream_split_signature_disconnect_cleanup(temporary_uploads):
    async def run(chunks):
        iterator = iter(chunks)
        async def receive():
            return next(iterator)
        return await admin_trailers.upload_trailer(Request({"type": "http", "headers": [(b"content-type", b"video/mp4")]}, receive), None)
    result = asyncio.run(run([{"type": "http.request", "body": MP4[:3], "more_body": True}, {"type": "http.request", "body": MP4[3:], "more_body": False}]))
    assert result["trailer_url"].endswith(".mp4")
    from starlette.requests import ClientDisconnect
    with pytest.raises(ClientDisconnect):
        asyncio.run(run([{"type": "http.request", "body": MP4[:3], "more_body": True}, {"type": "http.disconnect"}]))
    assert not list(temporary_uploads.rglob("*.tmp"))


def test_content_length_rejected_without_reading_body(temporary_uploads):
    async def receive():
        pytest.fail("Oversized declared body must not be read")
    request = Request({"type": "http", "headers": [(b"content-type", b"video/mp4"), (b"content-length", b"104857601")]}, receive)
    with pytest.raises(HTTPException) as error:
        asyncio.run(admin_trailers.upload_trailer(request, None))
    assert error.value.status_code == 413
    assert not (temporary_uploads / "trailers").exists()


def test_upload_exact_stream_limit(client, auth_headers, monkeypatch):
    # Exercise equality with a small limit rather than allocating 100 MiB.
    monkeypatch.setattr(admin_trailers, "MAX_VIDEO_BYTES", len(MP4))
    response = client.post("/api/admin/trailers", content=iter([MP4[:7], MP4[7:]]), headers={**auth_headers["admin"], "Content-Type": "video/mp4"})
    assert response.status_code == 201


def test_create_with_trailer_and_synopsis(client, auth_headers, movie_payload):
    response = client.post("/api/admin/movies", headers=auth_headers["admin"], json={**movie_payload, "poster_url": "https://example.com/poster.png", "trailer_url": "https://youtu.be/AbCd_12-xyz", "synopsis": "Nội dung mới."})
    assert response.status_code == 201
    assert response.json()["synopsis"] == "Nội dung mới."
    assert response.json()["trailer_url"] == "https://www.youtube.com/watch?v=AbCd_12-xyz"


@pytest.mark.parametrize("value,start,end", [("bytes=0-1023", 0, 1023), ("bytes=100-", 100, len(MP4)-1), ("bytes=-17", len(MP4)-17, len(MP4)-1), ("bytes=0-999999", 0, len(MP4)-1), ("bytes=-999999", 0, len(MP4)-1)])
def test_ranges(client, temporary_uploads, value, start, end):
    path = temporary_uploads / "trailers" / ("a" * 32 + ".mp4")
    path.parent.mkdir()
    path.write_bytes(MP4)
    result = client.get(f"/uploads/trailers/{path.name}", headers={"Range": value})
    assert result.status_code == 206
    assert result.content == MP4[start:end+1]
    assert result.headers["content-range"] == f"bytes {start}-{end}/{len(MP4)}"
    assert int(result.headers["content-length"]) == end-start+1
    assert result.headers["accept-ranges"] == "bytes"


@pytest.mark.parametrize("value", ["bytes=99999-", "bytes=5-3", "bytes=-0", "bytes=-", "items=0-1", "bytes=0-1,3-4", "nonsense"])
def test_unsatisfiable_ranges(client, temporary_uploads, value):
    path = temporary_uploads / "trailers" / ("b" * 32 + ".webm")
    path.parent.mkdir()
    path.write_bytes(WEBM)
    result = client.get(f"/uploads/trailers/{path.name}", headers={"Range": value})
    assert result.status_code == 416
    assert result.headers["content-range"] == f"bytes */{len(WEBM)}"
    assert result.headers["accept-ranges"] == "bytes"


@pytest.mark.parametrize("name", ["x.mp4", "..%2Fx.mp4", "A" * 32 + ".mp4", "a" * 32 + ".exe", "a" * 32 + ".mp4"])
def test_invalid_or_missing_video(client, name):
    assert client.get(f"/uploads/trailers/{name}").status_code == 404


@pytest.mark.parametrize("url", ["https://youtu.be/AbCd_12-xyz?si=hello", "http://m.youtube.com/watch?v=AbCd_12-xyz&t=30s", "https://youtube.com/shorts/AbCd_12-xyz", "https://www.youtube.com/embed/AbCd_12-xyz?list=foo"])
def test_youtube_normalization(client, auth_headers, movie, movie_payload, url):
    result = client.put(f"/api/admin/movies/{movie.id}", json={**movie_payload, "trailer_url": url, "synopsis": "  Đoạn một.\n\nĐoạn hai.  "}, headers=auth_headers["admin"])
    assert result.status_code == 200
    assert result.json()["trailer_url"] == "https://www.youtube.com/watch?v=AbCd_12-xyz"
    public = client.get(f"/api/movies/{movie.id}").json()
    assert public["synopsis"] == "Đoạn một.\n\nĐoạn hai."
    assert public["trailer_url"] == result.json()["trailer_url"]


@pytest.mark.parametrize("url", ["https://evil.com/watch?v=AbCd_12-xyz", "javascript:alert(1)", "https://youtu.be/short", "/uploads/trailers/../x.mp4", "/uploads/posters/" + "a" * 32 + ".jpg", "https://youtube.com.evil.com/watch?v=AbCd_12-xyz", "https://evil@youtube.com/watch?v=AbCd_12-xyz", "blob:abc", "https://youtu.be:8080/AbCd_12-xyz"])
def test_bad_trailer_validator(client, auth_headers, movie, movie_payload, url):
    result = client.put(f"/api/admin/movies/{movie.id}", json={**movie_payload, "trailer_url": url}, headers=auth_headers["admin"])
    assert result.status_code == 422
    assert "Link trailer phải là link YouTube hoặc video đã tải lên." in result.json()["detail"]


def test_optional_fields_limits_and_remove(client, auth_headers, movie, movie_payload):
    path = "/uploads/trailers/" + "a" * 32 + ".mp4"
    def update(**values):
        return client.put(f"/api/admin/movies/{movie.id}", json={**movie_payload, **values}, headers=auth_headers["admin"])
    assert update(trailer_url=path, synopsis="x" * 5000).status_code == 200
    result = update(synopsis="x" * 5001)
    assert result.status_code == 422 and "5000 ký tự" in result.json()["detail"]
    result = update(trailer_url="  ", synopsis=" \n ")
    assert result.status_code == 200
    assert result.json()["trailer_url"] is None and result.json()["synopsis"] is None


def test_seed_movie_parity():
    root = Path(__file__).resolve().parents[2]
    backend = (root / "backend/app/data/movies.json").read_bytes()
    assert backend == (root / "frontend/src/api/movies.json").read_bytes()
    for movie in json.loads(backend):
        assert movie["trailer_url"] is None
        assert 2 <= len(movie["synopsis"].split("\n\n")) <= 3
        assert len(movie["synopsis"]) <= 5000
