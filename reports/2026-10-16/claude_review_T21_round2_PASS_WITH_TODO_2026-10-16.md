# Claude Review — T21 — Round 2 (fix TODO-01 theo yêu cầu PO) — PASS_WITH_TODO — 16/10/2026

- Nhánh: `task/T21-thong-ke-cam-xuc`, tip `8745c65` ("[T21] Fix TODO-01 bố cục biểu đồ theo ngày").
- Vòng trước: `reports/2026-10-16/claude_review_T21_PASS_WITH_TODO_2026-10-16.md`.
- Report Codex: `reports/2026-10-16/codex_fix_T21_todo01_2026-10-16.md` (bằng chứng phụ).
- Probe trên SQLite tạm (dữ liệu demo T12 tạo bằng `reset_demo.py`) trong scratchpad của Claude; không chạm `backend/firefly.db`.

## 1. Scope của bản fix

`git diff --stat 2ef8939 8745c65`: `frontend/src/pages/AdminSentiment.jsx`, `frontend/src/styles/global.css` (chỉ khối T21), report fix, file điều phối. Đúng danh sách trong prompt. Không đổi backend, `package.json`, schema.

## 2. Thay đổi

- `DailyChart` đo bề rộng khung bằng `ResizeObserver` (API có sẵn của trình duyệt), SVG có `width` = bề rộng khung và viewBox cùng tỷ lệ, nên chữ không bị co. Cột chia đều trên vùng vẽ, có lề 2 bên 22 px.
- Ở khung < 600 px, chỉ khoảng 90 ngày mới được rộng tối thiểu 16 px/ngày (cuộn ngang trong khung riêng).
- Nhãn ngày thưa theo khoảng tối thiểu 48 px, luôn giữ nhãn ngày cuối; chữ 11 px.
- TODO-04 (tùy chọn) đã làm: dùng cờ `active` trong `useEffect` để bỏ phản hồi cũ; nút "Thử lại" đổi sang `reloadKey`.
- Giữ nguyên `role="img"`, `aria-label`, `<title>` từng cột, chú thích, bảng số liệu, màu T18.

## 3. Đo lại (Claude, trình duyệt thật, dữ liệu demo)

| Viewport | Khoảng | Khung / SVG (px) | Cuộn trong khung | Nhãn | Nhãn đè nhau | Cỡ chữ | Trang tràn ngang |
|---|---|---|---|---|---|---|---|
| 1280 | 7 | 1094 / 1094 | không | 7 | 0 | 11 px | không |
| 1280 | 30 | 1094 / 1094 | không | 15 | 0 | 11 px | không |
| 1280 | 90 | 1094 / 1094 | không | 18 | 0 | 11 px | không |
| 768 | 7 / 30 / 90 | 667 / 667 | không | 7 / 10 / 13 | 0 | 11 px | không |
| 375 | 7 | 322 / 321 | không | 4 | 0 | 11 px | không |
| 375 | 30 | 322 / 321 | không | 5 | 0 | 11 px | không |
| 375 | 90 | 322 / 1440 | có (đúng yêu cầu) | 23 | 0 | 11 px | không |

So với vòng 1 ở 1280 px: 30 ngày từ 17 cặp nhãn đè nhau xuống **0**; 7 ngày từ chỉ chiếm ~190 px lên phủ 77–1017 px của khung 1094 px; 90 ngày từ 2553 px phải cuộn xuống **vừa khung**.

Kiểm thêm:
- Đổi kích thước 1280 → 768 → 375 px mà không tải lại trang: biểu đồ tự co theo (`ResizeObserver` hoạt động).
- Bấm nhanh 90 rồi 7 ngày: trang ở "7 ngày", bảng có 7 dòng, nên phản hồi cũ không ghi đè (TODO-04 CLOSED).
- Sau khi tải lại trang, đổi qua 7/90/30 ngày: không có lỗi JS mới. Mọi request `/api/admin/sentiment` đều 200. Có 9 dòng `ERR_CONNECTION_REFUSED` trong bộ đệm console từ lúc tab mở khi backend còn đang nạp model; số dòng không đổi sau khi tải lại trang, không liên quan bản fix.
- Mock mode (`VITE_USE_MOCK=true`): biểu đồ vừa khung (923/923 px), tổng 30 bình luận.

## 4. Gate

| Gate | Kết quả |
|---|---|
| `npm run build` | đạt |
| pytest đầy đủ | 85 passed, 1 warning thư viện |
| Backend | không đổi so với vòng 1 (compileall và đối chiếu SQL giữ kết quả vòng 1) |

## 5. TODO

| TODO | Trạng thái |
|---|---|
| TODO-01 bố cục biểu đồ ngày | **CLOSED / VERIFIED BY CLAUDE** |
| TODO-04 phản hồi cũ khi đổi nhanh | **CLOSED** (phần `role="tab"` không có `tabpanel` vẫn còn, Low) |
| TODO-02 số mock khác số thật | mở, Low |
| TODO-03 test fail nếu chạy 00:00–02:00 | mở, Low |
| TODO-05 chỗ trống `<a / b / c>` của T12 trong file điều phối | mở, Tín cần ghi quyết định |

## 6. Kết luận

**PASS_WITH_TODO.** RF 0, blocker 0. T21 `CLAUDE_REVIEW → PO_REVIEW`. AC 8/8 giữ nguyên.

T14 vẫn `READY_FOR_HANDOFF`; prompt Codex T14 ở mục 8 của `claude_review_T21_PASS_WITH_TODO_2026-10-16.md`, không đổi.
