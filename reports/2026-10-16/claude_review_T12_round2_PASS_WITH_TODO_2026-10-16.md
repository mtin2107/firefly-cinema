# Claude Review — T12 — Round 2 — PASS_WITH_TODO — 16/10/2026

- Nhánh: `task/T12-demo`, tip `1ca55f9` ("[T12] Fix RF-01 RF-02 an toàn reset demo").
- Vòng trước: `reports/2026-10-16/claude_review_T12_FAIL_2026-10-16.md` (RF-01, RF-02 Medium).
- Report Codex: `reports/2026-10-16/codex_fix_T12_round1_2026-10-16.md` (bằng chứng phụ).
- Mọi probe trên SQLite tạm trong scratchpad của Claude; không chạm `backend/firefly.db`.

## 1. Scope của bản fix

`git diff --stat 23df507 1ca55f9`: `backend/app/seed.py` (+2/−2), `backend/scripts/reset_demo.py` (+92), `docs/KICH_BAN_DEMO.md` (+1), file điều phối, report fix. Đều trong Allowed Files. Không đổi schema, không thêm thư viện, không sửa test cũ. `HUONG_DAN.md` không cần sửa vì đã khớp lại hành vi `admin123`.

## 2. Xác minh RF

### RF-01 — CLOSED / VERIFIED BY CLAUDE
- `seed.py`: `ADMIN_PASSWORD or "admin123"` + cảnh báo log, khớp T20.md mục 3.
- Probe: DB mới, `ADMIN_PASSWORD=""` → log `WARNING ... đang dùng mật khẩu admin mặc định cho máy dev`, `verify_password("admin123")` = `True`.
- `reset_demo.py` vẫn bắt buộc `ADMIN_PASSWORD`: chạy với biến rỗng → "Chưa cấu hình ADMIN_PASSWORD…", exit 2, không tạo DB.

### RF-02 — CLOSED / VERIFIED BY CLAUDE
- `ensure_database_unlocked()` thử `os.replace` DB sang file probe rồi đổi lại, chạy **trước** backup, import seed và mọi thao tác xóa. Thứ tự xóa trong `try` đổi thành DB trước, sidecar sau. `restore_after_failure()` gom lỗi từng bước, không ném lỗi giữa chừng.
- Probe 1: uvicorn cổng 8010 giữ DB tạm, health 200 → `reset_demo.py` → `LỖI: Database đang được Backend sử dụng. Hãy tắt Backend trước khi đặt lại dữ liệu demo.`, exit 2, trong 0 s; sha256 của DB và sidecar không đổi; không tạo thêm bản sao lưu.
- Probe 2: cùng tình huống qua `reset-demo.bat` → câu lỗi trên + "Dat lai du lieu demo that bai.", exit 1.
- Probe 3: tắt backend, chạy lại `reset-demo.bat` → thành công, exit 0, kết quả 21/99/143/30, 16 nhãn tiêu cực, 8 đã duyệt, vé expired 1 / paid 141 / pending_verify 1 (giống vòng 1).
- Kịch bản có dòng "Tắt cửa sổ **Backend** cũ trước khi chạy lại `reset-demo.bat`".

## 3. Gate cuối

| Gate | Kết quả |
|---|---|
| `compileall -q backend/app backend/scripts` | exit 0 |
| `npm run build` | đạt |
| pytest đầy đủ (`--basetemp` trong scratchpad) | 81 passed, 1 warning thư viện, 23 s |
| Reset trên DB tạm (sau fix) | 2 lần đạt, cùng kết quả, seed 1,4–1,6 s |

Các phần không đổi so với vòng 1 (A/B câu "lê thê" bằng model thật, health `phobert_b`, nhãn giao diện, mock) giữ kết quả đã ghi ở report vòng 1.

## 4. Acceptance Criteria

| AC | Kết quả |
|---|---|
| AC-01 | PASS |
| AC-02 | PENDING PO — Tín chạy trọn kịch bản 2 lần từ lúc khởi động máy, ghi giờ trong PO report |
| AC-03 | PASS |
| AC-04 | PASS |
| AC-05 | PASS |

## 5. TODO (giữ từ vòng 1, không chặn)

- **TODO-01 — Medium — PO quyết định trước AC-02:** model B chấm tiêu cực nhiều câu khen trên phim mở đầu (phim 1: 4/5 bình luận bị che, trong đó "Diễn xuất tự nhiên…" 0,825, "Nhạc nền vừa đủ…" 0,998). Chọn (a) admin duyệt sẵn các câu này, (b) đổi phim mở đầu, hoặc (c) giữ nguyên và chuẩn bị câu giải thích. Lưu ý cho T21: tỷ lệ tiêu cực phim 1 trên trang Thống kê phụ thuộc lựa chọn này.
- **TODO-02 — Low:** `review: confirm/opposite` tính tương đối theo model lúc seed; nên ghi `human_label` tuyệt đối.
- **TODO-03 — Low:** bước 2 kịch bản gõ trùng câu đã seed trên phim 1.
- **TODO-04 — Low (dọn dẹp, không thuộc Git):** `backup\` còn `T12_gate\`, `T12_fix_round1\`, `T12_reset_run1.txt`, `T12_reset_run2.txt` và vài file `demo-*.db` từ probe của Codex. Không bị commit; Tín có thể xóa.

## 6. Kết luận

**PASS_WITH_TODO.** RF-01, RF-02 CLOSED; RF mở 0; blocker 0. T12 `CLAUDE_REVIEW → PO_REVIEW`.

## 7. Bàn giao task kế tiếp

Theo lộ trình cuối (15/10/2026) `T20 → T12 → T21 → T14 → T13`: **T21** phụ thuộc T20 (CLOSED) và T12 (vừa PASS), không có câu hỏi mở. T21 → `READY_FOR_HANDOFF`.

**Tín làm trước khi gửi prompt:**
1. PO review T12: chạy AC-02 (2 lần, ghi giờ), quyết định TODO-01..04.
2. Commit 2 report review của Claude (FAIL và round 2) cùng file điều phối lên nhánh T12 nếu chưa commit.
3. `git checkout master` → `git merge --no-ff task/T12-demo -m "[T12] Merge demo data and script"`.
4. `git checkout -b task/T21-thong-ke-cam-xuc`.

**Prompt Codex cho T21:**

```text
Bạn là Codex, Primary Implementer của dự án Firefly Cinema.
Chỉ đọc: docs/PROJECT_SOURCE_OF_TRUTH.md, docs/AGENT_RULES.md, docs/TASK_COORDINATION_ACTIVE.md (Snapshot, Status, lộ trình cuối 15/10),
docs/tasks/T21.md, docs/ARCHITECTURE.md (mục endpoint), backend/app/models.py (bảng comments, chỉ đọc),
backend/app/routers/comments.py (chỉ đọc: cách tính effective_negative, dòng ~40; require_admin cho admin comments), backend/app/schemas.py,
frontend/src/api/real.js, frontend/src/api/mock.js, frontend/src/pages/AdminComments.jsx (mẫu trang admin),
frontend/src/App.jsx, frontend/src/components/Header.jsx, và source/test liên quan trực tiếp.

Thực hiện T21 trên nhánh task/T21-thong-ke-cam-xuc (tạo từ master sau khi merge T12), chỉ sửa file trong mục 6 Allowed Files của T21.md.
Thư mục gốc duy nhất: C:\Projects\firefly-cinema.

Yêu cầu chính:
1. GET /api/admin/sentiment?days=30 dùng require_admin; days 1..365, ngoài khoảng → 422 kèm câu tiếng Việt.
   Trả summary / movies / daily đúng mục 3 của T21.md. Nhãn đếm là nhãn hiệu lực (human_label nếu đã duyệt, ngược lại is_negative),
   tính cả bình luận đã ẩn. Tổng hợp bằng SQL GROUP BY, không nạp toàn bộ bình luận vào bộ nhớ.
   daily có đủ đúng `days` ngày (ngày trống = 0), ngày theo giờ địa phương như created_at đang lưu; ghi rõ ngày đầu/cuối được tính thế nào.
   Nhãn hiệu lực phải cùng nghĩa với effective_negative trong routers/comments.py (không sửa file đó).
2. backend/tests/test_sentiment.py với dữ liệu biết trước: 401/403/422, số tổng, số tiêu cực, tỷ lệ theo phim và theo ngày,
   bình luận đã duyệt đổi nhãn được đếm theo human_label, daily đủ số ngày.
3. Trang /quan-tri/thong-ke "Thống kê cảm xúc": 4 ô tóm tắt, thanh ngang tỷ lệ tiêu cực theo phim (bấm tên mở trang chi tiết phim),
   biểu đồ cột theo ngày (tổng và tiêu cực), chọn 7/30/90 ngày cập nhật cả 3 phần, trạng thái rỗng.
   Biểu đồ SVG/CSS thuần trong React, có aria-label và bảng số liệu đi kèm. Màu theo hệ T18, không đổi layout chung.
   Thêm liên kết "Thống kê cảm xúc" trong menu admin.
4. api.admin.sentiment(days) có ở cả real.js và mock.js, cùng cấu trúc JSON; giao diện chỉ import từ src/api/index.js.
   Mock tính từ bộ bình luận mock hiện có (nhãn hiệu lực giống backend), không trả số viết cứng.

Cấm: sửa models.py, classifier.py, routers/comments.py, package.json, requirements*.txt; thêm thư viện; đổi schema;
sửa hoặc commit backend/.env, *.db, backup\, model. Không chạy backend trên backend/firefly.db thật;
kiểm AC-04 bằng DB tạm tạo qua backend/scripts/reset_demo.py với DATABASE_URL trỏ file tạm (cần ADMIN_PASSWORD trong môi trường).
Kiểm AC-05 ở 375px và 1280px, không tràn ngang, không lỗi console.
Chạy gate theo AGENT_RULES.md mục 3: compileall, backend khởi động + health, pytest đầy đủ, npm run build, mock mode, checklist hồi quy 7/7.
Tạo reports/<YYYY-MM-DD>/codex_implementation_T21_<YYYY-MM-DD>.md: ghi "Đổi schema: Không", số liệu trang với dữ liệu demo T12
(đối chiếu với truy vấn SQL độc lập), ảnh chụp hoặc mô tả 375px/1280px, checklist hồi quy.
Cập nhật TASK_COORDINATION_ACTIVE.md: T21 READY_FOR_HANDOFF -> IN_PROGRESS -> CLAUDE_REVIEW; thêm endpoint vào docs/ARCHITECTURE.md.
Commit dạng "[T21] mô tả". Không tự review, không tự PASS, không mở task kế tiếp. Trả lời bằng tiếng Việt.
```
