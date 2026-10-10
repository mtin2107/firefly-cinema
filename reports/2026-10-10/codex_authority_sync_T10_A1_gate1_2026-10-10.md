# Codex Authority Sync Report — T10 A1 Gate 1 — 10/10/2026

## 1. Task, branch và HEAD

- Task: `T10 — Gắn model B vào web`.
- Branch: `task/T10-gan-model-B`.
- HEAD thực tế trước/sau docs sync: `498d4b866d1bc2f258cb020faf0bee1ef133563a`.
- Implementation `0e80015`, fix `ed26454` và Claude Round 2 `498d4b8` đều thuộc lịch sử HEAD.
- Claude Round 2: `PASS_WITH_TODO`; RF-01 `CLOSED / VERIFIED BY CLAUDE`; AC 7/7; Required Fixes 0.
- Workflow: `PO_REVIEW / PENDING_PO_DB_ACTION`.
- T11: `PLANNED / NOT AUTHORIZED`.

## 2. PO Decision

Decision ID: `PO-DECISION-T10-REALDB-A1-GATE1-20261010`.

- **GATE 1 APPROVED** ngày 10/10/2026.
- PO chọn phương án kỹ thuật A1 cho riêng T10: chuẩn bị manual SQLite ALTER bổ sung duy nhất `comments.model_version VARCHAR(100) NULL`, không dùng Alembic, không reset theo A1 và bảo toàn dữ liệu cũ.
- **GATE 2 NOT AUTHORIZED**: chưa được ghi, ALTER, reset, migrate, seed, restore/ghi đè hoặc startup có khả năng ghi DB thật.
- Phê duyệt phương án kỹ thuật không đồng nghĩa với phê duyệt thực thi.

## 3. Phạm vi ủy quyền PO-owned

PO cấp ngoại lệ một lần để Codex sửa tối thiểu `docs/PROJECT_SOURCE_OF_TRUTH.md`, duy nhất nhằm ghi nhận Gate 1 A1. Ngoại lệ không mở rộng sang `AGENT_RULES.md`, `BOI_CANH_DU_AN.md`, Task Record hoặc quyết định PO khác. Không có file production/test/model/database nào được phép sửa.

Report DB preflight `reports/2026-10-10/codex_db_preflight_T10_2026-10-10.md` đã tồn tại ở trạng thái untracked khi bắt đầu lượt này; được bảo toàn nguyên vẹn và không tính là file bị sửa bởi authority sync.

## 4. Files changed trong lượt Gate 1

1. `docs/PROJECT_SOURCE_OF_TRUTH.md`.
2. `docs/TASK_COORDINATION_ACTIVE.md`.
3. `HUONG_DAN.md`.
4. `reports/2026-10-10/codex_authority_sync_T10_A1_gate1_2026-10-10.md` — file mới.

Không sửa `AGENT_RULES.md`, `BOI_CANH_DU_AN.md`, `docs/tasks/T10.md`, source code, checkpoint hoặc database.

## 5. Source of Truth — Q2 exception

Giữ nguyên quyết định lịch sử `Q2 RESOLVED 08/10/2026 — NO ALEMBIC / BACKUP_BEFORE_RESET`. Bổ sung một mục riêng cho `PO-DECISION-T10-REALDB-A1-GATE1-20261010`, ghi rõ:

- Gate 1 APPROVED; A1 chỉ áp dụng cho T10.
- Mục tiêu duy nhất là `comments.model_version VARCHAR(100) NULL`.
- Không Alembic, không reset theo A1, phải bảo toàn dữ liệu.
- Backup/restore/schema/API clone preflight PASS.
- Gate 2 NOT AUTHORIZED; DB thật chưa READY; mọi thao tác ghi cần PO quyết định riêng.
- Runbook ở `HUONG_DAN.md` mục 2.1.

Q1, Q3, Q4 và ngày/kết quả Q2 lịch sử không bị thay đổi.

## 6. Coordination sync

Các trạng thái hiện hành được đồng bộ:

- Overall: `PO_REVIEW / PENDING_PO_DB_ACTION`.
- Current active task: `T10 — PO_REVIEW / PENDING_PO_DB_ACTION`.
- Next task: `T11 — PLANNED / NOT AUTHORIZED`.
- Claude Round 2, RF-01 CLOSED, AC 7/7 và Required Fixes 0 được giữ nguyên.
- `T10 REAL_DB_SCHEMA_READINESS = PENDING_PO_GATE2`.
- Technical dry-run PASS; Gate 1 APPROVED; Gate 2 NOT AUTHORIZED.
- Database thật `UNCHANGED / NOT READY FOR T10 RUNTIME`.
- TODO-01 vẫn `PO ACTION REQUIRED / OPEN`, không ghi RESOLVED.

Current Next Step được tách thành: docs sync → PO review diff → PO commit → quyết định Gate 2 riêng → fresh backup + A1 sau Gate 2 → verify DB/API thật → tiếp tục PO Review/merge/tag/closure. Timeline được nối thêm sự kiện Gate 1, không xóa/viết lại lịch sử.

## 7. Runbook A1 changes

`HUONG_DAN.md` mục 2.1 mang nhãn bắt buộc:

`DRAFT — GATE 2 NOT AUTHORIZED — DO NOT EXECUTE`

Runbook A1 có đủ sáu giai đoạn:

1. Pre-execution gate: đúng repo/branch/HEAD, Gate 2 riêng, đúng runtime DB, backend dừng, schema đúng và cột chưa tồn tại.
2. Fresh consistent backup: timestamp mới, SQLite Online Backup, integrity/FK/count/fingerprint/restore validation; snapshot 14:50 chỉ là evidence lịch sử.
3. Schema change: draft transaction, kiểm cột, chỉ một ALTER; rollback transaction nếu lỗi; không DROP/DELETE/reset/seed.
4. Post-schema verification trước startup: nullable/default NULL, 100% dữ liệu gốc/PK/FK/index/constraint/fingerprint giữ nguyên.
5. Runtime smoke: health/movies/comments/admin/security/model version; ghi nhận `_ensure_showtimes` có thể thêm suất mới.
6. Rollback: dừng backend, quarantine DB lỗi, không ghi đè backup, restore chỉ sau PO authorization riêng và validation đầy đủ.

Các câu lệnh là draft cho PO review, không được chạy trong lượt này.

## 8. A1 và A2 governance

- A1 là ngoại lệ có kiểm soát cho T10, mới được duyệt ở Gate 1. Nó không trở thành chính sách migration mặc định.
- A2 vẫn là quy trình Q2 lịch sử: backup trước khi PO reset. Runbook giữ A2 và cảnh báo reset/seed không tự bảo toàn tài khoản, vé, ghế, bình luận.
- Không tự chuyển từ A1 sang A2 nếu ALTER fail; phải hard stop và xin PO quyết định.

## 9. Backup evidence đã đối chiếu

Evidence lịch sử từ preflight tại `498d4b8`:

- Source: `backend/firefly.db`.
- Source SHA-256: `ED3ABDBAD7FF65F74D2182DC8B5C757E8FC32EDF37DCAF4073EAC1D375E70D0A`.
- Online backup: `backup/T10_2026-10-10/db_preflight_20261010_145049/firefly_online_backup.db`.
- Backup SHA-256: `BADCE9E0D9E0262F2DD3903BD451F4C0DA1E2F72913F02049BA36504C1878782`.
- Snapshot: users 3, movies 21, showtimes 99, bookings 141, booking_seats 282, comments 13.
- Source integrity, FK check, online backup, restore dry-run, schema dry-run và data preservation: PASS.
- API regression clone: 10/10 PASS.

Số liệu này chỉ chứng minh snapshot lúc 14:50 ngày 10/10/2026. Gate 2 bắt buộc fresh backup/evidence mới.

## 10. Authority conflicts còn tồn tại

1. `docs/BOI_CANH_DU_AN.md` mục 6.5 vẫn ghi hướng dẫn legacy: thêm/đổi cột thì xóa `firefly.db`; mục 12 còn giữ Q2 như câu hỏi cũ. Đây là documentation conflict/legacy guidance. Source of Truth Gate 1 là quyết định PO mới hơn và thắng riêng cho T10, nhưng vẫn chưa cho phép thực thi. File legacy không được sửa trong lượt này.
2. `docs/tasks/T10.md` còn `Current Status: IN_PROGRESS`; coordination là nguồn trạng thái hiện hành và đang `PO_REVIEW / PENDING_PO_DB_ACTION`. TODO-04 giữ nguyên, Task Record không sửa.
3. `AGENT_RULES.md` mục 1.1 cho phép Claude chuẩn bị task tiếp theo sau PASS, nhưng PO hiện giữ T11 `PLANNED / NOT AUTHORIZED`. Quyết định PO mới hơn được giữ; không mở T11.

Không có xung đột nào cấp quyền Gate 2 hoặc yêu cầu sửa ngoài bốn file được phép.

## 11. Authority conflict audit — kết quả

| Kiểm tra | Kết quả |
|---|---|
| Q2 không thành ALTER mặc định | PASS |
| Gate 1 APPROVED ở ba tài liệu cập nhật | PASS |
| Gate 2 NOT AUTHORIZED ở ba tài liệu cập nhật | PASS |
| Không hướng dẫn hiểu Gate 1 là quyền chạy thật | PASS |
| T10 vẫn PO_REVIEW / pending DB action | PASS |
| T11 vẫn PLANNED / NOT AUTHORIZED | PASS |
| RF-01 vẫn CLOSED; Required Fixes 0 | PASS |
| TODO-01 vẫn OPEN / PO ACTION REQUIRED | PASS |
| Quyết định PO lịch sử không bị thay đổi | PASS |
| Source/checkpoint/database thật không thay đổi | PASS |

## 12. Git và scope gates

- Đúng branch T10; HEAD không đổi.
- Không reset/stash/restore/checkout/merge/tag.
- `git diff --check`: PASS.
- Tracked diff chỉ có ba tài liệu được phép.
- Hai report untracked: DB preflight có trước và được bảo toàn; authority-sync là report mới của lượt này.
- Không stage và không commit.
- Không có production, test, model, `.env` hoặc database trong diff/staging.

## 13. Database safety

Không chạy lại database test, backend, seed, migration hoặc ALTER. DB thật không bị ghi. Source checksum đối chiếu read-only vẫn là `ED3ABDBAD7FF65F74D2182DC8B5C757E8FC32EDF37DCAF4073EAC1D375E70D0A`; `model_version` vẫn chưa tồn tại, đúng trạng thái `PENDING_PO_GATE2`.

`REAL DB MODIFIED = NO`.

## 14. Những gì PO cần review trước commit

1. Ngoại lệ Q2 trong Source of Truth có đúng phạm vi T10 và không làm suy yếu Gate 2 hay không.
2. Coordination có giữ đúng PO_REVIEW, TODO-01 và T11 chưa authorized hay không.
3. Sáu giai đoạn runbook, draft backup/ALTER và rollback có đủ điều kiện hard-stop hay không.
4. Disposition đối với ba conflict legacy ở mục 10.
5. Chỉ sau khi chấp nhận diff, PO mới commit tài liệu; Gate 2 vẫn cần quyết định riêng sau đó.

## 15. Kết luận

- Gate 1: **APPROVED / SYNCED IN WORKTREE**.
- Gate 2: **NOT AUTHORIZED**.
- Database thật: unchanged, not ready.
- Commit: không tạo; chờ PO review.
- Next step: PO review document diff.
