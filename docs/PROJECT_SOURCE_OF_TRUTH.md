# PROJECT SOURCE OF TRUTH — Firefly Cinema

> Cổng vào duy nhất cho mọi agent. Đọc file này trước, sau đó đọc `TASK_COORDINATION_ACTIVE.md` và Task Record đang làm.
> Cập nhật: 03/10/2026.

## 1. Project Snapshot

| Mục | Giá trị |
|---|---|
| Sản phẩm | Firefly Cinema — website đặt vé xem phim tích hợp PhoBERT phân loại bình luận tiêu cực |
| Đề tài | Khóa luận #67, Khoa học dữ liệu, NTTU — sinh viên Lê Minh Tín |
| Hạn | Sản phẩm 05/10 – 01/11/2026 · Báo cáo 02/11 – 29/11/2026 |
| Repo | `C:\Projects\firefly-cinema` (thư mục gốc duy nhất), nhánh chính `master` |
| Kho file lớn | `D:\KhoaLuan_PhimVe\` — không chứa code đang dùng, không sửa code ở đây |
| Mốc đã có | tag `giao-dien-v1`, `phobert-v1` |
| Stack | React 18 + Vite 5 · FastAPI 0.115 + SQLAlchemy 2 + SQLite · PhoBERT (transformers 5.18, torch 2.11 CPU) |

## 2. Vai trò

| Vai trò | Ai | Được làm | Không được làm |
|---|---|---|---|
| **Product Owner / Approver** | **Tín** | Chốt Task Record, chạy code trên máy và Colab, ra quyết định PO (`APPROVED` / `APPROVED_WITH_NOTES` / `CHANGES_REQUESTED` / `REJECTED`), merge, gắn tag | — |
| **Primary Implementer** | **Codex / ChatGPT** | Soạn Task Record (bước PLANNING), viết code + test, chạy gate, viết implementation/fix report, chuyển `IN_PROGRESS → CLAUDE_REVIEW` | Tự review, tự PASS, tự chuyển `PO_REVIEW`, tự đóng task, tự mở task kế tiếp, mở rộng scope |
| **Independent Reviewer / Tester** | **Claude** | Đọc code và test thật, chạy gate độc lập, probe tạm, kết luận `PASS` / `PASS_WITH_TODO` / `FAIL`, viết review report | Sửa production code, tự làm Required Fix, approve, đóng task |

**Quy ước duyệt (Tín chốt 04/10/2026):** Task Record T00–T15 đã có sẵn bản nháp. Khi Tín gửi `Txx.md` cho ChatGPT/Codex để bắt đầu, task đó **được coi là PO đã duyệt và ở trạng thái `READY_FOR_HANDOFF`** theo đúng nội dung file lúc gửi. Muốn đổi gì thì Tín sửa `Txx.md` trước khi gửi.

## 3. Thứ tự ưu tiên nguồn khi mâu thuẫn

1. Code và test thật trong repo (đã kiểm chứng).
2. `docs/TASK_COORDINATION_ACTIVE.md`.
3. Quyết định PO mới nhất (report `po_review_*`).
4. `docs/PROJECT_SOURCE_OF_TRUTH.md` → `docs/ARCHITECTURE.md` → `docs/BOI_CANH_DU_AN.md`.
5. Review Claude mới nhất của task hiện tại.
6. Report Codex mới nhất.
7. Report cũ, archive.

Không âm thầm trộn hai phiên bản mâu thuẫn. Ghi conflict vào mục "Open Blockers" của file điều phối và hỏi Tín.

## 4. Quyết định đã chốt (không tự đổi)

- Thiết kế giao diện ở `BOI_CANH_DU_AN.md` mục 4 (màu, font, hero bảng hiệu, PosterIntro, header).
- Kiến trúc lớp API frontend: chỉ import từ `src/api/index.js`, mọi endpoint có cả `real.js` và `mock.js`.
- Model PhoBERT A: nhãn `0 = binh_thuong`, `1 = tieu_cuc`, đầu vào chuẩn hóa bằng `normalize()`, không tách từ, ngưỡng 0,5.
- Không thêm thư viện ngoài danh sách đã cho phép trong task (scikit-learn, joblib cho T01/T07; pytest cho T11).
- Lệnh hướng dẫn viết cho Windows PowerShell. Giao diện tiếng Việt, code tiếng Anh, trả lời Tín bằng tiếng Việt.

## 5. Câu hỏi còn mở (chỉ Tín quyết định)

| # | Câu hỏi | Ảnh hưởng task | Trạng thái |
|---|---|---|---|
| Q1 | Nguồn thu bình luận phim và người gán nhãn thứ hai | T03 | MỞ |
| Q2 | Dùng Alembic hay chấp nhận xóa `firefly.db` khi đổi schema | T06 trở đi | MỞ |
| Q3 | Model mặc định sau T10: PhoBERT B hay admin chọn | T10 | MỞ |
| Q4 | Deploy lên mạng hay chỉ chạy máy khi bảo vệ | T12, T13 | MỞ |

Khi Tín trả lời, đổi trạng thái thành `CHỐT: <nội dung>, <ngày>`.

## 6. Bản đồ tài liệu

Xem `docs/README.md`.
