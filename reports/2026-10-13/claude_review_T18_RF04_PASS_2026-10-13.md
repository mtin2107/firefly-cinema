# Claude Independent Review — T18 RF-04 — PASS

| Trường | Giá trị |
|---|---|
| Task | T18 — Chuyển động và hiệu ứng 3D |
| Phạm vi review | Chỉ Required Fix RF-04 do Codex triển khai |
| Nhánh | `task/T18-giao-dien-chuyen-dong` |
| Delta review | `7f6a0c2..490ac8a` |
| Fix RF-04 | `490ac8aeaf2ebcb41c38b8226a596b3958235479` |
| Reviewer | Claude (Independent Reviewer) |
| Ngày | 13/10/2026 |
| Kết luận | **PASS** |

Không review lại phần code Claude đã viết trước đó trong T18. Không sửa production code.

## 1. Kết luận

RF-04 được sửa đúng phạm vi: chỉ đổi `frontend/src/components/PosterIntro.jsx` (+4/−2). Fix import `createPortal` từ `react-dom` có sẵn và đưa lớp `.intro` vào `document.body`. Không thêm dependency, không đổi CSS, không đổi `route-fade`, timer, Esc, click nền hay nhánh reduced-motion. `git diff --check 7f6a0c2..490ac8a` sạch.

**Không có Required Fix mới.**

## 2. Bằng chứng độc lập

Trình duyệt chạy mock mode (`VITE_USE_MOCK=true`, cổng 5174). Đo bằng DOM và `getBoundingClientRect`/`elementFromPoint`.

| Ca kiểm | Kết quả |
|---|---|
| Desktop 1280×720, trang chủ cuộn 650px, bấm hero "Đặt vé" | `.intro` là con trực tiếp của `BODY`, `closest('.route-fade') = null`. Kích thước `0,0,1280,720` đúng bằng viewport. Tâm bubble x=640 nằm giữa. `elementFromPoint` tại vị trí header trúng `.intro`, tức nền đã phủ header. |
| Không bị `route-fade` làm lệch | Tại thời điểm đo, `.route-fade` vẫn có `transform: matrix(1,0,0,1,0,12)` (animation `route-in` đang chạy). Overlay vẫn ở `0,0`, đúng tình huống gây lỗi trước khi sửa. |
| Mobile 375×812, cuộn 650px, bấm "Đặt vé" trên MovieCard | Overlay `0,0,375,812`. Bubble `111,260,153×230`, tâm ngang ≈187 nằm giữa. Nền phủ header, không tràn ngang (`scrollWidth − innerWidth = 0`). URL `/phim/5#lich-chieu`. |
| Tự đóng | Đo bằng MutationObserver: chuyển `intro--leaving` ở 1791ms (thiết kế 1800ms), sau đó overlay được gỡ khỏi DOM. |
| Esc | Bấm lúc 389ms → `leaving` lúc 390ms. Overlay được gỡ sau đó, khớp FADE 600ms cộng độ trễ do timer bị hãm. |
| Click nền | Bấm lúc 806ms → `leaving` lúc 813ms → gỡ lúc 1433ms (≈620ms). URL giữ `#lich-chieu`. |
| Hash lịch chiếu | Mở qua Link "Đặt vé": sau khi intro đóng, `#lich-chieu` cuộn về top ≈80. |
| Direct URL | Mở thẳng `/phim/4#lich-chieu`: không có `.intro`, `#lich-chieu` top=80. |
| Reload | `history.state.usr = null` sau khi vào trang nên F5 không phát lại intro. |
| Cleanup | Rời trang khi intro đang mở: không còn `.intro` sót trong `body`. Portal được React gỡ khi unmount, timer và listener Esc được dọn trong cleanup của effect. Không có page error. |
| Reduced-motion | Giả lập `matchMedia('(prefers-reduced-motion: reduce)')` trả `true`: intro bị gỡ ngay (≈40ms), điều hướng tới `/phim/9#lich-chieu` vẫn đủ và trang chi tiết render. CSS chung `*{animation:none!important}` vẫn áp dụng cho node đã portal vì selector toàn cục. |
| Stacking | `.intro` z-index 50, cao hơn header (20), chat widget (45) và summary-bar (15). Node nằm ở `body` nên không bị stacking context của `.route-fade` giới hạn. |

## 3. Gate

| Gate | Kết quả |
|---|---|
| `git diff --check 7f6a0c2..490ac8a` | PASS |
| Scope commit fix | PASS: chỉ `frontend/src/components/PosterIntro.jsx`, là ngoại lệ PO đã chỉ định cho RF-04 |
| `npm run build` | PASS: Vite, CSS gzip 9,25 KB, JS gzip 134,82 KB, khớp số đo của Codex |
| Dependency | PASS: `react-dom` đã có sẵn, không thêm package |
| Working tree sau review | Sạch: không còn probe, server preview đã dừng, viewport đã trả về desktop |

## 4. Ghi chú không chặn (có từ trước, không do RF-04)

- **OBS-01 (Low):** Khi bật reduced-motion, `PosterIntro` vẫn mount và render overlay khoảng 40ms rồi `useEffect` mới gọi `onDone()` để gỡ. Trên máy thật có thể thấy nền đen chớp trong 1–2 frame. Logic này đã tồn tại ở `7f6a0c2`, RF-04 không làm thay đổi. Hướng xử lý nếu PO muốn: kiểm tra reduced-motion tại `MovieDetail` trước khi khởi tạo state `intro`. PO quyết định xử lý trong T18 hay để task sau.

## 5. Giới hạn của review

- Pane trình duyệt bị ẩn trong lúc kiểm nên chụp màn hình ra trang đen, và timer bị trình duyệt hãm (lệch khoảng 100–900ms ở bước gỡ overlay). Bằng chứng ở trên là số đo DOM. Ảnh trực quan tham chiếu `reports/2026-10-13/evidence/T18_RF04_*.png` của Codex.
- Reduced-motion được giả lập bằng cách thay `window.matchMedia`, không phải emulation media thật của trình duyệt.
- Không chạy lại backend, pytest hay real mode vì fix chỉ đụng một component frontend và Codex đã chạy các gate đó ở Round 3.

## 6. Bàn giao

- RF-04: **CLOSED / VERIFIED BY CLAUDE**.
- T18 giữ ở `PO_REVIEW` theo Codex Round 3. Claude không cập nhật file điều phối.
- Claude không APPROVE, không merge, không CLOSED T18 và không mở task kế tiếp.
