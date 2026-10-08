# Implementation Report — T05 Quản lý suất chiếu (admin)

## 1. Thông tin bàn giao

- Task: `T05`
- Nhánh: `task/T05-quan-ly-suat-chieu`
- Git baseline: `a09fe6736d4a5d465e07dfa026b032caf9afe0be`
- Dependency T04 merge đã xác minh: `fced3d7`
- Implementation commits: `214fcaa1ebd41299bd00d69c0b3d76091655061c`, scope refinement `033e420863775489c3efe80fdb2f25a07f2c6cd5`
- Đổi schema: **Không**
- Trạng thái bàn giao: `CLAUDE_REVIEW` (chờ Claude kiểm tra độc lập; Codex không tự review/PASS)

## 2. Nội dung đã triển khai

- Thêm CRUD `GET/POST /api/admin/showtimes`, `PUT/DELETE /api/admin/showtimes/{id}`; cả bốn endpoint dùng `require_admin`.
- Thêm `ShowtimeIn`: phim phải tồn tại và chưa `ended`, giờ tương lai, phòng thuộc `Phòng 1`–`Phòng 4`, giá 10.000–500.000 đồng và là bội số 1.000.
- Thêm luật dùng chung `find_showtime_conflict()` với khoảng chiếm phòng `[start, start + duration_min + 15 phút)`.
- Chặn sửa/xóa suất có `booking_seats`, trả 409 kèm đúng tổng số vé.
- Sửa `_ensure_showtimes()` để xét từng suất, bỏ qua trùng/chồng với suất admin và không bỏ qua toàn bộ ngày chỉ vì đã có dữ liệu.
- Thêm trang `/quan-tri/suat-chieu`: danh sách, lọc ngày/phim, thêm/sửa/xóa, loading/empty/error, thông báo tiếng Việt, responsive 375px, focus và reduced motion.
- Bổ sung contract `api.admin.showtimes.{list,create,update,remove}` ở real và mock; mock có validation, chống chồng, khóa suất có vé, CRUD và localStorage persistence.
- Phim mới tạo ở T04 có thể được chọn để tạo suất; suất xuất hiện ở API/trang chi tiết và đặt vé được.

## 3. Files changed (so với master, sau commit report/coordination)

- `backend/app/main.py`
- `backend/app/routers/admin_showtimes.py` (mới)
- `backend/app/schemas.py`
- `backend/app/seed.py` (chỉ `_ensure_showtimes`; import luật chung đặt cục bộ trong hàm)
- `backend/app/showtime_rules.py` (mới)
- `frontend/src/App.jsx`
- `frontend/src/api/mock.js`
- `frontend/src/api/real.js`
- `frontend/src/components/Header.jsx`
- `frontend/src/pages/AdminShowtimes.jsx` (mới)
- `frontend/src/styles/global.css` (chỉ class T05 và responsive liên quan)
- `docs/ARCHITECTURE.md`
- `docs/TASK_COORDINATION_ACTIVE.md`
- `reports/2026-10-08/codex_implementation_T05_2026-10-08.md`

## 4. Evidence Acceptance Criteria

Các kết quả dưới đây là evidence của implementer, chờ Claude xác minh độc lập.

| AC | Kết quả kiểm tra Codex | Evidence |
|---|---|---|
| AC-01 | Đạt | Real API probe đủ GET/POST/PUT/DELETE: chưa đăng nhập `401`, user thường `403`. Mock dùng chung `requireAdmin()`; probe contract admin thành công. |
| AC-02 | Đạt | Cùng phòng, bắt đầu ở `duration + 14 phút` trả `409` đúng câu `Phòng 1 đã có suất ... lúc 10:00. Hãy chọn giờ khác hoặc phòng khác.`; đúng `duration + 15 phút` trả `201`. |
| AC-03 | Đạt | Cùng giờ, `Phòng 2` trả `201` trong real và mock. |
| AC-04 | Đạt | Đặt thật 2 ghế qua `/api/bookings`; PUT và DELETE suất đều `409`, đúng câu `Suất chiếu đã có 2 vé, không sửa hay xóa được.`; mock cho kết quả tương đương. |
| AC-05 | Đạt | Tạo suất admin trong ngày seed, gọi lại `_ensure_showtimes()` như bước startup; truy vấn luật chung xác nhận không có suất giao trong cùng phòng, ngày vẫn được lấp các khung hợp lệ. |
| AC-06 | Đạt | Phim mới tạo qua admin `201` → tạo suất `201`; `/api/movies/{id}/showtimes` có suất. Một suất admin khác được user đặt 2 ghế `201`, ghế hiện trong detail và vé có trong `/api/bookings/me`. |
| AC-07 | Đạt | Probe mock: phim mới → CRUD suất, 409 chồng giờ, mốc +15 phút, khác phòng, khóa 2 vé, chặn phim `ended`, lọc và dữ liệu tồn tại trong `firefly_mockdb_v2`. Vite mock server trả trang admin `200`. |
| AC-08 | Đạt theo evidence bên dưới | Checklist hồi quy 7 mục đã chạy; browser headless xác nhận poster intro, auth redirect, trang admin 375px, focusable controls và reduced motion. |

## 5. Focused tests

- Real API trên SQLite tạm (không chạm `firefly.db`):
  - phân quyền: `GET/POST/PUT/DELETE = (401, 403)` cho anonymous/user;
  - 5 validation case (phim không tồn tại, phim ended, giờ quá khứ, phòng sai, giá 75.500) đều `422`;
  - chồng giờ `409`; biên +15 phút `201`; khác phòng `201`;
  - booking `201`; sửa/xóa suất có 2 ghế `409` đúng số vé;
  - lọc `movie_id + date` trả đúng 3 suất;
  - create/update/delete hợp lệ lần lượt `201/200/200`; hai biên giá `10.000/500.000` được nhận.
- Mock probe qua Vite SSR:
  - chồng giờ `409`, biên `201`, khác phòng `201`, public showtimes = 3;
  - suất có 2 vé bị khóa `409`; phim ended bị chặn `422`; persistence có dữ liệu localStorage.
- Browser headless, mock mode, viewport 375×812:
  - trang chủ có 9 movie cards; poster intro hiển thị sau click;
  - chưa đăng nhập vào `/dat-ve/1` chuyển `/dang-nhap`;
  - `/quan-tri/suat-chieu` có form, hai bộ lọc, 12 dòng dữ liệu mẫu;
  - `innerWidth=375`, `documentElement.scrollWidth=360`, bảng có `overflow-x:auto`;
  - 39 điều khiển focusable; `prefers-reduced-motion: reduce` được nhận.

## 6. Final gates

| Gate | Kết quả |
|---|---|
| Backend compileall | `backend\venv\Scripts\python -m compileall -q backend\app` → exit 0 |
| Backend startup | Uvicorn `127.0.0.1:8015` trên SQLite tạm → startup complete |
| Health | `GET /api/health` → `200`, `classifier=phobert`, `classifier_error=null` |
| Frontend build | `npm run build` → 69 modules, build thành công |
| Real API probes | Đạt các probe ở mục 5 |
| Mock mode | Vite `VITE_USE_MOCK=true`, route admin `200`, API/browser probes đạt |
| Diff check | `git diff --check` không có lỗi sau khi chốt code |
| Pytest | Không bắt buộc trước T11 theo `AGENT_RULES.md`; không thêm thư viện/test ngoài allowlist |

## 7. Checklist hồi quy BOI_CANH mục 7

1. Trang chủ có 21 phim qua API; browser có 9 card ở tab mặc định; click poster hiện `PosterIntro` và chuyển trang chi tiết.
2. Tìm `meo muop` trả `Mèo Mướp Đi Lạc`; các tệp menu/taxonomy không bị sửa trong T05.
3. Đăng ký user mới `201`; browser chưa đăng nhập vào route đặt vé chuyển `/dang-nhap`. Luồng route/auth cũ không bị sửa.
4. Đặt 2 ghế `A1, A2` trả `201`; mở lại detail thấy hai ghế trong `booked_seats`; `/api/bookings/me` có vé.
5. Bình luận `Ko hay như quảng cáo, hơi thất vọng` bị phân loại tiêu cực; admin thấy `negative_score=0.9937`.
6. `/api/health`: `classifier=phobert`, không lỗi classifier.
7. `VITE_USE_MOCK=true`: mock API CRUD/booking và trang quản trị chạy được; persistence được xác minh.

## 8. Security / permission

- Tất cả endpoint admin showtimes dùng `Depends(require_admin)`.
- 4/4 endpoint đã probe 401 anonymous và 403 user thường.
- Payload Pydantic `extra="forbid"`; validation nghiệp vụ trả một câu tiếng Việt.
- Không sửa `normalize()`, `classifier.py`, `models.py`, `seats.py`, `.env` hay schema.

## 9. Scope allowlist

- Toàn bộ file thay đổi nằm đúng mục 6 `docs/tasks/T05.md`.
- Không có file ngoài allowlist.
- Diff không chứa `.env`, `*.db`, `backend/models/`, model, CSV/dữ liệu lớn hay secret.
- Các SQLite probe tạm đã được xóa sau kiểm tra; `firefly.db` thật không bị dùng hoặc sửa.

## 10. Required Fixes

- Không có Required Fix do Codex tự đặt. Chờ Claude review độc lập.

## 11. Blockers / scope conflict

- T04 TODO-07, vế 1 (phim mới chưa có suất): đã giải quyết trong T05 bằng luồng admin tạo suất; đã probe cả real và mock.
- T04 TODO-07, vế 2 (phim chuyển `ended` nhưng suất tương lai cũ vẫn có thể bị gọi trực tiếp để đặt vé): **chưa thể sửa đầy đủ trong allowlist T05**. Việc chặn ở nguồn cần sửa `backend/app/routers/bookings.py`, là file ngoài allowlist và prompt cấm tự sửa. UI chi tiết phim hiện đã ẩn lịch của phim `ended`; T05 cũng chặn tạo/cập nhật suất sang phim `ended`, nhưng endpoint booking trực tiếp vẫn là dependency/scope conflict cần PO authorize ở task khác hoặc mở rộng allowlist.

## 12. TODO

- Claude chạy review/gate độc lập.
- PO quyết định nơi xử lý chặn booking trực tiếp cho suất thuộc phim `ended` (mở rộng T05 hoặc task sau); Codex không tự sửa file ngoài allowlist.
