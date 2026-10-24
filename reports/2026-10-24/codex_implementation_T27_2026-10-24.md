# Codex Implementation Report

Task: T27 — Thang điểm 10 và khung đánh giá có hiệu ứng
Date: 2026-10-24
Result: IMPLEMENTATION_COMPLETED — chờ Claude review độc lập
Branch: `task/T27-thang-diem-10`; baseline master `ea79fe6` (chứa T26 merge `c1916c6`).
Đổi schema: Có — `ck_rating_stars CHECK (stars BETWEEN 1 AND 10)`.

## Files Changed
- Backend: models.py, schemas.py, seed.py, routers/ratings.py; tests/test_ratings.py, tests/test_t23_dashboard_checkin.py.
- Frontend: api/mock.js; components/RatingDialog.jsx, StarRating.jsx, CommentSection.jsx; pages/MovieDetail.jsx, AdminDashboard.jsx; utils/ratings.js; styles/global.css (chỉ rating).
- Tài liệu: ARCHITECTURE.md, HUONG_DAN.md, CHANGELOG.md, TASK_COORDINATION_ACTIVE.md và report này.

## Implemented / Architecture / Contract
- Điểm nguyên strict 1–10 cho rating và bình luận, CHECK SQLite; lỗi biên/type có câu “Điểm phải từ 1 đến 10.” trong detail tiếng Việt theo handler hiện hữu.
- PUT/DELETE rating và GET my-rating trả `stars`, `rating_avg`, `rating_count`, `distribution` đủ khóa chuỗi 1..10. Không đổi đường dẫn hay luật ai được chấm.
- Seed real/mock cùng công thức 6 + ((movie.id + index) % 5); namespace mock v6 tránh dùng lại seed thang 5. Dashboard giữ công thức cũ.
- ratingText có `/10`; bình luận `★ 8/10`; dashboard `/ 10`; nhãn cá nhân `Bạn đã chấm 8/10`. Nhãn 10 mức dùng chung trong ratings.js.
- Dialog native: Poster nền/fallback, ✕, vòng conic-gradient, 5 nhóm phân bố, 10 sao 28px, nhãn chữ, thanh Đóng/Lưu và Hủy khi đã chấm. Draft không ghi API cho đến khi lưu.
- GSAP qua motion.js: mở 300ms, hover, nảy stagger, 8/18 đom đóm, vòng điểm và thanh phân bố chạy 700ms, xác nhận rồi đóng 1,2s. Chỉ MOTION_OK; cleanup khi đóng/unmount/đổi reduced motion. Lớp hạt aria-hidden và cắt tràn riêng.
- T26 TODO-01 đã xử lý ở implementation: focus không thay preview/tô sao; chờ reviewer xác minh đóng TODO.

## Focused Tests / Acceptance Evidence
- AC-01/02: nhận 1/10; từ chối 0/11/5.5/"8"/bool, cả rating và comment; CHECK chặn ghi 11; lifecycle upsert/delete, đủ 10 khóa, tổng count, trung bình 5.5 với điểm 1 và 10.
- AC-03: so sánh toàn bộ tuple movie/user/stars trên hai SQLite mới độc lập; mọi điểm 6–10; restart vẫn bảo toàn thao tác xóa điểm.
- Test dashboard dùng điểm 10. Sửa fixture suất 23:59 thành ngày hôm sau: chạy sát cutoff 30 phút đã khiến held bị expire, gây KeyError trong test cũ; không đổi production booking/dashboard.
- AC-04/05/09/10: Chrome real 5270 + mock 5271 ở 375/1280. 10 nút đều 28px; clientWidth/scrollWidth dialog lần lượt 335/335 và 518/518. Trong lúc hạt bay: dialog 335/335, document 375/viewport 375. Contract rating real/mock cùng bốn khóa, phân bố 10 khóa.
- AC-06/08: khách bấm điểm → đăng nhập → quay lại; chọn/lưu/hủy; Esc, ✕, backdrop không lưu; focus trả về trigger, Tab/Shift+Tab giữ trong modal; focus sao chưa chọn có 0 sao active. Phim sắp chiếu không có trigger. Bình luận chấm 8 hiển thị `★ 8/10`.
- AC-07: chọn 2 sinh 8 hạt, chọn 10 sinh 18; sau 2s = 0; lưu đóng và trả focus. Emulate reduce trước mở và đổi no-preference → reduce khi đang mở: không còn hạt/chuyển động, vẫn lưu được. Vòng/nhãn/điểm cập nhật; không có pageerror trong lượt browser cuối trên real/mock.

## Final Gates
| Gate | Kết quả |
|---|---|
| compileall backend/app | exit 0 |
| Backend startup + health | SQLite tạm `%TEMP%/firefly-t27-runtime.db`, UPLOAD_DIR tạm; status ok, classifier phobert_b, version phobert-B-2026-10-09, không fallback |
| SQLite schema/integrity | CHECK BETWEEN 1 AND 10, integrity ok |
| Full pytest | **201 passed**, 1 warning deprecation Starlette/AnyIO hiện hữu |
| npm run build real + mock | cả hai exit 0, không thêm dependency |
| Browser 375/1280 real/mock + reduced motion | đạt DEV; ảnh dưới đây |
| Whitespace / scope | git diff --check sạch; 19 file trong allowlist |

## Checklist hồi quy BOI_CANH mục 7
1. Trang chủ có phim; autoplay chuyển 01 → 02 sau khoảng 6s; Xem chi tiết và Đặt vé đều mở PosterIntro: đạt real/mock.
2. Menu Thể loại → Hành động; tìm “meo muop” ra Mèo Mướp: đạt real/mock. Không đổi taxonomy.
3. Đăng ký mới qua form thành công; luồng khách bấm giờ chiếu → đăng nhập → quay lại đúng /dat-ve/21 và khách bấm điểm → quay lại phim: đạt real/mock; bảo vệ API/showtime vẫn qua full suite.
4. Chọn hai ghế, xác nhận đặt, Vé của tôi có vé; mở lại suất thấy hai ghế disabled: đạt real/mock (DB tạm/browser storage riêng).
5. Bình luận “Ko hay như quảng cáo, hơi thất vọng” được che bằng thông báo tiêu cực; admin thấy nội dung và score **0.9992** với model thật. Mock cùng luồng che bình luận, score giả **0.87** theo classifier mock hiện hữu.
6. Health đạt với **phobert_b**, đúng quyết định model B hiện hành; checklist cũ ghi phobert là tên model A.
7. Mock hoạt động đủ luồng rating, comment, booking, dashboard: đạt.

## Ảnh kiểm chứng
Ảnh nằm ngoài Git để tuân thủ allowlist chỉ cho report Markdown; đường dẫn local bên dưới dùng để PO/reviewer xem trên máy này.

| Chế độ / kích thước | Mở | Chọn | Lưu |
|---|---|---|---|
| Real 375px | [Mở](C:/Users/lemin/.codex/visualizations/2026/10/24/01a16eb7-259c-7242-b90b-ad3b31086a1e/T27/t27-5270-375-open.png) | [Chọn](C:/Users/lemin/.codex/visualizations/2026/10/24/01a16eb7-259c-7242-b90b-ad3b31086a1e/T27/t27-5270-375-select.png) | [Lưu](C:/Users/lemin/.codex/visualizations/2026/10/24/01a16eb7-259c-7242-b90b-ad3b31086a1e/T27/t27-5270-375-save.png) |
| Real 1280px | [Mở](C:/Users/lemin/.codex/visualizations/2026/10/24/01a16eb7-259c-7242-b90b-ad3b31086a1e/T27/t27-5270-1280-open.png) | [Chọn](C:/Users/lemin/.codex/visualizations/2026/10/24/01a16eb7-259c-7242-b90b-ad3b31086a1e/T27/t27-5270-1280-select.png) | [Lưu](C:/Users/lemin/.codex/visualizations/2026/10/24/01a16eb7-259c-7242-b90b-ad3b31086a1e/T27/t27-5270-1280-save.png) |
| Mock 375px | [Mở](C:/Users/lemin/.codex/visualizations/2026/10/24/01a16eb7-259c-7242-b90b-ad3b31086a1e/T27/t27-5271-375-open.png) | [Chọn](C:/Users/lemin/.codex/visualizations/2026/10/24/01a16eb7-259c-7242-b90b-ad3b31086a1e/T27/t27-5271-375-select.png) | [Lưu](C:/Users/lemin/.codex/visualizations/2026/10/24/01a16eb7-259c-7242-b90b-ad3b31086a1e/T27/t27-5271-375-save.png) |
| Mock 1280px | [Mở](C:/Users/lemin/.codex/visualizations/2026/10/24/01a16eb7-259c-7242-b90b-ad3b31086a1e/T27/t27-5271-1280-open.png) | [Chọn](C:/Users/lemin/.codex/visualizations/2026/10/24/01a16eb7-259c-7242-b90b-ad3b31086a1e/T27/t27-5271-1280-select.png) | [Lưu](C:/Users/lemin/.codex/visualizations/2026/10/24/01a16eb7-259c-7242-b90b-ad3b31086a1e/T27/t27-5271-1280-save.png) |

## Security / Scope / Blockers
- Không sửa `.env`, `firefly.db`, model, `:root`, task record hay file ngoài allowlist; không thêm thư viện. Backend riêng chỉ dùng SQLite/UPLOAD_DIR tạm; không dùng backend thật đang có ở port 8000.
- Không merge, không mở T13, không tự kết luận review PASS hay PO approve.
- Blocker kỹ thuật: 0. `HUONG_DAN.md` có quy trình PO dừng backend → backup DB/sidecar/uploads → so hash/integrity → reset sau merge.

## Required Follow-up / Handoff
Claude review độc lập T27. PO sau duyệt/merge thực hiện backup/reset DB thật theo HUONG_DAN mục T27; chưa thực thi reset trong phiên này. T27 chuyển CLAUDE_REVIEW; T13 tiếp tục chờ T27.
