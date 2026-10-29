# Claude implementation — T31 Sửa 6 mục Low trước v1.0 (29/10/2026)

Người viết code: **Claude** (PO yêu cầu trong chat 29/10/2026). Reviewer: **Codex** (độc lập). Nhánh `task/T31-sua-low`, baseline master `a772cdf`. Task Record: `docs/tasks/T31.md`.

## 1. Việc làm trước T31 (theo lệnh PO)
- **Reset DB thật T29 + T30.** Không có backend nào chạy. Sao lưu `firefly.db` và `firefly.db.showtime-seed.json` vào `backup\T30-20261029-121409\` kèm `db-sha256.csv`; SHA-256 nguồn = bản sao (`DDB0C547…7E06`, `1FEFA47C…2564`); `integrity_check` = ok, `foreign_key_check` rỗng trên bản sao chỉ đọc. Không có `backend\uploads\`. Xóa `firefly.db`, khởi động uvicorn để seed lại: `users` có `birth_date`, `gender`, `avatar_url`; `bookings` có `AUTOINCREMENT`; integrity ok; health `classifier: phobert_b`. Đã dừng backend. **Không** chạy bước "đặt → hủy → đặt lại" trên DB thật để giữ dữ liệu demo sạch (đã có test tự động T30).
- Xóa thư mục `firefly-cinema/` (bản clone chưa track nằm trong repo, commit `b361d2a`, `git status` sạch) theo quyết định PO.

## 2. Thay đổi
| ID | File | Nội dung |
|---|---|---|
| FX-01 (T25 TODO-01) | `AdminMovies.jsx` | `selectVideo` không gọi `clearVideo()` trước; chỉ xóa ô file khi file bị từ chối. |
| FX-02 (T25 TODO-02) | `AdminMovies.jsx` | `uploadedTrailer` = trailer bắt đầu bằng `/uploads/trailers/` (thật) hoặc `blob:` (mock). Ô YouTube hiện trống + "Đang dùng video đã tải lên."; `form.trailer_url` giữ nguyên nên lưu không mất trailer; gõ link mới thì thay thế. |
| FX-03 (T27 TODO-01) | `schemas.py` | `ScoreInput.allow_empty_score: ClassVar[bool] = False`, `CommentIn` = True; bỏ so sánh `cls.__name__`. |
| FX-04 (T30 TODO-01) | `admin_posters.py`, `mock.js` | `_jpeg_complete` / `jpegComplete`: nhận nếu kết thúc bằng FFD9 (giữ hành vi cũ, fixture cũ vẫn đạt); nếu không, đi theo độ dài segment từ SOI tới SOS rồi tìm FFD9 sau SOS. FFD9 nằm trong APP (ảnh thu nhỏ EXIF) không được tính. Áp dụng cho poster và ảnh đại diện (chung `validate_image`). |
| FX-05 (audit OBS-05) | `Header.jsx`, `global.css` | Label nút tài khoản = avatar/chữ viết tắt (`.header__avatar`, ẩn trên 420px) + tên (`.header__name`, ẩn kiểu sr-only ở ≤420px). ≤420px: gap 8px, logo 1.2rem. Desktop không đổi. |
| FX-06 (audit OBS-06) | `AdminDashboard.jsx`, `global.css` | Thẻ Điểm: `8.0 / 10` + dòng phụ `67 lượt chấm` (`small` có sẵn style). `.sentiment-summary--dashboard` 3 cột ở 861–1100px. Trang Thống kê cảm xúc không đổi. |
| Test | `backend/tests/test_t31_low_fixes.py` | JPEG có dữ liệu sau EOI → 201; 3 dạng JPEG hỏng → 422 và không ghi file; luật điểm theo cờ lớp, kể cả lớp con đổi tên. |

Không đổi schema, không thêm thư viện, không sửa `movies.json`, `seed.py`, `normalize()`.

## 3. Gate (Claude, 29/10/2026)
| Gate | Kết quả |
|---|---|
| `python -m compileall -q backend\app` | exit 0 |
| Focused: `test_t31_low_fixes`, `test_poster_upload`, `test_ratings`, `test_t29_account`, `test_comments_health` | 75 passed |
| Full `pytest -q` (12:27:26 → 12:30:31 +07:00) | **268 passed** (263 của T30 + 5 test T31) |
| `npm run build` (real) | đạt |
| `vite build` với `VITE_USE_MOCK=true` (outDir tạm) | đạt |
| `jpegComplete` mock chạy bằng Node trên 5 mẫu | `[true,false,false,false,true]` — khớp backend |

## 4. Kiểm trên trình duyệt (DB + UPLOAD_DIR tạm ở scratchpad, cổng 8007/5182, admin mật khẩu thử)
- AC-01: chọn `trailer-test.webm` → `input.files.length = 1`, hiện "Đã chọn: trailer-test.webm"; chọn `note.txt` → `files = 0`, lỗi "Chỉ nhận video MP4 hoặc WebM."; chọn lại webm và Lưu → "Đã cập nhật phim.".
- AC-02: mở lại phim 19: ô YouTube `""`, có "Đang dùng video đã tải lên." và nút Gỡ trailer; Lưu lại → API vẫn `/uploads/trailers/b886…fd7e.webm`.
- AC-05: admin "Quản trị viên" ở 375px: header 115px → **71px**, Menu cùng hàng (top 15), `scrollWidth = 375`; 360px: 71px, `scrollWidth = 360`.
- AC-06: Tổng quan ở 800 (2 cột), 862 và 1100 (3 cột), 1101 và 1280 (4 cột): 0 giá trị xuống dòng. Trước sửa ở 880px cả "23.310.000 đ" và "8.0 / 10 · 67 lượt" đều 2 dòng.
- Console: chỉ 2 lỗi `ERR_CONNECTION_REFUSED` lúc Claude khởi động lại backend tạm; không có lỗi JS.

**Chưa kiểm:** mock trên trình duyệt (chỉ build + Node), ảnh JPEG chụp từ điện thoại thật, trình đọc màn hình thật cho FX-05.

## 5. Ghi chú cho reviewer
- FX-04 cố ý giữ nhánh "kết thúc bằng FFD9" để không đổi hành vi với fixture và file đã được nhận trước đây.
- FX-05 thay `label` của `Dropdown` bằng JSX (Dropdown chỉ đặt label trong `<span className="dd__label">`), tên tài khoản vẫn nằm trong nút nên accessible name không đổi; chữ viết tắt `aria-hidden`.
- `.claude/launch.json` có thêm cấu hình `backend-t31` / `frontend-real-t31` (file bị `.git/info/exclude`, không commit).

## 6. Dọn dẹp
DB, uploads và bản build mock tạm nằm trong scratchpad phiên Claude, không trong repo. Backend 8000 trên DB thật đã dừng.

## 7. Prompt Codex review T31
```text
Bạn là Codex, reviewer độc lập cho T31 dự án Firefly Cinema (C:\Projects\firefly-cinema, Windows + PowerShell). Lần này Claude viết code theo lệnh PO, nên bạn review; không sửa production code, không merge, không mở task.
Đọc: docs/AGENT_RULES.md, docs/TASK_COORDINATION_ACTIVE.md, docs/tasks/T31.md, reports/2026-10-29/claude_implementation_T31_2026-10-29.md.
Diff thật: git diff master...task/T31-sua-low. Kiểm scope theo mục 6 T31.md.
Đối chiếu AC-01..07: chạy compileall, full pytest, npm run build (real + mock), mở trình duyệt trên DB/UPLOAD_DIR tạm (không đụng backend/firefly.db) để kiểm form trailer, header 360/375/421px khi đăng nhập admin, thẻ Tổng quan 800–1280px, và mock mode. Thử thêm JPEG có dữ liệu sau FFD9 và JPEG bị cắt cho cả poster lẫn ảnh đại diện.
Kết luận PASS / PASS_WITH_TODO / FAIL (RF có Severity, File, Problem, Evidence, Expected Fix). Viết reports/YYYY-MM-DD/codex_review_T31_<RESULT>_YYYY-MM-DD.md, cập nhật file điều phối: PASS → PO_REVIEW, FAIL → FIX_LOOP. Commit "[T31] Codex review ...".
```

## 8. Prompt Codex T13 (đã điền quyết định PO, gửi sau khi T31 merge)
```text
Bạn là Codex, dự án Firefly Cinema (C:\Projects\firefly-cinema, Windows + PowerShell).
Đọc theo thứ tự: docs/PROJECT_SOURCE_OF_TRUTH.md, docs/AGENT_RULES.md, docs/TASK_COORDINATION_ACTIVE.md, docs/tasks/T13.md. T13.md là bản PO đã duyệt.
T24–T31 đã merge vào master; DB thật đã reset ngày 29/10 (backup\T30-20261029-121409). Làm trên nhánh task/T13-v1 tạo lại từ master mới. Đầu tiên ghi closure T24–T31 (merge hash) và đặt T13 → IN_PROGRESS.

Quyết định PO (29/10/2026):
- T12 TODO-01 (model B che câu khen phim 1): giữ nguyên, ghi Hạn chế (ví dụ lệch miền).
- T14 TODO-02 mã vé dùng lại: ĐÃ SỬA ở T30 (BUG-02). T27 OBS-01 test_sentiment theo giờ: ĐÃ SỬA ở T30 (TEST-01).
- T25 TODO-01/02, T27 TODO-01, T30 TODO-01, audit OBS-05/06: ĐÃ SỬA ở T31.
- T28 OBS-01..03 (poster không bắt buộc, menu gọn ở ≤1360px, line-height tiêu đề): chấp nhận, ghi vào Hạn chế/ghi chú thiết kế.
- Audit 27/10 OBS-01 (vé chờ chuyển khoản không hết hạn, xác nhận được sau giờ chiếu), OBS-02 (soát vé không chặn theo ngày), OBS-03 (chưa khai ngày sinh vẫn đặt phim T18), OBS-04 (đổi mật khẩu/email không thu hồi token cũ), OBS-07 (số liệu mock ít hơn real), OBS-08 (độ khớp model ở Thống kê theo cửa sổ ngày, ở Kiểm duyệt toàn thời gian): ghi Hạn chế.

Nhiệm vụ: T13 "Chốt v1.0 và sao lưu" — chỉ tài liệu và sao lưu, không viết tính năng.
- README.md (giới thiệu, ảnh, tính năng gồm T16–T31; kết quả F1 A/B/SVM/NB/LR và T15; cách chạy nhanh), HUONG_DAN.md (cài từ số 0, gắn model A/B/SVM, cấu hình .env gồm BANK_* và CHAT_* — chỉ tên khóa, không giá trị; chạy test; reset demo; định dạng video trailer).
- Mục "Hạn chế" gom: các quyết định PO ở trên, T22 (ai đăng nhập cũng chấm điểm), T25 (file video mồ côi khi thay/gỡ; YouTube cần mạng; video mock mất khi tải lại), T29 (đổi email chưa xác minh qua thư; admin dùng chung), T30 (giới hạn 2 vé giữ chỉ đảm bảo khi chạy 1 worker uvicorn), T17 (chatbot Gemini chỉ MVP/local).
- docs/SAO_LUU.md gồm cả backend\uploads\ (poster, trailers, avatars) và bản backup DB 29/10; docs/images/* (≥ 8 ảnh, có Thống kê cảm xúc và So sánh mô hình), CHANGELOG.md [1.0.0], cập nhật cuối CONG_NGHE.md/ARCHITECTURE.md; xử lý T18 TODO-03 và T00 TODO-03 theo T13.md. AC-01 clone ra C:\Temp\firefly-test, không clone vào trong repo.
Ràng buộc: chỉ file trong mục 6 của T13.md; không sửa code; không commit model/DB/.env/video/ảnh tải lên/dữ liệu lớn; không đọc hay in giá trị khóa trong .env.
Gate: compileall, pytest, npm run build (real + mock) trên bản clone mới.
Commit "[T13] mô tả". Viết reports/YYYY-MM-DD/codex_implementation_T13_YYYY-MM-DD.md, đặt T13 sang CLAUDE_REVIEW. Không merge, không gắn tag v1.0 (Tín gắn).
```
