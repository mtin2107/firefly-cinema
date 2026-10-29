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


def upload(client, headers, raw):
    return client.post("/api/admin/posters", headers=headers,
                       json={"filename": "photo.jpg", "data": base64.b64encode(raw).decode("ascii")})


def test_accept_jpeg_with_data_after_eoi(client, auth_headers, posters_dir):  # noqa: F811
    raw = SOI + APP0 + SOS + EOI + b"MotionPhoto_Data" + b"\x00" * 64
    result = upload(client, auth_headers["admin"], raw)
    assert result.status_code == 201
    assert result.json()["poster_url"].endswith(".jpg")


@pytest.mark.parametrize("raw", [
    SOI + APP0 + SOS,                       # bị cắt giữa dữ liệu ảnh
    SOI + APP0 + APP1_WITH_EOI + SOS,       # FFD9 chỉ nằm trong segment trước SOS
    SOI + APP0 + APP1_WITH_EOI + b"junk",   # không có SOS
])
def test_reject_truncated_jpeg(client, auth_headers, posters_dir, raw):  # noqa: F811
    result = upload(client, auth_headers["admin"], raw)
    assert result.status_code == 422
    assert result.json() == {"detail": "Ảnh bị hỏng hoặc không đầy đủ."}
    assert not (posters_dir / "posters").exists()


def test_score_rules_follow_class_flag_not_name():
    assert CommentIn(content="ổn", stars=None).stars is None
    with pytest.raises(ValidationError):
        RatingIn(stars=None)

    class RenamedComment(CommentIn):
        pass

    assert RenamedComment(content="ổn", stars=None).stars is None
    with pytest.raises(ValidationError):
        RenamedComment(content="ổn", stars=11)
