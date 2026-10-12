# Claude Review — T17 Chatbot AI tư vấn phim

- Ngày: 13/10/2026
- Reviewer: Claude (Independent Reviewer / Tester)
- Nhánh: `task/T17-chatbot-tu-van` · commit implementation `8ab2f00` · base `master` `c07fc4a`
- Report Codex: `reports/2026-10-12/codex_implementation_T17_2026-10-12.md` (chỉ dùng làm bằng chứng phụ)
- **Kết luận: PASS_WITH_TODO** · Required Fix: 0 · TODO: 8 · **AC-02: PENDING PO_REVIEW** (chưa có bằng chứng với key Gemini thật)

## 1. Phạm vi đã kiểm
- Đọc diff thật `git diff master...HEAD`: 18 file (+828/−16), một commit `[T17] Implement read-only AI cinema chatbot`.
- Đọc trực tiếp `chat_assistant.py`, `routers/chat.py`, phần thêm ở `schemas.py`, `config.py`, `main.py`, `ChatWidget.jsx`, `mock.js`, `real.js`, CSS, `test_chat.py`.
- Đối chiếu AC-01..AC-11, Definition of Done, allowlist/forbidden list, bảo mật, hồi quy.
- Chạy gate độc lập, probe tạm 7 test (đã xóa trước gate cuối), backend thật trên SQLite tạm, giao diện mock trên trình duyệt ở 375×740.
- Không dùng, không nhận, không ghi API key thật. Không đụng `backend/firefly.db`.

## 2. Scope và bí mật
- Mọi file trong diff thuộc Allowed Files của `T17.md` mục 6. `routers/movies.py` không đổi (chỉ import `_plain`, `_split`).
- Không file nào thuộc Forbidden Files: không `.env`, `*.db`, `backend/models/`, `models.py`, `seats.py`, `classifier.py`, `bookings.py`, `package.json`, `docs/tasks/*`, tài liệu PO.
- `global.css` chỉ thêm class `.chat-*`, không đổi `:root`.
- `requirements.txt` chỉ thêm đúng một dòng `+openai==3.29.0` (venv có `openai 3.29.0`).
- Quét regex key (`AIza…`, `sk-…`, `gsk_…`) trên toàn diff: không có. `.env.example` để `CHAT_API_KEY=` rỗng.
- `git diff --check master...HEAD`: sạch.
- `backend/firefly.db` SHA-256 trước và sau review: `B3F7DF79BDA4478412200EA80B8EC15E6B73DA730068A52E11C40136EAC4CFE3` (không đổi).

## 3. Gate độc lập (AGENT_RULES.md mục 3.1)
| Gate | Kết quả |
|---|---|
| `python -m compileall -q backend\app` | PASS (exit 0) |
| `pytest -q` toàn bộ | **50 passed**, 1 warning Starlette có từ trước (chạy 2 lần: trước probe và gate cuối sau khi xóa probe) |
| `pytest -q tests/test_chat.py` | **14 passed** |
| Backend khởi động (uvicorn cổng 8017, SQLite tạm trong scratchpad, `CHAT_API_KEY` rỗng) + `/api/health` | PASS — `status: ok`, `classifier: phobert_b`, `classifier_error: null` |
| `npm run build` (real) | PASS |
| `VITE_USE_MOCK=true npm run build` | PASS |
| Mock mode trên trình duyệt | PASS — xem mục 5 |
| Scope / bí mật | PASS — mục 2 |
| Hồi quy | Xem mục 7 |

Ghi chú môi trường: sandbox chặn thư mục tạm mặc định của pytest nên Claude chạy với `-p no:cacheprovider --basetemp <scratchpad>`; không ảnh hưởng kết quả.

## 4. Probe độc lập
### 4.1. Backend thật (uvicorn + SQLite tạm, không key)
| Kiểm tra | Kết quả |
|---|---|
| Khách gọi `POST /api/chat` | 401 |
| User đăng ký mới, gọi `/api/chat` khi không có key | 503 `"Trợ lý chưa được bật."` |
| Log uvicorn | Chỉ có dòng access 401/503, không traceback, không key/URL nhà cung cấp |

### 4.2. Probe pytest tạm (`tests/test_zz_claude_probe_t17.py`, đã xóa) — 7/7 PASS
| # | Kiểm tra | Kết quả |
|---|---|---|
| P01 | Validation: 11 tin; tin 501 ký tự; tin cuối `assistant`; role `system`; trường thừa; nội dung rỗng | Tất cả 422, câu tiếng Việt dạng `Trường '…' không hợp lệ: …`. 11 tin trả câu chung "Giá trị không hợp lệ." (TODO-06) |
| P02 | `openai.RateLimitError`, `APITimeoutError`, `APIConnectionError`, `AuthenticationError` có chuỗi key giả trong message | Tất cả 503 `"Trợ lý đang bận, bạn thử lại sau ít phút."`; body không chứa key, không chứa `googleapis` |
| P03 | Model gọi công cụ lạ `delete_bookings`, `movie_id` chèn SQL, tham số không phải JSON, tham số mảng, tham số thừa `sql`, ngày `2099-99-99` | Lần lượt trả `Công cụ không hợp lệ`, `Mã phim không hợp lệ`, `Tham số công cụ không hợp lệ`, bỏ qua trường thừa, `Tham số…`, `Ngày phải có dạng YYYY-MM-DD`; không ngoại lệ, không ghi DB |
| P04 | `search_movies(genre=…)` với "Tâm lý" / "tâm lý" / "tam ly"; câu trả lời viết tên phim không dấu | Chỉ "Tâm lý" khớp; nút phim rỗng khi tên không trùng nguyên văn (TODO-01, TODO-02) |
| P05 | Nhà cung cấp lỗi liên tục | 5 lần 503 rồi 429: lượt lỗi vẫn bị trừ hạn mức (TODO-07) |
| P06 | `CHAT_RATE_PER_DAY=3` | `[200, 200, 200, 429]` |
| P07 | Dữ liệu ba công cụ gửi cho nhà cung cấp | Chỉ id, tên, thể loại, thời lượng, độ tuổi, trạng thái, mô tả ≤240 ký tự, giờ/phòng/giá suất, phụ thu VIP; không có email, mật khẩu, vé, ghế đã đặt |

Thêm: kiểm tra trên SDK `openai 3.29.0` cho thấy `tool_call.model_dump(exclude_none=True)` giữ trường phụ `extra_content` (nơi Gemini đặt thought signature), nên vòng gọi công cụ thứ hai không làm mất chữ ký. Chỉ là kiểm tra cấu trúc, chưa thay được AC-02.

## 5. Giao diện (mock, trình duyệt, 375×740)
| Kiểm tra | Kết quả |
|---|---|
| Nút tròn `aria-label="Mở trợ lý"`, mặc định ở cạnh phải, 46×46 px | PASS |
| Khách: focus nút → Enter mở khung, hiện "Đăng nhập để trò chuyện với trợ lý." + link Đăng nhập + dòng "Không nhập thông tin cá nhân…" | PASS |
| Esc đóng khung, focus trả về nút | PASS |
| User demo: lời chào + 3 câu gợi ý; gửi câu, nhận `{reply, movies}`, nút dẫn `/phim/:id` | PASS |
| "Bản Hòa Âm Mùa Hạ chiếu mấy giờ, giá bao nhiêu?" | Trả 2 suất tương lai kèm giá, phụ thu VIP 20.000đ (tính từ `totalPrice`), 1 nút `/phim/9` |
| "Gợi ý phim hài đang chiếu" (câu gợi ý số 2) | **Mock trả câu về giá vé** thay vì gợi ý phim (TODO-03) |
| Kéo thả bằng chuột: thả ở đáy, nút hút về cạnh phải, lưu `{"side":"right","fraction":1}`; thả không bật/tắt khung | PASS |
| Tải lại trang: nút giữ vị trí đã lưu, khung đóng, lịch sử chat mất (đúng spec) | PASS |
| Không cuộn ngang ở 375px (`scrollWidth = 375`) | PASS |
| Trang chọn ghế `/dat-ve/21`, vị trí mặc định: nút "Tiếp tục" (y 672–726) không bị che, `elementFromPoint` ở tâm trúng nút | PASS |
| Trang chọn ghế, nút chat kéo xuống đáy | Nút chat đè mép phải của "Tiếp tục"; tâm nút vẫn bấm được và có thể kéo nút chat đi (TODO-04) |

Không kiểm trên trình duyệt: trang `/xac-nhan` (cùng kiểu thanh `summary-bar` cố định ở đáy), thiết bị cảm ứng thật, trình đọc màn hình.

## 6. Acceptance Criteria
| AC | Kết quả | Bằng chứng |
|---|---|---|
| AC-01 | PASS | Uvicorn 401; `test_login_required`; widget khách hiện lời mời đăng nhập (mục 5) |
| AC-02 | **PENDING PO_REVIEW** | Không có key thật. Cấu trúc tool loop, link phim và giữ thought signature đã kiểm gián tiếp. Rủi ro cần PO để ý khi thử: TODO-01, TODO-02, TODO-05 |
| AC-03 | PASS | `test_get_showtimes_and_links_from_tools`, `test_three_rounds_maximum` (đúng 4 lần gọi, lần cuối không có `tools`); P03 |
| AC-04 | PASS | `test_invalid_messages` + P01; mọi câu 422 bằng tiếng Việt, không lộ câu Pydantic tiếng Anh |
| AC-05 | PASS | `test_rate_limit_independent_accounts` (tin thứ 6 → 429 đúng câu, tài khoản khác 200); P06 hạn mức ngày |
| AC-06 | PASS | Uvicorn không key: health ok + 503 "Trợ lý chưa được bật."; P02 bốn loại lỗi SDK → 503 sạch. `classifier: phobert_b` là mặc định đã chốt ở Q3 (T10), không phải lỗi |
| AC-07 | PASS | Đọc code: chỉ 3 công cụ, whitelist tên, chỉ `select` trên `Movie`/`Showtime` + hằng số `seats.py`; `test_tools_do_not_write_to_db`; P03, P07 |
| AC-08 | PASS | `real.js` và `mock.js` cùng `chat.send(messages)` → `{reply, movies}`; mock chạy trên trình duyệt; build mock PASS |
| AC-09 | PASS | Chuột + bàn phím (Enter/Esc/focus-visible), 375px, không che "Tiếp tục" ở vị trí mặc định; xem TODO-04 |
| AC-10 | PASS | Không `.env` trong diff; `requirements.txt` đúng một dòng `openai==3.29.0` |
| AC-11 | PASS (backend/build) · hồi quy xem mục 7 | pytest 50/50 gồm T11, T16 và 14 test T17 |

**Kết quả AC: 10/11 PASS, AC-02 PENDING PO_REVIEW.**

## 7. Checklist hồi quy `BOI_CANH_DU_AN.md` mục 7
| # | Mục | Claude kiểm | Ghi chú |
|---|---|---|---|
| 1 | Trang chủ, hiệu ứng poster | Một phần: trang chủ mock hiện phim, nút "Đặt vé"/"Xem chi tiết" hiển thị | Hiệu ứng: PO attested |
| 2 | Thể loại/chủ đề, tìm "meo muop" | Gián tiếp: pytest T11 PASS; T17 không đổi `movies.py` | PO attested trên giao diện |
| 3 | Đăng ký, chuyển hướng đăng nhập | Đăng ký qua API backend thật (SQLite tạm) PASS | Chuyển hướng: PO attested |
| 4 | Đặt 2 ghế, ghế xám, Vé của tôi | Gián tiếp: pytest T16 PASS; trang chọn ghế mock render đúng, ghế đã đặt xám | PO attested |
| 5 | Bình luận tiêu cực bị ẩn, điểm ~0,99 | Gián tiếp: pytest comment PASS (classifier giả lập) | PhoBERT thật: PO attested; T17 không đụng classifier |
| 6 | `/api/health` | PASS — `phobert_b` (mặc định sau Q3) | |
| 7 | Mock mode | PASS | |

**Đối chiếu với PO:** khớp với 7/7 PO xác nhận thủ công trong report Codex. Claude không tự nâng các mục "PO attested" thành bằng chứng độc lập. T17 không sửa file nào liên quan mục 1–5 ngoài việc gắn `<ChatWidget />` vào `App.jsx`, nên rủi ro hồi quy thấp.

## 8. Required Fixes
Không có.

## 9. TODO (không chặn, đề xuất disposition cho PO)
| ID | Mức | Vấn đề | Bằng chứng | Đề xuất |
|---|---|---|---|---|
| TODO-01 | **Medium (chất lượng AC-02)** | `search_movies(genre=…)` so khớp nguyên văn có dấu, phân biệt hoa thường (giống `movies.py`), và schema công cụ không liệt kê thể loại hợp lệ. Model gửi "hài" hoặc "hai" thay vì "Hài" sẽ nhận danh sách rỗng, bot có thể trả lời "không có phim hài". | P04: "tâm lý", "tam ly" → `[]`; `chat_assistant.py` dòng so khớp `str(genre).strip() in _split(m.genre)` | PO thử câu "Gợi ý phim hài đang chiếu" khi làm AC-02. Nếu sai: `FIX_NOW` bằng so khớp qua `_plain()` hoặc thêm `enum` thể loại vào schema công cụ (chỉ trong `chat_assistant.py`) |
| TODO-02 | Low–Medium (AC-02) | Nút phim chỉ hiện khi tên phim từ công cụ xuất hiện **nguyên văn** trong câu trả lời. Model viết tắt, viết hoa, bỏ dấu hoặc chỉ nói "phim này" thì không có nút. Chặt hơn spec ("phim bot đã nhắc tới, lấy từ kết quả công cụ") nhưng giảm khả năng đạt vế "có nút dẫn tới trang phim" của AC-02. | P04: câu trả lời "PHIM THU NGHIEM" → `movies: []` | Theo dõi ở AC-02. Nếu thiếu nút: so khớp không dấu bằng `_plain()` hoặc dùng phim của lần gọi `get_showtimes` cuối cùng |
| TODO-03 | Low (mock) | Mock coi câu có "hai" (sau khi bỏ dấu, tức "hài") là câu hỏi giá. Câu gợi ý số 2 "Gợi ý phim hài đang chiếu" trả về câu về giá vé, không gợi ý phim hài. | Trình duyệt mock, mục 5; `mock.js` `mockChat`, điều kiện `question.includes("hai")` | `FIX_NOW` nếu dùng mock khi bảo vệ (bỏ `"hai"` khỏi điều kiện giá, lọc theo thể loại "Hài"); nếu không thì `ACCEPT_LATER` |
| TODO-04 | Low (UX) | Khi người dùng kéo nút chat xuống đáy màn hình, nút đè mép phải của "Tiếp tục" trên `summary-bar` (trang chọn ghế, có thể cả xác nhận). Vẫn bấm được và kéo nút chat đi được. | Mục 5: mép phải `elementFromPoint` trúng nút chat, tâm trúng "Tiếp tục" | `ACCEPT_LATER`. Muốn sửa: giới hạn vùng thả phía trên `summary-bar` hoặc ẩn nút khi có thanh tóm tắt |
| TODO-05 | Info (PO verify) | Model mặc định `gemini-3.8-flash` và hạn mức RPM/TPM/RPD chưa được kiểm trên tài khoản AI Studio. Claude không xác minh được tên model này còn hợp lệ. | Report Codex: quota "PENDING ACCOUNT-SPECIFIC PO VERIFICATION" | PO kiểm khi làm AC-02; nếu model không tồn tại thì đổi `CHAT_MODEL` trong `.env` (không cần sửa code) và ghi tên model thật vào PO review |
| TODO-06 | Low | 11 tin nhắn trả câu chung "Trường 'messages' không hợp lệ: Giá trị không hợp lệ." vì kiểu lỗi `too_long` của list chưa có trong bảng dịch. Vẫn là tiếng Việt, đạt AC-04. | P01 | `ACCEPT_LATER` hoặc `WONT_FIX`; giao diện đã tự cắt còn 10 tin nên người dùng thường không gặp |
| TODO-07 | Info | Hạn mức bị trừ trước khi gọi nhà cung cấp, nên lượt 503 do nhà cung cấp lỗi vẫn tính. Hợp lý để chống spam khi nhà cung cấp đang lỗi. Bộ đếm trong bộ nhớ, reset khi restart, không chia sẻ giữa worker (đã có comment `shortcut:` theo spec). | P05 | `ACCEPT`; ghi vào hạn chế khóa luận nếu cần |
| TODO-08 | Info (vận hành) | `backend/firefly.db` vẫn có SHA-256 trùng giá trị sau ALTER của T10 (`B3F7…CFE3`), tức DB thật **chưa** được xử lý schema T16 (T16 TODO-01). Nếu PO làm AC-02 trên DB thật, backend có thể lỗi ở truy vấn `bookings` trước cả khi chat. | Mục 2 | Làm AC-02 trên SQLite tạm (như `HUONG_DAN.md` mục T17 hướng dẫn), hoặc xử lý T16 TODO-01 trước. Không đổi disposition của T16 TODO-01 |

## 10. TODO-01..07 của T16
Giữ nguyên nội dung và disposition theo `reports/2026-10-12/claude_review_T16_PASS_WITH_TODO_2026-10-12.md`. Review này không sửa, không đóng TODO nào của T16. TODO-08 ở trên chỉ ghi nhận rằng T16 TODO-01 vẫn còn mở trên DB thật.

## 11. Definition of Done
| Mục | Kết quả |
|---|---|
| Code trong allowlist, commit `[T17] …` | Đạt |
| Gate web 3.1 | Đạt (mục 3) |
| Test mới cho logic mới, test cũ PASS | Đạt (14 test T17, 50/50 tổng) |
| Report ghi phiên bản `openai`, tên model, hạn mức free | Có `openai==3.29.0` và `gemini-3.8-flash`; hạn mức **PENDING PO** (TODO-05) |
| Tài liệu `HUONG_DAN.md`, `ARCHITECTURE.md`, `CONG_NGHE.md` | Đã cập nhật; `HUONG_DAN` nhắc dùng SQLite tạm và không commit key |
| Đổi schema | Không |

**Technical DoD: MET, trừ phần cần key/tài khoản thật (AC-02, hạn mức) để PO_REVIEW.**

## 12. Không kiểm / giới hạn của review
- Gọi Gemini thật (không có key, theo yêu cầu không dùng key thật).
- Trang `/xac-nhan` ở 375px, thiết bị cảm ứng thật, trình đọc màn hình.
- Giao diện real mode với backend thật trên trình duyệt (real được kiểm bằng API).
- Mục hồi quy 1–5 trên giao diện real (dựa PO attestation + pytest).
- Backend trên database thật (bị cấm khi chưa có authorization PO).

## 13. Trạng thái
- T17: `CLAUDE_REVIEW → PO_REVIEW`. AC-02 giữ `PENDING PO_REVIEW`.
- **Task kế tiếp: không mở.** Theo thứ tự bàn giao, task chưa xong tiếp theo là T12, nhưng T12 đang `PLANNED / NOT AUTHORIZED` và có mâu thuẫn chưa giải quyết (PO báo T12/T13 đã xong/deploy ngày 12/10 nhưng repo chưa có commit; Q4 còn mở). Vì vậy T12 không đạt điều kiện "không bị chặn bởi câu hỏi mở hay blocker" ở `AGENT_RULES.md` mục 1.1. Tín cần đồng bộ T12/T13 hoặc chỉ định task kế tiếp.
- Claude không merge, không tag, không đóng T17, không approve.

## 14. Việc Tín làm ở PO_REVIEW
1. Tạo SQLite tạm (hoặc DB đã xử lý T16 TODO-01), đặt `CHAT_API_KEY` trong `backend\.env` (không commit, không dán vào report).
2. Kiểm tên model `CHAT_MODEL` còn hợp lệ và hạn mức free trong AI Studio (TODO-05).
3. Thử AC-02: "Tối nay có phim gì?", "Phim <tên> chiếu mấy giờ ngày mai, giá bao nhiêu?", và thêm "Gợi ý phim hài đang chiếu" (TODO-01). Đối chiếu giờ/giá với trang phim, kiểm có nút dẫn tới trang phim (TODO-02).
4. Ghi disposition cho TODO-01..08 trong `po_review_T17_*`.
5. Nếu đạt: merge `task/T17-chatbot-tu-van` vào `master`; chỉ định task kế tiếp.
