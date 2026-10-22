# T10 Gate 2 A1 — tzdata Stage A Evidence Report

> **PO AUTHORITY: STAGE A ONLY**  
> **WHEEL ACQUISITION AND SHA-256 VERIFICATION — NO INSTALLATION**

## 1. Authority and scope

- Task: T10.
- Authorized action: read-only venv/package/Git prechecks, download exactly `tzdata==2026.5` from official PyPI into the external wheelhouse, and verify SHA-256.
- Python target: `C:\Projects\firefly-cinema\backend\venv\Scripts\python.exe`.
- Wheelhouse: `C:\Projects\T10_GATE2_TZDATA_WHEELHOUSE_20261010`.
- PyPI index: `https://pypi.org/simple`.
- Reference: `https://pypi.org/project/tzdata/2026.5/`.
- Stage B installation, backup retry and Gate 2 retry were not authorized.
- This report is outside the production repository and outside the six-file execution package hash-set.

## 2. Read-only prechecks

| Check | Observed result |
|---|---|
| Exact Python executable | `C:\Projects\firefly-cinema\backend\venv\Scripts\python.exe` |
| Python version | `3.13.2` — PASS |
| Venv purelib | `C:\Projects\firefly-cinema\backend\venv\Lib\site-packages` |
| Exact pip binding | `pip 24.3.1` from the same venv purelib — PASS |
| `tzdata` package installed | NO |
| Existing `tzdata*` entries in venv | 0 |
| `PYTHONTZPATH` | UNSET |
| Wheelhouse before acquisition | DID NOT EXIST |
| Git branch | `task/T10-gan-model-B` |
| Git HEAD | `27701d19a150117919e0172f2386d819a7b9d369` |
| Git worktree | CLEAN |
| Six-file package canonical hash-set | `ABDC69930EC41034B5A7ED8C566FEF945D11843D60F9413BE0C2192CD2C9899A` — PASS |

Audit note: two initial read-only checker attempts stopped on command-construction errors in the verifier itself (an over-escaped path literal, then an invalid PowerShell `IndexOf` overload). Both occurred before wheelhouse creation and made no environment/package/repository change. The corrected full fail-closed precheck then passed before download.

## 3. Authorized download

The exact venv executed `python -B -m pip download` with:

- `--isolated`;
- `--disable-pip-version-check`;
- `--no-cache-dir`;
- `--index-url https://pypi.org/simple`;
- `--only-binary=:all:`;
- `--no-deps`;
- exact requirement `tzdata==2026.5`;
- destination `C:\Projects\T10_GATE2_TZDATA_WHEELHOUSE_20261010`.

Pip reported `Successfully downloaded tzdata`. No `pip install` or `pip uninstall` command was run.

## 4. Wheel identity and mandatory hash verification

| Field | Value |
|---|---|
| Wheelhouse file count | `1` |
| Exact filename | `tzdata-2026.5-py2.py3-none-any.whl` |
| Exact wheel path | `C:\Projects\T10_GATE2_TZDATA_WHEELHOUSE_20261010\tzdata-2026.5-py2.py3-none-any.whl` |
| File size | `347996` bytes |
| Observed SHA-256 | `B683BD1B6659DDCD810FF02AD09BA821D4BF1065072805063EB35C49617905AC` |
| Official PyPI SHA-256 supplied by PO | `B683BD1B6659DDCD810FF02AD09BA821D4BF1065072805063EB35C49617905AC` |
| Exact executable comparison | PASS |
| Hash match | YES |

Runtime result markers:

```text
TZDATA_WHEEL_DOWNLOAD=PASS
TZDATA_VERSION=2026.5
TZDATA_WHEEL_SHA256=B683BD1B6659DDCD810FF02AD09BA821D4BF1065072805063EB35C49617905AC
WHEEL_HASH_MATCH=YES
PO_INSTALL_CHECKPOINT_REQUIRED=YES
```

The wheel was not renamed, edited, unpacked or imported.

## 5. Six-file Gate 2 package integrity

| File | SHA-256 |
|---|---|
| `01_preflight.ps1` | `56CAB1EE118FF9EEB54D844480CB7F0C080AC0A282AA1C69F187A56E61943F1F` |
| `02_fresh_backup.py` | `F81496DBCA717C892EAA0BC11BAF10C63E7DA7C537F2660E3ACA3ACB1DD10BC9` |
| `03_schema_alter.py` | `6F812ECE3266DC8EDFC4473CED41FDA8B14F180E872C39985FC8CB80B90D4A47` |
| `04_postverify.py` | `E957A2D229DA336839CA48A38608870F572673E802AD01772F7B55E6A2C2303C` |
| `05_clone_smoke.py` | `3624F17763A87E41717088F3E09A211B9C245B134B497129FC1082BE69D0D0B0` |
| `T10_GATE2_EXECUTION_PACKAGE_DRAFT.md` | `FDCDCCA403654D601A13653B0493C3E46B190B389472BC3C75DD101FE97C7044` |

Canonical package hash-set after download:

`ABDC69930EC41034B5A7ED8C566FEF945D11843D60F9413BE0C2192CD2C9899A`

Result: all six PO-authorized hashes and the canonical hash-set remain unchanged.

## 6. Post-download environment and Git checks

- `pip show tzdata`: package remains absent.
- Venv `site-packages`: no `tzdata*` entries.
- `PYTHONTZPATH`: remains unset.
- Environment package installed: NO.
- Git branch/HEAD: unchanged.
- Git worktree: CLEAN.
- Execution package: unchanged.

## 7. Actions performed

- Executed read-only Python/venv identity checks.
- Executed read-only `pip --version` and `pip show tzdata` checks.
- Read Git branch, HEAD and worktree status.
- Hashed the six execution-package files.
- Created the external wheelhouse.
- Downloaded exactly one approved wheel from the specified official PyPI index.
- Calculated and conditionally compared the wheel SHA-256 with the PO-supplied official value.
- Created this evidence report outside the repository.

## 8. Actions not performed

- No `pip install` or `pip uninstall`.
- No venv package modification.
- No requirements, source-code or execution-package modification.
- No Gate 2 script 01–05 invocation.
- No SQLite connection or database access.
- No backup creation or retry.
- No ALTER, restore, postverify, API smoke or backend startup.
- No credentials.
- No Git stage/commit/merge/tag and no T11 action.
- No Stage B or Gate 2 retry assertion.

## 9. Remaining blockers

1. PO must separately approve Stage B installation using this exact wheel path and SHA-256.
2. Stage B must verify the wheel hash again immediately before offline installation.
3. After installation, timezone resolution and venv integrity require separate verification without SQLite.
4. Backup retry remains separately unauthorized and, if later approved, must start from a new persistent PowerShell 5.1 session with package gate and preflight.
5. ALTER remains prohibited until a successful fresh backup/restore manifest reaches the separate live PO checkpoint.

## 10. Final status

TASK: T10  
STAGE A: COMPLETED  
WHEEL DOWNLOAD: PASS  
WHEEL HASH MATCH: YES  
ENVIRONMENT PACKAGE INSTALLED: NO  
REAL DB MODIFIED: NO  
BACKUP RETRY: NOT AUTHORIZED  
ALTER EXECUTED: NO  
GATE 2 RETRY: NOT AUTHORIZED  
NEXT STEP: PO STAGE B INSTALLATION DECISION

**HARD STOP — dừng và gửi báo cáo cho PO.**
