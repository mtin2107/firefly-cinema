# Claude — Full System Audit trước T13 (v1.0)

- Ngày: 27/10/2026, 13:40–14:25 (+07:00)
- Người thực hiện: Claude (Independent QA Auditor), theo yêu cầu PO trong chat
- Loại: READ-ONLY audit. Không sửa production code, không commit, không đổi trạng thái task, không mở T13.
- Kết luận chung: **FAIL** (1 lỗi P1, 3 lỗi P2, 2 lỗi P3, 1 blocker baseline).
- A. Thống kê cảm xúc T21: **DYNAMIC_VERIFIED**
- B. Tổng quan quản trị T23: **DATA_ACCURACY_VERIFIED**

---

## 1. Audit Baseline

| Mục | Giá trị |
|---|---|
| Branch | `master` |
| Commit | `73eb3c737fe304f7ec1e58ca1f925010de24f5fe` — `[T29] Claude review round 3 PASS, TODO-03 CLOSED` |
| origin/master | trùng `73eb3c7` |
| T29 merge | **ĐÃ MERGE**. `git reflog master`: `merge task/T29-tai-khoan: Fast-forward` lúc 13:31:59 27/10. `task/T29-tai-khoan` = master. |
| Working tree | sạch trước và sau audit (`git status --short` rỗng) |
| Coordination | Mục 4/5 vẫn ghi T29 `PO_REVIEW`, "chờ PO merge và reset DB" → **lệch trạng thái**: T29 đã merge nhưng file điều phối chưa cập nhật. Mục "Current Next Step" nhắc T27 là thông tin cũ (đúng như PO lưu ý). Claude không sửa file điều phối. |
| DB thật `backend/firefly.db` | **chưa reset sau T29**. Đọc chế độ `mode=ro`: bảng `users` chỉ có `id, full_name, email, password_hash, role, created_at` — thiếu `birth_date, gender, avatar_url`. `integrity_check = ok`. → **BASE-01** (mục 8). |
| Môi trường kiểm thử | Python 3.13 venv, Node 24, Windows. Backend uvicorn cổng 8010 trên **SQLite tạm** (scratchpad) + **UPLOAD_DIR tạm**, SECRET_KEY/ADMIN_PASSWORD test, `CHAT_API_KEY=""`, BANK_* là giá trị test giả (`TESTBANK`). PhoBERT B thật (`phobert-B-2026-10-09`) nạp chỉ đọc. Frontend REAL Vite 5180 → 8010; MOCK Vite 5174. Probe đồng hồ kiểm soát: app in-process trên SQLite tạm, model vắng (keyword). |
| Bảo toàn production | SHA-256 trước/sau trùng: `firefly.db` `b9a80817…b15270`, sidecar `6a7b97cf…338e14`; `backend/uploads/` không có file, trước/sau như nhau. Không đọc/ghi `.env` (chỉ liệt kê tên khóa). |

## 2. System Coverage

| Hạng mục | Số lượng |
|---|---|
| Route frontend | 17 (5 công khai, 4 khách, 8 admin) + 404 |
| Trang | 18 · Component | 20 |
| Endpoint API | 46 (17 cần đăng nhập, 23 admin, 6 công khai) + `/uploads` tĩnh |
| Bảng DB | 7 (`users, movies, ratings, showtimes, bookings, booking_seats, comments`) |
| Ca kiểm thử HTTP thực thi (REAL, DB tạm) | 125 (120 PASS, 5 FAIL) |
| Ca đồng hồ kiểm soát | 9 (9 PASS) |
| Luồng trình duyệt REAL | 14 luồng · MOCK 3 luồng |
| pytest | 241/241 |

Phần không chạy được bằng trình duyệt được đánh dấu `API_ONLY` hoặc `SOURCE_REVIEW_ONLY` ở mục 3 và mục 10.

### 2.1 Function Inventory (rút gọn theo module)

| ID | Module | Trang / Control | Vai trò | API | Nguồn dữ liệu | Kỳ vọng | Test ID |
|---|---|---|---|---|---|---|---|
| F01 | Auth | Đăng nhập (form, Enter, sai mật khẩu, khóa 5 lần) | Khách | POST /auth/login | users | token; 401/429 tiếng Việt | E2E-01, pytest |
| F02 | Auth | Đăng ký | Khách | POST /auth/register | users | 201, email trùng 400 | probe setup (14 tài khoản) |
| F03 | Auth | Đăng xuất (menu) | Tất cả | — | localStorage | xóa token, route bảo vệ chuyển /dang-nhap | E2E-03 |
| F04 | Header | Menu tài khoản (mở/Esc/focus), nút Menu, tìm kiếm | Tất cả | — | — | Esc đóng, focus về nút | E2E-02 |
| F05 | Home/Explore | Lọc trạng thái/thể loại/quốc gia/năm/độ tuổi/định dạng/bộ sưu tập/tìm không dấu | Khách | GET /movies | movies, ratings, bookings, comments | đúng tập phim, 422 khi tham số sai | FLT-01..17, BUG-04 |
| F06 | MovieDetail | Thông tin, lịch chiếu theo ngày, trailer, nội dung | Khách | GET /movies/{id}, /showtimes | movies, showtimes | | E2E-04 (một phần) |
| F07 | Rating | Nút điểm → dialog, chọn điểm, phím, Esc, Lưu, refresh | Đăng nhập | GET my-rating, PUT/DELETE rating | ratings | 1–10, không đếm trùng | E2E-06, R27-* |
| F08 | Comment | Form: sao, ẩn danh, nội dung, Gửi, Xóa của mình | Đăng nhập | POST/DELETE comments | comments, ratings | PhoBERT gán nhãn, ẩn danh | E2E-04, S21-* |
| F09 | Booking | Sơ đồ ghế, thường/VIP, tổng tiền, Tiếp tục, Chọn lại, Đặt vé (double-click) | Khách | GET /showtimes/{id}, POST /bookings | showtimes, booking_seats | giữ chỗ, chống trùng | E2E-05, B-* |
| F10 | MyTickets | Đếm ngược, QR, "Tôi đã chuyển khoản", Hủy vé, Lật vé, refresh | Khách | GET /bookings/me, POST claim, DELETE | bookings | | E2E-05, BUG-01/02 |
| F11 | Account (khách) | Hồ sơ, ngày sinh, giới tính, email, mật khẩu, ảnh đại diện, 4 thẻ, hạng | Khách | /auth/me*, avatar, summary | users, bookings | | ACC-*, AV-* (API) |
| F12 | Account (admin) | Việc cần làm, công việc, hoạt động gần đây | Admin | GET /admin/me/summary | comments, bookings | khớp SQL | ADM-*, E2E-11 |
| F13 | Tuổi | Chặn đặt vé theo tuổi ngày suất chiếu | Khách | POST /bookings | users.birth_date | 400 tiếng Việt | AGE-* |
| F14 | Admin Tổng quan | Tab 7/30/90, 6 thẻ, biểu đồ, bảng theo phim | Admin | GET /admin/dashboard | bookings, seats, showtimes, ratings, comments | khớp SQL, cập nhật | D23-*, E2E-08/10 |
| F15 | Admin Thống kê | Tab 7/30/90, 4 thẻ, theo phim, biểu đồ + bảng ngày | Admin | GET /admin/sentiment | comments | khớp SQL, stale-safe | S21-*, E2E-07 |
| F16 | Admin Soát vé | Ô mã, Tra cứu, Xác nhận vào rạp | Admin | GET/POST /admin/checkin/{code} | bookings | 404/409/200 | CK-*, E2E-10 |
| F17 | Admin Vé | Lọc trạng thái/mã, Đã nhận tiền (confirm), Từ chối | Admin | /admin/bookings* | bookings | | E2E-09, D23-04/05 |
| F18 | Admin Phim | Thêm/sửa/xóa, poster, trailer, trạng thái | Admin | /admin/movies*, posters, trailers | movies | | D23-07, BUG-01 (API) |
| F19 | Admin Suất chiếu | Thêm/sửa/xóa, chồng giờ, buffer 15', quá khứ, có vé | Admin | /admin/showtimes* | showtimes | | ST-01..05, D23-06 (API) |
| F20 | Admin Bình luận | Lọc, phân trang, duyệt/đổi nhãn/ẩn/hiện, thống kê, CSV | Admin | /admin/comments* | comments | | S21-03/04, MOD-*, CSV-01 (API) |
| F21 | So sánh mô hình | Nhập câu, kết quả nhiều model | Admin | POST /admin/predict | models | nhãn, điểm, ms, version | ML-01 (API) |
| F22 | Chatbot | Mở/đóng, kéo, gửi | Khách | POST /chat | Gemini | 503 khi chưa bật, admin 403 | CHAT-01; Gemini thật BLOCKED |
| F23 | Health | — | — | GET /api/health | classifier | phobert_b active | BL-health |

## 3. Functional Test Matrix (chọn lọc; danh sách đầy đủ trong `probe_http_results.json` của scratchpad)

| ID | Module | Function | Expected | Actual | Evidence | Status |
|---|---|---|---|---|---|---|
| ML-01 | ML | Đo trước 2 câu thử | có nhãn từng model | NEG: phobert_b `tieu_cuc` 0.9992; NOR: phobert_b `binh_thuong`; đủ phobert/phobert_b/svm/lr/nb/keyword | probe | PASS |
| R27-VAL ×6 | Rating | stars 0, 11, 5.5, "5", null, true | 422 tiếng Việt | 422 "Điểm phải từ 1 đến 10." | probe | PASS |
| R27-02 | Rating | Chấm 10 rồi chấm lại 1 | count giữ 1, avg = SQL, 10 khóa distribution | đúng | probe | PASS |
| R27-01 | Rating | Bình luận lần 2 kèm sao khác | cập nhật, không thêm dòng | ratings giữ nguyên, stars 9→7 | probe | PASS |
| R27-04 | Rating | Chấm phim sắp chiếu | 400 | 400 | probe | PASS |
| BUG-TOPRATED | Explore | "Đánh giá cao" trên thang 10 | phim ~5/10 không lọt | phim 6.43/10 và 5.06/10 nằm trong `top_rated` | probe | **FAIL → BUG-04** |
| B-VAL ×4 | Booking | 9 ghế, ghế Z9, rỗng, ghế đã có người | 400/400/400/409 | đúng, tiếng Việt | probe | PASS |
| B-RACE-SEAT | Booking | 4 người cùng 1 ghế đồng thời | đúng 1 thành công | `[201,409,409,409]`, DB 1 dòng | probe | PASS |
| B-RACE-HOLD | Booking | 1 người, 4 suất khác nhau, đồng thời | tối đa 2 vé giữ | `[201,201,201,201]`, 4 vé held | probe | **FAIL → BUG-03** |
| BUG-CODE-REUSE | Booking | Hủy vé giữ rồi người khác đặt | mã mới khác | người 16 hủy FF00147, người 17 nhận lại FF00147 | probe | **FAIL → BUG-02** |
| B-QR | QR | QR của vé giữ | amount + addInfo = mã vé | `amount=305000&addInfo=FF00144` | probe | PASS |
| ST-01..05 | Suất chiếu | chồng giờ / đúng biên +15' / trong buffer 1' / quá khứ / có vé | 409/201/409/422/409 | đúng | probe | PASS |
| CK-01..03 | Soát vé | paid → 200; lặp 409; FF99999/XYZ/mã 30 số 404; rejected/expired 409; user 403 | đúng | đúng, câu tiếng Việt kèm giờ soát | probe | PASS |
| AGE-T18 | Tuổi | thiếu 1 ngày → 400; đúng sinh nhật ngày suất → 201 | đúng | `[400, 201]` | probe | PASS |
| ACC-01..05 | Tài khoản | tên 1 ký tự/ngày tương lai/1899/giới tính lạ → 422; gửi `role:"admin"` bị bỏ qua; đổi email (trùng/sai mật khẩu/chữ hoa); đổi mật khẩu | đúng | đúng, không lộ `password_hash` | probe | PASS |
| AV-01..05 | Ảnh đại diện | tải 2 lần xóa file cũ; base64 sai/không phải ảnh 422; chunked > 3 MiB không Content-Length 413; chunked hợp lệ 200; xóa ảnh | đúng | đúng | probe | PASS |
| AV-02 (ảnh hỏng) | Ảnh đại diện | PNG cắt cụt 30 byte | 422 | **200**, file được lưu | probe | **FAIL → BUG-05** |
| BUG-ORPHAN | Phim/Vé | Xóa phim chỉ có vé rejected/expired | các trang vé vẫn tải | `/bookings/me` 500, `/admin/bookings` 500, `/admin/checkin/{code}` 500 | probe + E2E-09 | **FAIL → BUG-01** |
| D23-07 | Phim | Thêm phim | 201, có trong tổng quan với 0 | đúng | probe | PASS |
| SEARCH/FLT | Explore | 17 tổ hợp bộ lọc; tổng 3 trạng thái = 21 | đúng | 10+3+8=21; tham số sai 422 | api | PASS (API_ONLY) |
| CSV-01 | Kiểm duyệt | Xuất CSV | BOM, header `text,text_norm,label` | đúng | probe | PASS |
| MOD-01/02 | Kiểm duyệt | lọc khớp SQL; action sai 422 | đúng | đúng | probe | PASS |
| CHAT-01 | Chatbot | admin 403; khách khi chưa có khóa 503 | đúng | `[403, 503]` "Trợ lý chưa được bật." | probe | PASS |
| SYNC-01 | Dữ liệu | `movies.json` backend = frontend; luật ghế seats.py = seats.js | trùng | `cmp` trùng; 8×12, VIP F–H +20.000, tối đa 8 | source | PASS |
| GATE | Hồi quy | compileall / pytest / build real / build mock | exit 0 | 0 / **241 passed** (13:54:49–13:56:07) / 0 / 0 | log | PASS |

## 4. Sentiment Analytics Verification (T21)

Truy vết: `POST /movies/{id}/comments` → `classifier.predict` (PhoBERT B thật) → lưu `is_negative`, `negative_score`, `model_name=phobert_b`, `model_version` → `GET /admin/sentiment` dùng một truy vấn `SELECT … WHERE created_at ∈ [00:00 ngày đầu, 00:00 ngày mai)` với nhãn hiệu lực `CASE human_label IS NOT NULL THEN human_label ELSE is_negative` → `AdminSentiment.jsx` hiển thị trực tiếp JSON. **Không có giá trị cố định hay dữ liệu mẫu trong REAL** (source `admin_sentiment.py:15-82`; UI chỉ gọi `api.admin.sentiment`). SQL đối chiếu viết độc lập (`COALESCE(human_label, is_negative)`).

| Case | Before (7 ngày) | Action | Expected After | SQL | API | UI | Result |
|---|---|---|---|---|---|---|---|
| S21-00 | — | Baseline 7/30/90 | API = SQL | 15/8/8/0.75 · 30/18 · 30/18 | trùng | 30 ngày: 47/30/63.8%/77.8% sau thao tác, khớp API | PASS |
| S21-01 | 15 tổng, 8 tiêu cực | Bình luận thường (đã đo: binh_thuong) | 16 / 8 | 16/8, `is_negative=0`, `phobert_b` | 16/8 | — | PASS |
| S21-02 | 16/8 | Bình luận tiêu cực (đã đo 0.9992) | 17 / 9 | 17/9, score 0.9992 | 17/9 | — | PASS |
| S21-03 | 17/9, duyệt 8, acc 0.75 | Admin đổi nhãn tiêu cực → bình thường | 17/8, duyệt 9, acc 6/9; `is_negative` giữ 1 | `is_negative=1, human_label=0`, reviewer/time ghi | 17/8/9/0.667; `/comments/stats` = SQL | — | PASS |
| S21-04 | 17/8/10/0.7 | Ẩn rồi hiện | Thống kê không đổi (T21: tính cả ẩn); trang phim ẩn/hiện | không đổi | không đổi | công khai ẩn → hiện lại | PASS |
| S21-05 | 17/8/10 | Người khác xóa (404) rồi chủ xóa | 16, duyệt 9 | 16/8/9 | 16/8/9/0.778 | — | PASS |
| S21-06 | 16 | 4 bình luận ở 2 phim khác (1 ẩn danh + 9 điểm) | từng phim khớp GROUP BY, 7/30/90 khớp | khớp | khớp | — | PASS |
| S21-07 | 21 | 8 tài khoản gửi đồng thời | +8, không mất | +8 | `[201×8]`, +8 | — | PASS |
| S21-08 | — | Restart backend cùng DB; reload; đăng xuất/đăng nhập | không đổi | — | snapshot 7/30/90 trước/sau restart **trùng từng byte** | sau đăng nhập lại khớp | PASS |
| S21-09 | — | Bấm 7 (trả chậm 1,5 s) → 90 (0,7 s) → 30 | hiển thị 30 ngày | — | 3 request | UI 30 ngày = 47 (không bị 32 của 7 ngày đè); bấm lại 7 → 32 | PASS |
| S21-10 | — | Ẩn danh + sao; admin xem | công khai "Khán giả ẩn danh", không lộ khóa riêng; admin thấy tên thật; rating +1, bình luận đếm 1 lần | ratings +1 | 12 khóa công khai, không có `human_label/reviewed_*/user_id/email` | — | PASS |
| S21-UI | 7 ngày: 32/20 | Demo gửi qua UI: 3 điểm, ẩn danh, câu tiêu cực | 33/21; phim 3: 0/3 → 1/4; ratings 72→73 | dòng 48: `is_anonymous=1, is_negative=1, 0.9992, phobert_b`; rating 3 | 33/21, phim 3 1/4 | thông báo "Đã đăng… ẩn mặc định"; tổng quan phim 3 tiêu cực 25.0% | PASS |
| S21-TZ | — | Đồng hồ cố định 00:30, 06:59, 23:59:59 với bình luận lúc 00:00:00 (×2 cùng giây), 23:59:59.999999 hôm qua, 00:00 ngày đầu cửa sổ, 23:59:59 trước cửa sổ, 00:00 ngày mai | tổng 4; 27/10=2, 26/10=1, 21/10=1 | — | đúng cả 3 mốc giờ | — | PASS |
| S21-EMPTY | DB rỗng | 7/30/90 | 0, không NaN/Infinity, `model_human_accuracy=0` | — | đúng, đủ 7/30/90 ngày | trang hiển thị "Chưa có bình luận…" (source) | PASS |

**Công thức đã xác minh:** `negative_ratio = negative/total` (0 khi total=0); `model_human_accuracy = Σ(human_label = is_negative) / Σ(human_label IS NOT NULL)` trong cửa sổ — mẫu số là bình luận đã duyệt trong khoảng thời gian, kể cả bình luận ẩn; 0 khi chưa duyệt. Trang Kiểm duyệt (`/admin/comments/stats`) dùng mẫu số **toàn thời gian** (không lọc ngày), khác trang Thống kê — đúng theo contract từng task, cần nói rõ khi thuyết trình.

**Lỗi timezone từng ghi nhận (OBS-01 T27/T28/T29):** production **không** lệch giờ — mọi `created_at` và cửa sổ đều dùng giờ máy (naive local). Nguyên nhân là test `test_sentiment_uses_effective_label_group_by_and_complete_daily` tạo bình luận lúc `now − 1h` và `now − 2h` rồi khẳng định chúng thuộc "hôm nay"; khi chạy trong khoảng **00:00–01:59** một hoặc cả hai rơi sang hôm qua. Khoảng ghi "0h–7h" trong coordination rộng hơn thực tế. Lần pytest này chạy lúc 13:54 nên đạt. → **TEST-01** (mục 10).

## 5. Admin Dashboard Accuracy (T23)

Truy vấn: `admin_dashboard.py:13-55`. Trước khi tính, gọi `expire_holds()` rồi commit. Cửa sổ `[00:00 ngày đầu, 00:00 ngày mai)` theo `bookings.created_at` / `ratings.created_at` / `comments.created_at`; lấp ghế theo `showtimes.start_time ≥ 00:00 ngày đầu` (không chặn trên, gồm suất tương lai — theo bản sửa R2 của T23 và chú thích trên UI).

| KPI | Formula | Source | Expected (sau thao tác UI) | SQL Actual | API Actual | UI Actual | Result |
|---|---|---|---|---|---|---|---|
| Doanh thu | Σ total, status=paid | bookings | 11.425.000 + 210.000 | 11.635.000 | 11.635.000 | 11.635.000 đ | PASS |
| Vé đã thanh toán | đếm **đơn** paid (không phải ghế) | bookings | 69 + 1 | 70 | 70 | 70 | PASS |
| Vé đang chờ | held + pending_verify | bookings | 7 − 1 | 6 | 6 | 6 | PASS |
| Vé đã hủy | expired + rejected (vé khách tự hủy bị xóa hẳn, không tính) | bookings | 4 | 4 | 4 | 4 | PASS |
| Ghế đã bán | đếm booking_seats của đơn paid | booking_seats | 139 + 2 | 141 | 141 | 141 | PASS |
| Điểm toàn rạp | AVG/COUNT ratings tạo trong cửa sổ | ratings | 73 lượt | 7.616 / 73 | 7.616 / 73 | 7.6 / 10 · 73 lượt | PASS |
| Theo phim — vé/doanh thu | như trên GROUP BY phim | bookings ⨝ showtimes | phim 3: 10 vé | khớp | khớp | 10 · 1.835.000 đ | PASS |
| Theo phim — lấp ghế | ghế paid của suất ≥ đầu cửa sổ / (số suất ≥ đầu cửa sổ × 96) | booking_seats, showtimes | tăng khi bán vé suất tương lai | khớp mọi phim | khớp | phim 3: 2.0% → 2.1% | PASS |
| Theo phim — tiêu cực | nhãn hiệu lực / tổng (cửa sổ) | comments | phim 3: 1/4 | 0.25 | 0.25 | 25.0% | PASS |
| Biểu đồ ngày | doanh thu, vé paid theo `date(created_at)`; đủ N ngày | bookings | đủ 7/30/90 cột, ngày trống = 0 | khớp | khớp | 5 nhãn trục, không đè ở ~800px | PASS |

| Case | Before → After | Result |
|---|---|---|
| D23-00 | 7/30/90 trên seed: 11.120.000/68/1/1/136 · 23.310.000/141/1/1/282 — API = SQL từng khóa, từng phim | PASS |
| D23-01/02/03 | Đặt 2 ghế thường + 1 VIP: total = 3×95.000 + 20.000 = 305.000; đang chờ +1, doanh thu và ghế bán **không đổi** | PASS |
| D23-04 | Báo chuyển khoản → pending_verify; admin xác nhận: doanh thu +305.000, paid +1, ghế +3, chờ −1, lấp ghế phim 1,84% → 2,02% (đúng kịch bản T23 R1 từng FAIL) | PASS |
| D23-05 | Từ chối → hủy +1, ghế trả; vé giữ quá 15' (sửa `created_at` trên DB tạm) → expired khi mở tổng quan, ghế trả, hủy +1; khách tự hủy → xóa đơn, các số khớp SQL | PASS |
| D23-06 | Thêm suất tương lai → mẫu số tăng, lấp ghế giảm 2,02% → 1,91%; xóa suất trống → về đúng giá trị cũ; suất có vé không sửa/xóa được (409) | PASS |
| D23-07 | Thêm phim → xuất hiện với số 0 | PASS |
| D23-08 | Bình luận + sao qua UI → lượt chấm 72→73, tiêu cực phim 3 → 25% | PASS |
| D23-09 | Tab 7/30/90; days=0/5/366 → 422; đồng hồ cố định 00:30/06:59/23:59:59 cho bookings biên ngày → đúng ngày; DB rỗng → 0, không NaN | PASS |
| D23-10 | Restart backend cùng DB tạm → JSON 7/30/90 trùng từng byte; reload trình duyệt giữ số | PASS |
| OCC-01/02 | Lấp ghế đếm cả vé paid đặt ngoài cửa sổ cho suất trong phạm vi; loại vé held; suất quá khứ trước cửa sổ không vào mẫu số; vé giữ hết hạn tại `min(created+15', start−30')` | PASS |

**Soát vé** (API + UI): mã chữ thường có khoảng trắng tra được; paid → "Xác nhận vào rạp" (double-click chỉ gửi **1** POST); soát lại 409 kèm giờ; sau refresh tra lại hiện "Đã vào rạp lúc 14:09 · Quản trị viên", nút bị vô hiệu; held/pending/expired/rejected 409 đúng câu; mã sai 404; user thường 403. Không có contract cho "vé của suất đã qua" và "vé người khác" (admin soát mọi vé) → OBS-02.

## 6. User & Admin E2E Results (trình duyệt thật, REAL trên DB tạm)

| ID | Luồng | Kết quả |
|---|---|---|
| E2E-01 | Đăng nhập admin bằng form + Enter | PASS |
| E2E-02 | Menu tài khoản admin: 1 cột tài khoản + nhóm Quản trị 8 mục, không xuống dòng; Esc đóng, focus trả về nút | PASS |
| E2E-03 | Đăng xuất → mở `/quan-tri/tong-quan` → chuyển `/dang-nhap`, token xóa; demo đăng nhập vào route admin → "Không có quyền truy cập" | PASS |
| E2E-04 | Demo bình luận trên `/phim/3`: chọn 3 điểm, ẩn danh, câu tiêu cực → thông báo, hiện "Khán giả ẩn danh ★ 3/10" bản che; payload XSS `<img onerror>` hiện dạng chữ | PASS |
| E2E-05 | Chọn C5 + F6 (VIP) → 210.000 đ → Xác nhận (double-click) → 1 đơn FF00153 → QR + đếm ngược → "Tôi đã chuyển khoản" → refresh: "Chờ xác nhận chuyển khoản" | PASS (kèm BUG-06) |
| E2E-06 | Dialog điểm: mở, focus "Đóng", Esc không lưu; chọn 8 → Lưu → refresh: ★ 7.0/10 (3 lượt) = (6+7+8)/3 | PASS |
| E2E-07 | Thống kê cảm xúc: số liệu = API; chặn phản hồi cũ (mục 4 S21-09) | PASS |
| E2E-08 | Tổng quan 30 ngày = API = SQL | PASS |
| E2E-09 | Quản lý vé: "Đã nhận tiền" — hộp xác nhận Hủy thì không đổi DB; Đồng ý → "Đã xác nhận vé FF00153"; lọc "Tất cả trạng thái" → **"Không kết nối được máy chủ"** (500 do BUG-01) | FAIL → BUG-01 |
| E2E-10 | Tổng quan 7 ngày sau xác nhận cập nhật đúng (mục 5) ; soát vé UI (mục 5) | PASS |
| E2E-11 | Tài khoản admin 375px: không tràn ngang (scrollWidth 375), việc cần làm 27/1/20, công việc 2/9/2/2 = API | PASS (OBS-05) |
| E2E-12 | Console lỗi trên các trang đã duyệt | 0 lỗi |
| MOCK-01 | Đăng nhập admin mock, Thống kê (30/7/23.3%/75%), Tổng quan hiển thị, 0 lỗi console | PASS |
| MOCK-02 | Thêm bình luận tiêu cực trong mock → Thống kê 30→31, 7→8 (tính động) | PASS |

Lưu ý môi trường: pane trình duyệt bị ẩn nên `requestAnimationFrame` chậm ~765 ms; vòng điểm GSAP đọc giữa chừng hiện 4.0–4.5 rồi về đúng 6.5. Không phải lỗi sản phẩm.

## 7. Security Results

| Nhóm | Kiểm tra | Kết quả |
|---|---|---|
| 23 endpoint admin × 5 trạng thái xác thực | không token 401; user thường 403; JWT hết hạn 401; JWT ký sai khóa 401; chuỗi rác 401 | 115/115 đúng — PASS |
| 17 endpoint cần đăng nhập | không token → 401 | PASS |
| IDOR | Người khác hủy/báo chuyển khoản vé → 404, không thấy vé trong "Vé của tôi"; người khác xóa bình luận → 404 | PASS |
| Leo quyền | `PATCH /auth/me` kèm `role:"admin"` bị bỏ qua | PASS |
| Lộ dữ liệu | `UserOut` không có `password_hash`; bình luận công khai 12 khóa, ẩn danh không lộ danh tính | PASS |
| SQL injection | `q=' OR 1=1 --` → 200, 0 kết quả | PASS |
| XSS | Nội dung lưu nguyên văn, React escape; không có `dangerouslySetInnerHTML`/`innerHTML` trong `frontend/src` | PASS |
| CSV injection | `_csv_safe` thêm `'` trước `= + - @` | SOURCE_REVIEW_ONLY (pytest có test) |
| Upload | Content-Length và chunked > 3 MiB → 413 dừng sớm; không phải JPG/PNG/WebP → 422; tên file UUID; `/uploads/../app/config.py` và `%2e%2e` → 404 | PASS (trừ BUG-05) |
| Rate limit | Bình luận 3/60s → 429; chatbot user/admin 503/403 | PASS |
| Phiên | JWT cũ vẫn dùng được sau đổi mật khẩu/email | OBS-04 |
| Race | Ghế trùng đồng thời an toàn; giới hạn 2 vé giữ bị vượt | BUG-03 |

## 8. Bug List

### BASE-01 — Blocker trước T13/demo: DB thật chưa reset sau T29 (P1 vận hành)
- Evidence: `PRAGMA table_info(users)` (mode=ro) thiếu `birth_date, gender, avatar_url`; `models.User` khai báo 3 cột này; master đã chứa T29. Mọi truy vấn `User` (đăng nhập, `get_current_user`) sẽ lỗi `no such column` khi chạy backend với `firefly.db` hiện tại. Claude **không** khởi động backend trên DB thật để xác nhận (bị cấm) — kết luận từ schema + model.
- Expected: PO làm đúng quy trình `HUONG_DAN.md` mục T29 (dừng backend, sao lưu DB + sidecar + `backend\uploads\`, SHA-256/integrity, xóa `firefly.db`, khởi động lại) và cập nhật coordination (T29 đã merge 13:31).

### BUG-01 — P1 HIGH: Xóa phim để lại vé mồ côi, làm hỏng "Vé của tôi", "Quản lý vé" và soát vé
- File: `backend/app/routers/admin_movies.py:55-70` (`delete_movie`); hệ quả ở `backend/app/booking_rules.py:42-54` (`booking_out` đọc `booking.showtime.movie`).
- Steps: admin tạo phim + suất → khách đặt 1 vé → admin "Từ chối" (hoặc để vé hết hạn) → admin xóa phim (được phép vì chỉ chặn khi có vé không phải expired/rejected) → khách mở "Vé của tôi"; admin mở "Quản lý vé" với "Tất cả trạng thái" hoặc "Đã hủy…"; tra mã vé đó ở Soát vé.
- Expected: các trang vẫn tải; hoặc không cho xóa phim còn bất kỳ vé nào.
- Actual: `GET /api/bookings/me` 500, `GET /api/admin/bookings` 500, `GET /api/admin/checkin/FF…` 500; DB còn 1 booking trỏ tới showtime đã xóa (SQLite không bật FK). UI hiện "Không kết nối được máy chủ" vì phản hồi 500 không kèm CORS header.
- Evidence: probe `BUG-ORPHAN` `{"delete":200,"my_tickets":500,"admin_bookings":500,"checkin_lookup":500,"orphan_rows":1}`; E2E-09 network `GET /api/admin/bookings [FAILED]`.
- Rủi ro demo: dọn phim thử trước bảo vệ sẽ làm hỏng trang vé của khách/admin.
- Suggested fix: chặn xóa phim khi có **bất kỳ** booking nào (gợi ý chuyển "Đã chiếu xong"), hoặc xóa kèm booking expired/rejected và booking_seats của các suất bị xóa trong cùng transaction. Thêm regression test.

### BUG-02 — P2 MEDIUM: Mã vé bị cấp lại sau khi khách hủy vé giữ chỗ
- File: `backend/app/routers/bookings.py:86-105` (`cancel_booking` xóa hẳn dòng) + `models.Booking.id` (INTEGER PRIMARY KEY không AUTOINCREMENT) + `booking_rules.booking_code`.
- Steps: khách A đặt vé (id lớn nhất, ví dụ FF00147) → hủy → khách B đặt vé.
- Expected: B nhận mã mới.
- Actual: B nhận **FF00147** (`cancelled_user=16, new_user=17`).
- Impact: nội dung chuyển khoản/QR dùng mã vé; nếu A đã chuyển tiền theo QR rồi hủy, admin đối chiếu theo mã sẽ xác nhận nhầm vé của B. Soát vé theo mã cũ cũng trỏ sang vé B.
- Suggested fix: không xóa cứng (thêm trạng thái hủy — cần đổi CHECK, tức đổi schema) hoặc dùng `sqlite_autoincrement`/mã ngẫu nhiên. Cả hai đều đổi schema → cần PO quyết.

### BUG-03 — P2 MEDIUM: Giới hạn "tối đa 2 vé giữ chỗ" bị vượt khi gửi đồng thời
- File: `backend/app/routers/bookings.py:39-53` (đếm rồi mới insert, không khóa).
- Steps: 1 tài khoản gửi đồng thời 4 `POST /api/bookings` cho 4 suất khác nhau.
- Expected: 2 thành công, 2 nhận 409.
- Actual: `[201,201,201,201]`, DB 4 vé `held` (lần chạy trước: 3).
- Suggested fix: tuần tự hóa theo user (ví dụ `BEGIN IMMEDIATE` trước khi đếm, hoặc kiểm lại số vé held sau insert và rollback).

### BUG-04 — P2 MEDIUM (regression T27): Bộ sưu tập "Đánh giá cao" vẫn dùng ngưỡng của thang 5
- File: `backend/app/routers/movies.py:103` (`m.rating_avg >= 4.0`), `frontend/src/api/mock.js:625` (`>= 4`). T22 đặt 4.0 cho thang 5; T27 đổi sang thang 10 nhưng không đổi ngưỡng.
- Steps: 3 khán giả chấm 4/10 cho một phim → mở Khám phá → "Đánh giá cao".
- Actual: phim trung bình 6.43/10 (và 5.06/10 ở lần chạy khác) nằm trong "Đánh giá cao"; phim 4.0/10 cũng lọt.
- Suggested fix: ngưỡng 8.0 (tương đương 4/5) ở cả real và mock, thêm test.

### BUG-05 — P3 LOW: Ảnh hỏng/cắt cụt vẫn được nhận làm ảnh đại diện (và poster)
- File: `backend/app/routers/admin_posters.py:43-59` (`validate_image` chỉ kiểm magic bytes).
- Actual: 30 byte đầu của một PNG → 200, file được lưu, trình duyệt hiện ảnh vỡ.
- Suggested fix: kiểm cấu trúc tối thiểu không cần thư viện mới (PNG có `IHDR` + `IEND`, JPEG kết thúc `FFD9`, WebP `RIFF` size khớp). Không thêm thư viện khi chưa hỏi Tín.

### BUG-06 — P3 LOW: Thông báo "Đã giữ chỗ thành công…" còn hiện sau khi tải lại và khi vé đã sang "Chờ xác nhận"
- File: `frontend/src/pages/MyTickets.jsx:60-62` (đọc `location.state.newBookingId`, state của history còn sau reload).
- Suggested fix: xóa state sau lần hiển thị đầu (`navigate(".", { replace: true, state: null })`) hoặc chỉ hiện khi vé còn `held`.

## 9. Existing TODO / Known Issues (không đổi disposition)

| Nguồn | Mục | Trạng thái theo coordination | Ghi chú audit |
|---|---|---|---|
| T12 | TODO-01 | PO chưa quyết, giữ mở trước T13 | chưa kiểm lại |
| T14 | TODO-02 | PO điền trước khi gửi T13 | chưa kiểm lại |
| T16 | TODO-01 (DB thật/deploy) | còn hiệu lực | liên quan BASE-01 |
| T17 | Gemini production chưa được phép; model mặc định phải là model đã kiểm | còn hiệu lực | chatbot thật **BLOCKED** (không dùng khóa thật) |
| T21 | TODO-02/03/05 Low | còn mở | không phát hiện sai số liệu |
| T23 | OBS-01..03 ACCEPT_LATER | | lấp ghế không chặn trên theo thời gian — đúng bản sửa R2, đã có chú thích UI |
| T25 | TODO-01/02 Low (form admin) | chờ PO | không kiểm lại form admin bằng trình duyệt |
| T27 | TODO-01 Low; OBS-01 test_sentiment 0h–7h | chờ PO | OBS-01 thực chất là lỗi test, cửa sổ 00:00–01:59 (TEST-01) |
| T28 | OBS-01..06 round 1 | chờ PO | OBS-05 dưới đây có thể trùng "menu gọn ở ≤1360px" |
| T29 | TODO-01/02/03 CLOSED | — | AV-03/04 xác nhận lại 413 chunked và chunked hợp lệ |

**Quan sát mới (không có contract, chờ PO quyết, không phải bug):**
- OBS-01: Vé `pending_verify` không bao giờ hết hạn; suất đã chiếu vẫn có thể "Đã nhận tiền" và cộng vào doanh thu (seed có FF00142 suất 09:30 hôm nay vẫn chờ).
- OBS-02: Soát vé không giới hạn theo ngày suất chiếu.
- OBS-03: Tài khoản chưa nhập ngày sinh vẫn đặt được phim T18 (T29 chỉ quy định admin không bị chặn).
- OBS-04: JWT cũ còn hiệu lực sau đổi mật khẩu/email (không thu hồi phiên).
- OBS-05: Ở 375px, header xuống 2 hàng (nút "Menu" sang hàng dưới) khi tên "Quản trị viên".
- OBS-06: Thẻ "Điểm" trên Tổng quan xuống dòng ở bề rộng ~800px (giống T24 OBS-01).
- OBS-07: Dữ liệu mock ít hơn real (mock 1 vé paid, real 141) — khóa JSON giống nhau nhưng con số demo khác nhau giữa hai chế độ.
- OBS-08: Trang Thống kê tính độ khớp model theo cửa sổ ngày, trang Kiểm duyệt tính toàn thời gian → hai con số "độ chính xác" khác nhau là đúng thiết kế, nên nói rõ khi bảo vệ.

## 10. Test Coverage Gaps

- **TEST-01**: `backend/tests/test_sentiment.py:47-59,88-95` phụ thuộc đồng hồ (fail 00:00–01:59). Đề xuất dùng mốc cố định giữa ngày hoặc monkeypatch `admin_sentiment.datetime` như `probe_clock.py`.
- Chưa có regression test cho BUG-01..05 và cho giới hạn 2 vé giữ dưới tải đồng thời.
- pytest dùng FakeClassifier → không chứng minh PhoBERT B. Audit này đo riêng PhoBERT B thật qua `/api/admin/predict` và luồng bình luận (nhãn, điểm, `model_name`, `model_version`), `normalize()` không đổi từ T10 (`ed26454`). Không đo lại F1.
- Chưa chạy bằng trình duyệt (chỉ API hoặc đọc mã): form Thêm/Sửa phim, tải poster/trailer, phát trailer MP4/WebM/YouTube và Range; trang Suất chiếu; trang Kiểm duyệt (bấm duyệt/đổi nhãn/ẩn/CSV); So sánh mô hình; Khám phá (bộ lọc, reset); trang chủ/carousel/hiệu ứng; reduced motion; đăng ký; đổi mật khẩu/email/ảnh đại diện bằng UI; chatbot kéo thả và mock chat; độ rộng 1366/1440; điều hướng bàn phím toàn trang; back/forward.
- Chatbot Gemini thật: **BLOCKED** (không có môi trường/khóa test được phép).
- Phim T13/T16: probe tuổi chỉ chạy được T18 (không có suất T13 khả dụng trong seed tại thời điểm chạy); helper dùng chung nên rủi ro thấp.
- Ca "vé paid của suất quá khứ" (CK-04) không có dữ liệu phù hợp trong DB tạm nên không chạy.

## 11. Final Readiness

**FAIL** — chưa sẵn sàng chốt v1.0:
1. BASE-01: DB thật chưa reset theo T29 → backend thật sẽ lỗi khi đăng nhập.
2. BUG-01 (P1): một thao tác quản trị hợp lệ (xóa phim) làm hỏng trang vé của khách và admin.
3. BUG-02/03/04 (P2) là lỗi nghiệp vụ thật, có bằng chứng tái hiện.

Riêng hai trọng tâm PO yêu cầu:
- **A. Sentiment Analytics T21: DYNAMIC_VERIFIED** — số liệu đi từ PhoBERT B thật → SQLite → API → UI, thay đổi đúng sau thêm, đổi nhãn, ẩn/hiện, xóa, đồng thời, restart, bộ lọc 7/30/90, biên ngày 00:00–07:00 và DB rỗng; khớp SQL độc lập ở mọi bước.
- **B. Admin Dashboard T23: DATA_ACCURACY_VERIFIED** — mọi thẻ, biểu đồ và bảng theo phim khớp SQL độc lập ở 7/30/90 ngày, thay đổi đúng khi giữ chỗ, thanh toán, từ chối, hết hạn, hủy, thêm/xóa suất, thêm phim, chấm điểm, bình luận; vé held không vào doanh thu; lấp ghế tăng khi bán vé suất tương lai.

Pytest 241/241 không có nghĩa là sẵn sàng release: 4 lỗi trên đều không có test.

### Dọn dẹp
- Đã dừng backend 8010 và Vite 5180/5174; không còn cổng nào lắng nghe.
- Đã xóa DB tạm, sidecar tạm, UPLOAD_DIR tạm, `dist` mock, thư mục probe đồng hồ; khôi phục `.claude/launch.json` (file bị loại khỏi Git) về bản gốc; xóa localStorage của hai origin trong pane trình duyệt.
- `frontend/dist/` được build lại bởi gate REAL (thư mục bị gitignore).
- Giữ lại trong scratchpad (ngoài repo): `probe_http.py`, `probe_clock.py`, `run_final.log`, `probe_http_results.json`, `snap_before/after.json` làm bằng chứng.
- Production: hash `firefly.db` và sidecar không đổi; `backend/uploads/` không đổi; `git status` sạch. Báo cáo này **chưa commit**.

## Phụ lục A — Vòng bổ sung sau T30 (27/10/2026, 20:58–21:15)

- Mục đích: lấp các khoảng trống ở mục 10 và kiểm lại các lỗi T30 trên giao diện thật.
- Code: nhánh `task/T30-sua-loi-audit` @ `3655b5e` (T30 đã PASS_WITH_TODO).
- Môi trường:
  - backend 8012 với SQLite và UPLOAD_DIR tạm, PhoBERT B thật (`phobert-B-2026-10-09`);
  - frontend real 5183 và mock 5184;
  - `CHAT_API_KEY` để trống, BANK_* không cấu hình.
- Tài khoản: tài khoản thử tạo riêng trong DB tạm.

| Mã | Phạm vi | Thao tác (trình duyệt thật) | Kết quả |
|---|---|---|---|
| A-01 | Form phim + poster | Thêm phim T16 qua form. Chọn PNG cắt cụt → bấm Thêm. Sau đó chọn PNG hợp lệ (canvas) → Thêm | Ảnh hỏng: `POST /admin/posters` 422 "Ảnh bị hỏng hoặc không đầy đủ.", không tạo phim. Ảnh hợp lệ: "Đã thêm phim mới.", DB có `poster_url`, file nằm trong UPLOAD_DIR tạm. **PASS** |
| A-02 | Trailer | Sửa phim, chọn WebM thật ghi từ canvas (3.143 byte) → lưu → trang chi tiết → bấm phát | `<video>` readyState 4, dài 2,275 giây; Range trả 206. File WebM rỗng (110 byte) → "Không phát được video trailer." **PASS**. File trailer cũ còn lại sau khi thay (hạn chế đã biết T25). |
| A-03 | Suất chiếu | Thêm 10:00 Phòng 4 (phim 105'); thêm 11:59 cùng phòng; thêm 12:00; sửa 10:00→10:30; xóa suất 12:00 | 11:59 bị chặn "Phòng 4 đã có suất … lúc 10:00", 12:00 đúng biên đệm 15' nên được nhận. Sửa: "Đã cập nhật suất chiếu.". Xóa có hộp xác nhận, sau đó "Đã xóa suất chiếu.". **PASS** |
| A-04 | Kiểm duyệt | Khách gửi 1 câu chê, 1 câu khen (PhoBERT B thật: 1.00 / 0.00). Admin: Xác nhận nhãn, Đổi sang tiêu cực, Ẩn | Nhãn, người duyệt, trạng thái "Đã ẩn" cập nhật ngay. API công khai không còn bình luận đã ẩn. **PASS** |
| A-05 | BUG-06 (T30) | Đặt vé qua UI → "Vé của tôi" → F5 | Lần đầu hiện thông báo, `history.state.usr` = null. Sau F5 không còn thông báo. **PASS** |
| A-06 | BUG-02 (T30) | Hủy FF00144 bằng nút "Hủy vé" (có hộp xác nhận), đặt lại | Mã mới FF00145. Mock: FF00005 → FF00006. **PASS** |
| A-07 | BUG-01 (T30) | Vé FF00145 hết hạn → admin bấm Xóa phim ở trang Quản lý phim | Trả 409 "Phim đã có vé, không xóa được…", phim vẫn còn. `/admin/bookings` 200, `/admin/checkin/FF00145` 200, `/bookings/me` thấy `expired`. Mock: vé rejected → 409. **PASS** |
| A-08 | BUG-04 (T30) | `collection=top_rated` real + mock | 13 phim, tất cả ≥ 8.0. Phim cao nhất dưới ngưỡng là 6.5, không lọt. **PASS** |
| A-09 | BUG-05 mock | `putAvatar` với PNG cắt cụt / JPEG thiếu FFD9 / WebP sai kích thước / PNG hợp lệ | 3 ca hỏng → 422 đúng câu, PNG hợp lệ được nhận. **PASS** |
| A-10 | 1366 / 1440 | Trang chủ, Khám phá, chi tiết phim, Tài khoản, Tổng quan, Thống kê, Quản lý vé, Soát vé, So sánh mô hình, Kiểm duyệt, Quản lý phim, Suất chiếu | `scrollWidth` = `clientWidth` ở mọi trang (không tràn ngang). Header không có mục nào xuống dòng. **PASS** |
| A-11 | Reduced motion | Đọc code: `global.css` có 8 khối `prefers-reduced-motion`; `utils/motion.js` có `MOTION_OK` / `useReducedMotion`; mọi component/trang gọi `gsap.to/from/fromTo/timeline` đều có chặn | **PASS (đọc code)**. Trình duyệt tích hợp không giả lập được media này. |
| A-12 | Chuyển khoản | "Tôi đã chuyển khoản" khi không có BANK_* | 409, đúng thiết kế T16 (chưa bật QR). Không phải lỗi. |

**Quan sát mới (không chặn):**
- OBS-A1 (Low): khi poster hỏng, câu "Ảnh bị hỏng hoặc không đầy đủ." xuất hiện ở **2 phần tử** trên form Quản lý phim (lỗi của ô chọn file và thông báo chung). Em chưa chụp ảnh để xác nhận có hiển thị trùng trên màn hình hay không. Đề xuất PO nhìn lại khi PO review. Nếu trùng thì ghi Hạn chế hoặc sửa ở T13.

**Vẫn chưa kiểm:**
- Chatbot Gemini thật: BLOCKED, không có khóa được phép dùng.
- Reduced motion trên trình duyệt thật: chỉ đọc code.
- Backend trên DB thật: chờ PO reset sau merge T30.

**Kết luận phụ lục:**
- Không phát hiện lỗi mới cần Task Record.
- BUG-01, 02, 04, 05, 06 đã được xác nhận sửa trên giao diện thật (real) và trong mock. BUG-03 đã xác nhận qua test đồng thời ở review T30.
- Khi PO merge T30 và reset DB, các lỗi P1/P2 của kết luận FAIL ban đầu không còn.

**Dọn dẹp:**
- Đã dừng 3 server tạm và khôi phục `.claude/launch.json` từ bản sao.
- Đã xóa DB, UPLOAD_DIR và tài khoản thử (nằm trong DB tạm). Đã xóa localStorage và sessionStorage ở cả hai tab, đưa viewport về mặc định.
- SHA-256 của `backend/firefly.db` và sidecar trùng với lần đo trước audit, tức không thay đổi.
