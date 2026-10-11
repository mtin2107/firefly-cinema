# T11 — Fix Loop Round 3

- Ngày: 11/10/2026
- Branch: `task/T11-kiem-thu`
- Claude Round 2: `FAIL`, review HEAD `70e2c93544ab73dec9ae4cfe91777546a899e6af`
- Coordination vào vòng sửa: commit `35bf82bdf29d1958c0867ff6b87063a6f037b4e5`, trạng thái `FIX_LOOP`
- Fix implementation commit: `062b9a8eedbc2b3268bf4e66e17992a308629d3f`
- Trạng thái bàn giao: `FIX_LOOP → CLAUDE_REVIEW` (chờ Claude xác minh độc lập)

## 1. RF-03 — nguyên nhân gốc và bằng chứng trước sửa

Sidecar `<db>.showtime-seed.json` chỉ gắn với đường dẫn file SQLite. Khi reset bằng cách thay file DB nhưng giữ sidecar tại cùng đường dẫn, `seed()` không phân biệt được DB mới với DB cũ. State cũ đánh dấu toàn bộ movie/ngày đã xử lý nên DB thay thế tạo `0/99` suất; `_seed_bookings()` vì thế cũng không có suất để tạo vé.

Regression test được thêm trước khi sửa và chạy riêng trên code lỗi:

```text
FAILED test_reset_database_ignores_stale_sidecar_and_reseeds_all_data
assert 0 == 99
1 failed, 1 warning
```

Test tạo/seed DB thứ nhất, giữ nguyên sidecar, đóng engine, xóa duy nhất DB tạm dưới `tmp_path`, tạo DB mới đúng đường dẫn rồi gọi vòng đời `seed()`.

## 2. Cách sửa và an toàn dữ liệu

- `seed()` kiểm tra số dòng `movies` ngay khi bắt đầu. Chỉ khi bảng này rỗng, DB được xem là khởi tạo mới.
- State rỗng được ghi bằng cơ chế file tạm + `flush` + `fsync` + `os.replace` nguyên tử **trước mọi commit dữ liệu seed**. Sidecar cũ hoặc hỏng vì vậy không chặn DB mới.
- Nếu tiến trình dừng giữa chừng, state rỗng đã publish: lần khởi động sau có thể chạy lại với duplicate/conflict guard và hoàn tất seed.
- Database hiện hữu không đi qua nhánh reset state, nên dấu ngày/movie đã xử lý tiếp tục ngăn tái tạo suất admin đã xóa.
- Sidecar hỏng trên DB hiện hữu vẫn hard-fail bằng `RuntimeError`; test xác nhận movie/showtime và chính file hỏng không bị sửa.
- Không đổi schema, model artifact hoặc `normalize()`; không kết nối/startup/seed database thật.

Sau sửa, test reset xác nhận DB mới có đúng số suất, booking và booking seat như lần seed đầu; cả ba số đều lớn hơn 0.

## 3. Regression và ảnh hưởng RF-01/RF-02

`backend/tests/test_seed.py` hiện có 9 test:

1. Reset DB khi sidecar cũ còn tồn tại vẫn seed đủ lịch/vé/ghế.
2. Xóa một suất seed không bị tái tạo.
3. Xóa sạch một ngày không bị tái tạo sau Session mới.
4. DB hiện hữu thiếu sidecar được khởi tạo bảo thủ, giữ ngày đã xóa.
5. Sidecar hỏng trên DB hiện hữu dừng an toàn, không mutation.
6. Rolling 5 ngày bổ sung ngày mới cho đủ phim.
7. Ngày rolling có suất admin vẫn seed phim còn thiếu và không overlap.
8. Phim mới chuyển `now_showing` vẫn nhận lịch trên các ngày đã seed.
9. Suất admin, booking và booking seat không thay đổi.

RF-01/RF-02 không được mở lại hoặc sửa logic phân bổ. Focused suite `9 passed`; rolling 5 ngày, fairness, cleanup conflict và dữ liệu admin đều giữ nguyên.

## 4. Sidecar, backup/restore và giới hạn đã biết

`HUONG_DAN.md` nay yêu cầu:

- dừng backend trước backup/reset/restore;
- backup và restore DB + sidecar như một cặp cùng snapshot;
- sidecar hỏng trên DB hiện hữu phải hard stop, không tự xóa state hay dữ liệu sản phẩm;
- reset thật chỉ thực hiện sau PO authorization.

Không đổi schema đồng nghĩa sidecar chưa có định danh bền vững được lưu bên trong DB. Vì vậy code không thể phát hiện tin cậy mọi trường hợp restore một DB cũ với sidecar thuộc snapshot khác. Giới hạn này được báo rõ, không giả định âm thầm: nếu không chứng minh được cặp snapshot thì HARD STOP và khôi phục đúng cặp backup.

`*.showtime-seed.json` chưa được ignore. `.gitignore` ngoài allowlist Round 3 nên không sửa. Rủi ro là state runtime có thể bị add nhầm. Đề xuất PO cho phép thêm đúng một dòng hẹp:

```gitignore
/backend/*.db.showtime-seed.json
```

Dòng này chỉ nhắm sidecar của SQLite DB trực tiếp dưới `backend/`, không bỏ qua report/evidence hoặc file tài liệu ở nơi khác.

## 5. Kết quả kiểm thử

| Gate | Kết quả |
|---|---|
| RF-03 trước sửa | Expected FAIL — `0/99` suất sau reset, `1 failed` |
| Focused seed sau sửa | PASS — `9 passed, 1 warning` |
| Full pytest venv dự án | PASS — `28 passed, 1 warning` |
| Pytest môi trường thật sự không torch/model | PASS — `TORCH_SPEC=None`, `TRANSFORMERS_SPEC=None`, `MODELS_DIR_EXISTS=False`; `28 passed, 1 warning` |
| Backend compileall | PASS — `app` và `tests` |
| Frontend build real | PASS — 70 modules |
| Frontend build mock | PASS — 70 modules |
| `git diff --check` | PASS; chỉ cảnh báo chuyển LF/CRLF của working copy, không có whitespace error |
| Scope/protected files | PASS — Round 3 chỉ code/test/doc/report/coordination được phép; không schema/model/normalize/.env/DB |
| Security/secret scan | PASS — không phát hiện secret mới |
| Skip/xfail | PASS — không thêm skip/xfail |
| Runtime state | PASS — không có `*.showtime-seed.json` được Git track |
| Database thật | Chỉ đọc SHA-256, không kết nối: `B3F7DF79BDA4478412200EA80B8EC15E6B73DA730068A52E11C40136EAC4CFE3`, không đổi so với baseline |

Cảnh báo duy nhất là deprecation Starlette TestClient/AnyIO đã có từ trước; không nâng/thêm thư viện ngoài scope.

## 6. AC matrix

| AC | Trạng thái sau Round 3 | Evidence |
|---|---|---|
| AC-01 | PASS | 28/28 trong môi trường không torch, transformers hoặc thư mục model |
| AC-02 | PASS / không đổi | Full suite duyệt 13/13 route-method admin với 401/403 |
| AC-03 | PASS / không đổi | Full suite giữ regression ghế trùng 409 và đúng một booking seat |
| AC-04 | PASS | RF-03 có test trước/sau và mục F-02 trong `[Unreleased]` được cập nhật |
| AC-05 | PASS | `HUONG_DAN.md` có mục chạy test và quy trình sidecar |
| AC-06 | PENDING fresh runtime verification | Không chạy backend/model thật trong Round 3 vì chưa có runtime authorization riêng cho code cuối; evidence lịch sử Round 1 không bị tự nâng thành PASS mới |

## 7. File thay đổi Round 3

- `backend/app/seed.py`
- `backend/tests/test_seed.py`
- `HUONG_DAN.md`
- `CHANGELOG.md`
- `reports/2026-10-11/codex_fix_T11_round3_2026-10-11.md`
- `docs/TASK_COORDINATION_ACTIVE.md`

## 8. Required Fix, blocker và TODO

- RF-01: **CLOSED / VERIFIED BY CLAUDE**, không thay đổi.
- RF-02: **CLOSED / VERIFIED BY CLAUDE**, regression PASS.
- RF-03: **DEV FIXED / PENDING CLAUDE VERIFICATION**.
- Blocker implementation Round 3: 0.
- TODO-01: AC-06 cần runtime authorization riêng nếu PO/Claude yêu cầu chạy lại trên code cuối.
- TODO-02: `.gitignore` chờ PO mở scope cho dòng `/backend/*.db.showtime-seed.json`.
- Không tự PASS/PO_APPROVE, không merge/close T11 và không mở T12.
