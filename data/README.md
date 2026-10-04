# Dữ liệu cục bộ của Firefly Cinema

Project chính: `C:\Projects\firefly-cinema`. CSV nằm trong project để các task ML dùng trực tiếp, nhưng bị `.gitignore` loại khỏi Git.

| Nội dung | Đường dẫn trong project | Bản Drive cần lưu |
|---|---|---|
| Tập train/dev/test cố định | `data/uit-visfd/processed/{train,dev,test}.csv` | `MyDrive/thesis/data/processed/` |
| Các tập aspect/sentiment đã xử lý | `data/uit-visfd/processed/{train,dev,test}_aspect_sentiment.csv` | Chưa thuộc yêu cầu upload T00 |
| Phân tích lỗi Task A | `data/uit-visfd/results/error_analysis_taskA.csv` | `MyDrive/thesis/results/error_analysis_taskA.csv` |

Để khôi phục sau khi thay máy, tải đúng file từ Drive về các đường dẫn trong bảng. Đối chiếu số dòng và phân bố `has_negative` với `ml/model_card_A.md` trước khi dùng. Không tạo split mới hoặc đưa CSV vào Git.

Notebook phần A cần được Tín lưu trên Drive và cung cấp đường dẫn. Runtime Colab mới phải mount Drive rồi đọc trực tiếp ba CSV từ `MyDrive/thesis/data/processed/`; đó là bằng chứng AC-02.
