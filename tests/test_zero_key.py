"""Zero-key test: full RAG flow with no .env file."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from langchain_core.documents import Document


def test_zero_key_flow(monkeypatch):
    # Ensure no API keys leak into the test
    for var in (
        "GEMINI_API_KEY",
        "GROQ_API_KEY",
        "PINECONE_API_KEY",
        "QDRANT_API_KEY",
        "QDRANT_URL",
        "GITHUB_MCP_PAT",
        "GOOGLE_CLIENT_ID",
    ):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("MAKPA_MODE", "demo")
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("VECTOR_STORE", "chroma_local")
    monkeypatch.setenv("EMBEDDING_PROVIDER", "huggingface")

    # Fresh settings resolution
    from makpa.config import get_settings

    get_settings.cache_clear() if hasattr(get_settings, "cache_clear") else None
    try:
        from makpa.llm import clear_llm_cache
        from makpa.vectorstore import clear_embeddings_cache, clear_vector_store_cache

        clear_llm_cache()
        clear_embeddings_cache()
        clear_vector_store_cache()
    except Exception:
        pass

    # Mock heavy backends: embeddings + vector store
    doc = Document(
        page_content="MAKPA demo content about agents.",
        metadata={"source": "sample.pdf", "page": 1, "chunk_index": 0, "doc_id": "z"},
    )
    fake_store = MagicMock()
    fake_store.similarity_search_with_mmr.return_value = [(doc, 0.9)]
    fake_store.collection_info.return_value = {"type": "chroma_local"}
    fake_store.add_documents.return_value = ["z-0000"]

    with (
        patch("makpa.vectorstore.create_vector_store", return_value=fake_store),
        patch("makpa.rag.graph.retrieve_documents", return_value=[(doc, 0.9)]),
    ):
        from makpa.rag import run_rag

        result = run_rag("What is in the demo document?")
        assert result["status"] in ("ok", "empty")
        if result["status"] == "ok":
            assert result["citations"]
            assert "[" in result["answer"]
