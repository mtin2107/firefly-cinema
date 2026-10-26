# Claude review T28 — PASS_WITH_TODO (27/10/2026)

- Nhánh: `task/T28-giao-dien-tai-khoan` @ `0589cec`, baseline master `bca6d23`.
- Nguồn đối chiếu: `docs/tasks/T28.md`, `git diff master...task/T28-giao-dien-tai-khoan`; report Codex `reports/2026-10-27/codex_implementation_T28_2026-10-27.md` chỉ là bằng chứng phụ.
- Runtime độc lập: backend cổng 8005 trên SQLite tạm (scratchpad), frontend real 5179, mock 5180. Không đụng `backend/firefly.db`.
- **Đổi schema: Không** (xác nhận: `models.py`, `seed.py` không có trong diff).

## 1. Kết luận
**PASS_WITH_TODO.** RF 0. TODO-01 Medium (form admin), OBS-01..06.

## 2. Scope và bảo mật
| Kiểm tra | Kết quả |
|---|---|
| File trong diff | 28 file, tất cả thuộc mục 6. 2 test cũ (`test_poster_upload.py`, `test_ratings.py`) bị ảnh hưởng trực tiếp: đúng ngoại lệ "test cũ chỉ sửa nếu bị ảnh hưởng trực tiếp" |
| File cấm | Không có `.env`, `*.db`, `movies.json`, `models.py`, `seed.py`, `package*.json`, `requirements*`, `classifier.py` |
| `:root` | Không đổi |
| `git diff --check` | exit 0 |
| Nguyên tắc 4.0 | Không có CSS hay điều kiện theo id/tên phim. Quy tắc dùng chung: `effective_status` (backend, kèm biểu thức SQL) và `effectiveStatus` (frontend + mock) |
| Endpoint mới | `GET /api/auth/me/summary` dùng `get_current_user`, mọi truy vấn lọc theo `user.id`; probe không token → 401 tiếng Việt |

## 3. Gate độc lập
| Gate | Kết quả |
|---|---|
| `compileall -q backend\app` | exit 0 |
| Backend + `/api/health` (8005, DB tạm) | `status: ok`, `classifier: phobert_b` |
| `npm run build` real | đạt, JS 437.25 kB, CSS 54.08 kB |
| Build mock (`VITE_USE_MOCK=true`) | đạt, JS 462.30 kB |
| pytest toàn bộ (chạy 00:11 ngày 27/10) | **208 passed, 1 failed** — lỗi duy nhất `test_sentiment_uses_effective_label_group_by_and_complete_daily`, đúng OBS-01 T27 (fail 0h–7h, có cả trên master). Được ngoại lệ ở AC-12 |
| Mock mode | Đăng nhập, trang Tài khoản đủ khối, footer đúng link, không lỗi console |

## 4. Đối chiếu AC
| AC | Kết quả | Bằng chứng của Claude |
|---|---|---|
| AC-01 UI-01 | PASS | Ảnh headless 1280px trang chủ và Khám phá: "THỨ BẢY KHÔNG / NGỦ", "NỬA VẦNG TRĂNG / HÀ TIÊN", "SƠN TINH THỦY / TINH: TRẬN CHIẾN / CUỐI" không còn dấu đè dòng. `line-height` 1.35, Codex giải thích vì sao vượt khoảng gợi ý 1.12–1.15: chấp nhận |
| AC-02 UI-02 | PASS | Ảnh Khám phá 1280px: hàng trộn sắp chiếu / đang chiếu / ngừng chiếu, các dòng thời lượng, điểm, thể loại và phần cuối thẳng hàng; tên 2 dòng không đẩy lệch |
| AC-02b UI-04 | PASS | API DB tạm ngày 27/10: phim 6 (24/10) `status=now_showing`, `stored_status=coming_soon`, nằm trong `?status=now_showing`; phim 11, 7, 19 vẫn `coming_soon`. Trang chi tiết phim 6 cho chấm điểm. Test `test_t28_movie_status.py` có trong pytest |
| AC-03 UI-03 | PASS | Ảnh 1280px: logo 1 dòng, nút Đăng nhập/Đăng ký 1 dòng, chuyển sang nút Menu. 1440px: menu đầy đủ, logo 1 dòng |
| AC-04 FX-01 | PASS | Probe 10 sao trong dialog ở 375px: mouseover → 40ms → mouseout → 500ms, 0/10 nút còn transform (trước sửa: kẹt `matrix(1.2…)`) |
| AC-05 FX-02 | PASS | 375px: 10 nút rộng 58px, 2 hàng; dialog clientWidth = scrollWidth = 336 |
| AC-06 FX-03 | PASS | Ảnh `/phim/6` 1280px: banner thấp, nền tối, tên phim trắng rõ, không còn khối trống lớn |
| AC-07 FX-04 | PASS | Ảnh hero 1440px: poster phụ không còn mảnh chữ |
| AC-08 | PASS | Summary của demo trên DB tạm: bookings 2 (không tính vé hết hạn), paid 1, total 150.000, 3 bình luận mới nhất đúng thứ tự; test `test_t28_account_summary.py` kiểm cách ly người dùng và nhãn người duyệt |
| AC-09 | PASS | `/tai-khoan` real 375px: hồ sơ (avatar chữ cái, vai trò, ngày tham gia), 6 ô số liệu, thể loại hay xem, vé gần đây, bình luận, điểm (trạng thái rỗng "Bạn chưa chấm điểm phim nào."), form cài đặt; không tràn ngang |
| AC-10 | PASS | Mock cùng bố cục và khóa; `meSummary` ở cả `real.js` và `mock.js` |
| AC-11 | PASS (theo code + report Codex) | `StarRating` bỏ tween khi `reduced`/`disabled`; số liệu không có tween. Claude không chạy lại riêng chế độ giảm chuyển động |
| AC-12 | PASS | Gate như mục 3; hồi quy: trang chủ, Khám phá, chi tiết, đăng nhập, chấm điểm, tài khoản chạy được trên real/mock. Claude không đặt vé hay bình luận lại, dựa vào report Codex mục hồi quy |
| AC-12b UI-05 | PASS | Footer: `mailto:2311558892@nttu.edu.vn`, `tel:0329711217`; giá trị chỉ khai báo trong `CONTACT` ở `config.js` |
| AC-13 | PASS (theo report Codex) | Codex tạo phim tên 200 ký tự qua form admin. Claude kiểm phần quy tắc chung bằng dữ liệu seed có sẵn (tên dài, 3 thể loại, không trailer) |

## 5. TODO
**TODO-01 — Medium — `frontend/src/pages/AdminMovies.jsx:145`**
- Problem: khi sửa một phim đã tự chuyển sang Đang chiếu, form điền `stored_status` (Sắp chiếu). Bấm Lưu mà không đổi gì thì bị chặn với câu "Phim sắp chiếu phải có ngày khởi chiếu sau hôm nay.", câu này dễ khiến admin đổi ngày thay vì đổi trạng thái.
- Evidence: DB tạm, `PUT /api/admin/movies/6` với đúng dữ liệu form gửi (`status=coming_soon`, ngày 24/10) → 422. DB thật đang có đúng trường hợp này (phim 6).
- Expected Fix: form điền trạng thái hiệu lực (`movie.status`) thay cho `stored_status`, hoặc câu lỗi gợi ý "đổi trạng thái sang Đang chiếu". Một dòng code. PO quyết FIX_NOW hoặc ghi hạn chế.

## 6. Quan sát (không chặn)
- **OBS-01:** Bỏ yêu cầu bắt buộc có poster khi tạo phim (thay đổi so với T19). Lý do: AC-13 do Claude soạn yêu cầu tạo phim không poster qua form. Phim không poster vẫn có poster màu (`Poster`). PO xác nhận chấp nhận.
- **OBS-02:** Breakpoint header đổi từ 1100px lên 1360px: ở 1280–1360px (laptop phổ biến) menu Thể loại/Quốc gia… nằm sau nút **Menu**. Đúng phương án T28 cho phép; PO xem có ưng giao diện không.
- **OBS-03:** `h1, h2, h3` toàn trang và tiêu đề hero tăng `line-height` lên 1.35. Khi tên phim ở hero xuống 2 dòng (vd 1440px "MÈO MƯỚP ĐI / LẠC") khoảng cách hai dòng khá thoáng. Thẩm mỹ, PO quyết.
- **OBS-04:** Bóng chào của chatbot che một phần thẻ phim ở cột cuối (có trước T28, ngoài scope).
- **OBS-05:** OBS-01 của T27 (`test_sentiment` fail 0h–7h) vẫn còn.
- **OBS-06:** Mock chatbot thêm nhận diện "sắp chiếu"/"ngừng chiếu" để chọn trạng thái; thay đổi nhỏ ngoài mô tả nhưng nằm trong file được phép và đi kèm UI-04.

## 7. Việc PO cần làm
1. Xử lý TODO-01 (FIX_NOW qua Codex hoặc ghi hạn chế) và quyết OBS-01..03.
2. Merge `task/T28-giao-dien-tai-khoan` vào master. **Không cần reset DB.**
3. Xóa nhánh rỗng `task/T13-ten-task`, tạo `task/T13-v1` từ master mới.

## 8. Bàn giao task kế tiếp — prompt Codex T13
T28 PASS_WITH_TODO, TODO-01 không chặn T13, nên T13 chuyển sang `READY_FOR_HANDOFF` sau khi PO merge T28. Prompt giữ nguyên bản ở report T27 mục 8, bổ sung T28:

```text
Bạn là Codex, dự án Firefly Cinema (C:\Projects\firefly-cinema, Windows + PowerShell).
Đọc theo thứ tự: docs/PROJECT_SOURCE_OF_TRUTH.md, docs/AGENT_RULES.md, docs/TASK_COORDINATION_ACTIVE.md, docs/tasks/T13.md. T13.md là bản PO đã duyệt.
T24–T28 đã merge vào master; DB thật đã reset sau T27, T28 không đổi schema. Làm trên nhánh task/T13-v1 (tạo từ master mới). Đầu tiên ghi closure T24–T28 (merge hash) và đặt T13 → IN_PROGRESS.

Quyết định PO trước T13 (Tín điền trước khi gửi):
- T12 TODO-01 (model B che câu khen phim 1): <giữ nguyên + ghi hạn chế | admin duyệt sẵn | đổi phim mở đầu>
- T14 TODO-02 (mã vé dùng lại sau khi hủy): <ghi hạn chế | ...>
- T25 TODO-01/02 (ô chọn video báo trống; ô YouTube hiện đường dẫn nội bộ): <ghi hạn chế | ...>
- T27 TODO-01 (validator điểm dựa vào tên lớp) và OBS-01 (test_sentiment fail 0h–7h): <ghi hạn chế | ...>
- T28 TODO-01 (form sửa phim tự chuyển trạng thái) và OBS-01..03 (poster không bắt buộc, menu gọn ở ≤1360px, line-height tiêu đề): <đã sửa | ghi hạn chế | ...>

Nhiệm vụ: T13 "Chốt v1.0 và sao lưu" — chỉ tài liệu và sao lưu, không viết tính năng.
- README.md (giới thiệu, ảnh, tính năng gồm T16–T28: banner trailer, Nội dung phim, khung đánh giá thang 10 có hiệu ứng, trạng thái phim tự chuyển theo ngày khởi chiếu, trang Tài khoản có số liệu, liên hệ cuối trang; kết quả F1 A/B/SVM/NB/LR và T15; cách chạy nhanh), HUONG_DAN.md (cài từ số 0, gắn model A/B/SVM, cấu hình .env gồm BANK_* cho QR và CHAT_* cho chatbot — chỉ tên khóa, không giá trị; chạy test; reset demo; định dạng video trailer).
- Mục "Hạn chế" gom: các quyết định PO ở trên, T14 TODO-04 (đổi mật khẩu không vô hiệu token cũ), T22 (ai đăng nhập cũng chấm điểm; OBS-01 model B nhầm câu khen), T23 OBS-01 (soát vé không chặn theo giờ chiếu), T24 OBS-01, T25 (file video mồ côi khi thay/gỡ; YouTube cần mạng và quyền nhúng; video mock mất khi tải lại).
- docs/SAO_LUU.md phải gồm cả backend\uploads\ (poster và trailers); docs/images/*, CHANGELOG.md [1.0.0], cập nhật cuối CONG_NGHE.md/ARCHITECTURE.md; xử lý T18 TODO-03 và T00 TODO-03 theo T13.md.
Ràng buộc: chỉ file trong mục 6 của T13.md; không sửa code; không commit model/DB/.env/video/dữ liệu lớn; không đọc hay in giá trị khóa trong .env.
Gate: compileall, pytest (chạy ban ngày, sau 7h sáng), npm run build (real + mock) để xác nhận không hồi quy.
Commit "[T13] mô tả". Viết reports/YYYY-MM-DD/codex_implementation_T13_YYYY-MM-DD.md, đặt T13 sang CLAUDE_REVIEW. Không merge, không gắn tag v1.0 (Tín gắn).
```

**Việc Tín cần làm:** quyết TODO-01 → merge `task/T28-giao-dien-tai-khoan` → `git checkout -b task/T13-v1` từ master → điền quyết định PO → gửi prompt trên.
