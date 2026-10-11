# PROJECT SOURCE OF TRUTH — Firefly Cinema

> Cổng vào duy nhất cho mọi agent. Đọc file này trước, sau đó đọc `TASK_COORDINATION_ACTIVE.md` và Task Record đang làm.
> Cập nhật: 11/10/2026.

## 1. Project Snapshot

| Mục | Giá trị |
|---|---|
| Sản phẩm | Firefly Cinema — website đặt vé xem phim tích hợp PhoBERT phân loại bình luận tiêu cực |
| Đề tài | Khóa luận #67, Khoa học dữ liệu, NTTU — sinh viên Lê Minh Tín |
| Hạn | Sản phẩm 05/10 – 01/11/2026 · Báo cáo 02/11 – 29/11/2026 |
| Repo | `C:\Projects\firefly-cinema` (thư mục gốc duy nhất, **mọi hoạt động diễn ra ở đây**), nhánh chính `master` |
| File lớn | Trong repo nhưng ngoài Git: `data\` (CSV), `ml\artifacts\` (model gốc, joblib), `backend\models\` (model web dùng), `backup\`, `Bao_cao\*.docx`. Bản sao ngoài máy: Google Drive |
| Ổ D | `D:\KhoaLuan_PhimVe\` **ngừng sử dụng** từ 04/10/2026 (dữ liệu đã chép sang ổ C). Task mới không đọc, không ghi ở đây |
| Mốc đã có | tag `giao-dien-v1`, `phobert-v1` |
| Stack | React 18 + Vite 5 · FastAPI 0.115 + SQLAlchemy 2 + SQLite · PhoBERT (transformers 5.18, torch 2.11 CPU) |

## 2. Vai trò

| Vai trò | Ai | Được làm | Không được làm |
|---|---|---|---|
| **Product Owner / Approver** | **Tín** | Chốt Task Record, chạy code trên máy và Colab, ra quyết định PO (`APPROVED` / `APPROVED_WITH_NOTES` / `CHANGES_REQUESTED` / `REJECTED`), merge, gắn tag | — |
| **Primary Implementer** | **Codex / ChatGPT** | Soạn Task Record (bước PLANNING), viết code + test, chạy gate, viết implementation/fix report, chuyển `IN_PROGRESS → CLAUDE_REVIEW` | Tự review, tự PASS, tự chuyển `PO_REVIEW`, tự đóng task, tự mở task kế tiếp, mở rộng scope |
| **Independent Reviewer / Tester** | **Claude** | Đọc code và test thật, chạy gate độc lập, probe tạm, kết luận `PASS` / `PASS_WITH_TODO` / `FAIL`, viết review report | Sửa production code, tự làm Required Fix, approve, đóng task |

**Quy ước duyệt (Tín chốt 04/10/2026):** Task Record T00–T15 đã có sẵn bản nháp. Khi Tín gửi `Txx.md` cho ChatGPT/Codex để bắt đầu, task đó **được coi là PO đã duyệt và ở trạng thái `READY_FOR_HANDOFF`** theo đúng nội dung file lúc gửi. Muốn đổi gì thì Tín sửa `Txx.md` trước khi gửi.

**Ủy quyền cho Claude (04/10/2026):** khi review PASS / PASS_WITH_TODO, Claude đặt task kế tiếp sang `READY_FOR_HANDOFF` và soạn sẵn prompt bàn giao (`AGENT_RULES.md` mục 1.1). Duyệt PO, merge và tag vẫn do Tín làm.

## 3. Thứ tự ưu tiên nguồn khi mâu thuẫn

1. Code và test thật trong repo (đã kiểm chứng).
2. `docs/TASK_COORDINATION_ACTIVE.md`.
3. Quyết định PO mới nhất (report `po_review_*`).
4. `docs/PROJECT_SOURCE_OF_TRUTH.md` → `docs/ARCHITECTURE.md` → `docs/BOI_CANH_DU_AN.md`.
5. Review Claude mới nhất của task hiện tại.
6. Report Codex mới nhất.
7. Report cũ, archive.

Không âm thầm trộn hai phiên bản mâu thuẫn. Ghi conflict vào mục "Open Blockers" của file điều phối và hỏi Tín.

## 4. Quyết định đã chốt (không tự đổi)

- Thiết kế giao diện ở `BOI_CANH_DU_AN.md` mục 4 (màu, font, hero bảng hiệu, PosterIntro, header).
- Kiến trúc lớp API frontend: chỉ import từ `src/api/index.js`, mọi endpoint có cả `real.js` và `mock.js`.
- Model PhoBERT A: nhãn `0 = binh_thuong`, `1 = tieu_cuc`, đầu vào chuẩn hóa bằng `normalize()`, không tách từ, ngưỡng 0,5.
- Không thêm thư viện ngoài danh sách đã cho phép trong task (scikit-learn, joblib cho T01/T07; pytest cho T11).
- Lệnh hướng dẫn viết cho Windows PowerShell. Giao diện tiếng Việt, code tiếng Anh, trả lời Tín bằng tiếng Việt.

## 5. Câu hỏi còn mở (chỉ Tín quyết định)

| # | Câu hỏi | Ảnh hưởng task | Trạng thái |
|---|---|---|---|
| Q1 | Nguồn thu bình luận phim và người gán nhãn thứ hai | T03 | CHỐT: nguồn review_site + social là chính, self_written ≤20%; Annotator A = Lê Minh Tín, Annotator B = "Người 1" ẩn danh; 07/10/2026 |
| Q2 | Dùng Alembic hay chấp nhận xóa firefly.db khi đổi schema | T06 trở đi | CHỐT: NO ALEMBIC / BACKUP_BEFORE_RESET — RESOLVED 08/10/2026. Phải backup và xác minh checksum/integrity trước khi PO tự thực hiện reset database thật; Codex không được tự xóa/reset `firefly.db`. |
| Q3 | Model mặc định sau T10: PhoBERT B hay admin chọn | T10 | CHỐT: PhoBERT B mặc định (`ACTIVE_MODEL=phobert_b`); PhoBERT A fallback hoặc chọn qua `.env` (`ACTIVE_MODEL=phobert`) và restart backend; không bổ sung giao diện admin chọn model. PO APPROVED 10/10/2026 |
| Q4 | Deploy lên mạng hay chỉ chạy máy khi bảo vệ | T12, T13 | MỞ |

### Ngoại lệ T10 cho Q2 — Gate 1

`PO-DECISION-T10-REALDB-A1-GATE1-20261010` — **GATE 1 APPROVED ngày 10/10/2026**:

- PO lựa chọn phương án kỹ thuật A1 cho riêng schema T10: chuẩn bị manual SQLite ALTER để bổ sung duy nhất `comments.model_version VARCHAR(100) NULL`, không dùng Alembic, không reset database theo A1 và phải bảo toàn toàn bộ dữ liệu cũ.
- Preflight backup/restore/schema/API trên clone đã PASS. Runbook dự thảo nằm tại `HUONG_DAN.md` mục 2.1.
- Đây là ngoại lệ có kiểm soát cho T10, không thay thế quyết định lịch sử **Q2 RESOLVED 08/10/2026 — NO ALEMBIC / BACKUP_BEFORE_RESET** và không tạo chính sách ALTER mặc định cho task khác.
- **GATE 2 NOT AUTHORIZED**: chưa được ALTER, reset, migrate, seed, restore/ghi đè hoặc khởi động backend có khả năng ghi vào database thật. Mọi thao tác ghi cần một quyết định PO riêng; Codex không được tự thực hiện migration.
- Database thật chưa được đánh dấu READY. **Phê duyệt phương án kỹ thuật không đồng nghĩa với phê duyệt thao tác thực thi.**

### T10 Gate 2 và PO approval

`PO-DECISION-T10-REALDB-A1-GATE2-20261010` — **GATE 2 EXECUTED / ALTER COMMITTED**:

- Sau authorization và checkpoint riêng của PO, A1 đã bổ sung duy nhất `comments.model_version VARCHAR(100) NULL` bằng controlled ALTER; không dùng Alembic, không reset database.
- Postverify **PASS**: integrity/FK checks đạt, schema mới nullable đúng yêu cầu và toàn bộ **559 dòng dữ liệu gốc được bảo toàn**.
- Clone Smoke Attempt 1 `FAIL / ARCHIVED`; Credential Precheck V2 **PASS**; Clone Smoke Attempt 2 **PASS**; hash reconciliation **PASS**.
- SHA-256 database thật sau ALTER: `B3F7DF79BDA4478412200EA80B8EC15E6B73DA730068A52E11C40136EAC4CFE3`.
- DEV Final QA **PASS**; Claude Final Independent Review ngày 11/10/2026 **PASS_WITH_TODO**, AC `7/7 PASS`, Technical DoD `MET`, Required Fixes `0`.
- PO ngày 11/10/2026 quyết định **APPROVED_WITH_NOTES**; T10 ở `PO_APPROVED / CLOSURE_PENDING`. Hai TODO governance `F-TODO-01` và `F-TODO-03` được xử lý bằng đợt sync này; năm TODO còn lại giữ `ACCEPT_LATER` theo PO Review.
- PO amendment V2 cho phép lưu Claude Final Review như artifact thứ sáu trong cùng commit authority/coordination sync; báo cáo PO và Claude phải giữ nguyên byte-for-byte.
- PO amendment V3 cho phép ngoại lệ hẹp đối với đúng 12 Markdown hard-break bằng hai dấu cách cuối dòng trong immutable PO Review (dòng 3–7, 19–20, 84–88); năm file còn lại vẫn phải qua whitespace check bình thường. Ngoại lệ không thay đổi hash, nội dung authority hoặc policy whitespace toàn repository.
- Approval này **không** cấp quyền merge, tag, đóng T10, mở T11 hoặc khởi động backend trên database thật. Các bước đó cần authorization riêng của PO.

Khi Tín trả lời, đổi trạng thái thành `CHỐT: <nội dung>, <ngày>`.

## 6. Bản đồ tài liệu

Xem `docs/README.md`.
