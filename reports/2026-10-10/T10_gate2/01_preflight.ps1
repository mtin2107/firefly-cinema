# DRAFT ONLY — GATE 2 NOT AUTHORIZED — DO NOT EXECUTE
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$DecisionId,
    [Parameter(Mandatory = $true)][string]$POStoppedConfirmation,
    [Parameter(Mandatory = $true)][int]$OperatorShellPid,
    [Parameter(Mandatory = $true)][string]$OperatorShellCreationTimeUtc,
    [Parameter(Mandatory = $true)][string]$OperatorShellExeSha256
)

$ErrorActionPreference = 'Stop'
$ApprovedDecisionId = 'PO-DECISION-T10-REALDB-A1-GATE2-20261010'
$ExpectedRepo = 'C:\Projects\firefly-cinema'
$ExpectedBranch = 'task/T10-gan-model-B'
$Gate1Commit = '27701d1'
$ExpectedPython = 'C:\Projects\firefly-cinema\backend\venv\Scripts\python.exe'
$ExpectedDatabase = 'C:\Projects\firefly-cinema\backend\firefly.db'

function Stop-Gate([string]$Message) {
    [Console]::Error.WriteLine("HARD STOP: $Message")
    exit 1
}

if ($ApprovedDecisionId -eq 'PENDING_PO_GATE2') {
    Stop-Gate 'Source package has no PO-approved Gate 2 Decision ID.'
}
if ($DecisionId -ne $ApprovedDecisionId) {
    Stop-Gate 'Decision ID does not match the PO-approved package.'
}
if ($POStoppedConfirmation -ne 'PO_CONFIRMS_BACKEND_AND_ALL_DB_WRITERS_STOPPED') {
    Stop-Gate 'Independent PO confirmation that backend and all DB writers are stopped is missing.'
}

$ResolvedRepo = (Resolve-Path -LiteralPath $ExpectedRepo).Path
if ($ResolvedRepo -cne $ExpectedRepo) {
    Stop-Gate "Repository path mismatch: $ResolvedRepo"
}
$Branch = (& git -C $ExpectedRepo branch --show-current).Trim()
if ($LASTEXITCODE -ne 0 -or $Branch -ne $ExpectedBranch) {
    Stop-Gate "Expected branch $ExpectedBranch, got $Branch"
}
& git -C $ExpectedRepo merge-base --is-ancestor $Gate1Commit HEAD
if ($LASTEXITCODE -ne 0) {
    Stop-Gate "$Gate1Commit is not an ancestor of HEAD."
}
$Head = (& git -C $ExpectedRepo rev-parse HEAD).Trim()
$GitStatus = @(& git -C $ExpectedRepo status --porcelain=v1 --untracked-files=all)
if ($LASTEXITCODE -ne 0 -or $GitStatus.Count -ne 0) {
    Stop-Gate "Working tree is not clean: $($GitStatus -join '; ')"
}
if (-not (Test-Path -LiteralPath $ExpectedPython -PathType Leaf)) {
    Stop-Gate "Python interpreter not found: $ExpectedPython"
}

$BackendDir = Join-Path $ExpectedRepo 'backend'
$EnvFile = Join-Path $BackendDir '.env'
$EnvValues = @{}
if (Test-Path -LiteralPath $EnvFile -PathType Leaf) {
    foreach ($Line in Get-Content -LiteralPath $EnvFile) {
        $Trimmed = $Line.Trim()
        if ($Trimmed -and -not $Trimmed.StartsWith('#') -and $Trimmed.Contains('=')) {
            $Pair = $Trimmed.Split('=', 2)
            if (-not $EnvValues.ContainsKey($Pair[0].Trim())) {
                $EnvValues[$Pair[0].Trim()] = $Pair[1].Trim()
            }
        }
    }
}
$DatabaseUrl = $env:DATABASE_URL
if ([string]::IsNullOrWhiteSpace($DatabaseUrl)) {
    $DatabaseUrl = if ($EnvValues.ContainsKey('DATABASE_URL')) { $EnvValues['DATABASE_URL'] } else { 'sqlite:///./firefly.db' }
}
if (-not $DatabaseUrl.StartsWith('sqlite:///')) {
    Stop-Gate "DATABASE_URL is not the expected SQLite form: $DatabaseUrl"
}
$DatabasePart = $DatabaseUrl.Substring('sqlite:///'.Length)
if ([System.IO.Path]::IsPathRooted($DatabasePart)) {
    $RuntimeDatabase = [System.IO.Path]::GetFullPath($DatabasePart)
} else {
    $RuntimeDatabase = [System.IO.Path]::GetFullPath((Join-Path $BackendDir $DatabasePart))
}
if ($RuntimeDatabase -cne $ExpectedDatabase) {
    Stop-Gate "Runtime DATABASE_URL resolves to $RuntimeDatabase, not $ExpectedDatabase"
}
$DatabaseItem = Get-Item -LiteralPath $ExpectedDatabase -Force
if ($DatabaseItem.PSIsContainer -or ($DatabaseItem.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
    Stop-Gate 'Database is a directory, symlink, junction, or other reparse point.'
}
if ($DatabaseItem.FullName -cne $ExpectedDatabase) {
    Stop-Gate "Database path mismatch: $($DatabaseItem.FullName)"
}

$ProcessCommand = Get-Command Get-CimInstance -ErrorAction SilentlyContinue
if ($null -eq $ProcessCommand) {
    Stop-Gate 'Get-CimInstance is unavailable; process inspection cannot be trusted.'
}
try {
    $AllProcesses = @(Get-CimInstance Win32_Process -ErrorAction Stop)
} catch {
    Stop-Gate "Cannot enumerate processes reliably: $($_.Exception.Message)"
}
$CurrentProcess = $AllProcesses | Where-Object { $_.ProcessId -eq $PID } | Select-Object -First 1
$OperatorProcess = $AllProcesses | Where-Object { $_.ProcessId -eq $OperatorShellPid } | Select-Object -First 1
if ($null -eq $CurrentProcess -or $null -eq $OperatorProcess) {
    Stop-Gate 'Current preflight process or declared operator shell process is missing.'
}
if ([int]$CurrentProcess.ParentProcessId -ne $OperatorShellPid) {
    Stop-Gate 'Preflight PowerShell is not a direct child of the declared persistent operator shell.'
}
if ($OperatorProcess.Name -notmatch '^(pwsh|powershell)(\.exe)?$') {
    Stop-Gate "Declared operator PID is not PowerShell: $($OperatorProcess.Name)"
}
if ([string]::IsNullOrWhiteSpace($OperatorProcess.ExecutablePath)) {
    Stop-Gate 'Cannot inspect the persistent operator shell executable path.'
}
$ActualOperatorCreationTimeUtc = ([datetime]$OperatorProcess.CreationDate).ToUniversalTime().ToString('o')
if ($ActualOperatorCreationTimeUtc -cne $OperatorShellCreationTimeUtc) {
    Stop-Gate 'Persistent operator shell creation time does not match the declared session identity.'
}
$ActualOperatorExeSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $OperatorProcess.ExecutablePath).Hash
if ($ActualOperatorExeSha256 -cne $OperatorShellExeSha256) {
    Stop-Gate 'Persistent operator shell executable hash does not match the declared session identity.'
}
$AllowedOperatorPids = @([int]$PID, [int]$OperatorShellPid)
$RelevantProcessPattern = '^(python|pythonw|python3|uvicorn|sqlite|sqlite3|pwsh|powershell|cmd)(\.exe)?$'
$Uninspectable = @($AllProcesses | Where-Object {
    $_.ProcessId -notin $AllowedOperatorPids -and $_.Name -match $RelevantProcessPattern -and
    [string]::IsNullOrWhiteSpace($_.CommandLine)
})
if ($Uninspectable.Count -gt 0) {
    Stop-Gate "Relevant processes cannot be inspected: $($Uninspectable.ProcessId -join ', ')"
}
$WriterProcesses = @($AllProcesses | Where-Object {
    if ($_.ProcessId -in $AllowedOperatorPids -or $_.Name -notmatch $RelevantProcessPattern) { return $false }
    $Command = [string]$_.CommandLine
    $Executable = [string]$_.ExecutablePath
    return (
        $_.Name -match '^sqlite3?(\.exe)?$' -or
        $Executable.StartsWith('C:\Projects\firefly-cinema\backend\venv\', [System.StringComparison]::OrdinalIgnoreCase) -or
        $Command -match 'C:\\Projects\\firefly-cinema|firefly-cinema|backend[\\/]firefly\.db|app\.main|uvicorn'
    )
})
if ($WriterProcesses.Count -gt 0) {
    $Descriptions = $WriterProcesses | ForEach-Object { "PID=$($_.ProcessId) NAME=$($_.Name) CMD=$($_.CommandLine)" }
    Stop-Gate "Potential database writer processes are running: $($Descriptions -join ' | ')"
}
$ListenerCommand = Get-Command Get-NetTCPConnection -ErrorAction SilentlyContinue
if ($null -eq $ListenerCommand) {
    Stop-Gate 'Get-NetTCPConnection is unavailable; listener inspection cannot be trusted.'
}
try {
    $AllListeners = @(Get-NetTCPConnection -State Listen -ErrorAction Stop)
} catch {
    Stop-Gate "Cannot enumerate TCP listeners reliably: $($_.Exception.Message)"
}
$BackendListeners = @($AllListeners | Where-Object {
    $Owner = $_.OwningProcess
    $OwnerProcess = $AllProcesses | Where-Object { $_.ProcessId -eq $Owner } | Select-Object -First 1
    $_.LocalPort -in @(8000, 8001, 8011, 18110) -or
    ($null -ne $OwnerProcess -and $OwnerProcess.Name -match '^(python|pythonw|python3|uvicorn)(\.exe)?$')
})
if ($BackendListeners.Count -gt 0) {
    Stop-Gate "Potential backend listener detected on any port: $($BackendListeners | ConvertTo-Json -Compress)"
}
foreach ($Sidecar in @("$ExpectedDatabase-wal", "$ExpectedDatabase-shm", "$ExpectedDatabase-journal")) {
    if (Test-Path -LiteralPath $Sidecar) {
        Stop-Gate "Unexpected SQLite sidecar exists: $Sidecar"
    }
}
try {
    $ExclusiveProbe = [System.IO.File]::Open(
        $ExpectedDatabase,
        [System.IO.FileMode]::Open,
        [System.IO.FileAccess]::Read,
        [System.IO.FileShare]::None
    )
    $ExclusiveProbe.Close()
    $ExclusiveProbe.Dispose()
} catch {
    Stop-Gate "Database file has an open handle or cannot be exclusively inspected: $($_.Exception.Message)"
}

$SchemaProbe = @'
import json, sqlite3, sys
from pathlib import Path

path = Path(r"C:\Projects\firefly-cinema\backend\firefly.db").resolve(strict=True)
expected = [
    "id", "movie_id", "user_id", "content", "is_negative", "negative_score",
    "model_name", "human_label", "reviewed_by", "reviewed_at", "hidden", "created_at",
]
conn = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=5)
try:
    conn.execute("PRAGMA query_only=ON")
    tables = {row[0] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )}
    required = {"users", "movies", "showtimes", "bookings", "booking_seats", "comments"}
    if tables != required:
        raise RuntimeError(f"expected exactly six tables {sorted(required)}, got {sorted(tables)}")
    columns = [row[1] for row in conn.execute("PRAGMA table_info(comments)")]
    if columns != expected:
        raise RuntimeError(f"unexpected pre-T10 comments columns: {columns}")
    if "model_version" in columns:
        raise RuntimeError("comments.model_version already exists")
    index_names = {
        row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'"
        )
    }
    expected_indexes = {
        "ix_users_email", "ix_showtimes_movie_id", "ix_showtimes_start_time",
        "ix_bookings_user_id", "ix_booking_seats_showtime_id", "ix_comments_movie_id",
    }
    if index_names != expected_indexes:
        raise RuntimeError(f"unexpected explicit indexes: {sorted(index_names)}")
    triggers = conn.execute("SELECT name FROM sqlite_master WHERE type='trigger'").fetchall()
    if triggers:
        raise RuntimeError(f"unexpected triggers: {triggers}")
    comments_sql = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='comments'"
    ).fetchone()[0]
    if "human_label IN (0, 1) OR human_label IS NULL" not in comments_sql:
        raise RuntimeError("comments human_label check constraint is missing")
    hidden = next(row for row in conn.execute("PRAGMA table_info(comments)") if row[1] == "hidden")
    if str(hidden[4]).strip("'\"") != "0":
        raise RuntimeError(f"comments.hidden default is not 0: {hidden[4]}")
    expected_fks = {
        "showtimes": {("movie_id", "movies", "id")},
        "bookings": {("user_id", "users", "id"), ("showtime_id", "showtimes", "id")},
        "booking_seats": {("booking_id", "bookings", "id"), ("showtime_id", "showtimes", "id")},
        "comments": {
            ("movie_id", "movies", "id"), ("user_id", "users", "id"),
            ("reviewed_by", "users", "id"),
        },
    }
    for table, wanted in expected_fks.items():
        actual = {(row[3], row[2], row[4]) for row in conn.execute(f"PRAGMA foreign_key_list({table})")}
        if actual != wanted:
            raise RuntimeError(f"unexpected foreign keys for {table}: {sorted(actual)}")
    integrity = [row[0] for row in conn.execute("PRAGMA integrity_check")]
    fk = conn.execute("PRAGMA foreign_key_check").fetchall()
    if integrity != ["ok"] or fk:
        raise RuntimeError(f"database checks failed: integrity={integrity}, fk={fk}")
    print(json.dumps({"tables": sorted(tables), "comments_columns": columns, "integrity": integrity, "fk_errors": len(fk)}))
finally:
    conn.close()
'@
$SchemaResult = $SchemaProbe | & $ExpectedPython -
if ($LASTEXITCODE -ne 0) {
    Stop-Gate 'Read-only schema probe failed.'
}

Write-Output "PREFLIGHT=PASS"
Write-Output "HEAD=$Head"
Write-Output "OPERATOR_SHELL_PID=$OperatorShellPid"
Write-Output "OPERATOR_SHELL_CREATION_UTC=$OperatorShellCreationTimeUtc"
Write-Output "OPERATOR_SHELL_EXE_SHA256=$OperatorShellExeSha256"
Write-Output "DATABASE_URL=$DatabaseUrl"
Write-Output "DATABASE_PATH=$RuntimeDatabase"
Write-Output "SCHEMA=$SchemaResult"
Write-Output 'NEXT_REQUIRED_STEP=02_fresh_backup.py'
exit 0
