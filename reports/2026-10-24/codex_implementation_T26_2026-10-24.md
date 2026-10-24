# Codex Implementation Report

Task: T26 — Khung đánh giá sao bật lên khi bấm vào điểm
Date: 2026-10-24
Result: IMPLEMENTATION_COMPLETED / PENDING_CLAUDE_REVIEW
Branch: `task/T26-khung-danh-gia`
Baseline: `master` tại `6d49d16` (đã chứa T25 implementation `03e0d44` và review `c9f7eef`). Working tree sạch trước khi tạo nhánh.
Đổi schema: Không.

## Files Changed
- `frontend/src/components/RatingDialog.jsx`: component mới dùng dialog/showModal, StarRating hiện có, draft, thông báo, nút lưu/hủy/đóng và focus.
- `frontend/src/pages/MovieDetail.jsx`: nút điểm, dòng sao cá nhân, chuyển đăng nhập, nối dialog với API hiện có.
- `frontend/src/styles/global.css`: chỉ thêm class T26 và backdrop, không sửa :root hoặc luật CSS cũ.
- `CHANGELOG.md`, `docs/TASK_COORDINATION_ACTIVE.md` và report này.

## Implemented / Contract
- Bỏ hàng sao và status đầu MovieDetail; phim now_showing/ended có nút điểm, phim coming_soon chỉ hiện chữ.
- Dialog có tên truy cập qua h2/aria-labelledby, mở lấy số sao đã lưu. Chọn sao chỉ sửa draft. StarRating và CommentSection giữ nguyên file/hành vi.
- Lưu gọi api.ratings.set; hủy gọi remove. Cập nhật stars/avg/count và version bình luận; thông báo thành công ở dialog trong 1 giây rồi đóng. Lỗi hiển thị e.message và giữ dialog mở để thử lại.
- Khóa nút khi ratingBusy/commentBusy; khóa thêm thao tác lưu trong khoảng xác nhận thành công. Đóng qua nút, Esc hoặc tọa độ ngoài khung; trả focus về nút điểm. Vòng Tab/Shift+Tab trong các nút khả dụng.
- Chưa đăng nhập chuyển /dang-nhap với state.from nguyên location. Không thêm thư viện, animation hay thay đổi API/backend/schema.

## Focused browser verification (Chromium 156 / Playwright)
Dùng hai Vite dev server: real `http://localhost:5173` trỏ backend tạm cổng 8026; mock `http://localhost:5174`.
Playwright được cài ngoài repository trong `%TEMP%/firefly-t26-qa`; không sửa package/dependency của dự án. Script QA và log tạm cùng thư mục.

| AC | Bằng chứng thực thi |
|---|---|
| 01 | Không còn `.detail__info .star-rating`; có rating-trigger thay span điểm. |
| 02 | Real/mock ở 375/1280: chọn 4, lưu, thông báo, tự đóng, focus về nút và dòng Bạn đã chấm 4★. Probe riêng đối chiếu API: count +1, avg trên nút khớp kết quả. |
| 03 | Mở lại thấy 4, hủy → count -1, mất dòng sao cá nhân. Đóng/Esc/bấm ngoài sau chọn không lưu; probe đếm lời gọi set/remove xác nhận draft/đóng = 0, lưu = 1, hủy = 2. |
| 04 | Real/mock: nút điểm → đăng nhập, nhập tài khoản và quay lại /phim/1, mở được dialog. Cũng kiểm đăng ký từ luồng này. |
| 05 | Real/mock: coming_soon không có nút điểm hoặc dialog; real ended mở được dialog. |
| 06 | Real/mock ở cả hai viewport: Tab tới trigger, Enter mở, focus vào dialog, 12 lần Tab giữ bên trong; Esc đóng và trả focus. Kiểm Shift+Tab về trigger trước khi mở. |
| 07 | Real/mock: chọn 3 sao ở comment-form chưa đổi nút điểm; gửi bình luận mới lưu 3 sao và cập nhật trang. |
| 08 | Mock chạy cùng các probe draft/save/remove/coming_soon. |
| 09 | 4 tổ hợp real/mock × 375/1280: khung trong viewport, mọi nút sao >=44×44, ảnh đã xem trực tiếp; không pageerror hoặc console error trong luồng chính. 375 dùng reduced-motion: reduce, 1280 no-preference. |
| 10 | Full pytest và checklist hồi quy bên dưới. |

Probe bổ sung real: chặn request trả lỗi 400 thử nghiệm → nguyên thông báo trong dialog, dialog còn mở. Giữ request lưu pending → mọi nút bị disabled; giải phóng request lưu thành công. Các request bị chặn là probe lỗi có chủ đích, không dùng để thay gate runtime thật.

Ảnh bằng chứng (ngoài Git theo allowlist không cho thêm PNG):
- [Real 375](C:/Users/lemin/.codex/visualizations/2026/10/24/01a16e84-20c7-7200-973e-837ced77465f/T26-real-375.png)
- [Real 1280](C:/Users/lemin/.codex/visualizations/2026/10/24/01a16e84-20c7-7200-973e-837ced77465f/T26-real-1280.png)
- [Mock 375](C:/Users/lemin/.codex/visualizations/2026/10/24/01a16e84-20c7-7200-973e-837ced77465f/T26-mock-375.png)
- [Mock 1280](C:/Users/lemin/.codex/visualizations/2026/10/24/01a16e84-20c7-7200-973e-837ced77465f/T26-mock-1280.png)

## Final Gates
- `backend/venv/Scripts/python -m compileall -q backend/app`: exit 0.
- Backend uvicorn app.main:app cổng 8026, SQLite `%TEMP%/firefly-t26-qa/t26.db`, UPLOAD_DIR tạm: khởi động đạt. `/api/health`: status ok, classifier/active_model phobert_b, active_version phobert-B-2026-10-09, không fallback/lỗi.
- Chạy pytest từ backend: **194 passed**, 1 DeprecationWarning có sẵn của Starlette/anyio, 87.23s. Lần gọi ban đầu từ root thiếu module app; đã chạy lại đúng thư mục theo hướng dẫn.
- Build cuối sau thay đổi bàn phím: `VITE_USE_MOCK=false` và `true`, `npm run build`: cả hai exit 0, 92 modules.
- `git diff --check`: đạt; dự án không có linter riêng.
- Cổng 8000 đã có tiến trình khác: lần bind đầu không thành công; backend QA dùng 8026, frontend real trỏ rõ 8026, không dừng/dùng tiến trình cũ.

## Checklist hồi quy BOI_CANH mục 7
1. Real/mock: trang chủ có phim, hero chuyển phim bằng Phim sau; cả Xem chi tiết và Đặt vé mở PosterIntro, Esc đóng được.
2. Real/mock: menu Thể loại/Chủ đề chọn link lọc ra phim; tìm “meo muop” có Mèo Mướp.
3. Real/mock: khách bấm suất → đăng nhập; đăng ký tài khoản mới từ đó quay về đúng /dat-ve/:id. Luồng login có state.from cũng đã kiểm riêng.
4. Real/mock: chọn 2 ghế, xác nhận Đặt vé; Vé của tôi có vé, mở lại suất thấy cả 2 nút disabled với nhãn đã có người đặt (vé giữ chỗ theo T16).
5. Real/mock: gửi “Ko hay như quảng cáo, hơi thất vọng” bị ẩn; admin thấy điểm **1.00** với PhoBERT B thật; mock **0.87**. Điểm thật làm tròn 1.00 thay vì khoảng 0.99 của checklist cũ.
6. Health đạt với **phobert_b**, phù hợp quyết định Q3/model mặc định hiện tại; tên phobert trong checklist cũ là tên trước T10.
7. Mock dùng được đầy đủ luồng nhiệm vụ và hồi quy ở trên.

## Security / Scope
Không sửa backend, API, CommentSection, StarRating, :root, task record, .env, database thật hoặc dependency. Runtime QA chỉ ghi SQLite/upload tạm; không reset/migrate/seed database thật. Không đưa token/mật khẩu hoặc dữ liệu lớn vào Git. Không merge hoặc mở T13.

## Blockers / Follow-up
Không có blocker triển khai còn mở. Claude cần review độc lập code và gate, PO quyết định duyệt/merge. Đây là kết quả kiểm tra của implementer, không phải kết luận review độc lập hoặc tự PASS task.

## Handoff
T26 → CLAUDE_REVIEW. Task Record giữ nguyên bản PO đã duyệt. T13 tiếp tục chờ quyết định PO sau T26.
