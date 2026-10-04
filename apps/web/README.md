# MAKPA Web Frontend

Production-grade Next.js 15 interface for the LangGraph supervisor backend.

## Run

```bash
# backend adapter (thin wrapper, no business logic)
PYTHONPATH=src python -m makpa.api.server
# → http://127.0.0.1:8001, docs at /docs

# frontend (pro development, Turbopack)
cd apps/web
pnpm install
pnpm dev
# → http://localhost:3000 ( /api/* rewrites to :8001 )
```

## Gates

```bash
pnpm lint        # biome check ., zero warnings (Biome is the enforced gate)
pnpm typecheck   # tsc --noEmit, strict
pnpm test        # vitest run (26 passed)
pnpm test:e2e    # playwright test (mocked flows + live.spec.ts, needs servers)
pnpm test:a11y   # axe on 4 screens, 0 critical/serious
pnpm build       # next build (8 routes)
```

## Contract

Backend adapter endpoints: `POST /api/threads`, `GET /api/threads`,
`GET /api/threads/{id}`, `DELETE /api/threads/{id}`,
`POST /api/threads/{id}/invoke`, `POST /api/threads/{id}/stream` (SSE),
`POST /api/threads/{id}/resume` (`{confirm, rollback}`),
`GET /api/health`, `POST /api/ingest`.

SSE events: `routing, agent_start, agent_token, agent_tool, agent_end
(+ structured ids), interrupt, aggregate, error, done`. Unknown events are
logged and ignored. `agent_end.structured` carries typed ids threaded from
`tool_results` (RAG citations/chunk_count, GitHub pr/issue/commit ids + repo,
Google event/message/draft ids + availability) — the UI never parses prose.

Interrupt lifecycle: `interrupt` → modal in place → Confirm `{confirm:true}` /
Cancel `{confirm:false}` / Rollback `{rollback:true}` → stream continues,
scroll preserved, no navigation.
