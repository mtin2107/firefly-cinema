# Claude review T02 — FAIL — 05/10/2026

## 1. Task
T02 — So sánh PhoBERT với mô hình truyền thống (`docs/tasks/T02.md`).

## 2. Review verdict
**FAIL** — 2 Required Fix (cả hai mức Medium), 0 blocker.

Phần đo đạc kỹ thuật **đạt và tái lập được từng byte** (metric, 4 PNG, `error_analysis.md`). T02 FAIL vì hai lý do:
1. Phân nhóm nguyên nhân lỗi (AC-05) sinh bằng quy tắc từ khóa, sai ở nhiều câu, và bảng tổng hợp chỉ phản ánh hạn mức chọn mẫu.
2. Disposition PO giao cho T02 về hai checkpoint PhoBERT A chưa được thực hiện. Probe của Claude cho thấy mốc 0,918 trong AC-02 thực ra là số của **checkpoint backend**, không phải checkpoint T02 đã đo.

## 3. Reviewed commit / branch
- Nhánh `task/T02-so-sanh-A`, HEAD `dc2417f` (`[T02] Compare PhoBERT with traditional models`), base `master` `0ce4390`.
- Diff đã xem: `git diff master...task/T02-so-sanh-A` (11 file, +829/−11).

## 4. Scope review
| Kiểm tra | Kết quả |
|---|---|
| Đúng nhánh | Đạt — `task/T02-so-sanh-A`, working tree sạch |
| File trong allowlist | Đạt — `ml/src/eval_utils.py`, notebook, `comparison_A.csv`, `error_analysis.md`, 4 PNG, `model_card_A.md`, coordination, report Codex |
| `backend/**`, `frontend/**`, task CLOSED | Không sửa |
| Model / joblib / CSV dữ liệu / `.env` / `.db` | Không có trong diff (grep `name-only` rỗng) |
| Thư viện mới | Không. `psutil` chỉ import có `try/except`, không bắt buộc |
| `git diff --check master...task/T02-so-sanh-A` | Sạch (exit 0) |
| Commit message | `[T02] ...` đúng quy ước |
| Đường dẫn `D:\` | Không có |

## 5. Dataset / split verification
- Probe độc lập đọc `data/uit-visfd/processed/test.csv`: **2.224 dòng, nhãn 0 = 981, nhãn 1 = 1.243**. Khớp.
- `load_test()` assert đúng kích thước và phân bố trước khi đánh giá.
- Không có bước fit hay chọn tham số nào trên test. Baseline chỉ `joblib.load` + `predict`, PhoBERT chỉ inference. Ngưỡng 0,5 lấy từ model card, không chọn trên test.
- Artifact: `ml/artifacts/phobert_A_best/` (checkpoint gốc T00) và `ml/artifacts/baselines/{svm,lr,nb}_A.joblib` (T01). Đúng là artifact đóng băng.

## 6. Metric verification
- `compute_metrics()` dùng `pos_label=1` cho precision/recall/F1, `average="macro"` cho macro-F1, `accuracy_score`. Đúng quy ước nhãn 1 = tiêu cực.
- Claude tính lại **độc lập bằng đếm TP/FP/FN/TN thủ công** (không dùng sklearn metrics) cho 8 cấu hình. Mọi số khớp `comparison_A.csv` tới 6 chữ số thập phân.

| Model (text_norm) | TN | FP | FN | TP | F1 neg (probe) | CSV |
|---|---:|---:|---:|---:|---:|---:|
| PhoBERT A (gốc) | 876 | 105 | 91 | 1152 | 0,921600 | 0,921600 |
| SVM | 838 | 143 | 128 | 1115 | 0,891643 | 0,891643 |
| Logistic Regression | 839 | 142 | 132 | 1111 | 0,890224 | 0,890224 |
| Naive Bayes | 817 | 164 | 150 | 1093 | 0,874400 | 0,874400 |

- PhoBERT trong `eval_utils` chạy batch 16 có padding. Probe chạy **batch 1 không padding, giống backend**, và cho cùng confusion matrix. Padding không ảnh hưởng kết quả.

## 7. Preprocessing comparison
- `normalize()` trong `eval_utils.py` **giống hệt** `backend/app/classifier.py::normalize()`: probe exec trực tiếp source backend, 2.224/2.224 câu ra cùng chuỗi. `normalize(text_raw)` trùng `text_norm` ở 1.049/2.224 câu.
- Chênh lệch F1 tiêu cực |text_norm − normalize|:

| Model | text_norm | normalize | |Δ| |
|---|---:|---:|---:|
| PhoBERT A (gốc) | 0,921600 | 0,919936 | 0,001664 |
| SVM | 0,891643 | 0,893837 | 0,002194 |
| LR | 0,890224 | 0,893127 | 0,002903 |
| NB | 0,874400 | 0,877617 | 0,003217 |
| *PhoBERT backend (probe Claude)* | *0,917808* | *0,918046* | *0,000238* |

Max |Δ| = **0,003217 < 0,01**. Không phát sinh blocker preprocessing, không cần sửa `normalize()`. Khớp báo cáo Codex.

## 8. PhoBERT metric và hai checkpoint (AC-02, TODO-01 T00)
Probe Claude đo cả hai checkpoint trên cùng test, cùng phép tính, batch 1:

| Checkpoint | Input | Precision neg | Recall neg | F1 neg | Macro-F1 | Accuracy |
|---|---|---:|---:|---:|---:|---:|
| Gốc `ml/artifacts/phobert_A_best` | text_norm | 0,916468 | 0,926790 | **0,921600** | 0,910492 | 0,911871 |
| Gốc | normalize | 0,915538 | 0,924377 | 0,919936 | 0,908686 | 0,910072 |
| Backend `backend/models/phobert-binhluan` | text_norm | 0,919290 | 0,916331 | **0,917808** | 0,907022 | 0,908273 |
| Backend | normalize | 0,921394 | 0,914722 | 0,918046 | 0,907526 | 0,908723 |

Kết luận:
- AC-02 đạt về số: |0,921600 − 0,918| = 0,0036 ≤ 0,005.
- Nhưng mốc "0,9178 với `text_norm`, 0,9180 với `normalize()`" trong model card **chính là số của checkpoint backend** (probe ra 0,917808 / 0,918046). Checkpoint T02 đo là bản gốc, cao hơn 0,0038. Bảng so sánh hiện báo số của checkpoint **không phải bản web đang chạy**, và cả T02 lẫn model card đều không ghi điều này → RF-02.
- Cả hai checkpoint đều không tái lập `phobert_A.json` (test macro-F1 0,9128, acc 0,9141) → TODO-02.

## 9. Baseline parity (AC-03)
SVM/LR/NB `text_norm` trong `comparison_A.csv` so với các hàng `split=test` của `ml/results/baselines.csv` (T01): precision/recall/F1/macro-F1/accuracy giống hệt, **max diff 0,000000**. `size_mb` của NB chênh 1e-6 do làm tròn. Đạt.

## 10. CPU benchmark review (AC-06)
- `measure_cpu_latency()`: warm-up `predict_one(samples[0])` ngoài vùng đo, rồi lặp 1.000 câu đầu, batch 1, `time.perf_counter`, chia 1.000. **Cùng một hàm cho cả 4 model.** Không còn `process_time` của T01 → TODO-04 T01 đã xử lý.
- PhoBERT batch 1 qua `predict_phobert([text], batch_size=1)`, `torch.set_num_threads(4)` có ghi trong report.
- Cấu hình máy/runtime ghi trong report và model card: i5-12450HX 8C/12T, 16 GB, Windows 11, Python 3.13.2, torch 2.11.0+cpu, transformers 5.18.0, sklearn 1.7.2. Claude xác nhận CPU bằng `Win32_Processor`.
- Claude chạy lại trên cùng máy:

| Model (text_norm) | Codex ms/câu | Claude rerun script Codex | Claude probe độc lập |
|---|---:|---:|---:|
| PhoBERT A | 120,99 | 47,06 | 46,73 |
| SVM | 1,07 | 0,33 | 0,34 |
| LR | 1,08 | 0,35 | 0,35 |
| NB | 1,37 | 0,42 | 0,45 |

Số tuyệt đối của Claude thấp hơn khoảng 2,5–3,2 lần ở **mọi** model, nhiều khả năng do tải máy khi Codex đo. Thứ tự độ lớn và tỉ lệ vẫn nhất quán: PhoBERT chậm hơn baseline khoảng 110–145 lần. Methodology đạt → TODO-01.
- GPU `1,817131` = 4,0413 s / 2.224 câu từ `phobert_A.json` (đã đối chiếu). Được ghi rõ là số tham khảo có batching, chỉ điền ở một hàng, không trình bày như benchmark ngang CPU batch 1. Đạt.

## 11. Confusion matrix review (AC-04)
4 file `cm_{phobert,svm,lr,nb}_A.png` đều có. Tiêu đề ghi `text_norm`, trục "Nhãn thực tế" / "Nhãn dự đoán", lớp "Bình thường" / "Tiêu cực", dấu tiếng Việt hiển thị đúng. Số trong ô khớp TN/FP/FN/TP của probe (bảng mục 6). Rerun ra PNG giống từng byte. Đạt.

## 12. Error analysis review (AC-05)
Đạt về hình thức: 4 × 20 = 80 dòng ví dụ, có bảng tổng hợp và mục trade-off, có câu nói rõ không dùng lỗi test để tuning.

Không đạt về nội dung. Đây là RF-01:
- **Nhóm do quy tắc từ khóa gán, không ai rà lại**, dù chính file ghi "để hỗ trợ rà soát thủ công". Lỗi cụ thể:
  - `classify_error` khớp chuỗi con: `"tuy"` ⊂ "**tuy**ệt" → index 312 ("thật tuyệt khi một sản phẩm rẻ…") bị gán "Chê một phần".
  - `" k "` trong câu hỏi "có vấn đề j k anh" (index 27) bị gán "Phủ định". Thực ra đây là câu hỏi, không phải phủ định.
  - Emoticon `:)))` / `=)))` bị coi là "Châm biếm" (index 1879, 2221), dù hai câu không châm biếm.
  - Nhóm "Nhãn nhiễu" bằng **0 ở cả 4 model**, vì quy tắc chỉ bắt câu ≤ 3 từ và đứng sau các quy tắc khác. Trong khi đó nhiều câu rõ là nhãn nhiễu: index 178 "chỉ có cảm biến vân tay kém" (nhãn 0), index 58 "Video màu sắc nhợt nhạt lắm… mong sớm sửa lỗi" (nhãn 0), index 8 "Điểm yếu là cam trc" (nhãn 0).
- **Bảng tổng hợp gây hiểu sai.** `select_errors` lấy round-robin tối đa vài câu mỗi nhóm theo thứ tự index, nên con số 5/5/5/5 là hạn mức chọn mẫu, không phải phân bố lỗi. Nếu đưa vào chương Thực nghiệm sẽ dẫn tới kết luận sai.
- Thiết kế T02 mục 4 yêu cầu "5 ví dụ tiêu biểu mỗi nhóm". Hiện nhiều nhóm có 0–4 ví dụ.
- Mục trade-off không có số về tốc độ và dung lượng (ví dụ PhoBERT ~517 MB và chậm hơn ~100× so với ~0,5 MB của baseline), chỉ có F1.

## 13. Reproducibility
- Claude chạy lại `eval_utils.py` của Codex trong thư mục tạm (junction tới `data/` và `ml/artifacts/`, không ghi đè `ml/results/` của repo): 8 hàng metric, `error_analysis.md` và **cả 4 PNG giống từng byte** với bản commit. Max metric diff **0,000000 ≤ 0,001**. Đạt.
- Probe độc lập (cách tính và cách chạy PhoBERT khác) cũng ra cùng số.
- Lưu ý môi trường: không interpreter nào trên máy có đủ torch và sklearn. `backend\venv` thiếu sklearn, Python hệ thống thiếu torch. Claude chạy bằng Python hệ thống + `PYTHONPATH=backend\venv\Lib\site-packages`. Report Codex không ghi cách dựng môi trường này → TODO-01.

## 14. Acceptance Criteria
| AC | Kết quả | Ghi chú |
|---|---|---|
| AC-01 | Đạt | 8 hàng = 4 model × 2 input, đủ 10 cột đúng tên |
| AC-02 | Đạt về số, **kèm RF-02** | 0,921600, lệch 0,0036. Mốc 0,918 thuộc checkpoint backend |
| AC-03 | Đạt | max diff 0,000000 so với `baselines.csv` |
| AC-04 | Đạt | 4 PNG, trục và lớp tiếng Việt, số khớp |
| AC-05 | **Không đạt** | RF-01: phân nhóm sai, bảng tổng hợp là hạn mức, trade-off thiếu số |
| AC-06 | Đạt | perf_counter, cùng methodology, ghi máy/runtime |

## 15. Required Fixes

### RF-01 — Phân nhóm nguyên nhân lỗi không đáng tin
- **Severity:** Medium
- **File:** `ml/results/error_analysis.md`; `ml/src/eval_utils.py` (`classify_error`, `select_errors`, `write_error_analysis`)
- **Problem:** Nhóm nguyên nhân do quy tắc từ khóa gán và sai ở nhiều câu. Nhóm "Nhãn nhiễu" không bao giờ được gán. Bảng tổng hợp thể hiện hạn mức round-robin chứ không phải phân bố lỗi. Mục trade-off thiếu số tốc độ và dung lượng.
- **Evidence:** Mục 12, gồm index 312 (`"tuy"` ⊂ "tuyệt"), 27, 1879, 2221, 178, 58, 8; dòng "Nhãn nhiễu/thiếu ngữ cảnh | 0 | 0 | 0 | 0".
- **Expected Fix:**
  1. Rà và gán lại nhóm cho 80 câu theo đúng 6 nhóm của T02 mục 3. Được phép gán tay, hoặc giữ quy tắc làm gợi ý rồi ghi nhóm đã duyệt. Nếu sửa quy tắc thì khớp theo từ, không theo chuỗi con. Nêu rõ cách gán.
  2. Bảng tổng hợp phải ghi rõ là đếm trên mẫu 20 câu, kèm cách chọn mẫu. Nếu muốn nói về phân bố lỗi thì đếm trên **toàn bộ** câu sai của mỗi model.
  3. Mỗi nhóm có tới 5 ví dụ tiêu biểu như thiết kế mục 4 (ít hơn thì ghi lý do).
  4. Mục trade-off nêu số F1, ms/câu CPU và MB của từng model, kèm lưu ý latency phụ thuộc tải máy.
  5. Không đổi model, ngưỡng hay preprocessing dựa trên các lỗi này.

### RF-02 — Chưa thực hiện disposition hai checkpoint PhoBERT A
- **Severity:** Medium
- **File:** `ml/model_card_A.md`, report fix T02 (có thể thêm hàng tham khảo vào `comparison_A.csv` nếu PO đồng ý)
- **Problem:** File điều phối mục 10 ghi TODO-01 T00 là "ACCEPT_LATER — T02; đo F1 hai bản trên cùng test bằng `normalize()` hiện tại, PO chọn". T02 chỉ đo checkpoint gốc và không nhắc tới checkpoint backend. Mốc 0,918 của AC-02 thuộc checkpoint backend, nên bảng so sánh hiện không nói rõ PhoBERT là bản nào và lệch với model web đang chạy.
- **Evidence:** Probe Claude (mục 8): backend `text_norm` F1 0,917808, `normalize` 0,918046, trùng 0,9178/0,9180 trong model card. Gốc 0,921600/0,919936.
- **Expected Fix:**
  1. Đo checkpoint `backend/models/phobert-binhluan` (chỉ đọc, không sửa `backend/**`) bằng `compute_metrics()` trên cùng test, 2 input. Ghi vào model card và report.
  2. Ghi rõ trong model card và cạnh bảng so sánh rằng PhoBERT A trong `comparison_A.csv` là checkpoint gốc, và mốc 0,918 thuộc checkpoint backend.
  3. Không tự thay model backend, không tự chọn bản. Đưa bảng hai checkpoint cho PO quyết định.

## 16. TODOs (không chặn, đề xuất disposition)
| ID | TODO | Đề xuất |
|---|---|---|
| TODO-01 | Latency tuyệt đối phụ thuộc tải máy (Claude đo nhanh hơn khoảng 2,5–3×). Report chưa ghi cách dựng môi trường có cả torch và sklearn | ACCEPT trong vòng fix: ghi cách chạy (interpreter/PYTHONPATH), khuyến nghị đóng ứng dụng nền hoặc báo trung vị nhiều lần đo; luận văn nên nhấn mạnh tỉ lệ thay vì số tuyệt đối |
| TODO-02 | Không checkpoint nào tái lập `phobert_A.json` (macro 0,9128 / acc 0,9141; đo lại được 0,9105 và 0,9070) | ACCEPT_LATER → PO: ghi chú trong model card là số lịch sử không tái lập được, dùng số T02 cho luận văn |
| TODO-03 | Notebook commit không kèm output. Report Codex nhắc `NOTEBOOK_EXECUTION_OK` nhưng notebook không có dòng này và không có assert AC-03 | ACCEPT trong vòng fix: thêm assert AC-03 hoặc sửa câu trong report cho đúng; output không bắt buộc |
| TODO-04 | `size_mb` tính theo 1024² (MiB) nhưng ghi "MB" | WONT_FIX hoặc ghi chú đơn vị trong luận văn |

Disposition các TODO cũ:
- **T00 TODO-01 (hai checkpoint):** chưa xử lý → RF-02.
- **T00 TODO-02 (`normalize()` ≠ `text_utils.py`):** đã xử lý đúng ý: đo `normalize()` hiện hành so với `text_norm` dùng lúc train, max |Δ F1| 0,003217 < 0,01. Không cần sửa `normalize()`. Đề xuất đóng.
- **T01 TODO-04 (`process_time`):** đã thay bằng `perf_counter`, cùng methodology cho 4 model. Đề xuất đóng.

## 17. Blockers
Không có. Preprocessing không vượt 0,01. RF-02 cần PO chọn checkpoint sau khi có số, nhưng không chặn Codex sửa.

## 18. Final recommendation
- T02 `CLAUDE_REVIEW` → **`FIX_LOOP`**. Codex chỉ sửa RF-01, RF-02 (kèm TODO-01/03 nếu tiện), không đo lại hay đổi số các model khác.
- Không mở T04 hay task kế tiếp. Không merge.
- Probe của Claude chạy ở scratchpad ngoài repo. Repo không có file tạm nào, `git status` sạch trước khi commit report.
