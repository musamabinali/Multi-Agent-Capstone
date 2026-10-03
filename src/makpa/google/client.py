"""Dual-path Google MCP client for MAKPA Phase 3.

Resolves `official` | `local` | `auto` (+ `mock`) per service and talks
to both Calendar and Gmail through `MultiServerMCPClient`. Falls back
to the in-repo mock STDIO servers when no OAuth credentials exist.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any

from langchain_core.tools import BaseTool
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from makpa.config import GoogleMCPMode, get_settings

logger = logging.getLogger(__name__)

CALENDAR_SERVER = "calendar"
GMAIL_SERVER = "gmail"
TOOL_CACHE_TTL_SECONDS = 300
MAX_ATTEMPTS = 3
OFFICIAL_PROBE_TIMEOUT_SECONDS = 3

RETRYABLE_EXCEPTIONS: tuple[type[BaseException], ...] = (
    asyncio.TimeoutError,
    TimeoutError,
    ConnectionError,
    OSError,
)

try:  # pragma: no cover - optional dependency surface
    from mcp.shared.exceptions import McpError

    RETRYABLE_EXCEPTIONS = RETRYABLE_EXCEPTIONS + (McpError,)
except Exception:  # pragma: no cover
    pass


def _log_call(
    server: str,
    tool: str,
    duration_ms: int,
    status: str,
    path: str,
    error: str | None = None,
) -> None:
    """Emit one structured JSON log per MCP call (GitHub-client format)."""
    payload: dict[str, Any] = {
        "event": "google_mcp_call",
        "server": server,
        "tool": tool,
        "duration_ms": duration_ms,
        "status": status,
        "path": path,
    }
    if error:
        payload["error"] = error
    logger.info(json.dumps(payload))


def endpoint_reachable(url: str, timeout: float = OFFICIAL_PROBE_TIMEOUT_SECONDS) -> bool:
    """Probe an official MCP endpoint (any HTTP response counts as reachable)."""
    try:
        request = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(request, timeout=timeout):
            return True
    except Exception as e:
        # HTTPError (4xx/5xx) means the host answered; anything else did not.
        if isinstance(e, urllib.error.HTTPError):
            return True
        return False


def _has_oauth_credentials() -> bool:
    """Check for usable OAuth credentials without network access."""
    from makpa.google.oauth import load_token_cache

    cache = load_token_cache()
    return bool(cache and cache.get("refresh_token"))


class GoogleMCPClient:
    """Dual-path client for the Calendar and Gmail MCP servers."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._paths = self._resolve_paths()
        self._client: Any = None
        self._cached_tools: dict[str, list[BaseTool]] = {}
        self._cached_at: dict[str, float] = {}

    @property
    def paths(self) -> dict[str, str]:
        """Resolved path per server: official|local|mock."""
        return dict(self._paths)

    @property
    def timeout_seconds(self) -> int:
        """Per-tool timeout in seconds."""
        return int(self._settings.mcp_tool_timeout_seconds)

    def _resolve_paths(self) -> dict[str, str]:
        mode = self._settings.google_mcp_mode
        decision: dict[str, str] = {}
        for server in (CALENDAR_SERVER, GMAIL_SERVER):
            decision[server] = self._resolve_one(server, mode)
        logger.info(
            json.dumps(
                {
                    "event": "google_mcp_path_resolved",
                    "mode": mode.value,
                    "paths": decision,
                }
            )
        )
        return decision

    def _resolve_one(self, server: str, mode: GoogleMCPMode) -> str:
        if mode == GoogleMCPMode.MOCK:
            return "mock"
        if mode == GoogleMCPMode.OFFICIAL:
            return "official"
        if mode == GoogleMCPMode.LOCAL:
            if _has_oauth_credentials():
                return "local"
            logger.warning("No OAuth credentials; using mock %s MCP server", server)
            return "mock"
        # AUTO: probe official endpoints first with a short timeout.
        url = self._official_url(server)
        if url and endpoint_reachable(url):
            return "official"
        if _has_oauth_credentials():
            logger.info("Official %s MCP unreachable; falling back to local", server)
            return "local"
        logger.warning("No official %s MCP and no OAuth; using mock server", server)
        return "mock"

    def _official_url(self, server: str) -> str | None:
        if server == CALENDAR_SERVER:
            url = self._settings.google_calendar_mcp_url
        else:
            url = self._settings.google_gmail_mcp_url
        return str(url) if url else None

    def _connections(self) -> dict[str, Any]:
        # NOTE: MCP stdio passes only a subset of the parent environment by
        # default, so settings overridden via os.environ (e.g. attendee mode
        # in tests/demos) would be invisible to the servers. Propagate fully:
        # these are our own subprocesses.
        connections: dict[str, Any] = {}
        for server, path in self._paths.items():
            if path == "official":
                connections[server] = {
                    "transport": "streamable_http",
                    "url": self._official_url(server),
                    "timeout": float(self._settings.mcp_tool_timeout_seconds),
                }
            elif path == "local":
                module = (
                    "makpa.mcp_servers.google_calendar.server"
                    if server == CALENDAR_SERVER
                    else "makpa.mcp_servers.google_gmail.server"
                )
                connections[server] = {
                    "transport": "stdio",
                    "command": sys.executable,
                    "args": ["-m", module],
                    "env": dict(os.environ),
                }
            else:
                module = (
                    "makpa.mcp_servers.google_calendar.mock"
                    if server == CALENDAR_SERVER
                    else "makpa.mcp_servers.google_gmail.mock"
                )
                connections[server] = {
                    "transport": "stdio",
                    "command": sys.executable,
                    "args": ["-m", module],
                    "env": dict(os.environ),
                }
        return connections

    def _get_client(self) -> Any:
        if self._client is None:
            from langchain_mcp_adapters.client import MultiServerMCPClient

            self._client = MultiServerMCPClient(self._connections())
        return self._client

    async def aget_tools(
        self, server: str, *, force_refresh: bool = False
    ) -> list[BaseTool]:
        """Return one server's tool list, cached for 5 minutes."""
        now = time.monotonic()
        if (
            not force_refresh
            and server in self._cached_tools
            and (now - self._cached_at.get(server, 0.0)) < TOOL_CACHE_TTL_SECONDS
        ):
            return self._cached_tools[server]
        client = self._get_client()
        tools: list[BaseTool] = await client.get_tools(server_name=server)
        self._cached_tools[server] = tools
        self._cached_at[server] = now
        return tools

    def _retry_decorator(self) -> Any:
        return retry(
            stop=stop_after_attempt(MAX_ATTEMPTS),
            wait=wait_exponential_jitter(initial=1, max=10),
            retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
            reraise=True,
        )

    async def acall_tool(
        self, server: str, name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Call one Google MCP tool with retry, timeout, and JSON logging."""
        start = time.monotonic()
        path = self._paths.get(server, "mock")
        retryer = self._retry_decorator()

        async def _attempt() -> dict[str, Any]:
            tools = await self.aget_tools(server)
            matches = [t for t in tools if t.name == name]
            if not matches:
                raise ValueError(f"Unknown Google MCP tool: {name}")
            raw = await asyncio.wait_for(
                matches[0].ainvoke(arguments),
                timeout=float(self._settings.mcp_tool_timeout_seconds),
            )
            return _normalize_raw(raw)

        try:
            result: dict[str, Any] = await retryer(_attempt)()
        except Exception as e:
            duration_ms = int((time.monotonic() - start) * 1000)
            _log_call(server, name, duration_ms, "error", path, error=str(e))
            return {"status": "error", "message": str(e), "tool": name}
        duration_ms = int((time.monotonic() - start) * 1000)
        status = str(result.get("status", "ok"))
        _log_call(server, name, duration_ms, status, path)
        result.setdefault("tool", name)
        return result

    def call_tool(
        self, server: str, name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Synchronous wrapper around :meth:`acall_tool`."""
        from typing import cast

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.acall_tool(server, name, arguments))
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(
                asyncio.run, self.acall_tool(server, name, arguments)
            )
            raw = future.result(
                timeout=float(self._settings.mcp_tool_timeout_seconds) * MAX_ATTEMPTS + 30
            )
            return cast("dict[str, Any]", dict(raw))

    def clear_cache(self) -> None:
        """Clear cached tool lists (useful for testing)."""
        self._cached_tools = {}
        self._cached_at = {}


def _normalize_raw(raw: Any) -> dict[str, Any]:
    """Normalize a raw MCP tool result into a payload dict."""
    if isinstance(raw, dict):
        return dict(raw)
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass
        return {"status": "ok", "text": raw}
    if isinstance(raw, list) and raw:
        first = raw[0]
        text = getattr(first, "text", None)
        if text is None and isinstance(first, dict):
            maybe_text = first.get("text")
            text = maybe_text if isinstance(maybe_text, str) else None
        if isinstance(text, str):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
            return {"status": "ok", "text": text}
        return {"status": "ok", "text": str(raw)}
    return {"status": "ok", "text": str(raw)}


_client_instance: GoogleMCPClient | None = None


def get_google_client() -> GoogleMCPClient:
    """Return the process-wide Google MCP client singleton."""
    global _client_instance
    if _client_instance is None:
        _client_instance = GoogleMCPClient()
    return _client_instance


def clear_google_client_cache() -> None:
    """Drop the client singleton (useful for testing)."""
    global _client_instance
    if _client_instance is not None:
        _client_instance.clear_cache()
    _client_instance = None


__all__ = [
    "CALENDAR_SERVER",
    "GMAIL_SERVER",
    "GoogleMCPClient",
    "MAX_ATTEMPTS",
    "TOOL_CACHE_TTL_SECONDS",
    "clear_google_client_cache",
    "endpoint_reachable",
    "get_google_client",
]
