# Codex Implementation Report — T19

- **Task:** T19 — Tải ảnh poster từ máy khi thêm/sửa phim
- **Ngày:** 2026-10-13
- **Nhánh PO đã tạo:** `task/T19-tai-anh-poster` từ master sau T18 CLOSED / merge (`a81f7bb`)
- **Trạng thái:** **IN_PROGRESS / BLOCKED_PENDING_FULL_GATES**, **chưa bàn giao Claude**
- **Đổi schema: Không**. Tái sử dụng `movies.poster_url`.

## Files Changed
- Backend: `backend/app/routers/admin_posters.py` (mới), `backend/app/routers/admin_movies.py`, `backend/app/main.py`, `backend/app/config.py`, `backend/app/schemas.py`, `backend/.env.example`, `.gitignore`.
- Frontend: `frontend/src/pages/AdminMovies.jsx`, `frontend/src/components/Poster.jsx`, `frontend/src/api/real.js`, `frontend/src/api/mock.js`, `frontend/src/styles/global.css` (chỉ class bổ sung).
- Tests: `backend/tests/test_poster_upload.py` (mới).
- Tài liệu: `docs/ARCHITECTURE.md`, `HUONG_DAN.md`, `docs/TASK_COORDINATION_ACTIVE.md`, report này.
- **Không sửa tệp test cũ ngoài allowlist, không sửa `.env`, file DB/model thật, không tạo hoặc commit `backend/uploads/`.**

## Implementation / Contracts
- Upload admin JSON `{filename,data}` (base64 thuần), response 201 `{poster_url}`; chỉ chấp nhận JPG/PNG/WebP theo magic bytes, tối đa 2 MiB, lưu `uuid4.hex`, URL `/uploads/posters/...`. Starlette StaticFiles mount `/uploads`; `UPLOAD_DIR` mặc định từ `backend`.
- `MovieIn` tiếp tục dùng chung cho PUT và POST; chỉ router POST chặn poster rỗng (422 đúng câu). Poster URL nội bộ chỉ nhận mẫu UUID nghiêm ngặt; URL http(s) giữ nguyên.
- Form chọn ảnh, xem trước data URL, bỏ ảnh, upload trước khi lưu và ưu tiên upload hơn link; giữ ô đường dẫn poster và hai ô màu. Mock giới hạn 500 KiB, kiểm tra magic bytes, trả data URL lưu localStorage.
- Giới hạn chủ đích: không xóa ảnh mồ côi, ổ đĩa không bền vững khi deploy có thể mất ảnh.

## Focused tests đã chạy trong môi trường bản sao ZIP (không phải repository đầy đủ)
- `python -m compileall -q backend/app backend/tests/test_poster_upload.py`: **PASS**.
- `node --check --input-type=module` cho `real.js`, `mock.js`: **PASS**.
- Parser TypeScript (ScriptKind.JSX) cho `AdminMovies.jsx` và `Poster.jsx`: **PASS** (kiểm tra cú pháp, không thay thế Vite build).
- FastAPI TestClient isolated router với authentication test-double, upload temp + StaticFiles: **12/12 PASS** (JPG/PNG/WebP, URL/GET, malformed base64, 2 MB, GIF/SVG/text giả JPG, path traversal, anonymous/user).
- Pydantic MovieIn isolated schema test với taxonomy stubs: **10/10 PASS** (http(s), UUID paths, invalid paths, trường tùy chọn với PUT).
- Node isolated helper tests mock (magic bytes/base64): **9/9 PASS**.
- Tệp `backend/tests/test_poster_upload.py` được viết để chạy cùng pytest thật của repo (không ngụy nhận kết quả isolated là kết quả integration).

## Evidence theo Acceptance Criteria
| AC | Bằng chứng | Trạng thái |
|---|---|---|
| AC-01 | FastAPI isolated 3 định dạng trả 201, UUID file, GET cùng bytes | Focused PASS; integration repo PENDING |
| AC-02 | FastAPI isolated invalid base64, >2 MiB, text/GIF/SVG 422, không ghi file | Focused PASS; repo PENDING |
| AC-03 | Filename `../../fake.txt` không được dùng; file UUID nằm trong upload temp | Focused PASS; repo PENDING |
| AC-04 | FastAPI isolated auth test-double 401/403; code router dùng `require_admin` thật | Integration phân quyền thật PENDING |
| AC-05 | Code POST yêu cầu poster; Pydantic isolated http(s)/internal paths; test mới | Integration POST 201/422 PENDING |
| AC-06 | Code PUT không đổi; test mới cho phim seed không poster | Integration PUT PENDING |
| AC-07 | Pydantic isolated chặn path traversal, `/etc/passwd`, javascript | Integration 422 PENDING |
| AC-08 | UI có FileReader preview, remove, ưu tiên ảnh, Poster ghép API_URL | Browser real E2E PENDING |
| AC-09 | Mock implementation, Node helpers 9/9 | Browser mock upload/reload PENDING |
| AC-10 | `.gitignore` đã có `/backend/uploads/`; file ảnh trong test temp | Git trên máy PO PENDING |
| AC-11 | Test mới viết + xác định regression cũ, chưa chạy full suite | **BLOCKED** |

## Final Gates (AGENT_RULES 3.1)
- Compileall: **PASS** (mã có trong ZIP).
- Backend uvicorn + `/api/health`: **NOT RUN** — thiếu backend modules (`database.py`, `models.py`, `classifier.py`, ...) trong ZIP.
- Focused pytest T19 và pytest cũ: **BLOCKED** (import `app.database` không có trong ZIP; pytest exit 4).
- `npm run build`: **BLOCKED** (`frontend/package.json` không có trong ZIP; npm ENOENT).
- Real UI, mock UI reload, ảnh trang chủ/trang phim: **NOT RUN**, cần chạy trong repo/browser.
- Hồi quy 7 mục: **NOT RUN**. Checklist bên dưới ghi rõ.
- Scope/bí mật: patch đã `git apply --check` và kiểm tra khớp nội dung **17/17 file** trên bản sao Git sạch; `git -c core.whitespace=cr-at-eol diff --check` PASS; Git máy PO **PENDING**. Không đưa `.env`, DB, model hoặc upload vào bản vá.

## Checklist hồi quy (BOI_CANH_DU_AN mục 7)
1. Trang chủ hiện phim, PosterIntro/Xem chi tiết/Đặt vé: PENDING_BROWSER.
2. Menu Thể loại/Chủ đề, tìm `meo muop`: PENDING_BROWSER.
3. Đăng ký, đăng nhập rồi quay lại trang giờ chiếu: PENDING_BROWSER.
4. Đặt 2 ghế và thấy ghế bị khóa, Vé của tôi: PENDING_BROWSER.
5. Bình luận tiêu cực bị ẩn và admin kiểm duyệt: PENDING_BROWSER.
6. `/api/health` nhận đúng classifier PhoBERT: PENDING_TEMP_RUNTIME.
7. `VITE_USE_MOCK=true`, upload ≤500 KiB, reload và luồng đặt vé: PENDING_BROWSER.

## Blockers / Contract conflict
- **B-01 (environment):** ZIP được tạo bằng `git archive` theo danh sách source giới hạn; không có toàn repo/frontend deps nên không thể chạy final gates trên bản sao này. Dùng trên máy PO với `DATABASE_URL` SQLite tạm và `UPLOAD_DIR` tạm; tuyệt đối không chạy backend với database thật.
- **B-02 (scope/test conflict):** `backend/tests/conftest.py::movie_payload` hiện có `poster_url=None`; test cũ `backend/tests/test_admin_features.py::test_admin_movie_crud` mong POST trả 201. T19 AC-05 yêu cầu POST trả 422, nên test cũ sẽ thất bại nếu không cập nhật fixture/test. **Hai tệp test cũ đều ngoài Allowed Files T19**, cần PO phê duyệt scope exception hoặc chỉnh Task Record. Không làm yếu AC-05 và không tự sửa tests cũ để PASS.
- **Không tự review, không tự PASS, không tự chuyển PO_REVIEW, không tự CLOSED.** Trạng thái thực tế `IN_PROGRESS / BLOCKED_PENDING_FULL_GATES`.

## Handoff sau khi gỡ blockers
Áp dụng patch vào nhánh `task/T19-tai-anh-poster`; xác nhận scope exception trước khi thay test cũ; chạy focused trước và full gates sau. Chỉ khi mọi AC/gate đã đủ bằng chứng mới cập nhật coordination `IN_PROGRESS → CLAUDE_REVIEW` và giao Claude review độc lập.
