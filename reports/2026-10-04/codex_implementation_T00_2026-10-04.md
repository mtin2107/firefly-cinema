# Codex implementation report — T00 — 04/10/2026

## Task / Result

T00 — Gom mã và dữ liệu từ ổ D về repo ổ C, model card A. **Implementation hoàn tất, bàn giao `CLAUDE_REVIEW`.** Tín đã đưa riêng commit PO đổi phạm vi `a3ed4cb` vào `master` bằng fast-forward; scope gate `git diff --name-only master...HEAD` hiện chỉ liệt kê file trong allowlist T00.

## Files Changed

Phần Codex: `ml/src/{baselines,common,error_analysis,prep,train_phobert}.py`, `ml/results/{baseline_results,dataset_stats}.json`, `ml/README_goc.md`, `ml/README.md`, `ml/model_card_A.md`, `data/README.md`, `backend/requirements-ml.txt`, `backend/.env.example`, `HUONG_DAN.md`, `docs/TASK_COORDINATION_ACTIVE.md`, report này. Các file của commit PO `a3ed4cb` không do Codex sửa.

## Implemented

- Chép mã train và kết quả JSON nhỏ vào `ml/`; năm file Python có SHA-256 khớp nguồn khi sao chép.
- Ghi bảng lưu trữ project ổ C/Drive, trạng thái baseline truyền thống và model card phần A. `data/README.md` ghi cách lấy lại dữ liệu từ Drive.
- Đếm trực tiếp các split trong `data/uit-visfd/processed/`: train 7.786 (0: 3.484; 1: 4.302), dev 1.112 (0: 516; 1: 596), test 2.224 (0: 981; 1: 1.243).
- Đối chiếu `backup/02_api_cu/api/text_utils.py` với `backend/app/classifier.py::normalize()` trên 10 câu; 9 câu khác. Ghi nguyên ví dụ, không sửa classifier.
- Ghim `torch==2.11.0`, `transformers==5.18.0`; bỏ `underthesea` khỏi requirements và `HUONG_DAN.md` 4.2. Đồng bộ `.env.example` với cấu hình model A.
- Tín upload ba CSV split, CSV phân tích lỗi và bản sao notebook `phobert_A.ipynb` lên Drive. Runtime Colab mới đọc cả ba split và xác nhận số dòng/phân bố nhãn; `error_analysis=True`, `notebook_A=True`, `T00_DRIVE_CHECK_OK`.
- Kiểm hai model A trong project: cả hai nạp được; cùng 201 tensor nhưng cả 201 tensor khác giá trị. Chấm 10 câu bằng cùng `normalize()`: 1 câu đổi nhãn. Không thay bản backend.

## Đổi schema

Không.

## Architecture / Contract

Project chính duy nhất: `C:\Projects\firefly-cinema`. CSV ở `data/uit-visfd/`, model gốc ở `ml/artifacts/phobert_A_best/`, model web ở `backend/models/phobert-binhluan/`, API cũ ở `backup/02_api_cu/api/`; các tài sản lớn/backup ngoài Git. Drive lưu split tại `MyDrive/thesis/data/processed/`, error analysis tại `MyDrive/thesis/results/`, notebook tại `MyDrive/thesis/notebooks/phobert_A.ipynb`. Không đổi API hoặc schema.

## Focused Tests

- Năm file `ml/src/*.py` biên dịch; hai JSON trong `ml/results/` parse được.
- `git ls-files ml/` có mã, README và model card; không có CSV/model.
- `git check-ignore` xác nhận CSV, model và backup không vào Git.
- `rg -F 'D:\' ml/README.md ml/model_card_A.md data/README.md` không có kết quả.
- `HUONG_DAN.md` không có `underthesea`; requirements và `.env.example` khớp T00.
- Dữ liệu trên ổ C và Drive cùng số dòng/phân bố nhãn; bằng chứng Drive là output Colab của Tín ngày 04/10/2026.

## Final Gates

| Gate | Kết quả |
|---|---|
| `python -m compileall -q backend/app ml/src` | Đạt |
| Frontend `npm run build` | Đạt (67 modules, Vite build thành công) |
| Backend khởi động + `/api/health` | Đạt: HTTP 200, `status=ok`, `classifier=phobert`, `classifier_error=null` |
| ML đúng split | Đạt: đúng train/dev/test cố định, xác nhận lại từ runtime Colab mới |
| ML tái lập train | Không áp dụng cho T00: không train lại model trong scope |
| Hồi quy web | Health và build đạt; không đổi luồng web, không chạy checklist tương tác 7 mục |
| `git diff --cached --check` | Đạt |
| Scope `git diff --name-only master...HEAD` | Đạt: chỉ 16 file trong allowlist T00 |

## Acceptance Criteria AC-01 → AC-10

| AC | Kết quả | Evidence |
|---|---|---|
| AC-01 | Đạt | `git ls-files ml/` có `src/`, README, model card; không có CSV/model |
| AC-02 | Đạt | Tín chạy runtime Colab mới: train `(7786,20)`, dev `(1112,20)`, test `(2224,20)`, đúng phân bố; `T00_DRIVE_CHECK_OK` |
| AC-03 | Đạt | Đếm CSV thật trong project và đọc lại Drive; model card ghi đúng từng tập |
| AC-04 | Đạt | Model card có mục đối chiếu, khác biệt và 10 câu ví dụ |
| AC-05 | Đạt | README ghi `baselines.py` đã có NB/LR/SVM và T01 hoàn thiện tiếp |
| AC-06 | Đạt | Requirements ghim hai phiên bản, không có `underthesea`; hướng dẫn 4.2 đã sửa |
| AC-07 | Đạt | `.env.example`: `MODEL_DIR=models/phobert-binhluan`, `USE_WORD_SEGMENT=false`, `USE_TEXT_NORM=true` |
| AC-08 | Đạt với lưu ý PO | Hai SHA-256 và nguyên nhân trực tiếp (201 tensor có giá trị khác) trong model card; chưa biết chính xác checkpoint/lần lưu nào tạo khác biệt; 1/10 câu đổi nhãn |
| AC-09 | Đạt | Health HTTP 200, `classifier=phobert` |
| AC-10 | Đạt | Ba README/model card không chứa đường dẫn ổ D |

## Security / large-file check

Không stage/commit `.env`, `firefly.db`, CSV, `.safetensors`, `.bin`, `.zip`, `backend/models/`, `ml/artifacts/` hay `backup/`. Các tài sản lớn trong project bị `.gitignore` loại; không thêm thư viện ngoài hai phiên bản được T00 cho phép.

## Scope result

`git diff --name-only master...HEAD` sau khi Tín fast-forward `master` tới commit PO `a3ed4cb` chỉ có 16 file của implementation T00: `HUONG_DAN.md`, `backend/.env.example`, `backend/requirements-ml.txt`, `data/README.md`, `docs/TASK_COORDINATION_ACTIVE.md`, 10 file dưới `ml/`, và report này. Tất cả đều nằm trong allowlist. Không có `.env`, database, CSV hoặc model trong diff.

## Blockers

Không còn blocker cho bàn giao Claude review. Hai checkpoint model A khác trọng số và một câu đổi nhãn là vấn đề cần PO quyết sau khi đối chiếu nhật ký train và kết quả test; không tự thay model backend trong T00.

## Required Follow-up

- Claude review độc lập code, tài liệu, evidence Drive/Colab và final gates theo `AGENT_RULES.md`.
- PO quyết cách xử lý hai bản model A khác trọng số; nếu cần đo lại F1/đổi model, đưa vào task được duyệt riêng.

## TODO

- Chưa có bằng chứng tái lập huấn luyện PhoBERT A từ runtime mới; T00 chỉ yêu cầu xác nhận Drive/split, không train lại.
- Notebook `phobert_A.ipynb` là bản sao notebook lịch sử cho A/B/C, còn lệnh cài thư viện và đường dẫn cũ; không chạy lại toàn bộ như cấu hình hiện hành.
