# PO Review — T09 — APPROVED — 09/10/2026

> **BẢN NHÁP — CHỜ TÍN XÁC NHẬN.** Claude soạn hộ PO. Chưa phải quyết định chính thức cho đến khi Tín xác nhận trong chat.

| Trường | Giá trị |
|---|---|
| Task | T09 — Train PhoBERT phần B trên dữ liệu phim |
| Branch | `task/T09-phobert-B` |
| PO / Approver | Tín |
| Người soạn nháp | Claude (hỗ trợ PO) |
| Claude review | `PASS_WITH_TODO` (`273cc2d`) |
| Quyết định PO | **APPROVED** |
| Trạng thái workflow | `PO_APPROVED / PENDING_MERGE` |
| Đổi schema | Không |

## 1. Quyết định

PO chấp nhận kết quả review độc lập của Claude:

- Claude: **PASS_WITH_TODO**.
- Acceptance Criteria: **6/6 PASS**.
- Definition of Done: **MET theo quyết định PO**, kèm một evidence GPU còn PENDING (mục 4).
- Open Required Fixes: **0**.
- Blockers: **0**.
- CPU reproducibility: 14/14 dòng SVM/LR/NB/constant, sai lệch tối đa `0.0`. Hai dòng PhoBERT A khớp T08 đến từng chữ số.
- Normalize parity: 11.618/11.618 câu.
- Scope/Security: **PASS**.

T09 được **APPROVED** và sẵn sàng để PO merge vào `master`. Approval không có nghĩa task đã merge hoặc đã `DONE / CLOSED`.

## 2. Evidence được chấp nhận

- Implementation: `3b6e849`, `c8a0230`, `458a073`. Report: `reports/2026-10-09/codex_implementation_T09_2026-10-09.md`.
- Claude review: `reports/2026-10-09/claude_review_T09_PASS_WITH_TODO_2026-10-09.md`, commit `273cc2d`.
- Gói code chạy trên Colab có nội dung trùng `c8a0230`. Notebook trong Git chỉ khác bản đã chạy một dòng chữ trong template model card.
- Selection dựa trên validation 53 câu: config b, learning rate 2e-5, epoch 3. Test chỉ được đọc sau khi selection đã khóa.
- Movie F1 tiêu cực: A `0.857143`, B `0.917526`, Δ `+0.060383`. Macro-F1: A `0.816502`, B `0.881840`.
- Phone F1 tiêu cực: A `0.919936`, B `0.917153`, Δ(B−A) `−0.002783`. Macro-F1 giảm `0.006849`.
- `comparison_B.csv` SHA-256 `c10e49e4…0209ace`.
- `MODEL_VERSION` đề xuất: `phobert-B-2026-10-09`. Chỉ áp dụng ở T10; T09 không thay model production.

## 3. TODO disposition

| TODO | Quyết định PO | Ghi chú |
|---|---|---|
| TODO-01 (Low) notebook Git 0 output | **ACCEPT_LATER → T13** | T13 tải run2 có output về `ml/notebooks/` hoặc ghi Drive là nguồn evidence chuẩn. |
| TODO-02 (Medium) evidence GPU chưa xác minh độc lập | **ACCEPT_LATER → điều kiện tiên quyết để authorize T10** — trạng thái **PENDING** | Xem mục 4. Không chặn merge T09 vì AGENT_RULES 3.2 cho phép Tín chạy lại phần GPU khi cần. **Không được authorize T10** trước khi mục 4 hoàn tất. |
| TODO-03 (Low) model card thiếu disclosure | **ACCEPT_LATER → T13 / khóa luận** | Cần ghi: (a) SVM/LR/NB B được train lại trên 347+347 câu, PhoBERT B chỉ train trên 294+294; (b) cấu hình b chỉ thắng a 1 câu trên 53 câu validation; (c) model card được chỉnh tay sau khi chạy. |
| TODO-04 (Low) chưa có kiểm định cặp A–B | **ACCEPT_LATER → T10 (sau TODO-02) / khóa luận** | Khi đã có checkpoint ở máy, chạy dự đoán CPU trên 149 câu, tính McNemar/bootstrap CI. Chỉ để báo cáo, không dùng để chọn lại model. |
| TODO-05 (Low, process) T08 TODO bị ghi RESOLVED quá mức | **ACCEPT_WITH_NOTES** | Sửa disposition T08: TODO-01 và TODO-05 **RESOLVED** (Claude đã xác minh); TODO-03 **RESOLVED ở mức code**; TODO-04 giữ **ACCEPT_WITH_NOTES → T13**, chưa RESOLVED; TODO-02 giữ ACCEPT_WITH_DISCLOSURE. Từ nay Codex không tự đổi TODO do PO disposition sang RESOLVED. |
| TODO-06 (Low) GradScaler API cũ, scheduler step | **ACCEPT_LATER → T15** (hoặc lần train lại kế tiếp) | Không retrain T09. |
| TODO-07 (Info) `T09.md` ghi PLANNED | **ACCEPT_WITH_NOTES** | File điều phối là nguồn trạng thái, giống T06 TODO-06. |

Cả **7/7 TODO đã có disposition**. Các TODO `ACCEPT_LATER` và `ACCEPT_WITH_NOTES` được chấp nhận để merge T09 nhưng **chưa RESOLVED**.

## 4. TODO-02 — evidence GPU: **PENDING**

Claude không truy cập được Google Drive: phiên không có connector Drive, máy không có bản tải về, và `ml\artifacts\phobert_B_best\` chưa tồn tại. Claude **không** tuyên bố đã xác minh các mục dưới đây. Hiện chúng chỉ có trong report Codex.

| Mục cần xác minh | Giá trị Codex ghi | Trạng thái |
|---|---|---|
| `model.safetensors` | 540.023.384 B, `0b80947ca8fecffbfaa39373e92d1ed44d638dcb4981ff00da2dd08921d22f4f` | PENDING |
| `config.json` | 948 B, `3af764b446752118aa33982d7983f52919318373ff3108add0128834f28005da` | PENDING |
| `selection_manifest.json` | 2.477 B, `d21786d2354c9ac054155c8975da579cede1fc9d05a18b5949c9716f0fa34035` | PENDING |
| `firefly_phobert_B.zip` (run 2) | 502.655.745 B, `bd7d1544691e0e477ce42b5058cd650d2bf6b957cf335a80398f74bf71c438d1` | PENDING |
| run1/run2: `SELECTION_LOCKED=True` in trước `FINAL_TEST_COMPLETE=True` | — | PENDING |
| CPU reload trên máy Windows, Transformers 5.18.0 | Codex: OK trong Colab | PENDING |

Cách đóng TODO-02 (Tín làm, khoảng 10 phút):
1. Tải `MyDrive/thesis_results/firefly_phobert_B.zip`, giải nén vào `C:\Projects\firefly-cinema\ml\artifacts\phobert_B_best\`. Thư mục này nằm ngoài Git.
2. Chạy `Get-FileHash ml\artifacts\phobert_B_best\model.safetensors, ml\artifacts\phobert_B_best\config.json -Algorithm SHA256` và so với bảng trên.
3. Mở `T09_phobert_B_run1.ipynb` và `_run2.ipynb` trên Drive, xác nhận thứ tự marker.
4. Nhờ Claude chạy nạp lại trên CPU và dự đoán 149 câu movie test. Lần chạy này cũng phục vụ TODO-04 và câu demo "lê thê".

## 5. Definition of Done

| Điều kiện (`_TEMPLATE.md` mục 9) | Kết quả |
|---|---|
| Toàn bộ AC đạt, có bằng chứng | **MET.** AC 6/6; AC-04 dựa trên evidence Colab (xem mục 4). |
| Gate `AGENT_RULES.md` mục 3.2 | **MET theo quyết định PO.** Tái lập CPU và đúng `normalize()` đã được Claude kiểm độc lập; đúng cách chia được Claude kiểm bằng code và probe; model không vào Git. Tái lập GPU dựa trên evidence Drive của Codex, xác minh PENDING. |
| Không có file ngoài allowlist | **MET.** 8 file implementation + 2 file review đều nằm trong allowlist. |
| Tài liệu liên quan | **MET.** `ml/README.md`, `model_card_B.md`. Không đổi kiến trúc hay thư viện nên không cần sửa `ARCHITECTURE.md` hay `CONG_NGHE.md`. |
| Claude PASS/PASS_WITH_TODO + Tín APPROVED | **MET** sau khi Tín xác nhận. |

## 6. Giới hạn phương pháp được chấp nhận

- Movie test có 149 câu, trong đó 67,8 % tiêu cực. Phải công bố F1_neg, Macro-F1 và baseline hằng cùng nhau; B vượt baseline hằng ở cả hai chỉ số.
- Cải thiện trên movie tương ứng +11 TP và −1 TN. Chưa có kiểm định cặp (TODO-04).
- Validation chỉ có 53 câu nên việc chọn cấu hình có phương sai cao.
- Model B chưa vào production. T10 chỉ được dùng đúng artifact có hash đã xác minh ở mục 4.

## 7. Merge readiness

- Working tree sạch. `master` (`6c4b8de`) là ancestor của tip nhánh T09.
- Tag `phobert-B` gắn **cùng T10** theo Task Record, **không** gắn khi merge T09.
- Claude không merge và không gắn tag.

Lệnh merge dành cho PO:

```powershell
git checkout master
git merge --no-ff task/T09-phobert-B
```

Sau khi merge, phải xác minh lịch sử T09 đã nằm trong `master` rồi mới cập nhật T09 thành `DONE / CLOSED`.

## 8. Task kế tiếp

T10 giữ **PLANNED / NOT AUTHORIZED**. Ngoài quyết định riêng của PO, T10 còn có điều kiện tiên quyết là TODO-02 (mục 4) phải hoàn tất.
