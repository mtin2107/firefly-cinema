# Claude review T29 round 2 — PASS_WITH_TODO (27/10/2026)

- Nhánh: `task/T29-tai-khoan` @ `4b495d5`, so với `b044568` (PO duyệt bản mẫu v3, T29.md mục 14).
- Report Codex: `reports/2026-10-27/codex_fix_T29_round1_2026-10-27.md`.
- Runtime độc lập: backend 8006 + frontend 5181 trên SQLite và UPLOAD_DIR tạm. Không đụng DB/uploads thật.
- **Đổi schema:** vòng này không đổi thêm; T29 gốc vẫn cần reset DB sau merge.

## 1. Kết luận
**PASS_WITH_TODO.** R1-01..05 đạt. RF 0. TODO-01 của round 1 (Medium) **đã sửa phần lớn**, còn 1 lỗ nhỏ ghi thành TODO-03 (Low). TODO-02 CLOSED. OBS-01 (biểu tượng menu) CLOSED, OBS-04 (admin "Thành viên từ", hoạt động chỉ có mã) CLOSED.

## 2. Diff và scope
`git diff b044568..4b495d5`: 12 file — `admin_dashboard.py`, `admin_posters.py`, `auth.py`, `schemas.py`, `test_t29_round1.py` (mới), `mock.js`, `Header.jsx`, `Icons.jsx` (mới, được phép ở mục 14), `Account.jsx`, `global.css`, report, file điều phối. Không có file cấm, không sửa `:root`, `git diff --check` exit 0.

## 3. Gate độc lập
| Gate | Kết quả |
|---|---|
| `compileall -q backend\app` | exit 0 |
| Backend + `/api/health` | `phobert_b` |
| `npm run build` real / mock | đạt / đạt |
| pytest toàn bộ (12:26 ngày 27/10) | **239 passed**, 0 failed |

## 4. Đối chiếu AC vòng sửa 1
| AC | Kết quả | Bằng chứng của Claude |
|---|---|---|
| AC-R1-01 | PASS | Trang khách 1280px khớp bản mẫu v3: khung hồ sơ 3 vùng (avatar viền vàng mảnh + nút máy ảnh, tên, nhãn, ô Tổng chi tiêu có 3 huy hiệu), 4 ô số liệu có biểu tượng, thanh thẻ có biểu tượng và số thông báo, cuống vé. 375px không tràn ngang |
| AC-R1-02 | PASS (theo report Codex + quan sát) | 150.000 đ: huy hiệu Thành viên sáng, "Còn 850.000 đ để lên hạng Bạc". Các mốc đúng ngưỡng/vượt ngưỡng dựa vào probe của Codex |
| AC-R1-03 | PASS | Cuống vé dùng `Poster`, hiện mã vé `FF00142`, mã vạch; không còn "Xem vé #id" |
| AC-R1-04 | PASS | Ô ngày sinh là ô chữ placeholder `dd/mm/yyyy` (không còn `mm/dd/yyyy` của trình duyệt) |
| AC-R1-05 | PASS | Trang admin: không có chi tiêu/thang hạng/ngày sinh/giới tính/"Thành viên từ"; có "Không gian quản trị" với lối tắt; hoạt động gần đây có tên phim ("Duyệt bình luận · Chuyến Tàu Cuối Mùa Mưa") |
| AC-R1-06 | PASS | Probe menu: khách 3 mục / 3 biểu tượng khác nhau ở 375, 768, 1024, 1280, 1366, 1440px; admin 11 mục / 11 biểu tượng khác nhau ở 375 và 1280px. 0 mục xuống dòng, khung trong màn hình |
| AC-R1-07 | PASS (xem TODO-03) | Body 4 MB có `Content-Length` → **413** "Ảnh đại diện tối đa 2 MB."; ảnh hợp lệ → 200. `GET /api/movies/1/comments` trả đúng 12 khóa trước T29 (không còn `human_label`, `reviewed_at`) |
| AC-R1-08 | PASS (theo report Codex + build mock) | Claude không chạy lại luồng mock trên trình duyệt |

## 5. TODO
**TODO-03 — Low — `backend/app/routers/auth.py` `put_avatar`**
- Problem: chặn 413 chỉ dựa vào header `Content-Length`. Gửi kiểu `Transfer-Encoding: chunked` (không có `Content-Length`) thì `await request.body()` vẫn đọc **toàn bộ** body vào bộ nhớ rồi mới bị `max_length` từ chối.
- Evidence: probe gửi 4 MB dạng chunked → 422 "Ảnh đại diện tối đa 2 MB." (không ghi file, nhưng đã đọc hết 4 MB).
- Expected Fix: đọc bằng `request.stream()` và dừng khi vượt 3 MB (cách `admin_trailers.py` đang làm). Vài dòng. Rủi ro thực tế thấp với web chạy cục bộ khi bảo vệ.

## 6. Quan sát còn lại
- OBS-02 (câu lỗi ngày sinh ở backend chung chung), OBS-03 (summary admin tải toàn bộ bình luận/vé), OBS-05 (tài khoản admin dùng chung) giữ nguyên từ round 1.

## 7. Việc PO cần làm
1. Quyết TODO-03: sửa ngay (vài dòng) hoặc ghi hạn chế ở T13.
2. Merge `task/T29-tai-khoan` vào master; **dừng backend → sao lưu `firefly.db` + sidecar + `backend\uploads\` → kiểm SHA-256 → xóa `firefly.db` → khởi động lại** theo `HUONG_DAN.md` mục T29.
3. Xóa nhánh rỗng `task/T13-ten-task`, tạo `task/T13-v1`, gửi prompt T13 ở mục 8 của `claude_review_T29_PASS_WITH_TODO_2026-10-27.md`; dòng T29 ghi "TODO-01/02 đã sửa; TODO-03 <đã sửa | ghi hạn chế>".
