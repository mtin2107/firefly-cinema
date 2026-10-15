# Claude Independent Review — T20 Gia cố bảo mật, giữ chỗ và sửa lỗi giao diện

- Ngày: 16/10/2026
- Nhánh: `task/T20-gia-co`, tip `e9c117b` (base `c3f70df`)
- Kết luận: **FAIL**
- Required Fixes: **1** (RF-01 High) · TODO: 3 (Low) · OBS: 3

Toàn bộ phần còn lại của T20 đạt. FAIL chỉ vì RF-01: giới hạn đăng nhập sai không chặn được việc dò mật khẩu, trong khi đó là mục đích của F-02.

## 1. Phạm vi

`git diff --stat master...task/T20-gia-co`: 22 file, 414+/45−, **tất cả trong Allowed Files** của `docs/tasks/T20.md` (`rate_limit.py` là file mới được phép). Không sửa `models.py`, `classifier.py`, `seats.py`, `utils/seats.js`, `backend/.env`. Không thêm thư viện, không đổi schema. `git diff --check` sạch. Không có `.env`, `*.db`, `uploads/`, model trong diff.

## 2. Gate độc lập

| Gate | Kết quả |
|---|---|
| `compileall backend/app` | exit 0 |
| `pytest` đầy đủ | **80 passed**, 1 warning có sẵn (starlette) |
| `npm run build` | PASS |
| Backend thật | uvicorn 8005 + SQLite/UPLOAD_DIR tạm, health `phobert_b`. `firefly.db` không bị đụng |
| Real browser | 5178 → 8005: chọn ghế → xác nhận → đặt vé → Vé của tôi → chatbot → trang admin |
| Mock mode | 5174, gọi trực tiếp `mockApi` |
| Console | 0 lỗi ứng dụng (1 `ERR_BLOCKED_BY_CLIENT` do khung trình duyệt chặn tài nguyên ngoài) |

## 3. Acceptance Criteria

| AC | Kết quả | Bằng chứng (Claude tự chạy) |
|---|---|---|
| AC-01 SECRET_KEY | PASS | Import `app.config` với khóa mặc định / rỗng / 31 ký tự → `RuntimeError`, exit 1; 32 ký tự → exit 0. Token ký bằng `doi-chuoi-bi-mat-nay` → 401. |
| AC-02 Đăng nhập + ADMIN_PASSWORD | **FAIL** (RF-01) | 6 lần sai → `[401×5, 429]` đúng; nhưng **đúng mật khẩu ngay sau đó → 200**. Seed đọc `ADMIN_PASSWORD` (có pytest). |
| AC-03 Hạn giữ 15 phút | PASS | `hold_expires_at − created_at = 0:15:00` (real và mock); pytest phủ cả nhánh "30 phút trước giờ chiếu" và trả ghế. |
| AC-04 Tối đa 2 vé, transfer-claim | PASS | Vé thứ 3 → 409 đúng câu; transfer-claim khi chưa cấu hình QR → 409 "Rạp chưa bật thanh toán chuyển khoản." |
| AC-05 Bình luận 3/phút | PASS | `[201, 201, 201, 429]`; limiter chạy trước `classifier.predict`. |
| AC-06 Chatbot thể loại | PASS | Real browser, câu gợi ý "Gợi ý phim hài đang chiếu" → "Phim hài đang chiếu tại rạp là Thứ Bảy Không Ngủ" kèm thẻ phim (Gemini thật). Lần review 15/10 trả lời sai. |
| AC-07 Vé không tràn ngang | PASS | Ngay sau đặt vé: `scrollWidth 1265 = clientWidth 1265`, canvas burst vẫn có nhưng bị `overflow: clip`. |
| AC-08 Không thanh cuộn thừa | PASS | `.tabs` và `.seatmap__scroll` có `overflow-y: hidden`; hàng A và H của sơ đồ ghế hiển thị đủ. |
| AC-09 Nút chuyển khoản, chat admin | PASS | Không QR → không có nút. Admin ở `/quan-tri/so-sanh-mo-hinh` → không có `.chat-widget`. |
| AC-10 Mock | PASS | Mock: hạn giữ 15 phút, vé thứ 3 → 409, bình luận thứ 4 → 429. |
| AC-11 Gate + hồi quy | PASS | Như mục 2; luồng đặt vé, đăng nhập, bình luận, chatbot, admin hoạt động. |

## 4. Required Fix

### RF-01 — High: Giới hạn đăng nhập sai không chặn được dò mật khẩu

- **File:** `backend/app/routers/auth.py:28-36`
- **Problem:** Limiter chỉ được gọi **sau khi** mật khẩu sai. Request có mật khẩu đúng không bao giờ bị kiểm, nên kể cả khi email đang bị "khóa", đoán trúng vẫn đăng nhập được, rồi bộ đếm bị xóa. Kẻ tấn công vẫn thử mật khẩu không giới hạn; chỉ khác là mã lỗi đổi từ 401 sang 429. F-02 ("giới hạn đăng nhập sai") vì thế không đạt mục đích. Test `test_login_sixth_failure_is_limited_and_correct_login_works_after_window` chỉ kiểm đăng nhập đúng **sau** 5 phút, không kiểm **trong** 5 phút.
- **Evidence (probe trên uvicorn thật):**
  ```
  6 lần sai:                         [401, 401, 401, 401, 401, 429]
  đúng mật khẩu ngay khi đang bị khóa -> 200
  sau đó sai tiếp 3 lần:              [401, 401, 401]   (bộ đếm đã bị xóa)
  ```
- **Expected Fix:**
  1. Đầu hàm `login`, **trước** `verify_password`: nếu email đã có ≥ 5 lần sai trong 5 phút → 429 với câu hiện tại, bất kể mật khẩu đúng hay sai. Có thể thêm method `is_blocked(key, limit, seconds)` vào `SlidingWindowRateLimiter`, hoặc tách "đếm" và "kiểm".
  2. Sai mật khẩu → ghi nhận thất bại; lần sai thứ 6 vẫn trả 429 như hiện tại.
  3. Đúng mật khẩu khi chưa bị khóa → 200 và xóa bộ đếm (giữ nguyên).
  4. Thêm pytest: 5 lần sai → đúng mật khẩu **trong** cửa sổ → 429; sau 301 giây → 200.
  5. Không đổi file nào ngoài `backend/app/routers/auth.py`, `backend/app/rate_limit.py`, `backend/tests/**`.
- **Đánh đổi chấp nhận:** sau khi sửa, ai biết email admin có thể cố ý gõ sai 5 lần để khóa admin 5 phút. Với web chạy trên máy khi bảo vệ, rủi ro này chấp nhận được và nhỏ hơn rủi ro bị dò mật khẩu. Ghi vào hạn chế khóa luận.

## 5. TODO (không chặn)

| ID | Mức | Vấn đề | Đề xuất |
|---|---|---|---|
| TODO-01 | Low | `expire_holds` nạp mọi vé `held` rồi tính hạn bằng Python, mỗi vé lazy-load `showtime` (N+1). Hàm này chạy ở nhiều endpoint. Với vài chục vé giữ thì không đáng kể. | WONT_FIX cho v1.0, ghi `shortcut:`; chỉ cần SQL khi dữ liệu lớn. |
| TODO-02 | Low | `overflow-y: hidden` ở `.seatmap__scroll` cắt khoảng 18px phía trên của hiệu ứng hàng ghế trượt vào (GSAP `y: -18`) trong vài trăm ms đầu. Trạng thái cuối hiển thị đủ. | WONT_FIX hoặc đổi hiệu ứng sang `y: 18` khi tiện. |
| TODO-03 | Low | Mock không mô phỏng giới hạn đăng nhập sai. AC-10 không yêu cầu, nhưng real và mock lệch nhau ở hành vi 429 khi đăng nhập. | ACCEPT_LATER hoặc làm cùng RF-01 nếu Codex muốn (`mock.js` nằm trong allowlist). |

## 6. Observations

- **OBS-01:** `backend/.env` của PO chưa đặt `ADMIN_PASSWORD`. Log khi khởi động: "ADMIN_PASSWORD chưa được cấu hình; đang dùng mật khẩu admin mặc định cho máy dev." Đúng thiết kế T20. Chỉ ảnh hưởng **DB mới**: `firefly.db` hiện có giữ mật khẩu cũ cho tới khi T12 reset dữ liệu demo.
- **OBS-02:** `reports/2026-10-15/codex_implementation_T15_2026-10-15.md` vẫn untracked trong working tree nhánh T20. Codex đã loại đúng khỏi commit T20; Tín xóa bản này (đã có trên nhánh T15).
- **OBS-03:** `SECRET_KEY` trong `backend/.env` của PO đã hợp lệ: backend khởi động được với guard mới.

## 7. Kết luận

**FAIL**, chỉ vì RF-01. Fix nhỏ, khoảng 10 dòng cộng 1 test. Các mục khác (SECRET_KEY, giữ chỗ, giới hạn vé, chặn chuyển khoản, giới hạn bình luận, chatbot, 5 lỗi giao diện, mock) đều đã được Claude xác minh độc lập và đạt. T20 `CLAUDE_REVIEW → FIX_LOOP`. Không mở task kế tiếp.

## 8. Prompt Codex — Fix Round 1

```text
Bạn là Codex, Fix Implementer cho T20.
Chỉ đọc: docs/tasks/T20.md, docs/TASK_COORDINATION_ACTIVE.md, reports/2026-10-16/claude_review_T20_FAIL_2026-10-16.md,
backend/app/routers/auth.py, backend/app/rate_limit.py, backend/tests/test_t20_hardening.py, backend/tests/conftest.py.
Chỉ sửa RF-01 theo đúng Expected Fix trong review (kiểm khóa TRƯỚC verify_password; thêm pytest "đúng mật khẩu trong lúc bị khóa -> 429,
sau 301 giây -> 200"). Không thêm feature, không xóa hoặc nới test hiện có, không sửa file ngoài auth.py, rate_limit.py, backend/tests/**.
Chạy lại: focused pytest, full pytest, compileall, npm run build.
Tạo reports/<YYYY-MM-DD>/codex_fix_T20_round1_<YYYY-MM-DD>.md, cập nhật file điều phối FIX_LOOP -> CLAUDE_REVIEW.
Commit "[T20] Fix RF-01 chặn đăng nhập khi đang bị khóa". Không tự review, không tự PASS. Trả lời bằng tiếng Việt.
```
