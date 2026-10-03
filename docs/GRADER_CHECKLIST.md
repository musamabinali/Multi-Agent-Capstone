# MAKPA - Grader Checklist

How to verify every claim, file by file.

## Install & Smoke

| Check | Command | Evidence |
|-------|---------|----------|
| Bootstrap | `make bootstrap` | `scripts/bootstrap.py` (ruff-clean) |
| Zero-key smoke | `python -m makpa.cli.smoke_test` (no `.env`) | `RESULT: PASS`, DEMO banner |
| Lint | `ruff check src/ tests/ scripts/` | All checks passed |
| Types | `mypy src/makpa --config-file=mypy.ini --follow-imports=skip` | 60 files, no issues |
| Suite | `pytest tests/ -q` | 238 passed, 3 skipped, TOTAL 98% |

## Sub-Agents (Zero-Key)

| Check | Command | Evidence |
|-------|---------|----------|
| RAG ingest/ask | `python -m makpa.cli.rag_demo ingest` / `ask "..."` | 75 chunks; cited answer |
| GitHub flow | `python -m makpa.cli.github_demo list-prs --repo octo-demo/hello-world` | `status: ok`, PR #7 |
| GitHub gate | `... ask "Create an issue in ..."` then decline | exit 2, nothing created |
| Google flow | `python -m makpa.cli.google_demo list-events --days 7` | `evt-001`, `evt-002` |
| Composite gates | `... ask "schedule a meeting with a@example.com from <iso> to <iso>"` | gate 1, gate 2, `evt-mock-100` + message id |
| Gate-2 rollback | answer `rollback` at gate 2 | event cancelled, `rolled_back` |
| Partial availability | default mode + attendees | refusal message, no event |

## Supervisor & Demo

| Check | Command | Evidence |
|-------|---------|----------|
| One-shot | `python -m makpa.cli.agent "What does the sample PDF say?"` | routed to `rag_agent`, citations |
| REPL | `python -m makpa.cli.agent --interactive` | thread memory across turns |
| Full demo | `python scripts/demo.py [--mode demo\|free\|live]` | exit 0; `docs/DEMO_TRANSCRIPT.md` |
| Parallelism | `pytest tests/test_supervisor_e2e.py::test_parallel_faster_than_sequential -q` | parallel < sequential |
| Interrupts | `pytest tests/test_supervisor_e2e.py::test_interrupt_pass_through_and_resume -q` | two resumes to `ok` |

## Live & Credentials

| Check | Command | Evidence |
|-------|---------|----------|
| Live LLM | `MAKPA_MODE=free python -m makpa.cli.rag_demo ask "..."` (Groq key) | `llm: groq (...)`, raw output in `TRACE.md` FLAG-A |
| Live GitHub | `RUN_GITHUB_INTEGRATION=1 GITHUB_MCP_PAT=<pat> pytest tests/test_github_integration.py -q` | runs or skips with reason |
| Live Google | `RUN_LIVE_GOOGLE_TESTS=1 pytest tests/test_google_integration.py -q` | runs or skips with reason |
| Live Phase 4 | `RUN_LIVE_PHASE4_TESTS=1 ... tests/test_supervisor_live.py -q` | runs or skips with reason |
| Reauth | `GOOGLE_MCP_MODE=local python -m makpa.cli.google_demo list-events` (no creds) | exit 3 + reauth URL |
| OAuth manual | README "Manual OAuth verification guide" | 6 steps, user-signed |

## Docs & Design Honesty

| Check | Location |
|-------|----------|
| Spec drift | `README.md` table + `docs/SPEC_RECONCILIATION.md` |
| Architecture | `docs/ARCHITECTURE.md` |
| Transcript | `docs/DEMO_TRANSCRIPT.md` (demo + free) |
| Tasks/gates | `docs/TODO.md` (64/64), `docs/TRACE.md` |
| Risks | `docs/RISK_REGISTER.md` (R-01..R-26) |
