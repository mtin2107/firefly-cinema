# Claude implementation — T34 (13/11/2026)

PO yêu cầu trong chat ("fix và tự test luôn"). Vì Claude viết code, **cần người review độc lập** (Codex hoặc Tín) trước khi merge.

## Lỗi
`_ensure_showtimes` (`backend/app/seed.py`) chỉ sinh suất cho phim có `status == "now_showing"` lưu trong DB. API phim dùng `effective_status`: phim `coming_soon` đã tới ngày khởi chiếu hiển thị "Đang chiếu". DB thật ngày 13/11: phim 6, 7, 11 hiện "Đang chiếu" nhưng 0 suất.

## Sửa
- `seed.py`: lọc phim bằng `effective_status(sql=True, today=window_days[0]) == "now_showing"` — cùng luật với `routers/movies.py` và `mock.js buildShowtimes`.
- `tests/test_seed.py`: thêm `test_coming_soon_movie_past_release_date_gets_schedule` (phim đã khởi chiếu có suất đủ 5 ngày; phim chưa khởi chiếu 0 suất). Test **FAIL trước khi sửa, PASS sau khi sửa**.

## Gate
| Gate | Kết quả |
|---|---|
| `python -m compileall -q backend\app` | OK |
| `pytest -q` toàn bộ | 290 passed |
| `npm run build` | OK |
| Backend khởi động + `/api/health` | `status ok`, classifier `phobert_b` |
| Mock mode | Không áp dụng (không đụng lớp API; mock đã dùng `effectiveStatus`) |

## Dữ liệu DB thật (không commit)
Sau khi sửa code, lịch 13–17/11 đã kín (4 phòng × 5 khung giờ = 20 suất/ngày) nên 3 phim vẫn 0 suất cho tới ngày rolling mới (18/11). PO chọn trong chat: **chia lại lịch**.
- Sao lưu trước khi thao tác: thư mục scratchpad của phiên (`dbbackup` trước khi khởi động backend, `dbbackup2` ngay trước khi chia lại).
- Script một lần đổi `movie_id` của 24 suất tương lai **chưa có vé** (0 suất tương lai có vé) từ phim đang nhiều suất sang 3 phim mới; kiểm `find_showtime_conflict` theo thời lượng phim mới; phim nhường luôn còn ≥ 2 suất/ngày.
- Sau thao tác: `integrity_check ok`, `foreign_key_check` rỗng; 12/12 phim đang chiếu có suất tương lai (5–10 suất/phim). Khởi động lại backend: tổng suất giữ 238, không sinh trùng.
- Hôm nay 13/11 chỉ Nửa Vầng Trăng Hà Tiên có 1 suất (các khung còn lại đã qua giờ); từ 14/11 mỗi phim có 2 suất/ngày (sáng + tối).

## Kiểm tra giao diện
Frontend real (5173) `/phim/7` (Mật Mã Bến Nghé): mục LỊCH CHIẾU hiện các ngày 14–17/11, suất 09:30 Phòng 4 và 19:30 Phòng 1. Chưa đi hết luồng đặt vé (luồng không đổi).

## Còn lại / rủi ro
- Phim sẽ khởi chiếu trong 5 ngày tới chỉ có suất từ lần khởi động backend vào/sau ngày khởi chiếu (giống mock).
- Khi phòng đã kín, phim mới chuyển sang "Đang chiếu" vẫn phải chờ ngày rolling mới hoặc admin xếp tay — giới hạn sẵn có của seed, ngoài phạm vi.
