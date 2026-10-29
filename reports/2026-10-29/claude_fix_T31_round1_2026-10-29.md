# Claude fix — T31 round 1 (29/10/2026)

Người viết code: **Claude**. Reviewer: **Codex**. Nhánh `task/T31-sua-low`, baseline `ca881af` (Codex review FAIL). Review: `reports/2026-10-29/codex_review_T31_FAIL_2026-10-29.md`.

## RF-01 (Medium) — FFD9 trong header SOS được tính là EOI
- **Nguyên nhân:** khi gặp SOS, code tìm FFD9 từ `i + 2` (ngay trong header SOS) thay vì sau hết segment SOS theo độ dài khai báo.
- **Sửa:** `backend/app/routers/admin_posters.py` `_jpeg_complete` và `frontend/src/api/mock.js` `jpegComplete`: tính `end = i + 2 + độ dài segment` cho mọi segment. Với SOS: yêu cầu `end <= len(data)` và chỉ tìm FFD9 từ `end`. Giữ nguyên nhánh "file kết thúc bằng FFD9" và hỗ trợ dữ liệu thừa sau EOI thật. Ảnh đại diện dùng chung `validate_image` nên cũng được sửa.
- **Test (`backend/tests/test_t31_low_fixes.py`):** bộ `TRUNCATED` thêm đúng mẫu của Codex (`SOS_HEADER_EOI`) và mẫu SOS khai báo dài hơn file. Chạy cho **poster** (422, không tạo thư mục posters) và **ảnh đại diện** `PUT /api/auth/me/avatar` (422, không có file avatar). Thêm test ảnh đại diện nhận JPEG có dữ liệu sau EOI (200, file ghi đúng byte).
- **Mock:** script Node chạy `jpegComplete` trích từ `mock.js` trên 7 mẫu giống backend: 7/7 đúng. Cùng script trên `mock.js` ở `b57e274`: mẫu Codex trả `true` (tái hiện lỗi), nên script phân biệt được bản lỗi và bản sửa.

## Gate (Claude, 29/10/2026)
| Gate | Kết quả |
|---|---|
| Focused `test_t31_low_fixes` + `test_poster_upload` + `test_t29_account` | 49 passed |
| compileall | exit 0 |
| Full `pytest -q` (13:01:09 → 13:04:05 +07:00) | **276 passed** |
| `npm run build` real / `VITE_USE_MOCK=true` | đạt / đạt |
| Node `jpegComplete` 7 mẫu | 7/7 |

## Phạm vi
File đổi: `admin_posters.py`, `mock.js`, `test_t31_low_fixes.py`, file này, `TASK_COORDINATION_ACTIVE.md`. Đều trong allowlist mục 6 T31.md. Không đổi schema.

## Còn chờ Codex
Codex ghi các phần kiểm trên trình duyệt chưa chạy độc lập: form trailer (AC-01/02), header 360/375/421px khi đăng nhập admin (AC-05), Tổng quan 800/862/1100/1101/1280px (AC-06), mock mode. Bằng chứng của Claude ở `claude_implementation_T31_2026-10-29.md` mục 4 không thay được phần kiểm độc lập này.

## Prompt Codex review round 2
```text
Bạn là Codex, reviewer độc lập cho T31 round 2 dự án Firefly Cinema (C:\Projects\firefly-cinema, Windows + PowerShell). Claude viết code theo lệnh PO; bạn review, không sửa production code, không merge, không mở task.
Đọc: docs/tasks/T31.md, reports/2026-10-29/codex_review_T31_FAIL_2026-10-29.md (review của bạn), reports/2026-10-29/claude_fix_T31_round1_2026-10-29.md.
Diff vòng sửa: git diff ca881af..task/T31-sua-low; diff toàn task: git diff master...task/T31-sua-low.
1. Xác minh RF-01: chạy lại probe của bạn cho poster, ảnh đại diện và mock; thêm vài mẫu biên (SOS độ dài 0/1, nhiều byte đệm FF, dữ liệu thừa sau EOI thật).
2. Hoàn tất các bước kiểm trình duyệt còn pending ở round 1, trên DB/UPLOAD_DIR tạm (không đụng backend/firefly.db; đặt ADMIN_PASSWORD thử qua biến môi trường, không đọc .env): AC-01/02 form trailer, AC-05 header 360/375/421px khi đăng nhập admin, AC-06 Tổng quan 800/862/1100/1101/1280px, mock mode (upload poster JPEG có dữ liệu sau EOI và JPEG bị cắt).
3. Gate: compileall, full pytest (chạy trong backend\), npm run build real + mock.
Kết luận PASS / PASS_WITH_TODO / FAIL. Viết reports/YYYY-MM-DD/codex_review_T31_<RESULT>_YYYY-MM-DD_round2.md, cập nhật file điều phối: PASS → PO_REVIEW, FAIL → FIX_LOOP. Commit "[T31] Codex review round 2 ...".
```
