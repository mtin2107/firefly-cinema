# Product Owner Review — T06 — APPROVED — 09/10/2026

## 1. Thông tin và quyết định

| Trường | Giá trị |
|---|---|
| Dự án | Firefly Cinema |
| Task | **T06 — Kiểm duyệt có người duyệt** |
| Product Owner | Tín |
| PO Decision | **APPROVED — WITH DOCUMENTED DEFERRED ITEMS** |
| Claude Independent Review | **PASS_WITH_TODO**, Round 2, ngày 09/10/2026 |
| Review evidence | `reports/2026-10-09/claude_review_T06_round2_PASS_WITH_TODO_2026-10-09.md` |
| Acceptance Criteria | **8/8 PASS** |
| Regression | **7/7 PASS** |
| Focused RF-01 / Full API probes | **10/10** / **52/52 PASS** |
| Required Fixes còn mở | **0** — RF-01 (Medium) **CLOSED / VERIFIED BY CLAUDE** |
| Open blocking defects | **0** theo phạm vi nghiệm thu T06 |
| Definition of Done | **MET ở mức phê duyệt PO**, chờ hoàn tất merge/closure Git |
| Q2 | **RESOLVED — NO ALEMBIC / BACKUP_BEFORE_RESET** |
| Branch | `task/T06-kiem-duyet` |
| Implementation commit | `942d7197ed5c104e6267446866822c2a2b165401` |
| Fix commit | `8ef57ad4115d877aea14a19b706665a0b405a167` |
| Merge status | **PO_APPROVED / PENDING_MERGE** (chưa xác nhận merge) |

**Quyết định PO ngày 09/10/2026:** Phê duyệt kết quả T06 theo Claude Round 2 `PASS_WITH_TODO`. Chấp nhận và định hướng xử lý cả sáu TODO như mục 4. Cho phép ghi báo cáo phê duyệt, đồng bộ điều phối và chuẩn bị merge nhánh T06 vào `master` sau khi kiểm tra các gate Git. Quyết định này do PO đưa ra; Codex chỉ hỗ trợ ghi chép/commit theo chỉ thị, không tự phê duyệt.

**APPROVED không đồng nghĩa DONE/CLOSED.** Chỉ đóng T06 khi PO đã merge và xác minh toàn bộ lịch sử nhánh nằm trong `master`, sau đó hoàn tất closure-sync trong file điều phối.

## 2. Căn cứ nghiệm thu

- Claude Round 2 xác nhận **RF-01 CLOSED**: `AdminCommentAction.validate_action` kiểm tra `isinstance(value, str)` trước phép membership. Mười payload sai kiểu/giá trị trả **HTTP 422** với thông báo tiếng Việt, dữ liệu không đổi; bốn action hợp lệ vẫn hoạt động.
- **AC-01 → AC-08: 8/8 PASS**; giữ nguyên `is_negative`, `negative_score`, `model_name`; ưu tiên `human_label`, hide/unhide đúng; TP/FP/TN/FN và accuracy đúng; CSV UTF-8 BOM có đúng `text,text_norm,label` và `normalize()` parity; admin 401/403; phân trang; real/mock nhất quán.
- **Regression: 7/7 PASS**; API probes **52/52 PASS**; backend compile, health PhoBERT, frontend build, scope và secret scan đều PASS theo review độc lập.
- **Database/schema safety: PASS**. Backup trước T06 giữ nguyên checksum; reset/seed theo quyết định Q2 đã hoàn thành; Claude Round 2 chỉ ghi trên DB tạm/bản copy và không thay đổi DB thật/backup. Không cần reset lại khi merge.
- Review xác nhận không có sửa đổi trái allowlist, không đổi classifier, `normalize()`, model hoặc thư viện.

Evidence bổ sung: `reports/2026-10-09/claude_review_T06_FAIL_2026-10-09.md`; `reports/2026-10-09/codex_fix_T06_round1_2026-10-09.md`; `reports/2026-10-08/codex_implementation_T06_2026-10-08.md`.

## 3. Architecture, security, scope

- Chấp nhận thay đổi schema bảng `comments` và chức năng kiểm duyệt, thống kê, xuất CSV theo Task Record T06.
- Phân quyền `require_admin` và hợp đồng API real/mock đã được Claude kiểm chứng.
- Không thêm thư viện mới; không sửa `backend/app/classifier.py`, `backend/app/seats.py`, `normalize()` hay model.
- Không commit `.env`, `firefly.db`, `backup/`, model, dữ liệu lớn.
- Rủi ro CSV formula injection vẫn **OPEN** và được chuyển T11, không được ghi thành đã sửa hoặc chấp nhận an toàn tuyệt đối.

## 4. PO disposition — 6 TODO của Claude

| ID | Quyết định PO | Nội dung và hành động tiếp theo |
|---|---|---|
| **TODO-01** | **ACCEPT_LATER → T11** | Chuẩn hóa thông báo lỗi 422 do handler chung/Pydantic còn phần tiếng Anh; kiểm tra các payload thiếu trường, sai kiểu, JSON lỗi. |
| **TODO-02** | **ACCEPT_LATER → T11** | Đồng bộ validation trong mock với real: `admin.comments.list` phải xử lý bộ lọc `label`/`reviewed` không hợp lệ nhất quán. |
| **TODO-03** | **ACCEPT_LATER → T11 / RISK ACKNOWLEDGED** | Xử lý rủi ro **CSV formula injection** trước demo/sử dụng CSV trong Excel. Bảo toàn `text` gốc phục vụ huấn luyện T03/T09; nếu cần, tách định dạng export an toàn cho bảng tính khỏi dữ liệu train thay vì âm thầm sửa nội dung nhãn/text. Chưa sửa trong T06. |
| **TODO-04** | **ACCEPT_LATER → T12** | Điều chỉnh câu chữ hiển thị khi bình luận bị ẩn do nhãn của model hoặc do quyết định admin; không mở rộng T06. |
| **TODO-05** | **ACCEPT_LATER → T12** | Dữ liệu test được Codex tạo trên DB thật mới (1 booking/2 ghế, 1 bình luận thử, 4 nhãn duyệt). Trong T12 xác định và làm sạch dữ liệu demo theo quy trình có backup/xác minh, không tùy tiện xóa DB hiện hành. |
| **TODO-06** | **ACCEPT_WITH_NOTES** | Chấp nhận `docs/tasks/T06.md` còn header `PLANNED` như snapshot chưa đồng bộ; file điều phối là nguồn trạng thái vận hành. Không yêu cầu thêm thao tác bỏ duyệt hoặc audit hide/unhide vì ngoài spec T06. Nếu đồng bộ metadata Task Record, PO duyệt một thay đổi tài liệu riêng theo governance. |

Tất cả TODO đã được PO disposition, nhưng TODO-01→05 **chưa được xử lý kỹ thuật**. T11/T12 cần tiếp nhận ở planning của từng task; không mở rộng fix loop T06 để làm các TODO này.

## 5. Phê duyệt và kiểm tra trước merge

**PO APPROVED — 09/10/2026.** Cho phép chuẩn bị merge T06 vào `master` khi các điều kiện sau được xác minh:

1. Đúng nhánh `task/T06-kiem-duyet`, working tree sạch; report Claude Round 2 và bản PO approval hiện diện, đã commit; coordination phản ánh **T06 `PO_APPROVED / PENDING_MERGE`**, T07 **`PLANNED / NOT AUTHORIZED`**.
2. `git diff --check master...HEAD` PASS; toàn bộ diff chỉ chứa file thuộc T06/role-based report và coordination hợp lệ; không chứa secrets, database/backup, model hay file ngoài scope.
3. Commit triển khai, fix, Claude review và PO report là ancestor của tip nhánh T06; `master` chứa baseline T05 hợp lệ và không có thay đổi chưa xét.
4. **Chỉ PO (Tín)** thực hiện merge; không force/reset lịch sử. Nếu phát sinh xung đột Git, dừng để đánh giá, không tự chọn cách ghi đè.
5. Sau merge, xác minh tip nhánh T06 nằm trong lịch sử `master`; tạo closure-sync riêng trên `master`: `T06 DONE / CLOSED`, `Overall Status READY_FOR_NEXT_TASK`, `Current Active Task NONE`, `Next Task NOT SELECTED`; T07 vẫn chưa authorize.

## 6. PO xác nhận

- Người quyết định: **Tín — Product Owner**.
- Ngày: **09/10/2026**.
- Xác nhận được cung cấp trực tiếp trong cuộc trò chuyện: **“PO APPROVED T06. Tôi chấp nhận cả 6 TODO disposition theo đề xuất.”**
- Final decision: **APPROVED — WITH DOCUMENTED DEFERRED ITEMS / PENDING_MERGE**.
- Không yêu cầu sửa production code trong bước PO approval.
