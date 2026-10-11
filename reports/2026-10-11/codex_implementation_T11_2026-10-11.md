# Codex Implementation Report — T11

- Ngày: 11/10/2026
- Branch: `task/T11-kiem-thu`
- Baseline trước triển khai: `712ed73c77e8c44f94de9cfab2fbdc7a6e754c72` (trùng `master` lúc pre-flight)
- Release dependency T10: `857a8272a9c307734e713a2b5cdae12f8f60bb95` — ancestor PASS
- Trạng thái kết thúc lượt triển khai: `IN_PROGRESS / BLOCKED_PENDING_PO_RUNTIME_GATE`
- Đổi schema: **Không**
- Database thật: **Không khởi động, không ghi**; SHA-256 vẫn là `B3F7DF79BDA4478412200EA80B8EC15E6B73DA730068A52E11C40136EAC4CFE3`

## 1. Pre-flight

PASS toàn bộ:

- Đúng branch `task/T11-kiem-thu`, working tree sạch trước lần sửa đầu tiên.
- `master`, HEAD và merge-base ban đầu cùng ở `712ed73c`; commit release T10 `857a8272` là ancestor.
- T04–T10 đều `DONE / CLOSED`; không có task khác `IN_PROGRESS`.
- PO authorize T11 ngày 11/10/2026 và cho phép duy nhất `pytest`, `httpx` trong `backend/requirements-dev.txt`.
- Coordination được đồng bộ `PLANNED → READY_FOR_HANDOFF → IN_PROGRESS`; closure T10 không bị làm lùi.

## 2. Thiết kế kiểm thử

- `pytest` + FastAPI `TestClient`.
- Mỗi test dùng một SQLite file riêng dưới `tmp_path`; override `get_db`, không dùng `backend/firefly.db`.
- Biến môi trường model được đặt sang đường dẫn không tồn tại trước khi import app.
- Classifier giả cố định điểm/nhãn cho comment và admin predict; không cần torch, transformers hoặc checkpoint.
- Test AC-02 duyệt động `app.routes`, thu được 13 cặp method/path `/api/admin/*`, rồi kiểm cả 401 và 403 cho từng cặp.

## 3. Kết quả lỗi tái hiện và sửa

| ID | Lỗi / nguyên nhân gốc | Evidence trước sửa | Sửa hẹp | Evidence sau sửa |
|---|---|---|---|---|
| F-01 | Booking không kiểm tra `Movie.status`, nên suất tương lai của phim `ended` vẫn đặt được | pytest trả 201 thay vì 400; mock probe cũng chấp nhận | Chặn ở backend và mock | pytest + mock probe PASS, status 400 |
| F-02 | `seed()` luôn gọi `_ensure_showtimes()` trên DB đã tồn tại, làm suất admin xóa xuất hiện lại | count từ 3 sau xóa lên 16 sau `seed()` | Chỉ tạo dữ liệu/lịch seed khi DB chưa có phim | test seed PASS |
| F-03 | Handler 422 trả trực tiếp message tiếng Anh của Pydantic | `valid integer`, `input should be` xuất hiện | Map lỗi chuẩn sang một câu tiếng Việt; giữ custom error tiếng Việt | test movie/comment validation PASS |
| F-04 | CSV backend và mock ghi trực tiếp ô bắt đầu bằng `= + - @` | ô `=2+2` giữ dạng công thức | Prefix dấu nháy đơn chỉ trong bản export; dữ liệu lưu giữ nguyên | pytest + mock probe PASS |
| F-05 | Admin predict chỉ bắt `RuntimeError` | model ném `ValueError` làm request văng lỗi | Cô lập mọi exception theo từng model | model hỏng bị bỏ qua, model khỏe vẫn 200 |
| F-06 | Health công khai nguyên văn exception/đường dẫn | response có `WinError` và `C:\Users\...` | Chỉ trả trạng thái lỗi tổng quát | test health PASS |
| F-07 | JWT `sub` sai kiểu được ép `int` ngoài khối xử lý | request gây 500 `ValueError` | Bắt `KeyError/TypeError/ValueError`, trả 401 | test JWT PASS |
| F-08 | Comment chỉ có khoảng trắng qua `min_length` rồi bị strip thành rỗng | API trả 201 | Validator strip + chặn dưới 2 ký tự | test 422 PASS |
| F-09 | Mock dùng ghế trang trí `seedBooked()` như vé thật khi khóa CRUD suất | mock update suất seed trả 409 với 8 “vé” | `ensureMutableShowtime` chỉ đếm booking thật | mock probe update suất seed PASS |

Mọi mục F-01…F-09 đã được ghi trong `CHANGELOG.md` mục `[Unreleased]`. Không sửa `normalize()`.

## 4. Acceptance Criteria

| AC | Trạng thái DEV | Evidence |
|---|---|---|
| AC-01 | **PASS** | Virtualenv mới, không kế thừa site-packages: `TORCH=ABSENT`, `TRANSFORMERS=ABSENT`, `MODELS_DIR=ABSENT`; cài chỉ requirements + `pytest/httpx`; `20 passed` |
| AC-02 | **PASS** | Duyệt `app.routes`: 13/13 cặp method/path admin; mỗi endpoint có assertion 401 và 403 |
| AC-03 | **PASS** | Đặt trùng ghế trả 409; query DB xác nhận đúng 1 dòng `booking_seats` cho ghế đó |
| AC-04 | **PASS** | 9 lỗi có test/probe tái hiện và dòng tương ứng trong `[Unreleased]` |
| AC-05 | **PASS** | `HUONG_DAN.md` có mục `Chạy kiểm thử` và lệnh PowerShell |
| AC-06 | **PENDING — PO RUNTIME GATE** | Chưa được phép checkpoint/backup + khởi động web trên database thật với model thật; không tự nhận PASS |

## 5. Coverage chức năng

- Authentication/JWT: register, login, me, token sai chữ ký, hết hạn, `sub` sai kiểu.
- Booking/seat: thành công, duplicate 409 + uniqueness DB, tối đa 8, ghế sai, toàn bộ A–H × 1–12, VIP F–H +20.000, phim ended.
- T04: validation, CRUD phim, chặn xóa phim có vé.
- T05: conflict cùng phòng có cleanup, khác ngày không conflict, chặn sửa/xóa suất có vé, seed deletion persistence, mock seed CRUD.
- T06: score/nhãn model được bảo toàn khi duyệt, filter/stats/hide, CSV UTF-8 và formula mitigation.
- T07: thiếu model fallback keyword không import torch; admin predict cô lập model lỗi; health không rò thông tin.
- T10 regression: lưu `model_name`/`model_version`, health active model/version, classifier fake/missing-model behavior.
- Admin security: 13/13 route-method có 401 + 403.

## 6. Gate results

| Gate | Kết quả |
|---|---|
| Focused pytest sau fix | PASS — 15 test ban đầu, sau mở rộng full suite thành 20 test |
| `python -m compileall -q app` | PASS |
| `python -m pytest -q` | PASS — `20 passed, 1 warning` trong 8,18 giây |
| Pytest môi trường không torch/model | PASS — `20 passed, 1 warning`; torch/transformers/model dir đều ABSENT |
| Backend health trên DB tạm | PASS — HTTP 200, `status=ok`, fallback `keyword`, lỗi được làm sạch; SQLite `integrity=ok`, 21 phim |
| Frontend build real mode | PASS — 70 modules |
| Frontend build mock mode | PASS — 70 modules |
| Mock API regression phù hợp | PASS — seed-showtime update, ended booking 400, CSV formula safe |
| `git diff --check` | PASS (chỉ có cảnh báo line-ending hiện hữu khi Git chạm file) |
| Protected-file scan | PASS — không `.env`, DB, model, joblib, CSV dữ liệu |
| Secret scan | PASS sau review false-positive các tham chiếu hằng `SECRET_KEY`; không có credential mới |
| `normalize()` | UNCHANGED |
| Schema/model/real data | UNCHANGED |

Warning duy nhất của pytest là deprecation trong Starlette `TestClient` về alias AnyIO; không ảnh hưởng kết quả và không được phép thêm/nâng thư viện ngoài scope T11.

## 7. Checklist hồi quy BOI_CANH mục 7

| # | Trạng thái | Ghi chú |
|---|---|---|
| 1–6 | **PENDING** | Các bước browser end-to-end với backend/model thật thuộc AC-06; runtime gate chưa được PO cấp |
| 7 | **DEV PASS một phần phù hợp** | Mock build PASS; mock API probe cho CRUD suất seed, booking ended và CSV PASS. Chưa tự nhận browser checklist hoàn chỉnh |

## 8. Scope và file thay đổi

- Test/config dev: `backend/tests/**`, `backend/pytest.ini`, `backend/requirements-dev.txt`.
- Fix backend: `backend/app/main.py`, `security.py`, `schemas.py`, `seed.py`, `routers/bookings.py`, `comments.py`, `admin_predict.py`.
- Fix mock: `frontend/src/api/mock.js`.
- Tài liệu/evidence: `CHANGELOG.md`, `HUONG_DAN.md`, `docs/tasks/T11.md`, `docs/TASK_COORDINATION_ACTIVE.md`, report này.
- Không sửa `docs/AGENT_RULES.md`, schema/model/data thật hoặc `normalize()`.

## 9. Blocker và bàn giao

Blocker duy nhất: **AC-06 cần quyết định PO riêng** cho checkpoint/backup và runtime backend/web với database thật + model thật. T11 giữ `IN_PROGRESS / BLOCKED_PENDING_PO_RUNTIME_GATE`; không chuyển `CLAUDE_REVIEW`, không tự PASS/PO_APPROVE/merge/close và không mở T12.
