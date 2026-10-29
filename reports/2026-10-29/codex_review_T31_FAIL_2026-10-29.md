# Codex independent review T31 — FAIL — 2026-10-29

Reviewed branch: task/T31-sua-low, HEAD b57e2748d3e32dbb79df2953d02533ed2082de73. Diff: git diff master...task/T31-sua-low.

## Verdict
FAIL: AC-04 has a reproducible validation defect. Production code unchanged; no merge or next task opened.

## RF-01
- Severity: Medium
- File: backend/app/routers/admin_posters.py:52; frontend/src/api/mock.js:408
- Problem: EOI search starts inside the SOS header rather than after its declared segment length. A truncated JPEG containing FFD9 in that header is accepted without any EOI in scan data.
- Evidence: bytes.fromhex("ffd8ffe000104a46494600010100000100010000ffda00080101ffd93f00") + b"truncated" passed validate_image (returned jpg); extracted mock jpegComplete also returned true in Node. SOS length is 8; FFD9 is inside those 8 bytes. auth.py:163 shares validate_image for avatars, so both upload paths inherit the defect.
- Expected Fix: validate SOS length/bounds and search for EOI only after the complete SOS segment. Keep support for trailing data after real EOI. Add regression coverage for poster, avatar and mock; reject this input with 422 and create no file.

## Acceptance criteria and verification
- Scope: all 11 changed files are in section 6 allowlist; no schema/dependency changes in reviewed diff.
- AC-01/02: source reviewed; independent browser execution NOT COMPLETED.
- AC-03: class flag/inheritance implementation reviewed; full-suite result below.
- AC-04: FAIL on adversarial truncated SOS above. Existing implementation tests cover trailing data and ordinary truncation for poster only. Independent avatar HTTP probes and browser mock uploads NOT COMPLETED.
- AC-05/06: CSS/source reviewed; independent browser measurements at required widths NOT COMPLETED. Implementation report is not independent evidence.
- AC-07: compileall exit 0; npm run build real and VITE_USE_MOCK=true both exit 0. Full pytest launched from backend (initial root invocation could not import app; rerun in correct directory).

## Limits
No browser session was established. Required temporary DB/UPLOAD_DIR browser checks (trailer, authenticated header 360/375/421px, dashboard 800/862/1100/1101/1280px, mock mode) remain pending and must be run in the next review. No backend was started against backend/firefly.db. Validator probe only decodes bytes and writes no images.

Full pytest final: 268 passed, 1 deprecation warning, 176.18s; exit 0.
