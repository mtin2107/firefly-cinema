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

### Chạy kiểm thử

Bộ kiểm thử dùng SQLite tạm và classifier giả lập. Nó không đọc hoặc ghi `backend/firefly.db`, không cần thư mục `backend/models/`, `torch` hay file PhoBERT.

```powershell
Set-Location "C:\Projects\firefly-cinema\backend"
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\venv\Scripts\python.exe -m pytest -q
```

Mỗi test nhận database riêng trong thư mục tạm. Nếu máy có sẵn model hoặc thư viện ML, cấu hình test vẫn ép đường dẫn model sang vị trí không tồn tại và dùng classifier giả để kết quả không phụ thuộc môi trường cá nhân.

### 2.1. Cập nhật database cho T06/T10

> **DRAFT — GATE 2 NOT AUTHORIZED — DO NOT EXECUTE**

Dự án không dùng Alembic và `create_all` không tự thêm cột vào database cũ. Q2 lịch sử vẫn là `NO ALEMBIC / BACKUP_BEFORE_RESET`. Riêng T10, `PO-DECISION-T10-REALDB-A1-GATE1-20261010` đã phê duyệt **Gate 1** để chuẩn bị phương án A1 bảo toàn dữ liệu: manual ALTER bổ sung duy nhất `comments.model_version VARCHAR(100) NULL`. Gate 1 không cho phép chạy ALTER. Mọi thao tác ghi database thật phải chờ quyết định **Gate 2** riêng của PO.

Hai phương án được phân biệt như sau:

- **A1 — manual ALTER bảo toàn dữ liệu:** ngoại lệ chỉ dành cho T10, không dùng Alembic và không reset database. Technical dry-run đã PASS; Gate 2 chưa được authorize.
- **A2 — backup rồi reset:** phương án Q2 lịch sử, vẫn dùng cho trường hợp được PO chọn riêng. Reset + seed có thể làm mất dữ liệu người dùng, vé và bình luận cũ.

#### A1 — Giai đoạn 1: Pre-execution gate

Chỉ bắt đầu sau khi có quyết định Gate 2 riêng, ghi rõ thao tác, thời điểm, người thực hiện và rollback.

1. Xác minh repo `C:\Projects\firefly-cinema`, đúng branch/HEAD được PO duyệt và không có thay đổi chưa rõ nguồn gốc.
2. Xác minh runtime `DATABASE_URL` resolve đúng `C:\Projects\firefly-cinema\backend\firefly.db`. Nếu trỏ nơi khác: **HARD STOP**.
3. Dừng backend và mọi process có thể ghi DB. Lệnh sau không được trả listener:

   ```powershell
   Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
   ```

4. Mở DB ở `mode=ro`, `query_only=ON`; xác minh bảng `comments` đúng schema kỳ vọng và chưa có `model_version`. Nếu cột đã có hoặc schema khác: **HARD STOP**, không tự sửa tiếp.
5. Xác minh SHA-256, `integrity_check`, `foreign_key_check`, row counts và fingerprints hiện thời. Snapshot preflight lúc 14:50 ngày 10/10/2026 chỉ là evidence lịch sử, không thay fresh gate.

#### A1 — Giai đoạn 2: Fresh consistent backup

1. Tạo thư mục timestamp mới dưới `backup/T10_2026-10-10/`; không ghi đè bất kỳ backup nào.
2. Dùng SQLite Online Backup API với nguồn mở read-only; không sao chép thô khi có writer/WAL chưa được kiểm soát.
3. Ghi source path, backup path, thời gian, kích thước và SHA-256.
4. Trên source và backup, xác minh `integrity_check=ok`, `foreign_key_check` không có dòng, schema/PK/FK/index/constraint, counts và row fingerprints khớp.
5. Dựng một restore clone riêng từ backup và lặp lại validation. Nếu snapshot không phục hồi được hoặc logic không khớp: **HARD STOP**.

Lệnh tạo backup phải được PO duyệt ở Gate 2. Mẫu dự thảo, chưa chạy:

```powershell
$executionStamp = Get-Date -Format "yyyyMMdd_HHmmss"
$freshBackupDir = "C:\Projects\firefly-cinema\backup\T10_2026-10-10\gate2_$executionStamp"
New-Item -ItemType Directory -Path $freshBackupDir
$env:T10_GATE2_BACKUP = Join-Path $freshBackupDir "firefly_online_backup.db"
@'
import os, sqlite3
source = "file:C:/Projects/firefly-cinema/backend/firefly.db?mode=ro"
target = os.environ["T10_GATE2_BACKUP"]
src = sqlite3.connect(source, uri=True)
src.execute("PRAGMA query_only=ON")
dst = sqlite3.connect(target)
src.backup(dst)
dst.commit()
dst.close()
src.close()
'@ | C:\Projects\firefly-cinema\backend\venv\Scripts\python.exe -
Remove-Item Env:T10_GATE2_BACKUP
```

#### A1 — Giai đoạn 3: Schema change

> **DỰ THẢO CHO PO REVIEW — KHÔNG CHẠY KHI CHƯA CÓ GATE 2**

Chỉ một thay đổi được phép: `ALTER TABLE comments ADD COLUMN model_version VARCHAR(100);`. Không DROP, DELETE, reset, seed hoặc sửa cột khác.

```powershell
$env:T10_GATE2_REAL_DB = "C:\Projects\firefly-cinema\backend\firefly.db"
@'
import os, sqlite3
path = os.environ["T10_GATE2_REAL_DB"]
conn = sqlite3.connect(path)
try:
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("BEGIN IMMEDIATE")
    columns = [row[1] for row in conn.execute("PRAGMA table_info(comments)")]
    if "model_version" in columns:
        raise RuntimeError("model_version already exists; stop without ALTER")
    conn.execute("ALTER TABLE comments ADD COLUMN model_version VARCHAR(100)")
    conn.commit()
except Exception:
    conn.rollback()
    raise
finally:
    conn.close()
'@ | C:\Projects\firefly-cinema\backend\venv\Scripts\python.exe -
Remove-Item Env:T10_GATE2_REAL_DB
```

Nếu transaction lỗi: rollback và dừng. Không tự chuyển sang A2.

#### A1 — Giai đoạn 4: Post-schema verification

Trước khi startup backend, mở DB read-only và bắt buộc xác minh:

- `model_version` có kiểu `VARCHAR(100)`, nullable, default `NULL`.
- Mọi comment cũ có `model_version IS NULL`; ID, content, `model_name`, nhãn và điểm không đổi.
- Counts và fingerprints toàn bộ cột/bảng gốc khớp snapshot fresh.
- PK/FK/index/check constraint không đổi.
- `integrity_check=ok`; `foreign_key_check` không có lỗi.

Bất kỳ sai lệch nào cũng là **HARD STOP**; không startup backend.

#### A1 — Giai đoạn 5: Runtime smoke verification

Chỉ sau Gate 2 và Giai đoạn 4 PASS:

1. Khởi động backend trên database thật.
2. Kiểm tra `/api/health`, `/api/movies`, GET/POST comments và admin comments.
3. Xác minh comment mới lưu đúng `model_name`/`model_version`, comment cũ `model_version=NULL` vẫn hiển thị, admin security giữ 401/403/200 và không có HTTP 500 `no such column`.
4. Chạy lại integrity/FK và đối chiếu dữ liệu gốc.

`_ensure_showtimes` chạy khi startup và có thể bổ sung suất chiếu. Phải lưu snapshot/fingerprint trước startup, ghi riêng các dòng mới hợp lệ và chứng minh không có dòng gốc bị sửa hoặc mất.

#### A1 — Giai đoạn 6: Rollback

1. Dừng backend ngay; bảo toàn database gặp lỗi dưới tên quarantine để điều tra.
2. Không ghi đè backup gốc. Restore snapshot sang file mới và xác minh integrity, FK, counts, fingerprints.
3. Chỉ thay thế database thật khi PO authorize restore riêng và mọi validation PASS.
4. Rollback về snapshot cũ cũng đưa schema trở lại trạng thái chưa có `model_version`; T10 quay lại `PENDING_PO_DB_ACTION`.

#### A2 — Backup trước khi reset (quy trình Q2 lịch sử)

A2 chỉ được chạy khi PO chọn và authorize riêng. Dừng backend, tạo fresh backup đã xác minh như trên, rồi PO mới được xóa đúng `backend/firefly.db` và startup để `create_all` + seed tạo DB mới. Phải chấp nhận rõ rằng reset không tự bảo toàn tài khoản, vé, ghế và bình luận cũ; không import dữ liệu cũ nếu chưa có kế hoạch mapping/transaction/PK-FK validation riêng. Codex không tự xóa/reset database thật.

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

1. Giữ model A tại `backend/models/phobert-binhluan/`; đặt checkpoint B đã xác minh tại `backend/models/phobert-binhluan-B/`.
2. Cài thư viện ML đã ghim phiên bản (trong venv, PowerShell):
   ```powershell
   pip install torch==2.11.0 --index-url https://download.pytorch.org/whl/cpu
   pip install transformers==5.18.0
   ```
3. Sửa `backend/.env`:
   ```
    MODEL_DIR=models/phobert-binhluan
    MODEL_DIR_B=models/phobert-binhluan-B
    MODEL_VERSION_A=A-backend
    MODEL_VERSION_B=phobert-B-2026-10-09
    NEGATIVE_LABEL_ID=1
    USE_WORD_SEGMENT=false
    USE_TEXT_NORM=true
    ```
    - `NEGATIVE_LABEL_ID`: chỉ số của nhãn tiêu cực trong `id2label` bạn in ở 4.1. Ví dụ `{0: "binh_thuong", 1: "tieu_cuc"}` thì để `1`. Model 3 lớp cũng dùng được, chỉ cần trỏ đúng lớp tiêu cực.
    - Model A dùng cột `text_norm`: bật `USE_TEXT_NORM` và để `USE_WORD_SEGMENT=false`. Không tách từ vì dữ liệu train của model A không có dấu gạch dưới nối từ.
4. Chạy lại backend (`Ctrl + C`, rồi `uvicorn app.main:app --reload --port 8000`).
5. Mở http://localhost:8000/api/health, phải thấy `"classifier":"phobert_b"` và `"active_version":"phobert-B-2026-10-09"`. Nếu runtime fallback, xem `classifier_error` để biết lỗi.

### 4.4. Nạp các mô hình T01 và chọn model chấm bình luận

Artifact mặc định nằm ngoài Git tại `ml/artifacts/baselines/`. Cài đúng phiên bản đã tạo artifact rồi thêm cấu hình vào `backend/.env`:

```powershell
backend\venv\Scripts\python -m pip install -r backend\requirements-ml.txt
```

```env
ACTIVE_MODEL=phobert_b
SKLEARN_MODELS=svm:../ml/artifacts/baselines/svm_A.joblib,lr:../ml/artifacts/baselines/lr_A.joblib,nb:../ml/artifacts/baselines/nb_A.joblib
```

Khởi động lại backend và kiểm tra `/api/health`: `active_model` là model thực sự dùng, `active_version` là version tương ứng; mỗi model có `available`, `loaded`, `active` và `error`. Nếu B không nạp được, backend fallback về PhoBERT A rồi keyword và không báo B là active. Muốn quay lại A, đặt `ACTIVE_MODEL=phobert` rồi restart. Trang admin `/quan-tri/so-sanh-mo-hinh` chỉ so sánh model, không thay đổi `ACTIVE_MODEL`.

Chạy parity PhoBERT B:

```powershell
Set-Location "C:\Projects\firefly-cinema\backend"
.\venv\Scripts\python.exe scripts\check_model.py --model phobert_b
```

Kết quả phải là `PARITY=10/10` và `MAX_ABS_DELTA` không quá `0.001`.

### 4.3. Chấm lại dữ liệu mẫu bằng PhoBERT

Các bình luận mẫu được chấm lúc tạo database. Cột `model_name` và `model_version` ghi model thực tế đã dùng. Không tự xóa database để chấm lại; thực hiện đúng quy trình backup/PO reset ở mục 2.1 nếu thật sự cần tạo lại dữ liệu.

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
