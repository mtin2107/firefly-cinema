# Changelog

## [Unreleased]

### Fixed

- Chặn đặt vé cho suất thuộc phim đã `ended` ở backend và mock; nguyên nhân là hai luồng chỉ kiểm tra suất tồn tại mà không kiểm tra trạng thái phim; tái hiện bằng probe mock và khóa backend bằng `test_cannot_book_showtime_for_ended_movie`.
- Không tạo lại suất seed mà admin đã xóa khi backend khởi động lại; nguyên nhân là `seed()` luôn gọi `_ensure_showtimes()` trên database đã có dữ liệu; tái hiện và khóa bằng `test_deleted_seed_showtime_is_not_recreated_on_restart`.
- Chuẩn hóa lỗi validation 422 thành câu tiếng Việt, kể cả lỗi sai kiểu do Pydantic sinh ra; nguyên nhân là handler công khai trực tiếp `err['msg']`; tái hiện và khóa bằng các test validation trong `test_admin_features.py` và `test_comments_health.py`.
- Vô hiệu hóa ô CSV bắt đầu bằng ký tự công thức trong bản export backend và mock, trong khi nội dung gốc vẫn nguyên vẹn; nguyên nhân là ghi thẳng text vào CSV; tái hiện bằng probe mock và khóa backend bằng `test_review_preserves_original_model_result_and_csv_is_safe`.
- Cô lập lỗi theo từng model tại `/api/admin/predict`; nguyên nhân là endpoint chỉ bắt `RuntimeError`, nên lỗi kiểu khác làm cả request trả 500; tái hiện và khóa bằng `test_predict_isolates_each_model_failure`.
- Ẩn chi tiết lỗi và đường dẫn nội bộ khỏi `/api/health`; nguyên nhân là endpoint trả nguyên văn lỗi classifier/model; tái hiện và khóa bằng `test_health_does_not_expose_internal_classifier_errors`.
- Trả 401 cho JWT có `sub` thiếu hoặc sai kiểu thay vì lỗi 500; nguyên nhân là chuyển `sub` sang số ngoài khối xử lý token lỗi; tái hiện và khóa bằng `test_register_login_me_and_invalid_tokens`.
- Từ chối bình luận chỉ gồm khoảng trắng; nguyên nhân là kiểm tra độ dài chạy trước khi loại khoảng trắng; tái hiện và khóa bằng `test_blank_comment_returns_vietnamese_422`.
- Cho phép admin sửa hoặc xóa suất seed trong mock khi chưa có vé thật; nguyên nhân là ghế trang trí từ `seedBooked()` bị tính nhầm thành vé; tái hiện và xác minh bằng probe mock CRUD suất chiếu.
