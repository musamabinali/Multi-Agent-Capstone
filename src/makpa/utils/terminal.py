"""Shared terminal UX helpers for MAKPA CLIs.

Centralizes logging setup so every CLI behaves the same:

- root stays at INFO, preserving makpa's own concise logs,
- chatty third-party loggers (per-request lines, SDK retry notices
  with full JSON bodies) are capped at WARNING,
- ``MAKPA_VERBOSE=1`` restores the full firehose for debugging,
- repeated calls are safe (no handler duplication, never raises).
"""

from __future__ import annotations

import logging
import os
from typing import Any

#: Third-party loggers that spam INFO during normal CLI runs.
QUIET_LOGGERS = (
    "httpx",
    "httpcore",
    "google_genai",
    "google.api_core",
    "google.auth",
    "urllib3",
    "mcp",
)

_VERBOSE_VALUES = ("1", "true", "yes", "on")


def verbose_enabled() -> bool:
    """Return True when MAKPA_VERBOSE requests full debug logging."""
    return os.environ.get("MAKPA_VERBOSE", "").strip().lower() in _VERBOSE_VALUES


def confirmation_title(preview: dict[str, Any]) -> str:
    """Gate-aware confirmation title; no bogus "(gate ?)" when unset."""
    gate = preview.get("gate")
    if gate in (1, 2):
        return f"Confirmation required (gate {gate})"
    return "Confirmation required"


def wrap_box_lines(lines: list[str], width: int = 100) -> list[str]:
    """Word-wrap long confirmation-box lines so previews stay readable."""
    import textwrap

    wrapped: list[str] = []
    for line in lines:
        wrapped.extend(textwrap.wrap(line, width=width) or [""])
    return wrapped


def setup_logging() -> None:
    """Configure root logging; always safe to call repeatedly."""
    logging.basicConfig(
        level=logging.DEBUG if verbose_enabled() else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    for name in QUIET_LOGGERS:
        logging.getLogger(name).setLevel(
            logging.DEBUG if verbose_enabled() else logging.WARNING
        )


__all__ = [
    "QUIET_LOGGERS",
    "confirmation_title",
    "setup_logging",
    "verbose_enabled",
    "wrap_box_lines",
]
