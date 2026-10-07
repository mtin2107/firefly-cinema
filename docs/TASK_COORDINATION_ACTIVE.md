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
Trước khi áp dụng workflow: giao diện React đầy đủ (`giao-dien-v1`), backend FastAPI + SQLite, PhoBERT A gắn vào backend, F1 test 0,918 (`phobert-v1`).

## 4. Current Project Status
```
Overall Status: CLAUDE_REVIEW
Phase: T01 DONE/CLOSED; T02 CLAUDE_REVIEW (fix round 1)
Current Active Task: T02 — chờ Claude review lại RF-01, RF-02
Next Task: NONE — không mở task kế tiếp trước khi T02 qua review
Ngày bắt đầu sản phẩm: 05/10/2026 · Hạn: 01/11/2026
```

## 5. Current Active Task
T02 — So sánh PhoBERT với mô hình truyền thống · CLAUDE_REVIEW

## 6. Current Task Record
[docs/tasks/T02.md](tasks/T02.md)

## 7. Roadmap và trạng thái

| ID | Task | Loại | Tuần | Phụ thuộc | Task Record | Trạng thái |
|---|---|---|---|---|---|---|
| T00 | Gom mã và dữ liệu về project ổ C, model card A | ML | 1 | — | [T00.md](tasks/T00.md) | PO_APPROVED (đã có trên master tại `20daf6a`) |
| T01 | Mô hình truyền thống (NB, LR, SVM) | ML | 1 | T00 | [T01.md](tasks/T01.md) | DONE / CLOSED |
| T02 | So sánh PhoBERT với mô hình truyền thống | ML | 1 | T01 | [T02.md](tasks/T02.md) | CLAUDE_REVIEW |
| T03 | Bộ dữ liệu bình luận phim | Dữ liệu | 1–2 | — | [T03.md](tasks/T03.md) | PLANNED (BLOCKED Q1) |
| T04 | Quản lý phim (admin) | Web | 2 | — | [T04.md](tasks/T04.md) | PLANNED |
| T05 | Quản lý suất chiếu (admin) | Web | 2 | T04 | [T05.md](tasks/T05.md) | PLANNED |
| T06 | Kiểm duyệt có người duyệt (đổi schema) | Web | 2 | — | [T06.md](tasks/T06.md) | PLANNED (cần Q2) |
| T07 | Đa mô hình và trang So sánh mô hình | Web + ML | 2 | T01 | [T07.md](tasks/T07.md) | PLANNED |
| T08 | Đo lệch miền điện thoại → phim | ML | 3 | T02, T03 | [T08.md](tasks/T08.md) | PLANNED |
| T09 | Train PhoBERT phần B | ML | 3 | T08 | [T09.md](tasks/T09.md) | PLANNED |
| T10 | Gắn model B vào web | Web | 3 | T07, T09 | [T10.md](tasks/T10.md) | PLANNED |
| T11 | Kiểm thử tự động và sửa lỗi | Web | 4 | T04–T10 | [T11.md](tasks/T11.md) | PLANNED |
| T12 | Dữ liệu demo và kịch bản bảo vệ | Web | 4 | T10 | [T12.md](tasks/T12.md) | PLANNED |
| T13 | Chốt v1.0 và sao lưu | Tất cả | 4 | T11, T12 | [T13.md](tasks/T13.md) | PLANNED |
| T14 | *(tùy chọn)* Hủy vé, đổi mật khẩu | Web | dư | — | [T14.md](tasks/T14.md) | PLANNED |
| T15 | *(tùy chọn)* Thử nghiệm có tách từ | ML | dư | T09 | [T15.md](tasks/T15.md) | PLANNED |

Chuỗi chính: `T00 → T01 → T02` và `T03 → T08 → T09 → T10`. T03 bắt đầu ngay ngày đầu (song song).
Nếu trễ: cắt T14 → T15 → rút gọn T05. Không cắt T01–T03, T07–T10.

## 8. Open Blockers
- T02: không có blocker implementation. Codex đã đo đủ hai checkpoint: backend F1 neg 0,917808 (`text_norm`) / 0,918046 (`normalize`), gốc 0,921600 / 0,919936. Hai bản khác trọng số; không tự thay model backend, PO chọn disposition sau review. Chênh preprocessing lớn nhất `0,003217 < 0,01`.
- Q1 (nguồn bình luận phim, người gán nhãn 2) chặn T03.
- Q2 (Alembic hay xóa `firefly.db`) cần chốt trước T06.

## 9. Open Required Fixes
0 đang mở phía Codex — RF-01 và RF-02 đã sửa trong `reports/2026-10-07/codex_fix_T02_round1_2026-10-07.md`, chờ Claude xác minh vòng 2:
- RF-01: 80 dòng lỗi đã rà thủ công, category cố định theo index, bảng ghi rõ chỉ là mẫu, tối đa 5 ví dụ/nhóm, trade-off có F1/CPU/MiB.
- RF-02: đã đo cả checkpoint gốc và backend trên hai input, ghi rõ danh tính và số liệu; PO quyết định checkpoint sau review.

RF-01 → RF-03 của T00 đã đóng; T01 không có RF.

## 10. Open TODOs
| Nguồn | TODO | Disposition |
|---|---|---|
| Nợ kỹ thuật | `requirements-ml.txt` còn `underthesea`, chưa ghim phiên bản; `HUONG_DAN.md` 4.2 | Đã sửa và PO duyệt trong T00 |
| Phát hiện 03/10 | `backend/.env.example` ghi `USE_WORD_SEGMENT=true`, thiếu `USE_TEXT_NORM` — lệch BOI_CANH 3.4 | Đã sửa và PO duyệt trong T00 |
| Claude review T00 r2 | TODO-01 hai checkpoint model A | ACCEPT_LATER — T02; đo F1 hai bản trên cùng test bằng `normalize()` hiện tại, PO chọn |
| Claude review T00 r2 | TODO-02 `normalize()` ≠ `text_utils.py` | ACCEPT_LATER — T02; đo ảnh hưởng tiền xử lý trước khi quyết định sửa backend |
| Claude review T00 r2 | TODO-03 `firefly_phobert.zip` trên Drive chưa xác minh | ACCEPT_LATER — T13; xác minh file, checksum, khả năng khôi phục |
| Claude review T00 r2 | TODO-04 thụt lề `HUONG_DAN.md` 4.2 | WONT_FIX — Markdown hiển thị đúng, không ảnh hưởng nghiệm thu |
| Nợ kỹ thuật | `_SAMPLE_SALES` lặp ở `seed.py` và `mock.js` | T12 (tùy chọn) |
| Nợ kỹ thuật | `/api/admin/comments` chưa phân trang | Đưa vào T06 |
| Nợ kỹ thuật | `comments.model_name` chưa có phiên bản | Đưa vào T10 |
| Phát hiện 04/10 | `chay-firefly.bat` không có trong repo dù tài liệu ghi "Xong" | Chờ PO: commit file từ máy Tín hoặc đưa vào T00 |
| Phát hiện 04/10 | Thư mục rỗng `Bao_cao\` ở gốc | Đã xử lý 04/10: giữ làm nơi để bản Word (`*.docx` ngoài Git) |
| T11 | Cần thêm `httpx` (TestClient) cùng `pytest` | Chờ PO cho phép |
| Claude review T01 | TODO-01 ba `.joblib` chưa có trên `MyDrive/thesis_results/baselines/` | ACCEPT_WITH_ACTION — Tín upload trước khi bắt đầu implementation T02 |
| Claude review T01 | TODO-02 `baselines.py` viết lại, bỏ baseline Task B/C + ablation `text_raw`, report Codex không ghi | ACCEPT — PO chấp nhận, không yêu cầu sửa T01 |
| Claude review T01 | TODO-03 `EXPECTED_SPLITS` cố định cho UIT-ViSFD | ACCEPT_LATER → T09 |
| Claude review T01 | TODO-04 `ms_per_sentence` dùng `process_time` (độ phân giải Windows thô, dao động ~2×) | ACCEPT_LATER → T02; đo CPU 4 mô hình cùng phương pháp bằng `time.perf_counter` — Claude review T02: đã xử lý, đề xuất đóng |
| Claude review T02 | TODO-01 latency phụ thuộc tải máy; cách dựng môi trường torch + sklearn | Đã xử lý round 1: report ghi interpreter, `PYTHONPATH`, phiên bản và lưu ý ưu tiên thứ tự/tỉ lệ |
| Claude review T02 | TODO-02 không checkpoint nào tái lập `phobert_A.json` (macro 0,9128 / acc 0,9141) | ACCEPT_LATER → PO; model card đã phân biệt historical/remeasured metric |
| Claude review T02 | TODO-03 notebook thiếu assert AC-03 và marker | Đã xử lý round 1: có assert parity và `NOTEBOOK_EXECUTION_OK` thực |
| Claude review T02 | TODO-04 `size_mb` là MiB nhưng ghi MB | Đã ghi chú: giữ schema, giá trị tính theo MiB (`1024²` byte) |

## 11. Current Next Step
1. **Claude:** review độc lập fix round 1 của RF-01 và RF-02, chạy lại gate khả thi.
2. **Tín:** PO review sau kết luận của Claude; quyết định disposition checkpoint và metric lịch sử.
3. Không merge hoặc mở task phụ thuộc tiếp theo trước khi T02 qua Claude review và PO review.

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
