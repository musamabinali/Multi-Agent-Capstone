# MAKPA - Executive Summary

MAKPA is a hub-and-spoke LangGraph multi-agent system: a supervisor
classifies intent (structured LLM output, heuristic fallback), fans out
to RAG, GitHub, and Google Workspace subgraphs via parallel `Send`
dispatch, merges attributed results in `aggregate`, and retries errored
agents once in `reflection`.

- **Three modes**: `demo` (zero keys), `free` (LLM key only), `live`
  (live LLM; MCP mocked unless credentials present — bannered).
- **Safety**: every mutating tool stops at an `interrupt()` gate with a
  boxed payload preview; gate 2 of the scheduling flow offers rollback;
  availability with external attendees is labeled partial and refuses
  auto-create by default.
- **Proof**: 238+ tests, 98% coverage, `ruff` + `mypy --strict` clean at
  every gate, `python scripts/demo.py` exits 0 in demo and free modes,
  raw transcripts in `docs/DEMO_TRANSCRIPT.md`.
- **Honest limits**: live GitHub/Google MCP need user credentials
  (flagged tests skip cleanly); the OAuth browser handshake awaits manual
  verification (guide in README); Pinecone is a documented swap, not
  primary (Chroma HTTP is).
