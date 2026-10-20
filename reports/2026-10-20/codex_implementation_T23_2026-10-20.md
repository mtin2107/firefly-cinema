# Codex Implementation Report

Task: T23 — Tổng quan quản trị và soát vé tại quầy
Date: 2026-10-20
Result: IMPLEMENTATION_COMPLETED — chờ Claude Independent Review
Branch: `task/T23-tong-quan-soat-ve`
Baseline: `3afbf42` (T22 đã PO merge; HEAD khi bắt đầu, working tree sạch)
Đổi schema: **Có**.

## Files Changed / Implemented

- Backend: models/schemas/main, admin_dashboard.py, admin_checkin.py,
  admin_bookings.py (chỉ bổ sung metadata), bookings.py (chỉ bổ sung output),
  tests/test_t23_dashboard_checkin.py.
- Frontend: real.js/mock.js, App/Header/TicketStub, AdminDashboard/AdminCheckin,
  chỉ thêm class trong global.css.
- Tài liệu: HUONG_DAN.md, ARCHITECTURE.md, TASK_COORDINATION_ACTIVE.md và report này.
- Tổng quan gồm sáu thẻ số, SVG doanh thu đủ ngày, bảng từng phim và bộ chọn 7/30/90.
  Soát vé có tra cứu, lý do từ chối tiếng Việt, giờ vào rạp và người thực hiện.

## Architecture / Contract

- Mọi endpoint mới dùng require_admin. Dashboard gọi expire_holds trước thống kê;
  số liệu tính bằng SQL sum/count/group_by, chỉ lặp kết quả gộp/ngày/phim.
  Query-count test xác nhận không tăng theo số vé paid.
- Doanh thu/số vé/ghế bán theo bookings.created_at; lấp ghế theo start_time của suất,
  mẫu số len(ROWS) × COLS từ seats.py. Ratings/comments theo created_at.
  Khoảng gồm hôm nay, [00:00 ngày đầu, 00:00 ngày mai); dữ liệu rỗng trả 0.
- Tỷ lệ tiêu cực dùng human_label ưu tiên, nếu chưa duyệt dùng is_negative,
  tính cả bình luận hidden như T21. T21 chưa tách helper nên dùng cùng biểu thức SQL.
- POST checkin dùng UPDATE WHERE status='paid' AND checked_in_at IS NULL;
  một request thắng, request còn lại 409 và giờ đã soát. Không đổi trạng thái paid.
- Real/mock có cùng dashboard keys, movie keys, daily keys và metadata vé.
- MyTickets.jsx ngoài allowlist: TicketStub tự gọi bookings.mine khi hiển thị vé paid
  để lấy checked_in_at. Có thêm một request/thẻ paid; không đổi MyTickets hoặc booking_rules.
  Thông tin lấy khi mở trang; không có cập nhật trực tiếp nếu quầy soát trong lúc trang vẫn mở.

## Bằng chứng AC (mức DEV, không phải independent review)

| AC | Bằng chứng |
|---|---|
| AC-01 | Parametrized 7/30/90 ngày đối chiếu SQL độc lập trạng thái, SUM(total), COUNT ghế và AVG/COUNT ratings trên cùng DB tạm; vé ở mốc 6/7/29/30/89/90 ngày; stale held tự expired; số liệu ghế theo suất được kiểm riêng. |
| AC-02 | API tạo vé A1/A2 → admin confirm: +160.000đ, +1 paid, +2 ghế, occupancy +2/96; tạo rồi hủy held không làm tăng doanh thu. |
| AC-03 | Chrome headless: real/mock × 375/1280 × 7/30/90; số rect = số ngày; bounding boxes nhãn không giao nhau, document.scrollWidth = viewport. Xem ảnh và chỉnh biểu đồ theo ResizeObserver để nhãn không bị cắt. |
| AC-04 | Tests GET/POST mã thường; paid soát một lần, lưu admin; lần hai 409 có giờ. held/pending_verify/expired/rejected 409 lý do tương ứng; mã thiếu/sai/quá dài 404. Hai Session SQLite đồng thời: [200,409]. Browser real/mock có success, second=409, missing=404. |
| AC-05 | Parametrized cả ba method/path: không token 401, user 403. |
| AC-06 | API /bookings/me trả đúng checked_in_at đã lưu. Browser real/mock đăng nhập demo và xác nhận dòng “Đã vào rạp lúc …” hiện trong Vé của tôi. |
| AC-07 | Browser mock đủ dashboard mọi khoảng, tra cứu/soát vé, lỗi và Vé của tôi; đối chiếu keys với real khớp; build cả hai mode. |
| AC-08 | 23 case mới; full suite 141/141 (118 test cũ giữ nguyên). Có empty dashboard, invalid days và query-count không tăng theo số vé. |
| AC-09 | Hồi quy trình duyệt + API real/mock theo bảng dưới; PhoBERT B thật trên DB tạm. |

## Focused Tests / Final Gates

- Focused: `cd backend; venv\Scripts\python -m pytest -q tests/test_t23_dashboard_checkin.py`
  → **23 passed**, 1 warning Starlette/AnyIO đã có.
- Compile: `backend\venv\Scripts\python -m compileall -q backend\app` → exit 0.
- Backend thật: uvicorn port 8023, DATABASE_URL trỏ duy nhất
  `C:/Users/lemin/AppData/Local/Temp/firefly_t23_runtime.db`;
  UPLOAD_DIR cũng tạm, FRONTEND_ORIGIN override cho frontend kiểm thử 5124.
  `/api/health` → status=ok, classifier=phobert_b,
  active_version=phobert-B-2026-10-09.
- Full: `cd backend; venv\Scripts\python -m pytest -q --basetemp=C:/Users/lemin/AppData/Local/Temp/firefly_t23_pytest_release`
  → **141 passed**, 1 warning Starlette/AnyIO; SQLite test riêng cho mỗi fixture.
- Build: `VITE_USE_MOCK=false` và `true` qua biến môi trường PowerShell,
  `npm run build` cả hai exit 0; không sửa .env hay thêm package.
- Browser: Chrome cài sẵn + Playwright runtime có sẵn bên ngoài repo;
  dashboard/checkin không tràn ngang ở 375/1280, page errors = [].
- Format/scope: `git diff --check` đạt; không có linter riêng trong dự án.

## Checklist hồi quy

| Mục | Kết quả real / mock |
|---|---|
| 1. Home/hero/poster | Hero tự đổi; Xem chi tiết và Đặt vé hiện intro, Esc đóng được. |
| 2. Menu/tìm kiếm | Lọc thể loại Hài có phim; tìm “meo muop” có kết quả đúng. |
| 3. Auth/return path | Đăng ký mới, vào suất khi chưa đăng nhập → login, đăng nhập quay lại đúng /dat-ve/{id}. |
| 4. Đặt vé | UI chọn hai ghế → checkout → Vé của tôi; mở suất lại hai ghế disabled. |
| 5. Bình luận | Câu “Ko hay như quảng cáo, hơi thất vọng” ẩn mặc định trong UI; admin xem được, real score 0.9992, mock 0.87 (dữ liệu giả). |
| 6. Health | status ok, phobert_b, version B đúng cấu hình hiện hành; checklist cũ ghi phobert được hiểu theo quyết định Q3. |
| 7. Mock | Chạy đủ luồng trên Vite mock 5123, real 5124. |

## Security / Scope

- Không sửa classifier/seats/booking_rules, không thêm thư viện; không ghi, xóa,
  reset hoặc khởi động backend trên database thật. Không sửa seed/model/.env.
- Không đưa credentials/token/DB/model vào commit. Scope chỉ mục 6 T23.
- **PO cần sao lưu, xác minh checksum/integrity và khả năng phục hồi trước khi
  xóa `backend\firefly.db`, rồi khởi động lại để tạo schema mới.** Đã ghi bước xóa
  trong HUONG_DAN.md; Codex không thực hiện thao tác đó.

## Evidence artifacts

Ảnh nằm ngoài repo theo allowlist; các đường dẫn dùng trên máy hiện tại:
`C:/Users/lemin/.codex/visualizations/2026/10/20/01a15978-644d-7ae1-b4b5-e19d3e4cc3f5/`

- `T23-real-375.png`, `T23-real-1280.png`, `T23-mock-375.png`, `T23-mock-1280.png`
- `T23-checkin-real-375.png`, `T23-checkin-real-1280.png`,
  `T23-checkin-mock-375.png`, `T23-checkin-mock-1280.png`
- Browser logs/scripts tạm: `%TEMP%\codex_T23_browser.log`,
  `%TEMP%\codex_T23_regression.log` và hai script `.cjs` cùng tên.
  Tests có thể tái lập từ repo; ảnh/log tạm không phải artifact portable trong Git.

## Blockers / Required Follow-up / TODO

- Blocker kỹ thuật: 0. Required fix do Claude: chưa có (chưa review).
- PO ACTION: backup/reset DB thật sau khi duyệt schema, trước chạy demo schema T23.
- Hạn chế: metadata vé paid cần request bổ sung/thẻ do allowlist không chứa MyTickets.jsx.

## Handoff

T22 ghi DONE / CLOSED theo PO merge `3afbf42`; T23 → CLAUDE_REVIEW.
Chờ Claude kiểm tra độc lập; Codex không tự PASS, PO approve, merge hoặc mở T13.
