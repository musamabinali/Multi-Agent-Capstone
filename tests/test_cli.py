"""CLI tests for rag_demo, ingest, and github_demo (Typer CliRunner)."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

runner = CliRunner()


def _probe_ok():
    return SimpleNamespace(provider="mock", model="mock-canned", warnings=[], message="ok")


def test_rag_demo_ask_ok_and_error():
    from makpa.cli import rag_demo

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.rag.run_rag",
            return_value={
                "answer": "cited answer here",
                "citations": [{"source": "s.pdf", "page": 1, "chunk_id": 0}],
                "status": "ok",
            },
        ),
    ):
        res = runner.invoke(rag_demo.app, ["ask", "What is this?"])
    assert res.exit_code == 0, res.output
    assert "cited answer" in res.output

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.rag.run_rag", side_effect=RuntimeError("down")),
    ):
        res = runner.invoke(rag_demo.app, ["ask", "q"])
    assert res.exit_code == 1


def test_rag_demo_ingest_info_reset():
    from makpa.cli import rag_demo
    from makpa.rag.ingestion import IngestionResult

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.cli.rag_demo.ingest_pdf",
            return_value=IngestionResult(75, 0, "chroma_local", 10, ["a"]),
        ),
    ):
        res = runner.invoke(rag_demo.app, ["ingest"])
    assert res.exit_code == 0 and "75" in res.output

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.cli.rag_demo.ingest_pdf", side_effect=FileNotFoundError("x")),
    ):
        res = runner.invoke(rag_demo.app, ["ingest"])
    assert res.exit_code == 1

    store = MagicMock()
    store.collection_info.return_value = {"type": "chroma_local", "total_vectors": 75}
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.vectorstore.create_vector_store", return_value=store),
    ):
        res = runner.invoke(rag_demo.app, ["info"])
    assert res.exit_code == 0 and "75" in res.output

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.vectorstore.create_vector_store", return_value=store),
    ):
        res = runner.invoke(rag_demo.app, ["reset", "--yes"])
    assert res.exit_code == 0
    store.delete_collection.assert_called()
    res = runner.invoke(rag_demo.app, ["reset"], input="n\n")
    assert res.exit_code == 0 and "Aborted" in res.output


def test_rag_demo_probe_failure_exits():
    from makpa.cli import rag_demo

    with patch("makpa.llm.probe_llm", side_effect=RuntimeError("live on mock")):
        res = runner.invoke(rag_demo.app, ["info"])
    assert res.exit_code == 1


def test_ingest_cli_ok_and_failure():
    from makpa.cli import ingest as ingest_cli
    from makpa.rag.ingestion import IngestionResult

    with patch(
        "makpa.cli.ingest.ingest_pdf",
        return_value=IngestionResult(75, 0, "chroma_local", 10, ["a"]),
    ):
        res = runner.invoke(ingest_cli.app, ["ingest"])
    assert res.exit_code == 0 and "successful" in res.output

    with patch("makpa.cli.ingest.ingest_pdf", side_effect=RuntimeError("down")):
        res = runner.invoke(ingest_cli.app, ["ingest"])
    assert res.exit_code == 1

    store = MagicMock()
    store.collection_info.return_value = {"type": "chroma_local"}
    with patch("makpa.vectorstore.create_vector_store", return_value=store):
        res = runner.invoke(ingest_cli.app, ["info"])
    assert res.exit_code == 0


def test_github_demo_direct_commands():
    from makpa.cli import github_demo

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.subagents.github.tools.github_list_prs",
            MagicMock(
                **{"invoke.return_value": {"status": "ok", "prs": [{"number": 7}], "count": 1}}
            ),
        ),
    ):
        res = runner.invoke(github_demo.app, ["list-prs", "--repo", "o/r"])
    assert res.exit_code == 0 and "ok" in res.output

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.subagents.github.tools.github_search_code",
            MagicMock(**{"invoke.return_value": {"status": "ok", "results": []}}),
        ),
    ):
        res = runner.invoke(github_demo.app, ["search", "--query", "q"])
    assert res.exit_code == 0

    # create-issue abort path.
    with patch("makpa.llm.probe_llm", return_value=_probe_ok()):
        res = runner.invoke(
            github_demo.app,
            ["create-issue", "--repo", "o/r", "--title", "T"],
            input="n\n",
        )
    assert res.exit_code == 2 and "Aborted" in res.output

    # create-issue approved path.
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.subagents.github.tools.github_create_issue",
            MagicMock(**{"invoke.return_value": {"status": "ok", "issue": {"number": 99}}}),
        ),
    ):
        res = runner.invoke(
            github_demo.app,
            ["create-issue", "--repo", "o/r", "--title", "T", "--yes"],
        )
    assert res.exit_code == 0 and "99" in res.output


def test_github_demo_ask_read_only_and_failure():
    from makpa.cli import github_demo

    graph = MagicMock()
    graph.invoke.return_value = {"answer": "PR #7 is open", "status": "ok"}
    graph.get_state.return_value = SimpleNamespace(next=())
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.subagents.github.create_github_graph", return_value=graph
        ),
    ):
        res = runner.invoke(github_demo.app, ["ask", "List PRs in o/r"])
    assert res.exit_code == 0 and "PR #7" in res.output

    bad_graph = MagicMock()
    bad_graph.invoke.side_effect = RuntimeError("down")
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.subagents.github.create_github_graph", return_value=bad_graph),
    ):
        res = runner.invoke(github_demo.app, ["ask", "q"])
    assert res.exit_code == 1


def test_github_demo_helpers():
    from makpa.cli import github_demo

    assert github_demo._pending_preview(MagicMock(), {}) == {
        "payload_preview": "(unavailable)"
    }
    snap = SimpleNamespace(
        next=("confirm",),
        tasks=[SimpleNamespace(interrupts=[SimpleNamespace(value={"a": 1})])],
    )
    graph = MagicMock()
    graph.get_state.return_value = snap
    assert github_demo._pending_preview(graph, {}) == {"a": 1}
    assert github_demo._is_paused(graph, {}) is True
    graph.get_state.return_value = SimpleNamespace(next=())
    assert github_demo._is_paused(graph, {}) is False
    graph.get_state.side_effect = RuntimeError("down")
    assert github_demo._is_paused(graph, {}) is False


def test_smoke_imports_and_probe_step():
    from makpa.cli import smoke_test

    ok, errors = smoke_test.test_imports()
    assert ok, errors
