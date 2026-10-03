"""GitHub MCP client for MAKPA Phase 2.

Wires :class:`MultiServerMCPClient` from ``langchain-mcp-adapters`` to the
GitHub MCP server over **Streamable HTTP**, with automatic degradation to
the in-repo mock STDIO server when no PAT is configured.

Per-call guarantees:

- tool list cached for 5 minutes,
- 3-retry exponential backoff with jitter on transport errors,
- per-tool timeout from ``MCP_TOOL_TIMEOUT_SECONDS``,
- one structured JSON log per call.
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
import time
from typing import Any, cast

from langchain_core.tools import BaseTool
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from makpa.config import get_settings

logger = logging.getLogger(__name__)

SERVER_NAME = "github"
TOOL_CACHE_TTL_SECONDS = 300
MAX_ATTEMPTS = 3

#: Exceptions considered transient transport failures (retried).
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
    tool: str,
    duration_ms: int,
    status: str,
    path: str,
    error: str | None = None,
) -> None:
    """Emit one structured JSON log per MCP call."""
    payload: dict[str, Any] = {
        "event": "github_mcp_call",
        "server": SERVER_NAME,
        "tool": tool,
        "duration_ms": duration_ms,
        "status": status,
        "path": path,
    }
    if error:
        payload["error"] = error
    logger.info(json.dumps(payload))


class GitHubMCPClient:
    """Client for the GitHub MCP server (real or mock)."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._path = self._settings.resolved_github_mcp_path
        self._client: Any = None
        self._cached_tools: list[BaseTool] | None = None
        self._cached_at: float = 0.0

    @property
    def path(self) -> str:
        """Resolved GitHub MCP path: ``real`` or ``mock``."""
        return str(self._path)

    @property
    def timeout_seconds(self) -> int:
        """Per-tool timeout in seconds."""
        return int(self._settings.mcp_tool_timeout_seconds)

    def _connections(self) -> dict[str, Any]:
        """Build the MultiServerMCPClient connections dict."""
        if self._path == "real" and self._settings.github_mcp_pat:
            return {
                SERVER_NAME: {
                    "transport": "streamable_http",
                    "url": self._settings.github_mcp_url,
                    "headers": {
                        "Authorization": f"Bearer {self._settings.github_mcp_pat}"
                    },
                    "timeout": float(self._settings.mcp_tool_timeout_seconds),
                }
            }
        return {
            SERVER_NAME: {
                "transport": "stdio",
                "command": sys.executable,
                "args": ["-m", "makpa.mcp_servers.github.server"],
            }
        }

    def _get_client(self) -> Any:
        """Lazily construct the MultiServerMCPClient."""
        if self._client is None:
            from langchain_mcp_adapters.client import MultiServerMCPClient

            self._client = MultiServerMCPClient(self._connections())
        return self._client

    async def aget_tools(self, *, force_refresh: bool = False) -> list[BaseTool]:
        """Return the GitHub tool list, cached for 5 minutes."""
        now = time.monotonic()
        if (
            not force_refresh
            and self._cached_tools is not None
            and (now - self._cached_at) < TOOL_CACHE_TTL_SECONDS
        ):
            return self._cached_tools
        client = self._get_client()
        tools: list[BaseTool] = await client.get_tools(server_name=SERVER_NAME)
        self._cached_tools = tools
        self._cached_at = now
        logger.info(
            json.dumps(
                {
                    "event": "github_mcp_tools_cached",
                    "server": SERVER_NAME,
                    "count": len(tools),
                    "path": self._path,
                }
            )
        )
        return tools

    def _retry_decorator(self) -> Any:
        return retry(
            stop=stop_after_attempt(MAX_ATTEMPTS),
            wait=wait_exponential_jitter(initial=1, max=10),
            retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
            reraise=True,
        )

    async def acall_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Call one GitHub MCP tool with retry, timeout, and JSON logging."""
        start = time.monotonic()
        retryer = self._retry_decorator()

        async def _attempt() -> dict[str, Any]:
            tools = await self.aget_tools()
            matches = [t for t in tools if t.name == name]
            if not matches:
                raise ValueError(f"Unknown GitHub MCP tool: {name}")
            raw = await asyncio.wait_for(
                matches[0].ainvoke(arguments),
                timeout=float(self._settings.mcp_tool_timeout_seconds),
            )
            return _normalize_raw(raw)

        try:
            result: dict[str, Any] = await retryer(_attempt)()
        except Exception as e:
            duration_ms = int((time.monotonic() - start) * 1000)
            _log_call(name, duration_ms, "error", self._path, error=str(e))
            return {"status": "error", "message": str(e), "tool": name}
        duration_ms = int((time.monotonic() - start) * 1000)
        status = str(result.get("status", "ok"))
        _log_call(name, duration_ms, status, self._path)
        result.setdefault("tool", name)
        return result

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Synchronous wrapper around :meth:`acall_tool`."""
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.acall_tool(name, arguments))
        # A loop is already running: run in a dedicated thread to avoid
        # nesting event loops.
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(asyncio.run, self.acall_tool(name, arguments))
            raw = future.result(
                timeout=float(self._settings.mcp_tool_timeout_seconds) * MAX_ATTEMPTS + 30
            )
            return cast("dict[str, Any]", dict(raw))

    def clear_cache(self) -> None:
        """Clear the cached tool list (useful for testing)."""
        self._cached_tools = None
        self._cached_at = 0.0


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


_client_instance: GitHubMCPClient | None = None


def get_github_client() -> GitHubMCPClient:
    """Return the process-wide GitHub MCP client singleton."""
    global _client_instance
    if _client_instance is None:
        _client_instance = GitHubMCPClient()
    return _client_instance


def clear_github_client_cache() -> None:
    """Drop the client singleton (useful for testing)."""
    global _client_instance
    if _client_instance is not None:
        _client_instance.clear_cache()
    _client_instance = None


__all__ = [
    "GitHubMCPClient",
    "clear_github_client_cache",
    "get_github_client",
    "MAX_ATTEMPTS",
    "SERVER_NAME",
    "TOOL_CACHE_TTL_SECONDS",
]
