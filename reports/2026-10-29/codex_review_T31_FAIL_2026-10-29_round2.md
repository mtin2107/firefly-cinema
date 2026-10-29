# Codex review T31 round 2 — FAIL — 2026-10-29

Reviewed HEAD: a8053958d68529e10755bc632d57e320360dee38, branch task/T31-sua-low. Reviewed fix diff ca881af..task/T31-sua-low and whole-task diff master...task/T31-sua-low. Changed files remain within T31 section 6 allowlist. No production changes by reviewer, schema change, merge or next task.

## Findings
RF-01 CLOSED: original SOS-header embedded FFD9 sample now returns 422 for POST /api/admin/posters and PUT /api/auth/me/avatar on temporary backend. Extracted current mock jpegComplete returns false. Oversized SOS and prior cases also covered by passing full suite.

### RF-02
- Severity: Medium
- File: backend/app/routers/admin_posters.py:52; frontend/src/api/mock.js:407
- Problem: segment length has an upper bound check for SOS but no lower bound. SOS lengths 0 and 1 are accepted, despite being too short even to include the two length bytes. Thus malformed/truncated JPEG can still pass AC-04.
- Evidence: prefix hex `ffd8ffe000104a46494600010100000100010000`, followed by `ffda0000ffd97461696c` or `ffda0001ffd97461696c`. Both return poster 201 and avatar 200 via HTTP. Browser mock editor saves both with “Đã cập nhật phim.”. Neither file ends in FFD9, so these exercise the modified parser rather than legacy endswith acceptance.
- Expected Fix: reject invalid segment lengths before calculating/using end; at minimum require length >= 2, and validate the SOS header structure/length before treating subsequent bytes as scan data. Mirror rules in mock. Add tests for both lengths on poster, avatar and mock; expect 422 and no written image. Preserve valid FF padding and trailing-data support.

## Independent verification
Temporary workspace: %TEMP%/codex-t31-r2; SQLite review.db and uploads there. Backend port 8008; real frontend 5183; mock 5184. ADMIN_PASSWORD set via environment to a review-only value. Startup wrapper suppresses reading backend/.env (Path.read_text returns empty only for that exact path); application database and uploads explicitly overridden before import. No startup against backend/firefly.db; no credentials read from .env. Classifiers disabled for these UI checks; no claim of model inference validation.

| AC | Result | Evidence |
|---|---|---|
| AC-01 | PASS | Browser real: review.webm remains in input.files; bad.txt gives Vietnamese type error and files.length=0. |
| AC-02 | PASS | Upload/save trailer, reopen: YouTube empty and uploaded-video note present; save again/reopen retains note/trailer. Synthetic WebM signature fixture tests upload/form preservation, not video decoding. |
| AC-03 | PASS | Full suite includes optional score, RatingIn rejection and renamed subclass tests. |
| AC-04 | FAIL | Original RF rejected in poster/avatar/mock; ordinary cut rejected; trailing EOI accepted. New RF-02 above. |
| AC-05 | PASS | Authenticated admin real: 360/375px header 71px, document scrollWidth equals viewport. At 421px avatar hidden, name static, old layout restored (115.6875px header), no horizontal overflow. |
| AC-06 | PASS | Real seeded dashboard at 800/862/1100/1101/1280px: Range.getClientRects on all six strong values gives one line each; revenue 23.310.000 đ, rating 8.0 / 10. |
| AC-07 | PASS | compileall exit 0; full pytest from backend: 276 passed, 1 Starlette deprecation warning, 191.99s; explicit VITE_USE_MOCK=false/true builds both exit 0. |

Additional HTTP boundary matrix (poster/avatar): original RF 422/422; SOS length 0 201/200; length 1 201/200; multiple FF padding before valid SOS 201/200; trailing data after real EOI 201/200; truncated scan 422/422. Mock browser save: trailing accepted, truncated scan rejected with Vietnamese error, SOS 0/1 accepted. Original RF mock function false. Browser checks pending from round 1 are now completed.

## Decision
FAIL → FIX_LOOP for RF-02. RF-01's exact regression is closed; RF-02 is a separate minimum-length boundary missed by that fix. No TODO used to waive AC-04. PO review/merge not authorized by this result.
