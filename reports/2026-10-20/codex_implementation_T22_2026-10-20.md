# Codex Implementation Report — T22

- Task: T22 — Chấm sao, bình luận ẩn danh và hoàn thiện trải nghiệm người xem
- Date: 2026-10-20
- Result: IMPLEMENTATION_COMPLETED — chờ Claude Independent Review
- Nhánh: `task/T22-cham-sao-an-danh`
- Baseline: `master` tại `cdc9bdd` (dependency merge T14 `42c8269` là ancestor, đã kiểm chứng).
- **Đổi schema: Có. Phải xóa `backend\firefly.db` rồi khởi động lại để seed schema mới. PO thực hiện sau backup/checksum/integrity/restore checkpoint theo HUONG_DAN; Codex chưa reset hoặc khởi động DB thật.**

## Files Changed / Implemented

- Backend: models/schemas/seed/main, routers movies/comments và ratings mới; `backend/tests/test_ratings.py` mới.
- Frontend: real/mock API, StarRating mới, CommentSection, HeroCarousel, MovieCard, TicketStub, ChatWidget (chỉ vị trí), MovieDetail/SeatSelection/Explore/Home/MyTickets/Login/Register/AdminComments; utils ratings/pageTitle và class CSS mới. Các trang còn lại chỉ thêm tiêu đề tab.
- Tài liệu: HUONG_DAN, ARCHITECTURE, điều phối và report này. Không sửa Task Record PO đã duyệt.
- Hoàn thành chấm sao thật, ẩn danh, xóa bình luận, các BUG-1/2/3/4/6, vị trí chatbot và ba cách sắp xếp lưu URL.

## Architecture / Contract

- UNIQUE(user_id,movie_id), CHECK stars 1–5; SQLite upsert nguyên tử và timestamps. Một GROUP BY + LEFT JOIN cho danh sách, **1 câu SQL cho 4 phim** trong test; điểm phim lồng trong vé/suất lấy bằng SQL aggregate cùng SELECT. Điểm trống 0/0; làm tròn SQL nhất quán (4,25 → 4,3). ORM cascade dọn ratings khi admin xóa phim.
- GET my-rating, PUT/DELETE rating, DELETE comments theo Task Record; comment POST nhận object content/is_anonymous/stars. Thao tác sao dùng chung limiter 20/phút/người, kể cả POST kèm sao; comment limiter/PhoBERT/kiểm duyệt cũ giữ nguyên.
- Public thêm `is_anonymous`, `author_stars`, `can_delete` (boolean quyền của phiên, không có định danh tác giả). Admin thấy tên thật. Không lộ user_id/email trong public JSON. `author_stars` là điểm hiện tại, cập nhật cả bình luận cũ khi chấm lại/hủy.
- Hai dãy sao đồng bộ tại MovieDetail, khóa trong lúc gửi để tránh POST ghi đè điểm mới khi hai thao tác đang chạy. Phím Tab/Enter/Space qua button chuẩn, aria-label/aria-pressed, hover/focus preview và thông báo lưu/hủy.
- Mock v4 có cùng tập khóa JSON cho mine/set/create/remove và cùng mã lỗi; tính từ ratings mẫu, không đọc score. Seed mới có 2 điểm/phim now_showing/ended theo công thức cố định; restart không khôi phục điểm đã hủy. Giữ kịch bản T12.

## Focused Tests / Final Gates

| Gate | Bằng chứng |
|---|---|
| compileall | `backend\venv\Scripts\python -m compileall -q backend\app`: exit 0; chạy lại trên app trước full suite cũng exit 0 |
| Focused T22 | `venv\Scripts\python -m pytest -q tests/test_ratings.py --basetemp=tests/.t22-pytest-temp`: **17 passed**, exit 0 |
| Toàn bộ pytest | Từ backend: `venv\Scripts\python -m pytest -q --basetemp=tests/.t22-final-temp`: **115 passed**, exit 0 (98 test cũ + 17 mới), 75,38s |
| Backend thật | Uvicorn cổng 8022, DATABASE_URL trỏ SQLite tạm `backend/tests/t22-runtime.db`, ACTIVE_MODEL=phobert; khởi động được, health 200, classifier=phobert, active_version=A-backend, classifier_error=null |
| Build real/mock | `VITE_USE_MOCK=false` và `true`, `npm run build`: cả hai exit 0, 87 modules |
| Trình duyệt | Chrome headless dùng Playwright có sẵn trong runtime; Vite real 5222/mock 5223, không cài thư viện. UI/API/normal-motion probes dưới đây chạy cả hai chế độ; không có pageerror |
| Format/scope/security | `git diff --check` sạch; chỉ file trong mục 6, không dependency mới hoặc file bí mật/model/DB được stage |

Cảnh báo test còn lại: Starlette dùng alias BlockingPortal đã deprecated (có từ trước). Lần chạy ban đầu pytest gặp cảnh báo cleanup TEMP của Windows; lần cuối dùng basetemp riêng, không còn lỗi cleanup. Lần gọi pytest đầu từ root không có module app, đã chạy đúng từ backend như hướng dẫn.

## Bằng chứng từng Acceptance Criterion

| AC | Kết quả triển khai và bằng chứng |
|---|---|
| AC-01 | UI real/mock: khách bấm sao → login → quay về `/phim/1?demo=t22#lich-chieu`; chọn 2 sao ở đầu trang, dãy sao form đồng bộ; reload giữ aria-pressed=true. Thông báo lưu và điểm tổng cập nhật. `test_rating_lifecycle` xác minh lưu lại qua API/DB. |
| AC-02 | UI bấm lại 2 sao → thông báo hủy, aria-pressed=false; chọn 4 sao từ form bằng Enter. Pytest đặt 3→5 chỉ 1 dòng; thêm người thứ hai count=2, hủy còn 1, hủy lần nữa 200. Test DB trùng UNIQUE và stars=6 đều IntegrityError. |
| AC-03 | Khách đọc điểm và được chuyển login khi bấm sao, trở lại đủ query/hash. Pytest GET/PUT/DELETE không token 401, phim thiếu 404, 7 giá trị sao sai 422; coming_soon PUT/DELETE/POST 400 tiếng Việt, ended vẫn nhận điểm/bình luận. UI coming_soon không có StarRating/textarea. |
| AC-04 | Thẻ, hero, chi tiết, lịch chiếu, chọn ghế hiển thị điểm thật hoặc “Chưa có đánh giá”. Rà source chỉ còn result.score ở trang so sánh model admin, không còn movie.score cho người xem. Browser đối chiếu phim hero đầu với rating_avg/count; menu Chủ đề “Đánh giá cao” chỉ có >=4. Test nested showtime/booking và GROUP BY một câu SQL cho 4 phim đạt. |
| AC-05 | UI chọn sao ở form rồi gửi bình luận ẩn danh, cạnh bình luận hiện 4 sao. Test POST sao 5 ghi đè sao 3 và DB vẫn chỉ 1 dòng; chấm lại 2/hủy thì author_stars lần lượt 2/null. |
| AC-06 | Public JSON tên “Khán giả ẩn danh”, cờ true, không user_id/email/tên thật; pytest so với admin tên thật. UI real/mock đăng ký “T22 Viewer”, đăng ẩn danh, login admin → hàng kiểm duyệt hiện “T22 Viewer · Ẩn danh”. Câu hồi quy PhoBERT thật score **0.9937**, effective_negative=true, UI ẩn mặc định và có “Vẫn xem”. Suite kiểm duyệt/thống kê/CSV cũ đạt. |
| AC-07 | Nút xóa chỉ cho chủ qua can_delete; UI hỏi xác nhận rồi xóa, danh sách cập nhật. API chủ nhận `{ok:true}`; người khác (kể cả admin qua endpoint public) 404, không token 401; xóa lặp 404. |
| AC-08 | BUG-1: tiêm lỗi cancel/claim vào API adapter trong browser, cả hai hiện alert tại chỗ và số vé không đổi (real 6/mock 4 ở lần probe cuối). BUG-2: chỉ sửa created_at của vé DB tạm/localStorage để còn 5 giây; thấy Còn 00:0x, sau 6 giây tự reload thành hết hạn, không QR/claim. BUG-3: đã login truy cập dang-nhap/dang-ky tự về home. BUG-4: title phim theo dữ liệu, Vé của tôi và mọi trang có title riêng. BUG-6: login và register đều trở lại đủ query/hash. Chatbot và Tiếp tục không giao nhau theo bounding rectangles ở 375/1280. |
| AC-09 | Browser chọn lần lượt Tên A–Z/Đánh giá cao/Mới nhất; đối chiếu toàn bộ thứ tự DOM với danh sách API được sort độc lập. URL sap-xep giữ đúng sau reload; đổi sort không gọi tải lại danh sách phim. |
| AC-10 | Toàn bộ UI smoke/BUG probes/normal-motion/sort chạy real và mock. Probe JSON mine/set/comment/delete có tập khóa giống hệt; lỗi cùng `[422,422,400,404,401]`; đặt/ghi đè/hủy idempotent/count và anonymous author_stars/can_delete đúng. Mock score giả lập 0.87 được ghi rõ, không giả là PhoBERT. |
| AC-11 | 17 pytest mới: lifecycle, invalid 7 trường hợp, auth/missing/coming_soon/ended, anonymous public/admin + ownership, DB constraints, rate 429, aggregate một query/nhiều phim, delete movie cascade, seed deterministic/restart preserve removal, rounding và nested movie. Full 115/115 đạt. |
| AC-12 | Hồi quy 7 mục bên dưới; browser đo scrollWidth<=innerWidth tại phim, Khám phá, vé, chọn ghế ở 375/1280 cho cả real/mock. 375/375 và 1280/1280. Đã chụp và xem trực tiếp ảnh trang phim 375/1280; bố cục sao/điểm/bình luận không tràn. Ảnh/probe tạm được dọn, mô tả bước là bằng chứng theo AC. |

## Checklist hồi quy — BOI_CANH_DU_AN mục 7

1. Home có phim/hero; normal motion tự chuyển sau 6 giây. Cả “Xem chi tiết” và “Đặt vé” mở PosterIntro, Esc đóng đúng. Real/mock đạt.
2. Menu Thể loại → Hài hước lọc đúng, Chủ đề → Đánh giá cao dùng điểm thật; tìm “meo muop” ra Mèo Mướp. Real/mock đạt.
3. Chưa login vào suất bị đưa login; đăng nhập/đăng ký trở về đủ pathname/search/hash. Real/mock đạt.
4. Chọn 2 ghế A1/A2 → Tiếp tục → Đặt vé → Vé của tôi có vé giữ chỗ; mở lại đúng suất thấy cả hai nút disabled. Real/mock đạt.
5. Câu “Ko hay như quảng cáo, hơi thất vọng” bị ẩn mặc định; PhoBERT thật 0.9937, admin vẫn đọc/kiểm duyệt được. Mock dùng classifier mô phỏng 0.87.
6. Health 200, classifier phobert, không fallback. Database thật không được khởi động.
7. Mock chạy đủ các luồng, build và contract đối chiếu đạt.

## Security / Scope / Blockers / Follow-up

- Security: các gate quyền/ẩn danh/rate limit/ràng buộc DB đạt. Không sửa normalize(), classifier.py, seats hoặc biến màu :root; không thêm npm/pip dependency.
- Out-of-scope changes: NO. Không sửa .env, DB thật, model hay dữ liệu ML. SHA-256 DB thật trước/sau: `E9817891E6AB905D418E1460D23EABB03CB96F497DB7DEAED61E5351E64CA364`.
- Dừng server tạm và dọn SQLite/sidecar, ảnh, script browser và thư mục test tạm sau gate; chỉ test_ratings.py được giữ trong Git.
- Blockers: 0 về triển khai. Required Follow-up: PO backup/xác minh rồi reset DB thật theo HUONG_DAN trước khi chạy schema T22 trên dữ liệu local. Không tự làm thao tác này.
- TODO mới: 0. Giới hạn đã được PO chốt: người đăng nhập chưa cần mua vé để chấm; limiter chỉ trong một process, reset khi restart như cơ chế có sẵn.

## Handoff

T22 → **CLAUDE_REVIEW**. Đề nghị Claude chạy review/gate độc lập và kiểm từng AC. Không tự review/PASS task, merge, đóng T22 hoặc mở T23.
