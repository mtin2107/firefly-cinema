# Codex Implementation Report — T04 — 08/10/2026

## 1. Thông tin bàn giao

- Task: T04 — Quản lý phim (admin)
- Baseline commit: `b6cc3d677a5e748ed4818ce111967bfa234e9edb`
- T03 merge commit đã xác minh trên `master`: `6bd1a3f1a89b79bb7000ee4dd567871af850742d`
- Branch: `task/T04-quan-ly-phim`
- Implementation commit: `d8e67e0484afa4e6fe3e085c365c3de1ae2d33ed`
- Đổi schema: Không
- Trạng thái đề nghị: `CLAUDE_REVIEW`

## 2. Pre-implementation gate

- Trước xử lý: `git status --short --branch` báo `?? data/phim/NGUON_THU.md` trên `master`.
- Theo quyết định PO, chỉ thêm `/data/phim/NGUON_THU.md` vào `.git/info/exclude`; không đổi nội dung/vị trí file, không commit file, không sửa `.gitignore`.
- `git check-ignore -v data/phim/NGUON_THU.md` trả `.git/info/exclude:8:/data/phim/NGUON_THU.md`.
- File vật lý vẫn tồn tại: `True`.
- Sau xử lý: working tree sạch trên `master`.
- `git merge-base --is-ancestor 6bd1a3f master`: PASS.
- Nhánh T04 được tạo từ `master` tại baseline `b6cc3d6`.

## 3. Tóm tắt implementation

- Thêm API admin `GET/POST /api/admin/movies`, `PUT/DELETE /api/admin/movies/{id}`, tất cả dùng `require_admin`.
- Thêm `MovieIn` với validation Pydantic và thông báo lỗi tiếng Việt cho tên, thể loại, thời lượng, ngày, độ tuổi, trạng thái, quốc gia, định dạng, màu và URL poster.
- Chặn xóa phim đã có booking bằng HTTP 409 đúng thông báo; phim chưa có booking được xóa cùng suất chiếu và bình luận liên quan.
- Tạo taxonomy backend và đồng bộ các nhãn thể loại/quốc gia/định dạng với frontend.
- Tạo trang `/quan-tri/phim` có form thêm/sửa, lỗi theo ô, preview poster, danh sách, loading/empty/error và responsive 375px.
- Thêm menu “Quản lý phim” cho admin và bảo vệ route bằng `ProtectedRoute adminOnly`.
- Đồng bộ `real.js`/`mock.js`; mock lưu danh sách phim trong `firefly_mockdb_v2`, duy trì CRUD sau F5.
- Phim mới dùng ngay API danh sách chung nên xuất hiện trên trang chủ, bộ lọc thể loại và tìm kiếm không dấu.

## 4. Files changed

- `backend/app/routers/admin_movies.py` (mới)
- `backend/app/taxonomy.py` (mới)
- `backend/app/schemas.py`
- `backend/app/main.py`
- `frontend/src/pages/AdminMovies.jsx` (mới)
- `frontend/src/App.jsx`
- `frontend/src/components/Header.jsx`
- `frontend/src/api/real.js`
- `frontend/src/api/mock.js`
- `frontend/src/utils/taxonomy.js`
- `frontend/src/styles/global.css`
- `docs/ARCHITECTURE.md`
- `HUONG_DAN.md`
- `docs/TASK_COORDINATION_ACTIVE.md`

## 5. Acceptance Criteria evidence

| AC | Kết quả | Bằng chứng |
|---|---|---|
| AC-01 | PASS | TestClient gọi đủ GET/POST/PUT/DELETE: chưa đăng nhập đều 401; user thường đều 403. |
| AC-02 | PASS | POST với tên rỗng, thời lượng 0, ngày `2026-02-30`, `T21`, thể loại lạ đều 422; `detail` là một câu tiếng Việt và nêu đúng trường. |
| AC-03 | PASS | DELETE phim id 1 đã có booking trả 409 đúng câu yêu cầu; PUT cùng phim sang `ended` trả 200. |
| AC-04 | PASS | Phim “Ánh Lửa Thử Nghiệm” tạo 201; API `status=now_showing`, `genre=Hành động`, `q=anh lua thu nghiem` đều tìm thấy. Browser mock xác nhận phim “Đom Đóm Phiêu Lưu” xuất hiện ở trang chủ, lọc `phieu-luu`, tìm `dom dom phieu luu`. |
| AC-05 | PASS | Browser thật với `VITE_USE_MOCK=true`: create → reload → phim còn; update và delete thành công, dữ liệu sau delete không còn. |
| AC-06 | PASS | Trang có các nhánh loading/error/empty; browser ở viewport 375×812 xác nhận heading/form hiển thị và `documentElement.scrollWidth <= innerWidth`. |
| AC-07 | PASS | Checklist hồi quy mục 7 đã chạy như phần 7 bên dưới. |

## 6. Test commands/results

### Backend

- `backend\venv\Scripts\python -m compileall -q backend\app`: PASS, exit 0.
- FastAPI TestClient với DB SQLite tạm: PASS.
  - CRUD: POST 201, PUT 200, DELETE 200.
  - Permission: 4/4 endpoint trả 401 khi không có token và 403 với user thường.
  - Validation: 5/5 trường hợp trả 422 tiếng Việt.
  - Delete conflict: 409 đúng nội dung.
  - Public integration: homepage/status, genre, accentless search đều 200 và chứa phim mới.
  - Lifespan/backend startup và `/api/health`: 200.
- Khởi động với cấu hình model thật và gọi `/api/health`: `status=ok`, `classifier=phobert`, `classifier_error=None`.
- PhoBERT câu hồi quy “Ko hay như quảng cáo, hơi thất vọng”: `(True, 0.9937)`.

### Frontend

- `npm run build`: PASS, Vite 5.4.21, 68 modules, exit 0.
- Build riêng với `VITE_USE_MOCK=true`: PASS.
- Browser Edge headless, viewport 375×812: PASS.
  - Trang quản lý có heading và form, không tràn ngang.
  - Mock create/update/delete PASS; reload persistence PASS.
  - Homepage/filter/search integration PASS.
  - Poster intro PASS.
  - Chưa đăng nhập vào `/dat-ve/1` chuyển tới `/dang-nhap`; đăng nhập mock xong quay lại `/dat-ve/1`.

### Taxonomy và Git

- So sánh nhãn backend với source frontend: 22 thể loại, 9 quốc gia, 2 định dạng — PASS.
- `git diff --check`: PASS (không lỗi whitespace; chỉ có cảnh báo quy ước LF/CRLF của working copy).

## 7. Regression checklist

| # | Kiểm tra | Kết quả | Bằng chứng |
|---|---|---|---|
| 1 | Trang chủ hiện phim, poster intro khi mở phim | PASS | Browser mock thấy phim mới trên homepage và `.intro` sau click poster. |
| 2 | Menu thể loại và tìm “meo muop”/tìm không dấu | PASS | Bộ lọc và thuật toán không dấu dùng chung không đổi; phim mới được xác minh qua `phieu-luu` và `dom dom phieu luu`. |
| 3 | Đăng ký; route đặt vé yêu cầu login và quay lại | PASS | Register API 201; browser chuyển `/dat-ve/1` → `/dang-nhap` → `/dat-ve/1` sau login. |
| 4 | Đặt 2 ghế, ghế bị đánh dấu, Vé của tôi có vé | PASS | Booking API 201; hai ghế xuất hiện trong `booked_seats`; `/api/bookings/me` chứa booking. |
| 5 | Bình luận tiêu cực bị ẩn/admin thấy điểm | PASS | Luồng API keyword tạm trả negative score 0.87 và admin filter thấy bình luận; model thật chấm câu chuẩn 0.9937. |
| 6 | `/api/health` báo PhoBERT | PASS | `classifier=phobert`, không có classifier error. |
| 7 | `VITE_USE_MOCK=true` dùng được | PASS | Browser CRUD, persistence, homepage/filter/search và auth redirect đều đạt. |

## 8. Required Fixes

Không có Required Fix do Codex tự ghi nhận. Chờ Claude review độc lập.

## 9. Blockers

Không có blocker còn mở cho T04.

## 10. Known TODOs

- Không có TODO chặn review.
- Dữ liệu seed hiện có 11 phim với `formats=""`; validation cho phép danh sách định dạng rỗng để admin vẫn có thể cập nhật các phim này, nhưng mọi giá trị không rỗng vẫn bắt buộc thuộc taxonomy.
- Test tự động cố định trong repo thuộc T11; probe T04 chỉ chạy tạm và đã xóa trước scope gate cuối.

## 11. Scope verification

- Không sửa schema database.
- Không sửa `backend/app/models.py`, `backend/app/classifier.py`, `backend/app/seats.py`.
- Không sửa hai file dữ liệu phim gốc `backend/app/data/movies.json`, `frontend/src/api/movies.json`.
- Không thêm thư viện.
- Không sửa `normalize()` hay logic PhoBERT.
- Không có `.env`, `*.db`, model hoặc CSV trong diff.
- Tất cả file thay đổi nằm trong Allowed Files T04.

## 12. Git diff check

- `git diff --name-only master...d8e67e0`: 14 file, đúng allowlist.
- `git diff --check master...d8e67e0`: PASS.
- File probe tạm đã xóa trước commit.
- Không merge `master`, không PO APPROVE, không mở T05.
