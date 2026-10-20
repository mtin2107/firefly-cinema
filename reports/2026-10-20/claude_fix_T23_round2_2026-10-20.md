# Claude Fix Report — T23 Round 2

- Ngày: 2026-10-20 · Nhánh: `task/T23-tong-quan-soat-ve` · baseline `5b1bc40`
- Người sửa: **Claude, theo yêu cầu "fix" của Tín trong chat** (ngoại lệ vai trò reviewer theo CLAUDE.md).
- **Vì Claude vừa sửa vừa từng review, phần sửa này cần người review độc lập (Tín hoặc Codex) trước khi merge.**
- Phạm vi: Tín yêu cầu sửa nên coi như PO duyệt thêm `frontend/src/pages/MyTickets.jsx` vào allowlist cho TODO-01.

## Thay đổi
| Mục | File | Thay đổi |
|---|---|---|
| RF-01 | `backend/app/routers/admin_dashboard.py` | Lấp ghế tính trên suất `start_time >= đầu khoảng` (bỏ chặn trên), gồm suất sắp chiếu |
| RF-01 | `frontend/src/api/mock.js` | Cùng điều kiện ở mock |
| RF-01 | `frontend/src/pages/AdminDashboard.jsx` | Chú thích: "tỷ lệ lấp ghế tính trên các suất từ đầu khoảng thời gian, gồm suất sắp chiếu" |
| RF-01 | `backend/tests/test_t23_dashboard_checkin.py` | `test_payment_and_cancel_increase` chạy với suất +3 giờ và +3 ngày |
| TODO-01 | `frontend/src/components/TicketStub.jsx`, `frontend/src/pages/MyTickets.jsx` | Bỏ lời gọi `api.bookings.mine()` trong TicketStub; MyTickets truyền `checkedInAt={b.checked_in_at}` |

## Bằng chứng
- Trước khi sửa, test mới fail ở cả hai trường hợp. Trường hợp +3 giờ fail vì lúc chạy đã sau 21:00: suất rơi sang ngày mai. Nghĩa là test gốc của Codex fail theo giờ trong ngày.
- Sau khi sửa: compileall 0; pytest **142 passed**; `npm run build` đạt.
- Backend DB tạm: dashboard vẫn khớp SQL độc lập 7/30/90 ngày; bán 2 ghế suất tương lai + admin xác nhận → lấp ghế phim 1 `0,024740 → 0,026042` (= 2 / (16 suất × 96 ghế)).
- Mock: suất 24/10, bán 2 ghế + xác nhận → `0,001302 → 0,002604`.
- "Vé của tôi" (real, 2 vé paid): `/api/bookings/me` gọi **2 lần** (1 lượt tải trang × StrictMode dev), trước là 6; "Đã vào rạp lúc 21:16, Thứ 3 20/10/2026" vẫn hiện.

## Không đổi
OBS-01..03 trong `claude_review_T23_FAIL_2026-10-20.md` giữ nguyên. Không đổi schema thêm so với T23 vòng 1.
