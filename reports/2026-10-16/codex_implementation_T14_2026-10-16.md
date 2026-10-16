# Codex Implementation Report — T14

- Ngày: 16/10/2026
- Nhánh: `task/T14-huy-ve-tai-khoan`
- Baseline: `master` tại `5c10522`
- Trạng thái bàn giao: `CLAUDE_REVIEW`
- Đổi schema: Không

## 1. Phạm vi đã thực hiện

- Thêm `DELETE /api/bookings/{id}`. Endpoint gọi `expire_holds` trước, chỉ tra vé theo đồng thời `booking_id` và `user_id`, trả cùng 404 cho vé không tồn tại/vé người khác, và chỉ xóa vé `held` còn hạn.
- Khi hủy hợp lệ, dùng lại `release_booking_seats`, xóa booking và trả ghế về sơ đồ; không tạo logic giữ chỗ thứ hai.
- Thêm `PATCH /api/auth/me` để đổi họ tên với giới hạn 2–100 ký tự như đăng ký.
- Thêm `POST /api/auth/change-password`; mật khẩu mới 6–100 ký tự, mật khẩu hiện tại sai trả 400 `"Mật khẩu hiện tại không đúng."`.
- Thêm trang `/tai-khoan`, liên kết trong menu tài khoản, hai form đổi họ tên/mật khẩu. Auth context cập nhật user ngay nên tên mới hiện lập tức trên Header.
- Thêm nút `Hủy vé` chỉ trong khối vé `held`, có `window.confirm`; sau khi thành công tải lại danh sách.
- Đồng bộ hàm, response thành công và mã lỗi liên quan giữa `real.js`/`mock.js`.
- Thêm pytest cho hủy vé, quyền sở hữu, các trạng thái không được hủy, hold quá hạn, đổi mật khẩu, sai mật khẩu hiện tại, đổi họ tên và giới hạn trường.

## 2. Acceptance Criteria

| AC | Kết quả | Bằng chứng |
|---|---|---|
| AC-01 | PASS | API thật trên SQLite tạm: ghế A1 có trong `booked_seats` trước hủy và không còn sau hủy; pytest kiểm booking và booking_seats đã xóa. |
| AC-02 | PASS | Pytest: vé người khác/không tồn tại 404; `paid`, `pending_verify`, `expired`, và `held` quá hạn đều 409 đúng câu tiếng Việt; UI chỉ render nút trong nhánh `status === "held"`. |
| AC-03 | PASS | API thật và pytest: mật khẩu mới đăng nhập 200, mật khẩu cũ 401; token hiện có vẫn gọi `/api/auth/me` được. |
| AC-04 | PASS | Full pytest 95/95; build real/mock PASS; API mock có cùng `updateMe`, `changePassword`, `bookings.remove`. |
| AC-05 | PASS | Checklist hồi quy 7/7 bên dưới. |

## 3. Quality gate

| Gate | Kết quả |
|---|---|
| `python -m compileall -q backend/app` | PASS |
| Backend startup + `/api/health` | PASS — `status=ok`, active model `phobert_b`, port 8014, SQLite tạm |
| Focused pytest | PASS — 19/19 trước lượt full; test T14 bổ sung tiếp tục PASS trong full suite |
| Full pytest | PASS — 95/95, 1 deprecation warning từ Starlette; pytest có cảnh báo dọn symlink temp Windows sau exit code 0 |
| `npm run build` | PASS — 84 modules |
| `VITE_USE_MOCK=true; npm run build` | PASS — 84 modules |
| Mock dev smoke | PASS — Vite mock mode phục vụ `/` và module mock HTTP 200; endpoint T14 hiện diện; build mock PASS |
| API thật thủ công | PASS — đổi tên; đổi mật khẩu; login mới 200/cũ 401; tạo/hủy held và ghế trống lại |
| Scope/secret | PASS — chỉ file allowlist; không có `.env`, `*.db`, backup hay model trong diff |

DB gate được tạo bằng `backend/scripts/reset_demo.py` với `DATABASE_URL=sqlite:///C:/Projects/firefly-cinema/backend/t14_gate.db` và `ADMIN_PASSWORD` riêng. Sau gate đã tắt backend và xóa `t14_gate.db` cùng sidecar. Không chạy backend trên `backend/firefly.db` thật.

## 4. Checklist hồi quy 7/7

1. PASS — Trang chủ/danh sách phim và định tuyến frontend build được ở real và mock.
2. PASS — Chi tiết phim, suất chiếu và API đọc sơ đồ ghế không hồi quy trong full pytest.
3. PASS — Đặt vé held vẫn hoạt động; quy tắc cutoff, trùng ghế và tối đa hai hold vẫn PASS.
4. PASS — Vé của tôi hiển thị trạng thái/QR như trước; hủy held cập nhật danh sách và trả ghế.
5. PASS — Đăng ký/đăng nhập/token và khóa đăng nhập T20 vẫn PASS; tài khoản đổi tên/mật khẩu hoạt động.
6. PASS — Bình luận/chatbot/model health không đổi và full pytest PASS.
7. PASS — Các route admin, phân quyền 401/403 và luồng xác nhận/từ chối vé không hồi quy.

## 5. Hạn chế và lưu ý

- Đổi mật khẩu không làm token cũ hết hiệu lực. Token đã cấp tiếp tục hợp lệ tới khi hết hạn; đây là giới hạn được PO chấp nhận cho phạm vi T14 và đã có test xác nhận hành vi.
- Rate limiter/khóa đăng nhập của T20 không bị sửa; toàn bộ test T20 vẫn nằm trong full suite 95/95.
- Không đổi schema, không sửa `models.py`, `seats.py`, `classifier.py`, không thêm thư viện.

## 6. Bàn giao

- Open Required Fix: 0 ở phía implementer.
- Blocker: 0.
- Chờ Claude review độc lập; Codex không tự review, không tự PASS và không mở T13.
