# Codex Independent Review — T18 Round 2 — PASS_WITH_TODO

| Trường | Giá trị |
|---|---|
| Task | T18 — Chuyển động và hiệu ứng 3D |
| Nhánh | `task/T18-giao-dien-chuyen-dong` |
| Baseline | `master` tại `fdaa7acc0f2ff71d3ff99ee47d92eedde32fa283` |
| HEAD đã kiểm | `6653d945decc01844dd0b98cb7ad2580f04daf6b` |
| Fix commit | `4b9b1225a2a5f96c65e1c8828bdc0b4cb90f9da7` — là ancestor trực tiếp của HEAD qua commit report `6653d94` |
| Reviewer | Codex — Independent Reviewer / Tester |
| Ngày | 13/10/2026 |
| Kết luận | **PASS_WITH_TODO** |

## 1. Kết luận

Ba Required Fix của Round 1 đã được xác minh độc lập bằng Chrome thật và source code:

- **RF-01 CLOSED / VERIFIED BY CODEX:** hit-test đủ `96/96` ghế tại cả 375px và 1280px; không ghế nào, gồm vùng từng lỗi C9/D9, bị chat che. Chat mặc định không chồng chữ ghế, tổng tiền hay nút Tiếp tục; kéo không mở nhầm panel, sau đó vẫn mở/đóng được.
- **RF-02 CLOSED / VERIFIED BY CODEX:** đổi media thật sau mount theo chuỗi `no-preference → reduce → no-preference` dừng/khôi phục đúng autoplay, 3D, canvas, poster flight, parallax và hiệu ứng hàng ghế. Không nhân đôi timer; sau khi về `no-preference` chỉ có một delayed-call 6 giây.
- **RF-03 CLOSED / VERIFIED BY CODEX:** nút Tạm dừng/Tiếp tục có focus rõ và aria-label đúng. User-pause giữ nguyên qua đổi focus và bấm Phim sau; chỉ chạy lại sau khi người dùng bấm Tiếp tục và các điều kiện hover/focus không còn.

Kết quả AC: **11/11 PASS**. Không còn Required Fix mở. Giữ nguyên **TODO-01 → TODO-03** cho PO disposition; Codex không tự APPROVE, merge, đóng T18 hoặc mở task tiếp theo.

Không sửa production code trong review. Toàn bộ probe, Playwright và SQLite tạm đã xóa. `backend/firefly.db` thật không được khởi động và giữ nguyên SHA-256 trước/sau: `B3F7DF79BDA4478412200EA80B8EC15E6B73DA730068A52E11C40136EAC4CFE3`.

## 2. Xác minh RF Round 1

### RF-01 — Chat và toàn bộ vùng ghế

| Nội dung | 375px | 1280px |
|---|---:|---:|
| Tổng button ghế | 96 | 96 |
| Tâm ghế trả về đúng button sau khi cuộn ngang/dọc tới từng ghế | **96/96** | **96/96** |
| Miss do chat/summary/overlay | 0 | 0 |
| Tràn ngang toàn trang | 0px | 0px |
| Chat chồng chữ ghế / tổng tiền / Tiếp tục | Không / Không / Không | Không / Không / Không |

- Vị trí chat mặc định: `(319,611)`, kích thước `46×46` ở viewport `375×667`; `(1218,738)`, kích thước `52×52` ở `1280×800`. Nút nằm trong phần nền đã chừa chỗ của summary bar.
- Mouse, Enter và Space chọn/bỏ đúng A1, D6, H12 VIP và F1 VIP. Luồng real đặt A1+A2 thành công; quay lại suất chiếu thấy cả hai disabled.
- Kéo chat tới trái trên làm vị trí đổi nhưng panel vẫn đóng; click tiếp theo mở panel với `aria-expanded=true`; nút đóng hoạt động. Reload route ghế đưa chat về vị trí mặc định an toàn.

### RF-02 — Media emulation thật và cleanup

Probe dùng `page.emulateMedia({ reducedMotion: ... })` của Chrome/Playwright trên component đã mount, không thay `matchMedia` bằng object giả.

| Trạng thái | Bằng chứng |
|---|---|
| `no-preference` ban đầu | 5 slot đều có transform 3D, 1 canvas, 1 nút pause; hero đổi phim sau 6,4 giây. |
| Chuyển sang `reduce` | `matchMedia` trả `true`; canvas `1→0`; nút pause ẩn; 5/5 transform thành `none`; chỉ slot active hiện; 0 ScrollTrigger; tiêu đề không đổi qua 6,4 giây. |
| Chi tiết phim đang mount → `reduce` | Parallax ScrollTrigger `1→0`, poster transform `none`; chuyển lại `no-preference` tạo đúng 1 trigger hiện hành. |
| Poster navigation trong `reduce` | Link vẫn tới đúng `/phim/5`; poster đích `transform:none`, không FLIP; không canvas. |
| SeatMap đang mount → `reduce` | 8/8 hàng `opacity:1`, `visibility:visible`, `transform:none`; click ghế vẫn đổi `aria-pressed`; khôi phục mode không để hàng kẹt. |
| Trở lại `no-preference` | Canvas và 3D trở lại; đúng 1 delayed-call 6 giây; hero đổi đúng một phim sau 6,4 giây. |
| Cleanup | Ở reduce: 0 ScrollTrigger, không active tween có DOM target; node GSAP nội bộ còn lại ở trạng thái inactive/paused. Source hủy RAF, observers, delayedCall và media listener khi đổi mode/unmount. Rời Detail về Home chỉ còn trigger của các MovieCard đang connected, không còn trigger `.detail`. |

### RF-03 — Pause control và accessibility

- Focus bàn phím trên nút có outline; Enter đổi `Tạm dừng tự chuyển phim` → `Tiếp tục tự chuyển phim` và ngược lại.
- Sau user-pause, chuyển focus ra header, bấm Phim sau rồi chờ 6,4 giây: phim không tự đổi thêm.
- Sau bấm Tiếp tục, chuyển focus/chuột khỏi hero: phim tự đổi đúng một bước sau 6,4 giây.
- Hover giữ nguyên phim qua 6,4 giây; focus trong hero giữ nguyên phim qua 6,4 giây; rời focus thì autoplay tiếp tục. Kiểm tra Chrome headful với trang hero ở nền cũng giữ nguyên phim qua 6,4 giây và tiếp tục sau khi foreground. Source đăng ký và dọn `visibilitychange`, đồng bộ bằng `document.hidden`.

## 3. Acceptance Criteria

| AC | Kết quả | Bằng chứng review độc lập |
|---|---|---|
| AC-01 | **PASS** | Chỉ thêm đúng `gsap@3.15.0` và `@gsap/react@2.1.2`, ghim chính xác. Build: JS gzip `134,47 KB`; baseline `master` Codex Round 1 đo `85,29 KB`; tăng `49,18 KB` ≤ `60 KB`. |
| AC-02 | **PASS** | 5 phim; chu kỳ 6 giây; hover/focus/background pause; nút Trước/Sau, ArrowRight và swipe đổi đúng phim; Ctrl-click poster mở `/phim/9` ở tab mới và tab gốc giữ nguyên. 21/21 tiêu đề là NFC. Firefly canvas dừng/xóa trong reduce; source có IntersectionObserver khi hero ra ngoài viewport. |
| AC-03 | **PASS** | Tilt chỉ bật với fine pointer + no-preference. Sau 10 lần đổi tab và cuộn grid vào viewport, 9/9 card `opacity:1`, transform identity, không kẹt. TODO-01 giữ nguyên cho phần title không `translateZ`. |
| AC-04 | **PASS** | Card/hero poster, tên, Đặt vé, Xem chi tiết giữ link đúng; modifier-click giữ native behavior; direct URL fade; hash lịch chiếu hoạt động. `PosterIntro.jsx` đã xóa, không còn import. Reduce bỏ FLIP nhưng điều hướng vẫn đủ. |
| AC-05 | **PASS** | RF-01 đạt 96/96 tại 375/1280; chuột/Enter/Space, góc/giữa/VIP đạt; real đặt 2 ghế và mở lại đều locked. Perspective 22° desktop/12° mobile. |
| AC-06 | **PASS** | Vé held không có nút lật và nút chuyển khoản hoạt động; mock có QR. Sau claim thành pending, Enter lật/lật lại; mặt úp `inert` + `aria-hidden`, focus chuyển đúng nút mặt đang hiện. Vé mới có `ticket--new ticket--print`. Paid dùng cùng nhánh `flippable`. |
| AC-07 | **PASS** | Delayed API cho thấy Home skeleton; Explore dùng cùng skeleton component. Route/dropdown/tab/search/chat có motion; dropdown mở đúng; real/mock không lỗi. |
| AC-08 | **PASS** | Media emulation thật sau mount: không 3D, poster flight, autoplay, parallax hay đom đóm; seat/link/navigation vẫn thao tác đủ; đổi lại mode không nhân đôi timer/tween. |
| AC-09 | **PASS** | Trace 10,513 giây trên Home: `0` long task >50ms. Không page error/GSAP unmount error; detail trigger cleanup đúng; dynamic reduce không còn active DOM tween/ScrollTrigger. 404 favicon không phải lỗi T18. |
| AC-10 | **PASS** | 375/768/1280 đều `scrollWidth-innerWidth=0`; tiêu đề/controls tiếng Việt hiển thị đúng; slot ẩn không vào tab order; focus pause/ticket thấy rõ; ghế và CTA thao tác được. |
| AC-11 | **PASS** | Checklist real/mock 7/7 đạt, xem mục 6. |

Tổng: **11 PASS / 0 FAIL**.

## 4. Đối chiếu M1–M9

| Hạng mục | Kết quả | Nhận xét |
|---|---|---|
| M1 Hero carousel | **PASS** | 3D, 5 phim, timer, hover/focus/background, keyboard/swipe, links và pause control đạt. |
| M2 Đom đóm | **PASS** | Canvas/RAF/observer có cleanup; dynamic reduce xóa canvas; ngoài viewport có IntersectionObserver dừng vẽ. |
| M3 Card tilt + grid reveal | **PASS_WITH_TODO** | Fine-pointer tilt, glare, reveal và rapid tabs đạt; TODO-01 là trade-off thẩm mỹ đã biết. |
| M4 Poster FLIP | **PASS** | Card/hero/direct/hash/modifier-link và reduced-motion đạt; PosterIntro đã xóa. |
| M5 Ghế 3D | **PASS_WITH_TODO** | Perspective, hit-test, keyboard, disabled và booking đạt; TODO-02 giữ trade-off không dùng translateZ cho ghế chọn. |
| M6 Vé lật/in | **PASS** | Held/pending, keyboard, inert/focus, print/burst và reduced CSS đạt. |
| M7 Route + microinteraction | **PASS** | Fade, D1, navigation và state cần cho auth/checkout đạt. Chọn ghế khi quay lùi từ Checkout vẫn reset như baseline master, không phải regression T18. |
| M8 Skeleton | **PASS** | Home/Explore hiển thị skeleton khi response chậm; reduce dừng shimmer. |
| M9 Parallax | **PASS** | Trigger hoạt động ở no-preference, bị dọn khi reduce/unmount và tạo lại đúng một lần. |

## 5. Đối chiếu D1–D8

| Quyết định | Kết luận Round 2 |
|---|---|
| D1 seat route chỉ fade | **Chấp nhận.** Summary fixed ổn định; chat/CTA không va chạm. |
| D2 bỏ title `translateZ` | **Chấp nhận có TODO-01.** Không chặn chức năng; PO duyệt thẩm mỹ. |
| D3 stage `overflow: clip` | **Chấp nhận.** Cả 3 breakpoint không tràn ngang; vòng poster vẫn thể hiện 3D. |
| D4 scroll top trước FLIP | **Chấp nhận.** Đích đo đúng; hash cuộn sau intro. |
| D5 bỏ seat `translateZ` | **Chấp nhận có TODO-02.** 96/96 hit-test; PO duyệt cảm quan selected state. |
| D6 print dùng `backwards` | **Chấp nhận.** Vé mới vẫn lật được sau khi claim. |
| D7 xóa spinner | **Chấp nhận.** Không còn usage; skeleton/loading firefly thay thế và có reduce. |
| D8 `key={pathname}` | **Chấp nhận.** Auth context giữ nguyên; protected redirect và state vào Checkout đúng; query cùng pathname không remount. Việc reset local state khi đổi phim là trade-off đã công bố, không thấy regression luồng chính. |

## 6. Quality gates và checklist hồi quy

### Quality gates

| Gate | Kết quả | Bằng chứng |
|---|---|---|
| Git identity | **PASS** | HEAD thực `6653d94`; fix `4b9b122` đã xác minh là ancestor, parent là review FAIL `eb254ce`. |
| Python compileall | **PASS** | Final clean run: `COMPILEALL=PASS`. |
| Backend startup + health | **PASS** | Uvicorn dùng `C:\Users\lemin\AppData\Local\Temp\firefly_t18_final_gate.db`; health 200, `status=ok`, active `phobert_b`, version `phobert-B-2026-10-09`; DB tạm đã xóa. |
| Frontend build | **PASS** | Final clean run: Vite 5.4.21, 81 modules, JS gzip `134,47 KB`, CSS gzip `8,48 KB`. |
| Backend pytest | **PASS** | Final clean run: `50 passed, 1 warning` trong 25,90s. Starlette/anyio deprecation và thông báo cleanup symlink temp của pytest là cảnh báo môi trường sau suite; exit code 0, không có test fail. |
| Mock mode | **PASS** | 5-slot hero, search, auth redirect, đặt 2 ghế, Vé của tôi và locked-seat đều đạt ở `VITE_USE_MOCK=true`. |
| Real mode | **PASS** | SQLite tạm: auth, search, booking, ticket status/flip, comment model/admin và health đạt. |
| Scope integrity | **PASS** | 23 file trong `master...HEAD` đều thuộc T18 allowlist; fix commit chỉ sửa 7 production file được phép. Không file forbidden. |
| Secret/large-file scan | **PASS** | Không `.env`, `*.db`, `backend/models`, CSV/model artifact hay API/context file trong diff. |
| Whitespace | **PASS** | `git diff --check master...HEAD` exit 0 trước report. |
| DB thật | **PASS** | SHA-256 trước/sau cùng là `B3F7D...CFE3`; backend thật chỉ chạy trên SQLite tạm. |
| Probe cleanup | **PASS** | Tất cả `.codex_t18_*`, Playwright tạm và hai SQLite tạm đã xóa; server đã dừng trước final gates. |

### Checklist hồi quy 7 mục

| # | Kết quả | Bằng chứng |
|---|---|---|
| 1. Home/hero/link poster | **PASS** | Real/mock có 5 slot; Xem chi tiết, Đặt vé, poster và modifier-click tới đúng phim; FLIP/hash/direct đạt. |
| 2. Menu/search | **PASS** | Dropdown Thể loại mở; `meo muop` trả đúng “Mèo Mướp Đi Lạc” trong real và mock. |
| 3. Auth/protected return | **PASS** | Khách vào `/dat-ve/20` bị đưa tới login; đăng ký xong quay lại đúng `/dat-ve/20`. |
| 4. Đặt 2 ghế | **PASS** | Real A1+A2 và mock hai ghế khả dụng được đặt; Vé của tôi có vé mới; mở lại thấy cả hai disabled. |
| 5. Comment/admin | **PASS** | Comment marker bị ẩn với tác giả/guest; admin thấy `Tiêu cực`, `1.00`, `phobert_b`, version đúng. |
| 6. Health | **PASS** | HTTP 200, classifier active `phobert_b`; phù hợp trạng thái model B hiện hành. |
| 7. Mock | **PASS** | Home/search/auth/seat/booking/ticket chạy hoàn chỉnh, không page error. |

## 7. Required Fixes

**Không có Required Fix mở.**

| RF | Trạng thái | Evidence đóng |
|---|---|---|
| RF-01 | **CLOSED / VERIFIED BY CODEX** | 96/96 ghế ở cả 375/1280; chat/summary/CTA và drag/open đạt. |
| RF-02 | **CLOSED / VERIFIED BY CODEX** | Media emulation thật động; autoplay/3D/canvas/FLIP/parallax/seat cleanup đạt; một timer sau restore. |
| RF-03 | **CLOSED / VERIFIED BY CODEX** | Pause/resume keyboard, focus, aria-label và persistence qua manual navigation đạt. |

## 8. TODOs giữ nguyên cho PO disposition

| TODO | Mức | Nội dung |
|---|---|---|
| TODO-01 | Low / PO thẩm mỹ | D2 bỏ `translateZ` nhẹ cho tên phim trên MovieCard, nên M3 ít chiều sâu hơn spec. PO quyết định chấp nhận hay yêu cầu khôi phục theo cách không phá hit-test/overflow. |
| TODO-02 | Low / PO thẩm mỹ | D5 dùng `translateY(-3px) scale(1.06)` thay `translateZ` cho ghế chọn. Đây là trade-off hợp lý cho hit-test nhưng lệch mô tả 3D ban đầu; PO duyệt cảm quan. |
| TODO-03 | Low / process | Baseline bundle trong report Claude (`80,41 KB`) không tái lập từ `master`; Codex đo `85,29 KB`. Delta độc lập Round 2 vẫn đạt (`49,18 KB`). Lần sau ghi cả tên file/hash build hoặc môi trường Node/npm để tái lập. |

## 9. Bàn giao

- T18: `CODEX_REVIEW Round 2 → PO_REVIEW`.
- PO cần disposition TODO-01 → TODO-03 và duyệt thẩm mỹ.
- Codex không APPROVE, merge, đóng T18 hoặc mở task tiếp theo.
