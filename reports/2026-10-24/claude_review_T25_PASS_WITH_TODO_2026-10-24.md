# Claude Review — T25 Banner trailer và mục Nội dung phim

| Trường | Giá trị |
|---|---|
| Task | T25 |
| Nhánh / commit review | `task/T25-trailer-phim` @ `03e0d44` (base `master` `b8f6ef6`) |
| Ngày | 24/10/2026 |
| Reviewer | Claude (độc lập) |
| Kết luận | **PASS_WITH_TODO** |
| Required Fix | 0 |
| TODO | 2 (Low, không chặn) |

## 1. Scope
`git diff --stat master...task/T25-trailer-phim`: 20 file, +709/−61. **20/20 nằm trong allowlist** mục 6 của `T25.md`. Không có `.env`, `*.db`, video, model hay dữ liệu lớn trong diff. `requirements.txt`, `package.json` và biến `:root` không đổi.

`docs/tasks/T25.md` (bản PO duyệt) chưa từng được commit, vì Tín chưa trả lời câu hỏi commit lúc soạn. Codex đúng khi không stage file ngoài allowlist. Claude commit file này cùng review để Task Record có trong lịch sử, nội dung giữ nguyên.

## 2. Gate độc lập
| Gate | Kết quả |
|---|---|
| `compileall -q backend\app` | exit 0 |
| `pytest -q` | **194 passed** (148 cũ + 46 mới) |
| `npm run build` | đạt |
| Backend khởi động + health (SQLite và UPLOAD_DIR tạm, cổng 8005) | `status ok`, `classifier phobert_b` |
| Mock mode | đạt (mục 4) |
| Hồi quy | đạt (mục 5) |

## 3. Probe backend (HTTP thật, DB tạm)
| Trường hợp | Kết quả |
|---|---|
| Upload khi chưa đăng nhập / user thường | 401 / 403, câu tiếng Việt |
| Chữ ký PNG khai là `video/mp4`; body rỗng; `Content-Type: image/png` | 422 "Chỉ nhận video MP4 hoặc WebM." |
| `Content-Length` khai 101 MB | 413 ngay, không đọc body |
| Chunked 102 MB, không có `Content-Length` | 413, **không còn file `.tmp`** trong `uploads/trailers` |
| MP4 hợp lệ (200 KB) / WebM hợp lệ | 201, tên UUID đúng đuôi |
| GET không Range | 200, đúng byte, `Accept-Ranges: bytes`, `video/mp4` |
| `bytes=0-1023` / `bytes=1000-` / `bytes=-500` | 206, `Content-Range` đúng, nội dung khớp từng byte |
| Range vượt kích thước / multi-range | 416 `bytes */200012` |
| Tên sai, `..%2f..%2ffirefly.db`, UUID không tồn tại | 404 |
| `trailer_url`: youtu.be `?si=`, `watch&t=30s`, `m.`/shorts, embed, host viết HOA | 200, chuẩn hóa `https://www.youtube.com/watch?v=dQw4w9WgXcQ` |
| `evil.com`, `javascript:`, ID ngắn, `youtube.com.evil.com`, `user@`, cổng `:8080`, `/uploads/trailers/../x.mp4`, đường dẫn poster | 422 |
| `trailer_url` toàn khoảng trắng / `synopsis` toàn khoảng trắng | `null` |
| `synopsis` 5001 ký tự | 422 "Nội dung phim tối đa 5000 ký tự." |
| `GET /api/movies/{id}` | có `trailer_url`, `synopsis` |

## 4. Trình duyệt
**Real** (frontend 5179 → backend tạm 8005):
- **AC-01:** WebM thật 8 giây (tạo bằng canvas/MediaRecorder) chọn qua form Sửa phim "Mèo Mướp Đi Lạc". Lưu xong, banner có nút ▶ "Xem trailer phim Mèo Mướp Đi Lạc". Bấm thì video phát, `seekable` 0–7,9 s, tua tới 7,45 s được.
- **AC-03:** dán link YouTube kèm chọn file → lưu đường dẫn `/uploads/trailers/…webm` (file thắng). "Gỡ trailer" ở phim 2 → `trailer_url = null`.
- **AC-02:** phim 2 có link YouTube. Trước khi bấm không có iframe, 0 request tới youtube. Bấm thì iframe `youtube-nocookie.com/embed/dQw4w9WgXcQ?autoplay=1&rel=0`, có `title`, `allow`, `allowFullscreen`, phát được (có mạng); có link "Mở trên YouTube".
- **AC-06:** trước khi bấm, 0 request tới file trailer hay YouTube (chỉ có module `youtube.js` của chính web).
- Phim không có trailer: banner chỉ có poster, không nút ▶, không link ngoài. File hỏng (phim 19, byte ngẫu nhiên) → "Không phát được video trailer."
- **AC-07:** mục "NỘI DUNG PHIM" 2 đoạn, nằm sau khối thông tin, trước Lịch chiếu; `.detail__desc` đã bỏ. `synopsis` rỗng → hiện `description` (phim 3). Hero trang chủ vẫn dùng `description` ngắn.
- **AC-10:** 375px: `scrollWidth = 375`, nút ▶ 56px không đè tên phim; form admin 375px không tràn. 1280px: banner 1140×560, không tràn. Nút ▶ có `:focus-visible` outline.
- Console: 0 lỗi.

**Mock** (5174): upload WebM → `{trailer_url: "blob:…"}`; chữ ký PNG → 422; link `evil.com` → 422; youtu.be → chuẩn hóa. Trang chi tiết phát blob tới hết. Khóa JSON phim mock **trùng khít** real (20 khóa).

**AC-08:** hai `movies.json` giống hệt nhau, 21/21 phim có `synopsis` (2 đoạn, dài nhất 403 ký tự), 21/21 `trailer_url = null`.

## 5. Hồi quy
Phạm vi T25 chỉ đụng trang chi tiết phim, form phim và lớp API. Trên DB tạm: lịch chiếu `/phim/4` còn đủ 3 suất dẫn tới `/dat-ve/…`; hero trang chủ không đổi; health `phobert_b`. Sáng cùng ngày Claude đã chạy đủ checklist mục 7 trên `master` `b8f6ef6` (base của T25) và đạt; pytest 194/194 phủ đặt vé, bình luận, quyền admin. Report Codex ghi đủ 7 mục real/mock.

## 6. Kiến trúc / bảo mật
- Upload kiểm quyền bằng dependency **trước** khi đọc body, ghi dần ra file tạm, cắt ở 100 MiB, quyết định loại bằng chữ ký, `finally` dọn file tạm. Không ghép tên client vào đường dẫn.
- Route phát video đứng trước `app.mount("/uploads")`, tên phải khớp `fullmatch`, stream 64 KiB, không nạp cả file vào RAM.
- Validator YouTube chặn host giả, userinfo, cổng; lưu dạng chuẩn, bỏ tham số thừa. Frontend dùng một helper `utils/youtube.js` chung cho banner và mock.
- Iframe dùng `youtube-nocookie`, chỉ tạo sau khi bấm. Link ngoài có `rel="noopener noreferrer"`.
- Lỗi đều là `HTTPException` hoặc validator, kèm một câu tiếng Việt. Endpoint mới có ở cả `real.js` và `mock.js`, cùng JSON.

## 7. TODO (Low, không chặn)
**TODO-01 — Ô chọn file báo "No file chosen" sau khi đã chọn video.**
- File: `frontend/src/pages/AdminMovies.jsx`, hàm `selectVideo`.
- Problem: `selectVideo` gọi `clearVideo()` trước khi lưu file, mà `clearVideo` đặt `videoInputRef.current.value = ""`. Ô file trở về trống, trong khi dòng "Đã chọn: trailer-test.webm" vẫn hiện.
- Evidence: ảnh chụp form sửa phim 4 sau khi chọn file.
- Expected Fix: chỉ xóa state, không reset `input.value` khi đang chọn file mới. Có thể để T13 hoặc ghi là hạn chế.

**TODO-02 — Phim có video tải lên thì ô "Hoặc dán link YouTube" hiện đường dẫn nội bộ.**
- File: `frontend/src/pages/AdminMovies.jsx`.
- Problem: khi sửa phim có video tải lên, ô hiện `/uploads/trailers/<uuid>.webm`. Vẫn lưu đúng, nhưng nhãn dễ gây hiểu nhầm.
- Expected Fix: ô này hiện trống và có dòng "Đang dùng video đã tải lên" cùng nút Gỡ. Hoặc ghi là hạn chế.

## 8. Quan sát (không phải lỗi của T25)
- **OBS-01 (giao diện, PO tự đánh giá):** 21 phim mẫu đều không có `poster_url`, nên banner và khung poster ngay bên dưới cùng hiện một khối màu và tên phim, nhìn lặp. Khi có ảnh poster thật, ảnh dọc bị cắt theo khung 16:9.
- **OBS-02:** server trả 401 trước khi đọc body. Với file lớn và token đã hết hạn, một số client có thể bị đóng kết nối và thấy "Không kết nối được máy chủ" thay vì "phiên hết hạn". Probe bằng urllib gặp trường hợp này, http.client thì nhận 401 đúng. Khuyến nghị: đăng nhập lại trước khi tải video lên trong buổi demo.

## 9. Lưu ý cho PO trước khi merge
- **Đổi schema.** Backend thật đang chạy ở cổng 8000 vẫn là code cũ trong bộ nhớ. Sau khi merge, **không** khởi động lại backend trên `firefly.db` cũ, vì bảng `movies` thiếu 2 cột mới và trang phim sẽ lỗi. Làm theo `HUONG_DAN.md` mục T25: dừng backend, sao lưu DB, sidecar và cả `backend\uploads\`, kiểm SHA-256 và integrity, xóa `firefly.db`, rồi khởi động lại.
- Sau khi reset, mọi trailer đều trống. Tín tự thêm video hoặc link cho các phim muốn demo. Nên dùng MP4 H.264 dưới khoảng 50 MB; file MOV/HEVC phải chuyển định dạng trước.

## 10. Bàn giao task kế tiếp — prompt Codex T13
T25 PASS_WITH_TODO, nên T13 chuyển sang `READY_FOR_HANDOFF`, áp dụng **sau khi PO merge T25 và reset DB**. Tín điền quyết định trước khi gửi.

```text
Bạn là Codex, dự án Firefly Cinema (C:\Projects\firefly-cinema, Windows + PowerShell).
Đọc theo thứ tự: docs/PROJECT_SOURCE_OF_TRUTH.md, docs/AGENT_RULES.md, docs/TASK_COORDINATION_ACTIVE.md, docs/tasks/T13.md. T13.md là bản PO đã duyệt.
T24 và T25 đã merge vào master. Làm trên nhánh task/T13-v1 (tạo từ master mới). Đầu tiên ghi closure T24, T25 (merge hash) và đặt T13 → IN_PROGRESS.

Quyết định PO trước T13 (Tín điền trước khi gửi):
- T12 TODO-01 (model B che câu khen phim 1): <giữ nguyên + ghi hạn chế | admin duyệt sẵn | đổi phim mở đầu>
- T14 TODO-02 (mã vé dùng lại sau khi hủy): <ghi hạn chế | ...>
- T25 TODO-01/02 (ô chọn video báo trống; ô YouTube hiện đường dẫn nội bộ): <ghi hạn chế | ...>

Nhiệm vụ: T13 "Chốt v1.0 và sao lưu" — chỉ tài liệu và sao lưu, không viết tính năng.
- README.md (giới thiệu, ảnh, tính năng gồm T16–T25 với banner trailer, kết quả F1 A/B/SVM/NB/LR và T15, cách chạy nhanh), HUONG_DAN.md (cài từ số 0, gắn model A/B/SVM, cấu hình .env gồm BANK_* cho QR và CHAT_* cho chatbot — chỉ tên khóa, không giá trị; chạy test; reset demo; định dạng video trailer).
- Mục "Hạn chế" gom: các quyết định PO ở trên, T14 TODO-04 (đổi mật khẩu không vô hiệu token cũ), T22 (ai đăng nhập cũng chấm sao; OBS-01 model B nhầm câu khen), T23 OBS-01 (soát vé không chặn theo giờ chiếu), T24 OBS-01, T25 (file video mồ côi khi thay/gỡ; YouTube cần mạng và quyền nhúng; video mock mất khi tải lại).
- docs/SAO_LUU.md phải gồm cả backend\uploads\ (poster và trailers); docs/images/*, CHANGELOG.md [1.0.0], cập nhật cuối CONG_NGHE.md/ARCHITECTURE.md; xử lý T18 TODO-03 và T00 TODO-03 theo T13.md.
Ràng buộc: chỉ file trong mục 6 của T13.md; không sửa code; không commit model/DB/.env/video/dữ liệu lớn; không đọc hay in giá trị khóa trong .env.
Gate: compileall, pytest, npm run build (real + mock) để xác nhận không hồi quy.
Commit "[T13] mô tả". Viết reports/YYYY-MM-DD/codex_implementation_T13_YYYY-MM-DD.md, đặt T13 sang CLAUDE_REVIEW. Không merge, không gắn tag v1.0 (Tín gắn).
```

**Việc Tín cần làm:** review T25 → `git checkout master` → `git merge task/T25-trailer-phim` → làm reset DB theo mục 9 → thêm trailer thử → `git checkout -b task/T13-v1` → gửi prompt trên kèm `T13.md` và file điều phối.
