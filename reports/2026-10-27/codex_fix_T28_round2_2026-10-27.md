# T28 — Fix Round 2 — R2-01, R2-02

- Ngày: 27/10/2026, Asia/Saigon (UTC+07:00).
- Nhánh: `task/T28-giao-dien-tai-khoan`; baseline `00c5bdf7896abaa0e98c500338113109462d3758`, working tree sạch trước sửa.
- Phạm vi: yêu cầu PO ở T28 mục 14, tuân thủ nguyên tắc chung mục 4.0.
- **Đổi schema: Không**.
- Trạng thái bàn giao: **CLAUDE_REVIEW**, chờ Claude xác minh độc lập. Không tự review/PASS, không merge, không mở T13.

## Thay đổi

### R2-01 — Tên dài một hàng, chỉ chạy khi tràn

`frontend/src/components/MovieCard.jsx`:

- Giữ đúng một bản tên phim trong DOM, trong link ở h3 có `title` đầy đủ. Không thêm bản sao trang trí hoặc nội dung lặp cho trình đọc màn hình.
- Đo độ tràn bằng `link.scrollWidth - link.clientWidth`; chỉ tạo timeline khi kết quả >0. `ResizeObserver` đo lại khung, đồng thời đo sau khi font sẵn sàng/tải xong.
- Dùng GSAP hiện có: tốc độ 40px/giây theo khoảng cách thực tế, dừng 1,5 giây ở cuối, trở về đầu rồi dừng 1,5 giây trước vòng tiếp. Cảm ứng có thêm thời gian dừng 1,5 giây lúc bắt đầu.
- Với `(hover: hover)`: mặc định đứng yên/ellipsis; pointer vào thẻ hoặc focus vào bất kỳ link/nút trong thẻ thì chạy. Khi không còn hover lẫn focus trong thẻ, timeline bị hủy, x trở về đầu và khôi phục ellipsis.
- Không có hover: tự chạy nếu tràn. Không kiểm tra tên/id/slug hoặc dùng ngưỡng độ dài ký tự để quyết định.
- GSAP matchMedia theo dõi cả reduced motion và khả năng hover. Khi giảm chuyển động, đổi tiêu đề hoặc tháo component, dọn timeline/observer/listener; không còn transform chạy chữ.

`frontend/src/styles/global.css`:

- Tên bình thường chiếm đúng 1 dòng, bỏ vùng tên cao 2 dòng. Chỉ span đang chạy dùng inline-block/transform; vùng nhìn luôn cố định, không làm rộng thẻ.
- Reduced motion: tối đa 2 dòng, vùng tên 2 dòng để các hàng còn lại vẫn căn nhau; chữ đầy đủ vẫn nằm trong DOM.
- Không sửa tên in trên poster hoặc `.detail__title`; không sửa :root.

### R2-02 — Khôi phục chữ poster phụ

Chỉ bỏ cặp selector `visibility:hidden` áp lên tên/thể loại của poster không active ở hero. Không sửa `HeroCarousel.jsx` hoặc `utils/motion.js`; giữ nguyên hiệu ứng chuyển phim, SplitText bật sáng tên hero, quy tắc reduced motion sẵn có.

Production chỉ sửa **MovieCard.jsx và global.css**. Ngoài ra chỉ report này và TASK_COORDINATION_ACTIVE.md theo yêu cầu. Không thêm thư viện, không sửa backend/test/JSON phim.

## Kiểm chứng theo AC vòng 2

Các kết quả dưới đây là probe thực thi của Codex, chờ Claude xác minh; không phải kết luận review.

| AC | Kết quả |
|---|---|
| AC-R2-01 — 1280px có chuột | Tên tràn đứng yên trước hover; hover làm x thay đổi; rời thẻ x=0/transform none. Focus link poster cũng chạy (probe x=-15.28px), blur ra ngoài về đầu. Thẻ vừa khung x=0, không có class/timeline chạy chữ. Probe tên hợp lệ 200 ký tự: x từ -0.84 đến -25.04px trong 605.5ms, tương đương **39.967px/giây**. Chỉ một span tên, textContent=title đủ 200 ký tự; chiều cao tên **23.515625px**, line-height 23.52px. |
| AC-R2-01 — 375px cảm ứng | Browser isMobile/hasTouch, `(hover: hover)=false`: tự chạy không cần chạm thẻ. Trace lấy mẫu theo performance.now: bắt đầu chuyển động khoảng **1578ms**, tốc độ **39.996px/giây**, dừng cuối **1472ms**, dừng đầu **1499ms**, sau đó tiếp tục vòng mới. 9 tên vừa khung không có tween active, transform none. Tên 200 ký tự cũng chạy, đo **40.363px/giây**, chỉ chiếm 1 dòng. |
| Đo lại ResizeObserver | Khi link đang overflow/focus được mở rộng thành 1000px: scrollWidth=clientWidth=1000, chữ dừng/x=0. Trả khung về kích thước cũ: tự đo lại, nhận overflow và chạy lại khi vẫn focus. |
| AC-R2-02 — Reduced motion | Đổi chế độ ngay khi đang chạy ở cả chuột và cảm ứng: tất cả **21 tên** mỗi viewport không có tween active, transform none, không tràn ngang. Mỗi tên tối đa 2 dòng, vùng cao **47.03125px** trên line-height 23.52px. Tên fixture 200 ký tự cũng giữ đủ DOM, clamp 2 dòng và dừng. |
| AC-R2-03 — Căn hàng | Đo **124 thẻ** qua trang chủ + Khám phá × real/mock × 375/1280. Trong từng hàng, đỉnh thời lượng/điểm/thể loại/phần cuối và đáy thẻ chênh tối đa **0px ở 375**, **0.03125px ở 1280**. Tên một dòng ở mọi thẻ; cả 8 trang/viewports không tràn ngang. |
| AC-R2-04 — Hero | 1280 và 1440: trước sửa tên poster phụ hidden; sau sửa cả **8 phần tử tên/thể loại** của 4 poster phụ đều visibility visible. Bấm Phim sau đổi tiêu đề/phim active; SplitText vẫn tạo **13 ký tự** trên tiêu đề tiếp theo. Có ảnh trước/sau cả hai bề ngang. Source HeroCarousel nguyên vẹn so với baseline. |
| AC-R2-05 — Gate/mock | Build real/mock exit 0; browser real gọi backend DB tạm, mock chạy với VITE_USE_MOCK=true. Không có pageerror trong probe chuyển động. Các gate bên dưới đã chạy. |

Việc đo khoảng dừng cảm ứng dùng trace trong trình duyệt (lấy mẫu khoảng 80ms), nên số quan sát gần 1,5 giây có sai số lấy mẫu. Tốc độ được tính theo thời gian thực tế, không theo thời gian chờ của công cụ.

## Gate và môi trường

- Backend riêng: `127.0.0.1:8030`, DATABASE_URL=`sqlite:///C:/Users/lemin/AppData/Local/Temp/firefly-t28-round2-20261027-0040.db`; UPLOAD_DIR ở Temp. Không kết nối/đọc/ghi/reset backend/firefly.db.
- Frontend mock port 5190, VITE_USE_MOCK=true; frontend real port 5191, VITE_USE_MOCK=false và VITE_API_URL trỏ 8030.
- Pytest DATABASE_URL riêng `.../firefly-t28-round2-pytest.db`; fixture tạo SQLite tạm từng test.
- Dùng thư viện/Playwright/Edge có sẵn; probe/script/PNG/JSON chỉ lưu ngoài repo.

| Gate | Kết quả |
|---|---|
| compileall backend/app | exit 0 |
| Backend khởi động + /api/health ở 8030 | status=ok, classifier/active_model=phobert_b |
| npm run build real | exit 0; 92 modules; JS 438.75kB, CSS 54.48kB |
| npm run build mock | exit 0; 92 modules; JS 463.80kB, CSS 54.48kB |
| pytest toàn bộ | **00:41:06–00:42:24, 27/10/2026 +07:00**; **208 passed, 1 failed, 1 warning**, 75.58s, exit 1. |
| Lỗi duy nhất | `tests/test_sentiment.py::test_sentiment_uses_effective_label_group_by_and_complete_daily`, dòng 91, actual total/negative=0/0 thay vì 2/1 do fixture lùi 1–2 giờ sang hôm trước. Đúng OBS-01 T27, chạy trong 0h–7h, thuộc ngoại lệ PO cho phép. Không sửa/skip/xóa test; không có lỗi khác. |
| Scope và whitespace | git diff --check exit 0. HeroCarousel.jsx, utils/motion.js, :root, models.py/seed.py, JSON phim và package files không đổi. Chỉ hai production file được phép sửa theo mục 14. |

Warning hiện có là DeprecationWarning của Starlette/AnyIO. Không sửa vấn đề ngoài R2-01/R2-02.

## Ảnh và probe

Ảnh/probe nằm ngoài repo để giữ đúng allowlist; số đo chính đã chép vào report này.

| Hero | Trước | Sau |
|---|---|---|
| 1280px | [Trước](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/hero-before-1280.png>) | [Sau](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/hero-after-1280.png>) |
| 1440px | [Trước](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/hero-before-1440.png>) | [Sau](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/hero-after-1440.png>) |

| Trang/chế độ | 375px | 1280px |
|---|---|---|
| real / home | [375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/real-home-375.png>) | [1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/real-home-1280.png>) |
| real / explore | [375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/real-explore-375.png>) | [1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/real-explore-1280.png>) |
| mock / home | [375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/mock-home-375.png>) | [1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/mock-home-1280.png>) |
| mock / explore | [375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/mock-explore-375.png>) | [1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/mock-explore-1280.png>) |
| Reduced motion | [375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/reduced-375.png>) | [1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/reduced-1280.png>) |
| Tên 200 ký tự, reduced | [375](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/long-title-reduced-375.png>) | [1280](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/long-title-reduced-1280.png>) |

Probe gốc:

- [motion.json](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/motion.json>)
- [touch-timing.json](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/touch-timing.json>)
- [touch-short.json](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/touch-short.json>)
- [touch-reduced-all.json](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/touch-reduced-all.json>)
- [long-title.json](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/long-title.json>)
- [long-title-mobile.json](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/long-title-mobile.json>)
- [alignment.json](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/alignment.json>)
- [hero-before.json](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/hero-before.json>)
- [hero-after.json](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round2/hero-after.json>)

Chờ Claude kiểm tra source/gate và xác minh độc lập trước khi PO quyết định bước tiếp theo.
