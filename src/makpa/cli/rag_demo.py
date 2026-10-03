"""Standalone Phase 1 CLI for the RAG sub-agent."""

from __future__ import annotations

import typer

from makpa.config import print_startup_banner
from makpa.rag.ingestion import IngestionResult, ingest_pdf

app = typer.Typer(help="MAKPA RAG demo CLI (Phase 1)")

RAG_INDICATOR = "[RAG agent]"


def _setup_logging() -> None:
    from makpa.utils.terminal import setup_logging

    setup_logging()


def _run_startup_probe() -> None:
    """Run the model-name probe; exit non-zero when it fails fast."""
    from makpa.llm import probe_llm

    typer.echo(f"{RAG_INDICATOR} probing LLM (Gemini -> Groq -> mock)...")
    try:
        result = probe_llm()
    except RuntimeError as e:
        typer.echo(f"{RAG_INDICATOR} startup probe failed: {e}", err=True)
        raise typer.Exit(code=1)
    for warning in result.warnings:
        typer.echo(f"{RAG_INDICATOR} warning: {warning}")
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
    _setup_logging()
    print_startup_banner()
    _run_startup_probe()
    typer.echo(f"{RAG_INDICATOR} ingesting...")
    try:
        result: IngestionResult = ingest_pdf(pdf_path=pdf)
    except Exception as e:
        typer.echo(f"{RAG_INDICATOR} ingestion failed: {e}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"{RAG_INDICATOR} chunks: {result.chunks_created}")
    typer.echo(f"{RAG_INDICATOR} backend: {result.backend}")
    typer.echo(f"{RAG_INDICATOR} duration: {result.duration_ms}ms")


@app.command()  # type: ignore[untyped-decorator]
def ask(question: str = typer.Argument(..., help="Question to ask")) -> None:
    """Ask a question: python -m makpa.cli.rag_demo ask "<question>"."""
    _setup_logging()
    print_startup_banner()
    _run_startup_probe()
    typer.echo(f"{RAG_INDICATOR} thinking...")
    try:
        from makpa.rag import run_rag
    except Exception as e:
        typer.echo(f"{RAG_INDICATOR} failed to load RAG graph: {e}", err=True)
        raise typer.Exit(code=1)
    try:
        result = run_rag(question)
    except Exception as e:
        typer.echo(f"{RAG_INDICATOR} query failed: {e}", err=True)
        raise typer.Exit(code=1)
    answer = result.get("answer", "")
    citations = result.get("citations", [])
    status = result.get("status", "ok")
    # Stream the answer word by word
    for word in str(answer).split():
        typer.echo(word + " ", nl=False)
    typer.echo("")
    if citations:
        typer.echo(f"{RAG_INDICATOR} citations:")
        for c in citations:
            typer.echo(
                f"  [{c.get('source')}, page {c.get('page')}, "
                f"chunk {c.get('chunk_id')}]"
            )
    else:
        typer.echo(f"{RAG_INDICATOR} status: {status} (no citations)")
    if status == "error":
        raise typer.Exit(code=1)


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
