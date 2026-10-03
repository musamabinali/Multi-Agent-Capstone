"""Local Google Calendar MCP server package (real Calendar v3 wrapper)."""

from .mock import MOCK_EVENTS, MockCalendarMCPServer, handle_mock_calendar_tool
from .server import (
    CALENDAR_TOOL_DEFS,
    CALENDAR_TOOL_NAMES,
    CalendarMCPServer,
    attendee_mode,
    call_calendar_tool,
    handle_calendar_tool,
    list_calendar_tools,
    main,
    parse_iso_utc,
)

__all__ = [
    "CALENDAR_TOOL_DEFS",
    "CALENDAR_TOOL_NAMES",
    "MOCK_EVENTS",
    "CalendarMCPServer",
    "MockCalendarMCPServer",
    "attendee_mode",
    "call_calendar_tool",
    "handle_calendar_tool",
    "handle_mock_calendar_tool",
    "list_calendar_tools",
    "main",
    "parse_iso_utc",
]
