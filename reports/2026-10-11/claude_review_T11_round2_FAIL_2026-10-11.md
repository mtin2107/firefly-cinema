# Claude Independent Review — T11 Round 2: FAIL

- Ngày: 11/10/2026
- Reviewer: Claude (Independent Reviewer / Tester)
- Branch: `task/T11-kiem-thu`
- HEAD được review: `70e2c93544ab73dec9ae4cfe91777546a899e6af` (`[T11] ban giao fix round 2`)
- Fix commit: `b06b74eec4d18c5e8cd3e3117d352f10dd97b989`
- Review trước: `reports/2026-10-11/claude_review_T11_FAIL_2026-10-11.md` (HEAD `deafc6e`)
- Kết luận: **FAIL**
  - RF-01, RF-02: **CLOSED**
  - RF-03 mới (**High**): reset database theo quy trình chính thức thì DB mới có 0 suất chiếu
- Trạng thái chuyển: `CLAUDE_REVIEW → FIX_LOOP`

## 1. Tóm tắt

Round 2 sửa đúng hai RF của Round 1 bằng sidecar `<db>.showtime-seed.json`. Sidecar ghi theo từng ngày những phim đã được xử lý, và ghi file nguyên tử. Ba test mới fail trên `seed.py` của Round 1 và pass trên HEAD.

Tuy nhiên sidecar không gắn với **danh tính** database, chỉ gắn với **đường dẫn**. Tài liệu dự án quy định reset bằng cách xóa `backend/firefly.db` rồi khởi động lại:
- `HUONG_DAN.md` dòng 232 (A2), dòng 346 và 347;
- `docs/ARCHITECTURE.md` dòng 174 (Q2);
- `BOI_CANH_DU_AN.md` mục 6.5.

Làm đúng quy trình đó thì sidecar cũ vẫn nằm lại. DB mới đọc sidecar cũ, coi cả cửa sổ là "đã seed", và **không tạo suất nào**. Hệ quả là `_seed_bookings` cũng không có suất để tạo vé mẫu.

## 2. Git và phạm vi

| Kiểm tra | Kết quả |
|---|---|
| Branch / tree | `task/T11-kiem-thu`, sạch; HEAD `70e2c93` |
| Diff Round 2 (`77b123d..HEAD`) | `backend/app/seed.py`, `backend/tests/test_seed.py`, `CHANGELOG.md`, coordination, report Codex. Tất cả trong allowlist |
| Toàn task (`master...HEAD`) | Không có `.env`, `*.db`, `*.showtime-seed.json`, model, CSV, `backup/`, `data/` |
| `docs/tasks/T11.md`, `AGENT_RULES.md`, `classifier.py` (`normalize()`), `models.py`, `database.py`, `.gitignore` | Không đổi |
| Schema | Không đổi |
| `git diff --check` | PASS |
| skip / xfail | Không có |

## 3. Required Fixes

### RF-01 — Xóa nguyên ngày bị tạo lại: **CLOSED**

| Kiểm tra | Kết quả độc lập |
|---|---|
| Xóa một suất rồi restart | Không tạo lại (`test_deleted_seed_showtime_is_not_recreated_on_restart`) |
| Xóa toàn bộ suất một ngày rồi restart với **SQLAlchemy Session mới** | 0 suất (`test_deleting_all_showtimes_of_a_day_is_not_reverted`, dùng `Session(bind=...)` mới) |
| Test bắt lỗi thật | Fail trên `seed.py` Round 1, pass trên HEAD |
| Thiếu sidecar trên DB đang có dữ liệu (probe P3) | Khởi tạo bảo thủ. Suất đã xóa lẻ và ngày đã xóa sạch đều không quay lại, số suất và booking giữ nguyên |
| Sidecar hỏng: JSON lỗi / `version: 99` / movie id không phải int (probe P2 ×3) | `RuntimeError`, không ghi thêm suất nào, sidecar giữ nguyên byte |
| Ghi nguyên tử, không để lại file tạm (probe P4) | Sau 2 lần `seed()` chỉ còn `f.db` và `f.db.showtime-seed.json` |
| Đường dẫn sidecar với URL tương đối `sqlite:///./rel.db` (probe P5) | Nằm cạnh đúng file SQLite mà engine dùng |
| Không xóa hay sửa suất admin, booking | PASS (`test_seed_does_not_change_admin_showtime_or_bookings`, P3) |

### RF-02 — Ngày có sẵn suất admin bị bỏ qua: **CLOSED**

| Kiểm tra | Kết quả độc lập |
|---|---|
| Ngày mới vào cửa sổ đã có suất admin | Phim A và B đều có suất (`test_new_rolling_day_keeps_admin_showtime_and_seeds_other_movies`) |
| Không chồng giờ cùng phòng, tính `CLEANUP_MINUTES` | Test so từng cặp suất cùng phòng dùng `duration_min + CLEANUP_MINUTES` |
| Suất admin không bị sửa | Snapshot id, movie, start, room, price khớp |
| Phim chuyển sang `now_showing` vẫn được cấp lịch | Có lịch đủ 5 ngày (`test_new_now_showing_movie_gets_schedule_on_already_seeded_days`). Hành vi trước T11 được giữ nên không cần PO quyết định |
| Test bắt lỗi thật | 3 test mới fail trên Round 1 |

### RF-03 (mới) — Reset database theo quy trình thì DB mới không có suất chiếu

- **Severity:** High. Đây là lỗi toàn vẹn dữ liệu, chạm vào quy trình vận hành chính thức và ảnh hưởng demo T12.
- **File:** `backend/app/seed.py` (`_read_seed_state`, `seed`), `HUONG_DAN.md`
- **Problem:** Sidecar chỉ được nhận diện qua đường dẫn `<db>.showtime-seed.json`. Khi PO xóa `firefly.db` (A2, mục xử lý lỗi dòng 346/347, Q2), sidecar cũ vẫn còn. Ở lần khởi động đầu, `seed()` tạo phim, user và bình luận mới, rồi `_ensure_showtimes` đọc sidecar cũ. Mọi ngày trong cửa sổ đều đã có trong `handled`, nên DB mới có 0 suất và 0 vé mẫu. Trường hợp restore một bản backup DB cũ hơn mà sidecar mới hơn cũng hỏng tương tự (thiếu suất), nhưng report Codex đã ghi là "phải backup theo cặp".
- **Evidence:** probe P1, chạy trong worktree tạm và đã xóa:
  ```python
  def test_reset_db_with_stale_sidecar(tmp_path, monkeypatch):
      freeze_today(monkeypatch, date(2026, 10, 11))
      dbf = tmp_path / "firefly.db"
      eng = fresh_engine(dbf)                    # create_all
      with Session(eng) as s: seed(s); first = window_count(s)
      eng.dispose()
      dbf.unlink()                               # reset theo HUONG_DAN, sidecar còn lại
      eng = fresh_engine(dbf)
      with Session(eng) as s: seed(s); second = window_count(s)
      assert second == first
  # Kết quả HEAD: AssertionError: DB mới sau reset chỉ có 0/99 suất trong cửa sổ
  ```
- **Expected Fix:** không đổi schema và không đổi `normalize()`.
  1. Database mới (bảng `movies` rỗng khi `seed()` bắt đầu) phải bỏ qua và ghi đè mọi sidecar cũ, coi state là rỗng. Cách khác: gắn sidecar với danh tính DB bằng dấu vết đọc được từ chính dữ liệu và kiểm khi đọc. Nếu lệch thì không được dùng state cũ để chặn seed.
  2. Thêm test tái hiện như trên vào `backend/tests/test_seed.py`: reset có sidecar cũ thì DB mới đủ suất trong cửa sổ, và `_seed_bookings` có vé mẫu.
  3. Cập nhật `HUONG_DAN.md`:
     - các hướng dẫn "xóa `firefly.db`" (A2, dòng 346/347) ghi thêm việc xử lý `firefly.db.showtime-seed.json`;
     - backup/restore phải sao chép cặp DB + sidecar khi backend đã dừng.
  4. Sửa dòng F-02 trong `CHANGELOG.md` cho khớp.

## 4. Acceptance Criteria

| AC | Kết quả |
|---|---|
| AC-01 pytest 100 % không model/torch | **PASS**. Worktree tạm tại HEAD, venv mới chỉ cài `requirements-dev.txt`: `torch None`, `transformers None`, `models False`, kết quả `25 passed`. Venv dự án: `25 passed`. |
| AC-02 401 + 403 mọi `/api/admin/*` | **PASS**. Không đổi so với Round 1 (13 route-method, duyệt `app.routes`). |
| AC-03 trùng ghế 409 + 1 bản ghi | **PASS**. Không đổi. |
| AC-04 CHANGELOG + test cho mỗi lỗi | **FAIL (theo RF-03)**. F-02 có 6 test, nhưng bản sửa tạo lỗi mới khi reset DB và dòng CHANGELOG chưa nêu giới hạn đó. Các mục F-01, F-03…F-09 giữ kết quả Round 1. |
| AC-05 HUONG_DAN "Chạy kiểm thử" | **PASS** |
| AC-06 checklist hồi quy với model thật | **PENDING**. Chưa có xác nhận riêng của PO cho runtime Round 2, nên Claude không khởi động backend và không chạy lại browser regression. Evidence `ac06_20261011_codex_01` thuộc code trước Round 2, tức là trước khi có sidecar, nên không chứng minh code hiện tại. |

## 5. Definition of Done

| Mục | Kết quả |
|---|---|
| Code trong allowlist, commit `[T11] ...` | MET |
| Gate compile / pytest / build real-mock | MET |
| Không đổi schema / normalize / model / DB thật | MET |
| Mỗi lỗi sửa đúng, có test, không gây hồi quy | **NOT MET** (RF-03) |
| AC-06 trên code cuối | NOT MET, còn PENDING |

## 6. Kiến trúc sidecar và an toàn dữ liệu

| Hạng mục | Đánh giá |
|---|---|
| Gắn đúng SQLite database | Đúng theo **đường dẫn** (`bind.url.database` resolve theo cwd, giống SQLite). **Không** gắn theo danh tính DB, đây là nguồn gốc RF-03 |
| Ghi an toàn | `mkstemp` cùng thư mục, `fsync`, `os.replace`; file tạm được dọn trong `finally`. DB commit trước, sidecar ghi sau. Nếu tiến trình chết giữa hai bước, guard trùng suất và trùng phòng xử lý được ở lần chạy sau |
| Phục hồi sau lỗi | Sidecar hỏng hoặc sai version thì dừng khởi động bằng `RuntimeError` có câu tiếng Việt, không âm thầm tái tạo dữ liệu. Thông báo chưa nói cách khắc phục; nên bổ sung vào HUONG_DAN cùng RF-03 |
| Khởi tạo trên DB đang có dữ liệu | Bảo thủ: các ngày tới mốc lịch xa nhất trong cửa sổ được coi là đã seed (P3 PASS). Lần đầu chạy trên `firefly.db` thật sau merge cũng đi nhánh này |
| Backup/restore cặp DB + sidecar | Mới có trong report Codex, **chưa có trong `HUONG_DAN.md`** (gộp vào RF-03) |
| Thiếu sidecar | Không sinh dữ liệu sai trên DB đang có dữ liệu. Sidecar **thừa** (DB mới) mới sinh sai, xem RF-03 |
| `.gitignore` | `git check-ignore backend/firefly.db.showtime-seed.json` → **NOT_IGNORED**. Sau lần chạy thật đầu tiên, file này sẽ hiện là untracked và có thể bị commit nhầm. `.gitignore` nằm ngoài allowlist T11 nên cần PO quyết định (TODO-R2-01) |
| Database thật | Không có sidecar cạnh `backend/firefly.db`. SHA-256 `B3F7DF79…` không đổi; model B `0B80947C…` không đổi |
| Bộ test | Fixture `db` dùng file trong `tmp_path`, nên sidecar cũng nằm trong thư mục tạm. `TestClient(app)` không dùng context manager nên không chạy lifespan, tức là không seed DB thật |

## 7. Gate độc lập (sau khi xóa mọi probe)

| Gate | Kết quả |
|---|---|
| Focused `tests/test_seed.py` | `6 passed` (venv sạch); trên `seed.py` Round 1: `3 failed, 3 passed` |
| Full pytest venv dự án | `25 passed, 1 warning` |
| Full pytest không torch/transformers/model | `25 passed, 1 warning` |
| Probe sidecar P1–P5 (7 ca) | 6 PASS, **1 FAIL (P1 → RF-03)**. Đã xóa |
| `compileall backend\app` | PASS |
| `npm run build` real / mock | PASS, 70 / 70 modules |
| Scope / protected / secret / `diff --check` | PASS |
| Probe, worktree, venv tạm | Đã xóa; `git worktree list` chỉ còn repo chính, tree sạch |

## 8. TODO

| ID | Nội dung | Đề xuất |
|---|---|---|
| TODO-R2-01 (mới) | `*.showtime-seed.json` chưa nằm trong `.gitignore`. File ngoài allowlist T11 | PO cho phép thêm một dòng `.gitignore` trong Fix Round 3 hoặc tự thêm trước khi chạy backend thật |
| TODO-R2-02 (mới) | Test `test_new_now_showing_movie_gets_schedule_on_already_seeded_days` dùng `status="upcoming"`, taxonomy thật là `coming_soon`. Không ảnh hưởng kết quả vì seed chỉ lọc `now_showing` | Đổi sang `coming_soon` khi tiện |
| TODO-R2-03 (mới) | `state["days"]` không bao giờ xóa ngày cũ, file tăng khoảng một mục mỗi ngày | ACCEPT_LATER, không đáng kể ở quy mô khóa luận |
| TODO-01 (R1) | F-09 và phần mock của F-01/F-04 chỉ có probe | Giữ nguyên |
| TODO-02 (R1) | Evidence AC-06 thiếu log uvicorn và JSON health | Áp dụng khi chạy lại AC-06 |
| TODO-03 (R1) | DeprecationWarning của Starlette TestClient | WONT_FIX trong T11 |
| TODO-04 (R1) | `backup/T11_2026-10-11/ac06_*` chứa venv và chrome-profile nặng | PO dọn khi đóng T11 |

## 9. Kết luận

**FAIL.** RF-01 và RF-02 đã **CLOSED**. **RF-03 (High) OPEN**: sidecar cũ chặn seed của database mới sau khi reset theo quy trình chính thức.

- T11 `CLAUDE_REVIEW → FIX_LOOP`.
- Codex Fix Round 3 chỉ sửa RF-03 trong `backend/app/seed.py`, `backend/tests/test_seed.py`, `HUONG_DAN.md`, `CHANGELOG.md`. `.gitignore` chỉ sửa khi PO cho phép.
- AC-06 còn **PENDING**. Sau khi RF-03 đóng, cần PO xác nhận runtime authorization để Claude chạy lại browser regression với PhoBERT B thật trên SQLite tạm, dùng code cuối có sidecar.
- Không mở T12, không PO_APPROVE, merge hay đóng T11.
