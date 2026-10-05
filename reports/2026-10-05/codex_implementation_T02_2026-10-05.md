# Báo cáo implementation T02 — 05/10/2026

## Task / status

- Task: T02 — So sánh PhoBERT với mô hình truyền thống.
- Nhánh: `task/T02-so-sanh-A`.
- Trạng thái bàn giao: `CLAUDE_REVIEW`.
- Prerequisite: T01 `DONE/CLOSED`; nhánh T02 cùng commit `0ce4390` với `master` đã merge T01; PO xác nhận ba artifact đã upload vào `MyDrive/thesis_results/baselines/`. Máy Windows không mount MyDrive, nên phần chạy dùng ba bản local tương ứng tại `ml/artifacts/baselines/` (`nb_A.joblib`, `lr_A.joblib`, `svm_A.joblib`).

## Files changed

- `ml/src/eval_utils.py`
- `ml/notebooks/T02_comparison.ipynb`
- `ml/results/comparison_A.csv`
- `ml/results/error_analysis.md`
- `ml/results/figures/cm_phobert_A.png`
- `ml/results/figures/cm_svm_A.png`
- `ml/results/figures/cm_lr_A.png`
- `ml/results/figures/cm_nb_A.png`
- `ml/model_card_A.md`
- `docs/TASK_COORDINATION_ACTIVE.md`
- `reports/2026-10-05/codex_implementation_T02_2026-10-05.md`

## Đổi schema

Không.

## Implementation

- Thêm `compute_metrics()` dùng chung, quy ước nhãn `1 = tiêu cực`.
- Đánh giá artifact đóng băng; không train lại PhoBERT hoặc baseline, không chọn hyperparameter trên test.
- Sao chép nguyên contract `normalize()` hiện hành từ `backend/app/classifier.py` vào utility đánh giá để tránh import side effect load model.
- Cả bốn mô hình dùng cùng dữ liệu, metric và phương pháp CPU benchmark.
- Sinh CSV so sánh, bốn confusion matrix tiếng Việt và phân tích 20 lỗi/mô hình.

## Dataset / split

- UIT-ViSFD test cố định: 2.224 câu.
- Nhãn 0: 981; nhãn 1: 1.243.
- Chỉ đọc test sau khi các artifact và cấu hình đã đóng băng từ T01/T00; T02 không thực hiện tuning.
- Train/dev không được dùng lại vì task chỉ đánh giá artifact đã train.

## Hai kiểu preprocessing

- `text_norm`: cột đã xử lý và đóng băng trong split T00.
- `normalize`: áp dụng `normalize(text_raw)` theo contract backend hiện hành.

Chênh lệch F1 tiêu cực tuyệt đối `text_norm` so với `normalize(text_raw)`:

| Mô hình | Chênh lệch |
|---|---:|
| PhoBERT A | 0,001664 |
| SVM | 0,002194 |
| Logistic Regression | 0,002903 |
| Naive Bayes | 0,003217 |

Tất cả đều `< 0,01`; không phát sinh blocker và không sửa `normalize()`.

## Bảng metric 4 model

| Model | Input | Precision neg | Recall neg | F1 neg | Macro-F1 | Accuracy | CPU ms/câu | GPU ms/câu | Size MB |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| PhoBERT A | text_norm | 0,916468 | 0,926790 | 0,921600 | 0,910492 | 0,911871 | 120,992818 | 1,817131* | 516,949776 |
| PhoBERT A | normalize | 0,915538 | 0,924377 | 0,919936 | 0,908686 | 0,910072 | 123,056566 | — | 516,949776 |
| SVM | text_norm | 0,886328 | 0,897023 | 0,891643 | 0,876227 | 0,878147 | 1,067651 | — | 0,474196 |
| SVM | normalize | 0,883648 | 0,904264 | 0,893837 | 0,877855 | 0,879946 | 1,034027 | — | 0,474196 |
| Logistic Regression | text_norm | 0,886672 | 0,893805 | 0,890224 | 0,874928 | 0,876799 | 1,081002 | — | 0,474881 |
| Logistic Regression | normalize | 0,882261 | 0,904264 | 0,893127 | 0,876910 | 0,879047 | 1,133124 | — | 0,474881 |
| Naive Bayes | text_norm | 0,869531 | 0,879324 | 0,874400 | 0,856605 | 0,858813 | 1,372282 | — | 0,630453 |
| Naive Bayes | normalize | 0,878324 | 0,876911 | 0,877617 | 0,861415 | 0,863309 | 1,344792 | — | 0,630453 |

`*` GPU PhoBERT chỉ là số tham khảo: `4,0413 giây / 2.224 câu = 1,817131 ms/câu` từ runtime test lịch sử có batching, không so trực tiếp với CPU batch 1.

## CPU benchmark method + cấu hình

- Phương pháp chung: batch 1, warm-up 1 câu ngoài vùng đo, đo 1.000 câu test đầu tiên bằng `time.perf_counter`, lấy tổng thời gian / 1.000.
- Máy: Windows 11 `10.0.26200`, Intel Core i5-12450HX, 8 core/12 logical CPU, RAM vật lý 16 GB.
- Runtime: Python 3.13.2, scikit-learn 1.7.2, PyTorch 2.11.0+cpu, Transformers 5.18.0; device CPU; giới hạn PyTorch tối đa 4 thread để ổn định phép đo.
- Latency có dao động theo tải máy và không thuộc ngưỡng tái lập metric `≤ 0,001`; CSV giữ lần chạy notebook cuối.

## Confusion matrices

- Đã tạo 4 PNG cho kết quả `text_norm`: PhoBERT A, SVM, Logistic Regression và Naive Bayes.
- Cả trục thật và trục dự đoán đều ghi tiếng Việt; nhãn lớp là “Bình thường” và “Tiêu cực”.

## Error analysis

- `ml/results/error_analysis.md` có đúng 20 câu sai cho mỗi mô hình (80 dòng ví dụ).
- Nhóm nguyên nhân: phủ định, chê một phần, châm biếm, từ lóng/viết tắt, nhãn nhiễu/thiếu ngữ cảnh và khác.
- Có bảng tổng hợp và nhận xét trade-off độ chính xác / tốc độ / dung lượng.
- Phân nhóm dùng quy tắc cố định để hỗ trợ rà soát, không dùng lỗi test để chỉnh model hay hyperparameter.

## Focused tests

- `py_compile ml/src/eval_utils.py`: đạt.
- Notebook JSON: nbformat 4, 8 cell, parse thành công.
- `normalize()` kiểm tra mẫu contract: đạt.
- `compute_metrics()` kiểm tra nhãn 1: đạt.
- Gate split 2.224 dòng và phân bố 981/1.243: đạt.
- `comparison_A.csv`: 8 hàng, 4 model × 2 input, đúng 10 cột bắt buộc.
- Baseline `text_norm` so với các hàng test trong `baselines.csv`: max metric diff `0,000000`.
- Error analysis: đúng 20 dòng/mô hình.
- Bốn PNG đã mở kiểm tra; confusion matrix PhoBERT hiển thị đúng dấu tiếng Việt.
- `git diff --check`: đạt.

## Reproducibility gate

- Seed cố định `42`; PyTorch inference mode; artifact và test split đóng băng.
- Chạy utility trong hai tiến trình Python mới, sau đó chạy toàn bộ code cell của notebook trong tiến trình mới thứ ba.
- Ba lượt cho toàn bộ metric của 8 cấu hình giống tuyệt đối; max metric diff `0,000000 ≤ 0,001`.
- Notebook kết thúc bằng `NOTEBOOK_EXECUTION_OK`; các assertion AC và blocker preprocessing đều đạt.

## Scope gate

- Chỉ thay đổi file trong allowlist T02; không sửa `backend/**`, `frontend/**` hoặc task CLOSED.
- Không thêm thư viện.
- Không stage/commit model, `.joblib`, dữ liệu CSV lớn, `.env` hoặc file bí mật.
- Kết quả Git mới chỉ gồm CSV kết quả nhỏ, Markdown và bốn PNG.

## Acceptance Criteria

- AC-01: Đạt — 8 hàng, 4 model × 2 input, đủ cột.
- AC-02: Đạt — PhoBERT A `text_norm` F1 tiêu cực `0,921600`; lệch `0,003600` so với mốc `0,918`, trong ngưỡng `0,005`.
- AC-03: Đạt — SVM/LR/NB `text_norm` khớp `baselines.csv`, max diff `0,000000`.
- AC-04: Đạt — 4 confusion matrix, trục tiếng Việt.
- AC-05: Đạt — 20 câu sai/mô hình, có phân nhóm và trade-off.
- AC-06: Đạt — cùng phương pháp `time.perf_counter`, ghi đầy đủ máy/runtime.

## Blockers

Không có blocker implementation. Chênh F1 do preprocessing không vượt `0,01`.

Lưu ý kiểm chứng prerequisite: MyDrive không được mount trên máy Windows của phiên này; sự tồn tại trên Drive dựa trên xác nhận trực tiếp của PO trong prompt bàn giao. Ba artifact local đã được kiểm tra tồn tại và load/predict thành công.

## TODO

- Claude review độc lập code, kết quả và gate CPU có thể chạy lại.
- PO có thể chạy lại notebook trên Colab/Drive để đối chiếu mount MyDrive và số GPU nếu cần; không dùng số GPU tham khảo hiện tại như benchmark batch 1.
- Không mở T04 hoặc task kế tiếp trong T02.
