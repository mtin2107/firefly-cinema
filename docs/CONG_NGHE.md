# Công nghệ sử dụng — Firefly Cinema

> Chốt ngày 03/10/2026. Cập nhật file này mỗi khi thêm hoặc đổi thư viện.
> Phiên bản chính xác xem trong `frontend/package.json`, `backend/requirements.txt` và `backend/requirements-ml.txt`.

---

## 1. Sơ đồ hoạt động

```
Trình duyệt ──► React (cổng 5173) ──HTTP/JSON + token JWT──► FastAPI (cổng 8000)
                                                               │
                                       ┌───────────────────────┼─────────────────────┐
                                       ▼                       ▼                     ▼
                              SQLAlchemy → SQLite      PhoBERT (PyTorch)      Xác thực JWT
                              (firefly.db)             chấm điểm bình luận
```

Luồng xử lý một bình luận:
1. Giao diện React gọi `POST /api/movies/{id}/comments`.
2. FastAPI kiểm tra token đăng nhập.
3. Câu bình luận được chuẩn hóa bằng `normalize()` (chữ thường, tách dấu câu, viết đầy đủ từ viết tắt).
4. PhoBERT chấm điểm tiêu cực từ 0 đến 1.
5. Bình luận được lưu vào SQLite kèm điểm và tên model.
6. Giao diện ẩn bình luận nếu điểm từ 0,5 trở lên.

---

## 2. Giao diện (frontend)

| Thành phần | Công nghệ | Phiên bản | Vai trò |
|---|---|---|---|
| Thư viện giao diện | **React** | 18.3 | Xây giao diện theo dạng component (Header, SeatMap, CommentSection...) |
| Công cụ build | **Vite** | 5.4 | Chạy server phát triển ở cổng 5173, tự tải lại khi sửa code |
| Điều hướng trang | **React Router** | 6.26 | Chuyển trang không tải lại (`/phim/:id`, `/dat-ve/:id`...), chặn trang cần đăng nhập |
| Giao diện, màu sắc | **CSS thuần** | — | Một file `global.css`, màu khai báo bằng biến CSS, không dùng thư viện UI |
| Font | **Google Fonts** | — | Big Shoulders Display và Be Vietnam Pro, cả hai hỗ trợ tiếng Việt |
| Gọi API | **Fetch API** có sẵn của trình duyệt | — | Không cần cài thêm thư viện như axios |

Giao diện chỉ phụ thuộc 3 thư viện (`react`, `react-dom`, `react-router-dom`), nên nhẹ và dễ giải thích.

Lớp API có hai chế độ, chọn bằng `VITE_USE_MOCK` trong `frontend/.env`:
- `real.js`: gọi backend thật.
- `mock.js`: dùng dữ liệu giả trong trình duyệt, chạy được khi chưa có backend, phục vụ bản xem trước và demo.

---

## 3. Máy chủ (backend)

| Thành phần | Công nghệ | Phiên bản | Vai trò |
|---|---|---|---|
| Ngôn ngữ | **Python** | 3.13 | Cùng ngôn ngữ với phần train model |
| Framework API | **FastAPI** | 0.115 | Xây REST API, tự sinh tài liệu Swagger ở `/docs` |
| Server chạy API | **Uvicorn** | 0.30 | Chạy FastAPI ở cổng 8000 |
| ORM | **SQLAlchemy** | 2.0 | Làm việc với database qua lớp Python thay vì viết SQL tay |
| Kiểm tra dữ liệu | **Pydantic** (kèm email-validator) | 2.9 | Kiểm tra dữ liệu gửi lên (email hợp lệ, mật khẩu đủ 6 ký tự...) |
| Đăng nhập | **PyJWT** | 2.9 | Tạo và kiểm tra token đăng nhập (JWT HS256, hết hạn sau 24 giờ) |
| Mã hóa mật khẩu | **PBKDF2-SHA256** (thư viện chuẩn `hashlib`) | — | Băm mật khẩu kèm salt ngẫu nhiên, 200.000 vòng lặp |
| CORS | `CORSMiddleware` của FastAPI | — | Cho phép giao diện ở cổng 5173 gọi API ở cổng 8000 |

---

## 4. Cơ sở dữ liệu

- **Hệ quản trị:** **SQLite**. Toàn bộ dữ liệu nằm trong một file `backend/firefly.db`, không cần cài server database riêng, hợp với việc chạy demo trên máy cá nhân.
- **6 bảng:**

| Bảng | Nội dung |
|---|---|
| `users` | Tài khoản, vai trò `user` hoặc `admin` |
| `movies` | Thông tin phim, thể loại, quốc gia, định dạng, trạng thái chiếu |
| `showtimes` | Suất chiếu: phim, giờ, phòng, giá |
| `bookings` | Lượt đặt vé: người đặt, suất chiếu, tổng tiền |
| `booking_seats` | Từng ghế của mỗi lượt đặt |
| `comments` | Bình luận kèm `is_negative`, `negative_score`, `model_name` |

- **Ràng buộc quan trọng:** `UNIQUE(showtime_id, seat_code)` trên bảng `booking_seats`. Database tự chặn hai người đặt cùng một ghế, kể cả khi bấm đặt cùng lúc.
- **Dữ liệu mẫu:** `seed.py` tự thêm 21 phim, 3 tài khoản, bình luận và lượt đặt vé mẫu khi database trống; mỗi lần khởi động tự sinh suất chiếu cho 5 ngày tới.
- **Dễ chuyển hệ khác:** đổi sang PostgreSQL hoặc MySQL chỉ cần sửa `DATABASE_URL` trong `backend/.env` và cài driver tương ứng, code không phải sửa, nhờ SQLAlchemy.
- **Hạn chế:** chưa có migration. Khi đổi cấu trúc bảng phải xóa `firefly.db` để tạo lại.

---

## 5. Mô hình học sâu

| Thành phần | Công nghệ | Vai trò |
|---|---|---|
| Mô hình | **PhoBERT-base** (VinAI), `RobertaForSequenceClassification`, 2 lớp | Phân loại bình luận: 0 = bình thường, 1 = tiêu cực |
| Thư viện | **Transformers** 5.18 (Hugging Face) | Nạp model và tokenizer |
| Tính toán | **PyTorch** 2.11 | Bản GPU khi train trên Colab, bản CPU khi chạy trên máy |
| Dữ liệu train | **UIT-ViSFD** (bình luận điện thoại) | Bài toán A: nhãn `has_negative` |
| Nơi train | **Google Colab** (GPU T4) | Máy cá nhân không đủ mạnh để train PhoBERT |
| Kết quả | F1 lớp tiêu cực **0,918** trên tập test | Đầu vào chuẩn hóa, không tách từ |

Cấu hình trong `backend/.env`: `MODEL_DIR=models/phobert-binhluan`, `NEGATIVE_LABEL_ID=1`, `USE_WORD_SEGMENT=false`, `USE_TEXT_NORM=true`, `NEGATIVE_THRESHOLD=0.5`.

**Dự kiến thêm theo kế hoạch:**

| Thư viện | Task | Dùng để |
|---|---|---|
| pytest | T11 | Kiểm thử tự động backend |

## 5a. Mô hình truyền thống

| Thành phần | Phiên bản | Vai trò |
|---|---:|---|
| scikit-learn | 1.7.2 | TF-IDF word/character, MultinomialNB, LogisticRegression và LinearSVC |
| joblib | 1.5.2 | Lưu và nạp toàn bộ pipeline vectorizer + classifier |

T01 dùng `text_norm` và `has_negative` trên đúng split UIT-ViSFD của T00. Siêu tham số chỉ được chọn trên dev; test chỉ đánh giá các cấu hình cuối.

---

## 6. Công cụ làm việc

| Công cụ | Dùng để |
|---|---|
| **VS Code** | Viết và đọc code |
| **Git** | Quản lý phiên bản, đánh dấu mốc (`giao-dien-v1`, `phobert-v1`) |
| **PowerShell** | Chạy lệnh trên Windows |
| **Node.js 24 / npm 11** | Cài thư viện và chạy giao diện |
| **venv / pip** | Môi trường ảo và cài thư viện Python cho backend |
| **Swagger UI** | Thử API trên trình duyệt: http://localhost:8000/docs |
| **chay-firefly.bat** | Khởi động backend, giao diện và trình duyệt bằng một lần bấm đúp |
| **Google Colab + Google Drive** | Train model, lưu model và dữ liệu |
| **ChatGPT / Codex** | Viết đặc tả task và viết code |
| **Claude** | Review độc lập từng task (PASS / PASS_WITH_TODO / FAIL) |

---

## 7. Lý do lựa chọn (dùng cho báo cáo)

- **FastAPI thay vì .NET:** PhoBERT chạy bằng Python, nên FastAPI nạp model trực tiếp trong cùng một server. Với .NET sẽ phải chuyển model sang ONNX và viết lại bước tách từ, tokenizer bằng C#, hoặc dựng thêm một server Python riêng.
- **React + Vite thay vì React Native:** đề tài là *website*. React Native dùng để làm ứng dụng điện thoại.
- **SQLite:** gọn, không cần cài đặt, đủ cho quy mô khóa luận. Nhờ SQLAlchemy, có thể chuyển sang PostgreSQL khi triển khai thật.
- **CSS thuần:** kiểm soát hoàn toàn thiết kế (nền đen, vàng chủ đạo, đỏ phụ) và giảm số thư viện phụ thuộc.
- **Poster vẽ bằng CSS, phim hư cấu:** tránh vấn đề bản quyền hình ảnh.
