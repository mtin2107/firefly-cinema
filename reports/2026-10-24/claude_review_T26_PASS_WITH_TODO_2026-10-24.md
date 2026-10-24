# Claude Review — T26 Khung đánh giá sao bật lên khi bấm vào điểm

| Trường | Giá trị |
|---|---|
| Task | T26 |
| Nhánh / commit review | `task/T26-khung-danh-gia` @ `cffc533` (base `master` `6d49d16`, đã có T25) |
| Ngày | 24/10/2026 |
| Reviewer | Claude (độc lập) |
| Kết luận | **PASS_WITH_TODO** |
| Required Fix | 0 |
| TODO | 1 (Low, không chặn) |

## 1. Scope
`git diff --stat master...task/T26-khung-danh-gia`: 6 file, +171/−17. Đủ 6/6 file trong allowlist mục 6: `RatingDialog.jsx` (mới), `MovieDetail.jsx`, `global.css` (chỉ thêm class, `:root` không đổi), `CHANGELOG.md`, report Codex, file điều phối. Không đụng `backend/`, `frontend/src/api/**`, `CommentSection.jsx`, `StarRating.jsx`, `package.json`. Không đổi schema.

## 2. Gate độc lập
| Gate | Kết quả |
|---|---|
| `compileall -q backend\app` | exit 0 |
| `pytest -q` | 194 passed |
| `npm run build` real / mock (`VITE_USE_MOCK=true`) | đạt / đạt |
| Backend tạm + health (SQLite tạm, cổng 8005) | `ok`, `phobert_b` |

## 3. Kiểm trên trình duyệt
Real (frontend 5179 → backend tạm 8005, không ghi DB thật):

| AC | Kết quả |
|---|---|
| AC-01 | Phim 4: không còn `.star-rating` trong khối thông tin; nút `★ 4.0 (6 lượt)`, `aria-haspopup="dialog"`. |
| AC-04 | Chưa đăng nhập bấm nút điểm → `/dang-nhap`; đăng nhập bằng form → quay lại `/phim/4`. |
| AC-06 + AC-02 | Focus nút điểm, Enter → dialog `:modal`, tên truy cập "Đánh giá phim Mèo Mướp Đi Lạc", focus ở sao 1, "Lưu đánh giá" khóa khi chưa chọn. Tab ×3 + Enter chọn 4★, Tab ×2 tới "Lưu đánh giá", Enter → "Đã lưu đánh giá.", dialog tự đóng sau ~1 s, nút thành `★ 4.0 (7 lượt)`, hiện "Bạn đã chấm 4★", focus về nút điểm. |
| AC-03 | Mở lại thấy sẵn "Chấm 4 sao" và có thêm nút "Hủy đánh giá". Phim 2: chọn tạm 2★ rồi Esc → 0 request rating, điểm giữ `4.3 (4 lượt)`. "Hủy đánh giá" ở phim 4 → `DELETE /api/movies/4/rating` 200, `7 → 6 lượt`, dòng "Bạn đã chấm" biến mất. |
| AC-05 | Phim sắp chiếu (Sơn Tinh Thủy Tinh): điểm chỉ là chữ, không có nút, không render dialog. |
| AC-07 | Chọn sao ở form bình luận: `aria-pressed=true`, 0 request rating (vẫn chỉ lưu khi gửi bình luận, như T22). |
| AC-08 | Mock: mở dialog, chọn 5★, lưu → `★ 4.0 (6 lượt)` thành `★ 4.1 (7 lượt)`, "Bạn đã chấm 5★"; phim sắp chiếu không có nút. |
| AC-09 | 375px: dialog rộng 337px, `scrollWidth = 375`, 5 sao đều 44px. 1280px: dialog 480px ở giữa, không tràn. Request đều 200. Lỗi `ERR_CONNECTION_REFUSED` trong console chỉ xuất hiện lúc tab mở trước khi backend tạm nạp xong model. |
| AC-10 | pytest 194/194; T26 không đụng đặt vé, tìm kiếm hay backend. Checklist mục 7 đã chạy đủ sáng 24/10 trên base, và Codex ghi lại trên nhánh. |

**Ghi chú môi trường (không phải lỗi T26):** trình duyệt tích hợp của Claude bị ẩn thì không vẽ khung hình (0 rAF). Khi đó Chrome không phát sự kiện `close` của `<dialog>`, kể cả với một `<dialog>` trơn không dùng React, nên dialog trông như "không mở lại được". Đưa tab lên và buộc vẽ khung hình thì `close` chạy đúng: `open` về `false`, mở lại bình thường. Mọi kết quả AC-03 ở trên đo trong điều kiện có vẽ khung hình.

## 4. Kiến trúc / chất lượng
- Dùng `<dialog>` + `showModal()` gốc, không thêm thư viện. Tái dùng `StarRating` làm lựa chọn tạm (`draft`). Lưu/hủy đi qua `changeRating` sẵn có, giờ trả `true/false`.
- Esc, nút "Đóng" và bấm ra ngoài khung (so tọa độ với `getBoundingClientRect`) đều đóng; `onClose` trả focus về nút điểm. Có bẫy Tab trong dialog.
- `key={movie.id:user.id}` làm dialog dựng lại khi đổi phim hoặc đổi người dùng. Phim sắp chiếu không render dialog.
- Thông báo `role="status"` nằm trong dialog. Sau khi đóng, trang chỉ còn dòng "Bạn đã chấm N★"; với lỗi API, dialog không đóng.

## 5. TODO (Low, không chặn)
**TODO-01 — Mở dialog khi chưa chấm thì sao thứ nhất trông như đã chọn.**
- File: `frontend/src/components/RatingDialog.jsx` (qua `StarRating`).
- Problem: `showModal()` đưa focus vào sao 1. `StarRating` tô sáng theo focus (`onFocus → setPreview`), nên sao 1 sáng màu vàng dù `draft` rỗng và nút Lưu đang khóa.
- Evidence: ảnh dialog lần mở đầu ở phim 4 (sao 1 có viền và màu vàng; `aria-pressed` cả 5 sao đều `false`).
- Expected Fix: thêm `autoFocus` cho tiêu đề hoặc nút "Đóng" của dialog, hoặc cho `StarRating` bỏ preview khi focus đến từ việc mở dialog. Có thể ghi là hạn chế.

## 6. Quan sát
- **OBS-01:** nút điểm bị khóa khi `ratingBusy || commentBusy`. Nếu một bình luận đang gửi đúng lúc dialog đóng thì focus không trả về được nút đang khóa. Hiếm gặp, không ảnh hưởng dữ liệu.

## 7. Lưu ý cho PO
- T26 không đổi schema, merge xong **không** phải reset DB.
- Merge T26 xong thì T13 là task cuối trước hạn 01/11.

## 8. Bàn giao task kế tiếp — prompt Codex T13
T26 PASS_WITH_TODO, nên T13 chuyển sang `READY_FOR_HANDOFF` sau khi PO merge T26. Tín điền quyết định trước khi gửi.

```text
Bạn là Codex, dự án Firefly Cinema (C:\Projects\firefly-cinema, Windows + PowerShell).
Đọc theo thứ tự: docs/PROJECT_SOURCE_OF_TRUTH.md, docs/AGENT_RULES.md, docs/TASK_COORDINATION_ACTIVE.md, docs/tasks/T13.md. T13.md là bản PO đã duyệt.
T24, T25, T26 đã merge vào master (T25 đã reset DB thật, bản sao ở backup\db-truoc-T25). Làm trên nhánh task/T13-v1 (tạo từ master mới). Đầu tiên ghi closure T24/T25/T26 (merge hash) và đặt T13 → IN_PROGRESS.

Quyết định PO trước T13 (Tín điền trước khi gửi):
- T12 TODO-01 (model B che câu khen phim 1): <giữ nguyên + ghi hạn chế | admin duyệt sẵn | đổi phim mở đầu>
- T14 TODO-02 (mã vé dùng lại sau khi hủy): <ghi hạn chế | ...>
- T25 TODO-01/02 (ô chọn video báo trống; ô YouTube hiện đường dẫn nội bộ): <ghi hạn chế | ...>
- T26 TODO-01 (sao 1 sáng khi mở khung đánh giá): <ghi hạn chế | ...>

Nhiệm vụ: T13 "Chốt v1.0 và sao lưu" — chỉ tài liệu và sao lưu, không viết tính năng.
- README.md (giới thiệu, ảnh, tính năng gồm T16–T26: banner trailer, Nội dung phim, khung đánh giá sao; kết quả F1 A/B/SVM/NB/LR và T15; cách chạy nhanh), HUONG_DAN.md (cài từ số 0, gắn model A/B/SVM, cấu hình .env gồm BANK_* cho QR và CHAT_* cho chatbot — chỉ tên khóa, không giá trị; chạy test; reset demo; định dạng video trailer).
- Mục "Hạn chế" gom: các quyết định PO ở trên, T14 TODO-04 (đổi mật khẩu không vô hiệu token cũ), T22 (ai đăng nhập cũng chấm sao; OBS-01 model B nhầm câu khen), T23 OBS-01 (soát vé không chặn theo giờ chiếu), T24 OBS-01, T25 (file video mồ côi khi thay/gỡ; YouTube cần mạng và quyền nhúng; video mock mất khi tải lại).
- docs/SAO_LUU.md phải gồm cả backend\uploads\ (poster và trailers); docs/images/*, CHANGELOG.md [1.0.0], cập nhật cuối CONG_NGHE.md/ARCHITECTURE.md; xử lý T18 TODO-03 và T00 TODO-03 theo T13.md.
Ràng buộc: chỉ file trong mục 6 của T13.md; không sửa code; không commit model/DB/.env/video/dữ liệu lớn; không đọc hay in giá trị khóa trong .env.
Gate: compileall, pytest, npm run build (real + mock) để xác nhận không hồi quy.
Commit "[T13] mô tả". Viết reports/YYYY-MM-DD/codex_implementation_T13_YYYY-MM-DD.md, đặt T13 sang CLAUDE_REVIEW. Không merge, không gắn tag v1.0 (Tín gắn).
```

**Việc Tín cần làm:** `git checkout master` → `git merge task/T26-khung-danh-gia` (không phải reset DB) → `git checkout -b task/T13-v1` → gửi prompt trên kèm `T13.md` và file điều phối.
