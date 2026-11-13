# Claude implementation — T33 Tự xác nhận thanh toán VietQR qua webhook SePay

- Ngày: 13/11/2026
- Người làm: Claude (PO yêu cầu trong chat: "việc này bạn sẽ tự làm"; Q1 và Q2 "làm thêm liền bây giờ")
- Nhánh: `task/T33-sepay-webhook` từ master `7322d15`
- Trạng thái đề xuất: **INDEPENDENT_REVIEW**. Claude viết code nên cần Codex hoặc Tín review độc lập trước khi merge.

## 1. Quyết định của PO
| Câu hỏi | Chốt |
|---|---|
| Q1 Xác thực | Làm cả HMAC-SHA256 và API key. Có `SEPAY_WEBHOOK_SECRET` thì bắt buộc HMAC |
| Q2 Giao dịch cần xử lý tay | Thêm phần admin xem và đánh dấu "Đã xử lý", đặt trong trang Quản lý vé |
| Q3 Người code | Claude |

## 2. Thay đổi
**Backend**
- `config.py`: thêm `SEPAY_WEBHOOK_SECRET`, `SEPAY_API_KEY`. `.env.example` thêm hai dòng để trống.
- `models.py`: thêm `PaymentTransaction` (bảng `payment_transactions`). PK là `id` của SePay, dùng làm khóa chống trùng. CHECK `result IN ('paid','needs_review','ignored','resolved')`.
  - `booking_id` **không đặt FK** để khách vẫn hủy được vé đang giữ dù đã có giao dịch thiếu tiền gắn với vé đó (có test).
- `schemas.py`: thêm `SepayWebhookIn`, `PaymentOut`.
- `routers/payments.py` (mới):
  - `POST /api/payments/sepay-webhook`. Xác thực trên raw body bằng `hmac.compare_digest`; timestamp lệch quá 300 giây bị từ chối.
  - Chống trùng theo `id`, gọi `expire_holds` trước khi khớp vé.
  - Tìm mã vé trong `code` hoặc `content` bằng regex `FF(\d{5,9})`, không phân biệt hoa thường.
  - Đủ tiền → `paid`. Thiếu tiền, vé không còn chờ, không tìm thấy mã → `needs_review`. Tiền ra → `ignored`.
  - Đã xác thực thì luôn trả `{"success": true}`.
  - `GET /api/admin/payments?result=` và `POST /api/admin/payments/{id}/resolve` dùng `require_admin`.
- `main.py`: đăng ký router.

**Frontend**
- `real.js` và `mock.js`: thêm `admin.payments.list/resolve`, cùng cấu trúc JSON. Mock có 2 giao dịch mẫu, và tự bổ sung khi `localStorage` cũ chưa có `payments`.
- `AdminBookings.jsx`: thêm khu "Giao dịch SePay" (lọc theo kết quả, nút "Đã xử lý") dưới bảng vé.
- `MyTickets.jsx`: tự gọi lại `bookings.mine` mỗi 5 giây khi có vé `held` hoặc `pending_verify` của suất **chưa chiếu**. Dừng khi hết vé chờ hoặc rời trang.
- `TicketStub.jsx`: câu hướng dẫn cạnh mã QR.
- `global.css`: hai lớp `.admin-payments` (không đổi `:root`).

**Tài liệu:** `HUONG_DAN.md` thêm mục T33 (cấu hình SePay, `.env`, tunnel, thử bằng Test mode, xử lý giao dịch tay). `docs/tasks/T33.md`, `docs/DE_XUAT_T33_THANH_TOAN.md`.

**Không đổi:** `booking_rules.py`, luồng admin duyệt và từ chối tay, `requirements.txt`, `package.json`.

## 3. Gate
| Gate | Kết quả |
|---|---|
| `python -m compileall -q backend\app` | OK |
| `pytest` toàn bộ | **313/313 PASS** (290 cũ + 23 mới trong `test_t33_sepay_webhook.py`) |
| `npm run build` mock (`VITE_USE_MOCK=true`) | OK |
| `npm run build` real (`VITE_USE_MOCK=false`) | OK |
| `/api/health` | `"classifier":"phobert_b"` (backend của PO cổng 8000 và backend thử nghiệm cổng 8019) |

## 4. Bằng chứng theo AC
| AC | Kết quả | Bằng chứng |
|---|---|---|
| AC-01, AC-02 | PASS | `test_valid_webhook_marks_booking_paid[held/pending_verify]` |
| AC-03 | PASS | `test_hmac_rejects_bad_requests` (5 trường hợp), không ghi DB, vé giữ `held` |
| AC-04 | PASS | `test_api_key_mode`, `test_disabled_without_secret_or_key` (503) |
| AC-05 | PASS | `test_duplicate_id_is_processed_once` |
| AC-06 | PASS | `test_underpaid_needs_review_and_overpaid_is_paid` ("Thiếu 1.000 đ.", "Dư 5.000 đ.") |
| AC-07 | PASS | `test_non_pending_booking_is_not_changed` (3 trạng thái), `test_money_after_hold_expired_does_not_restore_seats` |
| AC-08 | PASS | `test_unmatched_or_outgoing` (3 trường hợp), `test_invalid_body_returns_422` |
| AC-09 | PASS | `test_code_from_sepay_or_bank_memo` (`code` và `MBVCB.123.ff000xx.chuyen tien`) |
| AC-10 | PASS | Trình duyệt real (5194 → 8019, DB tạm): vé FF00144 đang giữ chỗ, gửi webhook HMAC → sau khoảng 6 giây hiện "Đã thanh toán", không tải lại trang. Hết vé chờ của suất sắp chiếu thì không còn request (2 → 2 trong 11 giây). Có vé giữ chỗ thì request tăng (2 → 4) |
| AC-11 | **CHƯA LÀM: chờ PO** | Cần tài khoản SePay Test mode và tunnel. Claude không có quyền truy cập my.sepay.vn |
| AC-12 | PASS | Bản sao `firefly.db` (đã xóa bảng mới để thử từ đầu): users 9, bookings 143, comments 30, showtimes 238, movies 21 không đổi trước và sau `create_all`, bảng `payment_transactions` được tạo |
| AC-13 | PASS | `git diff` không có key; `.env.example` chỉ có hai dòng trống; log chỉ ghi `id`, mã vé, kết quả |
| AC-14 | Một phần | Gate đạt; pytest phủ luồng đặt vé, hủy, admin duyệt và từ chối. **Chưa chạy tay toàn bộ checklist `BOI_CANH_DU_AN.md` mục 7** |
| AC-15 | PASS | `test_admin_lists_and_resolves` (403 user thường, 409, 404). Trình duyệt real: bấm "Đã xử lý" giao dịch 330002 → biến khỏi danh sách "Cần xử lý tay". Trình duyệt mock: khu giao dịch hiện giao dịch mẫu 90002, "Đã xử lý" hoạt động |

## 5. Lỗi phát hiện và đã sửa trong lúc làm
- Bản đầu tự làm mới với mọi vé `pending_verify`. DB seed có vé `pending_verify` của suất đã qua nên trang tự làm mới mãi. Đã sửa: chỉ xét vé của suất chưa chiếu.
- Giờ giao dịch mẫu trong mock hiển thị theo UTC. Đã đổi sang giờ địa phương giống `transactionDate` của SePay.

## 6. Ghi chú cho reviewer
- **Định dạng chữ ký HMAC theo tài liệu SePay:** `X-SePay-Signature: sha256=<hex>`, ký `"{timestamp}.{raw_body}"`. Code so khớp với hex chữ thường (header được hạ chữ thường trước khi so). Chưa thử với SePay thật (AC-11). Nếu lệch, PO chuyển webhook sang API Key và để trống `SEPAY_WEBHOOK_SECRET`.
- **Regex mã vé** không có ranh giới từ, vì ngân hàng có thể dính liền chữ. Nếu khớp nhầm vé khác thì số tiền vẫn phải đủ mới thành `paid`. Ưu tiên `code` do SePay tách khi PO cấu hình tiền tố `FF`.
- **Tiền về sau khi hết hạn giữ chỗ:** vé không được cấp lại, giao dịch thành `needs_review` để hoàn tiền tay. Đây là hành vi có chủ đích (AC-07).
- **Endpoint là `async`** để đọc raw body, nhưng vẫn dùng Session đồng bộ. Mỗi webhook chỉ vài truy vấn SQLite nên chấp nhận được ở quy mô demo.
- **Bảng `payment_transactions` đã có sẵn trong `backend/firefly.db` thật** (0 dòng): backend của PO đang chạy `--reload` trên nhánh này nên đã tự tạo khi code đổi. Nếu không merge T33 thì bảng rỗng này vô hại.
- **Console lỗi `useAuth(...) is null`** chỉ xuất hiện khi Vite HMR nạp lại `AuthContext` lúc đang sửa `mock.js` (URL có `?t=`). Tải lại trang thì hết; không liên quan đến code T33.

## 7. Việc PO cần làm
1. Review độc lập (Codex hoặc Tín).
2. AC-11: cấu hình theo `HUONG_DAN.md` mục T33, mở tunnel, dùng "Mô phỏng giao dịch" ở Test mode, chụp log SePay báo thành công.
3. Chạy tay checklist hồi quy mục 7 nếu reviewer yêu cầu.
4. Merge do Tín quyết định.
