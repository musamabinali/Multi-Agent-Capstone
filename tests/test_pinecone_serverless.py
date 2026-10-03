"""P1-PINE-1: Pinecone serverless verification (mocked SDK).

Decision under test: pinecone 7.3.0 ``ServerlessSpec`` path works, but the
SDK is old, so Chroma HTTP is the primary hosted store and Pinecone is a
documented serverless-only swap.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch


def _make_store(index_exists: bool = False):
    from makpa.vectorstore.pinecone import PineconeVectorStore

    store = PineconeVectorStore.__new__(PineconeVectorStore)
    store._api_key = "test-key"
    store._index_name = "makpa-rag"
    store._cloud = "aws"
    store._region = "us-east-1"
    pc = MagicMock()
    existing = [MagicMock(name="makpa-rag")] if index_exists else []
    for m in existing:
        m.name = "makpa-rag"
    pc.list_indexes.return_value = existing
    store._pc = pc
    store._embeddings = None
    store._vectorstore = None
    return store, pc


def test_serverless_spec_used_on_create():
    store, pc = _make_store(index_exists=False)
    store._ensure_index_exists()
    assert pc.create_index.called
    kwargs = pc.create_index.call_args.kwargs
    assert kwargs["name"] == "makpa-rag"
    assert kwargs["metric"] == "cosine"
    spec = kwargs["spec"]
    assert type(spec).__name__ == "ServerlessSpec"
    assert spec.cloud == "aws" and spec.region == "us-east-1"


def test_existing_index_skips_create():
    store, pc = _make_store(index_exists=True)
    store._ensure_index_exists()
    assert not pc.create_index.called


def test_pinecone_delete_and_info_paths():
    store, pc = _make_store(index_exists=True)
    store.delete_collection()
    pc.delete_index.assert_called_once_with("makpa-rag")

    stats = MagicMock(total_vector_count=75, dimension=384)
    pc.Index.return_value.describe_index_stats.return_value = stats
    info = store.collection_info()
    assert info["type"] == "pinecone"
    assert info["total_vectors"] == 75

    pc.Index.side_effect = RuntimeError("down")
    info = store.collection_info()
    assert "error" in info

    pc.delete_index.side_effect = RuntimeError("down")
    try:
        store.delete_collection()
        raised = False
    except RuntimeError:
        raised = True
    assert raised


def test_pinecone_lazy_vectorstore_and_score_join_fallback():
    from langchain_core.documents import Document

    store, _ = _make_store(index_exists=True)
    fake_vs = MagicMock()
    doc = Document(page_content="hi", metadata={})
    fake_vs.max_marginal_relevance_search.return_value = [doc]
    fake_vs.similarity_search_with_score.side_effect = RuntimeError("no scores")
    with (
        patch.object(
            type(store), "_get_vectorstore", return_value=fake_vs
        ),
    ):
        out = store.similarity_search_with_mmr("q")
        assert out == [(doc, 0.0)]
        assert store.add_documents([doc]) == fake_vs.add_documents.return_value
