"""Tracing helper tests (conditional @traceable entrypoints)."""

from __future__ import annotations

from unittest.mock import patch


def test_tracing_disabled_by_default_without_key(monkeypatch):
    from makpa.utils import tracing as tracing_mod

    monkeypatch.delenv("LANGCHAIN_API_KEY", raising=False)
    assert tracing_mod.tracing_enabled() is False

    @tracing_mod.entrypoint("test.entry")
    def add(a: int, b: int) -> int:
        return a + b

    assert add(2, 3) == 5


def test_tracing_enabled_with_key_uses_langsmith(monkeypatch):
    from unittest.mock import MagicMock, patch

    from makpa.utils import tracing as tracing_mod

    monkeypatch.setenv("LANGCHAIN_API_KEY", "key-123")
    assert tracing_mod.tracing_enabled() is True

    fake_traceable = MagicMock(side_effect=lambda name=None: (lambda fn: fn))
    with patch.dict("sys.modules", {"langsmith": MagicMock(traceable=fake_traceable)}):
        import importlib

        reloaded = importlib.reload(tracing_mod)

        @reloaded.entrypoint("test.entry")
        def add(a: int, b: int) -> int:
            return a + b

        assert add(2, 3) == 5
    importlib.reload(tracing_mod)


def test_tracing_missing_langsmith_warns(monkeypatch, caplog):
    import importlib
    import logging

    from makpa.utils import tracing as tracing_mod

    monkeypatch.setenv("LANGCHAIN_API_KEY", "key-123")
    with patch.dict("sys.modules", {"langsmith": None}):
        reloaded = importlib.reload(tracing_mod)

        @reloaded.entrypoint("test.entry")
        def add(a: int, b: int) -> int:
            return a + b

        with caplog.at_level(logging.WARNING, logger="makpa.utils.tracing"):
            assert add(1, 1) == 2
    importlib.reload(tracing_mod)


def test_entrypoints_exist_on_run_functions():
    from makpa.rag.graph import run_rag
    from makpa.subagents.github.graph import run_github
    from makpa.subagents.google.graph import run_google
    from makpa.supervisor.graph import run_supervisor

    for fn in (run_rag, run_github, run_google, run_supervisor):
        assert callable(fn)
