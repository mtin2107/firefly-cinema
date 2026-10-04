# Claude review — T00 — 04/10/2026 — FAIL

| Mục | Giá trị |
|---|---|
| Task | T00 — Gom mã và dữ liệu về project ổ C, model card A |
| Nhánh | `task/T00-gom-ma-o-d` (HEAD `affdb0b`), so với `master` (`a3ed4cb`) |
| Report Codex | `reports/2026-10-04/codex_implementation_T00_2026-10-04.md` |
| Kết luận | **FAIL** — 1 RF Medium, 2 RF Low. Phần kỹ thuật đạt; lỗi nằm ở tài liệu bàn giao chưa cập nhật theo evidence Drive/Colab |
| Đổi schema | Không |

## 1. Tóm tắt

Phần kỹ thuật của T00 đúng: mã ML đã vào Git, không có file lớn/bí mật trong diff, số liệu split khớp file thật, đối chiếu `text_utils.py` ↔ `normalize()` và phép thử hai checkpoint tái lập được đúng từng chữ số. `normalize()` và backend không bị đụng. Gate kỹ thuật đều đạt.

FAIL vì ba tài liệu là sản phẩm chính của T00 (`ml/README.md`, `ml/model_card_A.md`, `data/README.md`) vẫn ghi Drive/notebook là "chờ upload / chờ Tín cung cấp đường dẫn / vẫn cần bằng chứng", trong khi report Codex và file điều phối ghi đã upload xong, Colab đã đọc lại và notebook ở `MyDrive/thesis/notebooks/phobert_A.ipynb`. Mục tiêu T00 là ghi đúng "thứ gì nằm ở đâu" để khôi phục; merge bản này vào `master` sẽ để lại thông tin sai cho T01, T02, T09, T13. Sửa nhỏ, chỉ trong allowlist.

## 2. Scope và file cấm

`git diff --name-only master...task/T00-gom-ma-o-d` — 16 file, tất cả nằm trong Allowed Files mục 6:

```
HUONG_DAN.md, backend/.env.example, backend/requirements-ml.txt, data/README.md,
docs/TASK_COORDINATION_ACTIVE.md, ml/README.md, ml/README_goc.md, ml/model_card_A.md,
ml/results/baseline_results.json, ml/results/dataset_stats.json,
ml/src/{baselines,common,error_analysis,prep,train_phobert}.py,
reports/2026-10-04/codex_implementation_T00_2026-10-04.md
```

- Lọc diff theo `.env|.db|.csv|.safetensors|.bin|.zip|.pt|.joblib|.ipynb|models/|artifacts/|backup/`: **không có kết quả**.
- `git diff master...HEAD -- backend/app frontend`: **rỗng** → `normalize()` và classifier không đổi.
- `git ls-files ml data`: chỉ mã, README, model card, 2 JSON nhỏ, `.gitkeep`. Không CSV/model.
- `git status` sau gate: sạch (pycache, `dist/` đã bị ignore).
- Commit đúng dạng `[T00] ...`.

## 3. Đối chiếu Acceptance Criteria (kiểm độc lập)

| AC | Kết quả Claude | Bằng chứng độc lập |
|---|---|---|
| AC-01 | Đạt | `git ls-files ml/` có `src/*.py`, `README.md`, `README_goc.md`, `model_card_A.md`; không CSV/model |
| AC-02 | Đạt một phần (xem RF-02) | Report và timeline ghi Tín chạy Colab mới: shape `(7786,20)/(1112,20)/(2224,20)`, `T00_DRIVE_CHECK_OK`. Claude không chạy được Colab; repo không lưu output ô/ảnh chụp gốc |
| AC-03 | Đạt | Claude đếm lại bằng `csv` trên `data/uit-visfd/processed/`: train 7.786 (0: 3.484 / 1: 4.302), dev 1.112 (516/596), test 2.224 (981/1.243), 20 cột. Khớp model card và `ml/results/dataset_stats.json` |
| AC-04 | Đạt | Chạy lại 10 câu với `backup/02_api_cu/api/text_utils.py::normalize` và `backend/app/classifier.py::normalize`: 9/10 khác, 1/10 giống (câu 2). Từng output khớp bảng model card |
| AC-05 | Đạt | `ml/README.md` và model card ghi `baselines.py` đã có NB/LR/SVM Task A (+B/C), T01 hoàn thiện tiếp, không viết lại. Số LogReg `text_norm` test macro-F1 0,8823 / F1 tiêu cực 0,8966 khớp `baseline_results.json` |
| AC-06 | Đạt | `requirements-ml.txt`: `torch==2.11.0`, `transformers==5.18.0`, không `underthesea`. `HUONG_DAN.md` không còn chữ `underthesea` |
| AC-07 | Đạt | `.env.example`: `MODEL_DIR=models/phobert-binhluan`, `NEGATIVE_LABEL_ID=1`, `USE_WORD_SEGMENT=false`, `USE_TEXT_NORM=true`, `NEGATIVE_THRESHOLD=0.5` — khớp BOI_CANH 3.4 |
| AC-08 | Đạt (ghi nhận cho PO) | SHA-256 Claude đo: gốc `121C2CBC…75B7`, backend `15D46589…D470`, cùng 540.023.384 byte. Cùng 201 khóa tensor, **201/201 khác**; chênh tuyệt đối lớn nhất 0,00483. Xác suất 10 câu khớp model card đến 6 chữ số; câu 2 đổi nhãn (0,960 / 0,049) |
| AC-09 | Đạt | Backend tự khởi động: `HTTP 200 {"status":"ok","classifier":"phobert","classifier_error":null}` |
| AC-10 | Đạt | `grep 'D:'` trên `ml/README.md`, `ml/model_card_A.md`, `data/README.md`, `ml/README_goc.md`, `ml/src/*.py`: không có |

## 4. Gate độc lập

| Gate | Lệnh | Kết quả |
|---|---|---|
| Biên dịch | `backend\venv\Scripts\python -m compileall -q backend\app ml\src` | Đạt (exit 0) |
| Backend + health | `python -m uvicorn app.main:app --port 8000` → `/api/health` | Đạt, `classifier=phobert` |
| Frontend build | `cd frontend; npm run build` | Đạt (67 modules, 1,35 s) |
| Scope / bí mật | `git diff --name-only master...HEAD` | Đạt (16 file allowlist, không file cấm) |
| ML đúng split | Đếm CSV thật | Đạt |
| ML tái lập | — | Không áp dụng (T00 không train) |
| Hồi quy web | — | Không chạy checklist tương tác: T00 không đụng `backend/app`, `frontend` (diff rỗng); build + health đạt |

Probe tạm: một script Python trong scratchpad của Claude (ngoài repo), đã xóa trước khi kết luận. Không tạo file nào trong repo ngoài report này và cập nhật file điều phối.

## 5. Required Fixes

### RF-01 — Medium — Tài liệu Drive/notebook lệch với evidence đã có

- **File:** `ml/README.md` (dòng 12, 13, 17), `ml/model_card_A.md` (dòng 27), `data/README.md` (dòng 13).
- **Problem:** Ba tài liệu vẫn ghi trạng thái trước khi Tín upload: "chờ upload và kiểm chứng từ Colab mới", "chờ upload", "Chờ Tín lưu trên Drive và cung cấp đường dẫn", "vẫn cần bằng chứng của Tín", "Notebook phần A cần được Tín lưu trên Drive và cung cấp đường dẫn".
- **Evidence:** Report Codex mục Implemented và Architecture ghi split ở `MyDrive/thesis/data/processed/`, error analysis ở `MyDrive/thesis/results/`, notebook ở `MyDrive/thesis/notebooks/phobert_A.ipynb`, Colab mới xác nhận `T00_DRIVE_CHECK_OK`. File điều phối timeline 04/10 ghi Tín đã upload. Mâu thuẫn trực tiếp với yêu cầu kiểm "evidence Drive/Colab được ghi nhất quán với report" và thiết kế T00 mục 4 (bảng "Thứ gì — nằm ở đâu" phải đúng).
- **Expected Fix:** Cập nhật ba file theo trạng thái thật: split và error analysis "đã upload, đã kiểm từ runtime Colab mới ngày 04/10/2026"; dòng notebook ghi đường dẫn `MyDrive/thesis/notebooks/phobert_A.ipynb` kèm lưu ý (từ TODO report) đây là bản sao notebook lịch sử A/B/C còn lệnh cài và đường dẫn cũ. Bỏ câu "vẫn cần bằng chứng" trong model card. `data/README.md` dòng 13 viết lại thành hướng dẫn khôi phục (không còn là việc chờ làm). Không ghi `D:\`.

### RF-02 — Low — Bằng chứng AC-02 chưa có output gốc

- **File:** report fix round 1 của Codex (mới).
- **Problem:** AC-02 yêu cầu "ảnh chụp hoặc output ô `pd.read_csv(...).shape`". Report hiện chỉ diễn giải kết quả; không có output ô gốc.
- **Evidence:** `codex_implementation_T00_2026-10-04.md` mục AC-02 chỉ có câu tóm tắt; không có file ảnh hay khối output nào trong repo.
- **Expected Fix:** Trong report fix, dán nguyên văn output ô Colab Tín đã chạy (đường dẫn file, `shape`, `value_counts` của `has_negative`, dòng kiểm `error_analysis`/`notebook_A`), ghi ngày chạy. Không commit ảnh lớn hay notebook.

### RF-03 — Low — Model card ghi sai biến thể PhoBERT

- **File:** `ml/model_card_A.md` dòng 11.
- **Problem:** Ghi "PhoBERT-base", nhưng `ml/artifacts/phobert_A.json` ghi `"model": "vinai/phobert-base-v2"`. Phiên bản pretrained là thông tin bắt buộc khi viết báo cáo khóa luận.
- **Evidence:** `ml/artifacts/phobert_A.json` (ngoài Git): `"task": "A", "model": "vinai/phobert-base-v2"`.
- **Expected Fix:** Ghi `vinai/phobert-base-v2`. Có thể thêm một dòng kết quả gốc từ `phobert_A.json` (dev macro-F1 0,9176 epoch 6; test macro-F1 0,9128, acc 0,9141) để phân biệt với F1 lớp tiêu cực 0,9178. Chỉ sửa model card.

## 6. Ghi nhận cho PO (không phải RF, không chặn)

1. **Hai checkpoint model A:** chênh lớn nhất giữa hai bản chỉ 0,0048 trên mỗi trọng số, nên nhiều khả năng là hai checkpoint gần nhau của **cùng một lần train** (khác bước/epoch), không phải hai model độc lập. Mốc lịch sử ở BOI_CANH mục 5 cũng lẫn: câu "Phim dài lê thê, nửa đầu buồn ngủ thật sự" ghi 0,944 (gần bản gốc 0,960, bản backend chỉ 0,049), còn câu "Phim dài lê thê, xem mà mệt" ghi 0,01 (gần bản backend 0,012, bản gốc 0,388). Vì vậy chưa biết F1 0,9178/0,9180 đã đo trên bản nào. Đề xuất PO: trước T02 cho đo F1 test của **cả hai** bản trên `test.csv` với `normalize()` hiện tại (CPU chạy được ~2.224 câu), rồi chọn bản. Không thay model backend trong T00.
2. **`normalize()` khác `text_utils.py` 9/10 câu**, trong đó có teencode (`bthg`, `cx`, `thik`, `hông`, `okie`), URL và ký tự lặp. Nếu model A train trên `text_norm` sinh từ `src/common.py` (giống `text_utils.py`), thì backend đang suy luận với chuẩn hóa khác lúc train. Đo ở T02 như Task Record đã định.
3. Chưa đối chiếu hash `ml/src/*.py` với nguồn ổ D vì ổ D đã ngừng dùng; chấp nhận theo report Codex. Nội dung khớp `ml/README_goc.md` và hai JSON kết quả.
4. `HUONG_DAN.md` 4.2: khối `.env` và hai gạch đầu dòng đổi thụt lề từ 3 lên 4 dấu cách. Markdown vẫn hiển thị được, chỉ là thay đổi thừa.
5. `ml/src/train_phobert.py` vẫn `pip install ... underthesea` và import `underthesea`; README đã ghi là mã lịch sử. Hợp lệ với T00 (AC-06 chỉ áp cho requirements và HUONG_DAN).

## 7. Trạng thái sau review

- T00: `CLAUDE_REVIEW` → **`FIX_LOOP`**. Codex sửa RF-01 → RF-03, viết `reports/YYYY-MM-DD/codex_fix_T00_round1_YYYY-MM-DD.md`, chuyển lại `CLAUDE_REVIEW`.
- FAIL nên **không mở task kế tiếp** (T01 giữ `PLANNED`).
- Claude không merge, không tag, không approve, không đóng T00.
