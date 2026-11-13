# Claude review — T34 — PASS_WITH_TODO (13/11/2026)

> **Lưu ý: đây là SELF-REVIEW, không độc lập.** Claude vừa viết code T34 vừa review theo yêu cầu PO trong chat ("bạn review cho tôi luôn được chứ"). PO quyết định có chấp nhận thay cho review độc lập hay không (tiền lệ T32).

- Nhánh: `task/T34-suat-chieu-phim-moi-khoi-chieu`, commit được review `2ae64ab`, base `master` `8a01a5f`.
- Kết luận: **PASS_WITH_TODO** — Required Fix 0, blocker 0.

## 1. Diff và phạm vi
`git diff master...task/T34-suat-chieu-phim-moi-khoi-chieu`: 5 file, đều trong allowlist `docs/tasks/T34.md` mục 6 — `backend/app/seed.py` (+5/−1), `backend/tests/test_seed.py` (+25), `docs/TASK_COORDINATION_ACTIVE.md`, `docs/tasks/T34.md`, report implementation. `git diff --check` sạch. Không file `.db`, `.env`, model, `backend/models/` nào bị track. Không đổi schema, không thêm thư viện, không đụng frontend/`normalize()`.

## 2. Acceptance Criteria
| AC | Kết quả | Bằng chứng |
|---|---|---|
| AC-01 phim coming_soon đã khởi chiếu có suất đủ cửa sổ | PASS | test mới; FAIL trên code cũ, PASS sau sửa |
| AC-02 phim chưa khởi chiếu 0 suất | PASS | cùng test; probe DB mới: không phim sắp chiếu/ngừng nào có suất |
| AC-03 test seed cũ vẫn đạt | PASS | `tests/test_seed.py` 10/10 |
| AC-04 DB thật: 3 phim có suất, trang phim hiện lịch | PASS | 12/12 phim đang chiếu có suất tương lai; `/phim/7` hiện 14–17/11 |
| AC-05 gate web | PASS | mục 4 |

## 3. Đánh giá kỹ thuật
- Dùng lại `effective_status(sql=True)` sẵn có — cùng luật với `routers/movies.py`, `chat_assistant.py`, `mock.js buildShowtimes`. Sửa gốc lỗi ở một chỗ, không nhân bản luật.
- Truyền `today=window_days[0]` thay vì để `taxonomy` tự gọi `date.today()`: cần thiết để test đóng băng ngày qua `app.seed.date` hoạt động đúng.
- So sánh chuỗi `release_date <= today.isoformat()` an toàn vì `schemas.py` bắt buộc dạng `YYYY-MM-DD`.
- `_read_seed_state` nhận `movie_ids` mới (gồm phim effective) — với DB chưa có sidecar, phim mới được đánh dấu "đã xử lý" cho các ngày đã seed, đúng nguyên tắc bảo thủ hiện có. Với DB đã có sidecar, phim mới chưa nằm trong `handled_movie_ids` nên được xếp suất nếu còn phòng.
- Bảo mật: không đổi endpoint, quyền, input.
- Probe DB mới hoàn toàn (`seed()` với ngày thật, DB tạm, đã xóa): 12/12 phim đang chiếu có suất (phim 6/7/11: 5–6 suất).

## 4. Gate chạy lại trên `2ae64ab`
| Gate | Kết quả |
|---|---|
| `python -m compileall -q backend\app` | OK |
| `pytest -q` toàn bộ | 290 passed |
| `npm run build` | OK |
| Backend + `/api/health` | `ok`, `phobert_b` (chạy trong implementation, DB thật) |
| Mock mode | Không áp dụng — không đụng lớp API |

## 5. TODO / OBS
- **TODO-01 (Low):** phim sẽ khởi chiếu trong cửa sổ 5 ngày chỉ được xếp suất từ lần khởi động backend vào/sau ngày khởi chiếu; khi phòng đã kín thì chờ ngày rolling mới hoặc admin xếp tay. Giống hành vi mock; ngoài phạm vi T34.
- **OBS-01:** thao tác chia lại 24 suất trên DB local là thao tác dữ liệu một lần, không nằm trong code; sao lưu ở thư mục scratchpad tạm của phiên — nên chép sang `backup\` nếu muốn giữ.
- **OBS-02:** self-review, xem lưu ý đầu report.

## 6. Bước tiếp theo
Task → `PO_REVIEW`. Không có task kế tiếp nào đã chọn để đặt `READY_FOR_HANDOFF` (T33 mới là đề xuất chưa duyệt). Tín merge `task/T34-suat-chieu-phim-moi-khoi-chieu` vào `master` nếu đồng ý; Claude không merge.
