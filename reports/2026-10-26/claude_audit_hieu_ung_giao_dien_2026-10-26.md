# Claude audit — hiệu ứng, cách dòng, trang tài khoản (26/10/2026)

- Phạm vi: theo phản hồi của Tín sau buổi test. Rà soát trên `master` @ `f48922a`, chạy thật (backend PhoBERT B, frontend 5173) ở 1280 và 375 px.
- Không sửa production code. Đây là audit để làm đầu vào cho FIX_LOOP hoặc task mới; PO quyết định.

## Kết quả

| ID | Mức | Vị trí | Vấn đề | Bằng chứng | Hướng sửa |
|---|---|---|---|---|---|
| UI-01 | Medium | `frontend/src/styles/global.css:205` `.poster__title`, `:235` `.detail__title` | `line-height: .95` quá chặt với chữ HOA tiếng Việt có dấu chồng (Ủ, Ầ, Ộ, Ế): dấu của dòng dưới đè lên chữ dòng trên. Thấy rõ ở poster "THỨ BẢY KHÔNG / NGỦ", "ĐỘI BÓNG XÓM / CHÀI", "CHUYẾN TÀU / CUỐI MÙA MƯA". | Đo bằng canvas với font Big Shoulders: poster cỡ 41.6px có line-height 39.5px nhưng chiều cao chữ kèm dấu là 47px; tiêu đề chi tiết cỡ 64px có line-height 60.8px nhưng cao 71px. | Tăng `line-height` lên khoảng 1.12–1.15 cho hai class này (và `.poster--lg`, `.intro__bubble`, `.trailer__banner` kế thừa). Kiểm tra lại không làm tràn khung poster. |
| UI-02 | Medium | `.movie-card__body` (`global.css:219-223`) | Thẻ phim cùng hàng lệch nhau: tên dài xuống 2 dòng thì thời lượng, điểm và nút **Đặt vé** bị đẩy xuống, không thẳng hàng với thẻ bên cạnh. | Ở 375px, hàng 2: nút "Đặt vé" của "Bóng Ma Hẻm 37" ở y=408, của "Ga Cuối Tàu Điện Ngầm" ở y=427. Ảnh PO gửi 26/10: hàng trộn phim sắp chiếu và đang chiếu thì dòng điểm, thể loại, "Khởi chiếu" và nút Đặt vé đều lệch, thể loại dài cũng xuống 2 dòng (`anh_audit/UI-02_the_phim_lech_hang_hang3_PO.png`). | Cho thẻ là cột flex cao bằng nhau, `.movie-card__body { flex: 1 }`, nút `margin-top: auto`; hoặc giới hạn tên 2 dòng (`-webkit-line-clamp: 2`) kèm `min-height` 2 dòng. |
| UI-03 | Medium | `.logo` (`global.css:89`), header | Ở 1280px, logo "FIREFLY CINEMA" bị xuống 2 dòng (cao 87px) vì menu chiếm hết chỗ. Lúc chưa đăng nhập, nút "Đăng nhập" và "Đăng ký" cũng bị xuống dòng. | Đo `.logo` ở 1280px: cao 87px, cỡ chữ 27.2px. Có ảnh chụp header lúc chưa đăng nhập. | `white-space: nowrap` cho `.logo` và các nút header; thu gọn menu (gap, cỡ chữ) hoặc chuyển sang nút Menu sớm hơn (breakpoint khoảng 1360px). |
| UI-04 | Medium | `movies.json` (backend + frontend), `MovieCard.jsx:59` | Phim `coming_soon` nhưng ngày khởi chiếu đã qua: "Nửa Vầng Trăng Hà Tiên" hiện "Khởi chiếu 24/10/2026" vào ngày 26/10. "Võ Sĩ Đường Phố Bangkok" (30/10) sẽ bị như vậy trước ngày bảo vệ. Cả 4 phim sắp chiếu đều chưa có suất chiếu. | Truy vấn DB thật: id 6 `2026-10-24`, id 11 `2026-10-30`, id 7 `2026-11-07`, id 19 `2026-12-18`, cả 4 đều 0 suất. Ảnh PO gửi 26/10. | Nguyên nhân gốc: `status` cố định, không theo ngày. Sửa bằng quy tắc chung (trạng thái hiệu lực theo `release_date`, dùng cho mọi API/bộ lọc/mock, chặn form admin), không vá ngày từng phim (PO chốt 26/10). |
| FX-01 | Medium | `frontend/src/components/StarRating.jsx:28` | Hiệu ứng phóng to sao khi rê chuột bị kẹt: rê nhanh qua rồi ra khỏi một sao thì sao đó vẫn to 1.2 lần. `gsap.set(..., {scale:1})` không dừng tween `gsap.to(scale:1.2)` đang chạy, nên tween chạy tiếp và kết thúc ở 1.2. | Probe JS: mouseover, 40ms sau mouseout, chờ 400ms → `transform: matrix(1.2,0,0,1.2,0,0)`. | Lúc rời chuột dùng `gsap.to(el, { scale: 1, duration: .15, overwrite: true })` (hoặc `gsap.killTweensOf(el)` trước `set`). |
| FX-02 | Low | `global.css:814-815` `.star-rating__button` | 10 ô sao hẹp (28×45px), khoảng cách 2px; nhìn chật và khó bấm trên điện thoại (dưới 44px). | Đo kích thước nút: 28×45. | Bỏ viền từng ô, tăng cỡ sao, rộng tối thiểu khoảng 32–36px; ở màn hình hẹp cho xuống 2 hàng × 5 sao. |
| FX-03 | Low | Banner trailer, trang chi tiết phim | Phim không có trailer vẫn hiện khối lớn khoảng 360px chỉ có nền xanh và tên phim mờ. Nhìn như lỗi tải video. | Ảnh chụp `/phim/1` ở 1280px. | Không có trailer thì thu nhỏ banner hoặc dùng poster làm nền, kèm chữ rõ hơn. |
| FX-04 | Low | Hero băng chuyền 3D | Poster hai bên bị cắt, chỉ còn mảnh chữ ("Đ S", "GA Đ") nên nhìn như vỡ chữ. | Ảnh chụp trang chủ ở 1280 và 375px. | Ẩn tên trên poster phụ (chỉ để màu/ảnh), hoặc làm mờ chúng. |

Các mục đã kiểm tra và đạt: dialog chấm điểm mở có hiệu ứng trượt; vòng điểm đếm từ 0 lên 8.0; thanh phân bố chạy; chọn 7 điểm thì sao sáng có stagger và đốm sáng, nhãn "7 điểm · Hay"; Esc đóng không lưu. Chữ hero bật sáng hết sau khoảng 1 giây (ảnh chụp sớm hơn bị mờ là do chụp giữa hiệu ứng). Không có tràn ngang ở 375px.

Chưa kiểm tra: các trang admin, sơ đồ ghế, trang vé, hiệu ứng poster intro khi bấm "Xem chi tiết"; hover sao trên chuột thật (chỉ probe bằng sự kiện JS).

## Trang tài khoản (yêu cầu mới, không phải lỗi)

Hiện chỉ có email, ô họ tên và form đổi mật khẩu. Bảng `users` chỉ có `full_name, email, role, created_at`.

Đề xuất chia 2 mức để PO chọn:

**Mức A — không đổi schema** (chỉ dùng dữ liệu đã có, thêm 1 endpoint thống kê, phải có ở cả `real.js` và `mock.js`):
- Thẻ hồ sơ: chữ cái đầu làm avatar, họ tên, email, vai trò, ngày tham gia (`created_at`).
- Thống kê: số vé đã đặt, số vé đã xem (đã soát), tổng chi tiêu, số bình luận, số phim đã chấm điểm.
- Hoạt động gần đây: 3 vé gần nhất, 3 bình luận gần nhất (kèm trạng thái ẩn/hiện), các phim đã chấm điểm kèm số điểm.
- Thể loại xem nhiều nhất (tính từ vé đã đặt).

**Mức B — đổi schema** (phải xóa `backend/firefly.db`): thêm số điện thoại, ngày sinh, giới tính, ảnh đại diện. Rủi ro cao hơn so với hạn 01/11.

Khuyến nghị: Mức A.

## Quy trình đề xuất

Lộ trình hiện tại chỉ còn T13. UI-01..03 và FX-01..04 là sửa lỗi giao diện nhỏ, có thể gộp vào một task sửa lỗi trước T13. Phần tài khoản Mức A là tính năng mới nên cần PO quyết định có mở task hay không.
