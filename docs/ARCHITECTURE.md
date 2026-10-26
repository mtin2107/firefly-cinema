# ARCHITECTURE — Firefly Cinema

> Hợp đồng kỹ thuật mà mọi task phải giữ. Mô tả chi tiết cây thư mục, routes, API, schema xem `BOI_CANH_DU_AN.md` mục 3.
> Task nào đổi một mục dưới đây phải cập nhật file này trong cùng nhánh và ghi vào report.
> Cập nhật: 12/10/2026 (T16 — giữ chỗ và thanh toán QR).

## 1. Sơ đồ thành phần

```
Trình duyệt
   │
   ▼
React SPA (Vite, cổng 5173)
   pages/ ─► components/ ─► api/index.js ──┬─► real.js ─► http.js ──HTTP/JSON + Bearer JWT──┐
                                           └─► mock.js (localStorage "firefly_mockdb_v2")   │
                                                                                            ▼
                                                                    FastAPI (cổng 8000) app/main.py
                                                                    ├─ routers/ auth · movies · bookings · admin_bookings · comments
                                                                    ├─ security.py (JWT HS256 24h, PBKDF2, require_admin)
                                                                    ├─ seats.py (luật ghế) · booking_rules.py (hạn giữ chỗ)
                                                                    ├─ classifier.py (normalize() + PhoBERT / keyword)
                                                                    └─ database.py ─► SQLite backend/firefly.db
```

## 1b. Cây thư mục đích (sau T00–T15)

**Không tổ chức lại cấu trúc hiện có.** Code mới chỉ được thêm vào đúng chỗ dưới đây. Ký hiệu: không ghi chú = đã có; `[Txx]` = task đó tạo; `(ngoài Git)` = có trên máy nhưng bị `.gitignore`.

```
C:\Projects\firefly-cinema\
├── CLAUDE.md                      hướng dẫn cho Claude Code
├── README.md                      [T13 hoàn thiện]
├── HUONG_DAN.md                   [T00, T06, T07, T10, T11, T12, T13 cập nhật]
├── CHANGELOG.md                   [T11]
├── chay-firefly.bat               ⚠ tài liệu ghi là có nhưng CHƯA có trong repo (xem mục 4)
├── reset-demo.bat                 [T12]
├── .gitignore
├── Bao_cao\                       bản Word báo cáo (*.docx ngoài Git)
├── backup\                        (ngoài Git) 02_api_cu\ API cũ, v1.0\ [T13]
│
├── frontend\                      ── GIAO DIỆN (React + Vite)
│   ├── .env                       (ngoài Git)
│   └── src\
│       ├── App.jsx                routes; thêm route admin ở T04, T05, T07, T14
│       ├── config.js
│       ├── api\
│       │   ├── index.js           điểm import duy nhất
│       │   ├── http.js
│       │   ├── real.js            + admin.movies [T04], admin.showtimes [T05], duyệt bình luận [T06],
│       │   ├── mock.js              admin.predict [T07], hủy vé/tài khoản [T14] — cả hai file
│       │   └── movies.json
│       ├── context\AuthContext.jsx
│       ├── components\            giữ nguyên; Header thêm mục menu admin
│       │   ├── HeroCarousel.jsx       [T18] hero băng chuyền poster 3D
│       │   └── FireflyField.jsx       [T18] đom đóm canvas (nền hero, bung khi in vé)
│       ├── pages\
│       │   ├── Home, Explore, MovieDetail, SeatSelection, Checkout, MyTickets,
│       │   │   Login, Register, NotFound, AdminComments
│       │   ├── AdminMovies.jsx        [T04]  /quan-tri/phim
│       │   ├── AdminShowtimes.jsx     [T05]  /quan-tri/suat-chieu
│       │   ├── AdminModelCompare.jsx  [T07]  /quan-tri/so-sanh-mo-hinh
│       │   └── Account.jsx            [T14]  /tai-khoan
│       ├── utils\                 format.js, seats.js, taxonomy.js, motion.js [T18]
│       └── styles\global.css
│
├── backend\                       ── MÁY CHỦ (FastAPI)
│   ├── .env                       (ngoài Git)
│   ├── .env.example               [T00, T07, T10 cập nhật]
│   ├── requirements.txt
│   ├── requirements-ml.txt        [T00 ghim phiên bản, T07 thêm scikit-learn/joblib]
│   ├── requirements-dev.txt       [T11] pytest, httpx
│   ├── pytest.ini                 [T11]
│   ├── firefly.db                 (ngoài Git)
│   ├── models\                    (ngoài Git)
│   │   ├── phobert-binhluan\          model A
│   │   ├── phobert-binhluan-B\        model B [T10]
│   │   └── baselines\svm_A.joblib …   [T07]
│   ├── scripts\                   [T10, T12]
│   │   ├── check_model.py             [T10] chấm 10 câu kiểm thử
│   │   └── reset_demo.py              [T12]
│   ├── tests\                     [T11]
│   │   ├── conftest.py                DB tạm + classifier giả lập
│   │   └── test_*.py
│   └── app\
│       ├── main.py, config.py, database.py, models.py, schemas.py, security.py, seats.py, seed.py
│       ├── classifier.py          normalize() + registry nhiều model [T07, T10]
│       ├── taxonomy.py            [T04] danh sách thể loại/quốc gia hợp lệ (khớp taxonomy.js)
│       ├── showtime_rules.py      [T05] luật chồng giờ
│       ├── data\
│       │   ├── movies.json
│       │   └── demo_comments.json     [T12]
│       └── routers\
│           ├── auth.py, movies.py, bookings.py, comments.py
│           ├── admin_movies.py        [T04] CRUD phim, require_admin, chặn xóa phim đã có vé
│           ├── admin_showtimes.py     [T05]
│           └── admin_predict.py       [T07]
│
├── ml\                            ── HỌC MÁY (mã train, notebook, kết quả nhỏ)
│   ├── README.md                  [T00] bản đồ dữ liệu / model / notebook
│   ├── README_goc.md              [T00] README cũ của thesis_project
│   ├── model_card_A.md            [T00]
│   ├── model_card_B.md            [T09]
│   ├── labeling_guideline.md      [T03]
│   ├── test_sentences.json        [T10]
│   ├── requirements-ml-train.txt  [T01]
│   ├── src\
│   │   ├── (mã cũ thesis_project)     [T00] prep, train, base…, comm…, erro…
│   │   ├── baselines.py               [T01]
│   │   ├── eval_utils.py              [T02] hàm tính chỉ số dùng chung
│   │   └── prepare_movie_data.py      [T03]
│   ├── notebooks\                 T01_baselines, T02_comparison, T08_domain_shift,
│   │                              T09_phobert_B, T15_word_segment (.ipynb)
│   ├── results\
│   │   ├── baselines.csv [T01], comparison_A.csv [T02], domain_shift.csv [T08],
│   │   │   comparison_B.csv [T09], word_segment.csv [T15]
│   │   ├── error_analysis.md [T02], domain_shift_errors.md [T08], movie_data_stats.md [T03]
│   │   └── figures\*.png
│   └── artifacts\                 (ngoài Git) phobert_A_best\ model A gốc, phobert_A.json,
│                                  phobert_B_best\ [T09], baselines\*.joblib [T01]
│
├── data\                          ── DỮ LIỆU: README trong Git, CSV ngoài Git
│   ├── README.md                  [T00 tạo, T03 bổ sung]
│   ├── uit-visfd\processed\       (ngoài Git) train/dev/test(.csv), *_aspect_sentiment.csv
│   ├── uit-visfd\results\         (ngoài Git) error_analysis_taskA.csv
│   └── phim\                      (ngoài Git) movie_comments_v1.csv, train/test [T03]
│
├── docs\                          ── TÀI LIỆU DỰ ÁN (xem docs/README.md)
│   ├── tasks\T00.md … T15.md
│   ├── images\                    ảnh cho báo cáo [T02, T08, T13]
│   ├── KICH_BAN_DEMO.md           [T12]
│   └── SAO_LUU.md                 [T13]
│
└── reports\YYYY-MM-DD\            ── BÁO CÁO Codex / Claude / PO theo từng task
```

Ngoài máy: Google Drive `MyDrive/thesis/data/…`, `MyDrive/thesis_results/…`, `MyDrive/thesis_backup_v1/` [T13].

**Ổ D ngừng sử dụng từ 04/10/2026.** Ánh xạ nơi cũ → nơi mới (Claude chép, kiểm SHA256 18/18 file khớp):

| Nơi cũ (`D:\KhoaLuan_PhimVe\`) | Nơi mới (`C:\Projects\firefly-cinema\`) |
|---|---|
| `01_training\thesis_project\processed\` | `data\uit-visfd\processed\` |
| `01_training\thesis_project\results\error_analysis_taskA.csv` | `data\uit-visfd\results\` |
| `01_training\thesis_project\src\`, `README.md`, `results\*.json` | `ml\src\`, `ml\README_goc.md`, `ml\results\` (Codex chép trong T00) |
| `thesis_results\` (model A gốc, `phobert_A.json`) | `ml\artifacts\` |
| `06_backup\02_api_cu\api\` (bỏ `venv\`) | `backup\02_api_cu\api\` |
| `04_data_phim\` (rỗng) | `data\phim\` |
| `05_baocao\` (rỗng) | `Bao_cao\` |

## 2. Hợp đồng bất biến

### 2.1. Lớp API frontend
- Page và component **chỉ** import `api` từ `src/api/index.js`.
- Thêm endpoint ⇒ thêm hàm cùng tên vào cả `real.js` và `mock.js`, trả cùng cấu trúc JSON.
- `VITE_USE_MOCK=true` phải luôn chạy được toàn bộ luồng.

### 2.2. Lỗi
- Backend: `HTTPException(status, "một câu tiếng Việt")` → `{"detail": "..."}`. 422 đã được gộp thành một câu.
- Frontend hiển thị thẳng `detail`, mọi trang có trạng thái loading / rỗng / lỗi qua `StateViews`.

### 2.3. Phân quyền
- Endpoint admin dùng dependency `require_admin`. User thường → 403. Chưa đăng nhập → 401.
- Route giao diện cần đăng nhập bọc bằng `ProtectedRoute`.

### 2.4. Dữ liệu và đồng bộ hai nơi

| Thứ phải khớp | Nơi 1 | Nơi 2 |
|---|---|---|
| Luật ghế (A–H, 12 ghế/hàng, F–H VIP +20.000 đ, tối đa 8 ghế) | `frontend/src/utils/seats.js` | `backend/app/seats.py` |
| Dữ liệu phim | `backend/app/data/movies.json` | `frontend/src/api/movies.json` |
| Nhãn thể loại / quốc gia / định dạng | `frontend/src/utils/taxonomy.js` | Dữ liệu phim |
| `_SAMPLE_SALES` (nợ kỹ thuật) | `backend/app/seed.py` | `frontend/src/api/mock.js` |

### 2.5. Cơ sở dữ liệu
- Ràng buộc `UNIQUE(showtime_id, seat_code)` trên `booking_seats` là cơ chế chống đặt trùng ghế. Không gỡ.
- Chưa có migration (`create_all`). Q2 đã chốt **NO ALEMBIC / BACKUP_BEFORE_RESET** cho T06: xác định đúng database, dừng backend, tạo và xác minh backup rồi PO mới tự xóa `firefly.db`; khởi động lại để `create_all` và seed tạo schema mới.

### 2.6. Mô hình
- `normalize()` trong `backend/app/classifier.py` là hàm tiền xử lý chuẩn. Notebook đánh giá mọi model phải dùng đúng hàm này.
- Không sửa `normalize()` khi chưa đo lại F1 trên test và ghi vào model card.
- Nhãn `1 = tieu_cuc`, ngưỡng mặc định `NEGATIVE_THRESHOLD=0.5`.
- T10 đăng ký `phobert_b` từ `MODEL_DIR_B` bên cạnh `phobert` (A). Mặc định `ACTIVE_MODEL=phobert_b`; nếu B thiếu hoặc không nạp được thì fallback sang A, sau đó mới tới keyword. `ACTIVE_MODEL=phobert` và restart chọn lại A.
- PhoBERT active được nạp khi registry khởi tạo; PhoBERT còn lại nạp lười khi trang so sánh gọi và được giải phóng sau inference để tránh giữ đồng thời hai checkpoint trong RAM. Model/tokenizer chỉ đọc file local.
- Version PhoBERT lấy từ `MODEL_VERSION_A`/`MODEL_VERSION_B`, hoặc `version.txt` trong thư mục model; nếu không có thì dùng fingerprint `config.json`. `/api/health` báo model thực sự active, `active_version`, trạng thái available/loaded và lỗi fallback.
- `comments.model_version` nullable để giữ dữ liệu cũ; bình luận mới lưu cả tên và version của model thực sự chấm điểm.
- `POST /api/admin/predict` chạy các model đã nạp trên cùng `normalize()` và chỉ dành cho admin. Điểm SVM là sigmoid của `decision_function`, không phải xác suất đã hiệu chỉnh.

### 2.7. Quản trị suất chiếu
- CRUD quản trị dùng `GET/POST /api/admin/showtimes` và `PUT/DELETE /api/admin/showtimes/{id}`; tất cả route dùng `require_admin`.
- `ShowtimeIn` chỉ nhận phim tồn tại chưa `ended`, giờ tương lai, một trong bốn phòng `Phòng 1`–`Phòng 4`, giá 10.000–500.000 đồng và là bội số 1.000.
- Khoảng chiếm phòng là `[start_time, start_time + duration_min + 15 phút)`. Hai khoảng giao nhau trong cùng phòng bị chặn; đúng mốc kết thúc cộng 15 phút được phép.
- `backend/app/showtime_rules.py` là luật dùng chung cho CRUD và `_ensure_showtimes()`; seed lấp từng khung còn trống thay vì bỏ qua hoặc ghi đè cả ngày có suất admin.
- Suất có dòng `booking_seats` không được sửa/xóa. Frontend real và mock cùng contract `api.admin.showtimes.{list,create,update,remove}`.

### 2.8. Kiểm duyệt bình luận có người duyệt
- `comments` giữ nguyên kết quả model ở `is_negative`, `negative_score`, `model_name`; nhãn người duyệt nằm riêng ở `human_label` (`0` hoặc `1`), kèm `reviewed_by`, `reviewed_at` và cờ `hidden`.
- Nhãn hiệu lực công khai là `human_label` nếu đã duyệt, ngược lại là `is_negative`; bình luận `hidden=true` không được trả về API công khai.
- API admin bình luận dùng `require_admin`, hỗ trợ phân trang/lọc trạng thái duyệt, confirm/relabel/hide/unhide, thống kê TP/FP/TN/FN và CSV UTF-8 BOM gồm đúng `text,text_norm,label`.
- `GET /api/admin/sentiment?days=30` dùng `require_admin`, nhận `days` từ 1 đến 365 và tổng hợp bằng SQL `GROUP BY`. Cả `summary`, `movies`, `daily` dùng nhãn hiệu lực (`human_label` nếu đã duyệt, nếu chưa dùng `is_negative`) và tính cả bình luận đã ẩn. Khoảng ngày gồm hôm nay cùng `days - 1` ngày trước: mốc đầu 00:00 ngày đầu được tính, mốc cuối 00:00 ngày mai không được tính, theo giờ địa phương như `created_at` đang lưu; `daily` luôn đủ đúng số ngày và lấp ngày trống bằng 0.

### 2.9. Giữ chỗ và thanh toán vé

- `bookings.status` chỉ nhận `held`, `pending_verify`, `paid`, `expired`, `rejected`; vé mới là `held`, dữ liệu seed là `paid`.
- Hạn giữ chỗ bằng giờ chiếu trừ 30 phút. `booking_rules.py` thực hiện hủy lười trước khi đọc sơ đồ ghế, tạo/đọc vé và liệt kê vé admin.
- Khi vé `held` hết hạn hoặc admin từ chối, các dòng `booking_seats` phải bị xóa để giải phóng ràng buộc `UNIQUE(showtime_id, seat_code)`; dòng `bookings` vẫn giữ làm lịch sử.
- `pending_verify` và `paid` không tự hết hạn. Mỗi tài khoản chỉ có tối đa một vé `held` cho một suất; 30 phút cuối không nhận đặt online.
- Mã vé là `FF` cộng ID đệm đủ 5 chữ số. Backend tạo VietQR từ `BANK_ID`, `BANK_ACCOUNT`, `BANK_ACCOUNT_NAME`; thiếu cấu hình thì `qr_url=null`.
- API mới gồm `POST /api/bookings/{id}/transfer-claim` và nhóm `GET/POST /api/admin/bookings`; mọi endpoint admin dùng `require_admin`. Real và mock giữ cùng cấu trúc JSON.
- `text_norm` trong CSV luôn dùng `normalize()` hiện hành của backend. Real API và mock API giữ cùng contract.

### 2.10. Bí mật và file lớn
- Không commit: `.env`, `firefly.db`, `backend/models/`, `venv/`, `node_modules/`, file model, CSV/XLSX lớn.

## 3. Thay đổi kiến trúc dự kiến theo kế hoạch

| Task | Thay đổi | Cập nhật mục |
|---|---|---|
| T04, T05 | `/api/admin/movies`, `/api/admin/showtimes` (CRUD) | 2.3, BOI_CANH 3.2 |
| T06 | `comments` thêm `human_label`, `reviewed_by`, `reviewed_at`, `hidden`; API xuất CSV | 2.5 |
| T07 | Registry nhiều model, `ACTIVE_MODEL`, `POST /api/admin/predict` | 2.6 |
| T10 | `MODEL_VERSION` trong `/api/health` và từng bình luận | 2.6 |
| T11 | Thư mục `backend/tests/` + pytest với model giả lập | — |

## 4. Nhật ký thay đổi kiến trúc

| Ngày | Task | Thay đổi |
|---|---|---|
| 03/10/2026 | — | Tạo file từ trạng thái `phobert-v1` |
| 04/10/2026 | — | Thêm cây thư mục đích. Phát hiện: `chay-firefly.bat` không có trong repo; thư mục `Bao_cao\` rỗng ở gốc trùng vai trò với `docs\` và `D:\KhoaLuan_PhimVe\05_baocao\` |
| 04/10/2026 | T00 (PO đổi phạm vi) | Mọi hoạt động chuyển về ổ C. Thêm `data\uit-visfd\`, `data\phim\`, `ml\artifacts\`, `backup\` (ngoài Git); `Bao_cao\` giữ lại làm nơi để bản Word. Ổ D ngừng sử dụng |
| 08/10/2026 | T04 | Thêm CRUD `/api/admin/movies`, taxonomy backend/frontend đồng bộ và trang `/quan-tri/phim`; không đổi schema |
| 08/10/2026 | T05 | Thêm CRUD `/api/admin/showtimes`, luật chống chồng phòng dùng chung với seed và trang `/quan-tri/suat-chieu`; không đổi schema |
| 08/10/2026 | T06 | Thêm nhãn người duyệt/ẩn bình luận, phân trang, thống kê model và CSV; đổi schema comments theo Q2 NO ALEMBIC / BACKUP_BEFORE_RESET |

## T17 — Trợ lý tư vấn phim (12/10/2026)

- `POST /api/chat`: yêu cầu token JWT qua `get_current_user`; chỉ role `user`, không dùng cho admin, guest. Request `messages` 1–10, mỗi tin ≤ 500 ký tự, cuối `user`. Response `{reply: string, movies: [{id, title}]}` tối đa 5 phim được nêu trong phản hồi và đã xuất hiện trong kết quả tool.
- Mô hình kết nối qua `openai` Python SDK bằng `CHAT_BASE_URL`, `CHAT_API_KEY`, `CHAT_MODEL`, hỗ trợ OpenAI-compatible Gemini/Groq. Client tạo lười; thiếu key chỉ tắt chat, backend/health vẫn hoạt động.
- Whitelist tool chỉ có `search_movies` (Movie), `get_showtimes` (Movie/Showtime tương lai), `get_price_rules` (quy tắc ghế từ `seats.py`), không `INSERT`/`UPDATE`/`DELETE`; không truy vấn bookings/users/comments trong lớp chatbot. Giới hạn 3 vòng công cụ, thời hạn tổng 30 giây, xử lý 503 an toàn.
- Quota trong bộ nhớ: 5 lần/phút và 50 lần/ngày cho mỗi user; reset khi restart, không chia sẻ nhiều worker. Chat history chỉ giữ trong React state. `ChatWidget` gắn vào App một lần; `real.js` và `mock.js` cùng API `chat.send(messages)`; không có thay đổi schema và không thêm thư viện frontend.


## T19 — Upload poster (13/10/2026)
- `POST /api/admin/posters` chỉ admin (`require_admin`), nhận JSON `{filename, data}` (base64 thuần), tối đa 2 MiB; phân loại JPG/PNG/WebP theo magic bytes; tên lưu `uuid4.hex`, không dùng filename do người gửi cung cấp.
- `UPLOAD_DIR` mặc định `backend/uploads` (đường dẫn tương đối từ `backend`), mount FastAPI StaticFiles `/uploads`. Ảnh trả URL `/uploads/posters/<32hex>.<ext>`; `backend/uploads/` ngoài Git.
- Validator phim giữ URL ngoài http(s), cho phép thêm đường dẫn poster nội bộ chặt chẽ; **chỉ router POST tạo phim** buộc có poster, PUT sửa phim cũ vẫn cho phép trống. Không đổi schema (`movies.poster_url` hiện có).
- Frontend lưu file base64 qua `api.admin.posters.upload`, ưu tiên upload thay vì link nếu đồng thời có cả hai; `Poster` ghép `API_URL` khi đường dẫn bắt đầu `/uploads/`. Mock dùng cùng JSON `{poster_url}`, trả data URL, giới hạn 500 KiB do localStorage. Hai ô màu poster vẫn tồn tại.
- Không xóa file khi sửa/xóa phim (file mồ côi được chấp nhận trong phạm vi khóa luận). Lưu trữ trên ổ đĩa không bền vững có thể mất ảnh khi môi trường triển khai reset.

## T22 — Chấm sao và bình luận ẩn danh (20/10/2026)

- `ratings(id, user_id, movie_id, stars, created_at, updated_at)`: UNIQUE(user_id, movie_id), CHECK stars BETWEEN 1 AND 5; FK phim có ON DELETE CASCADE. PUT dùng SQLite upsert nguyên tử; DELETE không có điểm vẫn 200.
- `MovieOut.rating_avg` (làm tròn một chữ số, 0 khi trống) và `rating_count` được tổng hợp từ ratings. Danh sách phim JOIN truy vấn GROUP BY một lần; chi tiết/phim lồng trong vé và suất dùng biểu thức SQL aggregate cùng SELECT, không truy vấn riêng cho từng phim.
- `GET /api/movies/{id}/my-rating` → `{stars: int|null}`; `PUT /api/movies/{id}/rating` nhận `{stars: 1..5}`; `DELETE /api/movies/{id}/rating` → `{stars, rating_avg, rating_count}`. Cần đăng nhập; ghi/xóa tối đa 20 lần/phút/người, POST bình luận kèm sao dùng chung bộ đếm. Coming soon không nhận ghi/xóa điểm hoặc bình luận (400 tiếng Việt).
- `comments.is_anonymous` mặc định false. POST bình luận nhận `{content, is_anonymous?, stars?}` và ghi sao vào cùng ratings trong transaction với bình luận. Public `CommentOut` chỉ hiện “Khán giả ẩn danh”, không chứa user_id/email; admin vẫn tên thật + cờ ẩn danh. `author_stars` là điểm hiện tại, null khi đã hủy. `can_delete` chỉ là boolean quyền của phiên đăng nhập, không chứa định danh tác giả; khách không token vẫn đọc được.
- `DELETE /api/comments/{id}` trả `{ok:true}` cho chủ bình luận, 404 cho ID không tồn tại hoặc không thuộc mình. Không xóa điểm khi xóa bình luận.
- API frontend real/mock cùng `ratings.mine/set/remove`, `comments.remove` và `comments.create(movieId, payload)`. Mock v5 tính điểm từ ratings; sáu khán giả mẫu riêng, lượt chấm `2 + movie_id % 5` và sao deterministic giống backend; admin/demo không có điểm mẫu. `StarRating` đầu trang lưu/hủy ngay; dãy trong form có draft riêng, mặc định điểm hiện tại. Chỉ POST bình luận mới lưu draft; bỏ chọn thì bỏ trường stars và giữ điểm cũ. Gửi thành công cập nhật điểm đầu trang và thống kê. Token 401 ở GET bình luận công khai được xem như khách, không đổi xác thực API ghi.
- Cột score cũ vẫn lưu nhưng không dùng hiển thị/xếp hạng người xem; hero theo rating_avg rồi rating_count, top_rated lọc >=4.0. Không đổi classifier/normalize/luật ghế. Reset schema do PO theo HUONG_DAN.

### T23 — Tổng quan kinh doanh và soát vé

- `GET /api/admin/dashboard?days=7|30|90`: require_admin, expire_holds trước
  thống kê; truy vấn SQL gộp số vé, doanh thu và ghế, không lặp từng vé.
  Sức chứa suất = len(ROWS) × COLS từ seats.py. Doanh thu/số vé/ghế bán
  theo bookings.created_at; lấp ghế trên các suất có start_time >= đầu khoảng (gồm suất sắp chiếu, không chặn trên); ratings và
  comments theo created_at. Khoảng ngày gồm hôm nay, nửa mở [00:00 đầu, 00:00 mai).
  Không có dữ liệu trả 0. Điểm sao là trung bình các lượt chấm trong khoảng;
  tiêu cực dùng human_label nếu đã duyệt, nếu chưa thì is_negative, gồm cả bình luận ẩn như T21.
- `GET/POST /api/admin/checkin/{code}`: require_admin. POST dùng một UPDATE
  có điều kiện status=paid AND checked_in_at IS NULL; rowcount quyết định thành công,
  chống soát hai lần kể cả đồng thời. Lưu bookings.checked_in_at và checked_in_by.
- BookingOut thêm checked_in_at; AdminBookingOut thêm checked_in_by_name.
  MyTickets truyền checked_in_at xuống TicketStub qua prop checkedInAt (không gọi API thêm).
- Real/mock cùng admin.dashboard, admin.checkin.get/confirm. Trang admin mới
  có ProtectedRoute adminOnly; biểu đồ SVG không dùng thư viện mới.
# T24 — khả năng đặt online

`GET /api/movies/{id}/showtimes` chỉ trả suất có `start_time > now + HOLD_CUTOFF_MINUTES`
(hằng số từ `booking_rules.py`). `GET /api/showtimes/{id}` bổ sung `bookable: bool`
theo cùng điều kiện, không đổi schema DB. Frontend khóa ghế và nút Tiếp tục khi
`bookable=false`; mock dùng cùng cutoff và thông báo phân biệt suất đã bắt đầu.


## T25 — Trailer và nội dung phim (24/10/2026)

- Movies thêm `trailer_url VARCHAR(500) NULL`, `synopsis TEXT NULL`; MovieIn/MovieOut có cả hai trường. Nội dung strip, tối đa 5000 ký tự; rỗng thành null. `description` tiếp tục là mô tả ngắn của hero.
- `POST /api/admin/trailers` cần require_admin, body thô MP4/WebM; không multipart/base64. Giới hạn 100 MiB, kiểm Content-Length trước khi đọc và đếm request.stream() khi ghi file tạm; mọi nhánh lỗi/ngắt kết nối đều dọn file tạm. Chữ ký quyết định đuôi UUID, không tin MIME để xác định định dạng. Lưu dưới UPLOAD_DIR/trailers, trả 201 `{trailer_url}`.
- `GET /uploads/trailers/{name}` đăng ký trước StaticFiles `/uploads`; bắt cả tên có slash rồi chỉ chấp nhận `[0-9a-f]{32}\.(mp4|webm)`. Stream khối 64 KiB; không Range trả 200, single byte range đóng/mở/suffix trả 206, range không hợp lệ hoặc ngoài file trả 416 với `Content-Range: bytes */size`. Có Accept-Ranges, Content-Length và MIME video đúng.
- Trailer chỉ nhận đường dẫn upload chuẩn hoặc YouTube http/https trên youtube.com/www/m/youtu.be; watch/shorts/embed được chuẩn hóa về `https://www.youtube.com/watch?v=ID`. Không nhận nguồn khác hay credentials/port tùy ý.
- Frontend gọi `api.admin.trailers.upload(File)`; real gửi raw body cùng token, mock kiểm chữ ký rồi trả blob URL (chỉ sống trong phiên). TrailerBanner chưa tạo video/iframe trước khi bấm; YouTube qua youtube-nocookie.com, có link mở ngoài. Nội dung nhiều đoạn đứng trước Lịch chiếu. File video ưu tiên hơn link nếu chọn cả hai; gỡ chỉ bỏ trường, không xóa file mồ côi.
- Hai movies.json giống byte, 21 synopsis hai đoạn, trailer_url null; schema thật do PO reset theo HUONG_DAN, không tự migrate.


### T27 — Điểm phim 1–10 và phân bố
- `ratings.stars` là số nguyên 1–10, strict tại RatingIn/CommentIn và CHECK tại SQLite. Điểm ngoài miền trả 422 tiếng Việt.
- PUT/DELETE `/api/movies/{id}/rating` và GET `/my-rating` cùng trả `stars`, `rating_avg` (1 chữ số), `rating_count`, `distribution` đủ khóa chuỗi 1..10. Distribution đếm từng mức; nhóm 9–10…1–2 được tính ở dialog.
- Seed real/mock dùng `6 + ((movie.id + index) % 5)`; mock nâng namespace dữ liệu lên v6 để không dùng điểm demo thang cũ. Dashboard giữ công thức trung bình.
- RatingDialog dùng native modal, lấy summary mới khi mở; draft chỉ lưu khi xác nhận. Hiệu ứng GSAP qua motion.js có điều kiện MOTION_OK, dọn hạt/tween khi đóng, unmount hoặc đổi reduced motion; auto-close xác nhận 1,2 giây.
- Schema cũ cần PO backup/checksum/integrity và reset theo HUONG_DAN mục T27. Không migrate/quy đổi hoặc thao tác DB thật trong implementation.

## T28 — Tổng quan tài khoản và trạng thái phim hiệu lực (26/10/2026)

- `GET /api/auth/me/summary`: cần bearer token như `/api/auth/me`; 401 dùng cùng thông báo tiếng Việt. Không đổi `UserOut`, `/me`, `/change-password`.
- Response `AccountSummary`: `member_since`; `stats` gồm `bookings`, `paid`, `watched`, `total_spent`, `comments`, `ratings`; `favorite_genre`; 3 `recent_comments` mới nhất; tối đa 5 `ratings` mới nhất. Mọi truy vấn giới hạn theo người gọi. Bình luận của chính chủ giữ nguyên nội dung, cờ `hidden`, `is_anonymous`, `effective_negative` (nhãn người duyệt ưu tiên).
- `bookings` loại expired/rejected; `paid` và chi tiêu chỉ tính paid; `watched` đếm checked_in_at khác null. Thể loại đếm theo phim của từng booking paid; hòa điểm chọn theo thứ tự chữ để real/mock ổn định.
- Frontend gọi `api.auth.meSummary()` ở cả real/mock, dùng lại `api.bookings.mine()` cho vé gần đây. Form đổi tên/mật khẩu giữ luồng T14; lỗi tải số liệu không chặn form.
- `taxonomy.effective_status(movie, today, sql=...)` là quy tắc chung backend: coming_soon có release_date <= hôm nay trả now_showing, các trạng thái khác giữ nguyên. Cùng quy tắc xây SQL CASE cho bộ lọc phim/chatbot và dùng trong MovieOut, quyền chấm điểm/bình luận qua ratings.require_rateable. Không UPDATE trạng thái DB.
- `MovieOut.status` là trạng thái hiệu lực; `stored_status` là trạng thái lưu để danh sách/form admin giải thích tự chuyển. Mock dùng `effectiveStatus` ở utils/taxonomy.js, không ghi đè trạng thái lưu khi đọc. Admin từ chối Sắp chiếu có ngày <= hôm nay với 422 tiếng Việt.
- T28 cho phép tạo phim không poster để dùng Poster màu theo AC-13; vẫn xác thực URL/file khi có ảnh. Không đổi schema DB, seed hay dữ liệu phim JSON.
- Thông tin liên hệ chỉ khai báo trong `CONTACT` (config.js), Footer dùng lại trên mọi trang.
## T29 — Hồ sơ và tài khoản (27/10/2026)

- Schema users thêm `birth_date DATE NULL`, `gender VARCHAR(20) NULL`, `avatar_url VARCHAR(500) NULL`. UserOut trả ba trường này và created_at; không trả password_hash.
- PATCH `/api/auth/me`: họ tên, ngày sinh 1900..hôm nay, giới tính male/female/unspecified/null; chỉ cập nhật trường gửi lên.
- POST `/api/auth/me/email`: `{new_email,current_password}`, dùng cùng limiter đăng nhập/đổi mật khẩu; email chữ thường, không gửi thư, token theo id vẫn dùng được.
- PUT `/api/auth/me/avatar`: `{filename,data}` base64; DELETE cùng đường dẫn; trả UserOut. Dùng chung validate_image của poster (magic bytes JPG/PNG/WebP, 2 MB), UUID dưới UPLOAD_DIR/avatars. Thay/gỡ xóa file cũ của chính chủ sau khi commit DB.
- GET `/api/auth/me/summary`: thêm spent_this_year từ vé paid tạo trong năm hiện tại; bình luận thêm human_label/is_negative/reviewed_at để giải thích kiểm duyệt. Giữ giới hạn T28: 3 bình luận, 5 điểm mới nhất.
- GET `/api/admin/me/summary` dùng require_admin: `todo{comments,pending_verify,showtimes_today}`, `work{reviewed_today,reviewed_total,overrides,checked_in_today}`, `recent_activity[{kind,id,at,label}]` tối đa 5. Công việc/hoạt động giới hạn theo admin hiện tại; todo là toàn rạp.
- booking_rules.age_allowed tính tuổi vào ngày suất chiếu; P/không khai/admin được qua. Frontend/mock dùng chung utils/account.js; API vẫn kiểm tra khi đặt vé.
- Ngưỡng hạng nằm tại config.js MEMBERSHIP. Khách có 4 thẻ nhớ URL hash; admin có việc cần làm và bảo mật. Mock DB v7; avatar lưu data URL trong localStorage; real/mock cùng khóa JSON.
- Không migration; PO sao lưu/kiểm tra/reset theo mục T29 trong HUONG_DAN.md.
