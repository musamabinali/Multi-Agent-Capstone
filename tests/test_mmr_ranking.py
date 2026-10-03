"""P1-MMR-1 + P1-DATA-1: multi-chunk corpus tests.

Uses a hermetic Chroma Local store in a temp directory with real
HuggingFace embeddings so MMR ranking is genuinely exercised.
"""

from __future__ import annotations

import os

import pytest
from langchain_core.documents import Document

TOPICS = [
    ("langgraph agents supervision", "The supervisor routes queries to sub-agents. "),
    ("vector stores embeddings pinecone", "Pinecone serverless hosts embeddings. "),
    ("retrieval mmr ranking diversity", "MMR balances similarity and diversity. "),
    ("github pull requests issues", "Pull request review starts with listing PRs. "),
    ("google calendar gmail scheduling", "Calendar scheduling checks availability. "),
]


def _corpus(n_per_topic: int = 8) -> list[Document]:
    docs: list[Document] = []
    idx = 0
    for topic, sentence in TOPICS:
        for i in range(n_per_topic):
            docs.append(
                Document(
                    page_content=(
                        f"Document {idx} about {topic}. {sentence * 12}"
                        f" Variant {i} adds extra detail paragraph {i}."
                    ),
                    metadata={"source": "corpus.pdf", "page": idx, "chunk_index": idx},
                )
            )
            idx += 1
    return docs


@pytest.fixture()
def mmr_store(tmp_path):
    from makpa.vectorstore.chroma_local import ChromaLocalVectorStore

    store = ChromaLocalVectorStore(
        persist_directory=str(tmp_path / "chroma"), collection_name="mmr-test"
    )
    docs = _corpus()
    ids = [f"doc-{i:04d}" for i in range(len(docs))]
    store.add_documents(docs, ids=ids)
    assert len(docs) >= 30
    yield store
    try:
        store.delete_collection()
    except Exception:
        pass


def test_mmr_reranks_ambiguous_query(mmr_store):
    """MMR with max diversity must order differently than similarity-like MMR."""
    query = "agents teams and shared project workflows"
    sim_like = mmr_store.similarity_search_with_mmr(
        query, k=5, fetch_k=20, lambda_mult=1.0
    )
    diverse = mmr_store.similarity_search_with_mmr(
        query, k=5, fetch_k=20, lambda_mult=0.0
    )
    assert len(sim_like) == 5
    assert len(diverse) == 5
    order_sim = [d.metadata["chunk_index"] for d, _ in sim_like]
    order_div = [d.metadata["chunk_index"] for d, _ in diverse]
    assert order_sim != order_div
    # Score join attaches floats for every MMR hit.
    assert all(isinstance(score, float) for _, score in diverse)


def test_mmr_respects_k_and_fetch_k(mmr_store):
    out = mmr_store.similarity_search_with_mmr("scheduling", k=3, fetch_k=10)
    assert len(out) == 3


def test_sample_pdf_has_ten_pages_and_thirty_chunks(tmp_path):
    """P1-DATA-1: the bundled sample PDF yields >=30 chunks on ingest."""
    from unittest.mock import patch

    from pypdf import PdfReader

    from makpa.config import get_settings
    from makpa.rag.ingestion import ingest_pdf
    from makpa.vectorstore.chroma_local import ChromaLocalVectorStore

    settings = get_settings()
    pdf_path = settings.sample_pdf_path
    assert os.path.exists(pdf_path), f"sample PDF missing: {pdf_path}"
    assert len(PdfReader(pdf_path).pages) >= 10

    store = ChromaLocalVectorStore(
        persist_directory=str(tmp_path / "chroma-data"), collection_name="data-test"
    )
    with patch("makpa.rag.ingestion.create_vector_store", return_value=store):
        result = ingest_pdf(pdf_path=pdf_path)
    assert result.chunks_created >= 30
