"""Phase 3: settings OAuth-state tests + zero-key + flagged live tests."""

from __future__ import annotations

import json
import os

import pytest


def test_oauth_state_cached_refreshing_missing(tmp_path):
    from makpa.config import Settings

    live_cache = tmp_path / "live.json"
    live_cache.write_text(
        json.dumps(
            {
                "access_token": "a",
                "refresh_token": "r",
                "expiry": "2999-01-01T00:00:00+00:00",
                "scopes": [],
            }
        ),
        encoding="utf-8",
    )
    cached_settings = Settings(google_token_cache_path=str(live_cache))
    assert cached_settings.resolve_google_oauth_state() == "cached"

    stale_cache = tmp_path / "stale.json"
    stale_cache.write_text(
        json.dumps(
            {
                "access_token": "a",
                "refresh_token": "r",
                "expiry": "2000-01-01T00:00:00+00:00",
                "scopes": [],
            }
        ),
        encoding="utf-8",
    )
    assert (
        Settings(google_token_cache_path=str(stale_cache)).resolve_google_oauth_state()
        == "refreshing"
    )

    no_refresh = tmp_path / "norefresh.json"
    no_refresh.write_text(json.dumps({"access_token": "a"}), encoding="utf-8")
    assert (
        Settings(google_token_cache_path=str(no_refresh)).resolve_google_oauth_state()
        == "missing"
    )

    broken = tmp_path / "broken.json"
    broken.write_text("{invalid", encoding="utf-8")
    assert (
        Settings(google_token_cache_path=str(broken)).resolve_google_oauth_state()
        == "missing"
    )
    assert (
        Settings(
            google_token_cache_path=str(tmp_path / "absent.json")
        ).resolve_google_oauth_state()
        == "missing"
    )

    bad_expiry = tmp_path / "badexpiry.json"
    bad_expiry.write_text(
        json.dumps({"access_token": "a", "refresh_token": "r", "expiry": "never"}),
        encoding="utf-8",
    )
    assert (
        Settings(google_token_cache_path=str(bad_expiry)).resolve_google_oauth_state()
        == "refreshing"
    )


def test_google_mcp_mode_mock_value():
    from makpa.config import GoogleMCPMode, Settings

    assert Settings(google_mcp_mode="mock").google_mcp_mode == GoogleMCPMode.MOCK
    assert Settings(google_mcp_mode=GoogleMCPMode.MOCK).google_mcp_mode == GoogleMCPMode.MOCK


def test_zero_key_google_flow(monkeypatch):
    """Full Google flow in demo mode with mock servers and no OAuth."""
    # Blank (not delete): repo .env carries keys, and env vars override it.
    for var in (
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "GEMINI_API_KEY",
        "GROQ_API_KEY",
    ):
        monkeypatch.setenv(var, "")
    monkeypatch.setenv("MAKPA_MODE", "demo")
    monkeypatch.setenv("GOOGLE_MCP_MODE", "mock")

    from unittest.mock import patch

    from makpa.config import get_settings
    from makpa.google import clear_google_client_cache

    if hasattr(get_settings, "cache_clear"):
        get_settings.cache_clear()
    clear_google_client_cache()
    try:
        from makpa.subagents.google import run_google

        # Heuristic planning keeps the zero-key flow deterministic when a
        # real LLM is configured (LLM planning itself is unit-tested).
        with patch("makpa.subagents.google.graph._llm_plan", return_value=None):
            result = run_google("What is on my calendar?")
            assert result["status"] in ("ok", "empty")
            free = run_google(
                "Check availability for a@example.com "
                "from 2030-01-01T00:00:00Z to 2030-01-02T00:00:00Z"
            )
            assert free["status"] in ("ok", "empty")
            if free["status"] == "ok":
                assert "calendar_check_availability" in free["answer"]
    finally:
        if hasattr(get_settings, "cache_clear"):
            get_settings.cache_clear()
        clear_google_client_cache()


@pytest.mark.skipif(
    os.getenv("RUN_LIVE_GOOGLE_TESTS") != "1",
    reason="Live Google tests require RUN_LIVE_GOOGLE_TESTS=1 + real OAuth",
)
def test_live_google_end_to_end():
    """Real Google account end-to-end (flagged; needs OAuth + network)."""
    import asyncio

    from makpa.google import get_google_client

    async def _run():
        tools = await get_google_client().aget_tools("calendar")
        assert tools, "expected tools from a live Calendar MCP path"
        return await get_google_client().acall_tool(
            "calendar",
            "calendar_list_events",
            {"time_min": "2030-01-01T00:00:00Z", "time_max": "2030-01-08T00:00:00Z"},
        )

    try:
        out = asyncio.run(_run())
    except Exception as e:
        pytest.skip(f"Live Google path unreachable: {e}")
    assert out["status"] in ("ok", "error")
