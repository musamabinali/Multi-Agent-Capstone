"""Unit tests for the ingestion pipeline, incl. idempotency."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

from langchain_core.documents import Document

from makpa.rag.ingestion import (
    _attach_metadata,
    _compute_file_hash,
    _generate_chunk_id,
    ingest_pdf,
)

SAMPLE_PDF = os.path.join(os.path.dirname(__file__), "..", "data", "sample.pdf")


def test_compute_file_hash_stable():
    h1 = _compute_file_hash(os.path.abspath(SAMPLE_PDF))
    h2 = _compute_file_hash(os.path.abspath(SAMPLE_PDF))
    assert h1 == h2
    assert len(h1) == 64


def test_generate_chunk_id_deterministic():
    assert _generate_chunk_id("abc123", 1) == _generate_chunk_id("abc123", 1)
    assert _generate_chunk_id("abc123", 1) != _generate_chunk_id("abc123", 2)


def test_attach_metadata():
    docs = [Document(page_content="hello", metadata={"page": 3})]
    out = _attach_metadata(docs, "sample.pdf", "f" * 64)
    assert out[0].metadata["source"] == "sample.pdf"
    assert out[0].metadata["page"] == 3
    assert out[0].metadata["chunk_index"] == 0
    assert "ingested_at" in out[0].metadata


def test_ingest_twice_idempotent_ids():
    """Ingesting twice must produce identical deterministic chunk IDs."""
    fake_store = MagicMock()
    fake_store.collection_info.return_value = {"type": "fake"}
    fake_store.add_documents.return_value = ["id1"]

    with patch("makpa.rag.ingestion.create_vector_store", return_value=fake_store):
        r1 = ingest_pdf(os.path.abspath(SAMPLE_PDF))
        r2 = ingest_pdf(os.path.abspath(SAMPLE_PDF))
    assert r1.chunks_created > 0
    assert r1.chunks_created == r2.chunks_created
    assert r1.document_ids == r2.document_ids
    # Same deterministic IDs -> no duplicates on re-ingest
    assert len(set(r1.document_ids)) == len(r1.document_ids)
