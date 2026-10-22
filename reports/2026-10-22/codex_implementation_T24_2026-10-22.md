# Codex Implementation Report — T24

- Date: 2026-10-22
- Result: IMPLEMENTATION_COMPLETED — bằng chứng DEV, chờ Claude review độc lập.
- Branch: `task/T24-sua-loi-ra-soat`; baseline `59dcaee` (master).
- Đổi schema: Không. Không thêm thư viện; không sửa `.env`, DB thật, booking_rules, models, seats hoặc classifier.

## Files Changed / Implemented

- Backend: `routers/movies.py`, `routers/bookings.py`, `schemas.py`; thêm `tests/test_t24_cutoff.py`.
- Frontend: mock, SeatSelection, MovieDetail, AdminDashboard, MyTickets, TicketStub, ProtectedRoute; global.css chỉ thêm hai class cho fieldset.
- Docs: ARCHITECTURE bổ sung contract; TASK_COORDINATION_ACTIVE ghi chuyển trạng thái; report này.
- Lịch chiếu lọc strict `start_time > now + HOLD_CUTOFF_MINUTES`, import hằng số hiện hữu. Chi tiết suất bổ sung `bookable`, không đổi bảng DB.
- SeatSelection dùng fieldset disabled để khóa cả bàn phím và chuột; khóa Tiếp tục, chặn handler, phân biệt thông báo đã bắt đầu/sắp bắt đầu và có link lịch chiếu.
- Booking phân biệt suất đã bắt đầu trước khi kiểm tra cutoff. Mock đồng bộ điều kiện và câu lỗi; movie không tồn tại cũng trả 404 khi lấy lịch.
- Dashboard dùng lại `tabs`, `tab`, `sentiment-summary`; chỉ sort bản sao theo doanh thu giảm dần rồi tên tiếng Việt, giữ các phép tính/số liệu API.
- ProtectedRoute cập nhật title bằng effect khi chặn. Hai trang chi tiết giữ ApiError.status để bỏ retry riêng cho 404.
- Vé nhóm theo thời gian suất và trạng thái expired/rejected; vé paid đã qua hiện “Đã chiếu”. Không đổi API vé.

## Bằng chứng AC

| AC | Kết quả DEV / bằng chứng |
|---|---|
| AC-01 | Pytest cố định đồng hồ: -1/0/29/30 phút không xuất hiện; 31 phút xuất hiện. API real và mock probe cùng kết quả `[false,false,false,true]` cho -1/29/30/31. |
| AC-02 | Chrome headless, real + mock, 375/1280: mỗi suất bị khóa có 96 nút ghế không thể thao tác, Tiếp tục disabled, link “Về lịch chiếu”; suất 31 phút chọn ghế và bật Tiếp tục được. |
| AC-03 | Pytest + API probe real/mock: suất quá giờ và đúng giờ trả 400 “Suất chiếu đã bắt đầu, không thể đặt vé.”; 29/30 phút trả câu mua tại quầy; 31 phút tạo booking 201. |
| AC-04 | Real/mock, hai kích thước: tab 7/30/90 chuyển dữ liệu, đủ 6 thẻ dùng class cảm xúc; từng dòng bảng được kiểm doanh thu giảm dần và tên khi bằng nhau. Backend dashboard không sửa; các test dashboard SQL hiện hữu đạt. |
| AC-05 | User thường mở `/quan-tri/tong-quan`, cả real/mock: title đúng “Không có quyền truy cập – Firefly Cinema”. |
| AC-06 | `/phim/9999`, `/dat-ve/999999` real/mock: không có Thử lại, có Về trang chủ. Chặn mạng và giả lập HTTP 500 cho cả trang phim/suất real: có Thử lại; bỏ lỗi, bấm retry tải thành công. |
| AC-07 | Fixture paid quá giờ và paid tương lai: cả real/mock thấy hai nhóm “Sắp xem”/“Đã qua”, vé paid quá giờ có “Đã chiếu”; source kiểm trạng thái expired/rejected luôn vào Đã qua, kể cả suất tương lai. |
| AC-08 | Full pytest 148/148; real/mock build thành công. Browser kiểm các trang bị ảnh hưởng ở 375/1280; `scrollWidth <= innerWidth`; đã xem ảnh dashboard desktop/mobile. Bảng rộng dùng vùng cuộn hiện hữu. |

## Focused Tests / Final Gates

Chạy từ root trừ pytest chạy trong backend:

```powershell
backend\venv\Scripts\python -m compileall -q backend\app
Set-Location backend
venv\Scripts\python -m pytest -q
Set-Location ..\frontend
$env:VITE_USE_MOCK='false'; npm run build
$env:VITE_USE_MOCK='true'; npm run build
```

- Compileall: exit 0.
- Pytest: **148 passed**, 97,76 giây; gồm 142 test cũ + 6 case mới. Một DeprecationWarning từ Starlette/AnyIO có sẵn.
- Build real + mock: exit 0, 89 modules mỗi mode.
- Backend uvicorn thật tại 8018; real Vite 5179, mock Vite 5178. Tất cả biến cấu hình đặt trong process, không sửa `.env`.
- Runtime SQLite duy nhất: `%TEMP%\firefly-t24-71964c13-6ae2-4972-bc58-5f2a3f4c5155.db`; seed và fixture đều ở DB này. `integrity_check=ok`, `foreign_key_check=0`.
- Health ban đầu kiểm fallback keyword; kiểm bổ sung với model thật: `status=ok`, `classifier=phobert_b`, version `phobert-B-2026-10-09`, active loaded, không fallback.
- Browser dùng Playwright có sẵn trong runtime + Chrome đã cài; không thêm dependency project. Probe tạm được xóa trước commit.
- Scope/security: chỉ file thuộc mục 6 T24; không có `.env`, `.db`, model hoặc dữ liệu lớn trong diff; `git diff --check` sạch.
- Lần chạy pytest đầu từ root sai import path (`No module named app`); chạy lại đúng cwd backend đạt kết quả trên. Probe đầu có lỗi fixture token/storage và giả định response admin là array; đã sửa probe, không đổi production ngoài scope.

## Checklist hồi quy

1. Trang chủ có phim; ảnh dashboard 375/1280 được xem trực tiếp. Hero/PosterIntro giữ nguyên code.
2. Search UI “meo muop” ra phim; menu Thể loại/Chủ đề mở và link điều hướng đúng, real/mock. Probe hover/click ban đầu timeout; kiểm link bằng DOM click, không coi là bằng chứng thao tác chuột đầy đủ cho menu.
3. Đăng ký qua API thành công; browser khách chọn suất → đăng nhập → quay lại đúng suất, real/mock.
4. Browser đặt hai ghế → xác nhận → Vé của tôi có giữ chỗ mới; mở lại hai ghế disabled, real/mock.
5. Bình luận mẫu bị ẩn trên real/mock; kiểm bổ sung PhoBERT B thật: negative_score=0,9992, is_negative=true; admin thấy đúng bình luận mới.
6. Health model thật đạt như trên; tên model hiện tại là phobert_b theo quyết định T10 (checklist cũ ghi phobert).
7. Mock mode đạt các luồng bị ảnh hưởng và hồi quy đặt vé nêu trên.

## Handoff

- Blockers: 0. Required follow-up: Claude review độc lập AC-01..AC-08.
- T24 → CLAUDE_REVIEW. Không tự PASS, không chuyển PO_REVIEW, không merge/tag hoặc mở T13.
- A-02/A-03 và các TODO đã chốt giữ nguyên, PO xử lý riêng.
