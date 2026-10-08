# Product Owner Review — T04 — APPROVED — 08/10/2026

## 1. Quyết định

| Mục | Kết quả |
|---|---|
| Task | T04 — Quản lý phim (admin) |
| Product Owner | Tín |
| PO Decision | **APPROVED** |
| Claude Review | **PASS_WITH_TODO** |
| Acceptance Criteria | **7/7 PASS** |
| Required Fixes | **0** |
| Technical Blockers | **0** |
| Definition of Done | **ACCEPTED BY PO**, với hai ngoại lệ scope SD-01 và SD-02 đã được phê duyệt hồi tố |
| Baseline | `b6cc3d677a5e748ed4818ce111967bfa234e9edb` |
| Implementation commit | `d8e67e0484afa4e6fe3e085c365c3de1ae2d33ed` |
| Claude review commit | `e9fb143` |

Review độc lập: `reports/2026-10-08/claude_review_T04_2026-10-08.md`.

## 2. Scope deviations và quyết định PO

Hai scope deviation đã thực sự tồn tại trong implementation và được Claude ghi nhận. PO không xóa hoặc phủ nhận lịch sử này.

### SD-01 — APPROVED RETROACTIVELY

- `frontend/src/utils/taxonomy.js` đã được sửa dù không nằm trong Allowed Files của Task Record T04.
- Thay đổi tách các nhãn taxonomy thành export dùng chung cho trang quản trị và mock.
- Claude xác minh các export/menu baseline và bản mới giữ nguyên hành vi, thứ tự và slug.
- PO chấp nhận hồi tố thay đổi này vì giúp frontend có một nguồn taxonomy duy nhất và không gây regression.

### SD-02 — APPROVED RETROACTIVELY

- `frontend/src/styles/global.css` không chỉ thêm class mới mà còn mở rộng một số rule có sẵn và điều chỉnh `.container`/`.page-title` trên màn hình nhỏ.
- Claude xác minh giao diện 375px, đăng nhập/đăng ký và các trang liên quan không bị regression.
- PO chấp nhận hồi tố thay đổi này trong phạm vi T04.

Hai approval trên là ngoại lệ scope có chủ đích cho T04, không thay đổi quy tắc allowlist của các task sau.

## 3. Acceptance Criteria

| AC | Kết quả |
|---|---|
| AC-01 — 401/403 cho toàn bộ endpoint admin movies | PASS |
| AC-02 — Validation 422, một câu tiếng Việt nêu đúng ô | PASS |
| AC-03 — Phim có vé trả 409; chuyển `ended` thành công | PASS |
| AC-04 — Trang chủ, lọc thể loại, tìm không dấu | PASS |
| AC-05 — Mock CRUD và persistence sau F5 | PASS |
| AC-06 — Loading/empty/error và responsive 375px | PASS |
| AC-07 — Regression checklist | PASS |

Kết luận: **7/7 PASS**.

## 4. Required Fixes và blockers

- Required Fixes: **0**.
- Technical Blockers: **0**.
- Không yêu cầu FIX_LOOP.

## 5. TODO dispositions

| ID | Quyết định PO | Nội dung |
|---|---|---|
| TODO-01 | **DOCUMENTED / PROCESS CORRECTION** | Report Codex đã ghi sai rằng toàn bộ file nằm trong allowlist. SD-01 đã được ghi nhận và phê duyệt hồi tố; từ T05 phải đối chiếu allowlist chính xác trước handoff. |
| TODO-02 | **ACCEPT_LATER — DOCUMENTATION** | Canonical là 22 thể loại thật; menu có 23 mục vì gồm “Phim 18+” là bộ lọc tuổi. Sửa câu chữ tài liệu khi cập nhật kế hoạch, không đổi code T04. |
| TODO-03 | **ACCEPT_LATER → T11** | Chuẩn hóa hoàn toàn thông báo 422 cho trường thiếu, sai kiểu hoặc trường thừa sang tiếng Việt. |
| TODO-04 | **ACCEPT_LATER → T11** | Bổ sung kiểm tra tổng độ dài chuỗi `genre` phù hợp giới hạn cột hiện tại, không đổi schema trong T04. |
| TODO-05 | **ACCEPT** | Chấp nhận việc xóa phim chưa có vé sẽ xóa bình luận liên quan để không để dữ liệu mồ côi. |
| TODO-06 | **WONT_FIX** | Mock giữ câu 422 tiếng Việt nhưng không bắt buộc tiền tố trường giống tuyệt đối backend; mã lỗi và cấu trúc lỗi vẫn tương thích. |
| TODO-07 | **ACCEPT_LATER → T05** | Quản lý suất chiếu cho phim mới và quy tắc suất tương lai của phim `ended` thuộc T05. |
| TODO-08 | **WONT_FIX** | Mock reset booking khi sang ngày là hành vi demo có từ trước; không ảnh hưởng AC T04. |

## 6. Definition of Done

PO chấp nhận Definition of Done của T04:

- Chức năng, phân quyền, validation, mock, responsive và regression đạt.
- Không đổi schema, không sửa Forbidden Files, không thêm thư viện.
- SD-01 và SD-02 được **APPROVED RETROACTIVELY** như hai ngoại lệ scope đã ghi rõ ở mục 2.
- RF 0, technical blocker 0.

## 7. Merge readiness

- Branch: `task/T04-quan-ly-phim`.
- Baseline đúng: `b6cc3d677a5e748ed4818ce111967bfa234e9edb`.
- Implementation commit đúng: `d8e67e0484afa4e6fe3e085c365c3de1ae2d33ed` và nằm trong lịch sử branch.
- Claude review: PASS_WITH_TODO tại commit `e9fb143`.
- `git diff --check master...HEAD`: PASS.
- Không có file dữ liệu, model, secrets hoặc Forbidden Files trong diff.
- Working tree sạch trước khi tạo report PO.

T04 ở trạng thái **PO_APPROVED — PENDING_MERGE**. Chỉ PO thực hiện merge; chưa được ghi `DONE/CLOSED` cho tới khi có bằng chứng merge thật trên `master` và coordination được đồng bộ.

## 8. PO approval

**APPROVED — 08/10/2026**

PO chấp nhận T04 để merge vào `master`, bao gồm hai scope deviation SD-01 và SD-02 đã được phê duyệt hồi tố cùng các TODO disposition ở trên.
