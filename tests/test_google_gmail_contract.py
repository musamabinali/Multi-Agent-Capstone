"""Phase 3: Gmail MCP tests (mock STDIO contract + real handler units)."""

from __future__ import annotations

import asyncio
import base64
import json
from unittest.mock import AsyncMock, MagicMock, patch

from tests.stdio_helpers import stdio_call, stdio_tools_list

MOCK_MODULE = "makpa.mcp_servers.google_gmail.mock"


def test_mock_gmail_lists_four_tools():
    assert asyncio.run(stdio_tools_list(MOCK_MODULE)) == [
        "gmail_search_messages",
        "gmail_read_message",
        "gmail_draft_message",
        "gmail_send_message",
    ]


def test_mock_gmail_calls_every_tool():
    out = asyncio.run(
        stdio_call(MOCK_MODULE, "gmail_search_messages", {"query": "standup"})
    )
    assert out["count"] == 1 and out["messages"][0]["id"] == "msg-001"
    out = asyncio.run(
        stdio_call(MOCK_MODULE, "gmail_read_message", {"message_id": "msg-001"})
    )
    assert out["message"]["subject"] == "Standup notes"
    out = asyncio.run(
        stdio_call(
            MOCK_MODULE, "gmail_draft_message", {"to": ["a@x.com"], "subject": "Hi"}
        )
    )
    assert out["draft"]["id"] == "draft-mock-100"
    out = asyncio.run(
        stdio_call(
            MOCK_MODULE,
            "gmail_send_message",
            {"to": ["a@x.com"], "subject": "Hi", "draft_id": "draft-mock-100"},
        )
    )
    assert out["sent"]["id"] == "msg-from-draft-mock-100"


def test_mock_gmail_error_shapes():
    assert asyncio.run(stdio_call(MOCK_MODULE, "nope", {}))["status"] == "error"
    empty_out = asyncio.run(stdio_call(MOCK_MODULE, "gmail_search_messages", {}))
    assert empty_out["status"] == "protocol_error"
    out = asyncio.run(
        stdio_call(MOCK_MODULE, "gmail_read_message", {"message_id": "msg-nope"})
    )
    assert "not found" in out["message"]
    out = asyncio.run(
        stdio_call(
            MOCK_MODULE, "gmail_draft_message", {"to": ["bad-addr"], "subject": "Hi"}
        )
    )
    assert out["status"] == "error"


def _fake_service():
    service = MagicMock()
    users = service.users.return_value
    users.messages.return_value.list.return_value.execute.return_value = {
        "messages": [{"id": "m1", "threadId": "t1", "labelIds": ["INBOX"], "snippet": "hi"}]
    }
    users.messages.return_value.get.return_value.execute.return_value = {
        "id": "m1", "threadId": "t1", "labelIds": ["INBOX"], "snippet": "hi",
        "payload": {"headers": [
            {"name": "Subject", "value": "Hello"},
            {"name": "From", "value": "a@x.com"},
        ]},
    }
    users.messages.return_value.send.return_value.execute.return_value = {
        "id": "s1", "threadId": "t1", "labelIds": ["SENT"]
    }
    users.drafts.return_value.create.return_value.execute.return_value = {
        "id": "d1", "message": {"id": "m2"}
    }
    users.drafts.return_value.send.return_value.execute.return_value = {
        "id": "s2", "threadId": "t2", "labelIds": ["SENT"]
    }
    return service


def test_real_gmail_handler_units():
    from makpa.mcp_servers.google_gmail import server as srv

    assert [t.name for t in asyncio.run(srv.list_gmail_tools())] == srv.GMAIL_TOOL_NAMES
    out = asyncio.run(srv.call_gmail_tool("nope", {}))
    assert json.loads(out[0].text)["status"] == "error"
    with patch.object(srv, "handle_gmail_tool", side_effect=RuntimeError("boom")):
        out = asyncio.run(srv.call_gmail_tool("gmail_search_messages", {"query": "q"}))
    assert "boom" in json.loads(out[0].text)["message"]

    service = _fake_service()
    with patch.object(srv, "_get_service", return_value=service):
        out = srv.handle_gmail_tool("gmail_search_messages", {"query": "q"})
        assert out["count"] == 1
        out = srv.handle_gmail_tool("gmail_read_message", {"message_id": "m1"})
        assert out["message"]["subject"] == "Hello"
        out = srv.handle_gmail_tool(
            "gmail_draft_message",
            {"to": ["a@x.com"], "subject": "Hi", "body": "b", "cc": ["c@x.com"]},
        )
        assert out["draft"]["id"] == "d1"
        out = srv.handle_gmail_tool(
            "gmail_send_message", {"to": ["a@x.com"], "subject": "Hi"}
        )
        assert out["sent"]["id"] == "s1"
        out = srv.handle_gmail_tool(
            "gmail_send_message",
            {"to": ["a@x.com"], "subject": "Hi", "draft_id": "d1"},
        )
        assert out["sent"]["id"] == "s2"

    with patch.object(srv, "_get_service", side_effect=RuntimeError("auth down")):
        search_err = srv.handle_gmail_tool("gmail_search_messages", {"query": "q"})
        assert "Gmail API error" in search_err["message"]
        read_err = srv.handle_gmail_tool("gmail_read_message", {"message_id": "m"})
        assert "Gmail API error" in read_err["message"]
        draft_err = srv.handle_gmail_tool(
            "gmail_draft_message", {"to": ["a@x.com"], "subject": "s"}
        )
        assert "Gmail API error" in draft_err["message"]
        send_err = srv.handle_gmail_tool(
            "gmail_send_message", {"to": ["a@x.com"], "subject": "s"}
        )
        assert "Gmail API error" in send_err["message"]

    # Validation branches.
    assert srv.handle_gmail_tool("gmail_search_messages", {})["status"] == "error"
    assert srv.handle_gmail_tool("gmail_read_message", {})["status"] == "error"
    no_recip = srv.handle_gmail_tool("gmail_draft_message", {"to": [], "subject": "s"})
    assert no_recip["status"] == "error"
    no_subj = srv.handle_gmail_tool("gmail_draft_message", {"to": ["a@x.com"]})
    assert no_subj["status"] == "error"
    bad_recip = srv.handle_gmail_tool("gmail_send_message", {"to": ["bad"], "subject": "s"})
    assert bad_recip["status"] == "error"

    # Recipients + RFC2822 branches.
    try:
        srv.validate_recipients([], field="to")
        raised = False
    except ValueError:
        raised = True
    assert raised
    try:
        srv.validate_recipients(["bad-addr"], field="cc")
        raised = False
    except ValueError:
        raised = True
    assert raised
    raw = srv.build_rfc2822(["a@x.com"], "Hi", "bod", ["c@x.com"], ["b@x.com"])
    decoded = base64.urlsafe_b64decode(raw.encode()).decode()
    assert "a@x.com" in decoded and "Hi" in decoded

    srv.GmailMCPServer()
    with patch.object(srv, "GmailMCPServer") as cls:
        cls.return_value.run = AsyncMock()
        asyncio.run(srv.main())
    cls.return_value.run.assert_awaited_once()
