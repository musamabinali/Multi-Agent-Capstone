"""Supervisor state schema for MAKPA Phase 4 (hub-and-spoke).

The supervisor fans out to isolated sub-agent subgraphs via ``Send``
and merges their outputs in ``aggregate``. Dict fields use merge
reducers so parallel branches never clobber each other.
"""

from __future__ import annotations

from typing import Annotated, Any, TypedDict


def _merge_str_dict(left: dict[str, str], right: dict[str, str]) -> dict[str, str]:
    """Merge parallel agent-output writes (last writer wins per key)."""
    merged = dict(left or {})
    merged.update(right or {})
    return merged


def _merge_bool_dict(left: dict[str, bool], right: dict[str, bool]) -> dict[str, bool]:
    """Merge parallel confirmation writes (last writer wins per key)."""
    merged = dict(left or {})
    merged.update(right or {})
    return merged


class SupervisorState(TypedDict, total=False):
    """State for the supervisor graph (Phase 4)."""

    messages: list[Any]
    next: list[str]
    task_description: str
    agent_outputs: Annotated[dict[str, str], _merge_str_dict]
    confirmations: Annotated[dict[str, bool], _merge_bool_dict]
    status: str


__all__ = [
    "SupervisorState",
    "_merge_bool_dict",
    "_merge_str_dict",
]
