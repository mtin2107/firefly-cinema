# T11 — Báo cáo Runtime AC-06 và bàn giao review

- Ngày thực hiện: 11/10/2026
- Branch: `task/T11-kiem-thu`
- Round 1 HEAD trước runtime: `f9a7f3409a3510b2d4176a1d08f1236ae0b35c13`
- PO decision: `APPROVED_WITH_CONDITIONS`, cấp Runtime Authorization riêng cho AC-06
- Trạng thái kết thúc DEV: `CLAUDE_REVIEW` (không tự review/PASS/PO_APPROVE/merge/close)

## 1. Preflight và isolation

- Branch, HEAD Round 1 và working tree sạch trước runtime: PASS.
- Backend chỉ được khởi động với `DATABASE_URL=sqlite:///C:/Projects/firefly-cinema/backup/T11_2026-10-11/ac06_20261011_codex_01/firefly-t11-ac06.db`; biến môi trường được đặt trước khi import app.
- Đường dẫn resolved nằm trong `backup/T11_2026-10-11/`, khác tuyệt đối `backend/firefly.db`: PASS.
- Không khởi động, kết nối, seed, reset hoặc restore database thật.
- SHA-256 `backend/firefly.db` trước và sau runtime đều là `B3F7DF79BDA4478412200EA80B8EC15E6B73DA730068A52E11C40136EAC4CFE3`.

## 2. Model thật và health

- `ACTIVE_MODEL=phobert_b`, `MODEL_VERSION_B=phobert-B-2026-10-09`, `NEGATIVE_LABEL_ID=1`, `USE_WORD_SEGMENT=false`, `USE_TEXT_NORM=true`.
- `model.safetensors`: `0B80947CA8FECFFBFAA39373E92D1ED44D638DCB4981FF00DA2DD08921D22F4F` trước/sau — khớp baseline T10.
- `config.json`: `3AF764B446752118AA33982D7983F52919318373FF3108ADD0128834F28005DA` trước/sau — khớp baseline T10.
- `/api/health`: HTTP 200, `status=ok`, `classifier=phobert_b`, `active_model=phobert_b`, `active_version=phobert-B-2026-10-09`, `classifier_error=null`.
- Registry xác nhận B `loaded=true/available=true/active=true`; A khả dụng nhưng chưa nạp; không có fallback ngoài dự kiến.

## 3. Checkpoint và restore probe

Backend được dừng sau lần seed đầu trước khi checkpoint:

- DB tạm ban đầu: users 3, movies 21, showtimes 99, bookings 140, booking_seats 280, comments 12.
- `checkpoint-pre-browser.db` được tạo bằng SQLite Online Backup API.
- Restore sang file mới `restore-probe.db`, không ghi đè source.
- Source/checkpoint/restore: schema, row counts và fingerprints khớp; `PRAGMA integrity_check=ok`; `PRAGMA foreign_key_check` rỗng.
- Checkpoint và restore probe cùng SHA-256 `50CDD3D2035345CAB6D248819ABF92E1D4504DA6863604D5A92A84CBA70CBC7B`; hash checkpoint không đổi sau browser run.
- Hậu runtime DB tạm: `integrity_check=ok`, 0 vi phạm FK; users 4, movies 21, showtimes 99, bookings 142, booking_seats 284, comments 13.

Hai booking browser tồn tại vì probe đầu đã đặt A1/A2 thành công nhưng harness chờ sai câu thông báo; lần xác minh lại dùng cặp ghế kế tiếp. Đây chỉ là dữ liệu trong SQLite tạm. Cả hai lần đều chứng minh vé được tạo và ghế đã khóa; không có dữ liệu thật bị tác động.

## 4. Checklist hồi quy mục 7 — 7/7 PASS

| # | Kết quả | Evidence |
|---|---|---|
| 1 | PASS | Trang chủ tải danh sách phim; poster intro chạy khi bấm cả `Xem chi tiết` và `Đặt vé`. Ảnh `01_poster_intro_detail.png`, `01_poster_intro_booking.png`. |
| 2 | PASS | Menu Thể loại/Chủ đề mở được; tìm `meo muop` trả đúng `Mèo Mướp Đi Lạc`. Ảnh `02_search_meo_muop.png`. |
| 3 | PASS | Đăng ký `t11.browser.20261011@example.com`; khi chưa đăng nhập mở giờ chiếu bị đưa tới login; đăng nhập xong quay lại đúng `/dat-ve/21`. Ảnh `03_login_return_booking.png`. |
| 4 | PASS | Đặt hai ghế ở suất tương lai 21; `Vé của tôi` có mã vé mới; mở lại suất thấy hai ghế disabled + `seat--taken`. Ảnh `04_ticket_success.png`; DB tạm có booking/booking_seats tương ứng. |
| 5 | PASS | Bình luận `Ko hay như quảng cáo, hơi thất vọng` bị ẩn mặc định; DB lưu `is_negative=1`, score `0.9992`, model `phobert_b`, version `phobert-B-2026-10-09`; admin hiển thị `1.00`. Ảnh `05_negative_comment_hidden.png`, `05_admin_model_score.png`. |
| 6 | PASS | Health dùng model thật: `classifier=phobert_b`, version B, không lỗi/fallback. |
| 7 | PASS | Frontend `VITE_USE_MOCK=true` tải phim, login demo, mở chi tiết/bình luận, có 2 suất và chọn ghế được; Performance Resource Timing ghi 0 request tới `127.0.0.1:8011`. Ảnh `07_mock_mode.png`. |

Evidence ảnh và runtime artifact nằm tại `backup/T11_2026-10-11/ac06_20261011_codex_01/` và không được commit.

## 5. Acceptance Criteria

| AC | Kết quả | Evidence |
|---|---|---|
| AC-01 | PASS | Virtualenv sạch riêng chỉ cài `requirements-dev.txt`: `find_spec('torch')=None`, `find_spec('transformers')=None`, cả hai model path giả không tồn tại; full suite `22 passed, 1 warning`. |
| AC-02 | PASS | Test duyệt `app.routes`; đủ 13 route-method `/api/admin/*`, mỗi route có 401 khi thiếu token và 403 với user thường. |
| AC-03 | PASS | Đặt trùng ghế trả 409; DB chỉ có một `booking_seats` cho ghế đã đặt. |
| AC-04 | PASS | Chín lỗi F-01…F-09 đều có test/probe tái hiện và dòng `[Unreleased]` trong `CHANGELOG.md`. |
| AC-05 | PASS | `HUONG_DAN.md` có mục `Chạy kiểm thử`. |
| AC-06 | PASS | Web thật với PhoBERT B và SQLite tạm; checklist mục 7 đạt 7/7. |

## 6. Regression F-01…F-09

| ID | Kết quả |
|---|---|
| F-01 phim `ended` vẫn đặt được vé | PASS; backend và mock chặn. Browser còn xác nhận suất đã bắt đầu bị chặn với thông báo phù hợp. |
| F-02 lịch seed xuất hiện lại | PASS; 3/3 focused test: suất admin xóa không trở lại, ngày mới được bổ sung theo rolling 5 ngày, suất admin/vé giữ nguyên. |
| F-03 lỗi validation 422 | PASS; lỗi sai kiểu/thiếu trường trả câu tiếng Việt. |
| F-04 CSV formula injection | PASS; export neutralize công thức, nội dung gốc trong DB không đổi. |
| F-05 admin predict | PASS; lỗi từng model được cô lập, model khỏe vẫn trả 200. |
| F-06 health rò thông tin | PASS; không trả lỗi thô/đường dẫn nội bộ. |
| F-07 JWT `sub` sai | PASS; trả 401 thay vì 500. |
| F-08 bình luận trắng | PASS; trả 422 tiếng Việt. |
| F-09 mock khóa suất seed | PASS; ghế trang trí không còn bị tính là vé thật khi admin sửa/xóa suất. |

## 7. Test và gate cuối

| Gate | Kết quả |
|---|---|
| Focused F-02 | PASS — `3 passed, 1 warning` |
| Backend compileall | PASS |
| Full pytest trong venv dự án | PASS — `22 passed, 1 warning` |
| Full pytest không torch/transformers/model | PASS — `22 passed, 1 warning` |
| Health model thật + DB tạm | PASS |
| Frontend build real | PASS — 70 modules |
| Frontend build mock | PASS — 70 modules |
| Browser checklist | PASS — 7/7 |
| SQLite checkpoint/restore/integrity/FK | PASS |
| `git diff --check` | PASS |
| Protected-file scan | PASS — không `.env`, DB, model, joblib hoặc CSV dữ liệu trong diff |
| Secret scan | PASS — không private key, AWS/GitHub/Google credential pattern mới |
| Hash DB thật/model artifact | PASS — không đổi |

Cảnh báo duy nhất là deprecation từ `starlette.testclient` về alias AnyIO; không làm yếu test và không ảnh hưởng kết quả.

## 8. Scope và file thay đổi

`docs/tasks/T11.md` không có diff so với `master`. Không sửa `docs/AGENT_RULES.md`, schema/model artifact, `normalize()` hoặc database thật.

Các file trong diff T11:

- `CHANGELOG.md`, `HUONG_DAN.md`.
- `backend/app/main.py`, `backend/app/routers/admin_predict.py`, `backend/app/routers/bookings.py`, `backend/app/routers/comments.py`, `backend/app/schemas.py`, `backend/app/security.py`, `backend/app/seed.py`.
- `backend/pytest.ini`, `backend/requirements-dev.txt`, `backend/tests/**`.
- `frontend/src/api/mock.js`.
- `docs/TASK_COORDINATION_ACTIVE.md`.
- `reports/2026-10-11/codex_implementation_T11_2026-10-11.md`, `codex_fix_T11_round1_2026-10-11.md`, và báo cáo này.

## 9. Blocker và TODO

- Blocker kỹ thuật: 0.
- Required Fix mở: 0.
- TODO không chặn: cảnh báo deprecation của Starlette/TestClient nêu trên.
- T11 chỉ được bàn giao `CLAUDE_REVIEW`; chưa tự review, chưa PO_APPROVE, chưa merge/close và không mở T12.
