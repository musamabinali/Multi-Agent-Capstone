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

## Verified after fixes

| Gate | Result |
|------|--------|
| `ruff check src/makpa/api/ tests/test_api_server.py` | clean |
| `mypy src/makpa/api --config-file=mypy.ini --follow-imports=skip` | clean (2 files) |
| `pytest tests/test_api_server.py -q` | 6 passed |
| `biome check .` | clean (54 files) |
| `tsc --noEmit` (strict + `noUncheckedIndexedAccess`) | clean |
| `vitest run` | 22 passed |
| `next build` | 8 routes green |

## Deferred (honest, not hidden)

- **D-01 — axe audit.** `@axe-core/playwright` not installed; no automated a11y run yet. Mitigation: biome
  `a11y` rules enforced (button types, semantic elements), focus ring/`aria-live`/`alertdialog`/keyboard chips
  implemented per §7.6. Run before any external release.
- **D-02 — Playwright against live servers.** E2E currently mocks the adapter. Still needed: backend `:8001` +
  `pnpm dev` pass covering RAG cited answer, composite two-gate confirm, and gate-2 rollback end to end.
- **D-03 — `StructuredResultTable` recall.** It regexes ids out of answer text; sub-agent summaries carry tool
  names/statuses but not always full payloads, so the table can be empty when the answer prose omits ids.
  The authoritative ids are always present in `agent_outputs` API responses — a future pass should thread the
  structured fields through instead of parsing prose.

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
