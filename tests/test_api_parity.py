"""Backend/frontend parity: structured ids flow end-to-end, never from prose."""

from __future__ import annotations

import json
from typing import Any


def test_extract_rag_structured_non_empty():
    from makpa.supervisor.graph import extract_structured

    result = {
        "citations": [{"source": "sample.pdf", "page": 7, "chunk_id": 36}],
        "answer": "details here",
    }
    structured = extract_structured("rag_agent", result)
    assert structured["chunk_count"] == 1
    assert structured["citations"] == result["citations"]


def test_extract_github_structured_non_empty():
    from makpa.supervisor.graph import extract_structured

    result = {
        "plan": [{"tool": "github_list_prs", "args": {"repo": "octo-demo/hello-world"}}],
        "tool_results": [
            {
                "tool": "github_list_prs",
                "status": "ok",
                "prs": [{"number": 7, "title": "Add RAG subgraph"}],
                "count": 1,
            },
            {
                "tool": "github_get_commits",
                "status": "ok",
                "commits": [{"sha": "a1b2c3d", "message": "x"}],
            },
        ],
    }
    structured = extract_structured("github_agent", result)
    assert structured["pr_numbers"] == [7]
    assert structured["commit_shas"] == ["a1b2c3d"]
    assert structured["repo"] == "octo-demo/hello-world"


def test_extract_google_structured_non_empty():
    from makpa.supervisor.graph import extract_structured

    result = {
        "tool_results": [
            {
                "tool": "calendar_create_event",
                "status": "ok",
                "event": {"id": "evt-mock-100", "status": "confirmed"},
            },
            {
                "tool": "gmail_send_message",
                "status": "ok",
                "sent": {"id": "msg-from-draft-mock-100"},
            },
        ]
    }
    structured = extract_structured("google_agent", result)
    assert structured["event_id"] == "evt-mock-100"
    assert structured["event_ids"] == ["evt-mock-100"]
    assert structured["calendar_status"] == "confirmed"
    assert structured["message_id"] == "msg-from-draft-mock-100"


def test_mock_calendar_create_then_update_for_rollback():
    """Gate-2 rollback needs update to find the just-created mock event."""
    from makpa.mcp_servers.google_calendar import mock as cal_mock

    try:
        created = cal_mock.handle_mock_calendar_tool(
            "calendar_create_event",
            {
                "summary": "T",
                "start": "2026-10-02T15:00:00Z",
                "end": "2026-10-02T16:00:00Z",
            },
        )
        assert created["status"] == "ok"
        updated = cal_mock.handle_mock_calendar_tool(
            "calendar_update_event",
            {"event_id": created["event"]["id"], "status": "cancelled"},
        )
        assert updated["status"] == "ok"
        assert updated["event"]["status"] == "cancelled"
    finally:
        # Keep the file-backed mock store pristine for other tests.
        cal_mock._save_events(
            [e for e in cal_mock._load_events() if e.get("id") != "evt-mock-100"]
        )


def test_worker_update_carries_structured():
    from makpa.supervisor import graph as g

    out = g._worker_update(
        "github_agent",
        {
            "status": "ok",
            "answer": "prs",
            "plan": [{"tool": "github_list_prs", "args": {"repo": "o/n"}}],
            "tool_results": [{"tool": "github_list_prs", "status": "ok", "prs": []}],
        },
    )
    summary = json.loads(out["agent_outputs"]["github_agent"])
    assert summary["structured"]["repo"] == "o/n"


def _force_mock_mcp(monkeypatch):
    """Pin mock MCP + heuristic planning (blank, never delete, per repo convention)."""
    monkeypatch.setenv("MAKPA_MODE", "demo")
    monkeypatch.setenv("GITHUB_MCP_PAT", "")
    monkeypatch.setenv("GITHUB_MCP_MODE", "mock")
    monkeypatch.setenv("GOOGLE_MCP_MODE", "mock")

    from makpa.config import get_settings
    from makpa.google.client import clear_google_client_cache
    from makpa.subagents.github import clear_github_client_cache

    if hasattr(get_settings, "cache_clear"):
        get_settings.cache_clear()
    clear_github_client_cache()
    clear_google_client_cache()


def _restore_mcp():
    from makpa.config import get_settings
    from makpa.google.client import clear_google_client_cache
    from makpa.subagents.github import clear_github_client_cache

    if hasattr(get_settings, "cache_clear"):
        get_settings.cache_clear()
    clear_github_client_cache()
    clear_google_client_cache()


def _supervisor_invoke(question: str) -> dict[str, Any]:
    from unittest.mock import patch

    from langchain_core.messages import HumanMessage

    from makpa.supervisor import create_supervisor_graph

    graph = create_supervisor_graph()
    # Heuristic planning keeps the mock-backed flow deterministic.
    with (
        patch("makpa.subagents.github.graph._llm_plan", return_value=None),
        patch("makpa.subagents.google.graph._llm_plan", return_value=None),
    ):
        return dict(graph.invoke({"messages": [HumanMessage(content=question)]}))


def test_live_github_structured_pr_numbers(monkeypatch):
    _force_mock_mcp(monkeypatch)
    try:
        result = _supervisor_invoke("List open pull requests in octo-demo/hello-world.")
    finally:
        _restore_mcp()
    outputs = result.get("agent_outputs", {})
    assert "github_agent" in outputs
    summary = json.loads(outputs["github_agent"])
    assert summary.get("status") == "ok"
    structured = summary.get("structured", {})
    assert 7 in structured.get("pr_numbers", [])
    assert structured.get("repo") == "octo-demo/hello-world"


def test_live_google_structured_event_ids(monkeypatch):
    _force_mock_mcp(monkeypatch)
    try:
        result = _supervisor_invoke(
            "List events from 2026-10-01T00:00:00Z to 2026-10-08T00:00:00Z."
        )
    finally:
        _restore_mcp()
    outputs = result.get("agent_outputs", {})
    assert "google_agent" in outputs
    summary = json.loads(outputs["google_agent"])
    assert summary.get("status") == "ok"
    structured = summary.get("structured", {})
    assert len(structured.get("event_ids", [])) >= 1


def test_live_rag_structured_citations(monkeypatch):
    _force_mock_mcp(monkeypatch)
    try:
        result = _supervisor_invoke(
            "What does the sample PDF say about implementation details?"
        )
    finally:
        _restore_mcp()
    outputs = result.get("agent_outputs", {})
    assert "rag_agent" in outputs
    summary = json.loads(outputs["rag_agent"])
    structured = summary.get("structured", {})
    assert structured.get("chunk_count", 0) >= 1
    assert len(structured.get("citations", [])) >= 1


def test_sse_agent_end_carries_structured(monkeypatch):
    from unittest.mock import patch

    from fastapi.testclient import TestClient

    from makpa.api.server import app

    _force_mock_mcp(monkeypatch)
    client = TestClient(app)
    thread_id = client.post("/api/threads").json()["thread_id"]
    try:
        with (
            patch("makpa.subagents.github.graph._llm_plan", return_value=None),
            patch("makpa.subagents.google.graph._llm_plan", return_value=None),
        ):
            response = client.post(
                f"/api/threads/{thread_id}/stream",
                json={"message": "List open pull requests in octo-demo/hello-world."},
            )
        assert response.status_code == 200
        end_events = [
            line for line in response.text.splitlines() if "agent_end" in line
        ]
        assert end_events, "expected at least one agent_end SSE event"
        payloads = []
        lines = response.text.splitlines()
        for i, line in enumerate(lines):
            if line.startswith("event: agent_end") and i + 1 < len(lines):
                data_line = lines[i + 1]
                assert data_line.startswith("data: ")
                payloads.append(json.loads(data_line[len("data: "):]))
        github = [p for p in payloads if p.get("agent") == "github_agent"]
        assert github, f"expected github agent_end, got {payloads}"
        assert 7 in github[0].get("structured", {}).get("pr_numbers", [])
    finally:
        client.delete(f"/api/threads/{thread_id}")
        _restore_mcp()
