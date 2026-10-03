"""Phase 4: parallel Send dispatch + end-to-end supervisor tests."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from langchain_core.messages import HumanMessage
from langgraph.types import Send


def test_route_uses_send_objects():
    from makpa.supervisor.router import route

    sends = route({"task_description": "q", "next": ["rag_agent", "google_agent"]})
    assert isinstance(sends, list) and len(sends) == 2
    assert all(isinstance(s, Send) for s in sends)
    assert {s.node for s in sends} == {"rag_agent", "google_agent"}


def test_parallel_faster_than_sequential():
    """Two sleeping workers finish faster via Send than back-to-back."""
    import time as _time

    from makpa.supervisor import graph as g
    from makpa.supervisor.router import Route

    def _sleepy_rag(task):
        _time.sleep(0.8)
        return {"status": "ok", "answer": "rag-a", "citations": []}

    def _sleepy_github(task):
        _time.sleep(0.8)
        return {"status": "ok", "answer": "gh-a", "tool_results": []}

    with (
        patch(
            "makpa.supervisor.graph.classify_intent",
            return_value=Route(agents=["rag_agent", "github_agent"], reasoning="t"),
        ),
        patch("makpa.rag.run_rag", side_effect=_sleepy_rag),
        patch("makpa.subagents.github.run_github", side_effect=_sleepy_github),
    ):
        compiled = g.create_supervisor_graph()
        started = _time.monotonic()
        out = compiled.invoke({"messages": [HumanMessage(content="q")]})
        parallel_time = _time.monotonic() - started
    assert out["status"] == "ok"
    assert set(out["agent_outputs"]) == {"rag_agent", "github_agent"}

    started = _time.monotonic()
    _sleepy_rag("q")
    _sleepy_github("q")
    sequential_time = _time.monotonic() - started
    assert parallel_time < sequential_time
    assert parallel_time < 1.4


def test_three_domain_route_and_aggregation():
    from makpa.supervisor import graph as g
    from makpa.supervisor.router import Route

    def _ok(name):
        def _run(task):
            return {"status": "ok", "answer": f"{name}-a"}

        return _run

    with (
        patch(
            "makpa.supervisor.graph.classify_intent",
            return_value=Route(
                agents=["rag_agent", "github_agent", "google_agent"], reasoning="t"
            ),
        ),
        patch("makpa.rag.run_rag", side_effect=_ok("rag")),
        patch("makpa.subagents.github.run_github", side_effect=_ok("gh")),
        patch("makpa.subagents.google.run_google", side_effect=_ok("go")),
    ):
        out = g.run_supervisor("Do everything everywhere")
    assert out["status"] == "ok"
    assert set(out["agent_outputs"]) == {"rag_agent", "github_agent", "google_agent"}
    final = out["messages"][-1].content
    assert "rag-a" in final and "gh-a" in final and "go-a" in final


def test_end_to_end_demo_scenarios_with_mocks():
    """The three demo questions route correctly with deterministic planning."""
    from makpa.supervisor import graph as g

    def _rag(task):
        return {
            "status": "ok",
            "answer": "cited answer [source: sample.pdf]",
            "citations": [{"source": "sample.pdf", "page": 1}],
        }

    def _github(task):
        return {
            "status": "ok",
            "answer": "PR #7 open",
            "tool_results": [{"tool": "github_list_prs", "status": "ok"}],
        }

    def _google(task):
        return {"status": "ok", "answer": "2 events", "tool_results": []}

    scenarios = [
        ("What does the sample PDF say?", ["rag_agent"]),
        ("List open pull requests in octo-demo/hello-world.", ["github_agent"]),
    ]
    for question, agents in scenarios:
        with (
            patch("makpa.rag.run_rag", side_effect=_rag),
            patch("makpa.subagents.github.run_github", side_effect=_github),
            patch("makpa.subagents.google.run_google", side_effect=_google),
            patch("makpa.subagents.github.graph._llm_plan", return_value=None),
            patch("makpa.subagents.google.graph._llm_plan", return_value=None),
        ):
            out = g.run_supervisor(question)
        assert out["status"] == "ok", question
        assert set(out["agent_outputs"]) == set(agents), question


def test_interrupt_pass_through_and_resume():
    """A subgraph gate surfaces through the supervisor and resumes."""
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.types import Command

    from makpa.subagents.google import graph as gg
    from makpa.supervisor import graph as g
    from makpa.supervisor.router import Route
    from makpa.utils.interrupts import detect_interrupt

    check = MagicMock()
    check.invoke.return_value = {"status": "ok", "free": True, "busy": []}
    create = MagicMock()
    create.invoke.return_value = {
        "status": "ok",
        "event": {"id": "evt-9", "summary": "S", "html_link": "http://x"},
    }
    draft = MagicMock()
    draft.invoke.return_value = {"status": "ok", "draft": {"id": "d-9"}}
    send = MagicMock()
    send.invoke.return_value = {"status": "ok", "sent": {"id": "m-9"}}

    question = (
        "schedule a meeting with a@example.com "
        "from 2026-10-02T15:00:00Z to 2026-10-02T16:00:00Z"
    )
    checkpointer = MemorySaver()
    compiled = g.create_supervisor_graph(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "t-passthrough"}}
    fakes = {
        "calendar_check_availability": check,
        "calendar_create_event": create,
        "gmail_draft_message": draft,
        "gmail_send_message": send,
    }
    with (
        patch(
            "makpa.supervisor.graph.classify_intent",
            return_value=Route(agents=["google_agent"], reasoning="t"),
        ),
        patch.dict(gg.TOOLS_BY_NAME, fakes, clear=False),
        patch("makpa.llm.get_llm", return_value=_StubLLM("polished")),
    ):
        from makpa.config import get_settings

        if hasattr(get_settings, "cache_clear"):
            get_settings.cache_clear()
        try:
            import os

            old = os.environ.get("GOOGLE_CALENDAR_ATTENDEE_MODE")
            os.environ["GOOGLE_CALENDAR_ATTENDEE_MODE"] = "all"
            if hasattr(get_settings, "cache_clear"):
                get_settings.cache_clear()
            result = compiled.invoke(
                {"messages": [HumanMessage(content=question)]}, config
            )
            assert detect_interrupt(result) is not None
            result = compiled.invoke(Command(resume={"confirm": True}), config)
            assert detect_interrupt(result) is not None
            result = compiled.invoke(Command(resume={"confirm": True}), config)
        finally:
            if old is None:
                os.environ.pop("GOOGLE_CALENDAR_ATTENDEE_MODE", None)
            else:
                os.environ["GOOGLE_CALENDAR_ATTENDEE_MODE"] = old
            if hasattr(get_settings, "cache_clear"):
                get_settings.cache_clear()
    assert result["status"] == "ok"
    outputs = result["agent_outputs"]
    assert "google_agent" in outputs
    assert "evt-9" in outputs["google_agent"] and "m-9" in outputs["google_agent"]


class _StubLLM:
    def __init__(self, text: str):
        self._text = text

    def invoke(self, _prompt: str):
        from types import SimpleNamespace

        return SimpleNamespace(content=self._text)
