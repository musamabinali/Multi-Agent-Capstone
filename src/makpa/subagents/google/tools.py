"""Google tool catalog for MAKPA Phase 3.

LangChain ``@tool`` wrappers over the dual-path Google MCP client with
strict Pydantic schemas, ISO 8601 timestamp validation, email
validation, and normalized payloads. Mutating tools carry
``requires_confirmation=True``; drafts are safe and need no gate.
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.tools import tool
from pydantic import BaseModel, Field, field_validator

from makpa.google.client import CALENDAR_SERVER, GMAIL_SERVER, get_google_client

logger = logging.getLogger(__name__)

#: Tools that mutate shared Google state and require interrupt() confirmation.
MUTATING_TOOLS: frozenset[str] = frozenset(
    {
        "calendar_create_event",
        "calendar_update_event",
        "gmail_send_message",
    }
)


def _mark(tool_obj: Any, *, mutating: bool) -> Any:
    existing = dict(tool_obj.metadata) if tool_obj.metadata else {}
    existing["requires_confirmation"] = mutating
    tool_obj.metadata = existing
    return tool_obj


def validate_iso(value: str, field: str = "timestamp") -> str:
    """Validate an ISO 8601 timestamp (UTC assumed when naive)."""
    from makpa.mcp_servers.google_calendar.server import parse_iso_utc

    try:
        parse_iso_utc(value)
    except ValueError as e:
        raise ValueError(f"Invalid {field}: {e}") from e
    return value


def validate_email_list(values: list[str] | None, field: str = "to") -> list[str]:
    """Validate a recipient list (empty allowed; malformed rejected)."""
    from makpa.mcp_servers.google_gmail.server import validate_recipients

    if not values:
        return []
    try:
        checked: list[str] = validate_recipients(values, field=field)
    except ValueError as e:
        raise ValueError(str(e)) from e
    return checked
    return checked


def _coerce_str_list(value: Any) -> Any:
    """Wrap a bare string in a list (planners often emit one bare address)."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    return value


class ListEventsArgs(BaseModel):  # type: ignore[misc]
    """Arguments for listing Calendar events."""

    time_min: str = Field(description="Range start (ISO 8601)")
    time_max: str = Field(description="Range end (ISO 8601)")
    calendar_id: str = Field(default="primary")
    max_results: int = Field(default=25, ge=1, le=250)


class CreateEventArgs(BaseModel):  # type: ignore[misc]
    """Arguments for creating a Calendar event (mutating)."""

    summary: str = Field(min_length=1)
    start: str = Field(description="Start (ISO 8601)")
    end: str = Field(description="End (ISO 8601)")
    attendees: list[str] = Field(default_factory=list)
    description: str = Field(default="")
    calendar_id: str = Field(default="primary")

    @field_validator("attendees", mode="before")  # type: ignore[untyped-decorator]
    @classmethod
    def _coerce_attendees(cls, v: Any) -> Any:
        return _coerce_str_list(v)


class CheckAvailabilityArgs(BaseModel):  # type: ignore[misc]
    """Arguments for free/busy checks."""

    time_min: str = Field(description="Range start (ISO 8601)")
    time_max: str = Field(description="Range end (ISO 8601)")
    attendees: list[str] = Field(default_factory=list)
    calendar_id: str = Field(default="primary")

    @field_validator("attendees", mode="before")  # type: ignore[untyped-decorator]
    @classmethod
    def _coerce_attendees(cls, v: Any) -> Any:
        return _coerce_str_list(v)


class UpdateEventArgs(BaseModel):  # type: ignore[misc]
    """Arguments for updating a Calendar event (mutating)."""

    event_id: str = Field(min_length=1)
    summary: str = Field(default="")
    start: str = Field(default="")
    end: str = Field(default="")
    status: str = Field(default="", description="e.g. cancelled (rollback)")
    calendar_id: str = Field(default="primary")


class SearchMessagesArgs(BaseModel):  # type: ignore[misc]
    """Arguments for Gmail search."""

    query: str = Field(min_length=1)
    max_results: int = Field(default=10, ge=1, le=100)


class ReadMessageArgs(BaseModel):  # type: ignore[misc]
    """Arguments for reading a Gmail message."""

    message_id: str = Field(min_length=1)


class DraftMessageArgs(BaseModel):  # type: ignore[misc]
    """Arguments for drafting (safe, no gate)."""

    to: list[str] = Field(min_length=1)
    subject: str = Field(min_length=1)
    body: str = Field(default="")
    cc: list[str] = Field(default_factory=list)
    bcc: list[str] = Field(default_factory=list)

    @field_validator("to", "cc", "bcc", mode="before")  # type: ignore[untyped-decorator]
    @classmethod
    def _coerce_recipients(cls, v: Any) -> Any:
        return _coerce_str_list(v)


class SendMessageArgs(BaseModel):  # type: ignore[misc]
    """Arguments for sending (mutating)."""

    to: list[str] = Field(min_length=1)
    subject: str = Field(min_length=1)
    body: str = Field(default="")
    cc: list[str] = Field(default_factory=list)
    bcc: list[str] = Field(default_factory=list)
    draft_id: str = Field(default="")

    @field_validator("to", "cc", "bcc", mode="before")  # type: ignore[untyped-decorator]
    @classmethod
    def _coerce_recipients(cls, v: Any) -> Any:
        return _coerce_str_list(v)


@tool("calendar_list_events", args_schema=ListEventsArgs)  # type: ignore[untyped-decorator]
def calendar_list_events(
    time_min: str, time_max: str, calendar_id: str = "primary", max_results: int = 25
) -> dict[str, Any]:
    """List Calendar events for a time range."""
    validate_iso(time_min, "time_min")
    validate_iso(time_max, "time_max")
    client = get_google_client()
    payload: dict[str, Any] = client.call_tool(
        CALENDAR_SERVER,
        "calendar_list_events",
        {
            "time_min": time_min,
            "time_max": time_max,
            "calendar_id": calendar_id,
            "max_results": max_results,
        },
    )
    return payload


@tool("calendar_create_event", args_schema=CreateEventArgs)  # type: ignore[untyped-decorator]
def calendar_create_event(
    summary: str,
    start: str,
    end: str,
    attendees: list[str] | None = None,
    description: str = "",
    calendar_id: str = "primary",
) -> dict[str, Any]:
    """Create a Calendar event. MUTATING: requires human confirmation."""
    validate_iso(start, "start")
    validate_iso(end, "end")
    checked = validate_email_list(attendees, field="attendees") if attendees else []
    client = get_google_client()
    payload: dict[str, Any] = client.call_tool(
        CALENDAR_SERVER,
        "calendar_create_event",
        {"summary": summary, "start": start, "end": end, "attendees": checked,
         "description": description, "calendar_id": calendar_id},
    )
    return payload


@tool("calendar_check_availability", args_schema=CheckAvailabilityArgs)  # type: ignore[untyped-decorator]
def calendar_check_availability(
    time_min: str, time_max: str, attendees: list[str] | None = None, calendar_id: str = "primary"
) -> dict[str, Any]:
    """Check free/busy for a time range."""
    validate_iso(time_min, "time_min")
    validate_iso(time_max, "time_max")
    checked = validate_email_list(attendees, field="attendees") if attendees else []
    client = get_google_client()
    payload: dict[str, Any] = client.call_tool(
        CALENDAR_SERVER,
        "calendar_check_availability",
        {
            "time_min": time_min,
            "time_max": time_max,
            "attendees": checked,
            "calendar_id": calendar_id,
        },
    )
    return payload


@tool("calendar_update_event", args_schema=UpdateEventArgs)  # type: ignore[untyped-decorator]
def calendar_update_event(
    event_id: str,
    summary: str = "",
    start: str = "",
    end: str = "",
    status: str = "",
    calendar_id: str = "primary",
) -> dict[str, Any]:
    """Update a Calendar event. MUTATING: requires human confirmation."""
    args: dict[str, Any] = {"event_id": event_id, "calendar_id": calendar_id}
    if summary:
        args["summary"] = summary
    if start:
        args["start"] = validate_iso(start, "start")
    if end:
        args["end"] = validate_iso(end, "end")
    if status:
        args["status"] = status
    client = get_google_client()
    payload: dict[str, Any] = client.call_tool(
        CALENDAR_SERVER, "calendar_update_event", args
    )
    return payload


@tool("gmail_search_messages", args_schema=SearchMessagesArgs)  # type: ignore[untyped-decorator]
def gmail_search_messages(query: str, max_results: int = 10) -> dict[str, Any]:
    """Search Gmail messages."""
    client = get_google_client()
    payload: dict[str, Any] = client.call_tool(
        GMAIL_SERVER, "gmail_search_messages", {"query": query, "max_results": max_results}
    )
    return payload


@tool("gmail_read_message", args_schema=ReadMessageArgs)  # type: ignore[untyped-decorator]
def gmail_read_message(message_id: str) -> dict[str, Any]:
    """Read a Gmail message by id."""
    client = get_google_client()
    payload: dict[str, Any] = client.call_tool(
        GMAIL_SERVER, "gmail_read_message", {"message_id": message_id}
    )
    return payload


@tool("gmail_draft_message", args_schema=DraftMessageArgs)  # type: ignore[untyped-decorator]
def gmail_draft_message(
    to: list[str],
    subject: str,
    body: str = "",
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
) -> dict[str, Any]:
    """Create a Gmail draft. Safe: no confirmation gate."""
    checked_to = validate_email_list(to, field="to")
    checked_cc = validate_email_list(cc, field="cc") if cc else []
    checked_bcc = validate_email_list(bcc, field="bcc") if bcc else []
    client = get_google_client()
    payload: dict[str, Any] = client.call_tool(
        GMAIL_SERVER,
        "gmail_draft_message",
        {"to": checked_to, "subject": subject, "body": body, "cc": checked_cc, "bcc": checked_bcc},
    )
    return payload


@tool("gmail_send_message", args_schema=SendMessageArgs)  # type: ignore[untyped-decorator]
def gmail_send_message(
    to: list[str],
    subject: str,
    body: str = "",
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    draft_id: str = "",
) -> dict[str, Any]:
    """Send an email. MUTATING: requires human confirmation."""
    checked_to = validate_email_list(to, field="to")
    checked_cc = validate_email_list(cc, field="cc") if cc else []
    checked_bcc = validate_email_list(bcc, field="bcc") if bcc else []
    args: dict[str, Any] = {
        "to": checked_to, "subject": subject, "body": body,
        "cc": checked_cc, "bcc": checked_bcc,
    }
    if draft_id:
        args["draft_id"] = draft_id
    client = get_google_client()
    payload: dict[str, Any] = client.call_tool(GMAIL_SERVER, "gmail_send_message", args)
    return payload


GOOGLE_TOOLS = [
    calendar_list_events,
    calendar_create_event,
    calendar_check_availability,
    calendar_update_event,
    gmail_search_messages,
    gmail_read_message,
    gmail_draft_message,
    gmail_send_message,
]

for _t in GOOGLE_TOOLS:
    _mark(_t, mutating=_t.name in MUTATING_TOOLS)

__all__ = [
    "GOOGLE_TOOLS",
    "MUTATING_TOOLS",
    "calendar_check_availability",
    "calendar_create_event",
    "calendar_list_events",
    "calendar_update_event",
    "gmail_draft_message",
    "gmail_read_message",
    "gmail_search_messages",
    "gmail_send_message",
    "validate_email_list",
    "validate_iso",
]
