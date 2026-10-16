# Claude Review — T12 — FAIL — 16/10/2026

- Nhánh: `task/T12-demo`, commit `23df507` (1 commit trên `master` `daa530b`).
- Report Codex: `reports/2026-10-16/codex_implementation_T12_2026-10-16.md` (bằng chứng phụ).
- Mọi probe chạy trên SQLite tạm trong scratchpad của Claude; không chạm `backend/firefly.db`.

## 1. Scope

`git diff --stat master...task/T12-demo`: 9 file, tất cả trong Allowed Files của T12.md (`demo_comments.json`, `seed.py`, `reset_demo.py`, `reset-demo.bat`, `chay-firefly.bat`, `KICH_BAN_DEMO.md`, `mock.js`, report Codex, file điều phối). Không sửa `classifier.py`, `models.py`, giao diện; không thêm thư viện; không đổi schema. Không có `.env`, `*.db`, `backup\`, model trong commit. Không có đường dẫn `D:\`.

## 2. Gate độc lập

| Gate | Kết quả |
|---|---|
| `compileall -q backend/app backend/scripts` | exit 0 |
| `npm run build` (real) | đạt |
| `reset_demo.py` 2 lần liên tiếp (DB tạm) | exit 0 cả hai; wall 15 s / 23 s (gồm nạp model); seed 3,91 s / 3,96 s; cả hai: phim 21, suất 99, vé 143, bình luận 30, model tiêu cực 16, đã duyệt 8; vé expired 1 / paid 141 / pending_verify 1 |
| Bình luận | 6 phim, 17 ngày lịch khác nhau, 8 đã duyệt, 2 ca model sai (đều là câu châm biếm model B chấm bình thường, admin gán tiêu cực) |
| Vé của `demo@firefly.vn` | paid (A1, A2), pending_verify (A3, A4), expired (0 ghế, tổng 0) |
| `DATABASE_URL=postgresql://…` | từ chối bằng tiếng Việt, exit 2 |
| Backend trên DB tạm, `/api/health` | `classifier=phobert_b`, `classifier_error=null` |
| `POST /api/admin/predict` câu "Phim dài lê thê, nửa đầu buồn ngủ thật sự." | A `binh_thuong 0,0485`, B `tieu_cuc 0,999` (SVM/LR/NB đều tiêu cực) — khớp report Codex |
| `/api/admin/comments/stats` | reviewed 8, agree 6, disagree 2 |
| `demo@firefly.vn` / `123456` | đăng nhập 200 |
| Nhãn giao diện trong kịch bản | đều có thật: "Giữ chỗ – chưa thanh toán", "Xác nhận nhãn", "Đổi sang bình thường", "Model sai", "Đã duyệt", "Vẫn xem", "Chờ xác nhận chuyển khoản" |
| pytest (`--basetemp` trong scratchpad) | 81 passed, 1 warning thư viện, 45 s |

## 3. Acceptance Criteria

| AC | Kết quả | Ghi chú |
|---|---|---|
| AC-01 reset < 1 phút, 2 lần cùng kết quả | PASS | Xem gate. Riêng trường hợp chạy khi backend đang mở: xem RF-02 |
| AC-02 PO chạy kịch bản 2 lần | PENDING PO | Việc của Tín ở PO review |
| AC-03 ≤ 7 phút, kết quả kiểm được | PASS | 6:30; nhãn giao diện đã đối chiếu |
| AC-04 dự phòng mock mode | PASS | Có mục mất mạng và model lỗi → `VITE_USE_MOCK=true` |
| AC-05 pytest + hồi quy | PASS | pytest 81/81; luồng hồi quy qua API thật trên DB tạm (phim, đăng nhập, bình luận, kiểm duyệt, so sánh model, health) + build |

## 4. Required Fix

### RF-01 — Medium — đổi quyết định mật khẩu admin dev mà không có phê duyệt
- **File:** `backend/app/seed.py` (dòng `admin_password = ADMIN_PASSWORD or secrets.token_urlsafe(24)`), `HUONG_DAN.md`.
- **Problem:** T20.md mục 3 đã chốt: thiếu `ADMIN_PASSWORD` thì giữ `admin123` cho máy dev và ghi cảnh báo. Codex đổi sang mật khẩu ngẫu nhiên. Việc này nằm ngoài yêu cầu T12, không được nêu là deviation trong report, và `HUONG_DAN.md` (thuộc allowlist) vẫn ghi `admin123` và "nếu để trống, dữ liệu dev vẫn dùng admin123".
- **Evidence:** `git diff master...task/T12-demo -- backend/app/seed.py`; `docs/tasks/T20.md:27`; `HUONG_DAN.md:56`, `HUONG_DAN.md:96`.
- **Expected Fix:** khôi phục fallback `admin123` + cảnh báo như T20 đã chốt (`reset_demo.py` vẫn bắt buộc `ADMIN_PASSWORD` như hiện tại, giữ được). Nếu Codex cho rằng nên bỏ `admin123` thì nêu trong report để PO quyết định, không tự đổi.

### RF-02 — Medium — reset khi backend đang chạy: lỗi traceback tiếng Anh và mất sidecar
- **File:** `backend/scripts/reset_demo.py` (khối `try` trong `main()`), `docs/KICH_BAN_DEMO.md`.
- **Problem:** trên Windows, uvicorn giữ file SQLite. Script xóa `*.showtime-seed.json` trước, rồi `database_path.unlink()` ném `PermissionError`. Trong `except`, lệnh `unlink` lặp lại ném lỗi lần nữa nên bước phục hồi sidecar không chạy. Kết quả: DB cũ còn nguyên nhưng sidecar bị xóa (chỉ còn trong `backup\`), người dùng thấy traceback tiếng Anh. `PRAGMA wal_checkpoint` không phát hiện được vì DB không ở chế độ WAL. AC-02 yêu cầu chạy kịch bản 2 lần liên tiếp, nên khả năng Tín bấm `reset-demo.bat` khi `chay-firefly.bat` còn mở là cao.
- **Evidence:** probe Claude: backend trên DB tạm cổng 8010 → `reset_demo.py` → `PermissionError: [WinError 32] … demo.db`; sau đó thư mục chỉ còn `demo.db`, sidecar mất; bản sao `backup\demo.db.showtime-seed.json-20261016-155555-261630.bak`.
- **Expected Fix:** kiểm tra file DB có bị khóa hay không **trước khi xóa bất cứ thứ gì** (ví dụ thử `os.replace` DB sang tên tạm rồi mới xóa sidecar); nếu bị khóa thì dừng với một câu tiếng Việt kiểu "Hãy tắt backend trước khi đặt lại dữ liệu demo", exit khác 0, không xóa gì. Bước phục hồi trong `except` không được tự ném lỗi trước khi khôi phục sidecar. Kịch bản ghi rõ: tắt cửa sổ Backend trước khi chạy lại `reset-demo.bat`. Thêm một test nhỏ cho ca bị khóa nếu làm được trên Windows.

## 5. TODO (không chặn)

- **TODO-01 — Medium — PO quyết định:** model B chấm tiêu cực nhiều câu khen trên chính phim mở đầu kịch bản (phim 1: "Diễn xuất tự nhiên…" 0,825; "Nhạc nền vừa đủ…" 0,998; "Phần hình ảnh rất thơ…" 0,997) → 4/5 bình luận phim 1 bị che khi hội đồng xem. Phim 3 và 9 cũng có câu khen kèm chê nhẹ bị che. Đây là hành vi thật của model, nhưng cần chọn: (a) cho admin duyệt sẵn vài câu này (thêm ca "Model sai"), (b) đổi phim mở đầu, hoặc (c) giữ nguyên và chuẩn bị câu giải thích trong kịch bản.
- **TODO-02 — Low:** `review: "confirm"/"opposite"` tính theo đầu ra model lúc seed. Với model B hiện tại kết quả đúng (2 ca "opposite" là câu châm biếm model chấm sai). Nếu đổi model active, nhãn admin có thể thành sai. Nên ghi nhãn người duyệt tuyệt đối (`human_label: 0/1`) trong `demo_comments.json`.
- **TODO-03 — Low:** bước 2 kịch bản gõ lại đúng câu "Phim dài lê thê… phí tiền vé." đã có sẵn trong seed của phim 1; ở bước 3 admin dễ thao tác nhầm bình luận cũ. Nên dùng một câu tiêu cực khác hoặc ghi "chọn bình luận mới nhất".

## 6. Kết luận

**FAIL** — RF-01, RF-02 (Medium). T12 `CLAUDE_REVIEW → FIX_LOOP`. Phần còn lại tốt: scope sạch, reset tái lập, câu "lê thê" xác nhận bằng model thật, kịch bản khớp giao diện.

**Prompt Fix Round 1 cho Codex:**

```text
Bạn là Codex. T12 Fix Round 1 trên nhánh task/T12-demo.
Đọc: reports/2026-10-16/claude_review_T12_FAIL_2026-10-16.md, docs/tasks/T12.md, docs/tasks/T20.md (mục 3),
backend/app/seed.py, backend/scripts/reset_demo.py, docs/KICH_BAN_DEMO.md, HUONG_DAN.md.
Sửa đúng RF-01 và RF-02 theo Expected Fix, chỉ trong Allowed Files của T12.md.
- RF-01: khôi phục fallback admin123 + cảnh báo log như T20 đã chốt; reset_demo.py vẫn bắt buộc ADMIN_PASSWORD.
- RF-02: phát hiện DB bị khóa trước khi xóa bất cứ file nào, báo tiếng Việt, exit khác 0, không mất sidecar;
  phục hồi trong except không được tự ném lỗi; kịch bản ghi rõ tắt Backend trước khi reset lại.
TODO-01..03 không bắt buộc; nếu làm TODO-02/03 thì ghi rõ trong report.
Probe ca bị khóa: bật uvicorn trên SQLite tạm rồi chạy reset_demo, dán đầu ra.
Chạy lại gate (compileall, reset 2 lần trên SQLite tạm, health, pytest, npm run build, mock mode).
KHÔNG chạy reset trên backend/firefly.db thật. Không thêm thư viện, không đổi schema.
Tạo reports/<YYYY-MM-DD>/codex_fix_T12_round1_<YYYY-MM-DD>.md. Cập nhật điều phối FIX_LOOP -> CLAUDE_REVIEW.
Commit "[T12] Fix RF-01 RF-02 ...". Không tự review, không tự PASS. Trả lời bằng tiếng Việt.
```
