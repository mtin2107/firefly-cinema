# Báo cáo fix T02 round 1 — 07/10/2026

## Task

T02 — So sánh PhoBERT với mô hình truyền thống, nhánh `task/T02-so-sanh-A`.

## Fix Round

Round 1, chỉ xử lý RF-01 và RF-02 của review T02.

## Claude verdict trước fix

`FAIL` tại commit `af48f52`: 2 Required Fix mức Medium, 0 blocker.

## RF-01 status

Đã xử lý.

## RF-01 evidence

- Loại bỏ `classify_error()` dựa trên substring/emoticon khỏi category cuối cùng.
- Giữ cố định 20 prediction sai/mô hình từ implementation đầu để review có thể đối chiếu; tổng cộng 80 dòng, 37 câu duy nhất do nhiều mô hình có thể sai cùng câu.
- Rà thủ công từng câu duy nhất và lưu category đã review bằng `REVIEWED_ERROR_CATEGORIES`; mọi lần sinh file sau dùng đúng index/category đã duyệt.
- `select_errors()` fail-fast nếu index không còn là prediction sai, nếu mẫu không đủ 20 hoặc nếu một category vượt 5 ví dụ.
- `error_analysis.md` ghi rõ đây là số trong mẫu 20, không phải phân bố toàn bộ lỗi; không suy rộng tỷ lệ nguyên nhân.
- Nhóm châm biếm giữ 0 ở cả bốn mẫu vì không có câu đủ bằng chứng ngữ cảnh; `:)))`/`=)))` không còn tự động bị coi là châm biếm.
- Những trường hợp review nêu đã sửa: index 312 → `Khác`; 27 → `Nhãn nhiễu/thiếu ngữ cảnh`; 1879/2221 → `Khác`; 8/58/178 → `Nhãn nhiễu/thiếu ngữ cảnh`.
- Gate tự động: đúng 20 mẫu/model, 80 dòng tổng, tối đa 5 ví dụ/category.

## RF-02 status

Đã xử lý phần đo và định danh; chờ PO quyết định disposition checkpoint, không tự chọn.

## RF-02 evidence

- Codex chạy lại cả hai checkpoint bằng cùng `compute_metrics()`, cùng UIT-ViSFD test, nhãn `1 = tiêu cực`, ngưỡng `0,5`, hai input `text_norm` và `normalize(text_raw)`.
- Notebook có cell chỉ đọc `backend/models/phobert-binhluan`; không sửa `backend/**`.
- `ml/model_card_A.md` ghi rõ `comparison_A.csv` dùng checkpoint gốc `ml/artifacts/phobert_A_best`.
- Mốc khoảng `0,918` được định danh là checkpoint backend.
- Hai checkpoint khác trọng số; không checkpoint nào tự động thay checkpoint còn lại; PO quyết định sau review.

## Bảng hai checkpoint

| Checkpoint | Input | Precision neg | Recall neg | F1 neg | Macro-F1 | Accuracy |
|---|---|---:|---:|---:|---:|---:|
| Gốc — `ml/artifacts/phobert_A_best` | `text_norm` | 0,916468 | 0,926790 | 0,921600 | 0,910492 | 0,911871 |
| Gốc — `ml/artifacts/phobert_A_best` | `normalize(text_raw)` | 0,915538 | 0,924377 | 0,919936 | 0,908686 | 0,910072 |
| Backend — `backend/models/phobert-binhluan` | `text_norm` | 0,919290 | 0,916331 | 0,917808 | 0,907022 | 0,908273 |
| Backend — `backend/models/phobert-binhluan` | `normalize(text_raw)` | 0,921394 | 0,914722 | 0,918046 | 0,907526 | 0,908723 |

Các số Codex tự đo khớp số tham chiếu Claude tới 6 chữ số thập phân.

## Error analysis methodology mới

1. Lấy đúng 20 index/model đã xuất hiện trong report đầu, không đổi prediction hoặc săn ví dụ mới từ test.
2. Đọc thủ công 37 câu duy nhất, xét nhãn thật/dự đoán và ngữ cảnh đầy đủ.
3. Gán một trong sáu category T02; category cuối được lưu theo index, không lấy trực tiếp từ rule.
4. Đếm category chỉ trong mẫu; mỗi category tối đa 5 ví dụ/model. Nếu ít hơn 5, bảng ghi đúng số tìm thấy; không bịa thêm.
5. Không dùng phân tích lỗi để đổi model, threshold, hyperparameter hoặc preprocessing.

## Trade-off numbers

| Model (`text_norm`) | F1 negative | CPU ms/câu | Dung lượng (MiB) |
|---|---:|---:|---:|
| PhoBERT A gốc | 0,921600 | 45,716840 | 516,949776 |
| SVM | 0,891643 | 0,354897 | 0,474196 |
| Logistic Regression | 0,890224 | 0,344190 | 0,474881 |
| Naive Bayes | 0,874400 | 0,418245 | 0,630453 |

PhoBERT lớn khoảng 517 MiB so với 0,47–0,63 MiB của baseline và chậm hơn khoảng 109–133 lần trên CPU batch 1 của lượt đo cuối, xấp xỉ hai bậc độ lớn. Latency tuyệt đối phụ thuộc tải máy/runtime; nên chú trọng thứ tự và tỉ lệ hơn số tuyệt đối.

Tên cột `size_mb` được giữ theo schema T02; giá trị thực tế tính theo MiB (`1024²` byte).

## TODO-01 disposition

Đã xử lý trong vòng fix. Runtime thực tế:

- Interpreter: `C:\Users\lemin\AppData\Local\Programs\Python\Python313\python.exe` (Python 3.13.2).
- sklearn/pandas/joblib từ Python hệ thống; torch/transformers từ `backend\venv\Lib\site-packages` qua `PYTHONPATH`.
- Lệnh PowerShell:

```powershell
$env:PYTHONPATH = "C:\Projects\firefly-cinema\backend\venv\Lib\site-packages"
python ml\src\eval_utils.py
```

Phiên bản: scikit-learn 1.7.2, pandas 2.2.3, joblib 1.5.2, torch 2.11.0+cpu, transformers 5.18.0. Không cài thêm thư viện.

## TODO-02 disposition

Đã ghi chú trong model card: `phobert_A.json` là metric lịch sử chưa tái lập đầy đủ. Cả checkpoint gốc và backend đều không cho đúng cặp test macro-F1 `0,9128` / accuracy `0,9141`. Không xóa số lịch sử; phân biệt rõ historical metric và remeasured T02 metric. PO quyết định cách dùng số sau review.

## TODO-03 disposition

Đã xử lý trong notebook:

- Thêm assertion AC-03, đối chiếu năm metric của SVM/LR/NB `text_norm` với `baselines.csv`; max diff phải bằng 0.
- Thêm output marker thực `AC-03_BASELINE_PARITY_OK` và `NOTEBOOK_EXECUTION_OK`.
- Lượt chạy sạch ngày 07/10/2026 kết thúc `NOTEBOOK_EXECUTION_OK` và runner kết thúc `NOTEBOOK_RUNNER_OK`.

## TODO-04 disposition

Giữ schema `size_mb` theo T02, bổ sung ghi chú trong model card, error analysis và report rằng phép tính là MiB (`1024²` byte).

## Validation gates

| Gate | Kết quả |
|---|---|
| Dataset | Đạt — 2.224 test; nhãn 0 = 981, nhãn 1 = 1.243 |
| comparison schema | Đạt — 8 hàng, 4 model × 2 input, đúng 10 cột |
| Baseline parity | Đạt — max metric diff = 0,000000 |
| Preprocessing | Đạt — max \|Δ F1\| = 0,003217 < 0,01 |
| Hai checkpoint | Đạt — đo đủ 4 hàng, định danh đường dẫn rõ ràng |
| Error analysis | Đạt — 20 mẫu/model, 80 dòng, category đã review, tối đa 5/category |
| Confusion matrix | Không đổi — prediction chính không đổi, 4 PNG không thay đổi |
| Reproducibility | Đạt — max metric diff với commit trước fix = 0,000000 ≤ 0,001 |
| Notebook | Đạt — JSON nbformat 4, 10 cell; full run kết thúc marker |
| Python compile | Đạt — `ml/src/eval_utils.py` |
| `git diff --check` | Đạt |
| Scope/secrets | Đạt — không sửa backend/frontend, không commit model/joblib/data/env/secret |

## Acceptance Criteria sau fix

- AC-01: Đạt — 8 hàng và đủ schema.
- AC-02: Đạt — checkpoint gốc trong bảng chính F1 `0,921600`; model card đã làm rõ mốc `0,918` thuộc checkpoint backend.
- AC-03: Đạt — max diff baseline `0,000000`, có assertion notebook.
- AC-04: Đạt — 4 confusion matrix tiếng Việt, prediction không đổi.
- AC-05: Đã sửa — 80 mẫu đã rà, methodology và giới hạn mẫu minh bạch, trade-off có số cụ thể.
- AC-06: Đạt — cùng `perf_counter`, cấu hình và runtime thực tế được ghi rõ.

## Files changed

- `ml/src/eval_utils.py`
- `ml/notebooks/T02_comparison.ipynb`
- `ml/results/comparison_A.csv` (chỉ latency từ lượt đo sạch mới; metric không đổi)
- `ml/results/error_analysis.md`
- `ml/model_card_A.md`
- `docs/TASK_COORDINATION_ACTIVE.md`
- `reports/2026-10-07/codex_fix_T02_round1_2026-10-07.md`

Không thay đổi bốn PNG vì prediction chính không đổi.

## Blockers

Không có blocker implementation. Quyết định checkpoint chính thức thuộc PO và không chặn việc review bản fix.

## Remaining TODO

- PO quyết định disposition giữa checkpoint gốc và checkpoint backend sau Claude review; Codex không tự chọn hoặc thay model web.
- PO quyết định cách trình bày metric lịch sử `phobert_A.json` trong luận văn; model card đã giữ và đánh dấu chưa tái lập đầy đủ.

## Final status

RF-01 và RF-02 đã được xử lý. T02 chuyển `FIX_LOOP` → `CLAUDE_REVIEW`; không chuyển `PO_REVIEW`, không merge, không close và không mở task kế tiếp.
