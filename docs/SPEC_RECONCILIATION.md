# MAKPA - Spec vs Delivered Reconciliation

Origin: the one-shot master build prompt that defined MAKPA before the
phase split. This document records every intentional drift with reasons
and dates. Nothing below is accidental.

## Drift 1 - Pinecone Demoted (2026-09-30, P1-PINE-1)

- **Spec:** Pinecone as the primary hosted vector store.
- **Delivered:** Chroma HTTP primary; Pinecone kept as a serverless-only
  swap (SDK pinned to 7.3.0).
- **Reason:** `langchain-pinecone` required `pinecone<8`, and the 7.x
  `ServerlessSpec` path could only be verified against a mocked SDK (no
  Starter account in sandbox). Chroma HTTP was verifiable, self-hostable,
  and free-tier friendly.
- **Stated in:** `.env.example` ("primary hosted store"), `README.md`
  (hosted-store policy + drift table), `docs/TRACE.md` (P1-PINE-1).

## Drift 2 - `live` Is a Soft Label (2026-09-30..2026-10-01, FLAG-1/FLAG-A)

- **Spec:** `live` = real GitHub + real Google MCP.
- **Delivered:** `live` = live LLM inference (Groq, metered, proven end to
  end with raw output in `TRACE.md`) with MCP on mock unless the user
  supplies `GITHUB_MCP_PAT` / Google OAuth. The downgrade chain
  (`live` -> `free` -> `demo`) is real and bannered.
- **Reason:** No PAT or Google account exists in any available
  environment. Renaming modes this late would churn every doc, test,
  and CLI; instead the startup banner annotates live mode explicitly:
  `live = live LLM; MCP mocked unless credentials present`.
- **Stated in:** banner note, `README.md` (mode table + drift table),
  `docs/TRACE.md` (FLAG-1 amendment, FLAG-A evidence).

## Drift 3 - LangSmith Is Conditional, Not Decorated Everywhere (2026-10-01)

- **Spec:** `@traceable` on every entry point.
- **Delivered:** `@entrypoint(name)` on all four `run_*` functions
  (`makpa.supervisor/rag/github/google`), applying langsmith's
  `@traceable` only when `LANGCHAIN_API_KEY` is set, strict no-op
  otherwise.
- **Reason:** Unconditional tracing warns on every zero-key call and
  adds network attempts to offline demos. Conditional decoration keeps
  demo output clean while sending real runs when configured.
- **Stated in:** `src/makpa/utils/tracing.py`, `tests/test_tracing.py`,
  this document.

## Non-Drifts Often Mistaken for Drift

- **Mock MCP paths** (GitHub + Calendar + Gmail): the spec's dual-path
  Google design generalized honestly; mocks preserve zero-key grading.
- **Gate-2 `rollback`**: additive option on top of the specified two
  gates; both gates still exist exactly as specified.
- **Heuristic planner fallbacks**: unspecified but required for zero-key
  routing; the LLM remains the primary decider whenever available.
