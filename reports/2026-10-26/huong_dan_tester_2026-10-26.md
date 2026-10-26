# Hướng dẫn test Firefly Cinema (26/10/2026)

Bản đang chạy: `master` @ `f48922a` (đã có T27 — thang điểm 10). Model bình luận: **PhoBERT B**.

## 1. Mở web

| Mục | Địa chỉ |
|---|---|
| Website | http://localhost:5173 |
| Kiểm tra máy chủ | http://localhost:8000/api/health → phải có `"classifier":"phobert_b"` |

Tài khoản:

| Vai trò | Email | Mật khẩu |
|---|---|---|
| Khách | demo@firefly.vn | 123456 |
| Quản trị | admin@firefly.vn | admin123 |

Nên mở **hai cửa sổ**: cửa sổ thường cho khách, cửa sổ ẩn danh cho admin. Có thể tự đăng ký thêm tài khoản khách.

## 2. Các ca test

Đánh dấu Đạt / Lỗi cho từng ca. Gặp lỗi thì ghi theo mẫu ở mục 3.

### A. Xem phim (chưa đăng nhập)
| # | Thao tác | Kết quả mong đợi |
|---|---|---|
| A1 | Mở trang chủ | Banner băng chuyền chạy, có danh sách phim, điểm hiển thị dạng `x.x/10` |
| A2 | Menu → Thể loại / Chủ đề, chọn một mục | Ra đúng phim thuộc mục đó |
| A3 | Ô tìm kiếm gõ `meo muop` (không dấu) | Ra phim **Mèo Mướp Đi Lạc** |
| A4 | Bấm "Xem chi tiết" một phim | Có hiệu ứng poster, trang chi tiết có nội dung phim, trailer, bình luận |
| A5 | Bấm vào một giờ chiếu khi chưa đăng nhập | Bị chuyển sang trang đăng nhập; đăng nhập xong quay lại đúng trang cũ |

### B. Tài khoản
| # | Thao tác | Kết quả mong đợi |
|---|---|---|
| B1 | Đăng ký tài khoản mới | Thành công, tự đăng nhập |
| B2 | Đăng ký trùng email / mật khẩu quá ngắn | Báo lỗi bằng tiếng Việt, không tạo tài khoản |
| B3 | Đăng nhập sai mật khẩu | Báo lỗi tiếng Việt |
| B4 | Trang tài khoản → đổi mật khẩu, đăng xuất rồi đăng nhập bằng mật khẩu mới | Đăng nhập được bằng mật khẩu mới, mật khẩu cũ không còn dùng được |

### C. Đặt vé (đăng nhập khách)
| # | Thao tác | Kết quả mong đợi |
|---|---|---|
| C1 | Chọn phim đang chiếu → ngày → giờ → chọn 2 ghế → Tiếp tục → Đặt vé | Có mã vé `FF…`, đúng 2 ghế, trạng thái **Giữ chỗ – chưa thanh toán**, hạn tự hủy ≤ 15 phút |
| C2 | Mở lại đúng suất đó | 2 ghế vừa đặt hiện màu xám, không bấm chọn được |
| C3 | Vào **Vé của tôi** | Thấy vé mới, cùng các vé mẫu `đã thanh toán`, `chờ xác nhận`, `hết hạn` |
| C4 | Hủy một vé đang giữ chỗ | Vé chuyển trạng thái hủy, ghế được nhả ra ở suất chiếu |
| C5 | Thử chọn ghế rời rạc, bỏ trống 1 ghế lẻ giữa hai ghế đã chọn | Hệ thống chặn hoặc cảnh báo theo luật ghế |

### D. Bình luận và chấm điểm (đăng nhập khách)
| # | Thao tác | Kết quả mong đợi |
|---|---|---|
| D1 | Gửi bình luận: `Ko hay như quảng cáo, hơi thất vọng` | Có cảnh báo; bình luận bị che, có nút **Vẫn xem** |
| D2 | Gửi bình luận tích cực: `Phim hay, diễn viên đóng rất tự nhiên` | Hiện bình thường, không bị che |
| D3 | Gửi bình luận ẩn danh | Bình luận không hiện tên người viết |
| D4 | Bấm vào điểm của phim → khung chấm điểm bật lên, chọn điểm từ 1–10 → Lưu | Điểm trung bình và số lượt cập nhật; mở lại thấy điểm mình đã chấm |
| D5 | Mở khung chấm điểm rồi bấm Hủy / phím Esc | Đóng khung, không lưu gì |
| D6 | Chấm điểm phim **sắp chiếu** | Không cho chấm (hoặc báo chưa chấm được) |

### E. Quản trị (đăng nhập admin)
| # | Thao tác | Kết quả mong đợi |
|---|---|---|
| E1 | **Tổng quan** | Có số liệu doanh thu, vé, bình luận |
| E2 | **Kiểm duyệt bình luận** → tìm bình luận ở D1 | Thấy điểm khoảng 0,99, nhãn Tiêu cực, phiên bản model |
| E3 | Bấm **Xác nhận nhãn**, rồi **Đổi sang bình thường** | Số Đã duyệt tăng; nhãn duyệt Bình thường, nhãn model vẫn Tiêu cực, số Model sai tăng. Tải lại trang phim: bình luận không còn bị che |
| E4 | **So sánh mô hình** → nhập `Phim dài lê thê, nửa đầu buồn ngủ thật sự.` → Chấm điểm | Bảng có PhoBERT A, PhoBERT B (và SVM/LR/NB), mỗi dòng có nhãn, điểm, thời gian |
| E5 | **Quản lý phim**: thêm phim mới (kèm poster), sửa, xóa | Thay đổi hiện ở trang chủ / trang chi tiết |
| E6 | **Quản lý suất chiếu**: thêm suất trùng giờ cùng phòng | Bị từ chối với thông báo tiếng Việt |
| E7 | **Quản lý vé**: lọc **Chờ xác nhận chuyển khoản**, xác nhận một vé | Vé chuyển sang đã thanh toán |
| E8 | **Soát vé**: nhập mã vé đã thanh toán | Báo hợp lệ, check-in thành công; nhập lại lần 2 báo đã soát |
| E9 | **Thống kê cảm xúc** | Có biểu đồ / số liệu bình luận theo phim |
| E10 | Đăng nhập khách rồi gõ thẳng địa chỉ trang admin (vd `/admin`) | Không vào được |

### F. Kiểm tra chung
| # | Thao tác | Kết quả mong đợi |
|---|---|---|
| F1 | Thu cửa sổ về bề ngang điện thoại (F12 → biểu tượng điện thoại, 375px) | Không bị tràn ngang, nút bấm được |
| F2 | Tải lại trang (F5) ở giữa các bước | Vẫn giữ đăng nhập, không trắng trang |
| F3 | Toàn bộ chữ trên giao diện và thông báo lỗi | Bằng tiếng Việt, không lỗi font |

## 3. Mẫu báo lỗi

```
Mã ca: (vd C4)
Tài khoản: demo / admin / tài khoản tự tạo
Các bước: 1) ... 2) ... 3) ...
Kết quả thực tế:
Kết quả mong đợi:
Ảnh chụp màn hình: (đính kèm)
Mức độ: Nghiêm trọng (chặn luồng) / Trung bình / Nhẹ (giao diện, chữ)
```

## 4. Lưu ý
- Đây là dữ liệu demo; mọi thao tác ghi vào database local. Sau buổi test, Tín chạy `reset-demo.bat` (tắt cửa sổ backend trước) để về dữ liệu gốc.
- Không có thanh toán thật; không nhập thông tin thẻ/tài khoản ngân hàng thật vào bất kỳ ô nào.
- Chatbot có thể cần Internet; nếu không trả lời thì ghi nhận, không tính là lỗi chặn.
