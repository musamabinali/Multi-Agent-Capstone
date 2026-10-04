"""Standalone Phase 1 CLI for the RAG sub-agent."""

from __future__ import annotations

import typer

from makpa.config import print_startup_banner
from makpa.rag.ingestion import IngestionResult, ingest_pdf

app = typer.Typer(help="MAKPA RAG demo CLI (Phase 1)")

RAG_INDICATOR = "[RAG agent]"


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


def _run_startup_probe(quiet: bool = False) -> None:
    """Run the model-name probe once per session; exit non-zero on fast fail."""
    from makpa.llm import probe_llm
    from makpa.utils.terminal import (
        banner_already_printed,
        fallback_notice,
        mark_banner_printed,
        verbose_enabled,
    )

    first = not banner_already_printed()
    # Banner state is owned here for rag_demo (no separate _startup).
    if first:
        mark_banner_printed()
    if first and not quiet:
        typer.echo(f"{RAG_INDICATOR} probing LLM (Gemini -> Groq -> mock)...")
    try:
        result = probe_llm()
    except RuntimeError as e:
        typer.echo(f"{RAG_INDICATOR} startup probe failed: {e}", err=True)
        raise typer.Exit(code=1)
    if first:
        if result.provider in ("groq", "mock"):
            notice = fallback_notice("Groq" if result.provider == "groq" else "mock")
            if notice and not quiet:
                typer.echo(f"{RAG_INDICATOR} {notice}")
        for warning in result.warnings:
            if verbose_enabled() or first:
                typer.echo(f"{RAG_INDICATOR} warning: {warning}", err=True)
    if first and not quiet:
        typer.echo(f"{RAG_INDICATOR} llm: {result.provider} ({result.model})")


@app.command()  # type: ignore[untyped-decorator]
def ingest(
    pdf: str = typer.Option(
        None,
        "--pdf",
        "-p",
        help="PDF path. Defaults to SAMPLE_PDF_PATH.",
    ),
) -> None:
    """Ingest a PDF: python -m makpa.cli.rag_demo ingest --pdf <path>."""
    import sys
    import time
    from contextlib import redirect_stdout

    from makpa.utils.terminal import format_timing, progress_done

    _setup_logging()
    print_startup_banner()
    _run_startup_probe()
    t0 = time.monotonic()
    typer.echo(f"{RAG_INDICATOR} ingesting...")
    try:
        # Embedding libs (tqdm) write progress bars to stdout; keep them
        # on stderr so user output stays clean and scriptable.
        with redirect_stdout(sys.stderr):
            result: IngestionResult = ingest_pdf(pdf_path=pdf)
    except Exception as e:
        typer.echo(f"{RAG_INDICATOR} ingestion failed: {e}", err=True)
        raise typer.Exit(code=1)
    elapsed = time.monotonic() - t0
    typer.echo(
        progress_done(
            "rag", f"ingested {result.chunks_created} chunks \u00b7 {result.backend}", elapsed
        )
    )
    typer.echo(format_timing(elapsed, {"RAG": elapsed}))


@app.command()  # type: ignore[untyped-decorator]
def ask(
    question: str = typer.Argument(..., help="Question to ask"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    quiet: bool = typer.Option(False, "--quiet", "-q"),
    json_output: bool = typer.Option(False, "--json"),
    no_color: bool = typer.Option(False, "--no-color"),
    no_emoji: bool = typer.Option(False, "--no-emoji"),
    log_file: str = typer.Option(""),
    interactive: bool = typer.Option(False, "--interactive", "-i"),
) -> None:
    """Ask a question: python -m makpa.cli.rag_demo ask "<question>"."""
    import time

    _apply_output_flags(verbose, quiet or json_output, no_color, no_emoji, log_file or None)
    if not (quiet or json_output):
        print_startup_banner()
    _run_startup_probe(quiet=quiet or json_output)
    if interactive:
        _ask_repl(verbose, quiet, json_output)
        return
    t0 = time.monotonic()
    result = _ask_once(question, quiet=quiet or json_output)
    _report_ask(result, time.monotonic() - t0, verbose, quiet, json_output)


def _ask_once(question: str, quiet: bool = False) -> dict[str, object]:
    """Run one RAG turn with a progress line."""
    import sys
    import time
    from contextlib import redirect_stdout

    from makpa.utils.terminal import progress_done

    if not quiet:
        typer.echo(f"{RAG_INDICATOR} working...")
    started = time.monotonic()
    try:
        from makpa.rag import run_rag
    except Exception as e:
        typer.echo(f"{RAG_INDICATOR} failed to load RAG graph: {e}", err=True)
        raise typer.Exit(code=1)
    try:
        # Embedding/model progress bars stay on stderr (see ingest).
        with redirect_stdout(sys.stderr):
            result = run_rag(question)
    except Exception as e:
        typer.echo(f"{RAG_INDICATOR} query failed: {e}", err=True)
        raise typer.Exit(code=1)
    if not quiet:
        typer.echo(progress_done("rag", "rag turn complete", time.monotonic() - started))
    return dict(result)


def _report_ask(
    result: dict[str, object], total_s: float, verbose: bool, quiet: bool, json_output: bool
) -> None:
    import json as _json

    from makpa.utils.terminal import clean_answer_text, format_timing, render_sectioned_result

    answer = clean_answer_text(str(result.get("answer", "")))
    raw_cites = result.get("citations", [])
    citations = [c for c in raw_cites if isinstance(c, dict)] if isinstance(raw_cites, list) else []
    status = str(result.get("status", "ok"))
    if json_output:
        typer.echo(
            _json.dumps(
                {"answer": answer, "citations": citations, "actions": {},
                 "timings": {"total_s": round(total_s, 2)}, "status": status},
                default=str,
            )
        )
    elif quiet:
        typer.echo(answer)
        typer.echo(format_timing(total_s, {}, parallel=False))
    else:
        _ = verbose
        typer.echo(
            render_sectioned_result(answer, citations=citations, structured={},
                                    total_s=total_s, parts={"RAG": total_s})
        )
    if status == "error":
        raise typer.Exit(code=1)


def _ask_repl(verbose: bool, quiet: bool, json_output: bool) -> None:
    import time

    typer.echo("makpa › interactive RAG session (:exit, :reset, :verbose)")
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
            typer.echo("thread reset.")
            continue
        if low == ":verbose":
            verbose = not verbose
            _setup_logging(verbose=verbose)
            typer.echo(f"verbose {'on' if verbose else 'off'}.")
            continue
        if low.startswith(":thread"):
            typer.echo("rag session uses one thread.")
            continue
        t0 = time.monotonic()
        try:
            result = _ask_once(line, quiet=quiet or json_output)
            _report_ask(result, time.monotonic() - t0, verbose, quiet, json_output)
        except typer.Exit as e:
            typer.echo(f"(turn exited with code {e.exit_code})")
        except Exception as e:
            typer.echo(f"Turn failed: {e}", err=True)


@app.command()  # type: ignore[untyped-decorator]
def info() -> None:
    """Show the current vector store."""
    _setup_logging()
    print_startup_banner()
    _run_startup_probe()
    from makpa.vectorstore import create_vector_store

    try:
        store = create_vector_store()
        details = store.collection_info()
    except Exception as e:
        typer.echo(f"{RAG_INDICATOR} info failed: {e}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"{RAG_INDICATOR} vector store:")
    for key, value in details.items():
        typer.echo(f"  {key}: {value}")


@app.command()  # type: ignore[untyped-decorator]
def reset(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Reset the vector store."""
    _setup_logging()
    print_startup_banner()
    _run_startup_probe()
    if not yes and not typer.confirm(f"{RAG_INDICATOR} delete all vectors?"):
        typer.echo("Aborted.")
        return
    from makpa.vectorstore import create_vector_store

    try:
        create_vector_store().delete_collection()
    except Exception as e:
        typer.echo(f"{RAG_INDICATOR} reset failed: {e}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"{RAG_INDICATOR} reset complete.")


def main() -> None:
    """Entry point."""
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
