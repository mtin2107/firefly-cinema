# Codex — Implementation T03 — 08/10/2026

## 1. Thông tin thực hiện

| Mục | Giá trị |
|---|---|
| Task | T03 — Bộ dữ liệu bình luận phim |
| Vai trò | Codex — Primary Implementer |
| Branch | `task/T03-du-lieu-phim` |
| Baseline branch lúc bắt đầu T03 | `c1480b56f8273cfccdb875b7c1eaca06eadbf9a2` |
| Quyết định PO áp dụng | Phương án A ngày 08/10/2026: chấp nhận label 1 = 67,94%; không thêm/bớt câu, không sửa nhãn |
| Trạng thái bàn giao | `CLAUDE_REVIEW` |
| Đổi schema | Không |

Report này ghi evidence implementation để Claude review độc lập. Codex không tự review, không tuyên bố PASS, không PO approve và không merge.

## 2. Phạm vi thay đổi vòng 08/10

| File | Thay đổi |
|---|---|
| `ml/src/prepare_movie_data.py` | Giữ cảnh báo tỷ lệ label 1 nhưng bỏ tỷ lệ khỏi điều kiện chặn theo quyết định PO; giữ nguyên các gate khác. Bổ sung thống kê nguồn cụ thể và độ phủ từ `note`. |
| `data/README.md` | Ghi snapshot 496 câu, phân bố nhãn/nguồn, độ phủ, split, PII, kappa và giải trình phương án A. |
| `ml/results/movie_data_stats.md` | Script tạo lại từ dữ liệu thật, trạng thái `READY_FOR_AC_REVIEW`. |
| `docs/TASK_COORDINATION_ACTIVE.md` | Xóa blocker dữ liệu/annotator đã hoàn thành và chuyển T03 `IN_PROGRESS → CLAUDE_REVIEW`. |
| `reports/2026-10-08/codex_implementation_T03_2026-10-08.md` | Report này. |

Không sửa `normalize()`, backend, frontend, cách chia, seed hoặc cách chọn mẫu kappa. Không sửa hay đưa CSV vào Git. Sau Claude review, Codex đã xóa `data/phim/movie_comments_v1.md` theo TODO-01 vì file này chứa toàn bộ 496 câu nhưng không được `.gitignore` bảo vệ.

## 3. Quyết định tỷ lệ nhãn

Output trước thay đổi báo `BLOCKED_BY_DATA_QUALITY` chỉ vì label 1 = 337/496 = 67,94%, cao hơn mục tiêu 35–60%. Theo `reports/2026-10-08/claude_po_decision_label_ratio_T03_2026-10-08.md`, PO chọn phương án A:

- chấp nhận phân bố thực tế;
- không thêm/bớt câu;
- không sửa nhãn;
- giữ nguyên mẫu kappa seed 42;
- tỷ lệ 35–60% tiếp tục được cảnh báo nhưng không phải gate chặn.

Các điều kiện khác vẫn chặn như cũ: tối thiểu 400 câu, tối đa 600 câu, quy tắc nguồn, đủ nhãn B, kappa ≥ 0,6, PII = 0 và duplicate cross-split = 0.

## 4. Gate chính

Đã dùng Python hệ thống, không dùng `backend\venv`:

```powershell
python ml\src\prepare_movie_data.py --input data\phim\movie_comments_v1.csv --out data\phim
```

Output:

```text
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
```

Exit code: 0.

## 5. Kiểm tra tái lập AC-04

Trước và sau lần chạy gate, SHA-256 của chuỗi ID theo đúng thứ tự trong mỗi split không đổi:

| Split | SHA-256 danh sách ID | Kết quả |
|---|---|---|
| Train | `dd2ef81de56ec17fc36028808ce1c72e42b6ebc40c95b92ff179a56ec1e260f5` | Không đổi |
| Test | `a0e36b5c687a2d5282803912a59d7f9c8c7a4ec3e74a20459756330db3db69d6` | Không đổi |

Kiểm tra độc lập còn xác nhận:

- raw/train/test/kappa: 496/347/149/100 dòng;
- hợp của ID train và test đúng bằng toàn bộ ID raw;
- giao ID train/test = 0;
- thiếu `label_b` = 0;
- Cohen's kappa tính độc lập = `0.602510460251`;
- train: label 0/1 = 111/236, label 1 = 68,011527%;
- test: label 0/1 = 48/101, label 1 = 67,785235%.

## 6. Kiểm tra nguồn và chất lượng

| Chỉ số | Kết quả |
|---|---:|
| Raw / final | 496 / 496 |
| Duplicate sau đúng `normalize()` backend | 0 |
| PII | 0 |
| `review_site` | 333 (67,14%) |
| `social` | 163 (32,86%) |
| `self_written` / `web_firefly` | 0 / 0 |
| Moveek | 178 (35,89%) |
| YouTube | 163 (32,86%) |
| Google Maps | 155 (31,25%) |
| Độ phủ phim | 83 phim, 341 câu; tối đa 20 câu/phim |
| Độ phủ rạp | 28 rạp, 155 câu |
| Nguồn cụ thể lớn nhất | 35,887097%, dưới 40% |
| Duplicate normalized giữa train/test | 0 |

## 7. Trạng thái Acceptance Criteria trước review

| AC | Evidence implementation | Trạng thái bàn giao |
|---|---|---|
| AC-01 | 496 câu sau khử trùng; script in loại 0 | Đủ evidence để Claude kiểm tra |
| AC-02 | PII scan email/điện thoại/`@username` = 0 | Đủ evidence để Claude kiểm tra |
| AC-03 | 100/100 nhãn B thật; kappa = 0,602510 ≥ 0,6 | Đủ evidence để Claude kiểm tra |
| AC-04 | Split 347/149 stratified seed 42; hash ID trước/sau không đổi | Đủ evidence để Claude kiểm tra |
| AC-05 | Duplicate normalized giữa train/test = 0 | Đủ evidence để Claude kiểm tra |
| AC-06 | README và stats có số dòng, phân bố, nguồn, split, PII, kappa, seed và quyết định PO | Đủ evidence để Claude kiểm tra |

Đây không phải kết luận PASS. Claude là người chạy lại và kết luận review.

## 8. Lệnh kiểm tra đã chạy

```powershell
python -m py_compile ml\src\prepare_movie_data.py
python ml\src\prepare_movie_data.py --input data\phim\movie_comments_v1.csv --out data\phim
# Probe Python hệ thống: hash ID, partition, overlap, kappa, phân bố split,
# duplicate normalize(), độ phủ phim/rạp và tỷ lệ nguồn cụ thể.
git status --short --branch
git diff --check
git diff --name-only master...HEAD
git ls-files data/phim
git check-ignore -v data/phim/*.csv
```

Kết quả gate Git cuối được ghi tại mục 9 sau lần kiểm tra cuối.

## 9. Git và dữ liệu ngoài Git

- Không dùng `git add .`.
- `git status --short --branch`: đúng `task/T03-du-lieu-phim`; working tree còn các thay đổi T03 và thay đổi Q1/PO đã có sẵn.
- `git diff --check`: exit code 0; chỉ có cảnh báo LF/CRLF cho hai Markdown đã track.
- `git diff --name-only master...HEAD`: rỗng vì branch chưa có commit mới so với baseline; lệnh này không hiện working tree/untracked.
- `git diff --cached --name-only`: rỗng; không file nào được stage.
- `git ls-files data/phim`: rỗng; không dữ liệu nào trong `data/phim/` được Git track.
- `git check-ignore -v` xác nhận bốn CSV chính khớp rule `.gitignore` `data/**/*.csv`.
- `data/phim/movie_comments_v1.md` đã được xóa theo TODO-01 và không xuất hiện trong status hoặc commit.
- Kiểm tra trailing whitespace riêng cho script, stats và report mới: không phát hiện.
- Dữ liệu thật, split, mẫu kappa và các bản sao đều giữ ngoài Git.

## 10. Xử lý TODO sau Claude review

| TODO | Disposition | Kết quả / hành động tiếp theo |
|---|---|---|
| TODO-01 | **RESOLVED** | Đã xóa `data/phim/movie_comments_v1.md`; CSV vẫn ignored; không dữ liệu thật nào được track/stage. Implementation, PO/governance và review được commit tách biệt, không dùng `git add .`. `data/phim/NGUON_THU.md` giữ untracked theo phương án mặc định. |
| TODO-02 | **ACCEPT_LATER / DOCUMENTED** | Dataset T03 v1 hiện đạt 83 phim, tối đa 20 câu/phim và nguồn lớn nhất 35,89%. Không mở rộng implementation ở PO_REVIEW. Nếu dataset v2 thay đổi, bổ sung gate tự động từ `note`. |
| TODO-03 | **ACCEPT_LATER / LOW PRIORITY** | Giữ chuỗi `67,94%` hard-code vì không ảnh hưởng AC. Không sửa code để tránh quay lại FIX_LOOP/review. |
| TODO-04 | **DOCUMENTED** | Claude đề xuất ứng viên theo batch; Tín duyệt câu giữ/bỏ và là Annotator A; “Người 1” là Annotator B; Claude chỉ chép nhãn theo ID sau sự cố encoding ANSI, không tự gán A/B; dataset cuối 496 câu và không sửa nhãn để tăng kappa. |
| TODO-05 | **ACCEPT_WITH_DISCLOSURE** | PO chấp nhận giới hạn độc lập vì Claude có hỗ trợ thu dữ liệu nhưng không gán A/B; split/hash/kappa/PII được kiểm tra lại cơ học và tái lập. Giới hạn này phải được nêu minh bạch trong khóa luận/report. |
| TODO-06 | **ACCEPT_WITH_DISCLOSURE** | Cohen's kappa = 0,6025; 19/100 câu bất đồng; mức đồng thuận vừa phải. Không sửa nhãn để tăng kappa; ghi rõ trong khóa luận. |
| TODO-07 | **PO ACTION REQUIRED** | Phiên Codex này không có quyền truy cập Google Drive nên không xác nhận hoặc bịa trạng thái upload. Tín cần tự upload/kiểm tra `movie_comments_v1.csv`, `movie_train.csv`, `movie_test.csv`, `kappa_sample.csv` tại `MyDrive/thesis/data/movie/` trước khi đóng T03. |
| TODO-08 | **ACCEPT_LATER — CLEANUP AFTER T03 CLOSED** | Giữ file trung gian ignored đến khi T03 CLOSED; ưu tiên giữ `candidates_batch*.csv` và `*_evidence.csv` để truy vết nguồn. |

T03 vẫn ở `PO_REVIEW`. Codex không PO approve, không merge, không tag, không đóng T03 và không mở T04.
