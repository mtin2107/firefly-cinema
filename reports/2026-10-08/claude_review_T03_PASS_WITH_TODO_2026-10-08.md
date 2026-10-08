# Claude Review — T03 Bộ dữ liệu bình luận phim — PASS_WITH_TODO — 08/10/2026

| Trường | Giá trị |
|---|---|
| Task | T03 — Bộ dữ liệu bình luận phim (FR-M05, NFR-10) |
| Reviewer | Claude (Independent Reviewer / Tester) |
| Branch | `task/T03-du-lieu-phim` |
| Commit | HEAD = `c1480b5` (= baseline `master`); **chưa có commit implementation** — review trên working tree |
| Report Codex | `reports/2026-10-08/codex_implementation_T03_2026-10-08.md` |
| Quyết định PO áp dụng | Q1 (07/10/2026); phương án A tỷ lệ nhãn (08/10/2026) |
| **Verdict** | **PASS_WITH_TODO** — AC 6/6, Required Fix 0, blocker 0 |

## 0. Giới hạn tính độc lập (phải đọc trước)

Trong cùng phiên chat ngày 07–08/10/2026, Claude đã **hỗ trợ thu thập dữ liệu** theo yêu cầu của Tín:

- chọn và đề xuất 9 batch ứng viên (`data/phim/candidates_batch01–09.csv`); Tín duyệt giữ/bỏ từng câu;
- dựng lại `movie_comments_v1.csv` từ ứng viên khi Tín duyệt lại, và **khôi phục text** sau hai lần file bị Excel lưu dạng ANSI (mất dấu);
- **chép nhãn theo `id`** (nhãn A của Tín từ file ANSI sang file UTF-8; `label_b` của Người 1 vào `kappa_sample.csv`);
- tạo bản làm việc cho Người 1 `kappa_sample_nguoi1.csv` chỉ gồm `id,text,label_b`.

Claude **không** gán nhãn A hay B, không xem/so sánh nhãn trước khi script tính kappa, không chạy script tạo split thay Tín ở bước chuẩn bị. Tuy vậy, các phần dưới đây **không phải review độc lập hoàn toàn** vì Claude là người thao tác: tính nguyên văn của text, cách chọn ứng viên (đã nghiêng về câu chê, xem quyết định PO 08/10), và việc chép nhãn. Review bù bằng kiểm tra cơ học có thể tái lập (mục 6.6) và đề nghị PO cân nhắc ở TODO-05.

## 1. File đã đọc

`docs/PROJECT_SOURCE_OF_TRUTH.md`, `docs/AGENT_RULES.md` (mục 1, 2, 3), `docs/TASK_COORDINATION_ACTIVE.md`, `docs/tasks/T03.md`, `docs/tasks/_TEMPLATE.md` mục 9, `ml/labeling_guideline.md`, `ml/src/prepare_movie_data.py` (toàn bộ), `data/README.md` (diff), `ml/results/movie_data_stats.md`, `reports/2026-10-07/claude_q1_decision_T03_2026-10-07.md`, `reports/2026-10-08/claude_po_decision_label_ratio_T03_2026-10-08.md`, `reports/2026-10-08/codex_implementation_T03_2026-10-08.md`; dữ liệu ngoài Git `data/phim/movie_comments_v1.csv`, `movie_train.csv`, `movie_test.csv`, `kappa_sample.csv`, `candidates_batch01–09.csv`.

## 2. Git và scope

```text
$ git branch --show-current          → task/T03-du-lieu-phim
$ git log -1 --oneline               → c1480b5 [T02] Close task after PO merge
$ git log --oneline master..HEAD     → (rỗng)
$ git diff --check                   → exit 0 (chỉ cảnh báo LF→CRLF ở 2 file .md đã track)
$ git diff --name-only master...HEAD → (rỗng — chưa commit)
$ git ls-files data/phim             → (rỗng — không dữ liệu nào bị track)
$ git diff --cached --name-only      → (rỗng)
$ git diff --stat master -- backend frontend → (rỗng)
```

Working tree so với `master`:

| File | Thuộc | Đánh giá |
|---|---|---|
| `ml/src/prepare_movie_data.py`, `ml/labeling_guideline.md`, `ml/results/movie_data_stats.md`, `data/README.md`, `docs/TASK_COORDINATION_ACTIVE.md`, `reports/2026-10-0{7,8}/codex_implementation_T03_*.md` | Allowlist T03 | ✅ |
| `docs/PROJECT_SOURCE_OF_TRUTH.md`, `docs/tasks/T03.md`, `reports/2026-10-07/claude_q1_decision_T03_*.md`, `reports/2026-10-08/claude_po_decision_label_ratio_T03_*.md` | Thay đổi PO / ghi nhận quyết định (Q1, phương án A) | Ngoài allowlist Codex nhưng là phạm vi PO — commit tách riêng (TODO-01) |
| `data/phim/NGUON_THU.md` | Tài liệu nguồn do Claude soạn ở Q1 | Ngoài allowlist; PO quyết định commit hay bỏ (TODO-01) |
| `data/phim/movie_comments_v1.md` | **Bản Markdown toàn bộ 496 câu**, Claude tạo theo yêu cầu của Tín | **Không bị `.gitignore`**; tuyệt đối không commit — xóa trước khi commit (TODO-01) |
| 29 CSV trong `data/phim/` | Dữ liệu | Đều khớp `.gitignore:10 data/**/*.csv` ✅ |

`backend/**`, `frontend/**`, `normalize()` không đổi ✅.

## 3. Review `ml/labeling_guideline.md`

- Định nghĩa nhãn 0/1 rõ (mục 1); nhãn 1 bao gồm chê phim, diễn xuất, kịch bản, hình/tiếng, rạp, dịch vụ, chê một phần, châm biếm (mục 1, 3) ✅
- 10 quy tắc quyết định, có phủ định của lời chê, emoji, câu không dấu (mục 2) ✅
- **30 ví dụ biên khó** (yêu cầu ≥ 15) ✅
- Quy trình A/B: A = Lê Minh Tín, B = "Người 1" ẩn danh, 100 câu seed 42, B không xem nhãn A, không đổi nhãn để tăng kappa, đo lại nếu < 0,6 (mục 5) ✅
- Cấm LLM làm annotator/tự điền `label_b` (dòng 85) ✅
- Không có quy tắc trái Task Record ✅

## 4. Review `ml/src/prepare_movie_data.py`

| Yêu cầu | Code | Kết quả |
|---|---|---|
| Schema đúng thứ tự `id,text,label,source_type,note` | `EXPECTED_COLUMNS`, dòng 79 | ✅ |
| `source_type` ∈ 4 giá trị | `ALLOWED_SOURCE_TYPES`, dòng 110–115 | ✅ |
| label chỉ 0/1, không trống, ID duy nhất | dòng 88–108 | ✅ |
| Dùng đúng `backend.app.classifier.normalize`, không copy/sửa | import dòng 31; đặt tạm `MODEL_DIR=""` để không nạp model rồi khôi phục env | ✅ |
| Duplicate xét sau `normalize()`, in số dòng loại | `remove_normalized_duplicates`, dòng 133–145, in dòng 351 | ✅ |
| PII email / SĐT / `@username` trên `text` và `note`, có lỗi thì dừng | dòng 53–57, 119–130, 338–347 | ✅ |
| Split `test_size=0.30`, `stratify=label`, `random_state=42` | dòng 154–159 | ✅ |
| Duplicate chéo sau `normalize()` = 0, có thì dừng | dòng 163–164, 402–406 | ✅ |
| Mẫu kappa `sample(n=100, random_state=42)` | dòng 174 | ✅ |
| Không giả `label_b`; không ghi đè mẫu đã có; kiểm tra ID, `label_a` khớp dataset | dòng 177–206 | ✅ |
| Chỉ tính kappa khi đủ 100 `label_b`; ngưỡng ≥ 0,6 | dòng 213–222 | ✅ |
| 400 câu tối thiểu chặn; >600 chặn | dòng 397, 412–419, 428 | ✅ |
| Nguồn chính ≥ 80 %, self_written ≤ 20 % chặn | dòng 391–392, 428 | ✅ |
| Phương án A: tỷ lệ 35–60 % chỉ cảnh báo | `label_ratio_ok` chỉ dùng để in WARNING (dòng 375–380), không có trong điều kiện dòng 428 | ✅ |
| ≥ 20 phim, ≤ 30 câu/phim, ≤ 40 %/nguồn cụ thể | Chỉ thống kê vào stats (dòng 240–263), **không chặn** | Dữ liệu đạt (mục 7) — TODO-02 |

Ghi chú nhỏ: chuỗi "67,94%" bị hard-code trong WARNING (dòng 379) và ghi chú stats (dòng 322) — TODO-03.

## 5. Gate (chạy độc lập bằng Python hệ thống)

```text
$ python -m py_compile ml\src\prepare_movie_data.py   → exit 0
$ python ml\src\prepare_movie_data.py --input data\phim\movie_comments_v1.csv --out data\phim
Raw rows: 496
Duplicate removed after normalize(): 0
Final rows: 496
PII scan: 0 findings
Label 1 ratio: 67.94%
WARNING: Tỷ lệ label 1 ngoài mục tiêu 35–60%; PO đã chấp nhận theo phương án A ngày 08/10/2026 (không chặn gate).
review_site + social ratio: 100.00%
self_written ratio: 0.00%
Train/test rows: 347/149
Cross-split normalized duplicates: 0
Kappa: 0.602510460251046
STATUS: READY_FOR_AC_REVIEW (KAPPA_ACCEPTED)
exit 0
```

Khớp hoàn toàn với evidence Codex.

**Tái lập:** chạy 2 lần liên tiếp; SHA-256 danh sách ID và SHA-256 file trước/sau không đổi:

| File | Dòng | SHA-256 danh sách ID | SHA-256 file (16 ký tự) |
|---|---:|---|---|
| `movie_train.csv` | 347 | `dd2ef81de56ec17fc36028808ce1c72e42b6ebc40c95b92ff179a56ec1e260f5` | `dbfe8bf7ecd395e1` |
| `movie_test.csv` | 149 | `a0e36b5c687a2d5282803912a59d7f9c8c7a4ec3e74a20459756330db3db69d6` | `5af8f616429e325f` |
| `kappa_sample.csv` | 100 | `bfb827d33d6bee2aa1a926a3de229869350ee288dfc7b8cc78e61db678ae00dc` | `588ac445f5e1229f` |
| `movie_comments_v1.csv` | 496 | `071bb5a01b61e8d12290d23ab1ac3ef920e16b087fded1fee4a11b225cf36db3` | `5993c620e7b2702d` |
| `ml/results/movie_data_stats.md` | — | — | `f740b1b394ba4b52` (không đổi) |

Hash ID train/test trùng với report Codex mục 5.

## 6. Kiểm tra dữ liệu độc lập (probe chỉ đọc, không qua script)

Probe tạm ở thư mục scratchpad ngoài repo (không có file probe nào trong repo).

### 6.1 AC-01
496 dòng (400 ≤ n ≤ 600); ID duy nhất; duplicate sau `normalize()` = 0; không câu nào rỗng sau `normalize()`; script in "Duplicate removed after normalize(): 0".

### 6.2 AC-02
- Regex của script: 0 phát hiện.
- Quét rộng hơn độc lập (email lỏng, SĐT 9–11 số có dấu cách/chấm, mọi `@\w`, URL/tên miền/facebook/zalo/tiktok, chuỗi ≥ 7 chữ số) trên `text` và `note`: 0 phát hiện thật (164 kết quả "url" là dương tính giả do regex bắt chữ "YouTube" trong `note`).
- Heuristic tên người ("bạn/chị/anh/nhân viên + Tên"): chỉ ra tên người của công chúng (Lý Hải, Minh Hà, Dưa Leo) hoặc dương tính giả; không có tên nhân viên rạp hay người viết. Trong phiên thu thập, các đánh giá có tên nhân viên đã bị loại từ đầu.

### 6.3 AC-03 — Cohen's kappa tính độc lập
- 100 dòng; `label_a` 100/100 và `label_b` 100/100 hợp lệ (0/1).
- ID mẫu trùng `df.sample(n=100, random_state=42)` trên dataset hiện tại ✅; `label_a` và `text` trùng dataset 100/100 ✅.
- Đồng ý quan sát p_o = 0,81 (19 câu bất đồng).
- Tính tay: κ = (p_o − p_e)/(1 − p_e) = **0,602510**; `sklearn.cohen_kappa_score` = **0,602510**. ≥ 0,6 ✅ (sát ngưỡng — TODO-06).

### 6.4 AC-04
- Tính lại `train_test_split(test_size=0.30, random_state=42, stratify=label)` độc lập: danh sách ID train và test **trùng đúng thứ tự** với file ✅.
- Test = 149/496 = 30,04 %. Phân tầng: train 236/111 (label 1 = 68,01 %), test 101/48 (67,79 %) so với toàn bộ 67,94 % ✅.
- Mỗi dòng train/test trùng nguyên văn dòng gốc ✅. Hai lần chạy cho cùng hash (mục 5) ✅.

### 6.5 AC-05
Giao ID train/test = 0; hợp ID = toàn bộ 496 ID gốc; giao chuỗi sau `normalize()` = 0 ✅.

### 6.6 Kiểm tra cơ học bù cho phần Claude thao tác
- Toàn bộ 496 ID có trong `candidates_batch01–09.csv`; `text`, `note`, `source_type` trùng nguyên văn 496/496 với ứng viên (là bản Tín đã duyệt) ✅.
- Không có ký tự thay thế (U+FFFD), không mojibake, không mẫu "chữ?chữ" của lỗi ANSI ✅.
- Nhãn A sau khi chép khớp file Tín gán 496/496; `label_b` khớp file Người 1 100/100 (đã kiểm tra lúc ghép; bản sao lưu ANSI vẫn còn trong `data/phim/`, ngoài Git).

## 7. Nguồn

| Tiêu chí (Q1) | Từ dữ liệu | Kết quả |
|---|---|---|
| review_site + social ≥ 80 % | 333 + 163 = 496 (100 %) | ✅ |
| self_written ≤ 20 % | 0 | ✅ |
| ≥ 20 phim | 83 phim (341 câu) + 28 rạp (155 câu); mọi dòng có thẻ `phim:` hoặc `rạp:` | ✅ |
| ≤ 30 câu/phim | Lớn nhất: Lật Mặt 8 = 20, Thanh Gươm Diệt Quỷ = 13, Mai = 12 | ✅ |
| ≤ 40 %/nguồn cụ thể | Moveek 178 (35,89 %), YouTube 163 (32,86 %), Google Maps 155 (31,25 %); rạp nhiều nhất 9 câu | ✅ |
| Ánh xạ nguồn → source_type | Moveek/Google Maps → `review_site`, YouTube → `social`, nhất quán 100 % | ✅ |

Khớp evidence Codex. Tỷ lệ nhãn 1 theo nguồn: Moveek 135/178, Google Maps 124/155, YouTube 78/163 — giải thích tại quyết định PO 08/10.

## 8. Độc lập annotator

- Repo chỉ ghi "Người 1"; không có tên thật trong guideline, README, report hay file điều phối ✅.
- Không có evidence LLM gán nhãn B. Bản làm việc giao cho Người 1 (`kappa_sample_nguoi1.csv`) chỉ có cột `id,text,label_b` (Claude tạo và xác nhận cột) ✅.
- Việc B không xem nhãn A ngoài bản làm việc dựa trên xác nhận của Tín; không có evidence trái ngược → TODO-04 (ghi lại quy trình thực tế).

## 9. Kết luận từng AC

| AC | Result | Evidence | Required Fix |
|---|---|---|---|
| AC-01 ≥ 400 câu sau khử trùng, script in số loại | **PASS** | 496/496, loại 0; script in dòng loại; probe độc lập dup = 0 | — |
| AC-02 Không PII (script trả 0) | **PASS** | Script 0; quét rộng độc lập 0 thật; heuristic tên chỉ ra người công chúng | — |
| AC-03 Kappa 100 câu ≥ 0,6 | **PASS** | 100/100 A và B; mẫu = seed 42; κ tay = sklearn = 0,602510 | — |
| AC-04 70/30 phân tầng, chạy lại cùng `id` | **PASS** | Tính lại split độc lập trùng thứ tự ID; 2 lần chạy cùng hash; 30,04 % test; tỷ lệ nhãn 68,01/67,79 % | — |
| AC-05 Không câu trùng train/test sau `normalize()` | **PASS** | Giao ID 0, hợp = 496, giao normalized 0 | — |
| AC-06 README + stats có số dòng, tỷ lệ nhãn, kappa | **PASS** | Cả hai có số dòng, phân bố nhãn, source_type, nguồn cụ thể, độ phủ, split, PII, kappa, seed, quyết định PO 67,94 % | — |

**AC 6/6.**

## 10. Required Fixes

**0.**

## 11. TODO (không chặn PO_REVIEW)

| ID | Mức | Nội dung | Đề xuất |
|---|---|---|---|
| TODO-01 | **Bắt buộc trước commit/merge** | Branch chưa có commit; working tree lẫn thay đổi implementation, thay đổi PO (`PROJECT_SOURCE_OF_TRUTH.md`, `T03.md`, report quyết định), `data/phim/NGUON_THU.md`, và **`data/phim/movie_comments_v1.md` chứa toàn bộ 496 câu, không bị ignore**. | Xóa `movie_comments_v1.md` (hoặc thêm vào `.gitignore` nếu PO cho phép). Commit implementation `[T03] …` chỉ gồm file allowlist; commit PO tách riêng; PO quyết định có giữ `NGUON_THU.md`. Không dùng `git add .`. Sau commit chạy lại `git diff --name-only master...HEAD` để xác nhận không có dữ liệu. |
| TODO-02 | Thấp | Script không chặn theo ≥ 20 phim / ≤ 30 câu/phim / ≤ 40 %/nguồn cụ thể; hiện chỉ thống kê. Dữ liệu hiện đạt (mục 7). | Nếu dataset còn thay đổi (v2), thêm cổng kiểm tra từ `note`, hoặc ghi rõ đây là kiểm tra thủ công. |
| TODO-03 | Thấp | Chuỗi "67,94%" hard-code trong WARNING và ghi chú stats. | Lấy giá trị từ dữ liệu khi in, giữ nội dung quyết định PO. |
| TODO-04 | Tài liệu | README bước 4 ghi "Tín ghép `label_b`"; file điều phối ghi "Tín + Người 1 hoàn tất 496 câu". Thực tế ứng viên do Claude đề xuất, Tín duyệt; nhãn A/B được Claude chép theo `id` sau sự cố file ANSI. | Ghi provenance thực tế (ai chọn, ai duyệt, ai gán, ai chép) trong report/khóa luận; quyết định PO 08/10 đã ghi một phần. |
| TODO-05 | PO cân nhắc | Giới hạn tính độc lập của review (mục 0). | PO có thể tự kiểm tra ngẫu nhiên vài câu so với nguồn trong `candidates_batch0x_evidence.csv`. |
| TODO-06 | Báo cáo | κ = 0,6025 sát ngưỡng (19/100 bất đồng). | Khóa luận ghi rõ mức đồng thuận vừa phải và nhóm câu gây bất đồng; không sửa nhãn. |
| TODO-07 | PO | Chưa xác minh được bản sao trên Drive `MyDrive/thesis/data/movie/` mà README nêu. | Tín upload/kiểm tra 4 CSV chính trước khi đóng T03. |
| TODO-08 | Dọn dẹp | `data/phim/` còn nhiều file trung gian (ứng viên, evidence, bản sao lưu ANSI/restored/before_merge, `kappa_sample_nguoi1*`), đều bị ignore. | Giữ đến khi T03 CLOSED rồi dọn; nên giữ `candidates_*` và `*_evidence.csv` làm truy vết nguồn. |

## 12. Blockers

Không.

## 13. Definition of Done

| Mục DoD (`_TEMPLATE.md` mục 9) | Trạng thái |
|---|---|
| Toàn bộ AC đạt, có bằng chứng trong report | ✅ AC 6/6 |
| Gate theo `AGENT_RULES.md` mục 3 (ML/dữ liệu: tái lập seed, đúng `normalize()`, không commit dữ liệu) | ✅ tái lập và `normalize()` đạt; không dữ liệu nào bị track |
| Không có file ngoài allowlist trong diff | ⏳ Chưa có commit; cần thực hiện TODO-01 khi commit |
| Tài liệu liên quan đã cập nhật | ✅ README, stats; không đổi kiến trúc/thư viện |
| Claude PASS / PASS_WITH_TODO, Tín APPROVED | ✅ Claude PASS_WITH_TODO; chờ PO |

**DoD: MET có điều kiện** — hoàn tất khi commit đúng theo TODO-01 và PO duyệt.

## 14. Verdict

**PASS_WITH_TODO** — AC 6/6, Required Fix 0, blocker 0. T03 `CLAUDE_REVIEW → PO_REVIEW`.

Claude không merge, không gắn tag, không PO approve, không đóng T03, không commit.

## 15. Bàn giao task kế tiếp

Theo `AGENT_RULES.md` mục 1.1, task kế tiếp theo thứ tự là **T04 — Quản lý phim (admin)** (không dependency, không bị Q1–Q4 chặn). Tuy nhiên file điều phối đang ghi rõ ý PO: "T04 — PLANNED, chờ PO authorize (chưa READY_FOR_HANDOFF)". Claude **giữ nguyên** trạng thái T04 theo ghi chú PO đó. Khi Tín muốn mở T04: gửi `docs/tasks/T04.md` cho ChatGPT (= PO duyệt Task Record), tạo nhánh `task/T04-quan-ly-phim` từ `master` sau khi merge T03, rồi dùng prompt dưới đây.

```text
Bạn là Codex, Primary Implementer của dự án Firefly Cinema.
Repo: C:\Projects\firefly-cinema. Task: T04 — Quản lý phim (admin). Branch: task/T04-quan-ly-phim (tách từ master).

Đọc theo thứ tự: docs/PROJECT_SOURCE_OF_TRUTH.md, docs/AGENT_RULES.md, docs/TASK_COORDINATION_ACTIVE.md,
docs/tasks/T04.md, docs/ARCHITECTURE.md (mục 1b, 2.1–2.4), docs/BOI_CANH_DU_AN.md (mục 6, 7).

Làm đúng Allowed Scope / Allowed Files của T04.md; không sửa file ngoài allowlist.
Quy ước bắt buộc: endpoint admin dùng require_admin (user thường 403); lỗi HTTPException kèm một câu tiếng Việt;
endpoint mới có ở CẢ frontend/src/api/real.js và mock.js cùng cấu trúc JSON; giao diện chỉ import từ src/api/index.js;
dữ liệu phim khớp giữa backend/app/data/movies.json và frontend/src/api/movies.json; không thêm thư viện;
không đổi thiết kế giao diện đã chốt; nếu đổi schema phải ghi rõ cần xóa backend/firefly.db.

Gate (AGENT_RULES mục 3.1): backend\venv\Scripts\python -m compileall -q backend\app; backend khởi động và
/api/health báo "classifier":"phobert"; cd frontend; npm run build; mock mode (VITE_USE_MOCK=true) đi hết luồng
admin phim; checklist hồi quy BOI_CANH mục 7; scope git diff --stat master...HEAD chỉ file allowlist.

Commit dạng [T04] mô tả, không git add . . Viết reports/YYYY-MM-DD/codex_implementation_T04_YYYY-MM-DD.md,
cập nhật docs/TASK_COORDINATION_ACTIVE.md T04 → CLAUDE_REVIEW. Không tự review, không merge.
```

**Nhắc Tín:** xử lý TODO-01, commit đúng file, duyệt PO_REVIEW, merge T03 vào `master`, rồi mới tạo nhánh T04 từ `master`.
