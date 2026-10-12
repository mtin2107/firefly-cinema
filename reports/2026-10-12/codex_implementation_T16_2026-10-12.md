# Codex Implementation Report — T16

- Ngày: 12/10/2026
- Nhánh: `task/T16-giu-cho-thanh-toan`
- Base: `master` tại `f67f72e`
- Vai trò: Codex — Primary Implementer
- Trạng thái bàn giao: `CLAUDE_REVIEW`
- **Đổi schema: Có** — thêm `bookings.status VARCHAR(20)` với check constraint 5 trạng thái.

## 1. Kết quả triển khai

- Backend có quy tắc dùng chung `HOLD_CUTOFF_MINUTES = 30`, mã vé `FF` + ID đệm 5 số, VietQR và hủy lười.
- Vé `held` hết hạn chuyển thành `expired` và xóa thật các dòng `booking_seats`; vé admin từ chối cũng xóa ghế. Ràng buộc `UNIQUE(showtime_id, seat_code)` được giữ nguyên.
- Thêm transfer claim cho chủ vé; admin liệt kê/lọc/tìm tối đa 200 vé mới nhất, xác nhận hoặc từ chối với đúng 401/403/404/409.
- API real và mock có cùng các hàm `bookings.claimTransfer`, `admin.bookings.list/confirm/reject` và cùng cấu trúc JSON.
- Giao diện có thời hạn cụ thể ở trang xác nhận, mã/trạng thái/QR/nút báo chuyển khoản ở Vé của tôi, và trang `/quan-tri/ve` đầy đủ loading/rỗng/lỗi/lọc/thao tác.
- Seed booking được gán `paid`; kiểm tra xóa phim bỏ qua booking `expired`/`rejected`.
- Không thêm thư viện, không sửa luật ghế, classifier, `normalize()` hoặc biến màu `:root`.

## 2. Bằng chứng Acceptance Criteria

| AC | Kết quả | Bằng chứng DEV |
|---|---|---|
| AC-01 | PASS | `test_new_booking_contract_and_one_hold_per_showtime`: 201, `held`, mã `FFxxxxx`, hạn = giờ chiếu − 30 phút; GET sơ đồ trả ghế đã đặt. |
| AC-02 | PASS | `test_expired_hold_releases_unique_seat_for_another_user`: GET sơ đồ kích hoạt hủy, booking thành `expired`, `booking_seats=0`, tài khoản khác đặt lại cùng ghế được 201. |
| AC-03 | PASS | `test_pending_and_paid_are_not_expired`: cả `pending_verify` và `paid` vẫn giữ ghế sau hạn. |
| AC-04 | PASS | Test trả 400 đúng câu trong 30 phút cuối và 409 đúng câu khi cùng tài khoản tạo vé `held` thứ hai cho cùng suất. |
| AC-05 | PASS | `test_transfer_claim_ownership_and_invalid_state`: chủ vé chuyển sang `pending_verify`; người khác 404; gọi lại/sai trạng thái 409. |
| AC-06 | PASS | `test_admin_list_security_confirm_reject_and_release`: confirm/reject đúng bảng chuyển trạng thái, reject xóa ghế; anonymous 401, user 403. |
| AC-07 | PASS | `test_qr_url_configured_and_missing`: URL đúng ngân hàng/tài khoản, amount, code, accountName; thiếu cấu hình trả `null`. |
| AC-08 | PASS (build + kiểm tra mã) | Route/menu/trang admin, Checkout, MyTickets và TicketStub đã nối; real build PASS. Chờ Claude/PO kiểm tra trực quan độc lập trên trình duyệt. |
| AC-09 | PASS | Probe trực tiếp lớp mock chạy `held → pending_verify → paid`, admin tìm đúng 1 vé `FF00001`, QR có giá trị; mock build PASS. |
| AC-10 | PASS | `test_delete_movie_ignores_expired_or_rejected_bookings` trả 200; real và mock đều bỏ qua hai trạng thái này. |
| AC-11 | PASS | Full pytest `36 passed`: 28 test T11 cũ + 8 test T16 mới. |
| AC-12 | PASS DEV | Checklist hồi quy mục 4 dưới đây đạt 7/7 bằng full pytest, build real/mock, health DB tạm và mock flow; chưa tự review. |

## 3. Quality gates — AGENT_RULES 3.1

Focused chạy trước full:

- `python -m compileall -q backend/app`: PASS.
- Focused `pytest tests/test_booking_payment.py tests/test_bookings.py`: **12 passed**.
- Full `pytest -q`: **36 passed**, 1 warning deprecation Starlette/anyio đã tồn tại, không có failure.
- Backend thật trên `sqlite:///./t16_gate_tmp.db`: startup PASS; `/api/health` 200, `status=ok`; `integrity_check=ok`; DDL có cột/default/check constraint đúng. DB và sidecar gate tạm đã xóa sau khi dừng backend.
- Frontend build real: PASS, 71 modules.
- Frontend build mock với `VITE_USE_MOCK=true`: PASS, 71 modules.
- Mock flow: PASS `held → pending_verify → paid`; tìm theo code và QR PASS.
- `git diff --check`: PASS (chỉ có cảnh báo chuyển LF/CRLF của Git trên Windows, không có whitespace error).
- Scope: chỉ các file trong Allowed Files của T16.
- Bí mật/file lớn: không có `.env`, `*.db`, model hoặc CSV trong thay đổi; không thêm dependency.

## 4. Checklist hồi quy 7 mục

| # | Hạng mục | Kết quả / bằng chứng |
|---|---|---|
| 1 | Trang phim, danh sách, tìm/lọc và suất chiếu | PASS — full pytest cũ; router phim giữ contract; build real/mock PASS. |
| 2 | Đăng ký, đăng nhập và phân quyền | PASS — pytest cũ; endpoint admin vé mới cũng đạt 401/403. |
| 3 | Chọn ghế, giá thường/VIP và chống trùng | PASS — test booking cũ + T16; UNIQUE giữ nguyên. |
| 4 | Đặt vé và xem Vé của tôi | PASS — vé mới hiểu là `held`; sơ đồ xám, lịch sử/trạng thái/hạn/QR đúng contract. |
| 5 | Hủy quá hạn/trả ghế và đặt lại | PASS — test SQLite tạm chứng minh xóa `booking_seats` và đặt lại ghế 201. |
| 6 | Bình luận, classifier và health | PASS — test T11 cũ; health trên DB tạm 200, classifier fallback an toàn. |
| 7 | Trang quản trị phim/suất/bình luận/vé, real và mock | PASS — full pytest, build hai mode và mock payment flow. |

## 5. Database thật — PO phải tự thực hiện

T16 **không** chạy, xóa, reset, seed hoặc restore `backend\firefly.db` thật. PO thực hiện đúng `HUONG_DAN.md` mục 2.2:

1. Dừng backend, xác nhận `DATABASE_URL` và không còn listener cổng 8000.
2. Tạo backup timestamp mới; sao lưu `firefly.db` cùng `firefly.db.showtime-seed.json` như một cặp.
3. Đối chiếu SHA-256 nguồn/bản sao; backup phải `integrity_check=ok`, `foreign_key_check` rỗng, counts hợp lý và đọc phục hồi được.
4. Sau khi chấp nhận reset làm mất dữ liệu runtime cũ, PO tự loại đúng DB + sidecar khỏi đường dẫn chạy; không xóa backup.
5. Khởi động backend tạo DB mới; xác minh schema `bookings.status`, constraint, seed `paid`, health, integrity và FK.
6. Có lỗi thì dừng, giữ file lỗi và chỉ restore đúng cặp khi PO authorize; không tự import booking cũ.

## 6. Giới hạn đã công bố

- Admin list giới hạn 200 vé mới nhất, đúng phương án cho phép trong Task Record.
- `pending_verify` giữ ghế đến khi admin xử lý; web không tự đối soát ngân hàng.
- Ảnh QR phụ thuộc `img.vietqr.io`; nếu dịch vụ lỗi, mã vé và lựa chọn thanh toán tại quầy vẫn còn.
- DEV không tự kết luận review/PASS; AC-08 trực quan cần Claude/PO xác minh độc lập.
