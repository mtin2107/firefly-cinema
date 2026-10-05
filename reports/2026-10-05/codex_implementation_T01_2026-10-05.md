# Codex Implementation Report

Task: T01 — Mô hình truyền thống (NB, LR, SVM)

Date: 2026-10-05

Result: IMPLEMENTATION_COMPLETED

Baseline commit: `20daf6a0b3a38b9fee93ee51c4bad64a34f035f7`

Branch: `task/T01-mo-hinh-truyen-thong`

## Files Changed

- `ml/src/baselines.py`
- `ml/notebooks/T01_baselines.ipynb`
- `ml/results/baselines.csv`
- `ml/requirements-ml-train.txt`
- `ml/README.md`
- `docs/CONG_NGHE.md`
- `reports/2026-10-05/codex_implementation_T01_2026-10-05.md`
- `docs/TASK_COORDINATION_ACTIVE.md`

Đổi schema: Không.

## Dataset / Split Evidence

Đầu vào duy nhất: `text_norm`; nhãn: `has_negative`. Script kiểm tra trực tiếp và dừng nếu lệch `ml/model_card_A.md`.

| Split | Dòng | Nhãn 0 | Nhãn 1 |
|---|---:|---:|---:|
| train | 7.786 | 3.484 | 4.302 |
| dev | 1.112 | 516 | 596 |
| test | 2.224 | 981 | 1.243 |

Luồng code chỉ load train/dev khi tuning. Sau khi chốt cấu hình, train ba pipeline cuối và lưu artifact, code mới load test để đánh giá.

## Model Configurations Tried

- Vectorizer: word TF-IDF `(1,2)`, char_wb TF-IDF `(2,5)`, FeatureUnion word + char.
- `min_df`: `2`, `3`.
- `sublinear_tf`: `false`, `true`.
- MultinomialNB `alpha`: `0.1`, `0.3`, `1.0`.
- LogisticRegression `C`: `0.5`, `1.0`, `5.0`; `class_weight=balanced`, `max_iter=2000`, `solver=liblinear`, `random_state=42`.
- LinearSVC `C`: `0.1`, `0.3`, `1.0`; `class_weight=balanced`, `max_iter=10000`, `random_state=42`.

Mỗi model thử 36 cấu hình, tổng cộng 108 cấu hình. Tiêu chí chọn duy nhất là dev macro-F1.

## Best Parameters

| Model | Vectorizer | Tham số tốt nhất | Dev macro-F1 |
|---|---|---|---:|
| MultinomialNB | word | `alpha=0.1, min_df=3, sublinear_tf=true` | 0,867135 |
| LogisticRegression | word | `C=1.0, min_df=2, sublinear_tf=true` | 0,886990 |
| LinearSVC | word | `C=0.1, min_df=2, sublinear_tf=true` | 0,886040 |

## Dev / Test Metrics

| Model | Split | Precision neg | Recall neg | F1 neg | Macro-F1 | Accuracy |
|---|---|---:|---:|---:|---:|---:|
| MultinomialNB | dev | 0,877311 | 0,875839 | 0,876574 | 0,867135 | 0,867806 |
| MultinomialNB | test | 0,869531 | 0,879324 | 0,874400 | 0,856605 | 0,858813 |
| LogisticRegression | dev | 0,894472 | 0,895973 | 0,895222 | 0,886990 | 0,887590 |
| LogisticRegression | test | 0,886672 | 0,893805 | 0,890224 | 0,874928 | 0,876799 |
| LinearSVC | dev | 0,891667 | 0,897651 | 0,894649 | 0,886040 | 0,886691 |
| LinearSVC | test | 0,886328 | 0,897023 | 0,891643 | 0,876227 | 0,878147 |

## CPU Latency / Model Size

Đo bằng CPU process time trên 1.000 câu đầu của test, gọi `predict([text])` riêng từng câu. Timing trong file kết quả là lượt chạy chính.

| Model | ms/câu | Dung lượng MiB |
|---|---:|---:|
| MultinomialNB | 0,843750 | 0,630454 |
| LogisticRegression | 0,640625 | 0,474881 |
| LinearSVC | 0,640625 | 0,474196 |

## Reproducibility

Chạy đúng lệnh chính, sau đó chạy lại với `--out $env:TEMP\t01_rerun`.

- Số dòng: 6 và 6.
- Cấu hình tốt nhất: giống hệt.
- Sai lệch lớn nhất trên `precision_neg`, `recall_neg`, `f1_neg`, `macro_f1`, `accuracy`: `0,000000`.
- Timing lượt hai dao động như dự kiến; metric vẫn giữ nguyên và đạt ngưỡng `<= 0,001`.

## Acceptance Criteria Evidence

- AC-01: PASS — split/count/label distribution khớp model card; script có assertion bắt buộc.
- AC-02: PASS — test chưa được load trong pha tuning; chỉ đánh giá sau khi cấu hình cuối đã chốt.
- AC-03: PASS — `baselines.csv` có đúng 11 cột bắt buộc và 3 model × dev/test = 6 dòng.
- AC-04: PASS — chạy lần hai có max metric diff `0,000000`.
- AC-05: PASS — load `svm_A.joblib` cho pipeline steps `vectorizer`, `classifier`; câu bắt buộc dự đoán `[1]`.
- AC-06: PASS — `ml/README.md` có dependency, lệnh chạy, input/output, vị trí model và quy tắc không commit artifact.

## Tests / Gates

- `python -m py_compile ml\src\baselines.py`: PASS.
- Notebook JSON và compile toàn bộ code cell: PASS.
- CSV schema, JSON `best_params`, row/model/split assertions: PASS.
- Hai lượt chạy CPU hoàn chỉnh: PASS.
- Load/predict cả ba pipeline: PASS; cả ba trả nhãn `1` cho câu smoke test.
- `.gitignore` áp dụng cho `ml/artifacts/baselines/*.joblib`; `git ls-files '*.joblib'` rỗng: PASS.
- `git diff --check`: PASS (chỉ có cảnh báo chuyển LF/CRLF của Git trên Windows, không có whitespace error).
- Checklist hồi quy web: NOT_APPLICABLE — không sửa `backend/**` hoặc `frontend/**`.
- Security: NOT_APPLICABLE — không có endpoint, secret hay dữ liệu người dùng mới.

## Artifact Paths

- Local ngoài Git: `ml/artifacts/baselines/{nb_A,lr_A,svm_A}.joblib`.
- Kết quả trong Git: `ml/results/baselines.csv`.
- Drive đích: `MyDrive/thesis_results/baselines/`.

Máy chạy hiện tại không có Google Drive mount. Script hỗ trợ `--drive-artifacts <mount>\MyDrive\thesis_results\baselines` để sao chép ba artifact khi Drive được mount; việc upload thực tế cần Tín thực hiện trước PO review.

## Scope / Git Summary

- Chỉ 8 file trong allowlist được thay đổi/thêm.
- Không có `backend/**`, `frontend/**`, `.env`, `firefly.db`, `backend/models/**` hoặc `.joblib` trong Git.
- Artifact model nằm ngoài Git theo đúng `.gitignore`.

## Blockers / TODO

- Blockers: 0.
- TODO-01 (external): sao chép ba `.joblib` lên `MyDrive/thesis_results/baselines/` khi Drive được mount; không ảnh hưởng code, metric hay DEV gate local.

## Handoff

Ready for Claude Independent Review. Codex không tự review hoặc tự PASS.
