"""State schemas for MAKPA supervisor and sub-agents."""

from __future__ import annotations

from typing import Any, Literal, TypedDict

from langchain_core.documents import Document


class RAGState(TypedDict, total=False):
    """Isolated state for the RAG sub-agent."""

    query: str
    retrieved_chunks: list[Document]
    citations: list[dict[str, Any]]
    answer: str
    status: Literal["ok", "empty", "error"]


class SupervisorState(TypedDict, total=False):
    """State for the supervisor graph (Phase 4)."""

    query: str
    intent: str
    rag_result: dict[str, Any]
    github_result: dict[str, Any]
    google_result: dict[str, Any]
    final_answer: str


class GitHubState(TypedDict, total=False):
    """Isolated state for the GitHub sub-agent (Phase 2)."""

    question: str
    plan: list[dict[str, Any]]
    tool_results: list[dict[str, Any]]
    answer: str
    needs_confirmation: bool
    confirmed: bool
    status: str


class GoogleState(TypedDict, total=False):
    """Isolated state for the Google Workspace sub-agent (Phase 3)."""

    question: str
    service: str
    action: str
    payload: dict[str, Any]
    plan: list[dict[str, Any]]
    tool_results: list[dict[str, Any]]
    answer: str
    needs_confirmation: bool
    confirmed: bool
    composite_stage: str
    status: str


__all__ = [
    "RAGState",
    "SupervisorState",
    "GitHubState",
    "GoogleState",
]
