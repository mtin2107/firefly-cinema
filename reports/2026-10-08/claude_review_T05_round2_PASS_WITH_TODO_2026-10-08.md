# Claude Independent Review — T05 Round 2

| Trường | Giá trị |
|---|---|
| Task | T05 — Quản lý suất chiếu (admin) |
| Nhánh | `task/T05-quan-ly-suat-chieu` (HEAD `c229656`) |
| Baseline | `a09fe6736d4a5d465e07dfa026b032caf9afe0be` |
| Review trước | `claude_review_T05_FAIL_2026-10-08.md` (commit `816f972`), RF-01 High |
| Fix commit | `f5fca8d151e214c333a3d1ad5a06a446db85e452` |
| Reviewer | Claude (Independent Reviewer / Tester) |
| Ngày | 08/10/2026 (probe chạy lúc khoảng 22:50–23:10) |
| **Kết quả** | **PASS_WITH_TODO** |
| RF-01 | **CLOSED** |
| AC | **8/8** |
| Chuyển trạng thái | `CLAUDE_REVIEW` → `PO_REVIEW` |

---

## 1. Source Review

Đã đọc: `docs/tasks/T05.md`, `docs/TASK_COORDINATION_ACTIVE.md`, review FAIL vòng 1, `reports/2026-10-08/codex_fix_T05_round1_2026-10-08.md`. Đã đọc diff thật `git diff 816f972 HEAD` của `seed.py` và `mock.js`.

Coordination trước review: `Overall Status: CLAUDE_REVIEW`, dòng T05 ghi `CLAUDE_REVIEW (Round 2; RF-01 fix f5fca8d)`. Codex đã đồng bộ `FIX_LOOP → CLAUDE_REVIEW` nên review chính thức được tiến hành.

## 2. Git / Scope Integrity

| Kiểm tra | Kết quả |
|---|---|
| Nhánh | `task/T05-quan-ly-suat-chieu` ✔ |
| `merge-base master HEAD` | `a09fe67…` = baseline ✔ |
| Fix commit `f5fca8d` | tồn tại, nằm sau review FAIL `816f972` ✔ |
| Working tree trước review | sạch ✔ |
| `git diff --check master...HEAD` | exit 0 ✔ |
| Diff `816f972..HEAD` | `backend/app/seed.py`, `frontend/src/api/mock.js`, `docs/TASK_COORDINATION_ACTIVE.md`, `reports/…/codex_fix_T05_round1_…md` ✔ |
| `seed.py` | 1 hunk `@@ -21,28 +21,58 @@ def _ensure_showtimes`, nằm trọn trong `_ensure_showtimes()` ✔ |
| `mock.js` | 2 hunk: `buildShowtimes()` và nhánh "cùng ngày" của `load()` (repair localStorage) — đúng phạm vi RF-01 ✔ |
| Toàn bộ `master...HEAD` | 16 file: 13 file T05 trong allowlist + 3 report (Codex impl, Codex fix, Claude review vòng 1) và coordination ✔ |
| Forbidden / ngoài allowlist (`models.py`, `seats.py`, `classifier.py`, `bookings.py`, `movies.py`) | 0 dòng diff ✔ |
| Secret, `.env`, `*.db`, model, CSV | 0 ✔ |
| Đổi schema / thư viện | Không ✔ |

## 3. Xác minh RF-01 độc lập

Cách làm: SQLite tạm sạch, **uvicorn thật** khởi động qua lifespan (PhoBERT thật), sau đó đọc trực tiếp bảng `showtimes`.

### 3.1. Phân bổ theo phim/ngày (DB sạch)

| Ngày | Tổng | 1 | 2 | 3 | 4 | 5 | 8 | 9 | 10 | 18 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 08/10 | 20 | 4 | 2 | 3 | 2 | 3 | 2 | 2 | 1 | 1 |
| 09/10 | 19 | 2 | 4 | 2 | 3 | 2 | 3 | 1 | 1 | 1 |
| 10/10 | 20 | 4 | 2 | 4 | 2 | 3 | 2 | 1 | 1 | 1 |
| 11/10 | 20 | 2 | 4 | 3 | 4 | 1 | 3 | 1 | 1 | 1 |
| 12/10 | 20 | 4 | 3 | 5 | 2 | 2 | 1 | 1 | 1 | 1 |

| Tiêu chí | Kết quả |
|---|---|
| 1. Cả 9 phim `now_showing` có suất | ✔ |
| 2. Mỗi phim có ≥ 1 suất mỗi ngày seed | ✔ (`missing = []` cả 5 ngày) |
| 3. Không chồng giờ cùng phòng | ✔ 0 cặp trên 99 suất |
| 4. Khoảng chiếm phòng vẫn `duration_min + 15` | ✔ `find_showtime_conflict()` không đổi; khe trống nhỏ nhất giữa hai suất liền kề cùng phòng sau khi trừ thời lượng phim là **19 phút** (≥ 15) |
| 5. Tổng số và bảng phân bổ | ✔ 99 suất; bảng trùng khớp từng ô với report Codex |
| 6. Hot week | ✔ `[9, 4, 8, 3, 18, 10, 1, 2, 5]` — đủ 9 phim, đúng thứ tự master |
| 7. Không mất phim/booking/booking seat | ✔ movies 21, bookings 140, booking_seats 280 (bằng master) |

### 3.2. Đối chiếu 99 / 79 / 20 của Codex

- **99** = tổng suất seed trong 5 ngày 08–12/10 ✔.
- **79** = tổng bảng "suất tương lai" `{1:12, 2:13, 3:14, 4:11, 5:8, 8:9, 9:4, 10:4, 18:4}` ✔ (đo lúc 22:51).
- **20** = số suất ngày 08/10 ✔.
- Chênh lệch **99 − 79 = 20 là đúng và có lý do**: khung giờ muộn nhất là 22:00. Khi đo sau 22:00 ngày 08/10, cả 20 suất hôm nay đã bắt đầu, nên `GET /api/movies/{id}/showtimes` (lọc `start_time > now`) không trả chúng. Không có suất nào bị mất. Nếu đo vào ban ngày, con số "tương lai" sẽ lớn hơn 79.

## 4. Restart / Idempotency

### 4.1. DB sạch + suất admin + booking (uvicorn thật, 3 lần khởi động)

1. Startup 1: 99 suất, 0 chồng.
2. Admin tạo suất #100 (phim 9, 10/10 06:00, Phòng 1) `201`; user đặt D4, D5 `201`.
3. (Thử thêm) Admin xóa một suất seed chưa bán vé (#61, phim 2, 11/10 22:00, Phòng 1) `200`.
4. Restart 2 và 3:

| Snapshot | showtimes | bookings | booking_seats | Chồng giờ | Dòng cũ giữ nguyên | Suất admin #100 |
|---|---:|---:|---:|---:|---|---|
| Sau bước 3 | 99 | 141 | 282 | 0 | — | có |
| Restart 2 | 100 | 141 | 282 | 0 | ✔ từng dòng | có |
| Restart 3 | 100 | 141 | 282 | 0 | ✔, giống hệt restart 2 | có |

- Không nhân đôi suất; restart 3 không đổi gì so với restart 2.
- Mọi phim có lịch đủ 5 ngày sau mỗi lần restart.
- Dòng duy nhất được thêm ở restart 2 là **#101 = đúng suất #61 admin vừa xóa** (cùng phim, giờ, phòng, giá) → TODO-05.

### 4.2. Mô phỏng các ngày khởi động kế tiếp

Đổi `date.today()` sang +1, +2, +3 ngày trên cùng DB: các ngày đã seed giữ nguyên số suất (19/21/20/20), chỉ ngày mới được thêm 20 suất. Chạy lại cùng ngày thêm 0. Lịch không tự phình ra theo ngày.

### 4.3. DB cũ bị RF-01 (tạo bằng code `816f972`)

Dùng git worktree tạm tại `816f972`, khởi động uvicorn để có DB lỗi: 60 suất, chỉ phim 1–4, phim 5/8/9/10/18 = 0 mọi ngày. Thêm 1 booking (C1, C2) trên suất cũ của phim 1. Sau đó khởi động **code HEAD** trên chính DB đó:

| | Trước | Sau |
|---|---|---|
| showtimes | 60 | 100 (+40) |
| bookings / booking_seats | 63 / 126 | 63 / 126 |
| Phim thiếu theo ngày | 5, 8, 9, 10, 18 ở cả 5 ngày | không thiếu |
| 60 dòng cũ | — | giữ nguyên từng cột (id, phim, giờ, phòng, giá) |
| Chồng giờ liên quan dòng mới | — | 0 |

### 4.4. Bản sao `backend/firefly.db` thật (chỉ đọc bản sao, không chạm file gốc)

- 270 dòng cũ giữ nguyên, booking 140/280 không đổi; mọi phim đủ 5 ngày.
- Seed thêm 38 suất mới, 0 suất mới chồng với bất kỳ suất nào.
- Dữ liệu cũ từ thời master vốn có 190 cặp chồng giờ. Seed không xóa hay sửa chúng (đúng nguyên tắc "chỉ thêm"); ghi chú ở TODO-06.

## 5. Backend / Mock Parity

| Kiểm tra (Vite `VITE_USE_MOCK=true`, cổng 5175) | Kết quả |
|---|---|
| Fresh mock | 99 suất, 0 chồng, bảng phân bổ trùng 3.1 từng ô; suất tương lai theo phim giống real |
| **Cùng thuật toán** | Tập `(phim, giờ, phòng, giá)` của 99 suất mock và 99 suất real (DB sạch, bỏ suất admin) có **SHA-256 trùng nhau** `cb091db4…bcec6bf` |
| F5 sau khi tạo suất admin #100 + booking D4/D5 | raw localStorage **không đổi một byte**; suất admin, `adminShowtimeIds=[100]`, vé trong "Vé của tôi" và ghế xám còn nguyên |
| Repair localStorage cũ | Xóa mọi suất của phim 5/8/9/10/18 (giữ #100), cùng `showtimesDay`, F5 → 62 → 100 suất; 62 dòng cũ giữ nguyên; 0 chồng; 0 ID trùng; `seq.showtime` 139 > max id 138; đủ 9 phim mỗi ngày; booking #100 còn |
| F5 lần nữa sau repair | raw localStorage giống hệt → idempotent |
| Luật đặt vé mock | không đổi (diff không đụng `bookings.create`); đặt lại ghế đã đặt → `409 Ghế E5 vừa có người đặt…` |
| Hot week mock | `[9, 4, 8, 3, 18, 10, 1, 2, 5, …]` |

## 6. Acceptance Criteria (chạy lại đầy đủ)

| AC | Kết quả | Bằng chứng |
|---|---|---|
| AC-01 | ✔ | Real: anon 401 / user 403 cho cả 4 route. Mock: anon 401 ×4, user 403 ×4. |
| AC-02 | ✔ | Real và mock: +114 → 409 đúng câu; +115 → 201; −114 → 409; −115 → 201. |
| AC-03 | ✔ | Khác phòng cùng giờ → 201 (real, mock). |
| AC-04 | ✔ | Suất có 2 vé: PUT/DELETE → 409 `Suất chiếu đã có 2 vé, không sửa hay xóa được.` (real, mock). |
| AC-05 | ✔ | Mục 4: 3 lần khởi động uvicorn thật, 0 chồng, không mất lịch phim, suất admin + booking giữ nguyên, DB cũ RF-01 được lấp mà không sửa/xóa dòng cũ. |
| AC-06 | ✔ | Phim mới → suất → public showtimes → đặt vé 201 (real); `/phim/<id>#lich-chieu` hiện lịch (mock, vòng 1, code trang không đổi). |
| AC-07 | ✔ | Mục 5 + contract mock: CRUD, 409, 422 (quá khứ, giá 75.500, phòng sai, phim ended), PUT chính nó, khóa vé, F5. |
| AC-08 | ✔ | Mục 7: 7/7. |

**8/8.**

Ca bổ sung (real): PUT chính nó 200; PUT đổi phòng sang phòng bận 409; 422 cho giá 9.000 / 501.000 / 75.500, phòng `Phòng 9`, phim 99999, phim ended, field lạ; giá 10.000 và 500.000 nhận.

## 7. Regression (BOI_CANH mục 7)

| # | Mục | Kết quả |
|---|---|---|
| 1 | Trang chủ, poster intro | ✔ Mock 375px: bấm "Xem chi tiết" hiện `intro` rồi vào `/phim/9`; API hot week đủ 9 phim |
| 2 | Tìm "meo muop" | ✔ `['Mèo Mướp Đi Lạc']` |
| 3 | Đăng ký; chưa đăng nhập bấm giờ chiếu | ✔ register 201; POST booking không token 401; mock: bấm 16:00 ở `/phim/9` → `/dang-nhap` với `from=/dat-ve/112` |
| 4 | Đặt 2 ghế, ghế xám, Vé của tôi | ✔ Real: đặt H3/H4 thành công cho **từng** phim 5, 8, 9, 10, 18 (8/9/4/4/4 suất tương lai), ghế xám, `/me` đủ 6 vé |
| 5 | Bình luận tiêu cực | ✔ `is_negative=True`, `0.9937`, admin thấy cùng điểm |
| 6 | Health | ✔ `{"status":"ok","classifier":"phobert","classifier_error":null}` |
| 7 | Mock | ✔ Mục 5; trang admin mock 375px: 20 dòng/9 phim, `scrollWidth = innerWidth = 375`, bảng `overflow-x:auto`; `/phim/9#lich-chieu` có lịch |

Probe real 40/41 check đạt. Check còn lại (`movies == 21`) sai do chính probe tạo thêm "Phim Thu R2" nên API trả 22. Không phải lỗi sản phẩm.

## 8. Definition of Done

| Mục | Trạng thái |
|---|---|
| Code đúng allowlist, commit `[T05]` | ✔ |
| RF-01 sửa đúng phạm vi | ✔ |
| Gate web | ✔ (mục 10) |
| Hồi quy 7/7 | ✔ |
| Report fix có bảng số suất từng phim/ngày, restart, repair | ✔ |
| `ARCHITECTURE.md` | ✔ (vòng 1; mô tả "seed lấp từng khung còn trống" vẫn đúng) |

**DoD: MET**, kèm các TODO và scope conflict để PO xử lý.

## 9. Independent Tests / Temporary Probes

Script probe đặt trong scratchpad của phiên Claude, ngoài repo: backend restart (uvicorn thật, port 8019), mô phỏng ngày kế tiếp, TestClient API/hồi quy, so sánh hash real–mock. Thêm một git worktree tạm tại `816f972` và một cấu hình Vite mock tạm trong `.claude/launch.json` (file bị `.git/info/exclude`).

**Đã xóa hết trước gate cuối:** script, mọi SQLite tạm, worktree (`git worktree list` chỉ còn repo chính), `launch.json` khôi phục bản gốc. `backend/firefly.db` thật không bị ghi.

## 10. Final Gates (sau khi xóa probe)

| Gate | Kết quả |
|---|---|
| `backend\venv\Scripts\python -m compileall -q backend\app` | exit 0 |
| Uvicorn startup (SQLite tạm, port 8021) | `Application startup complete` |
| `GET /api/health` | `{"status":"ok","classifier":"phobert","classifier_error":null}` |
| `cd frontend; npm run build` | ✓ built |
| Real API / mock / browser probes | đạt (mục 3–7) |
| Security 401/403 | 4/4 real, 8/8 mock |
| Responsive 375px | đạt |
| `git diff --check`, scope, secret | đạt |
| pytest | chưa bắt buộc trước T11 |

## 11. Required Fixes

| RF | Trạng thái |
|---|---|
| RF-01 (High) — seed bỏ trống 5/9 phim | **CLOSED** (mục 3–5) |

Không có RF mới.

## 12. TODO (không chặn, chờ PO disposition)

| ID | Mức | Nội dung | Đánh giá vòng 2 / đề xuất |
|---|---|---|---|
| TODO-01 | Low | Mock tính ghế giả `seedBooked()` là vé | **Còn.** Vòng 2 xác nhận cả 79/79 suất seed tương lai trong mock đều bị khóa 409, nên admin mock chỉ sửa/xóa được suất mình tạo. ACCEPT hoặc → T11 |
| TODO-02 | Low | Sửa suất của phim ended: ô Phim trống | **Còn** (`AdminShowtimes.jsx` không đổi). ACCEPT / WONT_FIX |
| TODO-03 | Low | `find_showtime_conflict()` không lọc theo ngày | **Còn, số lần gọi tăng:** mỗi ứng viên giờ thử tới 4 phòng và có thêm pass 1. Thời gian khởi động vẫn vài giây ở quy mô hiện tại. → T11 |
| TODO-04 | Process | Evidence report Codex | **RESOLVED** — fix report có bảng trước/sau theo phim, phân bổ theo ngày, restart, DB cũ, repair mock; số liệu khớp đo độc lập. Chỉ cần ghi rõ hơn rằng 79 = 99 − 20 suất đã qua giờ của ngày đo |
| TODO-05 | **Medium** (mới) | **Suất seed bị admin xóa sẽ quay lại khi khởi động lại backend.** Đã xác minh: xóa #61 → restart → seed tạo #101 cùng phim/giờ/phòng/giá. Nguyên nhân: seed lấp từng khung trống mỗi lần khởi động, không có chỗ ghi "admin đã xóa" (không đổi schema). Hành vi này đã có từ vòng 1 (Claude bỏ sót ở review vòng 1). Mock hiện không gặp vì TODO-01 khóa mọi suất seed, nhưng nhánh repair `load()` có cùng logic. | Không vi phạm AC (T05 mục 2/3 yêu cầu seed lấp khung trống). PO chọn: ghi nhận là giới hạn đã biết khi demo, hoặc → T11 (ví dụ chỉ lấp ngày chưa có suất nào), hoặc xem cùng Q2 nếu muốn lưu cờ vào schema |
| TODO-06 | Low (mới) | (a) Phân bổ không đều: phim 9, 10, 18 chỉ 1 suất/ngày (4 suất tương lai), trong khi phim 9 đứng đầu "Phim hot". Suất duy nhất trong ngày có thể đã qua giờ. (b) DB cũ thời master có sẵn 190 cặp chồng giờ, seed không dọn (đúng nguyên tắc chỉ thêm). Lần đầu chạy trên `firefly.db` thật sẽ thêm 38 suất vào các ngày đã có. | ACCEPT; nếu muốn dữ liệu demo sạch thì Tín xóa `firefly.db` trước buổi demo (T12) |

## 13. Scope Conflict — đặt vé phim `ended`

- **Trạng thái: OPEN / PO ACTION REQUIRED.** Vòng 2 xác minh lại: chuyển phim 1 sang `ended`, POST `/api/bookings` vào suất tương lai của nó → **201**. `bookings.py` và `movies.py` không bị sửa (đúng chỉ thị).
- **Có ảnh hưởng tới quyết định RF-01 / T05 không: KHÔNG.**
  - RF-01 là lỗi phân bổ seed, độc lập với luồng booking.
  - Không AC nào của T05 yêu cầu chặn đặt vé phim ended. Phần T05 làm được trong allowlist (không tạo/sửa suất cho phim ended) đã đạt.
  - Vấn đề có từ trước T05 (T04 TODO-07) và cần sửa file ngoài allowlist.
- **Yêu cầu:** Tín chốt trong PO review, **trước khi APPROVED**: (A) mở rộng scope T05 (thêm một vòng Codex + Claude cho `bookings.py` và mock), hoặc (B) ACCEPT_LATER → T11. Nếu chọn (B), nên ghi rõ trong PO review rằng tới T11, API vẫn cho đặt vé phim ended.

## 14. Final Decision

**PASS_WITH_TODO**

- RF-01: **CLOSED**. Required Fixes mở: 0.
- AC: **8/8**. DoD: MET.
- TODO: 6 (TODO-04 RESOLVED; TODO-05 Medium mới; còn lại Low).
- Scope conflict booking phim ended: OPEN, chờ PO, không chặn nghiệm thu kỹ thuật.
- Trạng thái: T05 `CLAUDE_REVIEW` → `PO_REVIEW`.
- Không PO APPROVED, không merge, không DONE/CLOSED. T06 giữ `PLANNED` (Q2 còn mở).

### Bàn giao task kế tiếp

Theo `AGENT_RULES.md` mục 1.1, task đủ điều kiện kế tiếp là **T07** (T06 bị chặn bởi Q2; T07 chỉ phụ thuộc T01 đã CLOSED). Ở T04 và T05, PO đều tự authorize task kế tiếp, và prompt review này chỉ yêu cầu giữ T06. Vì vậy Claude **không** đổi trạng thái T07, để Tín quyết sau PO review T05.

Trước khi gửi bất kỳ task nào, Tín cần:
1. PO review T05 và chốt scope conflict (A/B).
2. `git checkout master` → `git merge task/T05-quan-ly-suat-chieu`.
3. Tạo nhánh task mới **từ master đã merge**.
