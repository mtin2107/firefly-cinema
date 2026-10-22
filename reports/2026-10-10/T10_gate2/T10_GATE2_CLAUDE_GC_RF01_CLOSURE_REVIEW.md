# T10 Gate 2 A1 — Claude GC-RF-01 Closure Review (static)

> **STATIC REVIEW ONLY — GATE 2 EXECUTION NOT AUTHORIZED — NOTHING EXECUTED**

**Verdict: PASS_WITH_TODO**
**GC-RF-01: CLOSED / VERIFIED BY CLAUDE**
**Kết luận: `READY_FOR_PO_GATE2_EXECUTION_DECISION`** — đây **không** phải phê duyệt Gate 2.

## 1. Exact diff verification

So sánh runbook candidate hiện tại với runbook đã review ở vòng trước. Bản vòng trước có SHA `E78E4F5B…`, giống từng byte với runbook draft hiện vẫn nằm ở `C:\Projects\T10_GATE2_A1_DRAFT_20261010`, nên dùng file draft đó làm mốc. Kết quả `diff` thực tế:

```diff
64c64
< $Package = 'C:\Projects\T10_GATE2_A1_DRAFT_20261010'
---
> $Package = 'C:\Projects\T10_GATE2_A1_FINAL_CANDIDATE_20261010'
```

- Runbook: **đúng 1 dòng** thay đổi. Không đổi heading, trạng thái, recovery, SQL, timeout, bộ lọc tiến trình, chuỗi PID, backup, rollback hay cô lập clone.
- Script 01–05: `diff` so với draft vẫn chỉ là 5 dòng Decision ID như vòng trước. Hash 5/5 **không đổi** so với freeze report.
- Mọi tham chiếu thư mục package trong runbook đều qua `$Package`: dòng 116 (gate), 154, 164, 215, 228, 264. Đường dẫn draft **không còn** xuất hiện trong runbook candidate.

## 2. SHA-256 verification (Claude tự tính)

| File | SHA-256 | So với freeze / remediation |
|---|---|---|
| `01_preflight.ps1` | `56CAB1EE118FF9EEB54D844480CB7F0C080AC0A282AA1C69F187A56E61943F1F` | Không đổi |
| `02_fresh_backup.py` | `F81496DBCA717C892EAA0BC11BAF10C63E7DA7C537F2660E3ACA3ACB1DD10BC9` | Không đổi |
| `03_schema_alter.py` | `6F812ECE3266DC8EDFC4473CED41FDA8B14F180E872C39985FC8CB80B90D4A47` | Không đổi |
| `04_postverify.py` | `E957A2D229DA336839CA48A38608870F572673E802AD01772F7B55E6A2C2303C` | Không đổi |
| `05_clone_smoke.py` | `3624F17763A87E41717088F3E09A211B9C245B134B497129FC1082BE69D0D0B0` | Không đổi |
| `T10_GATE2_EXECUTION_PACKAGE_DRAFT.md` | `FDCDCCA403654D601A13653B0493C3E46B190B389472BC3C75DD101FE97C7044` | **Khớp giá trị kỳ vọng** |

**Canonical hash-set:** `ABDC69930EC41034B5A7ED8C566FEF945D11843D60F9413BE0C2192CD2C9899A` — **khớp**. Thuật toán giống bản đã review. Hash cũ `627AB637…` đã lỗi thời và không được dùng để duyệt.

## 3. Execution path resolution

- `$Package = 'C:\Projects\T10_GATE2_A1_FINAL_CANDIDATE_20261010'` (dòng 64). Thư mục này có đủ 5 script đã kiểm cùng runbook.
- Package Integrity Gate băm `Join-Path $Package $Name`, tức đúng 6 file candidate.
- Gate đứng trước mọi lời gọi script: `PACKAGE_INTEGRITY_GATE=PASS` in ở dòng 144, lời gọi script đầu tiên ở dòng 154. Cả 5 lời gọi (154/164/215/228/264) đều nằm sau gate.
- Các script Python tự băm package và nạp 02 theo `Path(__file__)`, nên khi được gọi từ candidate, mọi kiểm tra độc lập đều ràng buộc vào candidate.
- Session phục hồi (§4.10 A/C) bắt buộc chạy lại gate. Gate dùng `$Package` khai báo ở §4.1 — giờ đã đúng candidate. Thiếu §4.1 thì `Set-StrictMode`/`Assert-ReadyValue` làm gate dừng.
- Parser: 10/10 khối PowerShell trong runbook, 0 lỗi.

## 4. Safety verification

Không đổi so với các vòng đã review (5 script giữ nguyên byte):

| Điều kiện | Kết quả |
|---|---|
| Operator Codex, PO giám sát | §1, §4.1 |
| Một persistent Windows PowerShell 5.1 PTY | §1, §4.1; identity gồm PID, thời điểm tạo, hash exe; 01/03 kiểm chuỗi tiến trình theo hướng dừng an toàn |
| Package Integrity Gate trước script đầu | Có (mục 3) |
| Fresh backup + restore validation trước ALTER | 02; §4.5 so 3 cặp SHA |
| PO checkpoint giữa backup và ALTER | §4.6; ALTER cần chuỗi xác nhận `…_MANIFEST_REVIEWED` |
| Chính xác một ALTER `comments.model_version VARCHAR(100)` | 03: literal 1, `execute(ALTER_SQL)` 1 |
| Kiểm tra bảo toàn dữ liệu trước COMMIT | `ensure_only_allowed_schema_change` trước `commit()`; lỗi → rollback |
| Mất phiên / COMMIT không rõ → HARD STOP | §4.10 A/B; về cấu trúc không thể ALTER lần hai |
| Postverify chỉ đọc | 04 mở `mode=ro` |
| API smoke chỉ ghi clone | 05: marker cùng tiến trình chứng minh engine trỏ vào clone; SHA DB thật kiểm trước/sau |
| Không khởi động backend trên DB thật | §5 runbook |
| Không tự restore | Không có lệnh restore; §7 chỉ restore sang file mới khi PO quyết định riêng |
| Không merge / tag / mở T11 | Không có trong package |

## 5. Required Fixes

**0.** GC-RF-01 CLOSED.

## 6. Remaining TODO / blockers

**TODO (Info, không chặn):**
- GC-TODO-01: runbook vẫn ghi "DRAFT — DO NOT EXECUTE", "Gate 2 Decision ID: `PENDING_PO_GATE2`" và "Next step: Claude final independent review" (dòng 3, 10, 371, 377). PO đã chọn chỉ sửa 1 dòng; quyết định Gate 2 bên ngoài package là nguồn thẩm quyền. Chấp nhận, kèm ghi chú.
- G2-R4-01 → 04: PO đã ACCEPT_WITH_NOTES.

**Blocker (thủ tục — thuộc quyền PO):**
1. PO ban hành quyết định thực thi Gate 2 riêng, với Decision ID đúng `PO-DECISION-T10-REALDB-A1-GATE2-20261010`.
2. PO công bố bên ngoài package **6 hash từng file + hash-set `ABDC6993…899A`**, là giá trị operator nhập vào `$ApprovedPackageFileSha256` / `$ApprovedPackageHashSetSha256`.
3. Quyết định ghi rõ: operator Codex, PO giám sát, thời điểm, một persistent PowerShell 5.1 PTY, PO tự nhập credential smoke, **không** khởi động backend trên DB thật, không tự restore.
4. Mọi điều kiện runtime vẫn **NOT VERIFIED**: chuỗi PID thật, quyền đọc metadata tiến trình, probe handle file DB, Online Backup, `BEGIN EXCLUSIVE`, postverify, smoke trên clone. Không đạt thì `BLOCKED_EXECUTION_MODEL` / HARD STOP.

## 7. Recommendation for PO exact-hash execution decision

Package ở trạng thái **`READY_FOR_PO_GATE2_EXECUTION_DECISION`**. Nếu PO quyết định cho chạy:

- chỉ phê duyệt đúng hash-set `ABDC69930EC41034B5A7ED8C566FEF945D11843D60F9413BE0C2192CD2C9899A` và 6 hash ở mục 2;
- không sửa thêm byte nào trong 6 file — bất kỳ thay đổi nào cũng cần vòng review mới;
- sau gate, yêu cầu operator in `$Package` và `PACKAGE_HASH_SET_SHA256` để PO đối chiếu trực tiếp;
- chạy từng pha, dừng ở checkpoint §4.6 để PO review manifest trước ALTER.

## 8. Final state

- Diff: runbook **đúng 1 dòng**; script 01–05 không đổi (5/5 hash giữ nguyên).
- SHA-256 6/6 và hash-set: **khớp**.
- Bằng chứng DB: SHA-256 `backend/firefly.db` = `ED3ABDBA…0D0A` (trùng các lần trước); không có `-wal/-shm/-journal`; 0 thư mục `gate2_*`. Claude chỉ băm file, không kết nối SQLite. Repo sạch tại `27701d1`.

GATE 2 EXECUTION: NOT AUTHORIZED
REAL DB MODIFIED BY REVIEW: NO
BACKUP / ALTER / RESTORE / API SMOKE: NOT RUN
NEXT STEP: PO SEPARATE EXECUTION AUTHORIZATION

**HARD STOP — chờ PO.**
