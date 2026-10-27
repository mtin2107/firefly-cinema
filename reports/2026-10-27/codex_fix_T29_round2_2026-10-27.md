# T29 — Codex Fix vòng 2 — TODO-03 — 27/10/2026

- Vai trò: Fix Implementer, theo PO quyết TODO-03 = FIX_NOW ngày 27/10/2026.
- Nhánh `task/T29-tai-khoan`; baseline `51b4ddd`, working tree sạch trước khi sửa.
- **Đổi schema: Không.** Không thêm thư viện, không đổi API khác hoặc giao diện.
- Bàn giao Claude xác minh độc lập; không tự review/PASS, không merge, không mở T13.

## 1. Sửa TODO-03

`put_avatar` đọc bằng `request.stream()` thay cho `await request.body()`. Mỗi chunk tăng tổng số byte; vượt 3 × 1024² byte thì trả ngay 413 **“Ảnh đại diện tối đa 2 MB.”**, trước khi thêm chunk vượt ngưỡng vào bộ đệm. Bộ đệm chỉ giữ tối đa 3 MiB; không tiếp tục đọc các chunk sau.

Giữ nguyên chặn Content-Length sớm, kiểm media type, parse PosterUploadIn/ngữ cảnh lỗi, validate_image dùng chung, ghi ảnh mới, commit và xóa ảnh cũ. JSON hợp lệ vẫn được parse từ bytearray đã ghép. Không sửa schema hoặc endpoint khác.

## 2. Test bổ sung

Thêm đúng hai ca vào `backend/tests/test_t29_round1.py`:

1. Không Content-Length, có Transfer-Encoding: chunked; ba chunk mỗi chunk 1 MiB, chunk thứ tư làm tổng vượt 3 MiB, còn chunk thứ năm. Nhận 413 đúng câu tiếng Việt; xác minh chỉ đọc bốn chunk, không giải mã ảnh, không tạo thư mục/file upload.
2. Ảnh PNG hợp lệ trong JSON chia thành ba chunk, không Content-Length. Nhận 200, đọc đủ ba chunk, file ảnh dưới UPLOAD_DIR tạm có đúng nội dung.

Helper test gửi từng sự kiện `http.request` vào ứng dụng ASGI với header chunked, thay vì để transport TestClient gộp iterator thành một body. Các test đi qua endpoint/auth/dependency thực của ứng dụng với SQLite fixture tạm.

## 3. Gate

| Gate | Kết quả thực thi |
|---|---|
| compileall backend/app | Exit 0 |
| Focused test_t29_round1.py | 11/11 đạt |
| Pytest toàn bộ | 241/241 đạt, 0 lỗi, 73,84 giây; 1 cảnh báo DeprecationWarning từ Starlette/anyio |
| Giờ pytest toàn bộ | 27/10/2026, 12:51:48–12:53:04, Asia/Saigon (UTC+07:00) |
| npm run build real | Exit 0, VITE_USE_MOCK=false |
| npm run build mock | Exit 0, VITE_USE_MOCK=true |
| Scope / whitespace | Chỉ auth.py, test_t29_round1.py, report vòng 2 và file điều phối; git diff --check không lỗi |

DATABASE_URL đặt trước import thành SQLite dưới `%TEMP%/firefly-t29-r2-import.db`; UPLOAD_DIR môi trường cũng trỏ TEMP. Fixtures tạo DB và thư mục ảnh riêng dưới tmp_path. Không khởi động backend trên DB thật, không đọc/ghi/reset `backend/firefly.db` hoặc `backend/uploads` thật.

## 4. Bàn giao

TODO-03 đã được triển khai và có kiểm thử chặn đọc tiếp stream. Chuyển `FIX_LOOP → CLAUDE_REVIEW`, chờ Claude kết luận độc lập. Giữ nguyên các quyết định PO và trạng thái T13 hiện có.
