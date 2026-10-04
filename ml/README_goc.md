# Khóa luận: Phân tích cảm xúc theo khía cạnh cho bình luận tiếng Việt (nền ViSFD → chuyển miền sang phim)

## Cấu trúc
- `src/common.py` – đọc dữ liệu, tách nhãn `{ASPECT#Polarity}`, chuẩn hóa teencode
- `src/prep.py` – tạo `processed/*.csv` + `results/dataset_stats.json`
- `src/baselines.py` – baseline TF-IDF + NB/LogReg/LinearSVC (đã chạy)
- `src/error_analysis.py` – phân tích lỗi Task A → `results/error_analysis_taskA.csv`
- `src/train_phobert.py` – fine-tune PhoBERT (CHƯA chạy, dùng trên Colab GPU)

## Ba bài toán
- **A** Bình luận có ý kiến tiêu cực? (nhị phân) – dùng cho web: cờ cảnh báo bình luận tiêu cực
- **B** Phát hiện khía cạnh (đa nhãn, 10 khía cạnh)
- **C** Cảm xúc theo khía cạnh (3 lớp; đầu vào đã biết khía cạnh đúng)

## Kết quả baseline (Test, 1 lần chạy, chọn siêu tham số trên Dev)
| Bài toán | Mô hình tốt nhất | Chỉ số |
|---|---|---|
| A | LogReg, văn bản chuẩn hóa | macro-F1 0.882; F1(tiêu cực) 0.897 |
| B | LinearSVC | micro-F1 0.864; macro-F1 0.843 |
| C | LinearSVC theo từng khía cạnh | macro-F1 0.756 (Neg 0.85 / Neu 0.52 / Pos 0.90) |

Ablation chuẩn hóa teencode: A tăng ~0.7 điểm macro-F1 (LogReg), B và C gần như không đổi.

## Lưu ý trung thực
- Task C ở đây cho trước khía cạnh đúng, nên KHÔNG so trực tiếp được với số của bài báo gốc (end-to-end).
- Kết quả là một lần chạy, một seed; khi viết báo cáo nên chạy ≥3 seed và báo trung bình ± độ lệch chuẩn.
- Lớp Neutral yếu (F1 ≈ 0.52); STORAGE chỉ có 91 mẫu train nên khó học.
- Nhãn "has_negative" = có ít nhất một khía cạnh Negative (55% bình luận); nhãn "tổng thể 3 lớp" suy ra từ khía cạnh gần như không có Neutral (2.9%) nên không dùng.
- Dữ liệu là điện thoại, chưa phải phim. Cần bộ bình luận phim tự thu thập để làm thí nghiệm chuyển miền.
- Dữ liệu ViSFD dùng cho nghiên cứu; cần trích dẫn bài SA2SL (Phan et al., 2021). Dùng thương mại phải liên hệ tác giả.

## Bước tiếp theo
1. Chạy `train_phobert.py` cho A, B, C trên Colab; so với baseline.
2. Thu thập và gán nhãn 1.000–1.500 bình luận phim; thí nghiệm chuyển miền.
3. Thêm LIME/SHAP, dashboard, rồi web đặt vé (React + FastAPI).
