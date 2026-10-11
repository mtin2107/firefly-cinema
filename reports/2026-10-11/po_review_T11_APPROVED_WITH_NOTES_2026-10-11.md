# PO Review T11 — APPROVED_WITH_NOTES

- Task: T11 — Kiểm thử tự động và sửa lỗi
- Ngày quyết định: 11/10/2026
- Decision Authority: Tín (PO), xác nhận trực tiếp trong ChatGPT ngày 11/10/2026
- Loại bản ghi: ghi nhận quyết định PO đã có; Codex không tự đưa ra quyết định phê duyệt
- Branch: `task/T11-kiem-thu`
- Claude Final: **PASS_WITH_TODO** tại review commit `8b677daf74bbd8c521e7bcd1e08df37095571e5b`
- PO Decision: **APPROVED_WITH_NOTES**
- Merge status: **PENDING_PO_MERGE** — chỉ PO được merge vào `master`

## 1. Kết quả được PO chấp nhận

| Hạng mục | Kết quả |
|---|---|
| Acceptance Criteria | **6/6 PASS** |
| Pytest | **28/28 PASS** |
| Browser Regression | **7/7 PASS** |
| Technical Definition of Done | **MET** |
| RF-01 | **CLOSED** |
| RF-02 | **CLOSED** |
| RF-03 | **CLOSED** |
| Required Fix mở | **0** |
| Claude Round 3 | **PASS_WITH_TODO** |

Các kết quả trên là kết luận Claude Round 3 được PO chấp nhận, không phải Codex tự review hoặc tự nâng trạng thái PASS.

## 2. PO AUTHORIZED SCOPE EXCEPTION

PO cho phép ngoại lệ scope duy nhất trước merge: thêm đúng dòng sau vào `.gitignore`:

```gitignore
/backend/*.db.showtime-seed.json
```

Trạng thái: **PO AUTHORIZED SCOPE EXCEPTION — VERIFIED**.

Evidence:

- Diff `.gitignore`: đúng `1 insertion, 0 deletion`; không thay đổi rule khác.
- `git check-ignore -v backend/firefly.db.showtime-seed.json` trả rule `.gitignore:7:/backend/*.db.showtime-seed.json`.
- Không tạo, xóa, kết nối hoặc thay đổi database thật.
- Không thay đổi production code, tests, model, schema hoặc `normalize()` sau HEAD Claude review.

## 3. TODO disposition của PO

| ID | Disposition | Ghi chú |
|---|---|---|
| TODO-R3-01 | **RESOLVED_BEFORE_MERGE** | Rule `/backend/*.db.showtime-seed.json` đã được thêm và xác minh bằng `git check-ignore -v` theo scope exception của PO |
| TODO-R3-02 | **ACCEPT_WITH_DISCLOSURE → T13** | Backup/restore DB và sidecar phải cùng snapshot; mismatch không thể được nhận diện tin cậy nếu không đổi schema |
| TODO-R3-03 | **ACCEPT_LATER → T12** | Xử lý khe crash sau commit lịch nhưng trước khi tạo vé mẫu trong phạm vi dữ liệu demo |
| TODO-R3-04 | **ACCEPT_LATER → T12** | Sửa menu Chủ đề tràn viewport trong phạm vi UI/demo T12 |
| TODO-R2-02 | **ACCEPT_LATER** | Test dùng `upcoming` thay taxonomy thật `coming_soon`; không ảnh hưởng kết quả T11 |
| TODO-R2-03 | **ACCEPT_LATER** | Lịch sử sidecar tăng theo ngày; chưa nâng thành RESOLVED |
| TODO-01 Round 1 | **ACCEPT** | Frontend automatic tests ngoài scope T11 |
| TODO-02 Round 1 | **RESOLVED** | Round 3 đã có health JSON và uvicorn log |
| TODO-03 Round 1 | **WONT_FIX** | Starlette TestClient deprecation không ảnh hưởng AC |
| TODO-04 Round 1 | **DEFER_CLEANUP_AFTER_CLOSURE** | Giữ evidence; không xóa trong bước ghi nhận PO/pre-merge |

Không TODO deferred nào được tự nâng thành RESOLVED. T12/T13 không được mở trong bước này.

## 4. Runtime safety

- Database thật chưa được cấp quyền khởi động trong bước PO recording/pre-merge này.
- Không startup backend/model thật, không seed, reset, restore hoặc kết nối `backend/firefly.db`.
- Việc khởi động backend thật sau merge vẫn cần authorization riêng và quy trình backup/checkpoint tương ứng.
- Q4 giữ **OPEN**.

## 5. Trạng thái bàn giao

- T11: **PO_APPROVED / PENDING_PO_MERGE**.
- Current Active Task: T11.
- T12: **PLANNED / NOT AUTHORIZED**.
- Next Step: PO tự merge T11 vào `master`, sau đó mới xác minh merge và thực hiện closure riêng.
- Không merge, tag hoặc chuyển T11 thành DONE/CLOSED trong bản ghi này.
