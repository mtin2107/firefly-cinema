# Codex Implementation Report — T10 — 10/10/2026

## 1. Task và trạng thái

- Task ID: `T10`
- Task: Gắn model B vào web
- Branch: `task/T10-gan-model-B`
- Approved baseline: `38f63eedf3682216c1256cc581811e5ae9e05406`
- Amendment commit: `b3bbad2` — `[T10] Record PO-approved AC-01 amendment`
- Implementation commit: `0e80015630a7275f32719021b0928bac905a56c6`
- Reviewer tiếp theo: Claude
- Trạng thái: `READY_FOR_CLAUDE_REVIEW`
- Đổi schema: **Có** — thêm `comments.model_version` nullable

## 2. Lịch sử blocker và PO AC-01 amendment

Pre-flight ban đầu PASS nhưng T10 từng dừng ở `BLOCKED_PENDING_PO_EVIDENCE` vì T09 không lưu bộ 10 câu cùng expected score. Notebook Git có 19 cell nhưng không có output; manifest/model card chỉ có metric tổng hợp.

Ngày 10/10/2026, PO ban hành `PO-DECISION-T10-AC01-20261010`, APPROVED phương án B:

- Baseline 10 câu được tạo tại T10 bằng direct `transformers` reference inference, độc lập với backend classifier wrapper.
- Baseline dùng đúng checkpoint B đã xác minh, giữ parity tolerance `0.001`.
- Đây là kiểm thử implementation parity, không phải kiểm chứng độc lập chất lượng phân loại.
- Phải tái kiểm movie test 149 câu và đối chiếu metric T09.
- Không đổi checkpoint/model selection, không retrain, không mở lại T09, không miễn AC-02 đến AC-07.
- PO cho phép ngoại lệ tài liệu duy nhất là sửa `docs/tasks/T10.md`; allowlist production giữ nguyên.

Task Record và coordination được đồng bộ, T10 tiếp tục `IN_PROGRESS`. Q3 giữ nguyên: B mặc định, A fallback hoặc chọn qua `.env`, không có UI chọn model.

## 3. Checkpoint và runtime artifact

Nguồn: `ml/artifacts/phobert_B_best/`.

| File | SHA-256 | Kết quả |
|---|---|---|
| `model.safetensors` | `0b80947ca8fecffbfaa39373e92d1ed44d638dcb4981ff00da2dd08921d22f4f` | PASS |
| `config.json` | `3af764b446752118aa33982d7983f52919318373ff3108add0128834f28005da` | PASS |
| `selection_manifest.json` | `d21786d2354c9ac054155c8975da579cede1fc9d05a18b5949c9716f0fa34035` | PASS |

Checkpoint được sao chép ngoài Git sang `backend/models/phobert-binhluan-B/`. Sáu file runtime (`model.safetensors`, `config.json`, tokenizer, vocab, BPE, added tokens) đều byte-identical với nguồn. `version.txt` ghi `phobert-B-2026-10-09`. Model A không bị sửa hoặc thay thế.

Model/tokenizer chỉ được nạp local (`local_files_only=True`). `config.json` được kiểm tra đúng `0=binh_thuong`, `1=tieu_cuc`; runtime giữ `normalize()` hiện tại, không tách từ, `max_length=256`.

## 4. Reference baseline T10

Artifact: `ml/test_sentences.json`.

### Phương pháp

- Danh sách 10 câu được khóa trước khi chạy model; lấy từ probe T08 bắt buộc và bộ test T00 trong `ml/model_card_A.md`, có thêm trường hợp whitespace T10.
- Probe tạm sao chép nguyên contract normalization hiện hành nhưng không import/call `backend.app.classifier`.
- Load trực tiếp `AutoTokenizer` và `AutoModelForSequenceClassification` từ artifact B.
- `model.eval()`, `torch.inference_mode()`, softmax logits lớp 1, threshold `0.5`, `max_length=256`, không tách từ.
- Hai lượt reference inference liên tiếp cho `max_abs_delta=0.0`.
- Môi trường: Python `3.13.2`, PyTorch `2.11.0+cpu`, Transformers `5.18.0`.
- JSON lưu model/config/manifest hashes, tokenizer/model class, normalized input, nguồn câu, expected probability/label và phương pháp provenance `T10_PO_APPROVED_REFERENCE_BASELINE`.

### Kết quả 10 câu qua backend runtime

| ID | Expected score | Runtime score | `|Δ|` |
|---|---:|---:|---:|
| T10-01 | 0.998829186 | 0.9988 | 0.000029 |
| T10-02 | 0.999225497 | 0.9992 | 0.000025 |
| T10-03 | 0.998956084 | 0.9990 | 0.000044 |
| T10-04 | 0.001115250 | 0.0011 | 0.000015 |
| T10-05 | 0.001557850 | 0.0016 | 0.000042 |
| T10-06 | 0.999147773 | 0.9991 | 0.000048 |
| T10-07 | 0.001977055 | 0.0020 | 0.000023 |
| T10-08 | 0.998884976 | 0.9989 | 0.000015 |
| T10-09 | 0.001288521 | 0.0013 | 0.000011 |
| T10-10 | 0.999153256 | 0.9992 | 0.000047 |

Kết quả: `PARITY=10/10`, max `|Δ|=0.000048 ≤ 0.001`.

Probe bắt buộc `Phim dài lê thê, xem mà mệt`: reference `0.998829185963`, runtime `0.9988`, nhãn `tieu_cuc`.

## 5. Movie test 149 câu

Direct reference inference dùng đúng `data/phim/movie_test.csv`:

- SHA-256: `5af8f616429e325f89bef723e4d0fdf867b7cd7d1c777eb30bb024b18a95c660`
- Số dòng: 149; nhãn `{0: 48, 1: 101}`
- T10 F1 negative: `0.9175257731958762`
- T09 F1 negative: `0.917525773196`
- T10 Macro-F1: `0.8818398096748612`
- T09 Macro-F1: `0.881839809675`
- Độ lệch hai metric nhỏ hơn `1e-12`, đạt tolerance `0.001`.

Movie test chỉ dùng tái lập metric sau khi checkpoint đã khóa; không dùng để chọn model, threshold hoặc hyperparameter.

## 6. Implementation changes

- Registry thêm `phobert_b`, mặc định `ACTIVE_MODEL=phobert_b`.
- B active được nạp lúc khởi tạo; A nạp lười khi so sánh và được giải phóng sau inference để không giữ lâu hai PhoBERT trong RAM.
- Nếu B thiếu/không hợp lệ/không nạp được, registry fallback A rồi keyword. Health luôn báo model thực tế.
- Version đọc từ biến môi trường hoặc `version.txt`; nếu thiếu cả hai thì dùng fingerprint `config.json`.
- `/api/health` thêm `active_version`; từng model có `name`, `version`, `available`, `loaded`, `active`, `error`.
- `/api/admin/predict` trả đúng version cho A/B và bỏ qua PhoBERT phụ nếu lazy load thất bại; `require_admin` giữ nguyên.
- `comments.model_version` nullable; comment mới và dữ liệu seed mới lưu version model thực tế.
- Trang kiểm duyệt hiển thị model name + version; trang so sánh phân biệt A/B.
- Mock comment/predict dùng contract `phobert_b` + version mock tương ứng.
- `backend/scripts/check_model.py` xác minh hash, normalization, label và score parity 10 câu.
- `.env.example`, kiến trúc và hướng dẫn Q2/Q3 được cập nhật; không sửa `.env` thật.

## 7. Files changed

### PO amendment commit `b3bbad2`

- `docs/tasks/T10.md` — scope exception được PO cho phép
- `docs/TASK_COORDINATION_ACTIVE.md`

### Implementation commit `0e80015`

- `backend/app/classifier.py`
- `backend/app/config.py`
- `backend/app/models.py`
- `backend/app/schemas.py`
- `backend/app/routers/comments.py`
- `backend/app/routers/admin_predict.py`
- `backend/app/main.py`
- `backend/scripts/check_model.py`
- `backend/.env.example`
- `ml/test_sentences.json`
- `frontend/src/pages/AdminComments.jsx`
- `frontend/src/pages/AdminModelCompare.jsx`
- `frontend/src/api/mock.js`
- `docs/ARCHITECTURE.md`
- `HUONG_DAN.md`

Report và final coordination được ghi trong handoff commit sau implementation commit.

## 8. Acceptance Criteria

| AC | Kết quả | Evidence |
|---|---|---|
| AC-01 | **PASS** | Reference baseline T10 hai lượt ổn định; runtime 10/10, max Δ `0.000048`; movie test 149 câu khớp T09 |
| AC-02 | **PASS** | Câu bắt buộc runtime score `0.9988 ≥ 0.5`, nhãn tiêu cực |
| AC-03 | **PASS** | Uvicorn thật `/api/health`: active `phobert_b`, version `phobert-B-2026-10-09`; A/B và các model có version/trạng thái |
| AC-04 | **PASS** | DB tạm có cột nullable; API comment persist `('phobert_b','phobert-B-2026-10-09',0.9988)`; null cho dòng cũ được chấp nhận |
| AC-05 | **PASS** | Process restart độc lập với `ACTIVE_MODEL=phobert`: health A/version `A-backend`; comment `Ko hay...` score `0.9937`, persist A/version |
| AC-06 | **PASS** | `MODEL_DIR_B=models/T10-missing-phobert-B` (không đụng checkpoint thật): health active A, có lỗi B rõ ràng, comment vẫn phục vụ/persist A |
| AC-07 | **PASS** | Hồi quy chức năng 7/7; chi tiết mục 10 |

AC PASSED: **7/7**.

## 9. Backend, frontend, real/mock và security gates

| Gate | Kết quả |
|---|---|
| Backend compileall app + scripts | PASS |
| Uvicorn thật trên port 8010, DB tạm | PASS; `/api/health` HTTP 200 |
| `check_model.py --model phobert_b` | PASS 10/10, max Δ `0.000048` |
| B mặc định khi `.env` không đặt `ACTIVE_MODEL` | PASS |
| A qua env + restart | PASS |
| B missing safe simulation | PASS, fallback A |
| Admin predict security | PASS: không token 401, user thường 403, admin 200 |
| Admin predict A/B versions | PASS: A `A-backend`, B `phobert-B-2026-10-09` |
| Database temp schema/persistence | PASS; integrity `ok` |
| Frontend real build | PASS; Vite 70 modules |
| Frontend mock build | PASS; Vite 70 modules |
| Mock API runtime qua Vite SSR | PASS; comment và predict đúng model/version |
| Chrome headless mock UI smoke | PASS 3/3: home, admin comments version, model compare version |
| `git diff --check` | PASS |

## 10. Regression checklist 7/7

1. **PASS** — trang chủ render bằng Chrome headless, danh sách phim/hero có dữ liệu; code PosterIntro/đặt vé không thay đổi.
2. **PASS** — API search `q=meo muop` trả `Mèo Mướp Đi Lạc`; menu/taxonomy không thay đổi.
3. **PASS** — đăng ký mới HTTP 201; endpoint đặt vé khi chưa đăng nhập trả 401; protected-route/auth code không thay đổi.
4. **PASS** — đặt hai ghế `A1/A2`, mở lại suất thấy hai ghế đã đặt, `/api/bookings/me` có vé mới.
5. **PASS** — `Ko hay như quảng cáo, hơi thất vọng` đạt score B `0.9992`, `effective_negative=true`; admin thấy đúng B/version.
6. **PASS** — health báo classifier/active model `phobert_b` theo Q3 mới và version đúng.
7. **PASS** — mock build, mock API runtime và Chrome UI admin đều hoạt động; version B hiển thị.

## 11. Database safety

- Database thật: `backend/firefly.db`.
- Backup: `backup/T10_2026-10-10/firefly_before_T10.db` (ngoài Git).
- SHA-256 nguồn và backup: `ed3abdbad7ff65f74d2182dc8b5c757e8fc32edf37dcaf4073eac1d375e70d0a`.
- `PRAGMA integrity_check`: `ok` cho cả nguồn và backup.
- Sau toàn bộ test, checksum database thật vẫn không đổi.
- Schema, seed, comment persistence, nullable old value và regression chỉ chạy trên DB tạm trong `backup/T10_2026-10-10/`.
- Codex không xóa/reset/ghi đè database thật. Database thật hiện chưa có cột mới; nếu PO muốn dùng dữ liệu thật với T10, PO thực hiện quy trình backup-before-reset trong `HUONG_DAN.md`.

## 12. Scope, secret và large-file gates

- Production/test/docs diff nằm trong allowlist T10; `docs/tasks/T10.md` là scope exception được PO phê duyệt.
- Không sửa `frontend/src/api/real.js` hoặc file production ngoài allowlist.
- `normalize()` và `_ABBR` không đổi (diff guard PASS).
- Không commit `.env`, database, checkpoint, ZIP, CSV hoặc secret.
- `backend/models/` và `ml/artifacts/` vẫn ngoài Git; không có large model trong commit.
- Không retrain B; không sửa model A/B; runtime copy B được hash-check 6/6.

## 13. Required Fixes, blockers, TODO và giới hạn

- Required Fixes: **0**.
- Blockers: **0**.
- TODO chặn handoff: **0**.
- Evidence GPU T09 vẫn ở mức `PO_ATTESTED`, không phải `VERIFIED_BY_CLAUDE`.
- Baseline T10 chứng minh parity implementation trên cùng checkpoint, không chứng minh độc lập chất lượng model.
- Chrome smoke tập trung các trang bị T10 tác động; regression nghiệp vụ còn lại được kiểm qua API thật và build.
- Database thật chưa reset theo Q2; đây là hành động PO nếu muốn áp dụng schema mới lên dữ liệu thật.

## 14. Definition of Done

- Implementation đúng allowlist: MET.
- AC 7/7: MET.
- Full gates real/mock/security/schema/scope: MET.
- Report và coordination: MET.
- Implementation commit: `0e80015630a7275f32719021b0928bac905a56c6`.
- Sẵn sàng Claude independent review; chưa tự review/approve/merge/tag.

## 15. Lệnh tái lập chính

```powershell
Set-Location "C:\Projects\firefly-cinema"
backend\venv\Scripts\python -m compileall -q backend\app backend\scripts
Set-Location backend
.\venv\Scripts\python scripts\check_model.py --model phobert_b
Set-Location ..\frontend
npm run build
$env:VITE_USE_MOCK="true"
npm run build
Remove-Item Env:VITE_USE_MOCK
Set-Location ..
git diff --check
git status --short --branch
```

---

T10 STATUS: READY_FOR_CLAUDE_REVIEW  
AC PASSED / TOTAL: 7/7  
REQUIRED FIXES: 0  
BLOCKERS: 0  
IMPLEMENTATION COMMIT: `0e80015630a7275f32719021b0928bac905a56c6`  
NEXT STEP: Claude independent review
