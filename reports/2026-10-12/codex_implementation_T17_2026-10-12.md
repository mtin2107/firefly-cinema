# Codex Implementation Report — T17 (handoff for Claude)

- Task: **T17 — Chatbot AI tư vấn phim**
- Task date: **2026-10-12** · Evidence synchronized: **2026-10-13**
- Result: **DEV_IMPLEMENTATION_COMPLETED / READY_FOR_CLAUDE_INDEPENDENT_REVIEW** (NOT a Claude PASS)
- Branch: `task/T17-chatbot-tu-van` · Dependency: T16 `DONE / CLOSED` per PO, merged into master per PO statement
- **Đổi schema: Không** · No reset/delete of real `backend/firefly.db` or real runtime startup
- Model configured: `gemini-3.8-flash` · Base URL: `https://generativelanguage.googleapis.com/v1beta/openai/`
- Backend dependency: **`openai==3.29.0`**, exactly one line added to requirements; no frontend dependency changed
- Google AI Studio free quota RPM/TPM/RPD: **PENDING ACCOUNT-SPECIFIC PO VERIFICATION**; no real API key was used in DEV evidence

## Files Changed
Backend: `app/chat_assistant.py`, `routers/chat.py`, `main.py`, `config.py`, `schemas.py`, `requirements.txt`, `.env.example`, `tests/test_chat.py`.
Frontend: `src/components/ChatWidget.jsx`, `src/App.jsx`, `src/api/real.js`, `src/api/mock.js`, `src/styles/global.css`.
Documentation/governance: `docs/ARCHITECTURE.md`, `docs/CONG_NGHE.md`, `HUONG_DAN.md`, `docs/TASK_COORDINATION_ACTIVE.md`, this report.

## Implemented
- Authenticated user-only `POST /api/chat`; Vietnamese input validation, user-scoped in-memory rate limits, safe provider errors, lazy client initialization when key is absent.
- Read-only tools `search_movies`, `get_showtimes`, `get_price_rules`; no user/bookings/comments tool and no DB write; tool loops capped at three.
- Reply contract `{reply, movies}` in REAL and MOCK; floating chat, suggestion prompts, movie links, ESC and keyboard controls, reduced-motion support.
- Post-test UI improvement: draggable AssistiveTouch-like button, edge snapping and saved position; scope limited to `ChatWidget.jsx` and chatbot CSS.

## Focused tests and final gates (from PO Windows PowerShell transcripts)
| Gate | Evidence/result |
|---|---|
| Focused pytest T17 with fake AI client, no network | **14/14 PASS** |
| Full pytest including existing T11 and T16 | **50/50 PASS**, 1 Starlette deprecation warning |
| Backend compileall | **PASS** (earlier automatic gate) |
| Uvicorn real process with **temporary SQLite**, no key | **PASS** startup/shutdown; `/api/health`: `status=ok`, `classifier=phobert_b` |
| Guest `POST /api/chat` | **401**, observed in Uvicorn access log |
| Authenticated user without key | **503**, observed in Uvicorn access log |
| Frontend REAL build after draggable patch | **PASS**, 72 modules |
| Frontend MOCK build after draggable patch | **PASS**, 72 modules |
| Mock manual 375px & drag/drop/reload/Esc/link | **PASS per PO manual confirmation** |
| Regression BOI_CANH_DU_AN.md §7 | **7/7 per PO manual attestation in agreed test scope**; mock is not independent PhoBERT classification evidence |
| `git diff --check` | **PASS** (LF/CRLF warnings only) |
| Scope/forbidden file checks | **SCOPE_CHECK=PASS**, `FORBIDDEN_FILES=NONE` |
| Pattern-based secret scan | **SECRET_SCAN=PASS**; regex scan is not a security guarantee |
| Backend REAL Gemini with personal API key | **NOT_RUN / AC-02 PENDING PO_REVIEW** |

## Acceptance Criteria — DEV evidence status
| AC | Evidence | DEV status |
|---|---|---|
| AC-01 | Uvicorn guest 401; unauthenticated widget prompts login in mock | SUPPORTED |
| AC-02 | Tool and movie-link implementation present, but no Gemini key in DEV | **PENDING PO_REVIEW — real key** |
| AC-03 | Fake-client tool request, tool result and three-loop cap in test suite | SUPPORTED (14 focused tests) |
| AC-04 | Invalid messages (count/length/role/final assistant) covered by tests | SUPPORTED |
| AC-05 | Per-user minute quota and isolation covered by tests | SUPPORTED |
| AC-06 | Uvicorn + temp SQLite without key returns health ok/503; fake provider errors tested | SUPPORTED; `classifier=phobert_b` is expected after T10 |
| AC-07 | Only movie/showtime/price read-only tools; no booking/user/comment tool | IMPLEMENTED; Claude to inspect independently |
| AC-08 | MOCK chat sends and receives `{reply,movies}`; browser observed | SUPPORTED |
| AC-09 | 375px mock, mouse/keyboard open/close, drag/edge snap, seat/checkout usability per PO | SUPPORTED by manual PO test; Claude to reproduce |
| AC-10 | Only added `openai==3.29.0`; `.env`/DB/model excluded in changed files | SUPPORTED |
| AC-11 | 50/50 full pytest + 7/7 checklist with scope qualification | SUPPORTED; Claude to independently verify |

## Regression checklist (BOI_CANH_DU_AN.md §7)
1. Home/poster interaction — **PO attested**.
2. Genre/topic filters and `meo muop` search — **PO attested**.
3. Register/login/showtime redirect — **PO attested, mock**.
4. Book two seats / seat status / My Tickets — **PO attested, mock**.
5. Negative comment and admin review — **PO attested within mock; real PhoBERT decision not independently demonstrated by mock**.
6. Backend health — **verified by real Uvicorn + temporary SQLite (`phobert_b`, reflecting approved T10 default)**.
7. Mock full flow/chat — **PO attested**.

## Security, Scope and Limitations
- No provider key or provider URL/error is disclosed by the API response; synthetic clients used for pytest; backend starts with empty key.
- Real DB was never a gate target; temporary SQLite created and cleaned. PO confirmed `backend/firefly.db` exists after cleanup (existence only, no checksum).
- No `.env`/models/database in changed Git files; scope/script checks passed. Seven T16 Claude TODOs are not resolved or rewritten by this task.
- AC-02 cannot be declared PASS without PO's credentialed real-Gemini test; free quota must be checked in AI Studio account. Model hallucination may still occur.

## Handoff
**T17 = CLAUDE_REVIEW requested.** Independent Claude reviewer must inspect actual branch, run tests/gates and provide PASS / PASS_WITH_TODO / FAIL. Codex has **not** self-reviewed, approved, merged, or closed T17.
