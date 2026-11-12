# Claude implementation — T32 Menu mới (12/11/2026)

- **Người làm:** Claude, theo lệnh PO trong chat 12/11/2026 ("Codex đã hết hạn, phần này để bạn gánh toàn bộ").
- **Nhánh:** `task/T32-menu-moi`, từ master `c581ab7`.
- **Cần review độc lập:** có. Claude vừa viết vừa tự kiểm nên không tự PASS. Người review: Codex khi có lại, hoặc Tín.

## 1. Đã làm
| ID | Kết quả |
|---|---|
| UI-01 | `FireflyLogo` (SVG đom đóm 2 cánh, đuôi sáng nhấp nháy, bay nhẹ khi rê chuột) trong `Icons.jsx`, thay đốm sáng CSS |
| UI-02 | Menu Phim 4 cột: Trạng thái (Đang chiếu, Sắp chiếu), Thể loại (3 cột con), Quốc gia + Năm phát hành, Chủ đề. Dùng lại `FILTERS`/`exploreLink` |
| UI-03..05 | Link thẳng Lịch chiếu `/lich-chieu`, Giá vé `/gia-ve`, Ưu đãi `/uu-dai` |
| UI-06 | Menu Thành viên: Hạng thành viên (`/uu-dai#hang-thanh-vien`), Vé của tôi, Tài khoản của tôi, Đăng ký thành viên (khi chưa đăng nhập) |
| UI-07 | Nút "Mua vé ngay" → `/lich-chieu`, vệt sáng 3,6 s, icon vé lắc khi rê chuột. Ẩn ở ≤520px để header không xuống thêm hàng |
| UI-08 | Icon mới `receipt`, `gift`, `crown`; icon nảy khi rê chuột, gạch chân vàng trượt từ giữa ra (≥1361px). Rule chung `prefers-reduced-motion` có sẵn tắt toàn bộ |
| PG-01..03 | `Schedule.jsx`, `Prices.jsx`, `Offers.jsx` + route trong `App.jsx` |
| BE-01 | `GET /api/showtimes?date=` + `ScheduleOut`; `api.showtimes.list` ở `real.js` và `mock.js` cùng cấu trúc |

**Lệch so với demo đã duyệt:** ở ≥1361px nút "Đăng ký" góc phải bị ẩn (vẫn có trong menu Thành viên và trang Đăng nhập) vì 5 mục có icon cộng nút Mua vé làm tràn khung 1180px. Từ ≤1360px giữ như cũ.

**Không làm:** khuyến mãi giảm giá thật (hệ thống chưa tính giảm giá khi thanh toán), ghế đôi. Trang Ưu đãi chỉ hiện dữ liệu có thật: hạng thành viên và phim sắp chiếu.

## 2. Bằng chứng
| AC | Kết quả | Bằng chứng |
|---|---|---|
| AC-01 | PASS | Header real 1440px: logo, 5 mục có icon, nút Mua vé; mọi link tới trang có route |
| AC-02 | PASS | Menu Phim 44 link, link đầu `/kham-pha?trang-thai=dang-chieu`; cao 346px ở 1440px |
| AC-03 | PASS | `test_t32_schedule.py` 3/3; real DB tạm: 83 suất, lọc `2026-11-12` → 4 suất cùng ngày, `date=abc` → 422 "Trường 'date' không hợp lệ: Giá trị không hợp lệ."; khóa JSON real = mock (`id, movie_id, start_time, room, price, movie`) |
| AC-04 | PASS | Mock: 7 tab ngày, `?ngay=` đổi đúng, ngày 17–18/11 hiện thông báo trống; link suất `/dat-ve/:id`. Real: 4 phim/4 suất hôm nay |
| AC-05 | PASS | 75.000/95.000 đ → VIP 95.000/115.000 đ (= `VIP_SURCHARGE` 20.000) |
| AC-06 | PASS | 3 hạng Thành viên/Bạc/Vàng theo `MEMBERSHIP`, 1 phim sắp chiếu (real); link `#hang-thanh-vien` cuộn tới mục |
| AC-07 | PASS | Enter mở menu Phim (`aria-expanded=true`), Esc đóng và trả focus về nút; mọi icon `aria-hidden="true"` |
| AC-08 | PASS | `scrollWidth = clientWidth` ở 375/768/1280/1440px; 375px đã đăng nhập: header 1 hàng (giữ T31 AC-05); menu Phim ở 375px không link nào tràn |
| AC-09 | PASS | `compileall` exit 0; `pytest` **289 passed**; `npm run build` real và `VITE_USE_MOCK=true` đều built; health `classifier: phobert_b` |

## 3. Phạm vi file
Production: `backend/app/routers/movies.py`, `backend/app/schemas.py`, `frontend/src/App.jsx`, `frontend/src/api/{real,mock}.js`, `frontend/src/components/{Header,Icons}.jsx`, `frontend/src/pages/{Schedule,Prices,Offers}.jsx`, `frontend/src/styles/global.css` (không đổi `:root`).
Test/tài liệu: `backend/tests/test_t32_schedule.py`, `docs/tasks/T32.md`, `docs/TASK_COORDINATION_ACTIVE.md`, `docs/ARCHITECTURE.md`, `CHANGELOG.md`, report này. Đều trong allowlist. Không có DB, model, `.env`, `data/`. `Bao_cao/` (chưa track từ trước) không đụng tới.

## 4. Schema
Không đổi. Không cần xóa `firefly.db`.

## 5. Rủi ro cho người review
- Header ≥1361px rất sát khung: tên người dùng dài đã có `max-width` + ellipsis, nhưng nên kiểm tra thêm với admin tên dài.
- Menu Phim ở điện thoại cao khoảng 1.100px (23 thể loại); trước đây cũng dài như vậy khi mở lần lượt từng menu cũ.
- `Footer` vẫn dùng chữ, chưa gắn logo SVG (không bắt buộc).

## 6. Vòng sửa 1 — PO xem thử (12/11/2026)
PO chụp header ở màn ~1240px CSS (laptop 125%): menu bị gom vào nút "Menu", thanh header trống. Yêu cầu: để các mục ở ngoài.

- Mốc gom menu hạ từ ≤1360px xuống ≤1100px (khớp `Dropdown.canHover` vốn dùng 1101px). Khối CSS header cũ và khối T32 cùng đổi.
- 1101–1360px: logo 1.4rem, khoảng cách mục 7px, nút còn "Mua vé" (chữ "ngay" ẩn), tên tài khoản tối đa 150px có "…". Icon menu giữ nguyên.
- Menu Phim canh theo mép trái khung header (`.nav > .dd:first-child` static) để không tràn ở 1101px; rê chuột từ nút xuống menu vẫn giữ mở.
- Ẩn nút "Đăng ký" góc phải từ ≥1101px (trước là ≥1361px).

Kiểm tra: real đã đăng nhập ở 1101/1120/1180/1240/1241/1440px và mock chưa đăng nhập ở 1101/1440px: header 1 hàng (68px), không tràn khung, không tràn ngang; menu Phim 20→952px ở 1101px; menu Thành viên và tài khoản trong màn hình. 1100px vẫn gom vào "Menu"; 375px menu Phim không link nào tràn. `npm run build` real + mock đạt. Lần sửa này chỉ đụng `Header.jsx` và `global.css`; backend không đổi nên không chạy lại pytest (lần trước 289/289).
