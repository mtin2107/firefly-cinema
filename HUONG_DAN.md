# Firefly Cinema — Hướng dẫn chạy và kết nối từ đầu đến cuối

Bộ mã gồm hai phần chạy riêng:

```
firefly-cinema/
├── frontend/   Giao diện React (Vite) — chạy ở http://localhost:5173
│   ├── src/api/        Lớp gọi API: mock.js (dữ liệu giả) và real.js (backend thật)
│   ├── src/pages/      Các trang: trang chủ, lọc phim, chi tiết phim, đặt vé và quản trị
│   ├── src/components/ Thành phần dùng chung: poster, sơ đồ ghế, bình luận, cuống vé...
│   └── src/styles/global.css   Toàn bộ màu sắc và kiểu chữ (sửa biến trong :root)
└── backend/    API FastAPI — chạy ở http://localhost:8000
    ├── app/routers/    Các nhóm endpoint: auth, movies, bookings, comments, admin_movies
    ├── app/classifier.py   Nơi PhoBERT chấm điểm bình luận
    └── app/data/movies.json  Dữ liệu phim mẫu
```

Thứ tự làm: **Phần 1** chạy giao diện với dữ liệu giả, **Phần 2** chạy backend, **Phần 3** nối hai bên, **Phần 4** gắn PhoBERT.

---

## Phần 0. Cài công cụ (làm một lần)

1. **Node.js 20 LTS** trở lên: tải ở nodejs.org.
2. **Python 3.10, 3.11 hoặc 3.12**: tải ở python.org. Trên Windows nhớ tick *Add Python to PATH*.
3. **VS Code** để mở thư mục `firefly-cinema`.

Kiểm tra trong terminal:

```bash
node -v      # v20.x hoặc cao hơn
npm -v
python --version   # macOS/Linux có thể là python3
```

---

## Phần 1. Chạy giao diện với dữ liệu giả

Ở bước này chưa cần backend. Mọi dữ liệu (phim, suất chiếu, tài khoản, vé, bình luận) nằm trong `src/api/mock.js` và được lưu trong trình duyệt.

```bash
cd frontend
cp .env.example .env        # Windows (cmd): copy .env.example .env
npm install
npm run dev
```

Mở http://localhost:5173. Góc phải header có nhãn đỏ **"Dữ liệu mẫu"**, nghĩa là đang chạy mock.

Tài khoản mẫu:

| Vai trò | Email | Mật khẩu |
|---|---|---|
| Người dùng | demo@firefly.vn | 123456 |
| Quản trị | admin@firefly.vn | admin123 |

Thử đủ luồng: chọn phim → chọn ngày, giờ → chọn ghế → Tiếp tục → Đặt vé → xem ở *Vé của tôi*. Viết bình luận có chữ "chán" hoặc "thất vọng" để thấy bình luận bị ẩn. Đăng nhập admin để xem trang *Kiểm duyệt bình luận*.

Đăng nhập bằng tài khoản quản trị rồi mở **Quản lý phim** trong menu tài khoản để thêm, sửa hoặc xóa phim. Phim thêm trong chế độ mock được lưu ở Local Storage nên vẫn còn sau khi tải lại trang.

> Muốn xóa sạch dữ liệu mock: mở DevTools (F12) → Application → Local Storage → xóa khóa `firefly_mockdb_v2`.

---

## Phần 2. Chạy backend FastAPI

Mở **terminal thứ hai** (để terminal của frontend vẫn chạy).

```bash
cd backend
python -m venv venv
```

Kích hoạt môi trường ảo:

```bash
# Windows (PowerShell)
venv\Scripts\Activate.ps1
# Windows (cmd)
venv\Scripts\activate.bat
# macOS / Linux
source venv/bin/activate
```

Đầu dòng lệnh sẽ hiện `(venv)`. Tiếp tục:

```bash
pip install -r requirements.txt
cp .env.example .env        # Windows (cmd): copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Lần chạy đầu tiên backend tự tạo file `firefly.db` (SQLite), tạo bảng và thêm dữ liệu mẫu (21 phim gồm đang chiếu, sắp chiếu và đã chiếu, lượt đặt vé mẫu để xếp hạng phim hot, suất chiếu 5 ngày tới, 2 tài khoản như bảng trên, vài bình luận).

Kiểm tra:

- http://localhost:8000/api/health → `{"status":"ok","classifier":"keyword",...}`
- http://localhost:8000/docs → trang Swagger, bấm thử từng API được. Ảnh chụp trang này dùng tốt cho chương thiết kế API trong báo cáo.

### 2.1. Cập nhật database cho T06 (chỉ làm một lần)

T06 thêm cột kiểm duyệt vào bảng `comments`. Dự án không dùng Alembic, vì vậy database cũ phải được tạo lại. Việc này làm mất dữ liệu đang có; chỉ PO thực hiện sau khi đã xác minh backup.

1. Tắt backend bằng `Ctrl + C`. Từ thư mục gốc dự án, xác nhận không còn tiến trình nghe cổng 8000:
   ```powershell
   Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
   ```
   Lệnh không được trả về dòng nào.
2. Xác nhận bản backup T06 đã được ghi trong report, có checksum SHA-256 và `PRAGMA integrity_check` trả `ok`.
3. Chỉ khi hai bước trên đạt, PO xóa đúng database thật bằng lệnh:
   ```powershell
   Remove-Item -LiteralPath "C:\Projects\firefly-cinema\backend\firefly.db"
   ```
4. Khởi động backend để `create_all` tạo schema và seed lại dữ liệu:
   ```powershell
   Set-Location "C:\Projects\firefly-cinema\backend"
   .\venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
   ```
5. Trong terminal PowerShell khác, kiểm tra health và schema/dữ liệu mới:
   ```powershell
   Invoke-RestMethod "http://localhost:8000/api/health"
   Set-Location "C:\Projects\firefly-cinema"
   .\backend\venv\Scripts\python.exe -c "import sqlite3; c=sqlite3.connect(r'backend/firefly.db'); print(c.execute('pragma integrity_check').fetchone()); print([r[1] for r in c.execute('pragma table_info(comments)')]); print(c.execute('select count(*) from comments').fetchone())"
   ```
   Kết quả phải có `ok`; danh sách cột phải có `human_label`, `reviewed_by`, `reviewed_at`, `hidden`; số bình luận seed phải lớn hơn 0.

---

## Phần 3. Nối giao diện với backend

1. Mở `frontend/.env`, đổi:
   ```
   VITE_USE_MOCK=false
   VITE_API_URL=http://localhost:8000
   ```
2. Ở terminal frontend bấm `Ctrl + C` rồi chạy lại `npm run dev`. Vite chỉ đọc `.env` lúc khởi động nên **bắt buộc chạy lại**.
3. Tải lại trang. Nhãn "Dữ liệu mẫu" biến mất, nghĩa là giao diện đang gọi backend thật.

Danh sách kiểm tra sau khi nối:

- [ ] Trang chủ hiện 9 phim đang chiếu, 4 phim sắp chiếu
- [ ] Tìm "meo muop" (không dấu) ra phim Mèo Mướp Đi Lạc
- [ ] Đặt vé vài lần cho một phim, phim đó leo hạng trong "Phim hot trong tuần"
- [ ] Menu Thể loại / Quốc gia / Năm phát hành / Chủ đề mở ra và lọc đúng phim
- [ ] Đăng ký tài khoản mới được, đăng ký trùng email báo lỗi
- [ ] Chưa đăng nhập mà bấm giờ chiếu thì bị chuyển sang trang đăng nhập, đăng nhập xong quay lại đúng trang
- [ ] Đặt vé xong, ghế đó hiện màu xám khi mở lại cùng suất chiếu
- [ ] Mở hai trình duyệt, cùng chọn một ghế: người bấm Đặt vé sau nhận thông báo ghế vừa có người đặt
- [ ] Bình luận tiêu cực bị ẩn, trang quản trị hiện đúng điểm
- [ ] Tắt backend, tải lại trang: giao diện báo "Không kết nối được máy chủ" thay vì trắng trang

Mọi chỗ gọi API nằm trong `frontend/src/api/real.js`. Giao diện chỉ dùng `api` từ `src/api/index.js`, nên mock và backend thật trả về cùng cấu trúc JSON và không phải sửa trang nào khi chuyển.

---

## Phần 4. Gắn model PhoBERT đã train trên Colab

Khi chưa có model, backend dùng bộ lọc từ khóa tạm (`classifier: "keyword"`). Gắn model không cần sửa code, chỉ cấu hình.

### 4.1. Lưu model trên Colab

Ở cuối notebook train (sau khi đánh giá xong):

```python
save_dir = "/content/drive/MyDrive/khoaluan/phobert-binhluan"
model.save_pretrained(save_dir)        # hoặc trainer.save_model(save_dir)
tokenizer.save_pretrained(save_dir)
print(model.config.id2label)           # ghi lại: nhãn nào là "tiêu cực"
```

Thư mục phải có tối thiểu: `config.json`, `model.safetensors` (hoặc `pytorch_model.bin`), `vocab.txt`, `bpe.codes`, `tokenizer_config.json`.

### 4.2. Đưa model vào backend

1. Tải cả thư mục từ Google Drive về, đặt thành `backend/models/phobert-binhluan/`.
2. Cài thư viện ML đã ghim phiên bản (trong venv, PowerShell):
   ```powershell
   pip install torch==2.11.0 --index-url https://download.pytorch.org/whl/cpu
   pip install transformers==5.18.0
   ```
3. Sửa `backend/.env`:
   ```
    MODEL_DIR=models/phobert-binhluan
    NEGATIVE_LABEL_ID=1
    USE_WORD_SEGMENT=false
    USE_TEXT_NORM=true
    ```
    - `NEGATIVE_LABEL_ID`: chỉ số của nhãn tiêu cực trong `id2label` bạn in ở 4.1. Ví dụ `{0: "binh_thuong", 1: "tieu_cuc"}` thì để `1`. Model 3 lớp cũng dùng được, chỉ cần trỏ đúng lớp tiêu cực.
    - Model A dùng cột `text_norm`: bật `USE_TEXT_NORM` và để `USE_WORD_SEGMENT=false`. Không tách từ vì dữ liệu train của model A không có dấu gạch dưới nối từ.
4. Chạy lại backend (`Ctrl + C`, rồi `uvicorn app.main:app --reload --port 8000`).
5. Mở http://localhost:8000/api/health, phải thấy `"classifier":"phobert"`. Nếu vẫn là `keyword`, xem `classifier_error` để biết lỗi.

### 4.4. Nạp các mô hình T01 và chọn model chấm bình luận

Artifact mặc định nằm ngoài Git tại `ml/artifacts/baselines/`. Cài đúng phiên bản đã tạo artifact rồi thêm cấu hình vào `backend/.env`:

```powershell
backend\venv\Scripts\python -m pip install -r backend\requirements-ml.txt
```

```env
ACTIVE_MODEL=phobert
SKLEARN_MODELS=svm:../ml/artifacts/baselines/svm_A.joblib,lr:../ml/artifacts/baselines/lr_A.joblib,nb:../ml/artifacts/baselines/nb_A.joblib
```

Khởi động lại backend và kiểm tra `/api/health`: mỗi model có `loaded` và `error`, còn `active_model` là model thực sự dùng. Nếu `ACTIVE_MODEL` không nạp được, backend tự dùng PhoBERT rồi keyword. Trang admin `/quan-tri/so-sanh-mo-hinh` chỉ so sánh model, không thay đổi `ACTIVE_MODEL`.

### 4.3. Chấm lại dữ liệu mẫu bằng PhoBERT

Các bình luận mẫu được chấm lúc tạo database. Muốn chấm lại bằng PhoBERT: tắt backend, xóa file `backend/firefly.db`, chạy lại. Cột `model_name` trong bảng `comments` ghi rõ mỗi bình luận được chấm bởi `phobert` hay `keyword`, dùng khi viết phần thực nghiệm.

Ngưỡng ẩn bình luận chỉnh bằng `NEGATIVE_THRESHOLD` (mặc định 0.5).

---

## Phần 5. Lỗi thường gặp

| Hiện tượng | Nguyên nhân và cách sửa |
|---|---|
| Giao diện báo "Không kết nối được máy chủ" | Backend chưa chạy, hoặc `VITE_API_URL` sai cổng. Kiểm tra http://localhost:8000/api/health |
| Console trình duyệt báo lỗi CORS | Frontend không chạy ở cổng 5173. Sửa `FRONTEND_ORIGIN` trong `backend/.env` cho đúng địa chỉ, chạy lại backend |
| Sửa `.env` mà không thấy thay đổi | Phải tắt và chạy lại `npm run dev` hoặc `uvicorn` |
| `uvicorn` / `pip` không nhận lệnh | Chưa kích hoạt venv (không thấy `(venv)` đầu dòng) |
| PowerShell chặn `Activate.ps1` | Chạy `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` một lần, hoặc dùng cmd với `activate.bat` |
| `Address already in use` | Cổng đang bị chiếm, tắt terminal cũ hoặc đổi `--port 8001` (nhớ sửa `VITE_API_URL`) |
| Bị đăng xuất sau một ngày | Token hết hạn sau 24 giờ (`TOKEN_EXPIRE_HOURS` trong `app/config.py`) |
| Sửa `movies.json` mà web không đổi | Dữ liệu mẫu chỉ nạp khi database trống. Xóa `firefly.db` rồi chạy lại |
| Lỗi `no such column` sau khi cập nhật code | Bảng trong database cũ thiếu cột mới. Xóa `firefly.db` rồi chạy lại để tạo bảng mới |

---

## Phụ lục. Danh sách API

| Phương thức | Đường dẫn | Cần đăng nhập | Chức năng |
|---|---|---|---|
| POST | /api/auth/register | | Đăng ký, trả token |
| POST | /api/auth/login | | Đăng nhập, trả token |
| GET | /api/auth/me | ✔ | Thông tin tài khoản hiện tại |
| GET | /api/movies | | Danh sách phim. Lọc bằng `status` (`now_showing` / `coming_soon` / `ended`), `genre`, `country`, `year`, `year_before`, `age_rating`, `format` (`Phụ đề` / `Lồng tiếng`), `collection` (`hot_week` / `hot_month` / `top_comments` / `top_rated`), `q` (tìm theo tên, không cần dấu) |
| GET | /api/movies/{id} | | Chi tiết phim |
| GET | /api/movies/{id}/showtimes | | Suất chiếu sắp tới của phim |
| GET | /api/showtimes/{id} | | Suất chiếu + phim + danh sách ghế đã đặt |
| POST | /api/bookings | ✔ | Đặt vé `{showtime_id, seats}` |
| GET | /api/bookings/me | ✔ | Vé của tôi |
| GET | /api/movies/{id}/comments | | Bình luận không bị admin ẩn; kèm nhãn model, `effective_negative`, `reviewed` |
| POST | /api/movies/{id}/comments | ✔ | Viết bình luận, PhoBERT chấm điểm ngay |
| POST | /api/admin/predict | Admin | So sánh nhãn, điểm và thời gian của các model đã nạp |
| GET | /api/admin/comments | ✔ admin | Danh sách `{items,total}`; lọc `label`, `reviewed`; phân trang `page`, `page_size` tối đa 100 |
| PATCH | /api/admin/comments/{id} | ✔ admin | `confirm`, `relabel`, `hide`, `unhide`; relabel nhận `label` 0 hoặc 1 |
| GET | /api/admin/comments/stats | ✔ admin | Thống kê reviewed/agree/disagree/accuracy và TP/FP/TN/FN |
| GET | /api/admin/comments/export.csv | ✔ admin | CSV UTF-8 BOM gồm `text,text_norm,label`, chỉ lấy bình luận đã duyệt |
| GET | /api/admin/movies | ✔ admin | Danh sách phim dành cho quản trị |
| POST | /api/admin/movies | ✔ admin | Thêm phim |
| PUT | /api/admin/movies/{id} | ✔ admin | Cập nhật phim |
| DELETE | /api/admin/movies/{id} | ✔ admin | Xóa phim chưa có vé |
| GET | /api/health | | Trạng thái backend và model đang dùng |

Sơ đồ ghế: hàng A–H, mỗi hàng 12 ghế, hàng F–H là VIP (+20.000 đ). Quy tắc này nằm ở **hai nơi phải giống nhau**: `frontend/src/utils/seats.js` và `backend/app/seats.py`.

## Chỗ hay sửa

- Tên rạp: `frontend/src/config.js` (`SITE_NAME`)
- Màu: `frontend/src/styles/global.css`, các biến trong `:root`
- Danh mục menu (thể loại, quốc gia, năm, chủ đề): `frontend/src/utils/taxonomy.js`. Cách tính các bộ sưu tập hot / top bình luận: hàm `_ranking` trong `backend/app/routers/movies.py`. Chữ trong danh mục phải trùng đúng chữ trong dữ liệu phim
- Phim mẫu: `backend/app/data/movies.json` (giữ bản sao ở `frontend/src/api/movies.json` cho chế độ mock)
- Ảnh poster thật: thêm trường `poster_url` cho phim, component `Poster` sẽ tự dùng ảnh thay cho poster vẽ bằng CSS
