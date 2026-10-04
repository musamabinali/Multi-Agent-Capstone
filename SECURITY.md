# MAKPA — Security Policy

## The one rule

**`.env` never leaves a local machine.** It is gitignored (`.gitignore:53`) and has never
been committed (verified `2026-10-04`: `git check-ignore -v .env` matches, `git log --all -- .env`
is empty, no key patterns in the last 50 commits, `.env.example` carries blanks only).
No credential rotation is currently required. If that ever changes, rotate everything below today.

## Where each credential lives

| Credential | Env var | Lives in | Notes |
|---|---|---|---|
| Google Gemini API key | `GEMINI_API_KEY` | `.env` only | Free-tier quota exhausts fast; 429s fall back down the chain |
| Groq API key | `GROQ_API_KEY` | `.env` only | Metered inference; proven live in FLAG-A |
| GitHub fine-grained PAT | `GITHUB_MCP_PAT` | `.env` only | Scope to the repos you demo; read-only suffices except issue creation |
| Google OAuth client ID / secret | `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | `.env` only | Desktop-app credentials; localhost redirect only |
| Google OAuth tokens | `GOOGLE_TOKEN_CACHE_PATH` (`./data/google_token_cache.json`) | Local file, `0600`, gitignored (`.gitignore:72`) | Never logged; reauth exits 3 on refresh failure |
| Pinecone API key | `PINECONE_API_KEY` | `.env` only | Serverless indexes only |
| Qdrant URL + API key | `QDRANT_URL` / `QDRANT_API_KEY` | `.env` only | Cloud cluster URL counts as sensitive |
| ChromaDB host/port | `CHROMA_HOST` / `CHROMA_PORT` | `.env` / compose | Localhost by default; no secret |
| LangSmith API key | `LANGCHAIN_API_KEY` | `.env` only | Enables tracing; absence is a clean no-op |

## How to rotate each one

1. **GitHub PAT** — GitHub Settings → Developer settings → Fine-grained tokens → revoke, mint a new
   token with the same scopes, replace `GITHUB_MCP_PAT`, restart any running adapter (`/api/health`
   should flip `github_path`).
2. **Gemini / Groq keys** — revoke in Google AI Studio / Groq console, replace in `.env`. The LLM
   factory falls back automatically; `probe_llm()` (every CLI startup) confirms the winner.
3. **Google OAuth** — revoke at `https://myaccount.google.com/permissions`, delete the local token
   cache file, re-run any `google_demo` command and complete the browser consent again.
4. **Pinecone / Qdrant** — rotate in the provider console, replace in `.env`, re-run
   `rag_demo info` to confirm the resolved store.
5. **LangSmith** — regenerate in LangSmith settings, replace in `.env`.

## Rules for contributors and demos

- Never paste `.env` contents into issues, transcripts, screenshots, or chat logs. `TRACE.md` and
  `DEMO_TRANSCRIPT.md` record key *presence* (e.g. "Groq key set") and model names, never values.
- Never `git add -f` an ignored file. Before any `git push`, run:
  `git log --all --oneline -- .env` (must be empty) and re-check `git check-ignore -v .env`.
- Demo on shared screens with `LOG_LEVEL=INFO` (default): token values are never logged at any level
  (OAuth module redacts; verify after any logging change with `LOG_LEVEL=DEBUG` + a grep for the value).
- Test files blank credentials with `monkeypatch.setenv(VAR, "")` — never delete-and-rely, because the
  repo `.env` carries keys and deletion would re-expose real values mid-test.
- The mock calendar store (`data/mock_calendar.json`) is fixture/test residue by design; it contains
  only `example.com` addresses. Confirm no real attendee ever lands there before committing it.
