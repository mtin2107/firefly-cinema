# Claude — Ghi nhận quyết định PO: tỷ lệ nhãn 1 của T03 — 08/10/2026

| Trường | Giá trị |
|---|---|
| Loại | Ghi nhận quyết định PO (không phải review task) |
| Liên quan | T03, mục tiêu "tỷ lệ nhãn 1 35–60 %" (Scope) |
| Người quyết định | Tín (PO), xác nhận trong chat ngày 08/10/2026: "tôi chốt A" |
| Người soạn | Claude (phiên hỗ trợ thu dữ liệu, không review) |
| Nhánh | `task/T03-du-lieu-phim` |
| Trạng thái T03 | Không đổi (Claude không chuyển trạng thái) |

## 1. Số đo thật (output `prepare_movie_data.py`, 08/10/2026)

| Mục | Giá trị |
|---|---|
| Raw rows / sau khử trùng `normalize()` | 496 / 496 (loại 0) |
| PII scan | 0 |
| Tỷ lệ nhãn 1 | 67,94 % (337/496) — ngoài mục tiêu 35–60 % |
| review_site + social / self_written | 100 % / 0 % |
| Train / test | 347 / 149, trùng chéo sau `normalize()` = 0 |
| Cohen's kappa (100 câu, seed 42, A = Tín, B = "Người 1") | 0,6025 → `KAPPA_ACCEPTED` |
| STATUS script | `BLOCKED_BY_DATA_QUALITY` — chỉ do điều kiện tỷ lệ nhãn (`prepare_movie_data.py` dòng 394–397) |

## 2. Quyết định (phương án A)

Chấp nhận tỷ lệ nhãn 1 = 67,94 %, **không** thêm/bớt câu, **không** sửa nhãn. Dữ liệu và mẫu kappa giữ nguyên.

Lý do ghi nhận:
- Guideline định nghĩa nhãn 1 là "có ít nhất một nội dung tiêu cực", nên câu khen–chê lẫn lộn đều là nhãn 1.
- Cách chọn ứng viên trong phiên hỗ trợ thu dữ liệu nghiêng về câu chê: từ batch 4, Claude chủ động bổ sung câu chê; Google Maps ưu tiên đánh giá 1–2 sao và bỏ nhiều đánh giá 5 sao viết theo mẫu; một phần Moveek lọc theo từ khóa rạp/dịch vụ. Tỷ lệ theo nguồn: Moveek 76 %, Google Maps 80 %, YouTube 48 %.
- Phương án B (thêm ~66 câu nhãn 0) làm đổi mẫu kappa seed 42, buộc "Người 1" gán lại, và là chọn mẫu theo nhãn.
- Khoảng 35–60 % là mục tiêu trong Scope, không nằm trong AC-01…AC-06; chia train/test đã phân tầng theo nhãn và thước đo chính là macro-F1.

## 3. Việc cần làm (Codex, trong allowlist T03)

1. Ghi quyết định này vào report Codex và `ml/results/movie_data_stats.md`, `data/README.md` (số dòng, tỷ lệ nhãn, kappa, ngày tạo, giải trình lệch mục tiêu).
2. Điều chỉnh `ml/src/prepare_movie_data.py` để điều kiện tỷ lệ nhãn chỉ cảnh báo (không chặn) hoặc phản ánh mục tiêu PO đã chấp nhận; giữ nguyên các cổng khác. Không đổi `normalize()`, không đổi seed/split.
3. Chạy lại gate T03, xác nhận cùng `id` mỗi tập (AC-04) và kappa 0,6025 không đổi.
4. Ghi quyết định vào `docs/tasks/T03.md` mục 13 nếu PO cho phép sửa file đó (không nằm trong allowlist Codex hiện tại).

## 4. Ghi chú cho bước review

- Kappa 0,6025 sát ngưỡng; nên nêu trong báo cáo khóa luận là mức đồng thuận vừa phải và nguồn bất đồng chính.
- CSV nằm ngoài Git. Các file sao lưu phát sinh trong phiên (`data/phim/*_backup_*`, `*_corrupted_ansi_*`, `*_labeled_ansi_*`, `*_restored.csv`, `*_before_merge_*`, `kappa_sample_nguoi1*`) đều bị `.gitignore`; riêng `data/phim/movie_comments_v1.md` **không** bị ignore và không được `git add`.
- Hai lần file CSV bị Excel lưu dạng ANSI (mất dấu); Claude đã khôi phục text từ `candidates_batch01–09.csv` và chép nhãn theo `id`, kiểm tra khớp 496/496 và 100/100.
