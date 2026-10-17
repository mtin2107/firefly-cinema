# Claude Review — T14 — Round 2 (fix TODO-01 theo yêu cầu PO) — PASS_WITH_TODO — 17/10/2026

- Nhánh: `task/T14-huy-ve-tai-khoan`, tip `1118dbd` ("[T14] Fix TODO-01 giới hạn thử mật khẩu khi đổi mật khẩu").
- Vòng trước: `reports/2026-10-16/claude_review_T14_PASS_WITH_TODO_2026-10-16.md`.
- Report Codex: `reports/2026-10-17/codex_fix_T14_todo01_2026-10-17.md` (bằng chứng phụ).
- Probe trên SQLite tạm (dữ liệu demo T12) trong scratchpad của Claude; không chạm `backend/firefly.db`.

## 1. Scope của bản fix

`git diff --stat 91fc1fa 1118dbd`: `backend/app/routers/auth.py` (+11), `backend/tests/test_t14_account_and_cancellation.py` (+87/−1), report fix, file điều phối. Đúng danh sách trong prompt. Không đổi `rate_limit.py`, `login`, frontend, mock, schema, thư viện.

## 2. Thay đổi

- `change_password` dùng chung `_login_failures`, khóa theo `user.email.lower()`, cùng ngưỡng 5 lần / 300 giây như login.
- Kiểm `is_blocked` **trước** `verify_password`, nên lúc bị khóa không so mật khẩu và không đổi mật khẩu.
- Sai thì `hit` rồi trả 400; đổi thành công thì `clear`. Câu 429 riêng: "Bạn nhập sai mật khẩu quá nhiều lần. Hãy thử lại sau 5 phút."
- Test bỏ 2 import không dùng (`create_token`, `hash_password`) và thêm 3 test, giả lập đồng hồ qua `rate_limit.time.monotonic` giống cách test T20:
  1. 5 lần sai → lần đúng ngay sau bị 429, `verify_password` chỉ được gọi 5 lần, mật khẩu không đổi;
  2. sai qua đổi mật khẩu làm login cùng email (viết hoa) bị 429;
  3. sai 4 lần rồi đúng → 200; sai tiếp → 400, không 429.

## 3. Probe độc lập (backend thật, DB demo tạm)

| Ca | Kết quả |
|---|---|
| 6 lần sai mật khẩu hiện tại liên tiếp | `[400, 400, 400, 400, 400, 429]` (vòng 1: 12 × 400) |
| Mật khẩu đúng ngay sau đó | 429 "Bạn nhập sai mật khẩu quá nhiều lần…" |
| Login `DEMO@firefly.vn` đúng mật khẩu | 429 "Bạn đăng nhập sai quá nhiều lần…" (bộ đếm chung) |
| Kiểm DB trực tiếp | mật khẩu cũ vẫn đúng, mật khẩu mới không được đặt |
| Admin đăng nhập | 200 (không ảnh hưởng tài khoản khác) |

Trang `/tai-khoan` hiện `error.message` (đã kiểm ở vòng 1), nên câu 429 tự hiển thị.

## 4. Gate

| Gate | Kết quả |
|---|---|
| `compileall -q backend/app` | exit 0 |
| pytest đầy đủ | **98 passed**, 1 warning thư viện (95 + 3 mới) |
| `npm run build` | đạt (frontend không đổi) |

## 5. TODO

| TODO | Trạng thái |
|---|---|
| TODO-01 giới hạn thử mật khẩu | **CLOSED / VERIFIED BY CLAUDE** |
| TODO-02 mã vé dùng lại sau khi hủy (cần đổi schema nếu sửa) | mở, Medium, PO quyết trước T13 |
| TODO-03 câu 422 họ tên chung chung | mở, Low |
| TODO-04 token cũ còn hiệu lực sau khi đổi mật khẩu | mở, Low, ghi vào hạn chế ở T13 |

Hệ quả cần ghi vào HUONG_DAN ở T13: nhập sai mật khẩu 5 lần ở trang đổi mật khẩu thì email đó cũng bị khóa đăng nhập 5 phút, và ngược lại.

## 6. Kết luận

**PASS_WITH_TODO.** RF 0, blocker 0. AC 5/5 giữ nguyên. T14 `CLAUDE_REVIEW → PO_REVIEW`.

T13 vẫn `READY_FOR_HANDOFF`. Prompt Codex T13 ở mục 10 của `reports/2026-10-16/claude_review_T14_PASS_WITH_TODO_2026-10-16.md`; khi điền Bước 0 ghi "T14 TODO-01: đã sửa (Round 2)".
