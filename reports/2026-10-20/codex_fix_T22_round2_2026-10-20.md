# Codex Fix Report — T22 Round 2

- Ngày: 2026-10-20 · Nhánh: `task/T22-cham-sao-an-danh`
- Baseline vòng sửa: `f4e6924` — PO quyết sửa RF-01 + TODO-01..04; review gốc `claude_review_T22_FAIL_2026-10-20.md`.
- Result: FIX_IMPLEMENTATION_COMPLETED / PENDING_CLAUDE_REVIEW. Không tự kết luận review PASS hoặc đóng RF.
- Đổi schema: Không thêm so với T22. **Seed thay đổi: phải xóa `backend\firefly.db` rồi khởi động lại để có bộ mẫu mới. PO backup/xác minh checksum/integrity/restore trước khi reset theo HUONG_DAN. Codex chỉ chạy SQLite tạm, không xóa DB thật.**

## Các mục đã sửa và bằng chứng

| Mục | Thay đổi | Kiểm chứng |
|---|---|---|
| RF-01 | Explore không có sap-xep giữ nguyên danh sách API. Thêm “Mặc định” đầu select; chọn lại Mặc định xóa sap-xep trên URL. Chỉ ba lựa chọn rõ ràng mới sort. | Browser Chrome real/mock: `/kham-pha?chu-de=hot-trong-tuan` cùng API id `9,4,8,3,18,1,10,2,5`; `/kham-pha?chu-de=danh-gia-cao` cũng khớp toàn bộ thứ tự API. Chọn đủ Mới nhất/Đánh giá cao/Tên A–Z rồi Mặc định, so thứ tự DOM với API + comparator độc lập và kiểm URL; reload giữ Mặc định. |
| TODO-01 | Sáu khán giả mẫu riêng `khan-gia-1..6@firefly.vn`, role user, password ngẫu nhiên qua secrets và lưu hash, không in password. Mỗi phim now_showing/ended có `2 + movie_id % 5` lượt, sao `3 + ((movie_id + index) % 3)`. Admin/demo không chấm mẫu. Mock tương ứng dùng crypto.getRandomValues, khóa v5 để không dùng lại seed v4. | Pytest seed kiểm 6 khán giả, hash khác nhau, công thức điểm/lượt, số lượt đa dạng, không admin/demo hoặc coming_soon, đủ 30 comment T12 đều author_stars=null; restart không tạo lại điểm đã xóa. DB runtime tạm: 6 khán giả, phim 1..5 có 3/4/5/6/2 lượt; tổng 17 phim có 2–6 lượt. Join 30 comment gốc với ratings trả 0, integrity_check=ok. Không sửa dữ liệu/kịch bản bình luận, vé, suất T12. |
| TODO-02 | optional_user chỉ bắt HTTPException 401 và trả None; lỗi khác vẫn được ném. Không đổi get_current_user hoặc quyền API ghi. | Hai pytest Bearer hỏng/hết hạn: GET comment 200, can_delete=false và tên ẩn danh đúng; GET my-rating và DELETE comment với cùng token vẫn 401. Mock đọc công khai đã xử lý token hỏng như khách qua ownsComment, giữ contract. |
| TODO-03 | StarRating form dùng draftStars riêng, mặc định từ điểm hiện tại. Chọn/bỏ chọn không gọi rating API. POST chỉ kèm stars khi draft có giá trị; bỏ chọn không gửi stars, giữ điểm cũ. Thành công cập nhật sao đầu trang, điểm tổng và sao cạnh comment. Lỗi gửi giữ draft để thử lại. Đầu trang vẫn lưu/hủy ngay. | Browser real/mock instrument adapter: chọn 5 sao form → 0 rating writes/0 POST, mine=null, điểm tổng và sao đầu trang không đổi. Gửi → POST stars=5, mine=5, sao đầu trang/điểm tổng khớp API; reload form mặc định 5. Bấm lại 5 → draft rỗng, gửi payload không có stars, mine vẫn 5. Draft 2 + tiêm lỗi POST → giữ 2, mine vẫn 5; thử lại → mine=2. Bấm sao 4 ở đầu trang → lưu ngay 4, bấm lại → hủy ngay null. Pytest thêm POST không có stars giữ rating cũ. |
| TODO-04 | Chỉ tính/hiện đếm ngược và xét expired khi hold_expires_at có timestamp hợp lệ; không chạy timer khi thiếu/sai. | Browser real/mock dựng vé held qua adapter với null/undefined/invalid-date: vẫn “Giữ chỗ”, không “Còn”, NaN hoặc “Đã hủy”; số lần tải vé ổn định sau hơn 1 giây (không phát sinh reload do onExpire). React StrictMode có thể gọi load ban đầu hai lần; kiểm tra không tăng sau mount. |

## Gate

| Gate | Kết quả |
|---|---|
| Compile | Từ backend: `venv\Scripts\python -m compileall -q app`: exit 0 |
| Focused | `venv\Scripts\python -m pytest -q tests/test_ratings.py --basetemp=tests/.t22r2-focused`: **20 passed**, exit 0 |
| Full pytest | `venv\Scripts\python -m pytest -q --basetemp=tests/.t22r2-final`: **118 passed**, exit 0, 82,77s; chỉ cảnh báo Starlette BlockingPortal deprecated có từ trước |
| Frontend | npm run build với VITE_USE_MOCK=false và true: cả hai exit 0, 87 modules |
| Backend runtime | Uvicorn 8022 + SQLite tạm `backend/tests/t22r2-runtime.db`; health 200, status=ok, classifier=phobert, active_version=A-backend, classifier_error=null |
| Mock/browser | Vite real 5222/mock 5223; Chrome headless + Playwright có sẵn trong runtime, không thêm thư viện. Các bước RF-01/TODO-03/TODO-04 nêu trên chạy cả hai, không có pageerror |
| Scope/format | Chỉ allowlist T22 mục 6; git diff --check sạch. Không đổi classifier/seats/normalize, thư viện hoặc JSON contract real/mock |

## Phạm vi và bàn giao

- File sửa: Explore, seed, mock, comments router, CommentSection, MovieDetail, TicketStub, test_ratings; HUONG_DAN/ARCHITECTURE đồng bộ hành vi/seed, report và điều phối.
- API real.js không cần đổi: vẫn gửi payload object có/không stars; mock giữ cùng tập khóa JSON và hành vi POST. Không sửa Task Record hoặc report Claude.
- DB thật SHA-256 trước/sau giữ nguyên: `E9817891E6AB905D418E1460D23EABB03CB96F497DB7DEAED61E5351E64CA364`. Server, SQLite/sidecar, script browser và thư mục test tạm đã dọn sau gate.
- RF-01 và TODO-01..04: **DEV FIXED / PENDING CLAUDE VERIFICATION**. OBS-01/02 ngoài vòng sửa được giữ nguyên; không đổi model.
- T22 `FIX_LOOP → CLAUDE_REVIEW`, chờ Claude Round 2. Không merge, đóng task hoặc mở T23.
