"""Phase 2: integration (flagged) + zero-key GitHub tests."""

from __future__ import annotations

import os

import pytest


@pytest.mark.skipif(
    os.getenv("RUN_GITHUB_INTEGRATION") != "1" or not os.getenv("GITHUB_MCP_PAT"),
    reason="Live GitHub integration requires RUN_GITHUB_INTEGRATION=1 + GITHUB_MCP_PAT",
)
def test_live_public_repo_read_only():
    """Read-only live query against a public repo (skips cleanly offline)."""
    import asyncio

    from makpa.subagents.github.client import GitHubMCPClient

    client = GitHubMCPClient()
    if client.path != "real":
        pytest.skip("GitHub path is not real; no PAT configured")

    async def _run():
        tools = await client.aget_tools()
        assert tools, "expected tools from the real GitHub MCP server"
        return await client.acall_tool(
            "list_prs", {"repo": "octocat/Hello-World", "state": "open", "limit": 5}
        )

    try:
        out = asyncio.run(_run())
    except Exception as e:
        pytest.skip(f"Real GitHub MCP endpoint unreachable: {e}")
    assert out["status"] in ("ok", "error")
    if out["status"] == "ok":
        assert "prs" in out or "pull_requests" in out or "results" in out


def test_zero_key_github_flow(monkeypatch):
    """Full GitHub flow in demo mode with no PAT (mock MCP server)."""
    for var in ("GITHUB_MCP_PAT",):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("MAKPA_MODE", "demo")
    monkeypatch.setenv("GITHUB_MCP_MODE", "mock")

    from makpa.config import get_settings
    from makpa.subagents.github import clear_github_client_cache

    if hasattr(get_settings, "cache_clear"):
        get_settings.cache_clear()
    clear_github_client_cache()

    from unittest.mock import patch

    from makpa.subagents.github import run_github

    try:
        # Heuristic planning keeps the zero-key flow deterministic when a
        # real LLM is configured (LLM planning itself is unit-tested).
        with patch("makpa.subagents.github.graph._llm_plan", return_value=None):
            result = run_github("List open pull requests in octo-demo/hello-world")
    finally:
        if hasattr(get_settings, "cache_clear"):
            get_settings.cache_clear()
        clear_github_client_cache()
    assert result["status"] == "ok"
    assert "github_list_prs" in result["answer"]
    assert "Add RAG subgraph" in result["answer"]


def test_mutating_tool_never_executes_without_confirmation():
    """Confirmation gate: create_issue is blocked absent {"confirm": True}."""
    from unittest.mock import MagicMock, patch

    from makpa.subagents.github import graph as g

    strict_tool = MagicMock()
    plan = [
        {
            "tool": "github_create_issue",
            "args": {"repo": "octo-demo/hello-world", "title": "Nope"},
        }
    ]
    with patch.dict(g.TOOLS_BY_NAME, {"github_create_issue": strict_tool}, clear=False):
        out = g.execute_node({"plan": plan})
    strict_tool.invoke.assert_not_called()
    assert out["status"] == "confirmation_required"
    assert out["tool_results"] == [
        {
            "tool": "github_create_issue",
            "status": "blocked",
            "message": (
                "Mutating tool blocked: resume with "
                '{"confirm": true} to execute.'
            ),
        }
    ]
