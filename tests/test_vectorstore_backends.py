"""Unit tests for vector store backend implementations (mocked LangChain)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from langchain_core.documents import Document


def _doc(text="hello"):
    return Document(page_content=text, metadata={"source": "s", "page": 1})


def test_chroma_local_crud():
    from makpa.vectorstore.chroma_local import ChromaLocalVectorStore

    fake_vs = MagicMock()
    fake_vs.add_documents.return_value = ["a"]
    fake_vs.max_marginal_relevance_search.return_value = [_doc("hi")]
    fake_vs.similarity_search_with_score.return_value = [(_doc("hi"), 0.5)]
    fake_vs._collection.count.return_value = 1
    with patch.object(
        ChromaLocalVectorStore, "_get_vectorstore", return_value=fake_vs
    ):
        store = ChromaLocalVectorStore.__new__(ChromaLocalVectorStore)
        store._collection_name = "c"
        store._persist_directory = "d"
        assert store.add_documents([_doc()]) == ["a"]
        res = store.similarity_search_with_mmr("q")
        assert len(res) == 1 and res[0][1] == 0.5
        info = store.collection_info()
        assert info["total_vectors"] == 1
        store.delete_collection()
        fake_vs.delete_collection.assert_called_once()


def test_chroma_http_crud():
    from makpa.vectorstore.chroma_http import ChromaHTTPVectorStore

    fake_vs = MagicMock()
    fake_vs.add_documents.return_value = ["a"]
    fake_vs.max_marginal_relevance_search.return_value = [_doc("hi")]
    fake_vs.similarity_search_with_score.return_value = [(_doc("hi"), 0.7)]
    fake_vs._collection.count.return_value = 2
    with patch.object(ChromaHTTPVectorStore, "_get_vectorstore", return_value=fake_vs):
        store = ChromaHTTPVectorStore.__new__(ChromaHTTPVectorStore)
        store._collection_name = "c"
        store._host = "h"
        store._port = 1
        assert store.add_documents([_doc()]) == ["a"]
        res = store.similarity_search_with_mmr("q")
        assert res[0][1] == 0.7
        assert store.collection_info()["total_vectors"] == 2
        store.delete_collection()


def test_pinecone_crud():
    from makpa.vectorstore.pinecone import PineconeVectorStore

    fake_vs = MagicMock()
    fake_vs.add_documents.return_value = ["a"]
    fake_vs.max_marginal_relevance_search.return_value = [_doc("hi")]
    fake_vs.similarity_search_with_score.return_value = [(_doc("hi"), 0.9)]
    with patch.object(PineconeVectorStore, "_get_vectorstore", return_value=fake_vs):
        store = PineconeVectorStore.__new__(PineconeVectorStore)
        assert store.add_documents([_doc()]) == ["a"]
        res = store.similarity_search_with_mmr("q")
        assert res[0][1] == 0.9


def test_qdrant_crud():
    from makpa.vectorstore.qdrant import QdrantVectorStore

    fake_vs = MagicMock()
    fake_vs.add_documents.return_value = ["a"]
    fake_vs.max_marginal_relevance_search.return_value = [_doc("hi")]
    fake_vs.similarity_search_with_score.return_value = [(_doc("hi"), 0.3)]
    with patch.object(QdrantVectorStore, "_get_vectorstore", return_value=fake_vs):
        store = QdrantVectorStore.__new__(QdrantVectorStore)
        assert store.add_documents([_doc()]) == ["a"]
        res = store.similarity_search_with_mmr("q")
        assert res[0][1] == 0.3


def test_embeddings_fallback_and_cache():
    from makpa.vectorstore.embeddings import EmbeddingFactory

    f = EmbeddingFactory()
    f.clear_cache()
    fake = MagicMock()
    with patch.object(f, "_create_huggingface_embeddings", return_value=fake):
        assert f.get_embeddings_with_fallback() is fake
        # cached
        assert f.get_embeddings_with_fallback() is fake
    f.clear_cache()


def test_llm_no_key_branches():
    from makpa.llm.factory import LLMFactory

    f = LLMFactory()
    f.clear_cache()
    f._settings = MagicMock(gemini_api_key=None, groq_api_key=None)
    assert f._create_gemini_model() is None
    assert f._create_groq_model() is None
    f.clear_cache()


def test_ingest_missing_file_and_multi():
    import pytest

    from makpa.rag.ingestion import ingest_multiple_pdfs, ingest_pdf

    with pytest.raises(FileNotFoundError):
        ingest_pdf("/nonexistent/file.pdf")
    with pytest.raises(FileNotFoundError):
        ingest_multiple_pdfs(["/nonexistent/file.pdf"])
