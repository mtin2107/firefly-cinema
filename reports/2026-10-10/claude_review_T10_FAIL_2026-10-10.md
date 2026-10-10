# Claude Independent Review — T10 — Round 1 — 10/10/2026

**Kết luận: FAIL** — AC 7/7 đạt về chức năng, nhưng có **1 Required Fix (Medium)**: lazy-load/release PhoBERT không active bị race khi gọi `/api/admin/predict` đồng thời, tái hiện được 500 `AttributeError`.

## 1. Task, branch, baseline, review HEAD

| Trường | Giá trị |
|---|---|
| Task | T10 — Gắn model B vào web |
| Branch | `task/T10-gan-model-B` |
| Approved baseline | `38f63eedf3682216c1256cc581811e5ae9e05406` (ancestor của HEAD: có) |
| PO amendment | `b3bbad2` (có trong nhánh) |
| Implementation | `0e80015630a7275f32719021b0928bac905a56c6` (có trong nhánh) |
| Handoff / report | `13ea903`, `de90a45` (đã commit) |
| Review HEAD | `de90a452d6a02bc64b4851e9e73320a2cda19a87` |
| Môi trường | Windows, Python 3.13.2, torch 2.11.0+cpu, transformers 5.18.0, Node 24 |

## 2. Git / scope

- Working tree sạch trước review. `git diff --check 38f63ee...HEAD`: sạch.
- 18 file thay đổi, **tất cả nằm trong allowlist T10**; `docs/tasks/T10.md` là ngoại lệ PO cho phép (`PO-DECISION-T10-AC01-20261010`). Không sửa `frontend/src/api/real.js` (endpoint không đổi đường dẫn, chỉ thêm trường).
- Không có `.env`, `*.db`, checkpoint, ZIP, CSV trong diff. `ml/test_sentences.json` 4.993 byte. `backend/models/`, `ml/artifacts/`, `backup/` vẫn ngoài Git.
- `normalize()`, `_ABBR`, `_PUNCT`, `_REPEAT`: diff guard không có dòng nào thay đổi.
- Model A `backend/models/phobert-binhluan/` không bị đụng.

## 3. Source review (tóm tắt)

- `classifier.py`: `PhoBertModel(name, dir, version)` kiểm tra `id2label == {0: binh_thuong, 1: tieu_cuc}` và có `model.safetensors` trước khi đánh dấu `available`; nạp bằng `local_files_only=True`; version: env → `version.txt` → fingerprint `config.json`. Registry: `phobert`, `phobert_b`, sklearn, keyword; `_select_active` thử `requested → phobert → keyword`; `active_error` chỉ khác `None` khi model thực tế khác model yêu cầu.
- Model active nạp lúc khởi tạo; model PhoBERT còn lại nạp lười trong `/api/admin/predict` và `release()` sau mỗi request (`del self._model`, `del self._tokenizer`). **Đây là nguồn RF-01** (mục 11).
- `comments.model_version` `String(100)`, nullable; `create_comment` ghi `classifier.version`; seed dùng `classifier.name` + default `_active_model_version` → tên và version nhất quán.
- `AdminCommentOut.model_version: str | None`; `CommentOut` công khai **không** có `model_version` (đã xác minh không lộ).
- `admin_predict.py` giữ `Depends(require_admin)`; bắt `RuntimeError` của model phụ lazy-load lỗi.
- Frontend: `AdminComments.jsx` hiện `model_name · model_version`, null → "Chưa có phiên bản"; `AdminModelCompare.jsx` thêm 1 câu giới thiệu. `mock.js` cùng contract (`model_version` trong admin comment và predict), dữ liệu mock cũ được backfill `null`.
- `config.py`: mặc định `ACTIVE_MODEL=phobert_b`, `MODEL_DIR=models/phobert-binhluan` (trước đây rỗng), `MODEL_DIR_B=models/phobert-binhluan-B`.

## 4. PO AC-01 amendment

- `T10.md` ghi đúng `PO-DECISION-T10-AC01-20261010` (mục 14), AC-01 mới đúng nội dung PO; ngưỡng 0,001 giữ nguyên.
- AC-02 → AC-07 **không đổi** (đối chiếu diff `b3bbad2`).
- Task Record vẫn `Current Status: IN_PROGRESS` trong khi coordination là `CLAUDE_REVIEW` → ghi nhận (TODO-04), Claude không sửa.
- T09 TODO-02 vẫn `RESOLVED theo xác nhận PO` / `PO_ATTESTED`, không bị đổi thành Claude VERIFIED.
- `PROJECT_SOURCE_OF_TRUTH.md`, `AGENT_RULES.md`, `BOI_CANH_DU_AN.md` không bị sửa.

## 5. Independent reference baseline

**Artifact `ml/test_sentences.json`:** đúng 10 câu, có "Phim dài lê thê, xem mà mệt" (T10-01), mỗi câu có `source`, `normalized_text`, `expected_negative_score`, `expected_label`; metadata có model identifier, class model/tokenizer, SHA-256 `model.safetensors`/`config.json`/`selection_manifest.json`, `max_length=256`, `word_segmentation=false`, label mapping 0/1, threshold 0,5, môi trường. Nguồn câu: T08 probe + test T00 trong `ml/model_card_A.md` (bỏ test 5) + biến thể whitespace T10-09. Không thấy dấu hiệu chọn câu hay chỉnh score để tạo parity giả. Expected label nhất quán với threshold 0,5 ở cả 10 câu.

**Hash:** Claude tự tính SHA-256 — `ml/artifacts/phobert_B_best/model.safetensors` `0b80947c…22f4f`, `config.json` `3af764b4…05da`, `selection_manifest.json` `d21786d2…4035` khớp JSON và khớp giá trị trong `codex_implementation_T09` / `po_review_T09_APPROVED` trên `master`. Bản runtime `backend/models/phobert-binhluan-B/` byte-identical 6/6 file với artifact; `version.txt` = `phobert-B-2026-10-09`.

**Reference độc lập của Claude** (probe tạm, đã xóa): load trực tiếp `AutoTokenizer` + `AutoModelForSequenceClassification` từ `ml/artifacts/phobert_B_best` (không phải bản copy backend), `local_files_only`, `eval()`, `inference_mode()`, softmax lớp 1, `max_length=256`. Normalize lấy từ bản sao độc lập `ml/src/eval_utils.normalize` (trích qua AST, không import backend).

| Kiểm tra | Kết quả |
|---|---|
| `id2label` | `{0: binh_thuong, 1: tieu_cuc}` |
| Class | `PhobertTokenizer`, `RobertaForSequenceClassification` |
| Normalized text (ml/src) == JSON | 10/10 |
| Score Claude vs `expected_negative_score` | 10/10, **max \|Δ\| = 0,0** |
| Label Claude vs `expected_label` | 10/10 |

**Runtime backend** — `scripts\check_model.py --model phobert_b` (chạy độc lập): `PARITY=10/10 MAX_ABS_DELTA=0.000048`, exit 0. Normalize backend == JSON 10/10 (script tự kiểm).

**Độ chính xác runtime:** `PhoBertModel.predict` trả `round(score, 4)`, nên sai số làm tròn tối đa 5×10⁻⁵ (5 % ngưỡng). Max Δ quan sát 4,8×10⁻⁵ < 5×10⁻⁵ — đúng với parity tuyệt đối của score gốc (reference Claude khớp JSON Δ 0). Phép so sánh **hợp lệ theo AC-01**; ghi chú ở TODO-02.

**`check_model.py` có thật sự bắt mismatch?** Probe chạy `main()` với bản baseline bị nhiễu (bản sao tạm):

| Biến thể | Kết quả |
|---|---|
| T10-04 score +0,0011 | FAIL 9/10, exit 1 |
| T10-04 score +0,0009 (trong ngưỡng) | PASS 10/10 (đúng kỳ vọng) |
| T10-01 đổi `expected_label` | FAIL 9/10, exit 1 |
| T10-06 đổi `normalized_text` | SystemExit "normalize sai" |
| SHA-256 `config.json` sai | SystemExit "SHA-256 config.json sai" |
| Chỉ 9 câu | SystemExit "Baseline phải có đúng 10 câu" |

## 6. Movie test 149

Cùng probe reference độc lập trên `data/phim/movie_test.csv`:

| Chỉ số | Claude | T09 | \|Δ\| |
|---|---|---|---|
| SHA-256 | `5af8f616…c660` (khớp report T08) | — | — |
| Số câu / nhãn | 149 / {0: 48, 1: 101} | 149 / 48·101 | 0 |
| F1 negative | 0.917525773196 | 0.917525773196 | 1,2×10⁻¹³ |
| Macro-F1 | 0.881839809675 | 0.881839809675 | 1,4×10⁻¹³ |

Không đổi nhãn, không chọn lại checkpoint/threshold. Lưu ý: đây là **tái lập cùng checkpoint**, không phải kiểm chứng độc lập chất lượng mô hình (T09 TODO-04 về kiểm định cặp A–B vẫn ACCEPT_LATER).

## 7. AC-01 → AC-07

Kiểm tra trên uvicorn thật (cổng 8011/8000), mỗi kịch bản một tiến trình riêng, DB tạm trong scratchpad; `.env` thật **không** sửa (dùng env override).

| AC | Kết quả | Bằng chứng Claude |
|---|---|---|
| AC-01 | **PASS** | Mục 5–6: reference độc lập Δ 0 với JSON; runtime 10/10 max Δ 0,000048; movie test khớp T09 ≤ 1,4×10⁻¹³ |
| AC-02 | **PASS** | Backend thật: POST comment "Phim dài lê thê, xem mà mệt" → 201, `is_negative=true`, score `0.9988`; DB `('phobert_b','phobert-B-2026-10-09',0.9988)`; admin predict B `tieu_cuc 0.9988` |
| AC-03 | **PASS** | Health: `active_model=phobert_b`, `active_version=phobert-B-2026-10-09`, `classifier_error=null`; A `A-backend available, loaded=false`, B `loaded, active`; mỗi model có `version`. Khi fallback, B `active=false` và chỉ A `active=true` |
| AC-04 | **PASS (DB tạm)** | Cột nullable; comment mới lưu đúng name/version; 12 comment seed cũng `phobert_b/phobert-B-2026-10-09`; đặt `model_version=NULL` cho id=1 → `/api/admin/comments` 200, trả `null`, UI hiện "Chưa có phiên bản"; danh sách công khai không lộ `model_version`. **DB thật chưa sẵn sàng** — mục 10 |
| AC-05 | **PASS** | `ACTIVE_MODEL=phobert`: health `phobert/A-backend`, B available nhưng không load; "Ko hay như quảng cáo, hơi thất vọng" score `0.9937`, lưu `('phobert','A-backend',0.9937)`; admin predict vẫn có A + B |
| AC-06 | **PASS** | (a) `MODEL_DIR_B=models/T10-claude-missing-B`: không crash, active A, `classifier_error` = "Không tìm thấy thư mục model…", B `available=false`, comment lưu A; (b) thư mục B tồn tại, config/tokenizer thật, `model.safetensors` hỏng: active A, B `available=false`, lỗi deserialize, comment lưu A. Checkpoint B thật không bị di chuyển/sửa |
| AC-07 | **PASS** | Browser E2E 7/7 — mục 9 |

**AC PASSED / TOTAL: 7/7.**

## 8. Architecture, security, errors

| Hạng mục | Kết quả |
|---|---|
| Model T07 (svm/lr/nb/keyword) | Vẫn nạp, có trong predict và health |
| B mặc định theo Q3 | PASS — `.env` thật không có `ACTIVE_MODEL` → B |
| A fallback không phụ thuộc B | PASS (missing + broken B) |
| Version ghi theo model thực tế | PASS (B, A, fallback) |
| Admin predict 401 / 403 / 200 | PASS ở cả 4 kịch bản (403 kèm câu tiếng Việt) |
| Predict tuần tự nhiều lần | PASS — 2 lần liên tiếp cùng kết quả, A được release (`loaded=false`) |
| **Predict đồng thời** | **FAIL → RF-01** |
| Model/tokenizer local | PASS (`local_files_only=True`) |
| Dependency mới | Không |
| `.env` thật, DB thật, backup | Không sửa; SHA-256 `firefly.db` trước/sau review `ed3abdba…0d0a`, `integrity_check ok` |
| Lỗi lộ qua health công khai | Không lộ đường dẫn tuyệt đối mới (lỗi thiếu thư mục dùng giá trị cấu hình). Model hỏng vẫn trả chuỗi exception thô của thư viện — cùng loại với T07 TODO-03 (ACCEPT_LATER → T11), không phải lỗ mới |

`.env` cũ có `ACTIVE_MODEL=phobert`: runtime sẽ chạy **A** (đã chứng minh ở AC-05), health báo đúng `phobert/A-backend`. Sửa `.env.example` không đổi `.env` đang chạy. Máy Tín hiện **không** có dòng `ACTIVE_MODEL` trong `backend/.env` nên chạy B; nếu thêm dòng `ACTIVE_MODEL=phobert` thì phải đổi thành `phobert_b` (hoặc xóa dòng) rồi restart.

## 9. Real / mock / browser regression

Browser E2E trên trình duyệt trong app, frontend Vite thật + backend uvicorn thật (DB tạm):

| # | Mục checklist | Kết quả |
|---|---|---|
| 1 | Trang chủ hiện phim; "Xem chi tiết" mở trang phim | PASS (animation poster không đổi code, không kiểm từng khung hình) |
| 2 | Menu Thể loại → "Kinh dị" ra 2 phim kinh dị; tìm "meo muop" → "Mèo Mướp Đi Lạc" | PASS |
| 3 | Đăng ký tài khoản mới → đăng nhập ngay; chưa đăng nhập bấm 22:00 → `/dang-nhap`, đăng nhập xong về `/dat-ve/20` | PASS |
| 4 | Đặt A1, A2 → mã vé, "Vé của tôi" có vé; mở lại suất thấy A1/A2 `seat--taken`, disabled | PASS |
| 5 | Comment "Ko hay như quảng cáo, hơi thất vọng" → thông báo ẩn; admin thấy `1.00 · phobert_b · phobert-B-2026-10-09` (score gốc 0,9992) | PASS |
| 6 | Health báo classifier `phobert_b` (theo Q3; checklist BOI_CANH vẫn ghi `phobert` — TODO-03) | PASS |
| 7 | `VITE_USE_MOCK=true` (dev server riêng, 0 request tới :8000): admin comments hiện `phobert_b · phobert-B-2026-10-09-mock`; dữ liệu mock cũ thiếu `model_version` → "Chưa có phiên bản"; so sánh mô hình mock trả 1 dòng B | PASS |

Mobile 375×812: `/quan-tri/binh-luan` và `/quan-tri/so-sanh-mo-hinh` không có cuộn ngang trang (`scrollWidth=375`); bảng so sánh cuộn trong khung như trước. Frontend build real và mock: PASS. `compileall backend/app backend/scripts`: PASS.

## 10. Database: tạm vs thật

1. **Schema/chức năng trên DB tạm: PASS** (mục 7, AC-04).
2. **DB thật `backend/firefly.db` chưa sẵn sàng.** Đọc chỉ-đọc: `integrity_check ok`, bảng `comments` **không có** `model_version`, 13 comment `phobert`. Chạy uvicorn trên **bản sao** DB thật: health 200, `/api/movies` 200, nhưng `GET /api/movies/1/comments`, `POST` comment và `GET /api/admin/comments` đều **500** (`sqlite3.OperationalError: no such column: comments.model_version`). Nghĩa là nếu merge rồi chạy với DB hiện tại, phần bình luận và kiểm duyệt hỏng hoàn toàn.

Đây là hệ quả đã dự kiến của đổi schema theo Q2 (`NO ALEMBIC / BACKUP_BEFORE_RESET`), Codex đã disclose và cập nhật `HUONG_DAN.md` mục 2.1. Không phải lỗi code → **TODO-01, PO ACTION REQUIRED** trước khi chạy/demo trên DB thật. Claude không sửa/reset DB thật.

## 11. Required Fixes

### RF-01 — Race khi lazy-load/release PhoBERT không active trong `/api/admin/predict`

- **Severity:** Medium
- **File:** `backend/app/classifier.py` (`PhoBertModel.ensure_loaded`, `predict`, `release`; `ModelRegistry.release_if_inactive`), `backend/app/routers/admin_predict.py` (khối `finally`)
- **Problem:** Endpoint sync chạy trong threadpool. Request X đang predict bằng model không active (A khi B active, hoặc ngược lại) thì request Y chạy xong và gọi `release()` → `del self._model` / `del self._tokenizer` → X ném `AttributeError` (không phải `RuntimeError`, nên không bị bắt) → HTTP 500. Hai request cũng có thể cùng nạp một model hai lần. Đây là shared mutable state do T10 thêm vào, đúng điểm prompt review yêu cầu kiểm tra.
- **Evidence:** uvicorn thật, DB tạm, B active, admin token; 3 vòng × 6 request `POST /api/admin/predict` song song: vòng 0 6/6 200; **vòng 1 4/6 → 500**; vòng 2 6/6 200. Log server: `AttributeError: 'PhoBertModel' object has no attribute '_model'`. Gọi tuần tự thì luôn 200. Model active không bao giờ bị release nên luồng bình luận công khai không bị ảnh hưởng; kết quả 200 không sai, chỉ lỗi 500.
- **Expected Fix:** Đồng bộ hóa vòng đời model nạp lười, ví dụ một `threading.Lock` cho mỗi `PhoBertModel` bao quanh nạp + suy luận + giải phóng (hoặc đếm số người dùng và chỉ release khi về 0), sao cho predict đồng thời không bao giờ thấy model đang bị xóa. Giữ nguyên hành vi: B active không bị release, lỗi lazy-load vẫn bỏ qua model phụ, `require_admin` giữ nguyên. Kèm bằng chứng: lặp lại probe ≥ 3 vòng × 6 request song song đều 200, và ca tuần tự/health sau predict không đổi. Không đổi `normalize()`, không đổi file ngoài allowlist.

## 12. TODO và đề xuất disposition

| ID | Severity | Nội dung | Đề xuất |
|---|---|---|---|
| TODO-01 | High (vận hành) | DB thật thiếu `comments.model_version` → bình luận/kiểm duyệt 500 trên DB hiện tại | **PO ACTION REQUIRED** trước khi chạy/demo trên DB thật: backup + checksum + integrity, rồi PO reset theo `HUONG_DAN.md` 2.1 (Q2). Không chặn fix loop |
| TODO-02 | Low | `check_model.py` so sánh score runtime đã làm tròn 4 chữ số; hiệu lực ngưỡng thực là 0,001 ± 5×10⁻⁵ | ACCEPT_WITH_NOTES — hợp lệ với AC-01; nếu sau này cần chặt hơn thì so score chưa làm tròn |
| TODO-03 | Low (tài liệu PO) | `CLAUDE.md` ("health phải báo `classifier":"phobert"`) và `BOI_CANH_DU_AN.md` mục 7 item 6 còn ghi `phobert`, sau Q3 là `phobert_b` | PO cập nhật tài liệu PO-owned (Claude/Codex không sửa) |
| TODO-04 | Info | `T10.md` `Current Status: IN_PROGRESS`, coordination `CLAUDE_REVIEW` | ACCEPT_WITH_NOTES — coordination là nguồn trạng thái (giống T06/T09) |
| TODO-05 | Info | Mock gắn nhãn `phobert_b` nhưng điểm vẫn từ `fakeClassify` (keyword) | ACCEPT — mock chỉ giữ contract; version có hậu tố `-mock` |
| TODO-06 | Info | T07 TODO-05 (health thiếu thông tin khi fallback): nay có `active`, `active_version`, `classifier_error` | Đề xuất PO đánh dấu RESOLVED trong T10 |

## 13. Definition of Done

| Mục | Trạng thái |
|---|---|
| Code đúng allowlist | MET |
| AC 7/7 | MET (chức năng) |
| Gate web (compileall, startup, health, build real/mock, mock E2E, hồi quy 7/7, scope, secret) | MET |
| `check_model.py` | MET |
| Không có Required Fix mở | **NOT MET — RF-01** |
| Report + coordination | MET |

## 14. Temporary probes

Tạo (tất cả trong scratchpad ngoài repo, trừ một mục): `ref_t10.py` (reference + movie test), `mismatch_t10.py` (nhiễu baseline), `live_t10.py` (uvicorn đa kịch bản + concurrency), các DB tạm `t10_*.db`, thư mục `brokenB`, log uvicorn; thêm tạm 2 cấu hình vào `.claude/launch.json` (file local, bị ignore) để chạy backend DB tạm và frontend mock. Đã xóa toàn bộ scratchpad, khôi phục `launch.json` từ bản sao, dừng mọi server (không còn cổng 8000/8011/5173/5174 lắng nghe), `localStorage` mock đã xóa. `git status` sạch trước khi commit report.

**Temporary Probes Remaining = 0.**

## 15. Final verdict và next step

**T10 Round 1: FAIL** — AC 7/7, RF-01 (Medium) mở, TODO 6.

- Coordination: `CLAUDE_REVIEW → FIX_LOOP`.
- Codex chỉ sửa RF-01 trong allowlist T10, viết `reports/YYYY-MM-DD/codex_fix_T10_round1_YYYY-MM-DD.md`, rồi trả về `CLAUDE_REVIEW`.
- T11 giữ `PLANNED / NOT AUTHORIZED`. Verdict FAIL nên không áp dụng `AGENT_RULES.md` mục 1.1; không có xung đột cần PO xử lý ở vòng này. Khi T10 PASS ở vòng sau, mục 1.1 sẽ cho Claude đặt T11 `READY_FOR_HANDOFF`, trong khi coordination ghi T11 "NOT AUTHORIZED" — PO nên chốt trước quyền này.
- Không merge, không gắn tag `phobert-B`, không approve/close T10.
- TODO-01 (reset DB thật theo Q2) là việc của PO, có thể làm song song với fix loop.
