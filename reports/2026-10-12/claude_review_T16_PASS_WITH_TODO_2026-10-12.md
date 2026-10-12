# Claude Review — T16 Giữ chỗ có hạn và thanh toán QR

- Ngày: 12/10/2026
- Reviewer: Claude (Independent Reviewer / Tester)
- Nhánh: `task/T16-giu-cho-thanh-toan` · commit implementation `d2bfd02` · base `master` `f67f72e`
- Report Codex: `reports/2026-10-12/codex_implementation_T16_2026-10-12.md` (chỉ dùng làm bằng chứng phụ)
- **Kết luận: PASS_WITH_TODO** · Required Fix: 0 · TODO: 7 (không TODO nào chặn T17)

## 1. Phạm vi đã kiểm
- Đọc diff thật `git diff master...task/T16-giu-cho-thanh-toan`, 25 file (+747/−46).
- Đối chiếu AC-01..AC-12, Definition of Done, allowlist, kiến trúc, bảo mật, hồi quy.
- Chạy gate độc lập; probe backend thật trên SQLite tạm; đi luồng giao diện mock trên trình duyệt.

## 2. Scope và bí mật
- Mọi file trong diff đều thuộc Allowed Files của `T16.md` mục 6. Không file nào trong Forbidden Files.
- Không có `.env`, `*.db`, sidecar, model, CSV trong diff; không thêm dependency (`requirements*.txt`, `package.json` không đổi).
- `backend/firefly.db` thật không bị đụng; mọi probe dùng DB trong thư mục scratchpad của Claude.

## 3. Gate độc lập
| Gate | Kết quả |
|---|---|
| `python -m compileall -q backend\app` | PASS |
| `pytest -q` | **36 passed**, 1 warning Starlette có từ trước |
| Backend khởi động (uvicorn cổng 8010, DB tạm) + `/api/health` | PASS — `status: ok`, `classifier: phobert_b`, 6 model, không lỗi |
| `npm run build` (real) | PASS |
| `VITE_USE_MOCK=true npm run build` | PASS |
| Mock mode trên trình duyệt | PASS — xem mục 5 |
| Scope / bí mật | PASS |

## 4. Probe độc lập trên backend thật (uvicorn + SQLite tạm) — 19/19 PASS
| AC | Kiểm tra | Kết quả |
|---|---|---|
| AC-01 | Đặt 2 ghế suất > 2 giờ: 201, `held`, `FF00143`, `hold_expires_at` = giờ chiếu − 30 phút; ghế xám trên sơ đồ | PASS |
| AC-07 | Không cấu hình ngân hàng → `qr_url: null` | PASS (vế có cấu hình: dựa pytest `test_qr_url_configured_and_missing`) |
| AC-04 | Vé `held` thứ hai cùng suất → 409 đúng câu; suất bắt đầu sau 20 phút → 400 "Suất chiếu sắp bắt đầu, vui lòng mua vé tại quầy." | PASS |
| AC-05 | `transfer-claim`: người khác 404; chủ vé 200 `pending_verify`; gọi lại 409; vé đã `expired` 409 | PASS |
| AC-06 | Anonymous 401, user 403; tìm mã viết thường `ff00143` ra đúng 1 vé kèm email khách; confirm → `paid`, confirm lại 409; reject → `rejected` và ghế trống lại; id không tồn tại 404 | PASS |
| AC-02 | **Thời gian thật:** suất bắt đầu sau ~31 phút, đặt `held` ghế D1, chờ qua hạn (~43 giây) → đọc sơ đồ: D1 trống, vé thành `expired` | PASS |
| AC-03 | Cùng suất đó, vé `pending_verify` ghế D2 vẫn giữ ghế sau hạn | PASS |

Ghi chú: suất sát giờ được chèn thẳng vào DB tạm (phòng "Phòng probe") vì phòng thật đã kín lịch buổi tối; không ảnh hưởng logic đang kiểm. Vế "người khác đặt lại ghế vừa nhả" của AC-02 không làm được trên suất sát giờ (bị chặn 30 phút cuối, đúng thiết kế); vế này có trong pytest `test_expired_hold_releases_unique_seat_for_another_user`.

## 5. Giao diện (mock mode, trình duyệt) — AC-08, AC-09
- Trang xác nhận: "Vé giữ chỗ sẽ tự hủy lúc 21:30 ngày 12-10 nếu chưa thanh toán (30 phút trước giờ chiếu)…" — giờ đúng (suất 22:00).
- "Vé của tôi": thông báo giữ chỗ thành công, nhãn "Giữ chỗ – chưa thanh toán", "Tự hủy lúc 21:30, Thứ 2 12/10/2026", ảnh QR VietQR tải được (540 px, `amount=190000&addInfo=FF00001`), "Nội dung chuyển khoản: FF00001", nút "Tôi đã chuyển khoản".
- Bấm nút → thông báo đã gửi, nhãn "Chờ xác nhận chuyển khoản", QR và nút biến mất.
- Admin `/quan-tri/ve`: mặc định lọc "Chờ xác nhận", hiện vé, khách, phim, ghế, tiền; "Đã nhận tiền" → "Đã xác nhận vé FF00001.", localStorage `1:paid`.
- Toàn bộ chữ tiếng Việt. Không kiểm bề ngang 375 px và hộp `window.confirm` (đã thay tạm bằng hàm trả `true` trong phiên probe).

## 6. Đối chiếu AC
| AC | Kết luận | Nguồn bằng chứng |
|---|---|---|
| AC-01 | PASS | Probe + pytest |
| AC-02 | PASS | Probe thời gian thật + pytest |
| AC-03 | PASS | Probe + pytest |
| AC-04 | PASS | Probe + pytest |
| AC-05 | PASS | Probe + pytest |
| AC-06 | PASS | Probe + pytest |
| AC-07 | PASS | Probe (null) + pytest (có cấu hình) |
| AC-08 | PASS | Trình duyệt (mock); còn TODO-02/03/04 |
| AC-09 | PASS | Trình duyệt (mock) đủ luồng `held → pending_verify → paid` |
| AC-10 | PASS | Đọc code `admin_movies.py` + pytest `test_delete_movie_ignores_expired_or_rejected_bookings` |
| AC-11 | PASS | pytest 36/36 |
| AC-12 | PASS | Mục 7 |

## 7. Checklist hồi quy `BOI_CANH_DU_AN.md` mục 7
| # | Mục | Kết quả |
|---|---|---|
| 1 | Trang chủ, poster | PASS (mock, trang chủ tải và điều hướng bình thường) |
| 2 | Menu/tìm kiếm | Không kiểm tay lại; code không đổi, pytest cũ PASS |
| 3 | Đăng nhập/đăng ký, chuyển hướng | PASS (đăng ký probe trên real; đăng nhập mock) |
| 4 | Đặt 2 ghế, ghế xám, Vé của tôi | PASS — vé mới ở trạng thái giữ chỗ |
| 5 | Bình luận tiêu cực bị ẩn | Không kiểm tay; `comments.py` không đổi, pytest cũ PASS |
| 6 | `/api/health` | PASS — lưu ý giá trị hiện tại là `phobert_b` (model mặc định từ T10) |
| 7 | Mock mode | PASS |

## 8. Required Fixes
Không có.

## 9. TODO (không chặn)
| ID | Mức | Nội dung | Đề xuất |
|---|---|---|---|
| TODO-01 | **Medium (vận hành)** | Đổi schema nên DB cũ (không có cột `status`) phải reset. Web đang deploy trên internet: deploy T16 lên server sẽ **mất tài khoản và vé thật** nếu reset; nếu không reset thì truy vấn `bookings` sẽ lỗi vì thiếu cột (suy luận từ `create_all` không thêm cột, chưa chạy thử trên DB cũ). | PO quyết định trước khi deploy: sao lưu + reset (chấp nhận mất dữ liệu demo) hoặc thêm cột bằng một lệnh `ALTER TABLE` có duyệt riêng. |
| TODO-02 | Low (UX) | Trang phim và sơ đồ ghế vẫn cho chọn suất trong 30 phút cuối; khách chỉ biết bị chặn khi bấm "Đặt vé" ở bước cuối. | Ẩn/vô hiệu suất trong 30 phút cuối ở giao diện, hoặc báo sớm ở trang chọn ghế. |
| TODO-03 | Low | `Checkout.jsx` hiện ngày dạng "12-10" (spec ghi DD/MM, nơi khác dùng 12/10/2026) và chép cứng số 30 thay vì dùng chung hằng số. | Dùng `fullDateTime` có sẵn hoặc định dạng `DD/MM`. |
| TODO-04 | Low | Vé `expired`/`rejected` trong "Vé của tôi" hiện mục "Ghế" trống (ghế đã bị xóa khi nhả). Trang admin đã ghi "Đã trả ghế". | Hiện "Đã trả ghế" giống admin. |
| TODO-05 | Low | Kiểm tra "một vé `held` mỗi suất" không nguyên tử: hai request đồng thời của cùng tài khoản với ghế khác nhau có thể tạo hai vé `held`. Ràng buộc UNIQUE ghế vẫn chống trùng ghế. | Chấp nhận cho khóa luận hoặc thêm khóa/partial unique index ở task sau. |
| TODO-06 | Info | `mock.js` bỏ việc xóa vé mỗi ngày và giữ lại suất có vé (thay đổi so với T04 TODO-08 WONT_FIX). Hợp lý cho luồng hết hạn, nằm trong allowlist. | Chấp nhận. |
| TODO-07 | Info | Admin `confirm` không gọi `expire_holds`, nên vé `held` đã quá hạn nhưng chưa bị hủy lười vẫn xác nhận được thành `paid`. Phù hợp tình huống khách trả tại quầy sát giờ. | Chấp nhận; ghi vào hạn chế nếu cần. |

## 10. Không kiểm / giới hạn của review
- Bề ngang 375 px, giao diện real mode trên trình duyệt (đã kiểm real bằng probe API, giao diện bằng mock).
- QR với cấu hình ngân hàng thật trên backend real (chỉ pytest).
- Chạy backend trên database thật / DB cũ chưa có cột `status` (bị cấm khi chưa có authorization của PO).

## 11. Trạng thái
- T16: `CLAUDE_REVIEW → PO_REVIEW`.
- T17: `PLANNED → READY_FOR_HANDOFF` (dependency duy nhất là T16, vừa PASS_WITH_TODO; không bị chặn bởi blocker hay câu hỏi mở).
- Claude không merge, không tag, không đóng T16.

## 12. Bàn giao task kế tiếp — T17

**Việc Tín làm trước khi gửi:**
1. PO review T16 (xử lý TODO-01 trước khi deploy lên server).
2. `git checkout master` → `git merge task/T16-giu-cho-thanh-toan`.
3. `git checkout -b task/T17-chatbot-tu-van` từ master đã merge.
4. Tạo key Gemini tại Google AI Studio, đặt vào `backend\.env` (`CHAT_API_KEY=...`) — **không** gửi key cho ChatGPT/Codex.
5. Gửi prompt dưới đây kèm `docs/tasks/T17.md` và `docs/TASK_COORDINATION_ACTIVE.md`.

```text
Bạn là Codex, Primary Implementer của dự án Firefly Cinema.
Chỉ đọc: PROJECT_SOURCE_OF_TRUTH.md, AGENT_RULES.md, TASK_COORDINATION_ACTIVE.md (Snapshot, Status, Next Step),
docs/tasks/T17.md, và source/test liên quan trực tiếp. Không đọc task CLOSED trừ khi là dependency.

Thực hiện T17 trên nhánh task/T17-chatbot-tu-van, chỉ sửa file trong Allowed Files của T17.md.
Lưu ý riêng T17:
- PO đã cho phép thêm đúng một thư viện: openai (ghim phiên bản chính xác trong backend/requirements.txt).
- Gọi Gemini qua cổng tương thích OpenAI; CHAT_BASE_URL/CHAT_API_KEY/CHAT_MODEL đọc từ .env.
  Không commit .env, không in key ra log/report. Kiểm tra tên model Flash còn hợp lệ trong gói miễn phí và ghi vào report.
- Công cụ của bot chỉ đọc phim/suất chiếu/giá; không đọc users, bookings, comments; không ghi DB.
- pytest phải dùng client giả lập, không gọi mạng. Backend phải khởi động bình thường khi không có key.
- Endpoint mới có ở cả real.js và mock.js, cùng cấu trúc {reply, movies}. Không thêm thư viện frontend.
Chạy gate theo AGENT_RULES.md mục 3.1 (focused trước, full sau), gồm pytest cũ của T11 và T16.
Tạo reports/<YYYY-MM-DD>/codex_implementation_T17_<YYYY-MM-DD>.md, ghi "Đổi schema: Không",
phiên bản openai, tên model, bằng chứng từng AC-01..AC-11 và checklist hồi quy.
Cập nhật TASK_COORDINATION_ACTIVE.md: T17 READY_FOR_HANDOFF -> IN_PROGRESS -> CLAUDE_REVIEW.
Không tự review, không tự PASS. Trả lời bằng tiếng Việt.
```
