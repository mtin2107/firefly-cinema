# Claude review T29 — PASS_WITH_TODO (27/10/2026)

- Nhánh: `task/T29-tai-khoan` @ `667da93`, baseline master `9f7920e`.
- Nguồn đối chiếu: `docs/tasks/T29.md`, `git diff master...task/T29-tai-khoan`; report Codex `reports/2026-10-27/codex_implementation_T29_2026-10-27.md` là bằng chứng phụ.
- Runtime độc lập: backend 8006 trên SQLite và UPLOAD_DIR tạm (scratchpad), frontend real 5181. Không đụng `backend/firefly.db`, `backend/uploads` thật.
- **Đổi schema: Có** — `users.birth_date`, `users.gender`, `users.avatar_url`. PO sao lưu và reset DB sau merge (runbook `HUONG_DAN.md` mục T29).

## 1. Kết luận
**PASS_WITH_TODO.** RF 0. TODO-01 Medium (giới hạn kích thước body khi tải ảnh đại diện), TODO-02 Low (API bình luận công khai lộ thêm trường kiểm duyệt). OBS-01..05.

## 2. Scope và bảo mật
| Kiểm tra | Kết quả |
|---|---|
| File trong diff | 26 file, đều thuộc mục 6 (`utils/account.js` thuộc `utils/*.js`; `admin_dashboard.py` được phép). Test cũ sửa 1 file (`test_t28_account_summary.py`, thêm khóa `spent_this_year`) — bị ảnh hưởng trực tiếp |
| File cấm | Không có `.env`, `*.db`, `movies.json`, package, requirements, `classifier.py`, file trong `backend/uploads` |
| `:root` | Không đổi. `git diff --check` exit 0 |
| Quyền | `GET /api/admin/me/summary` dùng `require_admin` (user → 403 tiếng Việt). Avatar/email/hồ sơ chỉ thao tác trên `get_current_user` |
| Đường dẫn file | Tên file avatar là `uuid4().hex`; xóa file cũ chỉ khi URL khớp regex `/uploads/avatars/[0-9a-f]{32}\.(jpg|png|webp)` — không có path traversal |

## 3. Gate độc lập
| Gate | Kết quả |
|---|---|
| `compileall -q backend\app` | exit 0 |
| Backend + `/api/health` (8006, DB tạm schema mới) | `phobert_b` |
| `npm run build` real / mock | đạt / đạt |
| pytest toàn bộ (chạy 02:04 ngày 27/10) | **230 passed**, 0 failed (lần này OBS-01 T27 không rơi vào lỗi) |

## 4. Đối chiếu AC
| AC | Kết quả | Bằng chứng của Claude |
|---|---|---|
| AC-01 BUG-01 | PASS | Probe mở menu tài khoản, đếm số dòng chữ của từng mục, kiểm khung trong màn hình. **Admin** (11 mục) và **khách** (3 mục) ở 375, 768, 1024, 1280, 1366, 1440px: 0 mục xuống dòng, khung luôn nằm trong màn hình (admin rộng 492px, khách 302px; 375px: 351px / 302px) |
| AC-02 | PASS | Menu có avatar chữ cái, tên, email, vai trò; nhóm "Quản trị" 2 cột chỉ với admin; "Đăng xuất" tách cuối; badge vé giữ chỗ. Ảnh chụp ở bề ngang khung trình duyệt |
| AC-03 | PASS | `PATCH /me`: ngày 2099 → 422, 1899 → 422, giới tính lạ → 422 (tiếng Việt); hợp lệ lưu `2010-06-15`/`female`; `UserOut` không có `password_hash` |
| AC-04 | PASS | Sai mật khẩu 400, trùng email 400, sai định dạng 422; đổi sang `Demo.New@Firefly.vn` → lưu `demo.new@firefly.vn`; đăng nhập email mới 200, email cũ 401; token cũ gọi `/me` 200 |
| AC-05 | PASS (xem TODO-01) | File giả đuôi → 422 "Chỉ nhận ảnh JPG, PNG hoặc WebP."; > 2 MB → 422; thay ảnh: file cũ bị xóa, file mới còn; gỡ ảnh: file bị xóa; avatar admin không bị ảnh hưởng |
| AC-06 | PASS | Demo sinh 15/06/2010 (16 tuổi): T18 → 400 "Bạn chưa đủ 18 tuổi để xem phim T18."; P và T16 qua kiểm tra tuổi; bỏ ngày sinh → T18 qua kiểm tra tuổi. Helper tính theo ngày suất chiếu; test mốc sinh nhật có trong pytest |
| AC-07 | PASS | Trang khách 375px: 4 thẻ, mở `#ho-so` chọn đúng thẻ, bấm từng thẻ đổi hash (`#giao-dich`, `#ho-so`, `#hoat-dong`, `#chinh-sach`), không tràn ngang. Thẻ hồ sơ: "Tổng chi tiêu 2026 150.000 đ — Còn 850.000 đ để đạt hạng Bạc". Lịch sử nhóm "Tháng 10/2026". Thông báo "Quản trị viên đã duyệt lại: hiển thị bình thường" |
| AC-08 | PASS | Trang admin: Việc cần làm (14 bình luận chờ duyệt, 1 vé chờ xác nhận, 20 suất hôm nay), Công việc của tôi, 5 hoạt động gần đây, Bảo mật; không có hạng/chi tiêu/ngày sinh/giới tính |
| AC-09 | PASS (theo report Codex + build) | `real.js` và `mock.js` có đủ `changeEmail`, `putAvatar`, `deleteAvatar`, `admin.meSummary`; build mock đạt. Claude không chạy lại luồng mock trên trình duyệt |
| AC-10 | PASS | 375px không tràn ngang ở cả 4 thẻ; CSS reduced motion tắt animation trong `.account-page`, `.account-menu` |
| AC-11 | PASS (theo report Codex) | Gate như mục 3; hồi quy mục 7 dựa vào report Codex |

## 5. TODO
**TODO-01 — Medium — `backend/app/routers/auth.py` `put_avatar`, `admin_posters.py` `PosterUploadIn`**
- Problem: endpoint tải ảnh đại diện mở cho **mọi người đã đăng nhập** (đăng ký tự do), nhưng không giới hạn kích thước body. FastAPI đọc hết JSON vào bộ nhớ và giải base64 xong mới kiểm 2 MB. Trước T29, mẫu này chỉ admin dùng (poster).
- Evidence: `PosterUploadIn.data: str` không có `max_length`; không có kiểm tra `Content-Length` (khác `admin_trailers.py` có kiểm 413).
- Expected Fix: từ chối sớm khi `Content-Length` > khoảng 3 MB (413 tiếng Việt, như trailer), và/hoặc `data: str = Field(max_length=2_800_000)` cho schema avatar. Vài dòng.

**TODO-02 — Low — `backend/app/schemas.py` `CommentOut`**
- Problem: `CommentOut` (dùng cho `GET /api/movies/{id}/comments` công khai) thêm `human_label`, `reviewed_at` và khai báo lại `is_negative` (dòng sau ghi đè thành mặc định `False`). Trường kiểm duyệt giờ lộ ra cho mọi người xem; T29 không yêu cầu, trang Tài khoản đã dùng `AccountComment` riêng.
- Evidence: `GET /api/movies/1/comments` trả `human_label: 0`, `reviewed_at: 2026-10-27T01:04:40`.
- Expected Fix: bỏ 3 dòng thêm vào `CommentOut`.

## 6. Quan sát (không chặn)
- **OBS-01:** Mọi mục trong menu dùng chung một biểu tượng (ô vuông có 2 gạch), nên biểu tượng không giúp phân biệt mục. Nên mỗi mục một hình (người, vé, đăng xuất…).
- **OBS-02:** Ngày sinh sai ở backend báo câu chung "Giá trị không đúng định dạng yêu cầu." thay vì "Ngày sinh phải từ 01/01/1900 đến hôm nay." (bộ xử lý lỗi chung nuốt câu của validator). Frontend đã kiểm trước và hiện đúng câu cụ thể.
- **OBS-03:** `GET /api/admin/me/summary` tải toàn bộ bình luận và vé vào bộ nhớ rồi đếm; ổn ở quy mô demo, cần đếm bằng SQL nếu dữ liệu lớn.
- **OBS-04:** Trang admin ghi "Thành viên từ…" và hoạt động dạng "Duyệt bình luận #1" (chỉ có mã), chưa có tên phim.
- **OBS-05:** "Công việc của tôi" tính theo tài khoản admin chung (hạn chế đã ghi ở T29 mục 3).

## 7. Việc PO cần làm
1. Quyết TODO-01 (khuyến nghị FIX_NOW, vài dòng) và TODO-02 (FIX_NOW cùng lượt hoặc ghi hạn chế).
2. Sau khi quyết: merge `task/T29-tai-khoan` vào master; **dừng backend → sao lưu `firefly.db` + sidecar + `backend\uploads\` → kiểm SHA-256 → xóa `firefly.db` → khởi động lại** theo `HUONG_DAN.md` mục T29.
3. Xóa nhánh rỗng `task/T13-ten-task`, tạo `task/T13-v1` từ master mới, gửi prompt mục 8.

## 8. Bàn giao task kế tiếp — prompt Codex T13
T29 PASS_WITH_TODO, các TODO không chặn T13, nên T13 chuyển `READY_FOR_HANDOFF` sau khi PO merge T29 và reset DB.

```text
Bạn là Codex, dự án Firefly Cinema (C:\Projects\firefly-cinema, Windows + PowerShell).
Đọc theo thứ tự: docs/PROJECT_SOURCE_OF_TRUTH.md, docs/AGENT_RULES.md, docs/TASK_COORDINATION_ACTIVE.md, docs/tasks/T13.md. T13.md là bản PO đã duyệt.
T24–T29 đã merge vào master; DB thật đã reset sau T29 (schema users mới). Làm trên nhánh task/T13-v1 (tạo từ master mới). Đầu tiên ghi closure T24–T29 (merge hash) và đặt T13 → IN_PROGRESS.

Quyết định PO trước T13 (Tín điền trước khi gửi):
- T12 TODO-01 (model B che câu khen phim 1): <giữ nguyên + ghi hạn chế | admin duyệt sẵn | đổi phim mở đầu>
- T14 TODO-02 (mã vé dùng lại sau khi hủy): <ghi hạn chế | ...>
- T25 TODO-01/02 (ô chọn video báo trống; ô YouTube hiện đường dẫn nội bộ): <ghi hạn chế | ...>
- T27 TODO-01 (validator điểm dựa vào tên lớp) và OBS-01 (test_sentiment fail 0h–7h): <ghi hạn chế | ...>
- T28 TODO-01 đã sửa; OBS-01..03 (poster không bắt buộc, menu gọn ở ≤1360px, line-height tiêu đề): <chấp nhận | ghi hạn chế>
- T29 TODO-01 (giới hạn body tải ảnh đại diện), TODO-02 (trường kiểm duyệt ở API bình luận công khai): <đã sửa | ghi hạn chế>

Nhiệm vụ: T13 "Chốt v1.0 và sao lưu" — chỉ tài liệu và sao lưu, không viết tính năng.
- README.md (giới thiệu, ảnh, tính năng gồm T16–T29: banner trailer, Nội dung phim, khung đánh giá thang 10 có hiệu ứng, trạng thái phim tự chuyển theo ngày khởi chiếu, trang Tài khoản dạng thẻ với hạng thành viên, ngày sinh/giới tính/ảnh đại diện, chặn đặt vé theo độ tuổi, trang việc cần làm của quản trị, liên hệ cuối trang; kết quả F1 A/B/SVM/NB/LR và T15; cách chạy nhanh), HUONG_DAN.md (cài từ số 0, gắn model A/B/SVM, cấu hình .env gồm BANK_* cho QR và CHAT_* cho chatbot — chỉ tên khóa, không giá trị; chạy test; reset demo; định dạng video trailer).
- Mục "Hạn chế" gom: các quyết định PO ở trên, T14 TODO-04 (đổi mật khẩu không vô hiệu token cũ), T22 (ai đăng nhập cũng chấm điểm; OBS-01 model B nhầm câu khen), T23 OBS-01 (soát vé không chặn theo giờ chiếu), T24 OBS-01, T25 (file video mồ côi khi thay/gỡ; YouTube cần mạng và quyền nhúng; video mock mất khi tải lại), T29 (đổi email chưa xác minh qua thư; tài khoản admin dùng chung, chưa phân quyền theo nhân viên; không có điểm thưởng/quà tặng; chưa khai ngày sinh vẫn đặt được, kiểm giấy tờ tại rạp).
- docs/SAO_LUU.md phải gồm cả backend\uploads\ (poster, trailers, avatars); docs/images/*, CHANGELOG.md [1.0.0], cập nhật cuối CONG_NGHE.md/ARCHITECTURE.md; xử lý T18 TODO-03 và T00 TODO-03 theo T13.md.
Ràng buộc: chỉ file trong mục 6 của T13.md; không sửa code; không commit model/DB/.env/video/ảnh tải lên/dữ liệu lớn; không đọc hay in giá trị khóa trong .env.
Gate: compileall, pytest (chạy ban ngày, sau 7h sáng), npm run build (real + mock) để xác nhận không hồi quy.
Commit "[T13] mô tả". Viết reports/YYYY-MM-DD/codex_implementation_T13_YYYY-MM-DD.md, đặt T13 sang CLAUDE_REVIEW. Không merge, không gắn tag v1.0 (Tín gắn).
```

**Việc Tín cần làm:** quyết TODO-01/02 → merge `task/T29-tai-khoan` → sao lưu và reset DB theo HUONG_DAN mục T29 → `git checkout -b task/T13-v1` từ master → điền quyết định PO → gửi prompt trên.
