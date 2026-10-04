# MAKPA — LangGraph Multi-Agent Capstone

A multi-agent system built with LangGraph featuring three specialized sub-agents coordinated by a supervisor:
- **RAG Agent**: Document retrieval from hosted vector stores (Pinecone, ChromaDB, Qdrant)
- **GitHub Agent**: GitHub operations via MCP (repos, PRs, issues, code search)
- **Google Workspace Agent**: Calendar and Gmail via MCP (events, emails, scheduling)

## Features

- **Three Runtime Modes**: `demo` (zero keys), `free` (free-tier keys), `live` (production)
- **Zero-Key Demo**: Runs end-to-end with mock LLM and in-process ChromaDB
- **Multi-Provider LLMs**: Gemini, Groq, or Mock (auto-selected by available keys)
- **Multi-Backend Vector Stores**: Pinecone, ChromaDB HTTP, Qdrant, or ChromaDB Local
- **Dual Google MCP Paths**: Official MCP servers or local STDIO wrappers
- **Human-in-the-Loop**: Two `interrupt()` gates for calendar events and email sends
- **LangSmith Tracing**: Enabled automatically when `LANGCHAIN_API_KEY` is set
- **CLI Interface**: Emoji status indicators, streaming output, boxed confirmations

## Quick Start

```bash
# Clone and bootstrap (one command)
git clone <repo>
cd LangGraph-Agent
make bootstrap

# Run smoke test (verifies installation)
make smoke

# Run the agent (after configuring .env)
python -m makpa.cli.main
```

## Prerequisites

- Python 3.10+
- Git

## Installation

### Automated (Recommended)

```bash
make bootstrap
```

This will:
1. Verify Python version
2. Create virtual environment (`.venv/`)
3. Install dependencies from `requirements.txt`
4. Copy `.env.example` to `.env` (if not present)

### Manual

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
cp .env.example .env
```

## Configuration

All settings are driven by environment variables in `.env`. Key variables:

| Variable | Description | Required For |
|----------|-------------|--------------|
| `MAKPA_MODE` | Runtime mode: `demo`, `free`, `live` | All |
| `LLM_PROVIDER` | `gemini`, `groq`, `mock` | free, live |
| `GEMINI_API_KEY` | Google Gemini API key | free (gemini), live |
| `GROQ_API_KEY` | Groq API key | free (groq), live |
| `VECTOR_STORE` | `pinecone`, `chroma_http`, `qdrant`, `chroma_local` | free, live |
| `PINECONE_API_KEY` | Pinecone API key | free (pinecone), live |
| `CHROMA_HOST` / `CHROMA_PORT` | ChromaDB HTTP server | free (chroma_http), live |
| `GITHUB_MCP_PAT` | GitHub fine-grained PAT | live |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | OAuth credentials | free (local), live |
| `GOOGLE_MCP_MODE` | `official`, `local`, `auto` | free, live |

See `.env.example` for all 80+ variables with defaults and mode requirements.

## Runtime Modes

| Mode | LLM | Vector Store | MCP Servers | Use Case |
|------|-----|--------------|-------------|----------|
| `demo` | Mock | ChromaDB Local | Mock | Zero-setup grading |
| `free` | Gemini/Groq (Groq while the Gemini project denial lasts — see R-27) | Pinecone/Chroma HTTP | Local wrappers | Free-tier demo |
| `live` | Gemini/Groq | Pinecone/Chroma HTTP | Real GitHub + Google | Production |

Mode resolution cascades: missing credentials in `live` → `free`; missing LLM key in `free` → `demo`.

## Phase 1 Usage (RAG Sub-Agent)

```bash
# Ingest a PDF (defaults to SAMPLE_PDF_PATH)
python -m makpa.cli.rag_demo ingest --pdf ./data/sample.pdf

# Ask a question (streams answer + citations)
python -m makpa.cli.rag_demo ask "What is in the sample document?"

# Show the current vector store
python -m makpa.cli.rag_demo info

# Reset the vector store
python -m makpa.cli.rag_demo reset --yes
```

### Switching vector stores

```bash
VECTOR_STORE=chroma_local  # demo default, in-process, zero keys
VECTOR_STORE=chroma_http   # free/live: needs CHROMA_HOST + CHROMA_PORT
VECTOR_STORE=pinecone      # free/live: needs PINECONE_API_KEY (serverless only)
VECTOR_STORE=qdrant        # free/live: needs QDRANT_URL + QDRANT_API_KEY
```

### Switching embedding providers

```bash
EMBEDDING_PROVIDER=huggingface  # default, offline after first download
EMBEDDING_PROVIDER=gemini       # opt-in, needs GEMINI_API_KEY
```

> **Hosted-store policy (P1-PINE-1):** `chroma_http` is the primary hosted
> vector store for free/live modes. Pinecone is a documented swap
> (serverless indexes only, SDK pinned `<8` via `langchain-pinecone`).

### Startup model-name probe

Every CLI runs `probe_llm()` after the banner: a one-token completion that
warns on known-stale model names (`gemini-1.5-flash`, `llama-3.1-70b-versatile`)
and fails fast in `live` mode when no real provider validates.
Run the real flow with one line (from the repo root, keep GOOGLE_MCP_MODE=local):

python -c "from makpa.google.oauth import run_browser_flow; run_browser_flow(); print('cached OK')"


```bash
# Pre-warm the HF embedding cache once (first download ~60s, then cached)
python scripts/prewarm_embeddings.py
```

## Phase 2 Usage (GitHub MCP Sub-Agent)

```bash
# Ask anything (plans tools, confirms writes, synthesizes an answer)
python -m makpa.cli.github_demo ask "List open pull requests in octo-demo/hello-world"

# List PRs directly
python -m makpa.cli.github_demo list-prs --repo octo-demo/hello-world --state open

# Search code
python -m makpa.cli.github_demo search --query "def main" --repo octo-demo/hello-world

# Create an issue (boxed confirmation gate; --yes skips only in scripts)
python -m makpa.cli.github_demo create-issue --repo octo-demo/hello-world --title "Demo" --body "test"
```

### Switching between real and mock GitHub MCP

```bash
GITHUB_MCP_MODE=auto  # default: real server when GITHUB_MCP_PAT is set, else mock
GITHUB_MCP_MODE=mock  # force the in-repo STDIO mock (zero keys, demo fixtures)
GITHUB_MCP_MODE=real  # require the Streamable HTTP server (needs GITHUB_MCP_PAT)
```

The startup banner reports the resolved path (`GitHub MCP: real|mock`).
Without a PAT the sub-agent degrades to the mock server and says so.
`create_issue` always stops at an `interrupt()` confirmation showing the full
payload; resume with `{"confirm": true}` to proceed. Live read-only
verification is a flagged test (needs `RUN_GITHUB_INTEGRATION=1` + PAT):

```bash
RUN_GITHUB_INTEGRATION=1 GITHUB_MCP_PAT=<pat> pytest tests/test_github_integration.py -q
```

## Phase 3 Usage (Google Workspace Sub-Agent)

```bash
# List next 7 days of events
python -m makpa.cli.google_demo list-events --days 7

# Check availability for attendees in a window
python -m makpa.cli.google_demo check --attendees a@x.com --start 2026-10-02T15:00:00Z --end 2026-10-02T16:00:00Z

# Create an event (confirmation gate 1)
python -m makpa.cli.google_demo create-event --summary "Sync" --start 2026-10-02T15:00:00Z --end 2026-10-02T16:00:00Z --attendees a@x.com

# Draft an email (safe, no gate)
python -m makpa.cli.google_demo draft --to a@x.com --subject "Hi" --body "Hello"

# Send an email (confirmation gate 2)
python -m makpa.cli.google_demo send --to a@x.com --subject "Hi" --body "Hello"

# Composite scheduling flow (two gates: event, then email)
python -m makpa.cli.google_demo ask "schedule a meeting with a@x.com from 2026-10-02T15:00:00Z to 2026-10-02T16:00:00Z"
python -m makpa.cli.google_demo ask "Schedule 'Project Sync' with musamabinali@gmail.com from 2026-10-05T14:00:00+05:00 to 2026-10-05T14:30:00+05:00 and email them 'Hi, confirming our project sync on Monday at 2 PM PKT. Reply if another time suits you better.'"
```

### OAuth setup (free/live modes)

1. Create a Google Cloud project; enable Calendar + Gmail APIs.
2. Create OAuth Desktop credentials; set `GOOGLE_CLIENT_ID` (+secret unless PKCE-only).
3. First run opens the browser; tokens cache to `GOOGLE_TOKEN_CACHE_PATH` (0600).
4. Expiry triggers silent refresh; refresh failure prints the reauth URL and exits `3`.

### Manual OAuth verification guide (browser flow never ran in CI)

The automated suite covers PKCE generation, cache round-trip, silent refresh,
and reauth — but the real browser redirect → code → token exchange handshake
needs a human with a Google account. Until a grader completes it, the path is
marked **manually verified by the user**:

1. Set `GOOGLE_CLIENT_ID` (+secret), `GOOGLE_MCP_MODE=local`, and a fresh
   `GOOGLE_TOKEN_CACHE_PATH` in `.env`.
2. Run `python -m makpa.cli.google_demo login`. The CLI runs the real PKCE
   browser flow (opens the consent URL, listens on the redirect port,
   exchanges the code, caches tokens).
3. On the Google consent screen, confirm the app name matches your Cloud
   project and the requested scopes are Calendar + Gmail only, then approve.
4. The CLI prints cached events and `Google OAuth: cached` on the next run.
5. Verify `0600` permissions on the cache file and that no token value ever
   appears in logs (`LOG_LEVEL=DEBUG` output included).
6. Revoke access at `https://myaccount.google.com/permissions`, re-run, and
   confirm exit code `3` with a fresh reauth URL.

Record the date, account domain, and result in `docs/TRACE.md` when done.

### Switching between official / local / mock Google MCP

```bash
GOOGLE_MCP_MODE=auto      # probe official URLs, fall back to local wrappers, then mocks
GOOGLE_MCP_MODE=official  # Streamable HTTP to GOOGLE_CALENDAR_MCP_URL / GOOGLE_GMAIL_MCP_URL
GOOGLE_MCP_MODE=local     # in-repo STDIO wrappers (needs OAuth; missing creds + explicit local = exit 3)
GOOGLE_MCP_MODE=mock      # fixture STDIO servers (zero keys)
```

The banner reports `Google MCP Mode`, `Google OAuth` (`cached|refreshing|missing`),
and the CLI reports per-service paths. Declining gate 1 creates nothing;
declining gate 2 keeps the event and skips only the email. Answer `rollback`
at gate 2 to cancel the created event instead. Flagged live test:

```bash
RUN_LIVE_GOOGLE_TESTS=1 pytest tests/test_google_integration.py -q
```

## Phase 4 Usage (Supervisor + Final Demo)

```bash
# One-shot multi-agent query (routes to rag/github/google as needed)
python -m makpa.cli.agent "What does the sample PDF say?"

# Multi-turn REPL with thread memory
python -m makpa.cli.agent --interactive

# Resume a named thread
python -m makpa.cli.agent --thread my-thread "Follow up on that PR"

# Override mode for one run
python -m makpa.cli.agent --mode demo "List open pull requests in octo-demo/hello-world"

# Fixed three-scenario end-to-end demo (RAG, GitHub, composite scheduling)
python scripts/demo.py [--mode demo|free|live]
```

### What each mode actually requires

| Mode | LLM | Sub-agents | MCP servers | Credentials needed |
|------|-----|------------|-------------|-------------------|
| `demo` | Mock (zero keys) | all three on mocks | mock STDIO | none |
| `free` | Gemini/Groq (free tier) | all three (mock or local MCP) | auto/local/mock | LLM key only |
| `live` | Gemini/Groq | all three incl. official MCP | official/real | LLM key + `GITHUB_MCP_PAT` + Google OAuth |

Missing credentials downgrade automatically (`live` → `free` → `demo`),
and every downgrade is printed in the banner. Verified live so far:
metered LLM inference end to end (Groq, recorded in `docs/TRACE.md`);
live GitHub (PAT) and live Google (OAuth) run when the user supplies
credentials — see the manual OAuth guide above. Full transcripts for
demo and free modes: `docs/DEMO_TRANSCRIPT.md`. Architecture:
`docs/ARCHITECTURE.md`.

## Web Frontend (Next.js 15 + FastAPI adapter)

```bash
# Terminal 1: thin adapter (no business logic, wraps the supervisor)
PYTHONPATH=src ./.venv/Scripts/python.exe -m makpa.api.server
# → http://127.0.0.1:8001, OpenAPI at /docs

# Terminal 2: frontend (Turbopack dev, /api/* rewrites to :8001)
cd apps/web
pnpm install
pnpm dev
# → http://localhost:3000
```

Gates: `pnpm lint` (biome clean), `pnpm typecheck` (`tsc --noEmit` strict),
`pnpm test` (vitest 26 passed), `pnpm build` (8 routes green),
`pnpm test:a11y` (axe 4 screens, 0 critical/serious).
Adapter + parity tests: `pytest tests/test_api_server.py tests/test_api_parity.py -q` (15 passed).
Design artifacts 1–7: `apps/web/docs/BUILD.md` (spec: `apps/web/docs/Frontend Build.md`);
audit: `apps/web/docs/REVIEW.md`; gate prompt: `apps/web/docs/Web Phase Review.md`.

## Running the Web Stack (two terminals)

```powershell
# Terminal 1: deterministic backend harness (mock LLM + mock MCP, child env only)
.\.venv\Scripts\python.exe scripts/serve_web.py
# → http://127.0.0.1:8001, OpenAPI at /docs (health: llm mock, github/google mock)

# Terminal 2: frontend (Turbopack dev, /api/* rewrites to :8001)
cd apps/web
pnpm dev
# → http://localhost:3000
```

Live end-to-end (zero mocked routes — needs both servers up):

```powershell
cd apps/web
$env:PLAYWRIGHT_BROWSERS_PATH = "D:\playwright-browsers"  # C: is too full for browsers
$env:PLAYWRIGHT_API_URL = "http://127.0.0.1:8001"
$env:PLAYWRIGHT_BASE_URL = "http://localhost:3000"
./node_modules/.bin/playwright test tests/e2e/live.spec.ts
# 4/4 green: RAG citations, GitHub PR 7, composite two-gate ids, gate-2 rollback
```

Notes: `scripts/serve_web.py` forces the mock stack so turns stay fast and deterministic
(live Groq turns take 30–75s from here; Gemini free tier is 429-exhausted; live inference
stays proven by `docs/TRACE.md` FLAG-A). The harness also sets `GOOGLE_CALENDAR_ATTENDEE_MODE=all`
(the default `own_only` correctly refuses the composite auto-create) and points HF/tmp caches at
`D:\` (C: has no room). The mock calendar store persists to `data/mock_calendar.json` so
create→update (rollback) works across MCP subprocesses; the repo `.env` is never modified.

## Project Structure

```
LangGraph-Agent/
├── src/makpa/
│   ├── config/           # Pydantic settings, mode detection
│   ├── state/            # TypedDict state schemas
│   ├── llm/              # LLM factory (Gemini, Groq, Mock)
│   ├── vectorstore/      # Vector store factory + backends
│   ├── supervisor/       # Supervisor graph, intent router
│   ├── subagents/
│   │   ├── rag/          # RAG sub-agent (ingest, retrieve)
│   │   ├── github/       # GitHub MCP sub-agent
│   │   └── google/       # Google Workspace sub-agent
│   ├── mcp_servers/
│   │   ├── calendar/     # Local Calendar MCP (STDIO)
│   │   ├── gmail/        # Local Gmail MCP (STDIO)
│   │   └── retrieval/    # Local Retrieval MCP (STDIO)
│   ├── utils/            # Logging, tracing, helpers
│   └── cli/              # CLI entry points
├── tests/                # Test suite
├── scripts/              # Bootstrap, utilities
├── docs/                 # TODO.md, TRACE.md, RISK_REGISTER.md
├── data/                 # Sample PDF for RAG
├── requirements.txt
├── .env.example
├── pyproject.toml
└── Makefile
```

## Available Commands

```bash
make bootstrap   # Setup venv, install deps, create .env
make smoke       # Run smoke test (imports + MCP servers)
make lint        # Run ruff linter
make typecheck   # Run mypy --strict
make test        # Run pytest
make trace       # Open TRACE.md
make todo        # Open TODO.md
make check       # Full pipeline: lint + typecheck + test + smoke
make clean       # Remove generated files
```

## Development

### Adding a New Sub-Agent

1. Create package under `src/makpa/subagents/<name>/`
2. Define state schema in `src/makpa/state/__init__.py`
3. Implement graph in `create_<name>_graph()`
4. Register in supervisor's intent router

### Running Tests

```bash
make test
# or
pytest tests/ -v
```

### Code Quality

```bash
make lint      # ruff
make typecheck # mypy --strict
```

### Terminal Output

CLIs print a one-line `probing LLM...` note before the model probe (the
probe waits on network calls and can take ~40s when a provider quota is
exhausted), cap third-party SDK chatter at WARNING, and never print the
banner border twice. Full SDK logs return with `MAKPA_VERBOSE=1`.

## Architecture

```
User Query
    │
    ▼
┌─────────────────┐
│   Supervisor    │ ◄── Intent Router (Pydantic classifier)
│  (StateGraph)   │
└────────┬────────┘
         │ Send API (parallel)
    ┌────┼────┐
    ▼    ▼    ▼
┌──────┐ ┌────────┐ ┌────────────┐
│ RAG  │ │ GitHub │ │  Google    │
│Subgr.│ │Subgraph│ │ Subgraph   │
└──┬───┘ └────┬───┘ └─────┬──────┘
   │          │           │
   │    ┌─────┴─────┐     │
   │    │  MCP      │     │
   │    │  Client   │     │
   │    └───────────┘     │
   │                      │
   └──────────┬───────────┘
              ▼
       ┌─────────────┐
       │ Aggregation │
       │    Node     │
       └──────┬──────┘
              ▼
         Final Answer
```

## Google OAuth Setup (for free/live modes)

1. Create Google Cloud project
2. Enable Calendar API and Gmail API
3. Create OAuth 2.0 credentials (Desktop app)
4. Add authorized redirect URI: `http://localhost:8080/callback`
5. Set in `.env`:
   ```
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   GOOGLE_REDIRECT_URI=http://localhost:8080/callback
   GOOGLE_OAUTH_SCOPES=https://www.googleapis.com/auth/calendar,https://www.googleapis.com/auth/gmail.send,https://www.googleapis.com/auth/gmail.compose,https://www.googleapis.com/auth/gmail.readonly
   ```
6. First run launches browser for consent; tokens cached to `GOOGLE_TOKEN_CACHE_PATH`

## Vector Store Setup

### Pinecone (Cloud)
```bash
VECTOR_STORE=pinecone
PINECONE_API_KEY=your-key
PINECONE_INDEX_NAME=makpa-rag
PINECONE_ENVIRONMENT=us-east-1
PINECONE_CLOUD=aws
```

### ChromaDB HTTP (Local Hosted)
```bash
# Terminal 1: Start ChromaDB
docker run -p 8000:8000 chromadb/chroma

# Terminal 2: Configure
VECTOR_STORE=chroma_http
CHROMA_HOST=localhost
CHROMA_PORT=8000
```

### Qdrant Cloud
```bash
VECTOR_STORE=qdrant
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-key
QDRANT_COLLECTION_NAME=makpa-rag
```

## RAG Ingestion

```bash
# Ingest sample PDF (uses SAMPLE_PDF_PATH from .env)
python -m makpa.cli.ingest

# Ingest custom PDF
python -m makpa.cli.ingest --pdf path/to/document.pdf
```

## Spec vs Delivered (Drift Is Intentional and Documented)

The project began as a one-shot master prompt and was built in four phases.
Where reality diverged, the change was recorded with reasons (see
`docs/SPEC_RECONCILIATION.md`):

| Spec | Delivered | Status |
|------|-----------|--------|
| Three sub-agents: RAG, GitHub MCP, Google Workspace MCP | Exactly three sub-agents | Match |
| Google = one sub-agent, two MCP servers | One sub-agent, Calendar + Gmail clients | Match |
| Supervisor with `Send` parallel dispatch | Hub-and-spoke, `Send` fan-out, barrier aggregation | Match |
| Three modes: `demo`, `free`, `live` | Three modes with downgrade chain; `live` = live LLM, MCP mocked unless credentials present | Partial (banner says so) |
| Pinecone as primary hosted vector store | Chroma HTTP primary; Pinecone serverless-only swap | Reversed (P1-PINE-1) |
| Chroma HTTP local-hosted option | Chroma HTTP primary | Match |
| Qdrant one-file swap | Same interface, behind factory | Match |
| Google dual path: official + local wrapper | Dual path **plus** mock path | Exceeded |
| OAuth 2.0 + PKCE, refresh-token cache | Implemented; browser handshake user-verified (guide above) | Partial |
| Composite flow, exactly two `interrupt()` gates | Two gates **plus** gate-2 `rollback` | Exceeded |
| HuggingFace MiniLM default, Gemini opt-in | Confirmed | Match |
| Sample PDF + drop-in path | 15-page PDF, 75 chunks | Exceeded |
| CLI entry point, emoji indicators | `python -m makpa.cli.agent` | Match |
| Zero-key runnable end to end | Verified with blanked env | Match |
| LangSmith `@traceable` on entry points | Conditional `@entrypoint` on all four `run_*` (no-op without key) | Match |
| MemorySaver, deterministic thread IDs | Confirmed | Match |
| `mypy --strict` + `ruff` clean | Confirmed at every gate | Match |
| No web UI, Docker, Postgres; Pinecone serverless-only | Confirmed | Match |

## License

MIT License - see LICENSE file for details.

## Acknowledgments

Built for the 2026 Agentic AI Masterclass capstone using:
- LangChain, LangGraph, LangSmith
- Google GenAI, Groq
- MCP SDK, langchain-mcp-adapters
- Pinecone, ChromaDB, Qdrant
- HuggingFace Embeddings