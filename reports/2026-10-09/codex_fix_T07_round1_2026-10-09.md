# Codex Fix Report — T07 Round 1 — 09/10/2026

## 1. Required Fix

- RF-01 (Medium), nguồn: `claude_review_T07_FAIL_2026-10-09.md`.
- Trạng thái Codex: **DEV FIXED**, chờ Claude Round 2 xác minh.
- Fix commit: `06fbd3d` — `[T07] Fix empty prediction text validation`.
- Không tự kết luận AC-05 hay toàn task PASS.

## 2. Root cause

`AdminPredictIn.text` dùng `Field(min_length=1, max_length=1000)`. Với payload `{"text": ""}`, ràng buộc `min_length` của Pydantic chạy trước `field_validator` mode after, nên request dừng bằng thông báo tiếng Anh `String should have at least 1 character`. Validator tiếng Việt chỉ nhận được chuỗi có chiều dài ít nhất 1, vì vậy các chuỗi chỉ gồm khoảng trắng vẫn đúng nhưng chuỗi rỗng sai contract.

## 3. Diff và cách sửa

- Production file duy nhất: `backend/app/schemas.py`.
- Diff: đổi `Field(min_length=1, max_length=1000)` thành `Field(max_length=1000)`.
- Giữ nguyên validator hiện có: strip input, nếu rỗng thì ném `PydanticCustomError("predict_text", "Nội dung cần chấm điểm không được để trống.")`.
- Giữ nguyên giới hạn tối đa 1.000 ký tự, response thành công, registry/model/checkpoint, 401/403 và database schema.
- Không thêm feature; không xử lý TODO-01 đến TODO-06.

## 4. Bảng kiểm thử bắt buộc

Tất cả probe endpoint chạy qua `FastAPI TestClient` với SQLite trong thư mục tạm; model thật PhoBERT/SVM/LR/NB được nạp.

| # | Input / trường hợp | Kỳ vọng | Thực tế |
|---:|---|---|---|
| 1 | `{"text":""}` + admin | 422, thông báo rỗng tiếng Việt | **Đạt** — 422, có `Nội dung cần chấm điểm không được để trống.`; không còn câu `String should have at least 1 character` |
| 2 | `{"text":"   "}` + admin | 422 cùng thông báo | **Đạt** |
| 3 | `{"text":"\n\t"}` + admin | 422 cùng thông báo | **Đạt** |
| 4 | Chuỗi hợp lệ | 200 | **Đạt** — 4 model |
| 5 | Đúng 1.000 ký tự | 200 | **Đạt** — 4 model |
| 6 | 1.001 ký tự | 422 | **Đạt** |
| 7 | Không token | 401 | **Đạt** |
| 8 | User thường | 403 | **Đạt** |
| 9 | Admin + chuỗi hợp lệ | 200, đúng contract | **Đạt** — mỗi item đúng `{model, version, label, score, ms}` |
| 10 | `GET /api/health` | 200 | **Đạt** — `status=ok`, `active_model=phobert` |

## 5. Focused regression

- Ba biến thể rỗng đều đi qua validator tiếng Việt.
- Chuỗi hợp lệ và biên 1.000 ký tự vẫn suy luận thành công với đủ bốn model.
- 1.001 ký tự vẫn bị `max_length=1000` chặn.
- Phân quyền không đổi: 401/403 đúng; admin 200.
- Success response không đổi: đủ năm key `model`, `version`, `label`, `score`, `ms`.
- Health/model loading không đổi: PhoBERT/SVM/LR/NB loaded; active PhoBERT.

## 6. Final gates

| Gate | Kết quả |
|---|---|
| Backend `compileall -q app` | PASS |
| Uvicorn startup trên SQLite tạm | PASS |
| `/api/health` qua uvicorn thật | HTTP 200, PASS |
| Frontend `npm run build` | PASS — Vite 70 modules, 811 ms |
| Focused regression 10 ca | PASS 10/10 |
| `git diff --check` | PASS |
| Scope | PASS — fix commit chỉ đổi `backend/app/schemas.py` |
| Secret scan | PASS |

Pytest không chạy vì dự án quy định bắt buộc từ T11; focused probe dùng TestClient có assert và database tạm.

## 7. Security và scope

- Không token vẫn 401; user thường vẫn 403; admin hợp lệ mới chạy inference.
- Giới hạn 1.000 ký tự vẫn còn nguyên.
- Không ghi database thật; startup gate dùng SQLite tạm và đã dọn sau kiểm thử.
- Không sửa registry, checkpoint, model artifact, `normalize()`, `_ABBR`, schema database, frontend hay documentation kiến trúc.
- Production diff đúng một dòng trong file được RF-01 cho phép.
- Không thêm dependency, dữ liệu, secret hoặc file lớn.

## 8. Required Fixes còn lại

- RF-01: **DEV FIXED / PENDING CLAUDE ROUND 2**.
- Open Required Fixes sau phía Codex: **0**, chờ reviewer xác minh và đóng RF.
- Blocker mới: 0.

## 9. Evidence cho Claude Round 2

1. Review commit `06fbd3d`; production diff phải chỉ có một dòng bỏ `min_length=1`.
2. Gửi ba payload `""`, `"   "`, `"\n\t"` bằng admin token; cả ba phải 422 và chứa đúng câu `Nội dung cần chấm điểm không được để trống.`.
3. Xác minh 1.000 ký tự → 200; 1.001 ký tự → 422.
4. Xác minh 401/403, admin 200 với contract năm trường, và health 200.
5. Chạy compileall, frontend build, diff/scope/secret gates.

T07 chuyển `FIX_LOOP` → `CLAUDE_REVIEW` Round 2. Codex không tự PASS, approve, merge, tag, close task hoặc mở T08.
