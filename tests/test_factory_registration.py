"""Flag 3: vector-store backend registration test.

Every backend must register successfully when its dependency is
installed, and a missing dependency must log a clear warning —
never a silent null.
"""

from __future__ import annotations

import logging
from unittest.mock import patch


def test_all_backends_registered_when_deps_installed():
    import makpa.vectorstore.factory as fac

    assert fac.PineconeVectorStore is not None
    assert fac.ChromaHTTPVectorStore is not None
    assert fac.ChromaLocalVectorStore is not None
    assert fac.QdrantVectorStore is not None

    from makpa.vectorstore.chroma_http import ChromaHTTPVectorStore
    from makpa.vectorstore.chroma_local import ChromaLocalVectorStore
    from makpa.vectorstore.pinecone import PineconeVectorStore
    from makpa.vectorstore.qdrant import QdrantVectorStore

    assert fac.PineconeVectorStore is PineconeVectorStore
    assert fac.ChromaHTTPVectorStore is ChromaHTTPVectorStore
    assert fac.ChromaLocalVectorStore is ChromaLocalVectorStore
    assert fac.QdrantVectorStore is QdrantVectorStore

    for cls in (
        PineconeVectorStore,
        ChromaHTTPVectorStore,
        ChromaLocalVectorStore,
        QdrantVectorStore,
    ):
        for method in (
            "add_documents",
            "similarity_search_with_mmr",
            "delete_collection",
            "collection_info",
        ):
            assert callable(getattr(cls, method)), f"{cls.__name__}.{method}"


def test_missing_dependency_logs_warning_not_silent_null(caplog):
    import makpa.vectorstore.factory as fac

    with caplog.at_level(logging.WARNING, logger="makpa.vectorstore.factory"):
        assert fac._optional_import("no_such_backend_xyz", "MissingThing") is None
    assert any(
        "MissingThing backend unavailable" in message
        for message in caplog.messages
    )


def test_factory_creators_reject_missing_backends():
    from makpa.vectorstore.factory import VectorStoreFactory

    factory = VectorStoreFactory()
    with (
        patch("makpa.vectorstore.factory.PineconeVectorStore", None),
        patch.object(
            factory,
            "_settings",
            create_settings_stub(pinecone_api_key="key"),
        ),
    ):
        assert factory._create_pinecone_store() is None


def create_settings_stub(**overrides):
    from types import SimpleNamespace

    base = {
        "pinecone_api_key": None,
        "pinecone_index_name": "makpa-rag",
        "pinecone_environment": "us-east-1",
        "pinecone_cloud": "aws",
        "pinecone_region": "us-east-1",
        "chroma_host": "localhost",
        "chroma_port": 8000,
        "qdrant_url": None,
        "qdrant_api_key": None,
        "qdrant_collection_name": "makpa-rag",
    }
    base.update(overrides)
    return SimpleNamespace(**base)
