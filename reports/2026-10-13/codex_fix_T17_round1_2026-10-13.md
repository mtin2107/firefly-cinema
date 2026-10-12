# Codex Fix Report — T17 Round 1 / TODO-03

- Task: T17 — Chatbot AI tư vấn phim
- Date: 2026-10-13
- Branch: `task/T17-chatbot-tu-van`
- Base review commit: `7e161b1` (Claude `PASS_WITH_TODO`, RF 0, TODO 8)
- Current result: **FIX_IMPLEMENTED / READY_FOR_CLAUDE_INDEPENDENT_REVIEW** (NOT Claude PASS)
- Reason: PO elected `FIX_NOW` for T17 TODO-03 before final PO approval.
- Đổi schema: **Không**

## File changed
- `frontend/src/api/mock.js` only (production code fix).
- This report and `docs/TASK_COORDINATION_ACTIVE.md` are governance evidence; no forbidden files changed.

## Fix description
- Root cause: Vietnamese 'hài' becomes `hai` when normalized, and the prior `question.includes("hai")` misclassified genre recommendations as ticket-price questions.
- Implemented `wantsComedy` branch for movie-comedy requests, filtered `now_showing` films with genre `Hài hước`; removed `hai` as a price trigger.
- Kept VIP/regular ticket-price intent in the price branch. REAL API integration and Gemini model logic unchanged.

## Focused/manual evidence (from PO screenshots)
1. `Gợi ý phim hài đang chiếu` -> `Thứ Bảy Không Ngủ` (comedy), not price. **PASS**.
2. `Ghế VIP giá bao nhiêu?` -> VIP surcharge 20.000 VND. **PASS**.
3. `Tối nay có phim gì?` -> three now-showing movies and movie links. **PASS**.

## Post-fix quality gates (PO PowerShell transcript)
| Gate | Result |
|---|---|
| `python -m compileall -q backend/app` | PASS |
| `pytest -q tests/test_chat.py` | **14 passed**, 1 existing Starlette deprecation warning |
| Full `pytest -q` | **50 passed**, 1 existing Starlette deprecation warning |
| `node --check frontend/src/api/mock.js` | PASS |
| `VITE_USE_MOCK=true npm run build` | PASS (72 modules) |
| `VITE_USE_MOCK=false npm run build` | PASS (72 modules) |
| `git diff --check` | PASS; LF/CRLF conversion warning only |
| Git source scope | Only `frontend/src/api/mock.js` modified before report/coordination |

## Related PO AC-02 evidence (not a replacement for Claude Round 2)
- Google AI Studio project: Free Tier; model used for successful live tests: `gemini-3.5-flash-lite`, configured locally in ignored `backend/.env`.
- Gemini direct call and chatbot REAL returned answers. PO verified `Thứ Bảy Không Ngủ` showtimes 14/10/2026 at 09:30 and 13:15 (room 2), basic ticket 75.000 VND, movie button; `Gợi ý phim hài đang chiếu` returned that comedy movie and link.
- Original `gemini-3.8-flash` responded HTTP 503 in direct-call testing. No Gemini key placed in Git/report.
- AC-02 has **PO-observed PASS evidence**, awaiting formal PO report and TODO disposition after Claude's independent review.

## Scope, security, blockers
- Fix is limited to the T17 file allowlist; no database, schema, API key, dependency or backend source changed.
- Existing T16 TODO-01..07 remain unchanged in coordination; T16 real-DB migration/deploy gate remains separately controlled.
- Open required fixes at original Claude review: **0**. TODO-03 fix requires Claude verification; remaining TODO dispositions are PO-owned.

## Handoff
- Transition requested: **T17 FIX_LOOP -> CLAUDE_REVIEW Round 2**.
- Claude to independently verify mock comedy response, non-regression of VIP/today queries, full gates, diff scope, and retention of prior TODOs.
- **Do not self-approve, mark DONE/CLOSED or merge.**
