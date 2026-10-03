"""Shared STDIO helpers for MCP contract tests (spawn + JSON-RPC)."""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Any


async def readline(proc: Any, timeout: float = 10.0) -> bytes:
    """Read the next non-empty STDIO line (servers may emit blanks)."""
    assert proc.stdout
    for _ in range(5):
        raw = await asyncio.wait_for(proc.stdout.readline(), timeout=timeout)
        if raw.strip():
            return raw
    raise AssertionError("MCP server returned only blank lines")


async def _spawn(module: str):
    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        module,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    assert proc.stdin and proc.stdout
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
    await readline(proc)
    return proc


async def stdio_call(
    module: str, tool_name: str, arguments: dict[str, Any]
) -> dict[str, Any]:
    """Spawn an MCP server, call one tool, return the parsed payload."""
    proc = await _spawn(module)
    assert proc.stdin and proc.stdout
    try:
        call = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }
        proc.stdin.write((json.dumps(call) + "\n").encode())
        await proc.stdin.drain()
        raw = await readline(proc)
        data = json.loads(raw.decode())
        if "error" in data:
            return {"status": "protocol_error", "envelope": data["error"]}
        content = data["result"]["content"]
        text = content[0]["text"]
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"status": "protocol_error", "envelope": text}
    finally:
        try:
            proc.terminate()
            await proc.wait()
        except Exception:
            pass


async def stdio_tools_list(module: str) -> list[str]:
    """Spawn an MCP server and return its tool names."""
    proc = await _spawn(module)
    assert proc.stdin and proc.stdout
    try:
        req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        proc.stdin.write((json.dumps(req) + "\n").encode())
        await proc.stdin.drain()
        raw = await readline(proc)
        data = json.loads(raw.decode())
        return [t["name"] for t in data["result"]["tools"]]
    finally:
        try:
            proc.terminate()
            await proc.wait()
        except Exception:
            pass
