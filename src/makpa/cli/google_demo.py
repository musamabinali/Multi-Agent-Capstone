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


def _setup_logging(
    verbose: bool | None = None,
    quiet: bool = False,
    log_file: str | None = None,
) -> None:
    import os
    import sys

    for stream in (sys.stdout, sys.stderr):
        reconfig = getattr(stream, "reconfigure", None)
        if callable(reconfig):
            try:
                reconfig(encoding="utf-8", errors="replace")
            except Exception:
                pass
    # --no-color / --no-emoji propagate via env for the terminal layer.
    _ = os.environ
    from makpa.utils.terminal import reset_cli_ux_state, setup_logging

    # Each top-level command entry is a fresh session (separate OS process
    # in real use); REPL turns reuse the session via _ask_once/_run_once,
    # which never call _setup_logging.
    reset_cli_ux_state()
    setup_logging(verbose=verbose, quiet=quiet, log_file=log_file)


def _apply_output_flags(
    verbose: bool = False,
    quiet: bool = False,
    no_color: bool = False,
    no_emoji: bool = False,
    log_file: str | None = None,
) -> None:
    """Apply --verbose/--quiet/--no-color/--no-emoji/--log-file, then setup."""
    import os

    if no_color:
        os.environ["MAKPA_NO_COLOR"] = "1"
    if no_emoji:
        os.environ["MAKPA_NO_EMOJI"] = "1"
    if verbose:
        os.environ["MAKPA_VERBOSE"] = "1"
    if quiet:
        os.environ["MAKPA_QUIET"] = "1"
    _setup_logging(
        verbose=True if verbose else (None if not quiet else False),
        quiet=quiet,
        log_file=log_file,
    )


def _split_list(raw: str) -> list[str]:
    return [part.strip() for part in raw.split(",") if part.strip()]


def _startup(quiet: bool = False) -> dict[str, str]:
    """Banner, probe, OAuth/mode report. Returns resolved MCP paths.

    The banner and the Gemini->Groq fallback notice print once per
    session; later calls reuse the cached probe silently.
    """
    from makpa.google.client import get_google_client
    from makpa.llm import probe_llm
    from makpa.utils.terminal import (
        banner_already_printed,
        fallback_notice,
        mark_banner_printed,
        verbose_enabled,
    )

    first = not banner_already_printed()
    if first and not quiet:
        print_startup_banner()
    if first:
        mark_banner_printed()
    if first and not quiet:
        typer.echo(f"{CALENDAR_INDICATOR} probing LLM (Gemini -> Groq -> mock)...")
    try:
        result = probe_llm()
    except RuntimeError as e:
        typer.echo(f"{CALENDAR_INDICATOR} startup probe failed: {e}", err=True)
        raise typer.Exit(code=1)
    if first:
        # One-time fallback notice: Gemini 403 -> Groq, then silent.
        if result.provider in ("groq", "mock"):
            notice = fallback_notice("Groq" if result.provider == "groq" else "mock")
            if notice and not quiet:
                typer.echo(f"{CALENDAR_INDICATOR} {notice}")
        for warning in result.warnings:
            if verbose_enabled() or first:
                typer.echo(f"{CALENDAR_INDICATOR} warning: {warning}", err=True)
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
    if first and not quiet:
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

    lines = wrap_box_lines(lines, width=72)
    width = min(max([len(title)] + [len(line) for line in lines] + [10]) + 4, 78)
    border = "+" + "-" * (width - 2) + "+"
    typer.echo(border)
    typer.echo(f"| {title:<{width - 4}} |")
    typer.echo(border)
    for line in lines:
        typer.echo(f"| {line:<{width - 4}} |")
    typer.echo(border)


def _show_confirmation_card(preview: dict[str, Any]) -> str:
    """Render the adaptive confirmation card. Returns the prompt indicator."""
    from makpa.utils.terminal import (
        confirmation_indicator,
        format_confirmation_card,
    )

    typer.echo(format_confirmation_card(preview))
    return str(confirmation_indicator(preview))


def _stream_text(text: str, indicator: str = CALENDAR_INDICATOR) -> None:
    _ = indicator
    for word in str(text).split():
        typer.echo(word + " ", nl=False)
    typer.echo("")


def _render_payload(payload: Any, indicator: str) -> None:
    import json as _json

    if isinstance(payload, dict):
        _stream_text(f"status: {payload.get('status', '?')}", indicator)
        for key, value in payload.items():
            if key in ("status", "tool"):
                continue
            # JSON (double quotes) — never raw Python dict repr.
            rendered = (
                _json.dumps(value, default=str) if isinstance(value, (dict, list)) else str(value)
            )
            typer.echo(f"{indicator} {key}: {rendered}")
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
def ask(
    question: str = typer.Argument(..., help="Google Workspace question"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="INFO logs on stderr"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Answer + timing only"),
    json_output: bool = typer.Option(False, "--json", help="Single JSON object on stdout"),
    no_color: bool = typer.Option(False, "--no-color", help="Disable ANSI colors"),
    no_emoji: bool = typer.Option(False, "--no-emoji", help="Disable emoji"),
    log_file: str = typer.Option("", "--log-file", help="Full logs to PATH"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Warm session REPL"),
) -> None:
    """Ask: python -m makpa.cli.google_demo ask "schedule a meeting ..."."""
    import time

    from makpa.subagents.google import create_google_graph

    _apply_output_flags(verbose, quiet or json_output, no_color, no_emoji, log_file or None)
    paths = _startup(quiet=quiet or json_output)
    _ = paths
    settings = get_settings()
    checkpointer = MemorySaver()
    graph = create_google_graph(checkpointer=checkpointer)
    base_thread = f"{settings.thread_id_prefix}-google"
    if interactive:
        _ask_repl(graph, base_thread, verbose=verbose, quiet=quiet, json_output=json_output)
        return
    t0 = time.monotonic()
    result = _ask_once(graph, base_thread, question, quiet=quiet or json_output)
    total = time.monotonic() - t0
    _report_ask_result(result, total_s=total, verbose=verbose, quiet=quiet, json_output=json_output)


def _ask_once(
    graph: Any, thread_id: str, question: str, quiet: bool = False
) -> dict[str, Any]:
    """Invoke the google graph until no gate is pending."""
    import time

    from langgraph.errors import GraphInterrupt

    from makpa.utils.terminal import progress_done

    config = {"configurable": {"thread_id": thread_id}}
    started = time.monotonic()
    if not quiet:
        typer.echo(f"{CALENDAR_INDICATOR} working...")
    try:
        result = graph.invoke({"question": question}, config)
        for _ in range(MAX_RESUMES):
            if _is_interrupted(graph, config, result):
                result = _resolve_confirmation(graph, config, quiet=quiet)
            else:
                break
    except GraphInterrupt:
        result = _resolve_confirmation(graph, config, quiet=quiet)
    except typer.Exit as e:
        if e.exit_code == 2 and not quiet:
            from makpa.utils.terminal import format_cancelled_timing

            typer.echo(format_cancelled_timing(time.monotonic() - started))
        raise
    except ReauthRequiredError:
        _exit_reauth()
    except Exception as e:
        typer.echo(f"{CALENDAR_INDICATOR} query failed: {e}", err=True)
        raise typer.Exit(code=1)
    dur = time.monotonic() - started
    if not quiet:
        typer.echo(progress_done("calendar", "google turn complete", dur))
    return dict(result) if isinstance(result, dict) else {"answer": str(result)}


def _report_ask_result(
    result: dict[str, Any], total_s: float, verbose: bool, quiet: bool, json_output: bool
) -> None:
    """Render sectioned Answer/Actions + timing footer (or JSON)."""
    import json as _json

    from makpa.utils.terminal import (
        clean_answer_text,
        format_cancelled_timing,
        format_timing,
    )

    status = result.get("status", "ok")
    if status == "confirmation_required":
        typer.echo(f"{CALENDAR_INDICATOR} confirmation required but not granted.")
        if not json_output:
            typer.echo(format_cancelled_timing(total_s))
        raise typer.Exit(code=2)
    if status == "cancelled":
        _stream_text(result.get("answer", "Cancelled."))
        if not json_output:
            typer.echo(format_cancelled_timing(total_s))
        raise typer.Exit(code=2)
    answer = clean_answer_text(result.get("answer", ""))
    structured = result.get("structured") or _structured_from_result(result)
    if json_output:
        typer.echo(
            _json.dumps(
                {
                    "answer": answer,
                    "citations": [],
                    "actions": structured,
                    "timings": {"total_s": round(total_s, 2)},
                    "status": status,
                },
                default=str,
            )
        )
    elif quiet:
        typer.echo(answer)
        typer.echo(format_timing(total_s, {}, parallel=False))
    else:
        _render_sectioned(answer, structured, total_s, verbose=verbose)
    if status == "error":
        raise typer.Exit(code=1)


def _structured_from_result(result: dict[str, Any]) -> dict[str, Any]:
    """Best-effort structured ids from tool_results (never prose regex)."""
    structured: dict[str, Any] = {}
    tool_results = result.get("tool_results")
    items = tool_results if isinstance(tool_results, list) else []
    for item in items:
        if not isinstance(item, dict):
            continue
        event = item.get("event")
        if isinstance(event, dict) and event.get("id"):
            structured.setdefault("event_ids", []).append(str(event["id"]))
            structured["event_id"] = str(event["id"])
        for ev in item.get("events", []) if isinstance(item.get("events"), list) else []:
            if isinstance(ev, dict) and ev.get("id"):
                structured.setdefault("event_ids", []).append(str(ev["id"]))
        sent = item.get("sent")
        if isinstance(sent, dict) and sent.get("id"):
            structured["message_id"] = str(sent["id"])
        if item.get("message_id"):
            structured["message_id"] = str(item["message_id"])
        if item.get("draft_id"):
            structured["draft_id"] = str(item["draft_id"])
    return structured


def _render_sectioned(
    answer: str, structured: dict[str, Any], total_s: float, verbose: bool = False
) -> None:
    from makpa.utils.terminal import render_sectioned_result

    typer.echo(
        render_sectioned_result(
            answer,
            citations=[],
            structured=structured,
            total_s=total_s,
            parts={"Google": total_s},
            verbose=verbose,
        )
    )


def _ask_repl(
    graph: Any, base_thread: str, verbose: bool, quiet: bool, json_output: bool
) -> None:
    """Warm interactive session (banner/probe paid once)."""
    import time

    thread_id = base_thread
    typer.echo("makpa › interactive Google session (:exit, :reset, :thread <id>, :verbose)")
    while True:
        try:
            line = input("makpa › ").strip()
        except (EOFError, KeyboardInterrupt):
            typer.echo("")
            return
        if not line:
            continue
        low = line.lower()
        if low in (":exit", ":quit", "exit", "quit"):
            return
        if low == ":reset":
            thread_id = base_thread
            typer.echo("thread reset.")
            continue
        if low.startswith(":thread"):
            parts = line.split(None, 1)
            if len(parts) == 2 and parts[1].strip():
                thread_id = parts[1].strip()
                typer.echo(f"thread: {thread_id}")
            continue
        if low == ":verbose":
            verbose = not verbose
            _setup_logging(verbose=verbose)
            typer.echo(f"verbose {'on' if verbose else 'off'}.")
            continue
        t0 = time.monotonic()
        try:
            result = _ask_once(graph, thread_id, line, quiet=quiet or json_output)
            _report_ask_result(
                result,
                total_s=time.monotonic() - t0,
                verbose=verbose,
                quiet=quiet,
                json_output=json_output,
            )
        except typer.Exit as e:
            typer.echo(f"(turn exited with code {e.exit_code})")
        except Exception as e:
            typer.echo(f"Turn failed: {e}", err=True)


def _is_interrupted(graph: Any, config: dict[str, Any], result: Any) -> bool:
    """Detect a pending interrupt from the result or the snapshot."""
    if detect_interrupt(result) is not None:
        return True
    try:
        return bool(graph.get_state(config).next)
    except Exception:
        return False


def _resolve_confirmation(
    graph: Any, config: dict[str, Any], quiet: bool = False
) -> dict[str, Any]:
    """Show the adaptive confirmation card and resume or cancel."""
    from makpa.utils.interrupts import resume_with

    preview = _pending_preview(graph, config)
    gate = preview.get("gate", "?")
    indicator = _show_confirmation_card(preview) if not quiet else "Confirm"
    if gate == 2:
        return _resolve_gate2(graph, config, indicator, quiet=quiet)
    if not typer.confirm(f"{indicator} approve?"):
        declined = resume_with(graph, config, {"confirm": False})
        _stream_text(declined.get("answer", "Cancelled."))
        raise typer.Exit(code=2)
    resumed: dict[str, Any] = resume_with(graph, config, {"confirm": True})
    return resumed


def _resolve_gate2(
    graph: Any, config: dict[str, Any], indicator: str, quiet: bool = False
) -> dict[str, Any]:
    """Gate-2 prompt with rollback: [y/N/rollback]."""
    from makpa.utils.interrupts import resume_with

    _ = quiet
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
