"""Phase 4: final CLI (agent) tests."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

runner = CliRunner()


def _probe_ok():
    return SimpleNamespace(provider="mock", model="mock-canned", warnings=[], message="ok")


def _final(
    answer="done",
    status="ok",
    agents=("rag_agent",),
    confirmations=None,
):
    outputs = {name: f'{{"status": "ok", "answer": "{answer}"}}' for name in agents}
    return {
        "next": list(agents),
        "agent_outputs": outputs,
        "confirmations": dict(confirmations or {}),
        "status": status,
    }


def test_agent_one_shot_ok_and_helpers():
    from makpa.cli import agent as agent_cli

    graph = MagicMock()
    graph.get_state.return_value = SimpleNamespace(next=())
    graph.invoke.return_value = _final()
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.supervisor.create_supervisor_graph", return_value=graph),
    ):
        res = runner.invoke(agent_cli.app, ["What does the PDF say?"])
    assert res.exit_code == 0 and "done" in res.output
    assert "rag_agent" in res.output

    assert agent_cli._indicator_for_preview({"payload_preview": [{"tool": "gmail_x"}]}) == (
        "\u2709\ufe0f Gmail agent"
    )
    assert agent_cli._indicator_for_preview({"payload_preview": [{"tool": "calendar_x"}]}) == (
        "\U0001f4c5 Calendar agent"
    )
    assert agent_cli._indicator_for_preview({"payload_preview": [{"tool": "github_x"}]}) == (
        "\U0001f419 GitHub agent"
    )
    assert agent_cli._indicator_for_preview({}) == "\U0001f916 Supervisor"
    assert agent_cli._pending_preview(MagicMock(), {}) == {
        "payload_preview": "(unavailable)"
    }
    broken = MagicMock()
    broken.get_state.side_effect = RuntimeError("down")
    assert agent_cli._is_paused(broken, {}) is False
    assert agent_cli._initial_state("q")["messages"][0].content == "q"
    with patch.object(agent_cli, "app") as app_mock:
        agent_cli.json_dumps({"a": 1})
    app_mock.assert_not_called()


def test_agent_status_exits_and_failures():
    from makpa.cli import agent as agent_cli

    pending = MagicMock()
    pending.get_state.return_value = SimpleNamespace(next=())
    pending.invoke.return_value = _final(status="confirmation_required")
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.supervisor.create_supervisor_graph", return_value=pending),
    ):
        res = runner.invoke(agent_cli.app, ["Do it"])
    assert res.exit_code == 2

    cancelled = MagicMock()
    cancelled.get_state.return_value = SimpleNamespace(next=())
    cancelled.invoke.return_value = _final(status="cancelled")
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.supervisor.create_supervisor_graph", return_value=cancelled),
    ):
        res = runner.invoke(agent_cli.app, ["Do it"])
    assert res.exit_code == 2

    failing = MagicMock()
    failing.get_state.return_value = SimpleNamespace(next=())
    failing.invoke.return_value = _final(status="error")
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.supervisor.create_supervisor_graph", return_value=failing),
    ):
        res = runner.invoke(agent_cli.app, ["Do it"])
    assert res.exit_code == 1

    broken = MagicMock()
    broken.invoke.side_effect = RuntimeError("down")
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.supervisor.create_supervisor_graph", return_value=broken),
    ):
        res = runner.invoke(agent_cli.app, ["Do it"])
    assert res.exit_code == 1

    with patch("makpa.llm.probe_llm", side_effect=RuntimeError("live on mock")):
        res = runner.invoke(agent_cli.app, ["Do it"])
    assert res.exit_code == 1


def test_agent_interrupt_approve_decline_rollback():
    from makpa.cli import agent as agent_cli

    def _graph(final):
        snap = SimpleNamespace(
            next=("github_agent",),
            tasks=[SimpleNamespace(interrupts=[SimpleNamespace(value={"payload_preview": []})])],
        )
        idle = SimpleNamespace(next=(), tasks=[])
        graph = MagicMock()
        graph.get_state.side_effect = [snap, snap, idle]
        graph.invoke.side_effect = [
            {"__interrupt__": [{"tool": "github_create_issue"}]},
            final,
        ]
        return graph

    approved = {
        "answer": "created",
        "status": "ok",
        "next": [],
        "agent_outputs": {},
        "confirmations": {},
    }
    graph = _graph(approved)
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.supervisor.create_supervisor_graph", return_value=graph),
    ):
        res = runner.invoke(agent_cli.app, ["Create it"], input="y\n")
    assert res.exit_code == 0

    graph = MagicMock()
    snap = SimpleNamespace(
        next=("x",),
        tasks=[SimpleNamespace(interrupts=[SimpleNamespace(value={"payload_preview": []})])],
    )
    graph.get_state.side_effect = [snap, snap]
    graph.invoke.side_effect = [
        {"__interrupt__": [{"tool": "x"}]},
        {"answer": "nope", "status": "cancelled"},
    ]
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.supervisor.create_supervisor_graph", return_value=graph),
    ):
        res = runner.invoke(agent_cli.app, ["Create it"], input="n\n")
    assert res.exit_code == 2

    # Gate-2 rollback choice maps to a rollback resume.
    graph = MagicMock()
    snap2 = SimpleNamespace(
        next=("x",),
        tasks=[SimpleNamespace(interrupts=[SimpleNamespace(value={"gate": 2})])],
    )
    graph.get_state.side_effect = [snap2, snap2, SimpleNamespace(next=(), tasks=[])]
    graph.invoke.side_effect = [
        {"__interrupt__": [{"gate": 2}]},
        {"answer": "rolled back", "status": "rolled_back"},
    ]
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.supervisor.create_supervisor_graph", return_value=graph),
    ):
        res = runner.invoke(agent_cli.app, ["Send it"], input="rollback\n")
    assert res.exit_code == 0 and "rolled back" in res.output


def test_agent_modes_threads_repl_and_reauth():
    from makpa.cli import agent as agent_cli
    from makpa.google.oauth import ReauthRequiredError

    with patch("makpa.llm.probe_llm", return_value=_probe_ok()):
        res = runner.invoke(agent_cli.app, ["--mode", "bogus", "Hi"])
    assert res.exit_code == 1

    graph = MagicMock()
    graph.get_state.return_value = SimpleNamespace(next=())
    graph.invoke.return_value = _final()
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.supervisor.create_supervisor_graph", return_value=graph),
    ):
        res = runner.invoke(
            agent_cli.app, ["--mode", "demo", "--thread", "t-1", "Hi"]
        )
    assert res.exit_code == 0

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.supervisor.create_supervisor_graph", return_value=graph),
    ):
        res = runner.invoke(agent_cli.app, ["--interactive"], input="Hi\nexit\n")
    assert res.exit_code == 0

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.supervisor.create_supervisor_graph", return_value=graph),
    ):
        res = runner.invoke(agent_cli.app, ["--interactive"], input="\nHi\nquit\n")
    assert res.exit_code == 0

    reauth = MagicMock()
    reauth.invoke.side_effect = ReauthRequiredError("http://reauth")
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.supervisor.create_supervisor_graph", return_value=reauth),
    ):
        res = runner.invoke(agent_cli.app, ["Hi"])
    assert res.exit_code == 3
