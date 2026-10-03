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


def _store_path() -> str:
    """JSON file backing mock events across STDIO subprocesses.

    Each MCP tool call may spawn a fresh server subprocess, so in-memory
    fixtures alone cannot preserve created events for later update/delete
    (e.g. gate-2 rollback). The file holds fixture copies plus upserts.
    """
    import os

    try:
        from makpa.config import get_settings

        data_dir = os.path.dirname(get_settings().sample_pdf_path)
    except Exception:
        data_dir = "./data"
    return os.path.join(data_dir, "mock_calendar.json")


def _load_events() -> list[dict[str, Any]]:
    """Load events: persisted store if present, else fixture copies."""
    path = _store_path()
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, list):
            events = [dict(e) for e in data if isinstance(e, dict)]
            if events:
                return events
    except (OSError, ValueError):
        pass
    return [dict(e) for e in MOCK_EVENTS]


def _save_events(events: list[dict[str, Any]]) -> None:
    """Persist events atomically (tmp + rename)."""
    import os

    path = _store_path()
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        tmp_path = path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as handle:
            json.dump(events, handle)
        os.replace(tmp_path, path)
    except OSError as e:
        logger.warning("mock calendar store write failed: %s", e)


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
        for event in _load_events():
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
        created = {
            "id": "evt-mock-100",
            "summary": arguments["summary"],
            "start": start_iso,
            "end": end_iso,
            "attendees": arguments.get("attendees") or [],
            "html_link": "https://calendar.google.com/mock/evt-mock-100",
            "status": "confirmed",
            "mock": True,
        }
        # Upsert into the file-backed store so later update/delete calls
        # (e.g. gate-2 rollback) find the event across subprocesses.
        events = [e for e in _load_events() if e.get("id") != created["id"]]
        events.append(created)
        _save_events(events)
        return {"status": "ok", "event": dict(created)}
    if name == "calendar_check_availability":
        if not arguments.get("time_min") or not arguments.get("time_max"):
            return {"status": "error", "message": "time_min and time_max are required"}
        try:
            window_start = parse_iso_utc(str(arguments["time_min"]))
            window_end = parse_iso_utc(str(arguments["time_max"]))
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        busy = []
        for event in _load_events():
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
        events = _load_events()
        target = next(
            (e for e in events if e["id"] == arguments["event_id"]), None
        )
        if target is None:
            return {"status": "error", "message": f"event not found: {arguments['event_id']}"}
        updated = dict(target)
        if arguments.get("summary"):
            updated["summary"] = arguments["summary"]
        if arguments.get("status"):
            updated["status"] = arguments["status"]
        updated["mock"] = True
        _save_events([updated if e["id"] == updated["id"] else e for e in events])
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
