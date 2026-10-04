# Dữ liệu cục bộ của Firefly Cinema

Project chính: `C:\Projects\firefly-cinema`. CSV nằm trong project để các task ML dùng trực tiếp, nhưng bị `.gitignore` loại khỏi Git.

| Nội dung | Đường dẫn trong project | Bản đã lưu trên Drive |
|---|---|---|
| Tập train/dev/test cố định | `data/uit-visfd/processed/{train,dev,test}.csv` | `MyDrive/thesis/data/processed/` |
| Các tập aspect/sentiment đã xử lý | `data/uit-visfd/processed/{train,dev,test}_aspect_sentiment.csv` | Chưa thuộc yêu cầu upload T00 |
| Phân tích lỗi Task A | `data/uit-visfd/results/error_analysis_taskA.csv` | `MyDrive/thesis/results/error_analysis_taskA.csv` |

Ba split và file phân tích lỗi đã được upload lên Drive. Runtime Colab mới đọc thành công ba split ngày 04/10/2026: train 7.786 dòng, dev 1.112 dòng, test 2.224 dòng; phân bố `has_negative` khớp `ml/model_card_A.md`.

## Khôi phục trên máy mới

1. Tải `train.csv`, `dev.csv`, `test.csv` từ `MyDrive/thesis/data/processed/` về `data/uit-visfd/processed/` trong project.
2. Tải `error_analysis_taskA.csv` từ `MyDrive/thesis/results/` về `data/uit-visfd/results/`.
3. Đếm lại số dòng và phân bố `has_negative`, đối chiếu bảng trong `ml/model_card_A.md` trước khi dùng. Giữ nguyên split; không tạo split mới hoặc đưa CSV vào Git.

Bản sao notebook lịch sử A/B/C đã lưu tại `MyDrive/thesis/notebooks/phobert_A.ipynb`. File này còn lệnh cài thư viện và đường dẫn cũ, không phải bằng chứng notebook hiện hành đã tái lập toàn bộ quá trình train. Khi chỉ cần kiểm tra dữ liệu Drive, mở runtime Colab mới, mount Drive và đọc trực tiếp ba CSV từ `MyDrive/thesis/data/processed/`.
