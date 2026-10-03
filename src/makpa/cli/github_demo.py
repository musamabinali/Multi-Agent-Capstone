"""Standalone Phase 2 CLI for the GitHub MCP sub-agent."""

from __future__ import annotations

import logging
from typing import Any

import typer
from langgraph.checkpoint.memory import MemorySaver

from makpa.config import get_settings, print_startup_banner

app = typer.Typer(help="MAKPA GitHub demo CLI (Phase 2)")

GITHUB_INDICATOR = "\U0001f419 GitHub agent"


def _setup_logging() -> None:
    import sys

    for stream in (sys.stdout, sys.stderr):
        reconfig = getattr(stream, "reconfigure", None)
        if callable(reconfig):
            try:
                reconfig(encoding="utf-8", errors="replace")
            except Exception:
                pass
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def _startup() -> None:
    """Print banner, run the model probe, and report the GitHub path."""
    from makpa.llm import probe_llm

    print_startup_banner()
    try:
        result = probe_llm()
    except RuntimeError as e:
        typer.echo(f"{GITHUB_INDICATOR} startup probe failed: {e}", err=True)
        raise typer.Exit(code=1)
    for warning in result.warnings:
        typer.echo(f"{GITHUB_INDICATOR} warning: {warning}")
    settings = get_settings()
    typer.echo(
        f"{GITHUB_INDICATOR} path: {settings.resolved_github_mcp_path} "
        f"| llm: {result.provider} ({result.model})"
    )


def _boxed(title: str, lines: list[str]) -> None:
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


@app.command()  # type: ignore[untyped-decorator]
def ask(question: str = typer.Argument(..., help="GitHub question to ask")) -> None:
    """Ask: python -m makpa.cli.github_demo ask "<question>"."""
    from langgraph.errors import GraphInterrupt

    from makpa.subagents.github import create_github_graph
    from makpa.utils.interrupts import detect_interrupt

    _setup_logging()
    _startup()
    typer.echo(f"{GITHUB_INDICATOR} thinking...")
    settings = get_settings()
    checkpointer = MemorySaver()
    graph = create_github_graph(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": f"{settings.thread_id_prefix}-github"}}
    try:
        result = graph.invoke({"question": question}, config)
        if detect_interrupt(result) is not None or _is_paused(graph, config):
            result = _resolve_confirmation(graph, config)
    except GraphInterrupt:
        result = _resolve_confirmation(graph, config)
    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"{GITHUB_INDICATOR} query failed: {e}", err=True)
        raise typer.Exit(code=1)
    # A second interrupt can surface if confirmation was deferred.
    if isinstance(result, dict) and result.get("status") == "confirmation_required":
        typer.echo(f"{GITHUB_INDICATOR} confirmation required but not granted.")
        raise typer.Exit(code=2)
    _stream_text(result.get("answer", ""))
    if result.get("status") == "error":
        raise typer.Exit(code=1)


def _is_paused(graph: Any, config: dict[str, Any]) -> bool:
    """Return True when the graph is waiting at an interrupt() gate."""
    try:
        pending = graph.get_state(config).next
        return bool(pending)
    except Exception:
        return False


def _resolve_confirmation(graph: Any, config: dict[str, Any]) -> dict[str, Any]:
    """Show the boxed payload preview and resume (or cancel) the graph."""
    from makpa.utils.interrupts import resume_with

    preview = _pending_preview(graph, config)
    lines = [f"{k}: {v}" for k, v in preview.items()]
    _boxed("Confirmation required (mutating GitHub tool)", lines)
    if not typer.confirm(f"{GITHUB_INDICATOR} approve this write?"):
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
    if isinstance(payload, dict):
        _stream_text(f"status: {payload.get('status', '?')}")
        for key, value in payload.items():
            if key in ("status", "tool"):
                continue
            typer.echo(f"{GITHUB_INDICATOR} {key}: {value}")
        if payload.get("status") == "error":
            raise typer.Exit(code=1)
    else:
        _stream_text(str(payload))


def main() -> None:
    """Entry point."""
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
