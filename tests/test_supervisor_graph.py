"""Phase 4: supervisor graph unit tests (workers, aggregate, reflection)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from langchain_core.messages import HumanMessage


def test_classify_node_and_statuses():
    from makpa.supervisor import graph as g
    from makpa.supervisor.router import Route

    with patch(
        "makpa.supervisor.graph.classify_intent",
        return_value=Route(agents=["rag_agent"], reasoning="docs"),
    ):
        out = g._classify_node({"messages": [HumanMessage(content="Read the PDF")]})
    assert out["next"] == ["rag_agent"]
    assert out["task_description"] == "Read the PDF"
    assert out["status"] == "ok"

    with patch(
        "makpa.supervisor.graph.classify_intent",
        return_value=Route(agents=[], reasoning="none"),
    ):
        out = g._classify_node({"messages": [HumanMessage(content="Hi")]})
    assert out["next"] == [] and out["status"] == "error"

    assert g._compute_status({}) == "error"
    assert g._compute_status({"a": "ok", "b": "empty"}) == "ok"
    assert g._compute_status({"a": "error", "b": "error"}) == "error"
    assert g._compute_status({"a": "ok", "b": "error"}) == "partial"
    assert g._compute_status({"a": "confirmation_required"}) == "partial"
    assert g._compute_status({"a": "rolled_back"}) == "partial"


def test_worker_update_variants():
    from langgraph.types import Interrupt

    from makpa.supervisor import graph as g

    out = g._worker_update(
        "rag_agent",
        {"status": "ok", "answer": "a", "citations": [{"source": "s"}]},
    )
    assert json.loads(out["agent_outputs"]["rag_agent"])["citations"] == [{"source": "s"}]
    assert out["confirmations"] == {"rag_agent": True}

    out = g._worker_update(
        "github_agent", {"__interrupt__": [Interrupt(value=1)], "status": "ok"}
    )
    assert "confirmation_required" in out["agent_outputs"]["github_agent"]
    assert out["confirmations"] == {"github_agent": False}

    out = g._worker_update("google_agent", {"status": "error", "answer": "x"})
    assert out["confirmations"] == {"google_agent": False}

    tools = [{"tool": "t", "status": "ok"}, "junk"]
    out = g._worker_update(
        "github_agent", {"status": "ok", "answer": "a", "tool_results": tools}
    )
    assert json.loads(out["agent_outputs"]["github_agent"])["tools"] == [
        {"tool": "t", "status": "ok"}
    ]


def test_workers_use_helpers_without_checkpointer():
    from makpa.supervisor import graph as g

    rag_worker = g._make_rag_worker()
    with patch(
        "makpa.rag.run_rag",
        return_value={"status": "ok", "answer": "a", "citations": []},
    ):
        out = rag_worker({"task_description": "q"})
    assert "rag_agent" in out["agent_outputs"]

    with patch("makpa.rag.run_rag", side_effect=RuntimeError("down")):
        out = rag_worker({"task_description": "q"})
    assert json.loads(out["agent_outputs"]["rag_agent"])["status"] == "error"

    github_worker = g._make_github_worker(None)
    with patch(
        "makpa.subagents.github.run_github",
        return_value={"status": "ok", "answer": "a"},
    ):
        out = github_worker({"task_description": "q"})
    assert out["confirmations"] == {"github_agent": True}

    google_worker = g._make_google_worker(None)
    with patch(
        "makpa.subagents.google.run_google",
        return_value={"status": "empty", "answer": "none"},
    ):
        out = google_worker({"task_description": "q"})
    assert out["confirmations"] == {"google_agent": True}

    github_worker = g._make_github_worker(None)
    with patch(
        "makpa.subagents.github.run_github",
        side_effect=RuntimeError("down"),
    ):
        out = github_worker({"task_description": "q"})
    assert json.loads(out["agent_outputs"]["github_agent"])["status"] == "error"


def test_workers_propagate_interrupts_with_checkpointer():
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.errors import GraphInterrupt

    from makpa.supervisor import graph as g

    checkpointer = MemorySaver()
    github_worker = g._make_github_worker(checkpointer)
    inner = MagicMock()
    inner.invoke.side_effect = GraphInterrupt("gate")
    with patch(
        "makpa.subagents.github.create_github_graph", return_value=inner
    ):
        try:
            github_worker({"task_description": "q"}, {"configurable": {"thread_id": "t"}})
            raised = False
        except GraphInterrupt:
            raised = True
    assert raised

    google_worker = g._make_google_worker(checkpointer)
    inner = MagicMock()
    inner.invoke.side_effect = RuntimeError("down")
    with patch(
        "makpa.subagents.google.create_google_graph", return_value=inner
    ):
        out = google_worker({"task_description": "q"})
    assert json.loads(out["agent_outputs"]["google_agent"])["status"] == "error"


def test_aggregate_results_shapes():
    from makpa.supervisor import graph as g

    message, status = g.aggregate_results({})
    assert status == "error" and "No sub-agent" in message

    message, status = g.aggregate_results(
        {"rag_agent": json.dumps({"status": "ok", "answer": "cited", "citations": ["s"]})}
    )
    assert status == "ok" and "cited" in message and 'citations: ["s"]' in message

    message, status = g.aggregate_results({"rag_agent": "not-json{{{", "github_agent": "xx"})
    assert status == "error"

    message, status = g.aggregate_results({"rag_agent": "42"})
    assert status == "error" and "42" in message

    assert g._route_after_aggregate({"agent_outputs": {"a": "not-json"}}) == "reflection"

    message, status = g.aggregate_results(
        {
            "rag_agent": json.dumps({"status": "ok", "answer": "a"}),
            "github_agent": json.dumps({"status": "error", "answer": "b"}),
        }
    )
    assert status == "partial" and "### rag_agent [ok]" in message

    rag_ok = {"rag_agent": json.dumps({"status": "ok", "answer": "a"})}
    out = g._aggregate_node({"messages": [], "agent_outputs": rag_ok})
    assert out["status"] == "ok" and len(out["messages"]) == 1

    assert g._route_after_aggregate(
        {"agent_outputs": {"a": json.dumps({"status": "error"})}}
    ) == "reflection"
    assert g._route_after_aggregate(
        {"agent_outputs": {"a": json.dumps({"status": "ok"})}}
    ) == "__end__"


def test_reflection_retries_once():
    from makpa.supervisor import graph as g

    rag_worker = MagicMock(
        return_value={
            "agent_outputs": {"rag_agent": json.dumps({"status": "ok", "answer": "fixed"})},
            "confirmations": {"rag_agent": True},
        }
    )
    reflection = g._make_reflection_node(rag_worker, MagicMock(), MagicMock())
    state = {
        "messages": [],
        "agent_outputs": {"rag_agent": json.dumps({"status": "error", "answer": "bad"})},
        "confirmations": {"rag_agent": False},
    }
    out = reflection(state, {})
    assert out["status"] == "ok"
    assert "Retried once: rag_agent" in out["messages"][-1].content
    rag_worker.assert_called_once()

    # Unknown agent names and failing retries are skipped safely.
    reflection = g._make_reflection_node(MagicMock(), MagicMock(), MagicMock())
    out = reflection(
        {
            "messages": [],
            "agent_outputs": {"zzz": json.dumps({"status": "error"})},
            "confirmations": {},
        },
        {},
    )
    assert out["status"] == "error"

    boom = MagicMock(side_effect=RuntimeError("down"))
    reflection = g._make_reflection_node(boom, MagicMock(), MagicMock())
    out = reflection(
        {
            "messages": [],
            "agent_outputs": {"rag_agent": json.dumps({"status": "error"})},
            "confirmations": {},
        },
        {},
    )
    assert out["status"] == "error"


def test_graph_factory_and_run_helper():
    from makpa.supervisor import graph as g

    compiled = g.create_supervisor_graph()
    assert set(compiled.nodes) >= {
        "classify", "rag_agent", "github_agent", "google_agent",
        "aggregate", "reflection",
    }
    from langgraph.checkpoint.memory import MemorySaver

    assert g.create_supervisor_graph(checkpointer=MemorySaver()) is not None

    with (
        patch(
            "makpa.supervisor.graph.classify_intent",
            return_value=MagicMock(agents=["rag_agent"], reasoning="t"),
        ),
        patch(
            "makpa.rag.run_rag",
            return_value={"status": "ok", "answer": "a", "citations": []},
        ),
    ):
        out = g.run_supervisor("Read the PDF")
    assert out["status"] == "ok"
