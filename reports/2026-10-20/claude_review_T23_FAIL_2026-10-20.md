# Claude Independent Review — T23 (Round 1)

- Task: T23 — Tổng quan quản trị và soát vé tại quầy
- Nhánh: `task/T23-tong-quan-soat-ve` · commit review: `e2d82be` · baseline `master` `3afbf42`
- Ngày: 2026-10-20 · Reviewer: Claude
- **Kết luận: FAIL** — 1 Required Fix (Medium, AC-02), 1 TODO Medium, 3 OBS. Phần còn lại đạt.

## 1. Phạm vi và quy tắc
- 20 file, tất cả trong allowlist T23 mục 6. Không có `.env`, `*.db`, model trong Git; không thêm thư viện; `booking_rules.py`, `seats.py`, `classifier.py` không đổi.
- Endpoint mới có ở cả `real.js` và `mock.js`; tập khóa JSON của `dashboard` (top, `movies[]`, `daily[]`) giống hệt nhau giữa real và mock.
- Mọi endpoint mới dùng `require_admin`; lỗi trả câu tiếng Việt. Đổi schema (`checked_in_at`, `checked_in_by`) đã ghi trong `HUONG_DAN.md`.

## 2. Gate độc lập
| Gate | Kết quả |
|---|---|
| compileall | exit 0 |
| pytest | **141 passed** |
| npm run build | đạt |
| Backend DB tạm mới | health `ok`, `phobert_b` |
| Mock | đạt |
| Probe tạm (`scratchpad/probe_t23*.py`, ngoài repo) | đã chạy; working tree sạch |

## 3. Đối chiếu Acceptance Criteria
| AC | Kết quả | Bằng chứng |
|---|---|---|
| AC-01 | PASS | API khớp SQL độc lập cho 7/30/90 ngày: doanh thu, vé paid/chờ/hủy, ghế đã bán, lượt chấm (`match=True` cả 3) |
| AC-02 | **FAIL** | Doanh thu +230.000, vé paid +1, ghế +2, doanh thu phim 1 +230.000 đúng; nhưng **tỷ lệ lấp ghế phim 1 giữ nguyên 0,0365** — xem RF-01 |
| AC-03 | PASS | 7/30/90 ngày đủ cột; nhãn trục không đè nhau ở 1280px và 375px (0 overlap); trang không tràn ngang (375 = 375), bảng theo phim cuộn trong khung |
| AC-04 | PASS | Vé `held` → 409 "Vé chưa thanh toán, đang giữ chỗ."; xác nhận paid → soát lần 1 200 (kèm tên admin), lần 2 → 409 "Vé đã được soát lúc 20:53 20/10/2026."; mã chữ thường và có khoảng trắng vẫn nhận; `FF99999`, `abc` → 404. Cập nhật có điều kiện trong một câu `UPDATE` nên không soát trùng khi bấm đồng thời |
| AC-05 | PASS | User thường: dashboard/GET/POST checkin → 403; không token → 401 |
| AC-06 | PASS | "Vé của tôi" hiện "Đã vào rạp lúc 20:53, Thứ 3 20/10/2026" (xem TODO-01 về cách lấy dữ liệu) |
| AC-07 | PASS | Mock: dashboard đủ khóa; soát vé lần 1 ok, lần 2 409, không tìm thấy 404 |
| AC-08 | PASS | 141/141, gồm test mới cho dashboard và soát vé |
| AC-09 | PASS | Trang cũ không đổi hành vi; build và pytest cũ đạt |

## 4. Required Fixes
### RF-01 — Tỷ lệ lấp ghế không phản ánh vé vừa bán
- **Severity:** Medium (AC-02 không đạt)
- **File:** `backend/app/routers/admin_dashboard.py` (`capacities`, `occupied`), `frontend/src/api/mock.js` (`admin.dashboard`), `frontend/src/pages/AdminDashboard.jsx` (dòng chú thích)
- **Problem:** Lấp ghế chỉ tính các suất có `start_time` trong N ngày **đã qua** (tới hết hôm nay). Vé bán hôm nay gần như luôn cho suất sắp chiếu, nên không bao giờ làm tăng tỷ lệ; khi demo, cột "Lấp ghế" đứng yên dù vừa bán vé.
- **Evidence:** DB tạm 20/10/2026: đặt FF00144 (suất 22:00 24/10, 2 ghế), admin xác nhận → doanh thu phim 1 +230.000 nhưng `occupancy` 0,036458 → 0,036458.
- **Nguồn gốc:** Task Record T23 mục 3A (Claude soạn) ghi "theo `showtimes.start_time`" mà không nói rõ có gồm suất sắp chiếu, mâu thuẫn với AC-02. Codex làm đúng câu chữ mục 3A; lỗi thuộc đặc tả, sửa theo AC-02.
- **Expected Fix:** Tính lấp ghế trên các suất có `start_time >= đầu khoảng` (gồm cả suất sắp chiếu, không chặn trên), ở cả backend và mock; sửa dòng chú thích thành "tỷ lệ lấp ghế tính trên các suất từ đầu khoảng thời gian, gồm suất sắp chiếu". Thêm pytest: bán + xác nhận vé cho suất tương lai → `occupancy` của phim tăng đúng `ghế / (số suất × sức chứa)`.

## 5. TODO
- **TODO-01 (Medium, cần PO duyệt mở rộng phạm vi) — `TicketStub` gọi lại API cho từng vé.** Mỗi vé `paid` tự gọi `api.bookings.mine()` để lấy `checked_in_at`, dù danh sách vé đã có sẵn trường này. Đo trên trình duyệt: 2 vé paid → `/api/bookings/me` bị gọi 6 lần (dev StrictMode); mỗi lần chạy `expire_holds` + commit. Nguyên nhân: allowlist T23 (Claude soạn) thiếu `frontend/src/pages/MyTickets.jsx`, nên Codex không truyền prop được. Đề xuất: PO cho phép sửa `MyTickets.jsx` để truyền `checkedInAt={b.checked_in_at}` xuống `TicketStub` và bỏ lời gọi API trong `TicketStub`.

## 6. Quan sát
- **OBS-01:** Soát vé được cho vé paid của suất còn vài ngày nữa (soát ngày 20/10 cho suất 24/10). Task Record không yêu cầu chặn theo giờ chiếu; nếu PO muốn, chặn ngoài khoảng ví dụ 60 phút trước giờ chiếu đến khi suất kết thúc.
- **OBS-02:** Mã vé dùng lại (T14 TODO-02, đã biết): vé held bị hủy rồi đặt mới có thể nhận lại cùng mã (FF00144 trong probe). Vì vé bị hủy chưa từng paid nên soát vé không bị nhầm, nhưng khách cầm mã cũ có thể bối rối.
- **OBS-03:** `AdminCheckin.jsx` và `AdminDashboard.jsx` dồn nhiều logic vào ít dòng, khó đọc; thông báo 409 ở mock có giây (`20:55:31`) còn real thì không. Không ảnh hưởng chức năng.

## 7. Trạng thái
T23 `CLAUDE_REVIEW → FIX_LOOP`. RF-01 bắt buộc; TODO-01 chờ PO duyệt mở rộng allowlist thêm `frontend/src/pages/MyTickets.jsx`.

## 8. Prompt Codex cho vòng sửa
```text
Bạn là Codex, dự án Firefly Cinema (C:\Projects\firefly-cinema), nhánh task/T23-tong-quan-soat-ve.
Đọc reports/2026-10-20/claude_review_T23_FAIL_2026-10-20.md và docs/tasks/T23.md.
1. RF-01: tỷ lệ lấp ghế tính trên các suất có start_time >= đầu khoảng thời gian (gồm suất sắp chiếu, không chặn trên) ở backend/app/routers/admin_dashboard.py và mock.js; sửa dòng chú thích trong AdminDashboard.jsx. Thêm pytest: bán + admin xác nhận vé cho suất tương lai → occupancy phim tăng đúng ghế/(số suất × sức chứa).
2. [Nếu PO duyệt mở rộng allowlist thêm frontend/src/pages/MyTickets.jsx] TODO-01: MyTickets truyền checkedInAt={b.checked_in_at} xuống TicketStub; bỏ lời gọi api.bookings.mine() trong TicketStub.
Chỉ sửa file trong allowlist T23 (cộng MyTickets.jsx nếu PO duyệt). Gate: compileall, pytest, npm run build (real + mock), mock mode. Commit "[T23] Fix RF-01 ...", viết reports/YYYY-MM-DD/codex_fix_T23_round2_YYYY-MM-DD.md, đặt T23 về CLAUDE_REVIEW. Không merge.
```
