# Đề xuất T33 — Thanh toán trực tuyến (bản thảo để tham khảo)

> Trạng thái: **ĐỀ XUẤT, chưa duyệt.** Chưa phải Task Record, chưa có nhánh, chưa viết code.
> Người soạn: Claude, 12/11/2026. Người quyết: Tín.

## 1. Hiện trạng của web

- Vé có các trạng thái `held` → `pending_verify` → `paid`, cùng `expired` và `rejected` (ràng buộc nằm trong `backend/app/models.py`).
- Trang Checkout đã sinh mã **VietQR động** chứa số tiền và mã vé, tiền chuyển về tài khoản ngân hàng của Tín (`backend/app/booking_rules.py`, hàm `qr_url`).
- Khách quét QR bằng app của bất kỳ ngân hàng nào là chuyển được. **Phần còn thiếu duy nhất: hệ thống không tự biết tiền đã về.** Admin phải duyệt tay.

**Mục tiêu T33:** tiền về đúng tài khoản cá nhân của Tín, vé tự chuyển sang `paid` trong vài giây, không cần admin duyệt.

## 2. Các phương án

### A. VietQR + SePay webhook (đề xuất chính)

**Cách hoạt động:**
1. Liên kết tài khoản ngân hàng cá nhân của Tín với SePay. Tín tự làm trên my.sepay.vn.
2. Khách quét VietQR như hiện tại. Nội dung chuyển khoản có mã vé.
3. Khi tiền về, SePay gửi webhook (POST JSON) tới backend. Webhook có số tiền, nội dung chuyển khoản và mã giao dịch.
4. Backend xác thực webhook, tìm mã vé, kiểm tra số tiền và trạng thái, rồi chuyển vé sang `paid`.
5. Trang Checkout tự cập nhật trạng thái để khách thấy vé đã thanh toán.

| Ưu | Nhược |
|---|---|
| Tiền thật về tài khoản cá nhân | Webhook cần **URL công khai**: SePay không chấp nhận localhost, nên phải dùng ngrok/cloudflared hoặc deploy |
| Không cần giấy phép kinh doanh, không ký hợp đồng merchant | Phụ thuộc dịch vụ bên thứ ba; gói miễn phí và giới hạn **chưa xác minh** |
| Giữ nguyên VietQR, thay đổi nhỏ | Khách chuyển sai nội dung hoặc sai số tiền thì phải xử lý tay |
| Không cần thêm thư viện: chỉ dùng `hmac` có sẵn | |

### B. VNPay sandbox

Chuyển hướng khách sang cổng VNPay, dùng thẻ test NCB, VNPay trả kết quả về Return URL hoặc IPN, có chữ ký HMAC-SHA512.

| Ưu | Nhược |
|---|---|
| Giao diện cổng quen thuộc, hội đồng dễ nhận ra | **Tiền ảo**, không về tài khoản thật |
| Demo trên localhost được (dùng Return URL) | Phải đăng ký tài khoản sandbox; sandbox đôi khi chập chờn |
| Code mẫu nhiều trên mạng | IPN (xác nhận phía server) vẫn cần URL công khai |

### C. VNPay / MoMo production

| Ưu | Nhược |
|---|---|
| Cổng thật, chuyên nghiệp | Phải ký hợp đồng merchant và qua thẩm định. Chưa tìm được tài liệu chính thức nói cá nhân không có giấy phép kinh doanh có đăng ký được hay không. **Cần hỏi thẳng VNPay/MoMo** |
| | Thời gian duyệt có thể lâu, không chắc kịp tiến độ khóa luận |

### D. Cổng mô phỏng trong web

Một trang giả lập cổng thanh toán, có chữ ký HMAC, chạy offline. Ổn định nhất cho buổi bảo vệ, nhưng không có tiền thật. Chỉ nên làm **phương án dự phòng** khi demo.

## 3. Đề xuất của Claude

**Làm A (VietQR + SePay).** Đây là phương án duy nhất đáp ứng cả hai yêu cầu "tiền thật" và "tài khoản cá nhân" mà không cần giấy phép.
Giữ nguyên nút admin duyệt tay và trả tại quầy làm dự phòng.
B có thể làm thêm thành task riêng nếu muốn có nút "VNPay" trên giao diện.

## 4. Yêu cầu bảo mật bắt buộc (dùng làm tiêu chí nghiệm thu)

1. **Xác thực webhook.** SePay hỗ trợ API Key hoặc HMAC-SHA256. Sai thì trả 401 và không xử lý.
2. **Đối chiếu số tiền.** Số tiền nhận phải ≥ tổng tiền vé; trường hợp thiếu hoặc dư phải có quy tắc rõ ràng. Không tin bất kỳ tham số nào từ phía trình duyệt.
3. **Chống xử lý trùng.** Một mã giao dịch chỉ được xử lý một lần, vì webhook có thể được gửi lại.
4. **Vé hết hạn.** Tiền về khi vé đã `expired` thì không tự cấp vé. Phải ghi nhận lại để admin hoàn tiền tay.
5. **Bí mật.** Key để trong `.env`, không commit, không ghi log.
6. Endpoint webhook chỉ nhận đúng định dạng mong đợi; lỗi trả một câu tiếng Việt theo quy ước dự án.

## 5. Ảnh hưởng tới dự án

- **Schema:** để chống trùng cần lưu mã giao dịch, tức thêm bảng hoặc cột. Dự án chưa có migration nên **phải xóa `backend/firefly.db`** sau khi merge.
- **API:** endpoint webhook mới (chỉ backend). Nếu thêm API cho frontend kiểm tra trạng thái vé thì phải có ở cả `real.js` và `mock.js`.
- **Thư viện:** không thêm.
- **Demo:** chuẩn bị ngrok/cloudflared trước hôm bảo vệ, chỉ chuyển số tiền nhỏ, có kịch bản dự phòng (admin duyệt tay).

## 6. Rủi ro cần lưu ý

- **Pháp lý:** thu tiền thật của người lạ qua một web chưa đăng ký kinh doanh là rủi ro. Chỉ nên dùng cho Tín, giảng viên và hội đồng thử.
- **Hoàn tiền:** chuyển thiếu, chuyển dư, sai nội dung, vé hết hạn đều phải hoàn tay.
- **Trọng tâm khóa luận:** đề tài là PhoBERT. Phần thanh toán không nên lấy thời gian của phần ML và báo cáo.

## 7. Câu hỏi nên mang đi hỏi thêm

1. Giảng viên hướng dẫn có yêu cầu hay chấp nhận thanh toán thật không, hay sandbox là đủ?
2. SePay: gói miễn phí có giới hạn gì (số giao dịch, số tài khoản, webhook)? Ngân hàng của Tín có được hỗ trợ không?
3. VNPay/MoMo: cá nhân không có giấy phép kinh doanh có đăng ký merchant được không, và mất bao lâu?
4. Casso có rẻ hơn hoặc dễ hơn SePay cho trường hợp này không?
5. Hôm bảo vệ, phòng có internet ổn định để nhận webhook không?

## Nguồn đã tham khảo

- SePay Webhooks: https://developer.sepay.vn/en/sepay-webhooks
- SePay tạo webhook (URL công khai, kiểu xác thực): https://developer.sepay.vn/en/sepay-webhooks/tao-webhook
- SePay liên kết tài khoản ngân hàng: https://developer.sepay.vn/en/sepay-webhooks/tai-khoan-ngan-hang
- SePay ví dụ chống trùng (PHP): https://developer.sepay.vn/vi/sepay-webhooks/lap-trinh-webhooks/lap-trinh-webhook
- Điều kiện merchant VNPay: **chưa tìm thấy tài liệu chính thức**, chỉ có bài viết bên thứ ba.
