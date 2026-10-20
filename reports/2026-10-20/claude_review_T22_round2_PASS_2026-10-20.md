# Claude Independent Review — T22 Round 2

- Task: T22 — Chấm sao, bình luận ẩn danh và hoàn thiện trải nghiệm người xem
- Nhánh: `task/T22-cham-sao-an-danh` · commit review: `80037bb` (diff vòng sửa `f4e6924..80037bb`)
- Ngày: 2026-10-20 · Reviewer: Claude
- **Kết luận: PASS** — RF-01 CLOSED, TODO-01..04 CLOSED / VERIFIED BY CLAUDE, Required Fix mở 0. AC 12/12.

## 1. Phạm vi vòng sửa
- 12 file, đều trong allowlist T22 mục 6 (Explore, seed, mock, comments router, CommentSection, MovieDetail, TicketStub, test_ratings, HUONG_DAN, ARCHITECTURE, điều phối, report Codex).
- Không đổi schema so với vòng 1; **seed đổi → PO phải xóa `backend\firefly.db`** (đã ghi trong HUONG_DAN và report Codex).
- Không thêm thư viện; không đổi classifier/seats/normalize; JSON real/mock cùng cấu trúc. Working tree sạch sau review.

## 2. Gate độc lập
| Gate | Kết quả |
|---|---|
| compileall | exit 0 |
| pytest | **118 passed** (thêm 3 test: token hỏng/hết hạn, bình luận không kèm sao giữ điểm cũ; test seed viết lại) |
| npm run build | đạt |
| Backend DB tạm mới (seed lại) | health `ok`, `phobert_b`, PhoBERT loaded |
| Mock | đạt |

## 3. Kiểm chứng từng mục
| Mục | Kết quả | Bằng chứng |
|---|---|---|
| RF-01 | **CLOSED** | Real: API `hot_week` = `9,4,8,3,18,1,10,2,5`, giao diện mặc định = `9,4,8,3,18,1,10,2,5`, ô Sắp xếp hiện "Mặc định"; `danh-gia-cao` khớp API `10,2,17,13,9,4,14,8,1,21,16,5,20`; `&sap-xep=ten-a-z` sắp đúng theo `localeCompare(vi)`. Mock: `hot_week` cùng thứ tự trên giao diện |
| TODO-01 | **CLOSED** | API `/api/movies/1/comments`: `author_stars` toàn bộ `None`; số lượt chấm khác nhau giữa các phim (2..6); admin/demo không có điểm (pytest). Mock: bình luận mẫu không sao, lượt chấm {2,3,4,5,6} |
| TODO-02 | **CLOSED** | `GET /api/movies/1/comments` kèm Bearer hỏng → 200; pytest bao cả token hết hạn; API ghi vẫn 401 |
| TODO-03 | **CLOSED** | Trình duyệt real, phim 2: bấm 3 sao trong form → không có request PUT, điểm giữ "★ 4.3 (4 lượt)"; gửi bình luận → "★ 4.0 (5 lượt)", sao đầu trang và form cùng ở 3, bình luận hiện ★★★; bỏ chọn rồi gửi thêm → vẫn 5 lượt, điểm 3 giữ nguyên |
| TODO-04 | **CLOSED** | Đọc code: thiếu/sai `hold_expires_at` → không hiện đồng hồ, không coi là hết hạn, không chạy timer |

## 4. Quan sát giữ lại (không chặn)
- **OBS-01:** PhoBERT-B đoán nhầm một số câu khen là tiêu cực (giới hạn model, ngoài phạm vi T22).
- **OBS-02:** checkbox "Bình luận ẩn danh" và textarea có tên truy cập lấy từ value/placeholder; ảnh hưởng nhỏ tới trình đọc màn hình.

## 5. Trạng thái
T22 `CLAUDE_REVIEW → PO_REVIEW`. T23 → `READY_FOR_HANDOFF` (dependency là T22; chỉ tạo nhánh sau khi PO merge T22).
Việc của Tín: review, merge `task/T22-cham-sao-an-danh` vào `master`; backup rồi xóa `backend\firefly.db` để seed lại; tạo `task/T23-tong-quan-soat-ve` từ `master` mới.

## 6. Bàn giao task kế tiếp — prompt Codex T23
```text
Bạn là Codex, implementer dự án Firefly Cinema (C:\Projects\firefly-cinema, Windows + PowerShell).
Đọc theo thứ tự: docs/PROJECT_SOURCE_OF_TRUTH.md, docs/AGENT_RULES.md, docs/TASK_COORDINATION_ACTIVE.md, docs/tasks/T23.md. T23.md là bản PO đã duyệt.
Điều kiện: T22 đã merge vào master (bảng ratings có sẵn). Làm trên nhánh task/T23-tong-quan-soat-ve tạo từ master mới.

Nhiệm vụ: T23 "Tổng quan quản trị và soát vé tại quầy".
- GET /api/admin/dashboard?days=7|30|90 (require_admin): doanh thu vé paid, số vé theo nhóm trạng thái, ghế đã bán, điểm sao trung bình + lượt chấm, `daily` đủ mọi ngày, bảng theo phim (vé paid, doanh thu, tỷ lệ lấp ghế theo sức chứa từ seats.py, điểm sao, tỷ lệ bình luận tiêu cực — dùng lại cách tính T21 nếu có). Gọi expire_holds trước khi đếm; truy vấn gộp SQL, không lặp từng vé.
- GET/POST /api/admin/checkin/{code}: tra cứu và soát vé paid một lần; thêm bookings.checked_in_at, checked_in_by; lỗi 404/409 câu tiếng Việt. "Vé của tôi" hiện "Đã vào rạp lúc …".
- Trang AdminDashboard (/quan-tri/tong-quan, mục đầu menu admin) với biểu đồ SVG tự vẽ như T21, và AdminCheckin (/quan-tri/soat-ve).
- Hàm mới ở cả real.js và mock.js, cùng cấu trúc JSON.
Ràng buộc: chỉ file trong mục 6; không thêm thư viện; không sửa booking_rules/seats/classifier. Đổi schema → ghi bước xóa backend\firefly.db vào HUONG_DAN.md.
Gate: compileall, backend + /api/health, npm run build (real + mock), pytest (thêm test AC-08), hồi quy, 375px/1280px.
Commit "[T23] mô tả". Viết reports/YYYY-MM-DD/codex_implementation_T23_YYYY-MM-DD.md có bằng chứng AC-01..AC-09, đặt T23 sang CLAUDE_REVIEW. Không merge.
```
