# Claude Review Round 2 — T07 — Đa mô hình và trang So sánh mô hình — PASS_WITH_TODO — 09/10/2026

| Trường | Giá trị |
|---|---|
| Reviewer | Claude (Independent Reviewer / Tester) |
| Branch | `task/T07-da-mo-hinh` |
| Commits | `e84820d` implementation · `6a56818` handoff · `4002b12` Claude Round 1 FAIL · `06fbd3d` fix RF-01 · `ebc699a` fix report + coordination |
| Round 1 | `reports/2026-10-09/claude_review_T07_FAIL_2026-10-09.md`: FAIL, RF-01 (Medium, AC-05) |
| Codex fix report | `reports/2026-10-09/codex_fix_T07_round1_2026-10-09.md` (chỉ là bằng chứng phụ) |
| Kết luận | **PASS_WITH_TODO** |
| Chuyển trạng thái | T07 `CLAUDE_REVIEW` → `PO_REVIEW` |

## 1. Pre-flight

| Kiểm tra | Kết quả |
|---|---|
| Đúng branch `task/T07-da-mo-hinh` | Đạt |
| Working tree sạch trước review | Đạt |
| Đủ 5 commit T07 trong lịch sử branch (thứ tự đúng) | Đạt |
| Fix commit `06fbd3d` chỉ đổi production file `backend/app/schemas.py` (+1/−1) | Đạt |
| `4002b12..HEAD` chỉ gồm `schemas.py`, `TASK_COORDINATION_ACTIVE.md` và fix report | Đạt |
| `master...HEAD` vẫn 20 file, đều nằm trong allowlist T07 (cộng các report T07) | Đạt |
| Không track `.db`, `.joblib`, `backend/models/`, `ml/artifacts/`, `.env` | Đạt |

## 2. RF-01 verification

**Diff:** `text: str = Field(min_length=1, max_length=1000)` → `text: str = Field(max_length=1000)`. Validator `strip()` và câu tiếng Việt giữ nguyên. Chuỗi rỗng giờ đi vào validator, đúng nguyên nhân gốc mà Round 1 đã nêu.

**Probe độc lập:** chạy trên uvicorn thật, SQLite tạm trong scratchpad, cổng 8021, đủ 4 model. Không dùng TestClient như Codex.

| # | Input / ca | Kỳ vọng | Thực tế |
|---:|---|---|---|
| 1 | `{"text":""}` (admin) | 422 tiếng Việt | **422** `Trường 'text' không hợp lệ: Nội dung cần chấm điểm không được để trống.`, không còn `String should…` |
| 2 | `{"text":"   "}` | 422 tiếng Việt | **422**, cùng câu |
| 3 | `{"text":"\n\t"}` | 422 tiếng Việt | **422**, cùng câu |
| 4 | `"Ko hay như quảng cáo, hơi thất vọng"` | 200 | **200**, `phobert/svm/lr/nb`, mỗi item đúng 5 key `model, version, label, score, ms` (PhoBERT 0.9937, SVM 0.8205, giống Round 1) |
| 5 | 1.000 ký tự | 200 | **200**, 4 model, đủ 5 key |
| 6 | 1.000 ký tự có khoảng trắng hai đầu | 200 | **200** |
| 7 | 1.001 ký tự | 422 | **422** (`String should have at most 1000 characters`, thuộc TODO-04) |
| 8 | 1 ký tự `"x"` | 200 | **200** |
| 9 | Không token | 401 | **401** "Bạn cần đăng nhập để tiếp tục." |
| 10 | User thường | 403 | **403** "Chỉ quản trị viên mới xem được trang này." |
| 11 | `GET /api/health` | 200, đủ model | **200**, `phobert/svm/lr/nb/keyword` loaded, `active_model=phobert` |
| 12 | Bình luận "Ko hay như quảng cáo…" | Tiêu cực ~0,99 | **201**, `effective_negative=true`, 0.9937 |

Kết quả assert: **12/12 PASS**. Ghi nhận thêm (không phải RF): thiếu `text` hoặc `null` vẫn trả 422 với câu Pydantic tiếng Anh. Lỗi này thuộc TODO-04, đã có từ Round 1.

**RF-01: CLOSED / VERIFIED BY CLAUDE.**

## 3. Acceptance Criteria

| AC | Kết quả | Căn cứ |
|---|---|---|
| AC-01 | PASS | Round 1 + Round 2: health liệt kê PhoBERT/SVM/LR/NB `loaded:true` |
| AC-02 | PASS | Round 1 (đổi tên bản chép SVM: startup ổn, health `loaded:false`, predict bỏ SVM). `classifier.py`, `config.py`, `main.py` không đổi từ Round 1 |
| AC-03 | PASS | Round 1: 10 câu lệch ≤ 4,9e-5, nhãn 10/10; 2.224 câu test khớp tuyệt đối F1 T02. Code suy luận không đổi; Round 2 cho cùng score 0.9937/0.8205 |
| AC-04 | PASS | Hash đoạn `_ABBR`…`normalize()` ở `master` = `HEAD` = `270e12ef…0d76` |
| AC-05 | **PASS** | RF-01 đã đóng: 401/403/422 tiếng Việt cho cả ba dạng rỗng |
| AC-06 | PASS | Round 1: `ACTIVE_MODEL=svm` → `model_name="svm"`; fallback đúng |
| AC-07 | PASS | Round 1 (real/mock, 375px, loading/lỗi, ms). Frontend không đổi: build Round 2 ra cùng hash bundle `index-qNb2kX2q.js` như Round 1 |
| AC-08 | PASS | Round 1 hồi quy 7/7. Round 2 kiểm lại mục 5 và 6 (bình luận tiêu cực 0.9937 phobert, health `classifier=phobert`) |

**AC 8/8 PASS.**

## 4. Definition of Done

| Mục | Trạng thái |
|---|---|
| Đủ AC 8/8 | Đạt |
| Gate web (compile, startup + health, build, mock) | Đạt |
| Hồi quy 7/7 | Đạt (Round 1, cộng xác minh lại mục 5 và 6) |
| Scope / allowlist, không có file cấm | Đạt |
| Không có secret, DB, model | Đạt |
| Tài liệu | Đạt (không đổi từ Round 1) |
| Report Codex | Đạt: fix report mô tả đúng diff và nguyên nhân; bảng 10 ca khớp kết quả độc lập |

**DoD: MET** (còn TODO không chặn, chờ PO disposition).

## 5. Final independent gates

| Gate | Kết quả |
|---|---|
| `backend\venv\Scripts\python -m compileall -q backend\app` | PASS |
| Uvicorn startup + `/api/health` (DB tạm) | PASS, HTTP 200 |
| `cd frontend; npm run build` | PASS (791 ms, bundle hash không đổi) |
| Focused regression RF-01 | 12/12 PASS |
| `git diff --check master...HEAD` | PASS |
| Secret scan (`4002b12..HEAD`) | PASS: chỉ khớp chữ "Secret scan" trong report/coordination |
| `normalize()` / `_ABBR` | Không đổi |
| Checkpoint / artifact | `svm_A.joblib` SHA256 `51d061fb…` không đổi; `classifier.py` không đổi từ Round 1 |
| Database schema | `models.py`, `database.py` không đổi; không cần xóa `firefly.db` |
| DB thật | `backend/firefly.db` SHA256 `ed3abdba…` không đổi, không bị ghi |
| pytest | Không áp dụng (bắt buộc từ T11) |

## 6. Security

- Phân quyền không đổi: 401 không token, 403 user thường, chỉ admin chạy inference.
- Giới hạn 1.000 ký tự vẫn còn, nên không mở rộng bề mặt DoS.
- Fix không thêm dependency, không đổi contract response.

## 7. Regression

Fix chỉ bỏ ràng buộc `min_length` trong schema riêng của endpoint mới. Schema khác, router, classifier và frontend không đổi. Không phát hiện regression liên quan. Hồi quy 7/7 của Round 1 vẫn hiệu lực; mục 5 và 6 đã chạy lại và đạt.

## 8. Scope

Fix đúng phạm vi RF-01: một dòng trong `backend/app/schemas.py`. Toàn branch 20 file, đều nằm trong allowlist Task Record T07 mục 6 cộng các report T07. Không có đường dẫn `D:\`.

## 9. Required Fixes

| RF | Severity | Trạng thái |
|---|---|---|
| RF-01 — `text` rỗng trả 422 tiếng Anh (AC-05) | Medium | **CLOSED / VERIFIED BY CLAUDE** (fix `06fbd3d`) |

**Open Required Fixes: 0.**

## 10. TODO Round 1 (giữ nguyên, chờ PO disposition; không tự đánh dấu RESOLVED)

| ID | Mức | Nội dung | Đề xuất |
|---|---|---|---|
| TODO-01 | Medium (demo) | Câu mẫu "lê thê": PhoBERT backend 0,0485 (bình thường), checkpoint research `phobert_A_best` 0,9602 (tiêu cực) | PO chọn: giữ để minh họa lệch miền (T08–T10) hoặc thay checkpoint runtime ở task riêng |
| TODO-02 | Low | `/api/admin/predict` không cô lập exception theo từng model (một model lỗi → 500) | T11 |
| TODO-03 | Low | Health công khai trả lỗi thô (đường dẫn tuyệt đối, `"110"` khi joblib hỏng) | T11/T13 |
| TODO-04 | Low | 422 khi thiếu `text`, `null`, sai kiểu, quá 1.000 ký tự còn câu Pydantic tiếng Anh (xác nhận lại ở Round 2) | Gộp TODO-01 T06 → T11 |
| TODO-05 | Low | Health không có trường riêng cho `ACTIVE_MODEL` được yêu cầu khi fallback | T10 |
| TODO-06 | Info | Report implementation ghi AC-05 PASS khi chưa thử `""` | Process: ghi đủ ca biên AC |

## 11. Final Decision

**PASS_WITH_TODO.** RF-01 CLOSED / VERIFIED BY CLAUDE. AC 8/8 PASS, DoD MET, Open Required Fixes 0, blocker 0. Còn 6 TODO không chặn chờ PO disposition, trong đó TODO-01 cần PO quyết trước demo.

## 12. Workflow Transition

- T07: `CLAUDE_REVIEW` → **`PO_REVIEW`**.
- Claude không approve, merge, tag (`admin-v1`) hay đóng T07.
- **T08 giữ `PLANNED`.** Theo chỉ thị PO cho Round 2, Claude không tự mở T08 và không soạn prompt handoff T08. Khi PO authorize, T08 phụ thuộc T02 và T03 (đều đã CLOSED).
- Nhắc Tín: review PO, disposition 6 TODO, rồi tự merge `task/T07-da-mo-hinh` vào `master` và tag nếu duyệt.
