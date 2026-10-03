"""Local Google Calendar MCP server for MAKPA (real Calendar v3 wrapper).

Speaks MCP over STDIO. Uses OAuth credentials from the token cache;
every handler degrades to a structured error envelope on quota,
auth, or argument failures.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

logger = logging.getLogger(__name__)


def _get_service() -> Any:
    """Build the Calendar v3 service from cached OAuth credentials."""
    from googleapiclient.discovery import build

    from makpa.google.oauth import get_google_credentials

    return build("calendar", "v3", credentials=get_google_credentials())


def parse_iso_utc(raw: str) -> datetime:
    """Parse ISO 8601; naive timestamps are assumed UTC.

    Raises:
        ValueError: If the timestamp cannot be parsed.
    """
    try:
        parsed = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except ValueError as e:
        raise ValueError(f"Invalid ISO 8601 timestamp: {raw!r}") from e
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def attendee_mode() -> str:
    """Return the configured attendee-verification mode."""
    from makpa.config import get_settings

    return str(get_settings().google_calendar_attendee_mode)


def _availability_payload(
    free: bool, busy: list[dict[str, Any]], attendees: list[str]
) -> dict[str, Any]:
    """Label availability as partial when attendees exceed own calendar."""
    mode = attendee_mode()
    partial = mode == "own_only" and len(attendees) > 0
    payload: dict[str, Any] = {
        "status": "ok",
        "free": free,
        "busy": busy,
        "attendee_calendars": "unavailable (free/busy reflects the queried calendar only)",
        "attendees": attendees,
        "attendee_mode": mode,
        "partial": partial,
    }
    if partial:
        payload["message"] = (
            "Availability is partial: attendee calendars were not verified "
            "(GOOGLE_CALENDAR_ATTENDEE_MODE=own_only)."
        )
    return payload


def _event_to_payload(item: dict[str, Any]) -> dict[str, Any]:
    start = item.get("start", {})
    end = item.get("end", {})
    return {
        "id": item.get("id", ""),
        "summary": item.get("summary", ""),
        "start": start.get("dateTime") or start.get("date", ""),
        "end": end.get("dateTime") or end.get("date", ""),
        "attendees": [a.get("email", "") for a in item.get("attendees", [])],
        "html_link": item.get("htmlLink", ""),
        "status": item.get("status", ""),
    }


def handle_calendar_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute a Calendar tool against the v3 API."""
    if name == "calendar_list_events":
        for key in ("time_min", "time_max"):
            if not arguments.get(key):
                return {"status": "error", "message": f"{key} is required"}
        try:
            time_min = parse_iso_utc(str(arguments["time_min"])).isoformat()
            time_max = parse_iso_utc(str(arguments["time_max"])).isoformat()
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        calendar_id = arguments.get("calendar_id") or "primary"
        max_results = int(arguments.get("max_results") or 25)
        try:
            service = _get_service()
            response = (
                service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
        except Exception as e:
            logger.warning("calendar_list_events failed: %s", type(e).__name__)
            return {"status": "error", "message": f"Calendar API error: {e}"}
        items = response.get("items", [])
        return {
            "status": "ok",
            "events": [_event_to_payload(i) for i in items],
            "count": len(items),
        }
    if name == "calendar_create_event":
        for key in ("summary", "start", "end"):
            if not arguments.get(key):
                return {"status": "error", "message": f"{key} is required"}
        try:
            start = parse_iso_utc(str(arguments["start"])).isoformat()
            end = parse_iso_utc(str(arguments["end"])).isoformat()
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        if end <= start:
            return {"status": "error", "message": "end must be after start"}
        attendees = arguments.get("attendees") or []
        body: dict[str, Any] = {
            "summary": arguments["summary"],
            "start": {"dateTime": start, "timeZone": "UTC"},
            "end": {"dateTime": end, "timeZone": "UTC"},
        }
        if arguments.get("description"):
            body["description"] = arguments["description"]
        if attendees:
            body["attendees"] = [{"email": a} for a in attendees]
        calendar_id = arguments.get("calendar_id") or "primary"
        try:
            service = _get_service()
            created = service.events().insert(calendarId=calendar_id, body=body).execute()
        except Exception as e:
            logger.warning("calendar_create_event failed: %s", type(e).__name__)
            return {"status": "error", "message": f"Calendar API error: {e}"}
        return {"status": "ok", "event": _event_to_payload(created)}
    if name == "calendar_check_availability":
        for key in ("time_min", "time_max"):
            if not arguments.get(key):
                return {"status": "error", "message": f"{key} is required"}
        try:
            time_min = parse_iso_utc(str(arguments["time_min"])).isoformat()
            time_max = parse_iso_utc(str(arguments["time_max"])).isoformat()
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        calendar_id = arguments.get("calendar_id") or "primary"
        attendees = arguments.get("attendees") or []
        try:
            service = _get_service()
            response = (
                service.freebusy()
                .query(
                    body={
                        "timeMin": time_min,
                        "timeMax": time_max,
                        "items": [{"id": calendar_id}],
                    }
                )
                .execute()
            )
        except Exception as e:
            logger.warning("calendar_check_availability failed: %s", type(e).__name__)
            return {"status": "error", "message": f"Calendar API error: {e}"}
        calendars = response.get("calendars", {})
        busy = calendars.get(calendar_id, {}).get("busy", [])
        return _availability_payload(
            free=not busy, busy=busy, attendees=attendees
        )
    if name == "calendar_update_event":
        if not arguments.get("event_id"):
            return {"status": "error", "message": "event_id is required"}
        patch: dict[str, Any] = {}
        if arguments.get("summary"):
            patch["summary"] = arguments["summary"]
        if arguments.get("status"):
            patch["status"] = arguments["status"]
        for key, field in (("start", "start"), ("end", "end")):
            if arguments.get(key):
                try:
                    patch[field] = {
                        "dateTime": parse_iso_utc(str(arguments[key])).isoformat(),
                        "timeZone": "UTC",
                    }
                except ValueError as e:
                    return {"status": "error", "message": str(e)}
        if not patch:
            return {"status": "error", "message": "nothing to update"}
        calendar_id = arguments.get("calendar_id") or "primary"
        try:
            service = _get_service()
            updated = (
                service.events()
                .patch(calendarId=calendar_id, eventId=arguments["event_id"], body=patch)
                .execute()
            )
        except Exception as e:
            logger.warning("calendar_update_event failed: %s", type(e).__name__)
            return {"status": "error", "message": f"Calendar API error: {e}"}
        return {"status": "ok", "event": _event_to_payload(updated)}
    return {"status": "error", "message": f"Unknown tool: {name}"}


CALENDAR_TOOL_DEFS: list[Tool] = [
    Tool(
        name="calendar_list_events",
        description="List calendar events for a time range",
        inputSchema={
            "type": "object",
            "properties": {
                "time_min": {"type": "string"},
                "time_max": {"type": "string"},
                "calendar_id": {"type": "string", "default": "primary"},
                "max_results": {"type": "integer", "default": 25},
            },
            "required": ["time_min", "time_max"],
        },
    ),
    Tool(
        name="calendar_create_event",
        description="Create a calendar event (mutating)",
        inputSchema={
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "start": {"type": "string"},
                "end": {"type": "string"},
                "attendees": {"type": "array", "items": {"type": "string"}},
                "description": {"type": "string"},
                "calendar_id": {"type": "string", "default": "primary"},
            },
            "required": ["summary", "start", "end"],
        },
    ),
    Tool(
        name="calendar_check_availability",
        description="Check free/busy for a time range",
        inputSchema={
            "type": "object",
            "properties": {
                "time_min": {"type": "string"},
                "time_max": {"type": "string"},
                "attendees": {"type": "array", "items": {"type": "string"}},
                "calendar_id": {"type": "string", "default": "primary"},
            },
            "required": ["time_min", "time_max"],
        },
    ),
    Tool(
        name="calendar_update_event",
        description="Update a calendar event (mutating)",
        inputSchema={
            "type": "object",
            "properties": {
                "event_id": {"type": "string"},
                "summary": {"type": "string"},
                "start": {"type": "string"},
                "end": {"type": "string"},
                "status": {"type": "string"},
                "calendar_id": {"type": "string", "default": "primary"},
            },
            "required": ["event_id"],
        },
    ),
]

CALENDAR_TOOL_NAMES = [t.name for t in CALENDAR_TOOL_DEFS]


async def list_calendar_tools() -> list[Tool]:
    """Return the Calendar tool definitions."""
    return CALENDAR_TOOL_DEFS


async def call_calendar_tool(
    name: str, arguments: dict[str, Any]
) -> list[TextContent]:
    """Execute one Calendar tool and wrap the payload."""
    try:
        payload = handle_calendar_tool(name, arguments or {})
    except Exception as e:
        logger.warning("calendar tool %s failed: %s", name, type(e).__name__)
        payload = {"status": "error", "message": str(e)}
    return [TextContent(type="text", text=json.dumps(payload))]


class CalendarMCPServer:
    """Local Calendar MCP server speaking MCP over STDIO."""

    def __init__(self) -> None:
        self.server = Server("calendar-mcp")
        self.server.list_tools()(list_calendar_tools)
        self.server.call_tool()(call_calendar_tool)

    async def run(self) -> None:
        """Run the server over STDIO."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


async def main() -> None:
    """Entry point for the local Calendar MCP server."""
    server = CalendarMCPServer()
    await server.run()


if __name__ == "__main__":  # pragma: no cover
    import asyncio

    asyncio.run(main())
