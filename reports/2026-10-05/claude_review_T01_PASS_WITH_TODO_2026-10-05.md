# Claude Independent Review — T01

Task: T01 — Mô hình truyền thống (NB, LR, SVM)

Date: 2026-10-05

Reviewer: Claude (Independent Reviewer)

Result: **PASS_WITH_TODO**

Branch: `task/T01-mo-hinh-truyen-thong` · HEAD `b49a57d` · Baseline `20daf6a0b3a38b9fee93ee51c4bad64a34f035f7`

Implementation report: `reports/2026-10-05/codex_implementation_T01_2026-10-05.md` (chỉ dùng làm bằng chứng phụ; mọi kết luận dưới đây dựa trên source, diff và lượt chạy lại của Claude).

Required Fixes: **0** · TODO: 4 (không chặn PO review)

## 1. Git / Scope

| Kiểm tra | Lệnh | Kết quả |
|---|---|---|
| Branch | `git branch --show-current` | `task/T01-mo-hinh-truyen-thong` ✔ |
| Baseline | `git merge-base HEAD master` | `20daf6a0b3a38b9fee93ee51c4bad64a34f035f7` ✔ (một commit `[T01] Train traditional ML baselines` phía trên) |
| Working tree | `git status` | clean ✔ |
| Whitespace | `git diff --check 20daf6a..HEAD` | không lỗi ✔ |
| `.joblib` trong Git | `git ls-files "*.joblib"` | rỗng ✔ |
| Ignore | `git check-ignore -v ml/artifacts/baselines/svm_A.joblib` | `.gitignore:15:ml/artifacts/` ✔ |

`git diff --name-only 20daf6a..HEAD` — 8 file, tất cả thuộc Allowed Files mục 6:

```
docs/CONG_NGHE.md
docs/TASK_COORDINATION_ACTIVE.md
ml/README.md
ml/notebooks/T01_baselines.ipynb
ml/requirements-ml-train.txt
ml/results/baselines.csv
ml/src/baselines.py
reports/2026-10-05/codex_implementation_T01_2026-10-05.md
```

Không có `backend/**`, `frontend/**`, `.env`, `*.db`, `backend/models/**`, `*.joblib`, CSV dữ liệu. Không có đường dẫn `D:\` mới. Đổi schema: Không.

## 2. Dataset

- `ml/src/baselines.py:29-30`: `TEXT_COLUMN = "text_norm"`, `LABEL_COLUMN = "has_negative"`; `load_split()` chỉ đọc hai cột này, dừng nếu thiếu cột, text rỗng hoặc nhãn ngoài {0,1}.
- `EXPECTED_SPLITS` (dòng 31-35) khớp `ml/model_card_A.md` (dòng 24-26) cả số dòng lẫn phân bố nhãn; script raise nếu lệch.
- Lượt chạy của Claude in ra:

```
train: rows=7786, labels={0: 3484, 1: 4302} (model card OK)
dev: rows=1112, labels={0: 516, 1: 596} (model card OK)
test: rows=2224, labels={0: 981, 1: 1243} (model card OK)
```

## 3. Leakage / Tuning

Đọc luồng `main()` (dòng 349-385):

1. Chỉ `load_split(train)` và `load_split(dev)`.
2. `tune_on_dev()` — fit vectorizer trên train, chấm macro-F1 trên dev cho 36 cấu hình/mô hình (3 vectorizer × 2 `min_df` × 2 `sublinear_tf` × 3 giá trị `alpha`/`C`). Hàm không nhận tham số test.
3. `train_final_pipelines()` — build Pipeline từ cấu hình đã chọn, fit trên train, đo dev, `joblib.dump`.
4. Sau đó mới `load_split(test)` và `evaluate_test_and_write_results()` — mỗi pipeline `predict(test_texts)` một lần để tính metric, rồi đo latency (chỉ dự đoán, không ảnh hưởng lựa chọn).

Test không được đọc từ đĩa trước khi cả ba cấu hình chốt và artifact đã lưu → không có đường rò rỉ nào từ test sang lựa chọn siêu tham số. Tie-break dùng `>` (giữ cấu hình đầu tiên) — xác định. Dev metric trong CSV là của pipeline cuối (train-only fit), trùng với điểm tuning.

## 4. Models

| Yêu cầu | Source | Kết quả |
|---|---|---|
| MultinomialNB | dòng 63-69, `alpha ∈ {0.1, 0.3, 1.0}` | ✔ |
| LogisticRegression | dòng 70-82, `C ∈ {0.5, 1.0, 5.0}`, `liblinear`, `class_weight=balanced`, `random_state=42` | ✔ |
| LinearSVC | dòng 83-94, `C ∈ {0.1, 0.3, 1.0}`, `class_weight=balanced`, `random_state=42` | ✔ |
| word TF-IDF (1,2) | dòng 167-172 | ✔ |
| char_wb TF-IDF (2,5) | dòng 173-179, `max_features=150000` | ✔ |
| FeatureUnion word+char | dòng 184-185 | ✔ |
| `random_state=42` | Hai estimator có randomness (LR liblinear, LinearSVC) đều đặt; TF-IDF và MultinomialNB không có randomness; không có shuffle/split ngẫu nhiên | ✔ |

Cả ba mô hình đều chọn vectorizer `word`, `sublinear_tf=true`.

## 5. Result CSV — `ml/results/baselines.csv`

- Header đúng thứ tự 11 cột: `model, vectorizer, best_params, split, precision_neg, recall_neg, f1_neg, macro_f1, accuracy, ms_per_sentence, model_size_mb` ✔
- 6 dòng = {MultinomialNB, LogisticRegression, LinearSVC} × {dev, test} ✔
- `best_params` là JSON hợp lệ ✔
- Không có số hard-code: mọi metric được tính trong `calculate_metrics()` (sklearn, `pos_label=1` = tiêu cực).

| Model | Split | P_neg | R_neg | F1_neg | Macro-F1 | Acc |
|---|---|---:|---:|---:|---:|---:|
| MultinomialNB | dev | 0,877311 | 0,875839 | 0,876574 | 0,867135 | 0,867806 |
| MultinomialNB | test | 0,869531 | 0,879324 | 0,874400 | 0,856605 | 0,858813 |
| LogisticRegression | dev | 0,894472 | 0,895973 | 0,895222 | 0,886990 | 0,887590 |
| LogisticRegression | test | 0,886672 | 0,893805 | 0,890224 | 0,874928 | 0,876799 |
| LinearSVC | dev | 0,891667 | 0,897651 | 0,894649 | 0,886040 | 0,886691 |
| LinearSVC | test | 0,886328 | 0,897023 | 0,891643 | 0,876227 | 0,878147 |

## 6. Reproducibility (chạy lại độc lập trên CPU)

Môi trường: Windows 11, Python 3.13.2 hệ thống (`C:\Users\lemin\AppData\Local\Programs\Python\Python313`), scikit-learn 1.7.2, joblib 1.5.2, scipy 1.18.1, numpy 2.2.4. (`backend\venv` không có scikit-learn — đúng ý đồ, vì T01 không thêm thư viện vào backend.)

```powershell
python ml\src\baselines.py --data data\uit-visfd\processed `
  --out $env:TEMP\t01_claude_review --artifacts $env:TEMP\t01_claude_review\artifacts
```

Claude thêm `--artifacts` trỏ vào TEMP để không ghi đè artifact gốc của Codex. Thời gian chạy ≈ 47 giây.

| So sánh | Kết quả |
|---|---|
| Số dòng / cặp (model, split) | 6 / 6, khớp |
| `model`, `vectorizer`, `best_params` | giống hệt |
| max \|Δ\| trên `precision_neg, recall_neg, f1_neg, macro_f1, accuracy` | **0,0** (ngưỡng ≤ 0,001) ✔ |
| `model_size_mb` | giống, NB lệch 1e-6 (nén zlib) |
| `ms_per_sentence` | commit 0,84 / 0,64 / 0,64 — lượt Claude 0,44 / 0,33 / 0,36 (dao động timing, chấp nhận theo đề bài; xem TODO-04) |
| Dự đoán trên toàn bộ test: artifact gốc vs artifact chạy lại | giống hệt cả 3 mô hình ✔ |

## 7. Artifact Smoke Test — `ml/artifacts/baselines/`

Có đủ `nb_A.joblib` (661 078 B), `lr_A.joblib` (497 949 B), `svm_A.joblib` (497 231 B), ngoài Git.

| Artifact | Kiểu | Steps | `predict(["ko hay như quảng cáo , hơi thất vọng"])` |
|---|---|---|---|
| nb_A | Pipeline | `vectorizer`=TfidfVectorizer, `classifier`=MultinomialNB | `[1]` |
| lr_A | Pipeline | `vectorizer`=TfidfVectorizer, `classifier`=LogisticRegression | `[1]` |
| svm_A | Pipeline | `vectorizer`=TfidfVectorizer, `classifier`=LinearSVC | `[1]` |

AC-05 ghi "với chuỗi đã qua `normalize()`": Claude chạy thêm `backend/app/classifier.py::normalize("ko hay như quảng cáo , hơi thất vọng")` → `'không hay như quảng cáo , hơi thất vọng'`; `svm_A.predict([...])` → `[1]` ✔. `classes_ = [0, 1]` ở cả ba.

## 8. Notebook — `ml/notebooks/T01_baselines.ipynb`

- JSON nbformat 4 hợp lệ, 1 ô markdown + 2 ô code, không có output lưu sẵn.
- Ô 1 tìm thư mục gốc rồi `subprocess.run([sys.executable, ml/src/baselines.py, --data, --out], check=True)`; ô 2 chỉ đọc lại `baselines.csv`.
- Không có logic train/tuning riêng, không đọc test, không có metric hard-code ✔.

## 9. README / Requirements

- `ml/requirements-ml-train.txt`: `scikit-learn==1.7.2`, `joblib==1.5.2` — khớp môi trường chạy lại; `docs/CONG_NGHE.md` mục 5a ghi cùng phiên bản ✔.
- `ml/README.md` mục "Baseline truyền thống T01" có: dependency (`pip install -r ml\requirements-ml-train.txt`), lệnh chạy, input (`data\uit-visfd\processed\{train,dev,test}.csv`, `text_norm`/`has_negative`), output (`ml\results\baselines.csv`), artifact path (`ml\artifacts\baselines\` + Drive `MyDrive/thesis_results/baselines/` qua `--drive-artifacts`), quy tắc không `git add -f`/commit `.joblib`, lệnh kiểm tra tái lập ✔.

## 10. Git Gates (Claude chạy)

```
git status                                   -> nothing to commit, working tree clean
git diff --check 20daf6a..HEAD               -> exit 0
git diff --name-only 20daf6a..HEAD           -> 8 file allowlist (mục 1)
git ls-files "*.joblib"                      -> (rỗng)
python -m py_compile ml/src/baselines.py     -> OK
```

Checklist hồi quy web: NOT_APPLICABLE — không đụng `backend/**`, `frontend/**`.

## 11. Acceptance Criteria

| AC | Kết luận | Evidence độc lập |
|---|---|---|
| AC-01 Đúng split T00, số dòng khớp model card | **PASS** | Mục 2: script assert + output 7786/1112/2224 và phân bố nhãn khớp `model_card_A.md` |
| AC-02 Siêu tham số chọn trên dev, test chạy một lần | **PASS** | Mục 3: test chỉ được đọc sau khi chốt cấu hình và lưu artifact; `tune_on_dev()` không có đường vào test |
| AC-03 `baselines.csv` đủ 3 × (dev, test), đủ cột | **PASS** | Mục 5: header 11 cột đúng thứ tự, 6 dòng |
| AC-04 Chạy lại ra cùng số (≤ 0,001) | **PASS** | Mục 6: max \|Δ\| = 0,0; dự đoán test giống hệt |
| AC-05 `svm_A.joblib` predict câu đã qua `normalize()` | **PASS** | Mục 7: Pipeline vectorizer+classifier, trả `[1]` cả với chuỗi gốc và chuỗi qua `normalize()` |
| AC-06 README ghi cách chạy và nơi lưu `.joblib` | **PASS** | Mục 9 |

Definition of Done: code trong allowlist, gate ML mục 3.2 (seed, split, `text_norm`, kết quả nhỏ vào `ml/results/`) đạt, report Codex có bảng số liệu và AC. Phần "bằng chứng Drive" còn thiếu → TODO-01.

## 12. Required Fixes

**0.**

## 13. TODO (không chặn PO review)

| ID | Mức | Nội dung | Evidence | Đề xuất disposition |
|---|---|---|---|---|
| TODO-01 | Medium (external) | Ba `.joblib` chưa có trên `MyDrive/thesis_results/baselines/`. Task Record mục 4 yêu cầu lưu cả Drive, nhưng không đặt đây là blocker trước Claude review. | Report Codex mục Artifact Paths; máy review không mount Drive | Tín upload (hoặc chạy lại với `--drive-artifacts`) **trước khi gửi prompt T02**, vì T02 chạy trên Colab và cần đúng ba pipeline này. |
| TODO-02 | Low (quy trình) | `ml/src/baselines.py` được viết lại hoàn toàn (106 dòng cũ bị thay), bỏ baseline Task B/C và ablation `text_raw`; report Codex **không ghi** điều này dù prompt bàn giao yêu cầu "nếu cần tách hoặc bỏ phần đó thì ghi vào report để PO quyết". Task Record mục 2 nói "hoàn thiện tiếp, không viết lại". | `git diff 20daf6a..HEAD -- ml/src/baselines.py`; report Codex không có mục nào về B/C | Claude đánh giá thay đổi là hợp lý về kỹ thuật: mọi điểm khác đều do T01 bắt buộc (MultinomialNB thay ComplementNB, Pipeline cho AC-05, không đọc test trước khi chốt cho AC-02 — mã cũ đọc test ngay khi import), lưới tham số và cấu hình char_wb giữ nguyên tinh thần mã cũ. Mã B/C còn trong `20daf6a`; `ml/results/baseline_results.json` giữ số cũ nhưng không còn script sinh ra nó. PO xác nhận chấp nhận (đề xuất ACCEPT). |
| TODO-03 | Low | `EXPECTED_SPLITS` cố định cho UIT-ViSFD → T09 ("train lại SVM/LR/NB trên dữ liệu phim") không chạy được script nguyên trạng. | `ml/src/baselines.py:31-35` | ACCEPT_LATER — T09 tham số hóa phần kiểm tra split. |
| TODO-04 | Low | `ms_per_sentence` dùng `time.process_time_ns()`; trên Windows độ phân giải ≈ 15,625 ms nên giá trị là bội của 0,015625 ms/câu, và dao động ~2 lần giữa hai lượt (0,84 → 0,44 ms với NB). | Mục 6 | ACCEPT_LATER — T02 đo CPU cho cả 4 mô hình bằng cùng một phương pháp (đề xuất `perf_counter`), ghi cấu hình máy (T02 AC-06). |

Ghi chú nhỏ, không thành TODO:
- Codex sửa dòng Project Snapshot của file điều phối từ `nhánh master` sang `nhánh task/T01-mo-hinh-truyen-thong`; Claude trả lại `master` trong lần cập nhật này vì đó là snapshot của repo, không phải nhánh task.
- Lệnh tái lập trong `ml/README.md` không truyền `--artifacts`, nên lượt chạy lại sẽ ghi đè `ml\artifacts\baselines\`. Vì kết quả xác định, không có hại; Claude đã dùng `--artifacts` riêng khi review.

## 14. Kết luận

**PASS_WITH_TODO.** Required Fixes = 0. AC-01 → AC-06 đạt, tái lập chính xác tuyệt đối trên CPU, không rò rỉ test, scope sạch.

Cập nhật file điều phối: T01 `CLAUDE_REVIEW` → `PO_REVIEW`; T02 → `READY_FOR_HANDOFF` (theo `AGENT_RULES.md` mục 1.1 — chỉ là chuẩn bị bàn giao; **T02 không được bắt đầu implementation trước khi Tín PO approve T01 và merge T01 vào master**).

Claude không merge, không PO approve, không đóng T01.

Probe tạm: script so sánh đặt ở `%TEMP%` (ngoài repo) đã xóa; thư mục `%TEMP%\t01_claude_review` chỉ chứa output lượt chạy lại.

## 15. Bàn giao task kế tiếp

**Việc Tín làm trước khi gửi prompt:**
1. PO review T01, cho disposition TODO-01 → TODO-04.
2. Hoàn tất TODO-01: copy `nb_A.joblib`, `lr_A.joblib`, `svm_A.joblib` lên `MyDrive/thesis_results/baselines/`.
3. `git checkout master` → `git merge task/T01-mo-hinh-truyen-thong` (T01 không gắn tag; tag `ml-baselines` gắn khi xong T02).
4. `git checkout -b task/T02-so-sanh-A` từ master đã merge.
5. Gửi prompt dưới đây kèm `docs/tasks/T02.md` và `docs/TASK_COORDINATION_ACTIVE.md`.

**Prompt ChatGPT/Codex cho T02:**

```text
Bạn là Codex, Primary Implementer của dự án Firefly Cinema.
Task: T02 — So sánh PhoBERT với mô hình truyền thống.
Trạng thái: READY_FOR_HANDOFF (Tín gửi Task Record = PO đã duyệt). Chuyển sang IN_PROGRESS khi bắt đầu.
Repo: C:\Projects\firefly-cinema · Nhánh: task/T02-so-sanh-A (đã tách từ master sau khi merge T01).

Chỉ đọc:
1. docs/PROJECT_SOURCE_OF_TRUTH.md
2. docs/AGENT_RULES.md
3. docs/TASK_COORDINATION_ACTIVE.md (Snapshot, Status, Open Blockers, Open TODOs, Next Step)
4. docs/tasks/T02.md
5. Dependency T01 (đã PASS): ml/README.md, ml/results/baselines.csv, ml/src/baselines.py,
   reports/2026-10-05/claude_review_T01_PASS_WITH_TODO_2026-10-05.md (mục 13 TODO)
6. Dependency T00: ml/model_card_A.md, data/README.md
7. backend/app/classifier.py::normalize() — chỉ đọc, chép nguyên văn hoặc import vào notebook
Không đọc task CLOSED, không đọc report cũ khác trừ khi cần đối chiếu dependency.

Nhiệm vụ: thực hiện T02 đúng Task Record, chỉ sửa file trong Allowed Files mục 6.
- Tạo ml/src/eval_utils.py với compute_metrics(y_true, y_pred) dùng chung; nếu refactor
  baselines.py sang dùng hàm này thì số trong baselines.csv không được đổi (≤ 0,001).
- Đo PhoBERT A, SVM, LR, NB trên cùng test UIT-ViSFD (2.224 dòng) với 2 kiểu đầu vào:
  text_norm và normalize(text_raw). Dùng đúng ba pipeline T01 tại
  MyDrive/thesis_results/baselines/{svm_A,lr_A,nb_A}.joblib, không train lại.
- AC-02: F1 tiêu cực PhoBERT A với text_norm ≈ 0,918 (lệch ≤ 0,005).
- AC-03: số SVM/LR/NB với text_norm khớp ml/results/baselines.csv dòng split=test.
- Ghi ml/results/comparison_A.csv đúng cột mục 4; 4 hình ma trận nhầm lẫn
  ml/results/figures/cm_<model>_A.png, nhãn trục tiếng Việt.
- ml/results/error_analysis.md: 20 câu sai mỗi mô hình đã phân nhóm + nhận xét đánh đổi
  độ chính xác / tốc độ / dung lượng.
- AC-06: đo thời gian CPU batch 1 cho cả 4 mô hình bằng CÙNG một phương pháp
  (time.perf_counter, không dùng process_time vì độ phân giải Windows thô — TODO-04 của T01),
  ghi rõ cấu hình máy. GPU chỉ để tham khảo.
- Xử lý hai TODO PO đã giao cho T02 (xem Open TODOs): hai checkpoint model A khác trọng số,
  normalize() khác text_utils.py — đo trên cùng test, trình bày số để PO chọn; không sửa backend.

Điểm cần lưu ý, không tự quyết:
- Không sửa backend/**, frontend/**; không đổi normalize().
- Không commit .joblib, model, CSV dữ liệu. Không thêm thư viện ngoài requirements hiện có;
  nếu cần matplotlib/seaborn cho hình mà chưa có trong danh sách được phép thì hỏi Tín trước.
- Nếu baselines.py cần thay đổi ngoài việc dùng eval_utils thì ghi vào report để PO quyết.

Gate: theo AGENT_RULES.md mục 3.2 (chạy lại notebook từ runtime mới, sai lệch ≤ 0,001; đúng split;
đúng normalize(); kết quả nhỏ vào ml/results/) và scope: git diff --name-only master...HEAD
chỉ chứa Allowed Files, không có .joblib, CSV dữ liệu, model, .env, *.db.
Tạo reports/<YYYY-MM-DD>/codex_implementation_T02_<YYYY-MM-DD>.md, có dòng "Đổi schema: Không",
bảng AC-01 → AC-06 kèm evidence, đường dẫn notebook trên Drive.
Cập nhật TASK_COORDINATION_ACTIVE.md: IN_PROGRESS -> CLAUDE_REVIEW.
Commit dạng [T02] mô tả. Không tự review, không tự PASS, không merge, không mở task kế tiếp.
Trả lời bằng tiếng Việt.
```
