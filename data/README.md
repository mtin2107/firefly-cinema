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

## Dữ liệu bình luận phim T03

Toàn bộ CSV của T03 nằm tại `data/phim/` trên máy và bản sao tại `MyDrive/thesis/data/movie/`. Các CSV bị `.gitignore` loại khỏi Git; không dùng `git add -f` và không commit nội dung dữ liệu.

| File | Vai trò | Schema |
|---|---|---|
| `movie_comments_v1.csv` | Dữ liệu gốc do Tín thu và gán nhãn A | `id,text,label,source_type,note` |
| `movie_train.csv` | Split train 70% do script tạo | Giống dữ liệu gốc |
| `movie_test.csv` | Split test 30% do script tạo | Giống dữ liệu gốc |
| `kappa_sample.csv` | 100 câu gán đôi | `id,text,label_a,label_b` |

Quy ước cột dữ liệu gốc:

- `id`: mã ổn định, duy nhất, không chứa tên người viết.
- `text`: đoạn bình luận ngắn, giữ nguyên teencode, câu không dấu và emoji nhưng phải bỏ mọi PII.
- `label`: `0` = không có nội dung tiêu cực; `1` = có ít nhất một nội dung tiêu cực. Xem `ml/labeling_guideline.md`.
- `source_type`: chỉ nhận `review_site`, `social`, `self_written`, `web_firefly`.
- `note`: ghi thông tin nghiên cứu không định danh theo dạng `<nguồn> | phim: <tên phim>` hoặc `<nguồn> | rạp: <tên rạp>`. Không ghi tên/tài khoản người viết hay URL hồ sơ.

### Quy tắc thu thập

- Thu thủ công 400–600 câu thật; không dùng LLM để tạo hoặc gán nhãn dữ liệu.
- `review_site` + `social` chiếm ít nhất 80%; `self_written` tối đa 20%; `web_firefly` không đặt chỉ tiêu.
- Có ít nhất 20 phim, mỗi phim tối đa 30 câu, mỗi nguồn cụ thể tối đa 40% tổng dữ liệu. Theo dõi phim và nguồn cụ thể trong `note` vì `source_type` chỉ là nhóm nguồn.
- Chỉ lấy đoạn ngắn phục vụ nghiên cứu. Bỏ tên người viết, email, số điện thoại, `@username` và liên kết hồ sơ.
- Tập test nên ưu tiên bình luận thật; hạn chế `self_written` để tránh kết quả đánh giá cao giả tạo.

### Chạy kiểm tra và tạo split

Từ thư mục gốc `C:\Projects\firefly-cinema`, chạy:

```powershell
python ml\src\prepare_movie_data.py --input data\phim\movie_comments_v1.csv --out data\phim
```

Script kiểm tra schema, nhãn, nhóm nguồn và PII; loại câu trùng sau đúng `normalize()` hiện có của backend; in số dòng bị loại; rồi chia train/test 70/30 có phân tầng với `random_state=42`. Script cũng kiểm tra không có câu trùng giữa hai split và cập nhật `ml/results/movie_data_stats.md` bằng số đo thật.

Khi chưa đủ 400 câu, script vẫn kiểm tra và tạo split nếu dữ liệu hiện có hợp lệ, nhưng báo `BLOCKED_BY_DATA_COLLECTION`; không xem đó là AC-01 đạt. Nếu CSV mới có header, script báo `WAITING_FOR_DATA` và chưa tạo split.

### Gán nhãn B và tính kappa

Khi dữ liệu sau khử trùng đạt ít nhất 400 câu, script chọn cố định 100 câu bằng `random_state=42` và tạo `kappa_sample.csv` với `label_b` để trống.

1. Annotator A là Lê Minh Tín và `label_a` lấy từ nhãn A trong dữ liệu gốc.
2. Tạo một bản làm việc cho Annotator B (“Người 1”) chỉ gồm `id,text,label_b`; không cho B xem `label_a`.
3. B đọc guideline và gán độc lập đủ 100 giá trị `0` hoặc `1`. Không dùng ChatGPT, Claude hay LLM khác để điền nhãn.
4. Tín ghép `label_b` trở lại đúng `id` trong `kappa_sample.csv`, giữ nguyên thứ tự và `label_a`, rồi chạy lại lệnh trên.
5. Script chỉ tính Cohen's kappa khi đủ 100 nhãn B. Thiếu nhãn thì báo `WAITING_FOR_HUMAN_LABEL`; yêu cầu nghiệm thu là kappa ≥ 0,6.

Không tự xóa hoặc tạo lại `kappa_sample.csv` sau khi B đã bắt đầu gán. Nếu dataset thay đổi làm mẫu seed 42 không còn khớp, script sẽ dừng để tránh ghi đè nhãn người thật.

### Snapshot dữ liệu thật ngày 08/10/2026

| Chỉ số | Kết quả |
|---|---:|
| Raw / final sau `normalize()` | 496 / 496 câu |
| Duplicate removed | 0 |
| Label 0 | 159 (32,06%) |
| Label 1 | 337 (67,94%) |
| `review_site` / `social` | 333 (67,14%) / 163 (32,86%) |
| `self_written` / `web_firefly` | 0 / 0 |
| Nguồn cụ thể | Moveek 178 (35,89%); YouTube 163 (32,86%); Google Maps 155 (31,25%) |
| Độ phủ | 83 phim (341 câu) và 28 rạp (155 câu) |
| Train / test | 347 / 149 |
| Duplicate giữa train/test sau `normalize()` | 0 |
| PII scan | 0 phát hiện |
| Cohen's kappa | 0,602510 trên 100 câu, `KAPPA_ACCEPTED` |
| Seed | 42 |

Tỷ lệ label 1 là 67,94%, cao hơn mục tiêu 35–60%. PO đã chọn phương án A ngày 08/10/2026: chấp nhận tỷ lệ thực tế, không thêm/bớt câu và không sửa nhãn. Lý do là guideline đánh dấu mọi câu có ít nhất một vế tiêu cực là nhãn 1, còn quá trình chọn ứng viên thực tế nghiêng về câu chê. Đây là cảnh báo về phân bố dữ liệu, không phải điều kiện chặn script; split vẫn phân tầng theo nhãn. Quyết định được ghi tại `reports/2026-10-08/claude_po_decision_label_ratio_T03_2026-10-08.md`.
