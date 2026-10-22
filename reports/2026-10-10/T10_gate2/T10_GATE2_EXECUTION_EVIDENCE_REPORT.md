# T10 Gate 2 A1 — Execution Evidence Report

> **EXECUTION HARD STOPPED BEFORE BACKUP COMPLETION**  
> **ALTER NOT INVOKED — NO AUTOMATIC RETRY OR RESTORE**

## 1. Authority

- Task: T10.
- Decision ID: `PO-DECISION-T10-REALDB-A1-GATE2-20261010`.
- Gate 1: APPROVED — `27701d1` (`27701d19a150117919e0172f2386d819a7b9d369`).
- Authority: `PO_DECISION_T10_GATE2_EXECUTION_APPROVED_20261010.md`.
- Execution prompt: `CODEX_T10_GATE2_EXECUTION_PROMPT_20261010.md`.
- Operator: Codex.
- Supervisor: Product Owner.
- Authorized package: `C:\Projects\T10_GATE2_A1_FINAL_CANDIDATE_20261010`.
- Scope reached: package integrity gate, preflight, and attempted fresh-backup script.
- Mandatory post-backup PO checkpoint: **NOT REACHED**.

## 2. Immutable package verification

The package was verified before any script invocation, first read-only outside the operator session and again inside the persistent PowerShell 5.1 session.

| File | PO-authorized and observed SHA-256 |
|---|---|
| `01_preflight.ps1` | `56CAB1EE118FF9EEB54D844480CB7F0C080AC0A282AA1C69F187A56E61943F1F` |
| `02_fresh_backup.py` | `F81496DBCA717C892EAA0BC11BAF10C63E7DA7C537F2660E3ACA3ACB1DD10BC9` |
| `03_schema_alter.py` | `6F812ECE3266DC8EDFC4473CED41FDA8B14F180E872C39985FC8CB80B90D4A47` |
| `04_postverify.py` | `E957A2D229DA336839CA48A38608870F572673E802AD01772F7B55E6A2C2303C` |
| `05_clone_smoke.py` | `3624F17763A87E41717088F3E09A211B9C245B134B497129FC1082BE69D0D0B0` |
| `T10_GATE2_EXECUTION_PACKAGE_DRAFT.md` | `FDCDCCA403654D601A13653B0493C3E46B190B389472BC3C75DD101FE97C7044` |

PO-authorized and observed canonical package hash-set:

`ABDC69930EC41034B5A7ED8C566FEF945D11843D60F9413BE0C2192CD2C9899A`

Runtime gate output:

- `PACKAGE_INTEGRITY_GATE=PASS`
- `PACKAGE=C:\Projects\T10_GATE2_A1_FINAL_CANDIDATE_20261010`
- `PACKAGE_HASH_SET_SHA256=ABDC69930EC41034B5A7ED8C566FEF945D11843D60F9413BE0C2192CD2C9899A`

No package file was modified.

## 3. Persistent operator session

- Shell: Windows PowerShell `5.1.26100.9444`.
- Operator shell PID: `2684`.
- Creation time UTC: `2026-10-10T11:51:13.7118650Z`.
- Executable SHA-256: `8BB6FA8C283B4D92120B1EF249A9B311B0F804D4CABBE99811599776C8BE76A5E`.
- Package gate, preflight and backup attempt ran in the same persistent PTY session.
- On failure the session emitted:
  - `EXECUTION_STATUS=HARD_STOP_BEFORE_BACKUP_COMPLETION`
  - `ALTER_INVOKED=NO`
- The operator session was then closed to prevent accidental continuation.

## 4. Preflight evidence

Preflight result: **PASS**.

- `HEAD=27701d19a150117919e0172f2386d819a7b9d369`
- `DATABASE_URL=sqlite:///./firefly.db`
- `DATABASE_PATH=C:\Projects\firefly-cinema\backend\firefly.db`
- Tables: `booking_seats`, `bookings`, `comments`, `movies`, `showtimes`, `users`.
- `comments` had the expected 12 pre-T10 columns and no `model_version`.
- `integrity=["ok"]`.
- `fk_errors=0`.
- `NEXT_REQUIRED_STEP=02_fresh_backup.py`.
- Process, listener, sidecar, path and exclusive file-handle checks passed inside `01_preflight.ps1`.

## 5. Fresh-backup attempt and hard stop

`02_fresh_backup.py` was invoked with the approved Decision ID and supervisor confirmation. It exited with code `1` and printed:

```text
'No time zone found with key Asia/Ho_Chi_Minh'
HARD STOP: fresh backup failed with exit code 1.
```

Static location of the failure in the SHA-approved script:

- line 202 opens the source database read-only;
- lines 203–205 build and validate the pre-backup snapshot;
- line 207 calls `ZoneInfo("Asia/Ho_Chi_Minh")` and failed because the Python runtime could not resolve that timezone;
- `backup_dir.mkdir(...)` is line 209 and was not reached;
- online backup starts at line 215 and was not reached;
- restore validation starts at line 239 and was not reached;
- manifest creation starts at line 253 and was not reached.

Observed artifact state after failure:

- New `gate2_*` directory count: `0`.
- Fresh backup file: **NOT CREATED**.
- Restore-validation clone: **NOT CREATED**.
- Manifest: **NOT CREATED**.
- Manifest SHA-256: **UNAVAILABLE**.
- Live PO manifest checkpoint: **NOT REACHED / NOT ELIGIBLE FOR APPROVAL**.

No retry was attempted. No environment/package remediation was performed.

## 6. Real database preservation evidence

- Database: `C:\Projects\firefly-cinema\backend\firefly.db`.
- Post-failure SHA-256: `ED3ABDBAD7FF65F74D2182DC8B5C757E8FC32EDF37DCAF4073EAC1D375E70D0A`.
- This exactly matches the previously recorded pre-execution baseline in the Gate 1/preflight evidence.
- Size: `81920` bytes.
- Last-write UTC: `2026-10-08T17:05:50.2373703Z`.
- `-wal`: absent.
- `-shm`: absent.
- `-journal`: absent.
- The failing script path had only opened the source database read-only before the timezone exception.
- Real database modified: **NO**.

## 7. Prohibited later phases

The following were not invoked:

- `03_schema_alter.py`;
- any SQL ALTER or other real-database write;
- `04_postverify.py`;
- `05_clone_smoke.py`;
- backend startup against either real DB or clone;
- restore or database replacement;
- credential entry;
- merge, tag, task closure or T11.

ALTER/COMMIT state: **NOT STARTED / PROVEN NOT INVOKED**.

## 8. Git and package status

- Repository branch: `task/T10-gan-model-B`.
- Repository HEAD: `27701d19a150117919e0172f2386d819a7b9d369`.
- Repository worktree after hard stop: CLEAN.
- Six-file package: unchanged from PO-authorized hashes.
- Git commit: NONE.

## 9. Blocker and required next decision

Blocker: the approved Python runtime lacks timezone data for `ZoneInfo("Asia/Ho_Chi_Minh")`.

The immutable package cannot be patched or automatically rehashed under the current execution authority. Installing/changing runtime dependencies or changing timestamp logic was not authorized and was not attempted.

Before any retry, PO must decide and authorize the remediation path. Because this attempt stopped before ALTER and created no manifest, any future attempt must use a **new persistent session**, rerun package integrity gate and preflight, create a fresh backup, and stop again at the live PO checkpoint. Nothing from this failed attempt may be treated as a validated backup or checkpoint.

## 10. Status

TASK: T10  
EXECUTION STATUS: HARD STOP / BLOCKED BEFORE BACKUP CREATION  
PACKAGE INTEGRITY GATE: PASS  
PREFLIGHT: PASS  
BACKUP SCRIPT INVOKED: YES — EXIT 1  
BACKUP CREATED: NO  
RESTORE VALIDATION: NOT EXECUTED  
MANIFEST: NOT CREATED  
PO LIVE CHECKPOINT: NOT REACHED  
ALTER EXECUTED: NO  
COMMIT STATE: NOT STARTED  
POSTVERIFY EXECUTED: NO  
API SMOKE EXECUTED: NO  
REAL DB MODIFIED: NO  
GIT COMMIT: NONE  
NEXT STEP: PO DECISION ON TIMEZONE-RUNTIME REMEDIATION; THEN NEW SESSION/FRESH ATTEMPT IF AUTHORIZED

**HARD STOP — chờ PO.**
