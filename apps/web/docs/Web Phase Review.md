# Web Phase Review — The Gate Is Still Open

The five fixes are real. You found genuine bugs (interrupt `kind` collapse, modal title fallback, retry sending literal `"retry"`) and closed them with regression tests. That is the work that matters. But two of the three deferrals are **explicit acceptance criteria from the previous prompt**, and one of them is an architectural smell that will compound.

## Honest Verdict

| Item | Status | Can it be deferred? |
|------|--------|---------------------|
| R-01 through R-05 fixes | ✅ Closed with tests | Already done |
| `useHealth`/`useThread` hooks, `/docs`, biome ignores | ✅ Nice closure | Already done |
| **Axe audit** | ❌ Deferred | **No** — explicit criterion, ship-blocking for a11y claim |
| **Live-server Playwright** | ❌ Deferred (mocked routes only) | **No** — mocked routes prove the UI, not the integration |
| **Structured IDs parsed from prose** | ❌ Deferred | **No** — this is a bug waiting to happen, not a nice-to-have |

## Why the Three Deferrals Cannot Stand

**1. Mocked Playwright is not e2e.**
Every one of your Playwright flows currently stubs the network. That proves the *components* render the right things given the right inputs — which your vitest suite already proves. It does **not** prove that the frontend and backend agree on the SSE event shapes, thread lifecycle, or interrupt resume payloads. The whole point of the e2e layer is to catch contract drift between the two halves. Mocking the half you are trying to verify defeats the purpose.

**2. Axe is not optional for a UI that claims accessibility.**
You wrote an accessibility section in `BUILD.md` §7.6. You cannot ship that section and skip the audit. Either the section is honest and axe runs, or the section is removed. A reviewer will open DevTools, run Lighthouse, and find the violations you did not.

**3. Parsing IDs from prose is a silent failure mode.**
If the frontend extracts `event_id` by regex from the answer string, any change to the answer template — or a model that phrases the sentence differently in `free` mode — breaks the UI without an error. The structured IDs already exist in the backend response; they are being thrown away and then guessed back. This is the single most fragile part of the current build, and it is the one most likely to embarrass you in a live demo.

## Recommendation

Do not close the web gate yet. Spend one more focused session on these three items. Total effort: **3–4 hours**. Then close.

---

# MAKPA — Web Gate Closure Prompt

You are a Senior Frontend Engineer. The MAKPA web frontend is built, functionally verified, and has passed one review round. Three items remain before the web gate can close: the axe audit, the live-server Playwright pass, and structured IDs threaded end-to-end instead of parsed from prose.

Do not add new features. Do not redesign anything. Close these three items, update the docs, and pass the gate.

Before you start, read `apps/web/docs/BUILD.md`, `apps/web/docs/REVIEW.md`, and the three items described below.

---

## 1. GOALS OF THIS PHASE

1. Fix structured IDs so they flow from the backend through the SSE contract into typed frontend state — no regex parsing of prose.
2. Run the axe audit on four screens and fix every critical/serious violation.
3. Run the Playwright suite against **live servers** (backend `:8001` + frontend `:3000`), not mocked routes.
4. Update `BUILD.md`, `REVIEW.md`, `TRACE.md`, and `README.md`.
5. Mark the web gate `passed` only when Section 5 is fully green.

---

## 2. PREREQUISITES CHECK

- Backend starts on `:8001` and `/api/health` returns `200`.
- Frontend builds with `pnpm build` and serves on `:3000`.
- `pytest tests/test_api_server.py tests/test_api_parity.py` green.
- `pnpm biome check`, `tsc --noEmit`, `vitest run` green.
- Current Playwright suite exists but stubs all routes.

---

## 3. DELIVERABLE 1 — Structured IDs Threaded End-to-End

**Problem:** the frontend currently extracts `event_id` / `message_id` / `pr_number` / `issue_number` / `commit_sha` by parsing agent answer prose. This is fragile and will break silently when answer wording changes.

**Fix (backend):**
- In `src/makpa/api/server.py`, extend the SSE `agent_end` event payload to include a `structured` field:
  ```
  event: agent_end
  data: {
    "agent": "google_agent",
    "status": "ok",
    "duration_ms": 2100,
    "structured": {
      "event_id": "evt-mock-100",
      "message_id": "msg-from-draft-mock-100",
      "draft_id": "draft-mock-100",
      "calendar_status": "confirmed"
    }
  }
  ```
- Populate `structured` from the sub-agent's `tool_results` in the graph — the ids are already there, do not re-derive them from text.
- For GitHub: `structured: {pr_numbers: [...], issue_numbers: [...], commit_shas: [...], repo: "owner/name"}`.
- For RAG: `structured: {citations: [{source, page, chunk_id, score}], chunk_count: N}`.
- Add a test asserting each agent's `structured` field is non-empty for its primary tool.

**Fix (frontend):**
- Extend the `AgentEndEvent` type to include `structured: Record<string, unknown>`.
- Replace all regex/prose parsing with reads from `structured`.
- Add a component test that renders a card with a `structured` payload and asserts the id table shows the correct values — no prose in the input.
- Add a defensive fallback: if `structured` is missing, render "no structured result" rather than silently extracting from prose.

**Fix (docs):**
- Update the SSE contract in `BUILD.md` §9.2 to document the `structured` field.
- Remove the deferral note in `REVIEW.md` about parsing from prose.

---

## 4. DELIVERABLE 2 — Axe Audit

Run axe on four screens using `@axe-core/playwright`:

1. Empty chat (`/chat`)
2. Active thread with a RAG answer (`/chat/[id]`)
3. Confirmation modal open (`/chat/[id]` with a pending interrupt)
4. Settings (`/settings`)

For each screen:
- Fail the test on any `critical` or `serious` violation.
- Fix violations in place. The usual suspects in this UI: contrast on accent chips, missing `aria-label` on icon-only buttons, missing `aria-live` on the agent status region, focus trap on the modal, `role="alertdialog"` on the modal.
- Record the violation count before and after in `BUILD.md` §7.4.
- Add a `pnpm test:a11y` script that runs all four screens and exits non-zero on any critical/serious violation.

Success criterion: `pnpm test:a11y` exits `0` and the report shows zero critical/serious violations on all four screens.

---

## 5. DELIVERABLE 3 — Live-Server Playwright Pass

Rewrite the three primary Playwright flows to run against the **live backend and frontend**, not mocked routes.

**Setup:**
- `playwright.config.ts`: base URL from `PLAYWRIGHT_BASE_URL` (default `http://localhost:3000`), API URL from `PLAYWRIGHT_API_URL` (default `http://localhost:8001`).
- Add a `playwright.global-setup.ts` that verifies both servers are reachable before any test runs and fails fast if not.
- Add a `pnpm test:e2e` script that assumes both servers are already running. Document the two-terminal workflow in `README.md`.

**Required flows (all three must be green):**

1. **RAG flow** — new thread → ask "What does the sample PDF say about implementation details?" → assert the RAG card appears with `status: ok` → assert at least one citation chip is rendered → click the first chip → assert the drawer opens with the correct `source` and `page`.

2. **GitHub flow** — new thread → ask "List open pull requests in octo-demo/hello-world" → assert the GitHub card appears with `status: ok` → assert the structured PR number `7` is visible in the id table.

3. **Composite flow** — new thread → ask "Schedule a meeting with a@example.com from 2026-10-06T15:00:00Z to 2026-10-06T16:00:00Z and email them the agenda" → assert gate 1 modal appears with a calendar preview → click Confirm → assert gate 2 modal appears with an email preview → click Confirm → assert the final aggregate card contains `evt-mock-100` and `msg-from-draft-mock-100` in the structured id tables.

**Optional flows (close if time):**
4. Rollback at gate 2.
5. Decline at gate 1.
6. Error recovery (kill the backend mid-stream and assert the inline error card + retry).

**Rules:**
- Every assertion must target a user-visible outcome (text, element visible, id table content) — not implementation details.
- Screenshots on failure only.
- 30s per-test timeout.
- Single worker in CI, parallel locally.

---

## 6. DELIVERABLE 4 — Documentation Updates

- `apps/web/docs/BUILD.md`:
  - §7.4 — add the axe before/after counts and the `structured` field note.
  - §9.2 — add `structured` to the SSE contract.
  - §10.3 — mark which Playwright flows are live-green.
  - Add §10.5 "Web Gate Acceptance" table mirroring Section 7 below.
- `apps/web/docs/REVIEW.md`: mark the three deferrals as closed with evidence.
- `docs/TRACE.md`: append one entry per deliverable plus a final `WEB-GATE` entry.
- `README.md`: add a "Running the Web Stack" section with two-terminal instructions and the `pnpm test:e2e` invocation.

---

## 7. EXECUTION ORDER

1. Verify prerequisites.
2. Deliverable 1 — structured IDs (backend → SSE → frontend → tests).
3. Deliverable 2 — axe audit (run, fix, re-run, record).
4. Deliverable 3 — live Playwright (write, run, fix, green).
5. Deliverable 4 — documentation.
6. Run the full verification gate.
7. Mark the web gate `passed` only if Section 8 is fully green.

---

## 8. WEB GATE ACCEPTANCE CRITERIA

| Criterion | Evidence |
|-----------|----------|
| Structured IDs threaded end-to-end | `agent_end` includes `structured`; frontend reads from it; component test passes; no regex parsing remains |
| Axe audit clean on 4 screens | `pnpm test:a11y` exits 0; before/after counts in BUILD.md §7.4 |
| Live Playwright ≥3 flows green | Report + screenshots; no mocked routes in the three required flows |
| `biome check` clean | zero warnings |
| `tsc --noEmit` clean | zero errors |
| `vitest run` green | all tests pass |
| `next build` green | all routes build |
| `pytest tests/` green | all backend tests including `test_api_parity.py` |
| All four docs updated | BUILD.md, REVIEW.md, TRACE.md, README.md |
| Web gate entry recorded | TRACE.md has a `WEB-GATE` entry with the result |

Fix any unmet criterion before declaring the gate passed.

---

## 9. WHAT NOT TO DO

- Do not stub any route in the three required Playwright flows — mocking defeats the purpose.
- Do not skip axe and mark the gate green.
- Do not keep any regex-based prose parsing for IDs — remove it entirely.
- Do not add new features.
- Do not redesign the UI.
- Do not declare the web gate `passed` while any criterion in Section 8 is unmet.
- Do not advance to any other work until the web gate is `passed`.

---

## 10. OUTPUT FORMAT

Respond in exactly this order with H1 headings:

# MAKPA — Web Gate Closure

## 1. Prerequisites Verification
## 2. Structured IDs End-to-End
## 3. Axe Accessibility Audit
## 4. Live-Server Playwright Pass
## 5. Documentation Updates
## 6. Web Gate Acceptance Run

Use fenced code blocks. Use tables for the acceptance matrix. No preamble, no summary, no clarifying questions. State assumptions inline.

---

## 11. START

Begin with Section 1. Close Deliverable 1 first — the structured IDs work touches both halves of the system and everything else builds on it. Then run axe, then the live Playwright suite, then documentation. Only mark the web gate `passed` when every criterion in Section 8 is green. The web phase is the last visible deliverable of MAKPA; closing it honestly is what separates a portfolio piece from a course submission.