# T10 Gate 2 A1 — tzdata Stage B Evidence Report

> **PO AUTHORITY: STAGE B INSTALLATION ONLY**  
> **NO BACKUP RETRY OR GATE 2 RETRY AUTHORIZED**

## 1. Authority and approved artifacts

- Task: T10.
- Stage A: COMPLETED / WHEEL HASH MATCH.
- Stage B authority: offline installation of exactly `tzdata==2026.5` into the specified venv and environment-only verification.
- Python executable: `C:\Projects\firefly-cinema\backend\venv\Scripts\python.exe`.
- Approved wheel: `C:\Projects\T10_GATE2_TZDATA_WHEELHOUSE_20261010\tzdata-2026.5-py2.py3-none-any.whl`.
- Approved version: `2026.5`.
- Approved wheel SHA-256: `B683BD1B6659DDCD810FF02AD09BA821D4BF1065072805063EB35C49617905AC`.
- Approved Gate 2 package canonical hash-set: `ABDC69930EC41034B5A7ED8C566FEF945D11843D60F9413BE0C2192CD2C9899A`.
- Stage A evidence was read before pre-install checks.
- This report is outside the production repository and outside the six-file execution package.

## 2. Mandatory pre-install checks

| Check | Result |
|---|---|
| Exact wheel path exists | PASS |
| Wheelhouse contains exactly the approved wheel | PASS |
| Observed wheel SHA-256 | `B683BD1B6659DDCD810FF02AD09BA821D4BF1065072805063EB35C49617905AC` |
| Wheel hash equals PO approval | PASS |
| Exact Python executable | `C:\Projects\firefly-cinema\backend\venv\Scripts\python.exe` — PASS |
| Python version | `3.13.2` — PASS |
| `tzdata` installed before Stage B | NO |
| Existing `tzdata*` venv entries before install | 0 |
| `PYTHONTZPATH` | UNSET |
| `ZoneInfo("Asia/Ho_Chi_Minh")` before install | Expected `ZoneInfoNotFoundError` — PASS |
| Git branch | `task/T10-gan-model-B` — PASS |
| Git HEAD | `27701d19a150117919e0172f2386d819a7b9d369` — PASS |
| Git worktree | CLEAN |
| Gate 2 package hashes | PASS — 6/6 |
| Gate 2 canonical hash-set | PO-approved value — PASS |

No SQLite database was opened during these checks.

## 3. Exact installation

Executed command:

```powershell
& 'C:\Projects\firefly-cinema\backend\venv\Scripts\python.exe' -B -m pip install `
    --isolated `
    --disable-pip-version-check `
    --no-index `
    --no-deps `
    --no-cache-dir `
    --no-compile `
    'C:\Projects\T10_GATE2_TZDATA_WHEELHOUSE_20261010\tzdata-2026.5-py2.py3-none-any.whl'
```

Installation output:

```text
Processing c:\projects\t10_gate2_tzdata_wheelhouse_20261010\tzdata-2026.5-py2.py3-none-any.whl
Installing collected packages: tzdata
Successfully installed tzdata-2026.5
PIP_INSTALL_EXIT_CODE=0
TZDATA_INSTALLATION=PASS
```

- Installation exit code: `0`.
- No `--upgrade` or `--force-reinstall`.
- No dependency resolution, network index or additional package installation.
- No requirements/source/package file was edited.

## 4. Post-install verification

| Check | Result |
|---|---|
| `importlib.metadata.version("tzdata")` | `2026.5` — PASS |
| `ZoneInfo("Asia/Ho_Chi_Minh")` | Resolved — PASS |
| Zone key | `Asia/Ho_Chi_Minh` |
| `datetime.now(...)` | Executed successfully — PASS |
| Generated timestamp | `20261010_201506_829843+0700` |
| UTC offset | `+0700` / `25200` seconds — valid |
| `python -m pip check` exit code | `0` |
| `pip check` output | `No broken requirements found.` — PASS |
| Wheel SHA-256 after install | Still matches approved hash |

All Python checks used `-B`. They did not connect to SQLite or import/run a Gate 2 script.

## 5. Environment files changed

The authorized venv mutation created the installed package content represented by:

- `C:\Projects\firefly-cinema\backend\venv\Lib\site-packages\tzdata\`
- `C:\Projects\firefly-cinema\backend\venv\Lib\site-packages\tzdata-2026.5.dist-info\`
- `tzdata-2026.5.dist-info\RECORD` contains `636` installed-file entries.

The installer used `--no-compile`, and all verification imports used `-B`. No requirements file, production source or execution-package file changed. The approved wheel was preserved and not removed, renamed, edited or unpacked manually.

No automatic rollback or uninstall was performed.

## 6. Git and six-file package integrity after installation

- Branch: `task/T10-gan-model-B`.
- HEAD: `27701d19a150117919e0172f2386d819a7b9d369`.
- Worktree: CLEAN.

| File | SHA-256 |
|---|---|
| `01_preflight.ps1` | `56CAB1EE118FF9EEB54D844480CB7F0C080AC0A282AA1C69F187A56E61943F1F` |
| `02_fresh_backup.py` | `F81496DBCA717C892EAA0BC11BAF10C63E7DA7C537F2660E3ACA3ACB1DD10BC9` |
| `03_schema_alter.py` | `6F812ECE3266DC8EDFC4473CED41FDA8B14F180E872C39985FC8CB80B90D4A47` |
| `04_postverify.py` | `E957A2D229DA336839CA48A38608870F572673E802AD01772F7B55E6A2C2303C` |
| `05_clone_smoke.py` | `3624F17763A87E41717088F3E09A211B9C245B134B497129FC1082BE69D0D0B0` |
| `T10_GATE2_EXECUTION_PACKAGE_DRAFT.md` | `FDCDCCA403654D601A13653B0493C3E46B190B389472BC3C75DD101FE97C7044` |

Canonical package hash-set after Stage B:

`ABDC69930EC41034B5A7ED8C566FEF945D11843D60F9413BE0C2192CD2C9899A`

Result: **UNCHANGED / PASS**.

## 7. Explicitly not performed

- Did not run `01_preflight.ps1` or scripts 02–05.
- Did not retry fresh backup.
- Did not open, connect to or modify the real SQLite database.
- Did not run ALTER, restore or postverify.
- Did not start backend or API smoke.
- Did not modify source code, requirements or execution package.
- Did not stage, commit, merge, tag or open T11.
- Did not delete the wheel or Stage A evidence.
- Did not run pip uninstall or automatic rollback.
- Did not declare Stage B as backup-retry or Gate 2-retry authority.

## 8. Remaining blockers

1. PO must review this Stage B evidence.
2. Backup retry requires a separate explicit decision.
3. Any future retry must start in a new persistent Windows PowerShell 5.1 session, rerun package integrity gate and preflight, then create a fresh backup.
4. The retry must stop at the live PO manifest checkpoint before ALTER.
5. ALTER remains unauthorized until the live backup/restore evidence is separately approved.

## 9. Final status

TASK: T10  
STAGE A: COMPLETED  
STAGE B: COMPLETED  
TZDATA INSTALLED: YES  
ZONEINFO VERIFICATION: PASS  
PIP CHECK: PASS  
GATE 2 PACKAGE HASH: UNCHANGED  
REAL DB MODIFIED: NO  
BACKUP RETRY: NOT AUTHORIZED  
ALTER EXECUTED: NO  
GATE 2 RETRY: NOT AUTHORIZED  
NEXT STEP: PO REVIEW STAGE B EVIDENCE / SEPARATE BACKUP RETRY DECISION

**HARD STOP — gửi báo cáo cho PO, không tự tiếp tục.**
