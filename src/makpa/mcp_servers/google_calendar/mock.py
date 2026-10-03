"""Mock Google Calendar MCP server (zero-key demo fixtures)."""

from __future__ import annotations

import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent

from .server import (
    CALENDAR_TOOL_DEFS,
    CALENDAR_TOOL_NAMES,
    _availability_payload,
    parse_iso_utc,
)

logger = logging.getLogger(__name__)

MOCK_EVENTS: list[dict[str, Any]] = [
    {
        "id": "evt-001",
        "summary": "Team standup",
        "start": "2026-10-01T09:00:00+00:00",
        "end": "2026-10-01T09:30:00+00:00",
        "attendees": ["a@example.com"],
        "html_link": "https://calendar.google.com/mock/evt-001",
        "status": "confirmed",
    },
    {
        "id": "evt-002",
        "summary": "Design review",
        "start": "2026-10-01T14:00:00+00:00",
        "end": "2026-10-01T15:00:00+00:00",
        "attendees": ["b@example.com"],
        "html_link": "https://calendar.google.com/mock/evt-002",
        "status": "confirmed",
    },
]


def handle_mock_calendar_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute a mock Calendar tool call."""
    if name not in CALENDAR_TOOL_NAMES:
        return {"status": "error", "message": f"Unknown tool: {name}"}
    if name == "calendar_list_events":
        if not arguments.get("time_min") or not arguments.get("time_max"):
            return {"status": "error", "message": "time_min and time_max are required"}
        try:
            window_start = parse_iso_utc(str(arguments["time_min"]))
            window_end = parse_iso_utc(str(arguments["time_max"]))
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        in_window = []
        for event in MOCK_EVENTS:
            start = parse_iso_utc(str(event["start"]))
            if window_start <= start <= window_end:
                in_window.append(event)
        limit = int(arguments.get("max_results") or 25)
        in_window = in_window[:limit]
        return {"status": "ok", "events": in_window, "count": len(in_window)}
    if name == "calendar_create_event":
        for key in ("summary", "start", "end"):
            if not arguments.get(key):
                return {"status": "error", "message": f"{key} is required"}
        try:
            start_iso = parse_iso_utc(str(arguments["start"])).isoformat()
            end_iso = parse_iso_utc(str(arguments["end"])).isoformat()
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        if end_iso <= start_iso:
            return {"status": "error", "message": "end must be after start"}
        return {
            "status": "ok",
            "event": {
                "id": "evt-mock-100",
                "summary": arguments["summary"],
                "start": start_iso,
                "end": end_iso,
                "attendees": arguments.get("attendees") or [],
                "html_link": "https://calendar.google.com/mock/evt-mock-100",
                "status": "confirmed",
                "mock": True,
            },
        }
    if name == "calendar_check_availability":
        if not arguments.get("time_min") or not arguments.get("time_max"):
            return {"status": "error", "message": "time_min and time_max are required"}
        try:
            window_start = parse_iso_utc(str(arguments["time_min"]))
            window_end = parse_iso_utc(str(arguments["time_max"]))
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        busy = []
        for event in MOCK_EVENTS:
            event_start = parse_iso_utc(str(event["start"]))
            event_end = parse_iso_utc(str(event["end"]))
            if event_start < window_end and window_start < event_end:
                busy.append({"start": event["start"], "end": event["end"]})
        return _availability_payload(
            free=not busy,
            busy=busy,
            attendees=arguments.get("attendees") or [],
        )
    if name == "calendar_update_event":
        if not arguments.get("event_id"):
            return {"status": "error", "message": "event_id is required"}
        target = next(
            (e for e in MOCK_EVENTS if e["id"] == arguments["event_id"]), None
        )
        if target is None:
            return {"status": "error", "message": f"event not found: {arguments['event_id']}"}
        updated = dict(target)
        if arguments.get("summary"):
            updated["summary"] = arguments["summary"]
        if arguments.get("status"):
            updated["status"] = arguments["status"]
        updated["mock"] = True
        return {"status": "ok", "event": updated}
    return {"status": "error", "message": f"Unhandled tool: {name}"}  # pragma: no cover


async def _list_tools() -> list[Any]:
    return CALENDAR_TOOL_DEFS


async def _call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    try:
        payload = handle_mock_calendar_tool(name, arguments or {})
    except Exception as e:
        logger.warning("mock calendar tool %s failed: %s", name, e)
        payload = {"status": "error", "message": str(e)}
    return [TextContent(type="text", text=json.dumps(payload))]


class MockCalendarMCPServer:
    """Mock Calendar MCP server speaking MCP over STDIO."""

    def __init__(self) -> None:
        self.server = Server("calendar-mock-mcp")
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
    """Entry point for the mock Calendar MCP server."""
    server = MockCalendarMCPServer()
    await server.run()


if __name__ == "__main__":  # pragma: no cover
    import asyncio

    asyncio.run(main())


if __name__ == "__main__":  # pragma: no cover
    import asyncio

    asyncio.run(main())
