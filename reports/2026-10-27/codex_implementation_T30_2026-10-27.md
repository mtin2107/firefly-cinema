# T30 — Báo cáo triển khai Codex — 27/10/2026

- Vai trò: Primary Implementer; chờ Claude review độc lập. Đây là kết quả thực thi DEV, không phải kết luận review hay duyệt PO.
- Nhánh: `task/T30-sua-loi-audit`, tách từ master `73eb3c737fe304f7ec1e58ca1f925010de24f5fe` (đã xác minh HEAD ban đầu).
- **Đổi schema: Có** — chỉ `Booking.__table_args__`: SQLite AUTOINCREMENT. Giữ mã `FF{id:05d}`, giữ hủy bằng xóa dòng.
- PO chốt trong chat: Q1=(a), Q2=8.0/10, Q3=PO tự reset DB thật **một lần sau merge T30**, gộp schema T29/T30.
- Ngoại lệ allowlist được PO cấp rõ trong chat: `backend/tests/test_booking_payment.py`, chỉ test xóa phim expired/rejected. Test cũ kỳ vọng 200, trái BUG-01 mới 409. Đã đổi tên/kỳ vọng và thêm kiểm bảo toàn booking, GET vé vẫn 200. Không sửa Task Record.
- Hai file đầu vào `docs/tasks/T30.md` và report audit Claude có sẵn ở trạng thái untracked trước khi làm; giữ nguyên nội dung, không đưa vào commit của Codex.

## Thay đổi theo lỗi

| Mã | Nguyên nhân và thay đổi |
|---|---|
| BUG-01 | Bộ lọc xóa phim bỏ qua expired/rejected. Bỏ điều kiện trạng thái ở backend/mock; bất kỳ booking nào cũng chặn 409 với nguyên câu đã chốt. Không sửa booking_out. Xóa phim chưa có booking vẫn xóa lịch/bình luận. |
| BUG-02 | SQLite INTEGER PRIMARY KEY cấp lại id lớn nhất vừa xóa. Bật sqlite_autoincrement cho bảng bookings; không đổi định dạng mã/hành vi hủy. Mock seq đã tăng đơn điệu, không sửa. |
| BUG-03 | Đếm held rồi insert không được bảo vệ. Một Lock cấp module bao đoạn create_booking, giữ nguyên thứ tự validation/thông báo/UNIQUE ghế. Có chú thích đúng Task Record: chỉ một worker; nhiều worker cần khóa DB. |
| BUG-04 | Ngưỡng cũ 4/5 còn lại sau đổi thang. TOP_RATED_MIN=8.0 ở backend/mock. Kiểm **trung bình chưa làm tròn** trước khi chọn top_rated, để 7.99 không bị làm tròn 8.0 rồi lọt; điểm hiển thị và thứ tự điểm/lượt giữ nguyên. Backend dùng HAVING AVG >=8 trong tập id thuộc bộ sưu tập; mock tính từ các ratings gốc chỉ trong nhánh top_rated. |
| BUG-05 | Magic bytes không đủ chứng minh cấu trúc tối thiểu. PNG có IHDR và IEND đúng 12 byte cuối, JPEG kết thúc FFD9, WebP RIFF size +8 bằng độ dài. Sai trả 422 “Ảnh bị hỏng hoặc không đầy đủ.” trước ghi file, chung cho poster/avatar và mock. Giữ lỗi định dạng/dung lượng. Fixture ảnh/test giới hạn 2 MB được cập nhật, không xóa ca test. |
| BUG-06 | history state còn sau F5. MyTickets giữ newBookingId trong component state một lần, replace history với state:null; giữ nguyên chữ/giao diện. |
| TEST-01 | Test suy “hôm nay” từ now-trừ giờ. Monkeypatch admin_sentiment.datetime ở 00:30/12:00/23:59 ngày 27/10/2026; dữ liệu “hôm nay” nằm lúc 00:00 cùng ngày, các ngày khác vẫn kiểm đầy đủ. Rà test_t23_dashboard_checkin và test_admin_features: không có cùng khẳng định hôm nay từ giờ trừ cần sửa; giữ nguyên. |

Không xử lý OBS-01..08, không thêm tính năng/thư viện/migration, không sửa model/normalize.

## Regression đối chứng master và nhánh

Worktree tạm detached `73eb3c7`: `C:\Projects\firefly-cinema-t30-baseline`. Chỉ chép đúng test mới `test_t30_regressions.py` sang; không chép production code nhánh. Dùng python venv của repo hiện tại, cwd backend của worktree. Mỗi test dùng SQLite tạo mới bằng Base.metadata.create_all trong tmp_path. UPLOAD_DIR và DATABASE_URL mặc định import cũng được đặt tạm ngoài repo. Mọi test lỗi dưới đây là assertion đúng lỗi nghiệp vụ, không phải lỗi import/thiếu dependency.

Lệnh chung (chạy một lần mỗi cwd, không chỉnh test giữa hai lượt cuối):

```powershell
# Gán DATABASE_URL/UPLOAD_DIR sang đường dẫn tạm trước mỗi lượt.
# Nhánh, cwd backend:
venv\Scripts\python -m pytest -q tests/test_t30_regressions.py
# Master worktree, cwd backend của worktree:
C:\Projects\firefly-cinema\backend\venv\Scripts\python -m pytest -q tests/test_t30_regressions.py --tb=short
```

| Nhóm test | Master 73eb3c7 | Nhánh T30 |
|---|---|---|
| BUG-01: delete_preserves_tickets expired/rejected | 2 fail: nhận 200 thay 409 | 2 đạt; GET me/admin mọi status/checkin 200, orphan=0 |
| BUG-02: code_never_reused | 1 fail: mã mới bằng mã đã hủy | 1 đạt; khách A hủy, khách B nhận mã lớn hơn, sqlite_master có AUTOINCREMENT |
| BUG-03: concurrent_hold_limit, 5 lượt x 4 thread | 5 fail: vượt 2 lần 201 | 5 đạt: mỗi lượt 2x201, 2x409 đúng câu, đúng 2 held trong DB |
| BUG-04: top_rated_boundary 4.5/7.99 | 2 fail: đều lọt | 2 đạt: đều bị loại qua HTTP với ratings thật trong DB |
| BUG-05: corrupt_image_rejected 3 định dạng x poster/avatar | 6 fail: nhận ảnh hỏng | 6 đạt: đúng 422/câu lỗi, không tạo UPLOAD_DIR |
| Ca kiểm soát: xóa phim không vé, ngưỡng 8/10, tranh cùng ghế | 4 đạt | 4 đạt |
| Tổng regression cuối | **16 fail, 4 đạt** (16.25 giây) | **20 đạt** trong focused cuối |

Ca tranh ghế dùng hai thread/hai người/hai Session: đúng một 201 và một 409. Ca bốn request giữ vé dùng Session riêng từng request, Barrier khởi phát cùng lúc; after_cursor_execute chỉ làm chậm SELECT đếm held 150ms để mở rộng cửa sổ race, không đổi số đếm/kết quả, không mock khóa production.

Lượt đầu phát hiện fixture test đúng 2 MB bị thêm padding sau IEND/FFD9 hoặc sai RIFF size; sửa fixture có cấu trúc đúng thay vì nới validator. Lượt full đầu: 261 đạt/1 lỗi test xóa phim cũ; PO cấp ngoại lệ như trên. Lượt rà biên phát hiện làm tròn 7.99, đã thay ca unit aggregate bằng regression HTTP/DB thật và sửa lọc trước làm tròn ở cả hai chế độ.

## Gate và bằng chứng

- Focused trước full: nhóm T30/sentiment/ratings/poster/avatar 99/99; payment 8/8 sau ngoại lệ; focused cuối T30 + ratings + sentiment **53/53**, 45.96 giây.
- compileall `backend\venv\Scripts\python -m compileall -q backend\app`: exit 0.
- Full pytest cuối sau sửa lọc 7.99: **263/263 đạt**, 151.59 giây (exit 0). Chỉ một DeprecationWarning Starlette/anyio có sẵn; không còn ngoại lệ chạy theo giờ.
- `npm run build` với VITE_USE_MOCK=false và true: exit 0 cả hai sau sửa cuối; 94 modules; real 456.77 kB JS, mock 484.59 kB JS. Không đổi .env.
- Backend uvicorn cổng 8090 dùng `%TEMP%/t30-runtime.db` và `%TEMP%/t30-runtime-uploads`; startup tạo/seed DB tạm, `/api/health` status ok, classifier/active_model **phobert_b**, active_version **phobert-B-2026-10-09**, loaded=true, classifier_error=null. Đây là PhoBERT B thật đã chốt, không phải FakeClassifier; literal trường classifier của code hiện tại là phobert_b (không đổi sang tên phobert để khớp ví dụ tài liệu).
- Trình duyệt Chromium headless có sẵn; Vite real 5190 (API 8090), mock 5191. Không cài thêm package. Chạy với context/localStorage riêng, chỉ ghi dữ liệu thử vào SQLite/UPLOAD_DIR tạm hoặc localStorage context thử.
- Canvas trình duyệt xuất ảnh PNG/JPEG/WebP 1x1: cả poster và avatar nhận cả ba ở real/mock. PNG cắt cụt/JPEG thiếu đuôi/RIFF sai size: 6 kiểm tra mỗi chế độ đều trả 422 đúng câu. Backend test còn xác minh không tạo file/thư mục khi ảnh sai.
- Mock: fixture localStorage riêng có vé expired/rejected → xóa phim 409; top_rated loại trung bình 4.5 và **7.99**, nhận 8.0; mã sau đặt/hủy/đặt là FF00004 → FF00005.
- BUG-06 real/mock: qua UI đặt vé → thông báo hiện; history.state.usr=null; reload mất thông báo; mở suất thấy ghế bị disable; Back không hiện lại thông báo.

## Checklist hồi quy BOI_CANH_DU_AN mục 7

| # | Real | Mock |
|---|---|---|
| 1 Trang chủ/phim/hero/chi tiết/đặt vé/hiệu ứng | Đã chạy: 10 movie cards; nút Phim sau đổi tiêu đề hero; click Xem chi tiết/Đặt vé đi đúng phim, chờ chuyển cảnh | Đã chạy cùng luồng |
| 2 Menu Thể loại/Chủ đề, tìm “meo muop” | Đã bấm từng menu và ô tìm kiếm UI, nhận Mèo Mướp Đi Lạc | Đã chạy cùng luồng |
| 3 Đăng ký, chặn khách chưa đăng nhập, quay lại suất | Bấm giờ → đăng nhập → đăng ký mới bằng UI → đúng /dat-ve/:id | Đã chạy cùng luồng |
| 4 Hai ghế, ghế xám, Vé của tôi | Đặt hai ghế qua UI; trang vé/thông báo; F5/Back; mở lại suất hai ghế disabled | Đã chạy cùng luồng |
| 5 Bình luận tiêu cực và admin | UI gửi đúng câu; ẩn mặc định; API admin negative_score=0.9992, model B; bảng kiểm duyệt hiển thị Tiêu cực/1.00 | UI ẩn; mock score 0.87, cùng hành vi; không đòi mock giả điểm model thật |
| 6 Health PhoBERT | Đã chạy HTTP: phobert_b/version thật như trên | Không có backend health giả; dùng chung kiểm real, mock được kiểm luồng riêng |
| 7 Mock mode | So sánh real với mock đang chạy riêng | Đã chạy UI + API thực, không chỉ build |

Kiểm bằng browser automation và assertions cho hành vi; không đưa ra đánh giá thẩm mỹ hay kết luận independent review. Log/script scratch nằm trong TEMP trong lúc thực thi; kết quả cốt lõi được ghi ở report này.

## Phạm vi, dữ liệu và bàn giao

- Chỉ các file trong mục 6 T30, cộng ngoại lệ test_booking_payment.py do PO cấp. Không stage hai file đầu vào chưa tracked; không sửa Task Record.
- Không đọc/ghi/xóa/reset database thật, không ghi backend/uploads, .env, model hoặc backup. Runtime chỉ dùng temp; pytest dùng FakeClassifier theo fixture gốc và DB tmp_path. Model thật chỉ được runtime nạp để chạy PhoBERT, không thay artifact.
- `git diff --check`: exit 0. Kiểm danh sách file sửa không chứa .env/*.db/model/CSV/upload thật.
- HUONG_DAN mục T30 và CHANGELOG đã cập nhật; chưa thực thi reset DB. PO tự làm sau merge.
- Khóa chỉ có hiệu lực trong một worker như Task Record; chưa triển khai nhiều worker.
- T30 IN_PROGRESS → CLAUDE_REVIEW sau gate; chờ Claude kết luận và PO duyệt. Không tự review, không tự PASS, không merge, không đóng task, không mở T13.

Dọn dẹp cuối: đã dừng backend/Vite thử, xóa worktree master tạm và DB/uploads runtime tạm; giữ script/log scratch T30 trong `%TEMP%` để tra cứu khi cần. Không tác động worktree T15 hoặc tiến trình khác.
