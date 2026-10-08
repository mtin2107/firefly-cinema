# Claude Independent Review — T05 Quản lý suất chiếu (admin)

| Trường | Giá trị |
|---|---|
| Task | T05 — Quản lý suất chiếu (admin) |
| Nhánh | `task/T05-quan-ly-suat-chieu` (HEAD `83c5a9d`) |
| Baseline | `a09fe6736d4a5d465e07dfa026b032caf9afe0be` |
| Implementation commits | `214fcaa`, `033e420` |
| Reviewer | Claude (Independent Reviewer / Tester) |
| Ngày | 08/10/2026 |
| **Kết quả** | **FAIL** — 1 Required Fix (RF-01, High), 4 TODO, 1 scope conflict cần PO quyết |
| Chuyển trạng thái | `CLAUDE_REVIEW` → `FIX_LOOP` |

Tóm tắt: CRUD admin, luật chồng giờ, khóa suất có vé, phân quyền, validation và mock contract đều đúng (AC-01 → AC-05, AC-07 đạt khi kiểm độc lập). Tuy nhiên luật chống chồng giờ áp vào bộ sinh suất seed (backend `_ensure_showtimes()` và mock `buildShowtimes()`) làm **5/9 phim đang chiếu không còn suất chiếu nào** (phim 5, 8, 9, 10, 18). Đây là hồi quy chức năng đặt vé lõi do chính T05 gây ra, nên AC-08 không đạt.

---

## 1. Source Review

Đã đọc: `PROJECT_SOURCE_OF_TRUTH.md`, `AGENT_RULES.md`, `TASK_COORDINATION_ACTIVE.md`, `docs/tasks/T05.md`, `reports/2026-10-08/codex_implementation_T05_2026-10-08.md`, phần hợp đồng liên quan trong `ARCHITECTURE.md` và `BOI_CANH_DU_AN.md` mục 7. Đọc diff thật `git diff master...HEAD` và toàn bộ file mới: `admin_showtimes.py`, `showtime_rules.py`, `AdminShowtimes.jsx`, các hunk ở `schemas.py`, `seed.py`, `main.py`, `real.js`, `mock.js`, `App.jsx`, `Header.jsx`, `global.css`. Đọc thêm (chỉ đọc) `bookings.py`, `movies.py`, `security.py`, `models.py`, `seed._seed_bookings()` để kiểm tra dependency.

Report Codex chỉ dùng làm bằng chứng phụ. Mọi kết luận dưới đây dựa trên code và probe độc lập.

## 2. Git / Baseline Verification

| Kiểm tra | Kết quả |
|---|---|
| Nhánh hiện tại | `task/T05-quan-ly-suat-chieu` ✔ |
| `git merge-base master HEAD` | `a09fe6736d4a5d465e07dfa026b032caf9afe0be` = baseline ✔ |
| Dependency T04 | `fced3d7` nằm trong lịch sử HEAD ✔ |
| Implementation commits | `214fcaa1eb…`, `033e420863…` tồn tại ✔ |
| Working tree trước review | sạch ✔ |
| `git log master..HEAD` | 5 commit, đều dạng `[T05] …` ✔ |
| `git diff --check master...HEAD` | exit 0 ✔ |
| File ngoài allowlist | 0 (14 file, tất cả thuộc mục 6 T05.md) ✔ |
| Forbidden files (`models.py`, `seats.py`, `classifier.py`) | 0 dòng diff ✔ (`bookings.py` cũng 0 dòng) |
| `seed.py` | 1 hunk `@@ -18,20 +18,31 @@`, nằm trọn trong `_ensure_showtimes()` ✔ |
| `global.css` | +21 dòng, chỉ thêm class `.admin-showtime-*`, `.showtime-form`, `.showtime-filters` và responsive liên quan; không sửa selector cũ ✔ |
| Đổi schema | Không (`models.py` không đổi) ✔ |
| Secret / DB / model / CSV trong diff | 0 ✔ |

## 3. Acceptance Criteria

| AC | Kết quả | Bằng chứng độc lập |
|---|---|---|
| AC-01 | ✔ PASS | TestClient trên SQLite tạm: GET/POST/PUT/DELETE → anon `401`, user thường `403` (4/4). Mock: user `403` 4/4, chưa đăng nhập `401`. Cả 4 route có `Depends(require_admin)`. |
| AC-02 | ✔ PASS | Phim 100 phút, suất 10:00 Phòng 1: +114 phút → `409` đúng câu `Phòng 1 đã có suất Phim Thu T05 lúc 10:00. Hãy chọn giờ khác hoặc phòng khác.`; +115 → `201`; −114 (suất mới kết thúc lấn suất cũ) → `409`; −115 → `201`; trùng giờ → `409`. Mock cho kết quả giống hệt (câu lỗi khớp từng ký tự). |
| AC-03 | ✔ PASS | Cùng 10:00, Phòng 2 → `201` (real và mock). |
| AC-04 | ✔ PASS | User đặt E5, E6 → PUT/DELETE `409` `Suất chiếu đã có 2 vé, không sửa hay xóa được.`; đặt thêm F1 → `3 vé` (đếm đúng theo `booking_seats`). Mock: `409 … 2 vé`, giữ nguyên sau F5. |
| AC-05 | ✔ PASS (luật chống chồng) | Chạy **uvicorn thật** 3 lần trên SQLite tạm: lần 1 seed; xóa suất chưa bán vé của ngày +4; admin tạo 4 suất (09:00 P1, 12:30 P2, 15:45 P3, 13:00 P4); restart → `_ensure_showtimes()` sinh lại 4 suất, **0 cặp chồng giờ** trên toàn bảng (64 dòng), 4 suất admin giữ nguyên; restart lần 3 vẫn 64 dòng, 0 chồng (idempotent). Ghi chú: chính luật này gây RF-01. |
| AC-06 | ✔ PASS | Phim mới tạo qua `/api/admin/movies` `201` → tạo suất `201` → có trong `/api/movies/{id}/showtimes` → user đặt 2 ghế `201` → ghế xám trong `/api/showtimes/{id}` → có trong `/api/bookings/me`. Mock: trang `/phim/22#lich-chieu` hiện 4 giờ chiếu của phim mới. |
| AC-07 | ✔ PASS (contract) | Mock (Vite `VITE_USE_MOCK=true`, cổng 5175): 403 ×4, chồng giờ/biên +115/khác phòng, PUT chính nó, PUT đổi phòng `409`, 422 ×6 (quá khứ, giá 9.000/75.500, phòng sai, phim không tồn tại, phim ended), giá 10.000/500.000 nhận, PUT 404, khóa suất có vé, lọc ngày + phim; **F5** giữ nguyên 4 suất và khóa vé. UI mock hiện lỗi chồng giờ đúng câu. Khác biệt nhỏ: xem TODO-01. Seed mock cũng bị RF-01. |
| AC-08 | ✘ **FAIL** | Hồi quy: 5/9 phim đang chiếu không có suất → không đặt vé được; mục "Phim hot trong tuần" mất 5 phim. Xem RF-01 và mục 7. |

## 4. Definition of Done

| Mục | Trạng thái |
|---|---|
| Code đúng allowlist, commit `[T05]` | ✔ |
| Gate web (compileall, startup, health, build, mock) | ✔ |
| Checklist hồi quy 7 mục | ✘ (mục 1, 4 bị ảnh hưởng — RF-01) |
| Report Codex đầy đủ, đúng sự thật | Một phần — report ghi AC-05/AC-08 đạt và mô tả "trang admin 12 dòng dữ liệu mẫu" mà không nhận ra 12 dòng nghĩa là chỉ còn 4 phim (TODO-04) |
| Tài liệu `ARCHITECTURE.md` | ✔ (mục 2.7 mới, đánh lại 2.8) |

**DoD: NOT MET** do RF-01.

## 5. Architecture

- Router mới đặt đúng `backend/app/routers/`, luật dùng chung ở `backend/app/showtime_rules.py` theo thiết kế T05 mục 4; `seed.py` import cục bộ trong hàm để giữ diff trong `_ensure_showtimes()` — chấp nhận được.
- Frontend chỉ gọi `api.admin.showtimes.*` qua `src/api/index.js`; `real.js` và `mock.js` cùng 4 hàm, cùng cấu trúc JSON (`ShowtimeOut`).
- Mock áp dụng cùng luật chồng giờ (`intervalsOverlap`, `CLEANUP_MINUTES = 15`) và cùng câu lỗi.
- `find_showtime_conflict()` tải toàn bộ suất của phòng (không giới hạn theo ngày) mỗi lần gọi; seed gọi khoảng 45 lần mỗi lần khởi động. Ở quy mô khóa luận không đáng kể; ghi nhận ở TODO-03.
- Không đổi schema, không thêm thư viện.

## 6. Security

- 4/4 endpoint có `require_admin`; 401/403 đã probe ở cả real và mock.
- `ShowtimeIn` có `extra="forbid"` (field lạ → 422); `movie_id < 1` → 422; giờ có múi giờ (`+07:00`) được chuyển về giờ địa phương naive, khớp cách lưu hiện có.
- Lỗi nghiệp vụ trả `HTTPException` một câu tiếng Việt. Lỗi kiểu/thiếu field vẫn còn đuôi Pydantic tiếng Anh (`Field required`, `Extra inputs are not permitted`) — đây là TODO-03 của T04 đã ACCEPT_LATER → T11, không tính lại.
- Xóa suất hợp lệ không chạm `booking_seats` (127 → 127). Suất có vé không xóa được nên không mồ côi booking.
- Không có secret, `.env`, `*.db` hay model trong diff.

## 7. Regression (BOI_CANH_DU_AN mục 7)

Chạy trên backend thật (uvicorn cổng 8000, SQLite tạm) + frontend real cổng 5173 + frontend mock cổng 5175.

| # | Mục | Kết quả |
|---|---|---|
| 1 | Trang chủ hiện phim, poster intro | ⚠ API trả 21 phim, frontend không đổi phần này. Nhưng mục "Phim hot trong tuần" từ 9 phim (master) còn 4 phim (`[4, 3, 1, 2]`) vì `_seed_bookings()` bỏ qua phim không có suất — **RF-01** |
| 2 | Tìm "meo muop" | ✔ `['Mèo Mướp Đi Lạc']` |
| 3 | Đăng ký; chưa đăng nhập bị chặn đặt vé | ✔ register `201`; POST `/api/bookings` không token `401`; route/auth không đổi |
| 4 | Đặt vé 2 ghế, ghế xám, "Vé của tôi" | ⚠ Với phim 1: ✔ (`201`, H3/H4 xám, có trong `/me`). Với phim 5, 8, 9, 10, 18: **không có suất nào để đặt** (trang `/phim/9#lich-chieu` hiện "Hiện chưa có suất chiếu nào sắp tới.") — **RF-01** |
| 5 | Bình luận tiêu cực bị ẩn, admin thấy ~0,99 | ✔ `is_negative=True`, `negative_score=0.9937`, admin thấy cùng điểm |
| 6 | `/api/health` | ✔ `{"status":"ok","classifier":"phobert","classifier_error":null}` |
| 7 | `VITE_USE_MOCK=true` | ⚠ CRUD/booking/admin chạy; nhưng seed mock cũng chỉ còn 4 phim có suất — **RF-01** |

## 8. Scope Integrity

14 file trong diff đều thuộc allowlist T05 mục 6. Không file nào bị cấm bị sửa. `bookings.py` không bị sửa (đúng, vì ngoài allowlist). Diff `seed.py` chỉ trong `_ensure_showtimes()`; diff `global.css` chỉ thêm class T05.

## 9. Independent Tests

### 9.1. Real API (TestClient, SQLite tạm, PhoBERT thật) — 43/44 check đạt

- AC-01: 8/8 (4 route × anon/user).
- AC-02/03: 8 check biên ±114/±115, trùng giờ, khác phòng.
- PUT: chính nó (không tự xung đột) `200`; đổi phòng sang phòng bận `409`; đổi giờ cùng phòng `200`; id không tồn tại `404`.
- 422 (11 ca): quá khứ, giá 9.000 / 501.000 / 75.500, phòng `Phòng 9`, phim 99999, phim `ended` (#12), `movie_id=0`, field lạ, thiếu `price`, `start_time="abc"`. Câu lỗi nghiệp vụ tiếng Việt.
- Biên giá 10.000 và 500.000 → `201`.
- AC-04, AC-06, DELETE hợp lệ `200`, xóa lại `404`, `booking_seats` nguyên vẹn, lọc `movie_id + date`, `?date=xx` → `422`.
- 1 check "admin vs public consistent" báo FAIL là **lỗi của probe**: danh sách public được lấy trước khi probe xóa một suất (`sdel`), nên admin list không còn suất đó. Hai endpoint cùng serialize `ShowtimeOut` từ cùng bảng; các suất còn lại khớp.

### 9.2. So sánh seed master và T05 (DB trống, khởi động qua lifespan)

```
MASTER future showtimes: {1:12, 2:12, 3:12, 4:12, 5:12, 8:12, 9:12, 10:12, 18:12}
MASTER hot_week:         [9, 4, 8, 3, 18, 10, 1, 2, 5]
T05    future showtimes: {1:12, 2:12, 3:12, 4:12, 5:0, 8:0, 9:0, 10:0, 18:0}
T05    hot_week:         [4, 3, 1, 2]
```

Bản sao `backend/firefly.db` hiện tại (5 ngày đã có sẵn từ master), gọi `_ensure_showtimes(days=7)` của T05: ngày 13/10 chỉ có phim `{1, 2, 3, 4}`, ngày 14/10 cũng vậy. Tức là trên máy Tín, từ ngày mai mỗi ngày mới sinh ra chỉ còn 4 phim; sau 5 ngày, 5 phim đang chiếu hết suất.

### 9.3. AC-05 restart thật

Xem bảng AC. 3 lần khởi động uvicorn, 0 cặp chồng giờ, suất admin giữ nguyên.

### 9.4. Mock (Vite SSR module trong trình duyệt, cổng 5175)

26 check đạt (xem AC-07), F5 persistence đạt. Đếm suất seed mock: `{1:12, 2:12, 3:12, 4:12, 5:0, 8:0, 9:0, 10:0, 18:0}`.

### 9.5. UI

- Mock 375×812: `/quan-tri/suat-chieu` có form, 2 bộ lọc, bảng `overflow-x:auto`, `scrollWidth = innerWidth = 375` (không tràn ngang); gửi form chồng giờ hiện `Phòng 1 đã có suất Chuyến Tàu Cuối Mùa Mưa lúc 22:00. …`.
- Real (5173 → backend tạm 8000): admin page tải `GET /api/admin/movies` và `/api/admin/showtimes?date=…` `200`; thêm suất qua form → `POST 201`, thông báo "Đã thêm suất chiếu mới.", bảng 12 → 13 dòng. Bảng ngày 08/10 chỉ có 4 phim (Bóng Ma Hẻm 37, Mèo Mướp Đi Lạc, Chuyến Tàu Cuối Mùa Mưa, Đội Cứu Hộ Sông Hồng) — cùng triệu chứng RF-01.
- Header có mục "Quản lý suất chiếu" cho admin; route nằm trong `ProtectedRoute adminOnly`.

### 9.6. Gate cuối (sau khi xóa probe)

| Gate | Kết quả |
|---|---|
| `backend\venv\Scripts\python -m compileall -q backend\app` | exit 0 |
| Backend startup (uvicorn thật, SQLite tạm) | startup complete, 3 lần |
| `GET /api/health` | `200`, `classifier=phobert`, `classifier_error=null` |
| `cd frontend; npm run build` | ✓ built (231,93 kB JS) |
| Real API probes | 43/44 (1 lỗi probe, giải thích ở 9.1) |
| Mock mode | đạt contract; seed mock dính RF-01 |
| Hồi quy | 4/7 sạch, 3/7 bị RF-01 |
| Scope / secret | đạt |
| pytest | chưa bắt buộc trước T11 |

## 10. Temporary Probes

Tất cả nằm ngoài repo, trong scratchpad của phiên Claude: `seed_cmp.py`, `probe_api.py`, `restart_probe.py`, `regress.py`, các DB SQLite tạm, một git worktree `master` tạm để so sánh seed. Thêm tạm 2 cấu hình vào `.claude/launch.json` (file bị `.git/info/exclude`). **Đã xóa hết** trước gate cuối: script, DB, worktree (`git worktree list` chỉ còn repo chính), `launch.json` khôi phục bản gốc. `backend/firefly.db` thật không bị ghi (chỉ đọc bản sao). `git status` sạch trước khi viết report.

## 11. Required Fixes

### RF-01 — Seed sinh suất chiếu bỏ trống 5/9 phim đang chiếu

| Trường | Nội dung |
|---|---|
| Severity | **High** (hồi quy luồng đặt vé lõi và dữ liệu demo) |
| File | `backend/app/seed.py` (`_ensure_showtimes()`), `frontend/src/api/mock.js` (`buildShowtimes()`) |
| Problem | Phòng gán cố định `ROOMS[idx % 4]` và khung giờ chọn theo `(i + idx + ngày) % 2`. Phim có `idx` và `idx + 4` dùng chung phòng và có cùng tính chẵn lẻ, nên luôn rơi vào **cùng khung giờ**. Trước T05 các suất này chồng nhau nhưng vẫn được tạo; T05 bỏ qua suất chồng, nên phim đến sau (idx 4–8: phim 5, 8, 9, 10, 18) bị bỏ qua **toàn bộ**. `_seed_bookings()` gặp phim không có suất thì `continue`, nên bộ sưu tập "Phim hot" cũng mất các phim này. |
| Evidence | Mục 9.2 (DB trống: 5 phim 0 suất, hot_week 9 → 4 phim); bản sao `firefly.db`: ngày 13/10 và 14/10 chỉ có phim 1–4; mock: cùng số đếm; UI `/phim/9#lich-chieu`: "Hiện chưa có suất chiếu nào sắp tới."; admin page ngày 08/10 chỉ có 4 phim. |
| Expected Fix | Giữ nguyên luật chống chồng giờ (AC-05), nhưng sửa cách phân bổ trong `_ensure_showtimes()` và `buildShowtimes()` để **mọi phim `now_showing` đều có suất mỗi ngày**. Ví dụ: khi phòng ưu tiên bận thì thử phòng còn trống khác trong `ROOMS`, hoặc lệch khung giờ theo nhóm phim dùng chung phòng. Backend và mock phải cùng thuật toán. Không đổi schema, không sửa ngoài allowlist. Report fix cần có: (1) bảng số suất tương lai theo từng phim trên DB trống, mọi phim đang chiếu > 0, cho cả real và mock; (2) `hot_week` lại đủ 9 phim; (3) chạy lại AC-05 bằng restart thật, 0 cặp chồng giờ; (4) chạy lại checklist hồi quy. Lưu ý: DB đã có dữ liệu sẽ tự lấp ngày mới; không yêu cầu xóa `firefly.db`. |

## 12. TODO (không chặn, chờ PO disposition)

| ID | Mức | Nội dung | Đề xuất |
|---|---|---|---|
| TODO-01 | Low | Mock tính ghế giả `seedBooked()` là vé thật, nên **mọi suất seed trong mock đều bị khóa** (`409 … 9 vé`); real cho sửa/xóa suất seed chưa bán vé. Contract endpoint giống nhau, chỉ khác dữ liệu. | ACCEPT hoặc ACCEPT_LATER → T11 |
| TODO-02 | Low | Sửa suất của phim đã `ended`: ô "Phim" chỉ liệt kê phim chưa ended nên hiện trống, form báo "Hãy chọn phim." Backend cũng từ chối (422) nên nhất quán, chỉ là UX. Admin vẫn xóa được suất chưa bán vé. | ACCEPT / WONT_FIX |
| TODO-03 | Low | `find_showtime_conflict()` duyệt mọi suất của phòng, không lọc theo khoảng ngày. Ổn ở quy mô demo; nếu bảng lớn thì lọc `start_time` trong cửa sổ ±1 ngày. | ACCEPT_LATER → T11 |
| TODO-04 | Process | Report Codex ghi AC-05/AC-08 "Đạt" và "trang admin 12 dòng dữ liệu mẫu" nhưng không đối chiếu số suất theo phim với master; AC-05 chỉ kiểm "không chồng" mà không kiểm "vẫn đủ suất". | DOCUMENTED — fix report cần bảng số suất theo phim |

## 13. Scope Conflict / PO Decision Needed — T04 TODO-07 (đặt vé phim `ended`)

1. **Vấn đề có tồn tại không: CÓ (đã xác minh).** Đặt phim 1 sang `ended` qua `PUT /api/admin/movies/1` (`200`), rồi user `POST /api/bookings` vào suất tương lai của phim 1 → **`201`**, vé được tạo. `GET /api/movies/1/showtimes` vẫn trả 12 suất tương lai; chỉ giao diện chi tiết phim ẩn lịch. `create_booking()` chỉ kiểm suất tồn tại và chưa bắt đầu, không kiểm `movie.status`.
2. **Ảnh hưởng:**
   - Nghiệp vụ: Trung bình. Người dùng gọi API trực tiếp (hoặc giữ link `/dat-ve/<id>` cũ) vẫn mua được vé cho phim admin đã ngừng chiếu. Suất đó lại không sửa được (PUT với phim ended → 422) nên admin chỉ còn cách xóa trước khi có người đặt.
   - Bảo mật: Thấp. Không leo thang quyền, không lộ dữ liệu; cần tài khoản đã đăng nhập; đây là lỗ hổng logic nghiệp vụ, không phải lỗ hổng phân quyền.
3. **Có chặn AC/DoD T05 không: KHÔNG.** Không AC nào của T05 yêu cầu chặn đặt vé phim ended. Phần T05 làm được trong allowlist (không tạo/sửa suất cho phim ended) đã đúng. Vấn đề **chưa RESOLVED**.
4. **Đề xuất:** sửa ở nguồn bằng một kiểm tra trong `create_booking()` (`st.movie.status == "ended"` → `HTTPException` một câu tiếng Việt) và kiểm tra tương đương trong `mock.js` `bookings.create`; tùy chọn lọc phim ended ở `GET /api/movies/{id}/showtimes`.

> **PO ACTION REQUIRED:** Tín chọn một trong hai:
> (a) Mở rộng allowlist T05 cho `backend/app/routers/bookings.py` (và tùy chọn `backend/app/routers/movies.py`) để Codex sửa luôn trong vòng FIX_LOOP này, kèm AC bổ sung "đặt vé suất của phim `ended` → 4xx, real và mock".
> (b) Giữ nguyên allowlist T05, ghi TODO-07 vế 2 thành ACCEPT_LATER → T11 (kiểm thử và sửa lỗi).
> Claude nghiêng về (a) vì T05 đã vào FIX_LOOP và sửa chỉ vài dòng, nhưng đây là quyết định của PO. Nếu không có chỉ thị, Codex **không** được sửa `bookings.py`.

## 14. Final Decision

**FAIL**

- AC: 7/8 đạt (AC-01 → AC-07); AC-08 không đạt.
- Required Fixes: 1 (RF-01, High).
- TODO: 4 (Low/Process).
- Scope conflict: 1, cần PO quyết (mục 13).
- Trạng thái: T05 `CLAUDE_REVIEW` → `FIX_LOOP`. Không mở task kế tiếp. T06 giữ `PLANNED` (Q2 còn mở).
- Bước tiếp theo: Codex sửa đúng RF-01 (và bookings nếu PO chọn (a)), tạo `reports/YYYY-MM-DD/codex_fix_T05_round1_YYYY-MM-DD.md`, chuyển `FIX_LOOP` → `CLAUDE_REVIEW`.
