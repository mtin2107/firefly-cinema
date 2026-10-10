# Codex Fix Report — T10 Round 1 — 10/10/2026

## 1. Trạng thái

- Task: `T10 — Gắn model B vào web`
- Branch: `task/T10-gan-model-B`
- Approved baseline: `38f63eedf3682216c1256cc581811e5ae9e05406`
- Implementation commit: `0e80015630a7275f32719021b0928bac905a56c6`
- Claude Round 1 commit: `509b66326dc094a50493598be1ac596ce2513579`
- Claude Round 1 verdict: **FAIL**
- Required Fix: `RF-01` (Medium)
- RF-01 status sau vòng sửa: **DEV FIXED / PENDING CLAUDE VERIFICATION**
- Fix commit: commit mang message `[T10] Fix concurrent PhoBERT lazy loading race` chứa report này; hash đầy đủ được trả ở handoff sau commit.
- Reviewer tiếp theo: Claude Round 2

## 2. RF-01 và nguyên nhân gốc

`/api/admin/predict` là endpoint đồng bộ nên nhiều request có thể chạy trong threadpool. Trước fix, `PhoBertModel.ensure_loaded()`, `predict()` và `release()` cùng đọc/ghi `_model`, `_tokenizer` và `loaded` mà không có đồng bộ.

Khi model A không active, request X có thể đang inference trong `predict()` trong lúc request Y hoàn tất và gọi `release()`. Y xóa `_model`/`_tokenizer`, làm X ném `AttributeError` và API trả HTTP 500. Hai request cũng có thể cùng đi qua trạng thái `loaded=False` và nạp trùng model không an toàn.

## 3. Chiến lược synchronization

File production duy nhất được sửa: `backend/app/classifier.py`.

- Dòng 67: mỗi `PhoBertModel` có một `threading.RLock` riêng (`_lifecycle_lock`).
- Dòng 102–125: `ensure_loaded()` giữ lock trong toàn bộ kiểm tra trạng thái và quá trình nạp tokenizer/model.
- Dòng 127–134: `release()` giữ cùng lock trước khi xóa tài nguyên và đổi trạng thái.
- Dòng 147–157: `predict()` giữ cùng lock từ lúc bảo đảm model đã nạp đến khi inference và đọc score hoàn tất.
- `admin_predict.py` không cần sửa; `release_if_inactive()` vẫn bảo đảm model active không bị release.

`RLock` được dùng vì `predict()` giữ lock rồi gọi `ensure_loaded()` trên cùng instance. Mỗi luồng chỉ giữ lock của một model tại một thời điểm; không có khóa global hoặc thứ tự lấy nhiều lock, nên không hình thành vòng chờ deadlock. Request release phải chờ inference đang dùng model kết thúc. Request nạp đồng thời được tuần tự hóa; sau khi request đầu nạp xong, request kế tiếp thấy `loaded=True`, nên không có double-load chồng lấn. Model phụ vẫn được giải phóng khi lấy được lock, tức là sau khi không còn inference nào đang giữ tài nguyên.

Không thay đổi tokenizer, checkpoint, preprocessing, threshold, cấu hình mặc định, `normalize()`, `_ABBR`, API response hay `require_admin`.

## 4. Concurrency — B active

Môi trường: uvicorn thật `127.0.0.1:8011`, `ACTIVE_MODEL=phobert_b`, database tạm `backup/T10_2026-10-10/t10_fix_round1_b.db`, admin token thật.

| Probe | Kết quả |
|---|---|
| Bắt buộc, vòng 1 × 6 request song song | 6/6 HTTP 200 |
| Bắt buộc, vòng 2 × 6 request song song | 6/6 HTTP 200 |
| Bắt buộc, vòng 3 × 6 request song song | 6/6 HTTP 200 |
| Stress bổ sung, 50 request / 10 worker | 50/50 HTTP 200 |
| Contract mỗi dòng | Đủ `model`, `version`, `label`, `score`, `ms` |
| Lỗi/treo | 0 HTTP 500; 0 `AttributeError`; 0 timeout; 0 deadlock |
| Health sau probe | B active + loaded; A inactive + released |

Tổng bắt buộc: **18/18 HTTP 200**.

## 5. Concurrency — A active

Tiến trình độc lập: uvicorn thật `127.0.0.1:8012`, `ACTIVE_MODEL=phobert`, database tạm `t10_fix_round1_a.db`.

| Probe | Kết quả |
|---|---|
| Bắt buộc 3 vòng × 6 request song song | 18/18 HTTP 200 |
| Stress bổ sung, 30 request / 10 worker | 30/30 HTTP 200 |
| Lỗi/treo | 0 HTTP 500; 0 `AttributeError`; 0 timeout; 0 deadlock |
| Health sau probe | A active + loaded; B inactive + released |
| Comment sau restart | `phobert`, `A-backend`, score `0.9937` |

## 6. Sequential, fallback và error handling

- Predict A/B tuần tự nhiều lần: PASS; version và score không đổi.
- Câu `Phim dài lê thê, xem mà mệt`: B trả `tieu_cuc`, score `0.9988`.
- B missing qua `MODEL_DIR_B=models/T10-missing-phobert-B`: backend khởi động, fallback A `A-backend`, admin predict HTTP 200.
- B tồn tại nhưng `model.safetensors` hỏng trong scratch ngoài repo: lỗi `Error while deserializing header: header too large`, backend fallback A, admin predict HTTP 200.
- Model phụ A hỏng khi B active: admin predict bỏ qua A lỗi, trả B/SVM/LR/NB HTTP 200; backend không crash.
- Scratch checkpoint hỏng không thay thế hoặc chỉnh sửa checkpoint A/B thật.

## 7. Security

`POST /api/admin/predict`:

- Không token: **401**.
- User thường: **403**.
- Admin: **200**.
- `require_admin` và response contract không đổi.

## 8. Acceptance Criteria sau fix

| AC | Kết quả DEV | Evidence |
|---|---|---|
| AC-01 | PASS | `check_model.py`: 10/10; max Δ `0.000048 ≤ 0.001`. Direct movie test 149 câu: F1 negative `0.917525773196`, Macro-F1 `0.881839809675`, khớp T09 |
| AC-02 | PASS | Câu bắt buộc B score `0.9988`, nhãn tiêu cực |
| AC-03 | PASS | Health đúng active model, version và loaded state ở cả B-active/A-active |
| AC-04 | PASS | DB tạm persist `phobert_b`, `phobert-B-2026-10-09`, `0.9988` |
| AC-05 | PASS | Restart tiến trình với `ACTIVE_MODEL=phobert`; health A, comment persist A/version/score `0.9937` |
| AC-06 | PASS | B missing và B checkpoint hỏng đều fallback A, không crash |
| AC-07 | PASS | Hồi quy real API 6 mục + mock runtime mục 7; frontend build real/mock PASS |

**AC PASSED / TOTAL: 7/7 (DEV; chờ Claude Round 2).**

## 9. Hồi quy real/mock 7/7

1. Real API: danh sách phim đang chiếu có 9 phim; mở chi tiết phim PASS.
2. Real API: thể loại Kinh dị trả 2 phim; tìm `meo muop` thấy `Mèo Mướp Đi Lạc`.
3. Real API: đăng ký + `/auth/me` PASS; đặt vé không token trả 401.
4. Real API: đặt A1/A2, vé xuất hiện trong `/bookings/me`, sơ đồ suất chiếu ghi nhận hai ghế.
5. Real API: comment `Ko hay như quảng cáo, hơi thất vọng` score `0.9992`; admin thấy `phobert_b` + `phobert-B-2026-10-09`.
6. Real API: health báo active `phobert_b`, version `phobert-B-2026-10-09`.
7. Mock runtime qua Vite SSR: predict trả một dòng B/version `phobert-B-2026-10-09-mock`; comment cũ thiếu version được migrate thành `null`; frontend mock build PASS.

Kết quả: **7/7 PASS**. Fix không sửa frontend hoặc lớp API.

## 10. Quality gates

| Gate | Kết quả |
|---|---|
| Backend `compileall` app + scripts | PASS |
| Uvicorn thật + health | PASS |
| Concurrency B active | PASS, 18/18 bắt buộc + 50/50 stress |
| Concurrency A active | PASS, 18/18 bắt buộc + 30/30 stress |
| `check_model.py --model phobert_b` | PASS, 10/10, max Δ `0.000048` |
| Direct movie test 149 câu | PASS, metric khớp T09 |
| Frontend build real | PASS, 70 modules |
| Frontend build mock | PASS, 70 modules |
| Real/mock regression | PASS, 7/7 |
| Admin authorization | PASS, 401/403/200 |
| `git diff --check` | PASS |

## 11. Database safety

- Chỉ dùng database tạm cho mọi test ghi dữ liệu.
- DB thật `backend/firefly.db` chỉ được đọc để kiểm tra integrity/checksum/schema.
- SHA-256 DB thật trước và sau test: `ED3ABDBAD7FF65F74D2182DC8B5C757E8FC32EDF37DCAF4073EAC1D375E70D0A`.
- SHA-256 backup `backup/T10_2026-10-10/firefly_before_T10.db`: cùng giá trị trên.
- `PRAGMA integrity_check` DB thật: `ok`.
- DB thật vẫn thiếu `comments.model_version`; không reset, migrate, xóa hoặc ghi đè DB thật/backup.

`REAL_DB_SCHEMA_READINESS = PENDING_PO_ACTION`

TODO-01 giữ nguyên **PO ACTION REQUIRED** theo Q2 trước khi chạy/demo trên DB thật.

## 12. Scope, secret và large-file gates

- Production diff Round 1 chỉ có `backend/app/classifier.py`.
- Tài liệu chỉ có coordination và report fix này.
- `backend/app/routers/admin_predict.py` không cần thay đổi.
- Không sửa Task Record, PO docs, `.env`, database thật, checkpoint, `normalize()` hoặc `_ABBR`.
- Không thêm dependency, model, database, CSV lớn hoặc secret vào Git.
- Probe DB/checkpoint hỏng là tạm thời và được dọn sau kiểm thử.

## 13. Required Fixes, blockers và TODO

- RF-01: **DEV FIXED / PENDING CLAUDE VERIFICATION**.
- Open Required Fixes phía DEV: **0**.
- Blockers: **0**.
- TODO-01: DB thật thiếu schema mới — **PO ACTION REQUIRED**, không xử lý trong fix loop.
- Các TODO Claude Round 1 khác giữ nguyên disposition; không mở rộng scope.
- T11 giữ `PLANNED / NOT AUTHORIZED`.

## 14. Definition of Done và handoff

- RF-01 được sửa đúng allowlist: MET.
- Concurrency hai chiều và error/fallback: MET.
- AC 7/7 + quality gates sau fix: MET ở phía DEV.
- Database safety: MET; real DB readiness vẫn pending PO.
- Report + coordination: MET.
- Claude verification: PENDING.

T10 chuyển `FIX_LOOP → CLAUDE_REVIEW / ROUND_2_PENDING`. Codex không approve, merge, tag `phobert-B`, đóng T10 hoặc mở T11.

---

T10 STATUS: CLAUDE_REVIEW / ROUND_2_PENDING

CLAUDE ROUND 1 VERDICT: FAIL

RF-01 STATUS: DEV FIXED / PENDING CLAUDE VERIFICATION

CONCURRENCY B ACTIVE: 18/18 bắt buộc + 50/50 stress HTTP 200

CONCURRENCY A ACTIVE: 18/18 bắt buộc + 30/30 stress HTTP 200

AC PASSED / TOTAL: 7/7 DEV

REGRESSION: 7/7 PASS; real/mock build PASS

DATABASE REAL READINESS: PENDING_PO_ACTION

REQUIRED FIXES: 0 phía DEV; chờ Claude Round 2

BLOCKERS: 0

FIX COMMIT: `[T10] Fix concurrent PhoBERT lazy loading race` (commit chứa report này)

NEXT STEP: Claude Independent Review Round 2
