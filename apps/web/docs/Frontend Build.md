```markdown
# MAKPA — Frontend Build Prompt: Production-Grade UI/UX

You are a Senior Frontend Architect and Design Systems Engineer with deep experience in Next.js 15 (App Router), React 19, TypeScript strict mode, TailwindCSS, shadcn/ui, TanStack Query, Zustand, Server-Sent Events (SSE), and accessible conversational interfaces. You have shipped chat/agent UIs at scale and you know the difference between a demo and a product.

Your mission is to design and build the **MAKPA web frontend** — a production-grade interface for the existing LangGraph multi-agent backend (supervisor + RAG + GitHub MCP + Google Workspace MCP). The backend is already built and tested. The frontend must consume it cleanly, render agent activity transparently, gate mutating actions behind confirmation modals, and remain honest about mode (demo / free / live) and downgrades.

Build exactly what the backend supports. Do not invent capabilities the backend does not have. Do not omit capabilities the backend already provides.

---

## 1. BACKEND CONTRACT (ASSUME THIS EXISTS — DO NOT REBUILD)

The backend is a LangGraph supervisor with three sub-agents. The frontend consumes a thin HTTP + SSE adapter that must be specified in this build (a small FastAPI layer wrapping the existing CLI entry point). The following capabilities exist:

- **One-shot query** — accepts a natural-language prompt, returns a routed response.
- **Streaming response** — token/event stream via SSE.
- **Thread persistence** — deterministic `thread_id`, resumable across requests.
- **Multi-agent routing** — the supervisor picks one or more of: `rag_agent`, `github_agent`, `google_agent`.
- **Parallel dispatch** — a single query can fan out to two or three agents; the UI must show them concurrently.
- **Interrupt gates** — mutating tools (calendar create/update, email send, GitHub write) pause via `interrupt()` and require `{"confirm": true}` to resume.
- **Rollback option** — the composite flow's second gate accepts `{"rollback": true}` to cancel an already-created calendar event.
- **Citations** — RAG answers include `{source, page, chunk_id, score}`.
- **Structured results** — Google actions return `event_id`, `message_id`, `status`; GitHub actions return PR/issue/commit ids.
- **Status semantics** — every response carries `ok | partial | error`.
- **Mode + downgrade banner** — the backend reports resolved `mode`, `llm_provider`, `vector_store`, `github_path`, `google_path`, `oauth_state`, and any downgrade reasons.

If the HTTP/SSE adapter does not yet exist, specify and build it as part of this work (Section 9). It is a thin wrapper — do not add business logic.

---

## 2. TECH STACK (NON-NEGOTIABLE)

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Framework | **Next.js 15** (App Router) | Server components for shell, client components for the chat surface, streaming-friendly |
| Language | **TypeScript strict** | No `any`, no implicit returns, `strictNullChecks` on |
| Styling | **TailwindCSS v4** + **shadcn/ui** | Token-driven design system, accessible primitives |
| Icons | **lucide-react** | Consistency with shadcn |
| Client state | **Zustand** | Small, no boilerplate, thread-scoped stores |
| Server state | **TanStack Query** | Caching, retries, deduplication for non-streaming endpoints |
| Streaming | **SSE** via `EventSource` or `fetch` + `ReadableStream` | Backend emits SSE; do not use WebSocket |
| Forms | **react-hook-form** + **zod** | Confirmations, settings panel |
| Animation | **framer-motion** | Subtle agent-status transitions only — no decoration |
| Testing | **Vitest** + **React Testing Library** + **Playwright** | Unit, component, e2e |
| Lint/format | **ESLint** + **Prettier** + **biome** | Strict, zero warnings allowed |
| Bundle | **Turbopack** | Fast dev; Vercel-ready prod build |

---

## 3. DELIVERABLES — SEVEN ARTIFACTS IN THIS EXACT ORDER

1. **UI/UX Design Brief**
2. **Information Architecture**
3. **Wireframes (ASCII or Mermaid)**
4. **Design System & Tokens**
5. **Component Architecture**
6. **State Management & API Contract**
7. **Implementation & Testing Plan**

---

## 4. ARTIFACT 1 — UI/UX DESIGN BRIEF

Include:

- **Product vision** — one paragraph.
- **Primary users** — technical professionals who already use the CLI but want a persistent, visual, multi-thread workspace.
- **Design principles** (exactly five, no more):
  1. **Agent transparency** — the user always knows which agent is acting.
  2. **Confirmation before mutation** — no calendar write, email send, or GitHub write happens without an explicit modal confirmation.
  3. **Grounded answers** — every RAG citation is one click from its source.
  4. **Thread continuity** — conversations persist and are resumable from a sidebar.
  5. **Honest mode** — the UI never hides demo/free/live status or downgrade reasons.
- **Success metrics** — p95 first-token latency < 800ms; confirmation modal interaction < 3s; thread load < 500ms; zero a11y critical issues.
- **Out of scope** — file uploads beyond PDF ingestion URL, real-time collaboration, mobile-native apps, dark/light theme parity beyond tailwind defaults.

---

## 5. ARTIFACT 2 — INFORMATION ARCHITECTURE

Define the route map:

```
/                       → redirect to /chat
/chat                   → new thread (empty state)
/chat/[threadId]        → active conversation
/settings               → mode, providers, credentials status
/health                 → backend + MCP reachability panel (internal)
/docs                   → link to README + architecture (optional)
```

Sidebar (persistent, collapsible):
- **New chat** button
- **Thread list** — grouped by Today / Yesterday / This week / Older
- **Search threads** — client filter over cached list
- **Mode pill** — top of sidebar, colored by `demo | free | live`
- **Footer** — user menu, settings link, upgrade/reauth prompts when required

---

## 6. ARTIFACT 3 — WIREFRAMES

Provide ASCII wireframes for each of the following states:

### 6.1 Empty state (`/chat`)

```
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

### 6.2 Multi-agent parallel response

```
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

### 6.3 Interrupt confirmation modal (calendar event)

```
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

### 6.4 Interrupt confirmation modal (email, with rollback)

```
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

### 6.5 Partial availability state

```
+--------------------------------------------------------------+
|  📅 Calendar agent  [partial]                                 |
|                                                               |
|  ⚠ Availability check is partial — external attendee         |
|    calendars could not be verified. Auto-create is refused.   |
|                                                               |
|  To proceed: [ Verify manually ]  [ Change attendees ]        |
+--------------------------------------------------------------+
```

### 6.6 Downgrade banner

```
+--------------------------------------------------------------+
|  ⚠  Running in FREE mode                                      |
|     • GitHub PAT missing — using mock GitHub MCP server       |
|     • Google OAuth missing — using mock Google MCP server     |
|     [ Configure credentials ]                                 |
+--------------------------------------------------------------+
```

### 6.7 Error state

```
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

---

## 7. ARTIFACT 4 — DESIGN SYSTEM & TOKENS

### 7.1 Color tokens (CSS variables, dark-first)

```
--background:         #0B0F14
--surface:            #111720
--surface-elevated:   #1A2230
--border:             #243040
--foreground:         #E6EDF3
--muted-foreground:   #8B98A9
--primary:            #3B82F6
--primary-foreground: #FFFFFF
--accent-rag:         #8B5CF6   /* violet */
--accent-github:      #F97316   /* orange */
--accent-calendar:    #10B981   /* emerald */
--accent-gmail:       #EF4444   /* red */
--success:            #22C55E
--warning:            #F59E0B
--error:              #DC2626
--info:               #0EA5E9
```

Every agent has a distinct accent color used consistently in:
- status pills
- left border of message cards
- inline citation chips
- timeline entries

### 7.2 Typography

- **UI:** Inter, 14/16/18/20/24/32
- **Code:** JetBrains Mono, 13
- **Numerals:** tabular-nums enabled for timing and ids

### 7.3 Spacing scale

`4 · 8 · 12 · 16 · 24 · 32 · 48 · 64` — no arbitrary values.

### 7.4 Radii

`6 (chips) · 10 (cards) · 14 (modals) · full (pills)`

### 7.5 Motion

- Status transition (routing → executing → done): 200ms ease-out
- Modal open: 180ms spring
- Streamed token reveal: opacity 0→1 over 120ms
- **No ambient animation.** Motion communicates state, nothing else.

### 7.6 Accessibility (WCAG 2.1 AA)

- Every interactive element has a visible focus ring (`--primary` 2px offset 2px)
- All status indicators carry `aria-live="polite"` regions
- Confirmation modals trap focus and expose `role="alertdialog"`
- Citation chips are keyboard-navigable and open sources in a side panel
- Color is never the sole carrier of meaning — icons and labels accompany every accent

---

## 8. ARTIFACT 5 — COMPONENT ARCHITECTURE

Provide a full component tree. Minimum set:

```
<AppShell>
  <Sidebar>
    <NewChatButton />
    <ThreadList>
      <ThreadGroup />
      <ThreadItem />
    </ThreadList>
    <ModePill />
    <SettingsLink />
  </Sidebar>
  <MainPanel>
    <DowngradeBanner />
    <ChatView>
      <MessageList>
        <UserMessage />
        <SupervisorRoutingCard />        // shows which agents were dispatched
        <AgentMessageCard>               // one per agent
          <AgentHeader>                  // icon, name, status pill, duration
          <AgentBody>                    // streamed markdown
          <CitationChips />
          <StructuredResultTable />      // for GitHub / Google
        </AgentMessageCard>
        <PartialAvailabilityNotice />
        <ErrorCard />
        <AggregateSummary />
      </MessageList>
      <Composer>
        <TextArea />
        <SendButton />
        <ModeIndicator />
      </Composer>
    </ChatView>
  </MainPanel>
  <ConfirmationModal />                  // rendered when interrupt() fires
  <CitationDrawer />                     // side panel for source preview
</AppShell>
```

Each component must:
- Be a **client component** unless it is a layout wrapper with no interactivity
- Accept typed props via a `Props` interface, no `any`
- Have a colocated `*.test.tsx` with at least one behavior test
- Handle loading, empty, error, and success states explicitly

---

## 9. ARTIFACT 6 — STATE MANAGEMENT & API CONTRACT

### 9.1 Backend adapter endpoints (specify and implement)

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/threads` | Create a new thread → `{thread_id}` |
| `GET`  | `/api/threads` | List threads for the current user |
| `GET`  | `/api/threads/{id}` | Load full thread state + message history |
| `DELETE` | `/api/threads/{id}` | Delete thread |
| `POST` | `/api/threads/{id}/invoke` | One-shot query → returns final state (no streaming) |
| `POST` | `/api/threads/{id}/stream` | SSE stream of agent events |
| `POST` | `/api/threads/{id}/resume` | Resume after `interrupt()` with `{confirm: true}` / `{rollback: true}` |
| `GET`  | `/api/health` | Backend + MCP reachability + resolved mode |
| `POST` | `/api/ingest` | Trigger PDF ingestion (path or URL) |

### 9.2 SSE event shape (non-negotiable)

Every SSE event must be one of:

```
event: routing       data: {"agents": ["rag_agent","github_agent"], "reasoning": "..."}
event: agent_start   data: {"agent": "rag_agent", "started_at": "..."}
event: agent_token   data: {"agent": "rag_agent", "delta": "The document "}
event: agent_tool    data: {"agent": "github_agent", "tool": "github_list_prs", "status": "ok"}
event: agent_end     data: {"agent": "rag_agent", "status": "ok", "duration_ms": 2100, "citations": [...]}
event: interrupt     data: {"agent": "google_agent", "kind": "calendar_create", "payload": {...}}
event: aggregate     data: {"status": "ok", "duration_ms": 2400}
event: error         data: {"agent": "github_agent", "message": "...", "retryable": true}
event: done          data: {}
```

The frontend must handle **unknown event types gracefully** — log and ignore, never crash.

### 9.3 Client state (Zustand stores)

- `useThreadStore` — current thread, messages, agents by id, pending interrupt, mode
- `useUIStore` — sidebar collapsed, citation drawer open, selected citation
- `useSettingsStore` — user preferences (persisted to localStorage)

Server state lives in TanStack Query with the following keys:
- `['threads']`, `['thread', id]`, `['health']`

Streaming state lives in `useThreadStore` and is updated by the SSE handler.

### 9.4 Interrupt lifecycle

1. SSE emits `event: interrupt` with `kind` and `payload`
2. Frontend opens `<ConfirmationModal>` with the payload rendered as a **read-only form**
3. User clicks **Confirm** → `POST /resume` with `{confirm: true}` → SSE resumes
4. User clicks **Cancel** → `POST /resume` with `{confirm: false}` → stream ends with `status: cancelled`
5. User clicks **Rollback** (only on email-send gate after a calendar create) → `POST /resume` with `{rollback: true}`
6. After resume, the modal closes and the stream continues in place — **do not reopen the thread or lose scroll position**

### 9.5 Error handling

| Error | UI behavior |
|-------|-------------|
| SSE disconnect | Auto-reconnect ×3 with backoff; show "Reconnecting…" chip; preserve partial message |
| 401/403 from backend | Redirect to `/settings` with a reauth banner |
| `interrupt` with missing payload | Show raw JSON in a collapsible; disable Confirm |
| Backend 500 | Inline error card with retry button; do not clear the conversation |
| Tool timeout | Inline warning chip on the affected agent card; other agents keep streaming |

---

## 10. ARTIFACT 7 — IMPLEMENTATION & TESTING PLAN

### 10.1 File structure

```
apps/web/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── chat/page.tsx
│   ├── chat/[threadId]/page.tsx
│   ├── settings/page.tsx
│   └── api/                    // Next.js route handlers → proxy to backend
├── components/
│   ├── shell/
│   ├── chat/
│   ├── modals/
│   └── ui/                     // shadcn primitives
├── lib/
│   ├── api/                    // typed fetch clients
│   ├── sse/                    // SSE parser + reconnect
│   ├── stores/                 // zustand
│   ├── hooks/                  // useChatStream, useThread, useHealth
│   ├── types/                  // shared types generated from backend OpenAPI
│   └── utils/
├── styles/
│   └── globals.css             // tailwind + tokens
├── tests/
│   ├── unit/
│   ├── component/
│   └── e2e/
├── public/
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── README.md
```

### 10.2 Implementation order (four weeks)

| Week | Deliverable | Acceptance |
|------|-------------|------------|
| 1 | Shell + routing + thread store + `/health` panel | Empty chat renders; sidebar collapses; health shows mode |
| 2 | SSE streaming + agent cards + citations | Live stream renders per-agent cards; citations clickable |
| 3 | Interrupt modal + resume + rollback + partial availability | Composite flow runs end to end against mock backend |
| 4 | Polish, a11y audit, e2e tests, mode banner, settings panel | Lighthouse ≥ 95, axe clean, Playwright e2e green |

### 10.3 Tests (minimum)

**Unit (Vitest):**
- SSE parser handles every event type + unknown events
- Zustand store actions: append token, set interrupt, resolve interrupt
- Mode resolver: demo/free/live, downgrade reasons rendered

**Component (RTL):**
- `<AgentMessageCard>` renders all four agent states (streaming, ok, partial, error)
- `<ConfirmationModal>` traps focus, escapes on Cancel, calls resume with the right payload
- `<CitationChips>` opens the drawer with the correct source and page
- `<DowngradeBanner>` renders for every downgrade combination

**E2E (Playwright):**
- Full flow: new thread → ask RAG question → receive cited answer
- Full flow: ask GitHub question → receive PR list
- Full flow: ask to schedule meeting → gate 1 modal → confirm → gate 2 modal → confirm → see event + message ids
- Rollback path: schedule meeting → confirm gate 1 → at gate 2 click Rollback → event cancelled message appears
- Decline path: at gate 1 click Cancel → no side effects, thread marked cancelled
- Error path: mock backend 500 → inline error card → retry works

Coverage target: **≥85% on components and stores, ≥70% on pages**.

### 10.4 Lint and type gates

```
pnpm lint           # eslint + biome, zero warnings
pnpm typecheck      # tsc --noEmit, strict
pnpm test           # vitest run
pnpm test:e2e       # playwright test
pnpm build          # next build, no errors
```

All five must pass before any PR merges.

---

## 11. HARD CONSTRAINTS

1. **No `any`.** Every prop, API response, and store shape is typed. Generate types from backend OpenAPI where possible.
2. **No hardcoded colors.** Every color comes from a CSS variable in `globals.css`.
3. **No hardcoded mode.** Mode comes from `/api/health` and updates the UI globally.
4. **No silent failures.** Every network error surfaces to the user with a retry or explanation.
5. **No mutation without confirmation.** Calendar writes, email sends, and GitHub writes only ever fire after a modal confirm.
6. **No navigation on interrupt.** The modal opens in place; the user stays in the current thread.
7. **No unmounted stream leaks.** Every SSE connection is closed on unmount and on thread switch.
8. **No layout shift during streaming.** Agent cards reserve space; text reflows without jumping the scroll position.
9. **No emoji-only status.** Every status has an icon + label; emoji is decoration, not semantics.
10. **No accessibility regressions.** Axe must pass with zero critical or serious issues.

---

## 12. ANTI-PATTERNS — DO NOT DO

- Do not build a chat bubble UI that hides agent attribution — this is a multi-agent system, the UI must show it.
- Do not conflate supervisor status with sub-agent status — they are different levels.
- Do not auto-confirm any gate, even in demo mode (the demo banner is enough signal).
- Do not use WebSockets when the backend is SSE.
- Do not render raw JSON payloads in the main thread — use structured cards.
- Do not treat partial availability as success — always show the warning chip.
- Do not lose the user's scroll position on interrupt or resume.
- Do not use spinners where a status pill conveys more.
- Do not invent backend endpoints — if a feature requires a new one, list it explicitly in Section 9.1 and mark it as a new requirement.
- Do not skip the downgrade banner — the UI must always be honest about what is live and what is mocked.
- Do not use `useEffect` for streaming — use a dedicated SSE hook with an explicit lifecycle.
- Do not use random keys in list rendering.

---

## 13. OUTPUT FORMAT

Respond in exactly this order with H1 headings:

# MAKPA — Frontend Design & Build

## 1. UI/UX Design Brief
## 2. Information Architecture
## 3. Wireframes
## 4. Design System & Tokens
## 5. Component Architecture
## 6. State Management & API Contract
## 7. Implementation & Testing Plan

Use Mermaid for state diagrams and flow diagrams. Use fenced code blocks with language tags (`tsx`, `ts`, `css`, `bash`, `mermaid`). Use tables for matrices, plans, and the API contract. No preamble. No summary at the end. No clarifying questions. State assumptions inline and proceed.

---

## 14. QUALITY BAR — SELF-CHECK BEFORE RESPONDING

- [ ] All seven artifacts present in the correct order
- [ ] Every agent (RAG, GitHub, Google) has a distinct accent color and status treatment
- [ ] Interrupt modal spec covers Confirm, Cancel, and Rollback
- [ ] Partial availability is visually distinct from success
- [ ] Downgrade banner spec covers all three modes and every downgrade reason
- [ ] SSE event contract is complete and the frontend handles unknown events
- [ ] Zustand + TanStack Query responsibilities are clearly separated
- [ ] No `any`, no hardcoded colors, no hardcoded mode
- [ ] Accessibility section covers focus, aria-live, alertdialog, and keyboard navigation
- [ ] Testing plan covers unit, component, and e2e with target coverage
- [ ] Implementation plan is four weeks with per-week acceptance criteria
- [ ] Anti-patterns list is specific to this project, not generic

Fix any unchecked box before responding.

---

## 15. START

Begin with Section 1. Produce every artifact in order. Do not stop for clarification. Do not emit a preamble. Build a frontend that a technical reviewer would be comfortable shipping to internal users on day one and to external users within a month. Every design decision must be justifiable against the backend contract defined in Section 1.
```