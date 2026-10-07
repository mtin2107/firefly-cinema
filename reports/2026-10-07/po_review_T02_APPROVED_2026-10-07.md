# Product Owner Review T02 — APPROVED — 07/10/2026

## 1. Task

T02 — So sánh PhoBERT với mô hình truyền thống.

Branch:

`task/T02-so-sanh-A`

Reviewed implementation commit:

`86a4e9a` — `[T02] Fix Claude review round 1`

Claude Review Round 2:

`PASS_WITH_TODO`

## 2. Product Owner Decision

**APPROVED**

- Acceptance Criteria: **6 / 6 PASS**
- Required Fixes: **0**
- Open Blockers: **0**
- Definition of Done: **MET**
- RF-01: **CLOSED**
- RF-02: **CLOSED**

T02 đủ điều kiện merge vào `master` và đóng task theo workflow dự án.

## 3. Checkpoint disposition

Hai checkpoint PhoBERT A đã được đo lại trên cùng UIT-ViSFD test, cùng metric và cùng preprocessing contract.

### Canonical checkpoint cho nghiên cứu / luận văn / bảng so sánh T02

`ml/artifacts/phobert_A_best`

Kết quả `text_norm`:

- Precision negative: `0.916468`
- Recall negative: `0.926790`
- F1 negative: `0.921600`
- Macro-F1: `0.910492`
- Accuracy: `0.911871`

PO chọn checkpoint này làm **canonical research checkpoint của Model A** vì:

1. Đây là checkpoint được sử dụng trong `comparison_A.csv`.
2. Kết quả được Codex và Claude đo lại độc lập và tái lập.
3. F1 negative `0.921600` cao hơn checkpoint backend `0.917808` khi đo trên cùng điều kiện.

### Checkpoint backend hiện tại

`backend/models/phobert-binhluan`

Kết quả `text_norm`:

- F1 negative: `0.917808`

Checkpoint này tiếp tục được giữ nguyên cho runtime web hiện tại.

**Không thay checkpoint backend trong T02.**

Nếu dự án quyết định đồng bộ runtime web sang canonical checkpoint `ml/artifacts/phobert_A_best`, việc thay model phải được thực hiện trong một task riêng có regression test và review riêng.

## 4. Historical metric disposition

Các metric cũ trong `phobert_A.json` được giữ lại với trạng thái:

**HISTORICAL / NOT FULLY REPRODUCED**

Không xóa dữ liệu lịch sử.

Tuy nhiên, các số này không được dùng làm metric canonical cho phần so sánh mô hình trong luận văn.

Metric canonical cho T02 là kết quả được đo lại và xác minh độc lập trong T02.

## 5. TODO disposition

### TODO-R2-01 — Chọn checkpoint chính thức

**RESOLVED**

Canonical research checkpoint:

`ml/artifacts/phobert_A_best`

Backend checkpoint hiện tại:

`backend/models/phobert-binhluan`

Không thay backend trong T02.

### TODO-R2-02 — Runtime/PYTHONPATH chưa nằm trong model card/HUONG_DAN

**ACCEPT_LATER → T13**

Khi hoàn thiện tài liệu:

- bổ sung interpreter;
- bổ sung `PYTHONPATH`;
- bổ sung lệnh chạy tái lập;
- cập nhật ngày benchmark trong model card.

Không chặn T02.

### TODO-R2-03 — Category index 72 và 136 còn tranh luận

**WONT_FIX**

Đây là khác biệt diễn giải thủ công trong error analysis, không ảnh hưởng prediction, metric, Acceptance Criteria hoặc kết luận của T02.

### Metric lịch sử `phobert_A.json`

**ACCEPT_LATER / DOCUMENTED**

Giữ dưới nhãn historical metric, không dùng làm canonical metric.

## 6. Final PO status

Task:

`T02`

Product Owner Review:

**APPROVED**

Required Fixes:

`0`

Blockers:

`0`

Task disposition:

**READY_TO_MERGE**

Sau khi merge và tag thành công:

**DONE / CLOSED**

Required tag:

`ml-baselines`

Không thực hiện thêm thay đổi model trong T02.
