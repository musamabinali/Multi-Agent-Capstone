"""Phase 2 polish: server handler units + github_demo error/edge paths."""

from __future__ import annotations

import asyncio
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from typer.testing import CliRunner

runner = CliRunner()


def _probe_ok():
    return SimpleNamespace(provider="mock", model="mock-canned", warnings=[], message="ok")


# ---------------------------------------------------------------------------
# Mock GitHub server handlers
# ---------------------------------------------------------------------------


def test_github_server_handlers_and_main():
    import json

    from makpa.mcp_servers.github import server as srv

    assert srv.MOCK_REPO == "octo-demo/hello-world"
    assert asyncio.run(srv.list_github_tools()) == srv.TOOL_DEFS

    out = asyncio.run(srv.call_github_tool("list_prs", {"repo": "o/r"}))
    assert json.loads(out[0].text)["status"] == "ok"
    out = asyncio.run(srv.call_github_tool("nope", {}))
    assert json.loads(out[0].text)["status"] == "error"
    with patch.object(srv, "handle_tool", side_effect=RuntimeError("boom")):
        out = asyncio.run(srv.call_github_tool("list_prs", {"repo": "o/r"}))
    assert "boom" in json.loads(out[0].text)["message"]

    srv.GitHubMockMCPServer()  # registers handlers without error

    with patch.object(srv, "GitHubMockMCPServer") as cls:
        cls.return_value.run = AsyncMock()
        asyncio.run(srv.main())
    cls.return_value.run.assert_awaited_once()


def test_retrieval_server_handlers_and_main():
    import json

    from langchain_core.documents import Document

    from makpa.mcp_servers.retrieval import server as srv

    tools = asyncio.run(srv.list_retrieval_tools())
    assert [t.name for t in tools] == ["search_documents"]

    out = asyncio.run(srv.call_search_documents("nope", {}))
    assert json.loads(out[0].text)["status"] == "error"
    out = asyncio.run(srv.call_search_documents("search_documents", {}))
    assert "query is required" in json.loads(out[0].text)["message"]

    doc = Document(
        page_content="ctx",
        metadata={"source": "s.pdf", "page": 2, "chunk_index": 4, "doc_id": "d"},
    )
    with patch(
        "makpa.rag.retriever.retrieve_documents", return_value=[(doc, 0.5)]
    ):
        out = asyncio.run(srv.call_search_documents("search_documents", {"query": "q"}))
    payload = json.loads(out[0].text)
    assert payload["status"] == "ok" and payload["chunks"][0]["page"] == 2

    with patch("makpa.rag.retriever.retrieve_documents", return_value=[]):
        out = asyncio.run(srv.call_search_documents("search_documents", {"query": "q"}))
    assert json.loads(out[0].text)["status"] == "empty"

    with patch(
        "makpa.rag.retriever.retrieve_documents", side_effect=RuntimeError("down")
    ):
        out = asyncio.run(srv.call_search_documents("search_documents", {"query": "q"}))
    assert json.loads(out[0].text)["status"] == "error"

    srv.RetrievalMCPServer()
    with patch.object(srv, "RetrievalMCPServer") as cls:
        cls.return_value.run = AsyncMock()
        asyncio.run(srv.main())
    cls.return_value.run.assert_awaited_once()


# ---------------------------------------------------------------------------
# github_demo edge paths
# ---------------------------------------------------------------------------


def test_github_demo_probe_failure_and_warnings():
    from makpa.cli import github_demo

    with (
        patch("makpa.llm.probe_llm", side_effect=RuntimeError("live on mock")),
        patch(
            "makpa.subagents.github.tools.github_list_prs",
            MagicMock(**{"invoke.return_value": {"status": "ok"}}),
        ),
    ):
        res = runner.invoke(github_demo.app, ["list-prs", "--repo", "o/r"])
    assert res.exit_code == 1 and "startup probe failed" in res.output

    warned = SimpleNamespace(
        provider="mock", model="m", warnings=["stale model X"], message="ok"
    )
    with (
        patch("makpa.llm.probe_llm", return_value=warned),
        patch(
            "makpa.subagents.github.tools.github_list_prs",
            MagicMock(**{"invoke.return_value": {"status": "ok"}}),
        ),
    ):
        res = runner.invoke(github_demo.app, ["list-prs", "--repo", "o/r"])
    assert res.exit_code == 0 and "stale model X" in res.output


def test_github_demo_setup_logging_reconfigure_failure():
    from makpa.cli import github_demo

    bad = MagicMock()
    bad.reconfigure.side_effect = RuntimeError("nope")
    with (
        patch.object(sys, "stdout", bad),
        patch.object(sys, "stderr", bad),
    ):
        github_demo._setup_logging()  # must not raise


def _snap():
    return SimpleNamespace(
        next=("confirm",),
        tasks=[
            SimpleNamespace(
                interrupts=[
                    SimpleNamespace(
                        value={"payload_preview": [{"tool": "github_create_issue"}]}
                    )
                ]
            )
        ],
    )


def test_github_demo_ask_interrupt_approve_and_decline():
    from makpa.cli import github_demo

    graph = MagicMock()
    graph.get_state.return_value = _snap()
    graph.invoke.side_effect = [
        {"__interrupt__": [{"x": 1}], "status": "ok"},
        {"answer": "created #99", "status": "ok"},
    ]
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.subagents.github.create_github_graph", return_value=graph),
    ):
        res = runner.invoke(github_demo.app, ["ask", "create it"], input="y\n")
    assert res.exit_code == 0 and "created #99" in res.output

    graph2 = MagicMock()
    graph2.get_state.return_value = _snap()
    graph2.invoke.side_effect = [
        {"__interrupt__": [{"x": 1}], "status": "ok"},
        {"answer": "Write operation cancelled", "status": "confirmation_required"},
    ]
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.subagents.github.create_github_graph", return_value=graph2),
    ):
        res = runner.invoke(github_demo.app, ["ask", "create it"], input="n\n")
    assert res.exit_code == 2


def test_github_demo_ask_graph_interrupt_exception_and_statuses():
    from langgraph.errors import GraphInterrupt

    from makpa.cli import github_demo

    graph = MagicMock()
    graph.get_state.return_value = _snap()
    graph.invoke.side_effect = [
        GraphInterrupt("paused"),
        {"answer": "done", "status": "ok"},
    ]
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.subagents.github.create_github_graph", return_value=graph),
    ):
        res = runner.invoke(github_demo.app, ["ask", "create it"], input="y\n")
    assert res.exit_code == 0 and "done" in res.output

    pending = MagicMock()
    pending.get_state.return_value = SimpleNamespace(next=())
    pending.invoke.return_value = {
        "answer": "needs approval",
        "status": "confirmation_required",
    }
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.subagents.github.create_github_graph", return_value=pending),
    ):
        res = runner.invoke(github_demo.app, ["ask", "create it"])
    assert res.exit_code == 2

    for status, code in (("error", 1),):
        failing = MagicMock()
        failing.get_state.return_value = SimpleNamespace(next=())
        failing.invoke.return_value = {"answer": "bad", "status": status}
        with (
            patch("makpa.llm.probe_llm", return_value=_probe_ok()),
            patch("makpa.subagents.github.create_github_graph", return_value=failing),
        ):
            res = runner.invoke(github_demo.app, ["ask", "q"])
        assert res.exit_code == code

    broken = MagicMock()
    broken.invoke.side_effect = RuntimeError("down")
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.subagents.github.create_github_graph", return_value=broken),
    ):
        res = runner.invoke(github_demo.app, ["ask", "q"])
    assert res.exit_code == 1 and "query failed" in res.output


def test_github_demo_tool_failures_and_render():
    from makpa.cli import github_demo

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.subagents.github.tools.github_list_prs",
            MagicMock(**{"invoke.side_effect": RuntimeError("down")}),
        ),
    ):
        res = runner.invoke(github_demo.app, ["list-prs", "--repo", "o/r"])
    assert res.exit_code == 1

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.subagents.github.tools.github_search_code",
            MagicMock(**{"invoke.return_value": {"status": "ok", "results": []}}),
        ),
    ):
        res = runner.invoke(github_demo.app, ["search", "--query", "q", "--repo", "o/r"])
    assert res.exit_code == 0

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.subagents.github.tools.github_search_code",
            MagicMock(**{"invoke.side_effect": RuntimeError("down")}),
        ),
    ):
        res = runner.invoke(github_demo.app, ["search", "--query", "q"])
    assert res.exit_code == 1

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.subagents.github.tools.github_create_issue",
            MagicMock(**{"invoke.side_effect": RuntimeError("down")}),
        ),
    ):
        res = runner.invoke(
            github_demo.app, ["create-issue", "--repo", "o/r", "--title", "T", "--yes"]
        )
    assert res.exit_code == 1

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.subagents.github.tools.github_create_issue",
            MagicMock(**{"invoke.return_value": {"status": "error", "message": "bad"}}),
        ),
    ):
        res = runner.invoke(
            github_demo.app, ["create-issue", "--repo", "o/r", "--title", "T", "--yes"]
        )
    assert res.exit_code == 1

    # _render_payload branches directly.
    github_demo._render_payload("plain text")
    try:
        github_demo._render_payload({"status": "error", "message": "x"})
        raised = False
    except Exception as e:  # typer.Exit
        raised = getattr(e, "exit_code", None) == 1
    assert raised

    with patch.object(github_demo, "app") as app_mock:
        github_demo.main()
    app_mock.assert_called_once()


def test_github_graph_owner_branches_and_error_format():
    from makpa.subagents.github import graph as g

    with patch(
        "makpa.subagents.github.graph.get_settings",
        return_value=SimpleNamespace(resolved_github_mcp_path="mock"),
    ):
        assert g.heuristic_plan("list my repos") == [
            {"tool": "github_list_repos", "args": {"owner": "octo-demo"}}
        ]
    with patch(
        "makpa.subagents.github.graph.get_settings",
        return_value=SimpleNamespace(resolved_github_mcp_path="real"),
    ):
        assert g._default_owner() == ""
        assert g.heuristic_plan("list my repos") == []

    assert g.heuristic_plan("List repos in o/r") == [
        {"tool": "github_list_repos", "args": {"owner": "o"}}
    ]

    results = [
        {"tool": "github_list_prs", "status": "error", "message": "down"},
        {"tool": "github_get_pr", "status": "blocked", "message": "no confirm"},
    ]
    with patch(
        "makpa.llm.get_llm",
        return_value=SimpleNamespace(invoke=lambda p: SimpleNamespace(content="t")),
    ):
        out = g.synthesize_node({"question": "q", "tool_results": results})
    assert "[error]" in out["answer"] and "[blocked]" in out["answer"]
