"""Phase 2: contract tests against the mock GitHub MCP server over STDIO."""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Any


async def _readline(proc, timeout: float = 10.0) -> bytes:
    """Read the next non-empty STDIO line (servers may emit blanks)."""
    assert proc.stdout
    for _ in range(5):
        raw = await asyncio.wait_for(proc.stdout.readline(), timeout=timeout)
        if raw.strip():
            return raw
    raise AssertionError("MCP server returned only blank lines")


async def _stdio_call(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Spawn the mock server, call one tool, return the parsed payload."""
    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "makpa.mcp_servers.github.server",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    assert proc.stdin and proc.stdout
    try:
        init = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "contract-test", "version": "0.1.0"},
            },
        }
        proc.stdin.write((json.dumps(init) + "\n").encode())
        await proc.stdin.drain()
        await _readline(proc)

        call = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }
        proc.stdin.write((json.dumps(call) + "\n").encode())
        await proc.stdin.drain()
        raw = await _readline(proc)
        data = json.loads(raw.decode())
        if "error" in data:
            return {"status": "protocol_error", "envelope": data["error"]}
        content = data["result"]["content"]
        assert content and content[0]["type"] == "text"
        text = content[0]["text"]
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Schema violations arrive as isError result envelopes, plain text.
            return {"status": "protocol_error", "envelope": text}
    finally:
        try:
            proc.terminate()
            await proc.wait()
        except Exception:
            pass


async def _stdio_tools_list() -> list[str]:
    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "makpa.mcp_servers.github.server",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    assert proc.stdin and proc.stdout
    try:
        init = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "contract-test", "version": "0.1.0"},
            },
        }
        proc.stdin.write((json.dumps(init) + "\n").encode())
        await proc.stdin.drain()
        await _readline(proc)
        req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        proc.stdin.write((json.dumps(req) + "\n").encode())
        await proc.stdin.drain()
        raw = await _readline(proc)
        data = json.loads(raw.decode())
        return [t["name"] for t in data["result"]["tools"]]
    finally:
        try:
            proc.terminate()
            await proc.wait()
        except Exception:
            pass


def test_mock_server_lists_all_eight_tools():
    names = asyncio.run(_stdio_tools_list())
    assert names == [
        "list_repos",
        "list_prs",
        "get_pr",
        "list_issues",
        "create_issue",
        "search_code",
        "get_commits",
        "read_file",
    ]


def test_mock_server_calls_every_tool():
    cases = [
        ("list_repos", {"owner": "octo-demo"}),
        ("list_prs", {"repo": "octo-demo/hello-world"}),
        ("get_pr", {"repo": "octo-demo/hello-world", "number": 7}),
        ("list_issues", {"repo": "octo-demo/hello-world"}),
        (
            "create_issue",
            {"repo": "octo-demo/hello-world", "title": "Hi", "body": "b"},
        ),
        ("search_code", {"query": "def main"}),
        ("get_commits", {"repo": "octo-demo/hello-world"}),
        ("read_file", {"repo": "octo-demo/hello-world", "path": "README.md"}),
    ]
    for name, args in cases:
        payload = asyncio.run(_stdio_call(name, args))
        assert payload["status"] == "ok", f"{name}: {payload}"


def test_mock_server_error_shapes():
    payload = asyncio.run(_stdio_call("nope", {}))
    assert payload["status"] == "error"
    # Missing required args is rejected by SDK schema validation first.
    payload = asyncio.run(_stdio_call("list_prs", {}))
    assert payload["status"] == "protocol_error"
    assert "repo" in str(payload["envelope"])
    payload = asyncio.run(
        _stdio_call("get_pr", {"repo": "octo-demo/hello-world", "number": 999})
    )
    assert payload["status"] == "error"
    payload = asyncio.run(
        _stdio_call("read_file", {"repo": "octo-demo/hello-world", "path": "nope.txt"})
    )
    assert payload["status"] == "error"


def test_handle_tool_unit_branches():
    from makpa.mcp_servers.github.server import TOOL_NAMES, handle_tool

    assert len(TOOL_NAMES) == 8
    assert handle_tool("list_repos", {})["status"] == "error"
    out = handle_tool("list_repos", {"owner": "x", "limit": 1})
    assert out["count"] == 1
    out = handle_tool("list_prs", {"repo": "o/r", "state": "closed"})
    assert out["prs"] and all(p["state"] == "closed" for p in out["prs"])
    assert handle_tool("get_pr", {"repo": "o/r"})["status"] == "error"
    out = handle_tool(
        "list_issues", {"repo": "o/r", "state": "open", "labels": ["testing"]}
    )
    assert out["issues"] and out["issues"][0]["number"] == 12
    assert handle_tool("create_issue", {"repo": "o/r"})["status"] == "error"
    assert handle_tool("search_code", {})["status"] == "error"
    out = handle_tool("search_code", {"query": "q", "limit": 1})
    assert out["count"] == 1
    assert handle_tool("get_commits", {})["status"] == "error"
    out = handle_tool("get_commits", {"repo": "o/r", "branch": "dev", "limit": 1})
    assert out["branch"] == "dev" and out["count"] == 1
    assert handle_tool("read_file", {"repo": "o/r"})["status"] == "error"
