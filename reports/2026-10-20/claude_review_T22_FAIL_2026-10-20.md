# Claude Independent Review — T22 (Round 1)

- Task: T22 — Chấm sao, bình luận ẩn danh và hoàn thiện trải nghiệm người xem
- Nhánh: `task/T22-cham-sao-an-danh` · commit review: `bf3bb4a` · baseline `master` `cdc9bdd`
- Ngày: 2026-10-20 · Reviewer: Claude
- **Kết luận: FAIL** — 1 Required Fix (Medium, hồi quy), 4 TODO, 2 OBS. Phần còn lại đạt.

## 1. Phạm vi và quy tắc
- 39 file trong diff, **tất cả nằm trong allowlist mục 6** (các trang admin/Checkout/Account/NotFound chỉ thêm `usePageTitle`).
- Không có `.env`, `*.db`, model, dữ liệu lớn trong Git. Không thêm thư viện. `classifier.py`, `seats.py`, `utils/seats.js` không đổi.
- Endpoint mới có ở cả `real.js` và `mock.js`; mock trả cùng tập khóa JSON (kiểm trực tiếp, mục 3).
- Lỗi trả `HTTPException` kèm câu tiếng Việt. Đổi schema đã ghi trong `HUONG_DAN.md` và report Codex.

## 2. Gate độc lập
| Gate | Kết quả |
|---|---|
| `compileall -q backend\app` | exit 0 |
| `pytest -q` (basetemp scratchpad do quyền thư mục tạm của Windows) | **115 passed** |
| `npm run build` | đạt |
| Backend DB tạm + `/api/health` | `status ok`, `classifier: phobert_b` (model B active từ T10), PhoBERT loaded |
| Mock mode | đạt (mục 3) |
| Probe tạm `backend/tests/test_zz_claude_probe_t22.py` | đã chạy, **đã xóa**; working tree sạch |

## 3. Đối chiếu Acceptance Criteria
| AC | Kết quả | Bằng chứng |
|---|---|---|
| AC-01 | PASS | Trình duyệt (real, phim 2): bấm 2 sao → "★ 3.5 (2 lượt)", "Đã lưu đánh giá.", `aria-pressed` đúng nút 2 |
| AC-02 | PASS | Bấm lại 2 sao → "★ 5.0 (1 lượt)", "Đã hủy đánh giá."; pytest UNIQUE + ghi đè |
| AC-03 | PASS | pytest 401/422/400/404; StarRating khách → `/dang-nhap` kèm `from` (đọc code) |
| AC-04 | PASS | Điểm thật ở thẻ phim, trang phim, khu lịch chiếu, trang chọn ghế (ảnh 375px); không còn `movie.score` phía người xem; `top_rated` dùng `rating_avg >= 4` |
| AC-05 | PASS | Bình luận kèm 4 sao: số lượt giữ 2 (không đếm đôi), sao hiện cạnh bình luận |
| AC-06 | PASS | Public JSON: `user_name` "Khán giả ẩn danh", không có user_id/email; admin API: tên thật + `is_anonymous: true`; PhoBERT vẫn chấm/ẩn |
| AC-07 | PASS | Xóa bình luận người khác → 404 (probe); chủ bình luận thấy nút "Xóa bình luận" |
| AC-08 | PASS | BUG-1 (lỗi hiện tại chỗ, danh sách còn), BUG-2 đếm ngược `Còn 14:54 → 14:52`, BUG-3 đã đăng nhập vào `/dang-nhap` → về trang trước, BUG-4 tiêu đề tab theo trang, BUG-6 giữ `search`; chatbot 375px nằm trên thanh tóm tắt (616–662 so với 669) |
| AC-09 | **FAIL** | Xem RF-01 |
| AC-10 | PASS | Mock: set 1 → avg 3/2 lượt; set 2 → 3.5/2; comment ẩn danh 5 sao; remove → 5/1; coming_soon → 400 câu tiếng Việt; xóa bình luận ok |
| AC-11 | PASS | 17 test mới + 98 cũ = 115/115 |
| AC-12 | **FAIL** | Hồi quy bộ sưu tập "Chủ đề" (RF-01) |

## 4. Required Fixes
### RF-01 — Sắp xếp mặc định ở Khám phá phá thứ tự các bộ sưu tập
- **Severity:** Medium (hồi quy chức năng có sẵn từ trước T22)
- **File:** `frontend/src/pages/Explore.jsx` (khối `sort` / `sorted`)
- **Problem:** Khi URL không có `sap-xep`, trang mặc định `"moi-nhat"` và luôn sắp lại theo `release_date`. Các bộ sưu tập `hot_week`, `hot_month`, `top_comments`, `top_rated` vốn được backend xếp theo độ hot / số bình luận / điểm, nay bị xếp lại theo ngày khởi chiếu nên tên "Phim hot trong tuần" không còn đúng.
- **Evidence:** API `/api/movies?collection=hot_week` trả id `9,4,8,3,18,1,10,2,5`; giao diện `/kham-pha?chu-de=hot-trong-tuan` hiển thị `5,18,2,8,1,9,3,10,4` (DB tạm, 20/10/2026).
- **Expected Fix:** Khi không có `sap-xep` thì giữ nguyên thứ tự API trả về (thêm lựa chọn "Mặc định", hoặc chỉ sắp khi người dùng chọn). Ba kiểu sắp xếp cũ vẫn chạy và lưu URL. Thêm bằng chứng: thứ tự giao diện khớp API ở `hot-trong-tuan` và `danh-gia-cao` khi chưa chọn sắp xếp. Mock cũng phải khớp.

## 5. TODO (không chặn)
- **TODO-01 (Medium, cần PO quyết) — Seed làm sao bình luận demo mâu thuẫn.** Seed cho `admin` và `demo` chấm mọi phim; bình luận mẫu đều của `demo`, mà `author_stars` là điểm hiện tại của người viết, nên **mọi bình luận mẫu của một phim, kể cả bình luận tiêu cực, đều hiện cùng số sao** (phim 1: ★★★★★ cạnh bình luận bị ẩn vì tiêu cực). Mỗi phim cũng chỉ có đúng 2 lượt chấm, trong đó có admin. Đề xuất: seed điểm từ vài tài khoản khán giả mẫu riêng, không chấm bằng tài khoản viết bình luận mẫu (hoặc chọn điểm hợp với cảm xúc bình luận). Nên làm trước khi quay video demo T12/T13.
- **TODO-02 (Low) — Token hỏng làm API bình luận công khai trả 401.** `optional_user` trong `comments.py` gọi `get_current_user`, nên Bearer hết hạn/không hợp lệ → `GET /api/movies/{id}/comments` = 401 "Phiên đăng nhập không hợp lệ." (probe). Lần tải đầu trang không lộ vì `AuthContext` xóa token trước, nhưng token hết hạn giữa phiên sẽ làm khu bình luận báo lỗi. Đề xuất: bắt `HTTPException` 401 và coi như khách.
- **TODO-03 (Low) — Dãy sao trong form bình luận lưu ngay khi bấm**, không đợi "Gửi bình luận" như Task Record mục 3B viết; khi gửi, `stars` được upsert lại lần nữa (vô hại). Hành vi hợp lý vì chỉ có một điểm/phim; chỉ cần PO chấp nhận hoặc ghi lại.
- **TODO-04 (Low) — `TicketStub`:** vé `held` mà thiếu `hold_expires_at` sẽ hiện "Còn NaN:NaN". Backend luôn trả giá trị nên chưa xảy ra; nên chặn bằng một điều kiện.

## 6. Quan sát
- **OBS-01:** PhoBERT-B đoán câu khen "Phim dựng không khí rất tốt, diễn viên chính đóng hay." là tiêu cực (thử trên phim kinh dị "Bóng Ma Hẻm 37"). Là giới hạn của model, ngoài phạm vi T22; có thể dùng làm ví dụ lỗi trong chương đánh giá.
- **OBS-02:** Checkbox "Bình luận ẩn danh" và textarea bình luận có tên truy cập lấy từ value/placeholder thay cho nhãn; ảnh hưởng nhỏ tới trình đọc màn hình.

## 7. Trạng thái
T22 `CLAUDE_REVIEW → FIX_LOOP`. Chỉ RF-01 bắt buộc; TODO-01 chờ PO quyết có gộp vào vòng sửa này không.

## 8. Prompt Codex cho vòng sửa
```text
Bạn là Codex, dự án Firefly Cinema (C:\Projects\firefly-cinema), nhánh task/T22-cham-sao-an-danh.
Đọc reports/2026-10-20/claude_review_T22_FAIL_2026-10-20.md và docs/tasks/T22.md.
Sửa RF-01: ở frontend/src/pages/Explore.jsx, khi URL không có `sap-xep` thì giữ nguyên thứ tự danh sách API trả về (thêm lựa chọn "Mặc định"); chỉ sắp xếp khi người dùng chọn Mới nhất / Đánh giá cao / Tên A–Z, vẫn lưu trên URL. Kiểm chứng cả real và mock: /kham-pha?chu-de=hot-trong-tuan và ?chu-de=danh-gia-cao hiển thị đúng thứ tự API.
[Nếu PO đồng ý] Sửa thêm TODO-01 (seed điểm từ tài khoản khán giả mẫu riêng, bình luận mẫu không mang sao mâu thuẫn), TODO-02 (optional_user coi token hỏng là khách, thêm pytest), TODO-04.
Chỉ sửa file trong allowlist T22. Gate: compileall, pytest, npm run build, mock mode. Commit "[T22] Fix RF-01 ...", viết reports/YYYY-MM-DD/codex_fix_T22_round2_YYYY-MM-DD.md, đặt T22 về CLAUDE_REVIEW. Không merge.
```
