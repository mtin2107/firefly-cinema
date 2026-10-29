# Claude implementation — T13 Chốt v1.0 và sao lưu (29/10/2026)

Người làm: **Claude**, theo yêu cầu của PO trong chat ngày 29/10/2026 ("làm luôn để chốt hoàn thiện"). Reviewer: **Codex** (độc lập). Approver: Tín. Nhánh `task/T13-v1`, tạo lại từ master `db4b452` (đã có T31).

## 1. Trước T13
- Merge T31 vào master: `db4b452` (`--no-ff`, Codex round 3 PASS trên `984f06a`). Claude merge theo lệnh PO trong chat.
- Closure T24–T31 ở `TASK_COORDINATION_ACTIVE.md`: T24 `c2b7c4d`, T25 `6d49d16`, T26 `c1916c6`, T27 `f48922a` (merge commit); T28 `419b07e`, T29 `73eb3c7`, T30 `55a8cf5` (fast-forward, đã kiểm `merge-base --is-ancestor`); T31 `db4b452`. Tất cả → DONE / CLOSED.
- DB thật đã reset cho T29 + T30 trước đó trong ngày (`backup\T30-20261029-121409`).

## 2. Sản phẩm
| Mục T13 | File | Nội dung |
|---|---|---|
| README | `README.md` | Viết lại: giới thiệu, link bản mock, 8 ảnh, tính năng theo nhóm, bảng F1 (phone/movie, 5 mô hình + mốc hằng số), kết quả T15 tách từ, chạy nhanh, cấu trúc, **Hạn chế đã biết** gồm mọi mục PO quyết ghi hạn chế. Hướng dẫn cũ của README trùng với HUONG_DAN Phần 0–5 nên bỏ khỏi README |
| HUONG_DAN | `HUONG_DAN.md` | Thêm mục đầu **"Cài đặt từ số 0 (v1.0)"**: công cụ, clone, chép model A/B/SVM/LR/NB từ bản sao lưu, venv + pip, bảng khóa `.env` (chỉ tên khóa), frontend, kiểm thử, reset demo, định dạng trailer/ảnh, đổi schema. Phần cũ giữ nguyên làm ghi chú chi tiết |
| CHANGELOG | `CHANGELOG.md` | Mục `[1.0.0] — 29/10/2026` (tính năng theo task, T31, T13); `[Unreleased]` đổi thành "Ghi chú theo task trước 1.0.0" |
| Sao lưu | `docs/SAO_LUU.md`, `backup\v1.0\` (ngoài Git) | 72 file, 2.093,6 MB: `backend/models`, `ml/artifacts`, `data`, `firefly.db*`. SHA-256 từng file khớp file gốc (`backup\v1.0\sha256.csv`), DB qua `integrity_check` và `foreign_key_check`. Bảng hash các model, việc Tín cần làm (Drive, AC-02, T00 TODO-03, video, USB), nhật ký xác minh, cách khôi phục |
| Ảnh | `docs/images/` 14 ảnh, 1,7 MB | Trang chủ, khám phá, chi tiết phim, bình luận bị ẩn, chọn ghế, vé của tôi, tài khoản, Tổng quan, **Thống kê cảm xúc (T21)**, **So sánh mô hình** (có kết quả 5 mô hình), Kiểm duyệt, Quản lý phim, Soát vé, trang chủ điện thoại 390 px |
| CONG_NGHE | `docs/CONG_NGHE.md` | Bảng phiên bản đã kiểm ở v1.0; ghi chú `gemini-3.8-flash` là mặc định cũ; mốc dung lượng build v1.0 |
| ARCHITECTURE | `docs/ARCHITECTURE.md` | Mục T30–T31 và v1.0: AUTOINCREMENT, khóa 1 worker, chặn xóa phim, luật kiểm ảnh, `allow_empty_score`, header/dashboard |

Ảnh chụp bằng Chrome headless qua DevTools Protocol (script ở scratchpad, không vào repo), trên DB/UPLOAD_DIR tạm với mật khẩu admin thử, độ phân giải 1280 × 800 (ảnh 10: 1280 × 1250; ảnh 14: 390 × 844). Không dùng DB thật.

## 3. TODO chuyển về T13
| TODO | Xử lý |
|---|---|
| T18 TODO-03 (mốc bundle không tái lập) | **Đóng**: ghi mốc mới v1.0 vào CONG_NGHE (JS gzip 156,31 KB real, 165,27 KB mock; CSS gzip 14,78 KB) |
| T00 TODO-03 (`firefly_phobert.zip` trên Drive) | **Chờ Tín**: Claude không truy cập được Drive. Hướng dẫn kiểm ở `SAO_LUU.md` mục 4.3 |
| T15 TODO-02..04, T02 TODO-R2-02, T09 TODO-01/03, T08 TODO-04, T11 TODO-R3-02 (ACCEPT_LATER → T13) | Giữ nguyên disposition. Lệnh chạy và notebook đã có trong Git; số liệu dùng trong README lấy từ model card. Không sửa notebook/model card (ngoài allowlist T13) |
| T12 TODO-01, T25/T27/T28/T30 và audit OBS (PO quyết 29/10) | T25/T27/T30 TODO và audit OBS-05/06 đã sửa ở T31; các mục còn lại ghi trong README "Hạn chế đã biết" |

## 4. AC
| AC | Kết quả |
|---|---|
| AC-01 Clone ra `C:\Temp\firefly-test`, làm đúng HUONG_DAN → web chạy, health báo model, pytest đạt | **PASS ở lần 2** (lần 1 FAIL vì thiếu `tzdata`, mục 6). Clone `47dcdd1` (14:23–14:39): clone không có model; chép model từ `backup\v1.0`, hash PhoBERT B khớp; venv mới + pip theo HUONG_DAN; `.env` mới từ `.env.example` (SECRET_KEY mới, ADMIN_PASSWORD thử); compileall đạt; **pytest 286/286**; uvicorn :8000 → health `phobert_b`, 6/6 model available; đăng nhập demo, 10 phim đang chiếu; backend tự tạo `firefly.db`; `npm install` + build mock đạt; build real (`VITE_USE_MOCK=false`) ra `index-CuKoJ6_Y.js` trùng tên hash với repo chính |
| AC-02 SAO_LUU có checksum; tải lại 1 model từ Drive, checksum khớp | **Một phần**: checksum có; bước tải lại từ Drive **chờ Tín** (SAO_LUU mục 4.2) |
| AC-03 ≥ 8 ảnh tên rõ nghĩa, có Thống kê cảm xúc và So sánh mô hình | **PASS**: 14 ảnh (09, 10) |
| AC-04 Tín gắn tag `v1.0` sau PO_APPROVED | **Chờ Tín** |

## 5. Gate
| Gate | Kết quả |
|---|---|
| Trên repo chính, master `db4b452` (= T31 cuối): compileall, full pytest 286/286, build real + mock | Đạt (đo ở T31 round 2, code không đổi từ đó; T13 chỉ đổi tài liệu và ảnh) |
| Trên bản clone mới `C:\Temp\firefly-test` (`47dcdd1`) | compileall đạt, pytest 286/286, health `phobert_b`, build real + mock đạt (AC-01) |

Ghi chú: script dựng lại lần đầu chép `frontend/.env.example` (mặc định `VITE_USE_MOCK=true`) mà chưa sửa sang `false` như HUONG_DAN mục 4, nên bản build "real" trong log thực ra là mock. Claude build lại real riêng trên clone, kết quả như trên. Thư mục clone đã xóa sau khi kiểm để giải phóng ~3 GB.

## 6. Lỗi phát hiện khi dựng lại (AC-01 lần 1) và ngoại lệ allowlist
- **Lần 1** (clone `d26e0f0`): pip cài đủ, compileall đạt, nhưng `pytest` và `import app.main` đều lỗi `ZoneInfoNotFoundError: 'No time zone found with key Asia/Ho_Chi_Minh'`. Nguyên nhân: `chat_assistant.py:18` và `routers/chat.py:30` dùng `ZoneInfo`; Windows không có cơ sở dữ liệu múi giờ hệ thống, Python cần gói `tzdata`. Venv trên máy Tín tình cờ đã có `tzdata 2026.5` nên mọi gate trước đây vẫn đạt. Hậu quả: **cài mới theo hướng dẫn thì backend không khởi động được**.
- **Sửa** (`47dcdd1`): thêm `tzdata==2026.5` (đúng bản đang chạy) vào `backend/requirements.txt`. File này ngoài allowlist T13 và là thêm phụ thuộc → **PO cho phép trong chat 29/10/2026**. Không sửa code.
- **Lần 2**: xóa `C:\Temp\firefly-test`, clone lại từ `47dcdd1`, làm lại toàn bộ (kết quả ở mục 4).

## 7. Quan sát mới
- OBS-01: ở 390 px khi **chưa đăng nhập**, header xuống 2 hàng (ảnh 14). Không thuộc OBS-05 (chỉ trường hợp đã đăng nhập). Đã ghi vào Hạn chế; không sửa vì T13 không đụng code.

## 8. Phạm vi
File đổi: `README.md`, `HUONG_DAN.md`, `CHANGELOG.md`, `docs/SAO_LUU.md`, `docs/images/*`, `docs/CONG_NGHE.md`, `docs/ARCHITECTURE.md`, `docs/TASK_COORDINATION_ACTIVE.md`, report này (đúng mục 6 T13.md), cộng ngoại lệ `backend/requirements.txt` (mục 6). Không sửa code; không commit model/DB/.env/video/dữ liệu lớn.

## 9. Prompt Codex review T13
```text
Bạn là Codex, reviewer độc lập cho T13 "Chốt v1.0 và sao lưu" dự án Firefly Cinema (C:\Projects\firefly-cinema, Windows + PowerShell). Lần này Claude làm T13 theo lệnh PO; bạn review, không sửa file trong allowlist, không merge, không gắn tag.
Đọc: docs/tasks/T13.md, docs/TASK_COORDINATION_ACTIVE.md, reports/2026-10-29/claude_implementation_T13_2026-10-29.md.
Diff thật: git diff master...task/T13-v1. Kiểm scope theo mục 6 T13.md (chỉ tài liệu, ảnh, điều phối, report; không code; không model/DB/.env). Ngoại lệ duy nhất PO cho phép: thêm tzdata==2026.5 vào backend/requirements.txt (report mục 6) — xác minh lỗi thiếu tzdata trên venv mới và bản sửa.
1. Đối chiếu số liệu README (bảng F1, T15) với ml/model_card_B.md, ml/model_card_A.md, ml/results/*.csv; đối chiếu mục Hạn chế với quyết định PO ở docs/tasks/T31.md mục 13.
2. Làm lại AC-01 độc lập: clone ra một thư mục tạm khác (ví dụ C:\Temp\firefly-review), làm đúng HUONG_DAN mục "Cài đặt từ số 0", chép model từ backup\v1.0; chạy compileall, pytest, backend + /api/health (phobert_b, mọi model available), npm run build real + mock. Không đọc backend\.env thật; dùng .env mới từ .env.example với giá trị thử.
3. Kiểm docs/SAO_LUU.md: so 9 hash trong bảng với backup\v1.0\sha256.csv và với file thật trong repo.
4. Xem 14 ảnh docs/images: tên rõ nghĩa, đúng trang, không lộ dữ liệu nhạy cảm.
Kết luận PASS / PASS_WITH_TODO / FAIL. AC-02 (tải lại từ Drive) và AC-04 (tag) là việc của PO, không tính FAIL. Viết reports/YYYY-MM-DD/codex_review_T13_<RESULT>_YYYY-MM-DD.md, cập nhật file điều phối: PASS → PO_REVIEW, FAIL → FIX_LOOP. Commit "[T13] Codex review ...".
```
