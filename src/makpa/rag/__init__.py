"""RAG sub-agent for MAKPA.

Provides PDF ingestion, retrieval, and RAG subgraph functionality.
"""

from .graph import create_rag_graph, run_rag
from .ingestion import IngestionResult, ingest_multiple_pdfs, ingest_pdf
from .retriever import (
    NO_DOCS_MESSAGE,
    format_citations,
    grounded_answer,
    retrieve_documents,
    validate_answer,
)

__all__ = [
    "ingest_pdf",
    "ingest_multiple_pdfs",
    "IngestionResult",
    "retrieve_documents",
    "format_citations",
    "grounded_answer",
    "validate_answer",
    "NO_DOCS_MESSAGE",
    "create_rag_graph",
    "run_rag",
]
