# T29 — Báo cáo triển khai Codex — 27/10/2026

- Vai trò: Primary Implementer. Bàn giao để Claude review độc lập; không kết luận review/PASS, không merge, không mở T13.
- Nhánh: `task/T29-tai-khoan`; baseline `master 9f7920ed2d003437d3b6888fb6f546f4f53db865` theo yêu cầu PO. Task Record còn ghi dependency `419b07e`; đây là mốc cũ, dùng baseline PO chỉ định (đã xác minh merge-base).
- **Đổi schema: Có** — `users.birth_date DATE NULL`, `users.gender VARCHAR(20) NULL`, `users.avatar_url VARCHAR(500) NULL`.
- Chỉ sử dụng SQLite/UPLOAD_DIR tạm. Không mở, reset hoặc ghi `backend/firefly.db`, không ghi `backend/uploads` thật. Không migration, không thêm thư viện, không đổi `:root`/movies.json.

## 1. Thay đổi đã triển khai

1. BUG-01: lưới một cột của menu tài khoản có selector riêng, không còn bị media query 1360px ép hai cột. Nhóm Quản trị chủ động hai cột, chuyển một cột ở màn hình nhỏ. Mọi link/nút một dòng; menu neo vào header trên màn hình nhỏ, có giới hạn chiều rộng/chiều cao. Menu taxonomy giữ nguyên quy tắc hiện có. Esc đóng và đưa focus về nút mở; tên dài được rút gọn ở nút, đọc đầy đủ trong đầu menu.
2. Menu có avatar/chữ cái, tên/email/vai trò, tài khoản, vé giữ chỗ đếm khi mở từ bookings.mine(), tám trang quản trị và đăng xuất tách cuối. Avatar mới cập nhật cả AuthContext, header và trang tài khoản.
3. Khách: thẻ hồ sơ trái; chi tiêu năm, hạng và thanh tiến độ lấy ngưỡng duy nhất từ MEMBERSHIP trong config.js; bốn thẻ phải nhớ URL hash. Lịch sử nhóm theo tháng địa phương, poster có fallback khi không có ảnh, trạng thái/ghế/tổng tiền/link phim. Hoạt động giải thích kiểm duyệt, điểm chấm; chính sách giữ/hủy vé, hạng và P/T13/T16/T18. Hồ sơ, email, mật khẩu, ảnh có thông báo tiếng Việt và trạng thái đang lưu.
4. Admin: hồ sơ riêng; việc cần làm toàn rạp; công việc và năm thao tác gần đây theo chính admin; bảo mật. Không hiện ngày sinh/giới tính/hạng/chi tiêu/lịch sử mua vé trong trang admin.
5. Backend: UserOut thêm trường mới/created_at; PATCH hồ sơ kiểm tra ngày sinh/giới tính; POST đổi email bằng mật khẩu hiện tại, chuẩn hóa chữ thường, kiểm trùng, dùng cùng limiter đăng nhập/đổi mật khẩu, giữ token theo user id. PUT/DELETE avatar chỉ thao tác chính chủ. Tách validate_image từ poster để cả poster và avatar dùng chung; giữ câu lỗi poster cũ. Tên UUID, magic bytes, 2 MB; thay/gỡ xóa file cũ sau commit; lỗi commit khi tạo ảnh dọn file mới.
6. Summary khách thêm spent_this_year và metadata kiểm duyệt, giữ giới hạn T28 (3 bình luận/5 điểm gần nhất). GET `/api/admin/me/summary` nằm trong router admin_dashboard hiện có và dùng require_admin.
7. Tuổi: backend dùng một helper age_allowed, tính đủ tuổi theo ngày suất chiếu, bao gồm ngày sinh 29/2; P/không khai/admin được qua. SeatSelection/Checkout và mock dùng chung helper frontend, chặn trước khi đặt, nhắc kiểm tra giấy tờ khi chưa khai. Helper frontend xử lý ngày địa phương cả khi mock trả ISO có múi giờ.
8. Real/mock có đủ changeEmail, putAvatar, deleteAvatar, admin.meSummary, cùng khóa JSON. Mock DB đổi v7; avatar data URL lưu localStorage, kiểm tra ảnh dùng lại helper poster, báo lỗi khi thiếu dung lượng thay vì báo lưu thành công giả.

## 2. Kiểm thử backend và gate

| Gate | Kết quả thực thi |
|---|---|
| compileall backend/app | Exit 0, đã chạy lại sau thay đổi backend |
| Backend + GET /api/health | Khởi động trên SQLite/UPLOAD_DIR tạm, HTTP 200, status ok, classifier/active_model phobert_b, active_version phobert-B-2026-10-09 |
| Build real | npm run build với VITE_USE_MOCK=false: exit 0 |
| Build mock | npm run build với VITE_USE_MOCK=true: exit 0 |
| Focused | 38/38: 21 ca T29 + poster + summary T28 |
| Pytest toàn bộ cuối | 229 đạt, 1 lỗi duy nhất OBS-01 T27; 230 ca, 156,03 giây; 1 cảnh báo DeprecationWarning của Starlette/anyio |
| Giờ pytest toàn bộ | 27/10/2026, 01:46:58–01:49:37, UTC+07:00 (Asia/Saigon) |
| Ngoại lệ | tests/test_sentiment.py::test_sentiment_uses_effective_label_group_by_and_complete_daily, dòng 91: ca tạo bình luận trừ 2 giờ rơi sang hôm trước. Nằm trong ngoại lệ 0h–7h PO cho phép. Không sửa test/production sentiment |
| Mock mode | Luồng thực trên trình duyệt, không chỉ build; kết quả chi tiết mục 3–4 |
| Scope/whitespace/bí mật | git diff --check không lỗi; kiểm danh sách file với allowlist; không đổi DB/.env/movies.json/:root/package/lockfile |

Test mới `backend/tests/test_t29_account.py`: lưu/đọc/xóa ngày sinh và giới tính; ngày tương lai/trước 1900/ngày không tồn tại/giới tính sai; UserOut không lộ hash; đổi email sai mật khẩu/trùng/sai định dạng/giới hạn thử sai/chữ thường; đăng nhập email mới, email cũ không dùng được, token cũ còn dùng được. Avatar JPG/PNG/WebP theo magic bytes, filename giả/path traversal không được dùng, base64 sai/GIF/>2 MB bị từ chối, đúng 2 MB nhận; thay/gỡ xóa file cũ, không ảnh hưởng avatar người khác, chưa đăng nhập 401. Tuổi P/T13/T16/T18 tại sinh nhật/trước một ngày bằng ngày suất chiếu cố định 2035 và helper với ngày giả lập; năm nhuận; chưa khai/admin bypass. Admin summary kiểm số liệu thật trên fixture, 401/403 và cách ly công việc; chi tiêu năm không cộng vé năm trước/chưa paid/người khác.

Test cũ duy nhất điều chỉnh: `test_t28_account_summary.py` thêm khóa spent_this_year trong expected keys, do hợp đồng T29 bổ sung trường này; giữ các assertion số liệu/quyền riêng tư/giới hạn cũ.

Lượt full đầu 01:33:49–01:36:13: 217 đạt/4 lỗi, gồm hai câu lỗi poster do refactor, expected keys T28 và OBS-01. Đã khôi phục câu lỗi poster và cập nhật expected keys; focused sau sửa đạt 38/38. Lượt full cuối ở trên chỉ còn ngoại lệ được cho phép.

## 3. Kết quả giao diện và API real/mock

- 62 kiểm tra viewport cuối: menu khách/admin real/mock ở 768/1024/1280/1366/1440 và 375px, thêm 320/521/600px; mọi panel nằm trong viewport, link/nút nowrap và không vượt chiều rộng. Lỗi lệch trái menu khách 375px tìm thấy trong đợt probe đầu đã sửa, đo/chụp lại bản cuối.
- Trang khách/admin real/mock ở 375/1280px không tràn ngang; có ảnh cả bốn thẻ khách. Reload `#ho-so` giữ Thông tin cá nhân. Reduced motion: 0 animation chạy trong trang Tài khoản. Không pageerror trong các phiên đo.
- Nút tài khoản dùng Enter/Tab/Esc; đo cuối xác minh Esc trả focus. Menu Thể loại vẫn có 23 lựa chọn; truy cập kết quả lọc và tìm kiếm hoạt động.
- Đã đi UI real/mock: lưu tên/ngày sinh/giới tính; đổi email bằng mật khẩu; tải avatar, avatar hiện ở sidebar và menu; badge held = 1 khớp vé vừa đặt. Đổi mật khẩu: xác nhận không khớp báo tiếng Việt; đúng thì lưu và đăng nhập bằng mật khẩu mới.
- Bốn thông báo kiểm duyệt đã đi qua thao tác API admin thật ở cả real/mock: mô hình che; relabel 0 hiển thị bình thường; relabel 1 giữ ẩn; hide bị admin ẩn. Refresh trang sau thay đổi bên admin để nhận summary mới.
- Trên trình duyệt real/mock: ngày sinh trẻ em làm fieldset ghế disabled và hiện cảnh báo tuổi; bỏ ngày sinh bật chọn ghế và hiện nhắc giấy tờ. Probe ISO gần nửa đêm tại Asia/Ho_Chi_Minh cho đúng hai phía sinh nhật.
- Hạng: 0/999999/1000000/3000000/4000000 đồng lần lượt Thành viên/Thành viên/Bạc/Vàng/Vàng, progress ở trong 0..100. Thử tên 100 ký tự ở 375px không tràn trang/menu.
- Khóa JSON UserOut, summary khách, todo/work/summary admin đã đối chiếu real/mock trong phiên trình duyệt. User thường gọi admin.meSummary đều 403; ngày sai và ảnh giả ở mock/real đều 422.

## 4. Checklist hồi quy BOI_CANH_DU_AN mục 7

| Mục | Kết quả thực thi |
|---|---|
| 1. Trang chủ, hero, poster intro | Real/mock hiện phim; hero có 5 poster và animation chạy; Xem chi tiết mở intro, đóng được. Đặt vé cũng mở intro rồi tới #lich-chieu, có ảnh trong bằng chứng |
| 2. Menu và tìm kiếm | Real/mock mở menu Thể loại (23 lựa chọn), chọn lọc ra Khám phá; tìm “meo muop” ra Mèo Mướp. Menu Quốc gia giữ 9 lựa chọn; Enter/Tab/Esc của tài khoản đã thực thi |
| 3. Đăng ký / đăng nhập quay lại | UI real/mock đăng ký mới; bỏ token, bấm giờ chiếu → đăng nhập; đăng nhập quay lại đúng /dat-ve/{showtime_id} |
| 4. Đặt 2 ghế | UI real/mock đặt hai ghế, Vé của tôi có đúng ghế; mở lại suất thấy hai nút ghế disabled |
| 5. Bình luận tiêu cực | Câu mẫu được che; thông báo chính chủ đúng; admin đọc được điểm real 0,9992, mock 0,87 (điểm mẫu) |
| 6. Health | HTTP 200, classifier phobert_b theo quyết định model B hiện hành; checklist cũ ghi phobert, không ép đổi cấu hình về A |
| 7. Mock | Toàn bộ luồng trên chạy với VITE_USE_MOCK=true; hồ sơ/menu/trang admin hoạt động |

## 5. Bằng chứng và môi trường cách ly

- Chỉ mục ảnh và phép đo: [codex_evidence_T29_2026-10-27.md](codex_evidence_T29_2026-10-27.md).
- Ảnh nằm trong workspace visualization ngoài Git để không thêm PNG ngoài allowlist. Có ảnh menu trước/sau 1280px; ảnh trước tái hiện Header/global.css của baseline 9f7920e trong Vite bằng bộ nhớ, không ghi đè source.
- Backend riêng: localhost:8299, DATABASE_URL trỏ `%TEMP%/firefly-t29-runtime.db`, UPLOAD_DIR `%TEMP%/firefly-t29-runtime-uploads`; không dùng server/DB thật đang mở ở cổng 8000. Frontend riêng real 5193/mock 5194; không dừng các server có sẵn 5173/5174.
- Pytest: fixtures tạo SQLite dưới tmp_path và monkeypatch thư mục avatar; DATABASE_URL/UPLOAD_DIR môi trường cũng trỏ TEMP trước import ứng dụng. Log cuối trong chỉ mục bằng chứng.
- Runbook PO ở HUONG_DAN mục T29: dừng backend, sao lưu DB + sidecar + uploads, so SHA-256/integrity/khóa ngoại, PO tự reset và khởi động lại. Chưa thực thi trên dữ liệu thật.

## 6. Giới hạn và bàn giao

- Không cắt hạng mục nào theo thứ tự mục 13: giữ chặn tuổi, Chính sách và Hoạt động gần đây admin.
- Không gửi thư xác nhận email; không có điện thoại/điểm thưởng/voucher/phân quyền nhân viên/cắt xoay ảnh theo scope PO.
- Hoạt động khách dùng summary T28: tối đa 3 bình luận và 5 điểm gần nhất; không có bảng thông báo mới hoặc cập nhật đẩy, refresh để nhận thao tác kiểm duyệt từ phiên khác. Hạng tính theo năm tạo vé paid vì schema không có thời điểm thanh toán riêng.
- Chưa có ngày sinh thì vẫn đặt được; kiểm giấy tờ tại rạp theo thiết kế. Ngày 29/2 đủ tuổi vào 1/3 ở năm không nhuận.
- Đổi schema cần PO sao lưu/reset DB thật sau duyệt/merge; bản cũ không được chạy cùng schema mới theo kiểu migrate ngầm.
- Chuyển CLAUDE_REVIEW; chờ Claude kiểm tra độc lập. Không tự review, không tự PASS, không merge, không mở T13.
