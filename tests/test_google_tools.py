"""Phase 3: Google tool catalog tests (validation, shape, flags)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


def _fake_client():
    fake = MagicMock()
    fake.call_tool.return_value = {"status": "ok"}
    return fake


def test_validate_iso_and_emails():
    from makpa.subagents.google.tools import validate_email_list, validate_iso

    assert validate_iso("2026-10-01T09:00:00Z") == "2026-10-01T09:00:00Z"
    with pytest.raises(ValueError, match="Invalid"):
        validate_iso("bogus")
    assert validate_email_list(["a@x.com"]) == ["a@x.com"]
    assert validate_email_list(None) == []
    assert validate_email_list([]) == []
    with pytest.raises(ValueError, match="Invalid email"):
        validate_email_list(["bad-addr"])


def test_all_tools_call_client():
    from makpa.subagents.google import tools as tools_mod

    by_name = {t.name: t for t in tools_mod.GOOGLE_TOOLS}
    assert len(by_name) == 8
    cases = [
        (
            "calendar_list_events",
            {"time_min": "2026-10-01T00:00:00Z", "time_max": "2026-10-02T00:00:00Z"},
        ),
        (
            "calendar_create_event",
            {"summary": "S", "start": "2026-10-02T15:00:00Z", "end": "2026-10-02T16:00:00Z"},
        ),
        (
            "calendar_check_availability",
            {"time_min": "2026-10-01T00:00:00Z", "time_max": "2026-10-02T00:00:00Z"},
        ),
        ("calendar_update_event", {"event_id": "evt-1"}),
        ("gmail_search_messages", {"query": "standup"}),
        ("gmail_read_message", {"message_id": "msg-1"}),
        ("gmail_draft_message", {"to": ["a@x.com"], "subject": "Hi"}),
        ("gmail_send_message", {"to": ["a@x.com"], "subject": "Hi"}),
    ]
    for name, args in cases:
        fake = _fake_client()
        with patch.object(tools_mod, "get_google_client", return_value=fake):
            out = by_name[name].invoke(args)
        assert out == {"status": "ok"}
        assert fake.call_tool.call_count == 1
        assert fake.call_tool.call_args[0][1] == name


def test_tools_reject_bad_inputs():
    from makpa.subagents.google import tools as tools_mod

    by_name = {t.name: t for t in tools_mod.GOOGLE_TOOLS}
    with pytest.raises(Exception, match="Invalid"):
        by_name["calendar_list_events"].invoke(
            {"time_min": "bogus", "time_max": "2026-10-02T00:00:00Z"}
        )
    with pytest.raises(Exception, match="Invalid email"):
        by_name["gmail_send_message"].invoke({"to": ["bad"], "subject": "Hi"})
    with pytest.raises(Exception, match="Invalid email"):
        by_name["calendar_create_event"].invoke(
            {"summary": "S", "start": "2026-10-02T15:00:00Z",
             "end": "2026-10-02T16:00:00Z", "attendees": ["bad"]}
        )


def test_send_with_draft_id_and_update_with_times():
    from makpa.subagents.google import tools as tools_mod

    by_name = {t.name: t for t in tools_mod.GOOGLE_TOOLS}
    fake = _fake_client()
    with patch.object(tools_mod, "get_google_client", return_value=fake):
        by_name["gmail_send_message"].invoke(
            {"to": ["a@x.com"], "subject": "Hi", "draft_id": "d1"}
        )
    assert fake.call_tool.call_args[0][2]["draft_id"] == "d1"
    with patch.object(tools_mod, "get_google_client", return_value=fake):
        by_name["calendar_update_event"].invoke(
            {"event_id": "e", "start": "2026-10-02T15:00:00Z", "end": "2026-10-02T16:00:00Z"}
        )
    sent_args = fake.call_tool.call_args[0][2]
    assert sent_args["start"] == "2026-10-02T15:00:00Z"


def test_requires_confirmation_matrix():
    from makpa.subagents.google.tools import GOOGLE_TOOLS, MUTATING_TOOLS

    assert MUTATING_TOOLS == frozenset(
        {"calendar_create_event", "calendar_update_event", "gmail_send_message"}
    )
    assert "gmail_draft_message" not in MUTATING_TOOLS
    for tool_obj in GOOGLE_TOOLS:
        assert tool_obj.metadata["requires_confirmation"] is (
            tool_obj.name in MUTATING_TOOLS
        )
