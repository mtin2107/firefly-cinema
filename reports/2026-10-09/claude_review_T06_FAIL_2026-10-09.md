# Claude Independent Review — T06

Task: T06 — Kiểm duyệt có người duyệt
Date: 2026-10-09
Reviewer: Claude (Independent Reviewer / Tester)
Branch: `task/T06-kiem-duyet` · HEAD review: `e659244`
Implementation commit: `942d7197ed5c104e6267446866822c2a2b165401`
Report Codex: `reports/2026-10-08/codex_implementation_T06_2026-10-08.md` (bản cuối, commit `ca109c7`, `e659244`)
**Result: FAIL** (1 Required Fix, Severity Medium)

---

## 0. Pre-flight

| Kiểm tra | Kết quả |
|---|---|
| Branch hiện tại | `task/T06-kiem-duyet` ✔ |
| Commit implementation `942d719` + report `ca109c7`, `e659244` có trong lịch sử branch | ✔ |
| Working tree trước review | sạch ✔ |
| File điều phối: T06 `CLAUDE_REVIEW` | ✔ |
| DB thật `backend/firefly.db` SHA-256 trước/sau review | `ed3abdba…70d0a` — **không đổi** ✔ |
| Backup `backup/T06/firefly_pre_T06_20261008_234417.db` SHA-256 trước/sau review | `c27abfca…e23bc` — **không đổi**, khớp report Codex ✔ |
| Backend/frontend của PO (cổng 8000/5173) | không bị tắt, không bị ghi dữ liệu bởi review ✔ |

Mọi kiểm thử có ghi dữ liệu chạy trên DB tạm (TestClient, DB mới) hoặc **bản copy** DB thật trong scratchpad (backend review cổng 8001, frontend review 5174 real / 5175 mock). Không tạo blocker pre-flight.

## 1. Source Review — PASS (có 1 lỗi xử lý input, xem RF-01)

Đã đọc toàn bộ `git diff master...HEAD` (12 file):

- `models.py`: thêm `human_label` (Integer, null, CHECK 0/1/NULL), `reviewed_by` (FK `users.id`, null), `reviewed_at` (DateTime, null), `hidden` (Boolean, default False, server_default `0`, NOT NULL). Hai relationship `user`/`reviewer` khai báo `foreign_keys` rõ ràng — cần thiết vì `comments` giờ có 2 FK tới `users`.
- `routers/comments.py`:
  - `to_out()` tính `reviewed = human_label in (0,1)`, `effective_negative = bool(human_label) if reviewed else is_negative` — đúng thiết kế mục 4.
  - Public `GET /api/movies/{id}/comments` lọc `hidden IS FALSE`; `response_model=CommentOut` nên không lộ `human_label`, `hidden`, `reviewed_by*`.
  - `PATCH` chỉ gán `human_label`/`reviewed_by`/`reviewed_at` (confirm/relabel) hoặc `hidden` (hide/unhide). **Không có dòng nào gán `is_negative`, `negative_score`, `model_name`.**
  - List: `page`/`page_size` validate thủ công → 422 tiếng Việt; lọc `label` (theo nhãn model), `reviewed`; `total` đếm cùng bộ lọc; sắp xếp `created_at desc, id desc` (ổn định).
  - Stats: TP = model 1 & người 1, FP = model 1 & người 0, TN = 0/0, FN = model 0 & người 1 — đúng quy ước nhãn 1 = tiêu cực. `accuracy = agree/reviewed`, 0.0 khi chưa duyệt.
  - CSV: `csv.writer` + `utf-8-sig`, chỉ dòng `human_label IN (0,1)`, `text_norm = normalize(content)`.
  - Route tĩnh `/admin/comments/stats`, `/export.csv` là GET, PATCH dùng `{comment_id}` → không xung đột route.
- `schemas.py`: `CommentOut` thêm `effective_negative`, `reviewed`; `AdminCommentOut` thêm 5 trường duyệt; `AdminCommentAction` `extra="forbid"`, `Literal` + validator `mode="before"` có câu tiếng Việt. **Validator `validate_action` dùng `value not in {set}` → crash khi `action` là list/dict (RF-01).**
- Frontend: `real.js`/`mock.js` cùng namespace `api.admin.comments.{list,update,stats,exportCsv}`; `AdminComments.jsx` chỉ import từ `../api`; `CommentSection.jsx` dùng `effective_negative`.

## 2. Acceptance Criteria — 8/8 PASS

| AC | Kết quả | Bằng chứng độc lập |
|---|---|---|
| AC-01 | PASS | DB tạm: 4 bình luận mới (2 model tiêu cực 0.87, 2 bình thường 0.08). Sau confirm ×2, relabel ×2, hide, unhide: bộ `(is_negative, negative_score, model_name)` đọc trực tiếp bằng sqlite3 **trùng khớp trước/sau**. `reviewed_by=1`, `reviewed_at` được ghi. |
| AC-02 | PASS | Relabel bình luận model tiêu cực → 0: public trả `is_negative=true`, `effective_negative=false`, `reviewed=true`. Hide → biến khỏi public, vẫn có trong admin (`hidden=true`). Unhide → quay lại, `effective_negative=false` giữ nguyên, `human_label` không bị xóa. UI trang phim: bình luận `effective_negative` hiển thị khung ẩn đúng. |
| AC-03 | PASS | Bộ kiểm 4 dòng TP/FP/TN/FN: API trả `reviewed=4, agree=2, disagree=2, accuracy=0.5, tp=fp=tn=fn=1`; khớp `count(human_label not null)` trong DB. Trên DB copy, confirm qua UI cập nhật stats 4→5, 50%→60%, TP 1→2 tức thì. |
| AC-04 | PASS | 3 byte đầu `EF BB BF`; header đúng `text,text_norm,label`; 4 dòng = 4 dòng đã duyệt; `label` = `human_label`; `text_norm == normalize(text)` cho 100% dòng (kể cả nội dung có `"` và dấu phẩy, được quote đúng). `Content-Type: text/csv; charset=utf-8`, `Content-Disposition: attachment`. |
| AC-05 | PASS | 4 endpoint mới (list, PATCH, stats, export.csv): anonymous **401** ×4, user thường **403** ×4 kèm "Chỉ quản trị viên…"; PATCH của user không đổi `hidden` trong DB. Mock: anonymous 401, user 403. |
| AC-06 | PASS | `page_size=500` → 422 "Số bình luận mỗi trang phải từ 1 đến 100."; `page=0/-1`, `page_size=0` → 422 tiếng Việt; `page=abc`, `page_size=1.5`, `reviewed=maybe`, `label=xyz` → 422. Mặc định 20 dòng, `{items,total}`, trang rời nhau, trang vượt → `items=[]`, `total` đúng. |
| AC-07 | PASS | Mock (VITE_USE_MOCK=true, cổng 5175): confirm/relabel/hide/unhide, stats 1/1/1/1 + accuracy 0.5, CSV BOM + 5 dòng (header + 4), 422 cho page_size 500/page 0/relabel thiếu label/action lạ. Key set `AdminCommentOut` mock **trùng 16/16** với backend; public key set trùng 9/9. `normalizeComment()` mock vs `normalize()` backend: **20/20** câu mẫu giống hệt. |
| AC-08 | PASS | `HUONG_DAN.md` mục 2.1: dừng backend, kiểm tra cổng 8000, xác minh backup (SHA-256 + integrity), chỉ PO `Remove-Item -LiteralPath` đúng file, khởi động lại để `create_all` + seed, lệnh kiểm schema. Bảng API cập nhật 4 dòng. Hồi quy 7/7 (mục 7). |

AC-06 đạt theo đúng câu chữ ("page_size=500 → 422 có thông báo"). RF-01 nằm ở phần xử lý input của `action`, thuộc yêu cầu review "giá trị action không hợp lệ được xử lý an toàn" và quy ước dự án "lỗi trả HTTPException kèm một câu tiếng Việt" — không phải AC riêng, nên ghi ở DoD/Error handling.

## 3. Definition of Done — NOT_MET

| Mục (`_TEMPLATE.md` mục 9) | Trạng thái |
|---|---|
| Toàn bộ AC đạt, có bằng chứng | MET (8/8) |
| Gate `AGENT_RULES.md` mục 3 đạt | MET (compile, health phobert, build, mock, hồi quy, scope, bí mật) |
| Không có file ngoài allowlist | MET |
| Tài liệu cập nhật (`ARCHITECTURE.md`, `HUONG_DAN.md`) | MET |
| Claude PASS/PASS_WITH_TODO, Tín APPROVED | **NOT_MET** — RF-01 mở |

## 4. Architecture — PASS

- Code nằm đúng chỗ (router/schemas/models hiện có, không tạo cấu trúc mới).
- Giữ nguyên kết quả model, tách nhãn người duyệt — đúng `ARCHITECTURE.md` mục 2.8 mới.
- Real/mock cùng contract; giao diện chỉ import `src/api/index.js`.
- Không thêm thư viện (`csv`, `io` là stdlib). Không đụng `classifier.py`, `seats.py`, không đổi `normalize()`.

## 5. Security — PASS (kèm RF-01 về robustness)

- `require_admin` trên cả 4 endpoint mới; 401/403 xác minh độc lập.
- Public API không lộ `human_label`, `hidden`, `reviewed_by`, `reviewed_by_name`.
- Truy vấn dùng SQLAlchemy expression, không nối chuỗi SQL.
- `real.js` `download()` gửi Bearer token, không đưa token vào URL.
- Rủi ro thấp: CSV formula injection (TODO-03).
- RF-01: request crafted làm 500 (không lộ traceback ra client, không đổi dữ liệu) — lỗi robustness, admin-only.

## 6. Database / schema safety — PASS

- Schema DB thật (đọc read-only): đủ 12 cột; `CONSTRAINT ck_comments_human_label CHECK (human_label IN (0, 1) OR human_label IS NULL)`; `FOREIGN KEY(reviewed_by) REFERENCES users (id)`; `hidden BOOLEAN DEFAULT '0' NOT NULL`; `PRAGMA integrity_check = ok`.
- DB tạm: ghi `human_label=2` bị CHECK chặn (`IntegrityError`); INSERT không có `hidden` → mặc định `0`.
- DB thật và backup giữ nguyên SHA-256 trong suốt review. Review không xóa, reset, ghi đè DB thật hay backup.
- Ghi chú: report Codex mục 6 xác nhận final verification đã chạy regression **trên DB thật mới** (thêm 1 booking/2 ghế, 1 bình luận "kiểm thử final T06", 4 nhãn duyệt). Hiện DB thật có 13 bình luận, 4 đã duyệt. Có công bố trong report, không vi phạm Q2, nhưng PO nên biết trước demo (TODO-05).

## 7. Regression — PASS (7/7)

Chạy trên backend review (DB copy, PhoBERT) + frontend review real 5174; mục 7 trên mock 5175.

| # | Mục | Kết quả |
|---|---|---|
| 1 | Trang chủ hiện phim | PASS — hero + danh sách phim render, 0 lỗi console |
| 2 | Tìm "meo muop" | PASS — 1 phim "Mèo Mướp Đi Lạc" |
| 3 | Đăng ký; chưa đăng nhập vào `/dat-ve/1` → `/dang-nhap` có `state.from=/dat-ve/1` | PASS (register 201) |
| 4 | Đặt 2 ghế; ghế xám; Vé của tôi | PASS — POST 201, 2 ghế nằm trong danh sách đã đặt, `/api/bookings/me` 200 có vé |
| 5 | "Ko hay như quảng cáo, hơi thất vọng" bị ẩn, điểm ≈0,99 | PASS — `is_negative=true`, score 0.994, `effective_negative=true` |
| 6 | `/api/health` → phobert | PASS — cả backend PO (8000) và backend review (8001) |
| 7 | Mock mode | PASS — xem AC-07 |

Responsive 375×812: `scrollWidth` trang = 375 (không cuộn ngang), bảng 1120px chỉ cuộn trong `.table-wrap`, stats 2 cột + ô TP/FP/TN/FN full width, nút "Tải CSV" full width. 0 lỗi console ở real và mock.

## 8. Scope Integrity — PASS

`git diff --stat master...HEAD`: `HUONG_DAN.md`, `backend/app/{models,schemas}.py`, `backend/app/routers/comments.py`, `docs/ARCHITECTURE.md`, `docs/TASK_COORDINATION_ACTIVE.md`, `frontend/src/api/{mock,real}.js`, `frontend/src/components/CommentSection.jsx`, `frontend/src/pages/AdminComments.jsx`, `frontend/src/styles/global.css`, `reports/2026-10-08/codex_implementation_T06_2026-10-08.md` — tất cả trong allowlist mục 6. Không đụng `classifier.py`, `seats.py`. Không có đường dẫn `D:\`.

## 9. Independent Tests

| Gate | Kết quả |
|---|---|
| `python -m compileall -q backend\app` | PASS (chạy lại trên clean tree sau khi dọn probe) |
| Backend khởi động + `/api/health` | PASS — `{"status":"ok","classifier":"phobert","classifier_error":null}` |
| `npm run build` | PASS (69 modules, chạy lại trên clean tree) |
| pytest | N/A (bắt buộc từ T11) |
| API probe TestClient trên DB tạm | 58/60 — 2 ca lỗi đều là RF-01 |
| Real/mock contract | PASS (key set 16/16, 9/9; normalize parity 20/20) |
| Security 401/403 | 8/8 real + 3/3 mock |
| Moderation/stats/CSV | PASS |
| Regression 7 mục | 7/7 |
| `git diff --check master...HEAD` | PASS |
| Allowlist / forbidden file | PASS |
| Secret/DB/model scan (`.env`, `*.db`, joblib, safetensors, CSV, `backend/models`, `ml/artifacts`, `data/`, `backup/`) | PASS — không có trong diff; `backend/firefly.db`, `backup/` bị `.gitignore` |

Bảng PATCH input lạ (real, DB tạm):

| Body | Status | Đánh giá |
|---|---|---|
| `{"action":"relabel"}` / `label:null` | 422 "Đổi nhãn cần label là 0 hoặc 1." | OK |
| `label: 2` / `"1"` / `[]` | 422 "…Nhãn người duyệt phải là 0 hoặc 1." | OK |
| `label: true` / `1.0` | 422 "…Input should be 0 or 1" | OK (câu Pydantic tiếng Anh, TODO-01) |
| `action: "delete"` / `null` | 422 "…Thao tác phải là confirm, relabel, hide hoặc unhide." | OK |
| `{}` / thêm trường lạ / body không phải JSON | 422 (câu Pydantic tiếng Anh) | OK (TODO-01) |
| **`action: ["x"]`** | **500 Internal Server Error** | **RF-01** |
| **`action: {"a":1}`** | **500 Internal Server Error** | **RF-01** |

Temporary probes: Created 4 (`probe_t06.py`, `norm_parity.py/.mjs`, `regress_api.py`, đều ở scratchpad, ngoài repo) + DB tạm/DB copy + 3 server review. **Remaining: 0** — đã xóa thư mục probe, dừng server 8001/5174/5175; server của PO giữ nguyên; `git status` sạch trước khi viết report.

## 10. Required Fixes — 1

### RF-01
- **Severity:** Medium
- **File:** `backend/app/schemas.py:302-307` (`AdminCommentAction.validate_action`)
- **Problem:** Validator `mode="before"` kiểm tra `value not in {"confirm", "relabel", "hide", "unhide"}`. Khi `action` là kiểu không hash được (list, dict), phép kiểm tra thành viên của `set` ném `TypeError: unhashable type`. Pydantic v2 không chuyển `TypeError` thành lỗi validation nên exception lọt ra ngoài → FastAPI trả **500** thay vì 422 tiếng Việt. Vi phạm quy ước dự án "Lỗi trả HTTPException kèm một câu tiếng Việt" và yêu cầu review "giá trị action không hợp lệ được xử lý an toàn". Phản hồi 500 không qua CORS middleware nên giao diện chỉ nhận lỗi mạng chung chung.
- **Evidence:** TestClient trên DB tạm, admin token: `PATCH /api/admin/comments/14` body `{"action": ["x"]}` → `500 Internal Server Error`; body `{"action": {"a": 1}}` → `500`. Cùng endpoint với `{"action": "delete"}` hay `null` → 422 đúng. Dữ liệu không bị đổi (`human_label` giữ nguyên). Report Codex không probe ca này.
- **Expected Fix:** Validator phải trả lỗi validation cho mọi kiểu input, ví dụ kiểm tra `isinstance(value, str)` trước khi so tập hợp, hoặc so với tuple thay cho set, rồi vẫn raise `PydanticCustomError` với câu tiếng Việt hiện có. Probe lại: `action` = list, dict, số, bool, null, chuỗi lạ đều phải ra **422** với câu "Thao tác phải là confirm, relabel, hide hoặc unhide."; 4 action hợp lệ vẫn chạy như cũ. Chỉ sửa `schemas.py`, không đổi contract, không cần đổi mock (mock đã trả 422 "Thao tác kiểm duyệt không hợp lệ." cho action lạ). Không đổi schema DB, không cần reset DB.

## 11. TODOs (không chặn, chờ PO disposition)

| ID | Mức | Nội dung | Đề xuất |
|---|---|---|---|
| TODO-01 | Low | Lỗi 422 do handler chung vẫn ghép câu Pydantic tiếng Anh sau tiền tố tiếng Việt: `page=abc`, `reviewed=maybe`, body thiếu `action`, trường lạ, `label: true/1.0`, body không phải JSON ("Trường '0' không hợp lệ: JSON decode error"). Cùng loại với T04 TODO-03, handler có sẵn từ trước T06. | ACCEPT_LATER → T11 |
| TODO-02 | Low | Mock `admin.comments.list` bỏ qua `label`/`reviewed` không hợp lệ (trả toàn bộ danh sách) trong khi real trả 422. UI không gửi giá trị lạ nên không ảnh hưởng người dùng. | ACCEPT hoặc → T11 |
| TODO-03 | Low | CSV formula injection: nội dung bình luận bắt đầu bằng `=`, `+`, `-`, `@` được ghi nguyên văn (ví dụ `=1+1`), Excel có thể hiểu là công thức khi admin mở file. Admin-only, dữ liệu nội bộ. Nếu sửa phải cân nhắc vì CSV dùng để train (T03/T09), thêm ký tự đầu dòng sẽ làm sai `text`. | ACCEPT_WITH_NOTES hoặc → T11 |
| TODO-04 | Low | `CommentSection.jsx:19` vẫn ghi "ẩn vì **mô hình** đánh giá có nội dung tiêu cực" kể cả khi bình luận bị ẩn do admin relabel 0→1. Thông báo sau khi đăng bình luận cũng nói "Hệ thống đánh giá". Chỉ là câu chữ. | ACCEPT hoặc sửa nhẹ ở T11/T12 |
| TODO-05 | Info | Final verification của Codex ghi dữ liệu thử lên DB thật mới: 1 booking/2 ghế, 1 bình luận "…kiểm thử final T06", 4 nhãn duyệt (stats DB thật hiện là 4 reviewed, 50%). Có công bố trong report, không vi phạm Q2. PO quyết định có giữ trước demo hay không. | PO quyết (gợi ý: xử lý ở T12 dữ liệu demo) |
| TODO-06 | Info | `docs/tasks/T06.md` bảng đầu vẫn ghi `Current Status: PLANNED` trong khi file điều phối là CLAUDE_REVIEW. Chỉ PO được sửa Txx.md. Ngoài ra API không có thao tác "bỏ duyệt" (đưa `human_label` về NULL) và hide/unhide không ghi người thao tác; spec không yêu cầu. | PO quyết / ACCEPT |

## 12. Final Decision

**FAIL** — AC 8/8 PASS, hồi quy 7/7, scope/bảo mật/DB đạt, nhưng còn **RF-01 (Medium)**: input `action` sai kiểu làm endpoint admin mới trả 500. Lỗi nhỏ, sửa trong 1 file, không đổi contract, không đụng DB.

## 13. Coordination Transition

- T06: `CLAUDE_REVIEW` → **`FIX_LOOP`** (Open Required Fixes: RF-01).
- Không mở task kế tiếp (FAIL; đồng thời PO đã ghi T07 **PLANNED / NOT AUTHORIZED**).
- Không merge, không tag, không đóng T06, không PO APPROVED.
- Bước tiếp theo: Codex sửa đúng RF-01 trên `task/T06-kiem-duyet`, tạo `reports/YYYY-MM-DD/codex_fix_T06_round1_YYYY-MM-DD.md`, chuyển `FIX_LOOP` → `CLAUDE_REVIEW`; Claude review round 2 (`claude_review_T06_round2_<RESULT>_YYYY-MM-DD.md`).
