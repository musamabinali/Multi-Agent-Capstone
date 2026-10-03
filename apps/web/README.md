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
pnpm lint        # eslint + biome, zero warnings
pnpm typecheck   # tsc --noEmit, strict
pnpm test        # vitest run
pnpm test:e2e    # playwright test
pnpm build       # next build
```

## Contract

Backend adapter endpoints: `POST /api/threads`, `GET /api/threads`,
`GET /api/threads/{id}`, `DELETE /api/threads/{id}`,
`POST /api/threads/{id}/invoke`, `POST /api/threads/{id}/stream` (SSE),
`POST /api/threads/{id}/resume` (`{confirm, rollback}`),
`GET /api/health`, `POST /api/ingest`.

SSE events: `routing, agent_start, agent_token, agent_tool, agent_end,
interrupt, aggregate, error, done`. Unknown events are logged and ignored.

Interrupt lifecycle: `interrupt` → modal in place → Confirm `{confirm:true}` /
Cancel `{confirm:false}` / Rollback `{rollback:true}` → stream continues,
scroll preserved, no navigation.
