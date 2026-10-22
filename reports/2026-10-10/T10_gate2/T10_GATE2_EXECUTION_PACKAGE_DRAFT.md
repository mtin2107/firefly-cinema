# T10 Gate 2 A1 — Execution Package Draft

> **DRAFT — GATE 2 NOT AUTHORIZED — DO NOT EXECUTE**

## 1. Authority boundary

- Task: T10 — Gắn PhoBERT B vào web.
- Gate 1 authority commit: `27701d1`.
- Operator dự kiến: Codex, dưới giám sát trực tiếp của PO.
- Gate 2 Decision ID: `PENDING_PO_GATE2`.
- Database duy nhất trong phạm vi: `C:\Projects\firefly-cinema\backend\firefly.db`.
- Schema change duy nhất: `ALTER TABLE comments ADD COLUMN model_version VARCHAR(100);`.
- Không Alembic, reset, DROP, DELETE, seed lại hoặc thay đổi dữ liệu gốc.

Gói này không cấp quyền chạy. Việc đặt biến môi trường, nhập chuỗi xác nhận hoặc sửa giá trị `PENDING_PO_GATE2` không thay thế quyết định PO. Sau khi PO ban hành Gate 2, Codex mới được điền cùng một Decision ID vào hằng `APPROVED_DECISION_ID` của `01_preflight.ps1`, `02_fresh_backup.py`, `03_schema_alter.py`, `04_postverify.py`, `05_clone_smoke.py`. PO phải review lại toàn bộ source đã điền và từng lệnh cuối cùng trước khi chạy.

**Execution model duy nhất cho pre-COMMIT:** Codex là operator và phải dùng một Windows PowerShell 5.1 session bền trong cùng PTY từ package-integrity gate, qua preflight và backup, đến ALTER COMMIT; PO giám sát và xác nhận checkpoint. Không chạy từng block bằng các shell `powershell -Command` độc lập. Mất session/identity trước khi chắc chắn ALTER chưa COMMIT dẫn tới HARD STOP và fresh start theo mục 4.10. Sau COMMIT, tuyệt đối không quay lại preflight schema cũ hoặc chạy lại ALTER; recovery phụ thuộc trạng thái thực thi.

## 2. Package inventory

| File | Vai trò | Có thể ghi gì sau Gate 2 |
|---|---|---|
| `01_preflight.ps1` | Git/runtime/process/path/schema preflight | Không ghi database |
| `02_fresh_backup.py` | Online Backup + restore validation + manifest | Chỉ tạo thư mục backup timestamp mới |
| `03_schema_alter.py` | Transaction ALTER duy nhất | Chỉ thêm `comments.model_version` vào DB thật |
| `04_postverify.py` | Đọc DB thật bằng `mode=ro`, đối chiếu manifest | Chỉ ghi file evidence cạnh manifest |
| `05_clone_smoke.py` | Khởi động backend với DB clone, smoke B/A/security | Chỉ ghi clone, log và evidence trong thư mục backup |

Không script nào tự gọi script kế tiếp. Không có `--force`, `--skip-check` hoặc nhánh bypass approval.
Fresh-backup manifest ghi SHA-256 của cả sáu file và một canonical package hash-set SHA-256. ALTER chỉ chạy khi hash-set hiện tại đồng thời khớp manifest và giá trị PO đã duyệt trong quyết định Gate 2.

## 3. Preconditions PO phải ký trước execution

1. Decision ID Gate 2 cụ thể, người thực hiện, thời điểm và chính xác lệnh được duyệt.
2. Backend và mọi tiến trình có thể ghi DB đã dừng; supervisor xác nhận ngoài việc kiểm tra cổng.
3. Package source sau khi điền Decision ID được PO review nguyên văn.
4. Repo đúng nhánh `task/T10-gan-model-B`, chứa commit `27701d1`, working tree sạch.
5. `DATABASE_URL` resolve đúng DB thật và DB không phải symlink/junction.
6. Không có `-wal`, `-shm`, `-journal`; schema có đúng sáu bảng và chưa có `model_version`.
7. Đóng các terminal IDE/agent khác đang trỏ repo, DB Browser/SQLite CLI, Jupyter, Python server và uvicorn khác. Không tắt/bypass check nếu antivirus, quyền Windows hoặc process không liên quan gây false-positive; ghi `BLOCKED_EXECUTION_MODEL` và báo PO.
8. Hai tài khoản clone smoke `demo@firefly.vn` và `admin@firefly.vn` phải tồn tại trong snapshot và operator phải có credential thử nghiệm hợp lệ. Password được nhập kín vào session, không ghi vào command line, log hoặc report.

Sai bất kỳ điều kiện nào: **HARD STOP**, không chạy bước sau.

## 4. Exact PowerShell command sequence — hiện chưa được phép chạy

Mọi giá trị chưa thể biết trước được giữ nguyên là `PENDING_PO_GATE2`; không tự đoán.

### 4.1. Session constants

Codex tạo trực tiếp một persistent PTY process với executable `powershell.exe` và arguments `-NoLogo -NoProfile -NoExit`; đây là cấu hình launch của công cụ điều phối, không phải lệnh chạy bên trong shell khác. Expected result: Codex nhận prompt và session ID bền. Nếu không có persistent session thì `BLOCKED_EXECUTION_MODEL`; không tiếp tục. Các block dưới đây chạy **bên trong chính session đó**.

```powershell
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true

function Assert-ReadyValue([string]$Name, [string]$Value) {
    if ([string]::IsNullOrWhiteSpace($Value) -or $Value -eq 'PENDING_PO_GATE2') {
        throw "HARD STOP: $Name is not PO-approved."
    }
}

$Package = 'C:\Projects\T10_GATE2_A1_FINAL_CANDIDATE_20261010'
$Repo = 'C:\Projects\firefly-cinema'
$Python = 'C:\Projects\firefly-cinema\backend\venv\Scripts\python.exe'
$DecisionId = 'PENDING_PO_GATE2'
$Manifest = 'PENDING_PO_GATE2'
$ManifestSha256 = 'PENDING_PO_GATE2'
$PostverifyEvidence = 'PENDING_PO_GATE2'
$ApprovedPackageHashSetSha256 = 'PENDING_PO_GATE2'

# Sáu giá trị này phải được Codex gán trong session từ quyết định PO nằm ngoài package.
# Không lấy từ manifest/package và không sửa các placeholder trong runbook.
$ApprovedPackageFileSha256 = @{
    '01_preflight.ps1' = 'PENDING_PO_GATE2'
    '02_fresh_backup.py' = 'PENDING_PO_GATE2'
    '03_schema_alter.py' = 'PENDING_PO_GATE2'
    '04_postverify.py' = 'PENDING_PO_GATE2'
    '05_clone_smoke.py' = 'PENDING_PO_GATE2'
    'T10_GATE2_EXECUTION_PACKAGE_DRAFT.md' = 'PENDING_PO_GATE2'
}

$OperatorShellPid = $PID
$OperatorShellProcess = Get-CimInstance Win32_Process -Filter "ProcessId=$OperatorShellPid" -ErrorAction Stop
if ($OperatorShellProcess.Name -notmatch '^(powershell)(\.exe)?$') { throw 'HARD STOP: operator session is not Windows PowerShell.' }
$OperatorShellCreationTimeUtc = ([datetime]$OperatorShellProcess.CreationDate).ToUniversalTime().ToString('o')
$OperatorShellExeSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $OperatorShellProcess.ExecutablePath).Hash
```

Expected result: bật fail-closed, lưu identity bất biến của persistent operator shell và thiết lập biến phiên. Runbook Markdown **không được sửa sau khi PO duyệt hash**. Giá trị thực, gồm sáu per-file SHA-256 và canonical hash-set, được Codex nhập/gán trong session từ quyết định PO bên ngoài package; không thay placeholder trong file Markdown. Trước mỗi pha, biến cần dùng phải qua `Assert-ReadyValue`; không được chạy placeholder.

### 4.2. `PACKAGE_INTEGRITY_GATE` — bắt buộc trước mọi script 01–05

Khối chỉ đọc sau là lệnh chính xác để kiểm package. **Không chạy trong vòng chuẩn bị tĩnh này.** Không được gọi bất kỳ script 01–05 nào nếu khối chưa in `PACKAGE_INTEGRITY_GATE=PASS` trong chính operator session. Nguồn kỳ vọng duy nhất là quyết định PO bên ngoài package; manifest chưa tồn tại và không phải root of trust.

```powershell
Assert-ReadyValue 'ApprovedPackageHashSetSha256' $ApprovedPackageHashSetSha256
$PackageFiles = @(
    '01_preflight.ps1',
    '02_fresh_backup.py',
    '03_schema_alter.py',
    '04_postverify.py',
    '05_clone_smoke.py',
    'T10_GATE2_EXECUTION_PACKAGE_DRAFT.md'
)
if ($ApprovedPackageFileSha256.Count -ne $PackageFiles.Count) {
    throw 'HARD STOP: external PO approval must contain exactly six package hashes.'
}
$ActualPackageFileSha256 = [ordered]@{}
foreach ($Name in $PackageFiles) {
    if (-not $ApprovedPackageFileSha256.ContainsKey($Name)) {
        throw "HARD STOP: external PO approval hash is missing for $Name."
    }
    Assert-ReadyValue "ApprovedPackageFileSha256[$Name]" ([string]$ApprovedPackageFileSha256[$Name])
    $Path = Join-Path $Package $Name
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "HARD STOP: package file is missing: $Path"
    }
    $Actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path -ErrorAction Stop).Hash.ToUpperInvariant()
    $Expected = ([string]$ApprovedPackageFileSha256[$Name]).ToUpperInvariant()
    if ($Actual -ne $Expected) {
        throw "HARD STOP: package SHA-256 mismatch for $Name."
    }
    $ActualPackageFileSha256[$Name] = $Actual
}

# Exact current algorithm: JSON object, keys sorted, no whitespace, ASCII, then SHA-256.
$CanonicalPairs = foreach ($Name in ($PackageFiles | Sort-Object -CaseSensitive)) {
    '"' + $Name + '":"' + $ActualPackageFileSha256[$Name] + '"'
}
$CanonicalJson = '{' + ($CanonicalPairs -join ',') + '}'
$Sha256 = [Security.Cryptography.SHA256]::Create()
try {
    $CanonicalHashSet = ([BitConverter]::ToString(
        $Sha256.ComputeHash([Text.Encoding]::ASCII.GetBytes($CanonicalJson))
    )).Replace('-', '').ToUpperInvariant()
} finally {
    $Sha256.Dispose()
}
if ($CanonicalHashSet -ne $ApprovedPackageHashSetSha256.ToUpperInvariant()) {
    throw 'HARD STOP: canonical package hash-set differs from external PO approval.'
}
Write-Output 'PACKAGE_INTEGRITY_GATE=PASS'
Write-Output "PACKAGE_HASH_SET_SHA256=$CanonicalHashSet"
```

Expected result: đủ sáu file, từng SHA-256 khớp external PO approval và canonical hash-set khớp thuật toán của `02_fresh_backup.py`. Thiếu approval, placeholder, thiếu file hoặc bất kỳ mismatch nào: **HARD STOP trước script 01**. Việc PASS ở đây không thay thế các kiểm tra hash độc lập trước helper import/manifest trong `03_schema_alter.py`, `04_postverify.py` và `05_clone_smoke.py`.

### 4.3. Preflight

```powershell
Assert-ReadyValue 'DecisionId' $DecisionId
& powershell.exe -NoProfile -NonInteractive -File "$Package\01_preflight.ps1" -DecisionId $DecisionId -POStoppedConfirmation 'PO_CONFIRMS_BACKEND_AND_ALL_DB_WRITERS_STOPPED' -OperatorShellPid $OperatorShellPid -OperatorShellCreationTimeUtc $OperatorShellCreationTimeUtc -OperatorShellExeSha256 $OperatorShellExeSha256
if ($LASTEXITCODE -ne 0) { throw "HARD STOP: preflight failed with exit code $LASTEXITCODE." }
```

Expected result: `PREFLIGHT=PASS`, đúng HEAD/path/schema và `NEXT_REQUIRED_STEP=02_fresh_backup.py`. Exit code bắt buộc: `0`. Exit khác `0`: **HARD STOP**.

### 4.4. Fresh online backup và restore validation

```powershell
Assert-ReadyValue 'DecisionId' $DecisionId
& $Python "$Package\02_fresh_backup.py" --decision-id $DecisionId --supervisor-confirmation 'APPLICATION_WRITERS_STOPPED_AND_VERIFIED'
if ($LASTEXITCODE -ne 0) { throw "HARD STOP: fresh backup failed with exit code $LASTEXITCODE." }
```

Expected result: tạo duy nhất thư mục mới `C:\Projects\firefly-cinema\backup\T10_2026-10-10\gate2_<timestamp>`, Online Backup và restore clone cùng logic với nguồn; in `BACKUP_VALIDATED`, `MANIFEST`, `MANIFEST_SHA256`, `OPERATOR_CHECKPOINT_REQUIRED=YES`. Exit code bắt buộc: `0`. Exit khác `0`: **HARD STOP**. Script dừng tại đây và không gọi ALTER.

### 4.5. Backup validation review

Sau khi chép chính xác hai giá trị script vừa in vào `$Manifest` và `$ManifestSha256` (các giá trị trong bản nháp hiện là `PENDING_PO_GATE2`):

```powershell
Assert-ReadyValue 'DecisionId' $DecisionId
Assert-ReadyValue 'Manifest' $Manifest
Assert-ReadyValue 'ManifestSha256' $ManifestSha256
Assert-ReadyValue 'ApprovedPackageHashSetSha256' $ApprovedPackageHashSetSha256

$ActualManifestSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $Manifest).Hash
if ($ActualManifestSha256 -ne $ManifestSha256) { throw 'HARD STOP: manifest SHA-256 mismatch.' }
$ManifestData = Get-Content -LiteralPath $Manifest -Raw | ConvertFrom-Json
$ActualBackupSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $ManifestData.backup.path).Hash
if ($ActualBackupSha256 -ne $ManifestData.backup.sha256) { throw 'HARD STOP: backup SHA-256 mismatch.' }
$ActualRestoreSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $ManifestData.restore_validation.path).Hash
if ($ActualRestoreSha256 -ne $ManifestData.restore_validation.sha256) { throw 'HARD STOP: restore SHA-256 mismatch.' }
if ($ManifestData.decision_id -ne $DecisionId) { throw 'HARD STOP: manifest Decision ID mismatch.' }
if ($ManifestData.package_hash_set_sha256 -ne $ApprovedPackageHashSetSha256) { throw 'HARD STOP: package hash-set was not approved by PO.' }
Get-Content -LiteralPath $Manifest -Raw
```

Expected result: manifest hiển thị đúng source tuyệt đối, Git HEAD, Decision ID, sáu bảng, schema/count/fingerprint, `integrity_check=["ok"]`, FK rỗng; ba cặp SHA-256 khớp. Mỗi lệnh exit `0`. Bất kỳ sai lệch nào: **HARD STOP**.

### 4.6. Operator checkpoint bắt buộc

PO/supervisor phải review manifest và ghi nhận riêng:

- fresh backup path;
- source SHA-256;
- backup SHA-256;
- manifest SHA-256;
- restore validation PASS;
- backend/writer vẫn dừng;
- source DB chưa đổi sau backup.

Không có xác nhận này thì không được nhập chuỗi `APPLICATION_WRITERS_STOPPED_AND_MANIFEST_REVIEWED` và không được chạy bước 4.7.

### 4.7. Schema ALTER

```powershell
Assert-ReadyValue 'DecisionId' $DecisionId
Assert-ReadyValue 'Manifest' $Manifest
Assert-ReadyValue 'ManifestSha256' $ManifestSha256
Assert-ReadyValue 'ApprovedPackageHashSetSha256' $ApprovedPackageHashSetSha256
& $Python "$Package\03_schema_alter.py" --decision-id $DecisionId --manifest $Manifest --manifest-sha256 $ManifestSha256 --approved-package-hash-set-sha256 $ApprovedPackageHashSetSha256 --supervisor-confirmation 'APPLICATION_WRITERS_STOPPED_AND_MANIFEST_REVIEWED' --operator-shell-pid $OperatorShellPid --operator-shell-creation-time-utc $OperatorShellCreationTimeUtc --operator-shell-exe-sha256 $OperatorShellExeSha256
if ($LASTEXITCODE -ne 0) { throw "HARD STOP: ALTER failed with exit code $LASTEXITCODE." }
```

Expected result: `ALTER_COMMITTED=YES`, chính xác một câu `ALTER TABLE comments ADD COLUMN model_version VARCHAR(100);`, rồi yêu cầu postverify. Exit code bắt buộc: `0`. Nếu fail trước commit, transaction rollback và **HARD STOP**. Nếu có nghi vấn sau commit: giữ nguyên DB, không startup và không tự restore; báo PO.

### 4.8. Read-only postverification

```powershell
Assert-ReadyValue 'DecisionId' $DecisionId
Assert-ReadyValue 'Manifest' $Manifest
Assert-ReadyValue 'ManifestSha256' $ManifestSha256
Assert-ReadyValue 'ApprovedPackageHashSetSha256' $ApprovedPackageHashSetSha256
& $Python "$Package\04_postverify.py" --decision-id $DecisionId --manifest $Manifest --manifest-sha256 $ManifestSha256 --approved-package-hash-set-sha256 $ApprovedPackageHashSetSha256
if ($LASTEXITCODE -ne 0) { throw "HARD STOP: postverification failed with exit code $LASTEXITCODE." }
```

Expected result: `POSTVERIFY=PASS`, cột mới `VARCHAR(100)` nullable/default NULL, toàn bộ dòng/cột gốc và schema ngoài thay đổi cho phép được bảo toàn, integrity/FK PASS; in đường dẫn `postverify_evidence.json`. Exit code bắt buộc: `0`. Nếu fail: **HARD STOP**, không startup backend thật, không restore tự động.

Sau khi chép chính xác đường dẫn output vào `$PostverifyEvidence`:

```powershell
Assert-ReadyValue 'PostverifyEvidence' $PostverifyEvidence
$PostverifyData = Get-Content -LiteralPath $PostverifyEvidence -Raw | ConvertFrom-Json
if ($PostverifyData.result -ne 'PASS') { throw 'HARD STOP: postverify evidence is not PASS.' }
if ($PostverifyData.decision_id -ne $DecisionId) { throw 'HARD STOP: postverify Decision ID mismatch.' }
if ($PostverifyData.manifest_sha256 -ne $ManifestSha256) { throw 'HARD STOP: postverify is not bound to manifest.' }
if ($PostverifyData.package_hash_set_sha256 -ne $ApprovedPackageHashSetSha256) { throw 'HARD STOP: postverify is not bound to approved package.' }
Get-Content -LiteralPath $PostverifyEvidence -Raw
```

Expected result: evidence có `result=PASS`, đúng Decision ID, source path và post-ALTER SHA-256. Exit code: `0`; khác đi là **HARD STOP**.

### 4.9. Clone-only API smoke

```powershell
Assert-ReadyValue 'DecisionId' $DecisionId
Assert-ReadyValue 'Manifest' $Manifest
Assert-ReadyValue 'ManifestSha256' $ManifestSha256
Assert-ReadyValue 'PostverifyEvidence' $PostverifyEvidence
Assert-ReadyValue 'ApprovedPackageHashSetSha256' $ApprovedPackageHashSetSha256

$SmokeUserCredential = Get-Credential -UserName 'demo@firefly.vn' -Message 'Credential cho tài khoản thử nghiệm trên clone'
$SmokeAdminCredential = Get-Credential -UserName 'admin@firefly.vn' -Message 'Credential quản trị thử nghiệm trên clone'
$UserBstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SmokeUserCredential.Password)
$AdminBstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SmokeAdminCredential.Password)
try {
    $env:T10_SMOKE_USER_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($UserBstr)
    $env:T10_SMOKE_ADMIN_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($AdminBstr)
    & $Python "$Package\05_clone_smoke.py" --decision-id $DecisionId --manifest $Manifest --manifest-sha256 $ManifestSha256 --approved-package-hash-set-sha256 $ApprovedPackageHashSetSha256 --postverify-evidence $PostverifyEvidence
    if ($LASTEXITCODE -ne 0) { throw "HARD STOP: clone smoke failed with exit code $LASTEXITCODE." }
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($UserBstr)
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($AdminBstr)
    Remove-Item Env:T10_SMOKE_USER_PASSWORD -ErrorAction SilentlyContinue
    Remove-Item Env:T10_SMOKE_ADMIN_PASSWORD -ErrorAction SilentlyContinue
}
```

Expected result: `CLONE_API_SMOKE=PASS`, health/movies/GET+POST comments/admin predict/security `401/403/200`, B/version persistence và A fallback PASS; real DB SHA không đổi; test records chỉ nằm trong clone. Exit code bắt buộc: `0`. Fail: **HARD STOP**; không được chuyển record thử nghiệm vào DB thật.

### 4.10. Recovery theo trạng thái thực thi

#### A. Trước ALTER COMMIT và đã xác định chắc chắn chưa COMMIT

- Mất persistent PTY, PID/creation identity đổi hoặc operator identity không còn chứng minh được: **HARD STOP**.
- Không dùng lại session hoặc manifest cũ. Không được chỉ mở shell mới rồi tiếp tục ALTER.
- Lần thử lại phải dùng persistent session mới, PO xác nhận lại writer/process conditions, chạy lại `PACKAGE_INTEGRITY_GATE`, preflight và tạo fresh backup mới. Manifest cũ bị loại khỏi lần thử lại.
- Quy tắc này chỉ áp dụng khi evidence chứng minh ALTER chưa chạy/transaction chưa COMMIT. Nếu có nghi ngờ ALTER đã chạy hoặc COMMIT status không rõ, chuyển ngay sang nhánh B.

#### B. Sau ALTER COMMIT hoặc COMMIT status không xác định

- Không chạy lại preflight dành cho schema cũ, không chạy lại `02_fresh_backup.py` như một cách tiếp tục, và tuyệt đối không chạy lại ALTER.
- Không reset, replace hoặc restore tự động. Dừng và báo PO với output cuối cùng, timestamp, session identity, manifest/hash và lỗi quan sát được.
- Chỉ kiểm tra trạng thái database bằng quy trình read-only được PO chấp thuận riêng. Việc đó phải đối chiếu ít nhất: schema thực tế, manifest/backup binding, dữ liệu gốc (counts/fingerprints/schema ngoài thay đổi cho phép), `integrity_check` và `foreign_key_check`.
- Không suy diễn rollback từ lỗi. Nếu cần rollback/restore, phải có quyết định PO riêng và tuân theo mục 7.

#### C. Sau `POSTVERIFY=PASS` nhưng trước clone smoke

- Không chạy lại preflight, backup, ALTER hoặc postverify mutation path; không khởi động backend thật.
- Nếu session còn nguyên, tiếp tục mục 4.9 sau checkpoint PO. Nếu session mất, HARD STOP tại clone boundary và báo PO; chỉ được resume khi PO cho phép **clone-only smoke** riêng.
- Trong session mới được PO cho phép, gán lại các giá trị từ external PO decision/evidence, chạy lại nguyên khối read-only `PACKAGE_INTEGRITY_GATE`, xác minh lại manifest SHA/Decision ID/package hash-set theo mục 4.5, xác minh `postverify_evidence.json` theo mục 4.8, và xác minh SHA-256 hiện tại của DB thật vẫn bằng `post_alter_sha256` trong evidence.
- Nếu mọi đối chiếu PASS, chỉ chạy `05_clone_smoke.py` theo mục 4.9. Script này tạo/chạy backend trên clone; không được trỏ hoặc khởi động backend với DB thật. Mismatch hoặc thiếu evidence: HARD STOP và báo PO.

### 4.11. Final evidence collection

```powershell
Assert-ReadyValue 'Manifest' $Manifest
Assert-ReadyValue 'ManifestSha256' $ManifestSha256
Assert-ReadyValue 'PostverifyEvidence' $PostverifyEvidence
$FinalRealDbSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath 'C:\Projects\firefly-cinema\backend\firefly.db').Hash
$PostverifyData = Get-Content -LiteralPath $PostverifyEvidence -Raw | ConvertFrom-Json
if ($FinalRealDbSha256 -ne $PostverifyData.post_alter_sha256) { throw 'HARD STOP: real DB changed after postverify.' }
$ManifestData = Get-Content -LiteralPath $Manifest -Raw | ConvertFrom-Json
$BackupDirectory = Split-Path -Parent $ManifestData.backup.path
$CloneEvidencePath = Join-Path $BackupDirectory 'clone_smoke\clone_smoke_evidence.json'
$CloneEvidence = Get-Content -LiteralPath $CloneEvidencePath -Raw | ConvertFrom-Json
if ($CloneEvidence.result -ne 'PASS') { throw 'HARD STOP: clone smoke evidence is not PASS.' }
$GitStatus = @(& git -C $Repo status --short)
if ($LASTEXITCODE -ne 0) { throw "HARD STOP: git status failed with exit code $LASTEXITCODE." }
if ($GitStatus.Count -ne 0) { throw "HARD STOP: repository changed: $($GitStatus -join '; ')" }
Get-Content -LiteralPath $Manifest -Raw
Get-Content -LiteralPath $PostverifyEvidence -Raw
Get-Content -LiteralPath $CloneEvidencePath -Raw
```

Expected result: post-ALTER SHA khớp postverify; evidence PASS; Git worktree không có production/doc diff do execution; backup files nằm trong khu vực backup ngoài Git. Mỗi lệnh exit `0`. Sai lệch: **HARD STOP** và báo PO.

## 5. Runtime write-risk boundary

`backend/app/main.py` gọi `seed()` khi startup; `_ensure_showtimes()` có thể thêm suất chiếu và commit. Vì vậy:

1. Schema verification trên DB thật chỉ dùng SQLite URI `mode=ro` trong `04_postverify.py`.
2. API write smoke chỉ khởi động backend với `DATABASE_URL` trỏ tuyệt đối đến clone trong `05_clone_smoke.py`.
3. Gói này **không khởi động backend trên DB thật** và không POST comment vào DB thật.
4. Runtime startup trên DB thật cần PO xác nhận riêng phạm vi side effect của `_ensure_showtimes`; Gate 2 cho ALTER không mặc nhiên cấp quyền đó.
5. Child backend clone bắt buộc `PYTHONIOENCODING=utf-8`; credentials clone smoke bị xóa khỏi child backend environment và không được in/log.

## 5.1. Verified operator PID model

- Preflight process phải là direct child của persistent operator PowerShell; operator được xác minh bằng PID, UTC creation time, executable type và SHA-256.
- ALTER recheck process phải là direct child của Python đang chạy đúng `03_schema_alter.py`.
- Python ALTER phải là direct child của operator shell, hoặc đi qua đúng một optional venv launcher có executable path chính xác `backend\venv\Scripts\python.exe` và parent là operator shell.
- Chỉ bốn loại PID cụ thể sau có thể được loại: persistent operator shell, current preflight/recheck child, current ALTER Python và optional verified venv launcher. Không loại trừ theo quan hệ cha/con chung chung.
- Uvicorn, SQLite CLI, backend writer hoặc Python khác không bao giờ được loại chỉ vì là descendant/ancestor. Không chứng minh được exact chain: `BLOCKED_EXECUTION_MODEL` / HARD STOP.

## 6. Hard stops

- Sai repo/branch; `27701d1` không là ancestor; worktree không sạch.
- Decision ID còn pending, không khớp source/manifest hoặc chưa được PO review.
- `PACKAGE_INTEGRITY_GATE` chưa PASS trước script 01, thiếu external PO hash approval, thiếu file hoặc bất kỳ per-file/canonical hash mismatch nào.
- Python/runtime/database path sai; DB là reparse point; có process writer/listener/SQLite sidecar.
- Schema không đúng sáu bảng, `comments` khác kỳ vọng hoặc `model_version` đã tồn tại.
- Source thay đổi trong/sau backup; backup/restore logic khác nguồn.
- Integrity/FK/count/fingerprint/schema/PK/index/constraint sai.
- Manifest/backup SHA sai hoặc Git HEAD đổi giữa backup và ALTER.
- Không lấy được `BEGIN EXCLUSIVE` trong timeout hữu hạn.
- Bất kỳ DDL/data change nào ngoài một cột nullable được cho phép.
- Postverify hoặc clone smoke fail.
- Mất session/identity trước COMMIT; hoặc COMMIT status không rõ mà quy trình bị xử lý nhầm như pre-COMMIT retry.

## 7. Rollback plan — chuẩn bị, không thực hiện

1. Dừng toàn bộ backend/process có thể ghi DB.
2. Giữ riêng database lỗi để điều tra; không ghi đè hoặc chỉnh sửa snapshot đã xác minh.
3. Báo PO với source/backup/manifest/postverify hashes và lỗi cụ thể.
4. Chỉ sau quyết định restore riêng của PO, restore backup sang **file mới**.
5. Trên file mới, kiểm integrity/FK/schema/count/fingerprint và so với manifest.
6. Chỉ thay thế DB thật sau khi PO xác nhận chính xác lệnh thay thế.

Rollback về snapshot gốc cũng loại bỏ `comments.model_version`; backend T10 khi đó quay lại trạng thái chưa sẵn sàng với database thật. Không có script restore tự động trong gói này.

## 8. Current package status

- Gate 1: APPROVED / `27701d1`.
- Gate 2: NOT AUTHORIZED.
- Decision ID: `PENDING_PO_GATE2`.
- Real DB modified: NO.
- Backup created by this package: NO.
- ALTER executed: NO.
- Restore executed: NO.
- API smoke executed: NO.
- Next step: Claude final independent review; sau đó PO review exact source/commands và quyết định Gate 2 riêng.

**HARD STOP — chờ PO.**
