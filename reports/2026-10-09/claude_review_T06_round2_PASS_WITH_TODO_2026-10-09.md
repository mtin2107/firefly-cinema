# Claude Independent Review: T06, Round 2

Task: T06 (Kiểm duyệt có người duyệt)
Date: 2026-10-09
Reviewer: Claude (Independent Reviewer / Tester)
Branch: `task/T06-kiem-duyet` · HEAD lúc review: `8f6a464`
Fix commit: `8ef57ad4115d877aea14a19b706665a0b405a167`
Review trước: `reports/2026-10-09/claude_review_T06_FAIL_2026-10-09.md` (FAIL, RF-01 Medium)
Fix report: `reports/2026-10-09/codex_fix_T06_round1_2026-10-09.md`
**Result: PASS_WITH_TODO**

---

## 0. Pre-flight

| Kiểm tra | Kết quả |
|---|---|
| Branch | `task/T06-kiem-duyet` ✔ |
| Có commit `8ef57ad` (fix) và `8f6a464` (report/coordination) sau `7977ea5` (Claude FAIL) | ✔ |
| Working tree trước review | sạch ✔ |
| Coordination: T06 `CLAUDE_REVIEW (Round 2 PENDING)`, RF-01 DEV FIXED / PENDING CLAUDE VERIFICATION | ✔ |
| Diff `7977ea5..HEAD`: `backend/app/schemas.py` (+1/−1), `docs/TASK_COORDINATION_ACTIVE.md`, fix report | ✔ đúng phạm vi RF-01 |
| SHA-256 DB thật `backend/firefly.db` trước/sau review | `ed3abdba…70d0a`, **không đổi** (cũng trùng giá trị đo ở Round 1) ✔ |
| SHA-256 backup `backup/T06/firefly_pre_T06_20261008_234417.db` | `c27abfca…e23bc`, **không đổi** ✔ |

## 1. Source Review: PASS

Diff của fix (`backend/app/schemas.py:305`):

```diff
-        if value not in {"confirm", "relabel", "hide", "unhide"}:
+        if not isinstance(value, str) or value not in {"confirm", "relabel", "hide", "unhide"}:
```

- Toán tử `or` ngắt sớm: với input không phải `str`, phép membership trên set không chạy, nên không còn `TypeError`. Mọi input sai đều đi vào `PydanticCustomError("comment_action", ...)` kèm câu tiếng Việt cũ.
- `bool` không phải lớp con của `str`, nên `true` bị chặn đúng. Chuỗi lạ (`"delete"`, `""`, `"CONFIRM"`, `" confirm"`) vẫn bị chặn vì không nằm trong tập giá trị.
- Không đổi kiểu `Literal`, validator `label`, `extra="forbid"`, router, model, schema DB, frontend hay mock. Contract giữ nguyên.

## 2. RF-01: CLOSED / VERIFIED BY CLAUDE

Probe TestClient trên DB tạm mới, dùng token admin, gọi `PATCH /api/admin/comments/{id}`:

| `action` | Status | Detail | Dữ liệu |
|---|---|---|---|
| `["x"]` | 422 | "…Thao tác phải là confirm, relabel, hide hoặc unhide." | không đổi |
| `{"a":1}` | 422 | như trên | không đổi |
| `123` | 422 | như trên | không đổi |
| `true` | 422 | như trên | không đổi |
| `null` | 422 | như trên | không đổi |
| `"delete"` | 422 | như trên | không đổi |
| *(thêm)* `1.5`, `""`, `"CONFIRM"`, `" confirm"` | 422 | như trên | không đổi |

- Kết quả: 10/10 trả 422 đúng câu, không có 500. Snapshot toàn bộ bảng `comments` (mọi cột) trước và sau các request sai giống hệt nhau.
- Đã kiểm thêm trên **uvicorn thật** (backend review cổng 8001, DB copy): `{"action": ["x"]}` trả `422 {"detail": "Trường 'action' không hợp lệ: Thao tác phải là confirm, relabel, hide hoặc unhide."}`.
- 4 action hợp lệ `confirm`, `relabel`, `hide`, `unhide` đều trả 200. Response `AdminCommentOut` vẫn đủ 16 key như Round 1; public `CommentOut` vẫn 9 key, không lộ trường admin.

## 3. Acceptance Criteria: 8/8 PASS

Chạy lại toàn bộ trên DB tạm (TestClient, 52/52 check) cùng UI real/mock.

| AC | Kết quả | Bằng chứng Round 2 |
|---|---|---|
| AC-01 | PASS | Sau confirm ×2, relabel ×2, hide, unhide và 10 request sai: bộ `(is_negative, negative_score, model_name)` không đổi. `reviewed_by`/`reviewed_at` được ghi. |
| AC-02 | PASS | Relabel model tiêu cực → 0: public trả `effective_negative=false`, `reviewed=true`. Hide: biến mất khỏi public. Unhide: quay lại, `human_label` giữ nguyên. |
| AC-03 | PASS | Stats = `{reviewed 4, agree 2, disagree 2, accuracy 0.5, tp 1, fp 1, tn 1, fn 1}`. UI real: confirm làm stats đổi 4→5, 50%→60%, TP 1→2. |
| AC-04 | PASS | Có BOM `EF BB BF`; header `text,text_norm,label`; 4 dòng đã duyệt; `text_norm == normalize(text)`; `label == human_label`. |
| AC-05 | PASS | 4 endpoint mới: anonymous 401 ×4, user thường 403 ×4. PATCH của user không có tác dụng. Mock: 401/403. |
| AC-06 | PASS | `page_size=500` trả 422 "…từ 1 đến 100."; `page=0`, `page_size=0`, `page=abc`, `reviewed=maybe`, `label=xyz` đều 422. Lọc `reviewed=true/false` đúng tổng. |
| AC-07 | PASS | Mock (5175): confirm/relabel/hide/unhide, stats 1/1/1/1, CSV có BOM + 5 dòng, 6 action sai + `page_size=500` đều 422, user 403, anonymous 401. |
| AC-08 | PASS | `HUONG_DAN.md` mục 2.1 không đổi so với Round 1 (đã đạt). Hồi quy 7/7. |

## 4. Definition of Done: MET (phần thuộc Claude)

| Mục (`_TEMPLATE.md` mục 9) | Trạng thái |
|---|---|
| Toàn bộ AC đạt, có bằng chứng | MET (8/8) |
| Gate `AGENT_RULES.md` mục 3 | MET |
| Không có file ngoài allowlist | MET |
| Tài liệu cập nhật | MET |
| Claude PASS / PASS_WITH_TODO | MET (Round 2) |
| Tín APPROVED | Chờ PO_REVIEW |

## 5. Architecture: PASS
Fix chỉ có 1 dòng, nằm đúng lớp schema, không thêm thư viện, không đụng `classifier.py`, `seats.py`, `normalize()`.

## 6. Security: PASS
`require_admin` giữ nguyên, 401/403 xác minh lại. Endpoint không còn trả 500 với payload crafted. TODO-03 (CSV formula injection) vẫn mở, mức Low.

## 7. Database / schema safety: PASS
- Fix không đổi schema, không cần reset DB.
- Review không ghi DB thật hay backup; checksum hai file không đổi.
- Các thao tác ghi chỉ chạy trên DB tạm và bản copy trong scratchpad, cả hai đã bị xóa.
- Backend/frontend của PO (cổng 8000/5173) không bị đụng tới.
- CHECK `human_label` vẫn chặn giá trị 2.

## 8. Regression: PASS (7/7)

| # | Mục | Kết quả |
|---|---|---|
| 1 | Trang chủ hiện phim | PASS |
| 2 | Tìm "meo muop" | PASS, ra 1 phim "Mèo Mướp Đi Lạc" |
| 3 | Đăng ký; chưa đăng nhập vào `/dat-ve/1` bị chuyển sang `/dang-nhap`, kèm `from=/dat-ve/1` | PASS (register 201) |
| 4 | Đặt 2 ghế; ghế thành đã đặt; Vé của tôi | PASS (201, ghế H1/H2 có trong booked, `/bookings/me` 200) |
| 5 | "Ko hay như quảng cáo, hơi thất vọng" bị ẩn, điểm ≈0,99 | PASS (score 0.994, `effective_negative=true`) |
| 6 | `/api/health` báo phobert | PASS (cả 8000 và 8001) |
| 7 | Mock mode | PASS (AC-07) |

Responsive 375px: `scrollWidth` = 375, không cuộn ngang. 0 lỗi console ở cả real lẫn mock.

## 9. Scope Integrity: PASS
`git diff --name-only master...HEAD`: 11 file production/tài liệu trong allowlist T06, cộng 3 report (`codex_implementation_T06`, `claude_review_T06_FAIL`, `codex_fix_T06_round1`). Round 1 chỉ thêm thay đổi ở `schemas.py`. Không có file `.env`, `*.db`, model, CSV, `backup/`, `data/`, `ml/artifacts/`. Không có đường dẫn `D:\`.

## 10. Independent Tests

| Gate | Kết quả |
|---|---|
| Focused RF-01 (DB tạm) | 10/10 trả 422, dữ liệu không đổi |
| Full API probe (DB tạm) | 52/52 |
| `compileall -q backend\app` | PASS (chạy lại trên clean tree sau khi dọn probe) |
| `npm run build` | PASS (chạy lại trên clean tree) |
| Health | `{"status":"ok","classifier":"phobert","classifier_error":null}` |
| Real/mock contract | PASS (16/16 key admin, 9/9 key public, mock 422/401/403) |
| `git diff --check master...HEAD` | PASS |
| Allowlist / forbidden / secret scan | PASS |
| pytest | N/A (bắt buộc từ T11) |

Temporary probes: tạo 2 script (`probe_r2.py`, `regress_api.py`), 1 DB tạm, 1 DB copy và 3 server review (8001/5174/5175), tất cả nằm trong scratchpad, ngoài repo. **Còn lại: 0.**

## 11. Required Fixes: 0
RF-01 (Medium): **CLOSED / VERIFIED BY CLAUDE**. Open Required Fixes: **0**.

## 12. TODOs (giữ nguyên 6 TODO từ Round 1, chờ PO disposition)

| ID | Mức | Nội dung | Đề xuất |
|---|---|---|---|
| TODO-01 | Low | Một số lỗi 422 của handler chung vẫn kèm câu Pydantic tiếng Anh (`Field required`, `Extra inputs…`, `page=abc`, `label: true`, JSON decode). Handler này có từ trước T06. | ACCEPT_LATER → T11 |
| TODO-02 | Low | Mock `admin.comments.list` bỏ qua `label`/`reviewed` không hợp lệ, trong khi real trả 422. | ACCEPT hoặc → T11 |
| TODO-03 | Low | CSV formula injection: nội dung bắt đầu bằng `=`, `+`, `-`, `@` được ghi nguyên văn. Nếu sửa phải giữ đúng `text` để dùng train. | ACCEPT_WITH_NOTES hoặc → T11 |
| TODO-04 | Low | `CommentSection.jsx:19` vẫn ghi "ẩn vì mô hình đánh giá" kể cả khi admin relabel. | ACCEPT hoặc T11/T12 |
| TODO-05 | Info | DB thật đang chứa dữ liệu thử từ final verification của Codex (1 booking/2 ghế, 1 bình luận thử, 4 nhãn duyệt). | PO quyết (gợi ý T12) |
| TODO-06 | Info | `T06.md` vẫn ghi `Current Status: PLANNED`. API chưa có thao tác "bỏ duyệt"; hide/unhide không ghi người thao tác (spec không yêu cầu). | PO quyết / ACCEPT |

Không phát sinh TODO mới ở Round 2.

## 13. Final Decision
**PASS_WITH_TODO**: RF-01 đã được sửa và xác minh độc lập; AC 8/8, hồi quy 7/7, toàn bộ gate đạt. 6 TODO không chặn, chờ PO disposition.

## 14. Coordination Transition
- T06: `CLAUDE_REVIEW` → **`PO_REVIEW`**.
- RF-01: CLOSED / VERIFIED BY CLAUDE; Open Required Fixes: 0.
- **Không mở task kế tiếp:** PO đã chỉ định T07 giữ **PLANNED / NOT AUTHORIZED**. Chỉ thị này của PO được ưu tiên hơn bước tự động đặt task kế tiếp sang READY_FOR_HANDOFF trong AGENT_RULES mục 1.1, nên report này không có mục "Bàn giao task kế tiếp".
- Không PO APPROVED, không merge, không tag, không đóng T06.
- Việc của Tín: PO review T06 (chạy thử, disposition TODO-01→06), sau đó merge `task/T06-kiem-duyet` vào `master` nếu APPROVED, rồi quyết định có authorize T07 hay không.
