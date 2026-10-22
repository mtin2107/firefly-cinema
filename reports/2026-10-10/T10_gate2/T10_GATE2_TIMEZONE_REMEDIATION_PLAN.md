# T10 Gate 2 A1 — Timezone Remediation Plan

> **PLANNING ONLY — DO NOT RUN THESE COMMANDS WITHOUT NEW PO APPROVAL**  
> **BACKUP RETRY NOT AUTHORIZED — ALTER NOT AUTHORIZED**

## 1. Scope and evidence reviewed

- Reviewed `T10_GATE2_EXECUTION_EVIDENCE_REPORT.md`.
- Reviewed the complete `ZoneInfo` usage in the immutable `02_fresh_backup.py`.
- Exact runtime targeted by the runbook: `C:\Projects\firefly-cinema\backend\venv\Scripts\python.exe`.
- Venv metadata, read without executing Python:
  - Python `3.13.2`;
  - base interpreter `C:\Users\lemin\AppData\Local\Programs\Python\Python313\python.exe`;
  - `include-system-site-packages = false`;
  - pip metadata `24.3.1`;
  - no `tzdata` package or `tzdata-*.dist-info` directory in this venv.
- No repository dependency file inspected declares `tzdata`.
- No script 01–05, Python interpreter, pip command, SQLite connection or backup retry was run during this planning pass.

## 2. Probable root cause

`02_fresh_backup.py` imports the standard-library `zoneinfo.ZoneInfo` and resolves the IANA key twice:

- line 207: `ZoneInfo("Asia/Ho_Chi_Minh")` for the backup directory timestamp;
- line 258: the same key for manifest `created_at`.

On Windows, Python normally cannot rely on a system IANA timezone database. `zoneinfo` then falls back to the first-party Python `tzdata` package when installed. The exact venv is isolated from system site-packages and contains no `tzdata`, which is consistent with the runtime exception:

```text
No time zone found with key Asia/Ho_Chi_Minh
```

Most likely cause: the exact backend venv has neither usable system TZif data nor the `tzdata` fallback package.

Less likely causes to exclude during the approved verification phase:

- a custom `PYTHONTZPATH` overriding normal discovery;
- a corrupt or incomplete `tzdata` installation not visible from the directory-level check;
- pip using a different interpreter than the runbook venv;
- security software blocking access to installed package resources.

The failure occurred before `backup_dir.mkdir`, so the remediation does not require cleanup of a failed `gate2_*` directory.

## 3. Recommended minimal remediation

Install one pinned `tzdata` wheel into the **exact runbook venv only**. Do not edit requirements files, repository source, the six execution-package files or the backup script.

For reproducibility and supply-chain review:

1. PO selects an exact `tzdata` version.
2. Download exactly one universal wheel into an evidence/wheelhouse directory outside Git.
3. Calculate and record the wheel SHA-256.
4. Stop for PO confirmation of the version and wheel hash.
5. Install offline from that wheel into the exact venv with `--no-deps --no-index`.
6. Verify package metadata and `ZoneInfo("Asia/Ho_Chi_Minh")` without touching SQLite.

The report intentionally does not invent a version or wheel hash. Those two values must be established and approved externally before installation.

## 4. Proposed commands — not executed

All blocks in this section are **draft commands for a later PO-authorized remediation session**. They were not run while producing this plan.

### 4.1. Session constants and fail-closed placeholders

```powershell
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Assert-ApprovedValue([string]$Name, [string]$Value) {
    if ([string]::IsNullOrWhiteSpace($Value) -or $Value.StartsWith('<')) {
        throw "HARD STOP: $Name has not been approved by PO."
    }
}

$Python = 'C:\Projects\firefly-cinema\backend\venv\Scripts\python.exe'
$Wheelhouse = 'C:\Projects\T10_GATE2_TZDATA_WHEELHOUSE_20261010'
$TzdataVersion = '<PO_APPROVED_TZDATA_VERSION>'
$TzdataWheelSha256 = '<PO_APPROVED_TZDATA_WHEEL_SHA256>'

Assert-ApprovedValue 'TzdataVersion' $TzdataVersion
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw 'HARD STOP: exact runbook Python executable is missing.'
}
```

### 4.2. Read-only interpreter and current-state checks

These commands do not connect to SQLite:

```powershell
& $Python -c "import os,sys,sysconfig; print('EXECUTABLE='+sys.executable); print('VERSION='+sys.version); print('PURELIB='+sysconfig.get_paths()['purelib']); print('PYTHONTZPATH='+str(os.environ.get('PYTHONTZPATH')))"
if ($LASTEXITCODE -ne 0) { throw 'HARD STOP: exact venv identity check failed.' }

& $Python -m pip --version
if ($LASTEXITCODE -ne 0) { throw 'HARD STOP: pip is unavailable in exact venv.' }

& $Python -m pip show tzdata
$TzdataShowBeforeExit = $LASTEXITCODE
if ($TzdataShowBeforeExit -eq 0) {
    throw 'HARD STOP: tzdata is already installed; do not overwrite without PO review.'
}

& $Python -c "from zoneinfo import ZoneInfo, ZoneInfoNotFoundError; import sys; key='Asia/Ho_Chi_Minh';
try:
    ZoneInfo(key)
except ZoneInfoNotFoundError:
    print('ZONEINFO_PRECHECK=EXPECTED_MISSING'); sys.exit(0)
print('ZONEINFO_PRECHECK=ALREADY_AVAILABLE'); sys.exit(2)"
if ($LASTEXITCODE -ne 0) { throw 'HARD STOP: pre-install state differs from approved expectation.' }
```

Expected approved pre-state: exact executable is the backend venv, `pip show tzdata` reports absent, and the IANA key is unavailable. Any different result requires PO review instead of installation.

### 4.3. Wheel acquisition and hash checkpoint

This phase writes only to the external wheelhouse and accesses the configured package index. It requires explicit PO approval before use.

```powershell
Assert-ApprovedValue 'TzdataVersion' $TzdataVersion
if (Test-Path -LiteralPath $Wheelhouse) {
    throw 'HARD STOP: wheelhouse already exists; do not reuse or overwrite it.'
}
New-Item -ItemType Directory -Path $Wheelhouse -ErrorAction Stop | Out-Null

& $Python -m pip download --disable-pip-version-check --only-binary=:all: --no-deps --dest $Wheelhouse "tzdata==$TzdataVersion"
if ($LASTEXITCODE -ne 0) { throw 'HARD STOP: tzdata wheel download failed.' }

$Wheels = @(Get-ChildItem -LiteralPath $Wheelhouse -File -Filter 'tzdata-*.whl')
if ($Wheels.Count -ne 1) { throw 'HARD STOP: expected exactly one tzdata wheel.' }
$ObservedWheelSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $Wheels[0].FullName).Hash
Write-Output "TZDATA_WHEEL=$($Wheels[0].FullName)"
Write-Output "TZDATA_WHEEL_SHA256=$ObservedWheelSha256"
Write-Output 'HARD STOP: obtain PO approval for exact version and wheel SHA-256 before installation.'
```

Do not continue directly from download to install. The printed wheel path/hash is a mandatory approval checkpoint.

### 4.4. Exact offline installation after separate hash approval

```powershell
Assert-ApprovedValue 'TzdataVersion' $TzdataVersion
Assert-ApprovedValue 'TzdataWheelSha256' $TzdataWheelSha256
$Wheels = @(Get-ChildItem -LiteralPath $Wheelhouse -File -Filter 'tzdata-*.whl')
if ($Wheels.Count -ne 1) { throw 'HARD STOP: expected exactly one approved tzdata wheel.' }
$ObservedWheelSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $Wheels[0].FullName).Hash
if ($ObservedWheelSha256 -ne $TzdataWheelSha256.ToUpperInvariant()) {
    throw 'HARD STOP: tzdata wheel SHA-256 differs from PO approval.'
}

& $Python -m pip install --disable-pip-version-check --no-index --no-deps $Wheels[0].FullName
if ($LASTEXITCODE -ne 0) { throw 'HARD STOP: tzdata installation failed.' }
```

This is the minimal venv mutation. It installs only the approved wheel and resolves no transitive dependencies.

### 4.5. Post-install verification without SQLite

```powershell
& $Python -c "import importlib.metadata,sys; v=importlib.metadata.version('tzdata'); print('TZDATA_VERSION='+v); sys.exit(0 if v=='$TzdataVersion' else 2)"
if ($LASTEXITCODE -ne 0) { throw 'HARD STOP: installed tzdata version mismatch.' }

& $Python -c "from datetime import datetime; from zoneinfo import ZoneInfo; z=ZoneInfo('Asia/Ho_Chi_Minh'); now=datetime.now(z); print('ZONEINFO_KEY='+z.key); print('ZONEINFO_TIMESTAMP='+now.isoformat()); print('ZONEINFO_STAMP='+now.strftime('%Y%m%d_%H%M%S_%f%z'))"
if ($LASTEXITCODE -ne 0) { throw 'HARD STOP: Asia/Ho_Chi_Minh verification failed.' }

& $Python -m pip check
if ($LASTEXITCODE -ne 0) { throw 'HARD STOP: venv dependency check failed after tzdata install.' }
```

Required evidence: exact Python path/version, exact installed tzdata version, approved wheel hash, successful timezone key/timestamp/stamp, and `pip check` PASS. Do not run any Gate 2 script as part of this verification.

## 5. Environment impact

Expected changes are limited to the backend venv and external wheelhouse:

- new `tzdata` package directory under `backend\venv\Lib\site-packages`;
- new `tzdata-<version>.dist-info` metadata;
- possible pip cache entries outside the repository;
- one downloaded wheel and hash evidence in the external wheelhouse;
- possible Python bytecode cache generated by the verification import.

Expected non-changes:

- no modification to scripts 01–05 or the runbook;
- no modification to repository dependency files or production source;
- no Git commit;
- no SQLite connection or database write during remediation verification;
- no backup/restore/ALTER/backend/API activity.

Operational consideration: the venv is under the repository directory but is an environment artifact, not part of the immutable six-file package. Git status must still be checked after remediation; any tracked/unexpected repository diff is a HARD STOP.

## 6. Rollback plan — requires PO approval before use

If the approved installation must be reverted:

```powershell
$Python = 'C:\Projects\firefly-cinema\backend\venv\Scripts\python.exe'
& $Python -m pip uninstall --yes tzdata
if ($LASTEXITCODE -ne 0) { throw 'HARD STOP: tzdata uninstall failed.' }

& $Python -m pip show tzdata
if ($LASTEXITCODE -eq 0) { throw 'HARD STOP: tzdata remains installed after rollback.' }

& $Python -m pip check
if ($LASTEXITCODE -ne 0) { throw 'HARD STOP: venv dependency check failed after rollback.' }
```

Then verify read-only that `tzdata`/`tzdata-*.dist-info` are absent from the exact venv and record Git status. Preserve the downloaded wheel/hash evidence unless PO separately authorizes deletion. Do not delete or recreate the whole venv automatically.

Rollback limitation: Windows may have gained timezone availability through another mechanism after the original failure. Therefore inability/success of `ZoneInfo` after uninstall is diagnostic evidence, not the sole rollback criterion; package metadata and venv filesystem state are authoritative.

## 7. Immutable execution-package preservation

The six files remain at the PO-approved hashes:

| File | SHA-256 |
|---|---|
| `01_preflight.ps1` | `56CAB1EE118FF9EEB54D844480CB7F0C080AC0A282AA1C69F187A56E61943F1F` |
| `02_fresh_backup.py` | `F81496DBCA717C892EAA0BC11BAF10C63E7DA7C537F2660E3ACA3ACB1DD10BC9` |
| `03_schema_alter.py` | `6F812ECE3266DC8EDFC4473CED41FDA8B14F180E872C39985FC8CB80B90D4A47` |
| `04_postverify.py` | `E957A2D229DA336839CA48A38608870F572673E802AD01772F7B55E6A2C2303C` |
| `05_clone_smoke.py` | `3624F17763A87E41717088F3E09A211B9C245B134B497129FC1082BE69D0D0B0` |
| `T10_GATE2_EXECUTION_PACKAGE_DRAFT.md` | `FDCDCCA403654D601A13653B0493C3E46B190B389472BC3C75DD101FE97C7044` |

Canonical hash-set: `ABDC69930EC41034B5A7ED8C566FEF945D11843D60F9413BE0C2192CD2C9899A`.

This planning report is outside the six-file hash-set. After any separately authorized environment remediation and immediately before retry, recompute and compare all six hashes against the external PO decision. Any mismatch is a HARD STOP.

## 8. Proposed retry procedure — not authorized now

Only after PO approves remediation evidence **and separately authorizes backup retry**:

1. Confirm no prior manifest/backup is reused; the failed attempt created no `gate2_*` directory.
2. Confirm backend and all possible DB writers are stopped under live PO supervision.
3. Start a **new** persistent Windows PowerShell 5.1 PTY. Do not reuse the closed PID/session from the failed attempt.
4. Assign the same external Decision ID, all six PO-approved file hashes and canonical hash-set in the new session.
5. Run the complete `PACKAGE_INTEGRITY_GATE` from runbook §4.2 against `C:\Projects\T10_GATE2_A1_FINAL_CANDIDATE_20261010`; require PASS before any script.
6. Run exact preflight §4.3; require PASS and a newly verified operator PID/creation-time/executable identity.
7. Run exact fresh-backup command §4.4; require `BACKUP_VALIDATED`, `MANIFEST`, `MANIFEST_SHA256` and `OPERATOR_CHECKPOINT_REQUIRED=YES`.
8. Assign the newly printed manifest path/hash and perform all read-only manifest/backup/restore checks in §4.5.
9. Confirm source SHA before/after matches, backup and restore hashes match manifest, snapshots/counts/fingerprints/integrity/FK checks pass, package hash-set matches external approval, and writers remain stopped.
10. **HARD STOP at runbook §4.6.** Present manifest, source/backup/restore hashes and preservation evidence to PO.
11. Do not run `03_schema_alter.py` unless PO provides a separate live-checkpoint confirmation for that exact retry.

Any timezone verification failure, dependency inconsistency, hash mismatch, changed repository, process/lock failure or backup discrepancy causes HARD STOP. Never patch the immutable package, reuse stale evidence, auto-restore or continue to ALTER.

## 9. Approval items required from PO

Before environment mutation:

1. exact `tzdata` version;
2. authorization to create the external wheelhouse and download one wheel;
3. accepted package index/source;
4. mandatory wheel SHA checkpoint;
5. authorization for exact offline install commands into the backend venv;
6. rollback authorization boundary.

After remediation verification, a separate decision is still required to authorize backup retry from a new session.

## 10. Status

TIMEZONE REMEDIATION: PLANNED ONLY  
ENVIRONMENT MODIFIED: NO  
BACKUP RETRY: NOT AUTHORIZED  
ALTER EXECUTED: NO  
NEXT STEP: PO REMEDIATION APPROVAL

**HARD STOP — chờ PO.**
