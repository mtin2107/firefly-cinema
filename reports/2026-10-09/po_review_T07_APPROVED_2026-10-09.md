# PO Review — T07 — APPROVED — 09/10/2026

| Trường | Giá trị |
|---|---|
| Task | T07 — Đa mô hình và trang So sánh mô hình |
| Branch | `task/T07-da-mo-hinh` |
| PO / Approver | Tín |
| Claude Round 2 | `PASS_WITH_TODO` |
| Quyết định PO | **APPROVED** |
| Trạng thái workflow | `PO_APPROVED / PENDING_MERGE` |
| Đổi schema | Không |

## 1. Quyết định

PO chấp nhận kết quả review độc lập Round 2:

- AC 8/8 PASS.
- Definition of Done: MET.
- RF-01 CLOSED / VERIFIED BY CLAUDE.
- Open Required Fixes: 0.
- Blockers: 0.
- Hồi quy 7/7 và các gate compile/startup/health/build/scope/secret đạt.

T07 được **APPROVED** và sẵn sàng để PO merge vào `master`. Approval này không đồng nghĩa task đã merge hoặc CLOSED.

## 2. Evidence được chấp nhận

- Implementation: `e84820d`.
- Implementation handoff: `6a56818`.
- Claude Round 1 FAIL: `4002b12`.
- RF-01 fix: `06fbd3d`.
- Fix handoff: `ebc699a`.
- Claude Round 2 PASS_WITH_TODO: `d5c71ea`.
- Review report: `reports/2026-10-09/claude_review_T07_round2_PASS_WITH_TODO_2026-10-09.md`.
- Fix report: `reports/2026-10-09/codex_fix_T07_round1_2026-10-09.md`.

## 3. TODO disposition

| TODO | Quyết định PO | Ghi chú |
|---|---|---|
| TODO-01 | **ACCEPT_LATER → T08/T09/T10** | Giữ checkpoint backend hiện tại. Dùng T08 đo lệch miền, T09 train/so sánh model B và T10 quyết định model runtime; không thay checkpoint trong T07. |
| TODO-02 | **ACCEPT_LATER → T11** | Cô lập exception theo từng model trong endpoint predict. |
| TODO-03 | **ACCEPT_LATER → T11** | Rút gọn/ẩn lỗi thô và đường dẫn tuyệt đối trong health. |
| TODO-04 | **ACCEPT_LATER → T11** | Chuẩn hóa thêm lỗi Pydantic ngoài phạm vi RF-01. |
| TODO-05 | **ACCEPT_LATER → T10** | Cân nhắc trường model được yêu cầu khi `ACTIVE_MODEL` fallback. |
| TODO-06 | **ACCEPT_WITH_NOTES** | Chấp nhận sai sót evidence ban đầu; fix report và Claude Round 2 đã kiểm đủ ca `text=""`. Các task sau phải kiểm đủ ca biên trước khi ghi AC PASS. |

Không TODO nào chặn merge T07. TODO được disposition nhưng chưa được coi là resolved cho tới task đích tương ứng.

## 4. Security, scope và dữ liệu

- Endpoint admin giữ 401/403; input rỗng đã trả 422 tiếng Việt; giới hạn 1.000 ký tự giữ nguyên.
- Không đổi database schema, `normalize()`, `_ABBR`, checkpoint backend hoặc artifact.
- Không commit `.env`, database, model hay dữ liệu lớn.
- Scope T07 và Fix Loop đúng allowlist; working tree sạch trước PO report.

## 5. Merge readiness

- `master` là ancestor của tip T07 tại thời điểm PO review.
- `git diff --check master...task/T07-da-mo-hinh`: PASS.
- T07 ở trạng thái **PO_APPROVED / PENDING_MERGE**.
- PO thực hiện merge và tag theo workflow; Codex không tự merge hoặc tag.

Lệnh chuẩn bị cho PO:

```powershell
git checkout master
git merge task/T07-da-mo-hinh
git tag admin-v1
```

Sau merge, cần xác minh commit merge chứa toàn bộ lịch sử T07 rồi mới cập nhật T07 thành `DONE / CLOSED`.

## 6. Task kế tiếp

T08 giữ **PLANNED / NOT AUTHORIZED**. Không mở, không tạo branch và không bắt đầu T08 cho tới khi T07 hoàn tất closure và PO có ủy quyền riêng.
