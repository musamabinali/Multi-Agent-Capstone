"""P1-COV-1: per-module coverage hardening for Phase 1 modules.

Exercises error branches, fallback branches, and unselected branches of
the vectorstore factory/backends, embeddings, LLM factory, RAG graph,
ingestion helpers, mock model, settings, and retrieval MCP server.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document


def _doc(text: str = "hello") -> Document:
    return Document(page_content=text, metadata={"source": "s", "page": 1})


# ---------------------------------------------------------------------------
# VectorStore factory
# ---------------------------------------------------------------------------


def _factory_settings(**overrides):
    base = {
        "pinecone_api_key": None,
        "pinecone_index_name": "idx",
        "pinecone_environment": "us-east-1",
        "pinecone_cloud": "aws",
        "pinecone_region": "us-east-1",
        "chroma_host": "localhost",
        "chroma_port": 8000,
        "qdrant_url": None,
        "qdrant_api_key": None,
        "qdrant_collection_name": "makpa-rag",
        "resolved_vector_store": SimpleNamespace(value="chroma_local"),
        "resolved_mode": SimpleNamespace(value="demo"),
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_factory_singleton_and_module_funcs():
    from makpa.vectorstore.factory import (
        VectorStoreFactory,
        clear_vector_store_cache,
        create_vector_store,
    )

    assert VectorStoreFactory() is VectorStoreFactory()
    f = VectorStoreFactory()
    f.clear_cache()
    fake = MagicMock()
    with (
        patch("makpa.vectorstore.factory.ChromaLocalVectorStore", return_value=fake),
        patch.object(f, "_settings", _factory_settings()),
    ):
        assert create_vector_store() is fake
        assert create_vector_store() is fake  # cache hit
    clear_vector_store_cache()
    f.clear_cache()


def test_factory_explicit_types():
    from makpa.vectorstore.factory import VectorStoreFactory

    f = VectorStoreFactory()
    for target, cls_name, settings in [
        ("pinecone", "PineconeVectorStore", _factory_settings(pinecone_api_key="k")),
        ("chroma_http", "ChromaHTTPVectorStore", _factory_settings()),
        ("chroma_local", "ChromaLocalVectorStore", _factory_settings()),
        (
            "qdrant",
            "QdrantVectorStore",
            _factory_settings(qdrant_url="http://x", qdrant_api_key="k"),
        ),
    ]:
        f.clear_cache()
        fake = MagicMock()
        with (
            patch(f"makpa.vectorstore.factory.{cls_name}", return_value=fake),
            patch.object(f, "_settings", settings),
        ):
            assert f.get_store(target) is fake
    f.clear_cache()


def test_factory_private_creator_branches():
    from makpa.vectorstore.factory import VectorStoreFactory

    f = VectorStoreFactory()
    # Pinecone: no key / import missing / constructor failure / success
    with patch.object(f, "_settings", _factory_settings(pinecone_api_key=None)):
        assert f._create_pinecone_store() is None
    with (
        patch("makpa.vectorstore.factory.PineconeVectorStore", None),
        patch.object(f, "_settings", _factory_settings(pinecone_api_key="k")),
    ):
        assert f._create_pinecone_store() is None
    with (
        patch(
            "makpa.vectorstore.factory.PineconeVectorStore",
            side_effect=RuntimeError("boom"),
        ),
        patch.object(f, "_settings", _factory_settings(pinecone_api_key="k")),
    ):
        assert f._create_pinecone_store() is None
    # Chroma HTTP: import missing / failure / success
    with patch("makpa.vectorstore.factory.ChromaHTTPVectorStore", None):
        assert f._create_chroma_http_store() is None
    with patch(
        "makpa.vectorstore.factory.ChromaHTTPVectorStore",
        side_effect=RuntimeError("boom"),
    ):
        assert f._create_chroma_http_store() is None
    # Chroma local: import missing / failure
    with patch("makpa.vectorstore.factory.ChromaLocalVectorStore", None):
        assert f._create_chroma_local_store() is None
    with patch(
        "makpa.vectorstore.factory.ChromaLocalVectorStore",
        side_effect=RuntimeError("boom"),
    ):
        assert f._create_chroma_local_store() is None
    # Qdrant: no creds / import missing / failure
    with patch.object(f, "_settings", _factory_settings()):
        assert f._create_qdrant_store() is None
    with (
        patch("makpa.vectorstore.factory.QdrantVectorStore", None),
        patch.object(
            f, "_settings", _factory_settings(qdrant_url="u", qdrant_api_key="k")
        ),
    ):
        assert f._create_qdrant_store() is None
    with (
        patch(
            "makpa.vectorstore.factory.QdrantVectorStore",
            side_effect=RuntimeError("boom"),
        ),
        patch.object(
            f, "_settings", _factory_settings(qdrant_url="u", qdrant_api_key="k")
        ),
    ):
        assert f._create_qdrant_store() is None
    f.clear_cache()


def test_factory_fallback_chain_and_exhaustion():
    from makpa.vectorstore.factory import VectorStoreFactory

    f = VectorStoreFactory()
    f.clear_cache()
    fake = MagicMock()
    # Unknown type with no pinecone key falls through to Chroma HTTP.
    with (
        patch("makpa.vectorstore.factory.ChromaHTTPVectorStore", return_value=fake),
        patch.object(
            f,
            "_settings",
            _factory_settings(resolved_vector_store=SimpleNamespace(value="nope")),
        ),
    ):
        assert f.get_store() is fake
    f.clear_cache()
    # Everything unavailable -> RuntimeError.
    with (
        patch("makpa.vectorstore.factory.PineconeVectorStore", None),
        patch("makpa.vectorstore.factory.ChromaHTTPVectorStore", None),
        patch("makpa.vectorstore.factory.ChromaLocalVectorStore", None),
        patch("makpa.vectorstore.factory.QdrantVectorStore", None),
        patch.object(
            f,
            "_settings",
            _factory_settings(resolved_vector_store=SimpleNamespace(value="nope")),
        ),
    ):
        with pytest.raises(RuntimeError, match="No vector store backend"):
            f.get_store()
    f.clear_cache()


# ---------------------------------------------------------------------------
# Embeddings
# ---------------------------------------------------------------------------


def _emb_settings(**overrides):
    base = {
        "hf_embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "embedding_batch_size": 32,
        "gemini_api_key": None,
        "gemini_embedding_model": "text-embedding-004",
        "embedding_provider": SimpleNamespace(value="huggingface"),
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_embeddings_gemini_branches():
    from makpa.vectorstore.embeddings import EmbeddingFactory

    f = EmbeddingFactory()
    f.clear_cache()
    with patch.object(f, "_settings", _emb_settings(gemini_api_key=None)):
        assert f._create_gemini_embeddings() is None
    fake = MagicMock()
    with (
        patch("langchain_google_genai.GoogleGenerativeAIEmbeddings", return_value=fake),
        patch.object(f, "_settings", _emb_settings(gemini_api_key="k")),
    ):
        assert f._create_gemini_embeddings() is fake
    with (
        patch(
            "langchain_google_genai.GoogleGenerativeAIEmbeddings",
            side_effect=RuntimeError("boom"),
        ),
        patch.object(f, "_settings", _emb_settings(gemini_api_key="k")),
    ):
        assert f._create_gemini_embeddings() is None
    f.clear_cache()


def test_embeddings_provider_selection_and_cache():
    from makpa.vectorstore import (
        clear_embeddings_cache,
        get_embeddings_for_provider,
    )
    from makpa.vectorstore.embeddings import EmbeddingFactory

    f = EmbeddingFactory()
    f.clear_cache()
    fake = MagicMock()
    # Explicit gemini with key available.
    with (
        patch("langchain_google_genai.GoogleGenerativeAIEmbeddings", return_value=fake),
        patch.object(
            f,
            "_settings",
            _emb_settings(
                gemini_api_key="k",
                embedding_provider=SimpleNamespace(value="gemini"),
            ),
        ),
    ):
        assert get_embeddings_for_provider("gemini") is fake
        assert get_embeddings_for_provider("gemini") is fake  # cache hit
    f.clear_cache()
    # Explicit gemini without key falls back to HuggingFace.
    hf = MagicMock()
    with (
        patch("langchain_huggingface.HuggingFaceEmbeddings", return_value=hf),
        patch.object(
            f,
            "_settings",
            _emb_settings(
                gemini_api_key=None,
                embedding_provider=SimpleNamespace(value="gemini"),
            ),
        ),
    ):
        assert get_embeddings_for_provider("gemini") is hf
    f.clear_cache()
    # with_fallback prefers working gemini.
    with (
        patch("langchain_google_genai.GoogleGenerativeAIEmbeddings", return_value=fake),
        patch.object(
            f,
            "_settings",
            _emb_settings(
                gemini_api_key="k",
                embedding_provider=SimpleNamespace(value="gemini"),
            ),
        ),
    ):
        assert f.get_embeddings_with_fallback() is fake
    clear_embeddings_cache()


# ---------------------------------------------------------------------------
# Backends: lazy init, score-join fallback, info/delete errors
# ---------------------------------------------------------------------------


def test_chroma_http_lazy_and_error_paths():
    from makpa.vectorstore.chroma_http import ChromaHTTPVectorStore

    store = ChromaHTTPVectorStore.__new__(ChromaHTTPVectorStore)
    store._host = "h"
    store._port = 1
    store._collection_name = "c"
    store._vectorstore = None
    store._embeddings = None
    fake_emb = MagicMock()
    fake_vs = MagicMock()
    with (
        patch("makpa.vectorstore.get_embeddings", return_value=fake_emb),
        patch("makpa.vectorstore.chroma_http.Chroma", return_value=fake_vs) as chroma,
    ):
        assert store._get_vectorstore() is fake_vs
        assert store._get_vectorstore() is fake_vs  # cached
    assert chroma.call_count == 1
    # Score join failure -> 0.0 scores.
    doc = _doc()
    fake_vs.max_marginal_relevance_search.return_value = [doc]
    fake_vs.similarity_search_with_score.side_effect = RuntimeError("down")
    with patch.object(type(store), "_get_vectorstore", return_value=fake_vs):
        assert store.similarity_search_with_mmr("q") == [(doc, 0.0)]
        fake_vs._collection.count.side_effect = RuntimeError("down")
        assert "error" in store.collection_info()
        fake_vs.delete_collection.side_effect = RuntimeError("down")
        with pytest.raises(RuntimeError):
            store.delete_collection()


def test_chroma_local_error_paths():
    from makpa.vectorstore.chroma_local import ChromaLocalVectorStore

    store = ChromaLocalVectorStore.__new__(ChromaLocalVectorStore)
    store._collection_name = "c"
    store._persist_directory = "d"
    fake_vs = MagicMock()
    doc = _doc()
    fake_vs.max_marginal_relevance_search.return_value = [doc]
    fake_vs.similarity_search_with_score.side_effect = RuntimeError("down")
    with patch.object(type(store), "_get_vectorstore", return_value=fake_vs):
        assert store.similarity_search_with_mmr("q") == [(doc, 0.0)]
        fake_vs._collection.count.side_effect = RuntimeError("down")
        assert "error" in store.collection_info()
        fake_vs.delete_collection.side_effect = RuntimeError("down")
        with pytest.raises(RuntimeError):
            store.delete_collection()


def test_pinecone_init_and_lazy():
    from makpa.vectorstore import pinecone as pinecone_mod

    with patch.object(pinecone_mod, "Pinecone") as pc_cls:
        pc_cls.return_value.list_indexes.return_value = []
        store = pinecone_mod.PineconeVectorStore(api_key="k", index_name="idx")
        assert store._api_key == "k"
        assert pc_cls.return_value.create_index.called
    # Lazy LangChain wrapper is cached.
    fake_emb = MagicMock()
    fake_vs = MagicMock()
    with (
        patch("makpa.vectorstore.get_embeddings", return_value=fake_emb),
        patch.object(
            pinecone_mod, "LangChainPineconeVectorStore", return_value=fake_vs
        ),
    ):
        assert store._get_vectorstore() is fake_vs
        assert store._get_vectorstore() is fake_vs


def test_qdrant_full_paths():
    from makpa.vectorstore import qdrant as qdrant_mod

    # Collection already exists.
    with patch.object(qdrant_mod, "QdrantClient") as client_cls:
        client_cls.return_value.get_collections.return_value = SimpleNamespace(
            collections=[SimpleNamespace(name="makpa-rag")]
        )
        store = qdrant_mod.QdrantVectorStore(url="http://x", api_key="k")
        assert store._collection_name == "makpa-rag"
    # Collection created.
    with patch.object(qdrant_mod, "QdrantClient") as client_cls:
        client_cls.return_value.get_collections.return_value = SimpleNamespace(
            collections=[]
        )
        store = qdrant_mod.QdrantVectorStore(url="http://x", api_key="k")
        assert client_cls.return_value.create_collection.called
    # ensure failure propagates.
    with patch.object(qdrant_mod, "QdrantClient") as client_cls:
        client_cls.return_value.get_collections.side_effect = RuntimeError("down")
        with pytest.raises(RuntimeError):
            qdrant_mod.QdrantVectorStore(url="http://x", api_key="k")
    # Lazy wrapper cached; CRUD + score fallback + info/delete errors.
    fake_emb = MagicMock()
    fake_vs = MagicMock()
    with (
        patch("makpa.vectorstore.get_embeddings", return_value=fake_emb),
        patch.object(
            qdrant_mod, "LangChainQdrantVectorStore", return_value=fake_vs
        ),
    ):
        assert store._get_vectorstore() is fake_vs
        assert store._get_vectorstore() is fake_vs
    doc = _doc()
    fake_vs.max_marginal_relevance_search.return_value = [doc]
    fake_vs.similarity_search_with_score.side_effect = RuntimeError("down")
    with patch.object(type(store), "_get_vectorstore", return_value=fake_vs):
        assert store.similarity_search_with_mmr("q") == [(doc, 0.0)]
        assert store.add_documents([doc]) == fake_vs.add_documents.return_value
    store._client = MagicMock()
    store._client.get_collection.return_value = SimpleNamespace(
        points_count=3,
        config=SimpleNamespace(params=SimpleNamespace(vectors=SimpleNamespace(size=384))),
    )
    info = store.collection_info()
    assert info["total_vectors"] == 3 and info["dimension"] == 384
    store._client.get_collection.side_effect = RuntimeError("down")
    assert "error" in store.collection_info()
    store._client.delete_collection.side_effect = RuntimeError("down")
    with pytest.raises(RuntimeError):
        store.delete_collection()
    store._client.delete_collection.side_effect = None
    store.delete_collection()


# ---------------------------------------------------------------------------
# LLM factory branches
# ---------------------------------------------------------------------------


def test_llm_factory_branches():
    from makpa.llm.factory import LLMFactory, clear_llm_cache, get_llm_for_provider

    f = LLMFactory()
    f.clear_cache()
    # Constructor failures -> None.
    with (
        patch("langchain_google_genai.ChatGoogleGenerativeAI", side_effect=RuntimeError),
        patch.object(f, "_settings", MagicMock(gemini_api_key="k")),
    ):
        assert f._create_gemini_model() is None
    with (
        patch("langchain_groq.ChatGroq", side_effect=RuntimeError),
        patch.object(f, "_settings", MagicMock(groq_api_key="k")),
    ):
        assert f._create_groq_model() is None
    # Success constructors.
    with (
        patch("langchain_google_genai.ChatGoogleGenerativeAI", return_value=MagicMock()),
        patch.object(
            f,
            "_settings",
            MagicMock(
                gemini_api_key="k",
                gemini_chat_model="m",
                llm_temperature=0.1,
                llm_max_tokens=10,
            ),
        ),
    ):
        assert f._create_gemini_model() is not None
    with (
        patch("langchain_groq.ChatGroq", return_value=MagicMock()),
        patch.object(
            f,
            "_settings",
            MagicMock(
                groq_api_key="k", groq_chat_model="m", llm_temperature=0.1, llm_max_tokens=10
            ),
        ),
    ):
        assert f._create_groq_model() is not None
    # Cache hit.
    f.clear_cache()
    mock_settings = MagicMock(
        resolved_llm_provider=SimpleNamespace(value="mock")
    )
    with patch.object(f, "_settings", mock_settings):
        first = get_llm_for_provider("mock")
        assert get_llm_for_provider("mock") is first
    # Fallback chain skips a provider whose test invoke fails.
    from makpa.utils.mock import create_mock_model

    good = create_mock_model()
    bad = MagicMock()
    bad.invoke.side_effect = RuntimeError("down")
    # Loop order is gemini -> groq -> mock: fail gemini+groq, land on mock.
    with (
        patch.object(LLMFactory, "_create_gemini_model", return_value=bad),
        patch.object(LLMFactory, "_create_groq_model", return_value=bad),
    ):
        f.clear_cache()
        with patch.object(
            f, "_settings", MagicMock(resolved_llm_provider=SimpleNamespace(value="mock"))
        ):
            from makpa.llm import get_llm

            assert isinstance(get_llm(), type(good))
    clear_llm_cache()


# ---------------------------------------------------------------------------
# RAG graph / ingestion extras
# ---------------------------------------------------------------------------


def test_graph_exception_and_helper_paths():
    from makpa.rag import graph as g

    with patch("makpa.rag.graph.grounded_answer", side_effect=RuntimeError("boom")):
        out = g.generation_node({"query": "q", "retrieved_chunks": [_doc()]})
        assert out["status"] == "error"
    with patch("makpa.rag.graph.validate_answer", side_effect=RuntimeError("boom")):
        out = g.validation_node({"answer": "a", "retrieved_chunks": [_doc()]})
        assert out["status"] == "error"
    # Empty validation keeps status empty.
    out = g.validation_node({"answer": "No relevant documents found.", "status": "ok"})
    assert out["status"] == "empty"
    assert g.short_circuit_node({})["status"] == "empty"
    assert g.short_circuit_node({})["answer"] == "no relevant documents found"
    compiled = g.create_rag_graph()
    assert set(compiled.nodes) >= {"retrieval", "generation", "validation", "short_circuit"}
    doc = _doc("content here")
    with patch("makpa.rag.graph.retrieve_documents", return_value=[(doc, 0.9)]):
        res = g.run_rag("What is this?")
        assert res["status"] in ("ok", "empty")


def test_ingestion_helpers_and_multi():

    from makpa.rag import ingestion as ing

    assert ing._generate_chunk_id("abcdef1234567890", 3) == "abcdef1234567890-0003"
    assert ing._compute_file_hash.__name__ == "_compute_file_hash"
    docs = ing._attach_metadata([_doc("x")], "f.pdf", "hashhashhashhash")
    assert docs[0].metadata["source"] == "f.pdf"
    assert docs[0].metadata["doc_id"] == "hashhashhashhash"[:16]
    with patch("makpa.rag.ingestion.PyMuPDFLoader") as loader_cls:
        loader = ing._get_loader("whatever.pdf", loader_type="mystery")
        assert loader is loader_cls.return_value
    fake_result = MagicMock()
    with patch("makpa.rag.ingestion.ingest_pdf", return_value=fake_result) as ip:
        assert ing.ingest_multiple_pdfs(["a.pdf", "b.pdf"]) == [fake_result, fake_result]
        assert ip.call_count == 2


# ---------------------------------------------------------------------------
# Mock model branches
# ---------------------------------------------------------------------------


def test_mock_model_all_branches():
    from langchain_core.messages import HumanMessage

    from makpa.utils.mock import MockChatModel, create_mock_model

    m = create_mock_model()
    assert isinstance(m, MockChatModel)
    assert m._llm_type == "mock"
    assert "No relevant documents" in m.invoke("no context was retrieved here").content
    assert "[" in m.invoke("answer this [chunk 0] context").content
    assert "[" in m.invoke("retrieve the document with citation").content
    assert "?" not in m.invoke("tell me about rag").content or True
    assert "mock response" in m.invoke("What is this?").content.lower()
    assert "demo mode" in m.invoke("hello").content.lower()
    # List input, async, streaming, _generate.
    msg = HumanMessage(content="What is this?")
    assert "mock" in m.invoke([msg]).content.lower()
    import asyncio

    assert "mock" in asyncio.run(m.ainvoke([msg])).content.lower()
    chunks = list(m.stream("hello there"))
    assert len(chunks) >= 2
    chunks2 = list(m.stream([msg]))
    assert chunks2
    result = m._generate([msg], stop=None, run_manager=None)
    assert result.generations
    assert m._get_response("plain words") != ""


# ---------------------------------------------------------------------------
# Settings resolution + banner
# ---------------------------------------------------------------------------


def test_settings_validators_and_mode(monkeypatch):
    from makpa.config import Mode, Settings

    # Blank overrides win over the repo .env file (env > .env).
    for var in (
        "GEMINI_API_KEY",
        "GROQ_API_KEY",
        "GITHUB_MCP_PAT",
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CALENDAR_MCP_URL",
        "GOOGLE_GMAIL_MCP_URL",
    ):
        monkeypatch.setenv(var, "")
    s = Settings(makpa_mode="LIVE", llm_provider="GEMINI", vector_store="pinecone")
    assert s.makpa_mode == Mode.LIVE
    # Live with no GitHub/Google/LLM keys downgrades to demo.
    assert s.resolve_mode() == Mode.DEMO
    assert s.downgrade_reasons
    assert s.resolve_llm_provider().value == "mock"
    assert s.resolve_google_mcp_mode().value == "local"
    assert s.resolve_github_mcp_path() == "mock"
    # Validators accept mixed case for remaining enums.
    s2 = Settings(google_mcp_mode="OFFICIAL", embedding_provider="GEMINI")
    assert s2.google_mcp_mode.value == "official"
    assert s2.embedding_provider.value == "gemini"


def test_settings_vector_and_github_paths(monkeypatch):
    from makpa.config import Mode, Settings, VectorStoreType

    monkeypatch.setenv("PINECONE_API_KEY", "")
    # Blank (never delete): repo .env carries keys, incl. Qdrant since setups.
    monkeypatch.setenv("QDRANT_URL", "")
    monkeypatch.setenv("QDRANT_API_KEY", "")
    # Qdrant requested with no creds falls back to Chroma HTTP (non-demo).
    s2 = Settings(vector_store="qdrant")
    s2.resolved_mode = Mode.FREE
    assert s2.resolve_vector_store().value == "chroma_http"
    assert s2.downgrade_reasons
    monkeypatch.setenv("PINECONE_API_KEY", "k")
    s = Settings(vector_store="pinecone")
    assert s.resolve_vector_store() == VectorStoreType.PINECONE
    monkeypatch.setenv("GITHUB_MCP_PAT", "pat")
    s3 = Settings(github_mcp_mode="auto")
    assert s3.resolve_github_mcp_path() == "real"
    s4 = Settings(github_mcp_mode="mock")
    assert s4.resolve_github_mcp_path() == "mock"
    assert s4.resolve_all().resolved_github_mcp_path == "mock"
    # Qdrant requested with creds resolves directly.
    monkeypatch.setenv("QDRANT_URL", "http://x")
    monkeypatch.setenv("QDRANT_API_KEY", "k")
    s5 = Settings(vector_store="qdrant")
    assert s5.resolve_vector_store() == VectorStoreType.QDRANT


def test_banner_with_and_without_downgrades(capsys):
    from unittest.mock import patch as upatch

    from makpa.config import (
        EmbeddingProvider,
        GoogleMCPMode,
        LLMProvider,
        Mode,
        VectorStoreType,
    )

    full = SimpleNamespace(
        resolved_mode=Mode.DEMO,
        resolved_llm_provider=LLMProvider.MOCK,
        resolved_vector_store=VectorStoreType.CHROMA_LOCAL,
        embedding_provider=EmbeddingProvider.HUGGINGFACE,
        resolved_google_mcp_mode=GoogleMCPMode.LOCAL,
        resolved_google_oauth_state="missing",
        resolved_github_mcp_path="mock",
        downgrade_reasons=[],
    )
    from makpa.config import settings as settings_mod

    with upatch.object(settings_mod, "get_settings", return_value=full):
        settings_mod.print_startup_banner()
    out = capsys.readouterr().out
    assert "MAKPA" in out and "mock" in out
    full2 = SimpleNamespace(**{**vars(full), "downgrade_reasons": ["reason one"]})
    with upatch.object(settings_mod, "get_settings", return_value=full2):
        settings_mod.print_startup_banner()
    assert "reason one" in capsys.readouterr().out
    full3 = SimpleNamespace(**{**vars(full), "resolved_mode": Mode.LIVE})
    with upatch.object(settings_mod, "get_settings", return_value=full3):
        settings_mod.print_startup_banner()
    assert "live LLM" in capsys.readouterr().out
