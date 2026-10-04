"""Standalone Phase 2 CLI for the GitHub MCP sub-agent."""

from __future__ import annotations

from typing import Any

import typer
from langgraph.checkpoint.memory import MemorySaver

from makpa.config import get_settings, print_startup_banner

app = typer.Typer(help="MAKPA GitHub demo CLI (Phase 2)")

GITHUB_INDICATOR = "\U0001f419 GitHub agent"


def _setup_logging(
    verbose: bool | None = None,
    quiet: bool = False,
    log_file: str | None = None,
) -> None:
    import sys

    for stream in (sys.stdout, sys.stderr):
        reconfig = getattr(stream, "reconfigure", None)
        if callable(reconfig):
            try:
                reconfig(encoding="utf-8", errors="replace")
            except Exception:
                pass
    from makpa.utils.terminal import reset_cli_ux_state, setup_logging

    reset_cli_ux_state()
    setup_logging(verbose=verbose, quiet=quiet, log_file=log_file)


def _apply_output_flags(
    verbose: bool = False,
    quiet: bool = False,
    no_color: bool = False,
    no_emoji: bool = False,
    log_file: str | None = None,
) -> None:
    """Apply output flags, then setup logging."""
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


def _startup(quiet: bool = False) -> None:
    """Print banner, run the model probe, and report the GitHub path (once)."""
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
        typer.echo(f"{GITHUB_INDICATOR} probing LLM (Gemini -> Groq -> mock)...")
    try:
        result = probe_llm()
    except RuntimeError as e:
        typer.echo(f"{GITHUB_INDICATOR} startup probe failed: {e}", err=True)
        raise typer.Exit(code=1)
    if first:
        if result.provider in ("groq", "mock"):
            notice = fallback_notice("Groq" if result.provider == "groq" else "mock")
            if notice and not quiet:
                typer.echo(f"{GITHUB_INDICATOR} {notice}")
        for warning in result.warnings:
            if verbose_enabled() or first:
                typer.echo(f"{GITHUB_INDICATOR} warning: {warning}", err=True)
    settings = get_settings()
    if first and not quiet:
        typer.echo(
            f"{GITHUB_INDICATOR} path: {settings.resolved_github_mcp_path} "
            f"| llm: {result.provider} ({result.model})"
        )


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


def _stream_text(text: str) -> None:
    for word in str(text).split():
        typer.echo(word + " ", nl=False)
    typer.echo("")


@app.command()  # type: ignore[untyped-decorator]
def ask(
    question: str = typer.Argument(..., help="GitHub question to ask"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    quiet: bool = typer.Option(False, "--quiet", "-q"),
    json_output: bool = typer.Option(False, "--json"),
    no_color: bool = typer.Option(False, "--no-color"),
    no_emoji: bool = typer.Option(False, "--no-emoji"),
    log_file: str = typer.Option(""),
    interactive: bool = typer.Option(False, "--interactive", "-i"),
) -> None:
    """Ask: python -m makpa.cli.github_demo ask "<question>"."""
    import time

    from makpa.subagents.github import create_github_graph

    _apply_output_flags(verbose, quiet or json_output, no_color, no_emoji, log_file or None)
    _startup(quiet=quiet or json_output)
    settings = get_settings()
    checkpointer = MemorySaver()
    graph = create_github_graph(checkpointer=checkpointer)
    base_thread = f"{settings.thread_id_prefix}-github"
    if interactive:
        _ask_repl(graph, base_thread, verbose, quiet, json_output)
        return
    t0 = time.monotonic()
    result = _ask_once(graph, base_thread, question, quiet=quiet or json_output)
    _report_ask(result, time.monotonic() - t0, verbose, quiet, json_output)


def _ask_once(graph: Any, thread_id: str, question: str, quiet: bool = False) -> dict[str, Any]:
    """Invoke until no gate is pending."""
    import time

    from langgraph.errors import GraphInterrupt

    from makpa.utils.interrupts import detect_interrupt
    from makpa.utils.terminal import progress_done

    config = {"configurable": {"thread_id": thread_id}}
    started = time.monotonic()
    if not quiet:
        typer.echo(f"{GITHUB_INDICATOR} working...")
    try:
        result = graph.invoke({"question": question}, config)
        if detect_interrupt(result) is not None or _is_paused(graph, config):
            result = _resolve_confirmation(graph, config, quiet=quiet)
    except GraphInterrupt:
        result = _resolve_confirmation(graph, config, quiet=quiet)
    except typer.Exit as e:
        if e.exit_code == 2 and not quiet:
            from makpa.utils.terminal import format_cancelled_timing

            typer.echo(format_cancelled_timing(time.monotonic() - started))
        raise
    except Exception as e:
        typer.echo(f"{GITHUB_INDICATOR} query failed: {e}", err=True)
        raise typer.Exit(code=1)
    if not quiet:
        typer.echo(progress_done("github", "github turn complete", time.monotonic() - started))
    return dict(result) if isinstance(result, dict) else {"answer": str(result)}


def _report_ask(
    result: dict[str, Any], total_s: float, verbose: bool, quiet: bool, json_output: bool
) -> None:
    import json as _json

    from makpa.utils.terminal import (
        clean_answer_text,
        format_cancelled_timing,
        format_timing,
        render_sectioned_result,
    )

    if isinstance(result, dict) and result.get("status") == "confirmation_required":
        typer.echo(f"{GITHUB_INDICATOR} confirmation required but not granted.")
        if not json_output:
            typer.echo(format_cancelled_timing(total_s))
        raise typer.Exit(code=2)
    raw_answer = result.get("answer", "") if isinstance(result, dict) else str(result)
    answer = clean_answer_text(raw_answer)
    structured = result.get("structured", {}) if isinstance(result, dict) else {}
    if json_output:
        typer.echo(
            _json.dumps(
                {"answer": answer, "citations": [], "actions": structured,
                 "timings": {"total_s": round(total_s, 2)}, "status": result.get("status", "ok")},
                default=str,
            )
        )
    elif quiet:
        typer.echo(answer)
        typer.echo(format_timing(total_s, {}, parallel=False))
    else:
        typer.echo(
            render_sectioned_result(answer, citations=[], structured=structured,
                                    total_s=total_s, parts={"GitHub": total_s}, verbose=verbose)
        )
    if isinstance(result, dict) and result.get("status") == "error":
        raise typer.Exit(code=1)


def _ask_repl(graph: Any, base_thread: str, verbose: bool, quiet: bool, json_output: bool) -> None:
    import time

    thread_id = base_thread
    typer.echo("makpa › interactive GitHub session (:exit, :reset, :thread <id>, :verbose)")
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
            _report_ask(result, time.monotonic() - t0, verbose, quiet, json_output)
        except typer.Exit as e:
            typer.echo(f"(turn exited with code {e.exit_code})")
        except Exception as e:
            typer.echo(f"Turn failed: {e}", err=True)


def _is_paused(graph: Any, config: dict[str, Any]) -> bool:
    """Return True when the graph is waiting at an interrupt() gate."""
    try:
        pending = graph.get_state(config).next
        return bool(pending)
    except Exception:
        return False


def _resolve_confirmation(
    graph: Any, config: dict[str, Any], quiet: bool = False
) -> dict[str, Any]:
    """Show the adaptive confirmation card and resume (or cancel) the graph."""
    from makpa.utils.interrupts import resume_with
    from makpa.utils.terminal import confirmation_indicator, format_confirmation_card

    preview = _pending_preview(graph, config)
    if quiet:
        indicator = GITHUB_INDICATOR
    else:
        typer.echo(format_confirmation_card(preview))
        indicator = confirmation_indicator(preview)
    if not typer.confirm(f"{indicator} approve this write?"):
        declined = resume_with(graph, config, {"confirm": False})
        _stream_text(declined.get("answer", "Cancelled."))
        raise typer.Exit(code=2)
    resumed: dict[str, Any] = resume_with(graph, config, {"confirm": True})
    return resumed


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


@app.command(name="list-prs")  # type: ignore[untyped-decorator]
def list_prs(
    repo: str = typer.Option(..., "--repo", help="Repository slug 'owner/name'"),
    state: str = typer.Option("open", "--state", help="open | closed | all"),
) -> None:
    """List PRs: python -m makpa.cli.github_demo list-prs --repo <owner/repo>."""
    from makpa.subagents.github.tools import github_list_prs

    _setup_logging()
    _startup()
    try:
        payload = github_list_prs.invoke({"repo": repo, "state": state})
    except Exception as e:
        typer.echo(f"{GITHUB_INDICATOR} list-prs failed: {e}", err=True)
        raise typer.Exit(code=1)
    _render_payload(payload)


@app.command()  # type: ignore[untyped-decorator]
def search(
    query: str = typer.Option(..., "--query", help="Code search query"),
    repo: str = typer.Option("", "--repo", help="Optional 'owner/name' scope"),
) -> None:
    """Search: python -m makpa.cli.github_demo search --query "<q>" --repo <owner/repo>."""
    from makpa.subagents.github.tools import github_search_code

    _setup_logging()
    _startup()
    try:
        args: dict[str, Any] = {"query": query}
        if repo:
            args["repo"] = repo
        payload = github_search_code.invoke(args)
    except Exception as e:
        typer.echo(f"{GITHUB_INDICATOR} search failed: {e}", err=True)
        raise typer.Exit(code=1)
    _render_payload(payload)


@app.command(name="create-issue")  # type: ignore[untyped-decorator]
def create_issue(
    repo: str = typer.Option(..., "--repo", help="Repository slug 'owner/name'"),
    title: str = typer.Option(..., "--title", help="Issue title"),
    body: str = typer.Option("", "--body", help="Issue body"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Create an issue (confirmation-gated, like the interrupt() node)."""
    from makpa.subagents.github.tools import github_create_issue

    _setup_logging()
    _startup()
    _boxed(
        "Create GitHub issue (confirmation gate)",
        [f"repo: {repo}", f"title: {title}", f"body: {body[:120]}"],
    )
    if not yes and not typer.confirm(f"{GITHUB_INDICATOR} create this issue?"):
        typer.echo("Aborted.")
        raise typer.Exit(code=2)
    try:
        payload = github_create_issue.invoke({"repo": repo, "title": title, "body": body})
    except Exception as e:
        typer.echo(f"{GITHUB_INDICATOR} create-issue failed: {e}", err=True)
        raise typer.Exit(code=1)
    _render_payload(payload)


def _render_payload(payload: Any) -> None:
    import json as _json

    if isinstance(payload, dict):
        _stream_text(f"status: {payload.get('status', '?')}")
        for key, value in payload.items():
            if key in ("status", "tool"):
                continue
            rendered = (
                _json.dumps(value, default=str) if isinstance(value, (dict, list)) else str(value)
            )
            typer.echo(f"{GITHUB_INDICATOR} {key}: {rendered}")
        if payload.get("status") == "error":
            raise typer.Exit(code=1)
    else:
        _stream_text(str(payload))


def main() -> None:
    """Entry point."""
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
