# Claude Independent Review — T20 Round 2

- Ngày: 16/10/2026
- Nhánh: `task/T20-gia-co`, tip `8693e39` (fix RF-01 trên nền `6a82884`)
- Vòng trước: `reports/2026-10-16/claude_review_T20_FAIL_2026-10-16.md`
- Kết luận: **PASS_WITH_TODO**
- Required Fixes mở: **0** (RF-01 CLOSED) · TODO: 3 (Low, giữ từ vòng 1) · Blocker: 0

## 1. Phạm vi fix

`git diff --stat 6a82884 8693e39`: `backend/app/rate_limit.py` (+13), `backend/app/routers/auth.py` (+2), `backend/tests/test_t20_hardening.py` (+22), file điều phối, report fix. Đúng giới hạn prompt Fix Round 1. Không sửa frontend, không thêm thư viện, không đổi schema. Không xóa hoặc nới test cũ.

Việc dọn file: bản sao untracked `reports/2026-10-15/codex_implementation_T15_2026-10-15.md` đã được xóa khỏi working tree T20 sau khi so khớp nội dung với nhánh T15. Không có trong commit T20. `git status` sạch.

## 2. RF-01 — CLOSED / VERIFIED BY CLAUDE

**Thay đổi:** `SlidingWindowRateLimiter.is_blocked()` dọn mốc cũ trong cùng lock. `login()` gọi nó ngay sau khi lowercase email, **trước** truy vấn user và `verify_password`.

**Probe độc lập trên uvicorn thật** (cổng 8005, SQLite tạm, PhoBERT B):

```
5 sai:                                [401, 401, 401, 401, 401]
đúng mật khẩu khi đang bị khóa:       429   (vòng 1: 200)
email VIẾT HOA, đúng mật khẩu:        429
tài khoản khác không bị ảnh hưởng:    200
demo đăng nhập bình thường:           200
```

Nhánh "sau 300 giây đăng nhập lại được" do pytest `test_correct_password_is_blocked_during_login_lock_window` kiểm bằng đồng hồ điều khiển (`clock += 301` → 200). Claude đã đọc test và xác nhận assert đúng mã 429 cùng câu thông báo.

Đánh đổi đã chấp nhận ở vòng 1: ai biết email có thể khóa tài khoản đó 5 phút. Ghi vào hạn chế khóa luận.

## 3. Gate

| Gate | Kết quả |
|---|---|
| `compileall backend/app` | exit 0 |
| `pytest` đầy đủ | **81 passed** (80 + 1 test RF-01), 1 warning có sẵn |
| `npm run build` | PASS |
| File cấm trong diff `master...HEAD` | Không có |

Các AC khác đã được Claude xác minh độc lập ở vòng 1 (AC-01, AC-03..AC-11) và không bị fix này chạm tới. **AC 11/11 PASS.**

## 4. TODO giữ nguyên từ vòng 1

| ID | Mức | Nội dung | Đề xuất disposition |
|---|---|---|---|
| TODO-01 | Low | `expire_holds` nạp mọi vé `held` và tính hạn bằng Python (N+1 `showtime`) | WONT_FIX cho v1.0 |
| TODO-02 | Low | `overflow-y: hidden` cắt khoảng 18px của hiệu ứng hàng ghế trượt vào trong vài trăm ms đầu | WONT_FIX |
| TODO-03 | Low | Mock không mô phỏng giới hạn đăng nhập sai | ACCEPT_LATER / WONT_FIX |

OBS từ vòng 1: PO nên đặt `ADMIN_PASSWORD` trong `backend/.env` trước khi T12 tạo lại DB demo. Hiệu ứng lật vé sau `overflow: clip` chưa được xem trên vé đã thanh toán; PO kiểm khi review.

## 5. Kết luận

**PASS_WITH_TODO.** T20 `CLAUDE_REVIEW → PO_REVIEW`. Mọi TODO không chặn task sau.

## 6. Bàn giao task kế tiếp

Theo lộ trình cuối (15/10/2026): `T20 → T12 → T21 → T14 → T13`. **T12** đủ điều kiện: phụ thuộc T10 (CLOSED) và T20 (vừa PASS), Q4 đã áp dụng mặc định chạy trên máy. T12 → `READY_FOR_HANDOFF`.

**Tín làm trước khi gửi prompt:**
1. PO review T20 và disposition TODO-01..03. Mở một vé đã thanh toán (mock mode) để xem hiệu ứng lật vé.
2. `git checkout master` → `git merge --no-ff task/T20-gia-co -m "[T20] Merge hardening into master"`.
3. Nếu T15 đã PO duyệt thì merge T15 luôn: `git merge --no-ff task/T15-tach-tu -m "[T15] Merge word segmentation experiment"`.
4. Đặt `ADMIN_PASSWORD` trong `backend/.env`.
5. `git checkout -b task/T12-demo`.

**Prompt ChatGPT/Codex cho T12:**

```text
Bạn là Codex, Primary Implementer của dự án Firefly Cinema.
Chỉ đọc: PROJECT_SOURCE_OF_TRUTH.md, AGENT_RULES.md, TASK_COORDINATION_ACTIVE.md (Snapshot, Status, lộ trình cuối 15/10),
docs/tasks/T12.md, docs/tasks/T21.md (mục 3, để dữ liệu demo đủ cho trang Thống kê cảm xúc),
backend/app/seed.py, backend/app/booking_rules.py, và source/test liên quan trực tiếp.

Thực hiện T12 trên nhánh task/T12-demo (tạo từ master sau khi merge T20), chỉ sửa file trong Allowed Files của T12.md.
Lưu ý từ T20:
- Vé giữ chỗ hết hạn sau 15 phút, nên vé demo cần có trạng thái paid / pending_verify / expired rõ ràng,
  không dựa vào vé held cũ.
- Seed admin đọc ADMIN_PASSWORD từ môi trường; reset_demo dùng lại logic seed, không ghi mật khẩu vào code hay tài liệu.
- reset_demo.py phải từ chối chạy nếu DATABASE_URL không phải SQLite cục bộ, và sao lưu firefly.db hiện có
  (tên có timestamp, trong backup\ ngoài Git) trước khi xóa.
- Bình luận demo tự viết (demo_comments.json), chấm bằng model active, rải ≥ 14 ngày, ≥ 6 phim với tỷ lệ tiêu cực khác nhau,
  có vài bình luận đã duyệt, trong đó có ca model sai.
Không sửa classifier.py, models.py; không thêm thư viện; không đổi schema; không sửa backend/.env.
Chạy gate theo AGENT_RULES.md mục 3 trên SQLite tạm (KHÔNG chạy reset_demo trên backend/firefly.db thật khi chưa được PO cho phép),
cả real và mock mode.
Tạo reports/<YYYY-MM-DD>/codex_implementation_T12_<YYYY-MM-DD>.md, ghi "Đổi schema: Không" và checklist hồi quy.
Cập nhật TASK_COORDINATION_ACTIVE.md: T12 READY_FOR_HANDOFF -> IN_PROGRESS -> CLAUDE_REVIEW.
Commit dạng "[T12] mô tả". Không tự review, không tự PASS, không mở task kế tiếp. Trả lời bằng tiếng Việt.
```
