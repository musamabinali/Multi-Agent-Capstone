"""Phase 3: dual-path Google MCP client tests."""

from __future__ import annotations

import asyncio
import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch


def _settings(mode="auto", cal_url=None, gmail_url=None, creds=True):
    _ = creds
    return SimpleNamespace(
        google_mcp_mode=mode,
        google_calendar_mcp_url=cal_url,
        google_gmail_mcp_url=gmail_url,
        mcp_tool_timeout_seconds=5,
    )


def _client(mode="mock", cal_url=None, gmail_url=None, creds=True):
    from makpa.config import GoogleMCPMode
    from makpa.google import client as client_mod

    if isinstance(mode, str):
        mode = GoogleMCPMode(mode)
    with (
        patch.object(client_mod, "get_settings", return_value=_settings(mode, cal_url, gmail_url)),
        patch.object(client_mod, "_has_oauth_credentials", return_value=creds),
        patch.object(client_mod, "endpoint_reachable", return_value=False),
    ):
        return client_mod.GoogleMCPClient()


def test_endpoint_reachable_matrix():
    import urllib.error

    from makpa.google.client import endpoint_reachable

    with patch("urllib.request.urlopen", return_value=MagicMock()):
        # Context-manager protocol on MagicMock works via __enter__.
        assert endpoint_reachable("http://x") is True
    with patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.HTTPError("http://x", 404, "nf", {}, None),
    ):
        assert endpoint_reachable("http://x") is True
    with patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.URLError("refused"),
    ):
        assert endpoint_reachable("http://x") is False


def test_path_resolution_matrix():
    from makpa.config import GoogleMCPMode

    assert _client("mock").paths == {"calendar": "mock", "gmail": "mock"}
    assert _client("local", creds=True).paths == {"calendar": "local", "gmail": "local"}
    assert _client("local", creds=False).paths == {"calendar": "mock", "gmail": "mock"}
    assert _client("official").paths == {"calendar": "official", "gmail": "official"}

    from makpa.google import client as client_mod

    # AUTO with reachable official endpoints.
    with (
        patch.object(
            client_mod, "get_settings",
            return_value=_settings(GoogleMCPMode.AUTO, "http://cal", "http://gmail"),
        ),
        patch.object(client_mod, "_has_oauth_credentials", return_value=False),
        patch.object(client_mod, "endpoint_reachable", return_value=True),
    ):
        auto = client_mod.GoogleMCPClient()
    assert auto.paths == {"calendar": "official", "gmail": "official"}

    # AUTO with unreachable official + creds -> local.
    with (
        patch.object(
            client_mod, "get_settings",
            return_value=_settings(GoogleMCPMode.AUTO, "http://cal", "http://gmail"),
        ),
        patch.object(client_mod, "_has_oauth_credentials", return_value=True),
        patch.object(client_mod, "endpoint_reachable", return_value=False),
    ):
        auto = client_mod.GoogleMCPClient()
    assert auto.paths == {"calendar": "local", "gmail": "local"}

    # AUTO with nothing -> mock.
    assert _client(GoogleMCPMode.AUTO, creds=False).paths == {
        "calendar": "mock",
        "gmail": "mock",
    }


def test_connections_shapes():
    client = _client("mock")
    conns = client._connections()
    assert conns["calendar"]["transport"] == "stdio"
    assert conns["calendar"]["args"] == ["-m", "makpa.mcp_servers.google_calendar.mock"]
    assert conns["gmail"]["args"] == ["-m", "makpa.mcp_servers.google_gmail.mock"]

    from makpa.config import GoogleMCPMode as _GMM
    from makpa.google import client as client_mod

    with (
        patch.object(
            client_mod, "get_settings",
            return_value=_settings(_GMM.OFFICIAL, "http://cal", "http://gmail"),
        ),
        patch.object(client_mod, "_has_oauth_credentials", return_value=False),
    ):
        official = client_mod.GoogleMCPClient()
    conns = official._connections()
    assert conns["calendar"]["transport"] == "streamable_http"
    assert conns["calendar"]["url"] == "http://cal"
    assert official.timeout_seconds == 5

    local = _client("local", creds=True)
    conns = local._connections()
    assert conns["calendar"]["args"] == ["-m", "makpa.mcp_servers.google_calendar.server"]


def test_tool_cache_and_call_flow(caplog):
    from makpa.google.client import GoogleMCPClient

    client = _client("mock")
    inner = MagicMock()
    inner.get_tools = AsyncMock(return_value=["t"])
    client._client = inner
    assert asyncio.run(client.aget_tools("calendar")) == ["t"]
    assert asyncio.run(client.aget_tools("calendar")) == ["t"]
    assert inner.get_tools.await_count == 1
    asyncio.run(client.aget_tools("calendar", force_refresh=True))
    assert inner.get_tools.await_count == 2
    client.clear_cache()
    assert client._cached_tools == {}

    tool = MagicMock()
    tool.name = "calendar_list_events"
    tool.ainvoke = AsyncMock(return_value='{"status": "ok", "events": []}')
    with patch.object(GoogleMCPClient, "aget_tools", AsyncMock(return_value=[tool])):
        with caplog.at_level(logging.INFO, logger="makpa.google.client"):
            out = asyncio.run(
                client.acall_tool("calendar", "calendar_list_events", {})
            )
    assert out["status"] == "ok" and out["tool"] == "calendar_list_events"
    assert any('"event": "google_mcp_call"' in r.message for r in caplog.records)

    with patch.object(GoogleMCPClient, "aget_tools", AsyncMock(return_value=[])):
        out = asyncio.run(client.acall_tool("calendar", "nope", {}))
    assert out["status"] == "error"


def test_retry_timeout_and_sync_wrapper():
    from tenacity import wait_none

    from makpa.google.client import GoogleMCPClient

    client = _client("mock")
    tool = MagicMock()
    tool.name = "gmail_send_message"
    tool.ainvoke = AsyncMock(side_effect=[OSError("x"), '{"status": "ok"}'])
    with (
        patch.object(GoogleMCPClient, "aget_tools", AsyncMock(return_value=[tool])),
        patch(
            "makpa.google.client.wait_exponential_jitter",
            return_value=wait_none(),
        ),
    ):
        out = asyncio.run(client.acall_tool("gmail", "gmail_send_message", {}))
    assert out["status"] == "ok" and tool.ainvoke.await_count == 2

    with patch.object(
        GoogleMCPClient, "acall_tool", AsyncMock(return_value={"status": "ok"})
    ):
        assert client.call_tool("gmail", "x", {}) == {"status": "ok"}

    # Running-loop branch goes through the thread pool.
    async def _inside():
        return client.call_tool("gmail", "x", {})

    with patch.object(
        GoogleMCPClient, "acall_tool", AsyncMock(return_value={"status": "ok"})
    ):
        assert asyncio.run(_inside()) == {"status": "ok"}


def test_normalize_and_singleton():
    from makpa.google import client as client_mod

    assert client_mod._normalize_raw({"status": "ok"}) == {"status": "ok"}
    assert client_mod._normalize_raw("plain")["text"] == "plain"
    assert client_mod._normalize_raw([])["status"] == "ok"
    assert client_mod._normalize_raw([123])["text"] == "[123]"

    client_mod.clear_google_client_cache()
    first = client_mod.get_google_client()
    assert client_mod.get_google_client() is first
    client_mod.clear_google_client_cache()
    assert client_mod._client_instance is None
