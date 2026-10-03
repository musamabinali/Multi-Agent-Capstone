# MAKPA — Risk Register

| ID | Risk Description | Probability | Impact | Mitigation | Owner |
|----|------------------|-------------|--------|------------|-------|
| R-01 | Google's official MCP servers unavailable in environment | High | High | Implement local MCP wrappers as fallback; auto-detect and log choice; test local path in CI | |
| R-02 | OAuth refresh token expires between runs | Medium | High | Implement PKCE with automatic token refresh; cache tokens to file; print reauth URL on refresh failure | |
| R-03 | Pinecone free tier exhausted during demo | Medium | Medium | Default to Chroma HTTP for free mode; monitor usage; add quota check in vector store factory | |
| R-04 | GitHub PAT lacks required scopes | Medium | High | Document required scopes in .env.example; validate scopes at startup; clear error message | |
| R-05 | Sample PDF missing from data folder | Low | Medium | Bundle sample PDF in repo; validate path at startup; provide helpful error with download instructions | |
| R-06 | Mock chat model drifts from real model behavior | Medium | Medium | Version mock responses; test against real provider periodically; document known differences | |
| R-07 | STDIO MCP wrapper crashes on import | Low | High | Wrap MCP server imports in try/except; lazy-load servers; smoke test validates imports | |
| R-08 | Three-mode downgrade chain masks real configuration error | Medium | Medium | Log every downgrade with explicit reason; print startup banner with downgrade summary; fail fast in live mode if critical config missing | |
| R-09 | Chroma HTTP server not running in free mode | Medium | Medium | Health check at startup; clear error with start instructions; fallback to Chroma local in demo | |
| R-10 | LangSmith tracing fails silently | Low | Low | Make tracing optional; no-op when key missing; log tracing status at startup | |
| R-11 | LLM provider rate limits cause cascade failures | Medium | Medium | Implement retry with exponential backoff; fallback to next provider in chain; configurable timeout | |
| R-12 | Checkpointer thread_id collisions in concurrent runs | Low | Medium | Use deterministic thread_id from user + scenario; document isolation guarantees | |
| R-13 | LangChain wrapper API drift (MMR with scores removed) — MATERIALIZED | High | Medium | Use max_marginal_relevance_search + similarity_search_with_score to attach scores; pinned langchain-chroma/pinecone/qdrant in requirements | |
| R-14 | HF embedding first-download latency (~60s) + Windows symlink warning — MATERIALIZED | High | Low | Model cached after first download; document HF_TOKEN + Developer Mode notes | |
| R-15 | Default model names rot (gemini-1.5-flash 404, Groq model 403) — MATERIALIZED | Medium | Medium | Startup probe_llm() warns on KNOWN_STALE_MODELS and fails fast in live mode; runtime fallback Gemini→Groq→Mock verified; update GEMINI_CHAT_MODEL/GROQ_CHAT_MODEL defaults before live demo | |
| R-16 | Pinecone v10 incompatible with langchain-pinecone (<8) — MATERIALIZED | Medium | Medium | Pinned pinecone 7.3.0; ServerlessSpec verified via mocked SDK; Chroma HTTP promoted to primary hosted store, Pinecone is a documented swap | |
| R-17 | GitHub PAT scope drift (token lacks read/write scopes for planned tools) | Medium | High | Validate repo slug client-side; fail fast with clear MCP error; mock server preserves demo without PAT; document required scopes before live demo | |
| R-18 | GitHub rate limits / MCP transport flakiness cause cascading tool failures | Medium | Medium | 3-retry exponential backoff with jitter on transport errors; per-tool timeout; structured JSON logs per call for diagnosis | |
| R-19 | GitHub MCP server unreachable (network or endpoint retired) | Medium | High | Degrade to mock STDIO server with banner notice; flagged integration test skips cleanly; no hardcoded endpoint assumptions beyond GITHUB_MCP_URL | |
| R-20 | OAuth token cache leaks (0600 file copied, logged, or committed) | Medium | High | 0600 file mode enforced; token contents never logged (only presence/expiry); cache path inside data/ (git-ignored); reauth on scope drift | |
| R-21 | Google API quota limits (Calendar/Gmail 429s) during demos | Medium | Medium | Structured error envelopes on quota failures; short-circuit with clear message; no retry storms (retry applies to transport, not API errors) | |
| R-22 | Official Google MCP servers unreachable or retired | Medium | High | Auto-mode probing with 3s timeout; silent fallback to local wrappers, then mocks; decision logged as JSON; banner shows resolved path | |
| R-23 | Timezone mishandling (naive vs aware datetimes across DST) | Medium | Medium | Single `parse_iso_utc()` normalizer (naive assumed UTC, output UTC ISO); shared by servers, tools, mocks, and graph; unit-tested branches | |
| R-24 | Parallel dispatch race conditions (Send branches clobbering shared state) | Medium | High | Merge reducers on `agent_outputs`/`confirmations`; workers write only their own keys; wall-time test proves parallel barrier behavior | |
| R-25 | Aggregation lossy merges (citations/ids dropped in the final message) | Medium | High | JSON summaries per agent decoded into attributed sections; e2e tests assert citations, event ids, message ids preserved | |
| R-26 | Thread-state collisions (shared threads leaking state between scenarios) | Medium | High | Deterministic per-scenario threads (`demo-{i}`); explicit `--thread` ids; no random identifiers; leak caught once by isolated-thread demo runs | |

## Risk Assessment Matrix

| Probability \ Impact | Low | Medium | High |
|---------------------|-----|--------|------|
| **High** | | R-01 | |
| **Medium** | R-10 | R-03, R-06, R-08, R-09, R-11 | R-02, R-04 |
| **Low** | | R-05, R-12 | R-07 |

## Mitigation Verification

Each mitigation must be testable:

- **R-01**: Run in environment without Google MCP servers → local wrappers used
- **R-02**: Use expired refresh token → auto-refresh or reauth URL printed
- **R-03**: Exhaust Pinecone quota → fallback to Chroma HTTP
- **R-04**: Use PAT with missing scopes → clear error at startup
- **R-05**: Remove sample PDF → helpful error with path
- **R-06**: Compare mock vs real responses in tests
- **R-07**: Import all MCP modules in smoke test → no crashes
- **R-08**: Run with partial live config → banner shows downgrade reasons
- **R-09**: Run free mode without Chroma HTTP → clear error
- **R-10**: Run without LangSmith key → no tracing, no errors
- **R-11**: Hit rate limit → retry then fallback
- **R-12**: Run concurrent threads → no collisions