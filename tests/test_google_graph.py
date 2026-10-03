"""Phase 3: Google subgraph unit tests (plan/gate/confirm/execute/synthesize)."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch


class _StubLLM:
    def __init__(self, text: str):
        self._text = text

    def invoke(self, _prompt: str):
        return SimpleNamespace(content=self._text)


def test_extractors_and_composite_detection():
    from makpa.subagents.google import graph as g

    assert g.extract_emails("Meet a@x.com and b@y.org twice a@x.com") == ["a@x.com", "b@y.org"]
    assert g.extract_isos("from 2026-10-02T15:00:00Z to 2026-10-02T16:00:00Z") == [
        "2026-10-02T15:00:00Z",
        "2026-10-02T16:00:00Z",
    ]
    assert g.is_composite_request("Schedule a meeting with a@x.com") is True
    assert g.is_composite_request("List my events") is False


def test_heuristic_branches():
    from makpa.subagents.google import graph as g

    service, plan, action = g.heuristic_plan(
        "schedule a meeting with a@x.com from 2026-10-02T15:00:00Z to 2026-10-02T16:00:00Z"
    )
    assert (service, action) == ("both", "schedule_meeting")
    assert plan[0]["tool"] == "__composite__"

    service, plan, action = g.heuristic_plan("schedule a meeting")
    assert (service, action, plan) == ("both", "schedule_meeting", [])

    service, plan, action = g.heuristic_plan(
        "Am I free from 2026-10-01T09:00:00Z to 2026-10-01T10:00:00Z?"
    )
    assert plan[0]["tool"] == "calendar_check_availability"

    service, plan, action = g.heuristic_plan(
        "Update evt-001 to start 2026-10-02T15:00:00Z"
    )
    assert plan and plan[0]["tool"] == "calendar_update_event"
    assert g.heuristic_plan("Update something") == ("calendar", [], "update_event")

    service, plan, action = g.heuristic_plan(
        "Create new event from 2026-10-02T15:00:00Z to 2026-10-02T16:00:00Z with a@x.com"
    )
    assert plan[0]["tool"] == "calendar_create_event"
    assert g.heuristic_plan("create stuff") == ("calendar", [], "create_event")

    service, plan, action = g.heuristic_plan(
        "List events from 2026-10-01T00:00:00Z to 2026-10-02T00:00:00Z"
    )
    assert plan[0]["tool"] == "calendar_list_events"
    assert g.heuristic_plan("show my calendar") == ("calendar", [], "list_events")

    service, plan, action = g.heuristic_plan("Draft an email to a@x.com about launch")
    assert plan[0]["tool"] == "gmail_draft_message"
    assert g.heuristic_plan("draft something") == ("gmail", [], "draft_message")

    service, plan, action = g.heuristic_plan("Send email to a@x.com about launch")
    assert plan[0]["tool"] == "gmail_send_message"
    assert g.heuristic_plan("send something") == ("gmail", [], "send_message")

    service, plan, action = g.heuristic_plan("Read msg-001 please")
    assert plan[0] == {"tool": "gmail_read_message", "args": {"message_id": "msg-001"}}
    assert g.heuristic_plan("open it") == ("gmail", [], "read_message")

    service, plan, action = g.heuristic_plan("Search mail for standup")
    assert plan[0]["tool"] == "gmail_search_messages"
    assert g.heuristic_plan("tell me a joke") == ("calendar", [], "unknown")


def test_llm_plan_variants():
    from makpa.subagents.google import graph as g

    good = (
        '{"service": "gmail", "action": "search_messages", '
        '"plan": [{"tool": "gmail_search_messages", "args": {}}]}'
    )
    with patch("makpa.llm.get_llm", return_value=_StubLLM(good)):
        assert g._llm_plan("q") == (
            "gmail",
            [{"tool": "gmail_search_messages", "args": {}}],
            "search_messages",
        )
    weird = '{"service": "carrier-pigeon", "action": "x", "plan": []}'
    with patch("makpa.llm.get_llm", return_value=_StubLLM(weird)):
        out = g._llm_plan("q")
    assert out is not None and out[0] == "calendar"
    with patch("makpa.llm.get_llm", return_value=_StubLLM("not json")):
        assert g._llm_plan("q") is None
    with patch("makpa.llm.get_llm", side_effect=RuntimeError("down")):
        assert g._llm_plan("q") is None


def test_plan_node_and_routes():
    from makpa.subagents.google import graph as g

    out = g.plan_node({"question": "   "})
    assert out["status"] == "error" and out["plan"] == []

    with patch(
        "makpa.subagents.google.graph._llm_plan",
        return_value=("gmail", [{"tool": "gmail_send_message", "args": {}}], "send_message"),
    ):
        out = g.plan_node({"question": "send it"})
    assert out["needs_confirmation"] is True and out["service"] == "gmail"

    with patch(
        "makpa.subagents.google.graph._llm_plan",
        return_value=("calendar", [{"tool": "bogus", "args": {}}], "x"),
    ):
        out = g.plan_node({"question": "send it"})
    assert out["plan"] == []

    assert g.route_after_plan({"plan": []}) == "short_circuit"
    assert (
        g.route_after_plan(
            {"plan": [{"tool": "__composite__"}], "action": "schedule_meeting"}
        )
        == "composite_check"
    )
    assert (
        g.route_after_plan(
            {"plan": [{"tool": "gmail_send_message"}], "needs_confirmation": True}
        )
        == "confirm"
    )
    assert (
        g.route_after_plan(
            {"plan": [{"tool": "gmail_draft_message"}], "needs_confirmation": False}
        )
        == "execute"
    )
    assert g.route_after_confirm({"confirmed": True, "status": "ok"}) == "execute"
    assert g.route_after_confirm({"confirmed": False}) == "__end__"
    assert (
        g.route_after_confirm({"confirmed": True, "status": "cancelled"}) == "__end__"
    )


def test_confirm_and_execute_gate():
    from makpa.subagents.google import graph as g

    state = {"question": "q", "plan": [{"tool": "gmail_send_message", "args": {}}]}
    with patch(
        "makpa.subagents.google.graph.interrupt", return_value={"confirm": True}
    ):
        assert g.confirm_node(state) == {"confirmed": True, "status": "ok"}
    with patch(
        "makpa.subagents.google.graph.interrupt", return_value={"confirm": False}
    ):
        out = g.confirm_node(state)
        assert out["status"] == "cancelled" and out["confirmed"] is False

    strict = MagicMock()
    with patch.dict(g.TOOLS_BY_NAME, {"gmail_send_message": strict}, clear=False):
        out = g.execute_node(
            {"plan": [{"tool": "gmail_send_message", "args": {}}], "confirmed": False}
        )
    strict.invoke.assert_not_called()
    assert out["status"] == "confirmation_required"

    tool_ok = MagicMock()
    tool_ok.invoke.return_value = {"status": "ok", "draft": {"id": "d"}}
    with patch.dict(g.TOOLS_BY_NAME, {"gmail_draft_message": tool_ok}, clear=False):
        out = g.execute_node(
            {"plan": [{"tool": "gmail_draft_message", "args": {}}], "confirmed": False}
        )
    assert out["status"] == "ok"

    out = g.execute_node({"plan": [{"tool": "zzz", "args": {}}]})
    assert out["tool_results"][0]["status"] == "error"
    boom = MagicMock()
    boom.invoke.side_effect = RuntimeError("down")
    with patch.dict(g.TOOLS_BY_NAME, {"gmail_draft_message": boom}, clear=False):
        out = g.execute_node({"plan": [{"tool": "gmail_draft_message", "args": {}}]})
    assert out["tool_results"][0]["status"] == "error"
    plain = MagicMock()
    plain.invoke.return_value = "text-result"
    with patch.dict(g.TOOLS_BY_NAME, {"gmail_draft_message": plain}, clear=False):
        out = g.execute_node({"plan": [{"tool": "gmail_draft_message", "args": {}}]})
    assert out["tool_results"][0]["text"] == "text-result"


def test_synthesize_and_short_circuit():
    from makpa.subagents.google import graph as g

    results = [{"tool": "gmail_search_messages", "status": "ok", "messages": []}]
    with patch("makpa.llm.get_llm", return_value=_StubLLM("Short answer.")):
        out = g.synthesize_node({"question": "q", "tool_results": results})
    assert "gmail_search_messages" in out["answer"]
    with patch("makpa.llm.get_llm", side_effect=RuntimeError("down")):
        out = g.synthesize_node({"question": "q", "tool_results": results})
    assert "gmail_search_messages" in out["answer"]
    with patch("makpa.llm.get_llm", return_value=_StubLLM("   ")):
        out = g.synthesize_node({"question": "q", "tool_results": results})
    assert "gmail_search_messages" in out["answer"]

    err_results = [{"tool": "gmail_send_message", "status": "error", "message": "down"}]
    with patch("makpa.llm.get_llm", return_value=_StubLLM("t")):
        out = g.synthesize_node({"question": "q", "tool_results": err_results})
    assert "[error]" in out["answer"]

    cancelled = g.short_circuit_node({"status": "cancelled", "answer": "stopped"})
    assert cancelled == {"answer": "stopped", "status": "cancelled"}
    err = g.short_circuit_node({"status": "error", "answer": "empty question"})
    assert err["status"] == "error"
    sched = g.short_circuit_node(
        {"question": "schedule it", "action": "schedule_meeting", "plan": []}
    )
    assert "ISO" in sched["answer"]
    generic = g.short_circuit_node({"question": "hi", "plan": []})
    assert generic["status"] == "empty"
    empty = g.short_circuit_node({"question": "", "plan": []})
    assert empty["answer"] == "No Google results found."


def test_graph_structure_and_run_helpers():
    from langgraph.checkpoint.memory import MemorySaver

    from makpa.subagents.google import graph as g

    compiled = g.create_google_graph()
    assert set(compiled.nodes) >= {
        "plan", "confirm", "execute", "synthesize", "short_circuit",
        "composite_check", "composite_plan_event", "confirm_event",
        "composite_create", "composite_plan_email", "confirm_email", "composite_send",
    }
    assert g.create_google_graph(checkpointer=MemorySaver()) is not None

    fake_tool = MagicMock()
    fake_tool.invoke.return_value = {"status": "ok", "messages": []}
    with (
        patch("makpa.subagents.google.graph._llm_plan", return_value=None),
        patch(
            "makpa.subagents.google.graph.heuristic_plan",
            return_value=(
                "gmail",
                [{"tool": "gmail_search_messages", "args": {}}],
                "search_messages",
            ),
        ),
        patch.dict(g.TOOLS_BY_NAME, {"gmail_search_messages": fake_tool}, clear=False),
        patch("makpa.llm.get_llm", return_value=_StubLLM("done")),
    ):
        out = g.run_google("Search mail for standup")
    assert out["status"] == "ok" and out["answer"]

    with patch(
        "makpa.subagents.google.graph._llm_plan",
        return_value=("gmail", [{"tool": "gmail_send_message", "args": {}}], "send_message"),
    ):
        out = g.run_google("Send email to a@x.com")
    assert out["status"] == "confirmation_required"
