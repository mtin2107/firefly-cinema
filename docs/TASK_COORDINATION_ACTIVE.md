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
Overall Status: PO_REVIEW
Phase: Tín PO review T00 (Claude round 2: PASS_WITH_TODO)
Current Active Task: T00
Next Task: T01 — READY_FOR_HANDOFF, nhánh task/T01-mo-hinh-truyen-thong (tạo sau khi merge T00)
Ngày bắt đầu sản phẩm: 05/10/2026 · Hạn: 01/11/2026
```

## 5. Current Active Task
T00 — Gom mã và dữ liệu về project ổ C, model card A · PO_REVIEW

## 6. Current Task Record
[docs/tasks/T00.md](tasks/T00.md)

## 7. Roadmap và trạng thái

| ID | Task | Loại | Tuần | Phụ thuộc | Task Record | Trạng thái |
|---|---|---|---|---|---|---|
| T00 | Gom mã và dữ liệu về project ổ C, model card A | ML | 1 | — | [T00.md](tasks/T00.md) | PO_REVIEW |
| T01 | Mô hình truyền thống (NB, LR, SVM) | ML | 1 | T00 | [T01.md](tasks/T01.md) | READY_FOR_HANDOFF |
| T02 | So sánh PhoBERT với mô hình truyền thống | ML | 1 | T01 | [T02.md](tasks/T02.md) | PLANNED |
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
- T00 model A: hai bản trên ổ C khác toàn bộ 201 tensor; 1/10 câu kiểm thử đổi nhãn. Đã ghi trong model card; chờ PO quyết hướng xử lý sau khi đối chiếu checkpoint/test, không tự thay model backend. Không chặn T01 (T01 không dùng checkpoint PhoBERT); cần chốt trước T02.
- Q1 (nguồn bình luận phim, người gán nhãn 2) chặn T03.
- Q2 (Alembic hay xóa `firefly.db`) cần chốt trước T06.

## 9. Open Required Fixes
0 — RF-01 → RF-03 của T00 đã được Claude xác nhận sửa đủ (`reports/2026-10-04/claude_review_T00_round2_PASS_WITH_TODO_2026-10-04.md`).

## 10. Open TODOs
| Nguồn | TODO | Disposition |
|---|---|---|
| Nợ kỹ thuật | `requirements-ml.txt` còn `underthesea`, chưa ghim phiên bản; `HUONG_DAN.md` 4.2 | Đã sửa trong T00 (chờ PO duyệt) |
| Phát hiện 03/10 | `backend/.env.example` ghi `USE_WORD_SEGMENT=true`, thiếu `USE_TEXT_NORM` — lệch BOI_CANH 3.4 | Đã sửa trong T00 (chờ PO duyệt) |
| Claude review T00 r2 | TODO-01 hai checkpoint model A; TODO-02 `normalize()` ≠ `text_utils.py`; TODO-03 `firefly_phobert.zip` chưa xác minh; TODO-04 thụt lề HUONG_DAN 4.2 | Chờ PO disposition (đề xuất: T02 / T02 / T13 / WONT_FIX) |
| Nợ kỹ thuật | `_SAMPLE_SALES` lặp ở `seed.py` và `mock.js` | T12 (tùy chọn) |
| Nợ kỹ thuật | `/api/admin/comments` chưa phân trang | Đưa vào T06 |
| Nợ kỹ thuật | `comments.model_name` chưa có phiên bản | Đưa vào T10 |
| Phát hiện 04/10 | `chay-firefly.bat` không có trong repo dù tài liệu ghi "Xong" | Chờ PO: commit file từ máy Tín hoặc đưa vào T00 |
| Phát hiện 04/10 | Thư mục rỗng `Bao_cao\` ở gốc | Đã xử lý 04/10: giữ làm nơi để bản Word (`*.docx` ngoài Git) |
| T11 | Cần thêm `httpx` (TestClient) cùng `pytest` | Chờ PO cho phép |

## 11. Current Next Step
1. **Tín:** PO review T00, cho disposition TODO-01 → TODO-04 (review round 2 mục 3), quyết hướng xử lý hai checkpoint model A (Claude đề xuất đo F1 test cả hai bản trước T02).
2. **Tín:** `git checkout master` → `git merge task/T00-gom-ma-o-d` → `git checkout -b task/T01-mo-hinh-truyen-thong`.
3. **Tín:** gửi prompt ở mục "Bàn giao task kế tiếp" của review round 2 kèm `T01.md` và file này cho ChatGPT/Codex.

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
