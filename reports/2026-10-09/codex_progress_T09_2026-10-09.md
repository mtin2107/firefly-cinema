# Báo cáo tiến độ Codex — T09 — 09/10/2026

## 1. Trạng thái

- Task: T09 — Train PhoBERT phần B trên dữ liệu phim.
- Trạng thái hiện tại: **IN_PROGRESS / WAITING_FOR_COLAB_EVIDENCE**.
- Đây là báo cáo tiến độ, **không phải** implementation report cuối để bàn giao Claude.
- Không tự review, không ghi acceptance criterion PASS khi chưa có kết quả GPU thật.
- Không chuyển T09 sang `CLAUDE_REVIEW`.

## 2. Git baseline và commit

- Branch: `task/T09-phobert-B`.
- Baseline bắt đầu: `6c4b8de6ff4a9811b70acf7c1acd46ee1c6a74f5`.
- Baseline trùng `master` tại thời điểm pre-flight và chứa merge T08 `778675e`.
- Commit implementation hiện tại: `3b6e849facc23932fb9dbfb19d36650a78478213` — `[T09] Prepare PhoBERT B Colab training`.
- Working tree sạch sau commit.
- Nhánh đi trước `master` một commit.

## 3. Pre-flight

- Đúng branch `task/T09-phobert-B`: PASS.
- Working tree ban đầu sạch: PASS.
- Dependency T08 DONE/CLOSED và merge `778675e` là ancestor: PASS.
- Có `movie_train.csv` 347 dòng và `movie_test.csv` 149 dòng: PASS.
- Có phone train/dev/test cố định: PASS.
- Có checkpoint research `ml/artifacts/phobert_A_best/`: PASS.
- Có `svm_A.joblib`, `lr_A.joblib`, `nb_A.joblib`: PASS.
- Có baseline canonical T08 `ml/results/domain_shift.csv`: PASS.
- Dependency quan trọng còn thiếu: không có ở local; phần GPU và Drive evidence thuộc trách nhiệm chạy Colab của Tín.

## 4. Files Changed

- `docs/TASK_COORDINATION_ACTIVE.md`
- `ml/README.md`
- `ml/model_card_B.md`
- `ml/notebooks/T09_phobert_B.ipynb`
- `ml/src/model_b_utils.py`
- Báo cáo tiến độ này.

Không sửa `backend/**`, `frontend/**`, schema, `normalize()` hoặc production model.

## 5. Implementation

### Notebook Colab

Đã tạo `ml/notebooks/T09_phobert_B.ipynb` gồm:

- tự tìm repo bằng `FIREFLY_PROJECT_ROOT`, thư mục hiện tại, thư mục cha hoặc `/content/firefly-cinema`;
- fallback giải nén gói code từ `MyDrive/thesis/code/firefly-cinema-T09-code.zip`;
- fallback dữ liệu/checkpoint/baseline giữa project local và Drive;
- pin `transformers==5.18.0`, `scikit-learn==1.7.2`, `joblib==1.5.2`;
- bắt buộc GPU trước fine-tune;
- fine-tune mới từ checkpoint research PhoBERT A, có assertion không dùng đường dẫn backend;
- `normalize()` parity 20 câu giữa train/eval và runtime;
- nhãn `0 = binh_thuong`, `1 = tieu_cuc`, `max_length=256`, seed 42;
- validation 15% phân tầng từ movie train;
- config a chỉ movie; config b movie + phone train/dev theo tỷ lệ dòng 1:1;
- PhoBERT thử a/b × learning rate 1e-5/2e-5, tối đa 5 epoch, early stopping patience 2;
- SVM/LR/NB thử cả a/b với grid nhất quán T01;
- ghi selection manifest trước khi đọc test;
- chỉ cell final test mới gọi `pd.read_csv()` cho movie test và phone test;
- tạo bảng PhoBERT A/B, SVM/LR/NB A/B trên hai test set;
- thêm baseline dự đoán hằng nhãn 1 để công bố ảnh hưởng lệch nhãn;
- kiểm parity baseline A với T08, schema `comparison_B.csv`, CPU reload và `id2label`;
- lưu model/tokenizer lên Drive và tạo `firefly_phobert_B.zip`;
- in kích thước và SHA-256 artifact Drive.

### Helper CPU

Đã tạo `ml/src/model_b_utils.py` cho:

- data validation và SHA-256;
- split/lấy mẫu phân tầng tái lập;
- metric nhãn tiêu cực và macro-F1;
- grid SVM/LR/NB;
- selection manifest;
- kiểm schema `comparison_B.csv`.

PyTorch là import tùy chọn để phần traditional baseline chạy được trong môi trường CPU không cài PyTorch.

## 6. Kết quả cấu hình a/b hiện có

### Split và preprocessing

- Movie train gốc: 347 dòng.
- Movie train part: 294 dòng.
- Movie validation: 53 dòng, gồm nhãn 0 = 17 và nhãn 1 = 36.
- Config a: 294 dòng.
- Config b: 588 dòng, gồm 294 movie + 294 phone.
- Normalize parity local: 20/20.
- Split và mẫu phone tái lập cùng seed: PASS.

### Traditional baseline — validation local

| Model | Config chọn | Hyperparameter | Precision neg | Recall neg | F1 neg | Macro-F1 |
|---|:---:|---|---:|---:|---:|---:|
| SVM | b | word, min_df=2, sublinear_tf=False, C=1.0 | 0.914286 | 0.888889 | 0.901408 | 0.850704 |
| Logistic Regression | a | word, min_df=3, sublinear_tf=True, C=5.0 | 0.868421 | 0.916667 | 0.891892 | 0.820946 |
| Naive Bayes | a | word+char, min_df=3, sublinear_tf=True, alpha=0.1 | 0.795455 | 0.972222 | 0.875000 | 0.745192 |

Grid được chạy lại hai lần local và cho cùng selection/metric. Đây chỉ là validation, chưa phải kết quả final test.

### PhoBERT a/b

**PENDING_COLAB_EVIDENCE.** Chưa có metric thật; không giả lập.

## 7. Metrics PhoBERT A/B và SVM/LR/NB

- PhoBERT A và baseline A canonical: notebook sẽ đánh giá lại và assert lệch T08 không quá 0,001.
- PhoBERT B: PENDING.
- SVM/LR/NB B trên movie test và phone test: PENDING.
- Baseline dự đoán hằng: code đã có, output PENDING.
- `ml/results/comparison_B.csv`: chưa tạo trước Colab để tránh artifact rỗng hoặc số liệu giả.

## 8. Colab và Drive evidence

Chưa nhận từ Tín:

- hai clean-run Colab từ runtime mới;
- bảng bốn trial PhoBERT a/b × learning rate;
- selection PhoBERT đã khóa;
- final-test metrics;
- CPU reload marker với Transformers 5.18.0;
- SHA-256 và kích thước artifact Drive;
- xác minh `MyDrive/thesis_results/phobert_B_best/`;
- xác minh `MyDrive/thesis_results/firefly_phobert_B.zip`.

Do đó chưa tạo implementation report cuối.

## 9. Acceptance Criteria

| AC | Trạng thái | Evidence hiện có / còn thiếu |
|---|---|---|
| AC-01 | DEV STATIC OK / PENDING COLAB | Code chỉ đọc hai test trong cell final sau selection manifest; cần output clean-run xác nhận. |
| AC-02 | PENDING | Chưa có F1 PhoBERT B thật trên movie test. |
| AC-03 | PENDING | Chưa có F1 B phone và mức giảm so với A. |
| AC-04 | PENDING | Code kiểm `id2label`, CPU reload Transformers 5.18.0 và zip; chưa có artifact thật. |
| AC-05 | PENDING | Code sinh/kiểm đủ model × hai test; chưa có `comparison_B.csv` thật. |
| AC-06 | PENDING | Model card hiện là khung `PENDING_COLAB_EVIDENCE`; chưa có lý do chọn PhoBERT a/b dựa trên metric thật. |

Không AC nào được ghi PASS ở thời điểm báo cáo này.

## 10. Definition of Done

- Notebook và code local: DONE.
- CPU validation/reproducibility phần traditional: DONE.
- GPU fine-tune và hai clean-run: PENDING.
- Final test đúng một lần sau selection trong mỗi clean-run: PENDING.
- `comparison_B.csv` và model card hoàn chỉnh: PENDING.
- CPU reload artifact B: PENDING.
- Drive artifact/zip evidence: PENDING.
- Implementation report cuối: PENDING.
- Chuyển `CLAUDE_REVIEW`: NOT ALLOWED YET.

## 11. Quality gates

| Gate | Trạng thái |
|---|---|
| Seed/split/sample reproducibility local | PASS |
| Chống leakage — static notebook inspection | PASS |
| Normalize parity local | PASS 20/20 |
| Nhãn/max_length/checkpoint research — static | PASS |
| Notebook JSON và compile toàn bộ code cell | PASS |
| Traditional selection chạy lại | PASS, cùng số |
| GPU reproducibility sai lệch ≤ 0,001 | PENDING |
| Hai test set và metric thật | PENDING |
| CPU reload model B | PENDING |
| Scope | PASS |
| Secret scan | PASS |
| Không model/data/zip/CSV lớn trong Git | PASS |

## 12. TODO T08 chuyển sang T09

- Baseline dự đoán hằng: code đã triển khai; **chưa RESOLVED** đến khi có output thật.
- Ảnh hưởng lệch tỷ lệ nhãn: code/model-card generator đã triển khai; **chưa RESOLVED**.
- Notebook portability: đã triển khai tìm root/fallback Drive/gói code; **chưa RESOLVED** đến clean-run Colab.
- Preprocessing parity: local 20/20 và có assertion Colab; **chưa RESOLVED** đến clean-run.
- Giới hạn test 149 câu: đã có disclosure trong model-card generator; **chưa RESOLVED** đến artifact cuối.

## 13. Blockers và Required Fixes

- Blocker kỹ thuật local: 0.
- Required Fix mở: 0.
- External evidence đang chờ: Tín chạy Colab GPU và xác minh Drive theo phân công Task Record.
- Nếu PhoBERT B không thắng A, phải ghi kết quả thật và báo PO; không chọn lại dựa trên test.
