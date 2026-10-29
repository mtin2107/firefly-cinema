# Sao lưu v1.0 — Firefly Cinema

Lập ngày 29/10/2026 (T13). Mã nguồn nằm trong Git (`master`, tag `v1.0` do Tín gắn sau PO_APPROVED). File dưới đây **không** nằm trong Git vì lớn hoặc chứa dữ liệu chạy thật.

## 1. Vị trí

| Bản sao | Vị trí | Trạng thái |
|---|---|---|
| Máy local | `C:\Projects\firefly-cinema\backup\v1.0\` (cùng cấu trúc thư mục với repo) + `sha256.csv` | Đã tạo 29/10/2026, SHA-256 từng file khớp file gốc, `firefly.db` qua `integrity_check` và `foreign_key_check` |
| Google Drive | `MyDrive/thesis_backup_v1/` | **Tín cần làm** (xem mục 4). Cùng ổ C với repo nên bản local không thay được bản ngoài máy |
| USB / ổ ngoài | tùy Tín | **Nên làm**: chép nguyên thư mục `backup\v1.0\` |
| DB trước reset T29+T30 | `backup\T30-20261029-121409\` (`firefly.db`, sidecar, `db-sha256.csv`) | Bản cũ để phục hồi nếu cần quay về schema trước T29 |

Không sao lưu `backend\.env` vì chứa `SECRET_KEY`, mật khẩu admin và khóa API. Tín tự giữ riêng (ví dụ trình quản lý mật khẩu). `backend\uploads\` hiện chưa có (chưa tải poster/trailer/ảnh đại diện nào lên DB thật). Khi có, chép thêm cả thư mục này, cùng lúc với `firefly.db`.

## 2. Nội dung `backup\v1.0\`

| Nhóm | Số file | Dung lượng |
|---|---:|---:|
| `backend/firefly.db*` (DB demo sau reset 29/10 + sidecar lịch chiếu) | 2 | 0,1 MB |
| `backend/models/` (PhoBERT A-backend và B dùng trên web) | 13 | 1.033,9 MB |
| `ml/artifacts/` (PhoBERT A/B gốc, SVM/LR/NB `.joblib`, manifest) | 18 | 1.035,5 MB |
| `data/` (UIT-ViSFD processed, dữ liệu phim) | 39 | 24,1 MB |
| **Tổng** | **72** | **2.093,6 MB** |

Notebook (`ml/notebooks/T01…T15_*.ipynb`) và kết quả (`ml/results/`) nằm trong Git, không cần sao lưu riêng.

## 3. Checksum SHA-256 các file chính

Danh sách đầy đủ 72 file: `backup\v1.0\sha256.csv`.

| File | Kích thước | SHA-256 |
|---|---:|---|
| `backend/models/phobert-binhluan/model.safetensors` (PhoBERT A-backend) | 540.023.384 B | `15D4658955BA1F8E07C8F578BF53AA0A50A11EC7B27403C264985E55CD41D470` |
| `backend/models/phobert-binhluan-B/model.safetensors` (PhoBERT B, đang dùng) | 540.023.384 B | `0B80947CA8FECFFBFAA39373E92D1ED44D638DCB4981FF00DA2DD08921D22F4F` |
| `ml/artifacts/phobert_B_best/model.safetensors` | 540.023.384 B | `0B80947CA8FECFFBFAA39373E92D1ED44D638DCB4981FF00DA2DD08921D22F4F` |
| `ml/artifacts/phobert_A_best/model.safetensors` | 540.023.384 B | `121C2CBC9131A5B15464B452339C0A077F6FF20C09F52F05525C29466B1B75B7` |
| `ml/artifacts/baselines/svm_A.joblib` | 497.231 B | `51D061FBB3F682FD28A11EDC1D438CF46C67D67EAE4861A76690DC3D3A3E272C` |
| `ml/artifacts/baselines/lr_A.joblib` | 497.949 B | `1760B2EB8D8B6C9CC48AA7496D48062E4CC230998CAAD84E2033B84A402D67DB` |
| `ml/artifacts/baselines/nb_A.joblib` | 661.078 B | `26F2235789A8EBB06D2F1B689EF95EBE7138DE6A6F23D6A49451831474EF1510` |
| `backend/firefly.db` | 139.264 B | `656F1152B05E3861DA6A34AB5DB87B0AC935DC3F136371F8E773A81AF4F40198` |
| `backend/firefly.db.showtime-seed.json` | 250 B | `844BB0ED3576C715342A60000A1149110DABB6C925D6425B4F492AC8A170C631` |

Ghi chú:
- PhoBERT B trên web và `phobert_B_best` là **cùng một file** (hash trùng).
- PhoBERT A-backend **khác** `phobert_A_best` (model card A mục T02: không checkpoint nào tái lập đủ số lịch sử; báo cáo dùng số đo lại có định danh checkpoint).
- `firefly.db` là DB demo lúc sao lưu. Ngày suất chiếu tính theo ngày seed, nên trước buổi bảo vệ chạy `reset-demo.bat` để có lịch mới; không cần khôi phục file này.

## 4. Việc Tín cần làm (ngoài khả năng của Claude/Codex)

1. **Tải lên Drive:** chép `backup\v1.0\` vào `MyDrive/thesis_backup_v1/` (≈ 2,1 GB). Drive đã có sẵn bản cũ ở `MyDrive/thesis_results/phobert_A_best/`, `MyDrive/thesis_results/baselines/`, `MyDrive/thesis/data/…` (model card A, T00).
2. **AC-02 — tải lại một model và so checksum:** tải `thesis_backup_v1/backend/models/phobert-binhluan-B/model.safetensors` về thư mục tạm, chạy:
   ```powershell
   (Get-FileHash .\model.safetensors -Algorithm SHA256).Hash
   ```
   Kết quả phải là `0B80947CA8FECFFBFAA39373E92D1ED44D638DCB4981FF00DA2DD08921D22F4F`. Ghi ngày kiểm vào bảng mục 5.
3. **T00 TODO-03 — `MyDrive/thesis_results/firefly_phobert.zip`:** mở Drive xem file còn không. Còn thì tải về, giải nén, so hash `model.safetensors` với bảng mục 3 (A-backend hoặc A gốc) rồi ghi kết quả. Không còn thì ghi "không còn, thay bằng `thesis_backup_v1/`".
4. **Video demo dự phòng:** quay theo `docs/KICH_BAN_DEMO.md`, lưu `MyDrive/thesis_backup_v1/video/` và ghi đường dẫn vào mục 5.
5. **USB/ổ ngoài:** chép `backup\v1.0\`.

## 5. Nhật ký xác minh (Tín điền)

| Ngày | Việc | Kết quả |
|---|---|---|
| 29/10/2026 | Tạo `backup\v1.0\` + SHA-256 + integrity DB (Claude) | Đạt, 72/72 file khớp |
| | Upload Drive `thesis_backup_v1/` | |
| | Tải lại PhoBERT B từ Drive, so SHA-256 (AC-02) | |
| | Kiểm `firefly_phobert.zip` (T00 TODO-03) | |
| | Video demo dự phòng — vị trí | |
| | Chép USB/ổ ngoài | |

## 6. Khôi phục trên máy mới

Làm theo `HUONG_DAN.md` mục "Cài đặt từ số 0", rồi chép từ bản sao lưu vào đúng chỗ trong repo:
`backend\models\` → `backend\models\`, `ml\artifacts\` → `ml\artifacts\`, `data\` → `data\`. Không cần chép `firefly.db` (backend tự tạo và seed). Sau khi chép, so lại hash với `sha256.csv`.
