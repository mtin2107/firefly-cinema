# Codex Fix Report — T21 TODO-01

- Ngày: 16/10/2026
- Nhánh: `task/T21-thong-ke-cam-xuc`
- Yêu cầu: PO chọn sửa TODO-01 trước khi merge
- Đổi schema: Không
- File production sửa: `frontend/src/pages/AdminSentiment.jsx`, khối T21 trong `frontend/src/styles/global.css`

## 1. Thay đổi

- `DailyChart` dùng `ResizeObserver` để lấy bề rộng pixel thật của khung.
- Ở khung từ 600px, SVG của 7/30/90 ngày luôn bằng bề rộng khung; tâm các cặp cột phân bố đều trên toàn vùng vẽ.
- Ở khung dưới 600px, 7 và 30 ngày vừa khung; riêng 90 ngày dùng SVG tối thiểu 16px/ngày và cuộn ngang trong `.sentiment-chart-scroll`.
- Khoảng nhãn được tính từ số pixel thực tế (`labelEvery = ceil(48 / slot)`), tránh nhãn cuối va vào nhãn trước và luôn giữ ngày cuối.
- SVG hiển thị ở tỷ lệ pixel 1:1, chữ ngày `11px` thực tế.
- Giữ nguyên màu vàng/đỏ, chú thích, `role="img"`, `aria-label`, `<title>` từng ngày và bảng số liệu.
- Tùy chọn TODO-04: effect có cờ cleanup `active`; phản hồi cũ bị bỏ qua khi đổi nhanh 7/30/90. Không sửa API.

## 2. Môi trường kiểm chứng

- DB tạm: tạo bằng `backend/scripts/reset_demo.py`, `DATABASE_URL` trỏ file trong `%TEMP%`, `ADMIN_PASSWORD` riêng.
- Kết quả seed: 21 phim, 99 suất, 143 vé, 30 bình luận.
- Backend và frontend real/mock chỉ chạy với DB/profile tạm. Không khởi động backend trên `backend/firefly.db`.
- Chrome headless; đo qua `getBoundingClientRect()`, `scrollWidth`, vị trí từng nhãn và `getComputedStyle()`.

## 3. Số đo real mode

| Viewport | Khoảng | Khung / SVG | Cuộn trong khung | Nhãn | Cặp đè | Cỡ chữ | Trang tràn |
|---:|---:|---:|---|---:|---:|---:|
| 1280px | 7 ngày | 1094 / 1094px | Không | 7 | 0 | 11px | Không |
| 1280px | 30 ngày | 1094 / 1094px | Không | 15 | 0 | 11px | Không |
| 1280px | 90 ngày | 1094 / 1094px | Không | 18 | 0 | 11px | Không |
| 375px | 7 ngày | 321 / 321px | Không | 4 | 0 | 11px | Không |
| 375px | 30 ngày | 321 / 321px | Không | 5 | 0 | 11px | Không |
| 375px | 90 ngày | 321 / 1440px | Có, chỉ trong khung | 23 | 0 | 11px | Không |

`documentElement.scrollWidth`: 1265px ở viewport 1280 (trừ thanh cuộn dọc), 375px ở viewport 375. Lỗi JavaScript/console ứng dụng khi đổi 7/30/90: 0. Chrome có một network log 404 cho `/favicon.ico` có sẵn, ngoài phạm vi file được phép và không phải lỗi runtime của trang T21.

## 4. Số đo mock mode

| Viewport | Khoảng | Khung / SVG | Cuộn trong khung | Nhãn | Cặp đè | Cỡ chữ | Trang tràn |
|---:|---:|---:|---|---:|---:|---:|
| 1280px | 7 ngày | 1094 / 1094px | Không | 7 | 0 | 11px | Không |
| 1280px | 30 ngày | 1094 / 1094px | Không | 15 | 0 | 11px | Không |
| 1280px | 90 ngày | 1094 / 1094px | Không | 18 | 0 | 11px | Không |
| 375px | 7 ngày | 321 / 321px | Không | 4 | 0 | 11px | Không |
| 375px | 30 ngày | 321 / 321px | Không | 5 | 0 | 11px | Không |
| 375px | 90 ngày | 321 / 1440px | Có, chỉ trong khung | 23 | 0 | 11px | Không |

Lỗi JavaScript/console ứng dụng: 0; network log `/favicon.ico` giống real mode và không liên quan thay đổi T21.

## 5. Gate

- `npm run build` real: mã thoát 0, 83 module.
- `VITE_USE_MOCK=true; npm run build`: mã thoát 0, 83 module.
- Full pytest: 85/85, mã thoát 0; còn cảnh báo Starlette deprecation và thông báo cleanup TEMP của pytest trên Windows sau khi hoàn tất.
- `git diff --check`: đạt trước commit.
- Không thêm thư viện, không đổi schema, không sửa backend/API.

## 6. Checklist hồi quy liên quan trang admin — 7/7

1. Route admin real và mock vẫn yêu cầu tài khoản admin, trang thống kê mở được.
2. Chuyển 7/30/90 cập nhật dữ liệu và biểu đồ; phản hồi cũ không ghi đè state mới.
3. Bốn ô tóm tắt và danh sách tỷ lệ theo phim giữ nguyên.
4. Liên kết tên phim tới trang chi tiết giữ nguyên.
5. Chú thích Tổng/Tiêu cực, `role="img"`, `aria-label` và `<title>` giữ nguyên.
6. Bảng số liệu theo ngày giữ nguyên và đủ hàng theo khoảng chọn.
7. 375px/1280px không tràn trang; 12 tổ hợp real/mock đều 0 cặp nhãn đè nhau.

## 7. Bàn giao

T21 được chuyển `PO_REVIEW → CLAUDE_REVIEW` để Claude kiểm tra lại fix TODO-01 theo yêu cầu PO. Codex không tự review, không tự PASS và không mở task khác.
