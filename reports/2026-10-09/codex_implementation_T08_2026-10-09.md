# Codex Implementation Report — T08 — 09/10/2026

## 1. Task và Git baseline

- Task: **T08 — Đo lệch miền điện thoại → phim**.
- PO authorization: `APPROVED / READY_FOR_HANDOFF` theo prompt bàn giao ngày 09/10/2026.
- Branch: `task/T08-lech-mien`.
- Baseline lúc pre-flight: `5cf4eb0b06d23df765ccb7fc17fdd31d2beef4ca` (`master` cùng trỏ tại commit này).
- T07 merge `434a489` là ancestor của baseline: **PASS**.
- Working tree trước implementation: sạch.
- Dependencies T02, T03: **DONE / CLOSED**.
- Đổi schema: **Không**.

## 2. Files Changed

- `ml/notebooks/T08_domain_shift.ipynb`
- `ml/results/domain_shift.csv`
- `ml/results/domain_shift_errors.md`
- `ml/results/figures/domain_shift_f1.png`
- `reports/2026-10-09/codex_implementation_T08_2026-10-09.md`
- `docs/TASK_COORDINATION_ACTIVE.md`

Không sửa `backend/**`, `frontend/**`, dữ liệu T03, `ml/src/eval_utils.py`, checkpoint hoặc file `.joblib`.

## 3. Dữ liệu và model/checkpoint đã sử dụng

### Dữ liệu

| Tập | Đường dẫn | Dòng | Nhãn 0/1 | SHA-256 |
|---|---|---:|---:|---|
| Phone test | `data/uit-visfd/processed/test.csv` | 2.224 | 981 / 1.243 | `be74cfbf01a39dad7c7886b947d2eb4734135b0b1525304e8974be666f0e2fae` |
| Movie test | `data/phim/movie_test.csv` | 149 | 48 / 101 | `5af8f616429e325f89bef723e4d0fdf867b7cd7d1c777eb30bb024b18a95c660` |

Nhãn `0 = bình thường`, `1 = tiêu cực`. Cả hai tập không thiếu text/nhãn. Notebook không đọc `movie_train.csv`.

### Model

| Model | Artifact | SHA-256 |
|---|---|---|
| PhoBERT A research canonical | `ml/artifacts/phobert_A_best/model.safetensors` | `121c2cbc9131a5b15464b452339c0a077f6ff20c09f52f05525c29466b1b75b7` |
| SVM A | `ml/artifacts/baselines/svm_A.joblib` | `51d061fbb3f682fd28a11edc1d438cf46c67d67eae4861a76690dc3d3a3e272c` |
| Logistic Regression A | `ml/artifacts/baselines/lr_A.joblib` | `1760b2eb8d8b6c9cc48aa7496d48062e4cc230998caad84e2033b84a402d67db` |
| Naive Bayes A | `ml/artifacts/baselines/nb_A.joblib` | `26f2235789a8ebb06d2f1b689ef95ebe7138de6a6f23d6a49451831474ef1510` |

Bảng so sánh chính chỉ dùng checkpoint research canonical đã chốt tại T02. Checkpoint backend `backend/models/phobert-binhluan/model.safetensors` (SHA-256 `15d4658955ba1f8e07c8f578bf53aa0a50a11ec7b27403c264985e55cd41d470`) chỉ được dùng đối chiếu câu bắt buộc, không trộn vào metric chính.

## 4. Bảng metric và delta

Công thức: `delta_f1_neg = F1_neg(phone) - F1_neg(test_set)`.

- Dòng phone có delta `0`.
- Delta movie dương: F1 giảm khi chuyển từ phone sang movie.
- Delta movie âm: F1 movie cao hơn phone.

| Model | Test set | Precision neg | Recall neg | F1 neg | Macro-F1 | Delta F1 neg |
|---|---|---:|---:|---:|---:|---:|
| PhoBERT A | phone | 0,915538 | 0,924377 | 0,919936 | 0,908686 | 0,000000 |
| PhoBERT A | movie | 0,962963 | 0,772277 | 0,857143 | 0,816502 | 0,062793 |
| SVM A | phone | 0,883648 | 0,904264 | 0,893837 | 0,877855 | 0,000000 |
| SVM A | movie | 0,787037 | 0,841584 | 0,813397 | 0,687597 | 0,080440 |
| Logistic Regression A | phone | 0,882261 | 0,904264 | 0,893127 | 0,876910 | 0,000000 |
| Logistic Regression A | movie | 0,781818 | 0,851485 | 0,815166 | 0,683445 | 0,077961 |
| Naive Bayes A | phone | 0,878324 | 0,876911 | 0,877617 | 0,861415 | 0,000000 |
| Naive Bayes A | movie | 0,772727 | 0,841584 | 0,805687 | 0,667211 | 0,071930 |

Cả bốn delta movie nằm trong `[0,062793; 0,080440]`, đều lớn hơn `0,03`; **không kích hoạt cảnh báo xem lại cách trình bày mục tiêu T09**.

## 5. Acceptance Criteria

| AC | Kết quả DEV | Bằng chứng |
|---|---|---|
| AC-01 | **PASS** | Notebook import trực tiếp `backend.app.classifier.normalize`; so sánh 10 câu phone + 10 câu movie với contract `eval_utils.normalize`: `20/20` giống hệt. Không sửa source. |
| AC-02 | **PASS** | `domain_shift.csv` có chính xác `8` dòng, `4` model × `2` test set, đủ 7 cột yêu cầu. |
| AC-03 | **PASS** | So với các dòng `input=normalize` trong `comparison_A.csv`; sai khác metric phone lớn nhất `4,915526951032589e-07`, nhỏ hơn `0,001`. |
| AC-04 | **PASS** | Câu `Phim dài lê thê, xem mà mệt` không có trong movie test và được chạy như test riêng. Research PhoBERT: nhãn `0`, score `0,387731`; backend PhoBERT: nhãn `0`, score `0,012468` (API backend làm tròn `0,0125`). SVM: `1/0,501091`; LR: `1/0,508498`; NB: `0/0,464394`. |
| AC-05 | **PASS** | PNG `1620×972`, 47.756 byte; `domain_shift_errors.md` có đúng 20 ca thật, mỗi ca có nhãn, model sai, dự đoán/score và lý do. Phân nhóm: từ vựng phim 5, nhịp/nội dung 6, châm biếm 4, rạp/dịch vụ 5. |

Đây là kết quả self-check của implementer, không phải review độc lập hay PO approval.

## 6. Reproducibility Evidence

- Seed: Python/NumPy/PyTorch đều `42`; PyTorch deterministic algorithms được bật với `warn_only=True`.
- Runtime: Python `3.13.2`, torch `2.11.0+cpu`, transformers `5.18.0`, scikit-learn `1.7.2`, pandas `2.2.3`, NumPy `2.2.4`, joblib `1.5.2`, matplotlib `3.10.1`.
- Không cài thêm thư viện.
- Notebook đã được chạy lại từ một Python process sạch trên CPU, lần lượt chạy tất cả code cell; marker cuối: `NOTEBOOK_EXECUTION_OK` và `CLEAN_NOTEBOOK_RUN_OK`.
- Lượt clean-run tái tạo đúng 8 metric nêu trên. So với lượt đo implementation trước đó, sai lệch metric quan sát được là `0`, nhỏ hơn gate `0,001`.
- Hash dữ liệu/model được assert/ghi ngay trong notebook.
- `movie_train.csv` không được đọc; không fit, train hay chọn hyperparameter.

### Chạy lại trên Colab (tùy chọn, không phải blocker)

Môi trường local CPU đã tạo đủ evidence thật, nên PO không bắt buộc phải chạy Colab trước Claude review. Nếu muốn xác minh trên Colab:

1. Mount Drive/clone repo và đặt dữ liệu + artifact ngoài Git đúng các đường dẫn ở mục 3.
2. Chọn runtime có các phiên bản tương thích; không cần GPU để đúng metric, GPU chỉ giúp nhanh hơn.
3. Mở `ml/notebooks/T08_domain_shift.ipynb`, chạy `Runtime > Restart and run all`.
4. Xác minh các marker `AC-01...`, `AC-02...`, `AC-03...`, `AC-04...`, `AC-05...`, `NOTEBOOK_EXECUTION_OK`; metric sai lệch không quá `0,001`.
5. Không upload/commit checkpoint, `.joblib` hoặc dữ liệu lớn vào Git.

## 7. Final Gates

| Gate | Kết quả | Evidence |
|---|---|---|
| Seed cố định | PASS | `42` cho Python/NumPy/PyTorch. |
| Clean notebook run | PASS | Tất cả code cell chạy xong; hai marker OK. |
| Tái lập ≤ 0,001 | PASS | Hai lượt đo cho cùng metric 6 chữ số; phone parity max `4,92e-07`. |
| Đúng preprocessing | PASS | Backend `normalize()` parity 20/20. |
| Không dùng movie test để chọn hyperparameter | PASS | Chỉ inference artifact đóng băng. |
| Không đọc movie train | PASS | Không có code/path đọc `movie_train.csv`. |
| Artifact gate | PASS | CSV 8×7; Markdown 20 lỗi; PNG hợp lệ; notebook JSON/code syntax hợp lệ. |
| Scope allowlist | PASS | Mọi file thay đổi nằm trong exact allowlist. |
| Secret/model/data scan | PASS | Không `.env`, database, checkpoint, `.joblib`, dữ liệu lớn hay secret pattern mới. |
| Large-file scan | PASS | Không file thay đổi nào vượt 10 MiB; PNG 47.756 byte. |

## 8. Scope và Security

- Diff chỉ gồm notebook, ba result artifact, report và coordination đúng allowlist.
- Dữ liệu test, model và artifact baseline chỉ đọc; hash được ghi lại để truy vết.
- Không thay production `normalize()`, backend/frontend, schema hay dependency.
- Không có secret, credential, `.env`, database hoặc artifact model trong thay đổi Git.

## 9. Blockers, Required Fixes, TODO

- Blocker implementation: **0**.
- Required Fix đã biết: **0**.
- TODO chặn Claude review: **0**.
- T09 giữ **PLANNED / NOT AUTHORIZED**.
- Full Definition of Done chưa thể kết luận cho tới khi Claude review và PO approve; implementer không tự PASS task.

## 10. Handoff

- T08 chuyển `IN_PROGRESS → CLAUDE_REVIEW` sau commit implementation.
- Claude cần chạy gate độc lập, ưu tiên tái lập SVM/LR/NB trên CPU, kiểm phone parity, schema CSV, 20 ca lỗi và consistency giữa CSV/PNG/report.
- PO không cần chạy Colab để gỡ blocker; Colab run-all là bước xác minh tùy chọn theo hướng dẫn mục 6.
- Không review, không PO approve, không merge, không đóng T08 và không mở T09 trong handoff này.
