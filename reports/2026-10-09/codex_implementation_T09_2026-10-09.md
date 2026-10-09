# Báo cáo implementation Codex — T09 — 09/10/2026

## 1. Kết quả và trạng thái bàn giao

- Task: T09 — Train PhoBERT phần B trên dữ liệu phim.
- Branch: `task/T09-phobert-B`.
- Trạng thái: **CLAUDE_REVIEW**.
- Kết quả chính: PhoBERT B config b đạt F1 tiêu cực movie `0.917526`, cao hơn PhoBERT A `0.857143`; phone F1 giảm `0.002783` so với A.
- Hai clean-run Google Colab T4 từ runtime mới cho cùng selection, validation metrics, final-test metrics và cùng SHA-256 của checkpoint/config/manifest.
- T09 không thay model production. `phobert-B-2026-10-09` chỉ là phiên bản đề xuất cho T10 sau review và PO approval.

## 2. Git baseline và commit

- Baseline: `6c4b8de6ff4a9811b70acf7c1acd46ee1c6a74f5`, chứa merge T08 `778675e`.
- `3b6e849facc23932fb9dbfb19d36650a78478213` — `[T09] Prepare PhoBERT B Colab training`.
- `ad9394b` — `[T09] Add pre-Colab progress report`.
- `c8a0230` — `[T09] Align Colab Drive movie path`.
- `458a073fb1a471405de83234417ae1d8a7fdad60` — `[T09] Record PhoBERT B Colab results`.
- Working tree được kiểm tra sạch trước khi tạo report/coordination handoff.

## 3. Files Changed

- `ml/notebooks/T09_phobert_B.ipynb`
- `ml/src/model_b_utils.py`
- `ml/results/comparison_B.csv`
- `ml/model_card_B.md`
- `ml/README.md`
- `docs/TASK_COORDINATION_ACTIVE.md`
- `reports/2026-10-09/codex_progress_T09_2026-10-09.md`
- Báo cáo implementation này.

Không sửa `backend/**`, `frontend/**`, schema, `normalize()` hoặc production checkpoint. Không commit model/tokenizer/ZIP/data lớn.

## 4. Implementation

- Notebook Colab gồm 19 cell, pin `transformers==5.18.0`, `scikit-learn==1.7.2`, `joblib==1.5.2` và bắt buộc GPU.
- Fine-tune luôn khởi tạo mới từ checkpoint research PhoBERT A; có assertion không dùng checkpoint backend.
- Tách validation 15% phân tầng từ 347 movie train với seed 42: 294 train, 53 validation; movie validation có 17 nhãn 0 và 36 nhãn 1.
- Config a: 294 movie. Config b: 294 movie + 294 phone train/dev lấy mẫu phân tầng với seed 42.
- Nhãn giữ `0 = binh_thuong`, `1 = tieu_cuc`; `max_length=256`; preprocessing dùng `normalize()` hiện hành.
- PhoBERT thử a/b × learning rate 1e-5/2e-5, batch 8, AdamW, weight decay 0.01, warmup 10%, tối đa 5 epoch, early stopping patience 2.
- SVM/LR/NB được train lại trên cả config a/b bằng cùng preprocessing và seed.
- Selection manifest được khóa trước khi notebook đọc movie test hoặc phone test. Test không tham gia lựa chọn cấu hình/hyperparameter.
- Final cell đánh giá đúng movie test T08 và phone test cố định, tạo `comparison_B.csv`, model card, Drive checkpoint và ZIP.
- Cell cuối kiểm `id2label`, tokenizer/config, CPU reload bằng Transformers 5.18.0, kích thước và SHA-256 artifact.

## 5. Kết quả validation cấu hình a/b

### PhoBERT

| Config | Learning rate | Best epoch | Validation F1 neg | Validation macro-F1 |
|:---:|---:|---:|---:|---:|
| a | 1e-5 | 1 | 0.957746 | 0.936016 |
| a | 2e-5 | 4 | 0.956522 | 0.937720 |
| b | 1e-5 | 3 | 0.957746 | 0.936016 |
| b | 2e-5 | 3 | **0.971429** | **0.957937** |

Selection rule: macro-F1 movie validation cao nhất, sau đó F1 tiêu cực; không dùng test. Kết quả chọn config b, learning rate 2e-5, epoch 3.

### Mô hình truyền thống

| Model | Config chọn | Hyperparameter | Precision neg | Recall neg | F1 neg | Macro-F1 |
|---|:---:|---|---:|---:|---:|---:|
| SVM | b | word, min_df=2, sublinear=False, C=1.0 | 0.914286 | 0.888889 | 0.901408 | 0.850704 |
| Logistic Regression | a | word, min_df=3, sublinear=True, C=5.0 | 0.868421 | 0.916667 | 0.891892 | 0.820946 |
| Naive Bayes | a | word+char, min_df=3, sublinear=True, alpha=0.1 | 0.795455 | 0.972222 | 0.875000 | 0.745192 |

Grid truyền thống được chạy lại hai lần local và cho cùng selection/metric.

## 6. Final-test metrics

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

PhoBERT B tăng movie F1 neg `0.060383` và movie macro-F1 `0.065338` so với A. Phone F1 neg giảm `0.002783`; phone macro-F1 giảm `0.006849`. Không chọn lại cấu hình sau khi thấy các số test.

## 7. Colab và Drive evidence

- Run 1: `MyDrive/thesis/notebooks/T09_phobert_B_run1.ipynb`, Drive ID `1dpEXx7_1GTj46IicNM2sL1knpZZ_QCJy`.
- Run 2: `MyDrive/thesis/notebooks/T09_phobert_B_run2.ipynb`, Drive ID `1xEKLjORUQLNcvxW1IS4lIok7JFCI4a8g`.
- Cả hai run có `NORMALIZE_PARITY_OK=20/20`, `SELECTION_LOCKED=True`, `FINAL_TEST_COMPLETE=True`, `CPU_RELOAD_OK transformers=5.18.0` và `AC_02_PHOBERT_B_GT_A_MOVIE=True`.
- Cả hai run có cùng metric và cùng SHA-256:
  - `config.json`: 948 bytes, `3af764b446752118aa33982d7983f52919318373ff3108add0128834f28005da`.
  - `model.safetensors`: 540023384 bytes, `0b80947ca8fecffbfaa39373e92d1ed44d638dcb4981ff00da2dd08921d22f4f`.
  - `selection_manifest.json`: 2477 bytes, `d21786d2354c9ac054155c8975da579cede1fc9d05a18b5949c9716f0fa34035`.
- ZIP run 2: 502655745 bytes, SHA-256 `bd7d1544691e0e477ce42b5058cd650d2bf6b957cf335a80398f74bf71c438d1`. Hash ZIP khác run 1 vì metadata thời gian đóng gói; checkpoint/config/manifest bên trong có hash giống nhau.
- Drive checkpoint: `MyDrive/thesis_results/phobert_B_best/`, Drive folder ID `15s9Tb8POURevOvSzOMeM5fT_BD-67JlO`.
- Drive ZIP: `MyDrive/thesis_results/firefly_phobert_B.zip`, Drive file ID `1TIyXMh1TsGAuPAsFg_qykLHg-9ZsKNdY`.
- Drive checkpoint đã xác minh có `config.json`, `model.safetensors`, `tokenizer_config.json`, `added_tokens.json`, `vocab.txt`, `bpe.codes`, `selection_manifest.json`.
- `comparison_B.csv` local khớp byte với manifest/Drive: SHA-256 `c10e49e47ae45dac9ff3fc9114f9f3e94dbfb8b5a6caef7c3e30f85800209ace`.

## 8. Acceptance Criteria

| AC | Kết quả | Evidence |
|---|---|---|
| AC-01 | **DEV PASS** | Notebook chỉ nạp hai test set trong cell final sau selection manifest; hai run in `SELECTION_LOCKED=True; TEST_NOT_LOADED=True` trước final test. |
| AC-02 | **DEV PASS** | Movie F1 neg B `0.917526` > A `0.857143`; marker hai run đều True. |
| AC-03 | **DEV PASS** | Phone F1 neg B `0.917153`; `F1_A - F1_B = 0.002783`. |
| AC-04 | **DEV PASS** | `id2label` đúng; CPU reload Transformers 5.18.0 đạt; checkpoint/tokenizer/ZIP và SHA-256 có trên Drive. |
| AC-05 | **DEV PASS** | `comparison_B.csv` có PhoBERT A/B và SVM/LR/NB A/B trên phone/movie; thêm constant-positive reference; schema 7 cột, 18 dòng dữ liệu. |
| AC-06 | **DEV PASS** | Model card ghi dữ liệu, seed, hyperparameter, lý do chọn b, test metrics, phone drop, giới hạn và model version đề xuất. |

Các trạng thái trên là self-check của implementer, chưa thay review độc lập của Claude hoặc quyết định PO.

## 9. Definition of Done

- Toàn bộ AC có implementation evidence: **MET — pending independent review**.
- Gate ML theo `AGENT_RULES.md`: **PASS**.
- Không có file ngoài allowlist trong diff: **PASS**.
- Tài liệu T09 liên quan đã cập nhật: **PASS**.
- Claude PASS/PASS_WITH_TODO và Tín APPROVED: **PENDING**, đúng workflow sau handoff.

Implementation DoD đã đủ để bàn giao `CLAUDE_REVIEW`; full task DoD chưa được tự tuyên bố hoàn tất.

## 10. Quality gates

| Gate | Kết quả |
|---|---|
| Seed, split và sample reproducibility | PASS — seed 42; 294/53; config b 588 dòng |
| Chống leakage | PASS — test chưa được nạp khi khóa selection |
| Normalize parity | PASS 20/20 trong hai run |
| Nhãn, max_length, research checkpoint | PASS |
| PhoBERT reproducibility | PASS — selection/metric và ba hash cốt lõi giống nhau |
| Traditional reproducibility | PASS — chạy lại grid hai lần cùng kết quả |
| CSV schema/content | PASS — 18 dòng, 7 cột; artifact-tool scan không có formula error |
| Notebook JSON/code compile | PASS — 19 cell |
| CPU reload Transformers 5.18.0 | PASS trong hai run |
| Scope/secret/large artifact | PASS — không model/data/ZIP/secret vào Git |

## 11. TODO T08 chuyển sang T09

- Baseline dự đoán hằng: **RESOLVED** bằng kết quả thật trên hai test set.
- Ảnh hưởng lệch tỷ lệ nhãn: **RESOLVED ở mức phân tích/disclosure**; không tuyên bố đã loại bỏ lệch nhãn.
- Notebook portability: **RESOLVED** bằng hai clean-run từ runtime mới với Drive fallback/code ZIP.
- Preprocessing parity: **RESOLVED** bằng 20/20 trong cả hai run.
- Giới hạn movie test 149 câu: **RESOLVED ở mức disclosure**; giới hạn thống kê vẫn tồn tại.

## 12. Blockers, Required Fixes và TODO

- Blocker: 0.
- Open Required Fixes phía implementer: 0.
- TODO-01, non-blocking: log Colab có cảnh báo API AMP cũ và một lần scheduler step bị cảnh báo khi GradScaler bỏ qua optimizer step. Hai clean-run vẫn byte-identical ở checkpoint cốt lõi và metric; nếu retrain trong task sau, nên nâng cách gọi AMP và chỉ step scheduler khi optimizer thực sự step. Không sửa sau test trong T09 để tránh làm code lệch khỏi evidence đã khóa.
- T10 chưa được mở; T09 không tự review, không tự approve, không merge.
