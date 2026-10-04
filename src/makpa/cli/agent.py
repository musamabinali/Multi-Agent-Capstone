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


def _startup(quiet: bool = False) -> None:
    """Banner, probe, and indicator roll-call (once per session)."""
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
        typer.echo("\U0001f916 Supervisor probing LLM (Gemini -> Groq -> mock)...")
    try:
        result = probe_llm()
    except RuntimeError as e:
        typer.echo(f"\U0001f916 Supervisor startup probe failed: {e}", err=True)
        raise typer.Exit(code=1)
    if first:
        if result.provider in ("groq", "mock"):
            notice = fallback_notice("Groq" if result.provider == "groq" else "mock")
            if notice and not quiet:
                typer.echo(f"\U0001f916 Supervisor {notice}")
        for warning in result.warnings:
            if verbose_enabled() or first:
                typer.echo(f"\U0001f916 Supervisor warning: {warning}", err=True)
    settings = get_settings()
    if first and not quiet:
        typer.echo(
            f"\U0001f916 Supervisor ready | agents: rag+github+google "
            f"| github={settings.resolved_github_mcp_path} "
            f"google={settings.resolved_google_mcp_mode.value} "
            f"oauth={settings.resolved_google_oauth_state} "
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


def _indicator_for_preview(preview: dict[str, Any]) -> str:
    """Attribute an interrupt preview to its sub-agent (emoji matches tools)."""
    from makpa.utils.terminal import confirmation_indicator

    return str(confirmation_indicator(preview))


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


def _run_once(
    graph: Any, config: dict[str, Any], payload: dict[str, Any], quiet: bool = False
) -> dict[str, Any]:
    """Invoke (or resume) the supervisor until no gate is pending."""
    import sys
    import time
    from contextlib import redirect_stdout

    from langgraph.errors import GraphInterrupt

    from makpa.utils.interrupts import detect_interrupt

    started = time.monotonic()
    try:
        try:
            # Embedding/model progress bars stay on stderr (see rag ingest).
            with redirect_stdout(sys.stderr):
                result = graph.invoke(payload, config)
        except GraphInterrupt:
            result = {"__interrupt__": [True]}
        for _ in range(MAX_RESUMES):
            pending = detect_interrupt(result) is not None or _is_paused(graph, config)
            if not pending:
                break
            result = _resolve_confirmation(graph, config, quiet=quiet)
    except typer.Exit as e:
        if e.exit_code == 2 and not quiet:
            from makpa.utils.terminal import format_cancelled_timing

            typer.echo(format_cancelled_timing(time.monotonic() - started))
        raise
    return dict(result) if isinstance(result, dict) else {"answer": str(result)}


def _resolve_confirmation(
    graph: Any, config: dict[str, Any], quiet: bool = False
) -> dict[str, Any]:
    """Card gate prompt with rollback support for gate 2."""
    from makpa.utils.interrupts import resume_with
    from makpa.utils.terminal import format_confirmation_card

    preview = _pending_preview(graph, config)
    indicator = _indicator_for_preview(preview)
    gate = preview.get("gate", "?")
    if not quiet:
        typer.echo(format_confirmation_card(preview))
        typer.echo(f"prompt: {indicator} approve?")
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


def _report(
    result: dict[str, Any],
    total_s: float = 0.0,
    verbose: bool = False,
    quiet: bool = False,
    json_output: bool = False,
) -> int:
    """Sectioned Answer/Citations/Actions + timing footer. Returns exit code."""
    import json as _json

    from makpa.utils.terminal import (
        clean_answer_text,
        format_cancelled_timing,
        format_timing,
        render_sectioned_result,
    )

    agents = result.get("next", [])
    parallel = len(agents) > 1 if isinstance(agents, list) else False
    if agents and not (quiet or json_output):
        typer.echo(f"\U0001f916 Supervisor routed to: {', '.join(agents)}")
    outputs = result.get("agent_outputs", {})
    merged_cites: list[dict[str, Any]] = []
    merged_structured: dict[str, Any] = {}
    answer_parts: list[str] = []
    for name in ("rag_agent", "github_agent", "google_agent"):
        raw = outputs.get(name) if isinstance(outputs, dict) else None
        if raw is None:
            continue
        import json

        try:
            data = json.loads(raw)
        except (ValueError, TypeError):
            data = {"answer": str(raw), "status": "error"}
        if not isinstance(data, dict):
            continue
        ans = clean_answer_text(str(data.get("answer", "")))
        if ans:
            answer_parts.append(ans)
        for cite in data.get("citations", []) or []:
            if isinstance(cite, dict):
                merged_cites.append(cite)
        struct = data.get("structured")
        if isinstance(struct, dict):
            for key, value in struct.items():
                if key not in merged_structured:
                    merged_structured[key] = value
    final_answer = "\n\n".join(answer_parts) or clean_answer_text(str(result.get("answer", "")))
    status = result.get("status", "ok")
    confirmations = result.get("confirmations", {})
    if isinstance(confirmations, dict):
        waiting = [name for name, done in confirmations.items() if not done]
        if waiting and not (quiet or json_output):
            typer.echo(f"\U0001f916 Supervisor: awaiting confirmation: {', '.join(waiting)}")
    if status == "confirmation_required":
        if not json_output:
            typer.echo("\U0001f916 Supervisor: confirmation not granted.")
            typer.echo(format_cancelled_timing(total_s))
        raise typer.Exit(code=2)
    if status in ("cancelled",):
        if not json_output:
            typer.echo(final_answer or "Cancelled.")
            typer.echo(format_cancelled_timing(total_s))
        raise typer.Exit(code=2)
    parts = {"total": total_s} if total_s else {}
    if json_output:
        typer.echo(
            _json.dumps(
                {"answer": final_answer, "citations": merged_cites,
                 "actions": merged_structured, "timings": {"total_s": round(total_s, 2)},
                 "status": status},
                default=str,
            )
        )
    elif quiet:
        typer.echo(final_answer)
        typer.echo(format_timing(total_s, {}, parallel=False))
    else:
        typer.echo(
            render_sectioned_result(final_answer, citations=merged_cites,
                                    structured=merged_structured, total_s=total_s,
                                    parts={"supervisor": total_s} if total_s else {},
                                    parallel=parallel, verbose=verbose)
        )
        _ = parts
    if status == "error":
        raise typer.Exit(code=1)
    return 0


@app.callback()  # type: ignore[untyped-decorator]
def main(
    query: str = typer.Argument(None, help="Natural-language query (one-shot)"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Multi-turn REPL"),
    thread: str = typer.Option("", "--thread", "-t", help="Named thread id"),
    mode: str = typer.Option("", "--mode", "-m", help="Mode override: demo|free|live"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="INFO logs on stderr"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Answer + timing only"),
    json_output: bool = typer.Option(False, "--json", help="Single JSON object on stdout"),
    no_color: bool = typer.Option(False, "--no-color", help="Disable ANSI colors"),
    no_emoji: bool = typer.Option(False, "--no-emoji", help="Disable emoji"),
    log_file: str = typer.Option("", "--log-file", help="Full logs to PATH"),
) -> None:
    """Run the MAKPA supervisor: one-shot, interactive, or threaded."""
    import time

    from makpa.supervisor import create_supervisor_graph

    _apply_output_flags(verbose, quiet or json_output, no_color, no_emoji, log_file or None)
    if mode:
        _apply_mode_override(mode)
    _startup(quiet=quiet or json_output)
    settings = get_settings()
    thread_id = thread.strip() or f"{settings.thread_id_prefix}-main"
    checkpointer = MemorySaver()
    graph = create_supervisor_graph(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": thread_id}}
    try:
        if interactive or not query:
            _repl(graph, config, verbose=verbose, quiet=quiet, json_output=json_output)
            return
        t0 = time.monotonic()
        result = _run_once(graph, config, _initial_state(query), quiet=quiet or json_output)
        code = _report(result, time.monotonic() - t0, verbose, quiet, json_output)
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


def _repl(
    graph: Any,
    config: dict[str, Any],
    verbose: bool = False,
    quiet: bool = False,
    json_output: bool = False,
) -> None:
    """Warm multi-turn REPL sharing one thread's memory."""
    import copy
    import time

    base_config = copy.deepcopy(config)
    typer.echo("makpa › interactive supervisor session (:exit, :reset, :thread <id>, :verbose)")
    while True:
        try:
            query = input("makpa › ").strip()
        except (EOFError, KeyboardInterrupt):
            typer.echo("")
            return
        if not query:
            continue
        low = query.lower()
        if low in (":exit", ":quit", "exit", "quit"):
            return
        if low == ":reset":
            config["configurable"]["thread_id"] = base_config["configurable"]["thread_id"]
            typer.echo("thread reset.")
            continue
        if low.startswith(":thread"):
            parts = query.split(None, 1)
            if len(parts) == 2 and parts[1].strip():
                config["configurable"]["thread_id"] = parts[1].strip()
                typer.echo(f"thread: {parts[1].strip()}")
            continue
        if low == ":verbose":
            verbose = not verbose
            _setup_logging(verbose=verbose)
            typer.echo(f"verbose {'on' if verbose else 'off'}.")
            continue
        try:
            t0 = time.monotonic()
            result = _run_once(graph, config, _initial_state(query), quiet=quiet or json_output)
            _report(result, time.monotonic() - t0, verbose, quiet, json_output)
        except typer.Exit as e:
            typer.echo(f"(turn exited with code {e.exit_code})")
        except Exception as e:
            typer.echo(f"Turn failed: {e}", err=True)


if __name__ == "__main__":  # pragma: no cover
    app()
