# T10 Gate 2 A1 — Final Package Freeze Report

> **FINAL PACKAGE PREPARATION ONLY — GATE 2 EXECUTION NOT AUTHORIZED**

## 1. Authority and identity

- Task: T10.
- Gate 1 commit: `27701d1` (`27701d19a150117919e0172f2386d819a7b9d369`).
- Claude Final Independent Review: `PASS_WITH_TODO`.
- Required Fixes: `0`.
- G2-R4-01 through G2-R4-04: `PO ACCEPT_WITH_NOTES`.
- Proposed Decision ID: `PO-DECISION-T10-REALDB-A1-GATE2-20261010`.
- Intended operator: `CODEX / PO SUPERVISION`.
- Final package preparation: authorized.
- Gate 2 execution: **NOT AUTHORIZED**.

The proposed Decision ID is present only to prepare the candidate. It is not execution authority.

## 2. Package locations

- Source package: `C:\Projects\T10_GATE2_A1_DRAFT_20261010`.
- Final candidate: `C:\Projects\T10_GATE2_A1_FINAL_CANDIDATE_20261010`.
- Source canonical hash verified before copy: `9E2DBD32894FC522344D5EC5BE24FE16F173EAE009CC16220F81AFFE89639B4A`.
- Source package remained in place and was not edited or unlocked.
- The six package files were copied byte-for-byte before the five authorized replacements.
- This report is outside the six-file package hash-set.

## 3. Exact five-line Decision ID diff

No other candidate content changed.

```diff
--- 01_preflight.ps1
-$ApprovedDecisionId = 'PENDING_PO_GATE2'
+$ApprovedDecisionId = 'PO-DECISION-T10-REALDB-A1-GATE2-20261010'

--- 02_fresh_backup.py
-APPROVED_DECISION_ID = "PENDING_PO_GATE2"
+APPROVED_DECISION_ID = "PO-DECISION-T10-REALDB-A1-GATE2-20261010"

--- 03_schema_alter.py
-APPROVED_DECISION_ID = "PENDING_PO_GATE2"
+APPROVED_DECISION_ID = "PO-DECISION-T10-REALDB-A1-GATE2-20261010"

--- 04_postverify.py
-APPROVED_DECISION_ID = "PENDING_PO_GATE2"
+APPROVED_DECISION_ID = "PO-DECISION-T10-REALDB-A1-GATE2-20261010"

--- 05_clone_smoke.py
-APPROVED_DECISION_ID = "PENDING_PO_GATE2"
+APPROVED_DECISION_ID = "PO-DECISION-T10-REALDB-A1-GATE2-20261010"
```

`T10_GATE2_EXECUTION_PACKAGE_DRAFT.md` is byte-for-byte identical to the source runbook.

## 4. Final candidate SHA-256

| File | SHA-256 |
|---|---|
| `01_preflight.ps1` | `56CAB1EE118FF9EEB54D844480CB7F0C080AC0A282AA1C69F187A56E61943F1F` |
| `02_fresh_backup.py` | `F81496DBCA717C892EAA0BC11BAF10C63E7DA7C537F2660E3ACA3ACB1DD10BC9` |
| `03_schema_alter.py` | `6F812ECE3266DC8EDFC4473CED41FDA8B14F180E872C39985FC8CB80B90D4A47` |
| `04_postverify.py` | `E957A2D229DA336839CA48A38608870F572673E802AD01772F7B55E6A2C2303C` |
| `05_clone_smoke.py` | `3624F17763A87E41717088F3E09A211B9C245B134B497129FC1082BE69D0D0B0` |
| `T10_GATE2_EXECUTION_PACKAGE_DRAFT.md` | `E78E4F5B447E066E4ED759C53FA70111602FD825DDDE296F8FDE660C6077203D` |

Canonical final candidate hash-set:

`627AB637ECA04C15D1240053043D46B5A672786037D8104D12404233C485E884`

This is a **FINAL CANDIDATE HASH**, not a PO-approved execution hash.

Canonical algorithm: SHA-256 of the ASCII encoding of a compact JSON object containing the six uppercase per-file hashes, with file-name keys sorted and no whitespace. This matches the reviewed algorithm in the package.

## 5. Static validation

| Check | Result |
|---|---|
| Source canonical equals required value | PASS |
| Destination did not exist before creation | PASS |
| Initial copy matched all six source hashes | PASS |
| Source-to-candidate diff | PASS — exactly five Decision ID constant lines |
| In-memory reversal of each Decision ID restores exact source content | PASS — 5/5 |
| Candidate runbook byte-for-byte equals source | PASS |
| Proposed Decision ID in candidate constants | PASS — 5/5 |
| Source constants remain `PENDING_PO_GATE2` | PASS — 5/5 |
| Python AST, scripts 02–05 | PASS — 4/4 |
| PowerShell parser, `01_preflight.ps1` | PASS |
| PowerShell parser, embedded ALTER process recheck | PASS |
| PowerShell parser, runbook blocks | PASS — 10/10 |
| Package integrity gate precedes all script invocations | PASS — 5/5 invocations after gate |
| Backup/ALTER/postverify/clone isolation logic | UNCHANGED — exact content match after reversing only Decision ID |
| Repository | CLEAN on `task/T10-gan-model-B` at `27701d19a150117919e0172f2386d819a7b9d369` |

No package script or runbook command block was executed during these checks.

## 6. Package integrity verification

- Six candidate SHA-256 values were calculated directly from candidate files.
- Canonical hash-set was calculated from those six values using the current reviewed algorithm.
- The integrity gate remains before the first invocation of script 01 and therefore before every script 01–05 invocation.
- Pre-ALTER independent package checks in scripts 03–05 are unchanged.
- Runbook placeholders remain session values; no final candidate hash was written into a package file.
- No circular hash dependency was introduced.

## 7. PO ACCEPT_WITH_NOTES dispositions

- **G2-R4-01 — ACCEPT_WITH_NOTES:** unknown or missing COMMIT evidence is treated as `UNKNOWN`; stop and do not rerun ALTER.
- **G2-R4-02 — ACCEPT_WITH_NOTES:** return to a pre-COMMIT flow requires a separate PO decision based on read-only evidence.
- **G2-R4-03 — ACCEPT_WITH_NOTES:** if clone smoke is interrupted, preserve existing evidence; do not delete or arbitrarily reuse its directory.
- **G2-R4-04 — ACCEPT_WITH_NOTES:** PO enters test credentials directly; Codex must not collect or record passwords in reports.

Per PO instruction, no script was changed for these notes.

## 8. Prohibited actions retained

The following were not performed and remain prohibited without separate Gate 2 authority:

- executing `01_preflight.ps1` or scripts `02_fresh_backup.py` through `05_clone_smoke.py`;
- running any PowerShell block from the runbook;
- creating a persistent PowerShell execution session;
- opening or modifying the real SQLite database;
- creating a backup or running restore, ALTER, postverify, backend or API smoke;
- entering or collecting credentials;
- moving this candidate into the official execution path;
- declaring Gate 2 approved;
- modifying, staging or committing the production repository;
- merging, tagging or authorizing T11.

## 9. Source draft preservation

- Source draft canonical after candidate preparation: `9E2DBD32894FC522344D5EC5BE24FE16F173EAE009CC16220F81AFFE89639B4A` — unchanged.
- Proposed Decision ID occurrences in the five source scripts: `0`.
- Each source Decision ID constant remains `PENDING_PO_GATE2`.
- Candidate runbook SHA-256 equals source runbook SHA-256: `E78E4F5B447E066E4ED759C53FA70111602FD825DDDE296F8FDE660C6077203D`.

## 10. Remaining approval requirements

Before any execution, PO must separately review and approve externally:

1. all six final candidate SHA-256 values;
2. canonical final candidate hash-set;
3. exact commands and operator/session model;
4. execution timing and CODEX / PO SUPERVISION;
5. runtime scope, explicitly excluding backend startup on the real database;
6. final independent review result for this exact candidate.

The candidate must not be edited after exact-hash approval. Any byte change invalidates these hashes and requires a new review/approval cycle.

## 11. Runtime evidence not verified

The following remain unverified because Gate 2 execution is not authorized:

- persistent PTY and real PID-chain behavior;
- writer/listener/file-handle checks;
- fresh online backup and restore validation;
- manifest binding and runtime package-integrity result;
- database lock, `BEGIN EXCLUSIVE`, transaction, rollback and COMMIT state;
- real-database read-only postverification;
- clone isolation at runtime, B/A smoke, credentials and API/security results.

## 12. Final status

TASK: T10  
MODE: FINAL_PACKAGE_PREPARATION_ONLY  
CLAUDE FINAL REVIEW: PASS_WITH_TODO  
REQUIRED FIXES: 0  
G2-R4-01...04: PO ACCEPT_WITH_NOTES  
PROPOSED DECISION ID: PO-DECISION-T10-REALDB-A1-GATE2-20261010  
SOURCE PACKAGE HASH: 9E2DBD32894FC522344D5EC5BE24FE16F173EAE009CC16220F81AFFE89639B4A  
FINAL CANDIDATE HASH: 627AB637ECA04C15D1240053043D46B5A672786037D8104D12404233C485E884  
FINAL SIX FILE SHA256: RECORDED IN SECTION 4  
DIFF SCOPE: EXACTLY 5 DECISION CONSTANT LINES  
STATIC CHECKS: PASS  
SOURCE PACKAGE STILL LOCKED: YES — UNCHANGED / PENDING  
REAL DB MODIFIED: NO  
BACKUP EXECUTED: NO  
ALTER EXECUTED: NO  
RESTORE EXECUTED: NO  
API SMOKE EXECUTED: NO  
GIT COMMIT: NONE  
GATE 2 EXECUTION: NOT AUTHORIZED  
NEXT STEP: CLAUDE REVIEW FINAL CANDIDATE / PO EXACT-HASH APPROVAL

**HARD STOP — dừng và chờ PO.**
