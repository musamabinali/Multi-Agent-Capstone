# MAKPA — Frontend Review (audit vs `Frontend Build.md`)

Date: 2026-10-03. Scope: `src/makpa/api/server.py`, `apps/web/`, `tests/test_api_server.py`.
Method: read every adapter + UI path against spec §§1/9/11/12, then fixed what was genuinely wrong.

## Verdict

Ship the adapter + UI for internal use. Five genuine issues found and fixed (R-01…R-05).
Three deferred items remain (D-01…D-03) — all documented, none blocking internal use.

## Fixed

### R-01 — Interrupt `kind` collapsed to `"confirm"` for single gates (backend)
- **Found:** `_thread_state` resolved `kind` as `preview.get("action", preview.get("gate", "confirm"))`,
  but single mutating gates (GitHub confirm, Google confirm) carry neither key — their preview is
  `{"payload_preview", "question", "hint"}`. Composite gates carry `gate: 1 | 2` and were fine.
- **Risk:** frontend could never distinguish a calendar create from a GitHub write on single-gate flows.
- **Fix:** `src/makpa/api/server.py::_interrupt_kind` — `action` → `gate` → first
  `payload_preview[].tool` → `"confirm"`. Covered by `test_interrupt_kind_derives_from_payload_preview`.
- **Files:** `src/makpa/api/server.py`, `tests/test_api_server.py`.

### R-02 — Modal titles ignored the payload (frontend)
- **Found:** `ConfirmationModal` titled from `kind` only, so single-gate flows rendered the generic
  `"Confirm action"` instead of the wireframe titles (§6.3/§6.4).
- **Fix:** `previewTools()` reads `payload.payload_preview[].tool`; titles now resolve to
  `Confirm calendar event / Confirm email send / Confirm GitHub write / Confirm action`.
  Rollback visibility also keys off `gmail_send_message` in the payload, not just `kind == "2"`.
- **Files:** `components/modals/ConfirmationModal.tsx`, `tests/component/InterruptKind.test.tsx` (3 new tests).

### R-03 — `InterruptPayload.payload` type lied about its shape (frontend)
- **Found:** typed as `Record<string, string | number | boolean | null>`, but real previews contain
  `payload_preview` plan lists. Strict mode hid the mismatch behind casts.
- **Fix:** widened to `Record<string, unknown>`; narrowed the two casts in `useChatStream`.
- **Files:** `lib/types/index.ts`, `lib/hooks/useChatStream.ts`.

### R-04 — Error-card retry sent the literal string `"retry"` (frontend)
- **Found:** `ThreadPage` `onRetry` re-sent `"retry"` as the user query.
- **Fix:** retry re-sends the thread's last user message.
- **Files:** `app/chat/[threadId]/page.tsx`.

### R-05 — E2E suite was placeholder assertions (tests)
- **Found:** `flows.spec.ts` asserted static text only; never touched interrupts, rollback, or resume payloads.
- **Fix:** rewritten with `page.route` mocks — empty-state + mode honesty, gate-2 modal with disabled-until-acknowledge
  rollback asserting `{"rollback":true}`, decline path asserting `{"confirm":false}`, health MCP panel.
  Runs without a backend; live-server pass still pending (D-02).
- **Files:** `tests/e2e/flows.spec.ts`.

## Also fixed along the way

- Added missing `lib/hooks/useHealth.ts` + `lib/hooks/useThread.ts` (§10.1 file structure) and migrated
  all four pages onto them.
- Added the optional `/docs` hub page (IA map now complete: `/`, `/chat`, `/chat/[threadId]`,
  `/settings`, `/health`, `/docs`).
- `biome.json` now ignores `.next/**`, `out/**` (build output was being linted after `next build`).

## Verified after fixes (web-gate close-out)

| Gate | Result |
|------|--------|
| `ruff check src/ tests/ scripts/` | clean |
| `mypy` backend (strict, incl. new `extract_structured` + mock store) | clean |
| `pytest tests/test_api_server.py tests/test_api_parity.py -q` | 15 passed (6 + 9) |
| `biome check .` | clean (55 files) |
| `tsc --noEmit` (strict + `noUncheckedIndexedAccess`) | clean |
| `vitest run` | 26 passed |
| `next build` | 8 routes green |
| `pnpm test:a11y` | 4/4 screens, 0 critical/serious |
| live `playwright test tests/e2e/live.spec.ts` | 4/4 green, zero mocked routes |

## Deferred → closed in the web-gate pass (2026-10-03)

- **D-01 — axe audit: CLOSED.** `@axe-core/playwright` added; `tests/a11y/screens.spec.ts` covers empty chat,
  RAG thread, open modal, settings; `pnpm test:a11y` exits 0 with zero critical/serious on all four.
  Before: 4 screens × `color-contrast` serious. Fix: `--primary` → `#60A5FA` for text/links, new
  `--primary-solid #1D4ED8` for button fills, `--success-strong`/`--info-strong` solid pills, agent pills
  restyled to outlined surface + accent text. Recorded in `BUILD.md` §7.4.
- **D-02 — Playwright against live servers: CLOSED.** `tests/e2e/live.spec.ts` runs 4 flows against real
  backend `:8001` + frontend `:3000` with zero mocked routes (RAG citations+drawer, GitHub PR 7, composite
  two-gate ids, gate-2 rollback) — 4/4 green. Harness: `scripts/serve_web.py` (mock-backed stack, child env
  only, `.env` untouched) + `global-setup.ts` (fail-fast + RAG warmup). Mocked `flows.spec.ts` kept for
  payload-shape assertions only. Live-LLM turns take 30–75s from here and Gemini free tier is 429-exhausted,
  so the harness runs mock LLM; live inference stays proven by FLAG-A and the parity live-SSE test.
  Decline-at-gate-1 and kill-backend-mid-stream remain uncovered (optional per gate) — mocked decline payload
  is asserted in `flows.spec.ts`.
- **D-03 — `StructuredResultTable` recall: CLOSED.** Ids now thread from `tool_results` via
  `supervisor/graph.py::extract_structured` → `_worker_update.summary["structured"]` →
  `agent_end.structured` → typed `StructuredResult` state → data-driven table with a `no structured result`
  fallback. Zero regex remains (verified by search). Along the way this exposed and fixed a genuine mock bug:
  mock `calendar_create_event` never stored the event, so gate-2 rollback `update` always failed with
  `event not found` — the mock store is now file-backed (`data/mock_calendar.json`, atomic tmp+rename,
  fixed-id upsert; Gmail mock needed no change). Environment note: each MCP tool call can spawn a fresh
  server subprocess, which is why in-memory fixtures could never work here.

## Correction — prior rollback verification was weaker than claimed

Prior rollback verification (Phase 3 acceptance, `GRADER_CHECKLIST.md`, `VIVA_QA.md`) relied on a
mock that did not persist state: mock `calendar_create_event` returned a fixed `evt-mock-100` without
storing it, so any `calendar_update_event` for that id failed with `event not found` — and the mocked
unit tests passed anyway because they stubbed the service layer instead of exercising create→update.
Live e2e on 2026-10-04 exposed this: the gate-2 rollback flow ended in `error`, not `rolled_back`.
The mock now uses a file-backed store (`data/mock_calendar.json`, tmp+rename, fixed-id upsert) and the
rollback path is verified live (`live.spec.ts`: gate-2 Rollback → event cancelled). Earlier claims stand
corrected by this entry; nothing was quietly fixed underneath.

## Anti-pattern spot-check (§12)

- No hidden attribution: routing card + per-agent cards always render. Pass.
- No supervisor/sub-agent status conflation: `overallStatus` line separate from per-agent pills. Pass.
- No auto-confirm: modal requires checkbox + explicit click, even in demo. Pass.
- SSE only, no WebSockets. Pass.
- No raw JSON in thread: payloads render in modal `<dl>` / structured table only. Pass.
- Partial ≠ success: `PartialAvailabilityNotice` is a `role="alert"` warning. Pass.
- Scroll preserved: tokens append in place; modal opens without navigation. Pass.
- Status pills, not spinners. Pass.
- No invented endpoints: all 9 map 1:1 to existing backend functions. Pass.
- Downgrade banner always rendered when downgrades exist. Pass.
- Streaming only via `useChatStream` with `AbortController` cleanup. Pass.
- Keys: thread ids + `label-value` pairs; chat turns key on role+content (collides only on byte-identical
  consecutive messages — accepted, noted).

## Known-honest behaviors (by design, kept)

- `agent_token` deltas chunk final per-agent answers at 400 chars (supervisor has no token streaming);
  post-stream `GET /api/threads/{id}` reconciles authoritative citations/ids.
- `event_stream` is a sync generator (Starlette runs it in its threadpool); fine for internal use.
- Modal focus moves to the dialog on open + Escape cancels; full focus-trap cycle is D-01 scope.
