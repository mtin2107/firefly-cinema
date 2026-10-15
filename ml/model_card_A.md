# Model card — PhoBERT phần A

## Tổng quan

| Mục | Giá trị |
|---|---|
| Mục đích | Phát hiện bình luận có ít nhất một ý tiêu cực để hỗ trợ kiểm duyệt trên Firefly Cinema |
| Dữ liệu train | UIT-ViSFD, miền bình luận điện thoại |
| Bài toán | Phân loại nhị phân `has_negative` |
| Nhãn | `0 = binh_thuong`, `1 = tieu_cuc` |
| Kiến trúc | `RobertaForSequenceClassification` từ pretrained `vinai/phobert-base-v2`, 2 nhãn, `max_position_embeddings=258`, `max_length=256` |
| Đầu vào | Cột `text_norm`: chữ thường, tách dấu câu, mở rộng một số từ viết tắt; không tách từ |
| Ngưỡng quyết định | `0.5` cho xác suất nhãn tiêu cực |
| Phiên bản | `transformers==5.18.0`, `torch==2.11.0` |
| Kết quả lịch sử trong `ml/artifacts/phobert_A.json` | Dev macro-F1 `0,9176` tại epoch 6; test macro-F1 `0,9128`; test accuracy `0,9141`. Đây là số lịch sử, hiện chưa tái lập đầy đủ bằng một trong hai checkpoint còn trên máy |
| F1 lớp tiêu cực của checkpoint backend | `0,917808` với `text_norm`; `0,918046` khi dùng `normalize()` hiện tại — không phải macro-F1 |

## Dữ liệu và phân bố nhãn

Các số dưới đây được đếm trực tiếp từ ba CSV trong `data/uit-visfd/processed/` của project, theo cột `has_negative`.

| Tập | Số dòng | Nhãn 0 | Nhãn 1 |
|---|---:|---:|---:|
| Train | 7.786 | 3.484 | 4.302 |
| Dev | 1.112 | 516 | 596 |
| Test | 2.224 | 981 | 1.243 |

Đường dẫn nguồn: `data/uit-visfd/processed/{train,dev,test}.csv`. CSV ở trong project ổ C nhưng ngoài Git. Ba split đã upload lên `MyDrive/thesis/data/processed/`; runtime Colab mới đã đọc thành công ngày 04/10/2026. File phân tích lỗi ở `MyDrive/thesis/results/error_analysis_taskA.csv` và bản sao notebook ở `MyDrive/thesis/notebooks/phobert_A.ipynb` cũng đã được kiểm tra tồn tại.

Notebook `phobert_A.ipynb` là bản sao notebook lịch sử A/B/C; còn lệnh cài thư viện và đường dẫn cũ. Việc kiểm tra Drive không chứng minh notebook hiện hành đã tái lập toàn bộ quá trình train.

## Đối chiếu `text_utils.py` ↔ `normalize()`

Đã đối chiếu trực tiếp:

- Cũ: `backup/02_api_cu/api/text_utils.py`.
- Hiện tại: `backend/app/classifier.py::normalize()`.

Kết luận: **khác nhau**. Hàm cũ xóa URL, rút chuỗi ký tự lặp còn hai ký tự, gộp dấu `!?.,` lặp, tách thêm `/` và có bảng teencode rộng hơn. Hàm hiện tại chuẩn hóa Unicode NFC, rút ký tự từ ba lần lặp còn một ký tự, không xóa URL/không gộp dấu câu lặp, và có một số viết tắt riêng như `khg`, `đk`. T00 chỉ ghi nhận; không sửa `normalize()` hay classifier. Sai khác cần được đo/đánh giá lại ở T02 trước mọi quyết định thay đổi.

### 10 câu đối chiếu thực tế

| # | Đầu vào | `text_utils.py` cũ | `normalize()` hiện tại | Giống |
|---:|---|---|---|:---:|
| 1 | `Ko hay như quảng cáo, hơi thất vọng!!!` | `không hay như quảng cáo , hơi thất vọng !` | `không hay như quảng cáo , hơi thất vọng ! ! !` | Không |
| 2 | `Phim dài lê thê, nửa đầu buồn ngủ thật sự.` | `phim dài lê thê , nửa đầu buồn ngủ thật sự .` | như cũ | Có |
| 3 | `Tốtttt quáaaa!!!` | `tốtt quáaa !` | `tốt quáa ! ! !` | Không |
| 4 | `Xem tại https://example.com/phim?id=1 nhé` | `xem tại nhé` | `xem tại https : //example . com/phim ? id=1 nhé` | Không |
| 5 | `khong dc đâu, okie?` | `không được đâu , ổn ?` | `khong được đâu , okie ?` | Không |
| 6 | `khg ổn, đk xem lại` | `khg ổn , đk xem lại` | `không ổn , được xem lại` | Không |
| 7 | `Điện thoại/Phim - giá: 100k` | `điện thoại / phim - giá : 100k` | `điện thoại/phim - giá : 100k` | Không |
| 8 | `hông thik lắm nhưng diễn viên ổn` | `không thích lắm nhưng diễn viên ổn` | `hông thik lắm nhưng diễn viên ổn` | Không |
| 9 | `Mik thấy bthg, cx được.` | `mình thấy bình thường , cũng được .` | `mình thấy bthg , cx được .` | Không |
| 10 | Chuỗi Unicode phân rã tương đương `Phông cảnh đẹp… nhưng nhạc dở` | giữ dạng Unicode phân rã | `phông cảnh đẹp … nhưng nhạc dở` dạng NFC | Không |

## Trạng thái mã mô hình truyền thống

`ml/src/baselines.py` không phải khung rỗng: mã đã train và chọn tham số trên dev cho ComplementNB, Logistic Regression và LinearSVC của Task A, cùng baseline Task B/C. `ml/results/baseline_results.json` ghi một lần chạy; kết quả tốt nhất Task A hiện có là Logistic Regression trên `text_norm`, test macro-F1 `0,8823`, F1 tiêu cực `0,8966`.

T01 nên hoàn thiện trên mã hiện có (tái lập, nhiều seed và bằng chứng), không viết mới toàn bộ. `ml/src/train_phobert.py` là script cũ chưa phản ánh cấu hình model A đã chốt vì vẫn gọi `underthesea`; giữ nguyên để lưu lịch sử, không dùng nó làm chuẩn tiền xử lý hiện tại.

## Hai bản model A trong project ổ C

| Bản | Đường dẫn | SHA-256 `model.safetensors` |
|---|---|---|
| Gốc | `ml/artifacts/phobert_A_best/` | `121C2CBC9131A5B15464B452339C0A077F6FF20C09F52F05525C29466B1B75B7` |
| Backend | `backend/models/phobert-binhluan/` | `15D4658955BA1F8E07C8F578BF53AA0A50A11EC7B27403C264985E55CD41D470` |

Hai file đều 540.023.384 byte nhưng không chỉ khác metadata. Kiểm tra trực tiếp cho thấy cùng 201 tensor, và **cả 201 tensor đều khác giá trị**. Bản backend có thêm ánh xạ nhãn `0 = binh_thuong`, `1 = tieu_cuc` trong `config.json`; việc sửa config không giải thích khác biệt của trọng số. Có khả năng đây là hai checkpoint/lần lưu khác nhau, nhưng chưa có nhật ký train để xác định chính xác nguyên nhân.

### 10 câu kiểm thử hai bản model

Cùng dùng `normalize()` hiện tại, tokenizer của từng thư mục, `max_length=256`, ngưỡng 0,5. Số dưới đây là xác suất nhãn 1; `0` = bình thường, `1` = tiêu cực.

| # | Câu thử | Gốc | Backend | Nhãn gốc/backend |
|---:|---|---:|---:|:---:|
| 1 | Ko hay như quảng cáo, hơi thất vọng!!! | 0,996832 | 0,995723 | 1/1 |
| 2 | Phim dài lê thê, nửa đầu buồn ngủ thật sự. | 0,960167 | 0,048508 | 1/0 |
| 3 | Tốtttt quáaaa!!! | 0,005783 | 0,005155 | 0/0 |
| 4 | Xem tại https://example.com/phim?id=1 nhé | 0,004635 | 0,008241 | 0/0 |
| 5 | khong dc đâu, okie? | 0,851431 | 0,865625 | 1/1 |
| 6 | khg ổn, đk xem lại | 0,991317 | 0,981407 | 1/1 |
| 7 | Điện thoại/Phim - giá: 100k | 0,012546 | 0,011738 | 0/0 |
| 8 | hông thik lắm nhưng diễn viên ổn | 0,030112 | 0,024407 | 0/0 |
| 9 | Mik thấy bthg, cx được. | 0,004954 | 0,005478 | 0/0 |
| 10 | Phông cảnh đẹp… nhưng nhạc dở | 0,992757 | 0,984891 | 1/1 |

Một câu đổi nhãn. Đây là khác biệt có tác động tới sản phẩm, cần PO chọn hướng xử lý sau khi đối chiếu checkpoint và đo trên test. T00 không tự thay bản backend hoặc nhận một bản là đúng hơn.

## Hạn chế và sử dụng phù hợp

- Dữ liệu huấn luyện là bình luận điện thoại, nên model có thể bỏ sót cách chê đặc trưng của phim.
- Model chỉ hỗ trợ kiểm duyệt; không nên coi dự đoán tự động là đánh giá cuối cùng trong tình huống có ảnh hưởng tới người dùng.
- Không dùng test để chọn siêu tham số. Mọi notebook đánh giá sau phải dùng đúng split cố định và cùng logic `normalize()` đã chốt, hoặc ghi rõ thí nghiệm khác biệt.
- Dữ liệu ViSFD dùng cho nghiên cứu; cần trích dẫn SA2SL (Phan và cộng sự, 2021). Việc sử dụng thương mại cần kiểm tra lại quyền dữ liệu.

## T15 — Thử nghiệm tách từ (đang chờ chạy Colab)

Notebook `ml/notebooks/T15_word_segment.ipynb` huấn luyện cặp đối chứng chỉ khác tiền xử lý: `normalize(text)` và `word_segment(normalize(text))`. Hai bản cùng khởi tạo từ `vinai/phobert-base-v2`, dùng seed 42 và recipe T09 (`max_length=256`, batch 8, learning rate 2e-5, weight decay 0,01, warmup 10%, tối đa 5 epoch, early stopping patience 2), cùng split phone train/dev chính thức. Kết quả và khuyến nghị tích hợp chỉ được ghi sau hai clean-run Colab có sai lệch F1 không quá 0,001; chưa thay model web.

## Benchmark so sánh T02 (05/10/2026)

PhoBERT A trong `ml/results/comparison_A.csv` là **checkpoint gốc** tại `ml/artifacts/phobert_A_best/`, được đánh giá lại cùng ba pipeline T01 trên đúng 2.224 câu của UIT-ViSFD test. Mốc lịch sử khoảng `0,918` thuộc **checkpoint backend** tại `backend/models/phobert-binhluan/`, không phải checkpoint gốc trong bảng so sánh chính.

Hai checkpoint khác trọng số (cả 201 tensor đều khác). T02 chỉ đo và định danh, không tự động chọn checkpoint nào thay checkpoint còn lại, không thay model backend. PO sẽ quyết định disposition sau review.

### Đo lại hai checkpoint trên cùng test

Cùng dùng `compute_metrics()`, nhãn `1 = tiêu cực`, ngưỡng `0,5`, `max_length=256` và hai input T02:

| Checkpoint | Input | Precision neg | Recall neg | F1 neg | Macro-F1 | Accuracy |
|---|---|---:|---:|---:|---:|---:|
| Gốc — `ml/artifacts/phobert_A_best/` | `text_norm` | 0,916468 | 0,926790 | 0,921600 | 0,910492 | 0,911871 |
| Gốc — `ml/artifacts/phobert_A_best/` | `normalize(text_raw)` | 0,915538 | 0,924377 | 0,919936 | 0,908686 | 0,910072 |
| Backend — `backend/models/phobert-binhluan/` | `text_norm` | 0,919290 | 0,916331 | 0,917808 | 0,907022 | 0,908273 |
| Backend — `backend/models/phobert-binhluan/` | `normalize(text_raw)` | 0,921394 | 0,914722 | 0,918046 | 0,907526 | 0,908723 |

Không checkpoint nào tái lập đầy đủ cặp số lịch sử trong `phobert_A.json` (test macro-F1 `0,9128`, accuracy `0,9141`). Vì không còn nhật ký môi trường/lần lưu tương ứng, T02 giữ số lịch sử để truy vết nhưng dùng số đo lại có định danh checkpoint cho báo cáo thực nghiệm.

CPU batch 1 được đo bằng `time.perf_counter`, warm-up 1 câu rồi đo 1.000 câu test đầu tiên, cùng phương pháp cho cả bốn mô hình. Máy đo: Windows 11, Intel Core i5-12450HX (8 core/12 logical CPU), RAM 16 GB; Python 3.13.2, PyTorch 2.11.0+cpu, Transformers 5.18.0, scikit-learn 1.7.2. Độ trễ trung bình trên `text_norm`:

| Mô hình | ms/câu CPU |
|---|---:|
| PhoBERT A | 45,716840 |
| SVM | 0,354897 |
| Logistic Regression | 0,344190 |
| Naive Bayes | 0,418245 |

Số GPU `1,817131 ms/câu` của PhoBERT trong `comparison_A.csv` chỉ là tham khảo, quy đổi từ runtime test lịch sử `4,0413 giây / 2.224 câu`; phép đo lịch sử dùng batching nên không so trực tiếp với CPU batch 1. Kết quả đầy đủ cho `text_norm` và `normalize(text_raw)` nằm ở `ml/results/comparison_A.csv`.

Tên cột `size_mb` được giữ vì schema T02 đã cố định; giá trị thực tế được tính theo MiB (`1024²` byte).
