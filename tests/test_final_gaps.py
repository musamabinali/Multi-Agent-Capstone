"""Final gap coverage: factory reloads, server run(), smoke edges, CLI leftovers."""

from __future__ import annotations

import asyncio
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from typer.testing import CliRunner

runner = CliRunner()


def _probe_ok():
    return SimpleNamespace(provider="mock", model="mock-canned", warnings=[], message="ok")


# ---------------------------------------------------------------------------
# Factory: abstract bodies, import-failure reload, partial fallback chains
# ---------------------------------------------------------------------------


def test_factory_abstract_bodies_and_import_failures():
    from makpa.vectorstore.factory import VectorStore, _optional_import

    class _Dummy(VectorStore):
        def add_documents(self, documents, ids=None):
            return []

        def similarity_search_with_mmr(self, *args, **kwargs):
            return []

        def delete_collection(self):
            pass

        def collection_info(self):
            return {}

    dummy = _Dummy()
    assert VectorStore.add_documents(dummy, [], None) is None
    assert VectorStore.similarity_search_with_mmr(dummy, "q") is None
    assert VectorStore.delete_collection(dummy) is None
    assert VectorStore.collection_info(dummy) is None

    # Missing optional backend resolves to None without raising.
    assert _optional_import("no_such_backend_xyz", "Foo") is None


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


def test_factory_partial_fallback_chains():
    from makpa.vectorstore.factory import VectorStoreFactory

    f = VectorStoreFactory()
    f.clear_cache()
    fake = MagicMock()
    # Unknown target falls back to Pinecone when only Pinecone builds.
    with (
        patch.object(f, "_create_pinecone_store", return_value=fake),
        patch.object(f, "_create_chroma_http_store", return_value=None),
        patch.object(f, "_create_chroma_local_store", return_value=None),
        patch.object(f, "_create_qdrant_store", return_value=None),
        patch.object(
            f, "_settings", _factory_settings(resolved_vector_store=SimpleNamespace(value="nope"))
        ),
    ):
        assert f.get_store() is fake
    f.clear_cache()
    # ... or to Qdrant when it is the only builder left standing.
    with (
        patch.object(f, "_create_pinecone_store", return_value=None),
        patch.object(f, "_create_chroma_http_store", return_value=None),
        patch.object(f, "_create_chroma_local_store", return_value=None),
        patch.object(f, "_create_qdrant_store", return_value=fake),
        patch.object(
            f, "_settings", _factory_settings(resolved_vector_store=SimpleNamespace(value="nope"))
        ),
    ):
        assert f.get_store() is fake
    f.clear_cache()


# ---------------------------------------------------------------------------
# Settings validator else-branches (direct calls)
# ---------------------------------------------------------------------------


def test_settings_validators_with_enum_inputs():
    from makpa.config import (
        EmbeddingProvider,
        GitHubMCPMode,
        GoogleMCPMode,
        LLMProvider,
        Mode,
        Settings,
        VectorStoreType,
    )

    assert Settings._validate_mode(Mode.DEMO) == Mode.DEMO
    assert Settings._validate_llm_provider(LLMProvider.GEMINI) == LLMProvider.GEMINI
    assert Settings._validate_vector_store(VectorStoreType.QDRANT) == VectorStoreType.QDRANT
    assert Settings._validate_google_mcp_mode(GoogleMCPMode.LOCAL) == GoogleMCPMode.LOCAL
    assert (
        Settings._validate_embedding_provider(EmbeddingProvider.GEMINI)
        == EmbeddingProvider.GEMINI
    )
    assert Settings._validate_github_mcp_mode(GitHubMCPMode.REAL) == GitHubMCPMode.REAL


# ---------------------------------------------------------------------------
# Server run() over stubbed STDIO
# ---------------------------------------------------------------------------


def _run_over_stubbed_stdio(server_mod, instance):
    streams = (MagicMock(), MagicMock())
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=streams)
    cm.__aexit__ = AsyncMock(return_value=False)
    with (
        patch.object(server_mod, "stdio_server", return_value=cm),
        patch.object(instance.server, "run", AsyncMock()) as run_mock,
    ):
        asyncio.run(instance.run())
    run_mock.assert_awaited_once()


def test_servers_run_over_stubbed_stdio():
    from makpa.mcp_servers.github import server as gh
    from makpa.mcp_servers.retrieval import server as ret

    _run_over_stubbed_stdio(gh, gh.GitHubMockMCPServer())
    _run_over_stubbed_stdio(ret, ret.RetrievalMCPServer())


# ---------------------------------------------------------------------------
# handle_tool direct success/error branches
# ---------------------------------------------------------------------------


def test_handle_tool_remaining_branches():
    from makpa.mcp_servers.github import server as srv

    assert srv.handle_tool("list_prs", {})["status"] == "error"
    out = srv.handle_tool("get_pr", {"repo": "o/r", "number": 7})
    assert out == {"status": "ok", "pr": srv.FIXTURE_PRS[0]}
    assert "not found" in srv.handle_tool("get_pr", {"repo": "o/r", "number": 1})["message"]
    assert srv.handle_tool("list_issues", {})["status"] == "error"
    out = srv.handle_tool("create_issue", {"repo": "o/r", "title": "T", "body": "b"})
    assert out["issue"]["number"] == 99 and out["issue"]["body"] == "b"
    assert srv.handle_tool("read_file", {})["status"] == "error"
    assert "not found" in srv.handle_tool("read_file", {"repo": "o/r", "path": "x"})["message"]
    out = srv.handle_tool("read_file", {"repo": "o/r", "path": "README.md"})
    assert out["status"] == "ok" and out["ref"] == "main"


# ---------------------------------------------------------------------------
# Smoke edges: bad payloads, timeout, config/MCP failures, downgrades
# ---------------------------------------------------------------------------


def test_smoke_server_bad_payloads_and_timeout():
    from makpa.cli import smoke_test

    ok, errors = asyncio.run(
        smoke_test.test_mcp_server(
            "Junk",
            [sys.executable, "-c", "print('{\"x\":1}'); print('{\"y\":2}')"],
        )
    )
    assert not ok and any("Unexpected response" in e for e in errors)

    ok, errors = asyncio.run(
        smoke_test.test_mcp_server(
            "Junk2", [sys.executable, "-c", "print('hi'); print('not-json{{{')"]
        )
    )
    assert not ok and any("Failed to parse" in e for e in errors)

    ok, errors = asyncio.run(
        smoke_test.test_mcp_server(
            "Slow", [sys.executable, "-c", "import time; time.sleep(30)"]
        )
    )
    assert not ok and any("Timeout" in e for e in errors)


def test_smoke_run_variants():
    from makpa.cli import smoke_test
    from makpa.config import Mode

    downgraded = SimpleNamespace(
        resolved_mode=Mode.DEMO, downgrade_reasons=["PAT missing"]
    )
    warned_probe = SimpleNamespace(
        provider="mock",
        model="mock-canned",
        warnings=["stale model X"],
        message="LLM probe ok",
    )
    with (
        patch("makpa.cli.smoke_test.get_settings", return_value=downgraded),
        patch("makpa.cli.smoke_test.print_startup_banner"),
        patch("makpa.cli.smoke_test.test_imports", return_value=(True, [])),
        patch("makpa.cli.smoke_test.test_mcp_server", AsyncMock(return_value=(True, []))),
        patch("makpa.llm.probe_llm", return_value=warned_probe),
    ):
        assert asyncio.run(smoke_test.run_smoke_test()) == 0

    with (
        patch("makpa.cli.smoke_test.get_settings", side_effect=RuntimeError("cfg")),
        patch("makpa.cli.smoke_test.print_startup_banner"),
        patch("makpa.cli.smoke_test.test_imports", return_value=(True, [])),
        patch("makpa.cli.smoke_test.test_mcp_server", AsyncMock(return_value=(True, []))),
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
    ):
        assert asyncio.run(smoke_test.run_smoke_test()) == 1

    plain = SimpleNamespace(resolved_mode=Mode.DEMO, downgrade_reasons=[])
    with (
        patch("makpa.cli.smoke_test.get_settings", return_value=plain),
        patch("makpa.cli.smoke_test.print_startup_banner"),
        patch("makpa.cli.smoke_test.test_imports", return_value=(True, [])),
        patch(
            "makpa.cli.smoke_test.test_mcp_server",
            AsyncMock(return_value=(False, ["mcp down"])),
        ),
        patch("makpa.llm.probe_llm", return_value=_probe_ok()),
    ):
        assert asyncio.run(smoke_test.run_smoke_test()) == 1


# ---------------------------------------------------------------------------
# CLI leftovers: preview default, ingest abort
# ---------------------------------------------------------------------------


def test_github_demo_preview_default_and_ingest_abort():
    from makpa.cli import github_demo
    from makpa.cli import ingest as ingest_cli

    broken = MagicMock()
    broken.get_state.side_effect = RuntimeError("down")
    assert github_demo._pending_preview(broken, {}) == {
        "payload_preview": "(unavailable)"
    }

    with patch("makpa.vectorstore.create_vector_store") as factory:
        res = runner.invoke(ingest_cli.app, ["reset"], input="n\n")
    assert res.exit_code == 0 and "Aborted" in res.output
    factory.assert_not_called()
