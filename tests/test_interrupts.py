"""Shared interrupt helper tests + GitHub refactor regression."""

from __future__ import annotations

from unittest.mock import MagicMock

from langgraph.types import Interrupt


def test_detect_interrupt_real_and_empty():
    from makpa.utils.interrupts import detect_interrupt

    found = Interrupt(value={"confirm": True}, id="abc")
    assert detect_interrupt({"__interrupt__": [found]}) is found
    assert detect_interrupt({"__interrupt__": []}) is None
    assert detect_interrupt({"status": "ok"}) is None
    assert detect_interrupt(None) is None
    assert detect_interrupt([Interrupt(value=1)]) is None


def test_detect_interrupt_wrong_entry_type(caplog):
    import logging

    from makpa.utils.interrupts import detect_interrupt

    with caplog.at_level(logging.WARNING):
        assert detect_interrupt({"__interrupt__": ["not-an-interrupt"]}) is None


def test_resume_with_invokes_command():
    from langgraph.types import Command

    from makpa.utils.interrupts import resume_with

    graph = MagicMock()
    graph.invoke.return_value = {"answer": "done", "status": "ok"}
    out = resume_with(graph, {"configurable": {"thread_id": "t"}}, {"confirm": True})
    assert out == {"answer": "done", "status": "ok"}
    sent = graph.invoke.call_args[0][0]
    assert isinstance(sent, Command)
    assert sent.resume == {"confirm": True}  # type: ignore[attr-defined]


def test_github_run_uses_shared_helper():
    from unittest.mock import MagicMock, patch

    from makpa.subagents.github import graph as g

    # Mutating question still funnels to confirmation_required.
    with patch(
        "makpa.subagents.github.graph._llm_plan",
        return_value=[{"tool": "github_create_issue", "args": {"repo": "o/r"}}],
    ):
        out = g.run_github("Create an issue in o/r")
    assert out["status"] == "confirmation_required"

    # Read-only question flows through without interruption.
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
    assert out["status"] == "ok"


class _StubLLM:
    def __init__(self, text: str):
        self._text = text

    def invoke(self, _prompt: str):
        from types import SimpleNamespace

        return SimpleNamespace(content=self._text)
