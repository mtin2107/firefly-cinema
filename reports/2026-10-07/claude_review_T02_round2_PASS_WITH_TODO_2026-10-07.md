# Claude review T02 vòng 2 — PASS_WITH_TODO — 07/10/2026

## 1. Task
T02 — So sánh PhoBERT với mô hình truyền thống (`docs/tasks/T02.md`).

## 2. Reviewed commit
- Nhánh `task/T02-so-sanh-A`, HEAD `86a4e9a` (`[T02] Fix Claude review round 1`).
- Diff fix: `git diff af48f52..86a4e9a` (7 file, +466/−139). Diff tổng: `git diff master...task/T02-so-sanh-A`.
- Review trước: `reports/2026-10-05/claude_review_T02_FAIL_2026-10-05.md`. Fix report: `reports/2026-10-07/codex_fix_T02_round1_2026-10-07.md`.

## 3. Verdict
**PASS_WITH_TODO.** RF-01 và RF-02 đều **CLOSED**. Required Fixes còn mở: 0. Blocker: 0. Các TODO còn lại là quyết định của PO, không chặn task sau.

## 4. RF-01 verification — CLOSED

### A. 80 mẫu
- `error_analysis.md` có đúng **80 dòng ví dụ**, 4 model × 20, gồm 37 câu duy nhất.
- Danh sách index trong `REVIEWED_ERROR_INDICES` **giống hệt** 80 index của bản vòng 1 (`af48f52`), cả thứ tự. Claude so trực tiếp hai file, không có index nào bị chọn lại để làm đẹp kết quả.
- Mọi mẫu vẫn là prediction sai thật: `select_errors()` chỉ lấy dòng có `truth != prediction` rồi tra theo index. Lượt chạy notebook của Claude không raise lỗi nào.

### B. Manual review trong code
- `classify_error()` (substring/emoticon) **đã bị xóa**. Category cuối lấy từ `REVIEWED_ERROR_CATEGORIES` (dict cố định index → nhóm).
- Fail-fast: `ValueError` nếu index đã review không còn là prediction sai, nếu mẫu khác 20 dòng, hoặc nếu một nhóm vượt 5 ví dụ trong một model.
- Bảng đếm thực tế: tối đa 5 ví dụ mỗi ô, không ô nào vượt.

### C. Các index Claude nêu ở vòng 1 (đã đọc lại câu thật)
| Index | Nhãn thật → dự đoán | Câu (rút gọn) | Category mới | Nhận xét Claude |
|---:|---|---|---|---|
| 312 | 0 → 1 | "thật tuyệt khi một sản phẩm rẻ như này mà được điểm số cao" | Khác | Hợp lý. Câu khen, không có ý chê |
| 27 | 0 → 1 | Hỏi máy "nghe cái cốc… bị lỏng gì… có vấn đề j k anh" | Nhãn nhiễu/thiếu ngữ cảnh | Hợp lý. Câu hỏi mô tả sự cố mà nhãn 0, cần ngữ cảnh mới phán được |
| 1879 | 0 → 1 | "dùng thẻ nhớ thì chỉ dùng được 1 sim… :)))" | Khác | Hợp lý. Emoticon không phải châm biếm |
| 2221 | 0 → 1 | "Sản phẩm tốt 😊… =)))" | Khác | Hợp lý |
| 8 | 0 → 1 | "…Điểm yếu là cam trc thôi…" | Nhãn nhiễu/thiếu ngữ cảnh | Hợp lý. Có ý chê nhưng nhãn 0 |
| 58 | 0 → 1 | "Video màu sắc nhợt nhạt lắm… mong sớm sửa lỗi" | Nhãn nhiễu/thiếu ngữ cảnh | Hợp lý |
| 178 | 0 → 1 | "…chỉ có cảm biến vân tay kém" | Nhãn nhiễu/thiếu ngữ cảnh | Hợp lý |

Claude cũng đọc lướt 30 câu còn lại. Phần lớn gán hợp lý: 9/30/54/75 là phủ định; 38/41/64/187/227/1950/853 là chê một phần; 28/109/315/387/630/858 là từ lóng; 69/180 là nhãn nhiễu. Hai chỗ còn tranh luận được nhưng không chặn (TODO-R2-03):
- 72: phàn nàn ảnh bị vỡ, hỏi đổi trả, nhãn 0, được gán "Khác". Có thể xếp "Nhãn nhiễu".
- 136: "pin rõ chán… Còn cấu hình mượt đẹp", được gán "Khác". Có thể xếp "Chê một phần".

### D. Châm biếm
0 ví dụ ở cả 4 model, kèm giải thích không suy diễn từ emoticon. Chấp nhận được.

### E. Bảng tổng hợp
File ghi rõ đây là "mẫu cố định 20 lỗi/mô hình", "chỉ là số câu trong mẫu 20, không phải phân bố trên toàn bộ lỗi… không được dùng để suy rộng tỷ lệ nguyên nhân". Đạt.

### F. Trade-off
Bảng có F1 tiêu cực, CPU ms/câu, MiB:

| Model | F1 neg | ms/câu (commit) | MiB | Kỳ vọng |
|---|---:|---:|---:|---|
| PhoBERT A | 0,921600 | 45,716840 | 516,949776 | ~45,72 / ~516,95 ✓ |
| SVM | 0,891643 | 0,354897 | 0,474196 | ~0,35 / ~0,474 ✓ |
| LR | 0,890224 | 0,344190 | 0,474881 | ~0,34 / ~0,475 ✓ |
| NB | 0,874400 | 0,418245 | 0,630453 | ~0,42 / ~0,630 ✓ |

Tỉ lệ "chậm hơn 109–133×" tính đúng từ các số trên (45,72/0,4182 ≈ 109; 45,72/0,3442 ≈ 133). Có câu nói rõ latency tuyệt đối phụ thuộc tải máy và runtime. Đạt.

**RF-01 = CLOSED.** AC-05 đạt.

## 5. RF-02 verification — CLOSED
- `evaluate_phobert_checkpoint()` dùng cùng `compute_metrics()`, test, ngưỡng 0,5, `max_length=256` và hai input. Notebook cell 7 chỉ **đọc** `backend/models/phobert-binhluan`. Diff không chạm `backend/**`.
- Notebook do Claude chạy lại (batch 16 có padding) qua hai assert F1 backend (≤ 0,001). Macro-F1/accuracy ra 0,907022 / 0,908273 (`text_norm`) và 0,907526 / 0,908723 (`normalize`), khớp probe batch 1 của Claude ở vòng 1.
- Bảng hai checkpoint trong model card và fix report khớp **từng số** với kỳ vọng (gốc 0,916468 / 0,926790 / 0,921600 / 0,910492 / 0,911871 và 0,915538 / 0,924377 / 0,919936 / 0,908686 / 0,910072; backend 0,919290 / 0,916331 / 0,917808 / 0,907022 / 0,908273 và 0,921394 / 0,914722 / 0,918046 / 0,907526 / 0,908723).
- Model card ghi đủ 6 ý:
  - `comparison_A.csv` dùng checkpoint **gốc**.
  - Mốc ~0,918 thuộc checkpoint **backend**.
  - Hai bản khác trọng số (201/201 tensor).
  - Không tự chọn checkpoint chính thức.
  - Không thay model backend.
  - PO quyết định disposition.

**RF-02 = CLOSED.**

## 6. TODO-01 → TODO-04 (vòng 1) disposition
| TODO | Kiểm tra | Kết quả |
|---|---|---|
| TODO-01 runtime / latency | Fix report ghi interpreter `C:\Users\lemin\AppData\Local\Programs\Python\Python313\python.exe`, torch/transformers từ `backend\venv\Lib\site-packages` qua `PYTHONPATH`, lệnh PowerShell, phiên bản, "Không cài thêm thư viện". Claude chạy đúng cách này và thành công | **Đã xử lý.** Model card chưa chép phần interpreter/`PYTHONPATH` → TODO-R2-02 |
| TODO-02 metric lịch sử | Model card đổi nhãn thành "Kết quả lịch sử… chưa tái lập đầy đủ", **giữ nguyên** số 0,9176/0,9128/0,9141, tách riêng bảng đo lại có định danh checkpoint | **ACCEPT_LATER → PO** (cách trình bày trong luận văn) |
| TODO-03 notebook | Notebook có assert AC-03 (`max(baseline_diffs) == 0.0`) và in `AC-03_BASELINE_PARITY_OK`, `NOTEBOOK_EXECUTION_OK`. Claude chạy toàn bộ code cell trong process mới: thoát 0, in đủ hai marker | **Đã xử lý** |
| TODO-04 MiB | Model card, error analysis và report ghi `size_mb` giữ tên schema, giá trị theo MiB (1024²) | **Đã xử lý** |

## 7. Regression gates (Claude chạy độc lập)
Notebook chạy trong thư mục tạm: junction tới `data/`, `ml/artifacts/`, `backend/models/phobert-binhluan`. Không ghi đè `ml/results/` của repo.

| Gate | Kết quả |
|---|---|
| Dataset | 2.224 test; nhãn 0 = 981, nhãn 1 = 1.243 (assert notebook đạt) |
| `comparison_A.csv` | 8 hàng, 4 model × 2 input, đúng 10 cột |
| Metric so với commit | 5 cột metric + `ms_gpu` + `size_mb` **giống hệt** bản commit và bản vòng 1. Chỉ `ms_cpu` đổi (đo lại) |
| Baseline parity | max diff 0,000000 (assert AC-03 đạt) |
| Preprocessing | max \|Δ F1\| = 0,003217 (NB) < 0,01, "Không có blocker preprocessing" |
| Reproducibility | metric diff 0,000000 ≤ 0,001 |
| Confusion matrix | 4 PNG tạo lại **giống từng byte** với bản commit, prediction không đổi |
| Error analysis | phần thân (bảng nhóm + 80 dòng) tạo lại giống từng byte. Phần trade-off chỉ khác số latency |
| Latency lượt Claude | PhoBERT 45,49 · SVM 0,30 · LR 0,30 · NB 0,38 ms/câu. Cùng bậc với số commit |
| `py_compile ml/src/eval_utils.py` | Đạt |
| `git diff --check master...HEAD` | Sạch |
| Scope | Chỉ file allowlist. Không `backend/**`, `frontend/**`, model, joblib, data, `.env`, `.db` (grep name-only rỗng) |

## 8. Acceptance Criteria
| AC | Kết quả |
|---|---|
| AC-01 | **Đạt** — 8 hàng, đủ cột |
| AC-02 | **Đạt** — checkpoint gốc 0,921600, lệch 0,0036 ≤ 0,005. Model card đã định danh mốc 0,918 là checkpoint backend |
| AC-03 | **Đạt** — max diff 0, có assert trong notebook |
| AC-04 | **Đạt** — 4 PNG tiếng Việt, số khớp, không đổi |
| AC-05 | **Đạt** — RF-01 đã sửa thật: category rà tay, ghi rõ giới hạn mẫu, trade-off có số |
| AC-06 | **Đạt** — `perf_counter`, cùng methodology, cấu hình máy và runtime ghi rõ |

## 9. Required Fixes
0. RF-01, RF-02 CLOSED.

## 10. Blockers
Không có.

## 11. Remaining TODOs (không chặn)
| ID | TODO | Đề xuất disposition |
|---|---|---|
| TODO-R2-01 | PO chọn checkpoint chính thức (gốc 0,9216 hay backend 0,9178) cho luận văn và web | PO quyết định khi PO_REVIEW. Nếu đổi model backend thì cần task riêng, không làm trong T02 |
| TODO-R2-02 | Lệnh chạy (interpreter + `PYTHONPATH`) chỉ có trong fix report, chưa có trong model card / `HUONG_DAN.md`. Mục model card vẫn ghi "(05/10/2026)" dù latency đo 07/10 | ACCEPT_LATER — bổ sung khi cập nhật `HUONG_DAN.md` (T13) hoặc PO sửa nhanh |
| TODO-R2-03 | Category của index 72 ("Khác", có thể là "Nhãn nhiễu") và 136 ("Khác", có thể là "Chê một phần") còn tranh luận được | WONT_FIX hoặc PO chỉnh tay khi viết chương. Không ảnh hưởng kết luận |
| TODO-02 (vòng 1) | Metric lịch sử `phobert_A.json` chưa tái lập | ACCEPT_LATER → PO |

## 12. Final recommendation
- T02 `CLAUDE_REVIEW` → **`PO_REVIEW`**. Required Fixes = 0.
- Claude **không** merge, không PO_APPROVE, không CLOSE T02. Theo yêu cầu của prompt review vòng này, Claude **không mở task kế tiếp**: không đặt T04 `READY_FOR_HANDOFF`, dù AGENT_RULES 1.1 cho phép. Tín quyết định khi xong PO review.
- Việc của Tín:
  1. PO review, chốt TODO-R2-01 (checkpoint) và TODO-02 (số lịch sử).
  2. Merge `task/T02-so-sanh-A` vào `master`, gắn tag `ml-baselines` (AGENT_RULES mục 4).
  3. Mở task kế tiếp theo thứ tự bàn giao (T04).
- Probe và notebook run của Claude nằm ở scratchpad ngoài repo, junction đã gỡ. Repo không có file tạm.
