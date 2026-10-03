"""Integration test for the RAG subgraph."""

from __future__ import annotations

from unittest.mock import patch

from langchain_core.documents import Document

from makpa.rag import create_rag_graph


def _doc(text, chunk=0):
    return Document(
        page_content=text,
        metadata={
            "source": "sample.pdf",
            "page": 1,
            "chunk_index": chunk,
            "doc_id": "abc",
        },
    )


def _run(query, docs):
    tuples = [(d, 0.9 - i * 0.1) for i, d in enumerate(docs)]
    with patch("makpa.rag.graph.retrieve_documents", return_value=tuples):
        graph = create_rag_graph()
        return dict(graph.invoke({"query": query}))


def test_rag_answer_about_agents():
    result = _run(
        "What is MAKPA?",
        [_doc("MAKPA routes queries to RAG, GitHub, and Google sub-agents.", 0)],
    )
    assert result["status"] == "ok"
    assert result["answer"]
    assert len(result["citations"]) >= 1


def test_rag_answer_about_vector_stores():
    result = _run(
        "Which vector stores are supported?",
        [_doc("Vector stores include Pinecone, ChromaDB, and Qdrant.", 1)],
    )
    assert result["status"] == "ok"
    assert "Pinecone" in result["answer"] or len(result["citations"]) >= 1


def test_rag_answer_about_langgraph():
    result = _run(
        "How does routing work?",
        [_doc("LangGraph supervisor routes queries with an intent router.", 2)],
    )
    assert result["status"] == "ok"
    assert len(result["citations"]) >= 1


def test_rag_empty_context_short_circuits():
    with patch("makpa.rag.graph.retrieve_documents", return_value=[]):
        graph = create_rag_graph()
        result = dict(graph.invoke({"query": "zzz no match qqq"}))
    assert result["status"] == "empty"
    assert "no relevant documents found" in result["answer"].lower()
