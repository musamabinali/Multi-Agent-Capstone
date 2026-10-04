"""Coverage extras for Phase 1 leftovers: settings, LLM, CLI, smoke."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from typer.testing import CliRunner

runner = CliRunner()


def _probe_ok():
    return SimpleNamespace(provider="mock", model="mock-canned", warnings=[], message="ok")


# ---------------------------------------------------------------------------
# Settings branches
# ---------------------------------------------------------------------------


def test_settings_enum_inputs_and_provider_branches(monkeypatch):
    from makpa.config import (
        EmbeddingProvider,
        GitHubMCPMode,
        GoogleMCPMode,
        LLMProvider,
        Mode,
        Settings,
        VectorStoreType,
    )

    s = Settings(
        makpa_mode=Mode.DEMO,
        llm_provider=LLMProvider.GEMINI,
        vector_store=VectorStoreType.CHROMA_HTTP,
        google_mcp_mode=GoogleMCPMode.LOCAL,
        embedding_provider=EmbeddingProvider.HUGGINGFACE,
        github_mcp_mode=GitHubMCPMode.MOCK,
    )
    assert s.makpa_mode == Mode.DEMO
    assert s.resolve_vector_store() == VectorStoreType.CHROMA_HTTP

    for var in (
        "GEMINI_API_KEY",
        "GROQ_API_KEY",
        "PINECONE_API_KEY",
        "QDRANT_URL",
        "QDRANT_API_KEY",
    ):
        monkeypatch.setenv(var, "")
    monkeypatch.setenv("GROQ_API_KEY", "k")
    assert Settings().resolve_llm_provider() == LLMProvider.GROQ

    # Pinecone fallback when the requested store has no creds.
    monkeypatch.setenv("PINECONE_API_KEY", "k")
    s2 = Settings(vector_store="qdrant")
    s2.resolved_mode = Mode.FREE
    assert s2.resolve_vector_store() == VectorStoreType.PINECONE
    assert "Pinecone" in s2.downgrade_reasons[-1]

    # Demo fallback to Chroma local.
    monkeypatch.setenv("PINECONE_API_KEY", "")
    s3 = Settings(vector_store="qdrant")
    assert s3.resolve_vector_store() == VectorStoreType.CHROMA_LOCAL

    # Explicit Google modes pass through; auto+URLs selects official.
    assert Settings(google_mcp_mode="local").resolve_google_mcp_mode() == GoogleMCPMode.LOCAL
    assert (
        Settings(google_mcp_mode="official").resolve_google_mcp_mode()
        == GoogleMCPMode.OFFICIAL
    )
    monkeypatch.setenv("GOOGLE_CALENDAR_MCP_URL", "http://cal")
    monkeypatch.setenv("GOOGLE_GMAIL_MCP_URL", "http://gmail")
    # Pin auto: repo .env may pin a concrete GOOGLE_MCP_MODE since setups.
    monkeypatch.setenv("GOOGLE_MCP_MODE", "auto")
    assert Settings().resolve_google_mcp_mode() == GoogleMCPMode.OFFICIAL

    # Real mode in live without PAT warns and degrades.
    monkeypatch.setenv("GITHUB_MCP_PAT", "")
    s4 = Settings(github_mcp_mode="real")
    s4.resolved_mode = Mode.LIVE
    assert s4.resolve_github_mcp_path() == "mock"


# ---------------------------------------------------------------------------
# LLM factory leftovers
# ---------------------------------------------------------------------------


def test_llm_groq_fallback_and_loop_exhaustion():
    from makpa.llm.factory import LLMFactory, get_llm_for_provider

    f = LLMFactory()
    f.clear_cache()
    groq_less = MagicMock(
        groq_api_key=None,
        resolved_llm_provider=SimpleNamespace(value="groq"),
    )
    with patch.object(f, "_settings", groq_less):
        model = get_llm_for_provider("groq")
        assert model._llm_type == "mock"
    # Every provider fails incl. mock: the final safety net still returns.
    bad = MagicMock()
    bad.invoke.side_effect = RuntimeError("down")
    sentinel = MagicMock()
    sentinel.invoke.side_effect = RuntimeError("down")
    with (
        patch.object(LLMFactory, "_create_gemini_model", return_value=bad),
        patch.object(LLMFactory, "_create_groq_model", return_value=bad),
        patch.object(LLMFactory, "_create_mock_model", return_value=sentinel),
    ):
        f.clear_cache()
        with patch.object(
            f,
            "_settings",
            MagicMock(resolved_llm_provider=SimpleNamespace(value="mock")),
        ):
            from makpa.llm import get_llm

            assert get_llm() is sentinel
    f.clear_cache()


# ---------------------------------------------------------------------------
# Backend / client / embeddings / probe leftovers
# ---------------------------------------------------------------------------


def test_chroma_http_constructor_and_paths():
    from makpa.vectorstore.chroma_http import ChromaHTTPVectorStore

    store = ChromaHTTPVectorStore(host="h", port=1, collection_name="c")
    assert (store._host, store._port, store._collection_name) == ("h", 1, "c")
    defaulted = ChromaHTTPVectorStore()
    assert defaulted._collection_name == "makpa-rag"


def test_client_thread_pool_branch_and_normalize():
    import asyncio as aio

    from makpa.subagents.github.client import GitHubMCPClient, _normalize_raw

    assert _normalize_raw([123]) == {"status": "ok", "text": "[123]"}

    client = GitHubMCPClient.__new__(GitHubMCPClient)
    from makpa.config import get_settings

    client._settings = get_settings()
    client._path = "mock"
    client._client = None
    client._cached_tools = None
    client._cached_at = 0.0

    async def _inside_loop():
        return client.call_tool("list_prs", {"repo": "o/r"})

    with patch.object(
        GitHubMCPClient, "acall_tool", AsyncMock(return_value={"status": "ok"})
    ):
        out = aio.run(_inside_loop())
    assert out == {"status": "ok"}


def test_embeddings_gemini_configured_but_fails():
    from makpa.vectorstore.embeddings import EmbeddingFactory

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

    f = EmbeddingFactory()
    f.clear_cache()
    hf = MagicMock()
    with (
        patch.object(f, "_create_gemini_embeddings", return_value=None),
        patch.object(f, "_create_huggingface_embeddings", return_value=hf),
        patch.object(
            f,
            "_settings",
            _emb_settings(embedding_provider=SimpleNamespace(value="gemini")),
        ),
    ):
        assert f.get_embeddings_with_fallback() is hf
    f.clear_cache()


def test_probe_describe_branches_and_empty_completion():
    from makpa.config import Mode
    from makpa.llm.probe import _describe_model, probe_llm
    from makpa.utils.mock import create_mock_model

    settings = SimpleNamespace(
        resolved_mode=SimpleNamespace(value="demo"),
        resolved_llm_provider=SimpleNamespace(value="groq"),
        gemini_chat_model="g",
        groq_chat_model="q",
    )

    class FakeGroqChat:
        def invoke(self, prompt: str):
            return SimpleNamespace(content="ok")

    assert _describe_model(FakeGroqChat(), settings) == ("groq", "q")

    class OtherModel:
        def invoke(self, prompt: str):
            return SimpleNamespace(content="ok")

    assert _describe_model(OtherModel(), settings) == ("groq", "OtherModel".lower())

    class EmptyModel:
        _llm_type = "mock"

        def invoke(self, prompt: str):
            return SimpleNamespace(content="")

    demo = SimpleNamespace(
        resolved_mode=Mode.DEMO,
        resolved_llm_provider=SimpleNamespace(value="mock"),
        gemini_chat_model="gemini-2.0-flash",
        groq_chat_model="llama-3.3-70b-versatile",
    )
    with (
        patch("makpa.llm.probe.get_settings", return_value=demo),
        patch("makpa.llm.get_llm", return_value=EmptyModel()),
    ):
        out = probe_llm()
    assert out.ok is False

    live = SimpleNamespace(
        resolved_mode=Mode.LIVE,
        resolved_llm_provider=SimpleNamespace(value="mock"),
        gemini_chat_model="gemini-2.0-flash",
        groq_chat_model="llama-3.3-70b-versatile",
    )
    with (
        patch("makpa.llm.probe.get_settings", return_value=live),
        patch("makpa.llm.get_llm", return_value=create_mock_model()),
    ):
        # Mock model returns content, but provider is mock in live -> raises.
        try:
            probe_llm()
            raised = False
        except RuntimeError:
            raised = True
    assert raised

    with (
        patch("makpa.llm.probe.get_settings", return_value=live),
        patch("makpa.llm.get_llm", return_value=EmptyModel()),
    ):
        try:
            probe_llm()
            raised_live_empty = False
        except RuntimeError:
            raised_live_empty = True
    assert raised_live_empty


# ---------------------------------------------------------------------------
# rag_demo / ingest / smoke leftovers
# ---------------------------------------------------------------------------


def test_rag_demo_import_failure_no_citations_error_status_main():
    import sys as _sys

    from makpa.cli import rag_demo

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch.dict(_sys.modules, {"makpa.rag": None}),
    ):
        res = runner.invoke(rag_demo.app, ["ask", "q"])
    assert res.exit_code == 1

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.rag.run_rag",
            return_value={"answer": "a", "citations": [], "status": "ok"},
        ),
    ):
        res = runner.invoke(rag_demo.app, ["ask", "q"])
    assert res.exit_code == 0 and "no citations" in res.output

    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch(
            "makpa.rag.run_rag",
            return_value={"answer": "bad", "citations": [], "status": "error"},
        ),
    ):
        res = runner.invoke(rag_demo.app, ["ask", "q"])
    assert res.exit_code == 1

    store = MagicMock()
    store.collection_info.side_effect = RuntimeError("down")
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.vectorstore.create_vector_store", return_value=store),
    ):
        res = runner.invoke(rag_demo.app, ["info"])
    assert res.exit_code == 1

    store2 = MagicMock()
    store2.delete_collection.side_effect = RuntimeError("down")
    with (
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
        patch("makpa.vectorstore.create_vector_store", return_value=store2),
    ):
        res = runner.invoke(rag_demo.app, ["reset", "--yes"])
    assert res.exit_code == 1

    with patch.object(rag_demo, "app") as app_mock:
        rag_demo.main()
    app_mock.assert_called_once()


def test_ingest_cli_reset_confirm_yes():
    from makpa.cli import ingest as ingest_cli

    store = MagicMock()
    with patch("makpa.vectorstore.create_vector_store", return_value=store):
        res = runner.invoke(ingest_cli.app, ["reset"], input="y\n")
    assert res.exit_code == 0
    store.delete_collection.assert_called_once()


def test_smoke_variants_and_live_mcp_probe():
    import sys as _sys

    from makpa.cli import smoke_test

    with patch.object(smoke_test, "MODULES_TO_TEST", ["no.such.module.xyz"]):
        ok, errors = smoke_test.test_imports()
    assert not ok and errors

    ok, errors = asyncio.run(
        smoke_test.test_mcp_server(
            "GitHubMock", [_sys.executable, "-m", "makpa.mcp_servers.github.server"]
        )
    )
    assert ok, errors

    ok, errors = asyncio.run(smoke_test.test_mcp_server("Bad", ["no-such-binary-xyz"]))
    assert not ok

    from makpa.config import Mode

    settings = SimpleNamespace(resolved_mode=Mode.DEMO, downgrade_reasons=[])
    with (
        patch("makpa.cli.smoke_test.get_settings", return_value=settings),
        patch("makpa.cli.smoke_test.print_startup_banner"),
        patch("makpa.cli.smoke_test.test_imports", return_value=(True, [])),
        patch(
            "makpa.cli.smoke_test.test_mcp_server",
            AsyncMock(return_value=(True, [])),
        ),
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
    ):
        assert asyncio.run(smoke_test.run_smoke_test()) == 0

    with (
        patch("makpa.cli.smoke_test.get_settings", return_value=settings),
        patch("makpa.cli.smoke_test.print_startup_banner"),
        patch("makpa.cli.smoke_test.test_imports", return_value=(False, ["bad mod"])),
        patch(
            "makpa.cli.smoke_test.test_mcp_server",
            AsyncMock(return_value=(True, [])),
        ),
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
    ):
        assert asyncio.run(smoke_test.run_smoke_test()) == 1

    with patch(
        "makpa.cli.smoke_test.run_smoke_test", AsyncMock(return_value=0)
    ):
        assert smoke_test.main() == 0
