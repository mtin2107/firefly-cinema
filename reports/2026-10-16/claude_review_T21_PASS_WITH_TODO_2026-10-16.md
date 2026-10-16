# Claude Review — T21 — PASS_WITH_TODO — 16/10/2026

- Nhánh: `task/T21-thong-ke-cam-xuc`, commit `34e1aed` (1 commit trên `master` `0a717e9`).
- Report Codex: `reports/2026-10-16/codex_implementation_T21_2026-10-16.md` (bằng chứng phụ).
- Mọi probe dùng SQLite tạm trong scratchpad của Claude, tạo bằng `reset_demo.py`; không chạm `backend/firefly.db`.

## 1. Scope

13 file, tất cả trong Allowed Files của T21.md: `admin_sentiment.py` (mới), `main.py`, `schemas.py`, `test_sentiment.py` (mới), `AdminSentiment.jsx` (mới), `App.jsx`, `Header.jsx`, `real.js`, `mock.js`, `global.css`, `ARCHITECTURE.md`, file điều phối, report. Không sửa `models.py`, `classifier.py`, `routers/comments.py`. `package.json`, `requirements*.txt` không đổi. Không đổi schema. Không có `.env`, `*.db`, model trong commit.

## 2. Kiểm tra code

- Endpoint dùng `require_admin`; `days` 1..365, ngoài khoảng → `HTTPException(422, "Số ngày thống kê phải từ 1 đến 365.")`.
- Nhãn hiệu lực `CASE human_label IS NOT NULL THEN human_label ELSE is_negative` — cùng nghĩa với `effective_negative` ở `routers/comments.py:40`. Không lọc `hidden`, nên bình luận ẩn vẫn được tính.
- 3 truy vấn SQL `GROUP BY` (summary, theo phim, theo ngày), không nạp toàn bộ bình luận. `daily` lấp đủ `days` ngày, gồm hôm nay và `days − 1` ngày trước.
- Frontend chỉ import từ `src/api`; `real.js` và `mock.js` cùng có `api.admin.sentiment(days)`. Mock tính từ bộ bình luận mock, không viết cứng số.
- Biểu đồ SVG thuần, có `role="img"` + `aria-label`, kèm bảng số liệu có `caption`. Màu vàng/đỏ theo T18.

## 3. Gate độc lập

| Gate | Kết quả |
|---|---|
| `compileall -q backend/app` | exit 0 |
| pytest đầy đủ | **85 passed**, 1 warning thư viện (81 cũ + 4 mới) |
| `npm run build` | đạt |
| Backend trên DB demo tạm | health `phobert_b` |
| Quyền | không token 401, `demo@firefly.vn` 403, `days=abc` 422 tiếng Việt |
| Đối chiếu SQL độc lập (dữ liệu demo T12) | 7 ngày: API 15/8, đã duyệt 8, khớp 0,75 = SQL `(15, 8, 8, 6)`; 30 và 90 ngày: API 30/18/8/0,75 = SQL `(30, 18, 8, 6)`; từng phim khớp cả 3 khoảng; `daily` đủ 7/30/90 phần tử, tổng daily = tổng summary |
| Gửi bình luận tiêu cực mới (demo user, phim 4) | 7 ngày: 15/8 → 16/9; hôm nay +1; phim 4 từ 0/2 → 1/3 |
| Giao diện 1280px (real) | 4 ô tóm tắt, thanh theo phim, biểu đồ + bảng; đổi 7/30/90 cập nhật cả 3 phần; trang không tràn ngang |
| Giao diện 375px (real) | 7/30/90 đều không tràn ngang; biểu đồ và bảng cuộn trong khung riêng |
| Console | không lỗi (real và mock) |
| Mock mode (`VITE_USE_MOCK=true`) | trang hiển thị đủ, cùng cấu trúc JSON |

## 4. Acceptance Criteria

| AC | Kết quả |
|---|---|
| AC-01 401/403/422 | PASS |
| AC-02 pytest dữ liệu biết trước, `human_label` | PASS (`test_sentiment.py`) |
| AC-03 `daily` đủ ngày, ngày trống = 0 | PASS |
| AC-04 đúng số liệu với dữ liệu demo T12, đổi 7/30/90 | PASS (đối chiếu SQL độc lập) |
| AC-05 không tràn ngang 375/1280, không lỗi console | PASS |
| AC-06 mock mode | PASS |
| AC-07 không thêm thư viện | PASS |
| AC-08 compileall, pytest, build, hồi quy | PASS |

## 5. Required Fix

Không có.

## 6. TODO (không chặn)

- **TODO-01 — Medium — nên sửa trước khi chụp ảnh cho báo cáo (T13 AC-03):** biểu đồ theo ngày dùng khoảng cách cố định 24 đơn vị/ngày. Ở 1280px: khoảng **30 ngày (mặc định)** có 17/30 nhãn ngày chạm hoặc đè nhau (rộng 27,8 px, cách nhau 28,2 px); khoảng **7 ngày** chỉ vẽ trong khoảng 190 px giữa khung 1094 px nên trông trống; khoảng **90 ngày** rộng 2553 px, phải cuộn ngang mới xem hết. Không vi phạm AC-05 (trang không tràn) nhưng đây là trang trình diễn chính. Gợi ý: co giãn theo bề rộng khung, thưa nhãn ngày khi dày.
- **TODO-02 — Low:** mock tính trên `fakeClassify` nên tỷ lệ tiêu cực mock (23,3%) khác số thật (60%). `KICH_BAN_DEMO.md` (phần dự phòng) nên nói rõ số liệu mock chỉ minh họa.
- **TODO-03 — Low:** `test_sentiment.py` tạo bình luận "1 giờ" và "2 giờ trước" rồi khẳng định chúng thuộc **hôm nay**; chạy pytest trong khoảng 00:00–02:00 sẽ fail.
- **TODO-04 — Low:** `AdminSentiment` không hủy request cũ khi đổi 7/30/90 nhanh, nên phản hồi đến muộn có thể ghi đè. Các nút dùng `role="tab"` nhưng không có `tabpanel`.
- **TODO-05 — Low — điều phối:** dòng T12 trong `TASK_COORDINATION_ACTIVE.md` còn nguyên chỗ trống `TODO-01: PO chọn <a / b / c>`, do chỗ cần điền trong prompt chưa được điền. Tín cần ghi quyết định thật.

## 7. Kết luận

**PASS_WITH_TODO.** RF 0, blocker 0. T21 `CLAUDE_REVIEW → PO_REVIEW`.

## 8. Bàn giao task kế tiếp

Lộ trình cuối (15/10/2026): `T21 → T14 → T13`. **T14** phụ thuộc T20 (CLOSED); PO đã chọn làm từ 15/10, nên không còn là task tùy chọn bị chặn. T14 → `READY_FOR_HANDOFF`.

Câu hỏi mở trong T14.md mục 13: đổi mật khẩu có làm token cũ hết hiệu lực không. Prompt dưới dùng đề xuất mặc định của Task Record: **không**, ghi vào hạn chế. Nếu Tín muốn khác thì sửa dòng đó trong prompt.

**Tín làm trước khi gửi prompt:**
1. PO review T21, quyết định TODO-01..05 (nếu muốn sửa TODO-01 trước khi merge, báo Claude để soạn prompt fix).
2. `git checkout master` → `git merge --no-ff task/T21-thong-ke-cam-xuc -m "[T21] Merge sentiment statistics"`.
3. `git checkout -b task/T14-huy-ve-tai-khoan`.

**Prompt Codex cho T14:**

```text
Bạn là Codex, Primary Implementer của dự án Firefly Cinema.
Chỉ đọc: docs/PROJECT_SOURCE_OF_TRUTH.md, docs/AGENT_RULES.md, docs/TASK_COORDINATION_ACTIVE.md (Snapshot, Status, lộ trình cuối 15/10),
docs/tasks/T14.md, backend/app/routers/bookings.py, backend/app/routers/auth.py, backend/app/booking_rules.py (expire_holds,
release_booking_seats), backend/app/security.py, backend/app/rate_limit.py, backend/app/schemas.py, backend/app/models.py (chỉ đọc),
frontend/src/pages/MyTickets.jsx, frontend/src/components/TicketStub.jsx, frontend/src/context/AuthContext.jsx,
frontend/src/api/real.js, frontend/src/api/mock.js, và source/test liên quan trực tiếp.

Bước 0 (đồng bộ điều phối theo PO): T21 đã được PO duyệt và merge vào master tại <hash merge T21>.
Cập nhật TASK_COORDINATION_ACTIVE.md: T21 -> DONE / CLOSED. Thay chỗ trống TODO-01 của T12 bằng quyết định PO: <a / b / c>.

Thực hiện T14 trên nhánh task/T14-huy-ve-tai-khoan (tạo từ master sau merge T21), chỉ sửa file trong mục 6 Allowed Files của T14.md.
Thư mục gốc duy nhất: C:\Projects\firefly-cinema.

Yêu cầu chính:
1. DELETE /api/bookings/{id}: chỉ chủ vé (vé người khác hoặc không tồn tại -> 404, không lộ tồn tại);
   gọi expire_holds trước; chỉ vé held còn hạn, còn lại -> 409 "Chỉ hủy được vé đang giữ chỗ chưa thanh toán.";
   xóa booking cùng booking_seats để ghế trống lại. Dùng lại release_booking_seats/expire_holds, không viết logic giữ chỗ thứ hai.
2. PATCH /api/auth/me {full_name} (cùng ràng buộc độ dài với đăng ký);
   POST /api/auth/change-password {current_password, new_password} (new_password >= 6 ký tự như đăng ký;
   mật khẩu hiện tại sai -> 400 câu tiếng Việt). Không làm token cũ hết hiệu lực; ghi vào mục hạn chế trong report.
   Không làm yếu cơ chế rate limit/khóa đăng nhập của T20.
3. Nút "Hủy vé" chỉ ở vé held trong "Vé của tôi", có hộp xác nhận; sau khi hủy, danh sách cập nhật và ghế trống lại trên sơ đồ.
   Trang /tai-khoan đổi họ tên và mật khẩu, thêm liên kết trong menu tài khoản; họ tên mới hiện ngay trên Header.
   Không đổi thiết kế đã chốt; class mới thêm vào global.css.
4. real.js và mock.js cùng hàm, cùng cấu trúc JSON và cùng mã lỗi (404/409/400) cho các endpoint mới.
5. pytest: hủy hợp lệ -> ghế trống; vé người khác 404; paid / pending_verify / expired -> 409; held quá hạn -> 409;
   đổi mật khẩu -> đăng nhập mật khẩu mới được, mật khẩu cũ bị từ chối; mật khẩu hiện tại sai 400; đổi họ tên.

Cấm: sửa models.py, seats.py, classifier.py; thêm thư viện; đổi schema; sửa hoặc commit backend/.env, *.db, backup\, model.
Không chạy backend trên backend/firefly.db thật; kiểm tay bằng DB tạm tạo qua backend/scripts/reset_demo.py
(DATABASE_URL trỏ file tạm, ADMIN_PASSWORD trong môi trường).
Chạy gate theo AGENT_RULES.md mục 3: compileall, backend khởi động + health, pytest đầy đủ, npm run build, mock mode, checklist hồi quy 7/7.
Tạo reports/<YYYY-MM-DD>/codex_implementation_T14_<YYYY-MM-DD>.md: ghi "Đổi schema: Không", hạn chế token, checklist hồi quy.
Cập nhật TASK_COORDINATION_ACTIVE.md: T14 READY_FOR_HANDOFF -> IN_PROGRESS -> CLAUDE_REVIEW.
Commit dạng "[T14] mô tả". Không tự review, không tự PASS, không mở task kế tiếp. Trả lời bằng tiếng Việt.
```
