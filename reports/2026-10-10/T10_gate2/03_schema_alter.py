#!/usr/bin/env python3
"""DRAFT ONLY: apply the single PO-approved T10 ALTER transaction."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

APPROVED_DECISION_ID = "PO-DECISION-T10-REALDB-A1-GATE2-20261010"
EXPECTED_REPO = Path(r"C:\Projects\firefly-cinema")
EXPECTED_SOURCE = EXPECTED_REPO / "backend" / "firefly.db"
GATE1_COMMIT = "27701d1"
ALTER_SQL = "ALTER TABLE comments ADD COLUMN model_version VARCHAR(100);"
EXPECTED_BRANCH = "task/T10-gan-model-B"
PACKAGE_FILES = (
    "01_preflight.ps1", "02_fresh_backup.py", "03_schema_alter.py",
    "04_postverify.py", "05_clone_smoke.py", "T10_GATE2_EXECUTION_PACKAGE_DRAFT.md",
)
APPLICATION_STOP_RECHECK = r'''
$ErrorActionPreference = 'Stop'
$operatorPid = [int]$env:T10_OPERATOR_PID
$operatorCreationUtc = $env:T10_OPERATOR_CREATION_UTC
$operatorExeSha256 = $env:T10_OPERATOR_EXE_SHA256
$currentPythonPid = [int]$env:T10_CURRENT_PYTHON_PID
$expectedVenvPython = $env:T10_EXPECTED_VENV_PYTHON
$expectedScript = $env:T10_EXPECTED_ALTER_SCRIPT
$source = 'C:\Projects\firefly-cinema\backend\firefly.db'
$all = @(Get-CimInstance Win32_Process -ErrorAction Stop)
$recheck = $all | Where-Object { $_.ProcessId -eq $PID } | Select-Object -First 1
$python = $all | Where-Object { $_.ProcessId -eq $currentPythonPid } | Select-Object -First 1
$operator = $all | Where-Object { $_.ProcessId -eq $operatorPid } | Select-Object -First 1
if ($null -eq $recheck -or $null -eq $python -or $null -eq $operator) { throw 'Operator process tree is incomplete.' }
if ([int]$recheck.ParentProcessId -ne $currentPythonPid) { throw 'Recheck PowerShell is not a direct child of the ALTER Python process.' }
if ($python.Name -notmatch '^python(w|3)?(\.exe)?$') { throw 'Declared ALTER process is not Python.' }
if ($operator.Name -notmatch '^(pwsh|powershell)(\.exe)?$') { throw 'Declared operator PID is not PowerShell.' }
if ([string]::IsNullOrWhiteSpace($operator.ExecutablePath)) { throw 'Cannot inspect operator shell executable.' }
$actualCreation = ([datetime]$operator.CreationDate).ToUniversalTime().ToString('o')
if ($actualCreation -cne $operatorCreationUtc) { throw 'Operator shell creation time mismatch.' }
$actualOperatorHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $operator.ExecutablePath).Hash
if ($actualOperatorHash -cne $operatorExeSha256) { throw 'Operator shell executable hash mismatch.' }
if ([string]::IsNullOrWhiteSpace($python.CommandLine) -or
    $python.CommandLine.IndexOf($expectedScript, [System.StringComparison]::OrdinalIgnoreCase) -lt 0) {
    throw 'ALTER Python process command line does not identify the exact reviewed script.'
}
$allowed = [System.Collections.Generic.HashSet[int]]::new()
[void]$allowed.Add([int]$PID)
[void]$allowed.Add($currentPythonPid)
[void]$allowed.Add($operatorPid)
$pythonParent = $all | Where-Object { $_.ProcessId -eq $python.ParentProcessId } | Select-Object -First 1
if ([int]$python.ParentProcessId -ne $operatorPid) {
    if ($null -eq $pythonParent) { throw 'Python launcher process is missing.' }
    if ([int]$pythonParent.ParentProcessId -ne $operatorPid) { throw 'Python process is not in the verified operator chain.' }
    if ([string]::IsNullOrWhiteSpace($pythonParent.ExecutablePath)) { throw 'Cannot inspect Python launcher executable.' }
    $launcherPath = [System.IO.Path]::GetFullPath($pythonParent.ExecutablePath)
    if (-not [string]::Equals($launcherPath, [System.IO.Path]::GetFullPath($expectedVenvPython), [System.StringComparison]::OrdinalIgnoreCase)) { throw 'Unexpected Python launcher in operator chain.' }
    if ($pythonParent.Name -notmatch '^python(w|3)?(\.exe)?$') { throw 'Unexpected launcher process type.' }
    [void]$allowed.Add([int]$pythonParent.ProcessId)
}
$relevant = '^(python|pythonw|python3|uvicorn|sqlite|sqlite3|pwsh|powershell|cmd)(\.exe)?$'
$uninspectable = @($all | Where-Object {
    -not $allowed.Contains([int]$_.ProcessId) -and
    $_.Name -match $relevant -and [string]::IsNullOrWhiteSpace($_.CommandLine)
})
if ($uninspectable.Count -gt 0) { throw 'Relevant processes cannot be inspected.' }
$writers = @($all | Where-Object {
    if ($allowed.Contains([int]$_.ProcessId) -or $_.Name -notmatch $relevant) { return $false }
    $cmd = [string]$_.CommandLine
    $exe = [string]$_.ExecutablePath
    return ($_.Name -match '^sqlite3?(\.exe)?$' -or
        $exe.StartsWith('C:\Projects\firefly-cinema\backend\venv\', [System.StringComparison]::OrdinalIgnoreCase) -or
        $cmd -match 'C:\\Projects\\firefly-cinema|firefly-cinema|backend[\\/]firefly\.db|app\.main|uvicorn')
})
if ($writers.Count -gt 0) { throw 'Potential database writer process detected.' }
$listeners = @(Get-NetTCPConnection -State Listen -ErrorAction Stop)
$unsafeListeners = @($listeners | Where-Object {
    $owner = $_.OwningProcess
    $proc = $all | Where-Object { $_.ProcessId -eq $owner } | Select-Object -First 1
    $_.LocalPort -in @(8000, 8001, 8011, 18110) -or
    ($null -ne $proc -and -not $allowed.Contains([int]$proc.ProcessId) -and $proc.Name -match '^(python|pythonw|python3|uvicorn)(\.exe)?$')
})
if ($unsafeListeners.Count -gt 0) { throw 'Potential backend listener detected.' }
foreach ($sidecar in @("$source-wal", "$source-shm", "$source-journal")) {
    if (Test-Path -LiteralPath $sidecar) { throw "SQLite sidecar detected: $sidecar" }
}
$probe = [System.IO.File]::Open($source, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::None)
try { } finally { $probe.Close(); $probe.Dispose() }
'''


def hard_stop(message: str) -> "NoReturn":
    raise RuntimeError(f"HARD STOP: {message}")


def load_backup_helpers():
    helper_path = Path(__file__).with_name("02_fresh_backup.py")
    spec = importlib.util.spec_from_file_location("t10_backup_helpers", helper_path)
    if spec is None or spec.loader is None:
        hard_stop("cannot load reviewed backup helper module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def independent_package_hashes() -> tuple[dict[str, str], str]:
    package_dir = Path(__file__).resolve().parent
    values = {name: sha256_file(package_dir / name) for name in PACKAGE_FILES}
    canonical = json.dumps(values, sort_keys=True, separators=(",", ":")).encode("ascii")
    return values, hashlib.sha256(canonical).hexdigest().upper()


def git_output(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(EXPECTED_REPO), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def require_authorization(value: str) -> None:
    if APPROVED_DECISION_ID == "PENDING_PO_GATE2":
        hard_stop("source package has no PO-approved Gate 2 Decision ID")
    if value != APPROVED_DECISION_ID:
        hard_stop("Decision ID does not match the PO-approved source package")


def load_manifest(path: Path, expected_sha: str, backup_root: Path) -> dict:
    if not path.is_file():
        hard_stop(f"manifest not found: {path}")
    actual_sha = sha256_file(path)
    if actual_sha != expected_sha.upper():
        hard_stop(f"manifest SHA-256 mismatch: expected {expected_sha}, got {actual_sha}")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if backup_root not in path.resolve().parents or path.name != "manifest.json":
        hard_stop("manifest is outside the allowed backup root")
    if not path.parent.name.startswith("gate2_"):
        hard_stop("manifest is not from a fresh Gate 2 backup directory")
    if manifest.get("manifest_format") != "T10_GATE2_A1_FRESH_BACKUP_V1":
        hard_stop("manifest format is not the fresh-backup format")
    if manifest.get("fresh_backup_id") != path.parent.name:
        hard_stop("fresh backup ID does not match manifest directory")
    if manifest.get("package_status") != "GATE2_AUTHORIZED_AT_EXECUTION":
        hard_stop("manifest package status is invalid")
    if manifest.get("decision_id") != APPROVED_DECISION_ID:
        hard_stop("manifest Decision ID does not match approved Gate 2 Decision ID")
    backup = Path(manifest["backup"]["path"])
    restore = Path(manifest["restore_validation"]["path"])
    if backup.resolve() != path.parent / "firefly_online_backup.db":
        hard_stop("backup path is not the exact fresh-backup artifact")
    if restore.resolve() != path.parent / "restore_validation" / "firefly_restored.db":
        hard_stop("restore validation path is not inside the fresh-backup directory")
    if not backup.is_file() or sha256_file(backup) != manifest["backup"]["sha256"]:
        hard_stop("validated backup is missing or its SHA-256 changed")
    if not restore.is_file() or sha256_file(restore) != manifest["restore_validation"]["sha256"]:
        hard_stop("restore validation clone is missing or its SHA-256 changed")
    sidecar = path.parent / "manifest.sha256"
    expected_sidecar = f"{actual_sha}  manifest.json\n"
    if not sidecar.is_file() or sidecar.read_text(encoding="ascii") != expected_sidecar:
        hard_stop("manifest.sha256 sidecar is missing or does not match")
    return manifest


def recheck_application_stopped(args: argparse.Namespace) -> None:
    env = os.environ.copy()
    env["T10_OPERATOR_PID"] = str(args.operator_shell_pid)
    env["T10_OPERATOR_CREATION_UTC"] = args.operator_shell_creation_time_utc
    env["T10_OPERATOR_EXE_SHA256"] = args.operator_shell_exe_sha256.upper()
    env["T10_CURRENT_PYTHON_PID"] = str(os.getpid())
    env["T10_EXPECTED_VENV_PYTHON"] = str(EXPECTED_REPO / "backend" / "venv" / "Scripts" / "python.exe")
    env["T10_EXPECTED_ALTER_SCRIPT"] = str(Path(__file__).resolve())
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", APPLICATION_STOP_RECHECK],
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        hard_stop(f"application-stop recheck failed: {detail}")


def ensure_only_allowed_schema_change(before: dict, after: dict, conn: sqlite3.Connection, helpers) -> None:
    if after["integrity_check"] != ["ok"] or after["foreign_key_check"]:
        hard_stop("integrity or foreign-key validation failed before COMMIT")
    if after["user_version"] != before["user_version"]:
        hard_stop("user_version changed unexpectedly")
    for table in sorted(helpers.EXPECTED_TABLES - {"comments"}):
        if after["tables"][table] != before["tables"][table]:
            hard_stop(f"table changed unexpectedly: {table}")

    old_comments = before["tables"]["comments"]
    new_comments = after["tables"]["comments"]
    old_column_names = [row[1] for row in old_comments["columns"]]
    expected_new_column = [len(old_comments["columns"]), "model_version", "VARCHAR(100)", 0, None, 0]
    if new_comments["columns"] != old_comments["columns"] + [expected_new_column]:
        hard_stop(f"comments column definition differs from the one allowed: {new_comments['columns']}")
    if new_comments["count"] != old_comments["count"]:
        hard_stop("comments row count changed")
    if new_comments["foreign_keys"] != old_comments["foreign_keys"]:
        hard_stop("comments foreign keys changed")
    if new_comments["indexes"] != old_comments["indexes"]:
        hard_stop("comments indexes changed")
    original_fingerprint = helpers.table_fingerprint(conn, "comments", old_column_names)
    if original_fingerprint != old_comments["fingerprint"]:
        hard_stop("original comments data changed")
    non_null = conn.execute(
        "SELECT COUNT(*) FROM comments WHERE model_version IS NOT NULL"
    ).fetchone()[0]
    if non_null != 0:
        hard_stop("existing comments do not all have model_version=NULL")

    old_schema = {tuple(row[:3]): row[3] for row in before["schema_sql"]}
    new_schema = {tuple(row[:3]): row[3] for row in after["schema_sql"]}
    keys = set(old_schema) | set(new_schema)
    changed = {key for key in keys if old_schema.get(key) != new_schema.get(key)}
    if changed != {("table", "comments", "comments")}:
        hard_stop(f"unexpected schema objects changed: {sorted(changed)}")
    old_comments_sql = old_schema[("table", "comments", "comments")]
    new_comments_sql = new_schema[("table", "comments", "comments")]
    if not old_comments_sql or not new_comments_sql:
        hard_stop("comments CREATE TABLE SQL is missing")
    if "human_label IN (0, 1) OR human_label IS NULL" not in new_comments_sql:
        hard_stop("comments check constraint was not preserved")
    if "model_version VARCHAR(100)" not in new_comments_sql:
        hard_stop("comments CREATE TABLE SQL does not contain the approved new column")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision-id", required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--approved-package-hash-set-sha256", required=True)
    parser.add_argument("--supervisor-confirmation", required=True)
    parser.add_argument("--operator-shell-pid", required=True, type=int)
    parser.add_argument("--operator-shell-creation-time-utc", required=True)
    parser.add_argument("--operator-shell-exe-sha256", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    require_authorization(args.decision_id)
    if args.supervisor_confirmation != "APPLICATION_WRITERS_STOPPED_AND_MANIFEST_REVIEWED":
        hard_stop("missing exact supervisor confirmation for stopped writers and reviewed manifest")
    approved_hash_set = args.approved_package_hash_set_sha256.upper()
    if approved_hash_set == "PENDING_PO_GATE2" or len(approved_hash_set) != 64 or any(
        char not in "0123456789ABCDEF" for char in approved_hash_set
    ):
        hard_stop("PO-approved package hash-set SHA-256 is missing or invalid")
    current_package_files, current_package_hash_set = independent_package_hashes()
    if current_package_hash_set != approved_hash_set:
        hard_stop("current package differs from the exact package hash-set approved by PO")
    helpers = load_backup_helpers()
    if helpers.APPROVED_DECISION_ID != APPROVED_DECISION_ID:
        hard_stop("Decision ID constants differ between backup and ALTER scripts")
    helper_package_files, helper_package_hash_set = helpers.package_hashes()
    if helper_package_files != current_package_files or helper_package_hash_set != current_package_hash_set:
        hard_stop("verified helper reports package hashes inconsistent with independent verification")
    source = EXPECTED_SOURCE.resolve(strict=True)
    if source != EXPECTED_SOURCE or source.is_symlink():
        hard_stop(f"unexpected or linked source path: {source}")
    if subprocess.run(
        ["git", "-C", str(EXPECTED_REPO), "merge-base", "--is-ancestor", GATE1_COMMIT, "HEAD"]
    ).returncode != 0:
        hard_stop(f"Gate 1 commit {GATE1_COMMIT} is not an ancestor of HEAD")
    if git_output("branch", "--show-current") != EXPECTED_BRANCH:
        hard_stop(f"expected branch {EXPECTED_BRANCH}")
    if git_output("status", "--porcelain=v1", "--untracked-files=all"):
        hard_stop("repository working tree is not clean immediately before ALTER")
    manifest = load_manifest(
        args.manifest.resolve(strict=True), args.manifest_sha256, helpers.BACKUP_ROOT.resolve()
    )
    if manifest["source"]["path"] != str(source):
        hard_stop("manifest source path differs from the real database path")
    if manifest["git_head"] != git_output("rev-parse", "HEAD"):
        hard_stop("Git HEAD changed after fresh backup")
    if manifest.get("package_files_sha256") != current_package_files:
        hard_stop("package file hashes differ from the fresh-backup manifest")
    if manifest.get("package_hash_set_sha256") != current_package_hash_set:
        hard_stop("package hash-set differs from the fresh-backup manifest")
    current_sha = sha256_file(source)
    if current_sha != manifest["source"]["sha256_after"]:
        hard_stop("source database changed after fresh backup")
    recheck_application_stopped(args)
    if git_output("branch", "--show-current") != EXPECTED_BRANCH or git_output(
        "status", "--porcelain=v1", "--untracked-files=all"
    ):
        hard_stop("branch or working tree changed during final application-stop recheck")
    if sha256_file(source) != manifest["source"]["sha256_after"]:
        hard_stop("source database changed during final application-stop recheck")

    uri = source.as_uri() + "?mode=rw"
    conn = sqlite3.connect(uri, uri=True, timeout=5, isolation_level=None)
    committed = False
    try:
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA foreign_keys=ON")
        if conn.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
            hard_stop("foreign key enforcement could not be enabled")
        conn.execute("BEGIN EXCLUSIVE")
        before = helpers.snapshot(conn)
        helpers.validate_snapshot("source inside ALTER transaction", before)
        if before != manifest["database"]:
            hard_stop("schema, counts, metadata, or fingerprints differ from reviewed manifest")
        columns = [row[1] for row in before["tables"]["comments"]["columns"]]
        if "model_version" in columns:
            hard_stop("comments.model_version already exists")

        conn.execute(ALTER_SQL)

        after = helpers.snapshot(conn)
        ensure_only_allowed_schema_change(before, after, conn, helpers)
        conn.commit()
        committed = True
    except Exception:
        if not committed:
            conn.rollback()
        raise
    finally:
        conn.close()

    print("ALTER_COMMITTED=YES")
    print(f"ALTER_SQL={ALTER_SQL}")
    print(f"APPROVED_PACKAGE_HASH_SET_SHA256={current_package_hash_set}")
    print("NEXT_REQUIRED_STEP=04_postverify.py")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        print("No automatic restore was attempted.", file=sys.stderr)
        raise SystemExit(1)
