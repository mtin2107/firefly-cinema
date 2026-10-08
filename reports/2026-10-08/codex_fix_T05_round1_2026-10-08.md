# Fix Report — T05 Round 1

## 1. Thông tin

- Task: `T05 — Quản lý suất chiếu (admin)`
- Nhánh: `task/T05-quan-ly-suat-chieu`
- Review FAIL: `816f97225b11b1de07e350489320893e51a89c69`
- Fix commit: `f5fca8d151e214c333a3d1ad5a06a446db85e452`
- RF-01 (High): **FIXED theo evidence của Codex, chờ Claude xác minh độc lập**
- Đổi schema: **Không**

## 2. Root cause

Seed cũ gán cố định `ROOMS[idx % 4]`. Phim ở vị trí `idx` và `idx + 4` vừa dùng cùng phòng, vừa chọn cùng parity khung giờ. Khi T05 bắt đầu chặn chồng giờ, phim được xét sau bị bỏ qua ở mọi khung; vì vậy phim 5, 8, 9, 10, 18 có 0 suất.

Mock dùng cùng mô hình gán cố định nên lỗi tương đương. Ngoài ra, localStorage mock lỗi trong cùng ngày được trả ngay mà không chạy lại phân bổ, nên F5 không tự sửa dữ liệu cũ.

## 3. Cách sửa

- Backend `_ensure_showtimes()`:
  - Pass 1 bảo đảm mỗi phim `now_showing` có ít nhất một suất mỗi ngày.
  - Mỗi ứng viên thử tuần tự toàn bộ phòng, bắt đầu từ phòng xoay theo phim/ngày/khung giờ.
  - Nếu khung ưu tiên bận, thử các khung còn lại; mọi phép thử vẫn gọi `find_showtime_conflict()` với `duration_min + 15 phút`.
  - Pass 2 lấp thêm lịch mẫu theo pattern cũ, cũng thử phòng thay thế.
  - Chỉ thêm dòng còn thiếu; không update/delete suất, booking hoặc booking seat hiện hữu.
- Mock `buildShowtimes()` dùng cùng hai pass, thứ tự xoay phòng và quy tắc giao khoảng.
- Mock `load()` sửa dữ liệu localStorage cũ tại chỗ bằng cách chỉ append các suất còn thiếu; giữ ID cũ, suất admin và booking. Reload tiếp theo không thêm trùng.

## 4. Files changed trong Fix Round 1

- `backend/app/seed.py` — chỉ `_ensure_showtimes()`.
- `frontend/src/api/mock.js` — `buildShowtimes()` và nhánh `load()` trực tiếp cần để repair/persist RF-01.
- `reports/2026-10-08/codex_fix_T05_round1_2026-10-08.md`.
- `docs/TASK_COORDINATION_ACTIVE.md`.

Không sửa `bookings.py`, `movies.py`, model, classifier, `normalize()`, `seats.py`, schema hay thư viện.

## 5. Bảng số suất từng phim — trước/sau

DB SQLite tạm sạch, backend thật qua lifespan; số dưới đây là suất tương lai tại thời điểm probe. Mock cho kết quả giống hệt backend.

| Movie ID | Trước real | Trước mock | Sau real | Sau mock |
|---:|---:|---:|---:|---:|
| 1 | 12 | 12 | 12 | 12 |
| 2 | 12 | 12 | 13 | 13 |
| 3 | 12 | 12 | 14 | 14 |
| 4 | 12 | 12 | 11 | 11 |
| 5 | 0 | 0 | 8 | 8 |
| 8 | 0 | 0 | 9 | 9 |
| 9 | 0 | 0 | 4 | 4 |
| 10 | 0 | 0 | 4 | 4 |
| 18 | 0 | 0 | 4 | 4 |

Tổng sau sửa: 99 suất trong 5 ngày; mọi phim có suất tương lai.

## 6. Phân bổ từng ngày

Real và mock trả cùng bảng `{movie_id: số suất}`:

| Ngày | Phân bổ |
|---|---|
| 08/10/2026 | `1:4, 2:2, 3:3, 4:2, 5:3, 8:2, 9:2, 10:1, 18:1` |
| 09/10/2026 | `1:2, 2:4, 3:2, 4:3, 5:2, 8:3, 9:1, 10:1, 18:1` |
| 10/10/2026 | `1:4, 2:2, 3:4, 4:2, 5:3, 8:2, 9:1, 10:1, 18:1` |
| 11/10/2026 | `1:2, 2:4, 3:3, 4:4, 5:1, 8:3, 9:1, 10:1, 18:1` |
| 12/10/2026 | `1:4, 2:3, 3:5, 4:2, 5:2, 8:1, 9:1, 10:1, 18:1` |

Mỗi ngày có đủ cả 9 phim `now_showing` và có **0 cặp chồng giờ cùng phòng**.

## 7. Hot week

- Trước RF-01: `[4, 3, 1, 2]` — 4 phim.
- Sau RF-01: `[9, 4, 8, 3, 18, 10, 1, 2, 5]` — đủ 9 phim theo `_SAMPLE_SALES`.
- API dùng để xác minh: `GET /api/movies?collection=hot_week` trên DB tạm sạch sau lifespan.

## 8. Restart / idempotency

### DB sạch + suất admin + booking

1. Startup lần 1 qua lifespan tạo 99 suất, 0 chồng.
2. Tạo suất admin ID 100 lúc 06:00 ngày kế tiếp, đặt 2 ghế.
3. Startup lần 2 và lần 3 trên cùng DB tạm.

| Snapshot | Showtime IDs | Bookings | Booking seats | Chồng giờ |
|---|---:|---:|---:|---:|
| Sau admin + booking | 100 ID | 141 | 282 | 0 |
| Restart 2 | đúng cùng 100 ID | 141 | 282 | 0 |
| Restart 3 | đúng cùng 100 ID | 141 | 282 | 0 |

Suất admin ID 100 và booking của nó vẫn tồn tại. Hai lượt Uvicorn thật bổ sung trên cùng DB cũng startup thành công; `/api/health` trả 200 và không tạo thêm dữ liệu trùng.

### Database cũ + ngày mới

Mô phỏng ngày thứ 6 chỉ có bốn phim 1–4 lúc 09:30 ở bốn phòng, kèm một booking trên dòng cũ. Sau `_ensure_showtimes(days=6)`:

- Phân bổ ngày mới: `1:3, 2:4, 3:3, 4:3, 5:1, 8:3, 9:1, 10:1, 18:1`.
- Bốn ID suất cũ vẫn tồn tại.
- Booking và booking seat cũ vẫn tồn tại, tổng booking không đổi.
- 0 cặp chồng giờ.

### Mock persistence / dữ liệu cũ

- Fresh mock: 99 suất, bảng từng phim/ngày giống real, 0 chồng.
- Tạo suất admin ID 100 và booking ID 1; tải lại module như F5: cả hai còn nguyên, raw localStorage không đổi.
- Mô phỏng localStorage lỗi chỉ có phim 1–4: repair giữ 62 ID cũ, suất admin và booking; thêm đủ phim 5, 8, 9, 10, 18.
- Reload lần tiếp theo: số suất giữ nguyên 100, raw localStorage không đổi — idempotent.

## 9. AC-05 và AC-08

### AC-05

Đạt theo evidence implementer: ba startup lifespan và hai startup Uvicorn trên DB tạm không sinh trùng/chồng; suất admin, booking và booking seat giữ nguyên. DB cũ được lấp ngày mới mà không sửa/xóa dữ liệu cũ.

### AC-08 — checklist hồi quy 7 mục

1. Trang chủ: API có phim; browser mock có 9 card; click poster hiện `PosterIntro` và chuyển trang chi tiết.
2. Tìm `meo muop` trả `Mèo Mướp Đi Lạc`; menu/taxonomy không bị sửa.
3. Chưa đăng nhập vào `/dat-ve/1` chuyển `/dang-nhap`; auth code không bị sửa.
4. Phim 5 nay có 8 suất tương lai; đặt 2 ghế qua real API `201`, detail có ghế và `/api/bookings/me` có vé.
5. Bình luận `Ko hay như quảng cáo, hơi thất vọng` bị đánh dấu tiêu cực; admin thấy score `0.9937` bằng PhoBERT thật.
6. `/api/health` trả `classifier=phobert`, `classifier_error=null`.
7. Mock mode: fresh/old-data repair, booking, persistence/F5 và UI admin đều chạy; phim 5 có lịch.

Browser mock 375×812: trang admin có 20 dòng của 9 phim, `scrollWidth=360 <= innerWidth=375`, bảng `overflow-x:auto`, 55 control focusable, reduced motion được nhận.

## 10. AC-01 → AC-07 regression

| AC | Evidence sau fix |
|---|---|
| AC-01 | 4 endpoint admin: anonymous `401`, user `403`. |
| AC-02 | Cùng phòng tại `duration + 14` → `409`; đúng `duration + 15` → `201`. |
| AC-03 | Cùng giờ khác phòng → `201`. |
| AC-04 | Suất có 2 vé: PUT/DELETE → `409`, câu lỗi chứa đúng `2 vé`. |
| AC-05 | Mục 8 và 9: restart/idempotency, 0 chồng, không mất dữ liệu. |
| AC-06 | Tạo phim mới → tạo suất → public showtimes → booking đều `201`. |
| AC-07 | Mock dùng thuật toán tương đương; số phân bổ bằng real; persistence và old-data repair đạt. |

## 11. Focused tests

- Backend fresh lifespan: đếm suất theo 9 phim và từng ngày; hot_week; duyệt tất cả cặp suất theo phòng.
- Backend restart: so sánh tuple toàn bộ Showtime ID, tổng Booking/BookingSeat qua ba lifespan; hai Uvicorn startup bổ sung.
- Backend old-data/new-day: giữ bốn suất cũ + booking, chạy `days=6`, xác minh đủ 9 phim và 0 chồng.
- Real API: 401/403, 409 chồng, biên +15, khác phòng, khóa 2 vé, phim mới/showtime/booking.
- Mock Vite SSR: bảng real/mock bằng nhau, 0 chồng, hot_week 9, F5 persistence, repair DB cũ và idempotency.
- Browser headless mock: poster, auth redirect, phim 5 có lịch, admin 9 phim, responsive/focus/reduced motion.

## 12. Final gates

| Gate | Kết quả |
|---|---|
| Backend compileall | Exit 0 |
| Backend startup | Uvicorn thật startup complete, chạy hai lượt trên DB tạm |
| Health | `200`, `classifier=phobert`, không classifier error |
| Frontend build | Vite build thành công, 69 modules |
| Real API | AC-01→AC-06 probes đạt |
| Mock mode | Seed/API/persistence/browser probes đạt |
| Chồng giờ | 0 cặp trên fresh DB, restart DB, old-data day và mock |
| Schema/library | Không đổi schema, không thêm thư viện |

## 13. Security

- Không thay đổi auth/permission hoặc endpoint admin.
- 401/403 của cả bốn endpoint vẫn đúng.
- Không sửa `.env`, database thật, model, classifier, `normalize()` hay seat rules.
- Mọi SQLite probe là file tạm và đã xóa; `backend/firefly.db` không được dùng hoặc sửa.

## 14. Scope integrity

- Diff production của Fix Round 1 so với review FAIL chỉ có `backend/app/seed.py` và `frontend/src/api/mock.js`, đúng RF-01.
- Diff `seed.py` chỉ nằm trong `_ensure_showtimes()`.
- `git diff master...HEAD` gồm các file implementation T05 trong allowlist, report Codex/coordination, và review FAIL của Claude (`claude_review_T05_FAIL_2026-10-08.md`) đã được commit bởi reviewer theo workflow.
- Không có `.env`, `*.db`, model, CSV/dữ liệu lớn hoặc secret trong diff.

## 15. Remaining Required Fixes

- 0 theo self-check của Codex. Chờ Claude review độc lập; Codex không tự kết luận task PASS.

## 16. Scope conflict chưa giải quyết

Phim `ended` vẫn có thể bị đặt vé bằng cách gọi trực tiếp endpoint booking. Trạng thái: **OPEN / PO ACTION REQUIRED**.

Theo chỉ thị Fix Round 1, không sửa `backend/app/routers/bookings.py`, không sửa `backend/app/routers/movies.py`, không mở rộng allowlist. UI vẫn ẩn lịch phim ended và T05 vẫn chặn tạo/cập nhật suất cho phim ended.
