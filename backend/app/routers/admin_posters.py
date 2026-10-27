"""Nhận poster dạng JSON/base64 và lưu bằng tên UUID, không tin tên client."""
import base64
import binascii
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ValidationInfo, field_validator

from ..config import UPLOAD_DIR
from ..models import User
from ..security import require_admin

router = APIRouter(prefix="/api/admin/posters", tags=["Quản trị poster"])
MAX_POSTER_BYTES = 2 * 1024 * 1024
MAX_IMAGE_BASE64 = 4 * ((MAX_POSTER_BYTES + 2) // 3)


class PosterUploadIn(BaseModel):
    filename: str
    data: str = Field(max_length=MAX_IMAGE_BASE64)

    @field_validator("data", mode="before")
    @classmethod
    def bound_data(cls, value, info: ValidationInfo):
        # Giữ câu lỗi poster cũ khi schema chặn trước bước giải mã ảnh.
        if isinstance(value, str) and len(value) > MAX_IMAGE_BASE64:
            label = (info.context or {}).get("image_label", "Ảnh poster")
            raise HTTPException(422, f"{label} tối đa 2 MB.")
        return value


def _extension(data: bytes) -> str | None:
    if data.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


def validate_image(data: str, label: str = "Ảnh poster"):
    try:
        # Không chấp nhận tiền tố data: hoặc chuỗi base64 không hợp lệ.
        binary = base64.b64decode(data, validate=True)
    except (ValueError, binascii.Error):
        raise HTTPException(422, f"{label} không hợp lệ.") from None

    if not binary:
        raise HTTPException(422, f"{label} không hợp lệ.")
    if len(binary) > MAX_POSTER_BYTES:
        raise HTTPException(422, f"{label} tối đa 2 MB.")

    ext = _extension(binary)
    if ext is None:
        raise HTTPException(422, "Chỉ nhận ảnh JPG, PNG hoặc WebP.")

    valid = {
        "png": binary[12:16] == b"IHDR" and binary.endswith(bytes.fromhex("0000000049454e44ae426082")),
        "jpg": binary.endswith(b"\xff\xd9"),
        "webp": int.from_bytes(binary[4:8], "little") + 8 == len(binary),
    }[ext]
    if not valid:
        raise HTTPException(422, "Ảnh bị hỏng hoặc không đầy đủ.")
    return binary, ext


@router.post("", status_code=201)
def upload_poster(body: PosterUploadIn, _: User = Depends(require_admin)):
    binary, ext = validate_image(body.data)

    # Không bao giờ nối filename do client gửi vào đường dẫn.
    folder = Path(UPLOAD_DIR) / "posters"
    folder.mkdir(parents=True, exist_ok=True)
    name = f"{uuid4().hex}.{ext}"
    (folder / name).write_bytes(binary)
    return {"poster_url": f"/uploads/posters/{name}"}
