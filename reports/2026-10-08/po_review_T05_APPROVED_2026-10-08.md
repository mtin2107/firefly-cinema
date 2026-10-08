# Product Owner Review — T05 — APPROVED — 08/10/2026

## 1. Thông tin và quyết định

| Trường | Giá trị |
|---|---|
| Dự án | Firefly Cinema |
| Task | **T05 — Quản lý suất chiếu (admin)** |
| Product Owner | Tín |
| PO Decision | **APPROVED** |
| Claude Independent Review | **PASS_WITH_TODO**, vòng 2 — `claude_review_T05_round2_PASS_WITH_TODO_2026-10-08.md` |
| Acceptance Criteria | **8/8 PASS** |
| Definition of Done | **MET** |
| Regression | **7/7 PASS** |
| Required Fixes còn mở | **0**; RF-01 (High) **CLOSED** |
| Open task-level blocking defects | **0** theo tiêu chí nghiệm thu T05; các hạn chế đã được disposition rõ bên dưới |
| Đổi schema / thêm thư viện | **Không / Không** |
| Branch | `task/T05-quan-ly-suat-chieu` |
| Baseline | `a09fe6736d4a5d465e07dfa026b032caf9afe0be` |
| Implementation commits | `214fcaa1ebd41299bd00d69c0b3d76091655061c`, `033e420863775489c3efe80fdb2f25a07f2c6cd5` |
| RF-01 fix commit | `f5fca8d151e214c333a3d1ad5a06a446db85e452` |
| Merge status | **PO_APPROVED / PENDING_MERGE** |

**Quyết định PO ngày 08/10/2026:** Chấp nhận kết quả Claude `PASS_WITH_TODO`, phê duyệt T05 để thực hiện các bước commit/sync/merge theo workflow. PO chốt **phương án B**: lỗi đặt vé trực tiếp cho phim `ended` được **ACCEPT_LATER → T11**, không mở rộng allowlist T05. PO đồng ý các disposition TODO-01 đến TODO-06 ở mục 4.

Việc APPROVED **không** đồng nghĩa đã merge hoặc `DONE/CLOSED`. Chỉ đóng T05 sau khi merge vào `master` được kiểm chứng và file điều phối đã đồng bộ.

## 2. Đối chiếu nghiệm thu kỹ thuật

Claude kiểm tra độc lập sau RF-01:

- **AC-01 → AC-08: 8/8 PASS**; kiểm tra 401/403, luật chồng giờ có cộng 15 phút, suất khác phòng, khóa sửa/xóa suất có vé, seed/restart, luồng tạo phim → suất → đặt vé và tương đương real/mock.
- **RF-01 CLOSED:** cả 9 phim `now_showing` có ít nhất một suất trong từng ngày seed; tổng **99 suất/5 ngày** trên DB sạch; **0 cặp chồng giờ cùng phòng**; `hot_week` trở lại đủ 9 phim.
- Restart thật qua Uvicorn giữ suất admin và booking, không nhân đôi dữ liệu; backend/mock cùng tập suất trên DB/mock sạch và cơ chế repair mock có tính idempotent.
- **Regression 7/7 PASS**; health dùng PhoBERT và frontend build đạt.
- Git scope, forbidden files, secret scan: **PASS** theo report Claude; không đổi schema, không thêm thư viện.
- Chênh lệch **99 suất seed / 79 suất tương lai** trong thời điểm probe là hợp lý: **20 suất ngày 08/10** đã qua giờ bắt đầu khi kiểm tra sau 22:00, không phải mất dữ liệu.

Bằng chứng: `reports/2026-10-08/claude_review_T05_round2_PASS_WITH_TODO_2026-10-08.md` và `reports/2026-10-08/codex_fix_T05_round1_2026-10-08.md`.

## 3. Scope / security / architecture

- Chấp nhận chức năng quản lý suất chiếu, API admin, giao diện real/mock, luật chống chồng giờ và cơ chế seed theo Task Record T05.
- Xác minh phân quyền admin và mã 401/403 theo independent review.
- Không hồi tố cấp quyền sửa `backend/app/routers/bookings.py` hoặc `backend/app/routers/movies.py` trong T05.
- Không thay đổi `models.py`, `seats.py`, `classifier.py`, `normalize()`, `.env`, database thật hay model.
- Các hạn chế không chặn AC/DoD đã được ghi nhận và có nơi xử lý; không được mô tả chúng là đã sửa.

## 4. PO disposition cho 6 TODO của Claude

| ID | Quyết định PO | Nội dung / việc tiếp theo |
|---|---|---|
| **TODO-01** | **ACCEPT_LATER → T11** | Mock `seedBooked()` khiến 79/79 suất seed tương lai bị coi như có vé và admin mock không thể sửa/xóa chúng. Kiểm tra và đồng bộ hành vi mock/real khi thực hiện kiểm thử tự động T11. |
| **TODO-02** | **ACCEPT — KNOWN UX LIMITATION** | Form sửa suất của phim `ended` hiện ô Phim trống, trong khi backend không cho cập nhật suất thuộc phim đã kết thúc. Chấp nhận giới hạn UX hiện tại trong phạm vi T05; không yêu cầu sửa ngay. |
| **TODO-03** | **ACCEPT_LATER → T11** | Hàm `find_showtime_conflict()` hiện duyệt toàn bộ suất cùng phòng thay vì giới hạn khung ngày. T11 đánh giá/kiểm tra tối ưu hóa khi cần, không đánh đổi tính đúng đắn và luật 15 phút. |
| **TODO-04** | **RESOLVED / CLOSED** | Thiếu sót evidence ban đầu của Codex đã được khắc phục bằng fix report và kiểm tra độc lập: phân bổ theo phim/ngày, restart, DB cũ, mock repair. Ghi rõ `99 − 20 = 79` do mốc giờ probe. |
| **TODO-05** | **ACCEPT_LATER → T11 — PRIORITY BEFORE DEMO** | Suất seed đã được admin xóa có thể sinh lại sau restart (ví dụ #61 → #101). Đây là hạn chế nghiệp vụ hiện hữu, **chưa được sửa**. T11 phải xác định hành vi mong đợi và giải pháp ngăn tái tạo suất đã xóa, kiểm thử restart; nếu cần đổi schema/phạm vi, phải xin quyết định PO trước. Không được coi việc xóa suất seed là bền vững cho đến khi sửa. |
| **TODO-06** | **ACCEPT_WITH_NOTES → T12 (DEMO DATA)** | Phân bổ suất chưa đều (một số phim chỉ có 1 suất/ngày); DB cũ từ trước T05 chứa **190 cặp chồng giờ** mà seed không tự sửa. T12 chuẩn bị dữ liệu/kịch bản demo sạch, kiểm tra lịch và hot week. Nếu cần reset DB demo, phải sao lưu và xác nhận đúng DB trước; **không tự ý xóa `backend/firefly.db` đang sử dụng**. |

Các TODO trên **được PO disposition**, không đồng nghĩa toàn bộ đã giải quyết về mặt kỹ thuật. T11/T12 phải tiếp nhận ở bước planning/authorization của chính task đó.

## 5. Quyết định PO đối với T04 TODO-07 — booking phim `ended`

**PO Decision: B — ACCEPT_LATER → T11.**

- **Tình trạng hiện tại: OPEN / KNOWN BUSINESS LOGIC ISSUE**, không được ghi `RESOLVED`.
- Claude đã chứng minh `POST /api/bookings` trực tiếp vẫn có thể tạo vé (`201`) cho suất tương lai của phim đã chuyển `ended`; UI ẩn lịch không đủ để chặn API.
- Mức ảnh hưởng theo Claude: **nghiệp vụ trung bình, bảo mật thấp**; không vi phạm AC/DoD của T05 đã được phê duyệt.
- **T11 cần sửa tại nguồn** ở booking backend và đối chiếu mock, kiểm thử cả tình huống truy cập API trực tiếp/giữ link cũ. Kỳ vọng booking suất thuộc phim `ended` bị từ chối bằng mã 4xx và thông báo tiếng Việt rõ ràng; chi tiết hợp đồng và allowlist của T11 sẽ được duyệt trong planning T11.
- PO chấp nhận rủi ro tạm thời tới T11; **không mở rộng T05, không có FIX_LOOP bổ sung vì mục này**.

## 6. PO Final Approval / Merge Readiness

**PO APPROVED — 08/10/2026.**

Các gate cần xác minh ở repo trước merge:

1. Báo cáo Claude vòng 2, fix commit và báo cáo PO đều hiện diện, đúng nhánh T05; coordination ghi **T05 `PO_APPROVED / PENDING_MERGE`**, không ghi `DONE/CLOSED` trước merge.
2. `git status` sạch sau commit; `git diff --check master...HEAD` PASS; diff thuộc allowlist/những report đúng workflow; không có secrets, DB, model hoặc forbidden files.
3. Chỉ **Tín (PO)** thực hiện merge nhánh `task/T05-quan-ly-suat-chieu` vào `master`.
4. Sau merge: xác minh merge commit và toàn bộ nhánh T05 nằm trong lịch sử `master`; cập nhật `docs/TASK_COORDINATION_ACTIVE.md` thành **T05 DONE/CLOSED**, `Current Active Task: NONE`, `Overall Status: READY_FOR_NEXT_TASK`, `Next Task: NOT SELECTED`; commit closure-sync riêng.

**T05 hiện tại: PO_APPROVED / PENDING_MERGE**, không phải DONE/CLOSED. **T06 vẫn PLANNED, Q2 còn OPEN**. Task tiếp theo chỉ được chọn/authorize bằng bước planning riêng sau closure của T05.

## 7. PO xác nhận

- Người phê duyệt: **Tín — Product Owner**.
- Quyết định được PO xác nhận trong cuộc trò chuyện ngày **08/10/2026**: chọn phương án B (đưa lỗi booking phim `ended` sang T11), đồng ý toàn bộ TODO disposition được đề xuất cho T05 và yêu cầu chuẩn bị PO approval.
- Kết luận: **APPROVED, WITH DOCUMENTED DEFERRED ITEMS**; không còn Required Fix chặn nghiệm thu T05.
