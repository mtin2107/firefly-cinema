# Codex — Implementation T03 — 07/10/2026

## 1. Thông tin thực hiện

| Mục | Giá trị |
|---|---|
| Task | T03 — Bộ dữ liệu bình luận phim |
| Vai trò | Codex — Primary Implementer |
| Branch | `task/T03-du-lieu-phim` |
| Baseline | `c1480b56f8273cfccdb875b7c1eaca06eadbf9a2` (`master` và `HEAD` trùng nhau lúc bắt đầu) |
| Trạng thái sau implementation | `IN_PROGRESS` — `WAITING_FOR_DATA` |
| Đổi schema | Không |

Không tự review, không kết luận PASS, không chuyển `CLAUDE_REVIEW`, không PO approve và không merge.

## 2. File Codex đã sửa/tạo

| File | Nội dung |
|---|---|
| `ml/labeling_guideline.md` | Định nghĩa nhãn 0/1, quy tắc câu pha trộn/châm biếm, 30 ví dụ biên khó, quy trình Annotator A/B và cấm LLM gán nhãn |
| `ml/src/prepare_movie_data.py` | Kiểm tra schema/nhãn/nguồn/PII; dùng trực tiếp `normalize()` backend; khử trùng; split 70/30 stratified seed 42; mẫu kappa và thống kê |
| `data/README.md` | Vị trí/schema dữ liệu, quy tắc nguồn, dữ liệu ngoài Git, cách chạy và hướng dẫn gán nhãn B |
| `ml/results/movie_data_stats.md` | Thống kê thật của dữ liệu hiện có: 0 dòng, trạng thái `WAITING_FOR_DATA`; không bịa metric |
| `docs/TASK_COORDINATION_ACTIVE.md` | Chuyển T03 `READY_FOR_HANDOFF` → `IN_PROGRESS`, ghi blocker và next action |
| `reports/2026-10-07/codex_implementation_T03_2026-10-07.md` | Report này |

Các thay đổi đã có trước implementation trong `docs/PROJECT_SOURCE_OF_TRUTH.md`, `docs/tasks/T03.md`, `data/phim/NGUON_THU.md` và report quyết định Q1 được bảo toàn; Codex không sửa chúng. Không sửa `backend/**`, `frontend/**`, `normalize()` hoặc CSV dữ liệu.

## 3. Thiết kế và hành vi chính

- Schema dữ liệu gốc phải đúng thứ tự `id,text,label,source_type,note`.
- `source_type` chỉ nhận `review_site`, `social`, `self_written`, `web_firefly`; label chỉ nhận 0/1.
- Script import đúng `backend.app.classifier.normalize`; không chép lại hoặc sửa production code.
- Dòng có email, số điện thoại hoặc `@username` trong `text`/`note` làm gate dừng và báo rõ ID, cột, loại PII.
- Duplicate được xác định sau `normalize()`, giữ dòng xuất hiện đầu tiên và in số dòng bị loại.
- Split dùng `train_test_split(..., test_size=0.30, stratify=label, random_state=42)`; kiểm tra giao tập normalized bằng 0 trước khi ghi CSV.
- Chỉ tạo mẫu kappa sau khi có ít nhất 400 câu cuối. `label_b` luôn để trống khi tạo; script không giả hoặc tự điền nhãn B.
- Nếu mẫu kappa đã tồn tại, script kiểm tra đúng 100 ID seed 42 và không ghi đè. Chỉ khi đủ 100 nhãn B thật mới tính Cohen's kappa.
- CSV nằm ngoài Git theo `.gitignore`; các file train/test/kappa không được thêm vào Git.

## 4. Lệnh đã chạy và kết quả

### 4.1 Xác minh branch và baseline

```powershell
git branch --show-current
git status --short --branch
git log -1 --format='%H %s'
git merge-base master HEAD
git rev-parse master
git rev-parse HEAD
```

Kết quả: đúng branch `task/T03-du-lieu-phim`; baseline/`master`/`HEAD` đều là `c1480b56f8273cfccdb875b7c1eaca06eadbf9a2` lúc bắt đầu.

### 4.2 Gate bắt buộc trên dữ liệu hiện có

```powershell
python ml\src\prepare_movie_data.py --input data\phim\movie_comments_v1.csv --out data\phim
```

Kết quả sau khi sửa lỗi encoding Windows:

```text
Raw rows: 0
Duplicate removed after normalize(): 0
Final rows: 0
PII scan: 0 findings
STATUS: WAITING_FOR_DATA — CSV mới có header, chưa có bình luận thật.
EXIT_CODE=0
```

Không tạo train/test/kappa vì chưa có dòng dữ liệu. Đây không phải bằng chứng AC-01 hay AC-02 đạt trên bộ dữ liệu cuối.

### 4.3 Biên dịch và kiểm tra chức năng tập trung

```powershell
python -m py_compile ml\src\prepare_movie_data.py
```

Kết quả: exit code 0.

Đã chạy probe trong bộ nhớ và thư mục tạm, không ghi dữ liệu giả vào `data/phim/`, gồm:

- xác nhận `prepare_movie_data.normalize is backend.app.classifier.normalize`;
- hai câu “ko”/“không” trùng nhau sau normalize và bị loại đúng;
- hai lần split seed 42 cho cùng danh sách ID train/test;
- duplicate cross-split bằng 0;
- phát hiện email, số điện thoại và `@username`;
- mẫu kappa ban đầu trả `WAITING_FOR_HUMAN_LABEL`, sau khi probe tạm có đủ hai nhãn giống nhau thì công thức trả kappa 1,0.

Kết quả: `FUNCTIONAL_TESTS_OK`.

## 5. Trạng thái Acceptance Criteria

| AC | Trạng thái implementation/evidence | Ghi chú |
|---|---|---|
| AC-01 | **WAITING_FOR_DATA — chưa đủ evidence** | 0/400 câu cuối; script đã in duplicate removed = 0 trên file chỉ có header. Không đánh dấu PASS. |
| AC-02 | **WAITING_FOR_DATA — chưa đủ evidence** | PII scan = 0 trên 0 dòng không chứng minh bộ dữ liệu cuối sạch PII. |
| AC-03 | **WAITING_FOR_DATA / WAITING_FOR_HUMAN_LABEL** | Chưa có mẫu 100 câu và chưa có `label_b` thật của “Người 1”; không có kappa để báo. |
| AC-04 | **CODE VERIFIED, DATA EVIDENCE PENDING** | Logic split 70/30 stratified seed 42 và tính tái lập ID đã qua probe; chưa có split dữ liệu thật cuối. |
| AC-05 | **CODE VERIFIED, DATA EVIDENCE PENDING** | Logic normalized cross-split đã qua probe; chưa có split dữ liệu thật cuối. |
| AC-06 | **PARTIAL / WAITING_FOR_DATA** | README và file stats đã có; số liệu/kappa cuối chưa thể ghi khi chưa có dữ liệu thật. |

Các trạng thái trên là báo cáo implementation, không phải kết luận review/PASS thay Claude.

## 6. Dữ liệu Tín còn cần thực hiện

1. Thu thủ công 400–600 bình luận thật vào `data/phim/movie_comments_v1.csv`.
2. Gán nhãn A cho toàn bộ theo `ml/labeling_guideline.md`.
3. Bảo đảm `review_site + social ≥ 80%`, `self_written ≤ 20%`, ít nhất 20 phim, mỗi phim tối đa 30 câu và mỗi nguồn cụ thể tối đa 40%; giữ teencode/câu không dấu/emoji nhưng bỏ toàn bộ PII.
4. Chạy lại script trong quá trình thu để xử lý duplicate, cân tỷ lệ label 1 về 35–60% và kiểm tra PII.
5. Khi script tạo `kappa_sample.csv`, gửi bản không lộ `label_a` cho “Người 1”; sau đó ghép 100 nhãn B thật theo ID và chạy lại script.
6. Sao lưu CSV ngoài Git lên `MyDrive/thesis/data/movie/`.

## 7. Trạng thái Annotator B

**WAITING_FOR_DATA.** “Người 1” chưa thể gán vì dataset cuối chưa đạt 400 câu và `kappa_sample.csv` chưa được tạo. Script không tự điền `label_b`.

## 8. Blocker và next action

- Blocker hiện tại: `BLOCKED_BY_DATA_COLLECTION` / `WAITING_FOR_DATA` — CSV chỉ có header.
- Blocker kế tiếp: `WAITING_FOR_HUMAN_LABEL` sau khi có đủ dữ liệu và mẫu 100 câu.
- T03 được giữ ở `IN_PROGRESS`. Chỉ chuyển `CLAUDE_REVIEW` khi AC-01 đến AC-06 có evidence thực tế, gồm dữ liệu cuối, PII scan, split, duplicate cross-split và kappa ≥ 0,6.

## 9. Checklist hồi quy và phạm vi

- Backend/frontend: không sửa, nên không chạy gate web.
- Đổi schema: Không.
- Dữ liệu CSV: ngoài Git; không dùng `git add .` và không force-add CSV.
- `git status --short --branch`: đúng branch; hiện có các file implementation T03 và các thay đổi Q1 có sẵn từ trước. `data/phim/` hiện lên vì `NGUON_THU.md` chưa track; CSV bên trong vẫn ignored.
- `git diff --check`: exit code 0; chỉ có cảnh báo Git sẽ đổi LF thành CRLF khi chạm hai file Markdown đã track.
- `git diff --name-only master...HEAD`: rỗng vì branch chưa có commit mới so với baseline; lệnh này không liệt kê working tree/untracked files.
- `git diff --name-only`: có `data/README.md`, `docs/PROJECT_SOURCE_OF_TRUTH.md`, `docs/TASK_COORDINATION_ACTIVE.md`, `docs/tasks/T03.md`; hai file `PROJECT_SOURCE_OF_TRUTH.md` và `tasks/T03.md` là thay đổi Q1 đã tồn tại trước lượt implementation.
- `git ls-files 'data/phim/*.csv'`: rỗng. `git check-ignore -v` xác nhận cả bốn CSV T03 khớp rule `.gitignore` `data/**/*.csv`.
- Kiểm tra trailing whitespace riêng cho các file mới: không phát hiện.
