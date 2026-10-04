# Mã và tài sản ML — Firefly Cinema

`C:\Projects\firefly-cinema` là project duy nhất. Mã và tài liệu nhỏ vào Git; dữ liệu, model và backup ở trong project trên ổ C nhưng bị `.gitignore` loại khỏi Git.

## Thứ gì — nằm ở đâu

| Thứ gì | Trong project ổ C | Google Drive |
|---|---|---|
| Mã chuẩn bị dữ liệu, baseline và train PhoBERT | `ml/src/` | Chưa yêu cầu |
| README gốc của mã train | `ml/README_goc.md` | Chưa yêu cầu |
| Kết quả JSON nhỏ | `ml/results/` | Chưa yêu cầu |
| Dữ liệu processed `train/dev/test.csv` | `data/uit-visfd/processed/` (ngoài Git) | `MyDrive/thesis/data/processed/` — chờ upload và kiểm chứng từ Colab mới |
| Error analysis Task A | `data/uit-visfd/results/error_analysis_taskA.csv` (ngoài Git) | `MyDrive/thesis/results/error_analysis_taskA.csv` — chờ upload |
| Model A gốc | `ml/artifacts/phobert_A_best/` (ngoài Git) | `MyDrive/thesis_results/phobert_A_best/` |
| Model A backend | `backend/models/phobert-binhluan/` (ngoài Git) | Không áp dụng |
| Gói `firefly_phobert.zip` | Chưa có trong project | `MyDrive/thesis_results/firefly_phobert.zip` — chưa xác minh trong T00 |
| Notebook phần A | Chưa có file notebook trong project | Chờ Tín lưu trên Drive và cung cấp đường dẫn |
| API cũ để tham chiếu | `backup/02_api_cu/api/` (ngoài Git) | Không áp dụng |

Không chép CSV, model, file nén hoặc backup vào Git. Xem cách khôi phục dữ liệu tại `data/README.md` và thông tin model tại `ml/model_card_A.md`.

## Trạng thái baseline truyền thống

`ml/src/baselines.py` đã có TF-IDF word/character kết hợp ComplementNB, Logistic Regression và LinearSVC cho Task A; đồng thời có baseline cho Task B và C. Kết quả một lần chạy nằm trong `ml/results/baseline_results.json`.

T01 sẽ hoàn thiện trên mã hiện có: kiểm tra tái lập, dùng đúng tập train/dev/test cố định, bổ sung kết quả nhiều seed và bằng chứng cần thiết theo Task Record T01. Không cần viết lại toàn bộ baseline.

## Lưu ý khi tái lập

Script cũ dùng đường dẫn tương đối `processed/`, `results/`, `src/`; dữ liệu hiện ở `data/uit-visfd/processed/`. T01 cần nối đúng đường dẫn hoặc chạy trong workspace phù hợp. `ml/src/train_phobert.py` là mã lịch sử còn gọi `underthesea`; cấu hình model A đang dùng `text_norm` không tách từ. Không dùng script cũ làm chuẩn tiền xử lý hiện tại.
