# Claude fix — T31 round 2 (29/10/2026)

Người viết code: **Claude**. Reviewer: **Codex**. Nhánh `task/T31-sua-low`, baseline `dad5ff9` (Codex review round 2 FAIL). Review: `reports/2026-10-29/codex_review_T31_FAIL_2026-10-29_round2.md`. Round 2 của Codex: RF-01 CLOSED, AC-01/02/03/05/06/07 PASS, chỉ còn RF-02.

## RF-02 (Medium) — SOS khai báo độ dài 0/1 vẫn được nhận
- **Nguyên nhân:** chỉ chặn độ dài vượt quá file, không chặn độ dài quá nhỏ và không kiểm cấu trúc header SOS.
- **Sửa** (`backend/app/routers/admin_posters.py` `_jpeg_complete`, `frontend/src/api/mock.js` `jpegComplete`, cùng luật):
  - Mọi segment: độ dài < 2 → từ chối (độ dài luôn gồm 2 byte của chính nó).
  - SOS: số thành phần Ns (byte sau độ dài) phải từ 1 đến 4, độ dài phải đúng `6 + 2 × Ns` (chuẩn JPEG), `end <= len(data)`, rồi mới tìm FFD9 từ `end`.
  - Giữ nguyên: byte đệm FF, dữ liệu thừa sau EOI thật, file kết thúc bằng FFD9.
- **Test (`test_t31_low_fixes.py`):** bộ `TRUNCATED` (chạy cho cả poster và ảnh đại diện, kỳ vọng 422 và không ghi file) thêm 2 mẫu của Codex (SOS độ dài 0 và 1), SOS 5 thành phần, SOS độ dài lệch số thành phần, segment APP độ dài 0. `VALID_EXTRA` (poster 201): byte đệm FF trước SOS, SOS 3 thành phần + dữ liệu sau EOI.
- **Mock:** script Node trên 14 mẫu (7 cũ + 7 mới): 14/14 đúng. Cùng script trên `mock.js` của `a805395`: 4 mẫu RF-02 trả `true` (tái hiện lỗi).

## Gate (Claude, 29/10/2026)
| Gate | Kết quả |
|---|---|
| Focused `test_t31_low_fixes` + `test_poster_upload` + `test_t29_account` | 59 passed |
| compileall | exit 0 |
| Full `pytest -q` (13:36:53 → 13:40:02 +07:00) | **286 passed** |
| `npm run build` real / `VITE_USE_MOCK=true` | đạt / đạt |
| Node `jpegComplete` 14 mẫu | 14/14 |

## Phạm vi
File đổi: `admin_posters.py`, `mock.js`, `test_t31_low_fixes.py`, file này, `TASK_COORDINATION_ACTIVE.md`. Đều trong allowlist. Không đổi schema. Không chạm phần UI đã PASS ở round 2.

## Prompt Codex review round 3
```text
Bạn là Codex, reviewer độc lập cho T31 round 3 dự án Firefly Cinema (C:\Projects\firefly-cinema, Windows + PowerShell). Claude viết code theo lệnh PO; bạn review, không sửa production code, không merge, không mở task.
Đọc: reports/2026-10-29/codex_review_T31_FAIL_2026-10-29_round2.md (review của bạn), reports/2026-10-29/claude_fix_T31_round2_2026-10-29.md.
Diff vòng sửa: git diff dad5ff9..task/T31-sua-low. Round 2 đã PASS AC-01/02/03/05/06/07; vòng này chỉ đổi validator JPEG (backend + mock) và test.
1. Xác minh RF-02: chạy lại ma trận HTTP poster/avatar của bạn (SOS độ dài 0/1, RF-01 gốc, byte đệm FF, dữ liệu sau EOI thật, scan bị cắt) và mock trên trình duyệt (lưu poster). Thử thêm biên: SOS Ns = 0/4/5, độ dài SOS lệch Ns, segment APP độ dài 0/1.
2. Gate: compileall, full pytest (trong backend\), npm run build real + mock. DB/UPLOAD_DIR tạm, không đụng backend/firefly.db, không đọc .env.
Kết luận PASS / PASS_WITH_TODO / FAIL. Viết reports/YYYY-MM-DD/codex_review_T31_<RESULT>_YYYY-MM-DD_round3.md, cập nhật file điều phối: PASS → PO_REVIEW, FAIL → FIX_LOOP. Commit "[T31] Codex review round 3 ...".
```
