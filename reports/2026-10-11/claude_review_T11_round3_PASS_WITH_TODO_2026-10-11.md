# Claude Independent Review — T11 Round 3: PASS_WITH_TODO

- Ngày: 11/10/2026
- Reviewer: Claude (Independent Reviewer / Tester)
- Branch: `task/T11-kiem-thu`
- HEAD được review: `62bbf1d` (`[T11] ban giao fix round 3 cho Claude review`). Fix commit `062b9a8eedbc2b3268bf4e66e17992a308629d3f` nằm trong HEAD.
- Review trước: `reports/2026-10-11/claude_review_T11_round2_FAIL_2026-10-11.md`
- Kết luận: **PASS_WITH_TODO**. RF-03 **CLOSED**, RF-01/RF-02 không hồi quy, AC 6/6 PASS. AC-06 được Claude chạy lại độc lập trên code cuối theo Runtime Authorization PO cấp trong chat ngày 11/10/2026 cho Round 3.
- Trạng thái chuyển: `CLAUDE_REVIEW → PO_REVIEW`

## 1. Git preflight

| Kiểm tra | Kết quả |
|---|---|
| Branch / tree | `task/T11-kiem-thu`, sạch |
| `062b9a8` là ancestor của HEAD | PASS |
| Diff Round 3 (`35bf82b..HEAD`) | `backend/app/seed.py`, `backend/tests/test_seed.py`, `HUONG_DAN.md`, `CHANGELOG.md`, coordination, report Codex. Tất cả trong allowlist |
| Toàn task (`master...HEAD`) | 27 file, tất cả trong allowlist T11 |
| `.env`, `*.db`, `*.showtime-seed.json`, model, CSV, `backup/`, `data/` trong diff | Không có |
| `docs/tasks/T11.md`, `AGENT_RULES.md`, `classifier.py` (`normalize()`), `models.py`, `database.py`, `.gitignore`, `ml/` | Không đổi |
| Schema | Không đổi |
| `git diff --check` / skip / xfail / secret pattern | PASS / không có / không có / không có |

## 2. RF-03: **CLOSED / VERIFIED BY CLAUDE**

Cách sửa: `seed()` kiểm tra bảng `movies`. Nếu rỗng (DB mới), hàm ghi nguyên tử một state rỗng **trước mọi commit dữ liệu**, sau đó mới seed. Với DB đang có dữ liệu thì giữ nguyên cơ chế Round 2.

Probe độc lập `test_probe_r3.py` (6 ca) chạy trong worktree tạm ngoài repo, đã xóa:

| Kịch bản | Kết quả |
|---|---|
| 8 bước tái hiện: tạo SQLite tạm → seed → kiểm lịch, vé, ghế → giữ sidecar → dispose engine → xóa riêng file DB → tạo lại DB cùng đường dẫn → `seed()` theo vòng đời | Số dòng (movies, users, comments, showtimes, bookings, booking_seats) của DB mới **bằng đúng** lần seed đầu, tất cả > 0 |
| Restart thêm 2 lần sau reset | Số dòng không đổi, không nhân đôi |
| Sidecar hỏng + DB mới rỗng | Tự phục hồi: sidecar bị ghi đè thành state hợp lệ version 1, có đủ suất và vé mẫu |
| Sidecar hỏng + DB đang có dữ liệu | `RuntimeError`; số dòng DB và nội dung sidecar hỏng giữ nguyên |
| Tiến trình bị ngắt sau khi publish sidecar, trước commit seed (giả lập `KeyboardInterrupt` trong `hash_password`) | Sidecar đã là state rỗng, DB chưa có dòng nào; lần chạy sau seed đầy đủ, chạy tiếp lần nữa không nhân đôi |
| DB đang có dữ liệu: xóa cả một ngày, thêm suất admin ngoài cửa sổ, restart 3 lần, rồi dịch cửa sổ | Ngày đã xóa vẫn 0 suất; số dòng không đổi; ngày mới có đủ phim đang chiếu (RF-02); suất admin giữ giá 111.000 |

Test của Codex: `test_reset_database_ignores_stale_sidecar_and_reseeds_all_data` fail trên `seed.py` Round 2 (`1 failed, 8 passed`) và pass trên HEAD. Như vậy test bắt đúng lỗi.

## 3. RF-01 / RF-02: không hồi quy

- `tests/test_seed.py` 9/9 PASS (venv sạch). Các test RF-01, RF-02 và phim mới `now_showing` không đổi logic.
- Probe ở mục 2 (xóa nguyên ngày, suất admin ngoài cửa sổ, dịch cửa sổ) PASS trên code cuối.
- Runtime: restart backend trên DB tạm giữ nguyên 99 suất / 140 vé / 280 ghế.

## 4. Sidecar safety và rủi ro backup/restore

| Hạng mục | Đánh giá |
|---|---|
| Gắn đúng DB | Sidecar đặt cạnh file SQLite của engine (`<db>.showtime-seed.json`). Runtime tạo đúng `firefly-t11-r3.db.showtime-seed.json`, **không** tạo cạnh `backend/firefly.db` |
| Ghi nguyên tử | `mkstemp` cùng thư mục, `fsync`, `os.replace`; không để lại file tạm |
| DB mới / reset | State cũ hoặc hỏng không chặn seed nữa (RF-03) |
| DB đang có dữ liệu thiếu sidecar | Khởi tạo bảo thủ, không tái tạo suất đã xóa |
| DB đang có dữ liệu + sidecar hỏng | Dừng khởi động, không thay đổi gì. `HUONG_DAN.md` ghi cách xử lý: không tự xóa, khôi phục đúng cặp backup hoặc xin PO |
| Restore DB và sidecar từ **hai snapshot khác nhau** | **Không an toàn và không được coi là an toàn.** Code không phát hiện được vì không có định danh trong DB (T11 không được đổi schema). `HUONG_DAN.md` mục 2.1 điểm 5 ghi rõ đây là giới hạn đã biết: luôn restore theo cặp, HARD STOP nếu không chứng minh được cùng snapshot. Claude chấp nhận đây là giới hạn đã công bố, không phải đã được giải quyết |
| Khởi động lần đầu trên `firefly.db` thật sau merge | Đi nhánh "DB đang có dữ liệu, thiếu sidecar" (bảo thủ), nhưng vẫn cần PO authorization + backup như mọi lần khởi động DB thật |

## 5. Tài liệu

| Yêu cầu | `HUONG_DAN.md` |
|---|---|
| Xử lý sidecar khi reset | Có: DB có bảng `movies` rỗng thì state được làm mới; reset phải lưu cả cặp vào backup trước khi loại khỏi đường dẫn chạy |
| Dừng backend trước backup/restore | Có (điểm 1) |
| Backup/restore theo cặp DB + sidecar, kèm xác minh hash, integrity/FK, số dòng | Có (điểm 2) |
| Sidecar hỏng | Có (điểm 4) |
| Thao tác DB thật cần PO authorization | Có (A2 và điểm 3; bảng xử lý lỗi dòng 356/357 không còn bảo "tự xóa DB") |
| CHANGELOG F-02 khớp code cuối | Khớp: sidecar nguyên tử, xóa nguyên ngày, ngày rolling có suất admin, phim mới `now_showing`, reset `movies` rỗng; ghi "chín regression test", đúng 9 test trong `test_seed.py` |

## 6. AC-06: chạy lại độc lập trên code cuối

Authorization: PO cấp trong chat ngày 11/10/2026. Phạm vi: chỉ dùng SQLite tạm mới, có checkpoint/restore, PhoBERT B thật, browser real + mock; tuyệt đối không chạm `backend/firefly.db`.

**Cách ly:**
- Dùng wrapper riêng thay cho cấu hình `backend` sẵn có, vì cấu hình đó đọc `backend/.env`. Wrapper đặt `DATABASE_URL` trước khi import app. Process env thắng `.env` vì config dùng `setdefault`.
- Guard cứng: đường dẫn resolve phải nằm trong thư mục chạy và khác DB thật. Khi khởi động, `app.config.DATABASE_URL` in ra `.../ac06_20261011_claude_r3/firefly-t11-r3.db`.
- Backend chạy ở cổng 8012, frontend real ở 5174, mock ở 5175.

**Model:** `/api/health` trả `classifier=phobert_b`, `active_version=phobert-B-2026-10-09`, `classifier_error=null`; B `loaded=true`, không fallback, không rò đường dẫn hay `WinError`.

**Checkpoint (dừng backend trước):** DB và sidecar được checkpoint bằng SQLite Online Backup API + copy sidecar, rồi restore sang file mới.

| | Kết quả |
|---|---|
| Source / checkpoint / restore | integrity `ok`, FK rỗng; schema và số dòng giống nhau (users 3, movies 21, showtimes 99, bookings 140, seats 280, comments 12) |
| SHA checkpoint = restore | `68DD9086…835700` |
| Sidecar ba bản | Giống nhau |
| Checkpoint sau browser | Hash không đổi |

**Checklist BOI_CANH mục 7 (code cuối `62bbf1d`):**

| # | Kết quả | Bằng chứng |
|---|---|---|
| 1 | PASS | Trang chủ tải phim từ `127.0.0.1:8012`; `.intro` (PosterIntro) xuất hiện khi bấm cả "Xem chi tiết" và "Đặt vé" |
| 2 | PASS | Menu Thể loại (`/kham-pha?the-loai=…`) và Chủ đề mở được; tìm `meo muop` ra 1 phim "Mèo Mướp Đi Lạc" |
| 3 | PASS | Đăng ký `claude.r3.20261011@example.com`. Lần đầu dùng `@example.test` bị từ chối với câu 422 tiếng Việt, thêm một xác nhận cho F-03. Chưa đăng nhập bấm 19:30 thì bị đưa về `/dang-nhap`, đăng nhập xong quay lại đúng `/dat-ve/11` |
| 4 | PASS | Đặt A1, A2 → vé `FF000141`, 190.000 đ. Mở lại suất: A1, A2 `disabled` + `seat--taken`. DB: booking 141 = `A1,A2` |
| 5 | PASS | Bình luận `Ko hay như quảng cáo, hơi thất vọng` bị ẩn mặc định. DB lưu `is_negative=1`, score `0.9992`, `phobert_b`, `phobert-B-2026-10-09`. Admin hiển thị `Tiêu cực 1.00 · phobert_b · phobert-B-2026-10-09` |
| 6 | PASS | Health dùng model thật, không lỗi hay fallback (`health_final.json`) |
| 7 | PASS | Mock (backend đã tắt): đăng nhập demo, chi tiết phim có bình luận, 2 suất, chọn ghế A3 → `seat--chosen` 95.000 đ. Performance Resource Timing: **0** request tới `:8012` hoặc `:8000`, chỉ có `localhost:5175` + Google Fonts |

**Sau runtime:**
- DB tạm: integrity `ok`, FK rỗng; users 4, showtimes 99, bookings 141, seats 282, comments 13 (đúng +1 user / +1 vé / +2 ghế / +1 bình luận).
- `uvicorn.log` không có error hay traceback.
- Cổng 8012/5174/5175 đã tắt; `.claude/launch.json` khôi phục bản gốc; cửa sổ trình duyệt reset về desktop.

**Evidence:** `backup/T11_2026-10-11/ac06_20261011_claude_r3/`, ngoài Git, gồm:
- 12 ảnh;
- 3 file health JSON;
- `checkpoint_verify.txt`, `post_runtime_verify.txt`, `db_runtime_checks.txt`;
- `uvicorn.log`, `runtime_env.txt`, `run_backend_r3.ps1`, `hashes_before.txt`, `git_head.txt`, `test_account.txt` (tài khoản test chỉ thuộc DB tạm).

**Database thật và model:**

| File | Trước | Sau |
|---|---|---|
| `backend/firefly.db` | `B3F7DF79…C4CFE3` | `B3F7DF79…C4CFE3` |
| `model.safetensors` B | `0B80947C…28F4F` | `0B80947C…28F4F` |
| `config.json` B | `3AF764B4…8005DA` | `3AF764B4…8005DA` |
| `backend/firefly.db.showtime-seed.json` | không có | không có |

## 7. Acceptance Criteria

| AC | Kết quả | Bằng chứng độc lập |
|---|---|---|
| AC-01 | **PASS** | Venv mới chỉ cài `requirements-dev.txt`, worktree không có `backend/models`: `torch None`, `transformers None`, `models False` → `28 passed`. Venv dự án: `28 passed` |
| AC-02 | **PASS** | 13 route-method `/api/admin/*` đều có 401 + 403, test duyệt `app.routes` |
| AC-03 | **PASS** | Trùng ghế trả 409, DB còn 1 dòng `booking_seats` |
| AC-04 | **PASS** | F-01…F-09 có dòng CHANGELOG. F-01…F-08 có test fail trên master (Round 1); F-02 có 9 test, mỗi vòng sửa đều có test fail trên code trước đó; F-09 là probe mock (ngoài scope test frontend) |
| AC-05 | **PASS** | Mục "Chạy kiểm thử" và quy trình sidecar trong `HUONG_DAN.md` |
| AC-06 | **PASS** | Chạy lại trên code cuối với PhoBERT B thật + SQLite tạm; checklist 7/7 (mục 6) |

## 8. Definition of Done

| Mục | Kết quả |
|---|---|
| Code/test trong allowlist, commit `[T11] ...` | MET |
| compileall, pytest, build real/mock | MET |
| Mỗi lỗi có test tái hiện và dòng CHANGELOG | MET |
| Không đổi schema / `normalize()` / model / DB thật | MET (hash xác minh) |
| Hướng dẫn chạy test và vận hành sidecar | MET |
| Checklist hồi quy với model thật | MET (7/7, Claude chạy lại) |
| Required Fix mở | 0 |

## 9. Gate cuối

| Gate | Kết quả |
|---|---|
| Focused `tests/test_seed.py` | `9 passed` |
| Full pytest venv dự án | `28 passed, 1 warning` |
| Full pytest không torch/transformers/model | `28 passed, 1 warning` |
| `compileall backend\app` | PASS |
| `npm run build` real / mock | 70 / 70 modules |
| Scope / protected / secret / `diff --check` / skip-xfail | PASS |
| Probe, worktree, venv tạm | Đã xóa; `git worktree list` chỉ còn repo chính; tree sạch |

## 10. Required Fixes

| RF | Trạng thái |
|---|---|
| RF-01 (Medium) xóa nguyên ngày bị tạo lại | CLOSED (Round 2), không hồi quy |
| RF-02 (Medium) ngày có suất admin bị bỏ qua | CLOSED (Round 2), không hồi quy |
| RF-03 (High) reset DB với sidecar cũ | **CLOSED / VERIFIED BY CLAUDE** (Round 3) |
| RF mới | **0** |

## 11. TODO cho PO disposition

| ID | Nội dung | Đề xuất |
|---|---|---|
| TODO-R3-01 | `backend/firefly.db.showtime-seed.json` chưa được ignore (`git check-ignore` → không). `.gitignore` ngoài allowlist | **Nên làm trước lần khởi động backend thật đầu tiên sau merge.** PO thêm dòng `/backend/*.db.showtime-seed.json` như Codex đề xuất |
| TODO-R3-02 | Restore DB và sidecar khác snapshot không phát hiện được | ACCEPT_WITH_DISCLOSURE: đã ghi ở HUONG_DAN mục 2.1 điểm 5; giải pháp triệt để cần định danh trong DB, tức là đổi schema, nên để task sau nếu PO muốn |
| TODO-R3-03 | Khe hở có từ trước (master cũng vậy): tiến trình chết sau khi commit lịch, trước `_seed_bookings`, thì DB không bao giờ có vé mẫu (probe: 99 suất, 0 vé) | ACCEPT_LATER → T12 (dữ liệu demo); chỉ xảy ra khi crash ở lần khởi tạo đầu |
| TODO-R3-04 | Menu "Chủ đề" tràn phải viewport khoảng 95px ở 1280px (`.dd__list` right 1375 > 1280; `scrollWidth` 1386). `Dropdown` không bị T11 sửa nên lỗi có từ trước | ACCEPT_LATER → T12/T13 (UI polish) |
| TODO-R2-02 | Test `test_new_now_showing_movie_gets_schedule_on_already_seeded_days` dùng `status="upcoming"`, taxonomy thật là `coming_soon` | ACCEPT_LATER, không ảnh hưởng kết quả |
| TODO-R2-03 | `state["days"]` không xóa ngày cũ | ACCEPT_LATER |
| TODO-01 (R1) | F-09 và phần mock F-01/F-04 chỉ có probe | ACCEPT (test frontend ngoài scope) |
| TODO-02 (R1) | Evidence AC-06 thiếu log và health JSON | **RESOLVED**: Round 3 evidence có `uvicorn.log` và 3 file health JSON |
| TODO-03 (R1) | DeprecationWarning Starlette TestClient | WONT_FIX trong T11 |
| TODO-04 (R1) | `backup/T11_2026-10-11/` chứa venv, chrome-profile và DB tạm | PO dọn khi đóng T11 |

## 12. Kết luận và bàn giao

**PASS_WITH_TODO.** T11 `CLAUDE_REVIEW → PO_REVIEW`.

Task kế tiếp theo thứ tự AGENT_RULES 1.1 là T12, nhưng **không** đặt `READY_FOR_HANDOFF` vì hai lý do:
- Q4 (deploy) đang **MỞ** và ảnh hưởng T12;
- PO đã chỉ thị không mở T12 trong vòng review này.

T12 giữ `PLANNED / NOT AUTHORIZED`. Vì vậy report này không kèm prompt bàn giao.

Việc của Tín:
1. PO review, disposition các TODO, đặc biệt TODO-R3-01 (`.gitignore`).
2. Nếu APPROVED thì merge `task/T11-kiem-thu` vào `master`.
3. Chốt Q4 trước khi mở T12.

Claude không PO_APPROVE, không merge, không đóng T11.
