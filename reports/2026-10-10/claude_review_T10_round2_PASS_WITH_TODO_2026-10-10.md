# Claude Independent Review — T10 — Round 2 — 10/10/2026

**Kết luận: PASS_WITH_TODO** — `RF-01 = CLOSED / VERIFIED BY CLAUDE`. AC 7/7, không còn Required Fix. DB thật vẫn cần Tín xử lý (`REAL_DB_SCHEMA_READINESS = PENDING_PO_ACTION`).

## 1. Branch, baseline, fix commit, review HEAD

| Trường | Giá trị |
|---|---|
| Branch | `task/T10-gan-model-B` |
| Approved baseline | `38f63ee` |
| Implementation | `0e80015` |
| Claude Round 1 | `509b663` — FAIL, RF-01 Medium |
| Fix commit | `ed26454` — `[T10] Fix concurrent PhoBERT lazy loading race` (thuộc HEAD; gồm `classifier.py`, fix report, coordination) |
| Review HEAD | `ed26454` |

Working tree sạch trước review; `git diff --check 38f63ee...HEAD` PASS.

## 2. Source review và scope

- File production duy nhất sửa trong vòng fix: `backend/app/classifier.py` (allowlist). `frontend/`, `ml/test_sentences.json`, `backend/scripts/check_model.py` **không đổi** kể từ `0e80015`/`509b663`.
- Toàn nhánh: không có `.env`, `*.db`, checkpoint, ZIP, CSV trong diff. `normalize()`/`_ABBR` không đổi.

## 3. RF-01 — đối chiếu code path

Fix thêm `self._lifecycle_lock = threading.RLock()` cho **từng** `PhoBertModel` (thuộc tính instance → A và B có lock riêng).

| Yêu cầu | Đối chiếu | Kết quả |
|---|---|---|
| Không double-load | `ensure_loaded()` kiểm `loaded`/`available` và nạp tokenizer + model **bên trong** lock; luồng thứ hai chờ rồi thấy `loaded=True` | Đạt |
| Bảo vệ suốt inference | `predict()` giữ lock từ `ensure_loaded()` qua tokenizer, forward, softmax đến `return` | Đạt |
| Release không xóa model đang chạy | `release()` lấy cùng lock trước `del _model/_tokenizer` → phải chờ inference xong | Đạt |
| Model active không bị release | `ModelRegistry.release_if_inactive()` giữ điều kiện `model is not self.active` (không đổi) | Đạt |
| Model phụ được release sau inference | `admin_predict.py` `finally: release_if_inactive` (không đổi); health sau tải thấy model phụ `loaded=false` | Đạt |
| Deadlock / lock-order | Mỗi luồng chỉ giữ lock của **một** model; `predict → ensure_loaded` reentrant nhờ `RLock`; không có lock global hay lấy 2 lock lồng nhau | Không có vòng chờ |
| `loaded` sai | `loaded` chỉ đổi trong lock; lỗi nạp đặt `available=False`, `error` | Đạt |
| Exception | Load lỗi → `RuntimeError` (admin predict bỏ qua model phụ); không thêm catch-all, không nuốt lỗi khác | Đạt |
| Contract model | Tokenizer, `max_length`, `normalize`, threshold, weights không đổi | Đạt |

Đánh đổi (TODO-07): vì lock bao cả inference, các request dùng **cùng** model chạy tuần tự (kể cả model active khi nhiều người bình luận cùng lúc), và model phụ bị nạp lại ở mỗi request admin (~0,6–0,8 s). Đúng về logic, chấp nhận được ở quy mô khóa luận.

## 4. Concurrency — B active

Uvicorn thật cổng 8011, `ACTIVE_MODEL=phobert_b`, DB tạm, admin token thật. Mỗi response được kiểm: HTTP 200, đủ 5 trường `model/version/label/score/ms`, có cả `phobert` và `phobert_b`, A = `A-backend binh_thuong 0.0125`, B = `phobert-B-2026-10-09 tieu_cuc 0.9988`.

| Probe | Kết quả |
|---|---|
| 3 vòng × 6 request đồng thời | **18/18** đúng (2,3 s / 2,7 s / 1,9 s) |
| Stress 50 request, 10 worker | **50/50** đúng, 21,9 s, không timeout |
| Health sau stress | B `loaded, active`; A `available, loaded=false` |
| 3 request tuần tự sau stress | 3/3 đúng; health không đổi |
| Comment công khai sau stress | 201, DB `('phobert_b','phobert-B-2026-10-09',0.9988,1)` |
| Trộn 4 comment + 4 predict đồng thời | 4×201, 4×200 |
| Log uvicorn | 0 dòng `500`, 0 `Traceback`, 0 `AttributeError` |
| Nạp lại A sau release | Log có 36 lần "Loaded phobert" (1 B lúc khởi động + nạp lại A mỗi request) — reload hoạt động |

## 5. Concurrency — A active

Tiến trình riêng, `ACTIVE_MODEL=phobert`:

| Probe | Kết quả |
|---|---|
| Health đầu | `phobert / A-backend`, A `loaded, active`, B `available, loaded=false` |
| 3 vòng × 6 | **18/18** đúng |
| Stress 30 request, 10 worker | **30/30** đúng, 13,8 s |
| Health sau stress / tuần tự | A vẫn `loaded, active`; B `loaded=false` (đã release); 3/3 tuần tự đúng |
| Comment "Ko hay như quảng cáo, hơi thất vọng" | 201, DB `('phobert','A-backend',0.9937,1)` |
| Trộn comment + predict | 4×201, 4×200 |
| Log | 0 `500`, 0 `Traceback`, 0 `AttributeError` |

## 6. Stress và log

Tổng cộng 116 request admin predict đồng thời (18+50+18+30) và 8 request trộn: **0 lỗi**. So với Round 1: cùng probe 3×6 khi đó có 4/6 lỗi 500 `AttributeError`.

## 7. Sequential / fallback

| Kịch bản | Kết quả |
|---|---|
| B thiếu (`MODEL_DIR_B=models/T10-claude-r2-missing-B`) | Không crash; active `phobert/A-backend`; `classifier_error` báo thiếu thư mục; B `available=false`; comment lưu A; 12 predict đồng thời 12/12 (A + 3 sklearn) |
| B checkpoint hỏng (bản sao scratch, `model.safetensors` rác) | Active A; B `available=false`, lỗi deserialize; comment lưu A; 12/12 |
| A (model phụ) hỏng khi B active | 12 predict đồng thời 12/12, A bị bỏ qua an toàn; health A `available=false` kèm lỗi; B vẫn active |
| Artifact thật | Không bị đụng (`model.safetensors` B vẫn `0b80947c…`) |

## 8. Security

401 (không token) / 403 (user thường, câu tiếng Việt) / 200 (admin) ở **cả 5** tiến trình (B, A, missing-B, broken-B, broken-A). `require_admin` trong `admin_predict.py` không đổi.

## 9. AC-01 → AC-07

| AC | Kết quả | Bằng chứng Round 2 |
|---|---|---|
| AC-01 | **PASS** | `check_model.py --model phobert_b`: `PARITY=10/10 MAX_ABS_DELTA=0.000048`, exit 0. Baseline không đổi kể từ `0e80015`. Reference Transformers độc lập (artifact gốc, normalize `ml/src`): 10/10, Δ 0 với JSON. Movie test 149 (SHA `5af8f616…`, 48/101): F1_neg `0.917525773196`, Macro-F1 `0.881839809675`, lệch T09 ≈ 1e-13 |
| AC-02 | **PASS** | "Phim dài lê thê, xem mà mệt" → comment thật `is_negative=1`, `0.9988` |
| AC-03 | **PASS** | Health đúng `active_model`/`active_version`, version từng model, cờ `active` đúng cả khi fallback |
| AC-04 | **PASS (DB tạm)** | Comment lưu đúng name/version với B và A; UI kiểm duyệt hiện `phobert_b · phobert-B-2026-10-09` |
| AC-05 | **PASS** | `ACTIVE_MODEL=phobert` + tiến trình mới → A, score 0,9937 |
| AC-06 | **PASS** | Thiếu B / B hỏng → A |
| AC-07 | **PASS** | Mục 10 |

**AC PASSED / TOTAL: 7/7.**

## 10. Real / mock / regression

Gate: `compileall backend/app backend/scripts` PASS; frontend build real PASS, build mock PASS.

Phạm vi kiểm thử hồi quy Round 2 (frontend không đổi kể từ Round 1, nơi đã chạy browser E2E đủ 7/7):

| # | Mục | Round 2 |
|---|---|---|
| 1 | Trang chủ / trang phim | Browser: trang phim render, lịch chiếu có dữ liệu |
| 2 | Tìm "meo muop" | API: `GET /api/movies?q=meo muop` → `Mèo Mướp Đi Lạc` (browser đã kiểm ở Round 1) |
| 3 | Đăng ký; chưa đăng nhập bấm giờ chiếu → đăng nhập → quay lại | Browser: 22:00 → `/dang-nhap` → đăng nhập → `/dat-ve/20`. API: đăng ký 201 |
| 4 | Đặt 2 ghế | Browser: C1, C2 → mã vé, "Vé của tôi"; mở lại suất thấy C1/C2 đã đặt, disabled. API: đặt khi chưa đăng nhập 401, đặt B1/B2 201 |
| 5 | Bình luận tiêu cực bị ẩn; admin thấy ~0,99 | Browser: thông báo ẩn; admin thấy `1.00 · phobert_b · phobert-B-2026-10-09` |
| 6 | Health | `classifier: phobert_b` (theo Q3) |
| 7 | Mock | Browser dev server `VITE_USE_MOCK=true`: kiểm duyệt hiện `phobert_b · …-mock`, 0 request tới :8000 |

Thêm: trang So sánh mô hình trên browser, bấm đúp "Chấm điểm" → 1 POST 200, bảng 5 model đủ version. Mobile không kiểm lại ở Round 2 (giao diện không đổi; Round 1 đã PASS).

## 11. Database thật và PO action

Đọc chỉ-đọc `backend/firefly.db`: SHA-256 `ed3abdba…0d0a` (giống Round 1), `integrity_check ok`, **chưa có** `comments.model_version`. Claude không ghi, migrate hay reset DB thật, không đụng `backup/`.

- Code: PASS trên DB tạm.
- DB thật: **`REAL_DB_SCHEMA_READINESS = PENDING_PO_ACTION`**. Round 1 đã chứng minh trên bản sao DB thật: bình luận và kiểm duyệt trả 500 `no such column`. Merge rồi chạy/demo với DB hiện tại sẽ hỏng phần bình luận cho tới khi Tín backup + reset theo `HUONG_DAN.md` 2.1 (Q2).

## 12. Required Fixes

| RF | Trạng thái |
|---|---|
| RF-01 (Medium) race lazy-load/release | **CLOSED / VERIFIED BY CLAUDE** — source (mục 3) + 116 request đồng thời hai chiều, 0 lỗi |

Required Fix mới: **0**.

## 13. TODO — đề xuất disposition

| ID | Severity | Nội dung | Trạng thái / đề xuất |
|---|---|---|---|
| TODO-01 | High (vận hành) | DB thật thiếu `comments.model_version` | Còn mở — **PO ACTION REQUIRED** trước khi chạy/demo trên DB thật |
| TODO-02 | Low | `check_model.py` so score đã làm tròn 4 chữ số | ACCEPT_WITH_NOTES |
| TODO-03 | Low | `CLAUDE.md`, `BOI_CANH_DU_AN.md` mục 7 còn ghi health `phobert` | PO cập nhật tài liệu PO-owned |
| TODO-04 | Info | `T10.md` ghi `IN_PROGRESS` | ACCEPT_WITH_NOTES |
| TODO-05 | Info | Mock gắn nhãn `phobert_b` nhưng điểm từ keyword | ACCEPT |
| TODO-06 | Info | T07 TODO-05 nay đã có `active`/`active_version`/`classifier_error` | PO có thể đánh dấu RESOLVED |
| TODO-07 (mới) | Low | Lock bao cả inference → request cùng model chạy tuần tự; model phụ nạp lại ở mỗi request admin (~0,6–0,8 s) | ACCEPT_WITH_NOTES — đúng logic, đủ cho demo; tối ưu nếu sau này cần tải cao |

## 14. Definition of Done

| Mục | Trạng thái |
|---|---|
| Code đúng allowlist | MET |
| AC 7/7 | MET |
| Gate web (compileall, startup/health, build real/mock, mock, hồi quy, scope, secret, diff-check) | MET |
| `check_model.py` | MET |
| Không còn Required Fix | MET |
| Report + coordination | MET |
| DB thật sẵn sàng | Ngoài DoD code — PO ACTION (TODO-01) |

## 15. Temporary probes

Tạo trong scratchpad (ngoài repo): `r2_live.py` (uvicorn đa kịch bản, concurrency, stress, fallback, security, API regression), `r2_ref.py` (reference + movie test), DB tạm `r2_*.db`, thư mục `brokenA`/`brokenB`, log uvicorn; thêm tạm 2 cấu hình vào `.claude/launch.json` (local, bị ignore). Đã xóa toàn bộ scratchpad, khôi phục `launch.json`, dừng mọi server (8000/8011/5173/5174 không còn lắng nghe). `git status` sạch trước commit.

**Temporary Probes Remaining = 0.**

## 16. Final verdict

**T10 Round 2: PASS_WITH_TODO.** `RF-01 = CLOSED / VERIFIED BY CLAUDE`. Coordination: `CLAUDE_REVIEW → PO_REVIEW`.

- Không merge, không gắn tag `phobert-B`, không approve/close T10.
- **T11 giữ `PLANNED / NOT AUTHORIZED`** theo chỉ đạo PO hiện hành. Ghi nhận xung đột: `AGENT_RULES.md` mục 1.1 cho phép Claude đặt task kế tiếp (T11) sang `READY_FOR_HANDOFF` khi PASS, nhưng coordination do PO giữ ghi T11 NOT AUTHORIZED. Claude **không** chuyển T11, không tạo nhánh; PO quyết định.
- Việc PO: (1) PO review T10; (2) xử lý TODO-01 (backup + reset DB thật) trước khi chạy/demo trên DB thật; (3) disposition TODO-02 → 07; (4) nếu APPROVED: merge vào `master`, gắn `phobert-B`, rồi quyết định có authorize T11 hay không.

### Đề xuất bàn giao (chỉ để PO tham khảo, chưa được authorize)

Nếu PO authorize T11 sau khi merge T10, tạo nhánh `task/T11-...` từ `master` đã merge rồi gửi ChatGPT/Codex `docs/tasks/T11.md` + `docs/TASK_COORDINATION_ACTIVE.md` với prompt dạng: "Bạn là Codex của Firefly Cinema. Thực hiện T11 theo đúng Task Record, chỉ sửa file trong allowlist, chạy gate web + pytest, viết `codex_implementation_T11_*`, chuyển `CLAUDE_REVIEW`." Các TODO đã ACCEPT_LATER → T11 trong coordination (T04/T05/T06/T07) cần PO xác nhận phạm vi trước.
