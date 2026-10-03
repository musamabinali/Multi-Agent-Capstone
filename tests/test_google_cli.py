"""Phase 3: google_demo CLI tests (commands, gates, exit codes, reauth)."""

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

runner = CliRunner()


def _probe_ok():
    return SimpleNamespace(provider="mock", model="mock-canned", warnings=[], message="ok")


def _patch_startup(monkeypatch_probe=True):
    from makpa.google.oauth import REAUTH_EXIT_CODE  # noqa: F401

    return patch("makpa.llm.probe_llm", return_value=_probe_ok())


def test_list_events_and_check_ok():
    from makpa.cli import google_demo

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.subagents.google.tools.calendar_list_events",
            MagicMock(**{"invoke.return_value": {"status": "ok", "events": [], "count": 0}}),
        ),
    ):
        res = runner.invoke(google_demo.app, ["list-events", "--days", "7"])
    assert res.exit_code == 0 and "ok" in res.output

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.subagents.google.tools.calendar_check_availability",
            MagicMock(**{"invoke.return_value": {"status": "ok", "free": True}}),
        ),
    ):
        res = runner.invoke(
            google_demo.app,
            ["check", "--start", "2026-10-01T00:00:00Z", "--end", "2026-10-02T00:00:00Z"],
        )
    assert res.exit_code == 0


def test_tool_failure_exits_one():
    from makpa.cli import google_demo

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.subagents.google.tools.calendar_list_events",
            MagicMock(**{"invoke.side_effect": RuntimeError("down")}),
        ),
    ):
        res = runner.invoke(google_demo.app, ["list-events"])
    assert res.exit_code == 1

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.subagents.google.tools.gmail_draft_message",
            MagicMock(**{"invoke.side_effect": RuntimeError("down")}),
        ),
    ):
        res = runner.invoke(google_demo.app, ["draft", "--to", "a@x.com", "--subject", "Hi"])
    assert res.exit_code == 1


def test_draft_ok_no_gate():
    from makpa.cli import google_demo

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.subagents.google.tools.gmail_draft_message",
            MagicMock(**{"invoke.return_value": {"status": "ok", "draft": {"id": "d"}}}),
        ),
    ):
        res = runner.invoke(google_demo.app, ["draft", "--to", "a@x.com", "--subject", "Hi"])
    assert res.exit_code == 0 and "d" in res.output


def test_create_event_decline_and_approved():
    from makpa.cli import google_demo

    with patch("makpa.llm.probe_llm", return_value=_probe_ok()):
        res = runner.invoke(
            google_demo.app,
            ["create-event", "--summary", "S", "--start", "2026-10-02T15:00:00Z",
             "--end", "2026-10-02T16:00:00Z"],
            input="n\n",
        )
    assert res.exit_code == 2 and "Aborted" in res.output

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.subagents.google.tools.calendar_create_event",
            MagicMock(**{"invoke.return_value": {"status": "ok", "event": {"id": "e"}}}),
        ),
    ):
        res = runner.invoke(
            google_demo.app,
            ["create-event", "--summary", "S", "--start", "2026-10-02T15:00:00Z",
             "--end", "2026-10-02T16:00:00Z", "--yes"],
        )
    assert res.exit_code == 0

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.subagents.google.tools.calendar_create_event",
            MagicMock(**{"invoke.return_value": {"status": "error", "message": "bad"}}),
        ),
    ):
        res = runner.invoke(
            google_demo.app,
            ["create-event", "--summary", "S", "--start", "2026-10-02T15:00:00Z",
             "--end", "2026-10-02T16:00:00Z", "--yes"],
        )
    assert res.exit_code == 1


def test_send_decline_approved_and_failure():
    from makpa.cli import google_demo

    with patch("makpa.llm.probe_llm", return_value=_probe_ok()):
        res = runner.invoke(
            google_demo.app, ["send", "--to", "a@x.com", "--subject", "Hi"], input="n\n"
        )
    assert res.exit_code == 2

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.subagents.google.tools.gmail_send_message",
            MagicMock(**{"invoke.return_value": {"status": "ok", "sent": {"id": "m"}}}),
        ),
    ):
        res = runner.invoke(
            google_demo.app, ["send", "--to", "a@x.com", "--subject", "Hi", "--yes"]
        )
    assert res.exit_code == 0

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.subagents.google.tools.gmail_send_message",
            MagicMock(**{"invoke.side_effect": RuntimeError("down")}),
        ),
    ):
        res = runner.invoke(
            google_demo.app, ["send", "--to", "a@x.com", "--subject", "Hi", "--yes"]
        )
    assert res.exit_code == 1


def test_reauth_paths_exit_three():
    from makpa.cli import google_demo
    from makpa.google.oauth import ReauthRequiredError

    # Explicit local mode without credentials -> reauth at startup.
    settings = SimpleNamespace(
        google_mcp_mode=SimpleNamespace(value="local"),
        resolved_google_oauth_state="missing",
        thread_id_prefix="makpa",
    )
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.cli.google_demo.get_settings", return_value=settings),
        patch("makpa.cli.google_demo.print_startup_banner"),
    ):
        res = runner.invoke(google_demo.app, ["list-events"])
    assert res.exit_code == 3

    # Reauth raised mid-command maps to exit 3.
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.subagents.google.tools.calendar_list_events",
            MagicMock(**{"invoke.side_effect": ReauthRequiredError("http://reauth")}),
        ),
    ):
        res = runner.invoke(google_demo.app, ["list-events"])
    assert res.exit_code == 3


def test_probe_failure_and_ask_variants():
    from makpa.cli import google_demo

    with patch("makpa.llm.probe_llm", side_effect=RuntimeError("live on mock")):
        res = runner.invoke(google_demo.app, ["list-events"])
    assert res.exit_code == 1

    graph = MagicMock()
    graph.get_state.return_value = SimpleNamespace(next=())
    graph.invoke.return_value = {"answer": "2 events", "status": "ok"}
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.subagents.google.create_google_graph", return_value=graph),
    ):
        res = runner.invoke(google_demo.app, ["ask", "List events"])
    assert res.exit_code == 0 and "2 events" in res.output

    pending = MagicMock()
    pending.get_state.return_value = SimpleNamespace(next=())
    pending.invoke.return_value = {"answer": "needs approval", "status": "confirmation_required"}
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.subagents.google.create_google_graph", return_value=pending),
    ):
        res = runner.invoke(google_demo.app, ["ask", "Send it"])
    assert res.exit_code == 2

    cancelled = MagicMock()
    cancelled.get_state.return_value = SimpleNamespace(next=())
    cancelled.invoke.return_value = {"answer": "stopped", "status": "cancelled"}
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.subagents.google.create_google_graph", return_value=cancelled),
    ):
        res = runner.invoke(google_demo.app, ["ask", "Send it"])
    assert res.exit_code == 2

    failing = MagicMock()
    failing.get_state.return_value = SimpleNamespace(next=())
    failing.invoke.return_value = {"answer": "bad", "status": "error"}
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.subagents.google.create_google_graph", return_value=failing),
    ):
        res = runner.invoke(google_demo.app, ["ask", "q"])
    assert res.exit_code == 1

    broken = MagicMock()
    broken.invoke.side_effect = RuntimeError("down")
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.subagents.google.create_google_graph", return_value=broken),
    ):
        res = runner.invoke(google_demo.app, ["ask", "q"])
    assert res.exit_code == 1


def test_ask_two_gate_loop_and_graph_interrupt():
    from langgraph.errors import GraphInterrupt

    from makpa.cli import google_demo

    snap = SimpleNamespace(
        next=("confirm_event",),
        tasks=[SimpleNamespace(interrupts=[SimpleNamespace(value={"gate": 1})])],
    )
    idle = SimpleNamespace(next=(), tasks=[])
    graph = MagicMock()
    # Reads: check, preview, check, preview, final check.
    graph.get_state.side_effect = [snap, snap, snap, snap, idle]
    graph.invoke.side_effect = [
        {"__interrupt__": [{"gate": 1}], "status": "ok"},
        {"__interrupt__": [{"gate": 2}], "status": "ok"},
        {"answer": "scheduled evt-1 msg-1", "status": "ok"},
    ]
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.subagents.google.create_google_graph", return_value=graph),
    ):
        res = runner.invoke(google_demo.app, ["ask", "schedule it"], input="y\ny\n")
    assert res.exit_code == 0 and "scheduled" in res.output

    raising = MagicMock()
    raising.get_state.return_value = snap
    raising.invoke.side_effect = [
        GraphInterrupt("paused"),
        {"answer": "done", "status": "ok"},
    ]
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.subagents.google.create_google_graph", return_value=raising),
    ):
        res = runner.invoke(google_demo.app, ["ask", "schedule it"], input="y\n")
    assert res.exit_code == 0


def test_helpers_and_main():
    from makpa.cli import google_demo

    assert google_demo._split_list("a@x.com, ,b@y.org") == ["a@x.com", "b@y.org"]
    assert google_demo._pending_preview(MagicMock(), {}) == {
        "payload_preview": "(unavailable)"
    }
    broken = MagicMock()
    broken.get_state.side_effect = RuntimeError("down")
    assert google_demo._pending_preview(broken, {}) == {
        "payload_preview": "(unavailable)"
    }
    assert google_demo._is_interrupted(broken, {}, {"status": "ok"}) is False
    google_demo._render_payload("plain", google_demo.GMAIL_INDICATOR)
    try:
        google_demo._render_payload({"status": "error"}, google_demo.GMAIL_INDICATOR)
        raised = False
    except Exception as e:
        raised = getattr(e, "exit_code", None) == 1
    assert raised
    with patch.object(google_demo, "app") as app_mock:
        google_demo.main()
    app_mock.assert_called_once()
    # Setup logging tolerates streams without reconfigure.
    bad = MagicMock()
    del bad.reconfigure
    with (
        patch.object(sys, "stdout", bad),
        patch.object(sys, "stderr", bad),
    ):
        google_demo._setup_logging()
