# T10 Gate 2 A1 — Claude Final Candidate Review (static)

> **STATIC REVIEW ONLY — GATE 2 EXECUTION NOT AUTHORIZED — NOTHING EXECUTED**
> Proposed Decision ID `PO-DECISION-T10-REALDB-A1-GATE2-20261010` có mặt trong candidate **không** phải quyền chạy.

**Verdict: FAIL — package chưa sẵn sàng thực thi**, vì 1 Required Fix về đường dẫn thực thi (GC-RF-01).

Phần nội dung an toàn của candidate (SQL, transaction, backup, kiểm tra tiến trình, cô lập clone, phục hồi) **giống hệt** bản draft đã được review PASS_WITH_TODO; khác biệt chỉ nằm ở 5 dòng Decision ID. Lỗi đường dẫn **dừng theo hướng an toàn**: nếu chạy theo runbook hiện tại, bước Package Integrity Gate sẽ HARD STOP; kể cả khi lọt qua, các script draft cũng từ chối chạy vì Decision ID còn pending. Không có nguy cơ mất dữ liệu. Nhưng như hiện tại, runbook không thể dùng để chạy đúng final candidate.

## 1. Freeze verification

| Kiểm tra | Kết quả |
|---|---|
| Diff draft → candidate | **Đúng 5 dòng**, mỗi file script 1 dòng: `01_preflight.ps1:12`, `02_fresh_backup.py:22`, `03_schema_alter.py:16`, `04_postverify.py:15`, `05_clone_smoke.py:21`. `PENDING_PO_GATE2` → `PO-DECISION-T10-REALDB-A1-GATE2-20261010` (`diff` thực tế, không dựa report) |
| Runbook | `T10_GATE2_EXECUTION_PACKAGE_DRAFT.md` giống draft **từng byte** (`E78E4F5B…`; `diff` rỗng) |
| SQL / transaction / backup / process checks / clone isolation | Không đổi (ngoài 5 dòng trên không có byte nào khác) |
| Decision ID 5/5 | Đúng `PO-DECISION-T10-REALDB-A1-GATE2-20261010`. 03/04/05 so sánh hằng của mình với hằng của 02 nên nhất quán |
| Draft gốc | Vẫn nguyên: 6 hash như lần review trước, hash-set `9E2DBD32…9B4A`, 5 hằng vẫn `PENDING_PO_GATE2` |
| Static checks trên candidate | `01_preflight.ps1` parse 0 lỗi (pwsh 7.6 + Windows PowerShell 5.1); `ast.parse` 02–05 4/4 |

## 2. SHA-256 6/6 (Claude tự tính)

| File | SHA-256 | Khớp freeze report |
|---|---|---|
| `01_preflight.ps1` | `56CAB1EE118FF9EEB54D844480CB7F0C080AC0A282AA1C69F187A56E61943F1F` | Có |
| `02_fresh_backup.py` | `F81496DBCA717C892EAA0BC11BAF10C63E7DA7C537F2660E3ACA3ACB1DD10BC9` | Có |
| `03_schema_alter.py` | `6F812ECE3266DC8EDFC4473CED41FDA8B14F180E872C39985FC8CB80B90D4A47` | Có |
| `04_postverify.py` | `E957A2D229DA336839CA48A38608870F572673E802AD01772F7B55E6A2C2303C` | Có |
| `05_clone_smoke.py` | `3624F17763A87E41717088F3E09A211B9C245B134B497129FC1082BE69D0D0B0` | Có |
| `T10_GATE2_EXECUTION_PACKAGE_DRAFT.md` | `E78E4F5B447E066E4ED759C53FA70111602FD825DDDE296F8FDE660C6077203D` | Có |

**Canonical hash-set:** `627AB637ECA04C15D1240053043D46B5A672786037D8104D12404233C485E884` — **khớp**. Thuật toán giống bản đã review (JSON compact, khóa sắp xếp, ASCII). Đây là hash của **candidate**, chưa phải hash PO duyệt để chạy.

## 3. Execution path finding — GC-RF-01

- **Severity:** High (chặn khả năng thực thi; theo hướng an toàn, không gây hại dữ liệu)
- **File / dòng:** `T10_GATE2_EXECUTION_PACKAGE_DRAFT.md:64` (bản trong candidate): `$Package = 'C:\Projects\T10_GATE2_A1_DRAFT_20261010'`
- **Problem:** `$Package` trỏ tới **source draft**, không phải final candidate. Mọi tham chiếu đều đi qua biến này:
  - Package Integrity Gate (dòng 116: `Join-Path $Package $Name`);
  - 01 (dòng 154), 02 (164), 03 (215), 04 (228), 05 (264).
- **Hệ quả nếu chạy nguyên văn:**
  1. Gate băm 6 file **draft** rồi so với hash candidate mà PO duyệt → khác nhau → HARD STOP trước script 01.
  2. Nếu gate bị bỏ qua hoặc so nhầm, các script draft vẫn có `PENDING_PO_GATE2` → tự từ chối.
  3. Các script Python tự băm package và nạp 02 theo `Path(__file__)`, nên sẽ ràng buộc vào **thư mục được gọi**. Lỗi sửa đúng chỗ thì toàn bộ chuỗi tự nhất quán.
- **Evidence:** `grep` các dòng 64/116/154/164/215/228/264. Freeze report §5 ghi "integrity gate precedes all script invocations: PASS" nhưng không phát hiện đường dẫn này.
- **Expected fix (PO chọn, Claude không chọn thay):**
  - **A.** PO phê duyệt riêng, trong quyết định Gate 2 bên ngoài package, đúng một lệnh `$Package = 'C:\Projects\T10_GATE2_A1_FINAL_CANDIDATE_20261010'`. Lệnh này chạy trong persistent session, **sau** khối §4.1 và **trước** §4.2. Quyết định phải nêu rõ lệnh cũng phải chạy lại ở **mọi** session phục hồi (§4.10 A/C) trước khi chạy lại gate. Ưu: không đổi byte nào, hash `627AB637…` giữ nguyên. Nhược: lệnh thực thi lệch khỏi runbook đã băm, và độ an toàn phụ thuộc kỷ luật của operator ở mỗi session.
  - **B.** Codex sửa dòng 64 của runbook trong một candidate mới (hoặc tạo lại candidate), giữ nguyên mọi nội dung khác, đóng băng lại, tính 6 hash + hash-set mới, rồi review lại. Ưu: runbook đã băm khớp đúng lệnh thực thi. Nhược: thêm một vòng review. Có thể sửa luôn dòng trạng thái lỗi thời ở mục 6 bên dưới, nếu PO cho phép.

## 4. Safety verification (không đổi so với draft đã review)

| Yêu cầu | Kết quả |
|---|---|
| Operator Codex / PO giám sát | Runbook §1, §4.1. G2-R4-04 PO ACCEPT_WITH_NOTES: PO tự nhập credential |
| Persistent PowerShell session | §1, §4.1; identity gồm PID, thời điểm tạo, hash exe |
| Chuỗi tiến trình fail-closed | 01:102-123; 03 recheck: chỉ chấp nhận đúng chuỗi shell → (launcher venv) → Python → recheck, chỉ loại các PID cụ thể |
| Package Integrity Gate trước mọi script | Vị trí đúng (§4.2 đứng trước §4.3), **nhưng trỏ sai thư mục** → GC-RF-01 |
| Fresh backup + restore validation | 02 không đổi logic (chỉ khác hằng) |
| Đúng một SQLite ALTER | 03: literal 1, `execute(ALTER_SQL)` 1 |
| Kiểm tra dữ liệu trước COMMIT | `ensure_only_allowed_schema_change` chạy trước `commit()` |
| Phục hồi khi COMMIT đã biết / chưa rõ | §4.10 A/B/C; về cấu trúc không thể ALTER lần hai (01/02 đòi schema cũ; 03 đòi SHA và trạng thái DB khớp manifest trước ALTER) |
| Postverify chỉ đọc | 04 mở `mode=ro` |
| Smoke chỉ trên clone | 05: engine được chứng minh trỏ vào clone qua marker cùng tiến trình |
| Không khởi động backend trên DB thật | §5 runbook; 04 in `REAL_DB_RUNTIME_STARTUP_AUTHORIZED=NO` |
| Không tự restore / merge / tag / T11 | Không có lệnh nào như vậy trong package |

## 5. Required Fixes

| ID | Severity | Nội dung | Trạng thái |
|---|---|---|---|
| GC-RF-01 | High (thực thi, fail-closed) | `$Package` trong runbook trỏ tới draft thay vì final candidate | **OPEN** — chờ PO chọn A hoặc B |

## 6. Remaining TODOs

- G2-R4-01 → 04: PO đã ACCEPT_WITH_NOTES (freeze report §7). Claude ghi nhận, không đổi disposition.
- GC-TODO-01 (Info): runbook trong candidate vẫn ghi "DRAFT — DO NOT EXECUTE", "Gate 2 Decision ID: `PENDING_PO_GATE2`" (dòng 3, 10, 371) và "Next step: Claude final independent review". Không ảnh hưởng logic; quyết định Gate 2 bên ngoài package là nguồn thẩm quyền. Nếu chọn phương án B có thể sửa luôn, kèm PO duyệt.
- GC-TODO-02 (Info): nếu chọn A, PO nên yêu cầu operator in `$Package` và `PACKAGE_HASH_SET_SHA256` sau gate để PO đối chiếu trực tiếp với `627AB637…`.

## 7. Điều kiện PO phải chốt trước Gate 2

1. Chọn cách xử lý GC-RF-01 (A hoặc B). Nếu B: hash mới và review lại candidate mới.
2. Công bố bên ngoài package: 6 SHA-256 từng file + hash-set cuối (`627AB637…` nếu A; giá trị mới nếu B).
3. Ban hành Decision ID chính thức (đúng chuỗi trong 5 script), người chạy (Codex), PO giám sát, thời điểm, một persistent PowerShell 5.1 PTY.
4. Ghi rõ phạm vi: **không** khởi động backend trên DB thật; không tự restore; mọi nghi ngờ về COMMIT xử lý theo §4.10 B.
5. PO tự nhập credential cho smoke trên clone.

## 8. Trạng thái

- Diff: **đúng 5 dòng** Decision ID.
- SHA-256: **6/6 khớp**. Hash-set: **`627AB637…E884` khớp**.
- Execution path: **GC-RF-01 OPEN** (runbook trỏ draft).
- **Real DB Modified: NO** (trong phạm vi kiểm tra). SHA-256 `backend/firefly.db` = `ED3ABDBA…0D0A`, trùng giá trị ở các lần review trước; không có `-wal/-shm/-journal`; 0 thư mục `gate2_*`. Claude chỉ băm file, không mở SQLite. Repo sạch tại `27701d1`.
- Claude không chạy script hay khối PowerShell nào của runbook, không sửa candidate/draft/repo, không commit.
- **Gate 2 Execution: NOT AUTHORIZED.**

**HARD STOP — chờ PO.**
