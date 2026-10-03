"""Smoke test entry point for MAKPA.

Validates that the project skeleton imports correctly, configuration loads,
and local MCP server stubs respond to tools/list requests.
"""

from __future__ import annotations

import asyncio
import json
import sys

from makpa.config import get_settings, print_startup_banner

MODULES_TO_TEST = [
    "makpa",
    "makpa.config",
    "makpa.config.settings",
    "makpa.state",
    "makpa.llm",
    "makpa.vectorstore",
    "makpa.supervisor",
    "makpa.subagents.rag",
    "makpa.subagents.github",
    "makpa.subagents.google",
    "makpa.mcp_servers.calendar",
    "makpa.mcp_servers.calendar.server",
    "makpa.mcp_servers.gmail",
    "makpa.mcp_servers.gmail.server",
    "makpa.mcp_servers.retrieval",
    "makpa.mcp_servers.retrieval.server",
    "makpa.utils",
]


MCP_SERVERS = [
    ("Calendar", [sys.executable, "-m", "makpa.mcp_servers.calendar.server"]),
    ("Gmail", [sys.executable, "-m", "makpa.mcp_servers.gmail.server"]),
    ("Retrieval", [sys.executable, "-m", "makpa.mcp_servers.retrieval.server"]),
]


def test_imports() -> tuple[bool, list[str]]:
    """Test that all modules import without errors."""
    errors = []
    for module in MODULES_TO_TEST:
        try:
            __import__(module)
        except Exception as e:
            errors.append(f"{module}: {e}")
    return len(errors) == 0, errors


async def test_mcp_server(name: str, cmd: list[str]) -> tuple[bool, list[str]]:
    """Test an MCP server by sending a tools/list request."""
    errors = []
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "smoke-test", "version": "0.1.0"},
            },
        }
        init_json = json.dumps(init_request) + "\n"
        proc.stdin.write(init_json.encode())  # type: ignore[union-attr]
        await proc.stdin.drain()  # type: ignore[union-attr]

        # Read initialize response
        _ = await asyncio.wait_for(proc.stdout.readline(), timeout=5.0)  # type: ignore[union-attr]

        # Send tools/list request
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        }
        list_json = json.dumps(list_request) + "\n"
        proc.stdin.write(list_json.encode())  # type: ignore[union-attr]
        await proc.stdin.drain()  # type: ignore[union-attr]

        # Read tools/list response
        list_response = await asyncio.wait_for(proc.stdout.readline(), timeout=5.0)  # type: ignore[union-attr]

        # Parse response
        try:
            response_data = json.loads(list_response.decode())
            if "result" in response_data and "tools" in response_data["result"]:
                tool_names = [t["name"] for t in response_data["result"]["tools"]]
                print(f"  {name} MCP server tools: {', '.join(tool_names)}")
            else:
                errors.append(f"{name}: Unexpected response format: {response_data}")
        except json.JSONDecodeError as e:
            errors.append(f"{name}: Failed to parse JSON response: {e}")

        proc.terminate()
        await proc.wait()

    except asyncio.TimeoutError:
        errors.append(f"{name}: Timeout waiting for response")
        try:
            proc.terminate()
            await proc.wait()
        except Exception:
            pass
    except Exception as e:
        errors.append(f"{name}: {e}")

    return len(errors) == 0, errors


async def run_smoke_test() -> int:
    """Run the complete smoke test."""
    print("=" * 70)
    print("MAKPA Smoke Test")
    print("=" * 70)

    all_ok = True
    all_errors = []

    # Step 1: Load settings and print banner
    print("\n[1/4] Loading configuration...")
    try:
        settings = get_settings()
        print_startup_banner()
        print(f"\nResolved mode: {settings.resolved_mode.value}")
        if settings.downgrade_reasons:
            print("Downgrade reasons:")
            for reason in settings.downgrade_reasons:
                print(f"  - {reason}")
        from makpa.llm import probe_llm

        probe = probe_llm()
        print(f"LLM probe: {probe.message}")
        for warning in probe.warnings:
            print(f"  warning: {warning}")
    except Exception as e:
        print(f"  FAILED: {e}")
        all_ok = False
        all_errors.append(f"Configuration: {e}")

    # Step 2: Test imports
    print("\n[2/4] Testing module imports...")
    imports_ok, import_errors = test_imports()
    if imports_ok:
        print("  All modules imported successfully")
    else:
        print("  Import failures:")
        for err in import_errors:
            print(f"    - {err}")
        all_ok = False
        all_errors.extend(import_errors)

    # Step 3: Test MCP servers
    print("\n[3/4] Testing local MCP server stubs...")
    for name, cmd in MCP_SERVERS:
        print(f"  Testing {name}...")
        server_ok, server_errors = await test_mcp_server(name, cmd)
        if not server_ok:
            all_ok = False
            all_errors.extend(server_errors)

    # Step 4: Summary
    print("\n[4/4] Smoke test complete")
    print("=" * 70)
    if all_ok:
        print("RESULT: PASS - All checks passed")
        return 0
    else:
        print("RESULT: FAIL - Errors encountered:")
        for err in all_errors:
            print(f"  - {err}")
        return 1


def main() -> int:
    """Main entry point."""
    return asyncio.run(run_smoke_test())


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
