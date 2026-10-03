"""Final Phase 4 CLI: one-shot, interactive, and threaded multi-agent runs."""

from __future__ import annotations

from typing import Any

import typer
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

from makpa.config import get_settings, print_startup_banner
from makpa.google.oauth import ReauthRequiredError

app = typer.Typer(
    help="MAKPA multi-agent CLI (Phase 4)",
    invoke_without_command=True,
    no_args_is_help=False,
)

AGENT_INDICATORS = {
    "rag_agent": "[RAG agent]",
    "github_agent": "\U0001f419 GitHub agent",
    "google_agent": "\U0001f4c5 Calendar / \u2709\ufe0f Gmail agent",
}

MAX_RESUMES = 5


def _setup_logging() -> None:
    import sys

    for stream in (sys.stdout, sys.stderr):
        reconfig = getattr(stream, "reconfigure", None)
        if callable(reconfig):
            try:
                reconfig(encoding="utf-8", errors="replace")
            except Exception:
                pass
    from makpa.utils.terminal import setup_logging

    setup_logging()


def _apply_mode_override(mode: str) -> None:
    """Override MAKPA_MODE for one run (demo|free|live)."""
    import os

    choice = mode.strip().lower()
    if choice not in ("demo", "free", "live"):
        typer.echo(f"Invalid mode {mode!r}: expected demo|free|live", err=True)
        raise typer.Exit(code=1)
    os.environ["MAKPA_MODE"] = choice
    if hasattr(get_settings, "cache_clear"):
        get_settings.cache_clear()


def _startup() -> None:
    """Banner, probe, and indicator roll-call."""
    from makpa.llm import probe_llm

    print_startup_banner()
    typer.echo("\U0001f916 Supervisor probing LLM (Gemini -> Groq -> mock)...")
    try:
        result = probe_llm()
    except RuntimeError as e:
        typer.echo(f"\U0001f916 Supervisor startup probe failed: {e}", err=True)
        raise typer.Exit(code=1)
    for warning in result.warnings:
        typer.echo(f"\U0001f916 Supervisor warning: {warning}")
    settings = get_settings()
    typer.echo(
        f"\U0001f916 Supervisor ready | agents: rag+github+google "
        f"| github={settings.resolved_github_mcp_path} "
        f"google={settings.resolved_google_mcp_mode.value} "
        f"oauth={settings.resolved_google_oauth_state} "
        f"| llm: {result.provider} ({result.model})"
    )


def _boxed(title: str, lines: list[str]) -> None:
    from makpa.utils.terminal import wrap_box_lines

    lines = wrap_box_lines(lines)
    width = max([len(title)] + [len(line) for line in lines] + [10]) + 4
    border = "+" + "-" * (width - 2) + "+"
    typer.echo(border)
    typer.echo(f"| {title:<{width - 4}} |")
    typer.echo(border)
    for line in lines:
        typer.echo(f"| {line:<{width - 4}} |")
    typer.echo(border)


def _stream_text(text: str) -> None:
    for word in str(text).split():
        typer.echo(word + " ", nl=False)
    typer.echo("")


def _indicator_for_preview(preview: dict[str, Any]) -> str:
    """Attribute an interrupt preview to its sub-agent."""
    blob = json_dumps(preview)
    if "gmail_" in blob:
        return "\u2709\ufe0f Gmail agent"
    if "calendar_" in blob:
        return "\U0001f4c5 Calendar agent"
    if "github_" in blob:
        return "\U0001f419 GitHub agent"
    return "\U0001f916 Supervisor"


def json_dumps(payload: Any) -> str:
    """Best-effort JSON dump for attribution scanning."""
    import json

    try:
        return json.dumps(payload, default=str)
    except (TypeError, ValueError):
        return str(payload)


def _pending_preview(graph: Any, config: dict[str, Any]) -> dict[str, Any]:
    """Extract the interrupt payload preview from a paused graph."""
    try:
        snapshot = graph.get_state(config)
        for task in snapshot.tasks:
            for interrupt_obj in getattr(task, "interrupts", []):
                value = getattr(interrupt_obj, "value", {})
                if isinstance(value, dict):
                    preview: dict[str, Any] = value
                    return preview
    except Exception:
        pass
    return {"payload_preview": "(unavailable)"}


def _is_paused(graph: Any, config: dict[str, Any]) -> bool:
    """Check the snapshot when the result carries no interrupt."""
    try:
        return bool(graph.get_state(config).next)
    except Exception:
        return False


def _run_once(graph: Any, config: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    """Invoke (or resume) the supervisor until no gate is pending."""
    from langgraph.errors import GraphInterrupt

    from makpa.utils.interrupts import detect_interrupt

    try:
        result = graph.invoke(payload, config)
    except GraphInterrupt:
        result = {"__interrupt__": [True]}
    for _ in range(MAX_RESUMES):
        pending = detect_interrupt(result) is not None or _is_paused(graph, config)
        if not pending:
            break
        result = _resolve_confirmation(graph, config)
    return dict(result) if isinstance(result, dict) else {"answer": str(result)}


def _resolve_confirmation(graph: Any, config: dict[str, Any]) -> dict[str, Any]:
    """Boxed gate prompt with rollback support for gate 2."""
    from makpa.utils.interrupts import resume_with

    preview = _pending_preview(graph, config)
    indicator = _indicator_for_preview(preview)
    gate = preview.get("gate", "?")
    lines = [f"{k}: {v}" for k, v in preview.items()]
    _boxed(f"Confirmation required (gate {gate})", lines)
    if gate == 2:
        choice = typer.prompt(
            f"{indicator} approve? [y/N/rollback]", default="n"
        ).strip().lower()
        if choice in ("y", "yes"):
            resumed: dict[str, Any] = resume_with(graph, config, {"confirm": True})
            return resumed
        if choice == "rollback":
            rolled: dict[str, Any] = resume_with(graph, config, {"rollback": True})
            _stream_text(rolled.get("answer", "Rolled back."))
            return rolled
        declined = resume_with(graph, config, {"confirm": False})
        _stream_text(declined.get("answer", "Cancelled."))
        raise typer.Exit(code=2)
    if not typer.confirm(f"{indicator} approve?"):
        declined = resume_with(graph, config, {"confirm": False})
        _stream_text(declined.get("answer", "Cancelled."))
        raise typer.Exit(code=2)
    resumed = resume_with(graph, config, {"confirm": True})
    final: dict[str, Any] = resumed
    return final


def _report(result: dict[str, Any]) -> int:
    """Stream per-agent sections plus routing and statuses. Returns exit code."""
    agents = result.get("next", [])
    if agents:
        typer.echo(f"\U0001f916 Supervisor routed to: {', '.join(agents)}")
    outputs = result.get("agent_outputs", {})
    for name in ("rag_agent", "github_agent", "google_agent"):
        raw = outputs.get(name) if isinstance(outputs, dict) else None
        if raw is None:
            continue
        import json

        try:
            data = json.loads(raw)
        except (ValueError, TypeError):
            data = {"answer": str(raw), "status": "error"}
        indicator = AGENT_INDICATORS.get(name, name)
        tools = data.get("tools", []) if isinstance(data, dict) else []
        if tools:
            called = ", ".join(
                str(t.get("tool", "?")) for t in tools if isinstance(t, dict)
            )
            typer.echo(f"{indicator} tools called: {called}")
        _stream_text(data.get("answer", "") if isinstance(data, dict) else str(data))
    status = result.get("status", "ok")
    confirmations = result.get("confirmations", {})
    if isinstance(confirmations, dict):
        waiting = [name for name, done in confirmations.items() if not done]
        if waiting:
            typer.echo(f"\U0001f916 Supervisor: awaiting confirmation: {', '.join(waiting)}")
    if status == "confirmation_required":
        raise typer.Exit(code=2)
    if status in ("cancelled",):
        raise typer.Exit(code=2)
    if status == "error":
        raise typer.Exit(code=1)
    return 0


@app.callback()  # type: ignore[untyped-decorator]
def main(
    query: str = typer.Argument(None, help="Natural-language query (one-shot)"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Multi-turn REPL"),
    thread: str = typer.Option("", "--thread", "-t", help="Named thread id"),
    mode: str = typer.Option("", "--mode", "-m", help="Mode override: demo|free|live"),
) -> None:
    """Run the MAKPA supervisor: one-shot, interactive, or threaded."""
    from makpa.supervisor import create_supervisor_graph

    _setup_logging()
    if mode:
        _apply_mode_override(mode)
    _startup()
    settings = get_settings()
    thread_id = thread.strip() or f"{settings.thread_id_prefix}-main"
    checkpointer = MemorySaver()
    graph = create_supervisor_graph(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": thread_id}}
    try:
        if interactive or not query:
            _repl(graph, config)
            return
        result = _run_once(graph, config, _initial_state(query))
        code = _report(result)
        raise typer.Exit(code=code)
    except typer.Exit:
        raise
    except ReauthRequiredError:
        typer.echo("\U0001f916 Supervisor Google reauthentication required.", err=True)
        raise typer.Exit(code=3)
    except Exception as e:
        typer.echo(f"\U0001f916 Supervisor query failed: {e}", err=True)
        raise typer.Exit(code=1)


def _initial_state(query: str) -> dict[str, Any]:
    """Build the supervisor input state for one user query."""
    return {"messages": [HumanMessage(content=query)]}


def _repl(graph: Any, config: dict[str, Any]) -> None:
    """Multi-turn REPL sharing one thread's memory."""
    typer.echo("\U0001f916 Supervisor REPL (type 'exit' or 'quit' to leave)")
    while True:
        try:
            query = typer.prompt("\U0001f916 you")
        except (EOFError, KeyboardInterrupt):
            typer.echo("")
            return
        if query.strip().lower() in ("exit", "quit"):
            return
        if not query.strip():
            continue
        try:
            result = _run_once(graph, config, _initial_state(query))
            _report(result)
        except typer.Exit as e:
            typer.echo(f"(turn exited with code {e.exit_code})")
        except Exception as e:
            typer.echo(f"Turn failed: {e}", err=True)


if __name__ == "__main__":  # pragma: no cover
    app()
