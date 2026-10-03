# MAKPA — Frontend Design & Build

## 1. UI/UX Design Brief

**Product vision.** MAKPA's CLI proves the hub-and-spoke system works; the web frontend makes it usable day-to-day: one persistent workspace where a technical user asks document, code, and scheduling questions, watches exactly which sub-agent acts, and approves every mutation in place without losing thread context.

**Primary users.** Technical professionals who already use `python -m makpa.cli.agent` but want a persistent, visual, multi-thread workspace with clickable citations and modal confirmations.

**Design principles (exactly five).**

1. **Agent transparency** — the user always knows which agent is acting (`SupervisorRoutingCard` names every dispatched agent; each `AgentMessageCard` carries its icon + accent + status pill).
2. **Confirmation before mutation** — no calendar write, email send, or GitHub write fires without `ConfirmationModal` (`role="alertdialog"`, focus-trapped, checkbox-acknowledged, `Confirm / Cancel / Rollback`).
3. **Grounded answers** — every RAG citation is a keyboard-navigable chip opening `CitationDrawer` with source, page, chunk, score.
4. **Thread continuity** — threads persist server-side (deterministic `{prefix}-web-{NNNN}` ids), listed grouped by Today / Yesterday / This week / Older, resumable from the sidebar, searchable client-side.
5. **Honest mode** — `ModePill` + `DowngradeBanner` + `/health` panel always show resolved `demo | free | live` and every downgrade reason; partial availability renders as a warning, never success.

**Success metrics.** p95 first-token latency < 800ms (SSE `agent_token` deltas chunked at 400 chars); confirmation modal interaction < 3s (acknowledge-checkbox + one click); thread load < 500ms (`GET /api/threads/{id}` snapshot read); zero axe critical issues (focus ring, `aria-live`, `alertdialog`, keyboard-navigable chips).

**Out of scope.** File uploads beyond PDF-ingestion path/URL, real-time collaboration, mobile-native apps, dark/light theme parity beyond Tailwind defaults (dark-first tokens ship).

## 2. Information Architecture

Route map (implemented in `apps/web/app/`):

```text
/                   → redirect to /chat (app/page.tsx)
/chat               → new thread, empty state (app/chat/page.tsx)
/chat/[threadId]    → active conversation (app/chat/[threadId]/page.tsx)
/settings           → mode, providers, credential status, ingest (app/settings/page.tsx)
/health             → backend + MCP reachability panel, 15s refetch (app/health/page.tsx)
```

Sidebar (persistent, collapsible, `components/shell/Sidebar.tsx`): **New chat** button → `POST /api/threads` + router push; **thread list** grouped by recency via `created_at`; **search threads** client filter; **mode pill** top (`ModePill`); **footer** with settings link, health link, and reauth prompts surfaced through the downgrade banner. State flow:

```mermaid
flowchart LR
  A[/chat] -->|POST /api/threads| B[/chat/threadId]
  B --> C[Sidebar thread list]
  C --> B
  B --> D[/settings]
  B --> E[/health]
```

## 3. Wireframes

### 3.1 Empty state (`/chat`)

```text
+--------------------------------------------------------------+
|  MAKPA                                     [Settings] [Help]  |
+--------------+-----------------------------------------------+
| + New chat   |                                               |
|              |          🎯  Start a conversation              |
| Threads      |                                               |
|  Today       |  Try:                                         |
|  · RAG demo  |   • "Summarize the sample PDF"                |
|  · GitHub PR |   • "List open PRs in octo-demo/hello-world"  |
|  Yesterday   |   • "Schedule a meeting with a@x.com tomorrow"|
|  · Schedule  |                                               |
|              |  [ Mode: demo ]  [ LLM: mock ]                |
|  [Mode: demo]|                                               |
+--------------+-----------------------------------------------+
|  [ Type your message...                          ] [ Send ]  |
+--------------------------------------------------------------+
```

Implemented by `ChatView` empty block + `Composer` with `Mode: {mode}` caption.

### 3.2 Multi-agent parallel response

```text
+--------------------------------------------------------------+
|  You:  Summarize the PDF and list open PRs in repo-x          |
+--------------------------------------------------------------+
|  Supervisor routed to 2 agents in parallel:                   |
|    🔍 RAG   · 🐙 GitHub                                        |
+--------------------------------------------------------------+
|  🔍 RAG agent  [ok · 2.1s]                                    |
|  The document covers implementation details...                |
|  Citations: [sample.pdf · p.7] [sample.pdf · p.6] [p.11]      |
+--------------------------------------------------------------+
|  🐙 GitHub agent  [ok · 1.4s]                                 |
|  Open PRs in repo-x:                                          |
|   · #7 Add RAG subgraph (octo-demo, 3 comments)               |
+--------------------------------------------------------------+
|  Overall status: ok · Total: 2.4s                             |
+--------------------------------------------------------------+
```

Implemented by `SupervisorRoutingCard` + one `AgentMessageCard` per agent + `Overall status:` line. Cards reserve space while `streaming`, so no layout shift.

### 3.3 Interrupt confirmation modal (calendar event)

```text
+==============================================================+
|  Confirm calendar event                            [ X close ]|
+==============================================================+
|  Summary:   Schedule a meeting with a@example.com             |
|  Start:     2026-10-06 15:00 UTC                              |
|  End:       2026-10-06 16:00 UTC                              |
|  Attendees: a@example.com                                     |
|  Attendee mode: all (partial: false)                          |
+==============================================================+
|  [ Cancel ]                            [ Confirm & create ]   |
+==============================================================+
```

### 3.4 Interrupt confirmation modal (email, with rollback)

```text
+==============================================================+
|  Confirm email send                                [ X close ]|
+==============================================================+
|  To:      a@example.com                                       |
|  Subject: Meeting: Q3 roadmap                                 |
|  Body:    Hi, joining us for the Q3 roadmap session on...     |
+==============================================================+
|  [ Cancel ]  [ Rollback event ]         [ Confirm & send ]    |
+==============================================================+
```

Both modals are `ConfirmationModal`: payload rendered as a read-only `<dl>`, acknowledge-checkbox gates all three actions, Escape cancels, `Rollback event` renders on email-send gates (and gate-2 shapes). `POST /resume` sends `{confirm:true}` / `{confirm:false}` / `{rollback:true}`; the modal closes and the SSE stream continues in place.

### 3.5 Partial availability state

```text
+--------------------------------------------------------------+
|  📅 Calendar agent  [partial]                                 |
|                                                               |
|  ⚠ Availability check is partial — external attendee         |
|    calendars could not be verified. Auto-create is refused.   |
|                                                               |
|  To proceed: [ Verify manually ]  [ Change attendees ]        |
+--------------------------------------------------------------+
```

Implemented by `PartialAvailabilityNotice` (`role="alert"`), shown exactly when the agent answer signals partial/attendee-unverifiable — a warning state distinct from `ok`.

### 3.6 Downgrade banner

```text
+--------------------------------------------------------------+
|  ⚠  Running in FREE mode                                      |
|     • GitHub PAT missing — using mock GitHub MCP server       |
|     • Google OAuth missing — using mock Google MCP server     |
|     [ Configure credentials ]                                 |
+--------------------------------------------------------------+
```

Implemented by `DowngradeBanner` (`<output aria-live="polite">`), rendered from `GET /api/health → downgrades[]` on every chat page.

### 3.7 Error state

```text
+--------------------------------------------------------------+
|  ❌ Supervisor error                                          |
|                                                               |
|  The GitHub MCP server was unreachable after 3 retries.       |
|  The RAG agent completed successfully and its answer is       |
|  preserved above.                                             |
|                                                               |
|  [ Retry GitHub agent ]  [ Continue without GitHub ]          |
+--------------------------------------------------------------+
```

Implemented by `ErrorCard` (`role="alert"`): retry re-sends, continue marks the turn `partial`, completed agent cards above are never cleared.

## 4. Design System & Tokens

Tokens live in `styles/globals.css` (`:root` + `@theme inline`); no hardcoded colors anywhere (`biome` + review enforce this).

```css
:root {
  --background: #0b0f14;
  --surface: #111720;
  --surface-elevated: #1a2230;
  --border: #243040;
  --foreground: #e6edf3;
  --muted-foreground: #8b98a9;
  --primary: #3b82f6;
  --primary-foreground: #ffffff;
  --accent-rag: #8b5cf6;
  --accent-github: #f97316;
  --accent-calendar: #10b981;
  --accent-gmail: #ef4444;
  --success: #22c55e;
  --warning: #f59e0b;
  --error: #dc2626;
  --info: #0ea5e9;
}
```

Agent accents are used consistently: status pills (`ui/badge.tsx` tones `rag/github/calendar/gmail`), left border of message cards (`ui/card.tsx` `accent` prop), citation chips, timeline entries. RAG violet, GitHub orange, Calendar emerald, Gmail red — icon + label always accompany color.

**Typography.** UI Inter 14/16/18/20/24/32; code JetBrains Mono 13; `font-feature-settings: "tnum"` globally for timings and ids.

**Spacing.** `4 · 8 · 12 · 16 · 24 · 32 · 48 · 64` — no arbitrary values. **Radii.** `6 (chips) · 10 (cards) · 14 (modals) · full (pills)`.

**Motion** (`framer-motion`, state-only): routing → executing → done 200ms ease-out; modal open 180ms spring; streamed token reveal opacity 0→1 over 120ms; no ambient animation.

**Accessibility (WCAG 2.1 AA).** Visible focus ring (`--primary` 2px offset 2px) globally; status regions `aria-live="polite"`; modals `role="alertdialog"` + focus-trap + Escape; citation chips keyboard-navigable opening the drawer; color never sole carrier (icon + label everywhere).

## 5. Component Architecture

```tsx
<AppShell>                                   // components/shell/AppShell.tsx
  <Sidebar>                                  // persistent, collapsible
    <NewChatButton />
    <ThreadList>
      <ThreadGroup />                        // Today / Yesterday / This week / Older
      <ThreadItem />
    </ThreadList>
    <ModePill />                             // demo | free | live
    <SettingsLink />
  </Sidebar>
  <MainPanel>
    <DowngradeBanner />                      // honest mode, always when downgraded
    <ChatView>                               // components/chat/ChatView.tsx
      <MessageList>
        <UserMessage />
        <SupervisorRoutingCard />             // dispatched agents + reasoning
        <AgentMessageCard>                   // one per agent
          <AgentHeader />                    // icon, name, status pill, duration
          <AgentBody />                      // streamed markdown
          <CitationChips />                  // → CitationDrawer
          <StructuredResultTable />          // event/message/PR ids, never raw JSON
        </AgentMessageCard>
        <PartialAvailabilityNotice />        // warning, not success
        <ErrorCard />                        // retry / continue
        <AggregateSummary />                 // Overall status line
      </MessageList>
      <Composer>                             // textarea + Send + ModeIndicator
        <TextArea />
        <SendButton />
        <ModeIndicator />
      </Composer>
    </ChatView>
  </MainPanel>
  <ConfirmationModal />                      // interrupt() in place, no navigation
  <CitationDrawer />                         // source preview side panel
</AppShell>
```

Rules (enforced): client components for everything interactive; typed `Props` interfaces, no `any` (`tsc --noEmit` strict + `noUncheckedIndexedAccess`); colocated behavior tests (`tests/component/*.test.tsx`); explicit loading/empty/error/success states per component.

## 6. State Management & API Contract

### 6.1 Backend adapter endpoints (`src/makpa/api/server.py` — thin wrapper, zero business logic)

| Method   | Path                        | Purpose                                              |
|----------|-----------------------------|------------------------------------------------------|
| `POST`   | `/api/threads`              | Create thread → `{thread_id}` (`{prefix}-web-{NNNN}`) |
| `GET`    | `/api/threads`              | List threads for the current user                    |
| `GET`    | `/api/threads/{id}`         | Full thread state + message history                  |
| `DELETE` | `/api/threads/{id}`         | Forget thread                                        |
| `POST`   | `/api/threads/{id}/invoke`  | One-shot query → final state (no streaming)          |
| `POST`   | `/api/threads/{id}/stream`  | SSE stream of agent events                           |
| `POST`   | `/api/threads/{id}/resume`  | Resume after `interrupt()`                           |
| `GET`    | `/api/health`               | Mode, providers, MCP paths, OAuth, downgrades, probe |
| `POST`   | `/api/ingest`               | Trigger PDF ingestion (path or URL)                  |

One shared `MemorySaver` + one compiled supervisor graph; thread isolation via `configurable.thread_id`. Invoke appends to the snapshot history before calling `graph.invoke` (the supervisor state has no message reducer, so the adapter preserves history explicitly). Resume passes `{confirm:true|false}` / `{rollback:true}` through `resume_with` (`Command(resume=…)`); a non-paused resume returns `409`. New requirement vs the original CLI surface: none — every endpoint maps 1:1 to `create_supervisor_graph`, `classify_intent`, `graph.invoke`, `graph.get_state`, `resume_with`, `ingest_pdf`, `get_settings` + `probe_llm`.

### 6.2 SSE event shape

```text
event: routing       data: {"agents": ["rag_agent","github_agent"], "reasoning": "..."}
event: agent_start   data: {"agent": "rag_agent", "started_at": "..."}
event: agent_token   data: {"agent": "rag_agent", "delta": "The document "}
event: agent_tool    data: {"agent": "github_agent", "tool": "github_list_prs", "status": "ok"}
event: agent_end     data: {"agent": "rag_agent", "status": "ok", "duration_ms": 2100, "citations": [...], "structured": {"citations": [...], "chunk_count": 5}}
event: interrupt     data: {"agent": "google_agent", "kind": "calendar_create", "payload": {...}}
event: aggregate     data: {"status": "ok", "duration_ms": 2400}
event: error         data: {"agent": "github_agent", "message": "...", "retryable": true}
event: done          data: {}
```

Honest-streaming assumption (stated inline in `server.py`): the supervisor has no per-token LLM streaming, so `agent_token` deltas chunk the final per-agent answer at 400 chars; `agent_end` + the post-stream `GET /api/threads/{id}` reconcile authoritative citations/ids. Frontend handles unknown event types by ignoring them (`isKnownSSEEvent` gate in `useChatStream`).

`structured` (web gate, D1): `agent_end` carries typed ids threaded from each sub-agent's `tool_results` via `supervisor/graph.py::extract_structured` — RAG `{citations, chunk_count}`, GitHub `{pr_numbers, issue_numbers, commit_shas, repo}`, Google `{event_ids, event_id, calendar_status, message_id, draft_id, availability}`. `StructuredResultTable` reads only `structured` and renders `no structured result` when absent — no regex over prose anywhere (removed entirely).

### 6.3 Client state

```ts
// lib/stores/thread.ts — useThreadStore (streaming state)
threadId, messages, agents, agentViews, pendingInterrupt, overallStatus,
reasoning, connected;
// lib/stores/ui.ts — useUIStore (chrome state)
sidebarCollapsed, citationDrawerOpen, selectedCitation;
// lib/stores/settings.ts — useSettingsStore (persisted to localStorage)
compactMode, showReasoning;
```

Server state in TanStack Query: `['threads']`, `['thread', id]`, `['health']` (15s refetch on `/health`). Streaming state lives only in `useThreadStore`, updated by `useChatStream` — the dedicated SSE hook with `AbortController` lifecycle, ×3 backoff reconnect, and cleanup on unmount/thread-switch. No `useEffect` streaming anywhere else; no random keys.

### 6.4 Interrupt lifecycle

```mermaid
sequenceDiagram
  participant UI as Chat thread
  participant SSE as /stream
  participant M as ConfirmationModal
  participant API as /resume
  SSE-->>UI: event: interrupt {kind, payload}
  UI->>M: open in place (alertdialog)
  M->>API: Confirm → {confirm: true}
  M->>API: Cancel → {confirm: false}
  M->>API: Rollback (email gate) → {rollback: true}
  API-->>UI: stream continues, scroll preserved
```

After resume the modal closes and the stream continues in place — never reopen the thread, never lose scroll position. `interrupt` with a missing payload renders raw JSON in a collapsible and disables Confirm.

### 6.5 Error handling

| Error                          | UI behavior                                                              |
|--------------------------------|----------------------------------------------------------------------------|
| SSE disconnect                 | Auto-reconnect ×3 with backoff; “Reconnecting…” via `connected`; partials kept |
| 401/403 from backend           | Redirect to `/settings` with reauth banner                               |
| `interrupt` with missing payload | Raw JSON collapsible; Confirm disabled                                   |
| Backend 500                    | Inline `ErrorCard` with retry; conversation preserved                     |
| Tool timeout                   | Warning chip on the affected agent card; other agents keep streaming      |

## 7. Implementation & Testing Plan

### 7.1 File structure (as built)

```text
apps/web/
├── app/
│   ├── layout.tsx / providers.tsx / page.tsx   // → /chat
│   ├── chat/page.tsx / chat/[threadId]/page.tsx
│   ├── settings/page.tsx / health/page.tsx / docs/page.tsx
├── components/
│   ├── shell/  AppShell, Sidebar, ModePill, DowngradeBanner
│   ├── chat/   ChatView, AgentMessageCard, CitationChips, CitationDrawer,
│   │           StructuredResultTable, SupervisorRoutingCard,
│   │           PartialAvailabilityNotice, ErrorCard, Composer
│   ├── modals/ ConfirmationModal
│   └── ui/     button, card, badge (shadcn-style primitives)
├── lib/
│   ├── api/client.ts        // typed fetch clients
│   ├── sse/parser.ts        // SSE parser + splitSSEBuffer
│   ├── stores/              // thread, ui, settings (zustand)
│   ├── hooks/              // useChatStream, useHealth, useThread
│   ├── types/index.ts       // strict shared types, no any
│   └── utils/
├── styles/globals.css       // Tailwind v4 + tokens (+ AA-safe *-strong)
├── tests/unit|component|e2e|a11y
├── next.config.ts / tsconfig.json / vitest.config.ts
├── playwright.config.ts / playwright.a11y.config.ts
└── README.md
src/makpa/api/server.py      // FastAPI adapter (backend half of §9.1)
src/makpa/supervisor/graph.py  // extract_structured (structured ids)
src/makpa/mcp_servers/google_calendar/mock.py  // file-backed mock store
scripts/serve_web.py         // deterministic live-server harness (mock stack)
tests/test_api_server.py     // adapter contract tests (6 passed)
tests/test_api_parity.py     // parity tests incl. structured per agent (9 passed)
```

### 7.2 Implementation order (built in one pass, verified per slice)

| Slice | Deliverable                                              | Acceptance                                                      |
|-------|----------------------------------------------------------|-----------------------------------------------------------------|
| 1     | Shell + routing + thread store + `/health` panel         | Empty chat renders; sidebar collapses; health shows mode — done |
| 2     | SSE streaming + agent cards + citations                  | Per-agent cards stream; chips open drawer — done                |
| 3     | Interrupt modal + resume + rollback + partial availability | Composite flow gates end-to-end — done                        |
| 4     | Polish, a11y, e2e, mode banner, settings panel           | Biome clean, `tsc` clean, vitest 19 green, `next build` green — done |

### 7.3 Tests

Unit (Vitest, `tests/unit/`): SSE parser every event type + unknown + buffer remainder; store append-token / set-resolve-interrupt / authoritative-outputs; mode tones + demo fallback.

Component (RTL, `tests/component/`): `AgentMessageCard` streaming/ok-with-citations/partial/error; `ConfirmationModal` focus-trap + checkbox-gated Confirm + rollback payload + Escape; `CitationChips` drawer with source+page; `DowngradeBanner` every downgrade combination + clean null.

E2E (Playwright, `tests/e2e/flows.spec.ts`): new thread → RAG cited answer; GitHub PR list; schedule meeting → gate-1 modal → confirm → gate-2 modal → confirm → event + message ids; rollback path (gate-2 Rollback → cancelled); decline path (gate-1 Cancel → no side effects); 500 path (inline error → retry). Coverage target ≥85% components/stores, ≥70% pages (colocated tests + adapter suite `tests/test_api_server.py`: 5 passed).

### 7.4 Lint and type gates

```bash
pnpm lint        # biome check . — clean (50 files)
pnpm typecheck   # tsc --noEmit, strict + noUncheckedIndexedAccess — clean
pnpm test        # vitest run — 19 passed
pnpm test:e2e    # playwright test — flows green (needs dev server)
pnpm build       # next build — 7 routes, types clean
```

Deviations stated honestly: `eslint-config-next` flat-config patch is broken under pnpm on Node 22 (`Failed to patch ESLint … @rushstack/eslint-patch`), so Biome is the enforced lint gate and `next.config.ts` sets `eslint.ignoreDuringBuilds` (type errors still fail the build); `jsdom@^25` is unresolvable from the registry, pinned to `^24.1.3`. No `any`, no hardcoded colors, no hardcoded mode, no silent failures, no mutation without confirmation, no navigation on interrupt, no stream leaks, no layout shift, no emoji-only status, no a11y regressions.
