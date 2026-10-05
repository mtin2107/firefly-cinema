# Mã và tài sản ML — Firefly Cinema

`C:\Projects\firefly-cinema` là project duy nhất. Mã và tài liệu nhỏ vào Git; dữ liệu, model và backup ở trong project trên ổ C nhưng bị `.gitignore` loại khỏi Git.

## Thứ gì — nằm ở đâu

| Thứ gì | Trong project ổ C | Google Drive |
|---|---|---|
| Mã chuẩn bị dữ liệu, baseline và train PhoBERT | `ml/src/` | Chưa yêu cầu |
| README gốc của mã train | `ml/README_goc.md` | Chưa yêu cầu |
| Kết quả JSON nhỏ | `ml/results/` | Chưa yêu cầu |
| Dữ liệu processed `train/dev/test.csv` | `data/uit-visfd/processed/` (ngoài Git) | `MyDrive/thesis/data/processed/` — đã upload; runtime Colab mới đọc thành công ngày 04/10/2026 |
| Error analysis Task A | `data/uit-visfd/results/error_analysis_taskA.csv` (ngoài Git) | `MyDrive/thesis/results/error_analysis_taskA.csv` — đã upload, kiểm tra tồn tại từ runtime Colab mới ngày 04/10/2026 |
| Model A gốc | `ml/artifacts/phobert_A_best/` (ngoài Git) | `MyDrive/thesis_results/phobert_A_best/` |
| Model A backend | `backend/models/phobert-binhluan/` (ngoài Git) | Không áp dụng |
| Gói `firefly_phobert.zip` | Chưa có trong project | `MyDrive/thesis_results/firefly_phobert.zip` — chưa xác minh trong T00 |
| Notebook phần A | Không đưa notebook vào Git | `MyDrive/thesis/notebooks/phobert_A.ipynb` — bản sao notebook lịch sử A/B/C, đã kiểm tra tồn tại từ runtime Colab mới ngày 04/10/2026 |
| API cũ để tham chiếu | `backup/02_api_cu/api/` (ngoài Git) | Không áp dụng |

Không chép CSV, model, file nén hoặc backup vào Git. Xem cách khôi phục dữ liệu tại `data/README.md` và thông tin model tại `ml/model_card_A.md`.

Notebook `phobert_A.ipynb` còn lệnh cài thư viện và đường dẫn cũ. Việc lưu bản sao và đọc lại CSV trên Drive không có nghĩa notebook hiện hành đã tái lập toàn bộ quá trình train.

## Baseline truyền thống T01

Script `ml/src/baselines.py` huấn luyện ba baseline cho Task A trên CPU:

- TF-IDF + MultinomialNB;
- TF-IDF + LogisticRegression;
- TF-IDF + LinearSVC.

Mỗi model thử TF-IDF word n-gram `(1, 2)`, char n-gram `(2, 5)` và FeatureUnion word + char. Grid nhỏ gồm `min_df`, `sublinear_tf`, `alpha` hoặc `C`. Cấu hình được chọn chỉ bằng macro-F1 trên dev; script chưa đọc test cho tới khi cả ba cấu hình đã được chốt và pipeline cuối đã train xong.

### Cài dependency

Chạy ở thư mục gốc project bằng PowerShell:

```powershell
python -m pip install -r ml\requirements-ml-train.txt
```

### Dữ liệu vào

Ba file cố định từ T00 nằm tại `data\uit-visfd\processed\{train,dev,test}.csv`. Script chỉ dùng cột `text_norm` và nhãn `has_negative`, đồng thời dừng ngay nếu số dòng hoặc phân bố nhãn không khớp `ml/model_card_A.md`.

### Chạy baseline

```powershell
python ml\src\baselines.py `
  --data data\uit-visfd\processed `
  --out ml\results
```

Kết quả nhỏ được ghi vào `ml\results\baselines.csv`. Ba pipeline đầy đủ được ghi mặc định vào thư mục ngoài Git `ml\artifacts\baselines\`:

- `nb_A.joblib`;
- `lr_A.joblib`;
- `svm_A.joblib`.

Khi chạy trên Colab hoặc máy đã mount Google Drive, thêm đối số sau để đồng thời sao chép model tới `MyDrive/thesis_results/baselines/`:

```powershell
--drive-artifacts <duong-dan-mount>\MyDrive\thesis_results\baselines
```

Không `git add -f` hoặc commit bất kỳ `.joblib` nào. Model chỉ được lưu ở `ml\artifacts\baselines\` và bản sao Google Drive.

### Kiểm tra tái lập

```powershell
python ml\src\baselines.py `
  --data data\uit-visfd\processed `
  --out $env:TEMP\t01_rerun
```

So sánh các cột metric giữa hai file `baselines.csv`; timing CPU có thể dao động. Mọi vị trí có randomness dùng `random_state=42`.

## Lưu ý khi tái lập

Script cũ dùng đường dẫn tương đối `processed/`, `results/`, `src/`; dữ liệu hiện ở `data/uit-visfd/processed/`. T01 cần nối đúng đường dẫn hoặc chạy trong workspace phù hợp. `ml/src/train_phobert.py` là mã lịch sử còn gọi `underthesea`; cấu hình model A đang dùng `text_norm` không tách từ. Không dùng script cũ làm chuẩn tiền xử lý hiện tại.
