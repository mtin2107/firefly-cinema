# Kịch bản demo Firefly Cinema (6 phút 30 giây)

## Chuẩn bị trước khi trình bày

- Tắt cửa sổ **Backend** cũ trước khi chạy lại `reset-demo.bat`; script sẽ từ chối reset nếu database còn bị Backend khóa.
- Chạy `reset-demo.bat`, sau đó `chay-firefly.bat`; chỉ bắt đầu khi cửa sổ lệnh báo backend dùng PhoBERT.
- Dùng tài khoản khách `demo@firefly.vn` và tài khoản `admin@firefly.vn`; mật khẩu lấy từ cấu hình môi trường của máy demo, không ghi vào tài liệu.
- Mở sẵn hai cửa sổ trình duyệt: cửa sổ khách và cửa sổ riêng tư cho admin. Đặt mức thu phóng 100%.
- Câu bình luận và câu so sánh bên dưới nên được sao chép sẵn để tránh lỗi gõ.

## Luồng trình diễn

| Thời gian | Thao tác | Câu nói gợi ý | Nội dung sẽ gõ | Kết quả mong đợi có thể kiểm tra |
|---|---|---|---|---|
| 0:00–1:20 | Khách đăng nhập, mở **Chuyến Tàu Cuối Mùa Mưa**, chọn suất và hai ghế còn trống, bấm đặt vé. | “Khách chọn phim, suất và ghế trực tiếp; hệ thống giữ chỗ trong 15 phút để tránh chiếm ghế vô thời hạn.” | Không có. | Trang vé hiện mã `FF…`, đúng hai ghế, trạng thái **Giữ chỗ – chưa thanh toán** và thời điểm tự hủy không quá 15 phút sau lúc đặt. |
| 1:20–2:05 | Trở lại trang phim và gửi bình luận. | “PhoBERT B chấm ngay khi gửi. Bình luận tiêu cực vẫn được lưu, nhưng nội dung bị che mặc định với người xem.” | `Phim dài lê thê, nửa đầu buồn ngủ thật sự, phí tiền vé.` | Thông báo màu cảnh báo xuất hiện; bình luận mới đứng đầu và hiện dòng **Bình luận này đã được ẩn…** cùng nút **Vẫn xem**. |
| 2:05–3:15 | Sang cửa sổ admin → **Kiểm duyệt bình luận**. Tìm bình luận mới, bấm **Xác nhận nhãn**, rồi **Đổi sang bình thường**. | “Quản trị viên thấy điểm và phiên bản model, có thể xác nhận hoặc sửa nhãn; nhãn người duyệt được ưu tiên mà kết quả gốc vẫn được giữ.” | Không có. | Số **Đã duyệt** tăng; sau khi đổi nhãn, nhãn duyệt là **Bình thường**, nhãn model vẫn **Tiêu cực** và số **Model sai** tăng. Tải lại trang phim: nội dung không còn bị che bởi nhãn hiệu lực. |
| 3:15–4:20 | Admin mở **So sánh mô hình**, chọn câu mẫu đầu tiên và bấm **Chấm điểm**. | “Cùng một câu khó được đưa qua các checkpoint. Đây là đầu ra suy luận thật trên máy, không phải số viết sẵn.” | `Phim dài lê thê, nửa đầu buồn ngủ thật sự.` | Bảng trả ít nhất PhoBERT A và PhoBERT B, có phiên bản, nhãn, điểm và thời gian. Đối chiếu đầu ra thật đã ghi trong report T12; nếu A/B không còn cho kết quả như report thì nói rõ checkpoint đang chạy và không khẳng định kết luận cũ. |
| 4:20–5:25 | Trình bày bảng số liệu T02/T09 bên dưới. | “T02 cho mốc mô hình A trên miền gốc; T09 đo lại trên bình luận phim và huấn luyện B. Vì hai tập kiểm thử khác nhau, không so trực tiếp 0,9216 với 0,9175.” | Không có. | Người xem thấy rõ tên tập đo và chỉ số; nhấn mạnh trên movie test, F1 tiêu cực tăng từ `0,857143` lên `0,917526`. |
| 5:25–6:30 | Mở **Vé của tôi** rồi trang admin vé; chỉ nhanh ba trạng thái seed. | “Dữ liệu demo còn có vé đã thanh toán, chờ xác nhận và hết hạn; lần reset nào cũng tạo cùng số bản ghi.” | Không có. | Khách thấy vé `paid`, `pending_verify`, `expired`; admin lọc được **Chờ xác nhận chuyển khoản**. Kết thúc trước 7 phút. |

## Bảng số liệu nói trong demo

| Nguồn | Mô hình / tập đo | Chỉ số đã chốt |
|---|---|---|
| T02 | PhoBERT A canonical, tập kiểm thử miền gốc | F1 tiêu cực `0,9216` |
| T09 | PhoBERT A, movie test 149 câu | F1 tiêu cực `0,857143` |
| T09 | PhoBERT B, cùng movie test 149 câu | F1 tiêu cực `0,917526`; Macro-F1 `0,881840` |
| T09 | PhoBERT B, kiểm tra giữ chất lượng miền điện thoại | Mức giảm F1 `0,002783` |

## Phương án dự phòng

### Mất mạng

Luồng đặt vé, bình luận, kiểm duyệt và so sánh model đều chạy cục bộ. Không mở chatbot và không tải QR/poster từ URL ngoài. Nếu trình duyệt báo mất mạng, tiếp tục với `localhost`; dùng poster đã tải sẵn từ máy.

### Model lỗi hoặc khởi động quá lâu

1. Dừng frontend đang chạy.
2. Trong cửa sổ lệnh mới, chạy `cd frontend`, đặt `VITE_USE_MOCK=true`, rồi chạy `npm run dev`.
3. Mở lại trang, đăng nhập và thực hiện cùng kịch bản. Mock mode dùng bộ 30 bình luận, ba trạng thái vé và hai hàng PhoBERT A/B minh họa. Khi trình bày phải nói rõ đây là dữ liệu dự phòng, không gọi model thật.

Nếu localStorage chứa dữ liệu mock cũ, xóa dữ liệu trang `localhost:5173` rồi tải lại để nhận bộ demo mới.

## Poster thật — Tín bổ sung trước ngày bảo vệ

- [ ] Chuyến Tàu Cuối Mùa Mưa: ______________________________
- [ ] Bóng Ma Hẻm 37: ______________________________________
- [ ] Đội Cứu Hộ Sông Hồng: _________________________________
- [ ] Mèo Mướp Đi Lạc: _____________________________________
- [ ] Thứ Bảy Không Ngủ: ___________________________________
- [ ] Bản Hòa Âm Mùa Hạ: ___________________________________
