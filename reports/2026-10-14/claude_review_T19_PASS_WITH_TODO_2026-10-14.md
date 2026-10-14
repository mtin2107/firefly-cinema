# Claude Independent Review — T19

- **Task:** T19 — Tải ảnh poster từ máy khi thêm/sửa phim
- **Nhánh / commit review:** `task/T19-tai-anh-poster` @ `7c85db1` (merge-base với `master` = `a81f7bb`)
- **Reviewer:** Claude (Independent Reviewer / Tester)
- **Ngày chạy review:** 15/10/2026 (tên file giữ ngày 14/10 theo yêu cầu PO)
- **Kết luận:** **PASS_WITH_TODO**
- **AC:** 11/11 PASS · **Required Fixes:** 0 · **TODO:** 4 (Low) · **OBS:** 4 · **Blocker:** 0
- **Đổi schema:** Không (xác minh: `backend/app/models.py` không nằm trong diff)
- **Chuyển trạng thái:** `CLAUDE_REVIEW → PO_REVIEW`. Không approve, không merge, không đóng T19.

## 1. Nguồn đã đọc
`PROJECT_SOURCE_OF_TRUTH.md`, `AGENT_RULES.md`, `TASK_COORDINATION_ACTIVE.md`, `docs/tasks/T19.md` (untracked, bản PO trên máy), `reports/2026-10-13/codex_implementation_T19_2026-10-13.md`, `reports/2026-10-14/codex_implementation_T19_2026-10-14.md`, diff thật `git diff master...task/T19-tai-anh-poster` và source/test liên quan (`admin_posters.py`, `admin_movies.py`, `schemas.py`, `config.py`, `main.py`, `conftest.py`, `AdminMovies.jsx`, `Poster.jsx`, `real.js`, `mock.js`, `config.js`). Không đọc task CLOSED.

## 2. An toàn dữ liệu
- Mọi lần chạy pytest/uvicorn đều đặt `DATABASE_URL` = SQLite tạm và `UPLOAD_DIR` = thư mục tạm trong scratchpad Claude (ngoài repo). Backend runtime chạy cổng **8003**.
- `backend/firefly.db` SHA-256 **trước và sau** review: `56A5009D0CE25D26834C18583B5320AE0835B359AD6BF968B99DE54E77AAD8D8`, mtime giữ nguyên `13/10/2026 14:42:51`.
- `backend/uploads` **không tồn tại** sau review. `git status`: chỉ `?? docs/tasks/T19.md` (đã có từ trước).
- Cổng 8001 đang có một tiến trình `uvicorn ... --port 8001` có sẵn trên máy (không do Claude khởi động). Claude **không** đụng vào; Tín tự kiểm tra và tắt nếu là phiên thử cũ.

## 3. Scope và bảo mật Git

| Gate | Kết quả |
|---|---|
| `git diff --stat master...HEAD` | 19 file, +465/−23. Tất cả thuộc Allowed Files T19, cộng **đúng một** ngoại lệ PO đã duyệt: `backend/tests/test_admin_features.py` |
| Ngoại lệ test cũ | Chỉ đổi payload POST thành có `poster_url` hợp lệ; PUT vẫn dùng payload không poster; không bỏ assertion; `conftest.py` không đổi → **đúng phạm vi ngoại lệ** |
| File cấm (`.env`, `*.db`, model, CSV, `backend/uploads/`, `models.py`, `seats.py`, `classifier.py`, requirements, `package.json`, `:root`) | Không có trong diff |
| `.gitignore` | Thêm duy nhất `/backend/uploads/`; `git check-ignore -v backend/uploads/posters/x.png` → `.gitignore:9:/backend/uploads/` |
| `git diff --check` (cr-at-eol) | exit 0 |
| Đường dẫn `D:\` trong diff | Không có |
| Commit | `[T19] Implement poster upload and hand off to Claude` — đúng dạng `[Txx]` |
| Thư viện mới | Không (dùng `base64`, `uuid`, Starlette `StaticFiles` có sẵn) |

## 4. Gate độc lập (AGENT_RULES 3.1)

| Gate | Lệnh | Kết quả |
|---|---|---|
| Focused pytest | `pytest -q tests/test_poster_upload.py tests/test_admin_features.py::test_admin_movie_crud` | **16 passed**, exit 0 |
| Probe tạm Claude | `tests/test_zz_claude_probe_t19.py` (6 test, xem mục 5) | **6/6 PASS**; **đã xóa** trước gate cuối |
| Full pytest (gate cuối, sau khi xóa probe) | `python -m pytest -q` | **65 passed**, exit 0 (khớp evidence Codex 65/65) |
| compileall | `python -m compileall -q backend\app` | exit 0 |
| Frontend build | `npm run build` | exit 0 (`index-BG4K9w4L.js` 390,88 kB / gzip 135,51 kB) |
| Backend + health | uvicorn cổng 8003, DB/UPLOAD_DIR tạm | `200`, `"classifier":"phobert_b"`, `active_version":"phobert-B-2026-10-09"`, `classifier_error:null` |
| Real Mode (browser) | Vite 5175, `VITE_USE_MOCK=false`, `VITE_API_URL=http://localhost:8003` (khác origin) | PASS (mục 6) |
| Mock Mode (browser) | Vite 5177, `VITE_USE_MOCK=true` | PASS (mục 7) |
| Hồi quy BOI_CANH mục 7 | Claude tự chạy | **7/7 PASS** (mục 8) |

Cảnh báo không chặn: `DeprecationWarning` Starlette/AnyIO (có từ trước). Lỗi `PermissionError [WinError 5]` của pytest khi dọn `pytest-current` chỉ xuất hiện khi dùng basetemp mặc định, exit vẫn 0; dùng `--basetemp` riêng thì không xuất hiện.

## 5. Probe bảo mật backend (tạm, đã xóa)

| Probe | Kết quả |
|---|---|
| Ảnh đúng **2 MiB** → 201; **2 MiB + 1 byte** → 422 `"Ảnh poster tối đa 2 MB."` | PASS (biên đúng `>`) |
| Base64 có tiền tố `data:...`, có `\n`, chuỗi rỗng, `"QQ"` (thiếu padding) → 422 `"Ảnh poster không hợp lệ."`, không ghi file | PASS |
| Thiếu `filename`/`data`, `data` kiểu số → 422 với `detail` là một câu (handler hiện có) | PASS |
| StaticFiles: `/uploads/../secret.txt`, `/uploads/%2e%2e/secret.txt`, file không tồn tại → 404, không lộ nội dung ngoài `UPLOAD_DIR` | PASS |
| Validator `poster_url` (POST **và** PUT): hex in hoa, đuôi `.gif`, 31 hex, `...jpg/../x`, `...jpg\nx`, `data:image/png;base64,...`, `ftp://`, `https://` (không host) → 422 | PASS |
| Đường dẫn nội bộ có khoảng trắng hai đầu được `strip()` rồi chấp nhận; POST `poster_url="   "` → 422 câu bắt buộc | PASS |
| API công khai `/api/movies/{id}` trả nguyên đường dẫn nội bộ | PASS |

Runtime HTTP thật (cổng 8003): anonymous **401**, user thường **403**; admin upload PNG với `filename="../../evil.php"` → 201 `/uploads/posters/e0627943fc244ed3a21be75a5ddc4b09.png`; `GET` → 200 `image/png`, bytes trùng khớp; thư mục chỉ có file UUID; GIF đổi tên `.jpg` → 422.

Đánh giá code: `_extension()` kiểm magic bytes đúng spec (JPEG `FF D8 FF`, PNG đủ 8 byte chữ ký, WebP `RIFF....WEBP` có kiểm độ dài ≥ 12); tên file luôn `uuid4().hex` + đuôi theo magic bytes, không bao giờ dùng `filename`; mkdir chỉ sau khi đã validate xong nên request lỗi không tạo thư mục; `base64.b64decode(validate=True)` từ chối ký tự ngoài bảng mã.

## 6. Real Mode — browser (backend khác origin)
1. Thêm phim mới khi thiếu cả ảnh lẫn link → hiện `"Hãy chọn ảnh poster hoặc dán đường dẫn poster."`, **không có request POST** nào (network log chỉ có GET).
2. Chọn PNG (`filename="../../poster thu.png"`) → khung "Xem trước poster" đổi ngay sang `data:image/png;base64,...`; hiện "Đã chọn: …" + nút **Bỏ ảnh đã chọn**.
3. Bấm **Bỏ ảnh đã chọn** → `input.files.length = 0`, preview quay về poster màu.
4. Kiểm tra client: GIF → `"Chỉ nhận ảnh JPG, PNG hoặc WebP."`; file 2 MiB + 1 → `"Ảnh poster tối đa 2 MB."`.
5. Chọn PNG **và** nhập link `https://example.com/link-poster.jpg` → `POST /api/admin/posters` 201 rồi `POST /api/admin/movies` 201, body phim có `poster_url: "/uploads/posters/237283a5eef545bc92203510ac9ad119.png"` → **ảnh upload được ưu tiên**.
6. Trang phim `/phim/22` và trang chủ: `<img src="http://localhost:8003/uploads/posters/2372….png">`, `naturalWidth=200` → `Poster.jsx` ghép `API_URL` đúng, ảnh tải được khi khác origin.
7. Sửa phim seed "Mật Mã Bến Nghé" để trống poster → "Đã cập nhật phim."; nhãn ở chế độ sửa là "Đường dẫn poster (không bắt buộc)", chế độ thêm là "… (hoặc chọn ảnh từ máy) *".
8. Sửa phim có poster nội bộ (ô đường dẫn chứa `/uploads/posters/...`) → lưu được (form có `noValidate`, regex client chấp nhận đường dẫn nội bộ).
9. Ảnh giả (`type=image/png`, nội dung text) → client cho qua, server 422; lỗi hiện dưới ô chọn ảnh; **không tạo phim** (`/api/movies/23` → 404) và **không ghi file** (thư mục chỉ có 2 file hợp lệ).
10. Console: chỉ một lỗi 422 tài nguyên (đúng ca 9). Toàn bộ chữ trên giao diện là tiếng Việt.

## 7. Mock Mode — browser
- Thiếu poster khi thêm → lỗi đúng câu, không tạo phim.
- PNG 600 KB (đúng magic bytes) → `"Ảnh poster tối đa 500 KB."`, không có thông báo thành công.
- PNG nhỏ → "Đã thêm phim mới."; localStorage lưu `poster_url` dạng `data:image/png;base64,...` (7.714 ký tự).
- Tải lại trang `/phim/22` và trang chủ → poster hiện (`naturalWidth=200`).
- Gọi trực tiếp `api.admin.posters.upload`: trả `{poster_url}` (một key, **cùng cấu trúc real**); GIF → 422 `"Chỉ nhận ảnh JPG, PNG hoặc WebP."`; base64 hỏng → 422 `"Ảnh poster không hợp lệ."`.

## 8. Checklist hồi quy BOI_CANH mục 7 (Real Mode, DB tạm)
1. Trang chủ có hero + 60 thẻ phim; bấm "Xem chi tiết" → PosterIntro chạy rồi vào `/phim/9` — **PASS**.
2. Menu Thể loại/Chủ đề hiện; tìm `meo muop` → `/kham-pha?q=meo%20muop`, 1 phim "Meo Mướp Đi Lạc" — **PASS**.
3. Đăng ký tài khoản mới (đăng nhập tự động); đăng xuất, bấm giờ chiếu 22:00 → `/dang-nhap`; đăng nhập → quay lại `/dat-ve/20` — **PASS**.
4. Đặt A1, A2 (190.000 đ) → "Vé của tôi" có vé giữ chỗ; mở lại suất 20 → A1, A2 `seat--taken`, disabled — **PASS**.
5. Bình luận "Ko hay như quảng cáo, hơi thất vọng" → ẩn mặc định; admin API: `is_negative=true`, `negative_score=0.9992`, `phobert_b` — **PASS**.
6. `/api/health` → `phobert_b` (model mặc định theo Q3, PO APPROVED 10/10/2026) — **PASS**.
7. `VITE_USE_MOCK=true` dùng được (mục 7) — **PASS**.

## 9. Acceptance Criteria

| AC | Evidence độc lập | Kết quả |
|---|---|---|
| AC-01 | pytest 3 định dạng + runtime PNG 201, tên 32 hex, file trong UPLOAD_DIR, GET đúng bytes | PASS |
| AC-02 | pytest + probe: >2 MiB, base64 hỏng, text/GIF/SVG đổi đuôi → 422 đúng câu, không có file | PASS |
| AC-03 | `filename` traversal (pytest, runtime `../../evil.php`, browser `../../poster thu.png`) → luôn UUID | PASS |
| AC-04 | pytest + runtime: 401 / 403 | PASS |
| AC-05 | pytest + probe: POST thiếu/rỗng/khoảng trắng → 422 đúng câu; http(s) và `/uploads/posters/<32hex>.<ext>` → 201 | PASS |
| AC-06 | pytest + browser: PUT phim seed để trống poster → 200 | PASS |
| AC-07 | pytest + probe (POST và PUT): `/uploads/../x`, `/etc/passwd`, `javascript:` và các biến thể → 422 | PASS |
| AC-08 | Browser real mục 6 (preview, ưu tiên ảnh, trang chủ + trang phim khác origin, thiếu cả hai, bỏ ảnh, tiếng Việt) | PASS |
| AC-09 | Browser mock mục 7 (≤500 KB, reload, >500 KB báo lỗi, `{poster_url}` cùng cấu trúc) | PASS |
| AC-10 | `git status` sạch phần uploads; `check-ignore` đạt | PASS |
| AC-11 | Full pytest 65/65 sau khi xóa probe; hồi quy 7/7 | PASS |

Definition of Done: code + test trong allowlist, gate đầy đủ, docs (`ARCHITECTURE.md`, `HUONG_DAN.md`, `.env.example`) cập nhật, không đổi schema, không thêm thư viện → **MET**.

## 10. TODO (không chặn, đề xuất disposition cho PO)

| ID | Severity | File | Vấn đề | Đề xuất |
|---|---|---|---|---|
| TODO-01 | Low | `backend/app/routers/admin_posters.py:18-20` | `PosterUploadIn.data`/`filename` không có `max_length`; giới hạn 2 MB chỉ kiểm **sau** khi đọc toàn bộ JSON và giải mã base64. Admin (hoặc token admin bị lộ) gửi body vài trăm MB sẽ chiếm bộ nhớ tương ứng. Chỉ admin gọi được nên rủi ro thấp. | `Field(max_length=2_796_204)` cho `data` (≈ 4·⌈2 MiB/3⌉) và giới hạn ngắn cho `filename` — ACCEPT_LATER hoặc FIX khi có task bảo mật |
| TODO-02 | Low | `frontend/src/pages/AdminMovies.jsx:151-164` | Upload thành công nhưng tạo/sửa phim thất bại → (a) file mồ côi, mỗi lần bấm Lưu lại tạo thêm một file; (b) lỗi của bước tạo phim cũng hiện dưới ô "Chọn ảnh", dễ hiểu nhầm là lỗi ảnh. File mồ côi đã được chấp nhận trong Out of Scope. | Giữ `poster_url` đã upload trong state để lần lưu sau không upload lại; chỉ gán `poster_file` khi lỗi đến từ bước upload — ACCEPT_LATER |
| TODO-03 | Low | `frontend/src/pages/AdminMovies.jsx:32` | Regex client chấp nhận `data:image/...` ở cả Real Mode (backend sẽ từ chối); câu lỗi client vẫn chỉ nói "phải bắt đầu bằng http:// hoặc https://" dù đường dẫn nội bộ cũng hợp lệ. Chỉ là chênh lệch thông báo. | WONT_FIX hoặc ACCEPT_LATER |
| TODO-04 | Low | `backend/tests/test_poster_upload.py:85-87` | `test_create_requires_poster_and_accepts_links` chỉ so `detail`, không assert `status_code == 422`; test mới chưa phủ PUT với `poster_url` sai (Claude đã kiểm bằng probe). | Bổ sung assert khi có task test kế tiếp — ACCEPT_LATER |

## 11. Quan sát (không cần sửa trong T19)
- **OBS-01:** `StaticFiles` phục vụ toàn bộ `UPLOAD_DIR` (không riêng `posters/`) và không đặt `X-Content-Type-Options: nosniff`. Content-Type lấy theo đuôi do server chọn (`image/*`), file luôn có magic bytes ảnh, nên nguy cơ XSS qua polyglot rất thấp. Ghi nhận cho đợt hardening trước deploy (Q4).
- **OBS-02:** Mock lưu data URL trong localStorage; mỗi ảnh ≤ ~683 KB base64, vài lần upload có thể chạm quota ~5 MB của trình duyệt. Chỉ ảnh hưởng mock/demo.
- **OBS-03:** `docs/tasks/T19.md` vẫn untracked (đã ghi trong file điều phối); PO quyết việc đưa vào Git.
- **OBS-04:** Đăng ký bằng email đuôi `.test` bị `EmailStr` từ chối (hành vi có từ trước, không thuộc T19).

## 12. Required Fixes
**0.**

## 13. Bàn giao task kế tiếp
**Không mở.** Theo `AGENT_RULES.md` mục 1.1, task kế tiếp trong thứ tự là **T12**, nhưng T12 đang `PLANNED / NOT AUTHORIZED` và Q4 (deploy) còn **MỞ**; T19 cũng là task "phát triển thêm" ngoài chuỗi chính. Giữ tiền lệ review T17/T18. Tín quyết task tiếp theo sau PO review.

## 14. Việc của Tín
1. PO review T19, disposition TODO-01..04 và OBS-01..04.
2. Nếu APPROVED: `git checkout master` → `git merge task/T19-tai-anh-poster`.
3. Kiểm tra tiến trình uvicorn đang chiếm cổng 8001 (mục 2) và tắt nếu không còn dùng.
