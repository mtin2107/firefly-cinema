# Claude — Rà soát toàn web trước T13

- Ngày: 2026-10-22 · Commit: `master` `c8f3cf0` (đã có T22, T23)
- Cách làm: đọc tĩnh code; backend thật trên SQLite tạm (không đụng `backend\firefly.db`) + frontend thật; quét 28 route ở 1280px và 375px với ba vai trò khách / người dùng / admin; gọi API trực tiếp cho các trường hợp biên.

## 1. Đạt
- Không còn `console.log`/`debugger`; trang nào cũng có tiêu đề tab; mọi `<Link>` trỏ tới route có thật.
- 28 route: không ảnh lỗi, không ảnh thiếu `alt`, không nút/ô nhập thiếu tên truy cập, không tràn ngang ở 375px (các dải ngày và tab dùng cuộn ngang có chủ đích).
- Phân quyền: khách vào trang cần đăng nhập → sang đăng nhập; user vào trang admin → thông báo chặn; đã đăng nhập vào `/dang-nhap` → về trang chủ.
- Trang lỗi: phim/suất không tồn tại có thông báo tiếng Việt; route lạ ra trang 404.
- Đồng bộ: `movies.json` frontend = backend (21 phim); luật ghế khớp (A–H, 12 cột, VIP F–H, phụ thu 20.000).
- Health `ok`, `phobert_b`.

## 2. Phát hiện
| # | Mức | Vấn đề | Bằng chứng | Đề xuất |
|---|---|---|---|---|
| A-01 | Medium | Suất đã chiếu hoặc còn dưới 30 phút vẫn cho chọn ghế; tới bước cuối mới báo lỗi, câu báo "Suất chiếu sắp bắt đầu" sai với suất đã qua. Lịch chiếu ở trang phim vẫn liệt kê suất trong 30 phút trước giờ chiếu | Suất 09:30 22/10 mở `/dat-ve/1` lúc tối: ghế bấm được, nút "Tiếp tục" bật; `POST /api/bookings` → 400 "Suất chiếu sắp bắt đầu…" | Lịch chiếu chỉ hiện suất còn đặt online được (hoặc hiện mờ "Mua tại quầy"); trang chọn ghế khóa sơ đồ và báo rõ khi đã quá giờ |
| A-02 | Medium (demo) | Chưa cấu hình ngân hàng trong `backend\.env` (`BANK_ID`, `BANK_ACCOUNT`, `BANK_ACCOUNT_NAME` không có) → vé giữ chỗ không hiện QR, không có nút "Tôi đã chuyển khoản"; luồng thanh toán QR của T16 không demo được | Kiểm tra tên khóa trong `.env` (không đọc giá trị) | Tín điền 3 khóa (có thể dùng tài khoản demo) rồi khởi động lại backend |
| A-03 | Medium (demo) | Chatbot không trả lời: 2/2 lần gọi hết thời gian chờ 25 giây (`APITimeoutError`) → "Trợ lý đang bận". Cấu hình đúng (`CHAT_API_KEY` có, model `gemini-3.5-flash-lite`), mạng tới Google bình thường | Log backend; `curl` tới API Google 0,36 s | Tín kiểm tra hạn mức/khóa trong Google AI Studio và thử lại trước khi quay video |
| A-04 | Low | Trang Tổng quan quản trị (T23) lệch phong cách trang Thống kê cảm xúc (T21): chọn khoảng bằng ô thả xuống thay vì tab 7/30/90, số liệu không có màu nhấn, bảng xếp A–Z cả phim doanh thu 0 | Ảnh chụp hai trang 1280px | Dùng lại kiểu tab và thẻ số của T21; xếp bảng theo doanh thu giảm dần |
| A-05 | Low | User thường vào trang admin: thông báo chặn đúng nhưng tiêu đề tab giữ tiêu đề trang trước | `/quan-tri/tong-quan` với tài khoản demo → tiêu đề "Trang chủ – Firefly Cinema" | `ProtectedRoute` đặt tiêu đề khi chặn |
| A-06 | Low | Trang "không tìm thấy phim/suất" có nút "Thử lại" vô ích | `/phim/9999`, `/dat-ve/999999` | Bỏ nút Thử lại khi lỗi 404 |
| A-07 | Low | "Vé của tôi" trộn vé sắp xem với vé đã chiếu; vé paid của suất đã qua không có nhãn "Đã chiếu" | Đọc code `MyTickets.jsx`/`TicketStub.jsx` | Tách hai nhóm hoặc thêm nhãn |

Các mục đã biết, giữ nguyên: T12 TODO-01 (model B che câu khen phim 1), T14 TODO-02 (mã vé dùng lại), T22 OBS-01/02, T23 OBS-01..03.

## 3. Ngoài phạm vi v1.0 (đã chốt không làm)
Trailer, quên mật khẩu, quản lý/khóa tài khoản, sửa bình luận đã đăng, chỉ người đã mua vé mới chấm sao.

## 4. Đề xuất cho PO
- A-02, A-03 là cấu hình, Tín tự xử lý, không cần code.
- A-01 nên sửa trước T13 (ảnh hưởng luồng đặt vé chính khi demo buổi tối). A-04..A-07 có thể gộp chung một fix nhỏ hoặc ghi vào hạn chế.
