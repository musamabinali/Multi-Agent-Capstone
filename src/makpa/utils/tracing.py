"""LangSmith tracing helper for MAKPA entry points.

`@entrypoint(name)` applies langsmith's `@traceable` only when a
`LANGCHAIN_API_KEY` is configured; otherwise it is a strict no-op, so
zero-key demo output stays clean and offline runs never warn.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from typing import Any, TypeVar, cast

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def tracing_enabled() -> bool:
    """Check whether LangSmith tracing can actually send runs."""
    return bool(os.getenv("LANGCHAIN_API_KEY"))


def entrypoint(name: str) -> Callable[[F], F]:
    """Conditional `@traceable` decorator for agent entry points."""
    def _decorate(fn: F) -> F:
        if not tracing_enabled():
            return fn
        try:
            from langsmith import traceable
        except ImportError:
            logger.warning("langsmith not installed; tracing disabled")
            return fn
        return cast(F, traceable(name=name)(fn))

    return _decorate


__all__ = ["entrypoint", "tracing_enabled"]
