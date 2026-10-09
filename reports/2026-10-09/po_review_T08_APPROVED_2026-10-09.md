# PO Review — T08 — APPROVED — 09/10/2026

| Trường | Giá trị |
|---|---|
| Task | T08 — Đo lệch miền điện thoại → phim |
| Branch | `task/T08-lech-mien` |
| PO / Approver | Tín |
| Claude | `PASS_WITH_TODO` |
| Quyết định PO | **APPROVED** |
| Trạng thái workflow | `PO_APPROVED / PENDING_MERGE` |
| Đổi schema | Không |

## 1. Quyết định

PO chấp nhận kết quả review độc lập của Claude:

- Claude: **PASS_WITH_TODO**.
- Acceptance Criteria: **5/5 PASS**.
- Definition of Done: **MET theo quyết định PO**.
- Open Required Fixes: **0**.
- Blockers: **0**.
- Independent CPU reproducibility: **PASS 4/4 model**.
- Artifact reproducibility: **3/3 byte-identical**.
- Scope/Security: **PASS**.

T08 được **APPROVED** và sẵn sàng để PO merge vào `master`. Approval này không có nghĩa task đã merge hoặc `DONE / CLOSED`.

## 2. Evidence được chấp nhận

- Implementation được review: `47e044e` (`[T08] Measure phone-to-movie domain shift`).
- Claude review report: `reports/2026-10-09/claude_review_T08_PASS_WITH_TODO_2026-10-09.md`.
- Commit ghi Claude review và chuyển workflow sang `PO_REVIEW`: `621b75c`.
- Metric độc lập khớp CSV với sai lệch tối đa `4,92e-07`.
- PhoBERT A research, SVM A, Logistic Regression A và Naive Bayes A đều tái lập thành công trên CPU.
- `domain_shift.csv`, `domain_shift_errors.md` và `domain_shift_f1.png` được tái tạo giống từng byte.
- Normalize parity: 2.373/2.373 câu; không đọc `movie_train.csv`, không fit model, không đổi `normalize()`.

## 3. TODO disposition

| TODO | Quyết định PO | Ghi chú |
|---|---|---|
| TODO-01 | **ACCEPT_LATER → T09/khóa luận** | Trình bày `F1_neg` cùng `Macro-F1` và baseline dự đoán hằng “mọi câu đều tiêu cực”. F1_neg movie của ba baseline xấp xỉ baseline hằng; Macro-F1 phản ánh lệch miền rõ hơn. |
| TODO-02 | **ACCEPT_WITH_DISCLOSURE** | Ghi rõ movie test chỉ có 149 câu và CI 95% của ΔF1_neg. T09 phải dùng cùng `movie_test.csv` để so sánh A/B công bằng. |
| TODO-03 | **ACCEPT_LATER → T09/T13** | Cải thiện notebook portability và hướng dẫn cwd: chạy kernel từ gốc repo hoặc clone đúng `/content/firefly-cinema`; T09 nên dò thêm các parent path. |
| TODO-04 | **ACCEPT_WITH_NOTES → T13** | PO chấp nhận evidence tái lập độc lập, chưa bắt buộc sửa notebook T08 hoặc chạy Colab. Bằng chứng Drive/Colab vẫn còn thiếu; T13 cần bổ sung đường dẫn notebook/artifact và hướng dẫn môi trường: Python 3.13.2 hệ thống cho pandas/NumPy/scikit-learn/joblib/matplotlib, ghép `backend\venv\Lib\site-packages` qua `PYTHONPATH` cho torch/transformers, cwd ở gốc repo. |
| TODO-05 | **ACCEPT_LATER → T09/T10** | Giữ nguyên `normalize()`; T09/T10 phải kiểm tra tính đồng nhất giữa preprocessing train, eval và runtime, đặc biệt với câu “lê thê”. |

Toàn bộ **5/5 TODO đã có disposition**. Các TODO `ACCEPT_LATER` và `ACCEPT_WITH_NOTES` được chấp nhận cho merge T08 nhưng **chưa RESOLVED**; chỉ task đích hoặc evidence bổ sung sau này mới được đóng chúng.

## 4. Giới hạn phương pháp được chấp nhận

- Movie test có 149 câu và tỷ lệ nhãn tiêu cực 67,8%, khác phone test 55,9%; phải công bố F1_neg, Macro-F1 và baseline hằng cùng nhau.
- Bootstrap 2.000 lần cho CI 95% của ΔF1_neg có cận dưới `0,010–0,023`, thấp hơn ngưỡng `0,03`; hướng giảm vẫn vững với `P(Δ ≤ 0) ≤ 1%` cho cả bốn model.
- 20 lỗi là mẫu chọn có chủ đích, không phải ước lượng tần suất lỗi của toàn tập.
- T09 dùng cùng movie test và không dùng test để chọn hyperparameter.

## 5. Scope, security và merge readiness

- T08 không sửa production code, schema, dependency, checkpoint, model artifact hoặc dữ liệu.
- Scope/secret/large-file checks: PASS.
- Working tree sạch trước khi tạo PO report.
- `master` (`5cf4eb0`) là ancestor của tip nhánh T08.
- T08 ở trạng thái **PO_APPROVED / PENDING_MERGE**.
- T08 không có tag mốc. Codex không tự merge hoặc gắn tag.

Lệnh merge dành cho PO:

```powershell
git checkout master
git merge task/T08-lech-mien
```

Sau merge, phải xác minh commit merge chứa toàn bộ lịch sử T08 rồi mới cập nhật T08 thành `DONE / CLOSED`.

## 6. Task kế tiếp

T09 giữ **PLANNED / NOT AUTHORIZED**. Không chuyển `READY_FOR_HANDOFF`, không tạo nhánh và không bắt đầu T09 trong lần cập nhật này.
