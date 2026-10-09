# Claude Review — T09 — PASS_WITH_TODO — 09/10/2026

| Trường | Giá trị |
|---|---|
| Task | T09 — Train PhoBERT phần B trên dữ liệu phim |
| Branch | `task/T09-phobert-B` (HEAD `5c066d9`) |
| Baseline | `6c4b8de6ff4a9811b70acf7c1acd46ee1c6a74f5` (chứa merge T08 `778675e`) |
| Reviewer | Claude (Independent Reviewer / Tester) |
| Kết luận | **PASS_WITH_TODO** |
| AC | 6/6 PASS (phần GPU dựa trên evidence Drive, Claude không truy cập được — xem mục 6) |
| Required Fixes | 0 |
| Blocker | 0 |
| TODO mới | 7 (không chặn) |
| Chuyển trạng thái | T09 `CLAUDE_REVIEW` → `PO_REVIEW`; T10 giữ `PLANNED / NOT AUTHORIZED` theo chỉ định PO |

## 1. Phạm vi đã đọc

`PROJECT_SOURCE_OF_TRUTH.md`, `AGENT_RULES.md`, `TASK_COORDINATION_ACTIVE.md`, `docs/tasks/T09.md`, `reports/2026-10-09/codex_implementation_T09_2026-10-09.md` (và progress report để đối chiếu nguồn evidence), diff thật `6c4b8de...HEAD`, `ml/src/model_b_utils.py`, `ml/notebooks/T09_phobert_B.ipynb` (19 cell), `ml/results/comparison_B.csv`, `ml/model_card_B.md`, `ml/README.md`, `ml/results/domain_shift.csv` (T08, dependency).

## 2. Git

| Kiểm tra | Kết quả |
|---|---|
| Branch | `task/T09-phobert-B` ✔ |
| Baseline chứa T08 CLOSED | `6c4b8de` = tip `master`, chứa merge T08 `778675e` ✔ |
| Working tree trước review | sạch ✔ |
| Commit | 6 commit, đều dạng `[T09] ...` ✔ |
| Scope (`git diff --stat 6c4b8de...HEAD`) | 8 file, đều trong allowlist: notebook, `ml/src/model_b_utils.py`, `comparison_B.csv`, `model_card_B.md`, `ml/README.md`, 2 report Codex, file điều phối ✔ |
| `backend/**`, `frontend/**`, `normalize()` | không đổi ✔ |
| Model/tokenizer/ZIP/data lớn/secret | không có; file CSV duy nhất là `comparison_B.csv` 19 dòng; `git ls-files ml/artifacts data` chỉ có `.gitkeep`/`README.md`; grep secret 0 hit thật ✔ |
| `git diff --check` | OK ✔ |

**Code đã chạy trên Colab = commit nào?** `~/Downloads/firefly-cinema-T09-code.zip` có comment `c8a023096c…` (tạo bằng `git archive`). So nội dung (bỏ CR) 6/6 file trong ZIP trùng `c8a0230`. Sau đó chỉ commit `458a073` sửa notebook: **một dòng chữ** trong template model card (thêm "dương nghĩa là B thấp hơn A"), không đổi logic. → Code trong Git tương đương code đã chạy.

## 3. Kiểm tra độc lập trên CPU (probe trong scratchpad, ngoài repo, đã xóa)

Môi trường: Python 3.13 hệ thống, scikit-learn 1.7.2, joblib 1.5.2, pandas 2.2.3, numpy 2.2.4 (khớp pin notebook).

| Probe | Kết quả |
|---|---|
| Split validation | `stratified_movie_split` seed 42 → 294 train / 53 validation; validation {0: 17, 1: 36}, train {0: 94, 1: 200} — đúng 15 % phân tầng ✔ |
| Trùng train/validation | 0 ID ✔ |
| Trùng movie train/test | 0 ID, 0 câu sau `normalize()` ✔ |
| Trùng movie test với pool phone | 0 ✔ |
| Config a/b | a = 294; b = 588 (294 movie + 294 phone, phone {0: 132, 1: 162}) ✔ |
| Grid truyền thống | 216 trial, 38 s; chọn SVM b (word, min_df 2, C 1.0), LR a (word, min_df 3, sublinear, C 5.0), NB a (word+char, min_df 3, sublinear, α 0.1) — **khớp tuyệt đối** report/model card |
| Tái lập `comparison_B.csv` | 14/14 dòng (SVM/LR/NB A, SVM/LR/NB B, constant × 2 test) **max \|Δ\| = 0.0**, `train_config` khớp ✔ |
| PhoBERT A trong CSV vs T08 `domain_shift.csv` | 2 dòng trùng từng chữ số (`0.919936`, `0.857143`, …) ✔ |
| `normalize()` parity | `eval_utils.normalize` vs `backend/app/classifier.normalize`: **11.618/11.618** câu (movie train+test, phone train+dev+test) ✔ |
| SHA-256 `comparison_B.csv` | `c10e49e4…0209ace` = giá trị Codex ghi cho manifest/Drive ✔ |
| Notebook | JSON hợp lệ, 10/10 code cell parse được; 0 output (xem TODO-01) |

### Nhất quán số liệu PhoBERT (suy ra ma trận nhầm lẫn nguyên)

| Model | Test | TP | FN | FP | TN | Kiểm tra |
|---|---|---:|---:|---:|---:|---|
| PhoBERT A | movie (101/48) | 78 | 23 | 3 | 45 | P/R/F1/macro khớp CSV |
| PhoBERT B | movie | 89 | 12 | 4 | 44 | P 0.956989, R 0.881188, F1 0.917526, macro 0.881840 khớp |
| PhoBERT B | phone (1243/981) | 1179 | 64 | 149 | 832 | F1 0.917153, macro 0.901837 khớp |

Validation 53 câu (36/17) cũng ra số nguyên hợp lệ: a‑1e‑5 (TP34 FN2 FP1 TN16), a‑2e‑5 (TP33 FN3 FP0 TN17), b‑2e‑5 (TP34 FN2 FP0 TN17). → Bảng validation không phải số bịa; **b‑2e‑5 thắng a đúng 1 câu**.

Delta tính lại: movie ΔF1_neg `+0.060383`, Δmacro `+0.065338`; phone F1_A − F1_B `0.002783` (B − A = `−0.002783`), Δmacro phone `0.006849`. Khớp report, model card, file điều phối.

## 4. Đối chiếu Acceptance Criteria

| AC | Kết quả | Evidence Claude |
|---|---|---|
| AC-01 `movie_test` chỉ dùng ở ô cuối | **PASS** | Đọc code: `movie_test.csv`/phone `test.csv` chỉ được đọc ở cell 16 (`# TEST BOUNDARY`), sau cell 14 ghi manifest `test_loaded=False`. Cell 5 chỉ kiểm sự tồn tại của file (`first_dir_with_files`), không đọc nội dung. `model_b_utils.py` không có hàm đọc test. Selection PhoBERT (cell 12) và truyền thống (`select_traditional_models`) chỉ dùng `movie_validation`. Early stopping dùng `validation_norm`. Phone test không nằm trong pool lấy mẫu config b (pool = train+dev). |
| AC-02 B > A trên movie F1 neg | **PASS** | `0.917526 > 0.857143` (+0.060383); số nguyên nhất quán. Đồng thời macro-F1 B 0.881840 > A 0.816502 và > constant 0.404 → không phải chỉ do lệch nhãn. |
| AC-03 F1 B trên phone + mức giảm | **PASS** | B phone `0.917153`, giảm `0.002783` so với A; macro giảm `0.006849`; ghi trong CSV, model card, report. |
| AC-04 `id2label` + reload CPU Transformers 5.18.0 | **PASS (evidence Colab)** | Code: cell 11/14 ép `id2label={0: binh_thuong, 1: tieu_cuc}`, cell 18 assert `config_json['id2label'] == {'0': 'binh_thuong', '1': 'tieu_cuc'}`, `transformers.__version__ == '5.18.0'`, nạp lại `.to('cpu')` + tokenizer, logits `(1, 2)`; ZIP được assert có `config.json` + `model.safetensors`. Marker theo Codex: `CPU_RELOAD_OK transformers=5.18.0` ở hai run. Claude **không** nạp lại được trên máy local vì `ml\artifacts\phobert_B_best\` chưa tồn tại (TODO-02). |
| AC-05 `comparison_B.csv` đủ bảng | **PASS** | 18 dòng: PhoBERT A/B, SVM/LR/NB A, SVM/LR/NB B × phone/movie, + constant positive; schema 7 cột đúng Task Record. 14/14 dòng CPU tái lập Δ 0. |
| AC-06 `model_card_B.md` đầy đủ, có lý do chọn | **PASS** | Có dữ liệu/split, nguồn khởi tạo + SHA research, nhãn, `max_length`, hyperparameter, lý do chọn b (validation macro-F1 0.957937 / F1 0.971429), bảng test, phone drop, giới hạn lệch nhãn + 149 câu, `MODEL_VERSION` đề xuất `phobert-B-2026-10-09`. Thiếu một số disclosure (TODO-03). |

## 5. Các điểm PO yêu cầu xác minh riêng

1. **Test không tham gia train/validation/early stopping/tuning/selection** — xác minh bằng code (mục 4 AC-01) và probe overlap = 0. ✔
2. **B fine-tune từ research A, không phải backend** — cell 5: `RESEARCH_CKPT` chỉ tìm ở `ml/artifacts/phobert_A_best` hoặc `MyDrive/thesis_results/phobert_A_best`; assert `'backend/models' not in RESEARCH_CKPT`; mỗi trial `from_pretrained(RESEARCH_CKPT)` mới. Model card ghi SHA research `121c2cbc…b75b7`. ✔ (giá trị hash in trong output Colab Claude chưa thấy trực tiếp.)
3. **Validation 15 % phân tầng, seed 42, không trùng** — tái lập 294/53, overlap 0. ✔
4. **Chọn b / 2e‑5 / epoch 3 dựa trên validation trước test** — quy tắc `max(macro_f1, f1_neg, prefer a, smaller lr)` trên validation; b‑2e‑5 là max duy nhất; manifest ghi trước cell test. ✔ Biên thắng chỉ 1 câu validation (TODO-04).
5. **Movie F1 A 0.857143 / B 0.917526 / Δ +0.060383** ✔
6. **Phone F1 A 0.919936 / B 0.917153 / Δ(B−A) −0.002783** ✔
7. **`comparison_B.csv` đủ và thống nhất** — CSV = bảng model card = bảng report từng chữ số; hash CSV khớp giá trị manifest. ✔
8. **`id2label`, tokenizer, CPU load** — đúng ở mức code + evidence Colab; chưa reload trên máy Windows (TODO-02).
9. **Hai clean-run, manifest, hash** — Claude **không truy cập được Google Drive** trong phiên này (không có connector, không có bản tải về). Hash `config.json 3af764b4…`, `model.safetensors 0b80947c…` (540.023.384 B), `selection_manifest.json d21786d2…`, ZIP `bd7d1544…` chỉ có trong report Codex. Tính nhất quán nội bộ (số nguyên, CSV hash, code = `c8a0230`) đều đạt, nên không có dấu hiệu sai lệch, nhưng **phần GPU chưa được xác minh độc lập** → PO action ở TODO-02.
10. **TODO T08 → T09** — xem mục 7; hai mục bị ghi "RESOLVED" quá mức (TODO-05 của review này).

## 6. Rủi ro đã xem xét

| Rủi ro | Đánh giá |
|---|---|
| Movie test 149 câu, 67,8 % tiêu cực; constant F1 0.808 | B vượt constant cả F1 (0.918 vs 0.808) lẫn macro (0.882 vs 0.404). Model card công bố đúng. |
| Ý nghĩa thống kê | Cải thiện movie = +11 TP, −1 TN trên 149 câu. Notebook **không lưu dự đoán từng câu** nên không làm được McNemar/bootstrap cặp A–B (TODO-04). |
| Overfit movie train nhỏ | lr nhỏ, ≤ 5 epoch, patience 2, chọn trên validation; nhưng validation chỉ 53 câu và b thắng a đúng 1 câu → chọn cấu hình có phương sai cao. Phone gần như không giảm (−0.0028) nhờ trộn phone 1:1 (đúng mục tiêu config b). |
| AMP/GradScaler, scheduler | `torch.cuda.amp.GradScaler` là API cũ (deprecated, vẫn chạy). `scheduler.step()` gọi cả khi scaler bỏ qua `optimizer.step()` (overflow fp16 đầu tiên) → lịch LR lệch ~1 bước trên ~185–370 bước. Ảnh hưởng không đáng kể; **đúng là không nên retrain sau khi đã xem test**. Ghi TODO-06 cho lần train sau. |
| Công bằng A/B | PhoBERT A và B đánh giá cùng test, cùng `normalize()`, cùng code `predict_model` → công bằng. Bất đối xứng khác: baseline truyền thống B **được fit lại trên toàn bộ 347 movie + 347 phone** sau khi chọn, còn PhoBERT B chỉ train trên 294 (+294 phone), không refit. Bất lợi nghiêng về PhoBERT nên không thổi phồng kết luận, nhưng model card chưa nói (TODO-03). |
| Trùng lặp phone pool/test | 5 câu phone test trùng (sau normalize) với pool train+dev — thuộc tính sẵn có của split UIT‑ViSFD (T00), áp dụng như nhau cho A (train trên cùng pool); ảnh hưởng ≤ 5/2.224. Info. |
| Model B chưa vào production | Đúng phạm vi: không đụng `backend/`; model card ghi rõ chỉ đề xuất cho T10. Câu demo "lê thê" (T07 TODO-01) chưa kiểm được với B vì không có checkpoint local. |

## 7. TODO T08 chuyển sang T09 — đánh giá của Claude

| TODO T08 | Codex ghi | Claude đánh giá |
|---|---|---|
| TODO-01 baseline hằng / lệch nhãn | RESOLVED | **Đồng ý RESOLVED** — tái lập constant rows Δ 0; model card đọc F1 cùng macro-F1. |
| TODO-02 movie test 149 câu, CI | ACCEPT_WITH_DISCLOSURE | Đồng ý; model card nói "độ bất định cao" nhưng chưa có CI cho Δ A–B của T09 (TODO-04). |
| TODO-03 notebook phụ thuộc cwd | RESOLVED | **RESOLVED ở mức code** (đã đọc `discover_project_root`, fallback ZIP; ZIP = `c8a0230`). Clean-run Colab chưa được Claude xem trực tiếp. |
| TODO-04 thiếu output notebook, Drive path, hướng dẫn | RESOLVED | **Chưa RESOLVED đầy đủ — PARTIAL.** Notebook trong Git có **0 output**; `ml/README.md` bước 4 tự yêu cầu "tải notebook đã có toàn bộ output về lại `ml/notebooks/T09_phobert_B.ipynb`" nhưng chưa làm. Drive path/ID và hướng dẫn thì đã có. PO trước đó disposition ACCEPT_WITH_NOTES → T13; đề nghị giữ nguyên hướng đó. |
| TODO-05 PhoBERT nhạy `normalize()` | RESOLVED | **Đồng ý cho T09** — `normalize()` không đổi, parity 11.618/11.618 trên CPU. Câu "lê thê" với B vẫn phải kiểm ở T10. |

Lưu ý quy trình: Codex tự ghi "RESOLVED trong T09" cho TODO do PO disposition trước khi có review/PO. Quyết định cuối thuộc PO.

## 8. Required Fixes

Không có.

## 9. TODO (không chặn)

| ID | Mức | Nội dung | Đề xuất |
|---|---|---|---|
| TODO-01 | Low | Notebook trong Git không có output; run1/run2 chỉ ở Drive. Notebook Git khác notebook đã chạy đúng 1 dòng chữ template model card (`458a073`). | Tải bản run2 (có output) về `ml/notebooks/` hoặc ghi rõ Drive là nguồn evidence chuẩn; T13. |
| TODO-02 | Medium (PO action, trước T10) | Claude chưa xác minh độc lập phần GPU: output hai run, hash checkpoint/manifest/ZIP, CPU reload. `ml\artifacts\phobert_B_best\` chưa có trên máy. | Tín tải `firefly_phobert_B.zip` về `ml\artifacts\phobert_B_best\` (ngoài Git), đối chiếu SHA-256 `model.safetensors 0b80947c…22f4f` và `config.json 3af764b4…005da`, mở run1/run2 xác nhận marker `SELECTION_LOCKED=True` xuất hiện trước `FINAL_TEST_COMPLETE=True`. Việc này cũng là tiền đề của T10. |
| TODO-03 | Low | `model_card_B.md` được sửa tay sau run (khác bản notebook sinh ra trên Drive), và chưa nêu: (a) baseline truyền thống B refit trên 347+347, PhoBERT B không refit; (b) biên chọn b chỉ 1 câu validation. | Bổ sung disclosure khi viết khóa luận / T13. |
| TODO-04 | Low | Không lưu dự đoán từng câu → không làm được kiểm định cặp A–B (McNemar/bootstrap) trên 149 câu. | Khi có checkpoint local (TODO-02), chạy dự đoán CPU 149 câu, tính CI/McNemar cho khóa luận. Không được dùng để chọn lại model. |
| TODO-05 | Low (process) | Coordination ghi T08 TODO-04 "RESOLVED" dù notebook Git chưa có output; TODO-03 RESOLVED chỉ ở mức code. | PO quyết disposition cuối (đề xuất: TODO-04 giữ ACCEPT_WITH_NOTES → T13). |
| TODO-06 | Low | `torch.cuda.amp.GradScaler` deprecated; `scheduler.step()` không bị bỏ qua khi scaler skip optimizer step. | Sửa nếu có lần train sau (T15); không retrain T09. |
| TODO-07 | Info | Task Record `T09.md` còn ghi `Current Status: PLANNED`. | Như T06 TODO-06: coordination là nguồn trạng thái; Claude không sửa `Txx.md`. |

## 10. Gate cuối

- Probe (`probe_t09_trad.py`, `probe_t09_parity2.py`, thư mục giải nén ZIP) đặt trong scratchpad ngoài repo; đã xóa trước gate cuối.
- `git status` sau review chỉ có report này và `docs/TASK_COORDINATION_ACTIVE.md`.
- Không sửa production code, notebook, CSV, model card, checkpoint hay số liệu.

## 11. Kết luận và bước tiếp theo

**PASS_WITH_TODO.** AC 6/6 PASS, RF 0, blocker 0. Phần CPU tái lập tuyệt đối; phần GPU nhất quán nội bộ nhưng cần Tín xác minh evidence Drive (TODO-02) trong PO_REVIEW.

- T09: `CLAUDE_REVIEW` → `PO_REVIEW`.
- **Không** đặt T10 `READY_FOR_HANDOFF`: PO chỉ định T10 giữ `PLANNED / NOT AUTHORIZED` đến khi PO quyết định, nên review này không kèm prompt bàn giao.
- Claude không approve, không merge, không gắn tag `phobert-B`, không đóng T09.
