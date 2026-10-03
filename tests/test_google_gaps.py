"""Phase 3 gap coverage: mock handler units, OAuth edges, CLI reauth, graph leftovers."""

from __future__ import annotations

import asyncio
import json
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from typer.testing import CliRunner

runner = CliRunner()


def _probe_ok():
    return SimpleNamespace(provider="mock", model="mock-canned", warnings=[], message="ok")


# ---------------------------------------------------------------------------
# Mock handler direct units (in-process; STDIO covered by contract tests)
# ---------------------------------------------------------------------------


def test_mock_calendar_handler_units():
    from makpa.mcp_servers.google_calendar import mock as mock_mod

    assert mock_mod.handle_mock_calendar_tool("nope", {})["status"] == "error"
    window = {"time_min": "2026-10-01T00:00:00Z", "time_max": "2026-10-02T00:00:00Z"}
    out = mock_mod.handle_mock_calendar_tool("calendar_list_events", dict(window))
    assert out["count"] == 2
    narrow = {"time_min": "2026-10-01T09:00:00Z", "time_max": "2026-10-01T09:15:00Z"}
    out = mock_mod.handle_mock_calendar_tool("calendar_list_events", narrow)
    assert out["count"] == 1 and out["events"][0]["id"] == "evt-001"
    limited = dict(window, max_results=1)
    assert mock_mod.handle_mock_calendar_tool("calendar_list_events", limited)["count"] == 1
    assert mock_mod.handle_mock_calendar_tool("calendar_list_events", {})["status"] == "error"
    bad = dict(window, time_min="bogus")
    assert mock_mod.handle_mock_calendar_tool("calendar_list_events", bad)["status"] == "error"

    created = mock_mod.handle_mock_calendar_tool(
        "calendar_create_event",
        {"summary": "S", "start": "2026-10-02T15:00:00Z", "end": "2026-10-02T16:00:00Z",
         "attendees": ["a@x.com"]},
    )
    assert created["event"]["id"] == "evt-mock-100"
    assert mock_mod.handle_mock_calendar_tool("calendar_create_event", {})["status"] == "error"
    bad_iso = {"summary": "S", "start": "bogus", "end": "2026-10-02T16:00:00Z"}
    assert mock_mod.handle_mock_calendar_tool("calendar_create_event", bad_iso)["status"] == "error"
    flipped = {"summary": "S", "start": "2026-10-02T16:00:00Z", "end": "2026-10-02T15:00:00Z"}
    assert mock_mod.handle_mock_calendar_tool("calendar_create_event", flipped)["status"] == "error"

    free_window = {"time_min": "2026-10-05T00:00:00Z", "time_max": "2026-10-06T00:00:00Z"}
    free_out = mock_mod.handle_mock_calendar_tool("calendar_check_availability", free_window)
    assert free_out["free"] is True and free_out["busy"] == []
    busy_out = mock_mod.handle_mock_calendar_tool("calendar_check_availability", dict(window))
    assert busy_out["free"] is False and len(busy_out["busy"]) == 2
    empty_avail = mock_mod.handle_mock_calendar_tool("calendar_check_availability", {})
    assert empty_avail["status"] == "error"
    bad_avail = mock_mod.handle_mock_calendar_tool("calendar_check_availability", bad)
    assert bad_avail["status"] == "error"

    updated = mock_mod.handle_mock_calendar_tool(
        "calendar_update_event", {"event_id": "evt-001", "summary": "New"}
    )
    assert updated["event"]["summary"] == "New" and updated["event"]["mock"] is True
    assert mock_mod.handle_mock_calendar_tool("calendar_update_event", {})["status"] == "error"
    missing = mock_mod.handle_mock_calendar_tool("calendar_update_event", {"event_id": "evt-x"})
    assert "not found" in missing["message"]

    mock_mod.MockCalendarMCPServer()
    with patch.object(mock_mod, "MockCalendarMCPServer") as cls:
        cls.return_value.run = AsyncMock()
        asyncio.run(mock_mod.main())
    cls.return_value.run.assert_awaited_once()

    assert asyncio.run(mock_mod._list_tools()) == mock_mod.CALENDAR_TOOL_DEFS
    called = asyncio.run(mock_mod._call_tool("calendar_list_events", dict(window)))
    assert json.loads(called[0].text)["status"] == "ok"
    with patch.object(
        mock_mod, "handle_mock_calendar_tool", side_effect=RuntimeError("boom")
    ):
        called = asyncio.run(mock_mod._call_tool("calendar_list_events", dict(window)))
    assert "boom" in json.loads(called[0].text)["message"]


def test_mock_gmail_handler_units():
    from makpa.mcp_servers.google_gmail import mock as mock_mod

    assert mock_mod.handle_mock_gmail_tool("nope", {})["status"] == "error"
    out = mock_mod.handle_mock_gmail_tool("gmail_search_messages", {"query": "standup"})
    assert out["count"] == 1
    out = mock_mod.handle_mock_gmail_tool("gmail_search_messages", {"query": "zzz-no-match"})
    assert out["count"] == 0
    limited = mock_mod.handle_mock_gmail_tool(
        "gmail_search_messages", {"query": "e", "max_results": 1}
    )
    assert limited["count"] == 1
    assert mock_mod.handle_mock_gmail_tool("gmail_search_messages", {})["status"] == "error"

    out = mock_mod.handle_mock_gmail_tool("gmail_read_message", {"message_id": "msg-002"})
    assert out["message"]["id"] == "msg-002"
    assert mock_mod.handle_mock_gmail_tool("gmail_read_message", {})["status"] == "error"
    missing = mock_mod.handle_mock_gmail_tool("gmail_read_message", {"message_id": "msg-x"})
    assert "not found" in missing["message"]

    out = mock_mod.handle_mock_gmail_tool(
        "gmail_draft_message", {"to": ["a@x.com"], "subject": "Hi"}
    )
    assert out["draft"]["to"] == ["a@x.com"]
    assert mock_mod.handle_mock_gmail_tool("gmail_draft_message", {"to": [], "subject": "Hi"})
    no_subj = mock_mod.handle_mock_gmail_tool("gmail_draft_message", {"to": ["a@x.com"]})
    assert no_subj["status"] == "error"
    bad_to = mock_mod.handle_mock_gmail_tool(
        "gmail_draft_message", {"to": ["bad"], "subject": "Hi"}
    )
    assert bad_to["status"] == "error"

    out = mock_mod.handle_mock_gmail_tool(
        "gmail_send_message", {"to": ["a@x.com"], "subject": "Hi"}
    )
    assert out["sent"]["id"] == "msg-mock-101"
    via_draft = mock_mod.handle_mock_gmail_tool(
        "gmail_send_message", {"to": ["a@x.com"], "subject": "Hi", "draft_id": "d"}
    )
    assert via_draft["sent"]["id"] == "msg-from-draft-mock-100"
    assert mock_mod.handle_mock_gmail_tool(
        "gmail_send_message", {"to": ["a@x.com"]})["status"] == "error"
    assert mock_mod.handle_mock_gmail_tool(
        "gmail_send_message", {"to": ["bad"], "subject": "Hi"})["status"] == "error"

    mock_mod.MockGmailMCPServer()
    with patch.object(mock_mod, "MockGmailMCPServer") as cls:
        cls.return_value.run = AsyncMock()
        asyncio.run(mock_mod.main())
    cls.return_value.run.assert_awaited_once()

    assert asyncio.run(mock_mod._list_tools()) == mock_mod.GMAIL_TOOL_DEFS
    called = asyncio.run(
        mock_mod._call_tool("gmail_search_messages", {"query": "standup"})
    )
    assert json.loads(called[0].text)["status"] == "ok"
    with patch.object(
        mock_mod, "handle_mock_gmail_tool", side_effect=RuntimeError("boom")
    ):
        called = asyncio.run(
            mock_mod._call_tool("gmail_search_messages", {"query": "standup"})
        )
    assert "boom" in json.loads(called[0].text)["message"]


def test_mock_servers_run_over_stubbed_stdio():
    import asyncio

    from makpa.mcp_servers.google_calendar import mock as cal_mock
    from makpa.mcp_servers.google_gmail import mock as gmail_mock

    for mod, cls_name in (
        (cal_mock, "MockCalendarMCPServer"),
        (gmail_mock, "MockGmailMCPServer"),
    ):
        instance = getattr(mod, cls_name)()
        streams = (MagicMock(), MagicMock())
        context = MagicMock()
        context.__aenter__ = AsyncMock(return_value=streams)
        context.__aexit__ = AsyncMock(return_value=False)
        with (
            patch.object(mod, "stdio_server", return_value=context),
            patch.object(instance.server, "run", AsyncMock()) as run_mock,
        ):
            asyncio.run(instance.run())
        run_mock.assert_awaited_once()


def test_cli_is_interrupted_snapshot_true():
    from makpa.cli import google_demo

    snap = SimpleNamespace(next=("confirm_email",), tasks=[])
    graph = MagicMock()
    graph.get_state.return_value = snap
    assert google_demo._is_interrupted(graph, {}, {"status": "ok"}) is True

    from langgraph.types import Interrupt

    assert (
        google_demo._is_interrupted(
            MagicMock(), {}, {"__interrupt__": [Interrupt(value={"gate": 1})]}
        )
        is True
    )


def test_real_service_builders_and_run():
    import asyncio

    from makpa.mcp_servers.google_calendar import server as cal
    from makpa.mcp_servers.google_gmail import server as gmail

    with (
        patch("googleapiclient.discovery.build", return_value="cal-service") as build_mock,
        patch("makpa.google.oauth.get_google_credentials", return_value="creds"),
    ):
        assert cal._get_service() == "cal-service"
    build_mock.assert_called_once()
    with (
        patch("googleapiclient.discovery.build", return_value="gmail-service") as build_mock,
        patch("makpa.google.oauth.get_google_credentials", return_value="creds"),
    ):
        assert gmail._get_service() == "gmail-service"
    build_mock.assert_called_once()

    for mod, cls_name in ((cal, "CalendarMCPServer"), (gmail, "GmailMCPServer")):
        instance = getattr(mod, cls_name)()
        streams = (MagicMock(), MagicMock())
        context = MagicMock()
        context.__aenter__ = AsyncMock(return_value=streams)
        context.__aexit__ = AsyncMock(return_value=False)
        with (
            patch.object(mod, "stdio_server", return_value=context),
            patch.object(instance.server, "run", AsyncMock()) as run_mock,
        ):
            asyncio.run(instance.run())
        run_mock.assert_awaited_once()


def test_real_calendar_api_error_paths():
    from makpa.mcp_servers.google_calendar import server as srv

    bad_iso = {"summary": "S", "start": "bogus", "end": "2026-10-02T16:00:00Z"}
    assert srv.handle_calendar_tool("calendar_create_event", bad_iso)["status"] == "error"
    with patch.object(srv, "_get_service", side_effect=RuntimeError("quota")):
        create = srv.handle_calendar_tool(
            "calendar_create_event",
            {"summary": "S", "start": "2026-10-02T15:00:00Z", "end": "2026-10-02T16:00:00Z"},
        )
        assert "Calendar API error" in create["message"]
        window = {"time_min": "2026-10-01T00:00:00Z", "time_max": "2026-10-02T00:00:00Z"}
        bad_window = dict(window, time_min="bogus")
        bad_avail = srv.handle_calendar_tool("calendar_check_availability", bad_window)
        assert bad_avail["status"] == "error"
        avail = srv.handle_calendar_tool("calendar_check_availability", window)
        assert "Calendar API error" in avail["message"]
        updated = srv.handle_calendar_tool(
            "calendar_update_event", {"event_id": "e1", "summary": "New"}
        )
        assert "Calendar API error" in updated["message"]


def test_real_gmail_send_subject_required():
    from makpa.mcp_servers.google_gmail import server as srv

    out = srv.handle_gmail_tool("gmail_send_message", {"to": ["a@x.com"]})
    assert out["message"] == "subject is required"


# ---------------------------------------------------------------------------
# OAuth edges
# ---------------------------------------------------------------------------


def test_oauth_save_failure_and_chmod_warning(tmp_path):
    from makpa.google import oauth as oauth_mod

    settings = SimpleNamespace(google_token_cache_path=str(tmp_path / "t.json"))
    with patch("makpa.google.oauth.get_settings", return_value=settings):
        with (
            patch("os.fdopen", side_effect=RuntimeError("disk")),
            patch("os.close", side_effect=OSError("already-closed")),
        ):
            try:
                oauth_mod.save_token_cache({"a": 1})
                raised = False
            except RuntimeError:
                raised = True
        assert raised

        with patch("os.chmod", side_effect=OSError("readonly-fs")):
            oauth_mod.save_token_cache({"a": 1})  # warns, does not raise


def test_oauth_validity_and_local_server():
    import socket
    import threading
    import urllib.request

    from makpa.google import oauth as oauth_mod

    assert oauth_mod.access_token_valid({"access_token": "a", "expiry": "never"}) is False

    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    received = {}

    def _serve():
        received["code"] = oauth_mod._receive_code_via_local_server(port, timeout=10)

    thread = threading.Thread(target=_serve, daemon=True)
    thread.start()
    for _ in range(100):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/ping", timeout=2)
            break
        except Exception:
            import time

            time.sleep(0.05)
    urllib.request.urlopen(f"http://127.0.0.1:{port}/callback?code=abc123", timeout=5)
    thread.join(timeout=12)
    assert received.get("code") == "abc123"

    sock2 = socket.socket()
    sock2.bind(("127.0.0.1", 0))
    port2 = sock2.getsockname()[1]
    sock2.close()
    try:
        oauth_mod._receive_code_via_local_server(port2, timeout=1)
        raised = False
    except RuntimeError as e:
        raised = "Timed out" in str(e)
    assert raised


def test_oauth_browser_failure_and_delegate():
    from makpa.google import oauth as oauth_mod

    settings = SimpleNamespace(
        google_client_id="client-123",
        google_client_secret=None,
        google_redirect_uri="http://localhost:8080/callback",
        google_oauth_redirect_port=8080,
        google_oauth_scopes="scope-a",
        google_token_cache_path="/nonexistent/cache.json",
    )
    with (
        patch("makpa.google.oauth.get_settings", return_value=settings),
        patch("webbrowser.open", side_effect=RuntimeError("no browser")),
        patch(
            "makpa.google.oauth._receive_code_via_local_server",
            return_value="code-1",
        ),
        patch(
            "makpa.google.oauth.exchange_code_for_tokens",
            return_value={"access_token": "a", "refresh_token": "r"},
        ),
        patch("makpa.google.oauth.save_token_cache"),
    ):
        cache = oauth_mod.run_browser_flow()
    assert cache["refresh_token"] == "r"

    with patch(
        "makpa.google.oauth.ensure_credentials", return_value="creds-object"
    ):
        assert oauth_mod.get_google_credentials() == "creds-object"


# ---------------------------------------------------------------------------
# CLI reauth / decline / helper edges
# ---------------------------------------------------------------------------


def test_cli_generic_tool_failures():
    from makpa.cli import google_demo

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.subagents.google.tools.calendar_check_availability",
            MagicMock(**{"invoke.side_effect": RuntimeError("down")}),
        ),
    ):
        res = runner.invoke(
            google_demo.app,
            ["check", "--start", "2026-10-01T00:00:00Z", "--end", "2026-10-02T00:00:00Z"],
        )
    assert res.exit_code == 1

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.subagents.google.tools.calendar_create_event",
            MagicMock(**{"invoke.side_effect": RuntimeError("down")}),
        ),
    ):
        res = runner.invoke(
            google_demo.app,
            ["create-event", "--summary", "S", "--start", "2026-10-01T00:00:00Z",
             "--end", "2026-10-02T00:00:00Z", "--yes"],
        )
    assert res.exit_code == 1


def test_cli_reauth_and_warnings():
    from makpa.cli import google_demo
    from makpa.google.oauth import ReauthRequiredError

    warned = SimpleNamespace(
        provider="mock", model="m", warnings=["stale X"], message="ok"
    )
    with (
        patch("makpa.llm.probe_llm", return_value=warned),
        patch(
            "makpa.subagents.google.tools.calendar_list_events",
            MagicMock(**{"invoke.return_value": {"status": "ok", "events": []}}),
        ),
    ):
        res = runner.invoke(google_demo.app, ["list-events"])
    assert res.exit_code == 0 and "stale X" in res.output

    for command, args in (
        ("check", ["--start", "2026-10-01T00:00:00Z", "--end", "2026-10-02T00:00:00Z"]),
        ("create-event", ["--summary", "S", "--start", "2026-10-01T00:00:00Z",
                          "--end", "2026-10-02T00:00:00Z", "--yes"]),
        ("draft", ["--to", "a@x.com", "--subject", "Hi"]),
        ("send", ["--to", "a@x.com", "--subject", "Hi", "--yes"]),
    ):
        tool_map = {
            "check": "makpa.subagents.google.tools.calendar_check_availability",
            "create-event": "makpa.subagents.google.tools.calendar_create_event",
            "draft": "makpa.subagents.google.tools.gmail_draft_message",
            "send": "makpa.subagents.google.tools.gmail_send_message",
        }
        with (
            patch("makpa.llm.probe_llm", return_value=_probe_ok()),
            patch(tool_map[command], MagicMock(
                **{"invoke.side_effect": ReauthRequiredError("http://reauth")})),
        ):
            res = runner.invoke(google_demo.app, [command, *args])
        assert res.exit_code == 3, command

    # Logging setup tolerates raising reconfigure.
    bad = MagicMock()
    bad.reconfigure.side_effect = RuntimeError("nope")
    with (
        patch.object(sys, "stdout", bad),
        patch.object(sys, "stderr", bad),
    ):
        google_demo._setup_logging()

    # Snapshot-true pause detection.
    snap = SimpleNamespace(next=("confirm_event",), tasks=[])
    graph = MagicMock()
    graph.get_state.return_value = snap
    assert google_demo._is_interrupted(graph, {}, {}) is True


def test_cli_ask_decline_and_reauth():
    from makpa.cli import google_demo
    from makpa.google.oauth import ReauthRequiredError

    snap = SimpleNamespace(
        next=("confirm_event",),
        tasks=[SimpleNamespace(interrupts=[SimpleNamespace(value={"gate": 1})])],
    )
    idle = SimpleNamespace(next=(), tasks=[])
    graph = MagicMock()
    graph.get_state.side_effect = [snap, idle]
    graph.invoke.side_effect = [
        {"__interrupt__": [{"gate": 1}], "status": "ok"},
        {"answer": "cancelled at gate 1", "status": "cancelled"},
    ]
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.subagents.google.create_google_graph", return_value=graph),
    ):
        res = runner.invoke(google_demo.app, ["ask", "schedule it"], input="n\n")
    assert res.exit_code == 2 and "cancelled at gate 1" in res.output

    raising = MagicMock()
    raising.invoke.side_effect = ReauthRequiredError("http://reauth")
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.subagents.google.create_google_graph", return_value=raising),
    ):
        res = runner.invoke(google_demo.app, ["ask", "q"])
    assert res.exit_code == 3


# ---------------------------------------------------------------------------
# Graph + tools leftovers
# ---------------------------------------------------------------------------


def test_graph_leftovers():
    from makpa.subagents.google import graph as g

    out = g.heuristic_plan("Update evt-1 from 2026-10-02T15:00:00Z to 2026-10-02T16:00:00Z")
    assert out[1][0]["args"]["end"] == "2026-10-02T16:00:00Z"

    from types import SimpleNamespace as NS

    class _ListLLM:
        def invoke(self, _prompt: str):
            return NS(content="[1, 2, 3]")

    with patch("makpa.llm.get_llm", return_value=_ListLLM()):
        assert g._llm_plan("q") is None

    assert g._run_tool("zzz", {})["status"] == "error"
    plain = MagicMock()
    plain.invoke.return_value = "text-result"
    with patch.dict(g.TOOLS_BY_NAME, {"gmail_draft_message": plain}, clear=False):
        assert g._run_tool("gmail_draft_message", {})["text"] == "text-result"
    boom = MagicMock()
    boom.invoke.side_effect = RuntimeError("down")
    with patch.dict(g.TOOLS_BY_NAME, {"gmail_draft_message": boom}, clear=False):
        assert g._run_tool("gmail_draft_message", {})["status"] == "error"

    state = {
        "question": "schedule a meeting about launch with a@x.com "
                    "from 2026-10-02T15:00:00Z to 2026-10-02T16:00:00Z",
        "payload": {"time_min": "2026-10-02T15:00:00Z", "time_max": "2026-10-02T16:00:00Z",
                    "attendees": ["a@x.com"]},
    }
    out = g.composite_plan_event_node(state)
    assert out["plan"][0]["args"]["summary"] == "launch"


def test_attendee_mode_partial_and_all(monkeypatch):
    from makpa.config import Settings, get_settings
    from makpa.mcp_servers.google_calendar import mock as mock_mod
    from makpa.mcp_servers.google_calendar import server as srv

    assert Settings(google_calendar_attendee_mode="ALL").google_calendar_attendee_mode == "all"
    try:
        Settings(google_calendar_attendee_mode="everyone")
        raised = False
    except Exception:
        raised = True
    assert raised

    window = {"time_min": "2026-10-05T00:00:00Z", "time_max": "2026-10-06T00:00:00Z"}
    # Default own_only: attendees -> partial.
    if hasattr(get_settings, "cache_clear"):
        get_settings.cache_clear()
    try:
        out = mock_mod.handle_mock_calendar_tool(
            "calendar_check_availability", dict(window, attendees=["a@x.com"])
        )
        assert out["partial"] is True and out["attendee_mode"] == "own_only"
        assert "partial" in out["message"].lower()
        bare = mock_mod.handle_mock_calendar_tool("calendar_check_availability", dict(window))
        assert bare["partial"] is False
        assert srv.attendee_mode() == "own_only"
        # all mode: same attendees verified as before.
        monkeypatch.setenv("GOOGLE_CALENDAR_ATTENDEE_MODE", "all")
        if hasattr(get_settings, "cache_clear"):
            get_settings.cache_clear()
        out = mock_mod.handle_mock_calendar_tool(
            "calendar_check_availability", dict(window, attendees=["a@x.com"])
        )
        assert out["partial"] is False and out["attendee_mode"] == "all"
    finally:
        monkeypatch.undo()
        if hasattr(get_settings, "cache_clear"):
            get_settings.cache_clear()


def test_composite_refuses_partial_availability():
    from makpa.subagents.google import graph as g

    partial = {
        "tool": "calendar_check_availability",
        "status": "ok",
        "free": True,
        "busy": [],
        "partial": True,
        "attendees": ["a@x.com"],
    }
    assert g.route_after_check({"tool_results": [partial]}) == "synthesize"
    tiny_llm = SimpleNamespace(invoke=lambda p: SimpleNamespace(content="t"))
    with patch("makpa.llm.get_llm", return_value=tiny_llm):
        out = g.synthesize_node(
            {
                "question": "schedule it",
                "action": "schedule_meeting",
                "tool_results": [partial],
            }
        )
    assert "PARTIAL" in out["answer"]
    assert "GOOGLE_CALENDAR_ATTENDEE_MODE=all" in out["answer"]


def test_composite_rollback_cycle():
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.types import Command

    from makpa.subagents.google import graph as g
    from makpa.utils.interrupts import detect_interrupt
    from tests.test_google_composite import QUESTION, _fake_tools, _StubLLM

    fakes = _fake_tools()
    update = MagicMock()
    update.invoke.return_value = {"status": "ok", "event": {"id": "evt-1", "status": "cancelled"}}
    fakes["calendar_update_event"] = update

    compiled = g.create_google_graph(checkpointer=MemorySaver())
    config = {"configurable": {"thread_id": "t-rollback"}}
    with (
        patch.dict(g.TOOLS_BY_NAME, fakes, clear=False),
        patch("makpa.llm.get_llm", return_value=_StubLLM("polished")),
    ):
        result = compiled.invoke({"question": QUESTION}, config)
        assert detect_interrupt(result) is not None
        result = compiled.invoke(Command(resume={"confirm": True}), config)
        assert detect_interrupt(result) is not None
        result = compiled.invoke(Command(resume={"rollback": True}), config)
    assert result["status"] == "rolled_back"
    assert result["composite_stage"] == "rolled_back"
    assert "cancelled" in result["answer"]
    update.invoke.assert_called_once()
    assert update.invoke.call_args[0][0]["status"] == "cancelled"

    # Rollback with no created event id errors cleanly.
    out = g.composite_rollback_node({"tool_results": [], "plan": []})
    assert out["status"] == "error"

    # Rollback resume payload routes correctly.
    assert (
        g.route_after_confirm_email({"confirmed": False, "status": "rollback_requested"})
        == "composite_rollback"
    )


def test_cli_gate2_rollback_choices():
    from makpa.cli import google_demo

    snap = SimpleNamespace(
        next=("confirm_email",),
        tasks=[SimpleNamespace(interrupts=[SimpleNamespace(value={"gate": 2})])],
    )
    idle = SimpleNamespace(next=(), tasks=[])
    for choice, code, marker in (("rollback", 0, "Rolled back"), ("n", 2, "cancelled")):
        graph = MagicMock()
        # Reads: pause-check, preview, final pause-check.
        graph.get_state.side_effect = [snap, snap, idle]
        if choice == "rollback":
            graph.invoke.side_effect = [
                {"__interrupt__": [{"gate": 2}], "status": "ok"},
                {"answer": "Rolled back at gate 2", "status": "rolled_back"},
            ]
        else:
            graph.invoke.side_effect = [
                {"__interrupt__": [{"gate": 2}], "status": "ok"},
                {"answer": "Email cancelled", "status": "cancelled"},
            ]
        with (
            patch("makpa.llm.probe_llm", return_value=_probe_ok()),
            patch("makpa.subagents.google.create_google_graph", return_value=graph),
        ):
            res = runner.invoke(google_demo.app, ["ask", "send it"], input=f"{choice}\n")
        assert res.exit_code == code, choice
        assert marker in res.output, choice


def test_tools_update_summary_and_client_normalize():
    from types import SimpleNamespace as NS

    from makpa.google import client as client_mod
    from makpa.subagents.google import tools as tools_mod

    by_name = {t.name: t for t in tools_mod.GOOGLE_TOOLS}
    fake = MagicMock()
    fake.call_tool.return_value = {"status": "ok"}
    with patch.object(tools_mod, "get_google_client", return_value=fake):
        by_name["calendar_update_event"].invoke({"event_id": "e", "summary": "New title"})
    assert fake.call_tool.call_args[0][2]["summary"] == "New title"

    assert client_mod._normalize_raw([NS(text="plain")])["text"] == "plain"
