"""Unit tests for the vector store factory (all four branches, mocked)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from makpa.vectorstore import clear_vector_store_cache
from makpa.vectorstore.factory import VectorStoreFactory


def _factory():
    f = VectorStoreFactory()
    f.clear_cache()
    return f


def test_pinecone_branch():
    f = _factory()
    fake = MagicMock()
    with patch.object(f, "_create_pinecone_store", return_value=fake):
        assert f.get_store("pinecone") is fake
    f.clear_cache()


def test_chroma_http_branch():
    f = _factory()
    fake = MagicMock()
    with patch.object(f, "_create_chroma_http_store", return_value=fake):
        assert f.get_store("chroma_http") is fake
    f.clear_cache()


def test_chroma_local_branch():
    f = _factory()
    fake = MagicMock()
    with patch.object(f, "_create_chroma_local_store", return_value=fake):
        assert f.get_store("chroma_local") is fake
    f.clear_cache()


def test_qdrant_branch():
    f = _factory()
    fake = MagicMock()
    with patch.object(f, "_create_qdrant_store", return_value=fake):
        assert f.get_store("qdrant") is fake
    f.clear_cache()


def test_fallback_chain():
    f = _factory()
    fake = MagicMock()
    with (
        patch.object(f, "_create_pinecone_store", return_value=None),
        patch.object(f, "_create_chroma_http_store", return_value=None),
        patch.object(f, "_create_chroma_local_store", return_value=fake),
    ):
        assert f.get_store("pinecone") is fake
    f.clear_cache()
    clear_vector_store_cache()
