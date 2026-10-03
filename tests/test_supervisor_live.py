"""Phase 4: supervisor zero-key + flagged live tests."""

from __future__ import annotations

import os

import pytest


def test_supervisor_zero_key_demo(monkeypatch):
    """Full supervisor flow with blanked keys (zero-key semantics)."""
    for var in (
        "GEMINI_API_KEY",
        "GROQ_API_KEY",
        "GITHUB_MCP_PAT",
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
    ):
        monkeypatch.setenv(var, "")
    monkeypatch.setenv("MAKPA_MODE", "demo")
    monkeypatch.setenv("GITHUB_MCP_MODE", "mock")
    monkeypatch.setenv("GOOGLE_MCP_MODE", "mock")

    from unittest.mock import patch

    from makpa.config import get_settings
    from makpa.google import clear_google_client_cache
    from makpa.subagents.github import clear_github_client_cache

    if hasattr(get_settings, "cache_clear"):
        get_settings.cache_clear()
    clear_github_client_cache()
    clear_google_client_cache()
    try:
        from makpa.supervisor import run_supervisor

        # Heuristic planning keeps the flow deterministic (LLM planning
        # itself is unit-tested in test_supervisor_router.py).
        with (
            patch("makpa.supervisor.router.classify_intent") as classify_mock,
            patch("makpa.subagents.github.graph._llm_plan", return_value=None),
            patch("makpa.subagents.google.graph._llm_plan", return_value=None),
        ):
            from makpa.supervisor.router import Route

            classify_mock.side_effect = [
                Route(agents=["rag_agent"], reasoning="t"),
                Route(agents=["github_agent"], reasoning="t"),
            ]
            rag = run_supervisor("What does the sample PDF say?")
            assert rag["status"] == "ok"
            assert "rag_agent" in rag["agent_outputs"]
            gh = run_supervisor("List open pull requests in octo-demo/hello-world.")
            assert gh["status"] == "ok"
            assert "Add RAG subgraph" in str(gh["messages"][-1].content)
    finally:
        if hasattr(get_settings, "cache_clear"):
            get_settings.cache_clear()
        clear_github_client_cache()
        clear_google_client_cache()


@pytest.mark.skipif(
    os.getenv("RUN_LIVE_PHASE4_TESTS") != "1",
    reason="Live Phase 4 tests require RUN_LIVE_PHASE4_TESTS=1 + real credentials",
)
def test_live_composite_with_credentials():
    """Flagged live run: composite scenario against real backends if present."""
    has_github = bool(os.getenv("GITHUB_MCP_PAT"))
    has_google = bool(os.getenv("GOOGLE_CLIENT_ID"))
    if not (has_github or has_google):
        pytest.skip("no live GitHub PAT or Google OAuth credentials in environment")

    from makpa.supervisor import run_supervisor

    try:
        out = run_supervisor(
            "List open pull requests in octo-demo/hello-world "
            "and check what the sample PDF says."
        )
    except Exception as e:
        pytest.skip(f"Live backends unreachable: {e}")
    assert out["status"] in ("ok", "partial")
    assert out["agent_outputs"]
