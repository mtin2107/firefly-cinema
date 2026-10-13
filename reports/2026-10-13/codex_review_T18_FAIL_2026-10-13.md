# Codex Independent Review — T18 — FAIL

| Trường | Giá trị |
|---|---|
| Task | T18 — Chuyển động và hiệu ứng 3D |
| Nhánh | `task/T18-giao-dien-chuyen-dong` |
| Baseline | `master` tại `fdaa7acc0f2ff71d3ff99ee47d92eedde32fa283` |
| Bản review | `4ceac74c4ec1edf5edf7baaa6a42130f8d39c2a0` trước khi thêm report |
| Reviewer | Codex — Independent Reviewer / Tester |
| Ngày | 13/10/2026 |
| Kết luận | **FAIL** |

## 1. Kết luận

T18 chưa đủ điều kiện chuyển sang PO_REVIEW. Có **3 Required Fix mức Medium**:

1. Một ghế trong vùng thao tác ở 375px bị nút chat nổi che, nên AC-05 không đạt. Claude gặp D9; lần đo độc lập của Codex gặp C9. Việc mã ghế thay đổi theo vị trí cuộn không làm thay đổi kết luận: vẫn có ghế không nhận được click ở tâm.
2. Khi đổi `prefers-reduced-motion` sang `reduce` trong lúc trang đang mở, hero vẫn tự chuyển; các hiệu ứng đọc media query một lần thay vì phản ứng qua `gsap.matchMedia()`. AC-08 không đạt.
3. Hero tự cập nhật vô hạn mỗi 6 giây nhưng không có cơ chế pause/stop độc lập. Hover/focus chỉ tạm dừng khi người dùng giữ chuột/focus trong hero, không phải cơ chế pause dùng được trong khi tiếp tục thao tác trang. Đây là Required Fix accessibility, không hạ thành TODO.

Không sửa production code trong review. Ba probe trình duyệt tạm đã được xóa. Backend chỉ chạy với `C:\Users\lemin\AppData\Local\Temp\firefly_t18_codex_review.db`; file tạm đã xóa. `backend/firefly.db` thật giữ nguyên SHA-256 trước/sau: `B3F7DF79BDA4478412200EA80B8EC15E6B73DA730068A52E11C40136EAC4CFE3`.

## 2. Acceptance Criteria

| AC | Kết quả | Bằng chứng review độc lập |
|---|---|---|
| AC-01 | **PASS** | Diff `package.json` chỉ thêm đúng `gsap@3.15.0` và `@gsap/react@2.1.2`, ghim chính xác. Registry: phát hành lần lượt 13/04/2026 và 15/01/2025, đều hơn 2 tuần trước ngày cài. Build T18: JS gzip `134,11 KB`. Build độc lập từ worktree `master`: `85,29 KB`; tăng `48,82 KB` ≤ `60 KB`. Con số baseline `80,41 KB` trong report Claude không tái lập được nhưng không đổi kết luận PASS. |
| AC-02 | **PASS** | 5 poster; autoplay đổi phim sau 6,3 giây; hover và focus giữ nguyên phim qua 6,3 giây; phím phải và vuốt đổi đúng phim; link hero cập nhật theo phim giữa; Ctrl-click mở tab mới. 21/21 tiêu đề trong `movies.json` là NFC. Source có visibility listener và IntersectionObserver. |
| AC-03 | **PASS** | Tilt chỉ đăng ký với `(hover: hover) and (pointer: fine)`. Đổi tab 10 lần rồi cuộn lưới vào viewport: 4/4 thẻ quan sát được đều `opacity: 1`, transform về identity. D2 được ghi TODO vì bỏ `translateZ` của tên phim so với mô tả M3. |
| AC-04 | **PASS** | Card `/phim/5` điều hướng đúng `/phim/5`, poster kết thúc ở transform identity; URL trực tiếp `/phim/3` chỉ fade/scale nhẹ. Source truyền `state.from`, giữ modifier-click, cuộn `#lich-chieu` ở callback hoàn tất. `PosterIntro.jsx` bị xóa và không còn import/CSS `.intro*`. |
| AC-05 | **FAIL** | 1280px: 96/96 tâm ghế trúng đúng button. 375px: 95/96; C9 bị `.chat-widget__toggle` che trong probe Codex. Report Claude cũng ghi 135/136 và D9 bị che. Tab/Space chọn A1 thành công; real mode đặt C7+C8 thành công và mở lại thấy cả hai disabled. Góc 22° desktop, 12° mobile. Xem RF-01. |
| AC-06 | **PASS** | Real mode: vé `held` có nút “Tôi đã chuyển khoản”, không có nút lật; môi trường không cấu hình ngân hàng nên dùng fallback thay QR. Sau xác nhận `paid`, Enter lật: `ticket--flipped=true`, mặt trước `inert=true`, `aria-hidden=true`, mặt sau `inert=false`, focus sang “Lật lại”; Enter lần nữa trả focus về “Lật vé”. |
| AC-07 | **PASS** | Skeleton xuất hiện khi mock đang chờ; route/dropdown/tab/search/chat có CSS motion tương ứng. Rapid tab không kẹt opacity/transform. |
| AC-08 | **FAIL** | Fresh load với reduce: autoplay dừng và slot active không có transform. Nhưng bật reduce khi trang đã mount: tiêu đề đổi từ “Đội Bóng Xóm Chài” sang “Đội Cứu Hộ Sông Hồng” sau 6,3 giây. `HeroCarousel`, `FireflyField`, `SeatMap`, `MovieDetail` dùng `prefersReduced()` snapshot; không đáp ứng nguyên tắc “mọi GSAP qua `gsap.matchMedia()`”. Canvas vẫn tồn tại ở fresh-reduce dù không vẽ. Xem RF-02. |
| AC-09 | **PASS** | PerformanceObserver 10,5 giây sau khi trang ổn định: `0` long task, max `0 ms`. Đổi qua lại Home/Explore 8 lần không có page error/GSAP/unmount error. Console chỉ có hai React Router future warnings và 404 favicon vốn không do T18. Cleanup `useGSAP`, delayedCall, RAF, ResizeObserver, IntersectionObserver, listener và timeout đều có đường dọn. |
| AC-10 | **FAIL** | 375/768/1280: `scrollWidth === innerWidth`, không tràn ngang; focus global nhìn thấy được; tiếng Việt/NFC đạt. Tuy nhiên hero autoplay không có pause/stop dùng độc lập, không đạt yêu cầu accessibility; xem RF-03. AC-05 cũng chứng minh khả năng thao tác mobile chưa đầy đủ. |
| AC-11 | **PASS** | Checklist 7 mục real + mock đạt; chi tiết mục 6. Vi phạm AC-05/08/10 vẫn làm kết luận task là FAIL. |

Tổng: **8 PASS / 3 FAIL** (`AC-05`, `AC-08`, `AC-10`).

## 3. Đối chiếu M1–M9

| Hạng mục | Kết quả | Nhận xét |
|---|---|---|
| M1 Hero carousel | **PARTIAL / RF** | 3D, 5 phim, chu kỳ, hover/focus/tab-hidden, phím, vuốt, aria-live và link đạt. Thiếu cơ chế pause/stop độc lập; reduced-motion động không dừng autoplay. |
| M2 Đom đóm | **PARTIAL / RF** | Canvas, DPR, IntersectionObserver, visibility cleanup đạt. Media query chỉ đọc lúc mount; canvas vẫn render ở reduce và không phản ứng đầy đủ khi preference đổi động. |
| M3 Thẻ phim | **PASS_WITH_TODO** | Tilt/glare/grid reveal/tab đạt. D2 bỏ độ nổi `translateZ` của tên phim so với thiết kế. |
| M4 Poster FLIP | **PASS** | Điều hướng thường, hash, direct URL, modifier-click và xóa PosterIntro đạt. |
| M5 Ghế 3D | **FAIL** | Perspective/glow/keyboard/real booking đạt; mobile hit target không đạt vì chat overlay. D5 thay `translateZ` bằng `translateY+scale` được ghi TODO thẩm mỹ. |
| M6 Vé lật/in vé | **PASS** | Focus isolation/inert/aria-hidden và held-vs-paid đạt. Burst/timer có cleanup. |
| M7 Route + microinteraction | **PASS** | D1 và D8 không gây mất auth/booking state quan trọng trong các luồng kiểm. Query cùng pathname không remount. |
| M8 Skeleton | **PASS** | Home/Explore có skeleton; reduce CSS dừng shimmer. |
| M9 Parallax tùy chọn | **PARTIAL / RF** | Parallax hoạt động và có cleanup qua `useGSAP`; preference đổi động chưa dừng do cùng RF-02. |

## 4. Required Fixes

### RF-01 — Medium — Ghế mobile bị nút chat che

- **File:** `frontend/src/styles/global.css`; có thể cần `frontend/src/components/ChatWidget.jsx` / route presentation liên quan.
- **Problem:** Nút chat fixed nằm trên vùng ghế khi cuộn sơ đồ ở 375px. Một ghế không nhận click tại tâm; việc kéo chat đi là workaround, không đáp ứng AC “ghế phải bấm trúng”.
- **Evidence:** Codex hit-test 96 ghế ở 375px: C9 trả element `.chat-widget__toggle`; 95/96 đạt. Claude ghi D9 bị che. 1280px đạt 96/96.
- **Expected Fix:** Bảo đảm chat mặc định không chồng bất kỳ tâm ghế/nút thao tác nào ở 375px trong toàn bộ vùng cuộn; sau fix chạy lại hit-test tất cả ghế ở 375 và 1280, đồng thời giữ khả năng kéo/mở chat.

### RF-02 — Medium — Reduced-motion không phản ứng khi đổi động

- **File:** `frontend/src/components/HeroCarousel.jsx`, `frontend/src/components/FireflyField.jsx`, `frontend/src/components/SeatMap.jsx`, `frontend/src/pages/MovieDetail.jsx`, `frontend/src/utils/motion.js`.
- **Problem:** Các component dùng `prefersReduced()` như snapshot lúc render/mount. Khi người dùng/DevTools đổi preference lúc trang đang mở, delayedCall autoplay vẫn chạy; các hiệu ứng khác cũng không được quản lý đồng nhất bởi `gsap.matchMedia()` như nguyên tắc T18 mục 4.1.
- **Evidence:** Sau `page.emulateMedia({ reducedMotion: "reduce" })`, tiêu đề hero vẫn đổi sau 6,3 giây. Source có `const reduced = prefersReduced()` và `gsap.delayedCall(...)`; Firefly effect return sớm chỉ ở lần mount.
- **Expected Fix:** Đăng ký/cleanup toàn bộ animation, delayedCall, RAF và parallax theo media-query listener hoặc `gsap.matchMedia()`. Bật reduce khi trang đang chạy phải lập tức dừng autoplay, bỏ 3D/poster flight/parallax, dừng và xóa đom đóm; chức năng nút/phím/vuốt/đặt vé vẫn đủ. Tắt reduce lại không được nhân đôi timer/RAF/tween.

### RF-03 — Medium — Hero thiếu pause/stop độc lập

- **File:** `frontend/src/components/HeroCarousel.jsx`, `frontend/src/styles/global.css`.
- **Problem:** Hero tự cập nhật vô hạn mỗi 6 giây nhưng chỉ dừng khi hover/focus/tab hidden. Người dùng không thể pause rồi tiếp tục thao tác phần khác trên trang. W3C Understanding SC 2.2.2 nêu rõ dừng chỉ trong lúc focus không được xem là cơ chế pause.
- **Evidence:** Không có button/control pause trong DOM/source. Autoplay tiếp tục ngay khi focus rời hero. Tham chiếu: `https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html`, dòng giải thích cơ chế pause và trường hợp focus-only.
- **Expected Fix:** Thêm control tiếng Việt có trạng thái truy cập được (`Tạm dừng`/`Tiếp tục`, `aria-pressed` hoặc nhãn tương đương), focus rõ, không tự resume khi người dùng đã pause; giữ các điều kiện hover/focus/tab-hidden và reduced-motion hiện có.

## 5. TODOs không chặn sau khi RF được sửa

| TODO | Mức | Nội dung |
|---|---|---|
| TODO-01 | Low / PO thẩm mỹ | D2 bỏ `translateZ` nhẹ cho tên phim trên MovieCard, nên M3 ít chiều sâu hơn spec. PO quyết định chấp nhận hay yêu cầu khôi phục theo cách không phá hit-test/overflow. |
| TODO-02 | Low / PO thẩm mỹ | D5 dùng `translateY(-3px) scale(1.06)` thay `translateZ` cho ghế chọn. Đây là trade-off hợp lý cho hit-test nhưng lệch mô tả 3D ban đầu; PO duyệt cảm quan. |
| TODO-03 | Low / process | Baseline bundle trong report Claude (`80,41 KB`) không tái lập từ `master`; Codex đo `85,29 KB`. Delta độc lập vẫn đạt (`48,82 KB`). Lần sau ghi cả tên file/hash build hoặc môi trường Node/npm để tái lập. |

## 6. Quality gates và hồi quy

### Quality gates

| Gate | Kết quả | Bằng chứng |
|---|---|---|
| Python compileall | **PASS** | `backend\venv\Scripts\python.exe -m compileall -q backend\app` → `COMPILEALL_PASS`. |
| Backend startup + health | **PASS** | Uvicorn trên SQLite tạm; `/api/health` 200, `status=ok`, active `phobert_b`, version `phobert-B-2026-10-09`. |
| Frontend build | **PASS** | Vite 5.4.21, 81 modules, JS gzip `134,11 KB`, CSS gzip `8,40 KB`. |
| Backend pytest | **PASS** | `50 passed, 1 warning` trong `34,02s`; warning Starlette/anyio đã có từ trước. |
| Mock mode | **PASS với phát hiện AC** | Hero, tab, poster, seat keyboard, ticket flip và responsive chạy; phát hiện RF-01/RF-02. |
| Real mode | **PASS với phát hiện AC** | SQLite tạm: search, auth return, booking, comment moderation, health đạt. Không dùng DB thật. |
| Scope integrity | **PASS** | 21 file trước review đều thuộc allowlist; không có backend/API/context/forbidden file. Report và coordination update cũng thuộc allowlist. |
| Secret/large-file scan | **PASS** | Không `.env`, `*.db`, model, CSV/joblib/tensor; diff không có token/API key/secret mới. |
| Dependency audit | **PASS cho scope T18** | Chỉ 2 dependency được duyệt. `npm audit --omit=dev` báo 2 moderate ở React Router đã có từ baseline, không do GSAP/T18. |
| Whitespace | **PASS** | `git diff --check master...HEAD` không lỗi trước khi tạo review report. |
| DB thật trước/sau | **PASS** | SHA-256 không đổi: `B3F7D...CFE3`. |
| Probe cleanup | **PASS** | 3 file probe, worktree master, Playwright tạm và SQLite tạm đã xóa; server đã dừng. |

### Checklist hồi quy 7 mục

| # | Kết quả | Bằng chứng |
|---|---|---|
| 1. Trang chủ, hero, poster/link | **PASS** | Real + mock có 5 slot; card/hero tới đúng phim; FLIP/direct/hash đạt. |
| 2. Thể loại/chủ đề/tìm kiếm | **PASS** | Real search `meo muop` trả đúng 1 phim “Mèo Mướp Đi Lạc”; mock/filter không regression. |
| 3. Đăng ký, protected redirect | **PASS** | Chưa login vào `/dat-ve/20` → `/dang-nhap`; đăng ký xong quay lại đúng `/dat-ve/20`. |
| 4. Đặt 2 ghế | **PASS** | Real đặt C7+C8, thông báo giữ chỗ, Vé của tôi có vé; mở lại cả hai disabled. |
| 5. Bình luận + kiểm duyệt | **PASS** | Bình luận tiêu cực marker T18 không hiện với khách; admin thấy nội dung và `phobert_b`. |
| 6. Health | **PASS** | 200, classifier active đúng. |
| 7. Mock | **PASS** | Các luồng Home/Explore/detail/seat/ticket chạy; dữ liệu mock không bị commit. |

## 7. Đối chiếu D1–D8

| Quyết định | Kết luận review |
|---|---|
| D1 route seat chỉ fade | **Chấp nhận.** Tránh transform ancestor phá fixed summary; không mất chức năng. |
| D2 bỏ title `translateZ` | **Không chặn AC, TODO-01.** Lệch chi tiết M3, để PO duyệt thẩm mỹ. |
| D3 `overflow: clip`, không preserve-3d stage | **Chấp nhận.** 375px hết overflow ngang; poster slot vẫn có perspective/rotateY/z. |
| D4 scroll top trước FLIP | **Chấp nhận.** Hash cuộn sau timeline; direct URL hoạt động. |
| D5 bỏ seat `translateZ` | **Chấp nhận kỹ thuật, TODO-02 thẩm mỹ.** Hit-test desktop đạt; lỗi mobile là chat overlay riêng. |
| D6 `animation-fill-mode: backwards` | **Chấp nhận.** Vé mới vẫn lật được. |
| D7 xóa spinner | **Chấp nhận.** Không còn usage; loading firefly có reduced CSS. |
| D8 `key={pathname}` | **Chấp nhận có điều kiện.** Auth context nằm ngoài wrapper; booking redirect/state đạt. `/kham-pha?...` cùng pathname giữ state. Remount khi đổi `/phim/:id` giúp reset state riêng của phim; không thấy mất state quan trọng trong probe. |

## 8. Trạng thái bàn giao

- T18: `CODEX_REVIEW → FIX_LOOP`.
- Không APPROVE, merge, đóng T18 hoặc mở task kế tiếp.
- Claude chỉ sửa RF-01 → RF-03, không tự xử lý TODO hoặc thêm feature ngoài fix.
