# Product Owner Review — Firefly Cinema — T10

**Task:** T10 — Gắn PhoBERT B vào Web  
**Ngày:** 2026-10-11 (Asia/Ho_Chi_Minh)  
**Vai trò quyết định:** Product Owner (PO)  
**Quyết định PO:** **APPROVED_WITH_NOTES**  
**Tên file theo quy ước report PO:** `reports/2026-10-11/po_review_T10_APPROVED_2026-10-11.md`  
**Giai đoạn:** `PO_APPROVED — CLOSURE_PENDING` (chưa `DONE/CLOSED`)

## 1. Căn cứ và phạm vi quyết định

PO trực tiếp quyết định `APPROVED_WITH_NOTES` trong cuộc trao đổi ngày 2026-10-11, dựa trên:

- `reports/2026-10-11/claude_review_T10_PASS_WITH_TODO_2026-10-11.md`: Claude Final Independent Review `PASS_WITH_TODO`, AC `7/7 PASS`, Definition of Done kỹ thuật `MET`, Required Fixes `0`, TODO `7`.
- `backup/T10_2026-10-10/reports/T10_FINAL_QA_EVIDENCE_REPORT.md`: Codex DEV Final QA `PASS`, AC `7/7 PASS`, regression `7/7 PASS`.
- Gate 2 evidence: Postverify `PASS`; Clone Smoke Attempt 2 `PASS`; hash reconciliation `PASS`; bằng chứng ghi Model B, fallback A và API Security `401/403/200` trên clone.
- PO decision `PO-DECISION-T10-REALDB-A1-GATE2-20261010` và các checkpoint live riêng đã được báo cáo là hoàn thành.

**Reviewed implementation HEAD:** `27701d19a150117919e0172f2386d819a7b9d369`  
**Branch:** `task/T10-gan-model-B`  
**Baseline:** `38f63eedf3682216c1256cc581811e5ae9e05406`

Đây là quyết định phê duyệt nghiệm thu kỹ thuật **có ghi chú**; không thay thế việc xác minh commit đồng bộ và merge/closure ở các gate sau.

## 2. Kết quả Product Owner Review

| Tiêu chí | Kết quả chấp thuận |
|---|---|
| Claude Final Independent Review | `PASS_WITH_TODO` |
| Acceptance Criteria | `7/7 PASS` |
| Definition of Done kỹ thuật | `MET` |
| Frontend/backend gates | `PASS` |
| Web regression | `7/7 PASS` (kết hợp bằng chứng lịch sử cùng code và gate mới; không tuyên bố E2E mới toàn bộ) |
| Security | `PASS` |
| Scope integrity | `PASS` |
| Database evidence | `PASS` |
| Required Fixes | `0` |
| Open technical blockers tại thời điểm review | `0` |
| TODO | `7` đã có disposition ở mục 3 |

**Database thật:** `C:\Projects\firefly-cinema\backend\firefly.db`. SHA-256 post-ALTER được xác minh theo báo cáo: `B3F7DF79BDA4478412200EA80B8EC15E6B73DA730068A52E11C40136EAC4CFE3`. Không cấp phép chạy backend trên database thật trong quyết định này.

## 3. Quyết định xử lý toàn bộ TODO

| Mã | Disposition PO | Cách xử lý / giới hạn |
|---|---|---|
| **F-TODO-01** | **FIX_NOW — GOVERNANCE / PRE-CLOSURE** | Đồng bộ `docs/TASK_COORDINATION_ACTIVE.md`; ghi nhận thực thi Gate 2, Postverify, Clone Smoke, hash reconciliation, Final QA, Claude Final Review và PO decision. Ghi quyết định thực thi Gate 2 vào `docs/PROJECT_SOURCE_OF_TRUTH.md` bằng ngoại lệ chỉnh sửa hẹp được PO cho phép cho đợt authority sync này. Chưa chuyển `DONE/CLOSED`. |
| **F-TODO-02** | **ACCEPT_LATER — PO RUNTIME GATE** | Khởi động backend với DB thật có thể kích hoạt `seed()`/`_ensure_showtimes()` và phát sinh ghi dữ liệu. **Không được startup real backend** nếu chưa có checkpoint/backup và quyết định PO mới. Không được xem approval T10 là quyền startup. |
| **F-TODO-03** | **FIX_NOW — GOVERNANCE / PRE-CLOSURE** | Cập nhật duy nhất `Current Status` trong `docs/tasks/T10.md` từ `IN_PROGRESS` thành `PO_APPROVED`; ghi chú closure chưa thực hiện nếu cần. Không sửa yêu cầu/AC/scope. Đây là ngoại lệ hẹp do PO trực tiếp yêu cầu. |
| **F-TODO-04** | **ACCEPT_LATER — PO-OWNED DOCS** | Tài liệu `CLAUDE.md` và `docs/BOI_CANH_DU_AN.md` mục 7 còn mô tả default model A (`phobert`). Giữ trong backlog cập nhật tài liệu của PO; không sửa trong authority sync này. Giá trị runtime T10 đã duyệt là `phobert_b`. |
| **F-TODO-05** | **ACCEPT_LATER — ARTIFACT PRESERVATION** | Giữ nguyên `__pycache__/02_fresh_backup.cpython-313.pyc` trong canonical package ngoài Git. Không xóa/di chuyển/đổi tên. Chờ PO quyết định cleanup riêng; các lần chạy sau dùng `python -B`. |
| **F-TODO-06** | **ACCEPT_LATER — PROPOSED T11 BACKLOG** | Health có thể trả nguyên văn `classifier_error` kèm đường dẫn. Ghi nhận cần xử lý trước khi công khai/deploy; đề xuất backlog T11 nhưng **T11 chưa được authorize/mở**. |
| **F-TODO-07** | **ACCEPT_LATER — HISTORICAL DISPOSITIONS PRESERVED** | Giữ các TODO Round 2 và G2-R4-01…04 theo các quyết định trước; không tự mở lại, không tự thay đổi disposition. |

**Tổng:** 2 `FIX_NOW` trước closure (F-TODO-01, F-TODO-03); 5 `ACCEPT_LATER` có điều kiện/đầu mối. Không có RF bắt buộc phải sửa code.

## 4. Quyền hạn đồng bộ authority/coordination — đợt riêng

PO cho phép Codex thực hiện **một đợt đồng bộ tài liệu có kiểm soát** trên nhánh T10 hiện hành, sau khi kiểm tra lại live Git/evidence:

1. `docs/TASK_COORDINATION_ACTIVE.md` — ghi chính xác trạng thái `PO_APPROVED`, chưa CLOSED, T10 vẫn là active task; Gate 2 COMMITTED, Postverify/Clone Smoke/QA/Claude PASS và TODO dispositions; T11 vẫn `PLANNED / NOT AUTHORIZED`.
2. `docs/PROJECT_SOURCE_OF_TRUTH.md` — **ngoại lệ một lần, giới hạn trong bổ sung facts/PO decisions T10 Gate 2 và trạng thái PO approval**, không chỉnh sửa những quyết định khác hoặc nguồn authority toàn cục.
3. `docs/tasks/T10.md` — cập nhật `Current Status: PO_APPROVED` và ghi chú closure pending nếu cần; không thay nội dung AC, scope, schema, yêu cầu.
4. `reports/2026-10-11/po_review_T10_APPROVED_2026-10-11.md` — lưu nguyên quyết định PO này.
5. `reports/2026-10-11/codex_authority_coordination_sync_T10_2026-10-11.md` — báo cáo diff, bằng chứng và commit của đợt sync.

Nếu các file live hoặc Git ở Windows khác với thông tin đầu vào thì **HARD STOP, báo PO**, không tự chép đè bằng file snapshot/archive cũ. Nếu mọi safety gate và diff allowlist PASS, Codex được phép tạo **duy nhất một commit tài liệu** `[T10] Sync Gate 2 authority and PO approval`; commit không được chứa code/runtime, chỉ năm đường dẫn trên. Mọi sai lệch cần PO quyết định riêng.

## 5. Hành động chưa được cho phép

Quyết định `APPROVED_WITH_NOTES` **không** cấp quyền:

- Merge sang `master`, force-push hoặc rewrite history.
- Tạo, di chuyển, xóa hoặc overwrite tag `phobert-B` hay tag bất kỳ.
- Chuyển T10 sang `DONE/CLOSED` hoặc đặt `Current Active Task: NONE`.
- Mở T11, chuyển `READY_FOR_HANDOFF`, tạo nhánh T11, chạy work T11.
- Khởi động backend với real DB, seed, restore, sửa schema, clone smoke/ALTER/Postverify lại.
- Sửa model weights, source production, tests, dependency, `normalize()`; thay đổi package Gate 2 canonical.
- Cleanup, xóa, MOVE, RENAME các artifact T10 cũ hoặc sửa historical evidence.
- Sửa `docs/AGENT_RULES.md`, `docs/BOI_CANH_DU_AN.md`, `CLAUDE.md` trong đợt sync này.

## 6. Kết luận và chuyển bước

**Decision:** `APPROVED_WITH_NOTES`  
**Transition đã được PO phê duyệt:** `PO_REVIEW → PO_APPROVED (CLOSURE_PENDING)`  
**Chưa được phép:** `PO_APPROVED → DONE → CLOSED`  
**Open Required Fixes:** `0`  
**Governance pending:** F-TODO-01 và F-TODO-03 phải hoàn tất và xác minh trên Git trước closure  
**Next step:** Codex authority/coordination sync → Codex HARD STOP → PO xem evidence và quyết định riêng merge/tag/closure (nếu đủ điều kiện).

*Báo cáo được soạn từ quyết định PO đã nêu và evidence T10 do Codex/Claude cung cấp; việc ghi vào repository và thực hiện commit chỉ được xác nhận sau khi Codex gửi bằng chứng từ máy Windows.*
