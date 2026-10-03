"""Phase 3: Calendar MCP tests (mock STDIO contract + real handler units)."""

from __future__ import annotations

import asyncio
import json
from unittest.mock import MagicMock, patch

from tests.stdio_helpers import stdio_call, stdio_tools_list

MOCK_MODULE = "makpa.mcp_servers.google_calendar.mock"
WINDOW = {
    "time_min": "2026-10-01T00:00:00Z",
    "time_max": "2026-10-02T00:00:00Z",
}


def test_mock_calendar_lists_four_tools():
    assert asyncio.run(stdio_tools_list(MOCK_MODULE)) == [
        "calendar_list_events",
        "calendar_create_event",
        "calendar_check_availability",
        "calendar_update_event",
    ]


def test_mock_calendar_calls_every_tool():
    list_out = asyncio.run(stdio_call(MOCK_MODULE, "calendar_list_events", WINDOW))
    assert list_out["status"] == "ok"
    out = asyncio.run(
        stdio_call(
            MOCK_MODULE,
            "calendar_create_event",
            {
                "summary": "T",
                "start": "2026-10-02T15:00:00Z",
                "end": "2026-10-02T16:00:00Z",
            },
        )
    )
    assert out["event"]["id"] == "evt-mock-100"
    out = asyncio.run(stdio_call(MOCK_MODULE, "calendar_check_availability", WINDOW))
    assert out["status"] == "ok" and "free" in out
    out = asyncio.run(
        stdio_call(MOCK_MODULE, "calendar_update_event", {"event_id": "evt-001"})
    )
    assert out["event"]["id"] == "evt-001"


def test_mock_calendar_error_shapes():
    assert asyncio.run(stdio_call(MOCK_MODULE, "nope", {}))["status"] == "error"
    empty_out = asyncio.run(stdio_call(MOCK_MODULE, "calendar_list_events", {}))
    assert empty_out["status"] == "protocol_error"
    out = asyncio.run(
        stdio_call(
            MOCK_MODULE,
            "calendar_create_event",
            {
                "summary": "T",
                "start": "2026-10-02T16:00:00Z",
                "end": "2026-10-02T15:00:00Z",
            },
        )
    )
    assert out["status"] == "error"
    out = asyncio.run(
        stdio_call(MOCK_MODULE, "calendar_update_event", {"event_id": "evt-nope"})
    )
    assert "not found" in out["message"]
    out = asyncio.run(
        stdio_call(
            MOCK_MODULE,
            "calendar_list_events",
            {"time_min": "bogus", "time_max": "bogus"},
        )
    )
    assert out["status"] == "error"


def _fake_service():
    service = MagicMock()
    service.events.return_value.list.return_value.execute.return_value = {
        "items": [
            {"id": "e1", "summary": "S",
             "start": {"dateTime": "2026-10-01T09:00:00+00:00"},
             "end": {"dateTime": "2026-10-01T10:00:00+00:00"},
             "attendees": [{"email": "a@x.com"}], "htmlLink": "http://x", "status": "confirmed"}
        ]
    }
    service.events.return_value.insert.return_value.execute.return_value = {
        "id": "e9", "summary": "N", "start": {"date": "2026-10-03"},
        "end": {"date": "2026-10-03"}, "status": "confirmed",
    }
    service.events.return_value.patch.return_value.execute.return_value = {
        "id": "e1", "summary": "Updated", "start": {}, "end": {}, "status": "confirmed"
    }
    service.freebusy.return_value.query.return_value.execute.return_value = {
        "calendars": {"primary": {"busy": [{"start": "x", "end": "y"}]}}
    }
    return service


def test_real_calendar_handler_units():
    from makpa.mcp_servers.google_calendar import server as srv

    assert [t.name for t in asyncio.run(srv.list_calendar_tools())] == srv.CALENDAR_TOOL_NAMES
    out = asyncio.run(srv.call_calendar_tool("nope", {}))
    assert json.loads(out[0].text)["status"] == "error"

    with patch.object(srv, "handle_calendar_tool", side_effect=RuntimeError("boom")):
        out = asyncio.run(srv.call_calendar_tool("calendar_list_events", WINDOW))
    assert "boom" in json.loads(out[0].text)["message"]

    service = _fake_service()
    with patch.object(srv, "_get_service", return_value=service):
        out = srv.handle_calendar_tool("calendar_list_events", dict(WINDOW))
        assert out["count"] == 1 and out["events"][0]["attendees"] == ["a@x.com"]
        out = srv.handle_calendar_tool(
            "calendar_create_event",
            {"summary": "S", "start": "2026-10-02T15:00:00Z",
             "end": "2026-10-02T16:00:00Z", "attendees": ["a@x.com"], "description": "d"},
        )
        assert out["event"]["start"] == "2026-10-03"
        out = srv.handle_calendar_tool("calendar_check_availability", dict(WINDOW))
        assert out["free"] is False and out["busy"] == [{"start": "x", "end": "y"}]
        out = srv.handle_calendar_tool(
            "calendar_update_event", {"event_id": "e1", "summary": "Updated"}
        )
        assert out["event"]["summary"] == "Updated"

    with patch.object(srv, "_get_service", side_effect=RuntimeError("auth down")):
        out = srv.handle_calendar_tool("calendar_list_events", dict(WINDOW))
        assert "Calendar API error" in out["message"]

    # Validation branches without touching the API.
    assert srv.handle_calendar_tool("calendar_list_events", {})["status"] == "error"
    bad_time = dict(WINDOW, time_min="bogus")
    assert srv.handle_calendar_tool("calendar_list_events", bad_time)["status"] == "error"
    assert srv.handle_calendar_tool("calendar_create_event", {})["status"] == "error"
    flipped = {"summary": "S", "start": "2026-10-02T16:00:00Z", "end": "2026-10-02T15:00:00Z"}
    assert srv.handle_calendar_tool("calendar_create_event", flipped)["status"] == "error"
    assert srv.handle_calendar_tool("calendar_check_availability", {})["status"] == "error"
    assert srv.handle_calendar_tool("calendar_update_event", {})["status"] == "error"
    assert srv.handle_calendar_tool("calendar_update_event", {"event_id": "e"})["status"] == "error"
    bad_patch = {"event_id": "e", "start": "bogus"}
    assert srv.handle_calendar_tool("calendar_update_event", bad_patch)["status"] == "error"

    # parse_iso_utc branches.
    assert srv.parse_iso_utc("2026-10-01").tzinfo is not None
    try:
        srv.parse_iso_utc("not-a-time")
        raised = False
    except ValueError:
        raised = True
    assert raised

    # Server wiring + main entry.
    srv.CalendarMCPServer()
    with patch.object(srv, "CalendarMCPServer") as cls:
        from unittest.mock import AsyncMock

        cls.return_value.run = AsyncMock()
        asyncio.run(srv.main())
    cls.return_value.run.assert_awaited_once()
