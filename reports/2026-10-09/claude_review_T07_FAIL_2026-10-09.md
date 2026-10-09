# Claude Review — T07 — Đa mô hình và trang So sánh mô hình — FAIL — 09/10/2026

| Trường | Giá trị |
|---|---|
| Reviewer | Claude (Independent Reviewer / Tester) |
| Branch | `task/T07-da-mo-hinh` |
| Implementation commit | `e84820d` — `[T07] Add multi-model registry and comparison page` |
| Handoff commit | `6a56818` — `[T07] Record implementation handoff` (report + coordination) |
| Baseline | `master` `6d1d4bb` (chứa merge T06 `81330c2`) |
| Codex report | `reports/2026-10-09/codex_implementation_T07_2026-10-09.md` (chỉ dùng làm bằng chứng phụ) |
| Kết luận | **FAIL** — 1 Required Fix (RF-01, AC-05) |
| Chuyển trạng thái | T07 `CLAUDE_REVIEW` → `FIX_LOOP` |

## 1. Source Review

Đã đọc toàn bộ `git diff master...task/T07-da-mo-hinh` (18 file, +517/−53).

**Backend**
- `classifier.py`: `CommentClassifier` được tách thành `PhoBertModel`, `SklearnModel`, `KeywordModel` và `ModelRegistry`. Mỗi model có `name`, `version`, `loaded`, `error`, `predict(text) -> (is_negative, score)`. `ModelRegistry` vẫn giữ giao diện cũ (`name`, `error`, `predict`), nên `comments.py` và `seed.py` không cần sửa mà vẫn lưu đúng `model_name` của model active.
- `PhoBertModel._prepare` và đường suy luận (softmax lớp `NEGATIVE_LABEL_ID`, `max_length=256`, ngưỡng 0,5, `round(score, 4)`) giữ nguyên. Thêm `local_files_only=True`. Đường dẫn tương đối được resolve từ thư mục `backend`.
- `SklearnModel`: đầu vào là `normalize(text)`. Với SVM, score = sigmoid(`decision_function`), cài đặt theo hai nhánh nên ổn định số học (`d ≥ 0`: `1/(1+e^-d)`, `d < 0`: `e^d/(1+e^d)`). LR/NB dùng `predict_proba` cột `classes_.index(1)`. Đã xác minh `classes_ = [0, 1]` cho cả ba pipeline.
- Fallback `_select_active`: model được yêu cầu → `phobert` → `keyword`, có ghi log. `available_models()` chỉ trả model thật đã nạp và chỉ rơi về `keyword` khi không còn model thật nào.
- `admin_predict.py`: `POST /api/admin/predict` dùng `Depends(require_admin)`, `response_model=list[AdminPredictionOut]`, đo `ms` bằng `perf_counter` cho từng model.
- `schemas.py`: `AdminPredictIn.text = Field(min_length=1, max_length=1000)` cộng validator `strip()` trả câu tiếng Việt. Đây là nguồn gốc của RF-01.
- `main.py`: `/api/health` giữ `status`, `classifier`, `classifier_error`, thêm `models[]` và `active_model`.
- `config.py`, `.env.example`, `requirements-ml.txt`: thêm `ACTIVE_MODEL`, `SKLEARN_MODELS`, ghim `scikit-learn==1.7.2` và `joblib==1.5.2`, khớp môi trường tạo artifact T01.

**Frontend**
- `AdminModelCompare.jsx` chỉ import `api` từ `../api`. Trang có textarea (`maxLength=1000`), 5 câu mẫu dạng `<button>` (có câu "lê thê"), các trạng thái empty/loading/error/rỗng và bảng 5 cột Mô hình/Phiên bản/Nhãn/Điểm/Thời gian. Trang ghi rõ điểm SVM là sigmoid của decision function, không phải xác suất đã hiệu chỉnh.
- `real.js` / `mock.js` cùng có `admin.predict(text)` và trả cùng các key `{model, version, label, score, ms}`. Mock gọi `requireAdmin()`, báo 422 tiếng Việt khi text rỗng và đánh dấu `model: "mock"`.
- `App.jsx` thêm route vào trong guard admin hiện có. `Header.jsx` thêm link chỉ hiện khi `role === "admin"`. `global.css` chỉ thêm class `.model-*`, không sửa class có sẵn.

**Tài liệu**: `ARCHITECTURE.md` (endpoint), `CONG_NGHE.md` và `HUONG_DAN.md` 4.4 ghi rõ sigmoid(decision_function) không phải xác suất hiệu chỉnh, cùng cách cấu hình và thứ tự fallback.

## 2. Acceptance Criteria

| AC | Kết quả | Bằng chứng độc lập của Claude |
|---|---|---|
| AC-01 | **PASS** | Uvicorn thật (DB tạm, cổng 8011): `/api/health` → `phobert`, `svm`, `lr`, `nb` đều `loaded:true, error:null`, `keyword` loaded, `active_model:"phobert"`, `classifier:"phobert"`. Log không có cảnh báo phiên bản sklearn. |
| AC-02 | **PASS** | Chép 3 joblib sang thư mục tạm, **đổi tên** `svm_A.joblib` → `svm_A.renamed.joblib`, trỏ `SKLEARN_MODELS` vào bản chép (artifact thật không bị đụng, SHA256 giữ nguyên). Backend khởi động bình thường; health báo `svm loaded:false` kèm lỗi "Không tìm thấy file model…"; `/api/admin/predict` chỉ trả `phobert`, `lr`, `nb`. |
| AC-03 | **PASS** | Xem mục 4.1. Notebook T02 không lưu output và với SVM chỉ dùng `predict`, nên nguồn chuẩn là mã T02 `ml/src/eval_utils.py` (cùng `normalize`, tokenizer local, padding batch, `max_length=256`, softmax lớp 1, ngưỡng 0,5), chạy bằng đúng môi trường T02 (Python hệ thống + `PYTHONPATH` venv). Trên 10 câu so với API thật: nhãn khớp 10/10 cho mọi model; lệch score tối đa PhoBERT 4,3e-5, SVM 4,7e-5, LR 4,4e-5, NB 4,9e-5 (≤ 0,001). Trên toàn bộ 2.224 câu test qua registry, F1/macro/accuracy khớp **tuyệt đối** với T02 (mục 4.2). |
| AC-04 | **PASS** | Đoạn `_ABBR`…`normalize()` ở `master` và `HEAD` có cùng SHA256 `270e12ef…0d76`. Diff không có dòng +/− nào chạm `_ABBR`, `_PUNCT`, `_REPEAT`, `def normalize`. `models.py` không đổi. |
| AC-05 | **FAIL** | 401 khi chưa đăng nhập ("Bạn cần đăng nhập để tiếp tục."), 401 khi token sai, 403 với user thường ("Chỉ quản trị viên mới xem được trang này."): đạt. Text `"   "` hoặc `"\n\t"` → 422 tiếng Việt: đạt. **Nhưng `{"text": ""}` → 422 `"Trường 'text' không hợp lệ: String should have at least 1 character"`**, tức câu Pydantic tiếng Anh. Xem RF-01. |
| AC-06 | **PASS** | Uvicorn với `ACTIVE_MODEL=SVM` (kiểm tra luôn việc không phân biệt hoa thường): health `active_model:"svm"`; bình luận mới có `negative_score 0.8205`; SQLite tạm `model_name='svm'`. Fallback: `ACTIVE_MODEL=svm` + thiếu SVM → active `phobert`, `classifier_error` nêu lỗi SVM, bình luận lưu `phobert`. In-process: `ACTIVE_MODEL=zzz`, PhoBERT thiếu → `keyword` với lỗi "ACTIVE_MODEL không được cấu hình: zzz"; joblib hỏng + mục `SKLEARN_MODELS` sai cú pháp → bỏ qua, không crash. |
| AC-07 | **PASS** | Trình duyệt 375×812, chế độ real (backend DB tạm): bấm câu mẫu "lê thê" → loading ("Đang chấm điểm…", nút bị khóa) → 4 hàng PhoBERT/SVM/LR/NB có score và ms. `scrollWidth = 375` nên trang không tràn ngang; bảng cuộn trong `.table-wrap`. Tắt backend → ErrorState "Không kết nối được máy chủ…" có nút Thử lại. Chế độ mock (`VITE_USE_MOCK=true`, cổng 5174): empty → lỗi client "Hãy nhập nội dung cần chấm điểm." → loading → 1 hàng `mock / keyword-v1`. Real và mock cùng 5 key. |
| AC-08 | **PASS** | Hồi quy 7/7 với `ACTIVE_MODEL=phobert` (mục 5). |

## 3. Definition of Done

| Mục | Trạng thái |
|---|---|
| Đủ AC | **Chưa** — AC-05 FAIL |
| Gate web (compile, startup + health, build, mock) | Đạt |
| Hồi quy 7/7 | Đạt |
| Scope / allowlist | Đạt |
| Không commit secret, DB, model | Đạt |
| Tài liệu (`ARCHITECTURE`, `CONG_NGHE`, `HUONG_DAN`) | Đạt |
| Report Codex chính xác | **Một phần**: report ghi AC-05 PASS nhưng chỉ thử chuỗi toàn khoảng trắng, không thử `""` |

**DoD: NOT MET** (do RF-01).

## 4. Independent Tests

### 4.1. AC-03 trên 10 câu (registry qua HTTP so với mã T02 `eval_utils`)

Có 5 câu mẫu UI, 5 câu tự viết gồm viết tắt, lặp ký tự, câu miền điện thoại và câu phim. Score hiển thị dạng registry/tham chiếu:

| # | PhoBERT backend | SVM (decision) | Nhãn khớp | PhoBERT research `phobert_A_best` |
|---|---|---|---|---|
| 1 "Phim dài lê thê…" | 0.0485 / 0.048507 | 0.5807 (+0.3258) | 4/4 | **0.9602** |
| 2 | 0.0128 / 0.012824 | 0.6055 (+0.4286) | 4/4 | 0.0134 |
| 3 "Ko hay như quảng cáo…" | 0.9951 / 0.995073 | 0.8205 (+1.5194) | 4/4 | 0.9967 |
| 4 | 0.9820 / 0.982001 | 0.5396 (+0.1586) | 4/4 | 0.9929 |
| 5 | 0.0076 / 0.007557 | 0.4896 (−0.0418) | 4/4 | 0.0051 |
| 6 | 0.0039 / 0.003888 | 0.2990 (−0.8522) | 4/4 | 0.0033 |
| 7 | 0.9968 / 0.996780 | 0.6962 (+0.8291) | 4/4 | 0.9975 |
| 8 | 0.9831 / 0.983073 | 0.5819 (+0.3305) | 4/4 | 0.9958 |
| 9 | 0.0067 / 0.006737 | 0.4049 (−0.3849) | 4/4 | 0.0065 |
| 10 | 0.9377 / 0.937712 | 0.6137 (+0.4629) | 4/4 | 0.7382 |

- Lệch tối đa: PhoBERT 4,3e-5; SVM 4,7e-5; LR 4,4e-5; NB 4,9e-5. Toàn bộ là sai số làm tròn 4 chữ số của API.
- Nhãn SVM từ `pipeline.predict` (đúng đường T02) trùng `decision ≥ 0` trên cả 10 câu, nên ngưỡng sigmoid ≥ 0,5 không đổi quyết định của LinearSVC.
- **Phân biệt checkpoint:** registry dùng checkpoint backend `backend/models/phobert-binhluan` (`version: "A-backend"`). Checkpoint research `ml/artifacts/phobert_A_best` cho kết quả khác: lệch score tối đa 0,91 và khác nhãn 1/10, chính là câu mẫu "lê thê". AC-03 được đánh giá trên checkpoint backend, đúng phạm vi T07 (không thay model). Xem TODO-01.

### 4.2. Toàn bộ test UIT-ViSFD (2.224 câu, `text_raw` → registry)

| Model | f1_neg | macro_f1 | accuracy | Nguồn T02 |
|---|---|---|---|---|
| phobert (backend) | 0.918046 | 0.907526 | 0.908723 | Assert notebook T02 cell 7: backend `normalize` f1 = 0.918046 ✔ |
| svm | 0.893837 | 0.877855 | 0.879946 | `comparison_A.csv` SVM/normalize ✔ |
| lr | 0.893127 | 0.876910 | 0.879047 | `comparison_A.csv` LR/normalize ✔ |
| nb | 0.877617 | 0.861415 | 0.863309 | `comparison_A.csv` NB/normalize ✔ |

Như vậy registry tái lập đúng hành vi của notebook T02 trên cả 4 model, không chỉ khớp 10 câu.

### 4.3. API / validation (uvicorn thật, DB tạm)

| Ca | Kết quả |
|---|---|
| Không token / token sai / user thường | 401 / 401 / 403, câu tiếng Việt |
| `""` | **422 tiếng Anh** (RF-01) |
| `"   "`, `"\n\t"` | 422 "Nội dung cần chấm điểm không được để trống." |
| `{}`, `null`, `123`, `["a"]` | 422, phần thông báo vẫn tiếng Anh (cùng loại với TODO-01 T06 → T11) |
| 1.001 ký tự `a` / 1.001 khoảng trắng | 422 "String should have at most 1000 characters" (tiếng Anh) |
| 1.000 ký tự | 200, 4 model |
| `GET /api/admin/predict` | 405 |

### 4.4. Gate

| Gate | Kết quả |
|---|---|
| `backend\venv\Scripts\python -m compileall -q backend\app` | PASS |
| Backend khởi động + health | PASS ×4 cấu hình (đầy đủ, thiếu SVM, `ACTIVE_MODEL=SVM`, UI) |
| `cd frontend; npm run build` | PASS (Vite, 817 ms) |
| Mock mode | PASS |
| `git diff --check master...HEAD` | PASS |
| pytest | Không áp dụng (bắt buộc từ T11) |
| Phiên bản venv | scikit-learn 1.7.2, joblib 1.5.2, torch 2.11.0+cpu, transformers 5.18.0 |

## 5. Regression 7/7 (`ACTIVE_MODEL=phobert`, DB tạm)

| # | Kết quả | Bằng chứng |
|---|---|---|
| 1 | PASS | `GET /api/movies` 21 phim; trang chủ real render 29 link phim. Code PosterIntro/Home không đổi |
| 2 | PASS | `q=meo muop` → `["Mèo Mướp Đi Lạc"]`. Taxonomy/menu không đổi |
| 3 | PASS | Đăng ký mới 201 + token; đặt vé khi chưa đăng nhập → 401. Login/ProtectedRoute không đổi |
| 4 | PASS | Đặt `A1`, `A2` → 201; `booked_seats` có cả hai; `/api/bookings/me` có 1 vé |
| 5 | PASS | "Ko hay như quảng cáo, hơi thất vọng" → `effective_negative:true`, 0.9937. Trang phim hiện "Bình luận này đã được ẩn…". Trang kiểm duyệt hiện "Tiêu cực 0.99 · phobert" |
| 6 | PASS | `/api/health` `classifier:"phobert"`, `active_model:"phobert"` |
| 7 | PASS | `VITE_USE_MOCK=true` chạy trang so sánh, đăng nhập mock admin |

## 6. Architecture

- Registry đúng hợp đồng ARCHITECTURE 2.6 và Task Record mục 4: mọi model nhận cùng `normalize(text)` (PhoBERT qua `_prepare`), thiếu hoặc lỗi model thì bỏ qua, fallback `phobert` → `keyword`.
- SVM: score = sigmoid(decision_function), ổn định số học. Tài liệu và UI **không** diễn giải đây là xác suất hiệu chỉnh: đạt.
- Hành vi phân loại bình luận hiện hành không đổi: cùng checkpoint, cùng tiền xử lý, F1 test 0.918046 khớp T02. Trong mặc định, `classifier_error` vẫn mang lỗi của model active như trước.
- Không đổi schema DB: `models.py` không đổi, `model_name` là chuỗi sẵn có, không cần xóa `firefly.db`.
- Frontend chỉ gọi qua `src/api/index.js`. Contract real/mock khớp.

## 7. Security

- `require_admin` có trên endpoint mới (401/403 đã kiểm). Input giới hạn 1.000 ký tự, nên không có nguy cơ DoS lớn. PhoBERT cắt ở 256 token.
- Không có secret mới: scan các dòng thêm chỉ thấy tên hàm `AutoTokenizer` và chữ "token" trong tài liệu.
- Lưu ý (TODO-03): `/api/health` công khai trả `error` gồm đường dẫn tuyệt đối hoặc chuỗi exception thô của file model. Trước T07 health cũng đã lộ lỗi `MODEL_DIR`, nên đây là rủi ro thấp, không chặn.

## 8. Scope Integrity

- 18 file trong `master...HEAD`, **tất cả nằm trong allowlist** Task Record mục 6 (cộng report Codex và coordination). `comments.py` có trong allowlist nhưng không cần sửa.
- File cấm (`normalize()`, `_ABBR`, `models.py`) không đổi.
- Không track `.db`, `.joblib`, `backend/models/`, `data/` (chỉ `data/.gitkeep`, `data/README.md`), `.env`.
- Không thêm thư viện ngoài scikit-learn/joblib đã được Task Record cho phép.
- Không có đường dẫn `D:\`.
- Commit: `e84820d` (implementation, có kèm coordination) và `6a56818` (report + coordination), đúng định dạng `[T07] …`. Merge T06 `81330c2` là ancestor.
- Sau review: artifact SHA256 không đổi (`svm_A.joblib` `51d061fb…`), `backend/firefly.db` SHA256 không đổi (`ed3abdba…`). Probe, DB tạm và bản chép joblib nằm trong scratchpad ngoài repo. Đã dừng toàn bộ server. Working tree sạch trước khi commit review.

## 9. Required Fixes

### RF-01 — `text` rỗng trả 422 tiếng Anh (AC-05)

| Trường | Nội dung |
|---|---|
| Severity | **Medium**: AC-05 nêu đích danh "`text` rỗng → 422 tiếng Việt" và không đạt. Giao diện tự chặn chuỗi rỗng phía client nên người dùng UI không gặp, nhưng hợp đồng API sai |
| File | `backend/app/schemas.py`, `AdminPredictIn` (dòng `text: str = Field(min_length=1, max_length=1000)`) |
| Problem | Ràng buộc `min_length=1` chạy **trước** `field_validator` (mode after). Vì vậy `""` bị Pydantic chặn với câu tiếng Anh, validator tiếng Việt không bao giờ được gọi. Codex chỉ thử chuỗi toàn khoảng trắng (dài ≥ 1) |
| Evidence | Uvicorn thật, admin token: `POST /api/admin/predict {"text": ""}` → `422 {"detail": "Trường 'text' không hợp lệ: String should have at least 1 character"}`. Đối chứng: `{"text": "   "}` → `422 "…Nội dung cần chấm điểm không được để trống."` |
| Expected Fix | Để `""` đi vào validator tiếng Việt, ví dụ bỏ `min_length=1` và giữ kiểm tra rỗng sau `strip()`. Kết quả cần có: `""`, `"   "`, `"\n\t"` → 422 "Nội dung cần chấm điểm không được để trống.". Không đổi contract 200, 401/403, `max_length`. Nên (không bắt buộc) trả câu tiếng Việt cho quá 1.000 ký tự. Chỉ sửa `backend/app/schemas.py`. Gate lại: compileall, startup/health, các ca 4.3, build frontend |

**Open Required Fixes: 1.**

## 10. TODO (không chặn)

| ID | Mức | Nội dung | Đề xuất |
|---|---|---|---|
| TODO-01 | Medium (demo) | Câu mẫu "Phim dài lê thê, nửa đầu buồn ngủ thật sự." bị PhoBERT **backend** chấm 0.0485 (bình thường), trong khi checkpoint **research** `phobert_A_best` chấm 0.9602 (tiêu cực), còn SVM/LR/NB đều tiêu cực. Khi bảo vệ, trang so sánh sẽ cho thấy PhoBERT web "sai" đúng câu trình diễn. Không phải lỗi T07 (T07 không được thay model; PO đã chốt canonical research nhưng runtime web giữ checkpoint backend) | PO quyết định: giữ để minh họa lệch miền (T08/T09/T10), hoặc thay checkpoint runtime trong task riêng |
| TODO-02 | Low | `/api/admin/predict` không cô lập lỗi theo model: một model ném exception lúc predict sẽ làm cả request trả 500 | T11: bọc try/except từng model hoặc ghi rõ |
| TODO-03 | Low | Health công khai trả `error` thô: đường dẫn tuyệt đối, hoặc chỉ `"110"` khi joblib hỏng (khó hiểu) | T11/T13: rút gọn thông điệp, ẩn đường dẫn tuyệt đối |
| TODO-04 | Low | 422 cho thiếu `text`, `null`, sai kiểu, quá 1.000 ký tự vẫn dùng câu Pydantic tiếng Anh | Gộp vào TODO-01 của T06 → T11 (nếu RF-01 chưa xử lý luôn vế quá 1.000 ký tự) |
| TODO-05 | Low | Khi fallback, health không có trường riêng cho model được yêu cầu (`ACTIVE_MODEL`), chỉ suy ra từ `classifier_error` | T10: cân nhắc thêm `requested_active_model` |
| TODO-06 | Info | Report Codex ghi AC-05 PASS khi chưa thử `""`; coordination ghi "AC 8/8 DEV PASS" | Process: report fix round ghi đủ ca biên của AC |

## 11. Final Decision

**FAIL.** AC 7/8 PASS; AC-05 FAIL (RF-01 Medium). Hồi quy 7/7, gate kỹ thuật, scope, security, artifact và secret đều đạt. Registry, fallback, SVM sigmoid và parity T02 được xác minh độc lập và rất chặt (khớp tuyệt đối trên 2.224 câu). Chỉ cần sửa RF-01, một thay đổi nhỏ trong `schemas.py`.

## 12. Workflow Transition

- T07: `CLAUDE_REVIEW` → **`FIX_LOOP`** (Round 1, RF-01).
- Codex sửa RF-01 trên cùng nhánh `task/T07-da-mo-hinh`, viết `reports/YYYY-MM-DD/codex_fix_T07_round1_*.md`, rồi chuyển lại `CLAUDE_REVIEW` để Claude review Round 2.
- Không mở task mới. T08 giữ `PLANNED`. Claude không approve, merge, tag hay đóng T07.
