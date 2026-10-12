# Claude Review — T17 Round 2 (TODO-03 fix verification)

- Task: T17 — Chatbot AI tư vấn phim
- Ngày: 13/10/2026
- Nhánh: `task/T17-chatbot-tu-van`
- Commit được review: **`447c941`** `[T17] Fix mock comedy recommendation` (so với `7e161b1` — Claude Round 1)
- Implementation gốc: `8ab2f00`
- Kết luận: **PASS_WITH_TODO** — Required Fixes **0**; **TODO-03 FIXED (Claude xác minh độc lập)**; thêm 2 TODO Low mới (mock-only).
- Đổi schema: Không. Không cần xóa `backend/firefly.db`.

## 1. Phạm vi thay đổi của `447c941`
`git diff --stat 7e161b1..447c941`:

| File | Loại | Ghi chú |
|---|---|---|
| `frontend/src/api/mock.js` | production (mock) | +7/−1 trong `mockChat`: thêm `wantsComedy`, lọc phim `now_showing` có thể loại "Hài hước" (so khớp qua `plain()`), bỏ `"hai"` khỏi điều kiện câu hỏi giá |
| `docs/TASK_COORDINATION_ACTIVE.md` | điều phối | chuyển T17 sang CLAUDE_REVIEW Round 2 |
| `reports/2026-10-13/codex_fix_T17_round1_2026-10-13.md` | report Codex | bằng chứng fix |

Không đụng `real.js`, `ChatWidget.jsx`, backend, `chat_assistant.py`, schema, dependency. Hành vi REAL/Gemini, bảo mật và dữ liệu đặt vé **không thay đổi** (xác minh bằng diff: chỉ hàm `mockChat` thay đổi, không ghi `db`, không gọi `save()`).

## 2. Kết quả TODO-03 — **FIXED**
Probe tạm: tải `src/api/mock.js` qua Vite SSR (`ssrLoadModule`) với `localStorage` giả, đăng ký user mock, gọi `mockApi.chat.send(...)` — tức đúng đường code mà giao diện MOCK dùng. Chạy 2 bộ dữ liệu: mặc định và bộ đã chuyển mọi phim "Hài hước" đang chiếu sang `ended`. Probe nằm trong scratchpad, đã xóa trước gate cuối.

| # | Câu hỏi | Dữ liệu mặc định | Không có phim hài đang chiếu | Kết luận |
|---|---|---|---|---|
| 1 | Gợi ý phim hài đang chiếu | "Các phim bạn có thể xem: Thứ Bảy Không Ngủ…", nút `5:Thứ Bảy Không Ngủ` | "Hiện chưa có phim phù hợp…", không nút | **PASS** |
| 2 | goi y phim hai dang chieu (không dấu) | Thứ Bảy Không Ngủ | chưa có phim phù hợp | **PASS** |
| 3 | Có phim hài hước nào không? | Thứ Bảy Không Ngủ | chưa có phim phù hợp | **PASS** |
| 4 | Phim hài | Thứ Bảy Không Ngủ | chưa có phim phù hợp | **PASS** |
| 5 | Ghế VIP giá bao nhiêu? | "…Ghế VIP phụ thu 20.000đ…", `movies: []` | như cũ | **PASS** |
| 6 | Tối nay có phim gì? | 3 phim đang chiếu (id 1, 2, 3) kèm nút | như cũ | **PASS** — nút dẫn `/phim/{id}` (`ChatWidget.jsx:172`, không đổi từ Round 1) |
| 7 | Thứ hai có phim gì? | 3 phim đang chiếu, **không** còn trả câu giá | như cũ | **PASS** (trước fix: `"hai"` kích hoạt nhánh giá) |
| 8 | Phim chiếu thứ hai giá bao nhiêu? | câu giá (do có "giá") | như cũ | **PASS** — đúng ý định |
| 9 | Thứ hai có phim hài không? | Thứ Bảy Không Ngủ | chưa có phim phù hợp | **PASS** — "thứ hai" không làm hỏng nhận diện |
| 10 | Phim hài giá bao nhiêu? | câu giá + nút Thứ Bảy Không Ngủ | câu giá, không nút | Chấp nhận được |
| 11 | Gợi ý phim hài? (dấu `?` dính liền) | 3 phim đang chiếu chung, **không lọc hài** | như cũ | Lệch nhẹ → **TODO-09** |
| 12 | Gợi ý phim gia đình | **câu giá vé** | như cũ | Lỗi cùng loại TODO-03, có từ `8ab2f00` → **TODO-10** |

Dữ liệu `movies.json`: 9 phim `now_showing`, chỉ "Thứ Bảy Không Ngủ" (id 5, `Hài hước`) là phim hài đang chiếu → kết quả 1–4 đúng dữ liệu. So khớp thể loại qua `plain(genre.trim()) === "hai huoc"` nên dữ liệu có dấu hay không dấu đều khớp; tách theo dấu phẩy nên "Gia đình, Hài hước" / "Hài hước, Tâm lý" cũng được tính.

## 3. Quality gates độc lập (AGENT_RULES 3.1)
| Gate | Kết quả |
|---|---|
| `python -m compileall -q backend\app` | PASS |
| Focused `pytest -q tests/test_chat.py` | **14 passed**, 1 warning (Starlette deprecation có sẵn) |
| Full `pytest -q` | **50 passed**, 1 warning — chạy 2 lần (trước probe và gate cuối sau khi xóa probe) |
| `node --check src/api/mock.js` | PASS |
| Build `VITE_USE_MOCK=true` / `false` | PASS / PASS (cả trước và sau xóa probe) |
| Backend khởi động (uvicorn cổng 8018, `DATABASE_URL` SQLite tạm trong scratchpad, `CHAT_API_KEY` rỗng) | `/api/health`: `status: ok`, `classifier: phobert_b`, `classifier_error: null`; `POST /api/chat` khách → **401** |
| Mock mode | `mockChat` qua Vite SSR: PASS (mục 2). **Trình duyệt:** không thực hiện được — Browser pane từ chối mở `localhost:5174` (xem mục 6) |
| `git diff --check 7e161b1..447c941` | PASS |
| Scope `git diff --stat master...HEAD` | 20 file, đều thuộc allowlist T17 / report / điều phối (như Round 1 + `mock.js`, report fix) |
| Bí mật | Không có `.env`, `*.db`, model, CSV trong diff (`backend/.env.example` là file mẫu, đã có ở Round 1). Regex key (`AIza…`, `sk-…`, `api_key=…`) trên diff fix: không có |
| `backend/firefly.db` | SHA-256 `b3f7df79…cfe3` trước/sau review — **không đổi**; không mở, không reset |
| `git status` sau gate cuối | sạch |

Pytest phải chạy với `--basetemp` trong scratchpad và `-p no:cacheprovider` vì thư mục `%TEMP%\pytest-of-lemin\pytest-current` bị khóa quyền (WinError 5) — lỗi môi trường, không liên quan code.

## 4. AC / DoD liên quan
| Mục | Kết quả Round 2 |
|---|---|
| AC mock chatbot (endpoint có ở cả `real.js` và `mock.js`, cùng cấu trúc `{reply, movies:[{id,title}]}`) | PASS — cấu trúc trả về không đổi |
| AC-09 (UI chat) | Không đổi mã giao diện; giữ kết quả Round 1 |
| AC-02 (Gemini key thật) | **Bằng chứng do PO thực hiện, Claude không kiểm chứng độc lập** (xem mục 5) |
| DoD: chỉ file allowlist, commit `[T17] …`, không file cấm | PASS |
| Hồi quy | Thay đổi giới hạn trong `mockChat` (không ghi `db`, không đụng ghế/đặt vé/thanh toán/đăng nhập). Checklist 7 mục `BOI_CANH_DU_AN.md` mục 7 không chạy lại trên trình duyệt ở vòng này; pytest 50/50 phủ phía backend |

## 5. AC-02 — bằng chứng PO (không phải Claude kiểm chứng)
Theo `codex_fix_T17_round1_2026-10-13.md` và điều phối, **PO tự thử** Gemini thật với model `gemini-3.5-flash-lite` (cấu hình trong `backend/.env` cục bộ, không vào Git):
- Tư vấn "phim tối nay": có trả lời.
- Thứ Bảy Không Ngủ ngày 14/10/2026: suất 09:30 và 13:15, Phòng 2, giá từ 75.000đ; khớp trang phim.
- Nút liên kết dẫn đúng trang phim.
- "Gợi ý phim hài đang chiếu" → Thứ Bảy Không Ngủ.
- `gemini-3.8-flash` (mặc định trong code/`.env.example`) trả HTTP 503 khi PO gọi trực tiếp.

Claude **không** gọi Gemini thật, không đọc API key; ghi nhận đây là bằng chứng **PO_ATTESTED**. Disposition AC-02 thuộc PO Review.

## 6. Giới hạn kiểm thử
- Không kiểm giao diện MOCK trên trình duyệt: Browser pane từ chối điều hướng tới `http://localhost:5174` và `http://127.0.0.1:5174` (dev server chạy được, `curl` trả 200). Thay bằng gọi `mockApi.chat.send` qua Vite SSR — cùng mã nguồn, nhưng không kiểm render. `ChatWidget.jsx` không đổi từ Round 1 (đã kiểm trên trình duyệt 375px ở Round 1); PO có screenshot 3/3 câu sau fix.
- Không gọi Gemini thật (theo yêu cầu, thay đổi chỉ thuộc MOCK).
- Không chạy lại checklist hồi quy 7 mục trên trình duyệt.

## 7. Required Fixes
Không có.

## 8. TODO
| ID | Trạng thái Round 2 | Ghi chú |
|---|---|---|
| TODO-01 | Giữ nguyên (CHỜ PO) | Không có commit sửa `chat_assistant.py`. PO quan sát Gemini trả đúng phim hài — bằng chứng PO, chưa đổi code so khớp thể loại |
| TODO-02 | Giữ nguyên (CHỜ PO) | PO quan sát có nút phim; code chưa đổi |
| **TODO-03** | **FIXED — Claude xác minh độc lập** | Mục 2, dòng 1–9 |
| TODO-04 | Giữ nguyên | |
| TODO-05 | Giữ nguyên (CHỜ PO) | PO ghi nhận `gemini-3.8-flash` → 503, `gemini-3.5-flash-lite` chạy được; `CHAT_MODEL` mặc định trong code/`.env.example` chưa đổi; hạn mức chưa có số liệu |
| TODO-06 | Giữ nguyên | |
| TODO-07 | Giữ nguyên | |
| TODO-08 | Giữ nguyên | `firefly.db` hash vẫn `b3f7…cfe3` |
| **TODO-09** (mới) | Low (mock) | Regex `wantsComedy` yêu cầu khoảng trắng hoặc hết chuỗi sau "hài", nên "Gợi ý phim hài?" / "phim hài," rơi về danh sách chung (không sai sang giá, chỉ không lọc hài). Ngược lại "phim hai người" (số hai) bị coi là phim hài. Đề xuất: `ACCEPT_LATER`; nếu sửa thì dùng `\b` hoặc bỏ dấu câu trước khi so. |
| **TODO-10** (mới, có từ `8ab2f00`) | Low (mock) | Cùng loại TODO-03: `question.includes("gia")` khớp "gia đình" (thể loại thật "Gia đình"), nên "Gợi ý phim gia đình" trả câu giá vé. Tương tự `"thuong"` khớp "thương". Không có trong 3 câu gợi ý của widget. Đề xuất: `ACCEPT_LATER`, hoặc `FIX_NOW` nếu PO định demo câu hỏi theo thể loại trên MOCK. |

## 9. T16
TODO-01..07 của T16 giữ nguyên disposition theo `reports/2026-10-12/claude_review_T16_PASS_WITH_TODO_2026-10-12.md`. Review này không mở/đóng TODO nào của T16.

## 10. Chuyển trạng thái
- T17: `CLAUDE_REVIEW (Round 2)` → **`PO_REVIEW`**.
- Không PO approve, không merge, không đóng T17.
- Task kế tiếp: **NOT SELECTED** — T12 vẫn `PLANNED / NOT AUTHORIZED` và còn mâu thuẫn trạng thái cần PO đồng bộ (AGENT_RULES 1.1), nên không soạn prompt handoff.

## 11. Việc PO cần làm ở PO_REVIEW
1. Ghi disposition TODO-01..10 trong `po_review_T17_*`; với TODO-05 quyết định có đổi `CHAT_MODEL` mặc định sang model đã chạy được hay chỉ ghi chú `.env`.
2. Ghi AC-02 là bằng chứng PO (model `gemini-3.5-flash-lite`, không ghi key).
3. Merge `task/T17-chatbot-tu-van` vào `master` sau PO_APPROVED; DB thật vẫn chờ xử lý T16 TODO-01 riêng.
