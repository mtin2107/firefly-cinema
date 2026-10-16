# Codex Implementation Report — T12 — 16/10/2026

## Phạm vi

- Nhánh: `task/T12-demo`.
- Đổi schema: Không.
- Database thật `backend/firefly.db`: không reset, không khởi động backend trỏ vào file này.
- Toàn bộ reset, health và API gate dùng SQLite tạm dưới `backup/T12_gate/`.

## Kết quả triển khai

- Thêm `backend/scripts/reset_demo.py`: chỉ chấp nhận SQLite file cục bộ; đường dẫn tương đối luôn quy về `backend/`; yêu cầu `ADMIN_PASSWORD`; kiểm tra integrity, sao lưu DB/sidecar có timestamp trước khi thay; phục hồi bản cũ nếu seed lỗi.
- Dùng lại `seed.py`, bỏ mật khẩu admin mặc định viết trong code. Khi reset demo thiếu `ADMIN_PASSWORD`, script dừng trước khi tạo DB.
- Thêm 30 bình luận tự viết trong `demo_comments.json`, chấm bằng model active tại lúc seed; 6 phim, trải 17 ngày, có bình luận châm biếm/chê một phần/khen/chê rõ, 8 bình luận đã duyệt và 2 ca model–admin bất đồng.
- Seed vé demo có `paid`, `pending_verify`, `expired`; vé expired có mốc tạo `HOLD_MINUTES + 1` và không giữ ghế, không dựa vào vé `held` cũ chờ request dọn.
- Thêm `reset-demo.bat`, `chay-firefly.bat`, kịch bản 6 phút 30 giây và bộ dữ liệu mock tương ứng.
- Mock flow có 30 bình luận, ba trạng thái vé và hai hàng minh họa PhoBERT A/B cho câu “lê thê”.

## Gate an toàn của reset

| Probe | Kết quả |
|---|---|
| `DATABASE_URL=postgresql://...` | Từ chối bằng tiếng Việt, exit `2` |
| `ADMIN_PASSWORD` rỗng | Từ chối bằng tiếng Việt, exit `2`, không tạo DB |
| Resolve từ repo và từ `backend\` | Cùng `C:\Projects\firefly-cinema\backup\T12_gate\firefly.db` |
| SQLite integrity / foreign key | `ok` / không có vi phạm |
| Backup trước lần reset thứ hai | Tạo file timestamp trong `backup\` trước khi xóa DB tạm |
| `reset-demo.bat` | exit 0 trên DB tạm; kết quả đúng 21/99/143/30 |
| `chay-firefly.bat` | mở backend + frontend; tự chờ và báo `classifier=phobert_b`; hai tiến trình gate đã được dừng sau kiểm tra |

## Hai lần reset liên tiếp

Model active cả hai lần: `phobert_b`, phiên bản `phobert-B-2026-10-09`.

| Chỉ số | Lần 1 | Lần 2 | So sánh |
|---|---:|---:|---|
| Wall time, gồm nạp model | 23,08 giây | 23,26 giây | đều dưới 1 phút |
| Thời gian seed, không tính nạp model | 4,21 giây | 4,23 giây | đạt |
| Phim | 21 | 21 | bằng nhau |
| Suất chiếu | 99 | 99 | bằng nhau |
| Vé | 143 | 143 | bằng nhau |
| Bình luận | 30 | 30 | bằng nhau |
| Nhãn model tiêu cực | 16 | 16 | bằng nhau |
| Bình luận đã có nhãn admin | 8 | 8 | bằng nhau |
| Trạng thái vé | expired 1; paid 141; pending_verify 1 | expired 1; paid 141; pending_verify 1 | bằng nhau |

Phân bố tỷ lệ tiêu cực hiệu lực theo 6 phim: `0,00; 0,40; 0,60; 0,80; 0,80; 1,00`. Ngày bình luận từ `30/09/2026` đến `16/10/2026`, đủ 17 ngày lịch khác nhau.

## Đầu ra model thật cho câu “lê thê”

Câu chạy trực tiếp qua checkpoint thật ngày 16/10/2026:

`Phim dài lê thê, nửa đầu buồn ngủ thật sự.`

```text
phobert|A-backend|binh_thuong|0.0485
phobert_b|phobert-B-2026-10-09|tieu_cuc|0.9990
```

Kết quả xác nhận điều kiện demo tại thời điểm gate: A sai (bình thường), B đúng (tiêu cực).

## Quality gate

| Gate | Kết quả |
|---|---|
| `compileall` cho `backend/app`, `backend/scripts` | exit 0 |
| Backend thật trên SQLite tạm | startup đạt; `/api/health` 200, `classifier=phobert_b`, không fallback |
| API dữ liệu demo | 9 phim đang chiếu, 30 bình luận; vé có đủ ba trạng thái yêu cầu |
| Full pytest | `81 passed`, 1 warning thư viện; exit 0 |
| Frontend build real | đạt, 82 modules |
| Frontend build mock | đạt, 82 modules |
| Mock flow | đạt: danh sách phim → suất/ghế → booking `held` → bình luận bị che theo nhãn → admin confirm/relabel → so sánh A/B; seed có `paid/pending_verify/expired` |
| `git diff --check` | đạt |

## Checklist hồi quy 7 mục

- [x] Danh sách/phim đang chiếu: real API và mock đều trả 9 phim.
- [x] Chi tiết phim, suất chiếu và ghế: mock probe lấy được suất tương lai và ghế trống.
- [x] Đặt vé: khách tạo vé `held`, đúng luật giữ 15 phút.
- [x] Vé của tôi/admin vé: dữ liệu seed có `paid`, `pending_verify`, `expired`; lọc admin hoạt động.
- [x] Bình luận: câu tiêu cực trả `effective_negative=true` và bị che mặc định.
- [x] Kiểm duyệt: admin xác nhận rồi đổi nhãn sang `0`, nhãn hiệu lực cập nhật.
- [x] So sánh model/health: real health dùng PhoBERT B; model thật A/B và mock A/B đều trả đủ contract.

## Đối chiếu Acceptance Criteria

- AC-01: có bằng chứng DEV hai lần reset, số lượng bằng nhau và thời gian dưới 1 phút.
- AC-02: chờ Tín chạy trọn kịch bản hai lần từ lúc khởi động máy và ghi giờ trong PO report.
- AC-03: kịch bản 6 phút 30 giây; từng bước có thời lượng, câu nói, nội dung gõ và kết quả kiểm được.
- AC-04: có phương án mất mạng và model lỗi chuyển sang mock mode.
- AC-05: pytest, build real/mock và checklist hồi quy 7/7 đã chạy.

Không tự review, không tự kết luận PASS; bàn giao Claude kiểm tra độc lập.
