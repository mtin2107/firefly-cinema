# Claude Implementation Report — T18 Chuyển động và hiệu ứng 3D

| Trường | Giá trị |
|---|---|
| Task | T18 — `docs/tasks/T18.md` |
| Nhánh | `task/T18-giao-dien-chuyen-dong` (tách từ `master` tại `fdaa7ac`) |
| Người code | Claude (Tín yêu cầu trong chat 13/10/2026) |
| Reviewer | **Codex** (đúng/sai: AC, scope, hồi quy) · Tín duyệt thẩm mỹ |
| Ngày | 13/10/2026 |
| Trạng thái đề xuất | `CODEX_REVIEW` |

## 1. Tóm tắt
Đã làm đủ M1–M8 và cả M9 tùy chọn. Không đụng backend, API, màu, font, chữ hiển thị hay luật ghế/vé. Chỉ thêm 2 thư viện `gsap@3.15.0` và `@gsap/react@2.1.2` (ghim chính xác) như PO đã duyệt.

| Commit | Nội dung |
|---|---|
| `67d6c4b` | Cài GSAP, `utils/motion.js`, token chuyển động, chuyển trang |
| `fe552e8` | Vi tương tác: nút, dropdown, gạch vàng trượt theo tab, tìm kiếm, khung chat |
| `3cd84b7` | `MovieGridSkeleton`, đèn đom đóm thay spinner |
| `f188989` | Thẻ phim nghiêng theo chuột, lưới hiện dần |
| `be663e2` | Hero băng chuyền 3D, bóng đèn chạy vòng, đom đóm canvas |
| `7091d02` | Poster bay sang trang chi tiết; xóa `PosterIntro.jsx` |
| `21d31ff` | Sơ đồ ghế phối cảnh phòng chiếu |
| `c4c490b` | Vé lật 2 mặt, hiệu ứng in vé + đom đóm bung |
| `9b19d31` | Parallax và quầng màu poster ở trang chi tiết |
| *(commit cuối)* | BOI_CANH mục 4 + mục 7 dòng 1, CONG_NGHE, ARCHITECTURE 1b, report |


## 2. Đối chiếu Acceptance Criteria

| AC | Kết quả | Bằng chứng |
|---|---|---|
| AC-01 Thư viện, build, dung lượng | **PASS** | `package.json` chỉ thêm `"@gsap/react": "2.1.2"`, `"gsap": "3.15.0"`. `npm run build` OK. JS gzip **80,41 KB → 134,11 KB (+53,70 KB ≤ 60 KB)**. CSS gzip 7,08 → 8,40 KB. |
| AC-02 Hero + đom đóm | **PASS** (phần tự động) | 5 slot; bấm Sau/Trước và phím → cho đúng phim, `Đặt vé` trỏ đúng `/phim/<id>#lich-chieu`; bấm nhanh 12 lần, tiêu đề luôn khớp. 21/21 tên phim trong `movies.json` ở dạng NFC; zoom ảnh xác nhận dấu đúng ("BẢN HÒA ÂM MÙA HẠ"). Đom đóm dừng vẽ khi khuất (IntersectionObserver) hoặc tab ẩn (theo code). |
| AC-03 Thẻ phim 3D | **PASS** | Hover: `rotateY(5.83°) rotateX(5.60°)` (tối đa ±8°). Đổi tab 10 lần nhanh → 5/5 thẻ trong khung nhìn về `opacity 1`. Nghiêng chỉ bật với `(hover: hover) and (pointer: fine)`. |
| AC-04 Poster bay | **PASS** | Bấm thẻ → `/phim/18`, poster về `matrix(1,0,0,1,0,0)`, chữ về `opacity 1`. "Đặt vé" → bay xong mới cuộn, `#lich-chieu` cách đỉnh 80px. Vào thẳng `/phim/3` → chỉ mờ dần. `grep PosterIntro\|intro__\|bubble-pop` → không còn. Ctrl/Cmd/Shift-click giữ hành vi Link gốc (theo code). |
| AC-05 Ghế 3D | **PASS** | Hit-test tâm ghế: 1280px **96/96** trúng. 375px **135/136**: ghế D9 bị nút chat nổi của T17 che (có sẵn, kéo nút đi được). Space chọn B2, Tab + Enter chọn B3. Mock: đặt B11, C1 thành công; real: đặt C7, C8, mở lại suất thấy 2 ghế đã khóa. Góc nghiêng cuối: **22° desktop, 12° dưới 768px**. |
| AC-06 Vé lật | **PASS** | Vé `held`: không có nút lật, QR và "Tôi đã chuyển khoản" vẫn dùng được. Sau khi báo chuyển khoản (`pending_verify`): Enter lật → focus sang "Lật lại", `front.inert=true`. Enter lật lại → focus về "Lật vé". Vé mới có `ticket--print` và canvas bung. |
| AC-07 Chuyển trang, skeleton | **PASS** | `.route-fade` chạy `route-in` (trang có `.summary-bar` chỉ mờ, không trượt). Khám phá: 8 khung skeleton → 9 thẻ phim. Gạch tab trượt `--ink-x` 0 → 126px. Dropdown chạy `dd-in`. |
| AC-08 Giảm chuyển động | **CẦN KIỂM TAY** | Công cụ trình duyệt của Claude không giả lập được `prefers-reduced-motion`. Code: mọi GSAP chặn bằng `prefersReduced()`/`MOTION_OK`; CSS có khối reduce cho hero, ghế, vé, cộng luật toàn cục sẵn có tắt mọi animation/transition. Codex/Tín bật DevTools → Rendering → `prefers-reduced-motion: reduce` để xác nhận. |
| AC-09 Hiệu năng, sạch | **PASS một phần** | Phiên real không có cảnh báo GSAP/React mới. Lỗi console duy nhất: 422 do Claude thử email đuôi `.test`. Rời trang giữa lúc bay/đổi tab không lỗi. **Chưa đo được long task do animation**: pane trình duyệt của Claude bị ẩn nên không vẽ khung hình (0 frame/6 giây). Cần ghi Performance 10 giây ở Trang chủ trên máy thật. |
| AC-10 Responsive, a11y | **PASS** | 375px: `scrollWidth 375 = innerWidth` ở Trang chủ (đã sửa tràn 22px của băng chuyền). 1280px trang chi tiết: 1265 ≤ 1280. Nút hero có `aria-label`, `aria-live`; slot không active có `tabIndex=-1`/`aria-hidden`; nút lật vé nhận focus thấy được. |
| AC-11 Hồi quy | **PASS** | Xem mục 3. |

## 3. Gate (`AGENT_RULES.md` 3.1)

| Gate | Kết quả |
|---|---|
| compileall backend | `COMPILE_OK` |
| Backend khởi động + health | Chạy trên **DB tạm** trong thư mục nháp của Claude (`DATABASE_URL=sqlite:///…/scratchpad/t18_gate.db`), **không** đụng `backend/firefly.db` thật (giữ gate T16 TODO-01). `/api/health` → `"status":"ok","classifier":"phobert_b"`, `phobert` vẫn `available:true`. |
| `npm run build` | OK, JS gzip 134,11 KB |
| pytest | `50 passed, 1 warning` (`--basetemp` trỏ vào thư mục nháp vì sandbox chặn thư mục tạm mặc định) |
| Mock mode | Hero, thẻ, skeleton, poster bay, chọn ghế, đặt vé, báo chuyển khoản, lật vé |
| Hồi quy 7 mục (real, DB tạm) | 1 ✓ hero 5 phim, "Xem chi tiết" → `/phim/9` · 2 ✓ Thể loại "Hài hước" 5 phim, Chủ đề "Phim hot trong tuần" 9 phim, "meo muop" → "Mèo Mướp Đi Lạc" · 3 ✓ đăng ký tài khoản test mới; khi chưa đăng nhập bấm giờ chiếu → `/dang-nhap` → đăng nhập → quay về `/dat-ve/2` · 4 ✓ đặt C7, C8; ghế khóa; vé mới trong Vé của tôi · 5 ✓ bình luận bị ẩn; admin thấy "Tiêu cực 1.00 · phobert_b" · 6 ✓ health · 7 ✓ mock |
| Scope | Xem mục 4 |
| Bí mật | Diff không có `.env`, `*.db`, model, CSV |

## 4. Scope
`git diff --stat master...HEAD` chỉ gồm file trong allowlist mục 6:
- `frontend/package.json`, `frontend/package-lock.json`
- `frontend/src/App.jsx`, `styles/global.css`, `utils/motion.js` (mới)
- Components: `FireflyField.jsx` (mới), `HeroCarousel.jsx` (mới), `MovieCard.jsx`, `SeatMap.jsx`, `StateViews.jsx`, `TicketStub.jsx`, `PosterIntro.jsx` (xóa)
- Pages: `Home.jsx`, `Explore.jsx`, `MovieDetail.jsx`
- Docs: `docs/BOI_CANH_DU_AN.md` (chỉ mục 4 và mục 7 dòng 1), `docs/CONG_NGHE.md`, `docs/ARCHITECTURE.md` (1b), `docs/TASK_COORDINATION_ACTIVE.md`, `docs/tasks/T18.md`, report này

Không sửa (dù allowlist có cho phép): `Header.jsx`, `Dropdown.jsx`, `SearchBox.jsx`, `ChatWidget.jsx`, `Poster.jsx`, `SeatSelection.jsx`, `MyTickets.jsx`. Chuyển động của các phần này làm bằng CSS. `.claude/launch.json` có thêm 2 cấu hình xem thử nhưng file này không được Git theo dõi, nên không nằm trong diff.

## 5. Quyết định khi triển khai (đề nghị Codex soát)

| # | Quyết định | Lý do | Cái giá nếu sai |
|---|---|---|---|
| D1 | Trang có `.summary-bar` (chọn ghế) chuyển trang chỉ mờ, không trượt 12px | `transform` ở tổ tiên làm thanh `position: fixed` nhảy theo khung trong lúc animate | Trang chọn ghế thiếu 12px trượt |
| D2 | Bỏ hiệu ứng tên phim nổi `translateZ` trên thẻ | `.poster` có `overflow: hidden` làm phẳng 3D | Thẻ ít chiều sâu hơn mô tả |
| D3 | `.hero3d__stage` dùng `overflow: clip`, không dùng `preserve-3d` | Poster bên cạnh làm trang tràn ngang 22px ở 375px; `zIndex` đã đặt thủ công nên không cần sắp xếp 3D | Poster xa bị cắt ở mép stage |
| D4 | Có `state.from` thì `scrollTo(0,0)` trước khi đo đích | App không tự đưa trang về đầu khi đổi trang (hành vi sẵn có), nên poster đích có thể nằm ngoài màn hình | Không |
| D5 | Ghế: bỏ `preserve-3d` lồng nhau và `translateZ` của ghế đang chọn; ghế chọn dùng `translateY(-3px) scale(1.06)` + glow | Hit-test 3D lồng nhau của Chrome làm cả hàng C bấm trượt (12/96 ghế). Sau khi sửa: 96/96 | Ghế chọn không nổi theo trục Z thật |
| D6 | `ticket-print` dùng `animation-fill-mode: backwards` | `both`/`forwards` giữ `transform` cuối, đè lên `rotateY(180deg)`, khiến vé mới không lật được | Không |
| D7 | Xóa `.spinner` và `@keyframes spin` | Không còn chỗ dùng sau khi `Loading` đổi sang đèn đom đóm | Không |
| D8 | `key={pathname}` cho khung chuyển trang | Cần remount để chạy lại animation vào trang. `/phim/1` → `/phim/2` giờ remount trang (trước đây dùng lại component); `/kham-pha?…` giữ nguyên vì cùng pathname | Mất state cục bộ khi đổi giữa 2 phim (ngày đang chọn, ô bình luận đang gõ) |

## 6. Giới hạn đã biết, đề xuất TODO
- **TODO-A (Low, a11y):** hero tự chuyển phim, chỉ dừng khi hover/focus/tab ẩn, chưa có nút "Tạm dừng" riêng. WCAG 2.2.2 khuyến nghị có cơ chế dừng rõ ràng cho nội dung tự chuyển quá 5 giây.
- **TODO-B (Low):** nút chat nổi (T17) có thể che ghế ở mép phải trên điện thoại (D9 ở 375px). Có sẵn từ trước, không do T18.
- **TODO-C (Medium, kiểm tay):** AC-08 và phần đo hiệu năng của AC-09 cần kiểm trên trình duyệt thật đang hiện. Đường lui khi máy chiếu yếu: bật "Giảm chuyển động" trong Windows; đom đóm cũng tự giảm một nửa khi FPS < 25 kéo dài.
- **Ghi chú:** trang admin bình luận hiện "Đang hiện" cho bình luận đã bị ẩn với khách. Đây là ngữ nghĩa có từ T06, T18 không đổi.

## 7. Ảnh chụp cho PO duyệt thẩm mỹ
Ảnh chụp lưu trong lịch sử phiên Claude (không đưa vào repo). Mời Tín chạy `npm run dev` và xem trực tiếp:
1. Trang chủ desktop: hero băng chuyền, chữ bật sáng, bóng đèn chạy vòng, đom đóm.
2. Trang chủ 375px: băng chuyền nằm trên chữ.
3. Rê chuột qua thẻ phim; đổi tab Đang chiếu/Sắp chiếu.
4. Bấm một thẻ → poster bay; bấm "Đặt vé" → bay rồi cuộn tới lịch chiếu.
5. Chọn ghế: phòng chiếu nghiêng, ghế chọn sáng lên.
6. Vé của tôi: vé mới in ra; báo chuyển khoản rồi bấm "Lật vé".

## 8. Prompt cho Codex review (theo `AGENT_RULES.md` 6.3, đổi vai)
```text
Bạn là Codex, Independent Reviewer cho T18 của Firefly Cinema (task này Claude code theo yêu cầu của PO).
Đọc: docs/PROJECT_SOURCE_OF_TRUTH.md, docs/AGENT_RULES.md, docs/TASK_COORDINATION_ACTIVE.md, docs/tasks/T18.md,
reports/2026-10-13/claude_implementation_T18_2026-10-13.md, rồi `git diff master...task/T18-giao-dien-chuyen-dong`.
Đối chiếu AC-01..AC-11, allowlist mục 6, quyết định D1–D8 ở mục 5 của report.
Chạy gate AGENT_RULES.md 3.1 độc lập. Backend chỉ chạy trên DB tạm (DATABASE_URL trỏ ra file khác), KHÔNG chạy trên backend/firefly.db thật.
Tự kiểm AC-08 (DevTools → Rendering → prefers-reduced-motion: reduce) và đo Performance 10 giây ở Trang chủ cho AC-09.
Không sửa production code. Probe tạm phải xóa trước gate cuối.
Kết luận PASS / PASS_WITH_TODO / FAIL (RF-xx có Severity, File, Problem, Evidence, Expected Fix).
Tạo reports/<YYYY-MM-DD>/codex_review_T18_<RESULT>_<YYYY-MM-DD>.md và cập nhật file điều phối (PASS → PO_REVIEW, FAIL → FIX_LOOP).
```

---

## Fix Round 1 (13/10/2026)

Nguồn: `reports/2026-10-13/codex_review_T18_FAIL_2026-10-13.md` (FAIL, AC-05/08/10, RF-01 → RF-03). Chỉ sửa 3 RF, không xử lý TODO-01 → TODO-03, không thêm thư viện, không đụng backend/API/DB/dữ liệu phim.

**Commit sửa:** `4b9b122` — `[T18] Fix Round 1: RF-01 chat khong che ghe, RF-02 reduced-motion dong, RF-03 nut tam dung hero`

### RF-01 — Ghế mobile bị nút chat che → FIXED
**Cách sửa**
- `ChatWidget.jsx` (chỉ phần vị trí): trên route `/dat-ve/*`, vị trí mặc định của nút chat là góc phải dưới, nằm trong thanh tổng tiền cố định (`.summary-bar`). Ghế không bao giờ nằm dưới vùng này, vì thanh đã che sẵn và trang có `padding-bottom` để cuộn ghế lên trên thanh.
- Nếu người dùng kéo nút trên trang này thì theo vị trí kéo, cho tới khi đổi trang. Logic kéo, chạm để mở, lưu vị trí của T17 giữ nguyên.
- `global.css`: `.summary-bar` chừa `padding-right` 72px (≤1320px) và 62px (≤600px), để nút "Tiếp tục", tổng tiền và danh sách ghế không nằm dưới nút chat.

**Bằng chứng**
| Kiểm | Kết quả |
|---|---|
| 375px, quét toàn vùng cuộn: cuộn trang dọc từng 20px × cuộn sơ đồ ngang từng 20px, `elementFromPoint` tại tâm mọi ghế nằm giữa header và thanh tổng tiền | **30.064 lần đo, 96/96 ghế trúng đúng button, 0 lần trúng `.chat-widget`** |
| 1280px, quét dọc từng 20px | **1.440 lần đo, 96/96 ghế trúng, 0 bị che** |
| Nút chat so với các phần tử của thanh (375 và 1280) | Không chồng lên `summary-bar__seats`, `summary-bar__total`, nút "Tiếp tục" |
| Vị trí mặc định | 375px: nút ở y = 756, đỉnh thanh ở 669. 1280px: nút ở y = 738, đỉnh thanh ở 716 |
| Kéo và mở chat | Kéo (pointer 100px) → nút di chuyển, **không** mở panel; chạm (click `detail: 1`) → mở panel; vị trí lưu `localStorage` như cũ |
| Rời trang rồi quay lại | Trang chủ dùng vị trí đã lưu (y = 536); vào lại `/dat-ve/2` thì nút về chỗ mặc định trong thanh (y = 756) |
| Tràn ngang | 375px: `scrollWidth 375`; 1280px: 1265 |

### RF-02 — Reduced-motion thay đổi động → FIXED
**Cách sửa**
- `utils/motion.js`: thêm hook `useReducedMotion()`. Hook lắng nghe `change` của `matchMedia("(prefers-reduced-motion: reduce)")` và gỡ listener khi unmount. Thay toàn bộ chỗ đọc snapshot `prefersReduced()` trong component.
- `HeroCarousel.jsx`:
  - effect autoplay phụ thuộc `reduced`: bật reduce thì cleanup `kill` `delayedCall`;
  - effect slot: bật reduce thì `killTweensOf` và `clearProps` transform/opacity/zIndex, để CSS reduce chỉ hiện poster đang chọn;
  - SplitText: `revertOnUpdate` theo `reduced`.
- `FireflyField.jsx`: bật reduce thì **không render canvas**; effect cũ dọn RAF, ResizeObserver, IntersectionObserver, visibility listener và tia bung.
- `SeatMap.jsx`: hiện hàng ghế dùng `revertOnUpdate` theo `reduced`, nên bật reduce giữa chừng thì hàng ghế hiện ngay.
- `MovieDetail.jsx`:
  - poster bay và parallax phụ thuộc `reduced` với `revertOnUpdate`, và xóa transform của poster trước mỗi lần chạy lại (revert của tween scrub không luôn trả transform về trống);
  - hiệu ứng vào trang chỉ chạy một lần mỗi phim; cuộn tới `#lich-chieu` chỉ một lần mỗi phim, kể cả khi reduce bật giữa lúc poster đang bay.
- Lưới phim và thẻ nghiêng vốn đã dùng `gsap.matchMedia()` (Task 4), nên giữ nguyên.

**Bằng chứng.** Công cụ trình duyệt của Claude không giả lập được media. Probe tạm chỉ chạy trong trang, không ghi file, đã gỡ bằng cách nạp lại trang: vá getter `MediaQueryList.prototype.matches` cho 2 truy vấn reduce/no-preference, bắt các listener `change` mà ứng dụng và `gsap.matchMedia` đăng ký (25 listener), rồi bắn `change`. Số `delayedCall` đếm bằng chính instance `gsap` của ứng dụng (`await import('/src/utils/motion.js')`).

| Bước | Trang chủ | Trang chi tiết `/phim/2` | Chọn ghế |
|---|---|---|---|
| Trước | tiêu đề tách 13 ký tự; 5 slot có transform; 1 canvas; nút Tạm dừng có; **1** timer autoplay | 1 ScrollTrigger; poster đang animate | hàng ghế đang hiện dần |
| Bật reduce khi đang chạy | 0 ký tự tách; 5 slot không transform; **0 canvas**; nút Tạm dừng ẩn; **0** timer; 9/9 thẻ phim `opacity 1` | **0** ScrollTrigger; poster không transform; chữ `opacity 1` | 8/8 hàng `opacity 1 visible`; vẫn chọn được ghế A1 |
| Tắt reduce | 1 canvas; nút có lại; tách 13 ký tự; slot zIndex `10,9,8,8,9`; **1** timer | 1 ScrollTrigger; không chạy lại hiệu ứng vào trang | hiệu ứng hiện hàng chạy lại một lần |
| Bắn `change` lặp lại | vẫn **1** timer (không nhân đôi) | vẫn 1 ScrollTrigger | — |

Giới hạn: CSS `@media (prefers-reduced-motion: reduce)` không bị probe kích hoạt. Phần CSS (ẩn slot phụ, tắt transition/animation) đã có từ vòng trước và Codex đã xác minh ở fresh-load reduce.

### RF-03 — Hero thiếu nút tạm dừng → FIXED
**Cách sửa**
- `HeroCarousel.jsx`: thêm nút trong cụm điều khiển hero. Nhãn hiển thị "Tạm dừng"/"Tiếp tục" kèm biểu tượng `❚❚`/`▶` (`aria-hidden`), `aria-label` "Tạm dừng tự chuyển phim"/"Tiếp tục tự chuyển phim".
- Theo mẫu carousel của WAI-ARIA APG: đổi nhãn thay vì `aria-pressed`. Nhãn hiển thị nằm trong `aria-label` nên đạt SC 2.5.3.
- Cờ `user` trong `paused` ưu tiên cao nhất: rời chuột, rời focus hay bấm Trước/Sau đều không tự chạy lại. Hover, focus, tab ẩn và reduce vẫn dừng như cũ.
- Bật reduce thì không có autoplay nên ẩn nút.
- `global.css`: style `.hero3d__pause` (dạng viên thuốc, dùng biến màu có sẵn), `.hero3d__nav` cho phép xuống dòng.

**Bằng chứng**
| Kiểm | Kết quả |
|---|---|
| Bấm Tạm dừng | Nhãn "Tiếp tục", `aria-label` "Tiếp tục tự chuyển phim", `delayedCall.paused() = true` |
| Rời chuột khỏi hero, chuyển focus ra ngoài | vẫn `paused = true` |
| Bấm "Phim sau" khi đang dừng | phim đổi sang "Mèo Mướp Đi Lạc", timer mới vẫn `paused = true` |
| Bấm Tiếp tục, focus ở ngoài hero | `paused = false` |
| Bàn phím | Focus nút, nhấn Enter → đổi sang "Tiếp tục"; viền focus `solid rgb(255,199,44)` |
| 375px | Cụm ‹ 01/05 › Tạm dừng nằm trong hero (x 40 → 332, hero 14 → 361), `scrollWidth 375` |

### File thay đổi (Fix Round 1)
`frontend/src/components/ChatWidget.jsx`, `FireflyField.jsx`, `HeroCarousel.jsx`, `SeatMap.jsx`, `frontend/src/pages/MovieDetail.jsx`, `frontend/src/styles/global.css`, `frontend/src/utils/motion.js` (7 file, +90/−27); cộng report này và `docs/TASK_COORDINATION_ACTIVE.md`. Tất cả thuộc allowlist T18 mục 6. `ChatWidget.jsx` chỉ đổi phần vị trí, không đổi gọi API.

### Full gates sau sửa
| Gate | Kết quả |
|---|---|
| compileall | `COMPILE_OK` |
| Backend + health | Uvicorn với `DATABASE_URL` trỏ SQLite tạm trong thư mục nháp của Claude, đã xóa sau kiểm. `/api/health` → `status ok`, `classifier phobert_b` |
| DB thật | SHA-256 `backend/firefly.db` = `b3f7df79bda4478412200ea80b8ec15e6b73da730068a52e11c40136eac4cfe3`, khớp số Codex ghi trước review, không đổi |
| Frontend build | OK; JS gzip **134,47 KB**, CSS gzip 8,48 KB. So với mốc master Codex đo (85,29 KB): +49,18 KB ≤ 60 KB |
| pytest | `50 passed, 1 warning` |
| Self-check `motion.js` | `motion ok` |
| Mock mode | hero, nút Tạm dừng, chọn ghế, kéo/mở chat, poster bay, reduce probe |
| Real mode, hồi quy 7 mục | 1 ✓ 5 slot + nút Tạm dừng, "Xem chi tiết" → `/phim/9` · 2 ✓ "meo muop" → "Mèo Mướp Đi Lạc", Hài hước 5 phim · 3 ✓ chưa đăng nhập bấm giờ chiếu → `/dang-nhap`; đăng ký tài khoản test; đăng nhập lại → về đúng `/dat-ve/13` · 4 ✓ đặt D7 + D8, vé "Giữ chỗ" trong Vé của tôi, mở lại cả 2 ghế bị khóa · 5 ✓ bình luận bị ẩn; admin thấy "Tiêu cực · 1.00 · phobert_b" · 6 ✓ health · 7 ✓ mock |
| Console | Không có lỗi GSAP/React mới; 2 `ERR_CONNECTION_REFUSED` do frontend nạp trước khi backend nạp xong model |
| Scope / bí mật / whitespace | Chỉ file allowlist; không có `.env`, `*.db`, model, CSV, `backend/`, `src/api/`; `git diff --check` OK |

### AC sau Fix Round 1
| AC | Kết quả |
|---|---|
| AC-01 | PASS (134,47 KB; +49,18 KB so với mốc Codex) |
| AC-02 | PASS (thêm nút Tạm dừng; autoplay, phím, vuốt giữ nguyên) |
| AC-03 | PASS (không đổi) |
| AC-04 | PASS (không đổi; reduce giữa chừng không cuộn 2 lần) |
| AC-05 | **PASS**: 96/96 ghế ở 375px (30.064 lần đo, toàn vùng cuộn) và 1280px |
| AC-06 | PASS (không đổi) |
| AC-07 | PASS (không đổi) |
| AC-08 | **PASS phần JS/GSAP bằng probe**: bật/tắt reduce khi trang đang chạy dừng/khôi phục autoplay, 3D, đom đóm, parallax, poster bay, hiện ghế, không nhân đôi. Đề nghị Codex xác minh lại bằng `emulateMedia` thật |
| AC-09 | PASS (không có tween/timer/RAF/ScrollTrigger dư sau khi đổi reduce) |
| AC-10 | **PASS**: nút Tạm dừng/Tiếp tục truy cập được; 375/1280 không tràn |
| AC-11 | PASS (real + mock) |

### Required Fix còn lại
**0 RF mở theo đánh giá của Claude.** RF-01 → RF-03 ở trạng thái FIXED, chờ Codex xác minh độc lập ở Round 2. TODO-01 → TODO-03 giữ nguyên để PO quyết định.

### Prompt cho Codex review Round 2
```text
Bạn là Codex, Independent Reviewer cho T18 của Firefly Cinema — Round 2.
Đọc: docs/TASK_COORDINATION_ACTIVE.md, docs/tasks/T18.md, reports/2026-10-13/codex_review_T18_FAIL_2026-10-13.md,
mục "Fix Round 1" trong reports/2026-10-13/claude_implementation_T18_2026-10-13.md, rồi `git diff eb254ce..4b9b122` và `git diff master...task/T18-giao-dien-chuyen-dong`.
Xác minh RF-01 (hit-test toàn bộ ghế 375/1280 trên toàn vùng cuộn, kéo/mở chat), RF-02 (emulateMedia reducedMotion bật/tắt khi trang đã mount:
autoplay, slot 3D, canvas đom đóm, parallax/poster bay, hiện ghế; không nhân đôi timer/RAF/tween), RF-03 (nút Tạm dừng/Tiếp tục, bàn phím, không tự chạy lại).
Chạy lại gate AGENT_RULES.md 3.1 trên SQLite tạm, không dùng backend/firefly.db thật. Không sửa production code; xóa probe trước gate cuối.
Tạo reports/<YYYY-MM-DD>/codex_review_T18_<RESULT>_<YYYY-MM-DD>_round2.md và cập nhật file điều phối (PASS → PO_REVIEW, FAIL → FIX_LOOP).
```
