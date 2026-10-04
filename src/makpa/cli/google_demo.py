"""Standalone Phase 3 CLI for the Google Workspace sub-agent."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import typer
from langgraph.checkpoint.memory import MemorySaver

from makpa.config import get_settings, print_startup_banner
from makpa.google.oauth import REAUTH_EXIT_CODE, ReauthRequiredError
from makpa.utils.interrupts import detect_interrupt

app = typer.Typer(help="MAKPA Google demo CLI (Phase 3)")

CALENDAR_INDICATOR = "\U0001f4c5 Calendar"
GMAIL_INDICATOR = "\u2709\ufe0f Gmail"

MAX_RESUMES = 3


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


def _split_list(raw: str) -> list[str]:
    return [part.strip() for part in raw.split(",") if part.strip()]


def _startup() -> dict[str, str]:
    """Banner, probe, OAuth/mode report. Returns resolved MCP paths."""
    from makpa.google.client import get_google_client
    from makpa.llm import probe_llm

    print_startup_banner()
    typer.echo(f"{CALENDAR_INDICATOR} probing LLM (Gemini -> Groq -> mock)...")
    try:
        result = probe_llm()
    except RuntimeError as e:
        typer.echo(f"{CALENDAR_INDICATOR} startup probe failed: {e}", err=True)
        raise typer.Exit(code=1)
    for warning in result.warnings:
        typer.echo(f"{CALENDAR_INDICATOR} warning: {warning}")
    settings = get_settings()
    # Explicit local mode without credentials is a reauth situation, not
    # a silent mock fallback (auto mode still degrades to mock).
    if (
        settings.google_mcp_mode.value == "local"
        and settings.resolved_google_oauth_state == "missing"
    ):
        _exit_reauth()
    client = get_google_client()
    raw_paths = client.paths
    paths = {
        "calendar": str(raw_paths.get("calendar", "mock")),
        "gmail": str(raw_paths.get("gmail", "mock")),
    }
    typer.echo(
        f"{CALENDAR_INDICATOR} paths: calendar={paths.get('calendar')} "
        f"gmail={paths.get('gmail')} | oauth: {settings.resolved_google_oauth_state} "
        f"| llm: {result.provider} ({result.model})"
    )
    return paths


def _exit_reauth() -> None:
    """Print reauth next steps and exit with code 3."""
    from makpa.google.oauth import build_authorization_url

    typer.echo(
        f"{CALENDAR_INDICATOR} Google reauthentication required (no cached tokens).",
        err=True,
    )
    typer.echo(f"{CALENDAR_INDICATOR} 1. Run: python -m makpa.cli.google_demo login", err=True)
    typer.echo(
        f"{CALENDAR_INDICATOR} 2. Approve in the browser "
        "(Advanced -> Go to <project> on the unverified-app screen).",
        err=True,
    )
    typer.echo(f"{CALENDAR_INDICATOR} 3. Re-run your command.", err=True)
    typer.echo(
        f"{CALENDAR_INDICATOR} direct consent URL (the login command handles "
        "PKCE for you; this URL alone is not enough):",
        err=True,
    )
    typer.echo(build_authorization_url("reauth-required"), err=True)
    raise typer.Exit(code=REAUTH_EXIT_CODE)


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


def _stream_text(text: str, indicator: str = CALENDAR_INDICATOR) -> None:
    _ = indicator
    for word in str(text).split():
        typer.echo(word + " ", nl=False)
    typer.echo("")


def _render_payload(payload: Any, indicator: str) -> None:
    if isinstance(payload, dict):
        _stream_text(f"status: {payload.get('status', '?')}", indicator)
        for key, value in payload.items():
            if key in ("status", "tool"):
                continue
            typer.echo(f"{indicator} {key}: {value}")
        if payload.get("status") == "error":
            raise typer.Exit(code=1)
    else:
        _stream_text(str(payload), indicator)


def _confirm_or_exit(title: str, lines: list[str], prompt: str) -> None:
    _boxed(title, lines)
    if not typer.confirm(prompt):
        typer.echo("Aborted.")
        raise typer.Exit(code=2)


@app.command()  # type: ignore[untyped-decorator]
def login() -> None:
    """Run the Google OAuth browser flow and cache tokens.

    Example: python -m makpa.cli.google_demo login
    """
    from makpa.google.oauth import ReauthRequiredError, run_browser_flow

    _setup_logging()
    print_startup_banner()
    typer.echo(f"{CALENDAR_INDICATOR} opening browser for Google consent...")
    try:
        run_browser_flow()
    except ReauthRequiredError as e:
        typer.echo(f"{CALENDAR_INDICATOR} login could not start: {e}", err=True)
        raise typer.Exit(code=REAUTH_EXIT_CODE)
    except RuntimeError as e:
        message = str(e)
        typer.echo(f"{CALENDAR_INDICATOR} login failed: {message}", err=True)
        if "invalid_grant" in message:
            hint = (
                "that approval is spent or belongs to another run: approvals "
                "are single-use and bound to one run. Kill any stuck login, "
                "start one fresh run, and approve the URL THAT run prints."
            )
        elif "redirect_uri_mismatch" in message:
            hint = (
                "register http://localhost:8080/callback in the OAuth "
                "client's authorized redirect URIs, wait a few minutes, retry."
            )
        elif "invalid_client" in message:
            hint = "check GOOGLE_CLIENT_SECRET matches this client (or blank it)."
        else:
            hint = (
                "add your account under OAuth consent screen -> Test users, "
                "then retry."
            )
        typer.echo(f"{CALENDAR_INDICATOR} hint: {hint}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"{CALENDAR_INDICATOR} Google OAuth cached. Re-run your command.")


@app.command(name="list-events")  # type: ignore[untyped-decorator]
def list_events(
    days: int = typer.Option(7, "--days", help="Days ahead to list"),
    calendar_id: str = typer.Option("primary", "--calendar-id"),
) -> None:
    """List events: python -m makpa.cli.google_demo list-events --days 7."""
    from makpa.subagents.google.tools import calendar_list_events

    _setup_logging()
    _startup()
    now = datetime.now(timezone.utc)
    try:
        payload = calendar_list_events.invoke(
            {
                "time_min": now.isoformat(),
                "time_max": (now + timedelta(days=days)).isoformat(),
                "calendar_id": calendar_id,
            }
        )
    except ReauthRequiredError:
        _exit_reauth()
    except Exception as e:
        typer.echo(f"{CALENDAR_INDICATOR} list-events failed: {e}", err=True)
        raise typer.Exit(code=1)
    _render_payload(payload, CALENDAR_INDICATOR)


@app.command()  # type: ignore[untyped-decorator]
def check(
    attendees: str = typer.Option("", "--attendees", help="Comma-separated emails"),
    start: str = typer.Option(..., "--start", help="Window start (ISO 8601)"),
    end: str = typer.Option(..., "--end", help="Window end (ISO 8601)"),
) -> None:
    """Check availability for attendees in a window."""
    from makpa.subagents.google.tools import calendar_check_availability

    _setup_logging()
    _startup()
    try:
        payload = calendar_check_availability.invoke(
            {"time_min": start, "time_max": end, "attendees": _split_list(attendees)}
        )
    except ReauthRequiredError:
        _exit_reauth()
    except Exception as e:
        typer.echo(f"{CALENDAR_INDICATOR} check failed: {e}", err=True)
        raise typer.Exit(code=1)
    _render_payload(payload, CALENDAR_INDICATOR)


@app.command(name="create-event")  # type: ignore[untyped-decorator]
def create_event(
    summary: str = typer.Option(..., "--summary"),
    start: str = typer.Option(..., "--start"),
    end: str = typer.Option(..., "--end"),
    attendees: str = typer.Option("", "--attendees", help="Comma-separated emails"),
    description: str = typer.Option("", "--description"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Create an event (confirmation-gated like interrupt gate 1)."""
    from makpa.subagents.google.tools import calendar_create_event

    _setup_logging()
    _startup()
    attendee_list = _split_list(attendees)
    if not yes:
        _confirm_or_exit(
            "Create calendar event (gate 1)",
            [
                f"summary: {summary}",
                f"start: {start}",
                f"end: {end}",
                f"attendees: {attendee_list}",
            ],
            f"{CALENDAR_INDICATOR} create this event?",
        )
    try:
        payload = calendar_create_event.invoke(
            {"summary": summary, "start": start, "end": end,
             "attendees": attendee_list, "description": description}
        )
    except ReauthRequiredError:
        _exit_reauth()
    except Exception as e:
        typer.echo(f"{CALENDAR_INDICATOR} create-event failed: {e}", err=True)
        raise typer.Exit(code=1)
    _render_payload(payload, CALENDAR_INDICATOR)


@app.command()  # type: ignore[untyped-decorator]
def draft(
    to: str = typer.Option(..., "--to", help="Comma-separated recipients"),
    subject: str = typer.Option(..., "--subject"),
    body: str = typer.Option("", "--body"),
    cc: str = typer.Option("", "--cc"),
    bcc: str = typer.Option("", "--bcc"),
) -> None:
    """Draft an email (safe, no gate)."""
    from makpa.subagents.google.tools import gmail_draft_message

    _setup_logging()
    _startup()
    try:
        payload = gmail_draft_message.invoke(
            {"to": _split_list(to), "subject": subject, "body": body,
             "cc": _split_list(cc), "bcc": _split_list(bcc)}
        )
    except ReauthRequiredError:
        _exit_reauth()
    except Exception as e:
        typer.echo(f"{GMAIL_INDICATOR} draft failed: {e}", err=True)
        raise typer.Exit(code=1)
    _render_payload(payload, GMAIL_INDICATOR)


@app.command()  # type: ignore[untyped-decorator]
def send(
    to: str = typer.Option(..., "--to", help="Comma-separated recipients"),
    subject: str = typer.Option(..., "--subject"),
    body: str = typer.Option("", "--body"),
    cc: str = typer.Option("", "--cc"),
    bcc: str = typer.Option("", "--bcc"),
    draft_id: str = typer.Option("", "--draft-id"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Send an email (confirmation-gated like interrupt gate 2)."""
    from makpa.subagents.google.tools import gmail_send_message

    _setup_logging()
    _startup()
    to_list = _split_list(to)
    if not yes:
        _confirm_or_exit(
            "Send email (gate 2)",
            [
                f"to: {to_list}",
                f"subject: {subject}",
                f"body: {body[:120]}",
                f"draft_id: {draft_id or '-'}",
            ],
            f"{GMAIL_INDICATOR} send this email?",
        )
    try:
        payload = gmail_send_message.invoke(
            {"to": to_list, "subject": subject, "body": body,
             "cc": _split_list(cc), "bcc": _split_list(bcc), "draft_id": draft_id}
        )
    except ReauthRequiredError:
        _exit_reauth()
    except Exception as e:
        typer.echo(f"{GMAIL_INDICATOR} send failed: {e}", err=True)
        raise typer.Exit(code=1)
    _render_payload(payload, GMAIL_INDICATOR)


@app.command()  # type: ignore[untyped-decorator]
def ask(question: str = typer.Argument(..., help="Google Workspace question")) -> None:
    """Ask: python -m makpa.cli.google_demo ask "schedule a meeting ..."."""
    from langgraph.errors import GraphInterrupt

    from makpa.subagents.google import create_google_graph

    _setup_logging()
    _startup()
    typer.echo(f"{CALENDAR_INDICATOR} thinking...")
    settings = get_settings()
    checkpointer = MemorySaver()
    graph = create_google_graph(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": f"{settings.thread_id_prefix}-google"}}
    try:
        result = graph.invoke({"question": question}, config)
        for _ in range(MAX_RESUMES):
            if _is_interrupted(graph, config, result):
                result = _resolve_confirmation(graph, config)
            else:
                break
    except GraphInterrupt:
        result = _resolve_confirmation(graph, config)
    except typer.Exit:
        raise
    except ReauthRequiredError:
        _exit_reauth()
    except Exception as e:
        typer.echo(f"{CALENDAR_INDICATOR} query failed: {e}", err=True)
        raise typer.Exit(code=1)
    if isinstance(result, dict) and result.get("status") == "confirmation_required":
        typer.echo(f"{CALENDAR_INDICATOR} confirmation required but not granted.")
        raise typer.Exit(code=2)
    if isinstance(result, dict) and result.get("status") == "cancelled":
        _stream_text(result.get("answer", "Cancelled."))
        raise typer.Exit(code=2)
    _stream_text(result.get("answer", "") if isinstance(result, dict) else str(result))
    if isinstance(result, dict) and result.get("status") == "error":
        raise typer.Exit(code=1)


def _is_interrupted(graph: Any, config: dict[str, Any], result: Any) -> bool:
    """Detect a pending interrupt from the result or the snapshot."""
    if detect_interrupt(result) is not None:
        return True
    try:
        return bool(graph.get_state(config).next)
    except Exception:
        return False


def _resolve_confirmation(graph: Any, config: dict[str, Any]) -> dict[str, Any]:
    """Show the boxed preview for the pending gate and resume or cancel."""
    from makpa.utils.interrupts import resume_with
    from makpa.utils.terminal import confirmation_title

    preview = _pending_preview(graph, config)
    gate = preview.get("gate", "?")
    lines = [f"{k}: {v}" for k, v in preview.items()]
    indicator = CALENDAR_INDICATOR if gate == 1 else GMAIL_INDICATOR
    _boxed(confirmation_title(preview), lines)
    if gate == 2:
        return _resolve_gate2(graph, config, indicator)
    if not typer.confirm(f"{indicator} approve?"):
        declined = resume_with(graph, config, {"confirm": False})
        _stream_text(declined.get("answer", "Cancelled."))
        raise typer.Exit(code=2)
    resumed: dict[str, Any] = resume_with(graph, config, {"confirm": True})
    return resumed


def _resolve_gate2(graph: Any, config: dict[str, Any], indicator: str) -> dict[str, Any]:
    """Gate-2 prompt with rollback: [y/N/rollback]."""
    from makpa.utils.interrupts import resume_with

    choice = typer.prompt(
        f"{indicator} approve? [y/N/rollback]", default="n"
    ).strip().lower()
    if choice in ("y", "yes"):
        resumed: dict[str, Any] = resume_with(graph, config, {"confirm": True})
        return resumed
    if choice == "rollback":
        rolled: dict[str, Any] = resume_with(graph, config, {"rollback": True})
        _stream_text(rolled.get("answer", "Rolled back."))
        if rolled.get("status") != "rolled_back":
            raise typer.Exit(code=1)
        return rolled
    declined = resume_with(graph, config, {"confirm": False})
    _stream_text(declined.get("answer", "Cancelled."))
    raise typer.Exit(code=2)


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


def main() -> None:
    """Entry point."""
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
