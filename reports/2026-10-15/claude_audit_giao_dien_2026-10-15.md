# Claude — Rà soát giao diện thực tế Firefly Cinema (15/10/2026)

Bổ sung cho `claude_audit_toan_web_2026-10-15.md`. Chạy backend thật (PhoBERT B) và frontend real mode trên SQLite và UPLOAD_DIR tạm, cổng 8005/5178. Đã tắt server và gỡ cấu hình tạm sau khi kiểm. Không sửa production code.

Khổ màn hình đã xem: khoảng 535px (khung trình duyệt) và 375px (giả lập điện thoại, kiểm bằng DOM). Chưa chụp được ở 1280px vì khung trình duyệt nhỏ.

## 1. Luồng đã đi qua

| Luồng | Kết quả |
|---|---|
| Trang chủ: hero 3D, tab Đang chiếu/Sắp chiếu, lưới phim, footer | Hiển thị đúng, có lỗi UI-02 |
| Menu → Thể loại → Khám phá (lọc "Hài hước" ra 5 phim) | Đúng |
| Đăng nhập sai → báo lỗi tiếng Việt; đăng nhập đúng → về trang chủ | Đúng |
| Chi tiết phim → lịch chiếu 5 ngày → chọn suất | Đúng |
| Chọn ghế C5, C6 → tổng 190.000 đ → Xác nhận → Đặt vé → Vé của tôi (FF00141, "Giữ chỗ") | Đúng tiền, đúng trạng thái; có lỗi UI-01, UI-03 |
| Trợ lý chat: mở, gửi câu gợi ý "Gợi ý phim hài đang chiếu" | **Trả lời sai** (UI-04) |
| Admin: Quản lý phim, Suất chiếu, Vé, Bình luận, So sánh mô hình (chấm 5 mô hình) | Đều chạy được |
| 375px: 8 trang khách | Không trang nào tràn ngang |
| Console | 0 lỗi |

Hàng ghế A lần trước bị ẩn (`visibility:hidden`): lần này hiện đủ khi trình duyệt chạy thật. **Đóng nghi vấn, đó là do môi trường.**

## 2. Lỗi giao diện

### UI-04 — HIGH: Trợ lý chat trả lời sai "không có phim hài đang chiếu"
- File: `backend/app/chat_assistant.py:65` (`search_movies`)
- Evidence: câu gợi ý có sẵn "Gợi ý phim hài đang chiếu" nhận câu trả lời "Hiện tại rạp không có phim hài nào đang chiếu". Thực tế "Thứ Bảy Không Ngủ" (Hài hước, đang chiếu) chính là phim vừa đặt vé. Gọi thẳng hàm: `genre="Hài hước"` → 1 phim; `"hài hước"`, `"Hài"`, `"comedy"`, `"hai-huoc"` → rỗng.
- Nguyên nhân: so khớp thể loại chính xác tuyệt đối, phân biệt hoa/thường và có dấu/không dấu, trong khi model AI tự đặt chuỗi thể loại. T17 TODO-03 chỉ sửa phía mock.
- Expected fix: so sánh `_plain(genre)` nằm trong `_plain(g)` cho từng thể loại. Mô tả tham số `genre` trong `TOOLS` nên liệt kê tên thể loại hợp lệ. Thêm test cho chữ thường và không dấu.
- Ảnh hưởng: đây là **câu gợi ý mặc định**, nên hội đồng bấm thử là gặp ngay.

### UI-01 — MEDIUM: Trang "Vé của tôi" bị cuộn ngang sau khi đặt vé
- File: `frontend/src/styles/global.css:700` (`.ticket__burst { inset:-40px; width:calc(100% + 80px) }`), `frontend/src/components/TicketStub.jsx:82`
- Evidence: ngay sau khi đặt vé, `scrollWidth` 546 > `clientWidth` 520, xuất hiện thanh cuộn ngang ở đáy trang. Canvas hiệu ứng "in vé" vẫn còn trong DOM sau hơn 5 giây.
- Expected fix: gỡ canvas khi hiệu ứng chạy xong, hoặc cho khung cha `overflow:hidden` / `overflow-x:clip`.

### UI-03 — MEDIUM: Không có QR nhưng vẫn hiện nút "Tôi đã chuyển khoản"
- File: `frontend/src/components/TicketStub.jsx:58-61`
- Evidence: vé hiện dòng "Chưa cấu hình thanh toán QR. Vui lòng thanh toán tại quầy" và ngay dưới đó là nút "Tôi đã chuyển khoản". Người dùng không có số tài khoản nào để chuyển. Nếu bấm, vé chuyển sang `pending_verify` và giữ ghế vô thời hạn (F-03 của báo cáo trước).
- Expected fix: chỉ hiện nút khi có `qrUrl`. Trước demo, điền `BANK_ACCOUNT` và `BANK_ACCOUNT_NAME` trong `.env` để luồng QR hiển thị đầy đủ.

### UI-02 — LOW: Thanh cuộn dọc thừa ở tab "Đang chiếu / Sắp chiếu" và sơ đồ ghế
- File: `frontend/src/styles/global.css:212-213` (`.tabs { overflow-x:auto }` + `.tab { margin-bottom:-1px }`); `.seatmap__scroll` (cao 291 so với 288px)
- Evidence: trên Windows hiện một thanh cuộn dọc nhỏ có mũi tên ▲▼ cạnh tab và bên phải sơ đồ ghế. Nguyên nhân: `overflow-x:auto` kéo theo trục y cũng thành auto, và nội dung vượt 1–3px.
- Expected fix: thêm `overflow-y: hidden` cho `.tabs` và `.seatmap__scroll`.

### UI-05 — LOW: Nút chat đom đóm lệch và che nội dung
- File: `frontend/src/components/ChatWidget.jsx:36,117` dùng `window.innerWidth` (tính cả thanh cuộn)
- Evidence: nút nằm lệch 5px ra ngoài vùng nhìn thấy (`right:-5px`), che mũi tên mục "Chủ đề" trong menu mở và che cột bảng ở trang admin. Admin không được dùng trợ lý nhưng nút vẫn hiện.
- Expected fix: dùng `document.documentElement.clientWidth`; ẩn widget với admin.

### UI-06 — LOW: Chi tiết hoàn thiện
- Khung chat ở màn hình thấp: vùng tin nhắn chỉ khoảng 130px, câu chào bị cắt ở mép trên.
- Khám phá: 5 ô chọn lọc có độ rộng không đều (153/323/303/188px).
- Định dạng ngày không đồng nhất: "15-10" ở dòng hủy giữ chỗ, chỗ khác ghi "15/10/2026".
- Admin Quản lý vé mặc định lọc "Chờ xác nhận", nên vé giữ chỗ (trả tại quầy) không hiện tới khi đổi bộ lọc.
- So sánh mô hình: cột Mô hình hiện tên mã `phobert`, `svm`, `lr`, `nb`. Khi bảo vệ nên ghi "PhoBERT A", "SVM"...
- Ghế trên điện thoại cao khoảng 29px (khuyến nghị ≥ 44px). Chấp nhận được vì sơ đồ có 12 cột và cuộn ngang.
- Poster toàn bộ là khối màu kèm tên phim. Gọn và nhất quán, nhưng trông như bản nháp. Dùng chức năng T19 tải 5–9 poster thật cho phim demo thì giao diện sẽ thuyết phục hơn nhiều.

## 3. Đánh giá chung về giao diện

**Điểm mạnh:** phong cách thống nhất (nền đen, vàng đom đóm, font tiêu đề đậm). Chữ tiếng Việt đầy đủ, thông báo lỗi rõ. Luồng đặt vé ngắn, 4 bước, tổng tiền luôn hiển thị. Hiệu ứng T18 mượt, không lỗi console. Responsive tốt, không trang nào tràn ngang ở 375px (trừ UI-01 lúc vừa đặt vé).

**Điểm yếu:** chatbot trả lời sai ngay câu gợi ý mặc định (UI-04). Luồng thanh toán mâu thuẫn khi không có QR (UI-03). Vài lỗi tràn hoặc thanh cuộn lặt vặt làm giảm cảm giác hoàn thiện. Poster giả.

## 4. Kết luận

Giao diện **đạt mức bảo vệ được**. Nên sửa trước buổi bảo vệ theo thứ tự:
1. **UI-04** chatbot tìm thể loại (sửa vài dòng và thêm test), **UI-03** ẩn nút khi không có QR, kèm cấu hình tài khoản ngân hàng trong `.env`.
2. **UI-01, UI-02, UI-05**: mỗi lỗi sửa 1–2 dòng CSS/JS.
3. Tải poster thật cho phim demo (việc dữ liệu, không cần code). Có thể gộp vào T12.

Mục 1–2 có thể gộp chung với F-01..F-04 của báo cáo trước thành một task "gia cố trước bảo vệ". Không đổi schema.
