# REQUIREMENTS — Firefly Cinema

> Yêu cầu sản phẩm để hoàn thiện web và phần thực nghiệm. Mỗi yêu cầu có mã, gắn với task trong `BOI_CANH_DU_AN.md` mục 9.
> Trạng thái: `DONE` (đã có trong `phobert-v1`), `PLANNED`, `OPTIONAL`.
> Codex được đề xuất sửa file này ở bước PLANNING; Tín duyệt.

## 1. Người dùng

| Mã | Yêu cầu | Task | Trạng thái |
|---|---|---|---|
| FR-U01 | Xem phim đang chiếu / sắp chiếu, lọc theo thể loại, quốc gia, năm, chủ đề; tìm không dấu | — | DONE |
| FR-U02 | Xem chi tiết phim, lịch chiếu 5 ngày tới | — | DONE |
| FR-U03 | Đăng ký, đăng nhập (JWT 24h); chưa đăng nhập bấm giờ chiếu thì chuyển sang đăng nhập rồi quay lại | — | DONE |
| FR-U04 | Chọn ghế (tối đa 8, VIP F–H), đặt vé, không trùng ghế kể cả đặt đồng thời | — | DONE |
| FR-U05 | Xem "Vé của tôi" | — | DONE |
| FR-U06 | Gửi bình luận; bình luận tiêu cực bị ẩn khỏi trang phim | — | DONE |
| FR-U07 | Trang phim ưu tiên nhãn người duyệt nếu có | T06 | PLANNED |
| FR-U08 | Hủy vé trước giờ chiếu ít nhất 2 tiếng | T14 | OPTIONAL |
| FR-U09 | Đổi họ tên, đổi mật khẩu | T14 | OPTIONAL |

## 2. Quản trị

| Mã | Yêu cầu | Task | Trạng thái |
|---|---|---|---|
| FR-A01 | Xem bình luận theo nhãn tiêu cực / bình thường kèm điểm và tên model | — | DONE |
| FR-A02 | CRUD phim, kiểm tra dữ liệu, phim đã có vé chỉ chuyển `ended` | T04 | PLANNED |
| FR-A03 | CRUD suất chiếu, chặn chồng giờ cùng phòng (thời lượng + 15 phút), suất có vé không sửa/xóa | T05 | PLANNED |
| FR-A04 | Xác nhận / đổi nhãn / ẩn bình luận; giữ nguyên nhãn gốc của model | T06 | PLANNED |
| FR-A05 | Thống kê model đúng / sai so với người duyệt | T06 | PLANNED |
| FR-A06 | Xuất CSV bình luận đã duyệt (`text, text_norm, label`) | T06 | PLANNED |
| FR-A07 | Trang "So sánh mô hình": nhập một câu, xem các model chấm cạnh nhau (label, score, ms) | T07 | PLANNED |

## 3. Học máy và thực nghiệm

| Mã | Yêu cầu | Task | Trạng thái |
|---|---|---|---|
| FR-M01 | PhoBERT A phân loại bình luận, F1 lớp tiêu cực ≈ 0,918 trên test UIT-ViSFD | — | DONE |
| FR-M02 | Gom mã train, lưu dữ liệu lên Drive, model card A | T00 | PLANNED |
| FR-M03 | TF-IDF + NB / LR / LinearSVC, chọn siêu tham số trên dev, seed cố định | T01 | PLANNED |
| FR-M04 | Bảng so sánh ≥ 4 model cùng bộ chỉ số (P, R, F1 tiêu cực, macro-F1, ms/câu, dung lượng), ma trận nhầm lẫn, phân tích lỗi | T02 | PLANNED |
| FR-M05 | Bộ dữ liệu bình luận phim ≥ 400 câu, hướng dẫn gán nhãn, kappa ≥ 0,6 | T03 | PLANNED |
| FR-M06 | Đo lệch miền điện thoại → phim | T08 | PLANNED |
| FR-M07 | PhoBERT B fine-tune trên dữ liệu phim, tốt hơn A trên test phim | T09 | PLANNED |
| FR-M08 | Web nạp nhiều model, `ACTIVE_MODEL`, `MODEL_VERSION` | T07, T10 | PLANNED |
| FR-M09 | Thử nghiệm có tách từ | T15 | OPTIONAL |

## 4. Phi chức năng

| Mã | Yêu cầu | Kiểm bằng |
|---|---|---|
| NFR-01 | Giữ đúng thiết kế đã chốt (BOI_CANH mục 4) | Review giao diện |
| NFR-02 | Responsive tới điện thoại, focus bàn phím thấy được, tôn trọng `prefers-reduced-motion` | Kiểm tay |
| NFR-03 | Mọi trang có loading / rỗng / lỗi | Kiểm tay |
| NFR-04 | Lỗi trả một câu tiếng Việt rõ nguyên nhân và cách sửa | Review + probe |
| NFR-05 | Endpoint admin trả 403 với user thường | pytest (từ T11) / probe |
| NFR-06 | Web chạy được khi thiếu file model | Probe đổi `MODEL_DIR` |
| NFR-07 | Chế độ mock chạy đủ luồng | `VITE_USE_MOCK=true` |
| NFR-08 | Kết quả ML tái lập được (seed, cùng cách chia dữ liệu) | Chạy lại notebook |
| NFR-09 | Clone mới + làm theo `HUONG_DAN.md` là chạy được | T13 |
| NFR-10 | Dữ liệu bình luận thu thập không chứa tên người viết / thông tin cá nhân | Review T03 |

## 5. Ngoài phạm vi sản phẩm

Thanh toán thật, gửi email, ứng dụng điện thoại, đa rạp/đa chi nhánh, đăng nhập mạng xã hội.
