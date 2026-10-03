"""CLI for RAG ingestion."""

from __future__ import annotations

import logging
import sys

import typer

from makpa.config import print_startup_banner
from makpa.rag.ingestion import IngestionResult, ingest_pdf

app = typer.Typer(help="RAG Ingestion CLI")


def setup_logging() -> None:
    """Setup basic logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


@app.command()  # type: ignore[untyped-decorator]
def ingest(
    pdf: str = typer.Option(
        None,
        "--pdf",
        "-p",
        help="Path to PDF file to ingest. Uses SAMPLE_PDF_PATH from config if not provided.",
    ),
    chunk_size: int = typer.Option(
        None,
        "--chunk-size",
        help="Chunk size for text splitting. Uses RAG_CHUNK_SIZE from config if not provided.",
    ),
    chunk_overlap: int = typer.Option(
        None,
        "--chunk-overlap",
        help=(
            "Chunk overlap for text splitting. "
            "Uses RAG_CHUNK_OVERLAP from config if not provided."
        ),
    ),
    loader: str = typer.Option(
        None,
        "--loader",
        help="PDF loader type (pymupdf or pypdf). Uses PDF_LOADER from config if not provided.",
    ),
) -> None:
    """Ingest a PDF into the vector store."""
    setup_logging()
    print_startup_banner()

    try:
        result: IngestionResult = ingest_pdf(
            pdf_path=pdf,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            loader_type=loader,
        )

        typer.echo("\n✅ Ingestion successful!")
        typer.echo(f"   Chunks created: {result.chunks_created}")
        typer.echo(f"   Backend: {result.backend}")
        typer.echo(f"   Duration: {result.duration_ms}ms")

    except Exception as e:
        typer.echo(f"\n❌ Ingestion failed: {e}", err=True)
        sys.exit(1)


@app.command()  # type: ignore[untyped-decorator]
def info() -> None:
    """Show vector store information."""
    setup_logging()
    print_startup_banner()

    from makpa.vectorstore import create_vector_store

    vectorstore = create_vector_store()
    info = vectorstore.collection_info()

    typer.echo("\n📊 Vector Store Info:")
    for key, value in info.items():
        typer.echo(f"   {key}: {value}")


@app.command()  # type: ignore[untyped-decorator]
def reset(
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Confirm reset without prompting"
    ),
) -> None:
    """Reset the vector store (delete all data)."""
    setup_logging()
    print_startup_banner()

    if not yes:
        confirm = typer.confirm(
            "⚠️  This will delete all data in the vector store. Continue?"
        )
        if not confirm:
            typer.echo("Aborted.")
            return

    from makpa.vectorstore import create_vector_store

    vectorstore = create_vector_store()
    vectorstore.delete_collection()
    typer.echo("✅ Vector store reset complete.")


if __name__ == "__main__":  # pragma: no cover
    app()
