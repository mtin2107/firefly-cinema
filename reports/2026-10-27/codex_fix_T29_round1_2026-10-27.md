# T29 — Codex Fix vòng 1 — 27/10/2026

- Vai trò: Fix Implementer; nhánh `task/T29-tai-khoan`, baseline `b044568` như PO chỉ định, working tree sạch trước triển khai.
- Phạm vi: R1-01..05 và AC-R1-01..08 tại mục 14 T29. Không xử lý thêm OBS ngoài phạm vi này.
- **Đổi schema: Không** trong vòng sửa 1. Yêu cầu PO sao lưu/reset của T29 gốc vẫn giữ nguyên; không chạy trên DB/uploads thật.
- Bàn giao Claude kiểm tra độc lập; không tự review/PASS, không merge, không mở T13.

## 1. Thay đổi

**R1-01 — Khách theo mẫu v3.** Đã mở HTML mẫu bằng Chromium và đối chiếu PNG PO duyệt. Trang có khung hồ sơ ba vùng (avatar 112px viền vàng và nút máy ảnh; tên/email/tháng tham gia/nhãn; chi tiêu và thang huy hiệu), bốn ô số liệu, thanh thẻ có SVG/số thông báo và cuống vé. Dùng vàng phẳng, gradient nền nhẹ; không thêm chữ ánh kim, avatar xoay, đom đóm/vệt sáng. Hover cuống vé nhích nhẹ, bị tắt trong reduced motion.

Huy hiệu dùng ngưỡng từ MEMBERSHIP; vị trí và độ đầy đường ray tính theo tỉ lệ ngưỡng, không viết cứng 33,3%. Nút Thông báo đếm các thông báo kiểm duyệt suy ra từ bình luận hiện có trong summary. Giữ cả bốn hash cũ và nội dung hoạt động/chính sách.

Vé dùng component Poster hiện có (kể cả fallback không ảnh), mã `ticket.code` từ API, ghế dạng ô, nhãn trạng thái xanh/vàng/xám, cuống có đường đứt và hai lỗ, barcode CSS aria-hidden. Vé hết hạn/từ chối mờ; bỏ link dạng “Xem vé #id”, cả cuống dẫn tới trang Vé của tôi hiện có. Tên phim/ngày/ghế/dữ liệu đều lấy từ vé, không vá theo phim.

Form có hai cột, icon trong ô, ngày sinh text theo dd/mm/yyyy được kiểm tra trước khi chuyển ISO; ba nút giới tính; Hủy khôi phục hồ sơ hiện tại/Cập nhật lưu API cũ. Email và mật khẩu chỉ đọc có nút Thay đổi mở form tương ứng. Khung ảnh riêng hỗ trợ chọn/kéo thả/gỡ ảnh. 640px trở xuống form một cột; màn hẹp hồ sơ và cuống vé xếp dọc.

**R1-02 — Admin.** Cùng khung/màu/ô số liệu/form, có lối tắt kiểm duyệt và soát vé; không hiện chi tiêu/thang hạng/ngày sinh/giới tính hoặc “Thành viên từ”. Mỗi hoạt động hiện loại thao tác, tên phim và thời gian. Backend và mock thêm `movie_title` cho cả review/checkin. `real.js` đã trả JSON nguyên trạng qua getter hiện có nên không cần đổi hàm hoặc endpoint.

**R1-03 — SVG.** Tạo Icons.jsx làm nguồn dùng chung cho menu, thẻ, ô số liệu và form/huy hiệu. Ba mục khách và 11 mục admin có hình SVG khác nhau, đúng ý nghĩa. SVG trang trí có aria-hidden/focusable=false. Giữ cấu trúc lưới và hành vi Tab/Esc của menu đã được duyệt.

**R1-04 / TODO-01 — Body avatar.** Endpoint kiểm Content-Length > 3 × 1024² trước khi đọc JSON: 413 “Ảnh đại diện tối đa 2 MB.”. Dùng Request để FastAPI không parse body trước bộ chặn; sau đó kiểm bằng cùng schema PosterUploadIn. Schema có Field(max_length=2796204), đúng độ dài base64 của 2 MiB; poster dùng cùng giới hạn. Validator giữ câu lỗi poster cũ và dùng ngữ cảnh để báo đúng “Ảnh đại diện”. Giữ OpenAPI requestBody JSON với schema/giới hạn mới. JSON sai cấu trúc, body rỗng, kiểu data sai và media type khác JSON trả 422 tiếng Việt; vị trí lỗi được chuẩn hóa như FastAPI cũ. Hàm kiểm magic bytes vẫn dùng chung, không chép lại.

**R1-05 / TODO-02 — CommentOut.** Bỏ đúng human_label, reviewed_at và khai báo is_negative mặc định trùng. Public CommentOut trở lại 12 khóa trước T29. AdminCommentOut và AccountComment vẫn có metadata kiểm duyệt đúng phạm vi. Mock public response đã đúng khóa nên giữ nguyên.

## 2. Kiểm chứng AC vòng sửa

| AC | Bằng chứng thực thi |
|---|---|
| R1-01 | Ảnh guest real/mock 1280 đặt cạnh PNG v3, ảnh 375; kiểm trang không tràn, cuống xuống dưới và form một cột ở màn hẹp |
| R1-02 | Real/mock: 0 đ, đúng 1.000.000 đ và 3.500.000 đ; mốc hiện tại Thành viên/Bạc/Vàng, fill 0/33,3333/100%; còn 1.000.000/2.000.000 hoặc “Đã đạt hạng cao nhất” |
| R1-03 | Đối chiếu toàn bộ code cuống với api.bookings.mine(); số Poster và barcode aria-hidden khớp số vé; không còn “Xem vé #” |
| R1-04 | UI real/mock: 31/02/2010 bị chặn, 15/06/2010 lưu ISO 2010-06-15, reload vẫn hiện dd/mm/yyyy; nút Hủy khôi phục tên |
| R1-05 | Ảnh admin 375/1280 real/mock; không có spend/medal/gender/ngày sinh; danh sách tên phim có ở API và DOM. Test backend cho cả review/checkin; fixture mock kiểm riêng checkin |
| R1-06 | 24 probe menu: 375/768/1024/1280/1366/1440 × hai vai trò × real/mock; 11/3 SVG khác nhau, mọi mục nowrap, không tràn, panel nằm trong viewport, Esc trả focus |
| R1-07 | Test body >3 MB là JSON không hợp lệ vẫn nhận 413 trước parse; base64 quá dài nhận 422, không tạo thư mục ảnh; ảnh hợp lệ nhận. Public keys kiểm ở anonymous/user/admin và so real/mock |
| R1-08 | Real/mock cùng giao diện và khóa activity mới; hash giữ sau reload; 0 animation khi reduced motion, hover không transform. Gate ở mục 3 |

Fixture hạng: real dùng chặn response summary tại trình duyệt chỉ để đặt spent_this_year, mock thay tiền vé paid trong localStorage của context thử nghiệm; không đổi production code/threshold/DB thật. Nguồn số liệu summary backend vẫn được test T29 gốc kiểm bằng SQLite tạm.

Probe thêm dữ liệu xấu nhất hợp lệ: tên người dùng 100 ký tự, tên phim 200 ký tự có dấu chồng, bốn thể loại, không ảnh; ở 375/1280 không tràn. Không có điều kiện/CSS theo tên hoặc id phim.

## 3. Gate và hồi quy

| Gate | Kết quả thực thi |
|---|---|
| compileall backend/app | Exit 0 sau lần sửa backend cuối |
| Backend + /api/health | HTTP 200, status ok; PhoBERT B thật, active_version phobert-B-2026-10-09, không fallback |
| npm run build real | Exit 0, VITE_USE_MOCK=false |
| npm run build mock | Exit 0, VITE_USE_MOCK=true |
| Focused | 45/45: 9 ca round1, 21 ca T29, 15 ca poster |
| Pytest toàn bộ cuối | 239/239 đạt, 0 lỗi, 148,49 giây; không cần ngoại lệ OBS-01 T27 |
| Giờ pytest cuối | 27/10/2026, 03:17:07–03:19:38, Asia/Saigon (UTC+07:00) |
| Scope / whitespace | Chỉ allowlist T29 + Icons.jsx được bổ sung ở mục 14; git diff --check không lỗi; không sửa :root/movies.json/package/lockfile/models.py |

Lượt full đầu 03:05:27–03:08:34: 234/234 đạt. Sau đó bổ sung các ca JSON sai cấu trúc/media type cho bộ chặn để giữ hành vi 422 cũ, chạy lại focused và full cuối như trên. Có cảnh báo DeprecationWarning từ Starlette/anyio; không thêm thư viện hoặc sửa thư viện để né cảnh báo.

Checklist hồi quy BOI_CANH_DU_AN mục 7 (dùng checklist đã biết trong phiên, không đọc thêm tài liệu ngoài phạm vi PO):

1. Real/mock hiện hero với 5 poster, animation chạy; Xem chi tiết và Đặt vé đều mở/đóng intro được.
2. Thể loại có 23 lựa chọn, chọn lọc vào Khám phá; tìm “meo muop” ra Mèo Mướp. Các lưới taxonomy không bị đổi bởi CSS mới.
3. UI đăng ký mới real/mock; bỏ token, bấm suất → đăng nhập; đăng nhập quay về đúng suất.
4. UI đặt hai ghế, Vé của tôi có vé mới; mở lại suất hai ghế disabled. Cuống trên Tài khoản hiện đúng mã từ API; badge giữ chỗ = 1.
5. Câu “Ko hay như quảng cáo, hơi thất vọng” được mô hình đánh giá tiêu cực: real 0,9992, mock 0,87; thông báo chính chủ hiện đúng. Trang kiểm duyệt admin thấy bình luận và điểm (UI real làm tròn 1,00, mock 0,87). Bình luận công khai không thêm khóa nội bộ.
6. Health phobert_b theo cấu hình model B hiện hành; không đổi về phobert A chỉ để khớp chữ trong checklist cũ.
7. Toàn bộ luồng trên đi bằng mock mode, không chỉ kiểm build.

Ngoài checklist: UI real/mock lưu ngày sinh/giới tính; email sai mật khẩu bị chặn, email mới chuẩn hóa và token cũ giữ; đổi mật khẩu chặn xác nhận không khớp và đăng nhập được bằng mật khẩu mới. Chọn ảnh, kéo thả, ảnh hiện ở hai khung và header, gỡ được. Ngày sinh chưa đủ tuổi vẫn chặn ghế; chưa khai vẫn nhắc giấy tờ và đặt được. Không pageerror trong phiên kiểm tra.

## 4. Cách ly dữ liệu và giới hạn giữ nguyên

- Backend riêng 8309, frontend real 5293/mock 5294. DATABASE_URL là `%TEMP%/firefly-T29-R1-20261027/runtime.db`; UPLOAD_DIR cùng thư mục tạm `/uploads`. Không dùng/ghi DB và uploads thật, không dừng server có sẵn của người dùng.
- Pytest đặt môi trường DATABASE_URL/UPLOAD_DIR trỏ TEMP trước import; fixtures SQLite và avatar dưới tmp_path. Probe oversized xác minh không ghi ảnh, không nới giới hạn để làm test xanh.
- Mẫu HTML/PNG PO giữ nguyên. Ảnh so sánh chỉ ghép cạnh nhau trong trình duyệt để nhìn hai thiết kế, không sửa nội dung ảnh nguồn.
- Không thêm schema DB. Hành vi T29 và giới hạn đã duyệt giữ nguyên: chưa khai ngày sinh vẫn đặt được; admin không bị chặn tuổi; không thư xác nhận email; activity khách vẫn dựa tối đa 3 bình luận và 5 điểm từ summary; refresh để nhận thao tác từ phiên khác. OBS-02/03/05 không được mở rộng thành công việc mới.
- Chờ Claude review độc lập R1-01..05 và AC-R1-01..08. Không tự PASS/PO_APPROVE/merge, không mở T13.

## 5. Ảnh và log

Ảnh và log ở workspace visualization ngoài Git; mẫu PO giữ nguyên. Ảnh khách chính là thẻ Vé & giao dịch; form được chụp ở thẻ Thông tin cá nhân, theo hành vi chuyển thẻ thật.

### So sánh cạnh mẫu v3

- [Mẫu v3 cạnh trang khách real, mỗi bên 1280px](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/comparison_v3_real_1280.png)
- [Mẫu v3 cạnh trang khách mock, mỗi bên 1280px](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/comparison_v3_mock_1280.png)
- [Mẫu v3 cạnh form Thông tin cá nhân real](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/comparison_form_v3_1280.png)

### Trang khách/admin

| Chế độ / Vai trò | 375px | 1280px |
|---|---|---|
| real / guest | [375px](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/account_real_guest_375.png) | [1280px](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/account_real_guest_1280.png) |
| real / admin | [375px](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/account_real_admin_375.png) | [1280px](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/account_real_admin_1280.png) |
| mock / guest | [375px](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/account_mock_guest_375.png) | [1280px](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/account_mock_guest_1280.png) |
| mock / admin | [375px](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/account_mock_admin_375.png) | [1280px](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/account_mock_admin_1280.png) |

### Các thẻ khách

| Chế độ / Thẻ | 375px | 1280px |
|---|---|---|
| real / ho-so | [375px](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/account_real_guest_ho-so_375.png) | [1280px](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/account_real_guest_ho-so_1280.png) |
| real / hoat-dong | [375px](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/account_real_guest_hoat-dong_375.png) | [1280px](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/account_real_guest_hoat-dong_1280.png) |
| real / chinh-sach | [375px](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/account_real_guest_chinh-sach_375.png) | [1280px](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/account_real_guest_chinh-sach_1280.png) |
| mock / ho-so | [375px](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/account_mock_guest_ho-so_375.png) | [1280px](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/account_mock_guest_ho-so_1280.png) |
| mock / hoat-dong | [375px](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/account_mock_guest_hoat-dong_375.png) | [1280px](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/account_mock_guest_hoat-dong_1280.png) |
| mock / chinh-sach | [375px](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/account_mock_guest_chinh-sach_375.png) | [1280px](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/account_mock_guest_chinh-sach_1280.png) |

### Menu

| Chế độ / Vai trò | 375 | 768 | 1024 | 1280 | 1366 | 1440 |
|---|---|---|---|---|---|---|
| real / guest | [375](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/menu_real_guest_375.png) | [768](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/menu_real_guest_768.png) | [1024](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/menu_real_guest_1024.png) | [1280](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/menu_real_guest_1280.png) | [1366](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/menu_real_guest_1366.png) | [1440](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/menu_real_guest_1440.png) |
| real / admin | [375](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/menu_real_admin_375.png) | [768](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/menu_real_admin_768.png) | [1024](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/menu_real_admin_1024.png) | [1280](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/menu_real_admin_1280.png) | [1366](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/menu_real_admin_1366.png) | [1440](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/menu_real_admin_1440.png) |
| mock / guest | [375](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/menu_mock_guest_375.png) | [768](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/menu_mock_guest_768.png) | [1024](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/menu_mock_guest_1024.png) | [1280](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/menu_mock_guest_1280.png) | [1366](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/menu_mock_guest_1366.png) | [1440](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/menu_mock_guest_1440.png) |
| mock / admin | [375](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/menu_mock_admin_375.png) | [768](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/menu_mock_admin_768.png) | [1024](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/menu_mock_admin_1024.png) | [1280](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/menu_mock_admin_1280.png) | [1366](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/menu_mock_admin_1366.png) | [1440](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/menu_mock_admin_1440.png) |

### Hạng và stress fixture

| Chế độ | 0 đ | Đúng ngưỡng Bạc | Vượt ngưỡng Vàng |
|---|---|---|---|
| real | [0 đ](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/rank_real_0_1280.png) | [1,000,000 đ](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/rank_real_1000000_1280.png) | [3,500,000 đ](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/rank_real_3500000_1280.png) |
| mock | [0 đ](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/rank_mock_0_1280.png) | [1,000,000 đ](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/rank_mock_1000000_1280.png) | [3,500,000 đ](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/rank_mock_3500000_1280.png) |

- [Tên người dùng 100 ký tự, tên phim 200 ký tự, không ảnh — 375px](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/stress_mock_375.png)
- [Cùng fixture — 1280px](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/stress_mock_1280.png)
- [Admin mock: hoạt động soát vé có tên phim](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/admin_mock_checkin_1280.png)

### Log máy đọc được

- [measurements.json](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/measurements.json)
- [rank-checks.json](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/rank-checks.json)
- [flows.json](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/flows.json)
- [mock-checkin.json](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/mock-checkin.json)
- [stress.json](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/stress.json)
- [health.json](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/health.json)
- [pytest-final.txt](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/pytest-final.txt)

- [admin-comment-checks.json](C:/Users/lemin/.codex/visualizations/2026/10/26/01a17979-426d-79a3-8353-4b1adff78951/T29-R1/admin-comment-checks.json) — điểm/API và dòng hiển thị trang kiểm duyệt real/mock.
