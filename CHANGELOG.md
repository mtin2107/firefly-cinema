# Changelog

## [Unreleased]

### Fixed

- Chặn đặt vé cho suất thuộc phim đã `ended` ở backend và mock; nguyên nhân là hai luồng chỉ kiểm tra suất tồn tại mà không kiểm tra trạng thái phim; tái hiện bằng probe mock và khóa backend bằng `test_cannot_book_showtime_for_ended_movie`.
- **F-02:** Không tạo lại suất seed mà admin đã xóa, kể cả khi xóa sạch cả ngày, bằng sidecar trạng thái gắn với file SQLite và ghi nguyên tử; ngày mới trong cửa sổ rolling vẫn bổ sung các phim còn thiếu dù đã có suất admin, suất/vé admin giữ nguyên, và phim mới chuyển `now_showing` vẫn được cấp lịch. Khi `seed()` bắt đầu với bảng `movies` rỗng, state được làm mới nguyên tử trước mọi commit để sidecar cũ hoặc hỏng không chặn lịch và vé mẫu của DB vừa reset; DB hiện hữu vẫn giữ cơ chế bảo vệ thao tác xóa. Nguyên nhân RF-03 là sidecar trước đó chỉ gắn theo đường dẫn nên bị nhận nhầm sau khi file DB được thay; khóa bằng chín regression test về reset, sidecar thiếu/hỏng, restart, rolling, conflict, phim mới và bảo toàn dữ liệu admin.
- Chuẩn hóa lỗi validation 422 thành câu tiếng Việt, kể cả lỗi sai kiểu do Pydantic sinh ra; nguyên nhân là handler công khai trực tiếp `err['msg']`; tái hiện và khóa bằng các test validation trong `test_admin_features.py` và `test_comments_health.py`.
- Vô hiệu hóa ô CSV bắt đầu bằng ký tự công thức trong bản export backend và mock, trong khi nội dung gốc vẫn nguyên vẹn; nguyên nhân là ghi thẳng text vào CSV; tái hiện bằng probe mock và khóa backend bằng `test_review_preserves_original_model_result_and_csv_is_safe`.
- Cô lập lỗi theo từng model tại `/api/admin/predict`; nguyên nhân là endpoint chỉ bắt `RuntimeError`, nên lỗi kiểu khác làm cả request trả 500; tái hiện và khóa bằng `test_predict_isolates_each_model_failure`.
- Ẩn chi tiết lỗi và đường dẫn nội bộ khỏi `/api/health`; nguyên nhân là endpoint trả nguyên văn lỗi classifier/model; tái hiện và khóa bằng `test_health_does_not_expose_internal_classifier_errors`.
- Trả 401 cho JWT có `sub` thiếu hoặc sai kiểu thay vì lỗi 500; nguyên nhân là chuyển `sub` sang số ngoài khối xử lý token lỗi; tái hiện và khóa bằng `test_register_login_me_and_invalid_tokens`.
- Từ chối bình luận chỉ gồm khoảng trắng; nguyên nhân là kiểm tra độ dài chạy trước khi loại khoảng trắng; tái hiện và khóa bằng `test_blank_comment_returns_vietnamese_422`.
- Cho phép admin sửa hoặc xóa suất seed trong mock khi chưa có vé thật; nguyên nhân là ghế trang trí từ `seedBooked()` bị tính nhầm thành vé; tái hiện và xác minh bằng probe mock CRUD suất chiếu.


## T26 — 24/10/2026

- Thay hàng sao đầu trang chi tiết bằng nút điểm mở dialog gốc; chọn sao tạm, xác nhận lưu hoặc hủy qua API hiện có.
- Dialog thông báo kết quả/lỗi, hỗ trợ Esc, bấm ngoài, vòng Tab và trả focus; bố cục 375px/1280px, không thêm hiệu ứng hoặc thư viện.
- Giữ chuyển đăng nhập kèm trang quay lại, chặn phim sắp chiếu và giữ nguyên sao trong form bình luận; không đổi schema.

## T25 — 24/10/2026

- Thêm banner trailer chỉ nạp sau khi bấm, phát file video có tua hoặc YouTube riêng tư nâng cao; mục Nội dung phim nhiều đoạn trước Lịch chiếu.
- Admin upload MP4/WebM body thô tối đa 100 MiB, kiểm chữ ký và ghi dần; chọn file ưu tiên hơn link YouTube, có gỡ trailer. API real/mock cùng contract.
- Thêm synopsis và trailer_url nullable; seed 21 synopsis, không bịa link trailer. Schema cũ cần PO backup và reset theo HUONG_DAN.
- Route Range riêng cho Starlette 0.38.6; test upload, quyền, cleanup, Range và validator.


## 2026-10-24 — T27
- Thang điểm nguyên 1–10 xuyên suốt API, seed, bình luận, dashboard và mock; API rating bổ sung phân bố đầy đủ.
- Khung đánh giá có poster, vòng điểm, 5 thanh phân bố, 10 sao và nhãn tiếng Việt; giữ lưu/hủy/đóng và focus của T26.
- GSAP mở khung, nảy sao, đom đóm và cập nhật điểm khi lưu; hỗ trợ giảm chuyển động, tự dọn hiệu ứng. Focus đơn thuần không tô sao (T26 TODO-01).
- Đổi constraint SQLite; PO cần sao lưu/xác minh rồi reset sau merge theo HUONG_DAN mục T27. Implementation chỉ dùng SQLite tạm.

## T28 — 26/10/2026

- Sửa quy tắc chung cho dấu tiếng Việt, căn hàng thẻ phim, header, banner không trailer và poster phụ ở hero; không vá từng phim hoặc movies.json.
- Trạng thái phim hiệu lực theo ngày dùng chung ở API/SQL filter, chấm điểm, chatbot và mock; admin báo lỗi ngày Sắp chiếu không hợp lệ và giải thích trạng thái tự chuyển.
- Sửa tween sao khi rời chuột nhanh, tăng vùng bấm và khoảng cách, 2 hàng trên màn hình hẹp; tôn trọng giảm chuyển động.
- Thêm GET /api/auth/me/summary và trang Tài khoản gồm hồ sơ, 6 số liệu, vé/bình luận/điểm gần đây, cài đặt; giữ logic đổi tên và mật khẩu T14.
- Footer có Liên hệ, dữ liệu tập trung ở CONTACT; cho phép Poster màu khi thêm phim không ảnh theo T28 AC-13.
- Thêm test T28 về thống kê riêng tư/nhãn duyệt và trạng thái ngày hôm qua/hôm nay/ngày mai; điều chỉnh hai test cũ bị ảnh hưởng trực tiếp. Không đổi schema DB, không thêm thư viện, không đổi biến :root.
