# Model Card — PhoBERT B

## Phiên bản đề xuất

`phobert-B-2026-10-09` — chỉ là phiên bản đề xuất cho T10; chưa thay model production trong T09.

## Nguồn khởi tạo và nhãn

- Fine-tune từ checkpoint research canonical `ml/artifacts/phobert_A_best/`, SHA-256 `121c2cbc9131a5b15464b452339c0a077f6ff20c09f52f05525c29466b1b75b7`; không dùng checkpoint backend.
- `id2label`: `0 = binh_thuong`, `1 = tieu_cuc`; `max_length=256`; threshold/argmax mặc định hai lớp.
- `normalize()` giống runtime, parity notebook 20/20. Không tách từ.

## Dữ liệu và chống leakage

- Movie train: 347 câu. Validation 15% phân tầng bằng seed 42: 294 train / 53 validation.
- Config a chỉ dùng movie. Config b thêm mẫu phone train+dev có số dòng bằng movie (1:1), seed 42; phone test không thuộc pool lấy mẫu.
- `movie_test.csv` và phone `test.csv` chỉ được nạp sau marker `SELECTION_LOCKED`; không chọn lại sau khi xem test.

## Hyperparameter và lựa chọn bằng validation

- PhoBERT thử config a/b, learning rate 1e-5/2e-5, batch 8, AdamW, weight decay 0.01, warmup 10%, tối đa 5 epoch, early stopping patience 2.
- Chọn config `b`, learning rate `2e-05`, epoch `3` vì đạt validation macro-F1 `0.957937` và F1 neg `0.971429`.
- Logistic Regression: config `a`, word, `min_df=3`, `sublinear_tf=True`, `C=5.0`; validation macro-F1 `0.820946`, F1 neg `0.891892`.
- Naive Bayes: config `a`, word+char, `min_df=3`, `sublinear_tf=True`, `alpha=0.1`; validation macro-F1 `0.745192`, F1 neg `0.875000`.
- SVM: config `b`, word, `min_df=2`, `sublinear_tf=False`, `C=1.0`; validation macro-F1 `0.850704`, F1 neg `0.901408`.

## Kết quả final test

| Model | Config | Test | Precision neg | Recall neg | F1 neg | Macro-F1 |
|---|:---:|:---:|---:|---:|---:|---:|
| PhoBERT A | A | phone | 0.915538 | 0.924377 | 0.919936 | 0.908686 |
| PhoBERT A | A | movie | 0.962963 | 0.772277 | 0.857143 | 0.816502 |
| PhoBERT B | b | phone | 0.887801 | 0.948512 | 0.917153 | 0.901837 |
| PhoBERT B | b | movie | 0.956989 | 0.881188 | 0.917526 | 0.881840 |
| SVM A | A | phone | 0.883648 | 0.904264 | 0.893837 | 0.877855 |
| SVM A | A | movie | 0.787037 | 0.841584 | 0.813397 | 0.687597 |
| Logistic Regression A | A | phone | 0.882261 | 0.904264 | 0.893127 | 0.876910 |
| Logistic Regression A | A | movie | 0.781818 | 0.851485 | 0.815166 | 0.683445 |
| Naive Bayes A | A | phone | 0.878324 | 0.876911 | 0.877617 | 0.861415 |
| Naive Bayes A | A | movie | 0.772727 | 0.841584 | 0.805687 | 0.667211 |
| SVM B | b | phone | 0.833073 | 0.859212 | 0.845941 | 0.821826 |
| SVM B | b | movie | 0.855769 | 0.881188 | 0.868293 | 0.788985 |
| Logistic Regression B | a | phone | 0.637774 | 0.958970 | 0.766067 | 0.610578 |
| Logistic Regression B | a | movie | 0.830189 | 0.871287 | 0.850242 | 0.754791 |
| Naive Bayes B | a | phone | 0.618583 | 0.969429 | 0.755249 | 0.566964 |
| Naive Bayes B | a | movie | 0.821429 | 0.910891 | 0.863850 | 0.761337 |
| Constant positive | none | phone | 0.558903 | 1.000000 | 0.717046 | 0.358523 |
| Constant positive | none | movie | 0.677852 | 1.000000 | 0.808000 | 0.404000 |

PhoBERT B thắng PhoBERT A trên movie F1 tiêu cực: `0.917526` so với `0.857143`. Trên phone, `F1_A - F1_B = 0.002783`, tức B thấp hơn A 0,002783.

## Lệch nhãn và giới hạn

- Movie test có 149 câu, gồm 101 câu tiêu cực (67,8%). Baseline dự đoán hằng nhãn 1 đạt F1 neg `0.808000` nhưng macro-F1 chỉ `0.404000`; vì vậy phải đọc F1 neg cùng macro-F1.
- Movie test nhỏ và mất cân bằng; chênh lệch metric có độ bất định cao. Không dùng test này để tinh chỉnh tiếp.
- Dữ liệu phim chỉ 496 câu tổng cộng và bao gồm review phim/rạp. Model có thể chưa bao phủ tiếng lóng, châm biếm và câu khen/chê trộn lẫn.
- Fine-tune tiếp từ A có thể gây quên miền phone; mức giảm phone ở trên là trade-off thực nghiệm cần PO xem xét.
- Artifact chỉ được đề xuất cho T10 sau review/PO approval; T09 không thay checkpoint production.

## Tái lập và artifact

- Hai clean-run T4 từ runtime mới cho cùng selection, validation metrics, test metrics và cùng SHA-256 cho `config.json`, `model.safetensors`, `selection_manifest.json`.
- Seed 42; manifest khóa selection: `selection_manifest.json`.
- Đã nạp lại trên CPU bằng `transformers==5.18.0`, logits có shape `(1, 2)`, `config.json` có đúng `id2label`.
- Drive: `MyDrive/thesis_results/phobert_B_best/` và `MyDrive/thesis_results/firefly_phobert_B.zip`. Model/tokenizer/zip không commit Git.

## TODO T08 chuyển sang T09

- Baseline dự đoán hằng và ảnh hưởng lệch nhãn: **RESOLVED** bằng kết quả thật trên hai test set và disclosure macro-F1.
- Notebook portability: **RESOLVED** qua hai clean-run từ runtime mới, dùng gói code và fallback Drive.
- Preprocessing parity: **RESOLVED** bằng marker `NORMALIZE_PARITY_OK=20/20` trong cả hai clean-run.
- Giới hạn movie test 149 câu và tỷ lệ tiêu cực 67,8%: **RESOLVED** ở mức disclosure; giới hạn dữ liệu vẫn tồn tại, không được hiểu là đã loại bỏ.
