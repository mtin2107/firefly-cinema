# Codex Implementation Report — T07 — 09/10/2026

## 1. Branch / baseline / commits

- Branch: `task/T07-da-mo-hinh`.
- Baseline: `master` tại `6d1d4bb`; commit merge T06 `81330c2` là ancestor của `master`.
- Dependency: T01 `DONE / CLOSED`; PO report `po_review_T01_APPROVED_2026-10-05.md` ghi T01 `DONE / CLOSED`.
- Implementation commit: `e84820d` — `[T07] Add multi-model registry and comparison page`.
- Report + handoff: commit chứa chính report này.
- Đổi schema: **Không**.

## 2. Pre-flight

- Đúng branch và working tree sạch trước khi sửa.
- Có đủ artifact ngoài Git: `ml/artifacts/baselines/{svm_A,lr_A,nb_A}.joblib` và hai checkpoint PhoBERT.
- Môi trường tạo artifact T01: Python 3.13.2, scikit-learn 1.7.2, joblib 1.5.2. Backend venv ban đầu chưa có scikit-learn; đã ghim và cài đúng `scikit-learn==1.7.2`, `joblib==1.5.2`.
- Checkpoint backend: `backend/models/phobert-binhluan` (SHA/model card định danh checkpoint backend).
- Notebook T02: bảng chính dùng `ml/artifacts/phobert_A_best`; cell “Đối chiếu hai checkpoint PhoBERT A” đo riêng đúng `backend/models/phobert-binhluan`. T07 giữ nguyên checkpoint backend, không thay model.
- Không ghi đè model, artifact hay database. Các probe có ghi dữ liệu đều dùng SQLite trong thư mục tạm.

## 3. Files changed

- Backend: `backend/app/classifier.py`, `backend/app/config.py`, `backend/app/main.py`, `backend/app/routers/admin_predict.py`, `backend/app/schemas.py`, `backend/.env.example`, `backend/requirements-ml.txt`.
- Frontend: `frontend/src/pages/AdminModelCompare.jsx`, `frontend/src/App.jsx`, `frontend/src/components/Header.jsx`, `frontend/src/api/real.js`, `frontend/src/api/mock.js`, `frontend/src/styles/global.css`.
- Documentation/coordination: `docs/ARCHITECTURE.md`, `docs/CONG_NGHE.md`, `HUONG_DAN.md`, `docs/TASK_COORDINATION_ACTIVE.md`, report này.
- `backend/app/routers/comments.py` không cần sửa: code sẵn có gọi `classifier.predict()` và lưu `classifier.name`; registry mới trả đúng model active thực tế.

## 4. Implementation summary

- Registry cung cấp `name`, `version`, `predict`, `loaded`, `error` cho PhoBERT, SVM, LR, NB và keyword fallback.
- `ACTIVE_MODEL` chọn model chấm bình luận; model lỗi thì fallback PhoBERT rồi keyword. `SKLEARN_MODELS` khai báo các pipeline joblib; đường dẫn tương đối được resolve từ thư mục backend.
- SVM dùng sigmoid ổn định số học trên `decision_function`; UI và tài liệu ghi rõ đây không phải xác suất đã hiệu chỉnh.
- `POST /api/admin/predict` dùng `require_admin`, trả `{model, version, label, score, ms}` cho mọi model thật đã nạp.
- `/api/health` giữ trường cũ và thêm `models`, `active_model`.
- Trang `/quan-tri/so-sanh-mo-hinh` có route/menu admin, 5 câu mẫu (có “lê thê”), empty/loading/error, bảng kết quả, responsive và phần tử bàn phím chuẩn.
- `real.js` và `mock.js` có cùng `api.admin.predict`; page chỉ import từ `src/api/index.js`.

## 5. Acceptance Criteria

| AC | Kết quả | Evidence |
|---|---|---|
| AC-01 | PASS | Backend thật `/api/health`: `phobert`, `svm`, `lr`, `nb` đều `loaded:true`, `error:null`; `active_model=phobert`. |
| AC-02 | PASS | Probe đặt SVM thành `svm_A.missing.joblib`: import/startup thành công, SVM `loaded:false` với lỗi rõ, active fallback `phobert`, predict model còn lại chỉ PhoBERT. Không đổi tên artifact thật. |
| AC-03 | PASS | 10 câu cố định, direct inference theo T02 trên checkpoint backend và direct joblib SVM so với registry: label khớp 10/10; sai lệch score lớn nhất PhoBERT `0.000047410`, SVM `0.000046562` (≤ 0.001). |
| AC-04 | PASS | SHA256 source segment `normalize()` ở `master` và working branch cùng `51c8958e...91cdc`; diff không có marker sửa `normalize` hoặc `_ABBR`. |
| AC-05 | PASS | `/api/admin/predict`: chưa đăng nhập 401, user thường 403; text chỉ có khoảng trắng 422 với câu tiếng Việt “Nội dung cần chấm điểm không được để trống.” |
| AC-06 | PASS | Probe `ACTIVE_MODEL=svm` trên DB tạm: comment mới lưu `model_name="svm"`. |
| AC-07 | PASS | Browser mock 375×812: 5 mẫu, empty, loading, error, 1 hàng mock đủ 5 cột; browser real: 4 hàng PhoBERT/SVM/LR/NB có score và ms; tắt backend hiện lỗi kết nối. Không overflow; sample là button và form dùng submit chuẩn. |
| AC-08 | PASS | Hồi quy 7/7 ở mục 7, `ACTIVE_MODEL=phobert`. |

## 6. Focused tests và final gates

### Focused

- Model đầy đủ: PASS — 5 status gồm PhoBERT/SVM/LR/NB/keyword; bốn model chính loaded.
- Model thiếu: PASS — SVM lỗi không làm backend dừng, fallback đúng.
- Auth/validation: PASS — 401/403/422.
- Lưu model active: PASS — `svm` trên DB tạm.
- T02 parity: PASS — 10 câu, cả label và score trong tolerance.
- Normalize preservation: PASS — hash source segment giống baseline.
- Real/mock contract: PASS — cùng `api.admin.predict`; browser chạy cả hai mode.

### Final gates

- `backend\venv\Scripts\python -m compileall -q backend\app`: PASS (chạy tương đương từ `backend`: `-m compileall -q app`).
- Uvicorn thật port 8000: startup/shutdown sạch; `/api/health` HTTP 200, đủ model và active PhoBERT.
- `frontend\npm run build`: PASS, Vite 70 modules, build 756 ms ở lượt cuối.
- Pytest: không chạy; theo `AGENT_RULES.md`, pytest bắt buộc từ T11.
- `git diff --check`: PASS.
- Scope allowlist: PASS; không có file ngoài Allowed Files.
- Artifact/large file: PASS; không track `.joblib`, `.db`, `backend/models/*`, CSV.
- Secret scan trên dòng thêm: PASS, không có key/private key/password/secret thật.

## 7. Checklist hồi quy 7 mục

1. **PASS** — API trang chủ trả 21 phim; frontend build và mock browser hoạt động, code PosterIntro/luồng cũ không bị sửa.
2. **PASS** — tìm `meo muop` trả `Mèo Mướp Đi Lạc`; taxonomy/menu không bị sửa.
3. **PASS** — đăng ký tài khoản mới trên DB tạm trả 201/token; protected routing/AuthContext không bị sửa ngoài việc thêm route admin cùng guard hiện có.
4. **PASS** — đặt 2 ghế `A1`, `A2`; mở lại suất thấy cả hai trong `booked_seats`; `/api/bookings/me` có vé mới.
5. **PASS** — câu `Ko hay như quảng cáo, hơi thất vọng` có `effective_negative=true`, admin thấy score `0.9937`, `model_name=phobert`; UI contract ẩn mặc định giữ nguyên.
6. **PASS** — `/api/health` báo `classifier=phobert`.
7. **PASS** — `VITE_USE_MOCK=true`: trang so sánh chạy trọn empty → loading → result → error; mock trả đúng contract.

## 8. Security và scope

- Endpoint mới có `require_admin`; probe thật 401 và 403 đạt.
- Input giới hạn 1–1000 ký tự, strip khoảng trắng và trả 422 tiếng Việt.
- Không thay schema, `backend/app/models.py`, `normalize()`, `_ABBR`, dữ liệu, model hay artifact.
- Không thêm thư viện ngoài scikit-learn/joblib đã được Task Record duyệt.
- Không có giao diện thay `ACTIVE_MODEL`; Q3/T10 giữ ngoài scope.

## 9. Required Fixes, blockers và TODO

- Required Fixes mở: **0**.
- Blockers: **0**.
- TODO chặn handoff: **0**.
- Ghi chú vận hành: phải giữ đúng scikit-learn 1.7.2/joblib 1.5.2 khi nạp artifact T01; nếu artifact ngoài Git chưa được chép tới đường dẫn cấu hình, health sẽ báo `loaded:false` như thiết kế.

## 10. Evidence đối chiếu T02

- T02 main comparison và `comparison_A.csv` dùng checkpoint gốc; T02 cell backend checkpoint xác nhận đây là hai trọng số khác nhau. T07 không hòa trộn hoặc thay thế checkpoint.
- Probe T07 dùng đúng checkpoint web `backend/models/phobert-binhluan`, tokenizer local, `normalize()`, `max_length=256`, softmax lớp 1 và threshold 0.5 — cùng đường suy luận cell backend T02.
- SVM load đúng `ml/artifacts/baselines/svm_A.joblib`, nhận `normalize(text)`. Nhãn direct pipeline và registry khớp 10/10; score registry là sigmoid decision function theo Task Record.

## 11. Handoff

Điều kiện implementation handoff đã đạt. T07 chuyển `IN_PROGRESS` → `CLAUDE_REVIEW`; Codex không tự review, approve, merge, tag, đóng task hay mở T08.
