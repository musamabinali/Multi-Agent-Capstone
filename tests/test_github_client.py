"""Phase 2: GitHub MCP client unit tests (transport, retry, timeout, cache)."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch


def _settings(path: str = "mock", pat: str | None = None):
    return SimpleNamespace(
        github_mcp_pat=pat,
        github_mcp_url="https://example.com/mcp",
        mcp_tool_timeout_seconds=5,
        resolved_github_mcp_path=path,
    )


def _client(path: str = "mock", pat: str | None = None):
    from makpa.subagents.github.client import GitHubMCPClient

    with patch(
        "makpa.subagents.github.client.get_settings",
        return_value=_settings(path, pat),
    ):
        return GitHubMCPClient()


def test_connections_mock_and_real():
    import sys

    mock_client = _client("mock", None)
    conns = mock_client._connections()
    assert conns["github"]["transport"] == "stdio"
    assert conns["github"]["command"] == sys.executable
    assert conns["github"]["args"] == ["-m", "makpa.mcp_servers.github.server"]

    real_client = _client("real", "secret-pat")
    conns = real_client._connections()
    assert conns["github"]["transport"] == "streamable_http"
    assert conns["github"]["url"] == "https://example.com/mcp"
    assert conns["github"]["headers"]["Authorization"] == "Bearer secret-pat"
    assert real_client.path == "real"
    assert real_client.timeout_seconds == 5


def test_tool_list_cached_five_minutes():
    import time

    from makpa.subagents.github.client import TOOL_CACHE_TTL_SECONDS

    assert TOOL_CACHE_TTL_SECONDS == 300
    client = _client()
    inner = MagicMock()
    inner.get_tools = AsyncMock(return_value=["t1"])
    client._client = inner
    first = asyncio.run(client.aget_tools())
    second = asyncio.run(client.aget_tools())
    assert first == second == ["t1"]
    assert inner.get_tools.await_count == 1
    # Stale cache refetches.
    client._cached_at = time.monotonic() - 400
    asyncio.run(client.aget_tools())
    assert inner.get_tools.await_count == 2
    asyncio.run(client.aget_tools(force_refresh=True))
    assert inner.get_tools.await_count == 3
    client.clear_cache()
    assert client._cached_tools is None


def test_acall_tool_success_and_logging(caplog):
    import logging

    from makpa.subagents.github.client import GitHubMCPClient

    client = _client()
    tool = MagicMock()
    tool.name = "list_prs"
    tool.ainvoke = AsyncMock(return_value='{"status": "ok", "prs": []}')
    with patch.object(GitHubMCPClient, "aget_tools", AsyncMock(return_value=[tool])):
        with caplog.at_level(logging.INFO, logger="makpa.subagents.github.client"):
            out = asyncio.run(client.acall_tool("list_prs", {"repo": "o/r"}))
    assert out["status"] == "ok" and out["tool"] == "list_prs"
    assert any('"event": "github_mcp_call"' in r.message for r in caplog.records)


def test_acall_tool_unknown_tool_returns_error():
    from makpa.subagents.github.client import GitHubMCPClient

    client = _client()
    with patch.object(GitHubMCPClient, "aget_tools", AsyncMock(return_value=[])):
        out = asyncio.run(client.acall_tool("nope", {}))
    assert out["status"] == "error" and "Unknown" in out["message"]


def test_acall_tool_retries_transport_errors():
    from tenacity import wait_none

    from makpa.subagents.github.client import GitHubMCPClient

    client = _client()
    tool = MagicMock()
    tool.name = "list_prs"
    tool.ainvoke = AsyncMock(
        side_effect=[OSError("reset"), OSError("reset"), '{"status": "ok"}']
    )
    with (
        patch.object(GitHubMCPClient, "aget_tools", AsyncMock(return_value=[tool])),
        patch(
            "makpa.subagents.github.client.wait_exponential_jitter",
            return_value=wait_none(),
        ),
    ):
        out = asyncio.run(client.acall_tool("list_prs", {}))
    assert out["status"] == "ok"
    assert tool.ainvoke.await_count == 3


def test_acall_tool_timeout_returns_error():
    from tenacity import wait_none

    from makpa.subagents.github.client import GitHubMCPClient

    client = _client()
    client._settings = _settings("mock", None)
    client._settings.mcp_tool_timeout_seconds = 1

    async def _hang(_args):
        await asyncio.sleep(30)
        return "{}"

    tool = MagicMock()
    tool.name = "list_prs"
    tool.ainvoke = AsyncMock(side_effect=_hang)
    with (
        patch.object(GitHubMCPClient, "aget_tools", AsyncMock(return_value=[tool])),
        patch(
            "makpa.subagents.github.client.wait_exponential_jitter",
            return_value=wait_none(),
        ),
    ):
        out = asyncio.run(client.acall_tool("list_prs", {}))
    assert out["status"] == "error"


def test_call_tool_sync_wrapper():
    from makpa.subagents.github.client import GitHubMCPClient

    client = _client()
    with patch.object(
        GitHubMCPClient, "acall_tool", AsyncMock(return_value={"status": "ok"})
    ) as acall:
        out = client.call_tool("list_prs", {})
    assert out == {"status": "ok"}
    assert acall.await_count == 1


def test_normalize_raw_variants():
    from types import SimpleNamespace as NS

    from makpa.subagents.github.client import _normalize_raw

    assert _normalize_raw({"status": "ok"}) == {"status": "ok"}
    assert _normalize_raw('{"status": "ok", "n": 1}')["n"] == 1
    assert _normalize_raw("plain") == {"status": "ok", "text": "plain"}
    assert _normalize_raw([NS(text='{"status": "ok"}')]) == {"status": "ok"}
    assert _normalize_raw([{"type": "text", "text": '{"status": "ok"}'}]) == {
        "status": "ok"
    }
    assert _normalize_raw([NS(text="plain")])["text"] == "plain"
    assert _normalize_raw([])["status"] == "ok"
    assert _normalize_raw(42)["text"] == "42"


def test_singleton_accessors():
    from makpa.subagents.github import client as client_mod

    client_mod.clear_github_client_cache()
    with patch(
        "makpa.subagents.github.client.get_settings",
        return_value=_settings("mock", None),
    ):
        first = client_mod.get_github_client()
        assert client_mod.get_github_client() is first
    client_mod.clear_github_client_cache()
    assert client_mod._client_instance is None
