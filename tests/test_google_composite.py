"""Phase 3: composite scheduling flow tests (two real interrupt gates)."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command


class _StubLLM:
    def __init__(self, text: str):
        self._text = text

    def invoke(self, _prompt: str):
        return SimpleNamespace(content=self._text)


QUESTION = (
    "schedule a meeting with a@example.com "
    "from 2026-10-02T15:00:00Z to 2026-10-02T16:00:00Z"
)


def _fake_tools(free=True):

    check = MagicMock()
    check.invoke.return_value = {
        "status": "ok",
        "free": free,
        "busy": [] if free else [{"start": "x", "end": "y"}],
    }
    create = MagicMock()
    create.invoke.return_value = {
        "status": "ok",
        "event": {
            "id": "evt-1",
            "summary": "S",
            "start": "2026-10-02T15:00:00+00:00",
            "end": "2026-10-02T16:00:00+00:00",
            "html_link": "http://cal/evt-1",
        },
    }
    draft = MagicMock()
    draft.invoke.return_value = {"status": "ok", "draft": {"id": "draft-1"}}
    send = MagicMock()
    send.invoke.return_value = {"status": "ok", "sent": {"id": "msg-1"}}
    return {
        "calendar_check_availability": check,
        "calendar_create_event": create,
        "gmail_draft_message": draft,
        "gmail_send_message": send,
    }


def _run(fakes, inputs, thread="t-composite"):
    from makpa.subagents.google import graph as g
    from makpa.utils.interrupts import detect_interrupt

    compiled = g.create_google_graph(checkpointer=MemorySaver())
    config = {"configurable": {"thread_id": thread}}
    with (
        patch.dict(g.TOOLS_BY_NAME, fakes, clear=False),
        patch("makpa.llm.get_llm", return_value=_StubLLM("polished")),
    ):
        result = compiled.invoke({"question": QUESTION}, config)
        for payload in inputs:
            assert detect_interrupt(result) is not None
            result = compiled.invoke(Command(resume=payload), config)
    return result, fakes


def test_composite_approve_approve():
    result, fakes = _run(_fake_tools(), [{"confirm": True}, {"confirm": True}], "t-aa")
    assert result["status"] == "ok"
    assert result["composite_stage"] == "email_sent"
    names = [r["tool"] for r in result["tool_results"]]
    assert names == [
        "calendar_check_availability",
        "calendar_create_event",
        "gmail_draft_message",
        "gmail_send_message",
    ]
    assert "evt-1" in result["answer"] and "msg-1" in result["answer"]
    fakes["calendar_create_event"].invoke.assert_called_once()
    fakes["gmail_send_message"].invoke.assert_called_once()


def test_composite_decline_gate1_no_side_effects():
    result, fakes = _run(_fake_tools(), [{"confirm": False}], "t-d1")
    assert result["status"] == "cancelled"
    assert "no event was created" in result["answer"]
    fakes["calendar_create_event"].invoke.assert_not_called()
    fakes["gmail_send_message"].invoke.assert_not_called()


def test_composite_decline_gate2_keeps_event():
    result, fakes = _run(
        _fake_tools(), [{"confirm": True}, {"confirm": False}], "t-d2"
    )
    assert result["status"] == "cancelled"
    assert "stays" in result["answer"] or "keeps" in result["answer"]
    assert "no email was sent" in result["answer"]
    fakes["calendar_create_event"].invoke.assert_called_once()
    fakes["gmail_send_message"].invoke.assert_not_called()


def test_composite_busy_slot_proposes_alternatives():
    result, _ = _run(_fake_tools(free=False), [], "t-busy")
    assert result["status"] == "ok"
    assert "busy" in result["answer"].lower()
    names = [r["tool"] for r in result["tool_results"]]
    assert names == ["calendar_check_availability"]


def test_composite_nodes_guard_unconfirmed_execution():
    from makpa.subagents.google import graph as g

    out = g.composite_create_node(
        {"plan": [{"tool": "calendar_create_event", "args": {}}], "confirmed": False}
    )
    assert out["status"] == "cancelled"
    out = g.composite_send_node(
        {"plan": [{"tool": "gmail_send_message", "args": {}}], "confirmed": False}
    )
    assert out["status"] == "cancelled"


def test_composite_check_error_and_routes():
    from makpa.subagents.google import graph as g

    boom = MagicMock()
    boom.invoke.side_effect = RuntimeError("down")
    with patch.dict(g.TOOLS_BY_NAME, {"calendar_check_availability": boom}, clear=False):
        out = g.composite_check_node({"question": QUESTION})
    assert out["status"] == "error"
    assert g.route_after_check({"tool_results": []}) == "synthesize"
    free_results = {
        "tool_results": [
            {"tool": "calendar_check_availability", "status": "ok", "free": True}
        ]
    }
    busy_results = {
        "tool_results": [
            {"tool": "calendar_check_availability", "status": "ok", "free": False}
        ]
    }
    assert g.route_after_check(free_results) == "composite_plan_event"
    assert g.route_after_check(busy_results) == "synthesize"


def test_confirm_event_and_email_nodes():
    from makpa.subagents.google import graph as g

    state = {"question": QUESTION, "plan": [{"tool": "calendar_create_event", "args": {}}]}
    with patch(
        "makpa.subagents.google.graph.interrupt", return_value={"confirm": True}
    ):
        out = g.confirm_event_node(state)
    assert out["composite_stage"] == "event_confirmed"
    with patch(
        "makpa.subagents.google.graph.interrupt", return_value="nope"
    ):
        out = g.confirm_event_node(state)
    assert out["status"] == "cancelled" and "gate 1" in out["answer"]

    estate = {"question": QUESTION, "plan": [{"tool": "gmail_send_message", "args": {}}]}
    with patch(
        "makpa.subagents.google.graph.interrupt", return_value={"confirm": True}
    ):
        out = g.confirm_email_node(estate)
    assert out["composite_stage"] == "email_confirmed"
    with patch(
        "makpa.subagents.google.graph.interrupt", return_value={"confirm": False}
    ):
        out = g.confirm_email_node(estate)
    assert out["status"] == "cancelled" and "gate 2" in out["answer"]

    assert (
        g.route_after_confirm_event({"confirmed": True, "status": "ok"})
        == "composite_create"
    )
    assert g.route_after_confirm_event({"confirmed": False}) == "__end__"
    assert (
        g.route_after_confirm_email({"confirmed": True, "status": "ok"})
        == "composite_send"
    )
    assert g.route_after_confirm_email({"confirmed": True, "status": "cancelled"}) == "__end__"
