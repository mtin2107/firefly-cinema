# Claude Independent Review — T15 Thử nghiệm có tách từ

- Ngày: 16/10/2026
- Nhánh: `task/T15-tach-tu`, tip `ca0fd8f` (base `c3f70df`)
- Loại task: ML (Colab), chạy song song với T20
- Kết luận: **PASS_WITH_TODO**
- Required Fixes: 0 · TODO: 4 (Low) · OBS: 2 · Blocker: 0

## 1. Phạm vi

`git diff --stat master...task/T15-tach-tu`: 5 file, đều trong Allowed Files của `docs/tasks/T15.md`.

| File | Ghi chú |
|---|---|
| `ml/notebooks/T15_word_segment.ipynb` | Notebook mới, 8 code cell |
| `ml/results/word_segment.csv` | 4 dòng kết quả |
| `ml/model_card_A.md` | Thêm mục T15 |
| `reports/2026-10-15/codex_implementation_T15_2026-10-15.md` | Report Codex |
| `docs/TASK_COORDINATION_ACTIVE.md` | Chỉ dòng T15 |

Không đụng `backend/`, `frontend/`, `data/`. Không có model, checkpoint hay dữ liệu lớn trong Git. Không sửa `normalize()`, không thêm `underthesea` vào backend.

## 2. Acceptance Criteria

| AC | Kết quả | Bằng chứng |
|---|---|---|
| AC-01 Cùng chia, seed, siêu tham số | PASS | Hai biến thể train trong cùng một hàm `train_variant`, cùng `seed_everything()`, cùng `torch.Generator` cho thứ tự batch, cùng `vinai/phobert-base-v2`, max_length 256, batch 8, LR 2e-5, WD 0,01, warmup 10%, 5 epoch, patience 2, FP32 deterministic. Chỉ khác hàm tiền xử lý. |
| AC-02 CSV có F1 hai bản trên hai tập test | PASS | `word_segment.csv` đủ 4 cặp (variant × phone/movie). |
| AC-03 Thời gian tiền xử lý thêm | PASS | `1,712811 ms/câu`, median 3 lượt trên 2.373 câu; khớp hiệu `1,738582 − 0,025772`. |
| AC-04 Kết luận có nên đưa vào web | PASS | "Không nên đưa vào web", nêu đánh đổi F1 và chi phí. |

## 3. Gate ML (AGENT_RULES mục 3.2)

| Gate | Kết quả |
|---|---|
| Đúng cách chia | PASS. Train/dev chính thức (assert 7.786 / 1.112 dòng). Phone test (2.224; 981/1.243) và movie test (149; 48/101) chỉ được `read_csv` sau `assert locked['test_loaded'] is False` và marker `SELECTION_LOCKED`. Checkpoint chọn bằng dev macro-F1 rồi F1 tiêu cực. |
| Đúng tiền xử lý | PASS. Import `normalize` từ `ml/src/eval_utils.py` và đối chiếu `backend.app.classifier.normalize` trên 20 câu, assert 20/20. Tách từ áp dụng sau normalize. |
| Tái lập | **PO_ATTESTED** (xem TODO-01). Report ghi 2 clean-run FP32 lệch `0,0`; FP16 bị loại vì lệch `0,009365`. Code có assert ≤ 0,001 so với `word_segment_previous_fp32.csv` trên Drive. Claude không chạy được GPU. |
| Kết quả nhỏ vào Git | PASS. Chỉ CSV và Markdown; checkpoint ở `MyDrive/thesis_results/T15_word_segment/`. |
| Cú pháp notebook | PASS. JSON hợp lệ, 8/8 code cell parse được bằng `ast`. |

### Kiểm nhất quán số liệu độc lập

Suy ngược ma trận nhầm lẫn từ Precision/Recall và số câu mỗi lớp. Cả 4 dòng đều ra số nguyên chính xác; F1 tiêu cực, macro-F1 và delta khớp đến 6 chữ số:

| Biến thể | Test | TP | FP | FN | TN | F1 tiêu cực | Macro-F1 |
|---|---|---:|---:|---:|---:|---:|---:|
| Không tách | Phone | 1186 | 140 | 57 | 841 | 0,923316 | 0,909237 |
| Không tách | Movie | 85 | 6 | 16 | 42 | 0,885417 | 0,838935 |
| Có tách | Phone | 1160 | 120 | 83 | 861 | 0,919540 | 0,907043 |
| Có tách | Movie | 80 | 4 | 21 | 44 | 0,864865 | 0,821813 |

Delta F1 tiêu cực: phone `−0,003776`, movie `−0,020552`, đều khớp report.

## 4. TODO (không chặn)

| ID | Mức | Vấn đề | Đề xuất |
|---|---|---|---|
| TODO-01 | Low | Notebook trong Git **không có output**. Bằng chứng tái lập (lệch 0,0; FP16 lệch 0,009365) chỉ nằm trên Drive, Claude không kiểm được. | Ở PO review, Tín mở `MyDrive/thesis_results/T15/` và xác nhận có `selection_manifest.json` (`precision: fp32_deterministic`, `test_loaded: true`) và `word_segment_previous_fp32.csv` trùng CSV trong Git. Ghi `PO_ATTESTED`, giống T09 TODO-02. |
| TODO-02 | Low | Biến thể có tách từ đạt tốt nhất ở `best_epoch = 5`, đúng bằng trần epoch, nên có thể còn tăng nếu train thêm. Bản không tách dừng ở epoch 4. | Khi viết khóa luận ghi kết luận là "trong cùng ngân sách 5 epoch", không khẳng định tách từ kém hơn về bản chất. |
| TODO-03 | Low | Một seed. Movie test chỉ 149 câu: delta −0,0206 tương ứng 5 câu tiêu cực bị bỏ sót thêm trên 101 câu. Phone delta −0,0038 cũng nhỏ. | Viết là "tách từ **không cải thiện** F1", tránh "làm giảm rõ rệt". Đủ để kết luận không đưa vào web. |
| TODO-04 | Low | Phiên bản `underthesea==9.5.0` (đã đổi từ 6.8.4 ở commit đầu) chỉ có trong notebook, chưa ghi vào report hay model card. T15 dùng FP32 còn T09 dùng FP16, nên số "không tách từ" của T15 (phone F1 0,9233) **không phải** số của model đang chạy trên web. | T13 ghi rõ hai điểm này trong README/model card khi trích kết quả T15. |

## 5. Observations

- **OBS-01:** Một bản sao `reports/2026-10-15/codex_implementation_T15_2026-10-15.md` đang **untracked trong working tree của nhánh T20**. Nội dung giống hệt bản trên nhánh T15. Cần xóa bản này trước khi Codex commit T20, nếu không file T15 sẽ lọt vào commit T20 (ngoài allowlist).
- **OBS-02:** Nhánh T15 và T20 cùng sửa `docs/TASK_COORDINATION_ACTIVE.md`, ở các dòng khác nhau. Khi merge, nếu xung đột thì giữ cả hai.

## 6. Kết luận

**PASS_WITH_TODO.** Thiết kế đối chứng chặt chẽ, tập test được khóa đúng, số liệu nhất quán tuyệt đối khi kiểm ngược. Kết luận "không đưa tách từ vào web" có căn cứ. T15 chuyển `CLAUDE_REVIEW → PO_REVIEW`.

**Task kế tiếp:** không mở thêm. T20 đang `IN_PROGRESS` (Codex). T12 phụ thuộc T20 nên chưa đủ điều kiện `READY_FOR_HANDOFF`.

## 7. Việc của Tín

1. PO review T15: xác minh TODO-01 trên Drive, disposition TODO-01..04 (đề xuất: TODO-01 PO_ATTESTED; TODO-02..04 ACCEPT_LATER → T13 và chương kết quả khóa luận).
2. Merge T15 **sau khi Codex commit xong T20** để không đổi nhánh giữa chừng:
   ```
   git checkout master
   git merge --no-ff task/T15-tach-tu -m "[T15] Merge word segmentation experiment"
   ```
3. Xóa bản sao report T15 untracked trên nhánh T20 (OBS-01).
