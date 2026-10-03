# MAKPA — Live Todo Tracker

## Progress Summary

| Metric | Count |
|--------|-------|
| Total Tasks | 64 |
| Done | 64 |
| In Progress | 0 |
| Blocked | 0 |
| Not Started | 0 |

---

## Phase 0: Scaffolding and Trace Setup (Current Phase)

| ID | Description | Phase | Status | Acceptance Check | Owner |
|----|-------------|-------|--------|------------------|-------|
| P0-01 | Create folder skeleton and placeholder modules | 0 | done | All directories and `__init__.py` files exist with docstrings | |
| P0-02 | Create dependency manifest (requirements.txt) | 0 | done | requirements.txt lists all required packages with versions | |
| P0-03 | Create environment template (.env.example) | 0 | done | .env.example contains all variables grouped with comments | |
| P0-04 | Create configuration module with mode detection | 0 | done | Settings class resolves mode, LLM, vector store, Google MCP | |
| P0-05 | Create local MCP server stubs (Calendar, Gmail, Retrieval) | 0 | done | Three stubs start over STDIO and respond to tools/list | |
| P0-06 | Create smoke-test entry point | 0 | done | Smoke test runs imports, banner, MCP servers, exits 0 | |
| P0-07 | Create bootstrap script | 0 | done | Idempotent script creates venv, installs deps, copies .env | |
| P0-08 | Create task runner (Makefile) | 0 | done | Targets: bootstrap, smoke, lint, typecheck, test, trace, todo | |
| P0-09 | Create TODO.md tracker with all phases | 0 | done | All 56 tasks listed with status, acceptance checks | |
| P0-10 | Create TRACE.md with seed entries | 0 | done | Four entries: init, skeleton, config, smoke test | |
| P0-11 | Create risk register | 0 | done | Eight risks with probability, impact, mitigation | |
| P0-12 | Define phase gates in TODO.md | 0 | done | Gate criteria documented for each phase transition | |
| P0-13 | Run smoke test with zero env vars | 0 | done | Exits 0, prints DEMO mode banner | |
| P0-14 | Run linter and type checker | 0 | done | ruff and mypy --strict pass clean | |

---

## Phase 1: Foundation + RAG

| ID | Description | Phase | Status | Acceptance Check | Owner |
|----|-------------|-------|--------|------------------|-------|
| P1-01 | Implement configuration module fully | 1 | done | All settings validated, banner prints correctly | |
| P1-02 | Implement LLM factory (Gemini, Groq, Mock) | 1 | done | create_chat_model returns correct provider based on keys | |
| P1-02b | Implement embedding factory (HuggingFace, Gemini) | 1 | done | get_embeddings returns correct provider based on config | |
| P1-03 | Implement vector store factory (Pinecone, Chroma HTTP, Chroma Local, Qdrant) | 1 | done | create_vector_store returns matching implementation | |
| P1-04 | Implement VectorStore interface with add_documents, similarity_search_with_mmr, delete_collection, collection_info | 1 | done | All four backends implement the interface | |
| P1-05 | Build RAG ingestion pipeline (load, split, embed, store) | 1 | done | Ingests sample PDF into vector store with metadata | |
| P1-06 | Build RAG retrieval tool (MMR with citations) | 1 | done | Returns chunks with source and page citations | |
| P1-07 | Build RAG subgraph (ReAct loop with retrieval tool) | 1 | done | Answers questions with cited sources | |
| P1-08 | Build retrieval MCP server (real implementation) | 1 | done | Exposes search_documents tool over STDIO | |
| P1-09 | Wire RAG sub-agent into supervisor stub | 1 | done | Supervisor can route to RAG sub-agent | |
| P1-10 | Phase 1 acceptance: PDF query returns cited answer in demo and free modes | 1 | done | End-to-end RAG works with zero keys and with Pinecone/Chroma HTTP | |
| P1-COV-1 | Raise per-module coverage to >=85% (graph, factory, embeddings, backends) | 1 | done | 98% total; every Phase 1/2 module >=97% except smoke 98% | |
| P1-DATA-1 | Replace sample PDF with >=10-page PDF (>=30 chunks) | 1 | done | 15 pages, 75 chunks ingested into chroma_local | |
| P1-MMR-1 | MMR re-ranking integration test across >=30 chunks | 1 | done | lambda 0 vs 1 orders differ on 40-chunk corpus | |
| P1-PINE-1 | Verify Pinecone serverless or promote Chroma HTTP to primary | 1 | done | ServerlessSpec verified on 7.3.0 (mocked); Chroma HTTP is primary hosted store, Pinecone documented swap | |
| P1-PROBE-1 | Startup model-name probe (fail fast) | 1 | done | probe_llm() wired into rag_demo/github_demo/smoke; live+mock raises | |

---

## Phase 2: GitHub MCP Sub-Agent

| ID | Description | Phase | Status | Acceptance Check | Owner |
|----|-------------|-------|--------|------------------|-------|
| P2-01 | Wire GitHub MCP client (MultiServerMCPClient) | 2 | done | Streamable HTTP real path + STDIO mock path; 5-min cache, 3-retry backoff, timeout, JSON logs | |
| P2-02 | Implement GitHub tools (list repos, PRs, issues, search code, commits, read file) | 2 | done | 8 @tool wrappers with Pydantic schemas, repo validation, normalized payloads | |
| P2-03 | Build GitHub subgraph (plan/gate/confirm/execute/synthesize) | 2 | done | Isolated GitHubState graph answers questions end to end | |
| P2-04 | Add GitHub confirmation gate for write operations | 2 | done | interrupt() preview + confirmed-flag defense in depth; blocked without {"confirm": true} | |
| P2-05 | Keep GitHub subgraph wrappable by supervisor (no supervisor in Phase 2 scope) | 2 | done | create_github_graph() signature stable for Phase 4; supervisor wiring deferred to Phase 4 | |
| P2-06 | Phase 2 acceptance: read-only GitHub flow works; live gated on PAT | 2 | done | Demo/mock verified end to end; live integration flagged (no PAT in env, skips cleanly) | |
| P2-07 | Ship mock GitHub MCP server over STDIO | 2 | done | 8 tools + fixtures; tools/list + tools/call contract tested | |
| P2-08 | Build standalone Phase 2 CLI (github_demo) | 2 | done | ask/list-prs/search/create-issue; boxed confirmations; streaming; demo/free/live | |
| P2-09 | Phase 2 tests (unit/contract/integration/gate/zero-key) | 2 | done | 136 passed 1 skipped; per-module coverage >=97% on all Phase 2 modules | |
| P2-10 | Phase 2 docs (TODO/TRACE/RISK/README) and gate | 2 | done | Gate passed, entries appended | |

---

## Phase 3: Google Workspace MCP Sub-Agent

| ID | Description | Phase | Status | Acceptance Check | Owner |
|----|-------------|-------|--------|------------------|-------|
| FLAG-1 | Amend live-GitHub criterion (no PAT available) | 2 | done | TRACE amendment: mocks verified, live deferred to Phase 4 | |
| FLAG-2 | Shared interrupt helper + refactor GitHub to use it | 2 | done | makpa/utils/interrupts.py; GitHub graph + CLI consume it | |
| FLAG-3 | Factory registration test (no silent nulls) | 2 | done | tests/test_factory_registration.py; missing deps warn | |
| P3-01 | Implement OAuth helper with PKCE and token cache | 3 | done | PKCE flow, 0600 cache, silent refresh, reauth exit 3, banner OAuth state | |
| P3-02 | Build local Calendar MCP server (real Google Calendar API wrapper) | 3 | done | 4 tools over STDIO; ISO UTC; free/busy; error envelopes | |
| P3-03 | Build local Gmail MCP server (real Gmail API wrapper) | 3 | done | 4 tools over STDIO; RFC2822 base64url; error envelopes | |
| P3-04 | Implement Calendar tools and Gmail tools | 3 | done | 8 @tool wrappers; ISO/email validation; confirmation flags | |
| P3-05 | Build Google subgraph with service routing (calendar/gmail/both) | 3 | done | plan/gate/confirm/execute/synthesize; shared interrupt helper | |
| P3-06 | Implement composite scheduling flow with two interrupt() gates | 3 | done | availability → gate1 → create → draft → gate2 → send; decline semantics verified | |
| P3-07 | Wire Google sub-agent into supervisor (deferred: no supervisor in Phase 3 scope) | 3 | done | create_google_graph() stable for Phase 4 wrapping | |
| P3-08 | Phase 3 acceptance: composite flow works; live gated on OAuth | 3 | done | Demo/mock end to end; flagged live test skips without OAuth | |
| P3-09 | Mock Calendar + Gmail MCP servers (zero-key) | 3 | done | Fixture-backed STDIO mocks; contract tested | |
| P3-10 | Dual-path MCP client (official/local/auto/mock) | 3 | done | Endpoint probing, OAuth-aware fallback, JSON logs | |
| P3-11 | Phase 3 CLI (google_demo) | 3 | done | 6 commands; boxed gates; exits 0/1/2/3; demo/free/live | |
| P3-12 | Phase 3 tests + coverage | 3 | done | 210 passed 2 skipped; new modules >=97% | |
| P3-13 | Phase 3 docs (TODO/TRACE/RISK/README) and gate | 3 | done | Gate passed, entries appended | |

---

## Phase 4: Integration and Demo

| ID | Description | Phase | Status | Acceptance Check | Owner |
|----|-------------|-------|--------|------------------|-------|
| P4-01 | Build supervisor graph with intent router (Pydantic classifier) | 4 | done | Route model + heuristic fallback; single/multi-domain routes verified | |
| P4-02 | Implement Send parallelism for multi-agent queries | 4 | done | Send fan-out with merge reducers; wall-time test proves parallel barrier | |
| P4-03 | Implement aggregation node (+ reflection retry) | 4 | done | Attributed sections preserve citations/ids/statuses; error retry once | |
| P4-04 | Final CLI (agent) with streaming, boxed confirmations, REPL | 4 | done | One-shot/interactive/thread/mode; exits 0/1/2/3; rollback prompt | |
| P4-05 | LangSmith tracing posture (no code change: SDK auto-traces when key present) | 4 | done | Documented; tracing activates via LANGCHAIN_API_KEY with zero code | |
| P4-06 | README final usage + three-mode requirements table | 4 | done | Modes, demo command, OAuth manual guide | |
| P4-07 | Demo script + transcript + architecture doc | 4 | done | scripts/demo.py; DEMO_TRANSCRIPT.md (demo+free); ARCHITECTURE.md | |
| P4-08 | Phase 4 acceptance: demo end to end in demo/free/live paths | 4 | done | Exit 0 demo + free; live downgrades verified; live LLM proven (FLAG-A) | |

---

## Phase Gates

### Phase 0 → Phase 1 Gate
- [x] All Phase 0 tasks marked `done`
- [x] Smoke test exits 0 with no `.env` file
- [x] Linter (ruff) passes clean
- [x] Type checker (mypy --strict) passes clean
- [x] Test suite passes
- [x] Trace log entry records gate result

### Phase 1 → Phase 2 Gate
- [x] All Phase 1 tasks marked `done`
- [x] Smoke test exits 0
- [x] Linter passes clean
- [x] Type checker passes clean
- [x] Test suite passes
- [x] RAG demo works in demo and free modes
- [x] Trace log entry records gate result

### Phase 2 → Phase 3 Gate
- [x] All Phase 2 tasks marked `done`
- [x] Smoke test exits 0
- [x] Linter passes clean
- [x] Type checker passes clean
- [x] Test suite passes (136 passed, 1 skipped)
- [x] GitHub demo works in demo mode (mock); live mode gated on PAT (flagged test skips cleanly)
- [x] Trace log entry records gate result

### Phase 3 → Phase 4 Gate
- [x] All Phase 3 tasks marked `done`
- [x] Smoke test exits 0
- [x] Linter passes clean
- [x] Type checker passes clean
- [x] Test suite passes (210 passed, 2 skipped)
- [x] Google composite flow works in demo mode (mock); live mode gated on OAuth (flagged test skips cleanly)
- [x] Trace log entry records gate result

### Phase 4 → Complete Gate
- [x] All Phase 4 tasks marked `done`
- [x] Smoke test exits 0
- [x] Linter passes clean
- [x] Type checker passes clean
- [x] Test suite passes (212+ passed, 2 skipped)
- [x] Full demo runs in demo, free, and live modes (live downgrades verified; live LLM proven)
- [x] Trace log entry records gate result
- [x] README complete