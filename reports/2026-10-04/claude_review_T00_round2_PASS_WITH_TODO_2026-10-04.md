# Claude review — T00 — round 2 — 04/10/2026 — PASS_WITH_TODO

| Mục | Giá trị |
|---|---|
| Task | T00 — Gom mã và dữ liệu về project ổ C, model card A |
| Nhánh | `task/T00-gom-ma-o-d` (HEAD `7c31422`), so với `master` (`a3ed4cb`) |
| Đầu vào | `claude_review_T00_FAIL_2026-10-04.md`, `codex_fix_T00_round1_2026-10-04.md`, diff `b5a932c..7c31422` |
| Kết luận | **PASS_WITH_TODO**: RF-01 → RF-03 đã sửa đủ, gate đạt. Các TODO bên dưới thuộc PO hoặc task sau, không chặn T01 |
| Đổi schema | Không |

## 1. Kiểm từng Required Fix

### RF-01: Đã sửa

Commit fix `7c31422` chỉ sửa 3 tài liệu, file điều phối và report fix.

| Yêu cầu | `ml/README.md` | `ml/model_card_A.md` | `data/README.md` |
|---|---|---|---|
| Không còn "chờ upload", "chờ Tín", "vẫn cần bằng chứng", "cần được Tín", "chưa hoàn tất", `D:` | Đạt (grep rỗng trên cả 3 file) | Đạt | Đạt |
| Split ở `MyDrive/thesis/data/processed/` | Dòng 12 | Dòng 28 | Bảng + bước 1 |
| Error analysis ở `MyDrive/thesis/results/` | Dòng 13 | Dòng 28 | Bảng + bước 2 |
| Notebook ở `MyDrive/thesis/notebooks/phobert_A.ipynb` | Dòng 17 | Dòng 28 | Đoạn cuối |
| Runtime Colab mới đọc thành công ngày 04/10/2026 | Có | Có | Có (kèm số dòng 3 split) |
| Notebook ghi là bản lịch sử A/B/C, còn lệnh cài và đường dẫn cũ | Có | Có | Có |
| `data/README.md` là hướng dẫn khôi phục | — | — | Có mục "Khôi phục trên máy mới", 3 bước, nhắc đối chiếu số dòng/phân bố và không tạo split mới |

### RF-02: Đã sửa

Report fix có khối output Colab nguyên văn, ghi rõ nguồn là ảnh Tín gửi ngày 04/10/2026. Đã đối chiếu từng giá trị:

| Mục | Yêu cầu | Trong report |
|---|---|---|
| train | `(7786, 20)`, 0 = 3484, 1 = 4302 | Khớp |
| dev | `(1112, 20)`, 0 = 516, 1 = 596 | Khớp |
| test | `(2224, 20)`, 0 = 981, 1 = 1243 | Khớp |
| error_analysis | `True` | `.../MyDrive/thesis/results/error_analysis_taskA.csv True` |
| notebook_A | `True` | `.../MyDrive/thesis/notebooks/phobert_A.ipynb True` |
| Dấu hoàn tất | `T00_DRIVE_CHECK_OK` | Có |

Các số trong output khớp lần đếm CSV local Claude làm ở vòng 1. Claude không chạy lại Colab vì không bắt buộc. Ảnh gốc nằm trong chat của Tín, không nằm trong repo. Mức evidence này đủ cho AC-02.

### RF-03: Đã sửa

`ml/model_card_A.md`:
- Kiến trúc: pretrained `vinai/phobert-base-v2`. Khớp `ml/artifacts/phobert_A.json`.
- Thêm dòng "Kết quả gốc trong `phobert_A.json`": dev macro-F1 `0,9176` ở epoch 6, test macro-F1 `0,9128`, test accuracy `0,9141`. Claude đã đối chiếu với JSON gốc (`0.91759`, `0.91282`, `0.91412`).
- Tách thành dòng riêng "F1 lớp tiêu cực đã ghi nhận riêng: `0,9178` / `0,9180`, không phải macro-F1". Hai loại chỉ số đã được phân biệt rõ.

## 2. Gate độc lập (chạy lại sau fix)

| Gate | Kết quả |
|---|---|
| `backend\venv\Scripts\python -m compileall -q backend\app ml\src` | Đạt (exit 0) |
| Backend `uvicorn app.main:app --port 8000` → `/api/health` | Đạt: `HTTP 200 {"status":"ok","classifier":"phobert","classifier_error":null}` |
| `cd frontend; npm run build` | Đạt (exit 0) |
| Scope `git diff --name-only master...HEAD` | Đạt: 18 file = 15 file implementation T00 trong allowlist (gồm file điều phối) + 3 report (`codex_implementation`, `claude_review_..._FAIL`, `codex_fix_..._round1`) |
| File cấm (`.env`, `*.db`, `*.csv`, `*.safetensors`, `*.bin`, `*.zip`, `*.joblib`, `*.pt`, `*.ipynb`, `backend/models/`, `ml/artifacts/`, `backup/`) | Không có |
| `backend/app/`, `frontend/` trong diff | Không có → `normalize()` và classifier không đổi |
| `git status` sau gate | Sạch |

Vòng này Claude không dùng probe. Các kết quả về hai checkpoint và 10 câu `normalize()` ở vòng 1 vẫn còn hiệu lực, vì commit fix không đụng tới model hay mã.

## 3. TODO (không chặn T01, chờ PO disposition)

| # | TODO | Đề xuất disposition |
|---|---|---|
| TODO-01 | Hai checkpoint model A khác nhau (201/201 tensor, lệch tối đa 0,0048; câu "Phim dài lê thê, nửa đầu buồn ngủ thật sự." đổi nhãn). Chưa biết F1 0,9178/0,9180 được đo trên bản nào. **Chỉ là ghi nhận cho PO, không vi phạm Task Record, không thay model backend.** | ACCEPT_LATER: đo F1 test cả hai bản với `normalize()` hiện tại, ở T02 hoặc task PO duyệt riêng |
| TODO-02 | `normalize()` khác `text_utils.py` (dạng `text_norm` lúc train) ở 9/10 câu mẫu | ACCEPT_LATER (T02, như T00 mục 13 đã định) |
| TODO-03 | `MyDrive/thesis_results/firefly_phobert.zip` chưa được xác minh trong T00 | ACCEPT_LATER (T13 sao lưu) hoặc WONT_FIX |
| TODO-04 | `HUONG_DAN.md` 4.2 đổi thụt lề khối `.env` từ 3 lên 4 dấu cách. Hiển thị vẫn đúng | WONT_FIX (thẩm mỹ) |

Open Blocker "hai checkpoint" vẫn giữ trong file điều phối cho PO. Blocker này không chặn T01, vì T01 chỉ dùng CSV split và mô hình truyền thống, không dùng checkpoint PhoBERT.

## 4. Trạng thái sau review

- T00: `CLAUDE_REVIEW` → **`PO_REVIEW`**. Claude không approve, không merge, không tag, không đóng T00.
- Open Required Fixes: 0.
- Task kế tiếp theo `AGENT_RULES.md` mục 1.1: **T01**. Dependency duy nhất là T00 (task vừa PASS), T01 không bị Q1–Q4 chặn và không phải task tùy chọn. Vì vậy **T01 → `READY_FOR_HANDOFF`**.

## 5. Bàn giao task kế tiếp

**Việc Tín làm trước khi gửi prompt:**
1. PO review T00 (cho disposition từng TODO ở mục 3), rồi chạy `git checkout master` và `git merge task/T00-gom-ma-o-d`. T00 không phải mốc gắn tag.
2. Tạo nhánh mới từ master đã merge: `git checkout -b task/T01-mo-hinh-truyen-thong`.
3. Gửi prompt dưới đây kèm `docs/tasks/T01.md` và `docs/TASK_COORDINATION_ACTIVE.md`.

**Prompt ChatGPT/Codex cho T01:**

```text
Bạn là Codex, Primary Implementer của dự án Firefly Cinema.
Task: T01 — Mô hình truyền thống (NB, LR, SVM).
Trạng thái: READY_FOR_HANDOFF (Tín gửi Task Record = PO đã duyệt). Chuyển sang IN_PROGRESS khi bắt đầu.
Repo: C:\Projects\firefly-cinema · Nhánh: task/T01-mo-hinh-truyen-thong (đã tách từ master sau khi merge T00).

Chỉ đọc:
1. docs/PROJECT_SOURCE_OF_TRUTH.md
2. docs/AGENT_RULES.md
3. docs/TASK_COORDINATION_ACTIVE.md (Snapshot, Status, Next Step)
4. docs/tasks/T01.md
5. Dependency T00 (đã PASS): ml/README.md, ml/model_card_A.md, data/README.md
6. Source liên quan trực tiếp: ml/src/baselines.py, ml/src/common.py, ml/results/baseline_results.json,
   backend/app/classifier.py::normalize() (chỉ đọc, dùng cho AC-05)
Không đọc task CLOSED, không đọc report cũ trừ khi cần đối chiếu dependency.

Nhiệm vụ: thực hiện T01 đúng Task Record, chỉ sửa file trong Allowed Files mục 6.
- Hoàn thiện tiếp ml/src/baselines.py (T00 kết luận đã có NB/LR/SVM Task A, KHÔNG viết lại từ đầu).
- Thêm tham số dòng lệnh --data và --out theo mục 10; dữ liệu ở data\uit-visfd\processed\ (ngoài Git).
  Script cũ dùng đường dẫn tương đối "processed"/"results", phải sửa lại.
- Đầu vào text_norm, nhãn has_negative, đúng split T00: train 7.786 / dev 1.112 / test 2.224, in số dòng ra (AC-01).
- Chọn siêu tham số chỉ trên dev; test chạy một lần cho cấu hình đã chọn, code phải thể hiện rõ (AC-02).
- random_state=42 ở mọi chỗ có ngẫu nhiên; chạy hai lần ra cùng số, sai lệch ≤ 0,001 (AC-04).
- Ghi ml/results/baselines.csv đủ cột mục 4, gồm 3 mô hình × (dev, test) (AC-03);
  ms_per_sentence đo trên CPU, trung bình 1.000 câu test, dự đoán từng câu.
- Lưu nb_A.joblib, lr_A.joblib, svm_A.joblib (Pipeline vectorizer + model) vào ml\artifacts\baselines\ (ngoài Git).
  Ghi đường dẫn Drive MyDrive/thesis_results/baselines/. Không commit .joblib.
- AC-05: joblib.load(svm_A.joblib).predict([normalize("Ko hay như quảng cáo, hơi thất vọng")]) chạy được.
- Ghi phiên bản scikit-learn, joblib vào ml/requirements-ml-train.txt. Không thêm thư viện khác.
- Cập nhật ml/README.md: cách chạy, nơi lưu .joblib (AC-06). Không ghi đường dẫn D:\.

Điểm cần lưu ý, không tự quyết:
- Task Record ghi MultinomialNB, nhưng mã hiện có dùng ComplementNB. Làm theo Task Record (MultinomialNB).
  Nếu muốn giữ ComplementNB làm thêm thì ghi rõ lý do trong report, không thay thế.
- baselines.py hiện có thêm baseline Task B/C. T01 chỉ yêu cầu Task A. Không mở rộng B/C;
  nếu cần tách hoặc bỏ phần đó thì ghi vào report để PO quyết.
- text_norm trong CSV khác normalize() của backend (T00 đo được 9/10 câu mẫu khác).
  T01 train trên text_norm như PhoBERT A; không sửa normalize(), không sửa backend/**.
- Hai checkpoint PhoBERT A khác nhau là việc của PO/T02, không thuộc T01.

Gate: theo AGENT_RULES.md mục 3.2 (tái lập seed, đúng split, đúng text_norm, kết quả nhỏ vào ml/results/)
và scope/bí mật: git diff --name-only master...HEAD chỉ chứa Allowed Files,
không có .joblib, CSV, model, .env, *.db.
Tạo reports/<YYYY-MM-DD>/codex_implementation_T01_<YYYY-MM-DD>.md theo chính sách mục 11,
có dòng "Đổi schema: Không", bảng AC-01 → AC-06 kèm evidence, bảng số liệu dev/test.
Cập nhật TASK_COORDINATION_ACTIVE.md: IN_PROGRESS -> CLAUDE_REVIEW.
Commit dạng [T01] mô tả. Không tự review, không tự PASS, không merge, không mở task kế tiếp.
Trả lời bằng tiếng Việt.
```
