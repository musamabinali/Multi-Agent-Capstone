"""PDF ingestion pipeline for MAKPA RAG sub-agent.

Handles loading PDFs, splitting text, embedding, and storing in vector store
with idempotent re-ingestion support.
"""

from __future__ import annotations

import hashlib
import logging
import os
import time
from dataclasses import dataclass
from typing import Any

from langchain_community.document_loaders import PyMuPDFLoader, PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from makpa.config import get_settings
from makpa.vectorstore import create_vector_store

logger = logging.getLogger(__name__)


@dataclass
class IngestionResult:
    """Result of PDF ingestion."""

    chunks_created: int
    chunks_skipped: int
    backend: str
    duration_ms: int
    document_ids: list[str]


def _get_loader(pdf_path: str, loader_type: str = "pymupdf") -> Any:
    """Get the appropriate PDF loader."""
    if loader_type == "pymupdf":
        return PyMuPDFLoader(pdf_path)
    elif loader_type == "pypdf":
        return PyPDFLoader(pdf_path)
    else:
        logger.warning("Unknown loader type %s, defaulting to pymupdf", loader_type)
        return PyMuPDFLoader(pdf_path)


def _compute_file_hash(pdf_path: str) -> str:
    """Compute SHA256 hash of the PDF file."""
    hasher = hashlib.sha256()
    with open(pdf_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _generate_chunk_id(file_hash: str, chunk_index: int) -> str:
    """Generate a deterministic chunk ID from file hash and chunk index."""
    return f"{file_hash[:16]}-{chunk_index:04d}"


def _attach_metadata(
    documents: list[Document],
    source_filename: str,
    file_hash: str,
) -> list[Document]:
    """Attach metadata to each document chunk."""
    for i, doc in enumerate(documents):
        doc.metadata.update(
            {
                "source": source_filename,
                "page": doc.metadata.get("page", i + 1),
                "chunk_index": i,
                "doc_id": file_hash[:16],
                "ingested_at": int(time.time()),
            }
        )
    return documents


def ingest_pdf(
    pdf_path: str | None = None,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
    loader_type: str | None = None,
) -> IngestionResult:
    """Ingest a PDF into the vector store.

    Args:
        pdf_path: Path to the PDF file. If None, uses SAMPLE_PDF_PATH from settings.
        chunk_size: Size of text chunks. If None, uses RAG_CHUNK_SIZE from settings.
        chunk_overlap: Overlap between chunks. If None, uses RAG_CHUNK_OVERLAP from settings.
        loader_type: PDF loader type ('pymupdf' or 'pypdf'). If None, uses PDF_LOADER from settings.

    Returns:
        IngestionResult with details about the ingestion.
    """
    start_time = time.time()
    settings = get_settings()

    # Resolve parameters from settings if not provided
    pdf_path = pdf_path or settings.sample_pdf_path
    chunk_size = chunk_size or settings.rag_chunk_size
    chunk_overlap = chunk_overlap or settings.rag_chunk_overlap
    loader_type = loader_type or settings.pdf_loader

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    logger.info("Starting PDF ingestion: %s", pdf_path)

    # Compute file hash for idempotency
    file_hash = _compute_file_hash(pdf_path)
    logger.debug("File hash: %s", file_hash)

    # Load PDF
    loader = _get_loader(pdf_path, loader_type)
    documents = loader.load()
    logger.info("Loaded %d pages from PDF", len(documents))

    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = text_splitter.split_documents(documents)
    logger.info("Split into %d chunks", len(chunks))

    # Attach metadata
    source_filename = os.path.basename(pdf_path)
    chunks = _attach_metadata(chunks, source_filename, file_hash)

    # Generate deterministic IDs for idempotent upsert
    ids = [_generate_chunk_id(file_hash, i) for i in range(len(chunks))]

    # Get vector store
    vectorstore = create_vector_store()

    # Check which chunks already exist (by ID)
    # For simplicity, we'll just upsert all - the vector store handles duplicates
    # In a production system, we'd check existing IDs first
    logger.info("Upserting %d chunks to vector store", len(chunks))
    vectorstore.add_documents(chunks, ids=ids)

    # Get backend info
    backend_info = vectorstore.collection_info()
    backend_type = backend_info.get("type", "unknown")

    duration_ms = int((time.time() - start_time) * 1000)

    result = IngestionResult(
        chunks_created=len(chunks),
        chunks_skipped=0,  # Could be enhanced to track skipped duplicates
        backend=backend_type,
        duration_ms=duration_ms,
        document_ids=ids,
    )

    logger.info(
        "Ingestion complete: %d chunks, backend=%s, duration=%dms",
        result.chunks_created,
        result.backend,
        result.duration_ms,
    )

    return result


def ingest_multiple_pdfs(pdf_paths: list[str]) -> list[IngestionResult]:
    """Ingest multiple PDFs sequentially."""
    results = []
    for path in pdf_paths:
        try:
            result = ingest_pdf(path)
            results.append(result)
        except Exception as e:
            logger.error("Failed to ingest %s: %s", path, e)
            raise
    return results


__all__ = [
    "ingest_pdf",
    "ingest_multiple_pdfs",
    "IngestionResult",
]
