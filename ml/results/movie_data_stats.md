# Thống kê dữ liệu bình luận phim — T03

> File này do `ml/src/prepare_movie_data.py` cập nhật từ dữ liệu cục bộ ngoài Git. Không điền metric thủ công.

- Trạng thái: **READY_FOR_AC_REVIEW**
- Raw rows: 496
- Duplicate removed sau `normalize()`: 0
- Final rows: 496
- Train/test size: train=347, test=149
- Duplicate cross-split count sau `normalize()`: 0
- PII scan: 0 phát hiện
- Kappa: 0.602510 (KAPPA_ACCEPTED)
- Seed: 42

## Phân bố nhãn

- `0`: 159 (32.06%)
- `1`: 337 (67.94%)

## Phân bố source_type

- `review_site`: 333 (67.14%)
- `social`: 163 (32.86%)

## Nguồn cụ thể và độ phủ

- `Moveek`: 178 (35.89%)
- `YouTube`: 163 (32.86%)
- `Google Maps`: 155 (31.25%)
- Phim: 83 phim, 341 câu.
- Rạp: 28 rạp, 155 câu.

## Ghi chú nghiệm thu

- Mục tiêu dữ liệu cuối: 400–600 câu sau khử trùng lặp.
- Mục tiêu label 1: 35–60%. Dữ liệu thật có 67,94%; PO đã chọn phương án A ngày 08/10/2026: chấp nhận độ lệch, không thêm/bớt câu và không sửa nhãn. Điều kiện này chỉ cảnh báo, không chặn gate.
- Cohen's kappa chỉ được ghi khi `label_b` của 100 câu do người thật gán đầy đủ.
