"""Email-list coercion tests (planners emit bare strings, schemas want lists)."""

from __future__ import annotations

import pytest


def test_send_schema_coerces_bare_string() -> None:
    from makpa.subagents.google.tools import SendMessageArgs

    args = SendMessageArgs(to="a@x.com", subject="s", body="b")
    assert args.to == ["a@x.com"]
    args2 = SendMessageArgs(to=["a@x.com"], subject="s", cc="c@x.com", bcc=None)
    assert args2.to == ["a@x.com"] and args2.cc == ["c@x.com"] and args2.bcc == []
    with pytest.raises(Exception):
        SendMessageArgs(to="", subject="s")


def test_draft_schema_coerces_bare_string() -> None:
    from makpa.subagents.google.tools import DraftMessageArgs

    args = DraftMessageArgs(to="a@x.com", subject="s")
    assert args.to == ["a@x.com"]


def test_calendar_attendee_schemas_coerce() -> None:
    from makpa.subagents.google.tools import CheckAvailabilityArgs, CreateEventArgs

    assert CreateEventArgs(summary="s", start="2026-01-01T00:00:00Z",
                           end="2026-01-01T01:00:00Z",
                           attendees="a@x.com").attendees == ["a@x.com"]
    assert CheckAvailabilityArgs(time_min="2026-01-01T00:00:00Z",
                                 time_max="2026-01-01T01:00:00Z",
                                 attendees="a@x.com").attendees == ["a@x.com"]


def test_create_event_accepts_paraphrased_fields() -> None:
    from makpa.subagents.google.tools import CreateEventArgs

    args = CreateEventArgs(
        title="Project Sync",
        start_time="2026-10-05T14:00:00+05:00",
        end_time="2026-10-05T14:30:00+05:00",
        attendees="a@x.com",
    )
    assert args.summary == "Project Sync"
    assert args.start == "2026-10-05T14:00:00+05:00"
    assert args.end == "2026-10-05T14:30:00+05:00"
    assert args.attendees == ["a@x.com"]
    # Canonical names keep working.
    canon = CreateEventArgs(summary="s", start="a", end="b")
    assert (canon.summary, canon.start, canon.end) == ("s", "a", "b")


def test_create_event_tool_accepts_paraphrased_args() -> None:
    from unittest.mock import MagicMock, patch

    from makpa.subagents.google.tools import calendar_create_event

    client = MagicMock()
    client.call_tool.return_value = {"status": "ok", "event": {"id": "e1"}}
    with patch(
        "makpa.subagents.google.tools.get_google_client", return_value=client
    ):
        out = calendar_create_event.invoke(
            {
                "title": "Project Sync",
                "start_time": "2026-10-05T14:00:00+05:00",
                "end_time": "2026-10-05T14:30:00+05:00",
                "attendees": ["musamabinali@gmail.com"],
            }
        )
    assert out["status"] == "ok"
    sent = client.call_tool.call_args[0][2]
    assert sent["summary"] == "Project Sync"
    assert sent["start"] == "2026-10-05T14:00:00+05:00"


def test_send_tool_accepts_bare_string_recipient() -> None:
    from unittest.mock import MagicMock, patch

    from makpa.subagents.google.tools import gmail_send_message

    client = MagicMock()
    client.call_tool.return_value = {"status": "ok", "id": "m123"}
    with patch(
        "makpa.subagents.google.tools.get_google_client", return_value=client
    ):
        out = gmail_send_message.invoke(
            {"to": "musamabinali@gmail.com", "subject": "s", "body": "b"}
        )
    assert out["status"] == "ok"
    sent = client.call_tool.call_args[0][2]
    assert sent["to"] == ["musamabinali@gmail.com"]


def test_draft_tool_accepts_bare_string_recipient() -> None:
    from unittest.mock import MagicMock, patch

    from makpa.subagents.google.tools import gmail_draft_message

    client = MagicMock()
    client.call_tool.return_value = {"status": "ok", "draft": {"id": "d1"}}
    with patch(
        "makpa.subagents.google.tools.get_google_client", return_value=client
    ):
        out = gmail_draft_message.invoke({"to": "a@x.com", "subject": "s"})
    assert out["status"] == "ok"
    assert client.call_tool.call_args[0][2]["to"] == ["a@x.com"]
