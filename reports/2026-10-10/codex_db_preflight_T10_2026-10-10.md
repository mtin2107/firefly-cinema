# Codex Database Preflight Report — T10 — 10/10/2026

## 1. Phạm vi và authority

- Branch: `task/T10-gan-model-B`
- HEAD: `498d4b866d1bc2f258cb020faf0bee1ef133563a`
- Claude Round 2: `PASS_WITH_TODO`; RF-01 `CLOSED / VERIFIED BY CLAUDE`; AC 7/7 PASS.
- Workflow giữ nguyên: `PO_REVIEW / PENDING_PO_DB_ACTION`.
- Q2: `NO ALEMBIC / BACKUP_BEFORE_RESET`.
- T11: `PLANNED / NOT AUTHORIZED`.
- Authority của lần chạy này chỉ cho phép đọc DB thật, tạo backup mới, và thử nghiệm trên các bản sao. Không có quyền ALTER/reset/migrate/seed/restore DB thật.

Không sửa source code, Task Record, coordination hoặc tài liệu authority. Report này không được commit theo yêu cầu PO.

## 2. Database runtime thực tế

Kiểm tra cấu hình:

- Process environment `DATABASE_URL`: không đặt.
- `backend/.env`: `DATABASE_URL=sqlite:///./firefly.db`.
- Khi backend được chạy từ `backend/` theo hướng dẫn dự án, đường dẫn resolve là:
  `C:\Projects\firefly-cinema\backend\firefly.db`.

Đường dẫn này trùng database PO chỉ định. Gate đường dẫn: **PASS**.

Trước backup:

- Không có listener backend trên các cổng kiểm tra.
- Không có tiến trình uvicorn/backend đang chạy.
- Không có `firefly.db-wal`, `firefly.db-shm` hoặc `firefly.db-journal`.
- Journal mode: `delete`.
- Kích thước: `81,920` byte.
- `PRAGMA user_version = 0`.
- Page size `4096`, page count `20`, freelist count `0`.

## 3. Phase A — Inventory read-only

Nguồn được mở bằng URI SQLite `mode=ro` và `PRAGMA query_only=ON`. Không chạy `create_all`, seed, migration, VACUUM hay WAL checkpoint.

### 3.1. Integrity và checksum nguồn

- SHA-256: `ED3ABDBAD7FF65F74D2182DC8B5C757E8FC32EDF37DCAF4073EAC1D375E70D0A`.
- `PRAGMA integrity_check`: `ok`.
- `PRAGMA foreign_key_check`: 0 lỗi.
- Kích thước, mtime và SHA-256 không đổi trong lúc inventory.
- Sau toàn bộ dry-run/API test, SHA-256 và mtime nguồn vẫn giữ nguyên.

### 3.2. Tables và số dòng gốc

| Table | Rows | Primary key |
|---|---:|---|
| `users` | 3 | `id` |
| `movies` | 21 | `id` |
| `showtimes` | 99 | `id` |
| `bookings` | 141 | `id` |
| `booking_seats` | 282 | `id` |
| `comments` | 13 | `id` |

Có 6 index tường minh: `ix_users_email` (unique), `ix_showtimes_movie_id`, `ix_showtimes_start_time`, `ix_bookings_user_id`, `ix_booking_seats_showtime_id`, `ix_comments_movie_id`; ngoài ra có unique auto-index cho `(booking_seats.showtime_id, booking_seats.seat_code)`. Không có trigger.

Foreign keys:

- `showtimes.movie_id → movies.id`.
- `bookings.user_id → users.id`; `bookings.showtime_id → showtimes.id`.
- `booking_seats.booking_id → bookings.id`; `booking_seats.showtime_id → showtimes.id`.
- `comments.movie_id → movies.id`; `comments.user_id → users.id`; `comments.reviewed_by → users.id`.

### 3.3. Schema `comments` hiện tại

Các cột hiện có:

`id, movie_id, user_id, content, is_negative, negative_score, model_name, human_label, reviewed_by, reviewed_at, hidden, created_at`

Chưa có `model_version`. Bảng giữ check constraint `human_label IN (0, 1) OR human_label IS NULL`; `hidden` có default `0`.

Phân bố dữ liệu:

- 13/13 comment có `model_name='phobert'`.
- 9 comment chưa review; 2 nhãn người duyệt = 0; 2 nhãn người duyệt = 1.
- Hash danh sách comment ID: `6FE61CCA0DDE8B48DC2C0B4241AFD597EC079C8BE02CA21296076AAA3AF51EAB`.

## 4. Phase B — Consistent Online Backup

Backup mới được tạo bằng `sqlite3.Connection.backup()` với nguồn mở `mode=ro`. Không ghi đè `backup/T10_2026-10-10/firefly_before_T10.db`.

- Thời điểm: `2026-10-10 14:50:49` (Asia/Saigon).
- Thư mục snapshot: `C:\Projects\firefly-cinema\backup\T10_2026-10-10\db_preflight_20261010_145049\`.
- Backup: `firefly_online_backup.db`.
- Kích thước: `81,920` byte.
- SHA-256 backup: `BADCE9E0D9E0262F2DD3903BD451F4C0DA1E2F72913F02049BA36504C1878782`.
- `integrity_check`: `ok`.
- `foreign_key_check`: 0 lỗi.

SHA-256 backup khác SHA-256 nguồn. Đây không phải lỗi: SQLite Online Backup tạo snapshot logic nhất quán và có thể thay đổi các byte quản trị/header. Việc xác minh không dựa riêng vào byte identity.

Đối chiếu logic nguồn ↔ backup:

| Table | Row fingerprint SHA-256 | Kết quả |
|---|---|---|
| `users` | `993a621d4d5567cbc578085df373d6154b296b788cf93839054a9b1f09c002b6` | MATCH |
| `movies` | `5f590ac9174a381a98b4feca3068e31f99ac39a6a269d7e58032a2094706af80` | MATCH |
| `showtimes` | `fb4f24844ef44abf1a73a06e584d3fdb8ada92df6cd954d6a75ad7f9a67187e8` | MATCH |
| `bookings` | `6689eadcc524fe2aae51403ea233a817fb561398750ae415bd616ee6d7b9b497` | MATCH |
| `booking_seats` | `03764bd2e11e745f1312f5317708d6ff6a09cc6e68d7959177b1a6a6bd557457` | MATCH |
| `comments` | `8a9ead7caf4fca9e5764eb4de7ce6cbdd2c70632c9e623b18180c0ec45c15699` | MATCH |

Schema SQL, columns, PK, FK, indexes, user_version và số dòng đều khớp nguồn.

## 5. Phase C — Restore dry-run

Bản restore độc lập:

`C:\Projects\firefly-cinema\backup\T10_2026-10-10\db_preflight_20261010_145049\restore_dry_run\firefly_restored.db`

- Mở SQLite thành công.
- SHA-256: `BADCE9E0D9E0262F2DD3903BD451F4C0DA1E2F72913F02049BA36504C1878782`.
- `integrity_check`: `ok`.
- `foreign_key_check`: 0 lỗi.
- Schema/PK/FK/index: khớp snapshot.
- Counts: 3 users, 21 movies, 99 showtimes, 141 bookings, 282 booking seats, 13 comments.
- Fingerprint từng bảng: khớp nguồn và backup.

Restore dry-run: **PASS**.

## 6. Phase D — Schema upgrade dry-run

Database thử riêng:

`C:\Projects\firefly-cinema\backup\T10_2026-10-10\db_preflight_20261010_145049\schema_dry_run\firefly_schema_upgraded.db`

Trước ALTER, script xác minh bảng `comments` tồn tại, đúng 12 cột cũ và chưa có `model_version`. Câu lệnh duy nhất được chạy trên clone:

```sql
ALTER TABLE comments ADD COLUMN model_version VARCHAR(100);
```

Kết quả:

- Cột mới: `model_version VARCHAR(100)`.
- Nullable: YES (`notnull=0`).
- Default: `NULL`.
- 13/13 comment cũ có `model_version IS NULL`.
- Tổng comment: 13 trước và sau.
- ID, nội dung, `model_name`, nhãn, điểm và toàn bộ cột gốc không đổi.
- Fingerprint toàn bộ dữ liệu gốc của cả 6 bảng không đổi.
- PK/FK/index/constraint gốc được giữ; không có trigger để mất.
- `integrity_check`: `ok`.
- `foreign_key_check`: 0 lỗi.
- Chỉ schema SQL của `comments` thay đổi.

Schema dry-run: **PASS**.

## 7. Phase E — API verification trên clone

Database API test là bản sao thứ hai của DB đã nâng schema:

`C:\Projects\firefly-cinema\backup\T10_2026-10-10\db_preflight_20261010_145049\api_verification\firefly_api_test.db`

Backend được chạy với `DATABASE_URL` tuyệt đối trỏ riêng vào clone, không thể kết nối DB thật.

| Kiểm tra | Kết quả |
|---|---|
| `/api/health` | 200; active `phobert_b`; version `phobert-B-2026-10-09` |
| `/api/movies` | 200; truy xuất đủ 21 phim gốc |
| `GET /api/movies/1/comments` | 200; đọc được comment cũ; không còn `no such column` |
| POST comment mới | 201; ID 14, score `0.9988` |
| Persist model | `phobert_b / phobert-B-2026-10-09` |
| Admin comments | 200; tổng 14, gồm 13 cũ + 1 mới |
| Comment cũ nullable | 13/13 dòng cũ trả `model_version=null` hợp lệ |
| Admin security | 401 không token / 403 user / 200 admin |
| Integrity sau test | `ok`; foreign-key violations 0 |
| Log | Không có `no such column: comments.model_version`, HTTP 500 hay traceback |

Backend startup trên clone chạy `_ensure_showtimes`, bổ sung 20 suất tương lai (99 → 119), và API test thêm đúng 1 comment (13 → 14). Đây chỉ là dữ liệu test trên clone. Từng bản ghi gốc của users, movies, showtimes, bookings, booking_seats và comments được so sánh theo PK/cột gốc và **100% giữ nguyên**.

Fallback Q3 được thử trên clone thứ hai `firefly_fallback_test.db` với B bị cấu hình thiếu:

- Backend khởi động, fallback `phobert / A-backend`.
- Comment mới lưu `phobert / A-backend`, score `0.9937`.
- Integrity `ok`, foreign-key violations 0.

API regression trên clone: **PASS 10/10 yêu cầu Phase E**.

## 8. Lỗi/phát hiện

Không có gate database nào thất bại.

Các điểm cần lưu ý:

1. DB thật vẫn thiếu `comments.model_version`; chưa sẵn sàng chạy T10.
2. SHA file backup khác nguồn nhưng toàn bộ kiểm tra logic/schema/integrity đều khớp; đây là hành vi hợp lệ của Online Backup.
3. Khởi động backend có thể ghi thêm suất chiếu qua `_ensure_showtimes`; vì vậy tuyệt đối không dùng startup backend để “chỉ kiểm tra” DB thật trước khi schema được xử lý.
4. A1 chưa được Q2 hiện hành ủy quyền rõ ràng. Q2/runbook hiện mô tả PO reset DB sau backup; một ALTER bảo toàn dữ liệu cần PO ra quyết định bổ sung cụ thể.

## 9. Đánh giá phương án

### A1 — Bổ sung cột thủ công, bảo toàn dữ liệu

Kỹ thuật dry-run đã PASS. Một ALTER nullable không default vật lý phức tạp bảo toàn đầy đủ 3 users, 21 movies, 99 showtimes, 141 bookings, 282 booking seats và 13 comments; không cần import lại quan hệ.

Ưu điểm:

- Không mất tài khoản, vé, ghế, bình luận hoặc trạng thái duyệt.
- Thay đổi schema tối thiểu, đúng model SQLAlchemy T10.
- Rollback có snapshot logic đã xác minh.

Điều kiện:

- PO phải authorize riêng A1 vì Q2/runbook hiện chỉ nêu backup-before-reset.
- Backend phải dừng hoàn toàn.
- Tạo lại backup online ngay tại thời điểm thực thi và xác minh như preflight.
- Chỉ chạy đúng một ALTER sau khi kiểm tra cột chưa tồn tại.
- Dừng ngay nếu counts/fingerprint/integrity/FK không đạt.

### A2 — Backup rồi PO reset

A2 khớp trực tiếp runbook Q2 hiện hành, nhưng reset + seed không bảo toàn dữ liệu vận hành. Dữ liệu người dùng/vé/bình luận cũ sẽ không tự quay lại; muốn phục hồi cần quy trình import riêng và kiểm tra lại PK/FK/unique seat constraints. Không có quy trình import đó trong T10.

Rủi ro A2 cao hơn A1 về mất dữ liệu và referential integrity. Snapshot cho phép quay lại toàn bộ DB cũ, nhưng khi quay lại thì schema lại thiếu `model_version`.

### Khuyến nghị

**Khuyến nghị A1 về mặt kỹ thuật, nhưng chỉ sau khi PO ban hành authorization bổ sung rõ ràng cho manual ALTER không Alembic.** Evidence dry-run đủ để PO xem xét authorize. Nếu PO không thay đổi/diễn giải bổ sung Q2, phải dùng A2 theo governance hiện hành; Codex không tự chọn hoặc thực thi.

## 10. Runbook A1 đề xuất để PO xét duyệt — CHƯA CHẠY

Các lệnh dưới đây chỉ là dự thảo. Phải thay timestamp, kiểm tra đường dẫn và chỉ chạy sau authorization riêng.

1. Dừng backend và xác nhận không còn listener/process.
2. Tạo một Online Backup mới tại thời điểm thực thi; xác minh integrity, FK, counts và fingerprints.
3. PO chạy transaction ALTER tối thiểu:

```powershell
$env:T10_REAL_DB = "C:\Projects\firefly-cinema\backend\firefly.db"
@'
import os, sqlite3

path = os.environ["T10_REAL_DB"]
conn = sqlite3.connect(path)
try:
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("BEGIN IMMEDIATE")
    columns = [row[1] for row in conn.execute("PRAGMA table_info(comments)")]
    if "model_version" in columns:
        raise RuntimeError("model_version already exists; stop without ALTER")
    conn.execute("ALTER TABLE comments ADD COLUMN model_version VARCHAR(100)")
    conn.commit()
except Exception:
    conn.rollback()
    raise
finally:
    conn.close()
'@ | C:\Projects\firefly-cinema\backend\venv\Scripts\python.exe -
Remove-Item Env:T10_REAL_DB
```

4. Trước khi startup, mở read-only và xác minh column/count/fingerprint/integrity/FK.
5. Chỉ khi bước 4 PASS, PO khởi động backend và chạy smoke API.

## 11. Runbook A2 đề xuất để PO xét duyệt — CHƯA CHẠY

1. Dừng backend.
2. Tạo Online Backup mới và xác minh logic đầy đủ.
3. PO chấp nhận rõ việc reset sẽ mất dữ liệu chưa được import.
4. PO tự xóa đúng `backend/firefly.db` theo `HUONG_DAN.md` 2.1.
5. Startup để `create_all` + seed tạo DB mới.
6. Xác minh schema, integrity, FK, API và dữ liệu seed.
7. Không import dữ liệu cũ nếu chưa có kế hoạch mapping/transaction/validation riêng.

## 12. Rollback strategy

Cho cả A1/A2:

1. Dừng backend; không chạy thêm startup/seed.
2. Giữ nguyên DB lỗi dưới tên quarantine để điều tra; không ghi đè snapshot đã xác minh.
3. PO authorize restore cụ thể.
4. Phục hồi `firefly_online_backup.db` về một file mới, xác minh `integrity_check`, `foreign_key_check`, schema, counts và fingerprints.
5. Chỉ sau khi tất cả khớp, PO thay thế `backend/firefly.db` bằng bản restore và khởi động lại.

Lưu ý: rollback về snapshot khôi phục toàn bộ dữ liệu gốc nhưng cũng khôi phục schema cũ chưa có `model_version`. T10 sẽ lại ở `PENDING_PO_DB_ACTION` cho tới khi phương án schema được xử lý an toàn.

## 13. Kết luận và hard stop

- Backup nhất quán: PASS.
- Restore dry-run: PASS.
- Schema dry-run bảo toàn dữ liệu: PASS.
- API trên clone: PASS.
- Evidence kỹ thuật đủ để PO cân nhắc authorize A1.
- Governance authorization thực thi: CHƯA CÓ.
- `REAL_DB_SCHEMA_READINESS = PENDING_PO_ACTION`.
- DB thật không bị thay đổi.
- Không approve/merge/tag/đóng T10; không mở T11.

**DỪNG tại PO approval gate.**
