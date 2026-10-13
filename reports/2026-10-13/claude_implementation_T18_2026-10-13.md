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
