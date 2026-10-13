# Product Owner Review — T18 Chuyển động và hiệu ứng 3D

- **Task:** T18 — Chuyển động và hiệu ứng 3D
- **Ngày quyết định:** 13/10/2026
- **Approver:** Tín (Product Owner)
- **PO Decision:** **APPROVED**
- **Aesthetic Approval:** **ĐẠT**
- **Task branch:** `task/T18-giao-dien-chuyen-dong`
- **Codex result:** **PASS_WITH_TODO** — Round 3
- **Claude RF-04 result:** **PASS**
- **Acceptance Criteria:** **11/11 PASS**
- **Required Fixes:** **0 open; RF-01 đến RF-04 CLOSED**
- **Git disposition:** `PO_REVIEW → PO_APPROVED / PENDING_MERGE`
- **Merge status:** **PENDING** cho tới khi PO trực tiếp merge và xác minh trên `master`

## 1. Evidence được PO chấp nhận

- Codex Round 3: `reports/2026-10-13/codex_review_T18_round3_PASS_WITH_TODO_2026-10-13.md` — **PASS_WITH_TODO**, AC 11/11 PASS, RF-01 đến RF-04 CLOSED.
- Claude RF-04: `reports/2026-10-13/claude_review_T18_RF04_PASS_2026-10-13.md` — **PASS**, không có Required Fix mới.
- Fix RF-04: commit `490ac8aeaf2ebcb41c38b8226a596b3958235479` là ancestor của HEAD; PosterIntro được portal vào `document.body` mà không sửa `route-fade` hoặc thêm dependency.
- M4 hiện hành đã được PO thay đổi: hủy Poster Flight và giữ PosterIntro. Đây là đặc tả được nghiệm thu.
- PO đã chạy thử và xác nhận trực tiếp thẩm mỹ **ĐẠT**.

## 2. Acceptance Criteria và Required Fixes

| Nội dung | Kết quả PO |
|---|---|
| AC-01 đến AC-11 | **11/11 PASS — ACCEPTED** |
| RF-01 | **CLOSED / ACCEPTED** |
| RF-02 | **CLOSED / ACCEPTED** |
| RF-03 | **CLOSED / ACCEPTED** |
| RF-04 | **CLOSED / ACCEPTED** — Codex và Claude đã xác minh độc lập |
| Required Fix mở | **0** |
| Blocker cản closure | **Không còn** |

## 3. TODO và Observation Disposition

| Mục | PO disposition | Ghi chú |
|---|---|---|
| TODO-01 | **WONT_FIX** | PO chấp nhận quyết định D2 bỏ `translateZ` nhẹ cho tên phim MovieCard; thẩm mỹ hiện tại đạt. |
| TODO-02 | **WONT_FIX** | PO chấp nhận quyết định D5 dùng `translateY(-3px) scale(1.06)` thay `translateZ` cho ghế chọn; hit-test và thẩm mỹ đạt. |
| TODO-03 | **ACCEPT_LATER (T13)** | Chuẩn hóa bằng chứng baseline bundle và thông tin môi trường build để tăng khả năng tái lập trong T13. Không chặn merge/closure T18. |
| OBS-01 | **ACCEPT_LATER — future backlog** | Reduced-motion có thể render PosterIntro khoảng 1–2 frame trước khi effect gỡ. Không do RF-04, không chặn T18; chưa tạo hoặc authorize task mới. |

Toàn bộ TODO-01 đến TODO-03 và OBS-01 đã có PO disposition. Không mục nào yêu cầu quay lại FIX_LOOP.

## 4. Scope và conflict check

- Không có conflict về đặc tả hiện hành: `docs/tasks/T18.md` ghi rõ M4 đã hủy theo PO và giữ PosterIntro; evidence Codex/Claude cùng kiểm theo đặc tả này.
- Có một lệch hành chính không chặn: trường `Current Status` trong `docs/tasks/T18.md` vẫn ghi `CODEX_REVIEW`, trong khi coordination và evidence đã chuyển qua `PO_REVIEW`. PO sync này không sửa Task Record hoặc thay đổi đặc tả; trạng thái vận hành lấy từ `docs/TASK_COORDINATION_ACTIVE.md`.
- Không phê duyệt thêm tính năng, dependency hoặc production-code change qua quyết định này.

## 5. Final Transition

**Decision: APPROVED.**

1. T18 chuyển `PO_REVIEW → PO_APPROVED / PENDING_MERGE`.
2. Product Owner trực tiếp merge nhánh `task/T18-giao-dien-chuyen-dong` vào `master` theo `AGENT_RULES.md`.
3. Chỉ sau khi merge và xác minh thành công mới cập nhật T18 thành `DONE / CLOSED`.
4. Không tự tag hoặc mở task tiếp theo trong bước approval này.

## 6. PO Authorization Record

PO xác nhận trực tiếp ngày 13/10/2026: T18 **APPROVED**, thẩm mỹ **ĐẠT**; TODO-01 và TODO-02 là **WONT_FIX**; TODO-03 là **ACCEPT_LATER (T13)**; OBS-01 là **ACCEPT_LATER** trong future backlog. Merge vẫn **PENDING** và do PO trực tiếp thực hiện.
