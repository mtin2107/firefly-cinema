# T28 — Báo cáo triển khai của Codex

- Bắt đầu: 26/10/2026; hoàn tất báo cáo: 27/10/2026, Asia/Saigon.
- Nhánh: `task/T28-giao-dien-tai-khoan`; baseline master `bca6d23911fb0bc1366f010daabe0d5c9ffa6b8e`.
- Vai trò: Primary Implementer. Trạng thái bàn giao: **CLAUDE_REVIEW**, chờ Claude kiểm tra độc lập.
- **Đổi schema: Không**.
- Không merge, không mở T13, không kết luận review hoặc tự đánh dấu PASS.

## Thay đổi

1. Quy tắc dùng chung cho mọi phim: line-height chữ Việt, giới hạn dòng/title tooltip, thẻ flex cao bằng nhau với tên/thể loại/điểm có vùng ổn định, phần cuối cao 48px; header nowrap và Menu ở <=1360px. Không có CSS/điều kiện theo tên hoặc id phim.
2. UI-04: một helper backend `effective_status` cung cấp cả giá trị và SQL CASE. `MovieOut.status`, SQL filter phim/chatbot, quyền chấm điểm (và bình luận qua require_rateable) đều dùng quy tắc này. Không UPDATE trạng thái DB. `stored_status` giúp admin giải thích tự chuyển; form real/mock từ chối Sắp chiếu ngày <= hôm nay. Frontend/mock chỉ có một helper ngày `effectiveStatus`.
3. FX: dừng tween khi rời sao; xóa transform khi disabled/giảm chuyển động; vùng bấm lớn hơn, grid 5 sao/hàng trên điện thoại. Banner không trailer dùng Poster nền + lớp đen + tiêu đề trắng, cao <=40vh; poster phụ hero ẩn tên/thể loại.
4. `CONTACT` trong config.js là nguồn duy nhất cho khối Liên hệ ở Footer; 2 cột desktop, 1 cột <=640px, link mailto/tel và aria-label tiếng Việt.
5. Endpoint `GET /api/auth/me/summary` có response model, lọc theo người gọi; thống kê đúng trạng thái, thể loại từ vé paid, 3 bình luận mới nhất kể cả hidden, 5 điểm gần nhất. Nhãn người duyệt ưu tiên nhãn model. Real/mock cùng khóa JSON, gồm cờ `hidden` cần cho nhãn Đã bị ẩn.
6. Account có hồ sơ/avatar chữ cái, 6 ô số liệu, vé gần đây từ bookings.mine, bình luận/điểm có link, và cài đặt. Giữ nguyên logic/thông báo form đổi họ tên/mật khẩu T14; lỗi tải số liệu không chặn form. Không thêm hiệu ứng số đếm nên reduced-motion không cần tween ở số liệu.

### Quyết định triển khai theo yêu cầu T28

- `line-height:1.15` chưa đạt probe canvas với font thực tế. Dùng **1.35** cho toàn bộ biến thể tiêu đề poster và chi tiết; vẫn giữ font/cỡ chữ, clamp poster 3 dòng. Số đo ở bảng dưới là lý do chọn giá trị cao hơn khoảng gợi ý 1.12–1.15.
- AC-13 yêu cầu tạo phim không poster qua admin; do đó bỏ yêu cầu poster bắt buộc của luồng cũ ở real/mock/form. Vẫn xác thực URL/file khi có ảnh. Test poster cũ được đổi đúng tình huống này.
- Test ratings cũ chỉ đổi status thành coming_soon nhưng giữ ngày đã qua. Đã sửa fixture của riêng test đó sang ngày mai để tiếp tục kiểm tra chặn phim thực sự sắp chiếu theo T28. Không sửa test_sentiment/OBS-01.
- ARCHITECTURE và CHANGELOG đã bổ sung endpoint, trạng thái hiệu lực và thay đổi poster tùy chọn.

## AC và số đo thực thi

Đây là kết quả triển khai/probe của Codex, không phải kết luận của Independent Reviewer.

| AC / lỗi | Kết quả đo hoặc probe |
|---|---|
| AC-01 / UI-01 | Canvas `ỦẦỘẾ`: 40 mẫu mỗi viewport, 0 mẫu vượt line-height. 375px: poster lớn 39/41.04px, tiêu đề chi tiết 45/47.52px; 1280px: poster lớn 53/56.16px, chi tiết 80/86.4px (glyph/line-height). Khoảng dư nhỏ nhất toàn mẫu 0.60px / 1.64px. Có ảnh Thứ Bảy Không Ngủ, Chuyến Tàu Cuối Mùa Mưa trong lưới/chi tiết. |
| AC-02 / UI-02 | Trang chủ + Khám phá, 62 thẻ đo qua 2 viewport; trong từng hàng, đỉnh thời lượng/điểm/thể loại/phần cuối và đáy thẻ chênh tối đa 0px ở 375, 0.03125px ở 1280. Khám phá trộn đang/sắp/ngừng chiếu. |
| AC-02b / UI-04 | 6 test trạng thái: ngày giả lập 15/06/2030, hôm qua/hôm nay/ngày mai cho now_showing/now_showing/coming_soon ở list, detail, SQL filter và chatbot. Chấm phim hôm qua/hôm nay được, ngày mai bị chặn; trạng thái lưu không đổi. Admin ngày hôm nay trả 422 đúng câu; ngày mai + không poster tạo được. Mock probe cùng kết quả và filter, rating ngày mai 400; chatbot dùng trạng thái hiệu lực. |
| AC-03 / UI-03 | Real/mock × có/không đăng nhập × 375/768/1024/1280/1440: không tràn ngang. Logo 35.84375px trên line 35.84px ở 375; 43.515625px trên line 43.52px ở các cỡ còn lại (làm tròn layout). Logo/nút tài khoản nowrap. Probe thêm họ tên 100 ký tự: không tràn ở toàn bộ 5 bề ngang. |
| AC-04 / FX-01 | Cùng mouseover →40ms→mouseout→400ms: baseline scale matrix(1.2,0,0,1.2,0,0) ở cả 375/1280; bản sửa nút mục tiêu transform none ở cả hai. |
| AC-05 / FX-02 | Nút rộng tối thiểu 57.390625px ở 375, 45px ở 1280; gap 4px. 375 có 2 hàng ×5; dialog clientWidth/scrollWidth 335/335, desktop 518/518. Đã chọn bằng bàn phím Enter, Esc bỏ lựa chọn chưa lưu, lưu 8 điểm đúng thông báo. |
| AC-06 / FX-03 | Không trailer: Poster nền tồn tại, banner 320px ở 1280×900 (<=360px=40vh), chữ #fff trên lớp đen opacity .82. Kể cả nền trắng, tương phản tính theo luminance >13.5:1, vượt 4.5:1. Fixture mock có trailer tạo đúng iframe youtube-nocookie với autoplay=1 sau click; không kiểm chứng chất lượng phát từ dịch vụ YouTube bên ngoài. |
| AC-07 / FX-04 | Probe real/mock: tên/thể loại poster không active đều visibility:hidden; poster active còn nguyên, hero/điều khiển chuyển phim giữ nguyên. |
| AC-08 | Fixture SQLite: 2 paid×80.000 +1 held +1 expired +1 rejected => bookings=3, paid=2, watched=1, spent=160.000, comments=4, ratings=1; favorite=Tâm lý. Trả 3 bình luận mới nhất, giữ hidden/anonymous; kiểm nhãn human=1 thắng model=false và human=0 thắng model=true. Không lộ bình luận/vé người B. 401 giống /me; tài khoản rỗng có toàn số 0/list rỗng/null. |
| AC-09 | Browser real/mock: đủ 5 khối, ảnh rỗng và có hoạt động ở 375/1280; đổi họ tên, đổi mật khẩu rồi đăng nhập lại bằng mật khẩu mới. Chủ động giả lập 500 summary: hiện lỗi tiếng Việt, nút/form lưu tên vẫn dùng được. |
| AC-10 | Real/mock cùng tập khóa ở summary/stats/recent_comments/ratings; số liệu tính từ dữ liệu của tài khoản mới qua luồng thật. Không có pageerror trong cả hai luồng. |
| AC-11 | Real/mock reduced-motion: 0 tween trên 10 nút sao, mọi transform none sau hover. Có probe lưu 9 điểm bằng bàn phím trong reduced-motion. Số liệu không tạo tween. |
| AC-12b / UI-05 | Footer trên các trang đã đi qua real/mock ở 375/1280; link đúng mailto:2311558892@nttu.edu.vn và tel:0329711217. rg xác nhận họ tên/email/số hiển thị/href chỉ khai báo trong config.js. |
| AC-13 | Tạo bằng form Quản lý phim thật trên SQLite tạm (lượt bằng chứng cuối id=24): tên đúng maxLength 200, 4 thể loại, không poster/trailer, Sắp chiếu ngày mai. Form ngày hôm nay báo lỗi ngay trước khi đổi sang ngày mai. Home tab Sắp chiếu, Khám phá, chi tiết ở 375/1280 không tràn. Khi còn Sắp chiếu, không có nút mở dialog (đúng chặn chấm); đổi chính phim đó sang Đang chiếu bằng form để đo dialog 335/335 và 518/518; trang chi tiết hiện câu chưa có suất. Mã id chỉ có trong probe/báo cáo, không có trong production rule. |

## Gate và môi trường

- Python/pytest từ venv hiện có; Node/Vite và Playwright có sẵn. Không cài thư viện.
- DATABASE_URL runtime: SQLite tạm `C:/Users/lemin/AppData/Local/Temp/firefly-t28-runtime.db`; UPLOAD_DIR cũng ở Temp. Test dùng DATABASE_URL riêng `.../firefly-t28-gates.db`, fixture pytest tạo SQLite riêng từng test.
- Cổng 8000 đã có tiến trình khác nên lần khởi động đầu bị bind error. Runtime T28 chuyển **127.0.0.1:8028**; frontend real dùng VITE_API_URL trỏ chính cổng này. Không lấy health cổng 8000 làm bằng chứng T28. Không khởi động hoặc điều khiển backend trên firefly.db; không reset/seed/ALTER/restore database thật.

| Gate | Kết quả |
|---|---|
| compileall backend/app | exit 0 |
| Backend khởi động + health 8028 | status=ok, classifier/active_model=phobert_b, version=phobert-B-2026-10-09, classifier_error=null |
| npm run build real | exit 0; 92 modules; JS 437.25kB, CSS 54.08kB |
| npm run build mock | exit 0; 92 modules; JS 462.30kB, CSS 54.08kB |
| Focused T28 sau chỉnh sửa cuối | 8 passed, 1 warning; 2.32s |
| Full pytest trước 0h | 209 passed, 1 warning; các lượt 182.39s và 159.44s |
| Full pytest cuối, sang 27/10 0h–7h | **208 passed, 1 failed**, 1 warning, 160.29s. Lỗi duy nhất: tests/test_sentiment.py::test_sentiment_uses_effective_label_group_by_and_complete_daily, dòng 91 — OBS-01 T27 được ngoại lệ tại AC-12. |
| Đối chiếu OBS-01 | Chạy đúng test trên bản sao source master bca6d23 trong Temp: cùng lỗi dòng 91, expected total=2/negative=1 của hôm nay nhưng actual=0/0 vì fixture lùi 1–2 giờ qua ngày trước. 1 failed, 0.49s. Không sửa hoặc bỏ qua test. |
| Mock/browser | Hoàn tất luồng mô tả ở mục hồi quy; không pageerror |
| Scope/secret/whitespace | File thay đổi thuộc mục 6, gồm 2 test cũ bị ảnh hưởng trực tiếp; không .env/*.db/model/CSV/package changes; movies.json/models.py/seed.py/:root không đổi; git diff --check exit 0 |

Warning pytest là DeprecationWarning từ Starlette/AnyIO hiện có.

## Checklist hồi quy BOI_CANH_DU_AN mục 7

1. Trang chủ, hero/điều khiển chuyển phim, PosterIntro khi đi theo link phim/Đặt vé: đã thực thi ở real/mock; poster phụ chỉ ẩn nội dung theo FX-04. Ảnh trước/sau và probe hero đính kèm.
2. Lọc Thể loại/Chủ đề và tìm không dấu `meo muop`: Đã bấm menu Thể loại → Tâm lý, Chủ đề → Top bình luận và dùng ô tìm kiếm trên header ở real/mock; kết quả tìm thấy Mèo Mướp Đi Lạc ở cả real/mock.
3. Chưa đăng nhập bấm suất → Đăng nhập → link Đăng ký → đăng ký mới → quay lại đúng `/dat-ve/{id}`: đã thực thi real/mock.
4. Chọn 2 ghế bằng UI → Tiếp tục → Đặt vé → Vé của tôi; mở lại cùng suất cả 2 ghế disabled: đã thực thi real/mock.
5. Gửi “Ko hay như quảng cáo, hơi thất vọng” bằng UI: effective_negative=true; admin API thấy score **0.9992** với PhoBERT B thật; mock 0.87. Account chính chủ vẫn đọc được nội dung và nhãn tiêu cực.
6. Health runtime tạm: phobert_b, version B đúng quyết định Q3 trong PROJECT_SOURCE_OF_TRUTH. Checklist cũ ghi literal phobert; không đổi cấu hình về model A chỉ để khớp chữ cũ.
7. VITE_USE_MOCK=true: build và trọn luồng đăng ký/đặt vé/chấm điểm/bình luận/tài khoản/đổi tên/mật khẩu đã thực thi.

## Bằng chứng và giới hạn bàn giao

- [Chỉ mục ảnh trước/sau từng lỗi, Account real/mock và AC-13](codex_evidence_T28_2026-10-27.md).
- Ảnh/probe nằm ngoài repo theo allowlist, liên kết bằng đường dẫn tuyệt đối trong chỉ mục; các số liệu quan trọng đã ghi trong report này để lưu trong Git.
- Lưu ý OBS-01 khi reviewer chạy sau nửa đêm; đã chứng minh trên master, không dùng làm lý do sửa ngoài scope.
- Playback trailer xác minh hành vi tạo iframe/autoplay; khả năng phát thực tế phụ thuộc YouTube/mạng.
- Chờ Claude chạy gate và review độc lập. PO giữ quyền duyệt/merge; T13 chưa được mở.
