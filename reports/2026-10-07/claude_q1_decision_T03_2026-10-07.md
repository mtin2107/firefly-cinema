# Claude — Chốt Q1 (nguồn bình luận phim, người gán nhãn) cho T03 — 07/10/2026

| Trường | Giá trị |
|---|---|
| Loại | Ghi nhận quyết định PO (không phải review task) |
| Liên quan | Q1, T03 (FR-M05, NFR-10) |
| Người quyết định | Tín (PO), xác nhận trong chat ngày 07/10/2026 |
| Người soạn | Claude |
| Nhánh | `master` (`c1480b5`), không tạo nhánh task |
| Trạng thái T03 | PLANNED, hết BLOCKED về nội dung; **chưa** READY_FOR_HANDOFF (chờ Tín gửi T03.md cho ChatGPT) |

## 1. Bối cảnh
- `TASK_COORDINATION_ACTIVE.md` mục 8 ghi Q1 chặn T03; `PROJECT_SOURCE_OF_TRUTH.md` mục 5 ghi Q1 = MỞ.
- Theo kế hoạch, T03 bắt đầu từ 05/10 và chạy song song với T00–T02. Hôm nay đã 07/10, hạn sản phẩm 01/11/2026.
- T03 nằm trên đường găng T03 → T08 → T09 → T10 → T11, nên chốt Q1 sớm là ưu tiên.
- `docs/tasks/T03.md` đã có sẵn ràng buộc: `source_type` ∈ {`review_site`, `social`, `self_written`, `web_firefly`}; thu tay 400–600 câu; bỏ thông tin cá nhân; tỷ lệ nhãn 1 từ 35–60 %; kappa ≥ 0,6 trên 100 câu.

## 2. Quyết định Q1 (PO xác nhận)

### 2.1 Nguồn bình luận
- **Nguồn chính chiếm ≥ 80 %:** `review_site` + `social`, chép tay, bỏ thông tin cá nhân, chỉ lấy đoạn ngắn.
- **`self_written` tối đa 20 %:** chỉ dùng cho ví dụ biên khó (châm biếm, chê một phần, khen phim nhưng chê rạp), hạn chế đưa vào tập test.
  - Lý do: nếu tập test có nhiều câu tự viết thì F1 ở T08/T09 sẽ cao giả, hội đồng dễ chất vấn.
- **`web_firefly`:** không đặt chỉ tiêu, vì website chưa có người dùng thật.

### 2.2 Người gán nhãn
- **A:** Lê Minh Tín, gán toàn bộ.
- **B:** "Người 1", là người thật nhưng ghi ẩn danh.
  - Tên thật do Tín giữ riêng, không commit vào repo.
  - Gán độc lập 100 câu do script chọn ngẫu nhiên `random_state=42`, không xem nhãn của A.
- **Người thêm** đặt tên "Người 2", "Người 3"… Đây chỉ là phần phụ (phân xử câu bất đồng hoặc đo thêm kappa), không đổi AC-03.
  - AC-03 vẫn là Cohen's kappa giữa A và B.
  - `kappa_sample.csv` giữ hai cột `label_a`, `label_b`.
- **Không dùng LLM (ChatGPT, Claude) làm người gán nhãn.**
  - Kappa giữa người và LLM không phải inter-annotator agreement đúng nghĩa.
  - Claude là reviewer của T03, nên nếu gán nhãn sẽ mất tính độc lập.
  - Claude chỉ được hỗ trợ ở mức: góp ý hướng dẫn gán nhãn và chỉ ra các câu có nhãn nghi mâu thuẫn để Tín tự xem lại.

## 3. Bộ nguồn đề xuất
Chi tiết ở `data/phim/NGUON_THU.md`. Chỉ tiêu khoảng 500 câu, trong đó ~88 % là bình luận thật:

| Nguồn | `source_type` | Số câu |
|---|---|---|
| Moveek, trang từng phim | `review_site` | 120 |
| MoMo, phần đánh giá phim | `review_site` | 80 |
| Google Maps, đánh giá các rạp (lấy nhãn 1 kiểu chê rạp/dịch vụ) | `review_site` | 70 |
| YouTube: bình luận dưới video review và trailer | `social` | 120 |
| Facebook, TikTok (fanpage và nhóm review phim công khai) | `social` | 50 |
| Tự viết, chỉ cho ví dụ biên khó | `self_written` | ≤ 60 |
| Website Firefly | `web_firefly` | 0 |

**Quy tắc đa dạng:**
- Ít nhất 20 phim.
- Mỗi phim tối đa 30 câu.
- Mỗi nguồn tối đa 40 % tổng số câu.
- Có cả phim được khen lẫn phim bị chê.
- Giữ nguyên teencode, câu không dấu, emoji.

**Hạn chế:**
- Danh sách nguồn soạn theo hiểu biết chung, Claude chưa mở từng trang để xác minh. Tín cần kiểm tra từng nguồn còn phần bình luận công khai trước khi thu.
- Đã tìm nhưng không thấy bộ dữ liệu bình luận phim tiếng Việt công khai. Các bộ hiện có (UIT-ViSFD, VLSP) thuộc miền điện thoại, nhà hàng, khách sạn, nên bắt buộc phải thu thủ công.

## 4. File đã tạo
| File | Git | Ghi chú |
|---|---|---|
| `data/phim/NGUON_THU.md` | Untracked, **không** bị ignore | Ngoài allowlist T03; xem mục 6 |
| `data/phim/movie_comments_v1.csv` | Ignored (`.gitignore`: `data/**/*.csv`) | Chỉ có dòng tiêu đề `id,text,label,source_type,note` |
| `reports/2026-10-07/claude_q1_decision_T03_2026-10-07.md` | Untracked | Report này |

Không sửa production code (`frontend/`, `backend/`, `ml/src/`).

## 5. Việc chưa làm được
Lệnh ghi quyết định vào ba file sau bị bộ phân loại an toàn của auto mode chặn. Claude không tìm cách vượt qua lệnh chặn, nên cả ba file vẫn chưa đổi:

| File | Nội dung dự kiến |
|---|---|
| `docs/PROJECT_SOURCE_OF_TRUTH.md` mục 5 | Q1: `MỞ` → `CHỐT: <nội dung mục 2>, 07/10/2026` |
| `docs/TASK_COORDINATION_ACTIVE.md` | Mục 4 và bảng roadmap: T03 hết BLOCKED, PLANNED chờ PO authorize; mục 8: Q1 RESOLVED; mục 11: authorize T03 sớm, chuẩn bị "Người 1"; mục 12: thêm dòng timeline 07/10 |
| `docs/tasks/T03.md` | Dependencies, Current Status, mục 13 ghi Q1 đã chốt |

## 6. Việc Tín cần làm
1. Cho phép Claude sửa ba file ở mục 5, hoặc tự sửa tay.
2. Quyết định chỗ để `data/phim/NGUON_THU.md`, chọn một trong ba:
   - Commit trên `master` như tài liệu PO.
   - Chuyển nội dung sang `data/README.md`, file có trong allowlist T03.
   - Để ngoài Git. Khi đó **không** `git add` file này trong nhánh T03, nếu không sẽ bị tính là file ngoài scope.
3. Commit report này cùng các cập nhật tài liệu, ví dụ `[T03] Resolve Q1: data source and annotators`.
4. Khi sẵn sàng: gửi T03.md cho ChatGPT (theo quy ước, như vậy là PO duyệt → `READY_FOR_HANDOFF`), tạo nhánh `task/T03-du-lieu-phim` từ `master`. Theo `AGENT_RULES.md`, T03 được chạy song song với một task web như T04.
5. Liên hệ "Người 1" sớm: họ cần khoảng 30–45 phút để gán 100 câu, sau khi `ml/labeling_guideline.md` xong.
