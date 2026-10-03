"""Phase 2: GitHub subgraph unit tests (plan/gate/confirm/execute/synthesize)."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch


def test_extract_repo():
    from makpa.subagents.github.graph import extract_repo

    assert extract_repo("PRs in octo-demo/hello-world please") == "octo-demo/hello-world"
    assert extract_repo("no slug here") == ""


def test_heuristic_plan_branches():
    from makpa.subagents.github.graph import heuristic_plan

    create = heuristic_plan("Create an issue in o/r with title Hello")
    assert create[0]["tool"] == "github_create_issue"
    assert create[0]["args"]["repo"] == "o/r"

    pr_num = heuristic_plan("Show pull request #7 in o/r")
    assert pr_num[0] == {"tool": "github_get_pr", "args": {"repo": "o/r", "number": 7}}

    prs = heuristic_plan("List closed PRs in o/r")
    assert prs[0]["args"] == {"repo": "o/r", "state": "closed"}

    issues = heuristic_plan("What issues are open in o/r?")
    assert issues[0]["tool"] == "github_list_issues"

    commits = heuristic_plan("Show commits in o/r")
    assert commits[0]["tool"] == "github_get_commits"

    search = heuristic_plan("Search code for def main in o/r")
    assert search[0]["tool"] == "github_search_code"

    read = heuristic_plan("Read file README.md in o/r")
    assert read[0] == {
        "tool": "github_read_file",
        "args": {"repo": "o/r", "path": "README.md"},
    }

    repos = heuristic_plan("List repos for org octo-demo")
    assert repos[0] == {"tool": "github_list_repos", "args": {"owner": "octo-demo"}}

    bare = heuristic_plan("o/r")
    assert bare and bare[0]["tool"] == "github_list_prs"

    assert heuristic_plan("Tell me a joke") == []
    assert heuristic_plan("Read file without repo") == []


class _StubLLM:
    def __init__(self, text: str):
        self._text = text

    def invoke(self, _prompt: str):
        return SimpleNamespace(content=self._text)


def test_llm_plan_parses_filters_and_falls_back():
    from makpa.subagents.github import graph as g

    good = '[{"tool": "github_list_prs", "args": {"repo": "o/r"}}, {"tool": "nope"}]'
    with patch("makpa.llm.get_llm", return_value=_StubLLM(good)):
        assert g._llm_plan("q") == [
            {"tool": "github_list_prs", "args": {"repo": "o/r"}}
        ]
    with patch("makpa.llm.get_llm", return_value=_StubLLM("not json")):
        assert g._llm_plan("q") is None
    with patch("makpa.llm.get_llm", side_effect=RuntimeError("down")):
        assert g._llm_plan("q") is None


def test_plan_node_and_routes():
    from makpa.subagents.github import graph as g

    out = g.plan_node({"question": "   "})
    assert out["status"] == "error" and out["plan"] == []

    steps = [{"tool": "github_create_issue", "args": {}}]
    with patch("makpa.subagents.github.graph._llm_plan", return_value=steps):
        out = g.plan_node({"question": "create stuff"})
    assert out["needs_confirmation"] is True

    with patch(
        "makpa.subagents.github.graph._llm_plan",
        return_value=[{"tool": "unknown_tool", "args": {}}],
    ):
        out = g.plan_node({"question": "create stuff"})
    assert out["plan"] == [] and out["needs_confirmation"] is False

    assert g.route_after_plan({"plan": [], "needs_confirmation": False}) == "short_circuit"
    assert (
        g.route_after_plan(
            {"plan": [{"tool": "github_create_issue"}], "needs_confirmation": True}
        )
        == "confirm"
    )
    assert (
        g.route_after_plan(
            {"plan": [{"tool": "github_list_prs"}], "needs_confirmation": False}
        )
        == "execute"
    )
    assert g.route_after_confirm({"confirmed": True, "status": "ok"}) == "execute"
    assert g.route_after_confirm({"confirmed": False}) == "__end__"
    denied = g.route_after_confirm(
        {"confirmed": True, "status": "confirmation_required"}
    )
    assert denied == "__end__"


def test_confirm_node_grants_and_denies():
    from makpa.subagents.github import graph as g

    state = {
        "question": "q",
        "plan": [{"tool": "github_create_issue", "args": {"repo": "o/r"}}],
    }
    with patch("makpa.subagents.github.graph.interrupt", return_value={"confirm": True}):
        assert g.confirm_node(state) == {"confirmed": True, "status": "ok"}
    with patch("makpa.subagents.github.graph.interrupt", return_value={"confirm": False}):
        out = g.confirm_node(state)
        assert out["status"] == "confirmation_required"
        assert out["confirmed"] is False
    with patch("makpa.subagents.github.graph.interrupt", return_value=None):
        assert g.confirm_node(state)["confirmed"] is False


def test_execute_node_gate_and_errors():
    from makpa.subagents.github import graph as g

    mutating = {"tool": "github_create_issue", "args": {"repo": "o/r", "title": "T"}}
    # Blocked without confirmation: tool must not be invoked.
    strict = MagicMock()
    with patch.dict(g.TOOLS_BY_NAME, {"github_create_issue": strict}, clear=False):
        out = g.execute_node({"plan": [mutating], "confirmed": False})
    strict.invoke.assert_not_called()
    assert out["status"] == "confirmation_required"
    assert out["tool_results"][0]["status"] == "blocked"

    # Confirmed executes.
    tool_ok = MagicMock()
    tool_ok.invoke.return_value = {"status": "ok", "issue": {"number": 1}}
    with patch.dict(g.TOOLS_BY_NAME, {"github_create_issue": tool_ok}, clear=False):
        out = g.execute_node({"plan": [mutating], "confirmed": True})
    assert out["status"] == "ok"
    assert out["tool_results"][0]["issue"]["number"] == 1

    # Unknown tool + raising tool.
    out = g.execute_node({"plan": [{"tool": "zzz", "args": {}}]})
    assert out["tool_results"][0]["status"] == "error"
    boom = MagicMock()
    boom.invoke.side_effect = RuntimeError("down")
    with patch.dict(g.TOOLS_BY_NAME, {"github_list_prs": boom}, clear=False):
        out = g.execute_node(
            {"plan": [{"tool": "github_list_prs", "args": {}}], "confirmed": False}
        )
    assert out["tool_results"][0]["status"] == "error"
    # Non-dict tool output is wrapped.
    plain = MagicMock()
    plain.invoke.return_value = "text-result"
    with patch.dict(g.TOOLS_BY_NAME, {"github_list_prs": plain}, clear=False):
        out = g.execute_node(
            {"plan": [{"tool": "github_list_prs", "args": {}}], "confirmed": False}
        )
    assert out["tool_results"][0]["text"] == "text-result"


def test_synthesize_and_short_circuit():
    from makpa.subagents.github import graph as g

    results = [{"tool": "github_list_prs", "status": "ok", "prs": [{"number": 7}]}]
    with patch("makpa.llm.get_llm", return_value=_StubLLM("Short answer.")):
        out = g.synthesize_node({"question": "q", "tool_results": results})
    assert "github_list_prs" in out["answer"] and "Short answer." in out["answer"]

    with patch("makpa.llm.get_llm", side_effect=RuntimeError("down")):
        out = g.synthesize_node({"question": "q", "tool_results": results})
    assert "github_list_prs" in out["answer"]

    with patch("makpa.llm.get_llm", return_value=_StubLLM("   ")):
        out = g.synthesize_node({"question": "q", "tool_results": results})
    assert "github_list_prs" in out["answer"]

    err = g.short_circuit_node({"status": "error", "answer": "empty question"})
    assert err["status"] == "error"
    hint = g.short_circuit_node({"question": "PRs in o/r?", "plan": []})
    assert "o/r" in hint["answer"] and hint["status"] == "empty"
    generic = g.short_circuit_node({"question": "", "plan": []})
    assert generic["answer"] == "No GitHub results found."


def test_graph_structure_and_run_helpers():
    from makpa.subagents.github import graph as g

    compiled = g.create_github_graph()
    assert set(compiled.nodes) >= {"plan", "confirm", "execute", "synthesize", "short_circuit"}

    from langgraph.checkpoint.memory import MemorySaver

    assert g.create_github_graph(checkpointer=MemorySaver()) is not None

    # Read-only helper path.
    fake_tool = MagicMock()
    fake_tool.invoke.return_value = {"status": "ok", "prs": []}
    with (
        patch("makpa.subagents.github.graph._llm_plan", return_value=None),
        patch(
            "makpa.subagents.github.graph.heuristic_plan",
            return_value=[{"tool": "github_list_prs", "args": {"repo": "o/r"}}],
        ),
        patch.dict(g.TOOLS_BY_NAME, {"github_list_prs": fake_tool}, clear=False),
        patch("makpa.llm.get_llm", return_value=_StubLLM("done")),
    ):
        out = g.run_github("List PRs in o/r")
    assert out["status"] == "ok" and out["answer"]

    # Mutating helper path cannot execute without resume.
    with patch(
        "makpa.subagents.github.graph._llm_plan",
        return_value=[{"tool": "github_create_issue", "args": {"repo": "o/r"}}],
    ):
        out = g.run_github("Create an issue in o/r")
    assert out["status"] == "confirmation_required"
    assert out["needs_confirmation"] is True
