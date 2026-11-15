# T35 — Claude implementation + self-review — 15/11/2026

**Kết luận self-review: PASS_WITH_TODO** (không độc lập, Claude vừa viết vừa review theo yêu cầu PO trong chat).
Nhánh `task/T35-bao-mat-web` từ master `0121890`. Không đổi schema, không thêm thư viện, không đổi giao diện.

## 1. Thay đổi
| File | Nội dung |
|---|---|
| `backend/app/main.py` | Middleware `security_headers`: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin` (dùng `setdefault`, không ghi đè header sẵn có như của range video). Không thêm CSP vì Swagger `/docs` tải script từ CDN. |
| `backend/app/routers/auth.py` | `_register_limits`: 10 lần đăng ký/giờ/IP, quá thì 429 "Bạn đăng ký quá nhiều tài khoản. Hãy thử lại sau 1 giờ." Chỉ đếm sau khi body hợp lệ. |
| `backend/app/schemas.py` | `max_length=100` cho `LoginIn.password`, `ChangePasswordIn.current_password`, `ChangeEmailIn.current_password`. |
| `backend/tests/conftest.py` | Reset `_register_limits` giữa các test. |
| `backend/tests/test_t35_security.py` | 4 test cho AC-01..03. |

## 2. Gate
| Gate | Kết quả |
|---|---|
| `python -m compileall -q backend\app` | exit 0 |
| `pytest -q` toàn bộ | **317 passed** (313 cũ + 4 mới), 2:03 |
| `npm run build` | built OK |
| Backend thật cổng 8000 + `/api/health` | `"classifier":"phobert_b"`, 3 header có mặt, `access-control-allow-origin: http://localhost:5173` |
| `/docs` | 200 |
| Mock mode | Không áp dụng: không đổi endpoint hay JSON |

## 3. Đối chiếu AC
AC-01..05 PASS (bằng chứng: test + curl ở mục 2).

## 4. Self-review
- Scope: đúng 8 file trong allowlist. Không file `data/`, `ml/artifacts/`, `backend/models/`, `*.db`, `.env` nào bị add.
- Hồi quy: tài khoản cũ không bị khóa vì đăng ký đã giới hạn 100 ký tự từ trước.
- Lỗi trả `HTTPException` câu tiếng Việt; tên biến tiếng Anh.

### TODO
- **TODO-01 (Low):** limiter đăng ký dùng `request.client.host`. Nếu sau này đặt backend sau reverse proxy thì mọi người dùng chung một IP và chung quota. Khi deploy cần đọc IP thật từ proxy (`--proxy-headers` của uvicorn). Với chạy local hiện tại không ảnh hưởng.
- **TODO-02 (Low):** `mock.js` không giả lập 429 khi đăng ký (giống login hiện tại). Không đổi cấu trúc JSON nên không vi phạm quy ước real/mock.

### Ngoài phạm vi, đề xuất ghi Hạn chế khóa luận
- JWT trong `localStorage` (rủi ro nếu có XSS; hiện không thấy điểm XSS nào).
- `react-router-dom` 6.x có 2 advisory mức trung bình (open redirect qua `\`); `returnTo` chỉ đọc state nội bộ nên khó khai thác. Nâng v7 là breaking change.
- Rate limit in-memory, mất khi khởi động lại.
- Chưa chạy `pip-audit` (chưa cài trong venv).

## 5. Việc của PO
Duyệt và merge `task/T35-bao-mat-web` vào master. Vì Claude viết code, nếu muốn review độc lập thì giao Codex.
