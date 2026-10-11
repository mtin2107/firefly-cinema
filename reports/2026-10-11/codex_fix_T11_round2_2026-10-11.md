# T11 — Fix Loop Round 2

- Ngày: 11/10/2026
- Branch: `task/T11-kiem-thu`
- Claude Review Round 1: `FAIL`, review HEAD `deafc6edd6945d493e23ff83e7825735a8e167ff`
- Coordination chuyển sang `FIX_LOOP` tại commit Claude `77b123d614592b262dfae3b1575f687aa04b5475`
- Fix implementation commit: `b06b74eec4d18c5e8cd3e3117d352f10dd97b989`
- Trạng thái bàn giao: `FIX_LOOP → CLAUDE_REVIEW` (chờ review độc lập Round 2)

## 1. Bằng chứng tái hiện trước sửa

Ba regression test mới được thêm trước khi sửa `seed.py`. Focused run trên code lỗi:

```text
.F.FF.  [100%]
3 failed, 3 passed, 1 warning
```

- RF-01: sau khi xóa toàn bộ suất ngày D và gọi lại vòng đời `seed()`, ngày D bị tạo lại 4 suất.
- RF-02: khi ngày D+5 đã có suất admin cho phim A, sau khi cửa sổ dịch chuyển ngày đó chỉ có movie IDs `{1}`, thiếu phim B.
- Regression liên quan: phim mới chuyển từ `upcoming` sang `now_showing` không được cấp lịch ở các ngày đã seed.

## 2. RF-01 — dấu ngày/movie đã seed bền vững

Không đổi schema. `seed.py` dùng sidecar `<database>.showtime-seed.json`:

- Đường dẫn được suy ra từ `db.get_bind().url.database`, resolve tới đúng file SQLite mà session đang dùng; mỗi database có sidecar riêng.
- State lưu version và danh sách movie IDs đã được xử lý theo từng ngày. Vì trạng thái không phụ thuộc vào các suất còn tồn tại, xóa một suất hoặc xóa sạch ngày không làm seed tái tạo lại.
- Ghi an toàn bằng file tạm trong cùng thư mục, `flush` + `fsync`, sau đó `os.replace` nguyên tử. File tạm được dọn nếu ghi lỗi.
- DB commit trước khi publish state. Nếu tiến trình dừng đúng khe giữa commit và replace, lần sau duplicate/conflict guard chạy lại an toàn; state cũ của các ngày trước vẫn giữ nguyên.
- Sidecar hỏng/sai version làm startup hard-fail bằng `RuntimeError`; không âm thầm bỏ state rồi tái tạo dữ liệu đã xóa.
- SQLite `:memory:` dùng state trong `Session.info`; runtime chính vẫn là SQLite file.

Test `test_deleting_all_showtimes_of_a_day_is_not_reverted` mở một SQLAlchemy `Session` mới sau khi xóa cả ngày để kiểm đúng hành vi restart. Kết quả: ngày D giữ 0 suất.

## 3. Khởi tạo database hiện hữu và backup/restore

Khi database file đã có lịch nhưng chưa có sidecar:

1. Chỉ xét cửa sổ rolling hiện tại.
2. Tìm ngày có lịch xa nhất trong cửa sổ.
3. Các ngày từ đầu cửa sổ tới mốc đó được khởi tạo là đã xử lý cho tập phim `now_showing` hiện tại. Đây là lựa chọn bảo thủ để không đảo ngược các thao tác xóa cũ, kể cả khoảng ngày đã bị xóa sạch ở giữa.
4. Các ngày sau mốc vẫn được seed, nên rolling tiếp tục tiến về trước.
5. Nếu cửa sổ chưa có lịch, state bắt đầu rỗng và toàn bộ cửa sổ được seed bình thường.

Sidecar là một phần của trạng thái vận hành: backup/restore phải thực hiện khi backend dừng và sao chép **cả file DB lẫn sidecar cùng thời điểm**. Restore chỉ DB mà thiếu sidecar sẽ chạy quy tắc khởi tạo bảo thủ; cách đó không thể tái dựng hoàn hảo lịch sử xóa. Không có sidecar nào được tạo cạnh `backend/firefly.db` trong Fix Round 2; mọi test dùng SQLite tạm. Không commit file runtime state.

## 4. RF-02 — ngày có suất admin vẫn được seed công bằng

Khi một ngày chưa có state lần đầu vào cửa sổ:

- Suất admin hiện có được giữ nguyên tuyệt đối.
- Phim đã có suất được tính là đạt suất tối thiểu.
- Các phim `now_showing` còn thiếu vẫn đi qua hai pass phân bổ của T05: suất tối thiểu trước, lịch mẫu sau.
- `find_showtime_conflict` và vòng thử phòng khác vẫn được dùng; test kiểm từng cặp suất cùng phòng không chồng nhau, gồm 15 phút dọn phòng.
- Sau khi xử lý, movie IDs được ghi vào state để những suất seed bị xóa sau đó không tái xuất hiện.

Test `test_new_rolling_day_keeps_admin_showtime_and_seeds_other_movies` xác nhận phim A/B đều có lịch, snapshot suất admin không đổi và không có overlap.

## 5. Rolling 5 ngày và phim mới `now_showing`

- Cửa sổ vẫn bổ sung ngày mới khi `date.today()` dịch chuyển.
- Ngày mới có sẵn suất admin không còn bị bỏ qua toàn bộ.
- Ngày cũ đã seed không phục hồi suất bị xóa.
- Phim tồn tại với trạng thái `upcoming`, sau đó chuyển sang `now_showing`, chưa có trong danh sách handled của ngày nên vẫn được cấp lịch trên đủ 5 ngày. Hành vi trước T11 được giữ, không cần quyết định thay đổi hợp đồng từ PO.
- Suất admin và booking đã có tiếp tục được bảo toàn.

## 6. Test mới và regression

`backend/tests/test_seed.py` hiện có 6 test:

1. Xóa một suất không bị tái tạo.
2. Xóa sạch một ngày không bị tái tạo sau Session mới.
3. Rolling thêm ngày mới cho đủ phim.
4. Ngày mới có suất admin vẫn seed phim còn thiếu, giữ nguyên admin và không overlap.
5. Phim chuyển `upcoming → now_showing` được cấp đủ lịch đã seed.
6. Suất admin và booking không bị thay đổi.

Focused sau sửa: `6 passed, 1 warning`.

## 7. Verification đầy đủ

| Gate | Kết quả |
|---|---|
| Focused RF-01/RF-02 trước sửa | Expected FAIL — `3 failed, 3 passed` |
| Focused sau sửa | PASS — `6 passed, 1 warning` |
| Full pytest venv dự án | PASS — `25 passed, 1 warning` |
| Pytest source cô lập không model/torch | PASS — `25 passed, 1 warning`; `torch=None`, `transformers=None`, `models_dir=False` |
| Backend compileall | PASS |
| Frontend build real | PASS — 70 modules |
| Frontend build mock | PASS — 70 modules |
| Scope | PASS — implementation chỉ sửa `seed.py`, `test_seed.py`, `CHANGELOG.md` |
| Protected file / runtime state | PASS — không `.env`, DB, model, joblib, CSV hoặc `*.showtime-seed.json` trong diff |
| Secret scan / `git diff --check` | PASS |
| Database thật | Không khởi động/kết nối/ghi; SHA-256 vẫn `B3F7DF79BDA4478412200EA80B8EC15E6B73DA730068A52E11C40136EAC4CFE3` |

Cảnh báo duy nhất tiếp tục là deprecation từ Starlette TestClient/AnyIO; không nâng thư viện ngoài phạm vi.

## 8. File thay đổi Round 2

- `backend/app/seed.py`
- `backend/tests/test_seed.py`
- `CHANGELOG.md`
- `reports/2026-10-11/codex_fix_T11_round2_2026-10-11.md`
- `docs/TASK_COORDINATION_ACTIVE.md`

## 9. Blocker và TODO

- Blocker: 0.
- RF-01: DEV FIXED / PENDING CLAUDE VERIFICATION.
- RF-02: DEV FIXED / PENDING CLAUDE VERIFICATION.
- TODO vận hành: mọi quy trình backup/restore sau khi sidecar được tạo phải coi DB + sidecar là một cặp nhất quán; không xóa sidecar riêng lẻ.
- TODO không chặn: deprecation warning của Starlette TestClient.
- Không tự PASS/PO_APPROVE, không merge/close T11 và không mở T12.
