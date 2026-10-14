# Codex Implementation Report — T19 (Final Handoff)

- **Task:** T19 — Tải ảnh poster từ máy khi thêm/sửa phim
- **Ngày bổ sung evidence:** 2026-10-14
- **Nhánh:** `task/T19-tai-anh-poster` (T18 CLOSED/merged tại `a81f7bb` trên master)
- **Result:** `IMPLEMENTATION_COMPLETED / HANDOFF_TO_CLAUDE` (chỉ sau khi Git scope/security gate đạt)
- **Đổi schema: Không** — dùng cột `movies.poster_url`, không migration
- **Vai trò:** Codex Primary Implementer; Claude **chưa** independent review, chưa `PASS`; PO **chưa** review/approve/merge T19.

## Phạm vi triển khai

- Backend: `POST /api/admin/posters` chỉ admin, JSON `{filename,data}` chứa base64 thuần (không multipart), kiểm tra magic bytes JPEG/PNG/WebP, giới hạn 2 MiB, tên lưu `uuid4.hex`, phục vụ `/uploads/posters/...` từ `UPLOAD_DIR`; mount StaticFiles, validation URL nội bộ UUID.
- Create movie POST bắt buộc poster (`422` thiếu poster); PUT movie cũ không bị bắt buộc; không đặt rule vào `MovieIn` dùng chung.
- Frontend: chọn ảnh, FileReader preview, nút bỏ ảnh, upload trước khi lưu; ảnh upload ưu tiên hơn link; giữ đường dẫn và hai ô màu poster.
- `real.js` / `mock.js` có cùng API và cấu trúc `{poster_url}`; mock giới hạn 500 KiB, data URL lưu qua localStorage.
- Không thêm dependency, không sửa schema; không commit `backend/uploads/`; không đụng DB thật.

## Files changed và ngoại lệ PO

- Backend: `backend/app/routers/admin_posters.py`, `backend/app/routers/admin_movies.py`, `backend/app/main.py`, `backend/app/config.py`, `backend/app/schemas.py`, `backend/.env.example`, `.gitignore`.
- Frontend: `frontend/src/pages/AdminMovies.jsx`, `frontend/src/components/Poster.jsx`, `frontend/src/api/real.js`, `frontend/src/api/mock.js`, `frontend/src/styles/global.css` (class bổ sung).
- Test: `backend/tests/test_poster_upload.py`.
- Tài liệu / điều phối / report: `docs/ARCHITECTURE.md`, `HUONG_DAN.md`, `docs/TASK_COORDINATION_ACTIVE.md`, `reports/2026-10-13/codex_implementation_T19_2026-10-13.md` (evidence ban đầu) và report 14/10 này.
- **Ngoại lệ PO trong chat:** sửa đúng `backend/tests/test_admin_features.py::test_admin_movie_crud` cho POST có URL poster hợp lệ, giữ PUT không poster và mọi assertion; PO phê duyệt trong chat. Không sửa `conftest.py`.
- `docs/tasks/T19.md` đã untracked trước khi bắt đầu; không thêm nó vào commit T19 vì ngoài Allowed Files. PO quản lý việc tracking Task Record riêng.

## Kết quả tests/gates — theo transcript PO cung cấp

| Gate | Evidence | Kết quả |
|---|---|---|
| Focused poster upload ban đầu | `pytest -q tests/test_poster_upload.py` | **15/15 PASS** |
| Focused sau sửa CRUD test | `pytest -q tests/test_admin_features.py::test_admin_movie_crud tests/test_poster_upload.py` | **16/16 PASS**; exit 0 |
| Full pytest (toàn bộ test cũ + mới) | `python -m pytest -q` | **65/65 PASS**; exit 0 |
| Backend compileall | `python -m compileall -q backend/app` | **PASS**; exit 0 |
| Frontend build | `npm run build` | **PASS**; exit 0 |
| Backend runtime/health | `GET http://127.0.0.1:8001/api/health` trên DB và UPLOAD_DIR tạm | **200 OK**, classifier `phobert_b`, active_version `phobert-B-2026-10-09`, classifier_error null |
| Real Mode browser | PO xác nhận checklist | **7/7 đạt — PO_ATTESTED** |
| Mock Mode browser, cổng 5174 | PO xác nhận checklist | **7/7 đạt — PO_ATTESTED** |
| Hồi quy BOI_CANH mục 7 | PO xác nhận checklist | **7/7 đạt — PO_ATTESTED** |
| Git scope / protected paths / upload ignore | Gate PowerShell trước khi áp dụng handoff patch | **PASS (điều kiện bắt buộc trước khi báo cáo này được áp dụng)** |

**Cảnh báo không chặn:** `DeprecationWarning` Starlette/AnyIO; pytest callback `cleanup_numbered_dir` trên Windows có `PermissionError [WinError 5]` sau summary nhưng cả hai exit code vẫn là 0. Warning `Poster.jsx` LF → CRLF, `git diff --check` exit 0. Cần Claude đánh giá độc lập nếu có nghi vấn.

## Bằng chứng từng Acceptance Criterion

| AC | Evidence thực tế | Đánh giá Codex |
|---|---|---|
| AC-01 | `test_poster_upload.py`: JPG/PNG/WebP upload 201, tên UUID và GET đúng bytes; focused và full pytest đạt | DEV PASS |
| AC-02 | Test invalid base64, over 2 MiB và text/GIF/SVG giả jpg đều 422, không tạo file; pytest đạt | DEV PASS |
| AC-03 | Filename traversal bị bỏ qua; đường dẫn file lưu theo UUID | DEV PASS |
| AC-04 | Admin dependency, anonymous 401, user 403 trong pytest | DEV PASS |
| AC-05 | Không poster POST 422; URL http(s)/internal hợp lệ POST 201 trong test | DEV PASS |
| AC-06 | PUT phim seed cũ không poster 200; test CRUD cũ giữ PUT không poster | DEV PASS |
| AC-07 | Invalid `/uploads/../x`, `/etc/passwd`, `javascript:...` nhận 422 | DEV PASS |
| AC-08 | PO chạy luồng browser real 7/7: preview, remove, ưu tiên upload, tạo/sửa và hiển thị poster cross-origin | DEV PASS — PO_ATTESTED |
| AC-09 | PO chạy mock 7/7: 500 KiB, data URL, reload và create/edit đúng contract | DEV PASS — PO_ATTESTED |
| AC-10 | `.gitignore` bỏ qua `/backend/uploads/`; Git gate kiểm tra danh sách thay đổi và không track upload | DEV PASS — Git gate required |
| AC-11 | Full pytest cũ+mới **65/65**, hồi quy browser 7/7 PO xác nhận | DEV PASS — PO_ATTESTED_BROWSER |

## Checklist hồi quy (BOI_CANH mục 7)

1. Trang chủ/PosterIntro/Xem chi tiết/Đặt vé: **PO_ATTESTED PASS**.
2. Menu Thể loại/Chủ đề/tìm `meo muop`: **PO_ATTESTED PASS**.
3. Đăng ký/đăng nhập/quay lại đặt vé: **PO_ATTESTED PASS**.
4. Đặt 2 ghế, ghế xám, Vé của tôi: **PO_ATTESTED PASS**.
5. Bình luận tiêu cực bị ẩn, admin kiểm duyệt: **PO_ATTESTED PASS**.
6. `/api/health`: **200 OK**, PhoBERT B active, error null.
7. `VITE_USE_MOCK=true` và poster sau reload: **PO_ATTESTED PASS**.

## Scope / Security / Handoff

- **Scope:** thay đổi chỉ nằm trong Allowed Files của T19 và ngoại lệ **duy nhất** `backend/tests/test_admin_features.py` được PO phê duyệt; `docs/tasks/T19.md` chưa track, không stage.
- **Security:** không đưa `.env`, `backend/firefly.db`, model, file upload, dữ liệu lớn vào Git. DB thử và UPLOAD_DIR được đặt dưới `%TEMP%` theo transcript PO; không chạy trên DB thật.
- **Limitations:** không xóa file poster cũ/orphan khi đổi hoặc xóa phim; upload trên môi trường không có storage bền vững có thể mất sau restart; nguồn ảnh http(s) có thể chặn hotlink.
- **Required fixes:** 0 được biết ở Codex, chờ Claude kiểm tra độc lập.
- **Open blockers:** 0 sau khi Git gate PASS.
- **Transition:** `READY_FOR_HANDOFF → IN_PROGRESS → CLAUDE_REVIEW`, **không tự review / PASS / PO_REVIEW / APPROVE / CLOSED**. T18 giữ CLOSED, không tự mở task mới.
