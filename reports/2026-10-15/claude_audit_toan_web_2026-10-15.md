# Claude — Đánh giá phản biện toàn bộ web Firefly Cinema (15/10/2026)

Phạm vi: nhánh `task/T19-tai-anh-poster` (commit `5bd8d42`), backend + frontend, trước bước deploy và T12–T15.
Vai trò: Independent Reviewer. Không sửa production code. Probe chạy trên SQLite + UPLOAD_DIR tạm (cổng 8005/5178), đã tắt và xóa cấu hình tạm; `backend/firefly.db` không bị đụng.

## 1. Gate

| Gate | Kết quả |
|---|---|
| `compileall backend/app` | exit 0 |
| `pytest` (backend) | 65/65 PASS (phải đặt `--basetemp` vì sandbox chặn thư mục tạm mặc định, không phải lỗi dự án) |
| `npm run build` | PASS, JS 391 kB (gzip 136 kB), CSS 42 kB |
| Health | `classifier: phobert_b` |
| Console trình duyệt | 0 lỗi; chỉ 2 cảnh báo React Router v7 future flag |
| Trang chủ 375px | không tràn ngang, ảnh đủ `alt`, không ảnh hỏng |

Kết luận gate: **chức năng hiện có chạy ổn**, test xanh. Các vấn đề dưới đây là lỗ hổng/thiết kế mà test hiện tại không bắt được.

## 2. Phát hiện (xếp theo mức độ)

### F-01 — CRITICAL: Ai cũng giả mạo được token admin (chặn deploy)
- File: `backend/.env` (SECRET_KEY) + `backend/app/config.py:13`
- Problem: `SECRET_KEY` trong `.env` đang **trùng giá trị mặc định công khai** `doi-chuoi-bi-mat-nay` (có trong `config.py` và `.env.example` đã commit).
- Evidence: probe tự ký JWT `{"sub":"1"}` bằng chuỗi này → `GET /api/auth/me` trả `200 admin@firefly.vn role=admin`; `GET /api/admin/bookings` trả `200`. Không cần mật khẩu.
- Expected fix: sinh khóa ngẫu nhiên (`python -c "import secrets;print(secrets.token_urlsafe(48))"`) đặt vào `.env`; backend **từ chối khởi động** nếu SECRET_KEY bằng giá trị mặc định khi chạy ngoài máy dev.

### F-02 — HIGH: Tài khoản mặc định `admin@firefly.vn / admin123` + không giới hạn đăng nhập sai
- File: `backend/app/seed.py:196`, `backend/app/routers/auth.py`
- Evidence: 30 lần đăng nhập sai liên tiếp đều 401, không khóa/chậm; mật khẩu seed đăng nhập được.
- Expected fix: khi deploy công khai đổi mật khẩu admin (đọc từ biến môi trường) và thêm giới hạn số lần thử. Chạy máy local khi bảo vệ thì chấp nhận được.

### F-03 — HIGH (nghiệp vụ): Giữ chỗ không thanh toán chiếm ghế tới 30 phút trước suất chiếu
- File: `backend/app/booking_rules.py:19-20,55-66`
- Evidence: một tài khoản giữ **9/9 suất** (8 ghế mỗi suất) không trả tiền; vé giữ hết hạn lúc `start_time − 30 phút` (ví dụ đặt hôm nay, suất ngày mai → giữ ~1 ngày). Tài khoản thứ hai giữ tiếp cùng suất vẫn `201`. Vài tài khoản rác có thể khóa trống cả rạp.
- Thêm: vé `pending_verify` (đã bấm "Tôi đã chuyển khoản") **không bao giờ tự hết hạn**, kể cả khi suất đã chiếu xong — ghế bị khóa tới khi admin xử lý.
- Expected fix: hạn giữ = `min(created_at + 10–15 phút, start_time − 30 phút)`; giới hạn số vé `held` đồng thời mỗi user. Đổi hạn giữ không cần đổi schema (đã có `created_at`).

### F-04 — MEDIUM: Bình luận không giới hạn tần suất, không cần đã xem phim
- File: `backend/app/routers/comments.py:58`
- Evidence: 10 bình luận liên tiếp trong ~1 giây đều `201`, mỗi cái gọi PhoBERT (CPU nặng). Dễ spam và làm chậm server.
- Expected fix: giới hạn N bình luận/phút/user (tái dùng kiểu `_check_quota` của `chat.py`); tùy chọn: chỉ cho bình luận khi có vé `paid` của phim.

### F-05 — MEDIUM (deploy): Tài nguyên không vừa hosting miễn phí
- `backend/models/phobert-binhluan` 517 MB + `phobert-binhluan-B` 517 MB; SQLite là file cục bộ; poster lưu ở `uploads/` trên đĩa.
- Hệ quả: Render/Railway gói free (512 MB RAM, đĩa tạm) sẽ hết RAM hoặc **mất DB và poster mỗi lần redeploy**. Frontend dùng `BrowserRouter` nên host tĩnh cần rewrite mọi đường dẫn về `index.html` (hoặc build với `VITE_ROUTER=hash`).
- Khuyến nghị: xem mục 3.

### F-06 — LOW
- `backend/.env` có **hai dòng `CHAT_API_KEY`** (dòng 12 và 15); `config.py` dùng `setdefault` nên dòng đầu thắng — dễ nhầm khi đổi key.
- `CHAT_MODEL` mặc định `gemini-3.8-flash` chưa được duyệt (đã ghi ở T17); trước demo phải đặt model đã kiểm.
- Poster cũ không bị xóa khi sửa/xóa phim → file mồ côi trong `uploads/posters` (đã biết ở T19 TODO).
- `confirm_booking` không gọi `expire_holds` trước khi đổi trạng thái → về lý thuyết admin xác nhận được vé giữ đã quá hạn nếu chưa ai tải danh sách.
- Cảnh báo React Router v7 future flag (không ảnh hưởng chạy).

### OBS — Giao diện
- Trang chủ, chi tiết phim, chọn ghế, 3 trang admin: render đúng nội dung tiếng Việt, không lỗi console, không tràn ngang trang ở 375px (sơ đồ ghế và dải ngày cuộn ngang trong khung riêng — đúng chủ đích).
- Hàng ghế A, B… hiện bằng GSAP `autoAlpha` từ 0. Trong lần chạy này khung trình duyệt bị ẩn (rAF = 0 khung hình) nên hàng A đứng ở `visibility:hidden`. **Không phải lỗi đã xác nhận** trên trình duyệt thật, nhưng là điểm yếu: nội dung quan trọng phụ thuộc animation chạy xong. Cần Tín xem bằng mắt 1 lần trên trình duyệt thật.
- Không chụp được ảnh màn hình trong phiên này nên **thẩm mỹ chưa được đánh giá bằng mắt**; chỉ kiểm bằng DOM.

## 3. Kết luận và đề xuất

**Web đủ hoàn thiện cho bảo vệ khóa luận nếu chạy trên máy (local).** Không nên deploy công khai cho tới khi sửa F-01 (bắt buộc), F-02 và F-03.

Thứ tự đề xuất:
1. **Ngay (5 phút, Tín tự làm, không cần task):** đổi `SECRET_KEY` trong `backend/.env`, xóa dòng `CHAT_API_KEY` trùng, đặt `CHAT_MODEL` đã kiểm. Sau đổi khóa mọi token cũ hết hiệu lực — đăng nhập lại.
2. **Chốt Q4 (deploy hay chạy máy):** khuyến nghị **chạy local khi bảo vệ** + quay video demo dự phòng. Nếu buộc phải online: VPS ≥ 2 GB RAM (chỉ nạp model B), giữ SQLite + `uploads/` trên ổ bền, đổi mật khẩu admin, bật HTTPS.
3. **Task sửa nhỏ (đề xuất T20 "Gia cố trước deploy"):** F-01 (chặn khóa mặc định), F-02 (mật khẩu admin từ env + giới hạn đăng nhập), F-03 (hạn giữ chỗ 15 phút + giới hạn vé giữ), F-04 (giới hạn bình luận). Không đổi schema.
4. **Sau đó mới T12 → T13** (dữ liệu demo, kịch bản bảo vệ, README/sao lưu). T14 (hủy vé, đổi mật khẩu) đáng làm vì bổ sung đúng chỗ người dùng thiếu (không tự hủy vé giữ được). T15 chỉ làm nếu dư thời gian — không ảnh hưởng web.

Hạn 01/11/2026 còn ~16 ngày: đủ cho bước 1–4 nếu cắt T15.
