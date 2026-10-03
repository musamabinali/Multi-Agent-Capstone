"""Phase 4: supervisor intent-router tests."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from langchain_core.messages import HumanMessage


def test_route_model_defaults():
    from makpa.supervisor.router import Route

    route = Route()
    assert route.agents == [] and route.reasoning == ""


def test_heuristic_routes():
    from makpa.supervisor.router import heuristic_route

    assert heuristic_route("What does the PDF say?").agents == ["rag_agent"]
    assert heuristic_route("List PRs in octo-demo/hello-world").agents == ["github_agent"]
    assert heuristic_route("Am I free tomorrow?").agents == ["google_agent"]
    out = heuristic_route("Search documents about agents and list PRs in o/r")
    assert out.agents == ["rag_agent", "github_agent"]
    out = heuristic_route("Schedule a meeting and email the PR author about docs")
    assert out.agents == ["rag_agent", "github_agent", "google_agent"]
    assert heuristic_route("Tell me a joke").agents == []
    assert heuristic_route("Show PR #7").agents == ["github_agent"]
    assert heuristic_route("Mail a@x.com the notes").agents == ["google_agent"]


def test_message_text_extraction():
    from makpa.supervisor.router import _message_text

    assert _message_text([]) == ""
    assert _message_text([HumanMessage(content="hello")]) == "hello"
    assert _message_text([{"content": "dict form"}]) == "dict form"
    blocks = [{"type": "text", "text": "block text"}, {"type": "image", "text": ""}]
    assert _message_text([SimpleNamespace(content=blocks)]) == "block text"
    assert _message_text([SimpleNamespace(content="")]) == ""


def test_classify_intent_paths():
    from makpa.supervisor.router import Route, classify_intent

    assert classify_intent([]).agents == []
    assert classify_intent([HumanMessage(content="   ")]).agents == []

    # Structured-output success (dict and model forms).
    structured = MagicMock()
    structured.invoke.return_value = {
        "agents": ["github_agent"],
        "reasoning": "mentions PRs",
    }
    llm = MagicMock()
    llm.with_structured_output.return_value = structured
    with patch("makpa.llm.get_llm", return_value=llm):
        out = classify_intent([HumanMessage(content="List PRs")])
    assert out.agents == ["github_agent"] and "PRs" in out.reasoning

    structured.invoke.return_value = Route(agents=["rag_agent"], reasoning="docs")
    with patch("makpa.llm.get_llm", return_value=llm):
        out = classify_intent([HumanMessage(content="Read the PDF")])
    assert out.agents == ["rag_agent"]

    # Unknown garbage from the LLM falls back to heuristic.
    structured.invoke.return_value = "nonsense-string"
    with patch("makpa.llm.get_llm", return_value=llm):
        out = classify_intent([HumanMessage(content="List PRs in o/r")])
    assert out.agents == ["github_agent"]

    # No structured-output support (mock LLM) -> heuristic.
    with patch("makpa.llm.get_llm", return_value=MagicMock(spec=[])):
        out = classify_intent([HumanMessage(content="List PRs in o/r")])
    assert out.agents == ["github_agent"]

    # LLM raises -> heuristic.
    with patch("makpa.llm.get_llm", side_effect=RuntimeError("down")):
        out = classify_intent([HumanMessage(content="List PRs in o/r")])
    assert out.agents == ["github_agent"]

    # LLM returns invalid agent names -> ValidationError -> heuristic fallback.
    structured.invoke.return_value = {"agents": ["nope"], "reasoning": "x"}
    with patch("makpa.llm.get_llm", return_value=llm):
        out = classify_intent([HumanMessage(content="List PRs in o/r")])
    assert out.agents == ["github_agent"]


def test_route_builds_sends_and_end():
    from langgraph.graph import END
    from langgraph.types import Send

    from makpa.supervisor.router import IntentRouter, route

    sends = route({"task_description": "do it", "next": ["rag_agent", "github_agent"]})
    assert isinstance(sends, list) and len(sends) == 2
    assert all(isinstance(s, Send) for s in sends)
    assert [s.node for s in sends] == ["rag_agent", "github_agent"]
    assert sends[0].arg == {"task_description": "do it"}
    assert route({"task_description": "x", "next": []}) == END
    assert route({"task_description": "x", "next": ["bogus"]}) == END

    router = IntentRouter()
    assert router.route({"task_description": "x", "next": []}) == END
    out = router.classify([HumanMessage(content="List PRs in o/r")])
    assert out.agents == ["github_agent"]
