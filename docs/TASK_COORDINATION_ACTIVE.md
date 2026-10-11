# TASK COORDINATION — ACTIVE

> Single active source of truth cho task đang chạy. Không chép lịch sử task CLOSED vào đây, chỉ giữ tóm tắt 1 dòng.
> Mỗi lần đổi trạng thái: sửa file này trong repo, commit, rồi tải lại bản mới lên nguồn ChatGPT/Codex.

## 1. Project Snapshot
Firefly Cinema — website đặt vé phim + PhoBERT phân loại bình luận tiêu cực. Khóa luận #67 NTTU.
Repo `C:\Projects\firefly-cinema`, nhánh `master`. Chi tiết: `PROJECT_SOURCE_OF_TRUTH.md`.

## 2. Stable Rules (tóm tắt — bản đầy đủ ở ARCHITECTURE.md và BOI_CANH_DU_AN.md mục 6)
- Frontend chỉ gọi API qua `src/api/index.js`; endpoint mới có ở cả `real.js` và `mock.js`.
- Luật ghế, dữ liệu phim, taxonomy phải đồng bộ hai nơi.
- Endpoint admin dùng `require_admin` (user thường → 403). Lỗi trả một câu tiếng Việt.
- Không sửa `normalize()` khi chưa đo lại F1. Không thêm thư viện khi chưa hỏi Tín.
- Không commit `.env`, `firefly.db`, `backend/models/`, model, dữ liệu lớn.
- Mỗi task một nhánh `task/Txx-ten-ngan`, commit `[Txx] mô tả`. Chỉ Tín merge.

## 3. Latest Completed Task Summary
**T10 — Gắn model B vào web: DONE / CLOSED (11/10/2026).** Claude Final PASS_WITH_TODO, PO APPROVED_WITH_NOTES, AC 7/7 PASS, Technical DoD MET, Required Fixes 0; Gate 2 ALTER_COMMITTED, Postverify/Clone Smoke Attempt 2/Hash Reconciliation/DEV Final QA PASS; fast-forward merge và annotated tag `phobert-B` tại release commit `857a8272a9c307734e713a2b5cdae12f8f60bb95` đã được xác minh. Line-ending reconciliation PASS; database thật được bảo toàn. F-TODO-01/03 đã xử lý; F-TODO-02/04/05/06/07 giữ nguyên disposition ACCEPT_LATER.

Trước đó: **T09 — Train PhoBERT phần B: DONE / CLOSED (09/10/2026)**, merge `27c364e`; **T08 — Đo lệch miền điện thoại → phim: DONE / CLOSED (09/10/2026)**, merge `778675e`.

Trước khi áp dụng workflow: giao diện React đầy đủ (`giao-dien-v1`), backend FastAPI + SQLite, PhoBERT A gắn vào backend, F1 test 0,918 (`phobert-v1`).

## 4. Current Project Status
```
Overall Status: IN_PROGRESS / BLOCKED_PENDING_PO_RUNTIME_GATE
Phase: T11 — Kiểm thử tự động và sửa lỗi
Current Active Task: T11 — IN_PROGRESS / BLOCKED_PENDING_PO_RUNTIME_GATE
Next Task: T12 — PLANNED / NOT AUTHORIZED
Ngày bắt đầu sản phẩm: 05/10/2026 · Hạn: 01/11/2026
```

## 5. Current Active Task
**T11 — Kiểm thử tự động và sửa lỗi: IN_PROGRESS / BLOCKED_PENDING_PO_RUNTIME_GATE.** PO authorize ngày 11/10/2026 theo Task Record `docs/tasks/T11.md`, gồm ngoại lệ cho phép thêm duy nhất `pytest` và `httpx` vào `backend/requirements-dev.txt`. Pre-flight PASS: đúng nhánh `task/T11-kiem-thu`, working tree sạch, release T10 `857a8272a9c307734e713a2b5cdae12f8f60bb95` là ancestor, T04–T10 đều DONE / CLOSED và không có task khác IN_PROGRESS. Trạng thái đã đi qua `PLANNED → READY_FOR_HANDOFF → IN_PROGRESS`. DEV gates ngoài AC-06 đã hoàn tất; AC-06 web với model thật còn PENDING vì chưa có runtime authorization riêng.

T10 giữ nguyên **DONE / CLOSED**. Runtime backend trên database thật vẫn bị cấm nếu chưa có checkpoint/backup và authorization riêng của PO; T11 chỉ dùng SQLite tạm.

## 6. Current Task Record
Task Record hiện tại: [`docs/tasks/T11.md`](tasks/T11.md).

T07 và T09 đã DONE / CLOSED. TODO-02 của T09 đã RESOLVED theo xác nhận PO ngày 10/10/2026; evidence notebook ở mức `PO_ATTESTED`, không phải Claude xác minh độc lập. Q3 đã được PO phê duyệt: PhoBERT B là model mặc định, PhoBERT A được giữ làm fallback hoặc chọn qua `.env` và restart backend; không bổ sung giao diện admin chọn model.

## 7. Roadmap và trạng thái

| ID | Task | Loại | Tuần | Phụ thuộc | Task Record | Trạng thái |
|---|---|---|---|---|---|---|
| T00 | Gom mã và dữ liệu về project ổ C, model card A | ML | 1 | — | [T00.md](tasks/T00.md) | PO_APPROVED (đã có trên master tại `20daf6a`) |
| T01 | Mô hình truyền thống (NB, LR, SVM) | ML | 1 | T00 | [T01.md](tasks/T01.md) | DONE / CLOSED |
| T02 | So sánh PhoBERT với mô hình truyền thống | ML | 1 | T01 | [T02.md](tasks/T02.md) | DONE / CLOSED (merge `6d5fda5`, tag `ml-baselines`) |
| T03 | Bộ dữ liệu bình luận phim | Dữ liệu | 1–2 | — | [T03.md](tasks/T03.md) | DONE / CLOSED (Claude PASS_WITH_TODO; PO APPROVED; merge `6bd1a3f`; Drive VERIFIED) |
| T04 | Quản lý phim (admin) | Web | 2 | — | [T04.md](tasks/T04.md) | DONE / CLOSED (Claude PASS_WITH_TODO; PO APPROVED; AC 7/7; RF 0; blocker 0; SD-01/SD-02 approved retroactively; merge `fced3d7`) |
| T05 | Quản lý suất chiếu (admin) | Web | 2 | T04 | [T05.md](tasks/T05.md) | DONE / CLOSED (Claude Round 2 PASS_WITH_TODO; AC 8/8 PASS; DoD MET; RF-01 CLOSED; RF mở 0; PO APPROVED; merge `54a3715`; T05_MERGE_VERIFIED) |
| T06 | Kiểm duyệt có người duyệt (đổi schema) | Web | 2 | — | [T06.md](tasks/T06.md) | DONE / CLOSED (Claude Round 2 PASS_WITH_TODO; PO APPROVED; AC 8/8; hồi quy 7/7; RF-01 CLOSED; RF mở 0; TODO 6/6 dispositioned; merge `81330c2`; T06_MERGE_VERIFIED) |
| T07 | Đa mô hình và trang So sánh mô hình | Web + ML | 2 | T01 | [T07.md](tasks/T07.md) | DONE / CLOSED (Claude Round 2 PASS_WITH_TODO; AC 8/8; hồi quy 7/7; DoD MET; RF-01 CLOSED; RF mở 0; blocker 0; TODO 6/6 dispositioned; merge `434a489`; tag `admin-v1`; T07_MERGE_VERIFIED) |
| T08 | Đo lệch miền điện thoại → phim | ML | 3 | T02, T03 | [T08.md](tasks/T08.md) | DONE / CLOSED (Claude PASS_WITH_TODO; PO APPROVED; AC 5/5 PASS; DoD MET; RF 0; blocker 0; TODO 5/5 dispositioned, deferred chưa RESOLVED; merge `778675e`; T08_MERGE_VERIFIED) |
| T09 | Train PhoBERT phần B | ML | 3 | T08 | [T09.md](tasks/T09.md) | DONE / CLOSED (Claude PASS_WITH_TODO; PO APPROVED; AC 6/6; DoD MET theo PO; RF 0; blocker 0; TODO 7/7 dispositioned; TODO-02 RESOLVED 10/10/2026 theo PO, notebook `PO_ATTESTED`; merge `27c364e`; T09_MERGE_VERIFIED) |
| T10 | Gắn model B vào web | Web | 3 | T07, T09 | [T10.md](tasks/T10.md) | DONE / CLOSED — PO APPROVED_WITH_NOTES; Claude Final PASS_WITH_TODO; AC 7/7; Technical DoD MET; RF 0; fast-forward merge + annotated tag `phobert-B` VERIFIED tại `857a8272` |
| T11 | Kiểm thử tự động và sửa lỗi | Web | 4 | T04–T10 | [T11.md](tasks/T11.md) | IN_PROGRESS / BLOCKED_PENDING_PO_RUNTIME_GATE |
| T12 | Dữ liệu demo và kịch bản bảo vệ | Web | 4 | T10 | [T12.md](tasks/T12.md) | PLANNED |
| T13 | Chốt v1.0 và sao lưu | Tất cả | 4 | T11, T12 | [T13.md](tasks/T13.md) | PLANNED |
| T14 | *(tùy chọn)* Hủy vé, đổi mật khẩu | Web | dư | — | [T14.md](tasks/T14.md) | PLANNED |
| T15 | *(tùy chọn)* Thử nghiệm có tách từ | ML | dư | T09 | [T15.md](tasks/T15.md) | PLANNED |

Chuỗi chính: `T00 → T01 → T02` và `T03 → T08 → T09 → T10`. T03 bắt đầu ngay ngày đầu (song song).
Nếu trễ: cắt T14 → T15 → rút gọn T05. Không cắt T01–T03, T07–T10.

## 8. Open Blockers
- T11: **AC-06 PENDING / BLOCKED_PENDING_PO_RUNTIME_GATE.** Full pytest 20/20, isolated no-torch/no-model 20/20, compile/build real+mock, health DB tạm và scope/security gates PASS. Chưa được phép chạy web với model thật trên database thật; cần checkpoint/backup và PO runtime authorization riêng. Không chuyển `CLAUDE_REVIEW` trước gate này.
- T09: **DONE / CLOSED**, 0 blocker; merge `27c364e` đã xác minh (`T09_MERGE_VERIFIED`). TODO-02 **RESOLVED 10/10/2026 theo xác nhận PO**; evidence notebook là `PO_ATTESTED`, không phải Claude kiểm tra độc lập.
- T10: **DONE / CLOSED**, 0 blocker kỹ thuật; RF-01 CLOSED / VERIFIED BY CLAUDE. Gate 2 **EXECUTED / ALTER_COMMITTED**; Postverify PASS; 559 dòng gốc bảo toàn; Credential Precheck V2 PASS; Clone Smoke Attempt 1 FAIL / ARCHIVED; Attempt 2 PASS; Hash Reconciliation PASS; DEV Final QA PASS; Claude Final PASS_WITH_TODO; PO APPROVED_WITH_NOTES; fast-forward merge và annotated tag `phobert-B` VERIFIED. Real backend startup vẫn cần authorization riêng của PO; T11 không được dùng database thật.
- T08: **DONE / CLOSED**, 0 blocker; merge `778675e` đã xác minh (`T08_MERGE_VERIFIED`). TODO 5/5 đã disposition; deferred chưa RESOLVED.
- T06: 0 blocker; RF-01 CLOSED (Claude Round 2 xác minh 09/10/2026). `PENDING_PO_DATABASE_RESET` **RESOLVED 09/10/2026** — backup giữ nguyên checksum/integrity; database thật mới đủ schema, seed; AC 8/8 DEV PASS và regression real/mock 7/7.
- T04: 0 technical blockers; SD-01/SD-02 đã được PO phê duyệt hồi tố, không còn chặn merge.
- Q1 (nguồn bình luận phim, người gán nhãn thứ 2): RESOLVED 07/10/2026 — xem `PROJECT_SOURCE_OF_TRUTH.md` mục 5 và `docs/tasks/T03.md` mục 13.
- T03: RESOLVED — PO APPROVED, Drive Backup VERIFIED, DONE / CLOSED, merge `6bd1a3f`.
- T05 scope conflict: phim `ended` vẫn có thể bị đặt vé qua endpoint trực tiếp; fix nguồn cần sửa `backend/app/routers/bookings.py` ngoài allowlist T05. UI đã ẩn lịch ended và T05 chặn tạo/cập nhật suất cho phim ended. Claude xác minh 08/10: vẫn tồn tại (booking suất phim ended → `201`), không chặn AC T05. **PO chọn phương án B: ACCEPT_LATER → T11**; vấn đề chưa được sửa trong T05.
- Q2: **RESOLVED 08/10/2026 — NO ALEMBIC / BACKUP_BEFORE_RESET.** Sao lưu và xác minh đúng database trước khi PO tự reset; Codex không tự xóa database thật.

## 9. Open Required Fixes
- **Open Required Fixes: 0.** T10 RF-01 (Medium) **CLOSED / VERIFIED BY CLAUDE** (Round 2): per-model `RLock` bao nạp/suy luận/giải phóng; 116 request admin predict đồng thời hai chiều + 8 request trộn comment/predict, 0 lỗi; fallback/security/AC 7/7 giữ nguyên. Evidence: `reports/2026-10-10/claude_review_T10_round2_PASS_WITH_TODO_2026-10-10.md`.
- T09 DONE / CLOSED (RF 0); T08 DONE / CLOSED.
- T07 RF-01 (Medium) **CLOSED / VERIFIED BY CLAUDE**: fix `06fbd3d` bỏ `min_length=1`; Claude probe độc lập trên uvicorn thật + DB tạm: ba dạng chuỗi rỗng 422 đúng câu tiếng Việt, biên 1.000/1.001, 401/403, contract và health giữ nguyên (12/12). Evidence: `reports/2026-10-09/claude_review_T07_round2_PASS_WITH_TODO_2026-10-09.md`.
- T06 RF-01 (Medium) **CLOSED / VERIFIED BY CLAUDE**: fix commit `8ef57ad` (`isinstance(value, str)` trước membership); Claude probe độc lập trên DB tạm `action` list/dict/123/true/null/"delete" và 4 ca thêm đều trả 422 đúng câu, dữ liệu không đổi; uvicorn thật cũng trả 422. Evidence: `reports/2026-10-09/claude_review_T06_round2_PASS_WITH_TODO_2026-10-09.md`.
- T05 RF-01 (High) **CLOSED** — Claude Round 2 xác minh độc lập: fix commit `f5fca8d`; fresh real/mock đều có đủ 9 phim mỗi ngày, hot_week đủ 9, 0 cặp chồng, restart giữ nguyên suất admin/booking. Evidence: `reports/2026-10-08/codex_fix_T05_round1_2026-10-08.md`.

Đã đóng: T04 RF 0; RF-01, RF-02 của T02 CLOSED (Claude review vòng 2); RF-01 → RF-03 của T00 đã đóng; T01 không có RF.

## 10. Open TODOs
| Nguồn | TODO | Disposition |
|---|---|---|
| Nợ kỹ thuật | `requirements-ml.txt` còn `underthesea`, chưa ghim phiên bản; `HUONG_DAN.md` 4.2 | Đã sửa và PO duyệt trong T00 |
| Phát hiện 03/10 | `backend/.env.example` ghi `USE_WORD_SEGMENT=true`, thiếu `USE_TEXT_NORM` — lệch BOI_CANH 3.4 | Đã sửa và PO duyệt trong T00 |
| Claude review T00 r2 | TODO-01 hai checkpoint model A | RESOLVED trong T02 — đo cả hai; canonical research = `ml/artifacts/phobert_A_best`, runtime web giữ `backend/models/phobert-binhluan` |
| Claude review T00 r2 | TODO-02 `normalize()` ≠ `text_utils.py` | RESOLVED trong T02 — max \|Δ F1\| 0,003217 < 0,01, không sửa `normalize()` |
| Claude review T00 r2 | TODO-03 `firefly_phobert.zip` trên Drive chưa xác minh | ACCEPT_LATER — T13; xác minh file, checksum, khả năng khôi phục |
| Claude review T00 r2 | TODO-04 thụt lề `HUONG_DAN.md` 4.2 | WONT_FIX — Markdown hiển thị đúng, không ảnh hưởng nghiệm thu |
| Nợ kỹ thuật | `_SAMPLE_SALES` lặp ở `seed.py` và `mock.js` | T12 (tùy chọn) |
| Nợ kỹ thuật | `/api/admin/comments` chưa phân trang | Đưa vào T06 |
| Nợ kỹ thuật | `comments.model_name` chưa có phiên bản | Đưa vào T10 |
| Phát hiện 04/10 | `chay-firefly.bat` không có trong repo dù tài liệu ghi "Xong" | Chờ PO: commit file từ máy Tín hoặc đưa vào T00 |
| Phát hiện 04/10 | Thư mục rỗng `Bao_cao\` ở gốc | Đã xử lý 04/10: giữ làm nơi để bản Word (`*.docx` ngoài Git) |
| T11 | Cần thêm `httpx` (TestClient) cùng `pytest` | **RESOLVED 11/10/2026 — PO cho phép riêng trong `backend/requirements-dev.txt`** |
| Claude review T01 | TODO-01 ba `.joblib` chưa có trên `MyDrive/thesis_results/baselines/` | ACCEPT_WITH_ACTION — Tín upload trước khi bắt đầu implementation T02 |
| Claude review T01 | TODO-02 `baselines.py` viết lại, bỏ baseline Task B/C + ablation `text_raw`, report Codex không ghi | ACCEPT — PO chấp nhận, không yêu cầu sửa T01 |
| Claude review T01 | TODO-03 `EXPECTED_SPLITS` cố định cho UIT-ViSFD | ACCEPT_LATER → T09 |
| Claude review T01 | TODO-04 `ms_per_sentence` dùng `process_time` (độ phân giải Windows thô, dao động ~2×) | ACCEPT_LATER → T02; đo CPU 4 mô hình cùng phương pháp bằng `time.perf_counter` — RESOLVED trong T02 (`perf_counter`) |
| Claude review T02 | TODO-01 latency phụ thuộc tải máy; cách dựng môi trường torch + sklearn | Đã xử lý round 1: report ghi interpreter, `PYTHONPATH`, phiên bản và lưu ý ưu tiên thứ tự/tỉ lệ |
| Claude review T02 | TODO-02 không checkpoint nào tái lập `phobert_A.json` (macro 0,9128 / acc 0,9141) | ACCEPT_LATER / DOCUMENTED — HISTORICAL / NOT FULLY REPRODUCED, không dùng làm metric canonical |
| Claude review T02 | TODO-03 notebook thiếu assert AC-03 và marker | Đã xử lý round 1: có assert parity và `NOTEBOOK_EXECUTION_OK` thực |
| Claude review T02 | TODO-04 `size_mb` là MiB nhưng ghi MB | Đã ghi chú: giữ schema, giá trị tính theo MiB (`1024²` byte) |
| Claude review T02 r2 | TODO-R2-01 chọn checkpoint chính thức (gốc 0,9216 / backend 0,9178) | RESOLVED — PO chọn canonical research `ml/artifacts/phobert_A_best`; thay model backend (nếu có) là task riêng |
| Claude review T02 r2 | TODO-R2-02 lệnh chạy (interpreter + `PYTHONPATH`) chỉ có trong fix report; tiêu đề mục benchmark model card còn ghi 05/10 | ACCEPT_LATER → T13 (`HUONG_DAN.md`) |
| Claude review T02 r2 | TODO-R2-03 category index 72 và 136 còn tranh luận được | WONT_FIX |
| Claude review T03 | TODO-01 branch chưa commit; `movie_comments_v1.md` không bị ignore; cần tách implementation/PO | RESOLVED — đã xóa file Markdown dữ liệu; CSV ignored; tách commit; `NGUON_THU.md` không commit |
| Claude review T03 | TODO-02 script chưa chặn ≥ 20 phim / ≤ 30 câu/phim / ≤ 40 %/nguồn | ACCEPT_LATER / DOCUMENTED — v1 hiện đạt; thêm gate nếu dataset v2 thay đổi |
| Claude review T03 | TODO-03 chuỗi "67,94%" hard-code trong script | ACCEPT_LATER / LOW PRIORITY — không ảnh hưởng AC, không quay lại FIX_LOOP |
| Claude review T03 | TODO-04 provenance thu/gán/chép nhãn | DOCUMENTED — Claude đề xuất ứng viên; Tín duyệt và gán A; Người 1 gán B; Claude chỉ chép nhãn theo ID sau lỗi ANSI; không sửa nhãn tăng kappa |
| Claude review T03 | TODO-05 giới hạn độc lập do Claude hỗ trợ thu dữ liệu | ACCEPT_WITH_DISCLOSURE — không gán A/B; kiểm tra cơ học tái lập; ghi minh bạch trong khóa luận/report |
| Claude review T03 | TODO-06 kappa 0,6025 sát ngưỡng, 19/100 bất đồng | ACCEPT_WITH_DISCLOSURE — mức đồng thuận vừa phải; không sửa nhãn; ghi trong khóa luận |
| Claude review T03 | TODO-07 chưa xác minh 4 CSV trên Drive | PO ACTION REQUIRED — Tín upload/kiểm tra tại `MyDrive/thesis/data/movie/` trước khi đóng T03 |
| Claude review T03 | TODO-08 dọn file trung gian | ACCEPT_LATER — CLEANUP AFTER T03 CLOSED; giữ candidates/evidence để truy vết |
| Claude review T04 | SD-01 `frontend/src/utils/taxonomy.js` ngoài allowlist (refactor không đổi hành vi; report Codex ghi sai "đúng allowlist") | APPROVED RETROACTIVELY — ngoại lệ scope T04; quy tắc allowlist task sau giữ nguyên |
| Claude review T04 | SD-02 `global.css` sửa `.container`/`.page-title` (≤600px, toàn site) và mở rộng `.field input` | APPROVED RETROACTIVELY — Claude đã xác minh không regression |
| Claude review T04 | TODO-01 report Codex khẳng định sai về allowlist; TODO-02 T04 mục 13 ghi "23 mục" (đúng: 22 thể loại) | TODO-01 DOCUMENTED / PROCESS CORRECTION; TODO-02 ACCEPT_LATER — documentation |
| Claude review T04 | TODO-03 422 sai kiểu/thiếu trường còn câu Pydantic tiếng Anh; TODO-04 `genre` String(100) có thể vượt | ACCEPT_LATER → T11 |
| Claude review T04 | TODO-05 xóa phim xóa luôn bình luận; TODO-06 câu 422 mock thiếu tiền tố; TODO-08 mock reset vé mỗi ngày | TODO-05 ACCEPT; TODO-06 và TODO-08 WONT_FIX |
| Claude review T04 | TODO-07 phim mới chưa có suất chiếu; phim `ended` vẫn đặt vé được suất tương lai | Vế phim mới RESOLVED trong T05 (AC-06 Claude xác minh); vế booking phim ended **vẫn tồn tại** — PO chọn phương án B, ACCEPT_LATER → T11; chưa sửa trong T05 |
| Claude review T05 | TODO-01 mock khóa mọi suất seed do ghế giả `seedBooked` | ACCEPT_LATER → T11 |
| Claude review T05 | TODO-02 sửa suất phim ended hiện ô Phim trống | ACCEPT |
| Claude review T05 | TODO-03 `find_showtime_conflict` không lọc theo ngày | ACCEPT_LATER → T11 |
| Claude review T05 | TODO-04 report Codex không đối chiếu số suất theo phim | RESOLVED |
| Claude review T05 r2 | TODO-05 (Medium) suất seed admin đã xóa được seed tạo lại khi restart backend | ACCEPT_LATER → T11; ưu tiên trước demo |
| Claude review T05 r2 | TODO-06 (Low) phân bổ không đều (phim 9/10/18 1 suất/ngày), DB cũ giữ 190 cặp chồng lịch sử, lần đầu chạy trên `firefly.db` thật thêm 38 suất | ACCEPT_WITH_NOTES → T12 |
| Claude review T06 r2 | TODO-01 lỗi 422 còn nội dung Pydantic tiếng Anh | ACCEPT_LATER → T11 |
| Claude review T06 r2 | TODO-02 mock và real chưa đồng bộ validation `label`/`reviewed` không hợp lệ | ACCEPT_LATER → T11 |
| Claude review T06 r2 | TODO-03 CSV formula injection; phải bảo toàn text gốc phục vụ huấn luyện | ACCEPT_LATER → T11 / RISK ACKNOWLEDGED — rủi ro chưa sửa |
| Claude review T06 r2 | TODO-04 câu chữ khi admin đổi nhãn hoặc model đánh giá tiêu cực | ACCEPT_LATER → T12 |
| Claude review T06 r2 | TODO-05 dữ liệu kiểm thử trong database trước khi chuẩn bị demo | ACCEPT_LATER → T12 — phải backup, không tự xóa DB |
| Claude review T06 r2 | TODO-06 Task Record còn ghi PLANNED; API không thêm undo review/audit hide-unhide | ACCEPT_WITH_NOTES — coordination là nguồn trạng thái hoạt động; chấp nhận phạm vi API hiện có |
| Claude review T07 | TODO-01 (Medium, demo) câu mẫu "lê thê": PhoBERT backend 0,0485 (bình thường), research `phobert_A_best` 0,9602 | ACCEPT_LATER → T08/T09/T10 — giữ checkpoint backend hiện tại; không thay model trong T07 |
| Claude review T07 | TODO-02 `/api/admin/predict` không cô lập exception từng model (một model lỗi → 500) | ACCEPT_LATER → T11 |
| Claude review T07 | TODO-03 health công khai trả lỗi thô (đường dẫn tuyệt đối, `"110"` khi joblib hỏng) | ACCEPT_LATER → T11 |
| Claude review T07 | TODO-04 422 thiếu/sai kiểu/quá 1.000 ký tự còn câu Pydantic tiếng Anh | ACCEPT_LATER → T11 |
| Claude review T07 | TODO-05 health không có trường `ACTIVE_MODEL` được yêu cầu khi fallback | ACCEPT_LATER → T10 |
| Claude review T07 | TODO-06 report Codex ghi AC-05 PASS khi chưa thử `""` | ACCEPT_WITH_NOTES — fix report/Round 2 đã kiểm đủ; task sau phải kiểm ca biên trước khi ghi PASS |
| Claude review T08 | TODO-01 (Medium) F1_neg movie bị đẩy lên do tỷ lệ tiêu cực 67,8% (baseline hằng đạt 0,808) | **RESOLVED trong T09** (Claude xác minh: constant rows tái lập Δ 0) — đã ghi F1_neg, Macro-F1 và baseline hằng trên hai test set; giới hạn lệch nhãn vẫn được disclosure |
| Claude review T08 | TODO-02 (Low) movie test 149 câu; CI 95% ΔF1_neg cận dưới 0,010–0,023 | **ACCEPT_WITH_DISCLOSURE**; công bố giới hạn 149 câu/CI 95%, T09 dùng cùng movie test |
| Claude review T08 | TODO-03 (Low) notebook phụ thuộc cwd | **RESOLVED ở mức code trong T09** (PO, theo T09 TODO-05) — tìm repo/fallback code ZIP; clean-run Colab chưa được Claude xem trực tiếp |
| Claude review T08 | TODO-04 (Low) thiếu output notebook, Drive path và hướng dẫn ghép môi trường | **ACCEPT_WITH_NOTES → T13, chưa RESOLVED** (PO sửa theo T09 TODO-05) — Drive path/ID và hướng dẫn đã có trong T09; notebook Git vẫn 0 output |
| Claude review T08 | TODO-05 (Info) PhoBERT nhạy với `normalize()` ở câu "lê thê" | **RESOLVED trong T09** (Claude xác minh parity 11.618/11.618; `normalize()` không đổi) — T10 vẫn phải dùng artifact đã xác minh hash và kiểm câu "lê thê" |
| Claude review T09 | TODO-01 (Low) notebook Git 0 output; run1/run2 chỉ ở Drive; notebook Git khác bản chạy 1 dòng chữ template | ACCEPT_LATER → T13 |
| Claude review T09 | TODO-02 (Medium, PO action trước T10) Claude chưa xác minh trực tiếp evidence GPU; `ml\artifacts\phobert_B_best\` chưa có trên máy | **RESOLVED 10/10/2026 theo xác nhận PO** — SHA-256 artifact 4/4 PASS; checkpoint local + tokenizer/config nạp CPU PASS; 149 câu đạt F1_neg `0.917525773196`, Macro-F1 `0.881839809675`; probe negative score `0.998829185963`; run1/run2 có `SELECTION_LOCKED=True` trước `FINAL_TEST_COMPLETE=True` ở mức `PO_ATTESTED`, không phải Claude kiểm tra độc lập |
| Claude review T09 | TODO-03 (Low) model card sửa tay sau run; chưa nêu refit truyền thống 347+347 vs PhoBERT 294, biên chọn b = 1 câu validation | ACCEPT_LATER → T13 / khóa luận |
| Claude review T09 | TODO-04 (Low) không lưu dự đoán từng câu → chưa có kiểm định cặp A–B | ACCEPT_LATER → T10 (sau TODO-02) / khóa luận — không dùng để chọn lại model |
| Claude review T09 | TODO-05 (Low, process) T08 TODO-04 ghi RESOLVED quá mức (notebook Git chưa có output); TODO-03 chỉ RESOLVED mức code | ACCEPT_WITH_NOTES — đã sửa disposition T08 ở trên; Codex không tự đổi TODO do PO disposition sang RESOLVED |
| Claude review T09 | TODO-06 (Low) GradScaler API cũ; scheduler step khi optimizer bị skip | ACCEPT_LATER → T15 (hoặc lần train lại kế tiếp); không retrain T09 |
| Claude review T09 | TODO-07 (Info) `T09.md` còn ghi PLANNED | ACCEPT_WITH_NOTES — coordination là nguồn trạng thái |
| Claude Final T10 | F-TODO-01 (governance) coordination/authority chưa phản ánh Gate 2 và PO decision | **RESOLVED_BY_GOVERNANCE_SYNC** tại `857a827`; closure đã được PO authorize riêng |
| Claude Final T10 | F-TODO-02 (vận hành) startup backend thật có thể ghi seed/showtime | **ACCEPT_LATER — PO RUNTIME GATE**; cấm startup nếu chưa có checkpoint/backup và authorization mới |
| Claude Final T10 | F-TODO-03 Task Record còn `IN_PROGRESS` | **RESOLVED_BY_GOVERNANCE_SYNC** tại `857a827`; Task Record được đóng theo Closure Sync của PO |
| Claude Final T10 | F-TODO-04 tài liệu PO-owned còn mô tả default model A | **ACCEPT_LATER — PO-OWNED DOCS**; runtime T10 đã duyệt là `phobert_b` |
| Claude Final T10 | F-TODO-05 canonical package có `__pycache__/02_fresh_backup.cpython-313.pyc` ngoài hash-set | **ACCEPT_LATER — ARTIFACT PRESERVATION**; giữ nguyên, không cleanup; lần sau dùng `python -B` |
| Claude Final T10 | F-TODO-06 health có thể trả nguyên văn `classifier_error`/đường dẫn | **ACCEPT_LATER — PROPOSED T11 BACKLOG**; T11 chưa authorize |
| Claude Final T10 | F-TODO-07 các TODO Round 2 và G2-R4-01…04 | **ACCEPT_LATER — HISTORICAL DISPOSITIONS PRESERVED**; không tự mở lại |

## 11. Current Next Step
1. PO quyết định có cấp runtime gate riêng cho AC-06 hay không; nếu cấp phải nêu checkpoint/backup và phạm vi chạy database/model thật.
2. Khi được cấp, Codex chạy checklist browser thực với model thật, ghi evidence và chỉ chuyển `IN_PROGRESS → CLAUDE_REVIEW` nếu AC-06 PASS.
3. Nếu chưa được cấp, T11 giữ `IN_PROGRESS / BLOCKED_PENDING_PO_RUNTIME_GATE`; không tự nhận PASS.
4. Không mở T12, không tự PASS, PO_APPROVE, merge hoặc đóng T11.

## 12. Active Timeline
| Ngày | Ai | Sự kiện |
|---|---|---|
| 03/10/2026 | Tín + Claude | Dựng bộ tài liệu workflow (docs/README, SOURCE_OF_TRUTH, ARCHITECTURE, REQUIREMENTS, AGENT_RULES, file điều phối, mẫu task, reports/) |
| 03/10/2026 | Claude | Soạn bản nháp Task Record T00–T15 (PLANNED, chờ PO duyệt) |
| 04/10/2026 | Tín | Chốt quy ước: gửi Txx.md cho ChatGPT = PO duyệt. Commit bộ tài liệu (a9d6155) |
| 04/10/2026 | Tín | T00 → READY_FOR_HANDOFF, tạo nhánh task/T00-gom-ma-o-d |
| 04/10/2026 | Codex | T00: READY_FOR_HANDOFF → IN_PROGRESS; bắt đầu kiểm kê mã, dữ liệu và bản sao model trên ổ D |
| 04/10/2026 | Codex | Hoàn tất phần local của T00; chuyển API cũ vào `06_backup`, đưa bản gốc model về đúng `D:\KhoaLuan_PhimVe\thesis_results`; chờ Tín cung cấp evidence Drive/Colab và tự xóa hai bản sao model dư |
| 04/10/2026 | Tín + Claude | **PO đổi phạm vi: mọi hoạt động về ổ C.** Claude chép dữ liệu ổ D vào `data\uit-visfd\`, `ml\artifacts\`, `backup\02_api_cu\` (SHA256 18/18 khớp, ngoài Git); cập nhật T00/T01/T03/T09/T13, SOURCE_OF_TRUTH, ARCHITECTURE, BOI_CANH, AGENT_RULES, CLAUDE.md, `.gitignore`. Ổ D ngừng sử dụng |
| 04/10/2026 | Tín | Upload ba split CSV, error analysis và bản sao notebook phần A lên Drive; runtime Colab mới đọc đúng 7.786/1.112/2.224 dòng và phân bố nhãn |
| 04/10/2026 | Codex | Kiểm hai model ổ C: 201/201 tensor khác, 1/10 câu đổi nhãn; final gates kỹ thuật đạt, scope gate `master...HEAD` vướng commit PO ngoài allowlist nên giữ T00 `IN_PROGRESS` |
| 04/10/2026 | Tín | Fast-forward `master` tới commit PO `a3ed4cb`, tách thay đổi phạm vi khỏi diff implementation T00 |
| 04/10/2026 | Codex | Chạy lại scope gate: chỉ 16 file allowlist; cập nhật report, T00 `IN_PROGRESS` → `CLAUDE_REVIEW` |
| 04/10/2026 | Claude | Review T00: **FAIL** (3 RF tài liệu, gate kỹ thuật đạt). T00 `CLAUDE_REVIEW` → `FIX_LOOP`. Không mở T01 |
| 04/10/2026 | Tín | Gửi ảnh output Colab có đường dẫn, shape, phân bố nhãn từng split, error analysis, notebook và `T00_DRIVE_CHECK_OK` |
| 04/10/2026 | Codex | Sửa RF-01 → RF-03, ghi output Colab nguyên văn vào fix report; T00 `FIX_LOOP` → `CLAUDE_REVIEW` |
| 04/10/2026 | Claude | Review T00 vòng 2: **PASS_WITH_TODO** (RF-01 → RF-03 đã sửa, gate đạt). T00 `CLAUDE_REVIEW` → `PO_REVIEW`; T01 → `READY_FOR_HANDOFF` |
| 04/10/2026 | Tín | PO review T00: **APPROVED**, Required Fixes 0; TODO-01/02 → T02, TODO-03 → T13, TODO-04 WONT_FIX; chờ Tín merge vào `master` |
| 05/10/2026 | Codex | T01: train NB/LR/LinearSVC trên đúng split T00; 2 lượt chạy có max metric diff 0; pipeline load/predict đạt; T01 `IN_PROGRESS` → `CLAUDE_REVIEW` |
| 05/10/2026 | Claude | Review T01: **PASS_WITH_TODO** (RF 0, tái lập max diff 0,0, AC-01 → AC-06 đạt). T01 `CLAUDE_REVIEW` → `PO_REVIEW`; T02 → `READY_FOR_HANDOFF` (chờ merge T01) |
| 05/10/2026 | Tín | PO review T01: **APPROVED**; merge T01 vào `master`; T01 `DONE/CLOSED`; T02 `READY_FOR_HANDOFF` |
| 05/10/2026 | Codex | Xác minh đúng nhánh T02, nhánh chứa master đã merge T01; PO xác nhận artifact Drive và ba `.joblib` local tồn tại; T02 `READY_FOR_HANDOFF` → `IN_PROGRESS` |
| 05/10/2026 | Codex | Hoàn tất so sánh 4 model × 2 input, benchmark CPU, confusion matrix, error analysis và 3 lượt tái lập metric (max diff 0); T02 `IN_PROGRESS` → `CLAUDE_REVIEW` |
| 05/10/2026 | Claude | Review T02: **FAIL** (RF-01 error analysis, RF-02 hai checkpoint; metric/PNG/error_analysis tái lập từng byte, preprocessing max Δ 0,003217, baseline parity 0). T02 `CLAUDE_REVIEW` → `FIX_LOOP`. Không mở task kế tiếp |
| 07/10/2026 | Codex | Fix round 1: rà thủ công 80 dòng lỗi, đo hai checkpoint trên hai input, bổ sung notebook/assert/runtime/model card; gate đạt, T02 `FIX_LOOP` → `CLAUDE_REVIEW` |
| 07/10/2026 | Claude | Review T02 vòng 2: **PASS_WITH_TODO** (RF-01, RF-02 CLOSED; notebook full run đạt marker, metric/PNG tái lập, AC-01 → AC-06 đạt). T02 `CLAUDE_REVIEW` → `PO_REVIEW`. Không mở task kế tiếp |
| 07/10/2026 | Tín | PO review T02: **APPROVED** (AC 6/6, RF 0, blocker 0, DoD MET). TODO-R2-01 RESOLVED, TODO-R2-02 → T13, TODO-R2-03 WONT_FIX, metric lịch sử DOCUMENTED |
| 07/10/2026 | Tín | Merge T02 vào `master` tại `6d5fda5`, tag `ml-baselines`; T02 DONE/CLOSED |
| 07/10/2026 | Tín | PO chốt Q1 (`reports/2026-10-07/claude_q1_decision_T03_2026-10-07.md`): nguồn review_site + social ≥ 80 %, self_written ≤ 20 %; Annotator A = Tín, B = "Người 1" ẩn danh. Gửi T03.md → T03 được authorize, `READY_FOR_HANDOFF` trên branch `task/T03-du-lieu-phim` |
| 07/10/2026 | Codex | Xác minh branch/baseline và bắt đầu implementation T03; chuyển `READY_FOR_HANDOFF` → `IN_PROGRESS` |
| 07/10/2026 | Codex | Hoàn tất guideline, script, README và kiểm tra kỹ thuật trên dữ liệu hiện có; dataset chỉ có header nên T03 giữ `IN_PROGRESS`, trạng thái `WAITING_FOR_DATA` và sau đó cần nhãn B thật |
| 08/10/2026 | Tín + Người 1 | Hoàn tất 496 câu thật và 100 nhãn B; split 347/149, duplicate/PII/cross-split = 0, kappa 0,602510 |
| 08/10/2026 | Tín | Chọn phương án A: chấp nhận label 1 = 67,94%, không thêm/bớt câu và không sửa nhãn; độ lệch tỷ lệ chỉ là warning |
| 08/10/2026 | Codex | Cập nhật gate tỷ lệ theo quyết định PO, chạy lại bằng Python hệ thống; cùng ID train/test, kappa không đổi, trạng thái script `READY_FOR_AC_REVIEW`; T03 `IN_PROGRESS` → `CLAUDE_REVIEW` |
| 08/10/2026 | Claude | Review T03 độc lập: gate tái lập (hash ID train/test không đổi), kappa tính lại 0,602510, PII 0, split/cross-dup đạt; **PASS_WITH_TODO** (AC 6/6, RF 0, blocker 0, 8 TODO; có ghi giới hạn độc lập do Claude hỗ trợ thu dữ liệu). T03 `CLAUDE_REVIEW` → `PO_REVIEW`. T04 giữ PLANNED theo ghi chú PO |
| 08/10/2026 | Codex | Xử lý TODO trước PO approval: xóa `data/phim/movie_comments_v1.md`, giữ CSV ngoài Git, ghi disposition TODO-02–08 và tách commit implementation / review / quyết định PO; T03 giữ `PO_REVIEW`, T04 giữ `PLANNED` |
| 08/10/2026 | Tín | PO APPROVED T03; Drive Backup VERIFIED; merge T03 vào `master` tại `6bd1a3f`; T03 DONE / CLOSED; authorize T04 READY_FOR_HANDOFF |
| 08/10/2026 | Codex | Xác minh gate, bỏ qua cục bộ `data/phim/NGUON_THU.md` theo quyết định PO, tạo `task/T04-quan-ly-phim` từ `master` tại `b6cc3d6`; T04 READY_FOR_HANDOFF → IN_PROGRESS |
| 08/10/2026 | Codex | Hoàn tất CRUD phim admin, validation/taxonomy, mock persistence và UI responsive; compile/build, API/browser probes, AC 7/7 self-check đạt; commit implementation `d8e67e0`; T04 IN_PROGRESS → CLAUDE_REVIEW |
| 08/10/2026 | Claude | Review T04 độc lập: probe TestClient trên DB tạm (401/403 4/4, 422 5/5 + 8 ca thêm, 409 đúng câu, PUT `ended`, 21/21 phim seed lưu lại được), backend thật health `phobert`, UI real + mock (CRUD, F5, lọc/tìm không dấu, loading/rỗng/lỗi, 375px), hồi quy 7/7; **PASS_WITH_TODO** (AC 7/7, RF 0, blocker 0; SD-01/SD-02 chờ PO). T04 `CLAUDE_REVIEW` → `PO_REVIEW`. T05 giữ PLANNED theo yêu cầu PO |
| 08/10/2026 | Tín | PO review T04: **APPROVED**; AC 7/7, RF 0, technical blocker 0; SD-01 và SD-02 APPROVED RETROACTIVELY; DoD accepted với hai ngoại lệ scope; TODO-01→08 đã disposition tại `reports/2026-10-08/po_review_T04_APPROVED_2026-10-08.md`; chờ PO merge, T05 giữ PLANNED |
| 08/10/2026 | Tín | Merge T04 vào `master` tại `fced3d7`; xác minh `T04_MERGE_VERIFIED`, branch T04 nằm trong lịch sử master |
| 08/10/2026 | Codex | Final closure sync: T04 → DONE / CLOSED; Overall Status → READY_FOR_NEXT_TASK; Current Active Task → NONE; Next Task → NOT SELECTED; T05 giữ PLANNED |
| 08/10/2026 | Tín | Authorize T05; xác minh branch `task/T05-quan-ly-suat-chieu`, baseline `a09fe673`, dependency T04 merge `fced3d7` và working tree sạch |
| 08/10/2026 | Codex | T05 `READY_FOR_HANDOFF` → `IN_PROGRESS`; triển khai CRUD suất chiếu, luật chồng giờ +15 phút dùng chung với seed, real/mock API và UI responsive |
| 08/10/2026 | Codex | Hoàn tất focused/full gates, real/mock/browser probes và report; implementation commits `214fcaa`, `033e420` (giữ diff `seed.py` chỉ trong `_ensure_showtimes`); ghi scope conflict booking phim `ended`; T05 `IN_PROGRESS` → `CLAUDE_REVIEW` |
| 08/10/2026 | Claude | Review T05 độc lập: AC-01→AC-07 đạt (401/403 4/4, biên ±114/±115, 409 đúng câu, khóa vé đếm đúng, restart uvicorn thật 0 chồng giờ, mock contract + F5); **FAIL** do RF-01: seed backend + mock bỏ trống 5/9 phim đang chiếu, hot_week 9 → 4 phim (AC-08). Scope conflict booking phim ended xác minh còn tồn tại, chờ PO. T05 `CLAUDE_REVIEW` → `FIX_LOOP`; không mở task kế tiếp |
| 08/10/2026 | Codex | Fix Round 1: sửa phân bổ seed real/mock theo hai pass, đủ 9 phim mỗi ngày, hot_week đủ 9, 0 chồng; ba lifespan + hai Uvicorn restart giữ nguyên suất admin/booking; repair mock data cũ idempotent; fix commit `f5fca8d`; T05 `FIX_LOOP` → `CLAUDE_REVIEW` Round 2 |
| 08/10/2026 | Claude | Review T05 Round 2 độc lập: RF-01 CLOSED (DB sạch 99 suất, 9/9 phim mỗi ngày, 0 chồng, hot_week 9; uvicorn restart ×3 giữ nguyên suất admin/booking; DB cũ RF-01 được lấp, dòng cũ nguyên vẹn; real/mock cùng SHA-256 99 suất; repair localStorage idempotent); AC 8/8, hồi quy 7/7; **PASS_WITH_TODO** (TODO-05 Medium mới: suất seed bị xóa quay lại khi restart). T05 `CLAUDE_REVIEW` → `PO_REVIEW`; scope conflict ended vẫn chờ PO; không mở task kế tiếp |
| 08/10/2026 | Tín | PO review T05: **APPROVED**; Claude PASS_WITH_TODO, AC 8/8 PASS, DoD MET, RF-01 CLOSED, Open Required Fixes 0. TODO-01→T11, TODO-02 ACCEPT, TODO-03→T11, TODO-04 RESOLVED, TODO-05→T11 ưu tiên trước demo, TODO-06 ACCEPT_WITH_NOTES→T12. Scope conflict booking phim `ended`: chọn phương án B, ACCEPT_LATER→T11, chưa sửa trong T05. T05 → `PO_APPROVED / PENDING_MERGE`; Next Task NOT SELECTED; T06 PLANNED với Q2 OPEN; không authorize T07 |
| 08/10/2026 | Tín | Merge T05 vào `master` tại `54a3715`; merge commit có hai parent `a09fe673` và `b0a50de`; toàn bộ lịch sử branch `task/T05-quan-ly-suat-chieu` nằm trong `master` (`T05_MERGE_VERIFIED`) |
| 08/10/2026 | Codex | Final closure sync: T05 → DONE / CLOSED; Overall Status → READY_FOR_NEXT_TASK; Current Active Task → NONE; Next Task → NOT SELECTED. T06 giữ PLANNED với Q2 OPEN; T07 giữ PLANNED / NOT AUTHORIZED; không mở task tiếp theo |
| 08/10/2026 | Tín | PO authorize T06: `READY_FOR_HANDOFF`; Q2 RESOLVED theo phương án **NO ALEMBIC / BACKUP_BEFORE_RESET**; cho phép đổi schema comments, yêu cầu backup đã xác minh trước khi PO tự reset database thật; T07 giữ PLANNED / NOT AUTHORIZED |
| 08/10/2026 | Codex | Pre-flight PASS: working tree sạch, `54a3715` là ancestor của `master`, baseline mới nhất local `0b244b0`; tạo `task/T06-kiem-duyet` không ghi đè branch; T06 `READY_FOR_HANDOFF` → `IN_PROGRESS` |
| 08/10/2026 | Codex | T06 implementation commit `942d719`: schema/real+mock API/UI/tài liệu trong allowlist; backup DB thật VERIFIED; compile/build, DB tạm, real/mock API, permission, stats, CSV và responsive browser probe đạt. DB thật chưa reset theo đúng authorization nên T06 giữ `IN_PROGRESS / PENDING_PO_DATABASE_RESET`, chưa chuyển `CLAUDE_REVIEW` |
| 09/10/2026 | Tín | PO hoàn tất reset database thật theo Q2 NO ALEMBIC / BACKUP_BEFORE_RESET và yêu cầu Codex final verification thực tế |
| 09/10/2026 | Codex | Final verification PASS: backup checksum/integrity giữ nguyên; DB thật mới đủ schema + seed; AC 8/8 DEV PASS; regression browser/API real và mock 7/7; compile/build/health/security/scope đạt; blocker 0, implementation DoD 4/4. T06 `IN_PROGRESS` → `CLAUDE_REVIEW`; full task DoD chờ Claude/PO; T07 giữ PLANNED / NOT AUTHORIZED |
| 09/10/2026 | Claude | Review T06 độc lập (DB tạm + bản copy DB thật, không ghi DB thật/backup; checksum giữ nguyên): AC 8/8 PASS (AC-01 model fields không đổi, relabel/hide/unhide đúng, stats TP/FP/TN/FN 1/1/1/1 acc 0.5, CSV BOM + normalize parity, 401/403 8/8, page_size 500 → 422), mock contract 16/16 key + normalize 20/20, hồi quy 7/7, responsive 375px; **FAIL** do RF-01 (Medium): `action` list/dict → 500. T06 `CLAUDE_REVIEW` → `FIX_LOOP`; 6 TODO không chặn; T07 giữ PLANNED / NOT AUTHORIZED |
| 09/10/2026 | Codex | Fix Loop Round 1: sửa duy nhất production file `backend/app/schemas.py` tại `8ef57ad`; list/dict/số/bool/null/chuỗi lạ đều 422 đúng câu và không đổi dữ liệu, action hợp lệ/security/compile/build/hồi quy real+mock đạt trên DB tạm; RF-01 DEV FIXED, Open RF 0 pending Claude; T06 `FIX_LOOP` → `CLAUDE_REVIEW` Round 2 PENDING; T07 giữ PLANNED / NOT AUTHORIZED |
| 09/10/2026 | Claude | Review T06 Round 2 độc lập (DB tạm + DB copy; DB thật/backup không đổi checksum): RF-01 **CLOSED / VERIFIED** (10/10 action sai → 422 đúng câu, dữ liệu không đổi; 4 action hợp lệ và contract 16/9 key giữ nguyên); AC 8/8, full probe 52/52, mock đạt, hồi quy 7/7, compile/build/diff-check/scope/secret đạt; **PASS_WITH_TODO** (6 TODO cũ chờ PO, không có TODO mới). T06 `CLAUDE_REVIEW` → `PO_REVIEW`; T07 giữ PLANNED / NOT AUTHORIZED theo chỉ định PO |
| 09/10/2026 | Tín | PO review T06: **APPROVED**; Claude Round 2 PASS_WITH_TODO, AC 8/8 PASS, hồi quy 7/7 PASS, RF-01 CLOSED / VERIFIED BY CLAUDE, RF mở 0, blocker 0, DoD MET theo quyết định PO. TODO-01→T11, TODO-02→T11, TODO-03→T11 / RISK ACKNOWLEDGED, TODO-04→T12, TODO-05→T12 có backup/không tự xóa DB, TODO-06 ACCEPT_WITH_NOTES. T06 `PO_REVIEW` → `PO_APPROVED / PENDING_MERGE`; T07 giữ PLANNED / NOT AUTHORIZED |
| 09/10/2026 | Tín | Merge T06 vào `master` tại `81330c2`; merge commit có hai parent `0b244b0` và `bf12674`; toàn bộ lịch sử `task/T06-kiem-duyet` và PO report đã nằm trong `master` (`T06_MERGE_VERIFIED`) |
| 09/10/2026 | Codex | Final closure sync: T06 → DONE / CLOSED; Overall Status → READY_FOR_NEXT_TASK; Current Active Task → NONE; Next Task → NOT SELECTED / NOT AUTHORIZED. TODO deferred giữ ở T11/T12, không ghi RESOLVED; T07 giữ PLANNED / NOT AUTHORIZED |
| 09/10/2026 | Codex | PO authorize T07 `APPROVED / READY_FOR_HANDOFF`; pre-flight PASS: đúng branch, tree sạch, `master` chứa `81330c2`, T01 CLOSED, đủ `svm_A.joblib`/LR/NB, xác định môi trường artifact scikit-learn 1.7.2 + joblib 1.5.2 và hai checkpoint PhoBERT; T07 → `IN_PROGRESS`, T06 giữ DONE/CLOSED. |
| 09/10/2026 | Codex | T07 implementation `e84820d`: registry PhoBERT/SVM/LR/NB + fallback, admin predict/health, trang so sánh real/mock và tài liệu; AC 8/8 DEV PASS, hồi quy 7/7, full gates/security/scope/secret PASS; RF 0, blocker 0, TODO chặn 0; T07 `IN_PROGRESS` → `CLAUDE_REVIEW`. |
| 09/10/2026 | Claude | Review T07 độc lập (uvicorn thật trên DB tạm, bản chép joblib đổi tên; DB thật/artifact giữ nguyên checksum): AC-01/02/03/04/06/07/08 PASS — parity T02 10 câu lệch ≤ 4,9e-5 và 2.224 câu test khớp tuyệt đối F1 T02, fallback/`ACTIVE_MODEL=svm` đúng, real/mock 375px, hồi quy 7/7, scope/secret/gate đạt; **FAIL** do RF-01 (Medium, AC-05: `text` rỗng → 422 tiếng Anh). T07 `CLAUDE_REVIEW` → `FIX_LOOP`; 6 TODO không chặn; không mở T08 |
| 09/10/2026 | Codex | Fix Loop Round 1: sửa duy nhất production file `backend/app/schemas.py` tại `06fbd3d`; `""`/khoảng trắng/newline-tab đều 422 câu tiếng Việt, biên 1.000/1.001, 401/403/admin contract/health đạt; compile/build/startup/scope/secret PASS trên DB tạm. RF-01 DEV FIXED, Open RF 0 pending Claude; T07 `FIX_LOOP` → `CLAUDE_REVIEW` Round 2 pending; không xử lý 6 TODO, không mở T08. |
| 09/10/2026 | Claude | Review T07 Round 2 độc lập (uvicorn thật + DB tạm; DB thật/artifact giữ nguyên checksum): RF-01 **CLOSED / VERIFIED** (`""`, khoảng trắng, newline/tab → 422 tiếng Việt; 1.000/1.001; 401/403; contract 5 key; health 4 model; 12/12); compile/build (bundle hash không đổi)/diff-check/scope/secret đạt; AC 8/8, DoD MET; **PASS_WITH_TODO** (6 TODO Round 1 giữ nguyên chờ PO). T07 `CLAUDE_REVIEW` → `PO_REVIEW`; T08 giữ PLANNED / NOT AUTHORIZED |
| 09/10/2026 | Tín | PO review T07: **APPROVED**; chấp nhận Claude Round 2 PASS_WITH_TODO, AC 8/8, DoD MET, RF-01 CLOSED, RF mở 0, blocker 0. TODO-01→T08/T09/T10 và giữ checkpoint backend; TODO-02/03/04→T11; TODO-05→T10; TODO-06 ACCEPT_WITH_NOTES. T07 → `PO_APPROVED / PENDING_MERGE`; T08 giữ PLANNED / NOT AUTHORIZED. |
| 09/10/2026 | Tín | Merge T07 vào `master` tại `434a489`; merge commit có hai parent `6d1d4bb` và `245fab8`; toàn bộ lịch sử `task/T07-da-mo-hinh` và report PO/Claude đã nằm trong `master`; tag `admin-v1` trỏ đúng `434a489` (`T07_MERGE_VERIFIED`). |
| 09/10/2026 | Codex | Final Closure Sync: T07 → DONE / CLOSED; Overall Status → READY_FOR_NEXT_TASK; Current Active Task → NONE; Next Task → NOT SELECTED / NOT AUTHORIZED. TODO deferred giữ disposition và chưa RESOLVED; T08 giữ PLANNED / NOT AUTHORIZED, không tạo branch hoặc bắt đầu implementation. |
| 09/10/2026 | Codex | PO authorize T08 `APPROVED / READY_FOR_HANDOFF`; pre-flight PASS: đúng nhánh `task/T08-lech-mien`, tree sạch, baseline `5cf4eb0` chứa merge T07 `434a489`, T02/T03 CLOSED; đủ hai test set, checkpoint research canonical và ba baseline A; T08 → `IN_PROGRESS`, T09 giữ `PLANNED / NOT AUTHORIZED`. |
| 09/10/2026 | Codex | Hoàn tất T08: notebook clean-run trên CPU có marker OK; normalize parity 20/20, CSV 4 model × 2 miền, phone parity max `4,92e-07`, 20 lỗi + PNG; delta F1 phim `0,062793–0,080440`, không có delta < 0,03; AC 5/5 DEV PASS, scope/secret/large-file PASS; T08 `IN_PROGRESS` → `CLAUDE_REVIEW`, T09 giữ `PLANNED / NOT AUTHORIZED`. |
| 09/10/2026 | Claude | Review độc lập T08: **PASS_WITH_TODO**; AC 5/5; RF 0; blocker 0; TODO 5 chờ PO. Tái lập CPU 4/4 model lệch ≤ `4,92e-07`, 3 artifact byte-identical, hash/normalize/scope/secret/large-file PASS. T08 `CLAUDE_REVIEW` → `PO_REVIEW`; T09 giữ `PLANNED / NOT AUTHORIZED`. |
| 09/10/2026 | Tín | PO review T08: **APPROVED**; Claude PASS_WITH_TODO, AC 5/5 PASS, DoD MET theo quyết định PO, Open Required Fixes 0, blocker 0, CPU reproducibility 4/4 và artifact reproducibility 3/3. TODO 5/5 dispositioned: TODO-01→T09/khóa luận, TODO-02 ACCEPT_WITH_DISCLOSURE, TODO-03→T09/T13, TODO-04 ACCEPT_WITH_NOTES→T13, TODO-05→T09/T10; TODO deferred chưa RESOLVED. T08 → `PO_APPROVED / PENDING_MERGE`; T09 giữ `PLANNED / NOT AUTHORIZED`. |
| 09/10/2026 | Tín | Merge T08 vào `master` tại `778675e`; merge commit có hai parent `5cf4eb0` và tip T08 `886cba8`; toàn bộ implementation `47e044e`, Claude review `621b75c`, PO report và artifact T08 nằm trong `master` (`T08_MERGE_VERIFIED`). |
| 09/10/2026 | Codex | Final Closure Sync: T08 → DONE / CLOSED; Overall Status → READY_FOR_NEXT_TASK; Current Active Task → NONE; Next Task → NOT SELECTED / NOT AUTHORIZED. TODO 5/5 đã disposition, deferred chưa RESOLVED; T09 giữ PLANNED / NOT AUTHORIZED. |
| 09/10/2026 | Tín + Codex | PO authorize T09 `APPROVED / READY_FOR_HANDOFF`; pre-flight PASS: đúng branch `task/T09-phobert-B`, tree sạch, baseline `6c4b8de` trùng `master` và chứa merge T08 `778675e`; đủ dữ liệu movie/phone, checkpoint research PhoBERT A và baseline T08/T01. T09 `READY_FOR_HANDOFF → IN_PROGRESS`. |
| 09/10/2026 | Tín + Codex | Tín hoàn tất hai clean-run Colab T4 từ runtime mới; Codex xác minh run1/run2, Drive checkpoint/tokenizer/config/ZIP/SHA-256, CPU reload Transformers 5.18.0 và metric tái lập. PhoBERT B config b đạt movie F1 neg `0.917526` > A `0.857143`, phone drop `0.002783`; AC 6/6 DEV PASS, gate/scope/security PASS, blocker 0, Open RF 0. T09 `IN_PROGRESS → CLAUDE_REVIEW`; không mở T10. |
| 09/10/2026 | Claude | Review T09 độc lập: **PASS_WITH_TODO** (AC 6/6, RF 0, blocker 0, 7 TODO). Tái lập CPU 14/14 dòng truyền thống/constant Δ 0, A khớp T08, normalize parity 11.618/11.618, split 294/53 overlap 0, code ZIP Colab = `c8a0230`, số liệu PhoBERT nhất quán số nguyên; evidence GPU trên Drive chưa xác minh trực tiếp (TODO-02). T09 `CLAUDE_REVIEW` → `PO_REVIEW`; T10 giữ PLANNED / NOT AUTHORIZED theo chỉ định PO |
| 09/10/2026 | Tín | PO review T09: **APPROVED**; Claude PASS_WITH_TODO, AC 6/6 PASS, DoD MET theo quyết định PO, RF 0, blocker 0. TODO 7/7 dispositioned: TODO-01→T13, TODO-02 PENDING / REQUIRED BEFORE T10, TODO-03→T13/khóa luận, TODO-04→T10/khóa luận, TODO-05 ACCEPT_WITH_NOTES (sửa disposition T08 TODO-03/04), TODO-06→T15, TODO-07 ACCEPT_WITH_NOTES. PO report `d79b97a` |
| 09/10/2026 | Tín | Merge T09 vào `master` tại `27c364e`; merge commit có hai parent `6c4b8de` và tip T09 `273cc2d`; `task/T09-phobert-B` là ancestor của `master` (`T09_MERGE_VERIFIED`) |
| 09/10/2026 | Claude (thay Codex, PO ủy quyền) | Final Closure Sync: T09 → DONE / CLOSED; Overall Status → READY_FOR_NEXT_TASK; Current Active Task → NONE; Next Task → NOT SELECTED / NOT AUTHORIZED. TODO-02 PENDING / REQUIRED BEFORE T10; TODO deferred giữ disposition, chưa RESOLVED; T10 giữ PLANNED / NOT AUTHORIZED, không tạo nhánh, không gắn tag |
| 10/10/2026 | Tín + Codex | T10 pre-flight: PO xác nhận SHA-256 artifact PhoBERT B 4/4 PASS và run1/run2 có `SELECTION_LOCKED=True` trước `FINAL_TEST_COMPLETE=True` (`PO_ATTESTED`, không phải Claude kiểm tra độc lập); Codex tái lập CPU Windows PASS bằng Transformers 5.18.0, movie F1_neg `0.917525773196`, Macro-F1 `0.881839809675`, probe negative score `0.998829185963`. T09 TODO-02 → RESOLVED theo xác nhận PO. Q3 còn MỞ nên T10 giữ PLANNED / NOT AUTHORIZED; không tạo nhánh, không implementation, không gắn tag. |
| 10/10/2026 | Tín (PO) | Q3 RESOLVED: chọn PhoBERT B mặc định, PhoBERT A fallback hoặc chọn qua `.env` và restart; không bổ sung giao diện admin chọn model. PO AUTHORIZED T10 READY_FOR_HANDOFF. Chờ commit tài liệu authority và tạo branch T10 sạch; implementation chưa bắt đầu. |
| 10/10/2026 | Codex | T10 pre-flight PASS tại baseline `38f63ee`: đúng nhánh `task/T10-gan-model-B`, working tree sạch, T07 `434a489` và T09 `27c364e` là ancestor; Q2/Q3 và T09 TODO-02 RESOLVED. T10 `READY_FOR_HANDOFF → IN_PROGRESS`. |
| 10/10/2026 | Codex | T10 dừng trước production implementation do AC-01 thiếu evidence: notebook T09 trong Git không có output và không lưu bộ 10 câu/expected score; manifest, model card và report cũng không có bảng này. Chỉ probe "Phim dài lê thê, xem mà mệt" có score `0.998829185963` ở mức PO xác nhận. T10 `IN_PROGRESS / BLOCKED_PENDING_PO_EVIDENCE`; không tự lấy inference hiện tại làm ground truth. |
| 10/10/2026 | Tín (PO) | `PO-DECISION-T10-AC01-20261010` APPROVED phương án B: gỡ blocker bằng baseline reference tạo tại T10 qua inference trực tiếp checkpoint B, độc lập với backend classifier wrapper; parity giữ ngưỡng ≤ `0,001` và phải tái kiểm movie test 149 câu so với T09. Không mở lại T09, không đổi checkpoint/model selection, AC-02 đến AC-07 giữ nguyên. T10 tiếp tục `IN_PROGRESS`, AC 0/7 PASS. |
| 10/10/2026 | Codex | Hoàn tất T10 implementation `0e80015`: baseline T10 direct Transformers hai lượt Δ 0; movie test 149 câu khớp T09; runtime parity 10/10 max Δ `0,000048`; B mặc định, A switch/fallback, version persistence/health/admin, DB tạm, real/mock/browser smoke, regression 7/7, scope/secret/large-file PASS. AC 7/7 DEV PASS, RF 0, blocker 0; T10 `IN_PROGRESS → CLAUDE_REVIEW`, T11 giữ `PLANNED / NOT AUTHORIZED`. |
| 10/10/2026 | Claude | T10 Round 1 independent review: **FAIL**. AC 7/7 PASS (reference Transformers độc lập Δ 0 với baseline, runtime parity 10/10 max Δ `0,000048`, movie test 149 khớp T09, uvicorn thật B/A/missing-B/broken-B, 401/403/200, browser E2E real + mock 7/7, mobile). RF-01 (Medium) race lazy-load/release admin predict → 500 khi gọi đồng thời. DB thật chưa có `model_version` (TODO-01 PO ACTION). T10 `CLAUDE_REVIEW → FIX_LOOP`; T11 giữ `PLANNED / NOT AUTHORIZED`. Probe tạm còn 0. |
| 10/10/2026 | Codex | T10 Fix Round 1: sửa duy nhất RF-01 bằng per-model lifecycle `RLock` trong `backend/app/classifier.py`; B-active 18/18 + stress 50/50, A-active 18/18 + stress 30/30 đều HTTP 200, model phụ release và model active giữ loaded; fallback/error/security/parity/movie metric/comment persistence/build real+mock/hồi quy 7/7 đạt trên DB tạm. RF-01 **DEV FIXED / PENDING CLAUDE VERIFICATION**; T10 `FIX_LOOP → CLAUDE_REVIEW / ROUND_2_PENDING`; TODO-01 DB thật giữ `PO ACTION REQUIRED`; T11 giữ `PLANNED / NOT AUTHORIZED`. |
| 10/10/2026 | Claude | T10 Round 2 independent review: **PASS_WITH_TODO**. RF-01 **CLOSED / VERIFIED BY CLAUDE** (source review per-model `RLock`; uvicorn thật B-active 18/18 + stress 50/50, A-active 18/18 + stress 30/30, trộn comment/predict, 0 lỗi 500/`AttributeError`). AC 7/7 (check_model 10/10 max Δ `0,000048`; reference độc lập Δ 0; movie test khớp T09; fallback missing/broken B, broken A phụ; 401/403/200; browser real/mock cho luồng bị ảnh hưởng + API regression). DB thật vẫn thiếu `model_version` (PENDING_PO_ACTION). T10 `CLAUDE_REVIEW → PO_REVIEW`; T11 giữ `PLANNED / NOT AUTHORIZED`. Probe tạm còn 0. |
| 10/10/2026 | Tín (PO) | `PO-DECISION-T10-REALDB-A1-GATE1-20261010`: **APPROVED Gate 1 A1**, cho phép chuẩn bị manual ALTER duy nhất `comments.model_version VARCHAR(100) NULL` để bảo toàn dữ liệu; preflight clone PASS. **Gate 2 NOT AUTHORIZED**, DB thật không đổi/không READY; TODO-01 giữ PO ACTION REQUIRED; T10 `PO_REVIEW / PENDING_PO_DB_ACTION`, T11 giữ `PLANNED / NOT AUTHORIZED`. |
| 11/10/2026 | Tín + Codex | T10 Gate 2 Attempt 2: controlled ALTER `comments.model_version VARCHAR(100) NULL` **COMMITTED** theo `PO-DECISION-T10-REALDB-A1-GATE2-20261010`; Postverify PASS, 559 dòng gốc bảo toàn; Credential Precheck V2 PASS; Clone Smoke Attempt 1 FAIL/ARCHIVED, Attempt 2 PASS; hash reconciliation PASS; DB hash `B3F7DF79…CFE3` được bảo toàn. |
| 11/10/2026 | Codex + Claude | DEV Final QA PASS; Claude Final Independent Review **PASS_WITH_TODO**; AC 7/7, Technical DoD MET, RF 0, TODO 7; không startup backend thật trong final review. |
| 11/10/2026 | Tín (PO) | PO Review **APPROVED_WITH_NOTES**; T10 `PO_APPROVED / CLOSURE_PENDING`. F-TODO-01/03 FIX_NOW qua governance sync; F-TODO-02/04/05/06/07 ACCEPT_LATER. Amendment V2 mở allowlist thành sáu file, gồm Claude Final Review. Merge/tag/closure/real-backend startup/T11 đều NOT AUTHORIZED. |
| 11/10/2026 | Tín (PO) + Codex | PO xác minh fast-forward merge và tự tạo annotated tag `phobert-B` trỏ `857a8272`; line-ending reconciliation PASS. PO authorize Final Closure Sync: T10 → DONE / CLOSED; Overall Status → READY_FOR_NEXT_TASK; Current Active Task → NONE; Next Task → NOT SELECTED / NOT AUTHORIZED. F-TODO-02/04/05/06/07 giữ ACCEPT_LATER; real backend startup và T11 vẫn NOT AUTHORIZED. |
| 11/10/2026 | Tín (PO) + Codex | PO authorize T11 theo Task Record; cho phép thêm `pytest` và `httpx`, không cho thêm thư viện khác, đổi schema hoặc chạy backend với database thật. Pre-flight PASS trên `task/T11-kiem-thu`: tree sạch, release T10 `857a8272` là ancestor, T04–T10 CLOSED, không có task khác IN_PROGRESS. T11 `PLANNED → READY_FOR_HANDOFF → IN_PROGRESS`; T10 giữ DONE / CLOSED. |
| 11/10/2026 | Codex | T11 DEV: thêm pytest/TestClient + SQLite tạm + fake classifier; 20/20 test PASS cả trong virtualenv thật sự không torch/transformers/model; 13/13 route-method admin có 401/403; compile, health DB tạm, frontend build real/mock, mock probes, scope/security PASS. Sửa 9 lỗi có tái hiện và CHANGELOG; không đổi schema/normalize/DB thật. AC-06 web model thật PENDING do chưa có runtime authorization; T11 giữ `IN_PROGRESS / BLOCKED_PENDING_PO_RUNTIME_GATE`, chưa chuyển CLAUDE_REVIEW. |
