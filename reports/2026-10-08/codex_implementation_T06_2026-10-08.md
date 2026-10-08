# Báo cáo implementation T06 — 08/10/2026

## 1. Task, branch và baseline

- Task ID: `T06` — Kiểm duyệt có người duyệt.
- Branch: `task/T06-kiem-duyet`.
- Baseline: `0b244b034fed4c17dbe5d054c5bba4c5ca654382` (`master`).
- T05 merge `54a3715` đã được xác minh là ancestor của baseline.
- Implementation commit: `942d7197ed5c104e6267446866822c2a2b165401`.
- Trạng thái: `IN_PROGRESS / PENDING_PO_DATABASE_RESET`; chưa đủ điều kiện chuyển `CLAUDE_REVIEW`.

## 2. File thay đổi

- `backend/app/models.py`
- `backend/app/schemas.py`
- `backend/app/routers/comments.py`
- `frontend/src/pages/AdminComments.jsx`
- `frontend/src/components/CommentSection.jsx`
- `frontend/src/api/real.js`
- `frontend/src/api/mock.js`
- `frontend/src/styles/global.css`
- `docs/ARCHITECTURE.md`
- `HUONG_DAN.md`
- `docs/TASK_COORDINATION_ACTIVE.md`
- `reports/2026-10-08/codex_implementation_T06_2026-10-08.md`

Không sửa `classifier.py`, `seats.py`, `.env`, database, model hoặc dữ liệu lớn.

## 3. Chức năng đã triển khai

- Bổ sung `human_label`, `reviewed_by`, `reviewed_at`, `hidden` cho `comments`; có CHECK constraint chỉ nhận nhãn 0/1/null.
- Giữ nguyên ba trường model `is_negative`, `negative_score`, `model_name` trong mọi thao tác duyệt.
- Admin confirm/relabel/hide/unhide; danh sách lọc theo nhãn model và trạng thái duyệt; phân trang tối đa 100.
- Thống kê reviewed/agree/disagree/accuracy và TP/FP/TN/FN trên các dòng có human label hợp lệ.
- CSV UTF-8 BOM gồm đúng `text,text_norm,label`, chỉ xuất bình luận đã duyệt; `text_norm` dùng `normalize()` hiện hành.
- API công khai bỏ bình luận `hidden=true`, trả `effective_negative` và `reviewed`; human label được ưu tiên.
- Trang quản trị có thao tác, thống kê, tải CSV, loading/empty/error, phân trang và bố cục mobile.
- Real API và mock API có cùng contract; mock localStorage cũ được bổ sung trường mới khi load.

## 4. API contract

- `PATCH /api/admin/comments/{id}` — body `{action: confirm|relabel|hide|unhide, label?: 0|1}`; relabel thiếu/sai label trả 422 tiếng Việt.
- `GET /api/admin/comments?label=&reviewed=&page=1&page_size=20` — `{items,total}`; `page_size` từ 1 đến 100.
- `GET /api/admin/comments/stats` — `{reviewed,agree,disagree,accuracy,tp,fp,tn,fn}`.
- `GET /api/admin/comments/export.csv` — UTF-8 BOM, cột `text,text_norm,label`.
- `GET /api/movies/{id}/comments` — chỉ dòng không bị ẩn, bổ sung `effective_negative`, `reviewed`.
- Tất cả endpoint admin mới dùng `require_admin`: anonymous 401, user thường 403.

## 5. Đổi schema và Q2

- Đổi schema: **CÓ**.
- Q2: **RESOLVED / NO ALEMBIC / BACKUP_BEFORE_RESET**.
- Development và probe schema chỉ chạy trên database tạm `%TEMP%/firefly_t06_probe/firefly_t06.db` (đã dọn tiến trình sau test), không reset database thật.

## 6. Database backup evidence

- DATABASE_URL hiệu lực: `sqlite:///./firefly.db` khi backend chạy từ `backend`.
- Database thật: `C:\Projects\firefly-cinema\backend\firefly.db`, 102400 byte, thời điểm sửa cuối trước/sau implementation vẫn là `2026-10-08 21:11:56 +07:00`.
- Trước backup: backend process = 0; listener cổng 8000 = 0; `PRAGMA integrity_check=ok`.
- Nguồn có bảng `booking_seats, bookings, comments, movies, showtimes, users`; số dòng lần lượt `280, 140, 16, 21, 270, 3`.
- Backup: `C:\Projects\firefly-cinema\backup\T06\firefly_pre_T06_20261008_234417.db` (bị `.gitignore` loại khỏi Git).
- Thời điểm: `2026-10-08T23:44:17+07:00`; kích thước 102400 byte.
- SHA-256: `c27abfcad23c2c53bd1b2f827dce8aed541a64838d00c9ce0d6543dc0a3e23bc`.
- Xác minh backup: mở read-only được; `PRAGMA integrity_check=ok`; đủ sáu bảng và số dòng khớp nguồn; schema comments cũ đúng trạng thái trước T06.
- Database reset: **PENDING_PO**. Codex không chạy `Remove-Item` với database thật.
- Lệnh reset/khởi động/kiểm tra chính xác đã ghi tại `HUONG_DAN.md` mục 2.1.

## 7. Focused tests

- Backend compileall: PASS.
- Frontend Vite build: PASS, 69 modules.
- Backend thật (Uvicorn) trên DB tạm khởi động với `classifier=phobert`; `/api/health` trả 200/ok: PASS.
- Schema DB tạm có đủ 12 cột comments; integrity `ok`; ghi `human_label=2` bị CHECK constraint chặn: PASS.
- Bộ 4 dòng TP/FP/TN/FN: stats trả `reviewed=4, agree=2, disagree=2, accuracy=0.5, tp=1, fp=1, tn=1, fn=1`: PASS.
- Relabel model-negative thành 0: public trả `effective_negative=false`; hide loại khỏi API công khai; unhide hiện lại: PASS.
- Trước/sau confirm/relabel/hide, `is_negative` và `negative_score` so sánh bằng nhau: PASS.
- Relabel thiếu label: 422, `Đổi nhãn cần label là 0 hoặc 1.`: PASS.
- `page_size=500`: 422; contract max 100: PASS.
- CSV real: bytes đầu `EF BB BF`, header đúng 3 cột, 4/4 dòng đều đã duyệt: PASS.
- Permission real cho list/stats/export/PATCH: anonymous 401 và user thường 403 ở cả 4 endpoint: PASS.
- Mock module: đủ thao tác, stats 1/1/1/1, relabel/hide, paging 422, user 403, CSV BOM: PASS.
- Trình duyệt headless mock: 12 dòng tải thành công, đủ nút confirm/relabel/hide, confirm cập nhật stats, lọc reviewed còn đúng 1 dòng, không có exception runtime: PASS.
- Responsive 375x812: document width = viewport 375; bảng cuộn trong `.table-wrap` (347/1120), stats 2 cột, nút CSV rộng 347: PASS.

## 8. Final quality gates

- `backend\venv\Scripts\python.exe -m compileall -q backend\app`: PASS.
- Backend start + `/api/health` trên DB thử nghiệm: PASS.
- `frontend; npm run build`: PASS.
- Real API moderation/permissions/CSV/stats: PASS trên DB tạm.
- Mock API + browser probe: PASS.
- `git diff --check`: PASS (chỉ warning line ending LF/CRLF của Git, không có whitespace error).
- Allowlist/scope scan: PASS; implementation commit chỉ có 11 file allowlist.
- Secret/database/model scan: PASS; không có `.env`, `*.db`, CSV, model hoặc secret mới trong diff.
- Gate phụ thuộc database thật sau reset/seed: **PENDING_PO_DATABASE_RESET**.

## 9. Acceptance Criteria

| AC | Kết quả DEV | Evidence |
|---|---|---|
| AC-01 | PASS | Bốn ca duyệt/hide giữ nguyên `is_negative`, `negative_score`; model fields không bị gán trong PATCH. |
| AC-02 | PASS | Relabel negative→0 public effective false; hide vắng mặt; unhide hiện lại. |
| AC-03 | PASS | Bộ kiểm đủ TP/FP/TN/FN, mỗi ô = 1, accuracy = 0.5. |
| AC-04 | PASS | CSV real/mock BOM, đúng `text,text_norm,label`, chỉ 4 dòng reviewed. |
| AC-05 | PASS | 4 endpoint mới: anonymous 401, user 403. |
| AC-06 | PASS | `page_size=500` trả 422 rõ ràng ở real/mock. |
| AC-07 | PASS | Mock module và browser probe đạt đủ thao tác, stats, filter, CSV. |
| AC-08 | PENDING | Hướng dẫn DB đã có; regression trên DB tạm/mock đạt phần kiểm được, nhưng reset/seed và regression cuối trên DB thật chờ PO. |

Tổng: **7/8 DEV PASS**, không tuyên bố full PASS.

## 10. Regression checklist 7 mục

1. Trang chủ/dữ liệu phim: API tạm trả 21 phim, 9 đang chiếu; frontend build PASS. Tương tác poster cuối trên DB thật: PENDING PO reset.
2. Tìm `meo muop`: trả đúng `Mèo Mướp Đi Lạc`: PASS.
3. Đăng ký + `/auth/me`: PASS; redirect UI cuối trên DB thật: PENDING.
4. Đặt 2 ghế A1/A2, mở lại thấy booked và Vé của tôi có booking mới: PASS trên DB tạm.
5. Bình luận `Ko hay như quảng cáo, hơi thất vọng`: `effective_negative=true`, score 0.9937; logic UI ẩn theo effective label và admin contract/build đạt: PASS trên DB tạm.
6. `/api/health`: `status=ok`, `classifier=phobert`: PASS trên DB tạm.
7. `VITE_USE_MOCK=true`: module + browser moderation/responsive probe: PASS.

Kết luận regression cuối: **PARTIAL / PENDING_PO_DATABASE_RESET** do các bước UI real cuối chưa được phép chạy trên DB thật mới.

## 11. Security và scope

- Admin routes dùng `require_admin`; probe 401/403 đầy đủ.
- Không thêm thư viện.
- Không sửa `normalize()`; CSV import trực tiếp hàm hiện hành.
- Không sửa file ngoài allowlist; không commit backup/database/model/secret.
- T07 giữ `PLANNED / NOT AUTHORIZED`.

## 12. Blockers, Required Fixes và TODO

- Open blocker: 1 — `PENDING_PO_DATABASE_RESET`.
- Required Fixes: 0 tại thời điểm implementation; chưa qua independent Claude review.
- TODO bắt buộc: PO chạy reset/seed theo `HUONG_DAN.md` 2.1; Codex xác minh schema/dữ liệu DB thật, chạy regression UI real còn lại, cập nhật report/coordination rồi mới chuyển `CLAUDE_REVIEW`.

## 13. Commit

- Implementation commit: `942d7197ed5c104e6267446866822c2a2b165401` — `[T06] Implement human comment moderation`.
- Report/coordination commit: được tạo sau report này.

## 14. Handoff status

- Handoff: **BLOCKED / PENDING_PO_DATABASE_RESET**.
- Claude Review: PENDING.
- PO Approval: PENDING.
- Next Task: NOT AUTHORIZED.
