"""Shared terminal logging helper tests (quiet third-party firehose)."""

from __future__ import annotations

import logging

import pytest


@pytest.mark.parametrize("value", ["1", "true", "yes", "on", " TRUE "])
def test_verbose_enabled_truthy(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    from makpa.utils.terminal import verbose_enabled

    monkeypatch.setenv("MAKPA_VERBOSE", value)
    assert verbose_enabled() is True


@pytest.mark.parametrize("value", ["", "0", "false", "no", "off"])
def test_verbose_enabled_falsy(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    from makpa.utils.terminal import verbose_enabled

    monkeypatch.setenv("MAKPA_VERBOSE", value)
    assert verbose_enabled() is False


def test_verbose_unset_is_falsy(monkeypatch: pytest.MonkeyPatch) -> None:
    from makpa.utils.terminal import verbose_enabled

    monkeypatch.delenv("MAKPA_VERBOSE", raising=False)
    assert verbose_enabled() is False


def test_setup_logging_quiets_third_party(monkeypatch: pytest.MonkeyPatch) -> None:
    from makpa.utils.terminal import QUIET_LOGGERS, setup_logging

    monkeypatch.delenv("MAKPA_VERBOSE", raising=False)
    saved = {name: logging.getLogger(name).level for name in QUIET_LOGGERS}
    try:
        for name in QUIET_LOGGERS:
            logging.getLogger(name).setLevel(logging.DEBUG)
        setup_logging()
        for name in QUIET_LOGGERS:
            assert logging.getLogger(name).level == logging.WARNING
        # Repeated calls are safe and idempotent.
        setup_logging()
        for name in QUIET_LOGGERS:
            assert logging.getLogger(name).level == logging.WARNING
    finally:
        for name, level in saved.items():
            logging.getLogger(name).setLevel(level)


def test_setup_logging_verbose_restores_debug(monkeypatch: pytest.MonkeyPatch) -> None:
    from makpa.utils.terminal import QUIET_LOGGERS, setup_logging

    monkeypatch.setenv("MAKPA_VERBOSE", "1")
    saved = {name: logging.getLogger(name).level for name in QUIET_LOGGERS}
    try:
        setup_logging()
        for name in QUIET_LOGGERS:
            assert logging.getLogger(name).level == logging.DEBUG
    finally:
        for name, level in saved.items():
            logging.getLogger(name).setLevel(level)


def test_wrap_box_lines() -> None:
    from makpa.utils.terminal import wrap_box_lines

    assert wrap_box_lines(["short"]) == ["short"]
    assert wrap_box_lines([]) == []
    long_line = "x" * 250
    wrapped = wrap_box_lines([long_line])
    assert len(wrapped) > 1
    assert all(len(part) <= 100 for part in wrapped)
    assert "".join(wrapped) == long_line


def test_cli_setup_logging_delegates() -> None:
    """Every CLI keeps its _setup_logging entry point (tests call them)."""
    from makpa.cli import agent, github_demo, google_demo, rag_demo

    agent._setup_logging()
    github_demo._setup_logging()
    google_demo._setup_logging()
    rag_demo._setup_logging()
