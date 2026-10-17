# Codex Fix Report — T14 TODO-01

- Ngày: 17/10/2026
- Nhánh: `task/T14-huy-ve-tai-khoan`
- Nguồn yêu cầu: PO yêu cầu sửa TODO-01 trong Claude review T14
- Đổi schema: Không
- Trạng thái bàn giao: `CLAUDE_REVIEW`

## 1. Vấn đề

`POST /api/auth/change-password` trước đây gọi `verify_password` không giới hạn số lần. Người đang giữ token có thể thử mật khẩu hiện tại liên tục và không dùng chung cơ chế khóa đăng nhập của T20.

## 2. Thay đổi

- Dùng lại đúng `_login_failures`; không tạo limiter mới và không sửa `rate_limit.py`.
- Key là `user.email.lower()`, cùng key với `/api/auth/login`.
- Trước khi xác minh mật khẩu, gọi `is_blocked(email, limit=5, seconds=300)`. Khi đang khóa, endpoint trả 429 và không gọi `verify_password`.
- Mật khẩu hiện tại sai gọi `hit` với cùng ngưỡng 5 lần/300 giây; năm lần đầu trả 400, request tiếp theo trả 429.
- Đổi mật khẩu thành công gọi `clear(email)` trước khi lưu mật khẩu mới.
- Câu 429 của change-password: `Bạn nhập sai mật khẩu quá nhiều lần. Hãy thử lại sau 5 phút.`
- Không đổi hành vi hoặc câu lỗi của `/api/auth/login`.

## 3. Test bổ sung

1. Năm lần sai qua change-password, lần kế tiếp dùng mật khẩu đúng vẫn 429; `verify_password` chỉ được gọi đúng năm lần sai và mật khẩu trong DB không đổi.
2. Năm lần sai qua change-password làm login cùng email (kể cả email viết hoa) trả 429 với câu lỗi login cũ, chứng minh dùng chung bộ đếm.
3. Sai bốn lần rồi đổi đúng trả 200 và xóa bộ đếm; lần sai kế tiếp trả 400, không bị 429 ngay.

Mô phỏng thời gian bằng monkeypatch `rate_limit.time.monotonic`, không sleep thật.

## 4. Probe API thật trên SQLite tạm

- Database: `backend/t14_todo01_probe.db`, tạo bằng `backend/scripts/reset_demo.py` với `DATABASE_URL` trỏ file tạm và `ADMIN_PASSWORD` riêng.
- Sáu lần liên tiếp dùng sai mật khẩu hiện tại: `400,400,400,400,400,429`.
- Mật khẩu đúng ngay sau đó: `429`.
- Câu trả về ở cả lần sai thứ sáu và lần đúng: `Bạn nhập sai mật khẩu quá nhiều lần. Hãy thử lại sau 5 phút.`
- Backend đã tắt; DB, sidecar và bản backup tạm phát sinh trong lúc reset đều đã xóa. Không chạy backend trên `backend/firefly.db` thật.

## 5. Quality gate

| Gate | Kết quả |
|---|---|
| Focused pytest T14 + T20 | PASS — 29/29 |
| `python -m compileall -q backend/app` | PASS |
| Full pytest | PASS — 98/98; 1 warning deprecation Starlette; cảnh báo cleanup symlink temp Windows xuất hiện sau exit code 0 |
| `npm run build` | PASS — 84 modules |
| Scope | PASS — chỉ `routers/auth.py`, test T14, report fix và file điều phối |
| Schema/thư viện | Không đổi schema; không thêm thư viện |

## 6. Frontend và mock

Không sửa frontend hoặc mock theo quyết định PO. Trang `/tai-khoan` hiện đã render `err.message` khi request đổi mật khẩu thất bại, nên câu 429 từ backend tự hiển thị cho người dùng. Mock tiếp tục không mô phỏng khóa đăng nhập, thống nhất với phạm vi T20.

## 7. Bàn giao

- TODO-01: DEV FIXED / PENDING CLAUDE VERIFICATION.
- Không xử lý TODO-02/03/04.
- Không tự review, không tự PASS và không mở T13.
