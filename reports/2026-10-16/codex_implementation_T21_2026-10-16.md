# Codex Implementation Report — T21

- Ngày: 16/10/2026
- Nhánh: `task/T21-thong-ke-cam-xuc`
- Baseline: `master` tại `0a717e9270721b23a4270e7e81278393bf8aa1cc`
- Trạng thái bàn giao: `CLAUDE_REVIEW`
- Đổi schema: Không

## 1. Phạm vi đã thực hiện

- Thêm `GET /api/admin/sentiment?days=30`, bảo vệ bằng `require_admin`, kiểm tra `days` trong 1–365 với lỗi tiếng Việt.
- Tổng hợp hoàn toàn ở SQL: một truy vấn aggregate cho summary, một `GROUP BY` theo phim và một `GROUP BY` theo ngày; không tải toàn bộ bình luận vào bộ nhớ.
- Nhãn hiệu lực là `human_label` khi đã duyệt, nếu chưa là `is_negative`; không lọc `hidden` nên bình luận đã ẩn vẫn được tính.
- Khoảng ngày gồm hôm nay và `days - 1` ngày trước. Mốc đầu là 00:00 ngày đầu được tính; mốc cuối là 00:00 ngày mai và không được tính, theo giờ địa phương như `created_at` đang lưu. `daily` lấp đủ đúng số ngày bằng 0.
- Thêm trang `/quan-tri/thong-ke`, 4 ô tóm tắt, thanh ngang theo phim có liên kết chi tiết, SVG tổng/tiêu cực theo ngày, bảng số liệu, chọn 7/30/90 ngày và trạng thái rỗng.
- Thêm `api.admin.sentiment(days)` cho real/mock. Mock tính trực tiếp từ bộ bình luận mock và dùng cùng nhãn hiệu lực/contract với backend.

## 2. Kiểm thử backend

- Focused: `4 passed` cho `tests/test_sentiment.py`.
- Full suite: `85 passed`, 1 cảnh báo deprecation từ Starlette; mã thoát 0.
- `compileall`: mã thoát 0.
- Các ca T21: 401 chưa đăng nhập, 403 user thường, 422 cho 0/366; tổng/số tiêu cực/tỷ lệ phim/ngày; nhãn người duyệt đảo nhãn model; bình luận ẩn; đủ 7 ngày và ngày trống bằng 0.
- Backend thật khởi động trên SQLite tạm, `/api/health` trả 200. Không khởi động hoặc ghi vào `backend/firefly.db`.

## 3. Đối chiếu dữ liệu demo T12

DB tạm được tạo bằng `backend/scripts/reset_demo.py` với `DATABASE_URL` trỏ tới thư mục TEMP và `ADMIN_PASSWORD` riêng. Seed tạo 21 phim, 99 suất, 143 vé, 30 bình luận.

Kết quả endpoint 30 ngày:

| Chỉ số | Endpoint | SQL độc lập |
|---|---:|---:|
| Tổng bình luận | 30 | 30 |
| Tiêu cực hiệu lực | 7 | 7 |
| Đã duyệt | 8 | 8 |
| Model khớp người duyệt | 75,0% | 6/8 = 75,0% |

Theo phim: Bóng Ma Hẻm 37 `2/5`, Thứ Bảy Không Ngủ `2/5`, Bản Hòa Âm Mùa Hạ `1/5`, Chuyến Tàu Cuối Mùa Mưa `1/5`, Đội Cứu Hộ Sông Hồng `1/5`, Mèo Mướp Đi Lạc `0/5`. Kết quả endpoint trùng truy vấn SQLite độc lập. `daily` có đúng 30 dòng từ 17/09/2026 đến 16/10/2026; ngày đầu trống trả `0/0`, ngày cuối `3/0`.

## 4. Frontend, responsive và accessibility

- Build real: đạt, 83 module.
- Build mock (`VITE_USE_MOCK=true`): đạt, 83 module.
- Real mode với DB demo tạm: 4 ô tóm tắt `30 / 7 / 23,3% / 75,0%`, 6 dòng phim, 30 dòng ngày; console 0 lỗi.
- Mock mode: 30 ngày `30/7`, 7 ngày `15/4`, 90 ngày `30/7`; cả summary, danh sách phim và số dòng daily cùng cập nhật; số dòng lần lượt 30/7/90.
- Mô tả 375px: một cột, tab 7/30/90 vừa khung, các ô tóm tắt xếp dọc, thanh phim không đẩy trang; `innerWidth=375`, `scrollWidth=375`.
- Mô tả 1280px: bốn ô cùng hàng, nội dung phim và biểu đồ đủ rộng; `innerWidth=1280`, `scrollWidth=1265` (phần còn lại là thanh cuộn dọc, không có tràn ngang).
- SVG có `aria-label="Biểu đồ cột tổng số và số bình luận tiêu cực theo ngày"`; bảng đi kèm có caption “Số liệu bình luận theo từng ngày”.

## 5. Checklist hồi quy 7/7

1. Đăng ký/đăng nhập/phân quyền: đạt qua full pytest và probe 401/403/admin.
2. Danh sách, tìm kiếm và chi tiết phim: đạt; frontend real/mock khởi động và route chi tiết giữ nguyên.
3. Suất chiếu và sơ đồ ghế: đạt qua full pytest.
4. Giữ chỗ, thanh toán và vé của tôi: đạt qua full pytest.
5. Bình luận công khai và kiểm duyệt admin: đạt; test T21 bổ sung xác nhận nhãn hiệu lực/ẩn.
6. Quản trị phim, suất chiếu và vé: đạt qua full pytest; menu admin không tràn ở 375px.
7. So sánh model, chatbot và lớp API real/mock: đạt; cả hai build thành công, mock T21 chạy đủ 7/30/90.

## 6. Scope và an toàn

- Chỉ sửa/tạo file trong mục 6 của T21.
- `package.json`, `requirements*.txt`, schema DB, classifier, models và router comments không đổi.
- Không có `.env`, `*.db`, `backup/`, model hoặc dữ liệu lớn trong thay đổi Git.
- DB/profile trình duyệt tạm đã xóa sau gate.
- `git diff --check`: không lỗi.

## 7. Bàn giao

T21 được chuyển từ `IN_PROGRESS` sang `CLAUDE_REVIEW`. Codex không tự review, không tự kết luận PASS và không mở task tiếp theo.
