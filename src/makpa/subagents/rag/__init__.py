"""RAG sub-agent for MAKPA.

Thin wrapper over makpa.rag so the supervisor (Phase 4) can import
from a stable sub-agent path.
"""

from makpa.rag.graph import create_rag_graph, run_rag
from makpa.rag.ingestion import IngestionResult, ingest_multiple_pdfs, ingest_pdf
from makpa.rag.retriever import retrieve_documents

ingest_documents = ingest_pdf

__all__ = [
    "create_rag_graph",
    "run_rag",
    "ingest_documents",
    "ingest_multiple_pdfs",
    "ingest_pdf",
    "retrieve_documents",
    "IngestionResult",
]
