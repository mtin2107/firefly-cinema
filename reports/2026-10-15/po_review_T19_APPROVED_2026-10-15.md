# Product Owner Review — T19 Tải ảnh poster từ máy khi thêm/sửa phim

- **Task:** T19 — Tải ảnh poster từ máy khi thêm/sửa phim
- **Ngày quyết định:** 15/10/2026
- **Approver:** Tín (Product Owner)
- **PO Decision:** **APPROVED**
- **Task branch:** `task/T19-tai-anh-poster`
- **Claude result:** **PASS_WITH_TODO**
- **Acceptance Criteria:** **11/11 PASS**
- **Required Fixes:** **0**
- **Git disposition:** `PO_REVIEW → PO_APPROVED / PENDING_MERGE`
- **Merge status:** **PENDING** cho tới khi PO trực tiếp merge và xác minh trên `master`

## 1. Evidence được PO chấp nhận

- Claude Independent Review: `reports/2026-10-14/claude_review_T19_PASS_WITH_TODO_2026-10-14.md` — **PASS_WITH_TODO**, AC 11/11 PASS, Required Fixes 0, TODO-01..04 (Low), OBS-01..04, blocker 0.
- Gate độc lập: focused pytest 16/16 PASS, full pytest 65/65 PASS, probe 6/6 PASS và đã xóa, compileall/build exit 0, health dùng `phobert_b`, real mode + mock mode PASS, hồi quy 7/7 PASS.
- PO Tín đã tự chạy thử ngày 15/10/2026: thêm phim bằng ảnh từ máy, sửa poster và chọn file sai được báo lỗi — **ĐẠT**.
- Không đổi schema, không thêm thư viện; database thật không bị tác động trong quá trình review.

## 2. Acceptance Criteria và Required Fixes

| Nội dung | Kết quả PO |
|---|---|
| AC-01 đến AC-11 | **11/11 PASS — ACCEPTED** |
| Required Fix mở | **0** |
| Blocker cản closure | **Không còn** |

## 3. TODO và Observation Disposition

| Mục | PO disposition | Ghi chú |
|---|---|---|
| TODO-01 | **ACCEPT_LATER — Future Backlog** | Giới hạn `max_length` cho body upload poster. Chỉ admin gọi được nên rủi ro thấp; ghi vào hạn chế của khóa luận. |
| TODO-02 | **ACCEPT_LATER — Future Backlog** | File poster mồ côi khi upload thành công nhưng lưu phim thất bại. Không chặn T19. |
| TODO-03 | **WONT_FIX** | Chỉ chênh lệch câu chữ/regex phía client; backend đã chặn đúng dữ liệu không hợp lệ. |
| TODO-04 | **ACCEPT_LATER — Future Backlog** | Bổ sung assertion `status_code` và độ phủ PUT trong đợt test sau. Không chặn T19. |
| OBS-01 | **ACCEPT_LATER — khi deploy** | Chỉ cần hardening static upload khi triển khai; Q4 mặc định chạy trên máy khi bảo vệ. |
| OBS-02 | **WONT_FIX** | Chỉ ảnh hưởng mock/demo do giới hạn localStorage. |
| OBS-03 | **RESOLVED IN THIS COMMIT** | Đưa `docs/tasks/T19.md` vào Git trong commit đóng T19. |
| OBS-04 | **WONT_FIX** | Hành vi email `.test` có từ trước, không thuộc T19. |

Toàn bộ TODO-01 đến TODO-04 và OBS-01 đến OBS-04 đã có PO disposition. Không mục nào yêu cầu quay lại FIX_LOOP.

## 4. Scope và conflict check

- Quyết định này không phê duyệt thêm tính năng, dependency, thay đổi schema hoặc production-code change.
- TODO-01 được ghi nhận là hạn chế khóa luận vì endpoint chỉ dành cho admin; TODO-02 và TODO-04 vào Future Backlog; OBS-01 chỉ xử lý nếu triển khai.
- `docs/tasks/T19.md` được đưa vào Git theo quyết định OBS-03.
- Các cập nhật lộ trình cuối ngày 15/10/2026 cho T12–T15, T20, T21 và hai báo cáo audit được giữ nguyên trong commit tài liệu này theo chỉ đạo PO.

## 5. Final Transition

**Decision: APPROVED.**

1. T19 chuyển `PO_REVIEW → PO_APPROVED`; hồ sơ task được ghi nhận **DONE / CLOSED (chờ merge)**.
2. Product Owner trực tiếp merge nhánh `task/T19-tai-anh-poster` vào `master` theo `AGENT_RULES.md`.
3. Không tag và không merge trong bước ghi nhận approval này.
4. Sau khi merge T19, T20 là task web kế tiếp; T15 được phép bàn giao song song theo luồng ML/Colab.

## 6. PO Authorization Record

PO Tín xác nhận trực tiếp ngày 15/10/2026: đã tự chạy thử thêm phim bằng ảnh từ máy, sửa poster và chọn file sai được báo lỗi — **đạt**; quyết định T19 **APPROVED**. TODO-01, TODO-02, TODO-04 và OBS-01 là **ACCEPT_LATER** theo phạm vi nêu trên; TODO-03, OBS-02 và OBS-04 là **WONT_FIX**; OBS-03 được xử lý bằng cách commit `docs/tasks/T19.md`. Merge vẫn **PENDING** và do PO trực tiếp thực hiện.
