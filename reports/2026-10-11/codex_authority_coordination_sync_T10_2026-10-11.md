# Codex Authority / Coordination Sync Report — T10

**Ngày:** 2026-10-11 (Asia/Ho_Chi_Minh)

**Task:** T10 — Gắn PhoBERT B vào web

**PO Decision:** `APPROVED_WITH_NOTES`

**Authority amendment:** V2 — six-file allowlist / one documentation commit

**Kết quả hiện hành:** V3 exception verified; toàn bộ precommit gates ngoài ngoại lệ đã PASS; controlled commit pending

## 1. Checkpoint

| Trường | Giá trị |
|---|---|
| Branch | `task/T10-gan-model-B` |
| Baseline | `38f63eedf3682216c1256cc581811e5ae9e05406` |
| Original HEAD | `27701d19a150117919e0172f2386d819a7b9d369` |
| Commit message dự kiến | `[T10] Sync Gate 2 authority and PO approval` |
| Merge/tag/closure | `NOT AUTHORIZED` |
| T11 | `PLANNED / NOT AUTHORIZED` |

V2 do PO gửi trực tiếp trong hội thoại mở rộng allowlist từ năm lên sáu file, bổ sung Claude Final Independent Review. Amendment chỉ thay đổi allowlist/commit composition; các hạn chế còn lại trong PO Review giữ nguyên. Không sửa PO Review để thay mô tả lịch sử “5 file”.

V2 đã dừng đúng quy trình tại `BLOCKED_AT_CACHED_DIFF_CHECK`. PO sau đó cấp V3 scoped Markdown whitespace exception: chỉ miễn trừ intentional hard-break bằng đúng hai dấu cách cuối dòng trong immutable PO Review; không miễn trừ file khác và không tắt Git whitespace policy.

## 2. Authority report verification

| Report | SHA-256 thực tế | Expected | Nội dung | Kết quả |
|---|---|---|---|---|
| `reports/2026-10-11/po_review_T10_APPROVED_2026-10-11.md` | `1B03F754C4CAC3F84CAD72BA1EC6974B066A41DF71355ACC3D4253A4C0D3C9B1` | Cùng giá trị | `APPROVED_WITH_NOTES`, đủ 7 TODO dispositions | **MATCH / PASS** |
| `reports/2026-10-11/claude_review_T10_PASS_WITH_TODO_2026-10-11.md` | `E15B43D81F3FA4AAE2AF2E16424323AAAC823F2A504F91F624E697BC58A3C4ED` | Cùng giá trị | `PASS_WITH_TODO`; AC 7/7; Technical DoD MET; RF 0; TODO 7; reviewed HEAD đúng | **MATCH / PASS** |

Hai file report được giữ nguyên byte-for-byte; không chỉnh whitespace hoặc encoding.

## 3. Database và evidence safety

- Real DB: `C:\Projects\firefly-cinema\backend\firefly.db`.
- Expected SHA-256: `B3F7DF79BDA4478412200EA80B8EC15E6B73DA730068A52E11C40136EAC4CFE3`.
- SHA-256 trước sync: `B3F7DF79BDA4478412200EA80B8EC15E6B73DA730068A52E11C40136EAC4CFE3` — MATCH.
- SHA-256 sau chỉnh tài liệu, trước commit: `B3F7DF79BDA4478412200EA80B8EC15E6B73DA730068A52E11C40136EAC4CFE3` — MATCH.
- SQLite `-wal`, `-shm`, `-journal`: không tồn tại.
- Backend/SQLite writer liên quan: 0.
- Không mở SQLite connection; không startup backend; không MOVE/DELETE/cleanup evidence.

Evidence đối chiếu:

| Gate | Kết quả | Evidence chính |
|---|---|---|
| Gate 2 A1 | `EXECUTED / ALTER_COMMITTED` | `T10_GATE2_ATTEMPT2_ALTER_FINAL_EVIDENCE_REPORT.md` |
| Postverify | `PASS`; 559 dòng gốc bảo toàn | `T10_GATE2_ATTEMPT2_POSTVERIFY_EVIDENCE_REPORT.md`, SHA `A491117E0277A627D24F3A90C3ACC9B463542A968C652ABC3D8AABCFCB476638` |
| Credential Precheck V2 | `PASS` | `T10_CREDENTIAL_PRECHECK_V2_REPORT.md`, SHA `35442CB9982C3D7224887201E7ED0E5CAF396A51F67DA4E56A32A2D2DB444B9E` |
| Clone Smoke Attempt 1 | `FAIL / ARCHIVED` | historical failure evidence được bảo toàn |
| Clone Smoke Attempt 2 | `PASS` | retry2 report; historical hash transcription đã được reconciliation |
| Hash reconciliation | `PASS` | `T10_GATE2_CLONE_SMOKE_RETRY2_HASH_RECONCILIATION_REPORT.md`, SHA `8733C428A314E9A7C486C72AB8A5024650A4332D73E46E0B4FBA92D5B320BAD2` |
| DEV Final QA | `PASS` | `T10_FINAL_QA_EVIDENCE_REPORT.md`, SHA `E01F1749BEF85599BD59AAF424C8AA8F6F9AC15C4360696A3EB06DC225214023` |
| Claude Final | `PASS_WITH_TODO` | report trong commit này |

## 4. Governance changes

### `docs/TASK_COORDINATION_ACTIVE.md`

- Current Active Task vẫn là `T10`.
- Chuyển trạng thái sang `PO_APPROVED / CLOSURE_PENDING`.
- Ghi Gate 2 `EXECUTED / ALTER_COMMITTED`, Postverify PASS, Credential Precheck V2 PASS, Attempt 1 FAIL/ARCHIVED, Attempt 2 PASS, Hash Reconciliation PASS, DEV Final QA PASS và Claude Final PASS_WITH_TODO.
- Ghi AC 7/7, Technical DoD MET, Required Fixes 0 và PO APPROVED_WITH_NOTES.
- Ghi đủ F-TODO-01…07 và disposition PO.
- Giữ T11 `PLANNED / NOT AUTHORIZED`; không đặt active task thành NONE.

### `docs/PROJECT_SOURCE_OF_TRUTH.md`

- Chỉ thêm subsection T10 Gate 2 và PO approval.
- Ghi Decision ID `PO-DECISION-T10-REALDB-A1-GATE2-20261010`, ALTER duy nhất, schema nullable, 559 dòng bảo toàn, các gate PASS, DB hash và PO decision.
- Ghi V2 amendment bổ sung Claude Final Review thành artifact thứ sáu.
- Giữ nguyên authority toàn cục và các quyết định T00–T09.

### `docs/tasks/T10.md`

- Chỉ đổi `Current Status` từ `IN_PROGRESS` thành `PO_APPROVED`.
- Thêm `Closure: PENDING — chờ quyết định merge/closure riêng của PO`.
- Không sửa AC, scope, dependency, test instruction hoặc nghiệp vụ.

## 5. TODO dispositions

| ID | PO disposition | Sync result |
|---|---|---|
| F-TODO-01 | `FIX_NOW` — authority/coordination | `RESOLVED_BY_GOVERNANCE_SYNC` |
| F-TODO-02 | `ACCEPT_LATER` — real backend cần PO runtime gate | Bảo toàn |
| F-TODO-03 | `FIX_NOW` — Task Record status | `RESOLVED_BY_GOVERNANCE_SYNC` |
| F-TODO-04 | `ACCEPT_LATER` — PO-owned docs | Bảo toàn |
| F-TODO-05 | `ACCEPT_LATER` — immutable package pycache | Bảo toàn; không cleanup |
| F-TODO-06 | `ACCEPT_LATER` — proposed T11 backlog | Bảo toàn; T11 chưa authorize |
| F-TODO-07 | `ACCEPT_LATER` — historical dispositions | Bảo toàn |

T10 chưa `DONE/CLOSED`.

## 6. Exact six-file allowlist

1. `docs/TASK_COORDINATION_ACTIVE.md`
2. `docs/PROJECT_SOURCE_OF_TRUTH.md`
3. `docs/tasks/T10.md`
4. `reports/2026-10-11/po_review_T10_APPROVED_2026-10-11.md`
5. `reports/2026-10-11/codex_authority_coordination_sync_T10_2026-10-11.md`
6. `reports/2026-10-11/claude_review_T10_PASS_WITH_TODO_2026-10-11.md`

## 7. Controlled commit gates

| Gate | Kết quả |
|---|---|
| Working state trước sync | PASS — chỉ đúng hai authority reports untracked được V2 cho phép |
| `git diff --check` | PASS |
| PO/Claude hashes | MATCH |
| Real DB hash | MATCH |
| Production backend/frontend/ml diff so với original HEAD | PASS — rỗng |
| Dependency/model artifact changes | PASS — không có |
| Secret scan | PASS — 0 credential/private-key/bearer-token pattern |
| Exact six-file staged allowlist | PASS — đúng 6/6, không thiếu/thừa |
| Full `git diff --cached --check` | `EXPECTED_FAIL_WITH_PO_EXCEPTION` — exit 2, chỉ PO Review |
| PO Markdown hard-break exception | VERIFIED — 12 dòng, đúng hai space ASCII, không tab |
| Other five files whitespace check | PASS — exit 0 |
| Merge conflicts | PASS — 0 |
| Branch | PASS — `task/T10-gan-model-B` |

### Blocker tại commit gate

`git diff --cached --check` phát hiện trailing whitespace trong `reports/2026-10-11/po_review_T10_APPROVED_2026-10-11.md`, gồm các dòng Markdown dùng hai dấu cách cuối dòng. PO report phải giữ nguyên byte-for-byte theo V2 để duy trì SHA-256 `1B03F754C4CAC3F84CAD72BA1EC6974B066A41DF71355ACC3D4253A4C0D3C9B1`; vì vậy Codex không được tự chuẩn hóa whitespace. Report sync do Codex tạo ban đầu cũng có hard-break tương tự và đã được chuẩn hóa trong bản báo cáo blocker V2.

Theo V2: cached diff check FAIL dẫn đến **HARD STOP / NO COMMIT**. Codex không sửa report PO/Claude, không dùng cấu hình Git để che gate, không reset/unstage và không retry commit. PO đã xử lý blocker bằng V3 authorization.

V3 verification ghi nhận chính xác 12 dòng được miễn trừ: `3, 4, 5, 6, 7, 19, 20, 84, 85, 86, 87, 88`. Mỗi dòng có đúng hai dấu cách ASCII cuối dòng, không có tab; không có whitespace error nào khác trong PO Review. Full cached check vẫn trả exit `2` và được ghi đúng là `EXPECTED_FAIL_WITH_PO_EXCEPTION`. Lệnh kiểm tra riêng năm file ngoài PO Review trả exit `0`.

## 8. Không thực hiện

- Không merge, tag, push, amend, rebase, reset hoặc rewrite history.
- Không đóng T10 hoặc mở T11.
- Không khởi động backend trên database thật; không seed/ALTER/Postverify/Clone Smoke lại.
- Không sửa production source, tests, dependency, model hoặc package Gate 2.
- Không cleanup/move/delete evidence.

## 9. Disposition tại thời điểm lập báo cáo

V2 GOVERNANCE SYNC: BLOCKED_AT_CACHED_DIFF_CHECK (historical, preserved)

V3 WHITESPACE EXCEPTION: VERIFIED

FULL CACHED DIFF CHECK: EXPECTED_FAIL_WITH_PO_EXCEPTION

PO MARKDOWN HARDBREAK EXCEPTION: VERIFIED

OTHER FIVE FILES WHITESPACE CHECK: PASS

F-TODO-01: RESOLVED_BY_GOVERNANCE_SYNC khi commit thành công

F-TODO-03: RESOLVED_BY_GOVERNANCE_SYNC khi commit thành công

OTHER TODOs: ACCEPT_LATER

FILES STAGED: 6 / exact allowlist

COMMIT: NOT YET CREATED

REAL DB PRESERVED: YES

NEXT STEP: tạo đúng một documentation commit đã được PO phê duyệt, sau đó HARD STOP để PO review.
