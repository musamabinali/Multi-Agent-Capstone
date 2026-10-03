"""Intent router for the MAKPA supervisor (Phase 4).

Structured-output classification with a deterministic keyword-heuristic
fallback so zero-key (mock LLM) mode still routes correctly. Routing
decisions are never hardcoded per query — the LLM decides first, the
heuristic only fires when structured output is unavailable.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Literal

from langgraph.graph import END
from langgraph.types import Send
from pydantic import BaseModel, Field

from .state import SupervisorState

logger = logging.getLogger(__name__)

AGENT_NAMES: tuple[str, str, str] = ("rag_agent", "github_agent", "google_agent")

AgentName = Literal["rag_agent", "github_agent", "google_agent"]


class Route(BaseModel):  # type: ignore[misc]
    """Structured routing decision."""

    agents: list[AgentName] = Field(
        default_factory=list,
        description="Sub-agents to invoke (empty when no domain matches)",
    )
    reasoning: str = Field(
        default="", description="One-line justification for the routing decision"
    )


RAG_KEYWORDS = (
    "pdf", "document", "documents", "docs", "retriev", "rag", "search documents",
    "knowledge", "manual", "report", "implementation details",
)
GITHUB_KEYWORDS = (
    "github", "repo", "repository", "repositories", "pull request", "pull-request",
    " pr ", "prs", "issue", "issues", "commit", "code search", "branch",
)
GOOGLE_KEYWORDS = (
    "calendar", "gmail", "email", "mail", "meeting", "schedule", "event",
    "appointment", "availability", "available", "invite", "agenda",
    "free", "busy",
)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
REPO_RE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")


def _message_text(messages: list[Any]) -> str:
    """Extract the latest human-readable query from a message list."""
    for message in reversed(messages):
        if isinstance(message, dict):
            content = message.get("content", "")
        else:
            content = getattr(message, "content", message)
        if isinstance(content, str) and content.strip():
            return content
        if isinstance(content, list):
            parts = [
                block.get("text", "")
                for block in content
                if isinstance(block, dict) and block.get("type") == "text"
            ]
            text = " ".join(part for part in parts if part).strip()
            if text:
                return text
    return ""


def heuristic_route(text: str) -> Route:
    """Keyword-heuristic routing fallback (deterministic, zero-key safe)."""
    lowered = f" {text.lower()} "
    agents: list[AgentName] = []
    if any(keyword in lowered for keyword in RAG_KEYWORDS):
        agents.append("rag_agent")
    if (
        any(keyword in lowered for keyword in GITHUB_KEYWORDS)
        or REPO_RE.search(text)
        or re.search(r"#\d+", text)
    ):
        agents.append("github_agent")
    if (
        any(keyword in lowered for keyword in GOOGLE_KEYWORDS)
        or EMAIL_RE.search(text)
    ):
        agents.append("google_agent")
    # Deduplicate while preserving RAG -> GitHub -> Google order.
    unique: list[AgentName] = []
    for agent in agents:
        if agent not in unique:
            unique.append(agent)
    if not unique:
        return Route(agents=[], reasoning="no domain keywords matched")
    return Route(
        agents=unique,
        reasoning=f"heuristic keywords matched: {', '.join(unique)}",
    )


def classify_intent(messages: list[Any]) -> Route:
    """Classify intent via structured LLM output, heuristic on failure."""
    text = _message_text(messages)
    if not text.strip():
        return Route(agents=[], reasoning="empty query")
    try:
        from makpa.llm import get_llm

        llm = get_llm()
        structured_fn = getattr(llm, "with_structured_output", None)
        if structured_fn is None:
            raise TypeError("LLM does not support structured output")
        structured = structured_fn(Route)
        prompt = (
            "Route the user query to MAKPA sub-agents. Reply with a Route object.\n"
            "- rag_agent: PDF/document retrieval and questions about documents.\n"
            "- github_agent: repositories, pull requests, issues, commits, code.\n"
            "- google_agent: calendar events, meetings, availability, email.\n"
            "Select every agent whose domain appears in the query.\n"
            f"Query: {text}"
        )
        result = structured.invoke(prompt)
        if isinstance(result, dict):
            route = Route(**result)
        elif isinstance(result, Route):
            route = result
        else:
            raise TypeError(f"Unexpected structured result: {type(result).__name__}")
        valid = [a for a in route.agents if a in AGENT_NAMES]
        return Route(agents=valid, reasoning=route.reasoning or "llm classification")
    except Exception as e:
        logger.warning("Structured routing failed, using heuristic: %s", e)
        return heuristic_route(text)


class IntentRouter:
    """Intent router object (wraps classify + route for reuse)."""

    def classify(self, messages: list[Any]) -> Route:
        """Classify a message list into a routing decision."""
        return classify_intent(messages)

    def route(self, state: SupervisorState) -> list[Send] | str:
        """Build Send dispatches for the classified agents."""
        return route(state)


def route(state: SupervisorState) -> list[Send] | str:
    """Return Send objects for chosen agents, or END when none."""
    task = state.get("task_description", "")
    agents = [a for a in state.get("next", []) if a in AGENT_NAMES]
    if not agents:
        finished: str = str(END)
        return finished
    return [Send(agent, {"task_description": task}) for agent in agents]


__all__ = [
    "AGENT_NAMES",
    "AgentName",
    "IntentRouter",
    "Route",
    "classify_intent",
    "heuristic_route",
    "route",
]
