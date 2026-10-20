# Codex Independent Review — T23 Fix Round 2

- Ngày: 2026-10-20.
- Phạm vi: phần sửa của Claude, `git diff 5b1bc40..5d334ae`.
- Nhánh: `task/T23-tong-quan-soat-ve`; HEAD khi review: `5d334ae`; working tree ban đầu sạch.
- **Kết luận: PASS.** RF-01 và TODO-01 CLOSED / VERIFIED BY CODEX.
- Review độc lập phần sửa của Claude theo yêu cầu PO; không sửa production code hoặc test, không merge.

## Kết quả kiểm tra

| Mục | Bằng chứng độc lập |
|---|---|
| RF-01 backend | `capacities` và `occupied` cùng dùng `Showtime.start_time >= start`, không chặn trên; tử số chỉ paid, mẫu số lấy sức chứa từ seats.py. Doanh thu vẫn giữ khoảng bookings.created_at. |
| RF-01 probe biên | SQLite in-memory riêng: suất trước đầu khoảng 1 giây bị loại, đúng đầu khoảng được tính, suất +120 ngày được tính. Hai ghế paid sẵn trên hai suất hợp lệ → 2/192; thêm hai ghế held không tăng; chuyển paid → 4/192, doanh thu +160.000đ. |
| RF-01 mock | Điều kiện chọn suất cùng backend. Browser tạo vé hai ghế cho suất sau hơn hai ngày rồi admin xác nhận: delta occupancy `0.0012254901960784314`, đúng `2/(17*96)`. |
| Chú thích | AdminDashboard ghi rõ tính trên suất từ đầu khoảng, gồm suất sắp chiếu. |
| TODO-01 | TicketStub không import API, không gọi bookings.mine; nhận `checkedInAt = null`. MyTickets truyền `checkedInAt={b.checked_in_at}`; nội dung giờ vào rạp vẫn hiển thị. |
| Số lần tải | Browser mock: bọc api.bookings.mine bằng bộ đếm, điều hướng SPA Home → Vé của tôi: đúng 2 lần do StrictMode, không tăng theo số thẻ paid. |
| Checkout | Browser chọn ghế → Tiếp tục → Xác nhận đặt vé: TicketStub hiển thị bình thường khi không truyền checkedInAt, không hiện dòng giờ vào rạp, page errors = []. |

## Gates chạy lại

| Gate | Kết quả |
|---|---|
| `backend\venv\Scripts\python -m compileall -q backend\app` | exit 0 |
| `cd backend; venv\Scripts\python -m pytest -q --basetemp=C:/Users/lemin/AppData/Local/Temp/firefly_t23_independent_review` | **142 passed**, 50,52 giây; 1 warning Starlette/AnyIO đã có |
| `cd frontend; $env:VITE_USE_MOCK='false'; npm run build` | exit 0, 89 modules |
| `cd frontend; $env:VITE_USE_MOCK='true'; npm run build` | exit 0, 89 modules |
| Browser Chrome + Vite mock 5123 | RF-01, MyTickets và Checkout đạt; không lỗi JavaScript |

Pytest dùng SQLite tạm qua conftest; probe backend dùng SQLite in-memory.
Không mở, reset hoặc ghi DB thật; không sửa .env, không thêm thư viện.
Probe/scripts nằm trong `%TEMP%`, không thêm vào source/test trong repo.

## Scope

- Diff có 8 file: 5 production files, 1 test, điều phối và báo cáo sửa của Claude.
- 6 file source/test đều thuộc allowlist T23 + MyTickets.jsx đã được PO duyệt
  rõ trong prompt review này. Không đụng classifier/seats/booking_rules/schema hoặc dependencies.
- Hai file còn lại là TASK_COORDINATION_ACTIVE và artifact provenance
  `claude_fix_T23_round2_2026-10-20.md` được PO yêu cầu đọc/review.
- Phiên review này chỉ ghi report Codex và cập nhật điều phối; code/test giữ nguyên commit `5d334ae`.

## Ghi chú không chặn

- OBS-01..03 của review Round 1 giữ nguyên, không mở rộng phần sửa.
- ARCHITECTURE.md đoạn T23 vẫn mô tả cách lấy metadata cũ (request/thẻ paid)
  và khoảng ngày suất cũ. Đây là tài liệu chưa đồng bộ; source và chú thích giao diện
  đã đúng. Không sửa tài liệu kiến trúc trong phiên review theo yêu cầu không sửa code.
- Không có schema mới trong Round 2. Yêu cầu PO backup/xác minh rồi xóa
  `backend\firefly.db` để áp dụng schema T23 ban đầu vẫn còn; reviewer không thực hiện.

## Handoff

T23 → **PO_REVIEW**, review độc lập phần sửa hoàn tất. Required Fix mở: 0.
Chờ Tín quyết định PO; không merge, không mở task tiếp theo.
