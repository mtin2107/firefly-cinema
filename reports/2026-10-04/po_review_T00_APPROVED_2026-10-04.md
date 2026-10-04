# PO Review — T00 — APPROVED — 04/10/2026

## Kết quả

| Mục | Quyết định |
|---|---|
| Task | T00 — Gom mã và dữ liệu về project ổ C, model card A |
| Claude Review | PASS_WITH_TODO |
| Required Fixes | 0 |
| Acceptance Criteria | Đạt |
| Definition of Done | Đạt |
| Product Owner Decision | **APPROVED** |
| Đổi schema | Không |

Quyết định PO do Tín cung cấp ngày 04/10/2026. Tài liệu này ghi lại quyết định đó; không phải kết luận tự review của Codex.

## TODO Disposition

### TODO-01 — Hai checkpoint model A khác nhau

**ACCEPT_LATER — T02.** Không thay model backend trong T00. T02 sẽ đo F1 trên cùng tập test của cả hai checkpoint model A bằng `normalize()` hiện tại; sau đó PO chọn checkpoint chính thức dựa trên bằng chứng.

### TODO-02 — `normalize()` khác `text_utils.py`

**ACCEPT_LATER — T02.** Không sửa `normalize()` trong T00. T02 sẽ đo ảnh hưởng của khác biệt tiền xử lý bằng cùng bộ dữ liệu và chỉ số trước khi quyết định có thay đổi backend hay không.

### TODO-03 — `firefly_phobert.zip` trên Drive chưa xác minh

**ACCEPT_LATER — T13.** Xác minh file, checksum và khả năng khôi phục trong bước sao lưu/chốt v1.0 của T13.

### TODO-04 — Thụt lề `HUONG_DAN.md` 4.2

**WONT_FIX.** Markdown vẫn hiển thị đúng, không ảnh hưởng chức năng, cài đặt hoặc nghiệm thu.

## Model A

Hai checkpoint model A khác trọng số vẫn được giữ nguyên. Không thay model backend trong T00. Việc chọn checkpoint chính thức chuyển sang T02 sau khi đo F1 cả hai bản.

## Kết luận và bàn giao

T00: **APPROVED**, Required Fixes: **0**, Open Blockers chặn T01: **0**. T01 được ủy quyền bắt đầu **sau khi** T00 được Tín merge vào `master` và nhánh T01 được tạo từ `master` mới nhất. T00 chưa được đánh dấu CLOSED trong repo tại thời điểm lập report này; thao tác merge vẫn thuộc Tín.
