# MAKPA - Architecture

Hub-and-spoke multi-agent system on LangGraph. The supervisor classifies
intent, fans out to isolated sub-agent subgraphs via the `Send` API
(parallel), merges outputs in `aggregate`, and retries errored agents
once in `reflection`.

```
                    +------------------+
                    |    supervisor    |
                    | classify -> Send |
                    +--------+---------+
                             | Send (parallel)
             +---------------+---------------+
             |               |               |
      +------v------+ +------v------+ +------v------+
      | RAG subgraph| |GitHub subgr.| |Google subgr.|
      | retrieval   | |plan/gate/   | |plan/gate/   |
      | generation  | |confirm(char)| |confirm x2 / |
      | validation  | |execute/synth| |composite    |
      +------+------+ +------+------+ +------+------+
             |               |               |
             +---------------+---------------+
                             | (barrier)
                      +------v------+
                      |  aggregate  |--error--> reflection (retry once) --> END
                      +------+------+                    |
                             | (ok/partial)              v
                             +--------------------------------> END
```

## State schemas

- `SupervisorState` (`supervisor/state.py`): `messages`, `next: list[str]`,
  `task_description`, `agent_outputs: dict[str, str]` (JSON summaries,
  merge-reduced), `confirmations: dict[str, bool]`, `status`
  (`ok|partial|error`).
- `RAGState`: `query`, `retrieved_chunks`, `citations`, `answer`, `status`.
- `GitHubState`: `question`, `plan`, `tool_results`, `answer`,
  `needs_confirmation`, `confirmed`, `status`.
- `GoogleState`: `question`, `service`, `action`, `payload`, `plan`,
  `tool_results`, `answer`, `needs_confirmation`, `confirmed`,
  `composite_stage`, `status`.

## Key patterns

- **Interrupt propagation**: subgraph workers share the supervisor's
  checkpointer and re-raise `GraphInterrupt`; the parent pauses with
  `__interrupt__` state. All resume flows use `makpa.utils.interrupts`
  (`detect_interrupt`, `resume_with`).
- **Confirmation semantics**: `confirmations[name]` is true when the agent
  finished with no pending gate (`ok|empty|rolled_back`).
- **Aggregation**: per-agent JSON summaries decode into attributed sections
  (citations, event/message ids, per-tool statuses preserved); overall
  status is `ok` when all are `ok|empty`, `error` when all errored,
  otherwise `partial`.
- **Deterministic threads**: `makpa-demo-{i}`, `{prefix}-main`, or explicit
  `--thread` ids. No random identifiers anywhere.
- **Downgrade chains**: live -> free -> demo (mode), official -> local ->
  mock (Google MCP), real -> mock (GitHub MCP). Every downgrade is bannered.
