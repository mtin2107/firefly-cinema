# Codex Implementation — T20 (15/10/2026)

## 1. Kết quả triển khai

- Trạng thái bàn giao: `CLAUDE_REVIEW`.
- Đổi schema: Không.
- Không đọc/ghi `backend/firefly.db`; toàn bộ backend runtime dùng SQLite tạm và thư mục upload tạm, đã dọn sau gate.
- Không sửa `backend/.env`, `backend/app/models.py`, `backend/app/classifier.py`, `backend/app/seats.py` hoặc `frontend/src/utils/seats.js`.
- Không thêm thư viện.

## 2. Thay đổi chính

- Chặn backend khi `SECRET_KEY` trống, là khóa mặc định cũ hoặc ngắn hơn 32 ký tự; `.env.example` và `HUONG_DAN.md` có hướng dẫn sinh khóa.
- Seed admin đọc `ADMIN_PASSWORD`; khi thiếu vẫn dùng `admin123` cho môi trường dev và ghi cảnh báo.
- Thêm helper rate limit trong bộ nhớ; đăng nhập sai tối đa 5 lần/5 phút theo email và bình luận tối đa 3 lần/phút theo tài khoản. Rate limit bình luận chạy trước classifier.
- Hạn giữ vé dùng `min(created_at + 15 phút, start_time - 30 phút)`, trả ghế khi hết hạn, giới hạn 2 vé `held`, chặn báo chuyển khoản khi thiếu cấu hình QR; admin confirm/reject hết hạn vé trước khi xét trạng thái.
- Chatbot tìm thể loại không phân biệt hoa/thường, dấu và cho phép khớp một phần; mô tả tool dùng taxonomy chuẩn; model chat mặc định đổi sang `gemini-3.5-flash-lite`.
- Đồng bộ mock cho hạn giữ, giới hạn 2 vé, kiểm tra QR, rate limit bình luận và expire trước thao tác admin.
- Sửa UI vé, tabs, seatmap, vị trí/ẩn ChatWidget với admin, ngày `dd/mm/yyyy`, và tên mô hình dễ đọc.

## 3. Gate đã chạy

| Gate | Kết quả quan sát |
|---|---|
| Focused pytest | `46 passed, 1 warning` |
| Full pytest | `80 passed, 1 warning` |
| `compileall backend/app` | exit 0 |
| Frontend build real (`VITE_USE_MOCK=false`) | exit 0 |
| Frontend build mock (`VITE_USE_MOCK=true`) | exit 0 |
| Backend startup trên SQLite tạm | startup complete; `/api/health` trả 200, classifier fallback `keyword` do cố ý trỏ model test tới đường dẫn không tồn tại |
| Diff whitespace | `git diff --check` không có lỗi |

Cảnh báo pytest duy nhất là deprecation warning có sẵn của `starlette.testclient` về alias AnyIO; không có test fail.

## 4. Checklist hồi quy 7/7 — real mode

1. Trang chủ và danh sách/link phim render trong Chrome headless: đạt.
2. Đăng nhập user/admin, `/api/auth/me` và phân quyền admin: đạt.
3. Đặt vé/đọc Vé của tôi trên SQLite tạm, hạn giữ và trạng thái hiển thị: đạt.
4. Tạo bình luận; test rate limit và chatbot tìm "Hài hước"/"hài hước"/"hai huoc"/"Hài": đạt.
5. Vé không tràn ngang tại 375px và 1280px; thiếu QR không có nút "Tôi đã chuyển khoản": đạt.
6. `.tabs` và `.seatmap__scroll` có `overflow-y: hidden`: đạt.
7. Trang admin So sánh mô hình render và không có `.chat-widget`: đạt.

Kết quả quan sát: 7/7 mục hồi quy real mode đạt trong runtime tạm.

## 5. Checklist hồi quy 7/7 — mock mode

1. Trang chủ và danh sách/link phim render trong Chrome headless: đạt.
2. Đăng nhập mock và phân quyền user/admin: đạt.
3. Tạo vé mock, hạn giữ không quá 15 phút và Vé của tôi hiển thị: đạt.
4. Bình luận mock lần thứ tư trả 429; chatbot mock giữ luồng tư vấn phim: đạt.
5. Vé không tràn ngang tại 375px và 1280px: đạt.
6. `.tabs` và `.seatmap__scroll` có `overflow-y: hidden`: đạt.
7. Trang admin So sánh mô hình render và không có `.chat-widget`: đạt.

Kết quả quan sát: 7/7 mục hồi quy mock mode đạt; build mock cũng hoàn tất.

## 6. Test mới/cập nhật

- `backend/tests/test_t20_hardening.py`: SECRET_KEY, token khóa cũ, login rate limit, `ADMIN_PASSWORD`, hai nhánh hạn giữ, trả ghế, giới hạn vé, QR, comment rate limit trước classifier và tìm thể loại chatbot.
- `backend/tests/test_booking_payment.py`: cập nhật contract hạn giữ và cấu hình QR rõ ràng cho các ca chuyển khoản.
- `backend/tests/conftest.py`: khóa test đủ 32 ký tự và reset limiter giữa các test.

## 7. Ghi chú bàn giao

- `backend/.env` thật vẫn do PO tự cấu hình theo Task Record; Codex không sửa file này.
- Report T15 đang tồn tại dạng untracked trong working tree trước bước commit T20 và được loại khỏi commit T20.
- Không tự kết luận review/PASS; chờ Claude review độc lập.
