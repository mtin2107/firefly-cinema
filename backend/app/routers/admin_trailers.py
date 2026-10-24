"""Raw trailer uploads and bounded, single-range playback for Starlette 0.38."""
import re
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse, Response

from ..config import UPLOAD_DIR
from ..security import require_admin

router = APIRouter()
MAX_VIDEO_BYTES = 100 * 1024 * 1024
VIDEO_NAME = re.compile(r"[0-9a-f]{32}\.(mp4|webm)")


@router.post("/api/admin/trailers", status_code=201)
async def upload_trailer(request: Request, _=Depends(require_admin)):
    length = request.headers.get("content-length")
    if length and length.isdigit() and int(length) > MAX_VIDEO_BYTES:
        raise HTTPException(413, "Video trailer tối đa 100 MB.")
    if request.headers.get("content-type", "").split(";")[0].strip().lower() not in {"video/mp4", "video/webm"}:
        raise HTTPException(422, "Chỉ nhận video MP4 hoặc WebM.")
    directory = UPLOAD_DIR / "trailers"
    directory.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with NamedTemporaryFile(dir=directory, suffix=".tmp", delete=False) as output:
            temporary = Path(output.name)
            size = 0
            signature = bytearray()
            async for chunk in request.stream():
                size += len(chunk)
                if size > MAX_VIDEO_BYTES:
                    raise HTTPException(413, "Video trailer tối đa 100 MB.")
                signature.extend(chunk[:max(0, 8 - len(signature))])
                output.write(chunk)
        extension = "mp4" if signature[4:8] == b"ftyp" else "webm" if signature[:4] == b"\x1a\x45\xdf\xa3" else None
        if not extension:
            raise HTTPException(422, "Chỉ nhận video MP4 hoặc WebM.")
        name = f"{uuid4().hex}.{extension}"
        temporary.replace(directory / name)
        return {"trailer_url": f"/uploads/trailers/{name}"}
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


@router.get("/uploads/trailers/{name:path}")
def play_trailer(name: str, request: Request):
    if not VIDEO_NAME.fullmatch(name):
        raise HTTPException(404, "Không tìm thấy video trailer.")
    path = UPLOAD_DIR / "trailers" / name
    if not path.is_file():
        raise HTTPException(404, "Không tìm thấy video trailer.")
    size = path.stat().st_size
    media_type = "video/mp4" if name.endswith(".mp4") else "video/webm"
    headers = {"Accept-Ranges": "bytes"}
    start, end, status = 0, size - 1, 200
    value = request.headers.get("range")
    if value is not None:
        match = re.fullmatch(r"bytes=(\d*)-(\d*)", value)
        valid = bool(match and (match[1] or match[2]))
        try:
            if valid:
                if match[1]:
                    start = int(match[1])
                    end = min(int(match[2]), size - 1) if match[2] else size - 1
                else:
                    suffix = int(match[2])
                    start, end = max(0, size - suffix), size - 1
                    valid = suffix > 0
                valid = valid and 0 <= start <= end < size
        except ValueError:
            valid = False
        if not valid:
            return Response(status_code=416, headers={**headers, "Content-Range": f"bytes */{size}"}, media_type=media_type)
        status = 206
        headers["Content-Range"] = f"bytes {start}-{end}/{size}"
    headers["Content-Length"] = str(max(0, end - start + 1))

    def chunks():
        with path.open("rb") as video:
            video.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                chunk = video.read(min(64 * 1024, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk

    return StreamingResponse(chunks(), status_code=status, headers=headers, media_type=media_type)
