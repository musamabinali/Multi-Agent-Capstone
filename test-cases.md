# MAKPA — Test Cases & MCP/Plugin Integration Requirements

This document is the companion to `ARCHITECTURE.md`, `GRADER_CHECKLIST.md`, and `VIVA_QA.md`. It defines the **complete test-case matrix** for the agent and the **exact MCP servers and plugins** the system connects to, including URLs, transports, auth, and fallbacks.

---

## Part 1 — MCP Servers & Plugins to Connect

### 1.1 Connection Matrix

| MCP Server | Transport | Endpoint / Command | Auth | Required For | Fallback |
|------------|-----------|-------------------|------|--------------|----------|
| **GitHub MCP** (official remote) | Streamable HTTP | `https://api.githubcopilot.com/mcp/` | Fine-grained PAT or OAuth 2.0 | Any GitHub question | Mock STDIO server |
| **Google Calendar MCP** (official remote) | Streamable HTTP | `https://calendarmcp.googleapis.com/mcp/v1` | OAuth 2.0 + PKCE | Read/create/check meetings | Local STDIO wrapper → Mock |
| **Gmail MCP** (official remote) | Streamable HTTP | `https://gmailmcp.googleapis.com/mcp/v1` | OAuth 2.0 + PKCE | Draft/send/search emails | Local STDIO wrapper → Mock |
| **Local Calendar wrapper** | STDIO | `python -m makpa.mcp_servers.google_calendar.server` | OAuth 2.0 (Google API) | Guaranteed-path fallback | Mock |
| **Local Gmail wrapper** | STDIO | `python -m makpa.mcp_servers.google_gmail.server` | OAuth 2.0 (Google API) | Guaranteed-path fallback | Mock |
| **Retrieval MCP** (RAG) | STDIO | `python -m makpa.mcp_servers.retrieval.server` | None (local) | `search_documents` tool | N/A |
| **Mock GitHub MCP** | STDIO | `python -m makpa.mcp_servers.github.server` | None | Zero-key demo | N/A |
| **Mock Calendar MCP** | STDIO | `python -m makpa.mcp_servers.google_calendar.mock` | None | Zero-key demo | N/A |
| **Mock Gmail MCP** | STDIO | `python -m makpa.mcp_servers.google_gmail.mock` | None | Zero-key demo | N/A |

### 1.2 Required Plugins / Libraries

| Plugin | Purpose | Install |
|--------|---------|---------|
| `langchain-mcp-adapters` | `MultiServerMCPClient` — converts MCP tools to LangChain tools | `pip install langchain-mcp-adapters` |
| `mcp` (official SDK) | STDIO + Streamable HTTP transport | `pip install mcp>=1.0.0` |
| `langchain-google-genai` | Gemini LLM + embeddings | `pip install langchain-google-genai` |
| `langchain-groq` | Groq LLM | `pip install langchain-groq` |
| `langchain-chroma` / `langchain-pinecone` / `langchain-qdrant` | Vector store backends | `pip install langchain-chroma langchain-pinecone langchain-qdrant` |
| `langchain-huggingface` | Default embeddings (MiniLM) | `pip install langchain-huggingface` |
| `google-api-python-client` + `google-auth-oauthlib` | Local Google MCP wrappers | `pip install google-api-python-client google-auth-oauthlib` |
| `langgraph` + `langgraph-checkpoint` | Graph runtime + `MemorySaver` | `pip install langgraph` |

### 1.3 Environment Variables Per MCP Server

```bash
# GitHub MCP
GITHUB_MCP_URL=https://api.githubcopilot.com/mcp/
GITHUB_PAT=github_pat_...
GITHUB_MCP_MODE=auto          # auto | mock | real

# Google Calendar MCP
GOOGLE_CALENDAR_MCP_URL=https://calendarmcp.googleapis.com/mcp/v1
GOOGLE_MCP_MODE=auto          # official | local | auto | mock
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_OAUTH_SCOPES=https://www.googleapis.com/auth/calendar,https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.send
GOOGLE_TOKEN_CACHE_PATH=./data/google_token.json
GOOGLE_OAUTH_REDIRECT_PORT=8080

# Gmail MCP
GOOGLE_GMAIL_MCP_URL=https://gmailmcp.googleapis.com/mcp/v1

# Retrieval MCP
RAG_MCP_MODE=stdio

# Timeouts / retries
MCP_TOOL_TIMEOUT_SECONDS=30
MCP_RETRY_ATTEMPTS=3
MCP_TOOL_CACHE_TTL_SECONDS=300
```

### 1.4 Connection Failure Behaviour

| Failure | Behaviour |
|---------|-----------|
| GitHub MCP unreachable | Retry ×3 (exponential + jitter) → downgrade to mock STDIO server → banner shows `GitHub MCP: mock` |
| Google official MCP unreachable | `auto` probes with 3s timeout → fallback to local STDIO wrapper → fallback to mock |
| OAuth refresh failed | Print reauth URL, exit code `3` |
| PAT missing | Skip real path, use mock, banner shows downgrade reason |
| Tool timeout | Cancel, return partial result with structured warning |

---

## Part 2 — Test Cases for the Agent

Test cases are grouped by layer. Each row is a distinct assertion. IDs follow `TC-<layer>-<n>`.

### 2.1 Foundation / Configuration Tests (`tests/test_config.py`)

| ID | Test | Input | Expected |
|----|------|-------|----------|
| TC-CFG-01 | Mode resolution defaults to `demo` with no keys | empty env | `resolved_mode == DEMO` |
| TC-CFG-02 | `live` downgrades to `free` when GitHub PAT missing | `MAKPA_MODE=live`, no PAT | `resolved_mode == FREE`, downgrade reason logged |
| TC-CFG-03 | `free` downgrades to `demo` when no LLM key | `MAKPA_MODE=free`, no Gemini/Groq | `resolved_mode == DEMO` |
| TC-CFG-04 | LLM provider picks Gemini when key present | `GOOGLE_API_KEY=x` | `resolved_llm_provider == GEMINI` |
| TC-CFG-05 | LLM provider falls back to Groq | Gemini key absent, Groq present | `resolved_llm_provider == GROQ` |
| TC-CFG-06 | Vector store resolves `chroma_local` in demo | `MAKPA_MODE=demo` | `resolved_vector_store == CHROMA_LOCAL` |
| TC-CFG-07 | Vector store fallback chain | `VECTOR_STORE=pinecone`, no key | falls back to `chroma_http` or `chroma_local`, reason logged |
| TC-CFG-08 | Google MCP mode resolves `mock` without credentials | no OAuth cache | `resolved_google_mcp_mode == MOCK` |
| TC-CFG-09 | Startup banner prints all resolved fields | any env | banner contains mode, LLM, vector store, GitHub path, Google path, OAuth state |
| TC-CFG-10 | Invalid enum value rejected | `MAKPA_MODE=banana` | `ValidationError` |

### 2.2 LLM Factory Tests (`tests/test_llm_factory.py`)

| ID | Test | Expected |
|----|------|----------|
| TC-LLM-01 | `get_llm()` returns Gemini with Gemini key | `ChatGoogleGenerativeAI` instance |
| TC-LLM-02 | `get_llm()` returns Groq with Groq key | `ChatGroq` instance |
| TC-LLM-03 | `get_llm()` returns MockChatModel with no keys | `MockChatModel` instance |
| TC-LLM-04 | Rate-limit fallback Gemini → Groq | second call uses Groq, warning logged |
| TC-LLM-05 | Mock returns RAG-shaped answer for RAG prompt | answer contains `[source:` |
| TC-LLM-06 | Mock returns refusal for empty-context prompt | `"No relevant documents found."` |
| TC-LLM-07 | Cache returns same instance across calls | `get_llm() is get_llm()` |
| TC-LLM-08 | `clear_llm_cache()` resets | new instance after clear |

### 2.3 Embedding Factory Tests (`tests/test_embeddings.py`)

| ID | Test | Expected |
|----|------|----------|
| TC-EMB-01 | Default provider is HuggingFace | `HuggingFaceEmbeddings`, model `all-MiniLM-L6-v2` |
| TC-EMB-02 | Gemini opt-in with key | `GoogleGenerativeAIEmbeddings` |
| TC-EMB-03 | Fallback to HuggingFace when Gemini fails | HF instance returned, warning logged |
| TC-EMB-04 | Cache returns same instance | identity check passes |
| TC-EMB-05 | Batch size read from settings | `embed_documents` called with configured batch |

### 2.4 Vector Store Factory Tests (`tests/test_vectorstore_factory.py`, `tests/test_vectorstore_backends.py`)

| ID | Test | Expected |
|----|------|----------|
| TC-VS-01 | `pinecone` returns `PineconeVectorStore` | type check |
| TC-VS-02 | `chroma_http` returns `ChromaHTTPVectorStore` | type check |
| TC-VS-03 | `chroma_local` returns `ChromaLocalVectorStore` | type check |
| TC-VS-04 | `qdrant` returns `QdrantVectorStore` | type check |
| TC-VS-05 | Pinecone uses `ServerlessSpec` only | no pod-based index created |
| TC-VS-06 | Missing dependency logs warning (not silent null) | `warnings.warn` called |
| TC-VS-07 | `add_documents` returns deterministic IDs | same input → same IDs |
| TC-VS-08 | `similarity_search_with_mmr` returns `(Document, score)` tuples | shape check |
| TC-VS-09 | `delete_collection` clears all vectors | `collection_info()["count"] == 0` |
| TC-VS-10 | Metadata preserved on round-trip | `source`, `page`, `chunk_index` intact |

### 2.5 RAG Ingestion Tests (`tests/test_ingestion.py`)

| ID | Test | Expected |
|----|------|----------|
| TC-RAG-01 | Ingest sample PDF creates >0 chunks | `chunks_created >= 30` |
| TC-RAG-02 | Re-ingest is idempotent | two runs produce identical `document_ids` |
| TC-RAG-03 | Chunk metadata includes `source`, `page`, `chunk_index` | all present |
| TC-RAG-04 | Loader respects `PDF_LOADER` setting | pymupdf vs pypdf |
| TC-RAG-05 | Chunk size respects `RAG_CHUNK_SIZE` | no chunk exceeds configured max |
| TC-RAG-06 | Missing PDF raises clear error | message includes path |
| TC-RAG-07 | Document id derived from file hash | deterministic |

### 2.6 RAG Retriever + Faithfulness Tests (`tests/test_retriever.py`)

| ID | Test | Expected |
|----|------|----------|
| TC-RET-01 | MMR args forwarded from settings | `k`, `fetch_k`, `lambda_mult` match settings |
| TC-RET-02 | Empty retrieval returns `[]` (never raises) | no exception |
| TC-RET-03 | `format_citations` returns `{source, page, chunk_id}` | shape check |
| TC-RET-04 | `grounded_answer` refuses on empty context | `NO_DOCS_MESSAGE` |
| TC-RET-05 | `validate_answer` rejects uncited non-empty answer | appends citation or coerces to refusal |
| TC-RET-06 | MMR re-ranks across ≥30 chunks | lambda 0 vs 1 orders differ |
| TC-RET-07 | Citations include score | `score` field present |

### 2.7 RAG Subgraph Tests (`tests/test_rag_graph.py`)

| ID | Test | Expected |
|----|------|----------|
| TC-RG-01 | Single-question flow returns `status: ok` | state shape |
| TC-RG-02 | Empty retrieval short-circuits to `status: empty` | no LLM call |
| TC-RG-03 | Answer always has ≥1 citation on non-empty context | assertion |
| TC-RG-04 | State schema uses only declared keys | no extra keys |
| TC-RG-05 | Subgraph invokable standalone | `run_rag("...")` returns dict |

### 2.8 GitHub MCP Tests (`tests/test_github_client.py`, `tests/test_github_tools.py`, `tests/test_github_graph.py`, `tests/test_github_mock_contract.py`)

| ID | Test | Expected |
|----|------|----------|
| TC-GH-01 | Client uses Streamable HTTP when PAT present | transport string |
| TC-GH-02 | Client falls back to STDIO mock without PAT | path resolved to mock |
| TC-GH-03 | Tool list cached for 5 minutes | second call no network |
| TC-GH-04 | Transport retry ×3 with backoff | attempt count |
| TC-GH-05 | Per-tool timeout cancels slow call | `TimeoutError` handled |
| TC-GH-06 | All 8 tools return normalized payloads | shape check per tool |
| TC-GH-07 | Invalid repo slug rejected | `ValidationError` |
| TC-GH-08 | `github_create_issue` requires confirmation | `requires_confirmation == True` |
| TC-GH-09 | Subgraph routes mutating plan to `confirm` | gate node reached |
| TC-GH-10 | `execute` blocks mutating tool without `confirmed` flag | no tool call made |
| TC-GH-11 | Decline at gate leaves no side effects | exit code `2`, tool not called |
| TC-GH-12 | Mock server answers `tools/list` over STDIO | all 8 tool names returned |
| TC-GH-13 | Mock server answers `tools/call` for each tool | payload shape |
| TC-GH-14 | Zero-key GitHub flow completes | exit code `0` |
| TC-GH-15 | Live read-only query (flagged) | skips cleanly without PAT |

### 2.9 Google OAuth Tests (`tests/test_oauth.py`)

| ID | Test | Expected |
|----|------|----------|
| TC-OA-01 | PKCE verifier/challenge pair valid (RFC 7636) | S256 match |
| TC-OA-02 | Consent URL contains scopes | scopes present |
| TC-OA-03 | Token cache round-trip | tokens persisted, 0600 mode |
| TC-OA-04 | Silent refresh on expired access token | refresh called, no browser |
| TC-OA-05 | Scope drift triggers reauth | `ReauthRequiredError` raised |
| TC-OA-06 | Reauth path prints URL and exits `3` | exit code check |
| TC-OA-07 | Token contents never logged | log scan |
| TC-OA-08 | Cache file mode is `0600` | `stat` check |
| TC-OA-09 | Browser flow (mocked callback) exchanges code | tokens stored |

### 2.10 Calendar MCP Tests (`tests/test_google_calendar_contract.py`)

| ID | Test | Expected |
|----|------|----------|
| TC-CAL-01 | `calendar_list_events` returns ISO UTC timestamps | regex match |
| TC-CAL-02 | `calendar_create_event` guards end > start | `ValidationError` |
| TC-CAL-03 | `calendar_check_availability` returns free/busy payload | shape check |
| TC-CAL-04 | Availability payload includes `attendee_mode` and `partial` | fields present |
| TC-CAL-05 | `calendar_update_event` patch with no fields rejected | clear error |
| TC-CAL-06 | Quota error returns structured envelope | no crash |
| TC-CAL-07 | Mock server answers `tools/list` + `tools/call` | all 4 tools |

### 2.11 Gmail MCP Tests (`tests/test_google_gmail_contract.py`)

| ID | Test | Expected |
|----|------|----------|
| TC-GM-01 | `gmail_search_messages` returns message ids | list shape |
| TC-GM-02 | `gmail_read_message` extracts subject/from | fields present |
| TC-GM-03 | `gmail_draft_message` creates draft id | `draft_id` returned |
| TC-GM-04 | `gmail_send_message` sends direct or via `draft_id` | both paths work |
| TC-GM-05 | RFC 2822 encoding correct (UTF-8, base64url) | round-trip decode |
| TC-GM-06 | Invalid recipient rejected | `ValidationError` |
| TC-GM-07 | Auth failure returns structured envelope | no crash |
| TC-GM-08 | Mock server answers all 4 tools over STDIO | contract test |

### 2.12 Google Subgraph + Composite Flow Tests (`tests/test_google_graph.py`, `tests/test_google_composite.py`)

| ID | Test | Expected |
|----|------|----------|
| TC-GG-01 | Plan routes to correct service (calendar/gmail/both) | `service` field |
| TC-GG-02 | Gate routes mutating plan to `confirm` | gate reached |
| TC-GG-03 | `execute` blocks mutating tool without confirmation | no tool call |
| TC-GG-04 | Composite: approve/approve produces `evt` + `msg` ids | both present |
| TC-GG-05 | Composite: decline gate 1 → no side effects | calendar and gmail not called |
| TC-GG-06 | Composite: decline gate 2 → event kept, email skipped | explicit message |
| TC-GG-07 | Composite: busy slot proposes alternatives | alternatives in answer |
| TC-GG-08 | Composite: `rollback` at gate 2 cancels event | `status: cancelled` |
| TC-GG-09 | Partial availability refuses auto-create | refusal message |
| TC-GG-10 | Two gates used, no bypass | exactly two `interrupt()` calls |

### 2.13 Supervisor Tests (`tests/test_supervisor_router.py`, `tests/test_supervisor_graph.py`, `tests/test_supervisor_e2e.py`)

| ID | Test | Expected |
|----|------|----------|
| TC-SUP-01 | Single-domain query routes to exactly one agent | `next` length == 1 |
| TC-SUP-02 | Two-domain query dispatches both via `Send` | two `Send` objects |
| TC-SUP-03 | Three-domain query dispatches all three | three `Send` objects |
| TC-SUP-04 | Heuristic router works without LLM | zero-key routing |
| TC-SUP-05 | Invalid LLM literal falls back to heuristic | no crash |
| TC-SUP-06 | Aggregation preserves citations | citations intact |
| TC-SUP-07 | Aggregation preserves event + message ids | ids present |
| TC-SUP-08 | Overall status `ok` when all sub-agents ok | status check |
| TC-SUP-09 | Overall status `partial` when one errored | status check |
| TC-SUP-10 | Reflection retries errored agent once | retry count == 1 |
| TC-SUP-11 | Double error finalizes with `status: error` | no infinite loop |
| TC-SUP-12 | Parallel wall time < sequential (mock sleeps) | timing assertion |
| TC-SUP-13 | Subgraph `interrupt()` propagates to parent | `__interrupt__` present |
| TC-SUP-14 | Resume with `{"confirm": true}` continues flow | subgraph completes |
| TC-SUP-15 | Thread state does not bleed across threads | two threads isolated |

### 2.14 Zero-Key End-to-End Tests (`tests/test_zero_key.py`, `tests/test_supervisor_live.py`)

| ID | Test | Expected |
|----|------|----------|
| TC-E2E-01 | Full demo runs with no `.env` | exit `0` |
| TC-E2E-02 | RAG scenario returns cited answer | citation count ≥1 |
| TC-E2E-03 | GitHub scenario returns PR list | PR #7 present |
| TC-E2E-04 | Composite scenario returns event + message ids | both present |
| TC-E2E-05 | Demo transcript matches expected format | regex check |
| TC-E2E-06 | Live Groq path (flagged) | runs or skips with reason |
| TC-E2E-07 | Live GitHub path (flagged) | runs or skips with reason |
| TC-E2E-08 | Live Google path (flagged) | runs or skips with reason |

### 2.15 CLI Tests (`tests/test_cli.py`, `tests/test_cli_agent.py`, `tests/test_google_cli.py`)

| ID | Test | Expected |
|----|------|----------|
| TC-CLI-01 | One-shot query exits `0` | exit code |
| TC-CLI-02 | Approve at gate resumes and completes | exit `0` |
| TC-CLI-03 | Decline at gate exits `2` | exit code |
| TC-CLI-04 | Rollback at gate 2 exits `0` with rollback message | exit code |
| TC-CLI-05 | Reauth required exits `3` | exit code |
| TC-CLI-06 | `--mode demo` overrides mode | banner shows `demo` |
| TC-CLI-07 | `--thread` resumes same thread | state continuity |
| TC-CLI-08 | `--interactive` REPL keeps memory | multi-turn memory |
| TC-CLI-09 | Emoji indicators render on Windows UTF-8 | no crash |
| TC-CLI-10 | Failure path exits non-zero | exit `1` |

---

## Part 3 — Test Execution Order & Gates

| Gate | Command | Pass Criteria |
|------|---------|--------------|
| Lint | `ruff check src/ tests/ scripts/` | clean |
| Types | `mypy src/makpa --config-file=mypy.ini --follow-imports=skip` | clean |
| Unit + Contract | `pytest tests/ -q -m "not live"` | all pass |
| Coverage | `pytest tests/ --cov=src/makpa --cov-report=term-missing` | ≥85% per module |
| Zero-key | `pytest tests/test_zero_key.py -q` | pass with no `.env` |
| Live (flagged) | `RUN_LIVE_TESTS=1 pytest tests/ -q -m live` | runs or skips cleanly |
| Demo | `python scripts/demo.py` | exit `0` in `demo` and `free` |

---

## Part 4 — Risk Notes for MCP Connections

| Risk | Mitigation |
|------|-----------|
| Official Google MCP servers in preview | Local STDIO wrapper is the guaranteed path; `auto` mode probes and falls back |
| GitHub MCP endpoint retired | `GITHUB_MCP_URL` configurable; mock server preserves demo |
| OAuth refresh token expired | Reauth path prints URL, exit `3` |
| Pinecone free tier exhausted | Chroma HTTP is primary; Pinecone is documented swap |
| MCP STDIO does not forward parent env | Explicit `env=` passed to every STDIO connection |
| Tool timeout on slow networks | Configurable via `MCP_TOOL_TIMEOUT_SECONDS` |

---

## Part 5 — Minimal `.env` Per Mode

```bash
# DEMO — no keys, everything mocked
MAKPA_MODE=demo

# FREE — real LLM, mocked MCP
MAKPA_MODE=free
GOOGLE_API_KEY=...      # or GROQ_API_KEY=...

# LIVE — real LLM + real MCP (requires credentials)
MAKPA_MODE=live
GOOGLE_API_KEY=...
GITHUB_PAT=github_pat_...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_TOKEN_CACHE_PATH=./data/google_token.json
```

---

This document pairs with `GRADER_CHECKLIST.md` (how to verify) and `ARCHITECTURE.md` (how it fits together). Together they give a reviewer everything needed to run, verify, and defend the system without asking questions.