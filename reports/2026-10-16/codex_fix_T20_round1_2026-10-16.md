# Codex Fix T20 — Round 1 (16/10/2026)

## 1. Phạm vi

- Sửa duy nhất RF-01 (High) theo Claude review ngày 16/10/2026.
- File production thay đổi: `backend/app/routers/auth.py`, `backend/app/rate_limit.py`.
- Test thay đổi: `backend/tests/test_t20_hardening.py`.
- Đổi schema: Không.
- Không sửa frontend, không thêm thư viện, không dùng `backend/firefly.db`, không sửa `backend/.env`.

## 2. Thay đổi RF-01

- Thêm `SlidingWindowRateLimiter.is_blocked()` dùng chung lock và tự loại các mốc đã quá cửa sổ.
- `login()` kiểm tra email đã bị khóa ngay sau khi lowercase và trước truy vấn/xác thực mật khẩu.
- Email có từ 5 lần sai trong 300 giây luôn nhận HTTP 429, kể cả request tiếp theo dùng mật khẩu đúng.
- Mật khẩu sai khi chưa khóa vẫn ghi nhận một lần thất bại; request thứ sáu trả 429.
- Mật khẩu đúng khi chưa khóa vẫn xóa bộ đếm và trả 200.
- Thêm test riêng `test_correct_password_is_blocked_during_login_lock_window`; không xóa hoặc nới test cũ.

## 3. Probe tay trên SQLite tạm

```text
5 sai: [401, 401, 401, 401, 401]
đúng mật khẩu trong cửa sổ: 429
sau 5 phút: 200
```

Probe dùng TestClient với SQLite nằm trong thư mục tạm, đồng hồ monotonic điều khiển tại `3000.0` rồi tăng `301` giây. Thư mục tạm tự xóa sau khi chạy.

## 4. Kết quả gate

| Gate | Kết quả quan sát |
|---|---|
| Focused `tests/test_t20_hardening.py` | `16 passed, 1 warning` |
| Full pytest | `81 passed, 1 warning` |
| `python -m compileall -q backend/app` | exit 0 |
| `frontend; npm run build` | exit 0; 82 modules transformed |

Cảnh báo pytest duy nhất là deprecation warning đã có của `starlette.testclient` về alias AnyIO; không có test fail. Hai lượt pytest dùng `--basetemp` trong `backend/` và các thư mục tạm đã được xóa sau gate.

## 5. Dọn file T15 khỏi working tree T20

- Đã xuất bản chuẩn từ nhánh `task/T15-tach-tu` bằng `git show` vào `%TEMP%\t15_branch.md`.
- Đã so sánh sau khi chuẩn hóa CRLF/LF.
- Kết quả: nội dung giống hoàn toàn (`NORMALIZED_EQUAL=True`).
- SHA-256 nội dung chuẩn hóa của cả hai bản: `3DFC791B4E2123B5AF19672E75CB807FF4C6A4E8417A15898E50CBFDC2E91138`.
- Đã xóa file untracked `reports/2026-10-15/codex_implementation_T15_2026-10-15.md` khỏi working tree T20; file tạm cũng đã xóa.
- File T15 không được stage hoặc đưa vào commit T20.

## 6. Bàn giao

RF-01 đã được sửa ở mức implementation và chuyển lại `CLAUDE_REVIEW` để Claude xác minh độc lập. Codex không tự review, không tự kết luận PASS và không mở task kế tiếp.
