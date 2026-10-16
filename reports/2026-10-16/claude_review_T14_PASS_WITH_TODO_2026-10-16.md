# Claude Review — T14 — PASS_WITH_TODO — 16/10/2026

- Nhánh: `task/T14-huy-ve-tai-khoan`, commit `4eb0538` (1 commit trên `master` `5c10522`).
- Report Codex: `reports/2026-10-16/codex_implementation_T14_2026-10-16.md` (bằng chứng phụ).
- Probe trên SQLite tạm (dữ liệu demo T12 tạo bằng `reset_demo.py`) trong scratchpad của Claude; không chạm `backend/firefly.db`.

## 1. Scope

15 file, tất cả trong Allowed Files của T14.md: `routers/auth.py`, `routers/bookings.py`, `schemas.py`, `tests/test_t14_account_and_cancellation.py` (mới), `App.jsx`, `real.js`, `mock.js`, `Header.jsx`, `TicketStub.jsx`, `AuthContext.jsx`, `pages/Account.jsx` (mới), `MyTickets.jsx`, `global.css`, report, file điều phối. `models.py`, `seats.py`, `classifier.py`, `package.json`, `requirements*.txt` không đổi. Không đổi schema.

Bước 0 điều phối: T21 → DONE / CLOSED (merge `5c10522`); dòng T12 ghi "TODO-01: PO chưa quyết định — giữ mở, xử lý trước T13".

## 2. Kiểm tra code

- `DELETE /api/bookings/{id}`: gọi `expire_holds` trước, lọc theo `user_id` (vé người khác và vé không tồn tại cùng trả 404 "Không tìm thấy vé."), chỉ `held` mới hủy được, các trạng thái khác trả 409 đúng câu trong T14.md. Dùng lại `release_booking_seats` rồi `db.delete(booking)`; `Booking.seats` có `cascade="all, delete-orphan"`.
- `PATCH /api/auth/me`: `UpdateProfileIn` giới hạn 2–100 ký tự và cắt khoảng trắng hai đầu. `POST /api/auth/change-password`: `new_password` 6–100 ký tự như khi đăng ký; sai mật khẩu hiện tại trả 400 "Mật khẩu hiện tại không đúng.".
- Nút "Hủy vé" nằm trong khối `status === "held"` của `TicketStub`, có `window.confirm`. `Checkout` không truyền `status` nên nút không hiện ở đó.
- `AuthContext.updateProfile` gọi `setUser`, nên Header đổi tên ngay. `real.js` và `mock.js` cùng có `auth.updateMe`, `auth.changePassword`, `bookings.remove`.

## 3. Gate độc lập

| Gate | Kết quả |
|---|---|
| `compileall -q backend/app` | exit 0 |
| pytest đầy đủ | **95 passed**, 1 warning thư viện (85 cũ + 10 mới) |
| `npm run build` | đạt |

## 4. Probe API (backend thật, DB demo tạm)

| Ca | Kết quả |
|---|---|
| Demo tạo vé held E5–E6 (suất 80) | 201; E5 nằm trong `booked_seats` |
| Admin xóa vé của demo | 404 "Không tìm thấy vé." |
| Không token | 401 |
| Vé 999999 | 404 |
| Xóa vé paid / pending_verify / expired của demo | đều 409 "Chỉ hủy được vé đang giữ chỗ chưa thanh toán." |
| Demo hủy vé held | 200 "Đã hủy vé."; E5 đã trống |
| Hủy lại lần 2 | 404 |
| `full_name=" A "` | 422 (câu chung chung, xem TODO-03) |
| `full_name="  Lê Minh Tín  "` | lưu thành `"Lê Minh Tín"` |
| Mật khẩu mới 5 ký tự | 422 |
| Sai mật khẩu hiện tại 12 lần liên tiếp | 12 × 400, không lần nào 429 (xem TODO-01) |
| Đổi đúng | 200; đăng nhập bằng mật khẩu cũ 401, mật khẩu mới 200; token cũ gọi `/me` vẫn 200 (hạn chế đã ghi theo T14.md mục 13) |

## 5. Giao diện

- Real, "Vé của tôi" (demo có 4 vé: held, paid, pending_verify, expired): **đúng 1** nút "Hủy vé", ở vé held. Bấm → hộp xác nhận "Hủy vé FF00144 và trả lại các ghế đã giữ?" → thông báo "Đã hủy vé FF00144; các ghế đã được trả lại.", danh sách còn 3 vé, ghế D7 trên suất 80 đã trống.
- Real, `/tai-khoan`: đổi họ tên → "Đã cập nhật họ tên.", nút tài khoản trên Header đổi ngay sang tên mới. Sai mật khẩu hiện tại → "Mật khẩu hiện tại không đúng."; đổi đúng → "Đã đổi mật khẩu." và 3 ô mật khẩu được xóa trắng.
- 375 px: `/tai-khoan` và "Vé của tôi" không tràn ngang.
- Console: không có lỗi JS. Có một dòng 400 từ request sai mật khẩu do Claude cố ý gửi, và vài dòng `ERR_CONNECTION_REFUSED` từ lúc tab mở trước khi server sẵn sàng.
- Mock (`VITE_USE_MOCK=true`): paid / pending_verify / expired → 409, không tồn tại → 404, họ tên 1 ký tự → 422, sai mật khẩu → 400, mật khẩu ngắn → 422, đổi đúng → đăng nhập cũ 401 / mới được; tạo vé held rồi hủy → ghế E5 trống lại. Đã xóa dữ liệu mock do probe tạo trong trình duyệt.

## 6. Acceptance Criteria

| AC | Kết quả |
|---|---|
| AC-01 hủy vé hợp lệ → ghế trống | PASS (API, giao diện, mock) |
| AC-02 người khác 404; paid / pending_verify / expired 409; nút chỉ ở vé held | PASS |
| AC-03 đổi mật khẩu: mới được, cũ bị từ chối | PASS |
| AC-04 pytest + mock | PASS (10 test mới; mock đủ hàm, cùng mã lỗi) |
| AC-05 hồi quy | PASS (pytest 95/95, build, các luồng vé/tài khoản/đăng nhập) |

## 7. Required Fix

Không có.

## 8. TODO (không chặn)

- **TODO-01 — Medium — bảo mật:** `POST /api/auth/change-password` không giới hạn số lần thử mật khẩu hiện tại (12 lần sai liên tiếp đều 400, không 429). Ai cầm được token (ví dụ máy demo quên đăng xuất) có thể dò mật khẩu thật mà không bị chặn, vượt qua cơ chế khóa đăng nhập của T20. Sửa ít: dùng lại `SlidingWindowRateLimiter` đã có, đặt khóa theo `user.id`. T13 cấm sửa code, nên cần PO quyết: mở fix nhỏ trước T13, hoặc ghi vào mục hạn chế.
- **TODO-02 — Medium — PO quyết định, cần đổi schema nếu sửa:** mã vé sinh từ id (`booking_code = FF{id:05d}`) và bảng `bookings` không dùng `AUTOINCREMENT`. Khi vé held vừa hủy là dòng có id lớn nhất, vé tạo kế tiếp nhận lại đúng mã đó. Claude tái hiện được: hủy `FF00144` → vé mới cũng là `FF00144`. Rủi ro: khách đã chuyển khoản với nội dung mã cũ rồi hủy thay vì bấm "Tôi đã chuyển khoản"; admin có thể khớp tiền đó vào vé mới của người khác. Đây là hệ quả của thiết kế "xóa hẳn booking" mà T14.md đã chọn để không đổi schema. Đề xuất: ghi vào hạn chế của v1.0, hoặc mở task riêng dùng `AUTOINCREMENT` (cần xóa `firefly.db`).
- **TODO-03 — Low:** `full_name` không hợp lệ ở backend trả câu chung chung "Giá trị không hợp lệ." (bộ xử lý lỗi chung nuốt câu riêng của validator), trong khi mock trả "Họ tên cần từ 2 đến 100 ký tự.". Giao diện đã chặn bằng `minLength`, nên người dùng thường không gặp.
- **TODO-04 — Low:** đổi mật khẩu không làm token cũ hết hiệu lực (đúng đề xuất T14.md mục 13); cần ghi vào mục hạn chế của README/HUONG_DAN ở T13.

## 9. Kết luận

**PASS_WITH_TODO.** RF 0, blocker 0. T14 `CLAUDE_REVIEW → PO_REVIEW`.

## 10. Bàn giao task kế tiếp

**T13** (task cuối) phụ thuộc T11, T12, T15, T20, T21 (đều CLOSED) và T14 (vừa PASS). T13 → `READY_FOR_HANDOFF`.

**Tín quyết trước khi gửi prompt T13**, vì T13 cấm sửa code:
1. T12 TODO-01 (câu khen bị che trên phim 1): nếu chọn (a) "admin duyệt sẵn" thì cần sửa `demo_comments.json` — mở fix nhỏ **trước** T13, vì T13 sẽ chụp ảnh trang Thống kê.
2. T14 TODO-01 (giới hạn thử mật khẩu): sửa trước T13 hay ghi vào hạn chế.
3. T14 TODO-02 (dùng lại mã vé): ghi vào hạn chế hay mở task riêng sau v1.0.

**Tín làm:** PO review T14 → `git checkout master` → `git merge --no-ff task/T14-huy-ve-tai-khoan -m "[T14] Merge booking cancellation and account"` → nếu cần fix nhỏ ở mục trên thì báo Claude soạn prompt; nếu không thì `git checkout -b task/T13-v1`.

**Prompt Codex cho T13:**

```text
Bạn là Codex, Primary Implementer của dự án Firefly Cinema.
Chỉ đọc: docs/PROJECT_SOURCE_OF_TRUTH.md, docs/AGENT_RULES.md, docs/TASK_COORDINATION_ACTIVE.md (Snapshot, Status, bảng TODO),
docs/tasks/T13.md, README.md, HUONG_DAN.md, CHANGELOG.md, docs/CONG_NGHE.md, docs/ARCHITECTURE.md, docs/KICH_BAN_DEMO.md,
các report T02, T09, T15 có số F1 đã chốt, và các review Claude có TODO chuyển sang T13.

Bước 0 (đồng bộ điều phối theo PO): T14 đã được PO duyệt và merge vào master tại <hash merge T14>.
Cập nhật TASK_COORDINATION_ACTIVE.md: T14 -> DONE / CLOSED. Ghi quyết định PO cho T12 TODO-01: <...>, T14 TODO-01: <...>, T14 TODO-02: <...>.

Thực hiện T13 trên nhánh task/T13-v1 (tạo từ master sau merge T14), chỉ sửa file trong mục 6 Allowed Files của T13.md.
TUYỆT ĐỐI không sửa code trong backend/app/, frontend/src/; lỗi phát hiện -> ghi vào report để PO mở fix riêng.
Thư mục gốc duy nhất: C:\Projects\firefly-cinema.

Yêu cầu chính:
1. README.md: giới thiệu, tính năng (gồm hủy vé giữ chỗ, tài khoản, thống kê cảm xúc), ảnh, kết quả F1 T02/T09/T15
   (lấy đúng số đã chốt trong report, ghi rõ tập đo; không so trực tiếp số khác tập), cách chạy nhanh.
2. HUONG_DAN.md: cài từ số 0 trên máy mới (Python 3.13 venv, Node 24, backend/.env với SECRET_KEY >= 32 ký tự và ADMIN_PASSWORD),
   gắn model A/B/SVM vào đúng thư mục, chạy test (pytest + requirements-dev.txt), reset-demo.bat, chay-firefly.bat, mock mode.
   Thêm mục "Hạn chế đã biết" gồm các TODO PO chuyển sang hạn chế (ví dụ token không bị hủy khi đổi mật khẩu,
   mã vé có thể được dùng lại sau khi hủy, số liệu mock chỉ minh họa) — chỉ ghi những mục PO đã quyết ở Bước 0.
3. docs/SAO_LUU.md: bảng file đã sao lưu (model A, model B, *.joblib, dữ liệu processed + phim, notebook, firefly.db demo),
   vị trí Drive MyDrive/thesis_backup_v1/ và backup\v1.0\, kích thước, SHA256 (Get-FileHash) cho từng file model;
   chỗ trống để Tín ghi vị trí video demo và kết quả kiểm checksum sau khi tải lại từ Drive.
   Codex chỉ tính checksum và kích thước trên máy; việc tải lên Drive và chép ra USB là của Tín.
4. CHANGELOG.md mục [1.0.0]; cập nhật lần cuối docs/CONG_NGHE.md và docs/ARCHITECTURE.md cho khớp code hiện tại
   (endpoint T14, T21; không thêm thông tin không có trong code).
5. docs/images/: >= 8 ảnh chụp đặt tên rõ nghĩa (trang chủ, chi tiết phim, chọn ghế, vé của tôi, kiểm duyệt bình luận,
   so sánh mô hình với câu "lê thê", thống kê cảm xúc 30 ngày, tài khoản...). Chụp trên DB tạm tạo bằng backend/scripts/reset_demo.py
   (DATABASE_URL trỏ file tạm, ADMIN_PASSWORD trong môi trường); không lộ mật khẩu hay token trong ảnh.
6. Xử lý T18 TODO-03 và T00 TODO-03 theo T13.md mục 3 (việc nào cần Tín thao tác trên Drive thì ghi rõ chờ Tín).
7. AC-01: git clone C:\Projects\firefly-cinema C:\Temp\firefly-test, làm đúng HUONG_DAN.md từ đầu (chép model và .env theo hướng dẫn),
   ghi từng bước, lỗi gặp và cách sửa tài liệu; /api/health báo model active; pytest đạt; npm run build đạt. Xóa C:\Temp\firefly-test sau khi xong.

Cấm: sửa code; thêm thư viện; đổi schema; commit backend/.env, *.db, backup\, model, dữ liệu lớn; ghi mật khẩu thật vào tài liệu.
Không chạy backend trên backend/firefly.db thật.
Tạo reports/<YYYY-MM-DD>/codex_implementation_T13_<YYYY-MM-DD>.md: kết quả AC-01 từng bước, bảng checksum, danh sách ảnh,
việc còn chờ Tín (Drive, USB, video, tag v1.0).
Cập nhật TASK_COORDINATION_ACTIVE.md: T13 READY_FOR_HANDOFF -> IN_PROGRESS -> CLAUDE_REVIEW.
Commit dạng "[T13] mô tả". Không tự review, không tự PASS, không gắn tag. Trả lời bằng tiếng Việt.
```
