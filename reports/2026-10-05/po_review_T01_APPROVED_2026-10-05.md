# Product Owner Review — T01

Task: `T01 — Mô hình truyền thống (NB, LR, SVM)`

Date: `2026-10-05`

Product Owner: `Lê Minh Tín`

## Review Result

**APPROVED**

Claude Independent Review Result: `PASS_WITH_TODO`

Acceptance Criteria: `AC-01 → AC-06 PASS`

Definition of Done: `MET`

Required Fixes: `0`

Open Blockers: `0`

## TODO Disposition

### TODO-01 — Baseline `.joblib` chưa có trên Google Drive

**Disposition: ACCEPT_WITH_ACTION**

Ba artifact:

- `nb_A.joblib`
- `lr_A.joblib`
- `svm_A.joblib`

phải được sao chép lên:

`MyDrive/thesis_results/baselines/`

trước khi bắt đầu implementation T02 trên Colab.

TODO này không chặn PO approval của T01 nhưng phải hoàn thành trước T02.

### TODO-02 — `baselines.py` được viết lại và bỏ phần baseline B/C cũ

**Disposition: ACCEPT**

PO chấp nhận thay đổi.

Lý do:

- implementation mới đáp ứng đầy đủ AC của T01;
- không có leakage từ test;
- pipeline đáp ứng yêu cầu lưu/load `.joblib`;
- các metric tái lập chính xác;
- mã cũ vẫn còn trong lịch sử Git tại baseline T00.

Không yêu cầu sửa lại T01.

### TODO-03 — `EXPECTED_SPLITS` cố định cho UIT-ViSFD

**Disposition: ACCEPT_LATER — T09**

T01 chỉ phục vụ baseline phần A trên UIT-ViSFD nên hard-code split hiện tại được chấp nhận.

T09 phải tham số hóa hoặc thay cơ chế kiểm tra split khi sử dụng dữ liệu phim.

### TODO-04 — `ms_per_sentence` dùng `process_time`

**Disposition: ACCEPT_LATER — T02**

T01 giữ nguyên kết quả hiện tại.

T02 phải đo lại thời gian CPU của PhoBERT A, SVM, LR và NB bằng cùng một phương pháp, ưu tiên `time.perf_counter`, và ghi rõ cấu hình máy để đảm bảo so sánh công bằng.

## Final Decision

`T01 = PO_APPROVED`

Required Fixes: `0`

Task-level blockers: `0`

T01 được phép merge vào `master`.

Sau khi:

1. upload ba `.joblib` lên Google Drive;
2. merge `task/T01-mo-hinh-truyen-thong` vào `master`;

PO cho phép tạo nhánh:

`task/T02-so-sanh-A`

từ `master` mới nhất.

Không bắt đầu implementation T02 trước khi hoàn tất hai bước trên.

## Closure Status

Sau khi merge thành công:

`T01 = DONE / CLOSED`

`T02 = READY_FOR_HANDOFF`
