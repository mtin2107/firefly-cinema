# Claude review T28 round 3 — PASS (27/10/2026)

- Nhánh: `task/T28-giao-dien-tai-khoan` @ `5b27199`, so với `00c5bdf` (PO yêu cầu vòng sửa 2, T28.md mục 14).
- Report Codex: `reports/2026-10-27/codex_fix_T28_round2_2026-10-27.md`.
- **Đổi schema: Không.**

## 1. Kết luận
**PASS.** R2-01, R2-02 đạt. RF 0. OBS-01..06 của round 1 giữ nguyên để PO quyết.

## 2. Diff
`git diff 00c5bdf..5b27199`: `MovieCard.jsx`, `global.css`, report Codex, file điều phối. Đúng danh sách file mục 14; không đụng backend, mock, test, `:root`, `HeroCarousel.jsx`. `git diff --check` exit 0.

- R2-01: một bản tên duy nhất trong DOM (không nhân đôi cho trình đọc màn hình), giữ `title`. Đo tràn bằng `scrollWidth - clientWidth`, đo lại bằng `ResizeObserver` và khi font tải xong. Chạy bằng GSAP sẵn có (40px/giây, dừng 1,5 giây). `gsap.matchMedia` theo dõi reduced motion và `(hover: hover)`; dọn timeline, observer, listener khi tháo component. Không có điều kiện theo tên/id phim (nguyên tắc 4.0).
- R2-02: chỉ bỏ cặp selector `visibility: hidden` của poster phụ.

## 3. Kiểm chứng độc lập (frontend 5173 + backend 8000, chỉ đọc dữ liệu)
| AC | Kết quả |
|---|---|
| AC-R2-01 có chuột, 1280px | Khám phá 21 thẻ, 4 tên tràn. Lúc đứng yên cả 4 thẻ `transform: none`. Hover thẻ "Sơn Tinh Thủy Tinh…": 1,0 giây → `translateX(-40.28px)`, 1,5 giây → `-57px` (hết độ tràn); rời chuột → `none`. Thẻ tên vừa khung ("Mật Mã Bến Nghé") hover vẫn `none`. Tên mọi thẻ cao đúng 1 dòng (24px) |
| AC-R2-01 cảm ứng, 375px | `(hover: hover)` = false, 12 thẻ tràn; thẻ tràn được gắn lớp `movie-card--title-running`, tức là timeline tự chạy đã được tạo. **Không đo được chuyển động thực tế**: tab kiểm chạy nền nên trình duyệt dừng `requestAnimationFrame` (đo được 0 khung hình/giây). Phần này dựa vào report Codex và đọc code (cùng timeline với nhánh có chuột) |
| AC-R2-02 reduced motion | Ảnh Edge `--force-prefers-reduced-motion` 1280px Khám phá: tên dài hiện 2 dòng ("Sơn Tinh Thủy Tinh: Trận / Chiến Cuối"), các dòng thời lượng/điểm của cả hàng vẫn thẳng |
| AC-R2-03 thẳng hàng | Khám phá 1280px: 6 hàng, chênh lệch lớn nhất của mọi dòng trong thẻ và đáy thẻ = 0px. 375px: 0px, không tràn ngang |
| AC-R2-04 hero | Ảnh 1440px: poster phụ hiện lại tên và thể loại như trước T28; hiệu ứng bật sáng từng ký tự của tên phim hero vẫn chạy |
| AC-R2-05 gate | compileall 0; build real và mock đạt; pytest (00:57) **208 passed, 1 failed** — chỉ `test_sentiment` OBS-01 T27 (fail 0h–7h) |

## 4. Việc PO cần làm
1. Quyết OBS-01..03 của round 1 (poster không bắt buộc, menu gọn ở ≤1360px, line-height tiêu đề).
2. Merge `task/T28-giao-dien-tai-khoan` vào master. **Không cần reset DB.**
3. Xóa nhánh rỗng `task/T13-ten-task`, tạo `task/T13-v1`, gửi prompt T13 ở mục 8 report round 1; dòng T28 ghi "TODO-01 đã sửa; vòng 2 (chạy chữ, poster phụ) đã làm".
