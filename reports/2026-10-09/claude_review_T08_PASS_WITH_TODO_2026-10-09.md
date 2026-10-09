# Claude Review — T08 — Đo lệch miền điện thoại → phim — PASS_WITH_TODO — 09/10/2026

| Trường | Giá trị |
|---|---|
| Task | T08 — Đo lệch miền điện thoại → phim |
| Reviewer | Claude (Independent Reviewer / Tester) |
| Nhánh | `task/T08-lech-mien` |
| HEAD được review | `47e044e` `[T08] Measure phone-to-movie domain shift` |
| Baseline | `master` = `5cf4eb0`; T07 merge `434a489` là ancestor của HEAD (PASS) |
| Report Codex | `reports/2026-10-09/codex_implementation_T08_2026-10-09.md` |
| Kết quả | **PASS_WITH_TODO** — AC 5/5 PASS, RF 0, TODO 5 (không chặn) |

## 1. Source Review

Diff thật `git diff --name-status master...HEAD` (1 commit `47e044e`):

| Trạng thái | File | Allowlist T08 |
|---|---|---|
| M | `docs/TASK_COORDINATION_ACTIVE.md` | Có |
| A | `ml/notebooks/T08_domain_shift.ipynb` | Có |
| A | `ml/results/domain_shift.csv` | Có |
| A | `ml/results/domain_shift_errors.md` | Có |
| A | `ml/results/figures/domain_shift_f1.png` | Có |
| A | `reports/2026-10-09/codex_implementation_T08_2026-10-09.md` | Có |

- `git diff --check master...HEAD`: sạch. Working tree sạch trước review.
- Không đụng `backend/**`, `frontend/**`, `ml/src/**`, dữ liệu T03, `normalize()`, thư viện.
- Notebook (10 cell, nbformat 4.5, 0 output đã lưu, mọi code cell parse được):
  - Cell 1: import `normalize`/`compute_metrics` từ `ml/src/eval_utils.py` và `normalize`/registry từ `backend.app.classifier`; seed 42 cho Python/NumPy/PyTorch.
  - Cell 3: assert tồn tại artifact, kích thước và phân bố nhãn hai tập; so sánh `normalize()` backend với contract `eval_utils` trên 20 câu; in SHA-256.
  - Cell 5: chỉ `predict`/`predict_proba`/`decision_function` trên artifact đóng băng; PhoBERT research ở `eval()` + `torch.no_grad()`, `max_length=256`, softmax lớp 1, ngưỡng 0,5; `delta = F1(phone) − F1(test_set)`; assert parity với `comparison_A.csv` (`input == 'normalize'`) ≤ 0,001.
  - Cell 6: biểu đồ cột F1 tiêu cực 4 model × 2 miền; cảnh báo nếu delta < 0,03.
  - Cell 8–9: câu bắt buộc, 20 lỗi chọn thủ công theo ID, mỗi lỗi assert có ít nhất một model sai; ghi `domain_shift_errors.md`.
- Không có `fit`, `fit_transform`, `train.csv`, `dev.csv` hay `movie_train` trong code (chỉ xuất hiện trong câu markdown "không đọc `movie_train.csv`").

## 2. Acceptance Criteria

| AC | Kết quả | Bằng chứng độc lập |
|---|---|---|
| AC-01 Normalize parity | **PASS** | Notebook import trực tiếp `backend.app.classifier.normalize` và so với bản chép `eval_utils.normalize` trên 20 câu (10 phone + 10 movie). Claude kiểm thêm: 20 câu chọn ngẫu nhiên (seed 2026) giống 20/20, và **toàn bộ 2.373 câu** (2.224 phone + 149 movie) lệch **0**. Input của mọi model là `normalize(text)`; không có preprocessing ẩn nào khác. |
| AC-02 Domain shift CSV | **PASS** | 8 dòng × 7 cột đúng tên/thứ tự T08.md mục 4, 0 NaN. Claude tính lại P/R/F1/Macro-F1 thủ công từ confusion matrix (không dùng `compute_metrics`): lệch tối đa so với CSV **4,92e-07**. `delta_f1_neg` đúng công thức; dòng phone = 0. |
| AC-03 Phone parity | **PASS** | Tính lại độc lập so với dòng `input=normalize` của `comparison_A.csv`: lệch tối đa **4,915526951032589e-07** (≤ 0,001), trùng giá trị Codex báo. Phone dùng `text_raw → normalize`, đúng cách T02 tạo dòng `normalize`. |
| AC-04 Câu "Phim dài lê thê, xem mà mệt" | **PASS** | Câu không có trong `movie_test.csv` (Claude kiểm), được chấm như ca riêng. Tái lập: research 0/0,387731; backend checkpoint 0/0,012468 (registry trả 0,0125 do `round(…, 4)`); SVM 1/0,501091; LR 1/0,508498; NB 0/0,464394 — trùng 100% report Codex. Xem mục 2.1 về "mâu thuẫn" với T07 TODO-01. |
| AC-05 Figure + 20 lỗi | **PASS** | PNG 1620×972 hợp lệ, hai cột mỗi model (phone/movie), nhãn số khớp CSV làm tròn 3 chữ số. `domain_shift_errors.md` có đúng 20 dòng, 20 ID duy nhất, đều có trong `movie_test.csv`; Claude đối chiếu từng dòng với dự đoán thật: nhãn gold, câu gốc, danh sách model sai, nhãn dự đoán và score 4 model đều khớp (0 mismatch, sai số score ≤ 1e-5). Phân nhóm: nhịp/nội dung 6, từ vựng phim 5, rạp/dịch vụ 5, châm biếm 4. Không dùng tập train. |

### 2.1. Câu "lê thê": không có mâu thuẫn với T07 TODO-01

Đây là **hai câu khác nhau**, cùng hai checkpoint và cùng cách đo:

| Câu | Research `phobert_A_best` (normalize) | Backend `phobert-binhluan` (normalize) | Nguồn ghi trước đó |
|---|---:|---:|---|
| "Phim dài lê thê, xem mà mệt" (T08 AC-04) | 0,387731 → 0 | 0,012468 → 0 | T00 review: 0,388 / 0,012; BOI_CANH mục 5: 0,01 |
| "Phim dài lê thê, nửa đầu buồn ngủ thật sự." (T07 TODO-01) | 0,960167 → 1 | 0,048508 → 0 | T07 review: 0,9602 / 0,0485 |

- Checkpoint: research SHA-256 `121c2cbc…b75b7`, backend `15d46589…1d470` — trùng hash Codex ghi; registry backend nạp đúng `backend/models/phobert-binhluan`.
- Tokenizer (`tokenizer_config.json`, `vocab.txt`, `bpe.codes`) giống từng byte giữa hai checkpoint; `config.json` chỉ khác ở chỗ backend có thêm `id2label {0: binh_thuong, 1: tieu_cuc}`. Nhãn 1 = tiêu cực nhất quán (đã được T02 xác nhận qua F1 phone).
- Cả hai đường đo dùng `normalize()`, `max_length=256`, softmax lấy lớp 1, model ở `eval()` (Claude kiểm `model.training == False`).
- **Bằng chứng tái lập chính thức cho T08:** dòng research canonical 0,387731 (bảng chính); dòng backend chỉ là tham chiếu, không đưa vào metric.
- Ghi chú: hai câu này có điểm research trái ngược nhau (0,39 và 0,96). Khi viết khóa luận cần nêu rõ câu nào, tránh gộp thành "câu lê thê".

## 3. Definition of Done (`_TEMPLATE.md` mục 9)

| Mục | Trạng thái |
|---|---|
| Toàn bộ AC đạt, có bằng chứng trong report | MET (5/5) |
| Gate `AGENT_RULES.md` mục 3.2 | MET cho phần CPU (xem mục 4); "đường dẫn notebook trên Drive" chưa có → TODO-04 |
| Không có file ngoài allowlist | MET |
| Tài liệu liên quan (ARCHITECTURE/CONG_NGHE/HUONG_DAN) | Không áp dụng — không đổi kiến trúc, thư viện, cách chạy web |
| Claude PASS/PASS_WITH_TODO, Tín APPROVED | Claude PASS_WITH_TODO; chờ PO |

## 4. Independent Tests / Gates

Môi trường: Windows, CPU, Python 3.13.2 hệ thống (pandas 2.2.3, NumPy 2.2.4, scikit-learn 1.7.2, joblib 1.5.2, matplotlib 3.10.1) + `PYTHONPATH=backend\venv\Lib\site-packages` (torch 2.11.0+cpu, transformers 5.18.0) — cùng cách chạy Codex đã ghi ở T02 fix round 1. Không cài thêm thư viện.

| Gate | Kết quả | Chi tiết |
|---|---|---|
| Notebook/code integrity | PASS | JSON hợp lệ, code cell parse được; chạy lại **nguyên văn** 4 code cell (chỉ đổi 3 đường dẫn ghi ra scratchpad) với cwd = gốc repo: đủ marker `AC-01…AC-05`, `WARNING_DELTA_LT_0.03: none`, `NOTEBOOK_EXECUTION_OK`. |
| Tái lập artifact | PASS | `domain_shift.csv`, `domain_shift_errors.md`, `domain_shift_f1.png` tái tạo **giống từng byte** (`cmp`) với bản đã commit. |
| Data/model identity | PASS | 7 SHA-256 trùng report (mục 5). |
| Normalize parity | PASS | 20/20 notebook, 20/20 ngẫu nhiên, 2.373/2.373 toàn bộ. |
| Metric parity | PASS | Lệch tối đa 4,92e-07 so với CSV và với `comparison_A.csv`. |
| CPU reproducibility SVM/LR/NB | PASS | Tính lại độc lập bằng script riêng, khớp CSV. |
| PhoBERT A research (CPU) | PASS | Chạy được trên CPU, khớp CSV; batch 1 vs batch 16 trên movie lệch score tối đa 7,7e-06, 0 nhãn đổi (padding không ảnh hưởng). |
| Không đọc movie_train / không fit | PASS | Grep code notebook. |
| Scope | PASS | 6/6 file trong allowlist. |
| Secret scan | PASS | Chỉ hit giả (`tokenizer`, chữ "secret pattern" trong report). |
| Large-file scan | PASS | File lớn nhất PNG 47.756 byte; không `.env`, `.db`, `.joblib`, `.safetensors`, dữ liệu. `git ls-files` chỉ có `data/.gitkeep`, `data/README.md`. |
| `git diff --check` | PASS | Sạch. |
| Portability notebook | **Ghi chú** | Mở notebook trong Jupyter/VS Code với cwd mặc định `ml/notebooks/` → `StopIteration` ở cell 1. Kế thừa nguyên mẫu T02 (đã CLOSED) → TODO-03, không phải RF. |

Probe tạm (`probe_t08.py`, `run_nb.py`, output) chỉ nằm trong scratchpad ngoài repo; working tree sạch trước khi viết report này.

## 5. Data/Model Identity

| Đối tượng | Đường dẫn | Kiểm tra | SHA-256 |
|---|---|---|---|
| Phone test | `data/uit-visfd/processed/test.csv` | 2.224 dòng, 981/1.243 | `be74cfbf…0e2fae` ✓ |
| Movie test | `data/phim/movie_test.csv` | 149 dòng, 48/101, 0 ID trùng | `5af8f616…95c660` ✓ |
| PhoBERT A research (canonical T02) | `ml/artifacts/phobert_A_best/model.safetensors` | `eval()` | `121c2cbc…b75b7` ✓ |
| PhoBERT backend (chỉ tham chiếu) | `backend/models/phobert-binhluan/model.safetensors` | | `15d46589…1d470` ✓ |
| SVM A | `ml/artifacts/baselines/svm_A.joblib` | classes [0, 1] | `51d061fb…72c` ✓ |
| LR A | `ml/artifacts/baselines/lr_A.joblib` | classes [0, 1] | `1760b2eb…7db` ✓ |
| NB A | `ml/artifacts/baselines/nb_A.joblib` | classes [0, 1] | `26f22357…510` ✓ |

## 6. Metric Reproducibility

Confusion matrix Claude tính lại (nhãn 1 = tiêu cực):

| Model | Miền | TP | FP | FN | TN | P_neg | R_neg | F1_neg | Macro-F1 | ΔF1_neg |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| PhoBERT A | phone | 1149 | 106 | 94 | 875 | 0,915538 | 0,924377 | 0,919936 | 0,908686 | 0 |
| PhoBERT A | movie | 78 | 3 | 23 | 45 | 0,962963 | 0,772277 | 0,857143 | 0,816502 | 0,062793 |
| SVM A | phone | 1124 | 148 | 119 | 833 | 0,883648 | 0,904264 | 0,893837 | 0,877855 | 0 |
| SVM A | movie | 85 | 23 | 16 | 25 | 0,787037 | 0,841584 | 0,813397 | 0,687597 | 0,080440 |
| LR A | phone | 1124 | 150 | 119 | 831 | 0,882261 | 0,904264 | 0,893127 | 0,876910 | 0 |
| LR A | movie | 86 | 24 | 15 | 24 | 0,781818 | 0,851485 | 0,815166 | 0,683445 | 0,077961 |
| NB A | phone | 1090 | 151 | 153 | 830 | 0,878324 | 0,876911 | 0,877617 | 0,861415 | 0 |
| NB A | movie | 85 | 25 | 16 | 23 | 0,772727 | 0,841584 | 0,805687 | 0,667211 | 0,071930 |

Tất cả 40 giá trị số khớp CSV (lệch tối đa 4,92e-07 ≤ 0,001). **VERIFIED:** cả 4 model trên CPU. **NOT INDEPENDENTLY VERIFIED:** không có — PhoBERT không cần GPU để tái lập.

### 6.1. Nhận xét phương pháp (bằng chứng bổ sung, không thay đổi kết quả)

- **Tỷ lệ nhãn lệch giữa hai miền:** movie 67,8% tiêu cực, phone 55,9%. Bộ phân loại hằng "mọi câu đều tiêu cực" có F1_neg **0,808** trên movie (0,717 trên phone). F1_neg movie của ba baseline (0,806–0,815) xấp xỉ mức hằng này; Macro-F1 cho thấy lệch miền rõ hơn nhiều: Δ Macro-F1 = PhoBERT 0,092, SVM 0,190, LR 0,193, NB 0,194. → TODO-01.
- **Tập movie nhỏ (149 câu):** bootstrap 2.000 lần (seed 42, lấy mẫu lại độc lập hai tập), khoảng tin cậy 95% của ΔF1_neg: PhoBERT [0,010; 0,123], SVM [0,023; 0,140], LR [0,022; 0,139], NB [0,013; 0,136]; P(Δ ≤ 0) ≤ 1% cho cả 4 model. Hướng giảm F1 là vững; độ lớn có cận dưới < 0,03 → TODO-02.
- **20 lỗi chọn có chủ đích** (17 FN / 3 FP; tổng lỗi movie: PhoBERT 26, SVM 39, LR 39, NB 41). File đã ghi rõ không phải ước lượng tần suất — chấp nhận. Một số câu gold có thể gây tranh luận (ví dụ MOV0479 "phim ảo vãi" nhãn 1, "ảo" trong tiếng lóng có thể mang nghĩa khen); đây là nhãn T03 đã đóng, không sửa trong T08.
- **Không có dấu hiệu chọn metric/câu làm lệch kết luận:** metric chính (F1_neg) theo đúng T08.md; Macro-F1 cũng được ghi trong CSV và còn mạnh hơn kết luận.

**Kết luận phương pháp:** đủ bằng chứng để khẳng định **có lệch miền phone → movie** ở cả 4 model (ΔF1_neg 0,063–0,080 > 0,03; Δ Macro-F1 0,09–0,19), đủ làm lý do cho T09. Cần trình bày kèm giới hạn ở TODO-01/02.

## 7. Architecture / Security

- Đúng cây thư mục ARCHITECTURE: notebook ở `ml/notebooks/`, kết quả nhỏ ở `ml/results/` và `ml/results/figures/`.
- Không đổi production code, `normalize()`, schema, dependency hay checkpoint runtime. Notebook chỉ đọc artifact.
- Không có đường dẫn `D:\` trong diff. Không có secret, `.env`, database, model, dữ liệu trong Git.
- Notebook import registry backend (`backend.app.classifier.classifier`) — việc này nạp cả ba baseline và checkpoint backend khi chạy, chỉ đọc; chấp nhận được cho mục đích đối chiếu.

## 8. Scope Integrity

6/6 file trong allowlist T08 mục 6; không file cấm mục 7. `docs/tasks/T08.md` không bị sửa (giữ snapshot). Không scope deviation.

## 9. Required Fixes

**Không có.** Open Required Fixes: 0.

## 10. TODO (không chặn; chờ PO disposition)

| ID | Mức | Nội dung | Đề xuất |
|---|---|---|---|
| TODO-01 | Medium (khóa luận) | F1_neg movie bị đẩy lên do tỷ lệ tiêu cực cao (67,8% vs 55,9%): bộ phân loại hằng đạt 0,808 trên movie; baseline 0,806–0,815. Chỉ báo ΔF1_neg sẽ **đánh giá thấp** mức lệch miền của baseline. | Khi viết khóa luận/T09: trình bày ΔF1_neg kèm Δ Macro-F1 (0,09–0,19) và mức tham chiếu "mọi câu tiêu cực"; không cần chạy lại T08. |
| TODO-02 | Low (khóa luận) | Movie test 149 câu; CI 95% của ΔF1_neg có cận dưới 0,010–0,023, tức thấp hơn ngưỡng 0,03 ở T08.md mục 13. Hướng lệch vững (P(Δ≤0) ≤ 1%). | Ghi giới hạn cỡ mẫu trong khóa luận; T09 dùng cùng `movie_test.csv` để so A/B công bằng. |
| TODO-03 | Low (tái lập) | `PROJECT_ROOT` chỉ tìm được khi cwd là gốc repo hoặc `/content/firefly-cinema`. Mở bằng Jupyter/VS Code (cwd mặc định `ml/notebooks/`) hoặc Colab qua Drive mount → `StopIteration` ở cell 1. Kế thừa T02. Report Codex mục 6 hướng dẫn "Mount Drive/clone repo" nhưng không nói điều kiện cwd. | Khi PO chạy lại: `cd` về gốc repo trước khi mở kernel, hoặc clone vào `/content/firefly-cinema`. Notebook T09 nên dò thêm `Path.cwd().parents`. |
| TODO-04 | Low (bằng chứng) | Notebook commit không kèm output; hash dữ liệu/model chỉ được **in**, không assert (report ghi "assert/ghi"); chưa có đường dẫn notebook trên Drive (AGENT_RULES 3.2 "Bằng chứng"); report T08 không ghi cách ghép môi trường (Python hệ thống + `PYTHONPATH` venv). | PO chọn: chấp nhận (Claude đã tái lập byte-identical) hoặc yêu cầu bổ sung ở report sau. |
| TODO-05 | Info (T09/T10) | Điểm PhoBERT rất nhạy với `normalize()`: câu AC-04 research 0,977 trên text gốc → 0,388 sau normalize; backend 0,458 → 0,012. T10 AC-02 yêu cầu model B chấm câu này ≥ 0,5 (qua `normalize()`). | Không sửa `normalize()` (quy tắc dự án). T09 cần train/eval với đúng `normalize()` để khớp runtime; ghi nhận cho T09/T10. |

## 11. Final Decision

**PASS_WITH_TODO.**

- AC: **5/5 PASS**. DoD: MET phần Claude; chờ PO.
- Required Fixes: **0**. Blocker: **0**. TODO: 5 (đều không chặn).
- Tái lập: 4/4 model trên CPU khớp ≤ 4,92e-07; 3 artifact tái tạo giống từng byte.

## 12. Workflow Transition

- T08: `CLAUDE_REVIEW` → **`PO_REVIEW`**.
- Claude không PO approve, merge, tag hay đóng T08.
- **T09 giữ `PLANNED / NOT AUTHORIZED`.** Theo chỉ thị PO cho lượt review này (ưu tiên hơn AGENT_RULES mục 1.1, giống tiền lệ T07), Claude không đặt T09 `READY_FOR_HANDOFF` và không soạn prompt bàn giao T09. Khi PO authorize: T09 phụ thuộc T08; nên đọc kèm TODO-01/02/05.
- Nhắc Tín: PO review, disposition TODO-01→05, rồi tự merge `task/T08-lech-mien` vào `master` nếu duyệt (T08 không có tag mốc theo AGENT_RULES mục 4).
