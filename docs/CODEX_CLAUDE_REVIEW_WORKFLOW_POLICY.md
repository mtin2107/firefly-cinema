# CODEX_CLAUDE_REVIEW_WORKFLOW_POLICY

## 1. Mục đích

Tài liệu này định nghĩa workflow chuẩn để sử dụng **Codex** làm Primary Implementer và **Claude** làm Independent Reviewer / Tester cho các dự án phần mềm.

Mục tiêu:

- Tách rõ người triển khai và người review.
- Không để Codex tự review hoặc tự approve code của chính mình.
- Không để Claude tự sửa production code trong bước review.
- Có bằng chứng rõ ràng cho từng task thông qua report.
- Có Fix Loop khi review thất bại.
- Giảm token bằng cách không đọc lại toàn bộ lịch sử task đã CLOSED.
- Quản lý report theo ngày nhưng quản lý công việc theo Task ID.
- Chỉ đóng task sau khi review kỹ thuật đạt yêu cầu và Product Owner phê duyệt.

---

## 2. Vai trò

### 2.1. Codex — Primary Implementer

Codex chịu trách nhiệm:

- Đọc Task Record hiện tại.
- Kiểm tra dependency trực tiếp.
- Đọc source code và tests trực tiếp liên quan.
- Triển khai production code.
- Viết hoặc cập nhật tests.
- Chạy focused tests trong quá trình triển khai.
- Chạy full gates khi focused tests đã ổn định.
- Tạo implementation report.
- Cập nhật `TASK_COORDINATION_ACTIVE.md`.
- Chuyển task sang `CLAUDE_REVIEW`.

Codex không được:

- Tự review code của mình.
- Tự gán `PASS`.
- Tự chuyển sang `PO_REVIEW`.
- Tự approve task.
- Tự đóng task.
- Tự tạo task kế tiếp.
- Tự mở rộng scope ngoài Task Record.

---

### 2.2. Claude — Independent Reviewer / Tester

Claude chịu trách nhiệm:

- Đọc Task Record hiện tại.
- Đọc Codex implementation/fix report mới nhất.
- Review source code thực tế.
- Review tests thực tế.
- Kiểm tra Acceptance Criteria.
- Kiểm tra Definition of Done.
- Kiểm tra architecture.
- Kiểm tra security.
- Kiểm tra regression.
- Kiểm tra scope.
- Chạy tests độc lập.
- Tạo temporary probes khi thật sự cần thêm evidence.
- Xóa probes trước final gates.
- Tạo review report.
- Trả kết quả `PASS`, `PASS_WITH_TODO`, hoặc `FAIL`.

Claude không được:

- Sửa production code trong bước review.
- Tự implement Required Fix.
- Tự approve task.
- Tự đóng task.
- Tự tạo task tiếp theo.

---

### 2.3. Product Owner / Project Owner

Product Owner chịu trách nhiệm:

- Kiểm tra kết quả Claude.
- Kiểm tra task có đúng mục tiêu sản phẩm không.
- Kiểm tra Acceptance Criteria và Definition of Done.
- Disposition toàn bộ TODO.
- Chấp nhận hoặc yêu cầu thay đổi.

Kết quả:

```text
APPROVED
APPROVED_WITH_NOTES
CHANGES_REQUESTED
REJECTED
```

Chỉ `APPROVED` hoặc quyết định tương đương được Project Owner cho phép mới được đóng task.

---

## 3. Workflow chuẩn

```text
PLANNING
   ↓
READY_FOR_HANDOFF
   ↓
CODEX_IMPLEMENTATION
   ↓
CLAUDE_REVIEW
   ├── PASS ──────────────→ PO_REVIEW
   ├── PASS_WITH_TODO ───→ PO_REVIEW
   └── FAIL
        ↓
      FIX_LOOP
        ↓
      CODEX_FIX
        ↓
      CLAUDE_REVIEW
        ↓
      ... lặp cho đến PASS
                              ↓
                           PO_REVIEW
                              ↓
                           APPROVED
                              ↓
                         DONE / CLOSED
```

---

## 4. Trạng thái task

Các trạng thái chuẩn:

```text
PLANNED
READY_FOR_HANDOFF
IN_PROGRESS
CLAUDE_REVIEW
FIX_LOOP
PO_REVIEW
PO_APPROVED
DONE
CLOSED
BLOCKED
REJECTED
```

Luồng bình thường:

```text
PLANNED
-> READY_FOR_HANDOFF
-> IN_PROGRESS
-> CLAUDE_REVIEW
-> PO_REVIEW
-> PO_APPROVED
-> DONE
-> CLOSED
```

Nếu Claude FAIL:

```text
CLAUDE_REVIEW
-> FIX_LOOP
-> IN_PROGRESS
-> CLAUDE_REVIEW
```

Nếu Product Owner yêu cầu sửa:

```text
PO_REVIEW
-> FIX_LOOP
-> IN_PROGRESS
-> CLAUDE_REVIEW
```

---

## 5. File điều phối chính

Mỗi dự án nên có:

```text
TASK_COORDINATION_ACTIVE.md
```

Đây là **single active source of truth** cho task đang hoạt động.

File này chỉ nên chứa:

```text
1. Project Snapshot
2. Stable Architecture / Security / Scope Rules
3. Latest Completed Task Summary
4. Current Project Status
5. Current Active Task
6. Current Task Record
7. Open Blockers
8. Open Required Fixes
9. Open TODOs
10. Current Next Step
11. Active Timeline
```

Không chép toàn bộ lịch sử task CLOSED vào file active.

---

## 6. Quy tắc đọc tiết kiệm token

Mọi prompt cho Codex và Claude nên có nguyên tắc:

```text
Chỉ đọc:
- Project Snapshot
- Current Project Status
- Current Next Step
- Task Record <TASK-ID>
- Latest completed task summary nếu có dependency trực tiếp

Không đọc các task đã CLOSED trừ khi có dependency, conflict hoặc audit cụ thể.
```

Được đọc thêm:

```text
- Live source trực tiếp liên quan.
- Tests trực tiếp liên quan.
- Report mới nhất của task hiện tại.
- Dependency trực tiếp nếu thật sự cần.
```

Không mặc định đọc:

```text
- Toàn bộ repository.
- Toàn bộ coordination.
- Toàn bộ lịch sử task.
- Report cũ không liên quan.
- Archived coordination không có dependency.
```

---

## 7. Cấu trúc thư mục report theo ngày

Khuyến nghị:

```text
PROJECT/
│
├── docs/
│   ├── PROJECT_SOURCE_OF_TRUTH.md
│   ├── REQUIREMENTS.md
│   ├── ARCHITECTURE.md
│   ├── TASK_COORDINATION_ACTIVE.md
│   └── CODEX_CLAUDE_REVIEW_WORKFLOW_POLICY.md
│
├── reports/
│   ├── YYYY-MM-DD/
│   │   ├── codex_implementation_<TASK-ID>_YYYY-MM-DD.md
│   │   ├── claude_review_<TASK-ID>_PASS_YYYY-MM-DD.md
│   │   └── po_review_<TASK-ID>_APPROVED_YYYY-MM-DD.md
│   │
│   └── YYYY-MM-DD/
│       ├── codex_implementation_<TASK-ID>_YYYY-MM-DD.md
│       ├── claude_review_<TASK-ID>_FAIL_YYYY-MM-DD.md
│       ├── codex_fix_<TASK-ID>_round1_YYYY-MM-DD.md
│       ├── claude_review_<TASK-ID>_round2_PASS_YYYY-MM-DD.md
│       └── po_review_<TASK-ID>_APPROVED_YYYY-MM-DD.md
│
└── source-code/
```

Ngày dùng để quản lý report.

**Task ID mới là đơn vị quản lý công việc.**

Một ngày có thể hoàn thành nhiều task.

---

## 8. Quy tắc đặt tên report

### Codex implementation

```text
codex_implementation_<TASK-ID>_<YYYY-MM-DD>.md
```

Ví dụ:

```text
codex_implementation_GF-MVP-FOUNDATION-001_2026-08-16.md
```

### Codex fix

```text
codex_fix_<TASK-ID>_round<N>_<YYYY-MM-DD>.md
```

Ví dụ:

```text
codex_fix_GF-MVP-FOUNDATION-001_round1_2026-08-16.md
```

### Claude PASS

```text
claude_review_<TASK-ID>_PASS_<YYYY-MM-DD>.md
```

### Claude PASS_WITH_TODO

```text
claude_review_<TASK-ID>_PASS_WITH_TODO_<YYYY-MM-DD>.md
```

### Claude FAIL

```text
claude_review_<TASK-ID>_FAIL_<YYYY-MM-DD>.md
```

### Claude review vòng tiếp theo

```text
claude_review_<TASK-ID>_round2_PASS_<YYYY-MM-DD>.md
claude_review_<TASK-ID>_round3_FAIL_<YYYY-MM-DD>.md
```

### Product Owner

```text
po_review_<TASK-ID>_APPROVED_<YYYY-MM-DD>.md
```

---

## 9. Nội dung Task Record tối thiểu

Mỗi task cần có:

```text
Task ID:
Task Name:
Module:
Assignee:
Reviewer:
Approver:

Objective:

Context:

Dependencies:

Allowed Scope:

Out of Scope:

Allowed Files to Modify:

Forbidden Files to Modify:

Acceptance Criteria:

Definition of Done:

How to Test:

Required Gates:

Expected Reports:

Current Status:
```

Không giao task nếu chưa rõ:

```text
- Task ID
- Objective
- Scope
- Output
- Acceptance Criteria
- Definition of Done
- Test strategy
- Dependency
```

---

## 10. Codex Implementation Workflow

### Bước 1 — Nhận task

Codex xác nhận:

```text
Current Status: READY_FOR_HANDOFF
```

Sau đó chuyển:

```text
READY_FOR_HANDOFF -> IN_PROGRESS
```

### Bước 2 — Đọc đúng phạm vi

Codex chỉ đọc:

```text
- Task Record.
- Current project status.
- Current next step.
- Direct dependencies.
- Source và tests liên quan.
```

### Bước 3 — Implement

Codex:

```text
- Chỉ sửa file trong allowlist.
- Không tự mở rộng feature.
- Không đổi architecture ngoài task.
- Không bỏ security để fix nhanh.
- Không xóa test chỉ để PASS.
```

### Bước 4 — Focused tests

Trong quá trình implement:

```text
- Format scope liên quan.
- Analyze scope liên quan.
- Focused unit tests.
- Focused integration tests.
- Direct regression tests.
```

Không chạy full suite lặp đi lặp lại khi focused tests còn fail.

### Bước 5 — Final gates

Khi focused tests ổn định:

```text
FORMAT
ANALYZE / LINT
UNIT TEST
INTEGRATION TEST nếu có
FULL TEST SUITE
BUILD
SECURITY / MARKER SCAN nếu dự án yêu cầu
```

### Bước 6 — Report

Codex tạo:

```text
reports/YYYY-MM-DD/codex_implementation_<TASK-ID>_YYYY-MM-DD.md
```

### Bước 7 — Handoff

Cập nhật:

```text
IN_PROGRESS -> CLAUDE_REVIEW
```

---

## 11. Codex Implementation Report Template

```text
# Codex Implementation Report

Task: <TASK-ID>
Date: <YYYY-MM-DD>
Result: IMPLEMENTATION_COMPLETED

## Files Changed
- ...

## Implemented
- ...

## Architecture / Contract
- ...

## Focused Tests
- X/X PASS

## Final Gates
Format: PASS
Analyze/Lint: PASS
Tests: X/X PASS
Build: PASS

## Security
PASS / NOT_APPLICABLE / ISSUE

## Scope
Out-of-scope changes: NO

## Blockers
0

## Required Follow-up
0

## TODO
0

## Handoff
Ready for Claude Independent Review.
```

Report phải ngắn.

Không sao chép toàn bộ Task Record vào report.

---

## 12. Claude Independent Review Workflow

### Bước 1 — Đọc evidence

Claude đọc:

```text
- Current Task Record.
- Codex report mới nhất.
- Source code trực tiếp liên quan.
- Tests trực tiếp liên quan.
```

Codex report chỉ là bằng chứng hỗ trợ.

Claude phải xác minh source và tests thực tế.

### Bước 2 — Review

Claude kiểm tra:

```text
1. Task implementation.
2. Acceptance Criteria.
3. Definition of Done.
4. Architecture.
5. Security.
6. Permissions / isolation nếu có.
7. Error handling.
8. Regression.
9. Scope integrity.
10. Test quality.
```

### Bước 3 — Temporary probes

Chỉ tạo probe nếu existing evidence chưa đủ để chứng minh:

```text
- Exact request/response contract.
- Unauthorized behavior.
- Security.
- Data leakage.
- Tenant/store/user isolation.
- Race condition.
- Concurrency.
- Stale result suppression.
- Acceptance Criterion cụ thể.
```

Sau review:

```text
Temporary probes remaining: 0
```

### Bước 4 — Final independent gates

Claude chạy full gates độc lập trên clean tree.

### Bước 5 — Kết luận

Claude chỉ trả:

```text
PASS
PASS_WITH_TODO
FAIL
```

---

## 13. Claude Review Report Template

```text
# Claude Independent Review

Task: <TASK-ID>
Date: <YYYY-MM-DD>
Result: PASS / PASS_WITH_TODO / FAIL

## Source Review
PASS / FAIL

## Acceptance Criteria
X/X PASS

## Definition of Done
MET / NOT_MET

## Architecture
PASS / FAIL

## Security
PASS / FAIL / NOT_APPLICABLE

## Regression
PASS / FAIL

## Scope Integrity
PASS / FAIL

## Independent Tests
Analyze/Lint: PASS
Tests: X/X PASS
Build: PASS

## Temporary Probes
Created: N
Remaining: 0

## Required Fixes
0

## TODO
0

## Final Decision
PASS / PASS_WITH_TODO / FAIL

## Transition
PASS / PASS_WITH_TODO:
CLAUDE_REVIEW -> PO_REVIEW

FAIL:
CLAUDE_REVIEW -> FIX_LOOP
```

---

## 14. Khi Claude FAIL

Nếu Claude trả:

```text
FAIL
```

Claude report phải ghi Required Fix rõ ràng:

```text
RF-01
Severity:
File:
Problem:
Evidence:
Expected Fix:

RF-02
Severity:
File:
Problem:
Evidence:
Expected Fix:
```

Workflow:

```text
CLAUDE_REVIEW
-> FIX_LOOP
-> CODEX_FIX
-> CLAUDE_REVIEW
```

Codex chỉ được sửa Required Fix.

Không được dùng Fix Loop để thêm feature mới.

---

## 15. Codex Fix Workflow

Codex đọc:

```text
- Current Task Record.
- Claude FAIL report mới nhất.
- Source/tests trực tiếp liên quan.
```

Codex thực hiện:

```text
- Fix RF-01, RF-02, ...
- Update/add regression tests.
- Chạy focused tests.
- Chạy final gates.
- Tạo fix report.
```

Report:

```text
reports/YYYY-MM-DD/codex_fix_<TASK-ID>_round<N>_YYYY-MM-DD.md
```

Sau đó:

```text
FIX_LOOP -> CLAUDE_REVIEW
```

Codex vẫn không được tự PASS.

---

## 16. Codex Fix Report Template

```text
# Codex Fix Report

Task: <TASK-ID>
Round: <N>
Date: <YYYY-MM-DD>

## Required Fixes Addressed

### RF-01
Status: FIXED
Files:
- ...

### RF-02
Status: FIXED
Files:
- ...

## Regression Tests
- ...

## Final Gates
Format: PASS
Analyze/Lint: PASS
Tests: X/X PASS
Build: PASS

## New Feature Added
NO

## Remaining Required Fixes
0

## Handoff
Ready for Claude re-review.
```

---

## 17. Product Owner Review

Nếu Claude:

```text
PASS
```

hoặc:

```text
PASS_WITH_TODO
```

task chuyển:

```text
CLAUDE_REVIEW -> PO_REVIEW
```

Product Owner kiểm tra:

```text
- Đúng mục tiêu sản phẩm.
- Đúng scope.
- Đúng Acceptance Criteria.
- Definition of Done đã đạt.
- Không còn Required Fix.
- Security phù hợp.
- TODO đã được disposition.
```

Nếu:

```text
APPROVED
```

chuyển:

```text
PO_REVIEW
-> PO_APPROVED
-> DONE
-> CLOSED
```

---

## 18. Product Owner Report Template

```text
# Product Owner Review

Task: <TASK-ID>
Date: <YYYY-MM-DD>
Decision: APPROVED

## Claude Result
PASS

## Acceptance Criteria
X/X PASS

## Definition of Done
MET

## Security
PASS / NOT_APPLICABLE

## Scope
PASS

## Required Fixes
0

## TODO Disposition
0 open

## Final Transition
PO_REVIEW
-> PO_APPROVED
-> DONE
-> CLOSED
```

---

## 19. Prompt chuẩn cho Codex

```text
Bạn là Codex, Primary Implementer của dự án <PROJECT_NAME>.

Chỉ đọc:
- Project Snapshot
- Current Project Status
- Current Next Step
- Task Record <TASK-ID>
- Latest completed task summary nếu có dependency trực tiếp

Không đọc các task đã CLOSED trừ khi có dependency, conflict hoặc audit cụ thể.

Đọc thêm đúng live source và tests trực tiếp liên quan đến <TASK-ID>.
Không đọc toàn bộ repository hoặc archived coordination.

Thực hiện task đúng exact file allowlist.

Workflow:
READY_FOR_HANDOFF -> IN_PROGRESS -> CLAUDE_REVIEW

Trong quá trình triển khai:
- Chỉ sửa file được phép.
- Không tự mở rộng scope.
- Chạy focused tests trước.
- Chỉ chạy full gates sau khi focused tests đã ổn định.
- Không xóa/bỏ qua test để PASS.

Sau khi hoàn thành:

1. Tạo report:
reports/<YYYY-MM-DD>/codex_implementation_<TASK-ID>_<YYYY-MM-DD>.md

2. Report ghi ngắn:
- Task / status
- Files changed
- Implementation
- Architecture/contracts
- Focused tests
- Final gates
- Security
- Blockers
- TODO
- Scope result

3. Cập nhật TASK_COORDINATION_ACTIVE.md.

4. Chuyển:
IN_PROGRESS -> CLAUDE_REVIEW

Không:
- Tự review.
- Tự gán PASS.
- Tự chuyển PO_REVIEW.
- Tự approve.
- Tự close.
- Tự tạo task kế tiếp.
```

---

## 20. Prompt chuẩn cho Claude

```text
Bạn là Claude, Independent Reviewer / Tester của dự án <PROJECT_NAME>.

Chỉ đọc:
- Project Snapshot
- Current Project Status
- Current Next Step
- Task Record <TASK-ID>
- Latest completed task summary nếu có dependency trực tiếp

Không đọc các task đã CLOSED trừ khi có dependency, conflict hoặc audit cụ thể.

Đọc thêm:
- Codex implementation/fix report mới nhất.
- Live source trực tiếp liên quan.
- Tests trực tiếp liên quan.

Không đọc toàn bộ repository hoặc archived coordination.
Không coi Codex report là bằng chứng duy nhất.

Review độc lập:

1. Task implementation.
2. Acceptance Criteria.
3. Definition of Done.
4. Architecture.
5. Security.
6. Regression.
7. Scope.
8. Test quality.

Chỉ tạo temporary probe khi existing source/tests chưa đủ evidence.
Xóa toàn bộ probes trước final gates.
Chạy full gates độc lập trên clean tree.

Kết quả chỉ được là:

PASS
PASS_WITH_TODO
FAIL

Nếu PASS hoặc PASS_WITH_TODO:
CLAUDE_REVIEW -> PO_REVIEW

Nếu FAIL:
CLAUDE_REVIEW -> FIX_LOOP

Tạo report:

reports/<YYYY-MM-DD>/claude_review_<TASK-ID>_<RESULT>_<YYYY-MM-DD>.md

Không:
- Sửa production code.
- Implement Required Fix.
- Approve.
- Close task.
- Tạo task kế tiếp.
```

---

## 21. Prompt chuẩn cho Codex Fix

```text
Bạn là Codex, Fix Implementer cho <TASK-ID>.

Chỉ đọc:
- Current Task Record <TASK-ID>
- Current Project Status
- Current Next Step
- Claude FAIL report mới nhất
- Source/tests trực tiếp liên quan đến Required Fix

Không đọc các task đã CLOSED hoặc report cũ không liên quan.

Chỉ sửa các Required Fix Claude đã chỉ ra.

Không:
- Thêm feature mới.
- Mở rộng scope.
- Đổi architecture ngoài phạm vi fix.
- Xóa test để PASS.

Sau khi fix:

1. Chạy focused regression tests.
2. Chạy final gates.
3. Tạo:
reports/<YYYY-MM-DD>/codex_fix_<TASK-ID>_round<N>_<YYYY-MM-DD>.md
4. Cập nhật TASK_COORDINATION_ACTIVE.md.
5. Chuyển FIX_LOOP -> CLAUDE_REVIEW.

Không tự PASS hoặc approve.
```

---

## 22. Prompt Product Owner

```text
Bạn đang thực hiện Product Owner Review cho <TASK-ID>.

Chỉ đọc:
- Project Snapshot
- Current Project Status
- Current Next Step
- Task Record <TASK-ID>
- Claude review report mới nhất
- Codex report khi cần đối chiếu

Không đọc task CLOSED không liên quan.

Không chạy lại implementation hoặc build nếu Claude evidence đầy đủ.

Kiểm tra:
- Product value
- Acceptance Criteria
- Definition of Done
- Security
- Scope
- Required Fixes
- TODO

Nếu APPROVED:
PO_REVIEW -> PO_APPROVED -> DONE -> CLOSED

Tạo:
reports/<YYYY-MM-DD>/po_review_<TASK-ID>_APPROVED_<YYYY-MM-DD>.md

Không sửa production code.
Không tự tạo task kế tiếp.
```

---

## 23. Quy tắc report theo ngày

Report folder sử dụng:

```text
reports/YYYY-MM-DD/
```

Ví dụ:

```text
reports/2026-08-16/
```

Trong cùng ngày có thể có:

```text
codex_implementation_TASK001_2026-08-16.md
claude_review_TASK001_PASS_2026-08-16.md
po_review_TASK001_APPROVED_2026-08-16.md

codex_implementation_TASK002_2026-08-16.md
claude_review_TASK002_FAIL_2026-08-16.md
codex_fix_TASK002_round1_2026-08-16.md
claude_review_TASK002_round2_PASS_2026-08-16.md
po_review_TASK002_APPROVED_2026-08-16.md
```

Không sử dụng folder ngày để xác định task.

Luôn sử dụng Task ID.

---

## 24. Quy tắc archive

Khi `TASK_COORDINATION_ACTIVE.md` quá lớn:

```text
1. Đóng task hiện tại.
2. Archive active coordination.
3. Tạo active coordination mới.
4. Chỉ giữ summary task CLOSED.
5. Chỉ một active coordination tồn tại.
```

Ví dụ:

```text
TASK_COORDINATION_ARCHIVE_TASK001_TASK010.md
TASK_COORDINATION_ACTIVE.md
```

Archived coordination:

```text
READ-ONLY
```

Chỉ đọc archive khi có:

```text
dependency
conflict
audit
missing contract
historical verification
```

---

## 25. Source Priority

Khi có mâu thuẫn:

```text
1. Live verified source code và tests.
2. TASK_COORDINATION_ACTIVE.md.
3. Latest approved Product Owner decision.
4. Latest Claude review của task hiện tại.
5. Latest Codex implementation/fix report.
6. Archived coordination.
7. Older reports.
```

Không âm thầm trộn hai phiên bản mâu thuẫn.

Phải ghi conflict rõ ràng.

---

## 26. Nguyên tắc quality gate

Không được coi task PASS chỉ vì:

```text
- Code compile.
- Một vài unit test PASS.
- Codex nói đã hoàn thành.
- UI nhìn có vẻ đúng.
```

Task cần evidence phù hợp với phạm vi:

```text
- Format.
- Analyze/Lint.
- Unit tests.
- Integration tests nếu cần.
- Regression tests.
- Build.
- Security checks nếu cần.
- Acceptance Criteria.
- Definition of Done.
```

---

## 27. Nguyên tắc Fix Loop

Fix Loop:

```text
Fix lỗi, không thêm feature.
```

Không:

```text
- Bỏ security.
- Bỏ permission.
- Xóa test.
- Ignore exception để PASS.
- Đổi architecture tùy tiện.
- Refactor unrelated code.
- Thêm module ngoài task.
```

Nếu review FAIL nhiều vòng liên tiếp:

```text
- Dừng mở rộng thay đổi.
- Xác định root cause.
- Kiểm tra task requirement/architecture.
- Escalate lên Project Owner nếu contract không rõ.
```

---

## 28. Khi task đã CLOSED

Sau khi task:

```text
DONE / CLOSED
```

coordination phải trở về:

```text
Current Active Task: NONE
Overall Status: READY_FOR_NEXT_TASK
Next Task: NOT SELECTED
```

Task tiếp theo phải được tạo trong planning step riêng.

Không tự suy đoán task tiếp theo.

---

## 29. Bộ file tối thiểu cho dự án mới

Khuyến nghị tối thiểu:

```text
docs/
├── PROJECT_SOURCE_OF_TRUTH.md
├── REQUIREMENTS.md
├── ARCHITECTURE.md
├── TASK_COORDINATION_ACTIVE.md
└── CODEX_CLAUDE_REVIEW_WORKFLOW_POLICY.md

reports/
└── YYYY-MM-DD/
```

Có thể bổ sung:

```text
SECURITY.md
API_SPEC.md
DATA_MODEL.md
IMPLEMENTATION_PLAN.md
AGENT_RULES.md
```

---

## 30. Nguyên tắc cuối cùng

```text
Codex triển khai.
Claude review độc lập.
Claude không sửa production code.
Codex không tự review.
FAIL phải qua Fix Loop.
PASS chưa phải CLOSED.
Product Owner APPROVED mới đóng task.
Task ID quản lý công việc.
Ngày chỉ quản lý report.
Không đọc lại task CLOSED nếu không có dependency/conflict/audit.
Không mở rộng scope ngoài Task Record.
Không hy sinh security hoặc test integrity để tiết kiệm token.
```

---

## 31. Recommended Default Workflow

```text
Planning
↓
Codex Implementation
↓
Codex Report
↓
Claude Independent Review
↓
PASS?
├── NO → Codex Fix → Claude Re-review
└── YES
      ↓
Product Owner Review
      ↓
Approved
      ↓
DONE / CLOSED
      ↓
Planning task mới
```

---

## 32. Policy Status

```text
Policy Name: Codex + Claude Independent Review Workflow
Purpose: Reusable multi-agent software development workflow
Primary Implementer: Codex
Independent Reviewer: Claude
Final Approver: Product Owner / Project Owner
Report Organization: By date
Work Organization: By Task ID
Recommended Status: ACTIVE
```
