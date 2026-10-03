"""Mock Gmail MCP server (zero-key demo fixtures)."""

from __future__ import annotations

import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent

from .server import GMAIL_TOOL_DEFS, GMAIL_TOOL_NAMES, validate_recipients

logger = logging.getLogger(__name__)

MOCK_MESSAGES: list[dict[str, Any]] = [
    {
        "id": "msg-001",
        "thread_id": "thr-001",
        "label_ids": ["INBOX"],
        "snippet": "Standup notes for Monday",
        "subject": "Standup notes",
        "from": "a@example.com",
    },
    {
        "id": "msg-002",
        "thread_id": "thr-002",
        "label_ids": ["INBOX"],
        "snippet": "Design review agenda attached",
        "subject": "Design review",
        "from": "b@example.com",
    },
]

MOCK_DRAFTS: list[dict[str, Any]] = [
    {"id": "draft-001", "message_id": "msg-draft-001"},
]


def handle_mock_gmail_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute a mock Gmail tool call."""
    if name not in GMAIL_TOOL_NAMES:
        return {"status": "error", "message": f"Unknown tool: {name}"}
    if name == "gmail_search_messages":
        if not arguments.get("query"):
            return {"status": "error", "message": "query is required"}
        query = str(arguments["query"]).lower()
        limit = int(arguments.get("max_results") or 10)
        hits = [
            m
            for m in MOCK_MESSAGES
            if query in m["subject"].lower() or query in m["snippet"].lower()
        ][:limit]
        slim = [
            {
                "id": m["id"],
                "thread_id": m["thread_id"],
                "label_ids": m["label_ids"],
                "snippet": m["snippet"],
            }
            for m in hits
        ]
        return {"status": "ok", "messages": slim, "count": len(slim)}
    if name == "gmail_read_message":
        if not arguments.get("message_id"):
            return {"status": "error", "message": "message_id is required"}
        found = next(
            (m for m in MOCK_MESSAGES if m["id"] == arguments["message_id"]), None
        )
        if found is None:
            return {"status": "error", "message": f"message not found: {arguments['message_id']}"}
        return {"status": "ok", "message": found}
    if name == "gmail_draft_message":
        try:
            to = validate_recipients(arguments.get("to") or [], field="to")
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        if not arguments.get("subject"):
            return {"status": "error", "message": "subject is required"}
        return {
            "status": "ok",
            "draft": {"id": "draft-mock-100", "message_id": "msg-mock-100", "to": to, "mock": True},
        }
    if name == "gmail_send_message":
        try:
            to = validate_recipients(arguments.get("to") or [], field="to")
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        if not arguments.get("subject"):
            return {"status": "error", "message": "subject is required"}
        if arguments.get("draft_id"):
            sent_id, thread_id = "msg-from-draft-mock-100", "thr-mock-100"
        else:
            sent_id, thread_id = "msg-mock-101", "thr-mock-101"
        return {
            "status": "ok",
            "sent": {
                "id": sent_id,
                "thread_id": thread_id,
                "label_ids": ["SENT"],
                "to": to,
                "mock": True,
            },
        }
    return {"status": "error", "message": f"Unhandled tool: {name}"}  # pragma: no cover


async def _list_tools() -> list[Any]:
    return GMAIL_TOOL_DEFS


async def _call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    try:
        payload = handle_mock_gmail_tool(name, arguments or {})
    except Exception as e:
        logger.warning("mock gmail tool %s failed: %s", name, e)
        payload = {"status": "error", "message": str(e)}
    return [TextContent(type="text", text=json.dumps(payload))]


class MockGmailMCPServer:
    """Mock Gmail MCP server speaking MCP over STDIO."""

    def __init__(self) -> None:
        self.server = Server("gmail-mock-mcp")
        self.server.list_tools()(_list_tools)
        self.server.call_tool()(_call_tool)

    async def run(self) -> None:
        """Run the mock server over STDIO."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


async def main() -> None:
    """Entry point for the mock Gmail MCP server."""
    server = MockGmailMCPServer()
    await server.run()


if __name__ == "__main__":  # pragma: no cover
    import asyncio

    asyncio.run(main())


if __name__ == "__main__":  # pragma: no cover
    import asyncio

    asyncio.run(main())
