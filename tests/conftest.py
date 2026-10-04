"""Shared pytest fixtures: isolate per-session CLI UX caches between tests."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _isolate_cli_ux_session_state() -> object:
    """Clear one-shot banner/probe/LLM caches so tests never leak sessions."""
    from makpa.llm.factory import clear_llm_cache

    try:
        from makpa.llm.probe import clear_probe_cache

        clear_probe_cache()
    except ImportError:
        pass
    try:
        from makpa.utils.terminal import reset_cli_ux_state

        reset_cli_ux_state()
    except ImportError:
        pass
    try:
        clear_llm_cache()
    except Exception:
        pass
    yield
    try:
        from makpa.llm.probe import clear_probe_cache

        clear_probe_cache()
    except ImportError:
        pass
    try:
        from makpa.utils.terminal import reset_cli_ux_state

        reset_cli_ux_state()
    except ImportError:
        pass
