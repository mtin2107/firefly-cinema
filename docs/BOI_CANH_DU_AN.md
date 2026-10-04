# BỐI CẢNH DỰ ÁN FIREFLY CINEMA — TÀI LIỆU BÀN GIAO

> Tài liệu này tóm tắt toàn bộ những gì đã làm cùng Claude tính đến **03/10/2026**: quyết định thiết kế, kiến trúc mã nguồn, trạng thái mô hình PhoBERT, các quy ước bắt buộc và kế hoạch task T00–T15.
> Đặt file tại `docs/BOI_CANH_DU_AN.md` trong repo và đưa vào nguồn (project knowledge) của ChatGPT/Codex.

---

## 0. PROMPT MỞ ĐẦU (dán vào đầu cuộc trò chuyện với ChatGPT)

```
Bạn tham gia dự án khóa luận tốt nghiệp "Firefly Cinema" với vai trò NGƯỜI THỰC HIỆN (implementer).
Đọc kỹ docs/BOI_CANH_DU_AN.md trước khi làm bất cứ việc gì. Đó là nguồn sự thật về kiến trúc,
quy ước và kế hoạch.

Vai trò trong dự án:
- Tín (tôi): Product Owner. Giao task, chạy code trên máy (Windows, PowerShell), chạy notebook Colab, quyết định cuối cùng.
- ChatGPT/Codex (bạn): viết đặc tả task (docs/tasks/Txx.md) và viết code thực hiện từng task.
- Claude: reviewer độc lập. Chấm mỗi task theo PASS / PASS_WITH_TODO / FAIL dựa trên tiêu chí nghiệm thu.
  Claude không sửa code production.

Việc đầu tiên: từ mục 9 (Kế hoạch) và mục 10 (Mẫu đặc tả task), tạo các file docs/tasks/T00.md ... T15.md.
Sau đó chỉ làm MỘT task mỗi lần, theo đúng quy trình ở mục 11.
THƯ MỤC GỐC DUY NHẤT để cài đặt, chạy code và commit là C:\Projects\firefly-cinema.
Mọi hoạt động diễn ra ở C:\Projects\firefly-cinema. File lớn (model, dữ liệu, sao lưu, báo cáo Word) nằm trong repo nhưng ngoài Git. D:\KhoaLuan_PhimVe ngừng sử dụng từ 04/10/2026.
Khi không chắc một quyết định (đổi kiến trúc, đổi thư viện, đổi giao diện đã chốt), HỎI tôi trước, không tự quyết.
Trả lời tôi bằng tiếng Việt. Tên biến, hàm, API viết bằng tiếng Anh. Mọi chữ hiển thị trên giao diện viết bằng tiếng Việt.
```

---

## 1. Tổng quan đề tài

| Mục | Nội dung |
|---|---|
| Tên đề tài | Thiết kế và xây dựng website đặt vé xem phim trực tuyến tích hợp học sâu để phân loại bình luận tiêu cực |
| Mã đề tài | #67, ngành Khoa học dữ liệu, NTTU |
| Sinh viên | Lê Minh Tín |
| Tên sản phẩm | **Firefly Cinema** |
| Ý tưởng cốt lõi | Một website rạp phim bình thường, quen thuộc kiểu CGV/Galaxy. Điểm nổi bật là **PhoBERT phân loại bình luận tiêu cực** và **so sánh với các mô hình truyền thống** (Naive Bayes, Logistic Regression, SVM) |
| Thời gian | Hoàn thiện sản phẩm 05/10 – 01/11/2026, viết báo cáo 02/11 – 29/11/2026 |

---

## 2. Trạng thái hiện tại (đã hoàn thành)

| Hạng mục | Trạng thái | Mốc Git |
|---|---|---|
| Giao diện React đầy đủ luồng người dùng | Xong, đã chốt thiết kế | tag `giao-dien-v1` |
| Backend FastAPI + SQLite, nối với giao diện | Xong, chạy trên máy Tín | — |
| PhoBERT phần A (dữ liệu UIT-ViSFD) gắn vào backend | Xong, đã kiểm chứng trên web | tag `phobert-v1` |
| File khởi động một chạm `chay-firefly.bat` | Xong | — |
| Mô hình truyền thống, dữ liệu phim, trang quản trị phim/suất chiếu | **Chưa làm**, xem kế hoạch | — |

### Môi trường máy của Tín
- Windows, PowerShell (đã đặt `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`).
- Node.js v24.21, npm 11.19. Python **3.13.2**, Git 2.56.
- Repo ở `C:\Projects\firefly-cinema`, nhánh `master`.
- Backend dùng venv tại `backend\venv`; đã cài `torch==2.11.0` (bản CPU) và `transformers==5.18.0`.
- Model PhoBERT nằm ở `backend\models\phobert-binhluan\`. Thư mục này bị `.gitignore` loại ra.

### Cách chạy
- Bấm đúp `chay-firefly.bat` ở thư mục gốc: mở 2 cửa sổ (backend cổng 8000, frontend cổng 5173) rồi tự mở trình duyệt.
- Hoặc chạy tay:
  - Backend: `cd backend` → `venv\Scripts\Activate.ps1` → `uvicorn app.main:app --reload --port 8000`
  - Frontend: `cd frontend` → `npm run dev`
- Tài khoản mẫu: `demo@firefly.vn` / `123456` (người dùng), `admin@firefly.vn` / `admin123` (quản trị).
- Kiểm tra backend: http://localhost:8000/api/health phải trả `"classifier":"phobert"`. Swagger ở http://localhost:8000/docs.

### Nơi lưu trữ (đã chốt ngày 03/10/2026)

| Vị trí | Vai trò | Git |
|---|---|---|
| **`C:\Projects\firefly-cinema`** | **THƯ MỤC GỐC.** Toàn bộ mã nguồn (web, backend, `ml/` script + notebook + kết quả nhỏ), tài liệu `docs/`. Mọi lệnh cài đặt, chạy, commit đều làm ở đây | Có (nhánh `master`, tag `giao-dien-v1`, `phobert-v1`) |
| `C:\Projects\firefly-cinema\backend\models\phobert-binhluan\` | Bản model mà backend đang dùng | Không (`.gitignore`) |
| `ml\artifacts\` | Bản gốc model PhoBERT A (và model B, `*.joblib` sau này) | Không (gitignore) |
| `data\uit-visfd\` | Dữ liệu UIT-ViSFD đã xử lý (processed) | Không (gitignore CSV) |
| `data\phim\` | Dữ liệu bình luận phim cho T03 | Không (gitignore CSV) |
| `Bao_cao\` | Bản thảo báo cáo Word | Không (gitignore `*.docx`) |
| `backup\` | Sao lưu (T13) và code cũ đã ngừng dùng (`02_api_cu`) | Không (gitignore) |
| `D:\KhoaLuan_PhimVe\` | **Ngừng sử dụng từ 04/10/2026**, dữ liệu đã chép sang các thư mục trên | — |
| Google Drive `MyDrive/thesis_results/` | Model trên Colab, `firefly_phobert.zip` | — |

**Quy tắc đặt tên:** trong repo dùng tên theo chức năng (`ml`, `backend`, `frontend`, `data`, `docs`), không dùng tiền tố số như ổ D, vì `chay-firefly.bat` và mọi hướng dẫn đều trỏ tới `frontend`/`backend`. Thư mục `ml/`, `data/`, `docs/tasks/`, `docs/images/` đã được tạo sẵn (có `.gitkeep`).

**Những thứ từng ở ổ D (đã chép sang ổ C ngày 04/10/2026), cần xử lý trong T00:**
- `D:\KhoaLuan_PhimVe\01_training\thesis_project\`: mã train phần A dạng script (`src\prep.py`, `src\trai…`, `src\base…`, `src\comm…`, `src\erro…`), `README.md`, `processed\` (khoảng 23 MB, 6 file CSV), `results\`.
  - Chép `src\`, `README.md`, `results\` sang `C:\Projects\firefly-cinema\ml\` để đưa vào Git.
  - `processed\` đã chép sang `data\uit-visfd\processed\` (ngoài Git) và có trên Drive, chỉ ghi đường dẫn trong `ml\README.md`.
  - **Trước khi làm T01, kiểm tra file `src\base…`**. Nếu đã là mã mô hình truyền thống thì T01 chỉ hoàn thiện tiếp, không viết lại.
- `D:\KhoaLuan_PhimVe\02_api\api\`: API dự đoán cũ (`main.py`, `text_utils.py`, bản sao model). **Trùng chức năng với backend, ngừng dùng**, đã chép sang `backup\02_api_cu\` (bỏ venv).
  - Riêng `text_utils.py` nhiều khả năng là hàm chuẩn hóa gốc tạo ra `text_norm`. Phải đối chiếu với `normalize()` trong `backend/app/classifier.py`. Nếu khác nhau, dùng hàm gốc và đo lại F1.
- Model PhoBERT A đang có khoảng 4 bản sao (`01_training\thesis_results`, `02_api\api\model`, `thesis_results`, `06_backup`). Trên ổ C chỉ còn bản gốc `ml\artifacts\phobert_A_best\` và bản backend dùng.

---

## 3. Kiến trúc

```
firefly-cinema/
├── chay-firefly.bat            Khởi động một chạm (Windows)
├── HUONG_DAN.md / README.md    Hướng dẫn cài đặt, chạy, gắn model
├── .gitignore                  node_modules, dist, .env, venv, __pycache__, *.db, backend/models/,
│                               data/**/*.csv|xlsx, ml/**/*.safetensors|joblib|bin, ml/artifacts/,
│                               backup/, Bao_cao/*.docx, .idea/
├── ml/                         mã train (src/), notebooks/, results/ (file nhỏ), model_card_*.md, artifacts/ (model, ngoài Git)
├── data/                       README + hướng dẫn gán nhãn; uit-visfd/ và phim/ chứa CSV (ngoài Git)
├── docs/                       BOI_CANH_DU_AN.md, tasks/Txx.md, images/ (ảnh cho báo cáo)
├── frontend/                   React 18 + Vite 5 + react-router-dom 6, CSS thuần (không Tailwind)
│   ├── .env                    VITE_USE_MOCK=false, VITE_API_URL=http://localhost:8000
│   └── src/
│       ├── config.js           SITE_NAME="Firefly Cinema", USE_MOCK, API_URL, USE_HASH_ROUTER
│       ├── api/
│       │   ├── index.js        export api = USE_MOCK ? mockApi : realApi   ← GIAO DIỆN CHỈ IMPORT TỪ ĐÂY
│       │   ├── http.js         request(): fetch + Bearer token, tokenStore (localStorage "firefly_token"), ApiError
│       │   ├── real.js         Gọi backend thật
│       │   ├── mock.js         Dữ liệu giả cùng cấu trúc JSON (localStorage "firefly_mockdb_v2")
│       │   └── movies.json     BẢN SAO của backend/app/data/movies.json
│       ├── context/AuthContext.jsx   user, checking, login, register, logout
│       ├── components/         Header, Dropdown, SearchBox, Footer, Poster, PosterIntro, MovieCard, AgeBadge,
│       │                       SeatMap, TicketStub, CommentSection, ProtectedRoute, StateViews
│       ├── pages/              Home, Explore, MovieDetail, SeatSelection, Checkout, MyTickets,
│       │                       Login, Register, AdminComments, NotFound
│       ├── utils/              format.js, seats.js (luật ghế), taxonomy.js (menu lọc)
│       └── styles/global.css   Toàn bộ CSS, biến màu ở :root
└── backend/                    FastAPI 0.115, SQLAlchemy 2.0, SQLite, PyJWT (HS256, 24h), mật khẩu PBKDF2
    ├── .env                    xem mục 3.4
    ├── requirements.txt        fastapi, uvicorn, sqlalchemy, pyjwt, pydantic[email]
    ├── requirements-ml.txt     (cần cập nhật, xem mục 8)
    ├── models/phobert-binhluan/  model PhoBERT (không commit)
    └── app/
        ├── main.py             lifespan: create_all + seed; CORS; handler lỗi 422 → 1 câu tiếng Việt; /api/health
        ├── config.py           đọc backend/.env (không cần python-dotenv)
        ├── database.py, models.py, schemas.py, security.py, seats.py, seed.py
        ├── classifier.py       PhoBERT / bộ lọc từ khóa dự phòng + hàm normalize()
        ├── data/movies.json    21 phim hư cấu
        └── routers/            auth.py, movies.py, bookings.py, comments.py
```

### 3.1. Routes giao diện

| Đường dẫn | Trang | Quyền |
|---|---|---|
| `/` | Trang chủ: hero bảng hiệu + tab Đang chiếu/Sắp chiếu | Công khai |
| `/kham-pha?trang-thai=&the-loai=&quoc-gia=&nam=&chu-de=&q=` | Lọc và tìm kiếm phim | Công khai |
| `/phim/:id` (có `#lich-chieu`) | Chi tiết phim, lịch chiếu, bình luận | Công khai |
| `/dang-nhap`, `/dang-ky` | Đăng nhập, đăng ký | Công khai |
| `/dat-ve/:showtimeId` | Sơ đồ ghế | Đăng nhập |
| `/xac-nhan` | Xác nhận đặt vé (nhận state từ trang chọn ghế) | Đăng nhập |
| `/ve-cua-toi` | Vé đã đặt | Đăng nhập |
| `/quan-tri/binh-luan` | Kiểm duyệt bình luận | Admin |

### 3.2. API backend hiện có

| Phương thức | Đường dẫn | Quyền | Ghi chú |
|---|---|---|---|
| POST | /api/auth/register | — | Trả `{access_token, user}` |
| POST | /api/auth/login | — | Trả `{access_token, user}` |
| GET | /api/auth/me | user | |
| GET | /api/movies | — | Lọc: `status` (now_showing/coming_soon/ended), `genre`, `country`, `year`, `year_before`, `age_rating`, `format` (Phụ đề/Lồng tiếng), `collection` (hot_week/hot_month/top_comments/top_rated), `q` (tìm không dấu) |
| GET | /api/movies/{id} | — | |
| GET | /api/movies/{id}/showtimes | — | Chỉ các suất trong tương lai |
| GET | /api/showtimes/{id} | — | `{showtime, movie, booked_seats[]}` |
| POST | /api/bookings | user | `{showtime_id, seats[]}`; 409 nếu trùng ghế |
| GET | /api/bookings/me | user | |
| GET | /api/movies/{id}/comments | — | Kèm `is_negative`, `negative_score` |
| POST | /api/movies/{id}/comments | user | Model chấm điểm ngay khi tạo |
| GET | /api/admin/comments?label=negative\|normal | admin | Kèm `movie_title`, `model_name` |
| GET | /api/health | — | `{status, classifier, classifier_error}` |

Lỗi luôn trả dạng `{"detail": "<một câu tiếng Việt>"}` để giao diện hiển thị thẳng.

### 3.3. Cơ sở dữ liệu (SQLite `backend/firefly.db`)

- `users(id, full_name, email unique, password_hash, role user|admin, created_at)`
- `movies(id, title, genre "A, B", duration_min, age_rating P|T13|T16|T18, release_date "YYYY-MM-DD", status, director, cast, score, description, poster_bg, poster_fg, poster_url?, country, formats "Phụ đề, Lồng tiếng")`
- `showtimes(id, movie_id, start_time, room, price)`
- `bookings(id, user_id, showtime_id, total, created_at)`
- `booking_seats(id, booking_id, showtime_id, seat_code)` với **UNIQUE(showtime_id, seat_code)**: đảm bảo hai người không đặt trùng một ghế
- `comments(id, movie_id, user_id, content, is_negative, negative_score, model_name phobert|keyword, created_at)`

Seed (`seed.py`) chạy khi bảng phim trống: thêm 21 phim, 3 tài khoản (admin, demo, khách quầy), 12 bình luận mẫu, lượt đặt vé mẫu (`_SAMPLE_SALES`) phục vụ bảng xếp hạng phim hot. `_ensure_showtimes()` chạy mỗi lần khởi động, sinh suất chiếu cho 5 ngày tới.

### 3.4. Biến môi trường backend (`backend/.env`)

```
SECRET_KEY=doi-chuoi-bi-mat-nay
DATABASE_URL=sqlite:///./firefly.db
FRONTEND_ORIGIN=http://localhost:5173
MODEL_DIR=models/phobert-binhluan
NEGATIVE_LABEL_ID=1
USE_WORD_SEGMENT=false
USE_TEXT_NORM=true
NEGATIVE_THRESHOLD=0.5
```

---

## 4. Thiết kế giao diện đã chốt (KHÔNG tự ý thay đổi)

- **Màu**: nền đen `#000000`, bề mặt `#121212` / `#1c1c1c`, đường kẻ `#2e2e2e`, **vàng chủ đạo `#ffc72c`** (nút chính, ghế đang chọn, logo, tab đang chọn), **đỏ phụ `#d7263d`** (bình luận tiêu cực, lỗi, nhãn T18), chữ `#f3efe4`, chữ phụ `#a39e92`.
- **Font**: `Big Shoulders Display` (tiêu đề, viết hoa) + `Be Vietnam Pro` (nội dung). Cả hai đều hỗ trợ tiếng Việt.
- **Điểm nhấn duy nhất**: hero dạng bảng hiệu rạp, viền bóng đèn chấm chấm phát sáng. Logo là đốm sáng đom đóm nhấp nháy nhẹ. Các phần còn lại giữ tiết chế.
- **Poster** vẽ bằng CSS từ `poster_bg`/`poster_fg` (phim đều là phim hư cấu, tránh vấn đề bản quyền ảnh). Nếu phim có `poster_url` thì dùng ảnh.
- **Hiệu ứng PosterIntro**: bấm poster, tên phim, "Xem chi tiết" hoặc "Đặt vé" thì poster hiện trong khung bong bóng viền vàng, giữ 1,8 giây rồi mờ dần trong 0,6 giây. Truyền qua `state={{ intro: movie }}` của `<Link>`. Bấm bất kỳ đâu hoặc Esc để bỏ qua; tự tắt khi máy bật chế độ giảm chuyển động.
- **Header**: Đang chiếu, Sắp chiếu, Thể loại ▾ (23 mục, 3 cột), Quốc gia ▾, Năm phát hành ▾, Chủ đề ▾ (Phim hot trong tuần/tháng, Top bình luận, Đánh giá cao, Lồng tiếng, Phụ đề), kính lúp tìm kiếm, menu tài khoản (Vé của tôi, Kiểm duyệt bình luận, Đăng xuất). Dưới 1100px gom thành nút "Menu".
- **Văn phong**: tiếng Việt, câu ngắn, viết hoa chữ đầu câu. Nút ghi đúng hành động ("Đặt vé", "Gửi bình luận"). Thông báo lỗi nói rõ chuyện gì xảy ra và cách sửa, không xin lỗi.
- **Chất lượng tối thiểu**: responsive tới màn hình điện thoại, focus bàn phím nhìn thấy được, tôn trọng `prefers-reduced-motion`, mọi trang có đủ trạng thái loading / rỗng / lỗi (dùng `StateViews`).

---

## 5. Mô hình PhoBERT phần A (đã xong)

| Mục | Giá trị |
|---|---|
| Dữ liệu | UIT-ViSFD (bình luận **điện thoại**), đã xử lý ở Colab `/content/proj/processed/{train,dev,test}.csv` |
| Cột | `comment, n_star, label, asp_*, has_negative, overall, text_norm, text_raw, ...` |
| Bài toán A | Nhị phân `has_negative` (1 = bình luận có ý tiêu cực, kể cả chê một phần). Train 7.786 dòng: 4.302 nhãn 1 / 3.484 nhãn 0 |
| Đầu vào | Cột **`text_norm`**: chữ thường, tách dấu câu, viết đầy đủ từ viết tắt. **Không tách từ** (không có `_`) |
| Model | `RobertaForSequenceClassification` (PhoBERT-base), `num_labels=2`, `max_position_embeddings=258`, `max_length=256` |
| Nhãn | **0 = binh_thuong, 1 = tieu_cuc** (đã ghi `id2label`/`label2id` vào config của bản đóng gói) |
| Kết quả | F1 lớp tiêu cực trên test: **0,9178** (`text_norm`), **0,9180** (dùng `normalize()` của backend). Đảo nhãn chỉ được 0,096, đây là bằng chứng nhãn 1 là tiêu cực |
| Phiên bản thư viện | `transformers 5.18.0`, `torch 2.11.0` |
| Lưu trữ trên Drive | `MyDrive/thesis_results/phobert_A_best/` (bản gốc) và `MyDrive/thesis_results/firefly_phobert.zip` (542 MB, bản đóng gói cho backend) |
| Phân tích lỗi đã có | `/content/proj/results/error_analysis_taskA.csv` (nằm trong phiên Colab, **cần chép sang Drive ở T00**) |

**Tiền xử lý ở backend** (`app/classifier.py → normalize()`): NFC → chữ thường → rút gọn ký tự lặp từ 3 lần trở lên → tách dấu câu `.,!?;:()[]"“”…` bằng khoảng trắng → thay từ viết tắt theo bảng `_ABBR` (ko/k/kh/hok → không, đc/dc → được, j → gì, vs → với, ...). Hàm này **phải giống hệt** hàm dùng trong mọi notebook đánh giá về sau.

**Hạn chế đã phát hiện (lệch miền):** model học từ bình luận điện thoại nên bắt kém các cách chê đặc trưng của phim.
- "Phim dài lê thê, xem mà mệt" → **0,01** (đoán sai thành bình thường).
- "Phim dài lê thê, nửa đầu buồn ngủ thật sự" → 0,944 (đúng, nhiều khả năng nhờ cụm "buồn ngủ").
- "Ko hay như quảng cáo, hơi thất vọng" → 0,99. "Diễn viên đóng đạt, đáng đồng tiền" → 0,01. "Cũng được, không có gì đặc biệt" → 0,04.

Đây là lý do có T03, T08, T09 trong kế hoạch.

---

## 6. Quy ước BẮT BUỘC khi viết code

1. **Giao diện chỉ gọi API qua `src/api/index.js`.** Thêm endpoint mới thì phải thêm vào **cả `real.js` lẫn `mock.js`**, trả về cùng cấu trúc JSON. Chế độ mock phải luôn chạy được (bản xem trước và demo không cần backend dựa vào nó).
2. **Luật ghế nằm ở 2 nơi phải khớp nhau**: `frontend/src/utils/seats.js` và `backend/app/seats.py` (hàng A–H, 12 ghế mỗi hàng, F–H là VIP +20.000 đ, tối đa 8 ghế mỗi lần đặt).
3. **Dữ liệu phim có 2 bản sao**: `backend/app/data/movies.json` và `frontend/src/api/movies.json`. Sửa một bản thì sửa luôn bản kia.
4. **Nhãn trong `taxonomy.js` phải trùng đúng chữ** với dữ liệu phim (thể loại, quốc gia, định dạng).
5. **Chưa có migration**: backend dùng `create_all`. Thêm hay đổi cột thì người dùng phải xóa `firefly.db`. Mỗi task đổi schema phải ghi rõ điều này trong mô tả và trong `HUONG_DAN.md`. Có thể đề xuất Alembic, nhưng phải hỏi Tín trước.
6. **Lỗi backend** luôn trả `HTTPException(status, "câu tiếng Việt")`. Lỗi 422 đã được chuyển thành một câu.
7. **Endpoint admin** dùng dependency `require_admin`. Tài khoản thường gọi vào phải nhận 403.
8. **Tiền xử lý cho model** phải giống lúc train. Không sửa `normalize()` khi chưa đánh giá lại F1 trên tập test.
9. **Không commit**: `.env`, `firefly.db`, `backend/models/`, `venv/`, `node_modules/`, file model hay dữ liệu lớn.
10. **Lệnh hướng dẫn** viết cho Windows PowerShell. Đường dẫn không dấu, không khoảng trắng.
11. **Không thêm thư viện mới** khi chưa hỏi, trừ những thứ task đã ghi rõ (ví dụ scikit-learn, joblib cho T01/T07; pytest cho T11).
12. **Mỗi task một nhánh** `task/Txx-ten-ngan`, commit dạng `[Txx] mô tả`. Không sửa file ngoài phạm vi task.

---

## 7. Checklist hồi quy (chạy sau mọi task web)

1. Trang chủ hiện phim, hiệu ứng poster chạy khi bấm "Xem chi tiết" và "Đặt vé".
2. Menu Thể loại / Chủ đề và ô tìm kiếm (thử "meo muop") ra kết quả đúng.
3. Đăng ký tài khoản mới; chưa đăng nhập mà bấm giờ chiếu thì bị đưa sang trang đăng nhập, đăng nhập xong quay lại đúng trang.
4. Đặt vé 2 ghế; mở lại suất đó thấy 2 ghế đã xám; "Vé của tôi" có vé mới.
5. Bình luận "Ko hay như quảng cáo, hơi thất vọng" bị ẩn; admin thấy điểm khoảng 0,99 trong trang kiểm duyệt.
6. `/api/health` báo `classifier: phobert`.
7. Chạy với `VITE_USE_MOCK=true` vẫn dùng được (nếu task có đụng tới lớp API).

---

## 8. Nợ kỹ thuật đã biết

- `backend/requirements-ml.txt` chưa cập nhật (vẫn ghi `underthesea`, chưa ghim phiên bản). Cần sửa thành torch 2.11.0 (bản CPU) và transformers 5.18.0, kèm ghi chú cài torch qua `--index-url https://download.pytorch.org/whl/cpu`. Làm trong T00.
- `HUONG_DAN.md` phần 4.2 còn nhắc cài `underthesea`. Cần sửa cùng lúc.
- Chưa có migration (xem quy ước 5) và chưa có test tự động (sẽ làm ở T11).
- `_SAMPLE_SALES` bị lặp ở `seed.py` và `mock.js`.
- `/api/admin/comments` chưa phân trang.
- Cột `comments.model_name` chỉ phân biệt `phobert`/`keyword`, chưa có phiên bản model (sẽ làm ở T10).
- JWT lưu trong localStorage: chấp nhận được ở phạm vi khóa luận, nên ghi vào phần hạn chế của báo cáo.

---

## 9. Kế hoạch hoàn thiện sản phẩm (05/10 – 01/11/2026)

### 9.1. Tổng quan

| ID | Task | Loại | Tuần | Phụ thuộc | Ước lượng |
|---|---|---|---|---|---|
| T00 | Gom mã từ ổ D, lưu trữ dữ liệu, thẻ mô hình phần A | ML | 1 | — | 0,5–1 ngày |
| T01 | Mô hình truyền thống (NB, LR, SVM) | ML | 1 | T00 | 1,5 ngày |
| T02 | Bảng so sánh PhoBERT với mô hình truyền thống | ML | 1 | T01 | 1 ngày |
| T03 | Bộ dữ liệu bình luận phim | Dữ liệu | 1–2 | — | 3–4 buổi rải rác |
| T04 | Quản lý phim (admin) | Web | 2 | — | 1 ngày |
| T05 | Quản lý suất chiếu (admin) | Web | 2 | T04 | 1 ngày |
| T06 | Kiểm duyệt có người duyệt | Web | 2 | — | 1 ngày |
| T07 | Đa mô hình và trang So sánh mô hình | Web + ML | 2 | T01 | 1,5 ngày |
| T08 | Đo lệch miền điện thoại → phim | ML | 3 | T02, T03 | 0,5 ngày |
| T09 | Train PhoBERT phần B trên dữ liệu phim | ML | 3 | T08 | 1,5 ngày |
| T10 | Gắn model B vào web | Web | 3 | T07, T09 | 0,5 ngày |
| T11 | Kiểm thử tự động và sửa lỗi | Web | 4 | T04–T10 | 1,5 ngày |
| T12 | Dữ liệu demo và kịch bản bảo vệ | Web | 4 | T10 | 1 ngày |
| T13 | Chốt v1.0 và sao lưu | Tất cả | 4 | T11, T12 | 0,5 ngày |
| T14 | *(tùy chọn)* Hủy vé, đổi mật khẩu | Web | nếu dư | — | 1 ngày |
| T15 | *(tùy chọn)* Thử nghiệm có tách từ | ML | nếu dư | T09 | 1 ngày |

Hai chuỗi việc chính: `T00 → T01 → T02` và `T03 → T08 → T09 → T10`. **T03 bắt đầu ngay ngày đầu.**
Nếu trễ tiến độ, cắt theo thứ tự T14 → T15 → rút gọn T05. **Không cắt** T01–T03 và T07–T10 vì đó là cốt lõi đề tài.

### 9.2. Chi tiết

**T00. Gom mã từ ổ D, lưu trữ dữ liệu, thẻ mô hình phần A** (repo + Colab)
- Mục tiêu: không mất dữ liệu khi phiên Colab hết hạn; cố định cách chia dữ liệu cho mọi mô hình về sau.
- Đầu ra:
  - Gom mã train phần A từ `D:\KhoaLuan_PhimVe\01_training\thesis_project\` vào `C:\Projects\firefly-cinema\ml\` (xem mục "Nơi lưu trữ"); API cũ đã ở `backup\02_api_cu`; đối chiếu `text_utils.py` với `normalize()`; ghi SHA256 hai bản model A trên ổ C.
  - Drive `thesis/data/processed/{train,dev,test}.csv` và `error_analysis_taskA.csv`; notebook phần A lưu trên Drive.
  - Repo thêm `ml/README.md` (sơ đồ nơi lưu dữ liệu, model, notebook) và `ml/model_card_A.md` (nội dung mục 5).
  - Cập nhật `requirements-ml.txt` và `HUONG_DAN.md` (nợ kỹ thuật ở mục 8).
- Nghiệm thu: runtime Colab mới nạp được dữ liệu từ Drive; số dòng train/dev/test trong thẻ mô hình khớp với file; `ml/` có trong Git; kết quả đối chiếu `text_utils.py` với `normalize()` được ghi vào `model_card_A.md`; đã ghi rõ `src\base…` đã làm tới đâu so với T01.

**T01. Mô hình truyền thống** (Colab)
- Mục tiêu: TF-IDF (n-gram từ 1–2, thử thêm n-gram ký tự 2–5) kết hợp MultinomialNB, LogisticRegression, LinearSVC. Chọn siêu tham số trên **dev**, không đụng tới test. Đầu vào là `text_norm`, nhãn `has_negative`.
- Đầu ra: `ml/results/baselines.csv`, `svm_A.joblib` (Pipeline gồm vectorizer + model, lưu trên Drive), notebook.
- Nghiệm thu: đúng cách chia dữ liệu như phần A; có precision, recall, F1 lớp tiêu cực, macro-F1, thời gian dự đoán mỗi câu (ms); seed cố định nên chạy lại ra cùng số.

**T02. So sánh PhoBERT với mô hình truyền thống** (Colab)
- Mục tiêu: đo lại PhoBERT A bằng cùng bộ chỉ số, có thời gian chạy CPU; vẽ ma trận nhầm lẫn từng mô hình; phân tích 20 câu sai mỗi mô hình theo nhóm nguyên nhân.
- Đầu ra: `ml/results/comparison_A.csv`, hình ma trận nhầm lẫn, `ml/results/error_analysis.md`.
- Nghiệm thu: ít nhất 4 mô hình trên cùng bộ chỉ số; có nhận xét về đánh đổi giữa độ chính xác, tốc độ và dung lượng.

**T03. Bộ dữ liệu bình luận phim** (làm song song tuần 1–2)
- Mục tiêu:
  - Viết hướng dẫn gán nhãn thống nhất với `has_negative`: chê phim, chê rạp hay chê dịch vụ đều là tiêu cực; chê một phần cũng là tiêu cực; châm biếm cũng là tiêu cực.
  - Thu thủ công 400–600 bình luận ở quy mô nhỏ, bỏ tên người viết và mọi thông tin cá nhân.
  - Nhờ thêm một người gán nhãn lại 100 câu để đo Cohen's kappa.
- Đầu ra: `movie_comments_v1.csv` (`id, text, label, source_type, note`), `ml/labeling_guideline.md`, chia train/test 70/30 với seed cố định.
- Nghiệm thu: ít nhất 400 câu, không trùng lặp, kappa từ 0,6 trở lên (thấp hơn thì sửa hướng dẫn và gán lại).

**T04. Quản lý phim** (web)
- Mục tiêu: API `POST/PUT/DELETE /api/admin/movies`; trang admin gồm danh sách và form nhập (nhập màu poster hoặc `poster_url`).
- Nghiệm thu:
  - Tài khoản thường nhận 403.
  - Kiểm tra dữ liệu: tên không rỗng, thời lượng lớn hơn 0, ngày hợp lệ, `age_rating` thuộc P/T13/T16/T18, thể loại thuộc `taxonomy`.
  - Phim đã có vé không xóa được, chỉ chuyển sang `ended`.
  - Phim mới hiện ngay trong menu lọc.
  - Mock cũng hỗ trợ đủ; qua checklist hồi quy.

**T05. Quản lý suất chiếu** (web)
- Mục tiêu: CRUD suất chiếu; chặn trùng phòng khi chồng giờ, tính theo thời lượng phim cộng 15 phút dọn phòng.
- Nghiệm thu: hai suất chồng giờ cùng phòng bị chặn (409); suất đã có vé không sửa hay xóa được, có thông báo rõ lý do.

**T06. Kiểm duyệt có người duyệt** (web, **đổi schema**)
- Mục tiêu:
  - Bảng `comments` thêm `human_label` (nullable), `reviewed_by`, `reviewed_at`, `hidden`.
  - Admin có thể xác nhận, đổi nhãn, hoặc ẩn bình luận.
  - Trang phim ưu tiên nhãn của người duyệt nếu có.
  - Thêm API xuất CSV bình luận đã duyệt (`text`, `text_norm`, `label`).
- Nghiệm thu: **giữ nguyên `is_negative`/`negative_score` gốc của model**; trang admin có thống kê model đúng/sai so với người duyệt; file CSV dùng được cho T03/T09.

**T07. Đa mô hình và trang So sánh mô hình** (web + ML)
- Mục tiêu:
  - Backend nạp được nhiều model (PhoBERT, SVM từ joblib); `ACTIVE_MODEL` trong `.env` chọn model chấm bình luận.
  - API `POST /api/admin/predict {text}` trả `[{model, label, score, ms}]`.
  - Trang admin "So sánh mô hình": gõ một câu, xem các model chấm điểm cạnh nhau.
  - `/api/health` liệt kê các model đang có.
- Nghiệm thu: thiếu file SVM thì web vẫn chạy, chỉ bỏ qua model đó; kết quả cho cùng một câu khớp notebook; SVM dùng cùng `normalize()`.

**T08. Đo lệch miền** (Colab)
- Mục tiêu: chạy PhoBERT A và các mô hình truyền thống trên tập test phim của T03.
- Đầu ra: bảng F1 trên dữ liệu điện thoại so với dữ liệu phim; 20 câu sai tiêu biểu.
- Nghiệm thu: dùng đúng hàm `normalize()` của backend.

**T09. Train PhoBERT phần B** (Colab)
- Mục tiêu:
  - Train tiếp từ PhoBERT A trên tập train phim; có thể trộn thêm một phần dữ liệu điện thoại để model không quên kiến thức cũ.
  - Train lại các mô hình truyền thống trên dữ liệu phim.
  - So sánh trên cả hai tập test.
- Đầu ra: `firefly_phobert_B.zip` (có `id2label`), `comparison_B.csv`, `ml/model_card_B.md`.
- Nghiệm thu: test phim chỉ dùng cho lần đánh giá cuối; B tốt hơn A trên test phim; ghi lại mức giảm (nếu có) trên test điện thoại.

**T10. Gắn model B** (web)
- Mục tiêu: đổi `MODEL_DIR`; thêm `MODEL_VERSION` vào `/api/health` và vào từng bình luận.
- Nghiệm thu: bộ 10 câu kiểm thử cố định (có câu "lê thê") cho kết quả khớp notebook; giữ model A để quay lại nếu cần.

**T11. Kiểm thử và sửa lỗi** (web)
- Mục tiêu: viết `pytest` + TestClient cho đăng ký/đăng nhập, đặt trùng ghế, phân quyền admin, chấm điểm bình luận, các chức năng quản trị; kiểm thử tay giao diện theo checklist.
- Nghiệm thu: toàn bộ `pytest` chạy đạt (với model giả lập, không cần file PhoBERT); các lỗi đã sửa ghi vào `CHANGELOG.md`.

**T12. Demo** (web)
- Mục tiêu: dữ liệu demo sạch và script đặt lại dữ liệu; kịch bản 5–7 phút: khách đặt vé → bình luận tiêu cực bị ẩn → admin duyệt, sửa nhãn → so sánh mô hình → số liệu.
- Nghiệm thu: chạy trọn kịch bản 2 lần liên tiếp không lỗi, bắt đầu từ lúc máy vừa khởi động.

**T13. Chốt v1.0**
- Mục tiêu: gắn tag `v1.0`; sao lưu lên Drive model A, model B, SVM, dữ liệu, notebook; hoàn thiện README; gom ảnh chụp cho báo cáo.
- Nghiệm thu: clone repo ra thư mục mới, làm theo `HUONG_DAN.md` và chạy được.

**T14 (tùy chọn)**: hủy vé trước giờ chiếu ít nhất 2 tiếng; đổi họ tên và mật khẩu.
**T15 (tùy chọn)**: train lại có tách từ (underthesea hoặc VnCoreNLP) để so sánh với bản không tách.

### 9.3. Gắn với các chương báo cáo (02/11 – 29/11)

- **Phân tích thiết kế**: lấy từ T04–T07 (kèm sơ đồ ở mục 3).
- **Thực nghiệm**: lấy từ T01, T02, T08, T09.
- **Triển khai và kết quả**: lấy từ T10–T12.
- **Hạn chế và hướng phát triển**: lệch miền, không tách từ, JWT trong localStorage, chưa có migration.

---

## 10. Mẫu đặc tả task (`docs/tasks/Txx.md`)

```markdown
# Txx — <Tên task>

## Bối cảnh
<Vì sao cần task này, liên quan mục nào trong BOI_CANH_DU_AN.md>

## Phạm vi
- Làm: ...
- KHÔNG làm: ...

## Thiết kế
- Backend: model/schema/endpoint thay đổi (đường dẫn, request, response, mã lỗi)
- Frontend: trang/component mới, thay đổi ở real.js + mock.js
- Dữ liệu/ML: notebook, file đầu vào/đầu ra, đường dẫn Drive

## Đổi schema?
Có/Không. Nếu có: các bước người dùng phải làm (xóa firefly.db...)

## File dự kiến thay đổi
- ...

## Tiêu chí nghiệm thu
- [ ] ...
- [ ] Qua checklist hồi quy (mục 7) — nếu là task web

## Cách kiểm thử (lệnh PowerShell / ô Colab)
...

## Rủi ro / câu hỏi mở
...
```

---

## 11. Quy trình mỗi task

> **Từ 03/10/2026, quy trình chính thức nằm ở `docs/AGENT_RULES.md`** (trạng thái task, gate, tên report, prompt). Mục dưới đây giữ lại để tham khảo; khi khác nhau thì `AGENT_RULES.md` thắng.

1. Tín tạo nhánh: `git checkout -b task/Txx-ten-ngan`.
2. ChatGPT/Codex đọc `docs/tasks/Txx.md`, thực hiện, rồi báo cáo theo mẫu:

```
## Báo cáo Txx
- Tóm tắt thay đổi:
- File đã sửa/thêm:
- Đổi schema: Có/Không (+ hướng dẫn)
- Bằng chứng kiểm thử: lệnh đã chạy + kết quả / ảnh chụp
- Tiêu chí nghiệm thu: [x]/[ ] từng mục
- Việc còn tồn đọng / ngoài phạm vi:
```

3. Tín gửi Claude: đặc tả task, báo cáo, diff (`git diff master...HEAD`) và bằng chứng kiểm thử.
4. Claude trả kết quả: **PASS** (merge được), **PASS_WITH_TODO** (merge được, kèm danh sách việc cần làm sau) hoặc **FAIL** (sửa theo danh sách rồi review lại). Áp dụng theo `CODEX_CLAUDE_REVIEW_WORKFLOW_POLICY.md` của dự án nếu có.
5. PASS thì: `git checkout master` → `git merge task/Txx-...` → `git tag` theo mốc (`ml-baselines`, `admin-v1`, `phobert-B`, `v1.0`).

---

## 12. Câu hỏi còn mở (Tín quyết định)

- Nguồn thu bình luận phim cho T03 và ai là người gán nhãn thứ hai.
- Có dùng Alembic cho migration (từ T06) hay chấp nhận xóa `firefly.db` mỗi lần đổi schema.
- Model mặc định sau T10: PhoBERT B, hay để admin chọn trên trang quản trị.
- Có triển khai lên mạng (deploy) để demo hay chỉ chạy trên máy khi bảo vệ. Lưu ý model nặng 540 MB, khó chạy trên các gói hosting miễn phí.
