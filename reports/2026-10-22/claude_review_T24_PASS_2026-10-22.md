# Claude Independent Review — T24

- Task: T24 — Sửa lỗi rà soát trước v1.0
- Nhánh: `task/T24-sua-loi-ra-soat` · commit review: `32e6b4d` · baseline `master` `59dcaee`
- Ngày: 2026-10-22 · Reviewer: Claude
- **Kết luận: PASS** — AC 8/8, Required Fix 0, 1 OBS.

## 1. Phạm vi và quy tắc
- 15 file, tất cả trong allowlist T24 mục 6. Không đổi schema (không phải xóa `firefly.db`), không thêm thư viện; `booking_rules.py`, `models.py`, `seats.py`, `classifier.py` không đổi; `.env` và DB thật không đụng.
- Mock trả `bookable`, lọc lịch chiếu và câu lỗi giống real.

## 2. Gate độc lập
| Gate | Kết quả |
|---|---|
| compileall | exit 0 |
| pytest | **148 passed** (thêm `test_t24_cutoff.py`: đồng hồ cố định −1/0/29/30/31 phút) |
| npm run build | đạt |
| Backend DB tạm mới | health `ok`, `phobert_b` |
| Mock | đạt |

## 3. Đối chiếu Acceptance Criteria
| AC | Kết quả | Bằng chứng |
|---|---|---|
| AC-01 | PASS | Lúc 21:08: `/api/showtimes/1` (09:30 hôm nay) `bookable=false`; lịch chiếu phim 1 bắt đầu từ suất 22:00. Mock: suất sớm nhất được liệt kê cách hiện tại 50 phút. pytest kiểm biên 29/30/31 phút |
| AC-02 | PASS | Trình duyệt `/dat-ve/1`: "Suất chiếu đã bắt đầu, không thể đặt vé. Về lịch chiếu" (link `/phim/1#lich-chieu`), fieldset ghế `disabled`, bấm ghế không chọn được, nút "Tiếp tục" tắt |
| AC-03 | PASS | pytest: ≤0 phút → "Suất chiếu đã bắt đầu, không thể đặt vé."; 1..30 phút → câu "sắp bắt đầu" cũ. Mock: suất 09:30 → 400 câu "đã bắt đầu" |
| AC-04 | PASS | Tab 7/30/90 (`aria-selected` đúng, bấm 7 ngày → 7 cột), thẻ `sentiment-summary` giống trang Thống kê; bảng xếp doanh thu giảm dần (5.100.000 → 3.660.000 → 3.200.000 → 3.170.000); tải/lỗi dùng `Loading`/`ErrorState` |
| AC-05 | PASS | User thường vào `/quan-tri/tong-quan` → tiêu đề "Không có quyền truy cập – Firefly Cinema" |
| AC-06 | PASS | `/phim/9999`, `/dat-ve/999999` chỉ còn "Về trang chủ"; lỗi khác vẫn truyền `onRetry` (đọc code: điều kiện `status === 404`) |
| AC-07 | PASS | "Vé của tôi" có nhóm "Sắp xem" / "Đã qua"; vé paid suất 09:30 hiện "Đã chiếu"; vé hết hạn nằm ở "Đã qua" |
| AC-08 | PASS | Mock đạt; 375px: `/quan-tri/tong-quan`, `/ve-cua-toi`, `/dat-ve/1`, `/phim/1` không tràn ngang; pytest cũ + mới đạt |

## 4. Quan sát (không chặn)
- **OBS-01:** thẻ "Điểm sao" trên trang Tổng quan dùng cỡ chữ lớn của `sentiment-summary` nên "4.0 / 5 · 67 lượt" xuống dòng ở 1280px. Chỉ thẩm mỹ.

## 5. Trạng thái
T24 `CLAUDE_REVIEW → PO_REVIEW`. T13 → `READY_FOR_HANDOFF`, nhưng prompt T13 cần PO điền quyết định T12 TODO-01 và T14 TODO-02 trước khi gửi.
Việc của Tín: merge `task/T24-sua-loi-ra-soat` vào `master` (không phải xóa DB); tạo `task/T13-v1` từ `master` mới.

## 6. Bàn giao task kế tiếp — prompt Codex T13
```text
Bạn là Codex, dự án Firefly Cinema (C:\Projects\firefly-cinema, Windows + PowerShell).
Đọc theo thứ tự: docs/PROJECT_SOURCE_OF_TRUTH.md, docs/AGENT_RULES.md, docs/TASK_COORDINATION_ACTIVE.md, docs/tasks/T13.md. T13.md là bản PO đã duyệt.
T24 đã merge vào master. Làm trên nhánh task/T13-v1 (tạo từ master mới). Đầu tiên ghi closure T24 (merge hash) và đặt T13 → IN_PROGRESS.

Quyết định PO trước T13 (Tín điền trước khi gửi):
- T12 TODO-01 (model B che câu khen phim 1): <giữ nguyên + ghi hạn chế | admin duyệt sẵn | đổi phim mở đầu>
- T14 TODO-02 (mã vé dùng lại sau khi hủy): <ghi hạn chế | ...>

Nhiệm vụ: T13 "Chốt v1.0 và sao lưu" — chỉ tài liệu và sao lưu, không viết tính năng.
- README.md (giới thiệu, ảnh, tính năng gồm T16–T24, kết quả F1 A/B/SVM/NB/LR và T15, cách chạy nhanh), HUONG_DAN.md (cài từ số 0, gắn model A/B/SVM, cấu hình .env gồm BANK_* cho QR và CHAT_* cho chatbot — chỉ tên khóa, không giá trị; chạy test; reset demo).
- Mục "Hạn chế" gom: các quyết định PO ở trên, T14 TODO-04 (đổi mật khẩu không vô hiệu token cũ), T22 (ai đăng nhập cũng chấm sao; OBS-01 model B nhầm câu khen), T23 OBS-01 (soát vé không chặn theo giờ chiếu), T24 OBS-01.
- docs/SAO_LUU.md, docs/images/*, CHANGELOG.md [1.0.0], cập nhật cuối CONG_NGHE.md/ARCHITECTURE.md; xử lý T18 TODO-03 và T00 TODO-03 theo T13.md.
Ràng buộc: chỉ file trong mục 6 của T13.md; không sửa code; không commit model/DB/.env/dữ liệu lớn; không đọc hay in giá trị khóa trong .env.
Gate: compileall, pytest, npm run build (real + mock) để xác nhận không hồi quy.
Commit "[T13] mô tả". Viết reports/YYYY-MM-DD/codex_implementation_T13_YYYY-MM-DD.md, đặt T13 sang CLAUDE_REVIEW. Không merge, không gắn tag v1.0 (Tín gắn).
```

## 7. Quét hồi quy toàn web trước merge (theo yêu cầu PO, 22/10/2026 21:40)
Trên `task/T24-sua-loi-ra-soat` `d6cf6eb`, backend thật + DB tạm mới, health `phobert_b`.

| Luồng / phạm vi | Kết quả |
|---|---|
| Đặt vé bằng giao diện: trang chủ → "Đặt vé" → suất → 2 ghế VIP → xác nhận → Vé của tôi | Đạt: H11, H12 = 190.000 đ (95.000/ghế VIP); vé mới ở "Sắp xem", đếm ngược 14:57 |
| Admin: tìm vé theo mã → "Đã nhận tiền" → soát vé (mã chữ thường) | Đạt: "Đã xác nhận vé FF00144."; soát xong nút khóa; khách thấy "Đã vào rạp lúc 21:42" |
| Chấm sao + bình luận ẩn danh + xóa | Đạt: 4.3 (4) → 4.4 (5); "Khán giả ẩn danh ★★★★★"; xóa được |
| So sánh mô hình | Đạt: 5 mô hình trả nhãn và thời gian |
| 15 route user + 8 route admin, 1280px và 375px | Đạt: không tràn, không ảnh lỗi, không nút thiếu tên, tiêu đề đúng, 0 lỗi console |
| Mock, khách | Đạt: trang công khai hiển thị; trang cần đăng nhập/admin chuyển sang đăng nhập; 0 lỗi console |

Quan sát thêm (có từ trước, không do T24, không chặn): token sống 24 giờ; nếu hết hạn giữa phiên, trang báo "Phiên đăng nhập đã hết hạn" kèm nút "Thử lại" thay vì tự chuyển sang đăng nhập. Khuyến nghị: đăng nhập lại ngay trước buổi demo.

**Kết luận quét: không phát hiện hồi quy. T24 sẵn sàng merge.**
