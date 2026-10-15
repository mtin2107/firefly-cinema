# Codex Implementation Report — T15

- Ngày: 2026-10-15
- Nhánh: `task/T15-tach-tu`
- Đổi schema: Không
- Trạng thái: `IN_PROGRESS — PENDING COLAB CLEAN-RUN`

## Phạm vi đã triển khai

- Tạo notebook `ml/notebooks/T15_word_segment.ipynb` cho cặp đối chứng có/không tách từ.
- `underthesea==6.8.4` chỉ được cài trong Colab; không thêm dependency backend.
- Không sửa `normalize()`, không sửa `backend/` hoặc `frontend/`.
- Hai biến thể cùng model khởi tạo, split, seed và siêu tham số; phone/movie test chỉ đọc sau marker `SELECTION_LOCKED`.
- Notebook tự đo thời gian tiền xử lý tăng thêm, ghi `ml/results/word_segment.csv`, cập nhật mục T15 trong model card A và ghi lại report này sau khi có số thật.

## Bảng F1 có/không tách từ

| Biến thể | Phone F1 tiêu cực | Movie F1 tiêu cực | Phone macro-F1 | Movie macro-F1 |
|---|---:|---:|---:|---:|
| Không tách từ | Chờ Colab | Chờ Colab | Chờ Colab | Chờ Colab |
| Có tách từ | Chờ Colab | Chờ Colab | Chờ Colab | Chờ Colab |

Không điền số suy đoán hoặc dùng metric của checkpoint lịch sử vì như vậy không còn là cặp đối chứng cùng điều kiện train.

## Gate và kết luận tạm thời

- Static notebook/schema gate: sẽ chạy tại local trước handoff.
- Gate tái lập và kết quả F1: cần chạy notebook hai lần từ runtime Colab mới; sai lệch yêu cầu ≤ 0,001.
- Chi phí tách từ mỗi câu: chờ output Colab.
- Chưa có đủ bằng chứng để đề xuất đưa tách từ vào web. Dù kết quả tốt hơn, T15 chỉ đề xuất task tích hợp riêng để PO quyết định.
- Không tự review, không tự PASS và chưa chuyển `CLAUDE_REVIEW`.
