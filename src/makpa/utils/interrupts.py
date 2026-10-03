"""Shared interrupt() helpers for MAKPA sub-agent graphs.

Centralizes the langgraph 1.2 finding that ``graph.invoke()`` returns
``__interrupt__`` state instead of raising ``GraphInterrupt``. Every
sub-agent (GitHub, Google, supervisor) must use these helpers rather
than duplicating polling logic.
"""

from __future__ import annotations

import logging
from typing import Any

from langgraph.types import Command, Interrupt

logger = logging.getLogger(__name__)


def detect_interrupt(result: Any) -> Interrupt | None:
    """Return the pending interrupt from an invoke result, if any.

    Args:
        result: Whatever ``graph.invoke()`` returned.

    Returns:
        The first pending :class:`Interrupt`, or None when the graph
        did not pause at an ``interrupt()`` gate.
    """
    if isinstance(result, dict):
        pending = result.get("__interrupt__")
        if isinstance(pending, (list, tuple)) and pending:
            first = pending[0]
            if isinstance(first, Interrupt):
                return first
            logger.warning(
                "Unexpected __interrupt__ entry type: %s", type(first).__name__
            )
    return None


def resume_with(
    graph: Any, config: dict[str, Any], payload: dict[str, Any]
) -> dict[str, Any]:
    """Resume a paused graph with a resume payload.

    Args:
        graph: Compiled graph currently paused at ``interrupt()``.
        config: Runnable config (must carry the same thread_id).
        payload: Resume payload, e.g. ``{"confirm": True}``.

    Returns:
        The final invoke result as a plain dict.
    """
    result = graph.invoke(Command(resume=payload), config)
    return dict(result)


__all__ = ["detect_interrupt", "resume_with"]
