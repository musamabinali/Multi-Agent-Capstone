# MAKPA - Viva Q&A (Oral Defense Bank)

## Architecture

**Q: Why hub-and-spoke instead of peer-to-peer agents?**
A: One classifier, one merge point, one audit trail. `Send` fan-out gives
parallelism; the `aggregate` barrier gives a single place to enforce
attribution and status semantics. Peer-to-peer would scatter both.

**Q: How do parallel branches avoid clobbering shared state?**
A: `agent_outputs` and `confirmations` use merge reducers, and each worker
writes only its own key. The wall-time test proves the barrier works.

**Q: What happens when a sub-agent fails?**
A: Its summary carries `status: error`; `aggregate` computes overall
status (`ok` only if all clean, `error` only if all failed, else
`partial`); the `reflection` node retries errored agents exactly once,
then finalizes. No infinite loops by construction.

## Interrupt Model

**Q: How does a gate inside a subgraph reach the CLI?**
A: Workers share the supervisor's checkpointer and re-raise
`GraphInterrupt` instead of converting it to an error. The parent pauses
with `__interrupt__` state; the CLI polls via `detect_interrupt` /
snapshot `next` and resumes with `resume_with`. Proven by a two-resume
pass-through test and manual two-gate runs.

**Q: Why does `invoke()` return `__interrupt__` instead of raising?**
A: LangGraph 1.2 behavior with a checkpointer present: pause is state,
not an exception. Without a checkpointer it raises. The shared helper
handles both, which is why Phase 2 code had to be refactored in Phase 3.

**Q: Can a mutating tool run without confirmation?**
A: No, twice over: the graph routes mutating plans through `confirm`
nodes, and `execute` independently blocks mutating tools unless the
`confirmed` flag is set. Tests assert the block with strict no-invoke
mocks.

## Safety & Honesty

**Q: Gate-2 decline keeps the event — isn't that a trap?**
A: It was, so gate 2 offers `[y/N/rollback]`; rollback cancels the event
via `calendar_update_event(status=cancelled)` and reports `rolled_back`.

**Q: Does availability checking verify attendees?**
A: Only the queried calendar. With attendees present under the default
`own_only` mode the result is labeled `partial` and auto-create is
refused; `all` restores the old behavior explicitly.

**Q: What does `live` mode actually prove?**
A: Metered LLM inference end to end (raw output in TRACE). MCP stays
mocked without user credentials — bannered, documented, and tested via
flagged skipping tests. Deleting the mode would have hidden the
downgrade chain, which is itself a tested feature.

**Q: Why was Pinecone demoted?**
A: `langchain-pinecone` needed `pinecone<8`; the 7.x serverless path was
verifiable only against mocks. Chroma HTTP was verifiable for real, so
it became primary and Pinecone a documented swap. Recorded in P1-PINE-1.

## Engineering Process

**Q: 98% coverage — is it real or theater?**
A: Real branches: error envelopes, fallback chains, decline paths,
timeout/retry, resume cycles. Dead code found by coverage pressure was
deleted (two unreachable JSON guards), and one "coverage" chase exposed
a genuine regression (`__package__` bug that nulled all backends).

**Q: Biggest surprise?**
A: Nested `graph.invoke()` raising instead of propagating interrupts —
found only because isolated-thread demo runs removed leaked state that
had been masking the failure. The demo script is a better tester than
the unit suite for integration bugs.

**Q: What would you do with one more week?**
A: Live PAT/OAuth runs to close FLAG-A/B for real; a second vector-store
backend in the demo matrix; token-streaming in the CLI instead of
section printing.
