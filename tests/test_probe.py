"""P1-PROBE-1: startup model-name probe tests."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest


def _settings(mode: str, gemini_model: str = "gemini-2.0-flash") -> SimpleNamespace:
    from makpa.config import Mode

    return SimpleNamespace(
        resolved_mode=Mode(mode),
        resolved_llm_provider=SimpleNamespace(value="mock"),
        gemini_chat_model=gemini_model,
        groq_chat_model="llama-3.3-70b-versatile",
    )


def test_probe_demo_ok_with_mock():
    from makpa.llm.probe import probe_llm
    from makpa.utils.mock import create_mock_model

    with (
        patch("makpa.llm.probe.get_settings", return_value=_settings("demo")),
        patch("makpa.llm.get_llm", return_value=create_mock_model()),
    ):
        result = probe_llm()
    assert result.ok is True
    assert result.provider == "mock"
    assert result.warnings == []


def test_probe_warns_on_stale_names():
    from makpa.llm.probe import probe_llm
    from makpa.utils.mock import create_mock_model

    settings = _settings("demo", gemini_model="gemini-1.5-flash")
    with (
        patch("makpa.llm.probe.get_settings", return_value=settings),
        patch("makpa.llm.get_llm", return_value=create_mock_model()),
    ):
        result = probe_llm()
    assert result.ok is True
    assert any("GEMINI_CHAT_MODEL" in w for w in result.warnings)


def test_probe_live_with_mock_fails_fast():
    from makpa.llm.probe import probe_llm
    from makpa.utils.mock import create_mock_model

    with (
        patch("makpa.llm.probe.get_settings", return_value=_settings("live")),
        patch("makpa.llm.get_llm", return_value=create_mock_model()),
    ):
        with pytest.raises(RuntimeError, match="Live mode requires a working LLM"):
            probe_llm()


def test_probe_live_with_real_model_ok():
    from types import SimpleNamespace as NS

    from makpa.llm.probe import probe_llm

    class FakeGeminiChat:
        def invoke(self, prompt: str) -> NS:
            return NS(content="ok")

    settings = _settings("live")
    settings.resolved_llm_provider = SimpleNamespace(value="gemini")
    with (
        patch("makpa.llm.probe.get_settings", return_value=settings),
        patch("makpa.llm.get_llm", return_value=FakeGeminiChat()),
    ):
        result = probe_llm()
    assert result.ok is True
    assert result.provider == "gemini"


def test_probe_failed_completion_in_demo_returns_not_ok():
    from makpa.llm.probe import probe_llm

    bad = MagicMock()
    bad.invoke.side_effect = RuntimeError("network down")
    with (
        patch("makpa.llm.probe.get_settings", return_value=_settings("demo")),
        patch("makpa.llm.get_llm", return_value=bad),
    ):
        result = probe_llm()
    assert result.ok is False
    assert "LLM probe failed" in result.message
