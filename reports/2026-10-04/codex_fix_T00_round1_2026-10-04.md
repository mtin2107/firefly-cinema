# Codex fix — T00 — round 1 — 04/10/2026

## Task / Result

T00, vòng sửa sau review Claude FAIL: RF-01, RF-02, RF-03 đã xử lý; bàn giao lại `CLAUDE_REVIEW`. Không đổi schema, production code, classifier hoặc thư viện.

## Required Fixes

| RF | Kết quả | File |
|---|---|---|
| RF-01 | Đã sửa | `ml/README.md`, `ml/model_card_A.md`, `data/README.md` ghi đúng vị trí Drive, ngày Colab đọc thành công và giới hạn của notebook lịch sử; `data/README.md` có hướng dẫn khôi phục |
| RF-02 | Đã bổ sung evidence gốc | Output ô Colab do Tín gửi ngày 04/10/2026 được chép nguyên văn dưới đây; có đường dẫn, shape, value counts, hai kiểm tra tồn tại và `T00_DRIVE_CHECK_OK` |
| RF-03 | Đã sửa | `ml/model_card_A.md` ghi pretrained `vinai/phobert-base-v2`; tách dev/test macro-F1 và accuracy khỏi F1 lớp tiêu cực |

## RF-02 — Output Colab gốc

Nguồn: ảnh output ô Colab do Tín gửi trong chat ngày **04/10/2026**. Phần dưới là nguyên các dòng output hiển thị trong ảnh, không phải kết quả tự tạo hoặc chạy lại bằng dữ liệu local.

```text
FILE: /content/drive/MyDrive/thesis/data/processed/train.csv
shape: (7786, 20)
has_negative value_counts():
has_negative
0    3484
1    4302
FILE: /content/drive/MyDrive/thesis/data/processed/dev.csv
shape: (1112, 20)
has_negative value_counts():
has_negative
0    516
1    596
FILE: /content/drive/MyDrive/thesis/data/processed/test.csv
shape: (2224, 20)
has_negative value_counts():
has_negative
0     981
1    1243
error_analysis: /content/drive/MyDrive/thesis/results/error_analysis_taskA.csv True
notebook_A: /content/drive/MyDrive/thesis/notebooks/phobert_A.ipynb True
T00_DRIVE_CHECK_OK
```

Đối chiếu read-only từ CSV trong project: train 7.786 dòng/20 cột (0: 3.484, 1: 4.302); dev 1.112/20 (0: 516, 1: 596); test 2.224/20 (0: 981, 1: 1.243). Khớp output Colab. Output Colab là bằng chứng đọc trực tiếp từ Drive; đối chiếu local chỉ là kiểm tra bổ sung.

## Focused Checks

- Quét ba tài liệu RF-01: không còn `chờ upload`, `chờ Tín`, `vẫn cần bằng chứng`, `cần được Tín lưu`, `chưa hoàn tất` hoặc đường dẫn `D:\`.
- Cả ba tài liệu có đủ đường dẫn Drive của split, error analysis và notebook A.
- Model card có `vinai/phobert-base-v2`, dev macro-F1 `0,9176`, test macro-F1 `0,9128`, test accuracy `0,9141`; F1 lớp tiêu cực `0,9178`/`0,9180` được ghi là chỉ số khác.
- `git diff --check`: đạt.

## Scope / Security Gate

`git diff --name-only master...HEAD` sau commit fix chỉ gồm các file T00 và report Claude/Codex theo workflow. Trong commit fix round 1 chỉ sửa ba tài liệu RF-01/RF-03, file điều phối và report này. Kiểm tra tên file trong diff: không có `.env`, `*.db`, `*.csv`, `*.safetensors`, `*.bin`, `*.zip`, `*.joblib`, `backend/models/`, `ml/artifacts/`, `backup/`.

## Final Status / Follow-up

T00: `FIX_LOOP → CLAUDE_REVIEW`; Open Required Fixes: 0 để Claude kiểm độc lập. Không tự PASS, PO approve, merge, đóng T00 hoặc mở T01. Vấn đề hai checkpoint model A khác nhau vẫn chờ quyết định PO, ngoài ba RF của vòng sửa này.
