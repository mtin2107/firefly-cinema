"""T31: JPEG có dữ liệu sau EOI và validator điểm không dựa vào tên lớp."""
import base64

import pytest
from pydantic import ValidationError

from app.schemas import CommentIn, RatingIn
from test_poster_upload import posters_dir  # noqa: F401  (fixture thư mục upload tạm)


SOI = b"\xff\xd8"
APP0 = b"\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
# APP1 chứa sẵn cặp FFD9 (giống ảnh thu nhỏ trong EXIF) để chắc validator bỏ qua nội dung segment
APP1_WITH_EOI = b"\xff\xe1\x00\x08\xff\xd8\xff\xd9"
SOS = b"\xff\xda\x00\x08\x01\x01\x00\x00\x3f\x00" + b"\x12\x34" * 20
EOI = b"\xff\xd9"
# Codex RF-01: FFD9 nằm trong header SOS (dài 8 byte), dữ liệu ảnh bị cắt
SOS_HEADER_EOI = bytes.fromhex("ffd8ffe000104a46494600010100000100010000ffda00080101ffd93f00") + b"truncated"
TRAILING = SOI + APP0 + SOS + EOI + b"MotionPhoto_Data" + b"\x00" * 64
TRUNCATED = [
    SOI + APP0 + SOS,                       # bị cắt giữa dữ liệu ảnh
    SOI + APP0 + APP1_WITH_EOI + SOS,       # FFD9 chỉ nằm trong segment trước SOS
    SOI + APP0 + APP1_WITH_EOI + b"junk",   # không có SOS
    SOS_HEADER_EOI,
    SOI + APP0 + b"\xff\xda\x00\x40\x01",   # độ dài SOS vượt quá file
]


def upload(client, headers, raw):
    return client.post("/api/admin/posters", headers=headers,
                       json={"filename": "photo.jpg", "data": base64.b64encode(raw).decode("ascii")})


def test_accept_jpeg_with_data_after_eoi(client, auth_headers, posters_dir):  # noqa: F811
    result = upload(client, auth_headers["admin"], TRAILING)
    assert result.status_code == 201
    assert result.json()["poster_url"].endswith(".jpg")


@pytest.mark.parametrize("raw", TRUNCATED)
def test_reject_truncated_jpeg(client, auth_headers, posters_dir, raw):  # noqa: F811
    result = upload(client, auth_headers["admin"], raw)
    assert result.status_code == 422
    assert result.json() == {"detail": "Ảnh bị hỏng hoặc không đầy đủ."}
    assert not (posters_dir / "posters").exists()


def put_avatar(client, headers, raw):
    return client.put("/api/auth/me/avatar", headers=headers,
                      json={"filename": "me.jpg", "data": base64.b64encode(raw).decode("ascii")})


def test_avatar_accepts_jpeg_with_data_after_eoi(client, auth_headers, tmp_path, monkeypatch):
    from app.routers import auth
    monkeypatch.setattr(auth, "UPLOAD_DIR", tmp_path)
    result = put_avatar(client, auth_headers["user"], TRAILING)
    assert result.status_code == 200
    assert (tmp_path / "avatars" / result.json()["avatar_url"].rsplit("/", 1)[1]).read_bytes() == TRAILING


@pytest.mark.parametrize("raw", TRUNCATED)
def test_avatar_rejects_truncated_jpeg(client, auth_headers, tmp_path, monkeypatch, raw):
    from app.routers import auth
    monkeypatch.setattr(auth, "UPLOAD_DIR", tmp_path)
    result = put_avatar(client, auth_headers["user"], raw)
    assert result.status_code == 422
    assert result.json() == {"detail": "Ảnh bị hỏng hoặc không đầy đủ."}
    assert not (tmp_path / "avatars").exists() or not any((tmp_path / "avatars").iterdir())


def test_score_rules_follow_class_flag_not_name():
    assert CommentIn(content="ổn", stars=None).stars is None
    with pytest.raises(ValidationError):
        RatingIn(stars=None)

    class RenamedComment(CommentIn):
        pass

    assert RenamedComment(content="ổn", stars=None).stars is None
    with pytest.raises(ValidationError):
        RenamedComment(content="ổn", stars=11)
