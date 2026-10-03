"""Unit tests for retriever, citations, and faithfulness guard."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from langchain_core.documents import Document
from langchain_core.messages import AIMessage

from makpa.rag.retriever import (
    NO_DOCS_MESSAGE,
    format_citations,
    grounded_answer,
    retrieve_documents,
    validate_answer,
)


def _doc(text="agent content", source="sample.pdf", page=1, chunk=0):
    return Document(
        page_content=text,
        metadata={
            "source": source,
            "page": page,
            "chunk_index": chunk,
            "doc_id": "abc",
        },
    )


def test_retriever_uses_settings_and_preserves_metadata():
    fake_store = MagicMock()
    fake_store.similarity_search_with_mmr.return_value = [(_doc(), 0.9)]
    with patch("makpa.vectorstore.create_vector_store", return_value=fake_store):
        # Patch settings object attributes via get_settings mock
        results = retrieve_documents("agents", k=2, fetch_k=10, lambda_mult=0.5)
    assert len(results) == 1
    doc, score = results[0]
    assert doc.metadata["source"] == "sample.pdf"
    assert score == 0.9
    # MMR args forwarded
    _, kwargs = fake_store.similarity_search_with_mmr.call_args
    assert kwargs["k"] == 2
    assert kwargs["fetch_k"] == 10


def test_format_citations_shape():
    cites = format_citations([_doc()])
    assert cites[0]["source"] == "sample.pdf"
    assert cites[0]["page"] == 1
    assert cites[0]["chunk_id"] == 0


def test_grounded_answer_empty():
    assert grounded_answer("anything", []) == NO_DOCS_MESSAGE


def test_grounded_answer_has_citation():
    fake_llm = MagicMock()
    fake_llm.invoke.return_value = AIMessage(content="Answer without refs")
    with patch("makpa.llm.get_llm", return_value=fake_llm):
        ans = grounded_answer("what?", [_doc()])
    assert "[" in ans and "]" in ans


def test_faithfulness_guard_rejects_uncited():
    ans = validate_answer("plain answer no refs", [_doc()])
    assert "[" in ans


def test_faithfulness_guard_empty_context():
    assert validate_answer("something else", []) == NO_DOCS_MESSAGE
