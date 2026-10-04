# ARCHITECTURE — Firefly Cinema

> Hợp đồng kỹ thuật mà mọi task phải giữ. Mô tả chi tiết cây thư mục, routes, API, schema xem `BOI_CANH_DU_AN.md` mục 3.
> Task nào đổi một mục dưới đây phải cập nhật file này trong cùng nhánh và ghi vào report.
> Cập nhật: 03/10/2026 (trạng thái sau tag `phobert-v1`).

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
                                                                    ├─ routers/ auth · movies · bookings · comments
                                                                    ├─ security.py (JWT HS256 24h, PBKDF2, require_admin)
                                                                    ├─ seats.py (luật ghế)
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
│       ├── pages\
│       │   ├── Home, Explore, MovieDetail, SeatSelection, Checkout, MyTickets,
│       │   │   Login, Register, NotFound, AdminComments
│       │   ├── AdminMovies.jsx        [T04]  /quan-tri/phim
│       │   ├── AdminShowtimes.jsx     [T05]  /quan-tri/suat-chieu
│       │   ├── AdminModelCompare.jsx  [T07]  /quan-tri/so-sanh-mo-hinh
│       │   └── Account.jsx            [T14]  /tai-khoan
│       ├── utils\                 format.js, seats.js, taxonomy.js
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
│           ├── admin_movies.py        [T04]
│           ├── admin_showtimes.py     [T05]
│           └── admin_predict.py       [T07]
│
├── ml\                            ── HỌC MÁY (mã train, notebook, kết quả nhỏ)
│   ├── README.md                  [T00] bản đồ dữ liệu / model / notebook
│   ├── README_goc.md              [T00] README cũ từ ổ D
│   ├── model_card_A.md            [T00]
│   ├── model_card_B.md            [T09]
│   ├── labeling_guideline.md      [T03]
│   ├── test_sentences.json        [T10]
│   ├── requirements-ml-train.txt  [T01]
│   ├── src\
│   │   ├── (mã cũ từ ổ D)             [T00] prep, train, base…, comm…, erro…
│   │   ├── baselines.py               [T01]
│   │   ├── eval_utils.py              [T02] hàm tính chỉ số dùng chung
│   │   └── prepare_movie_data.py      [T03]
│   ├── notebooks\                 T01_baselines, T02_comparison, T08_domain_shift,
│   │                              T09_phobert_B, T15_word_segment (.ipynb)
│   └── results\
│       ├── baselines.csv [T01], comparison_A.csv [T02], domain_shift.csv [T08],
│       │   comparison_B.csv [T09], word_segment.csv [T15]
│       ├── error_analysis.md [T02], domain_shift_errors.md [T08], movie_data_stats.md [T03]
│       └── figures\*.png
│
├── data\                          ── DỮ LIỆU PHIM: chỉ README, CSV để ở ổ D
│   └── README.md                  [T03]
│
├── docs\                          ── TÀI LIỆU DỰ ÁN (xem docs/README.md)
│   ├── tasks\T00.md … T15.md
│   ├── images\                    ảnh cho báo cáo [T02, T08, T13]
│   ├── KICH_BAN_DEMO.md           [T12]
│   └── SAO_LUU.md                 [T13]
│
└── reports\YYYY-MM-DD\            ── BÁO CÁO Codex / Claude / PO theo từng task
```

Ngoài repo (không có Git):

```
D:\KhoaLuan_PhimVe\
├── 01_training\thesis_project\processed\   dữ liệu UIT-ViSFD đã xử lý (giữ nguyên)
├── 04_data_phim\                           movie_comments_v1.csv, train/test [T03]
├── 05_baocao\                              bản Word báo cáo
├── 06_backup\                              02_api_cu [T00], v1.0 [T13]
└── thesis_results\                         model A gốc, phobert_B [T09], baselines\*.joblib [T01]
Google Drive: MyDrive/thesis/data/…, MyDrive/thesis_results/…, MyDrive/thesis_backup_v1/ [T13]
```

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
- Chưa có migration (`create_all`). Task đổi schema phải ghi "Đổi schema: Có" và hướng dẫn xóa `firefly.db` trong report và `HUONG_DAN.md` (trừ khi Q2 chốt dùng Alembic).

### 2.6. Mô hình
- `normalize()` trong `backend/app/classifier.py` là hàm tiền xử lý chuẩn. Notebook đánh giá mọi model phải dùng đúng hàm này.
- Không sửa `normalize()` khi chưa đo lại F1 trên test và ghi vào model card.
- Nhãn `1 = tieu_cuc`, ngưỡng mặc định `NEGATIVE_THRESHOLD=0.5`.
- Thiếu file model ⇒ web vẫn chạy (fallback keyword hoặc bỏ qua model đó), `/api/health` báo lỗi rõ.

### 2.7. Bí mật và file lớn
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
