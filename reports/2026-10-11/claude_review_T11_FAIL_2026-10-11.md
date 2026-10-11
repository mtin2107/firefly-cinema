# Claude Independent Review — T11 Round 1: FAIL

- Ngày: 11/10/2026
- Reviewer: Claude (Independent Reviewer / Tester)
- Task: T11 — Kiểm thử tự động và sửa lỗi
- Branch: `task/T11-kiem-thu`
- HEAD được review: `deafc6edd6945d493e23ff83e7825735a8e167ff` (`[T11] hoan tat runtime AC06 va ban giao review`)
- Base: `master` = `712ed73c77e8c44f94de9cfab2fbdc7a6e754c72`; release T10 `857a8272` là ancestor: PASS
- Kết luận: **FAIL** — 2 Required Fix (Medium), cùng nằm ở F-02 (`backend/app/seed.py`)
- Trạng thái chuyển: `CLAUDE_REVIEW → FIX_LOOP`

## 1. Tóm tắt

Bộ pytest tốt: 22/22 PASS cả trong venv dự án lẫn venv sạch không torch/transformers/sklearn/model; 8/8 test hồi quy F-01…F-08 thực sự FAIL khi chạy trên code `backend/app` của master. Kiểm phân quyền admin, đặt trùng ghế, health, scope, bảo mật và bằng chứng AC-06 đều đạt.

FAIL vì F-02. Bản sửa coi "ngày đã có ít nhất một suất" là ngày admin quản lý. Probe độc lập cho thấy cách này:
- vẫn tạo lại suất đã xóa nếu admin xóa **toàn bộ** suất của một ngày (lỗi gốc F-02 còn, CHANGELOG ghi chưa đúng);
- gây **hồi quy so với master**: ngày có sẵn một suất admin tạo trước khi vào cửa sổ rolling bị bỏ qua hoàn toàn, nên các phim đang chiếu khác không có suất nào trong ngày đó.

## 2. Git và phạm vi

| Kiểm tra | Kết quả |
|---|---|
| Branch / tree | `task/T11-kiem-thu`, sạch |
| Commit | 3 commit `[T11] ...` trên master |
| Coordination đã commit, đúng trạng thái | PASS — T11 `CLAUDE_REVIEW`, T12 `PLANNED`, T10 giữ `DONE / CLOSED` |
| File trong diff (22) | Tất cả nằm trong allowlist T11 |
| `docs/tasks/T11.md`, `docs/AGENT_RULES.md`, `PROJECT_SOURCE_OF_TRUTH.md` | Không đổi |
| `normalize()` / `classifier.py`, `models.py`, `database.py` (schema), `ml/` | Không đổi |
| `.env`, `*.db`, model, joblib, CSV, `backup/`, `data/` trong diff | Không có |
| `git diff --check master...HEAD` | PASS |
| Thư viện mới | Chỉ `pytest==8.3.3`, `httpx==0.27.2` trong `requirements-dev.txt` (PO đã cho phép) |
| Đường dẫn `D:\` | Không có |

## 3. Acceptance Criteria

| AC | Kết quả | Bằng chứng độc lập |
|---|---|---|
| AC-01 pytest 100 % không model/torch | **PASS** | Worktree tạm tại HEAD (không có `backend/models/`), venv mới chỉ cài `requirements-dev.txt`: `torch None`, `transformers None`, `sklearn None`, `models_dir False` → `22 passed, 1 warning`. Venv dự án: `22 passed`. Không có `skip`/`xfail`. |
| AC-02 401 + 403 mọi `/api/admin/*` | **PASS** | Test duyệt `app.routes`, so tập đã kiểm với tập route-method mong đợi (13 cặp). Không hard-code danh sách. |
| AC-03 trùng ghế 409 + DB 1 bản ghi | **PASS** | `test_booking_duplicate_seat_and_vip_price`: lần 2 trả 409, đếm `booking_seats` của A1 = 1. |
| AC-04 CHANGELOG + test cho mỗi lỗi | **FAIL (theo RF-01)** | 9 dòng CHANGELOG có đủ. 8 test F-01…F-08 FAIL trên master, PASS trên HEAD. F-09 (mock) chỉ có probe, chấp nhận vì test frontend nằm ngoài scope. Nhưng dòng F-02 khẳng định "không tạo lại suất seed mà admin đã xóa", điều này sai với trường hợp xóa nguyên ngày (RF-01). |
| AC-05 HUONG_DAN "Chạy kiểm thử" | **PASS** | Có mục, lệnh PowerShell đúng. |
| AC-06 checklist hồi quy với model thật | **PASS theo bằng chứng, chưa chạy lại độc lập** | Xem mục 6. Vì `seed.py` phải sửa ở FIX_LOOP, Claude sẽ chạy lại browser regression độc lập ở Round 2 trên code cuối. |

## 4. Definition of Done

| Mục | Kết quả |
|---|---|
| Code trong allowlist, commit đúng quy ước | MET |
| Gate web (compile, build real/mock, pytest) | MET |
| Không đổi schema / normalize / model / DB thật | MET |
| Mỗi lỗi sửa đúng và có test | **NOT MET** — F-02 chưa đúng (RF-01, RF-02) |
| Report đầy đủ | MET |

## 5. Kiểm tra riêng F-02

Probe tạm `test_probe_f02.py` chạy trong worktree ngoài repo, đã xóa. Kết quả cùng một probe trên HEAD và trên `backend/app` của master:

| Kịch bản | HEAD | master | Đánh giá |
|---|---|---|---|
| Xóa một suất rồi restart cùng ngày | Không tạo lại (test Codex) | Tạo lại | Đã sửa |
| **Xóa toàn bộ suất của một ngày rồi restart** | **Tạo lại 4 suất** | Tạo lại | **Lỗi gốc còn → RF-01** |
| Dịch cửa sổ sang ngày kế tiếp | Ngày mới đủ phim (test Codex) | Đủ | PASS |
| Giữ nguyên suất admin + booking | Giữ nguyên (test Codex) | Giữ nguyên | PASS |
| **Admin tạo suất ngày D+5 (ngoài cửa sổ), sau đó cửa sổ dịch tới D+5** | **Phim đang chiếu khác không có suất nào ngày D+5** (`assert 2 in {1}`) | Có đủ | **Hồi quy → RF-02** |
| Phim `now_showing` mới thêm, restart | 0 suất trong các ngày đã có lịch | Có suất mỗi ngày | Đổi hành vi, xem RF-02 |

Ghi chú: sau khi bỏ qua cả ngày, khối `existing_movie_ids` / "Ưu tiên công bằng" trong `_ensure_showtimes` luôn rỗng, tức là code chết. Đây là dấu hiệu heuristic đang mâu thuẫn với luật cũ "mỗi phim đang chiếu có ít nhất một suất trong ngày" (hợp đồng T05 RF-01).

## 6. Runtime safety và AC-06

Claude không khởi động backend, không kết nối database thật. Mọi thao tác SQLite đều mở `mode=ro`.

| Kiểm tra | Kết quả |
|---|---|
| SHA-256 `backend/firefly.db` | `B3F7DF79…C4CFE3`, khớp baseline T10 |
| `model.safetensors` B / `config.json` B / `version.txt` | `0B80947C…28F4F` / `3AF764B4…8005DA` / `phobert-B-2026-10-09`, khớp |
| `checkpoint-pre-browser.db` = `restore-probe.db` | Cùng SHA-256 `50CDD3D2…70CBC7B`; integrity `ok`, FK rỗng; users 3 / movies 21 / showtimes 99 / bookings 140 / seats 280 / comments 12 |
| `firefly-t11-ac06.db` sau browser | integrity `ok`, FK rỗng; users 4 / bookings 142 / seats 284 / comments 13, khớp report |
| Dòng bình luận checklist #5 | `Ko hay như quảng cáo, hơi thất vọng`, `is_negative=1`, score `0.9992`, `phobert_b`, `phobert-B-2026-10-09` |
| Ảnh | 8 PNG có mặt; đã xem `04_ticket_success.png` (FF000141/142, ghế A1–A4) và `05_admin_model_score.png` (13 bình luận, nhãn `phobert_b · phobert-B-2026-10-09`). Nhất quán với DB. |
| Harness `cdp_runtime.py` | Chỉ trỏ `127.0.0.1:5173` và backend `127.0.0.1:8011` |

## 7. Bảo mật và hồi quy code

- F-03: handler 422 giữ thông báo custom cho prefix `movie_/showtime_/comment_/predict_`. Đã đối chiếu toàn bộ `PydanticCustomError` trong `schemas.py`: không type nào bị nuốt thành câu chung.
- F-05: `except Exception` chỉ bao quanh từng model trong `/api/admin/predict`. `finally` vẫn gọi `release_if_inactive`, nên không ảnh hưởng RLock của T10 RF-01.
- F-06: health không còn chuỗi lỗi thô; shape JSON giữ nguyên (`error` vẫn có, là câu chung hoặc `null`). Frontend không cần đổi.
- F-07: `sub` sai kiểu hoặc thiếu trả 401.
- F-08: validator strip trùng với `body.content.strip()` sẵn có trong router nên dữ liệu lưu không đổi.
- F-01: chặn `ended` ở cả backend và mock; câu tiếng Việt, mã 400 nhất quán.
- F-04: CSV neutralize ở cả backend và mock, DB giữ nguyên nội dung (test xác nhận).
- Parity real/mock: không thêm endpoint mới; hai thay đổi hành vi (F-01, F-04) có ở cả hai lớp.
- Không có credential mới trong diff (`SECRET_KEY` test là giá trị riêng trong `conftest.py`).

## 8. Gate cuối (sau khi xóa mọi probe và worktree tạm)

| Gate | Kết quả |
|---|---|
| `python -m compileall -q backend\app` | PASS |
| `python -m pytest -q` (venv dự án) | PASS — `22 passed, 1 warning` |
| pytest venv sạch không torch/model | PASS — `22 passed, 1 warning` |
| Test bắt lỗi thật (chạy trên app master) | 8 failed / 14 passed, đúng 8 test F-01…F-08 |
| `npm run build` real | PASS — 70 modules |
| `VITE_USE_MOCK=true npm run build` | PASS — 70 modules |
| Scope / bí mật / `diff --check` | PASS |
| Probe tạm | Đã xóa (worktree + venv trong scratchpad, không chạm repo) |

## 9. Required Fixes

### RF-01 — F-02 vẫn tạo lại suất khi admin xóa toàn bộ suất của một ngày

- Severity: **Medium**
- File: `backend/app/seed.py` (`_ensure_showtimes`), `CHANGELOG.md` (dòng F-02)
- Problem: Điều kiện "ngày đã có ≥ 1 suất thì bỏ qua" không phân biệt được "ngày chưa từng seed" với "ngày admin đã xóa hết suất". Ngày bị xóa sạch rỗng trở lại, nên lần restart sau seed lại toàn bộ.
- Evidence (tái hiện, cần thêm thành test):
  ```python
  def test_deleting_all_showtimes_of_a_day_is_not_reverted(db, movie, monkeypatch):
      freeze_today(monkeypatch, date(2026, 10, 11))
      _ensure_showtimes(db, days=5)
      target = date(2026, 10, 13); s = datetime.combine(target, time.min)
      db.execute(delete(Showtime).where(Showtime.start_time >= s, Showtime.start_time < s + timedelta(days=1)))
      db.commit()
      seed(db)
      # HEAD hiện tại: 4 suất bị tạo lại
      assert count_showtimes_on(db, target) == 0
  ```
- Expected Fix: Seed chỉ những ngày **chưa từng được seed**, không dựa vào việc ngày đó còn suất hay không. Không được đổi schema. Ví dụ: một mốc "đã seed tới ngày X" lưu ngoài schema (file trạng thái cạnh DB hoặc cơ chế tương đương, tự xác định lần đầu từ dữ liệu hiện có), chỉ seed các ngày > X trong cửa sổ. Nếu cách nào cũng cần đổi schema thì dừng, hỏi PO (AGENT_RULES mục 7). Thêm test trên và sửa dòng F-02 trong CHANGELOG cho đúng.

### RF-02 — Hồi quy: ngày có sẵn suất admin bị bỏ qua, phim đang chiếu khác mất lịch

- Severity: **Medium**
- File: `backend/app/seed.py`
- Problem: Admin được tạo suất ở bất kỳ ngày tương lai nào (validator chỉ yêu cầu `start_time` ở tương lai). Nếu ngày đó nằm ngoài cửa sổ 5 ngày và có suất admin trước khi cửa sổ dịch tới, seed bỏ qua cả ngày. Kết quả: các phim `now_showing` khác không có suất nào. Trên master, luật "mỗi phim đang chiếu có ≥ 1 suất mỗi ngày" vẫn được đảm bảo (hợp đồng T05 RF-01).
- Evidence (tái hiện, cần thêm thành test): hai phim `now_showing`; seed ngày 11/10; admin thêm suất phim 1 lúc 10:00 ngày 16/10; đặt `today` = 12/10, gọi `seed()`. Kết quả: movie_id trong ngày 16/10 = `{1}` (master: `{1, 2}`).
- Expected Fix: Khi một ngày lần đầu vào cửa sổ (theo mốc ở RF-01), vẫn chạy seed với logic công bằng và kiểm tra trùng phòng như cũ, kể cả khi ngày đó đã có suất admin. Không sửa hay xóa suất admin. Thêm test trên.
- Liên quan, PO cần quyết hoặc chấp nhận: phim `now_showing` mới thêm không còn được tự cấp suất ở các ngày đã seed (master có). Codex ghi rõ hành vi này trong CHANGELOG/report để PO xác nhận, hoặc giữ cấp suất cho phim mới nếu không xung đột với RF-01.

## 10. TODO (không chặn)

| ID | Nội dung | Đề xuất |
|---|---|---|
| TODO-01 | F-09 và phần mock của F-01/F-04 chỉ có probe, không có test tự động (test frontend nằm ngoài scope T11) | ACCEPT_LATER, hoặc ghi rõ trong CHANGELOG là "probe mock" (đã ghi) |
| TODO-02 | Thư mục bằng chứng AC-06 không có log backend/frontend và không có ảnh cho mục #6 (health); chỉ có kết quả trong report và `cdp_runtime.py` | Round 2 lưu `/api/health` JSON và log uvicorn vào thư mục evidence |
| TODO-03 | DeprecationWarning của Starlette `TestClient` (anyio alias) | WONT_FIX trong T11, không được nâng thư viện |
| TODO-04 | `backup/T11_2026-10-11/ac06_*/` chứa `venv-no-ml` và `chrome-profile-real` khá nặng (ngoài Git) | PO dọn khi đóng T11 nếu không cần giữ |

## 11. Bước tiếp theo

- T11: `CLAUDE_REVIEW → FIX_LOOP`. Codex chỉ sửa RF-01, RF-02 trong `backend/app/seed.py`, `backend/tests/test_seed.py`, `CHANGELOG.md`, rồi viết `codex_fix_T11_round2_2026-10-11.md`.
- Round 2: Claude chạy lại pytest, các probe F-02 và browser regression độc lập trên SQLite tạm, nếu PO xác nhận Runtime Authorization T11 áp dụng cho Round 2.
- FAIL nên không mở task kế tiếp. T12 giữ `PLANNED`.
