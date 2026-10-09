# Model Card — PhoBERT B

> Trạng thái: **PENDING_COLAB_EVIDENCE**. File này là khung bàn giao của T09 và sẽ được cell cuối trong `ml/notebooks/T09_phobert_B.ipynb` ghi lại bằng kết quả huấn luyện thật. Không coi các acceptance criterion cần GPU là PASS trước khi có output Colab và artifact Drive.

## Phiên bản đề xuất

Chưa chốt. Sau khi chạy thành công, notebook đề xuất phiên bản theo dạng `phobert-B-YYYY-MM-DD`. T09 không thay model production; việc gắn model thuộc T10 sau review và PO approval.

## Cấu hình cố định

- Checkpoint khởi tạo: research canonical `ml/artifacts/phobert_A_best/`, không dùng checkpoint backend.
- Nhãn: `0 = binh_thuong`, `1 = tieu_cuc`.
- Preprocessing: `normalize()` production hiện hành, không tách từ.
- `max_length=256`, seed 42.
- Validation: 15% phân tầng từ `movie_train.csv`; `movie_test.csv` không được đọc trước khi khóa selection.
- Config a: chỉ movie. Config b: movie + mẫu phone train/dev có cùng số dòng movie, seed 42.
- PhoBERT: learning rate 1e-5/2e-5, tối đa 5 epoch, early stopping patience 2.

## Evidence đang chờ

- Bảng validation PhoBERT a/b và learning rate/epoch được chọn.
- Kết quả final test PhoBERT A/B và SVM/LR/NB A/B trên movie/phone.
- Mức giảm F1 tiêu cực trên phone của B so với A.
- Kiểm tra `config.json`, CPU reload với `transformers==5.18.0`.
- `MyDrive/thesis_results/phobert_B_best/` và `firefly_phobert_B.zip`.

## Baseline CPU đã kiểm tra cục bộ trước Colab

Split phân tầng tạo 294 movie train và 53 validation (17 nhãn 0, 36 nhãn 1). Config b có 588 dòng. Grid validation hiện chọn:

- SVM: config b, word (1,2), `min_df=2`, `sublinear_tf=False`, `C=1.0`; validation macro-F1 0.850704, F1 tiêu cực 0.901408.
- Logistic Regression: config a, word (1,2), `min_df=3`, `sublinear_tf=True`, `C=5.0`; validation macro-F1 0.820946, F1 tiêu cực 0.891892.
- Naive Bayes: config a, word+char, `min_df=3`, `sublinear_tf=True`, `alpha=0.1`; validation macro-F1 0.745192, F1 tiêu cực 0.875000.

Các số trên chỉ là validation, chưa phải kết quả test và không đủ để nghiệm thu T09.

## TODO T08 chuyển sang T09

- Baseline dự đoán hằng và ảnh hưởng lệch nhãn: đã có code trong cell final test/model card; **chờ output thật, chưa RESOLVED**.
- Notebook portability: đã hỗ trợ `FIREFLY_PROJECT_ROOT`, tìm repo và fallback Drive; **chờ clean-run Colab, chưa RESOLVED**.
- Preprocessing parity: đã có assertion 20/20 giữa train/eval và runtime; **chờ output Colab, chưa RESOLVED**.
- Giới hạn movie test 149 câu và tỷ lệ tiêu cực 67,8%: đã đưa vào model card sinh tự động; **chờ output thật, chưa RESOLVED**.
