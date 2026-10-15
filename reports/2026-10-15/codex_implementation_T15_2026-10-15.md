# Codex Implementation Report — T15

- Ngày thực nghiệm: 15/10/2026
- Ngày hoàn tất đồng bộ: 16/10/2026
- Nhánh: `task/T15-tach-tu`
- Đổi schema: Không
- Phạm vi: chỉ notebook/artifact ML; không sửa `normalize()`, backend hoặc frontend.

## Bảng F1 có/không tách từ

| Biến thể | Tập test | Precision tiêu cực | Recall tiêu cực | F1 tiêu cực | Macro-F1 |
|---|---|---:|---:|---:|---:|
| Không tách từ | Phone | 0,894419 | 0,954143 | 0,923316 | 0,909237 |
| Không tách từ | Movie | 0,934066 | 0,841584 | 0,885417 | 0,838935 |
| Có tách từ | Phone | 0,906250 | 0,933226 | 0,919540 | 0,907043 |
| Có tách từ | Movie | 0,952381 | 0,792079 | 0,864865 | 0,821813 |

- Delta F1 tiêu cực (có − không), phone: `-0,003776`.
- Delta F1 tiêu cực (có − không), movie: `-0,020552`.
- Thời gian tách từ tăng thêm: `1,712811 ms/câu` (median ba lượt trên 2.373 câu).

## Thiết kế và gate

- Hai biến thể cùng `vinai/phobert-base-v2`, seed 42, `max_length=256`, batch 8, learning rate `2e-5`, weight decay 0,01, warmup 10%, tối đa 5 epoch và early stopping patience 2.
- Train/dev dùng split phone chính thức; phone test 2.224 câu và movie test 149 câu chỉ được đọc sau `SELECTION_LOCKED`.
- `normalize()` notebook khớp runtime 20/20 câu; tách từ áp dụng đúng sau normalize.
- Hai lượt FP16 ban đầu bị loại vì max delta `0,009365`.
- Hai clean-run FP32 deterministic từ runtime Colab T4 mới đạt `CLEAN_RUN_REPRODUCIBILITY_MAX_DELTA = 0,0`.
- Kết quả lưu tại `MyDrive/thesis_results/T15/`; checkpoint lưu tại `MyDrive/thesis_results/T15_word_segment/`.

## Kết luận

Không nên đưa bản tách từ vào web ở thời điểm này: F1 không tăng trên cả phone lẫn movie và phát sinh thêm chi phí tiền xử lý. Không thay model production, không sửa `normalize()` và không thêm `underthesea` vào backend.

Implementation được chuyển sang `CLAUDE_REVIEW`; Codex không tự review và không tự PASS.
