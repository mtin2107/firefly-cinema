# Codex review T31 round 3 — PASS — 2026-10-29

Reviewed HEAD: 984f06ab2209714dbcacc4e1910a9fffa200fa69 on task/T31-sua-low. Reviewed diff dad5ff9..task/T31-sua-low and round 2 review/fix report. Only JPEG validator, associated tests and allowed review/coordination documents changed. No schema/dependency/UI change.

## Findings
RF-01 CLOSED, RF-02 CLOSED / independently verified. Required Fixes: 0. No new TODO.

Segment lengths below 2 now reject early. SOS checks Ns 1–4, exact length 6+2*Ns, segment bounds, then searches EOI after the complete header. Backend/mock rules match. Legacy acceptance for files ending in FFD9 is preserved as explicitly scoped by T31; this review does not claim full JPEG decoding validation.

## Independent HTTP and browser evidence
Temporary backend on port 8008 uses %TEMP%/codex-t31-r3/review.db and uploads. ADMIN_PASSWORD set to a review-only value by environment. Startup wrapper suppresses reading backend/.env before application import. No backend startup against backend/firefly.db. Mock frontend port 5184, authenticated admin; each sample selected through poster file input and saved in existing movie editor.

| Sample | Poster HTTP | Avatar HTTP | Browser mock save |
|---|---|---|---|
| SOS length 0 | 422 | 422 | Vietnamese damaged-image error |
| SOS length 1 | 422 | 422 | Vietnamese damaged-image error |
| RF-01 original embedded header EOI | 422 | 422 | Vietnamese damaged-image error |
| Multiple FF padding before SOS | 201 | 200 | Saved successfully |
| Trailing data after real EOI | 201 | 200 | Saved successfully |
| Truncated scan without EOI | 422 | 422 | Vietnamese damaged-image error |
| SOS Ns 0, length consistent with Ns | 422 | 422 | Vietnamese damaged-image error |
| SOS Ns 4, length 14 | 201 | 200 | Saved successfully |
| SOS Ns 5, length 16 | 422 | 422 | Vietnamese damaged-image error |
| SOS Ns 1, declared length 10 | 422 | 422 | Vietnamese damaged-image error |
| APP length 0 | 422 | 422 | Vietnamese damaged-image error |
| APP length 1 | 422 | 422 | Vietnamese damaged-image error |

Synthetic byte fixtures exercise boundary validation; no claim that they are decodable photographs. Probe script remains outside repository at %TEMP%/codex-t31-r3/probe.cjs.

## Acceptance and gates
AC-04 PASS on independent matrix above. AC-01/02/03/05/06 retain independently verified round 2 PASS: current diff does not change their implementation. AC-07: compileall app exit 0; explicit VITE_USE_MOCK=false and true npm run build both exit 0. Full pytest final recorded below.

## Decision
PASS → PO_REVIEW. No production code edits, merge or next task opened by reviewer. PO retains merge decision.

Full pytest: 286 passed, 1 Starlette deprecation warning, exit 0. Direct backend run: 186.49s. Confirmatory backend run with exact backend/.env read suppressed and DATABASE_URL/UPLOAD_DIR temporary overrides: 286 passed in 184.83s. The initial direct invocation used the application's normal config loader; no .env values were inspected or printed. The isolated run supplies the final gate evidence.
