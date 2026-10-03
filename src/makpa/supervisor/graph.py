"""Supervisor graph for MAKPA Phase 4 (hub-and-spoke).

The supervisor classifies intent, fans out to isolated sub-agent
subgraphs via the ``Send`` API (parallel), merges outputs in
``aggregate``, and retries errored agents once in ``reflection``.
Subgraph ``interrupt()`` gates propagate to the caller, which resumes
with the shared ``makpa.utils.interrupts`` helpers.
"""

import json
import logging
from typing import Any

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from makpa.utils.tracing import entrypoint

from .router import AGENT_NAMES, classify_intent, route
from .state import SupervisorState

logger = logging.getLogger(__name__)

TERMINAL_OK = ("ok", "empty", "rolled_back")


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def extract_structured(agent: str, result: dict[str, Any]) -> dict[str, Any]:
    """Extract typed ids from a sub-agent result (never from prose).

    Reads ``citations`` for RAG and ``tool_results`` payloads for GitHub /
    Google, so the frontend renders ids from data instead of regexing answers.
    Always returns a dict (possibly empty); callers render "no structured
    result" for the empty case.
    """
    if agent == "rag_agent":
        citations = _as_list(result.get("citations"))
        return {"citations": citations, "chunk_count": len(citations)}
    tool_results = [r for r in _as_list(result.get("tool_results")) if isinstance(r, dict)]
    if agent == "github_agent":
        return _extract_github_structured(result, tool_results)
    if agent == "google_agent":
        return _extract_google_structured(tool_results)
    return {}


def _extract_github_structured(
    result: dict[str, Any], tool_results: list[dict[str, Any]]
) -> dict[str, Any]:
    """Collect PR/issue/commit ids and the repo slug from GitHub tool results."""
    pr_numbers: list[int] = []
    issue_numbers: list[int] = []
    commit_shas: list[str] = []
    for item in tool_results:
        for pr in _as_list(item.get("prs")):
            number = _as_dict(pr).get("number")
            if isinstance(number, int) and number not in pr_numbers:
                pr_numbers.append(number)
        number = _as_dict(item.get("pr")).get("number")
        if isinstance(number, int) and number not in pr_numbers:
            pr_numbers.append(number)
        for issue in _as_list(item.get("issues")):
            number = _as_dict(issue).get("number")
            if isinstance(number, int) and number not in issue_numbers:
                issue_numbers.append(number)
        number = _as_dict(item.get("issue")).get("number")
        if isinstance(number, int) and number not in issue_numbers:
            issue_numbers.append(number)
        for commit in _as_list(item.get("commits")):
            sha = _as_dict(commit).get("sha")
            if isinstance(sha, str) and sha and sha not in commit_shas:
                commit_shas.append(sha)
    repo = ""
    for step in _as_list(result.get("plan")):
        candidate = _as_dict(_as_dict(step).get("args")).get("repo")
        if isinstance(candidate, str) and candidate:
            # Plan args may carry trailing sentence punctuation
            # ("octo-demo/hello-world."); the executed tool path already
            # normalizes it, so strip it here for clean display.
            repo = candidate.strip().rstrip(".,;:!?")
            break
    return {
        "pr_numbers": pr_numbers,
        "issue_numbers": issue_numbers,
        "commit_shas": commit_shas,
        "repo": repo,
    }


def _extract_google_structured(tool_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Collect event/message/draft ids and availability from Google tool results."""
    event_ids: list[str] = []
    event_id = ""
    calendar_status = ""
    message_id = ""
    draft_id = ""
    availability: dict[str, Any] = {}
    for item in tool_results:
        for event in _as_list(item.get("events")):
            identifier = _as_dict(event).get("id")
            if isinstance(identifier, str) and identifier and identifier not in event_ids:
                event_ids.append(identifier)
        event = _as_dict(item.get("event"))
        if event.get("id"):
            event_id = str(event["id"])
            if event_id not in event_ids:
                event_ids.append(event_id)
            if event.get("status"):
                calendar_status = str(event["status"])
        draft = _as_dict(item.get("draft"))
        if draft.get("id"):
            draft_id = str(draft["id"])
        if draft.get("message_id"):
            message_id = str(draft["message_id"])
        sent = _as_dict(item.get("sent"))
        if sent.get("id"):
            message_id = str(sent["id"])
        message = _as_dict(item.get("message"))
        if message.get("id") and not message_id:
            message_id = str(message["id"])
        if item.get("tool") == "calendar_check_availability":
            availability = {
                "free": bool(item.get("free", False)),
                "partial": bool(item.get("partial", False)),
            }
    return {
        "event_ids": event_ids,
        "event_id": event_id,
        "calendar_status": calendar_status,
        "message_id": message_id,
        "draft_id": draft_id,
        "availability": availability,
    }


def _worker_update(agent: str, result: dict[str, Any]) -> dict[str, Any]:
    """Normalize one sub-agent result into state updates."""
    from makpa.utils.interrupts import detect_interrupt

    status = str(result.get("status", "error"))
    answer = str(result.get("answer", ""))
    if detect_interrupt(result) is not None and status not in ("cancelled",):
        status = "confirmation_required"
        if not answer:
            answer = f"{agent} paused at a confirmation gate."
    summary: dict[str, Any] = {
        "agent": agent,
        "status": status,
        "answer": answer,
    }
    if agent == "rag_agent" and isinstance(result.get("citations"), list):
        summary["citations"] = result.get("citations", [])
    summary["structured"] = extract_structured(agent, result)
    tool_results = result.get("tool_results")
    if isinstance(tool_results, list):
        summary["tools"] = [
            {"tool": item.get("tool"), "status": item.get("status")}
            for item in tool_results
            if isinstance(item, dict)
        ]
    confirmed = status in TERMINAL_OK
    return {
        "agent_outputs": {agent: json.dumps(summary)},
        "confirmations": {agent: confirmed},
    }


def _classify_node(state: SupervisorState) -> dict[str, Any]:
    """Classify intent and stage the dispatch list."""
    messages = state.get("messages", [])
    decision = classify_intent(messages)
    task = ""
    for message in reversed(messages):
        content = getattr(message, "content", message)
        if isinstance(content, str) and content.strip():
            task = content
            break
    agents = [agent for agent in decision.agents if agent in AGENT_NAMES]
    logger.info("Supervisor routing to %s (%s)", agents, decision.reasoning)
    return {
        "next": agents,
        "task_description": task,
        "status": "ok" if agents else "error",
    }


def _make_rag_worker() -> Any:
    """Worker node invoking the RAG subgraph (interrupt-free)."""

    def rag_agent_node(
        state: SupervisorState, config: RunnableConfig | None = None
    ) -> dict[str, Any]:
        _ = config
        from makpa.rag import run_rag

        task = state.get("task_description", "")
        try:
            result = run_rag(task)
        except Exception as e:
            logger.warning("rag_agent failed: %s", e)
            result = {"status": "error", "answer": str(e)}
        return _worker_update("rag_agent", dict(result))

    return rag_agent_node


def _make_github_worker(checkpointer: Any) -> Any:
    """Worker node invoking the GitHub subgraph (gates propagate)."""

    def github_agent_node(
        state: SupervisorState, config: RunnableConfig | None = None
    ) -> dict[str, Any]:
        from langgraph.errors import GraphInterrupt

        task = state.get("task_description", "")
        try:
            if checkpointer is None:
                from makpa.subagents.github import run_github

                result = run_github(task)
            else:
                from makpa.subagents.github import create_github_graph

                graph = create_github_graph(checkpointer=checkpointer)
                result = dict(graph.invoke({"question": task}, config))
        except GraphInterrupt:
            # Let the gate propagate: the parent pauses and the shared
            # checkpointer resumes the subgraph on Command(resume=...).
            raise
        except Exception as e:
            logger.warning("github_agent failed: %s", e)
            result = {"status": "error", "answer": str(e)}
        return _worker_update("github_agent", result)

    return github_agent_node


def _make_google_worker(checkpointer: Any) -> Any:
    """Worker node invoking the Google subgraph (gates propagate)."""

    def google_agent_node(
        state: SupervisorState, config: RunnableConfig | None = None
    ) -> dict[str, Any]:
        from langgraph.errors import GraphInterrupt

        task = state.get("task_description", "")
        try:
            if checkpointer is None:
                from makpa.subagents.google import run_google

                result = run_google(task)
            else:
                from makpa.subagents.google import create_google_graph

                graph = create_google_graph(checkpointer=checkpointer)
                result = dict(graph.invoke({"question": task}, config))
        except GraphInterrupt:
            # Let the gate propagate: the parent pauses and the shared
            # checkpointer resumes the subgraph on Command(resume=...).
            raise
        except Exception as e:
            logger.warning("google_agent failed: %s", e)
            result = {"status": "error", "answer": str(e)}
        return _worker_update("google_agent", result)

    return google_agent_node


def _compute_status(statuses: dict[str, str]) -> str:
    """Merge sub-agent statuses: ok | partial | error."""
    if not statuses:
        return "error"
    values = set(statuses.values())
    if values <= {"ok", "empty"}:
        return "ok"
    if "error" in values and not (values & {"ok", "empty", "rolled_back"}):
        return "error"
    return "partial"


def aggregate_results(agent_outputs: dict[str, str]) -> tuple[str, str]:
    """Merge sub-agent outputs into (final_message, status).

    Structured fields (citations, event/message ids, per-tool statuses)
    are preserved per agent section — never concatenated blindly.
    """
    sections: list[str] = []
    statuses: dict[str, str] = {}
    for name in AGENT_NAMES:
        raw = agent_outputs.get(name)
        if raw is None:
            continue
        try:
            data = json.loads(raw)
        except (ValueError, TypeError):
            data = {"status": "error", "answer": str(raw)}
        if not isinstance(data, dict):
            data = {"status": "error", "answer": str(data)}
        status = str(data.get("status", "error"))
        statuses[name] = status
        lines = [f"### {name} [{status}]", str(data.get("answer", ""))]
        for key in ("citations", "tools"):
            value = data.get(key)
            if value:
                lines.append(f"{key}: {json.dumps(value)}")
        sections.append("\n".join(lines))
    overall = _compute_status(statuses)
    if not sections:
        return ("No sub-agent produced output.", overall)
    lead = {
        "ok": "All sub-agents completed successfully.",
        "partial": "Completed with partial results (see per-agent statuses).",
        "error": "All sub-agents failed.",
    }[overall]
    return (lead + "\n\n" + "\n\n".join(sections), overall)


def _aggregate_node(state: SupervisorState) -> dict[str, Any]:
    """Merge agent outputs into the final assistant message."""
    message, overall = aggregate_results(dict(state.get("agent_outputs", {})))
    history = list(state.get("messages", []))
    history.append(AIMessage(content=message))
    return {"messages": history, "status": overall}


def _route_after_aggregate(state: SupervisorState) -> str:
    """Retry errored agents once via reflection, else finish."""
    outputs = state.get("agent_outputs", {})
    for raw in outputs.values():
        try:
            data = json.loads(raw)
        except (ValueError, TypeError):
            return "reflection"
        if not isinstance(data, dict) or data.get("status") == "error":
            return "reflection"
    return str(END)


def _make_reflection_node(
    rag_worker: Any, github_worker: Any, google_worker: Any
) -> Any:
    """Re-run errored agents once, then rebuild the final message."""

    def reflection_node(
        state: SupervisorState, config: RunnableConfig | None = None
    ) -> dict[str, Any]:
        workers = {
            "rag_agent": rag_worker,
            "github_agent": github_worker,
            "google_agent": google_worker,
        }
        outputs = dict(state.get("agent_outputs", {}))
        confirmations = dict(state.get("confirmations", {}))
        retried: list[str] = []
        for name, raw in outputs.items():
            try:
                data = json.loads(raw)
            except (ValueError, TypeError):
                data = {"status": "error"}
            if not isinstance(data, dict) or data.get("status") == "error":
                worker = workers.get(name)
                if worker is None:
                    continue
                try:
                    update = worker(state, config)
                except Exception as e:
                    logger.warning("reflection retry failed for %s: %s", name, e)
                    continue
                retried.append(name)
                for key, value in update.get("agent_outputs", {}).items():
                    outputs[key] = value
                for key, value in update.get("confirmations", {}).items():
                    confirmations[key] = value
        message, overall = aggregate_results(outputs)
        if retried:
            message = f"Retried once: {', '.join(retried)}.\n\n" + message
        history = list(state.get("messages", []))
        history.append(AIMessage(content=message))
        return {
            "agent_outputs": outputs,
            "confirmations": confirmations,
            "messages": history,
            "status": overall,
        }

    return reflection_node


def create_supervisor_graph(checkpointer: Any = None) -> Any:
    """Create the supervisor graph (hub-and-spoke over Send).

    Args:
        checkpointer: Optional checkpointer shared with the GitHub and
            Google subgraphs so their ``interrupt()`` gates propagate.

    Returns:
        Compiled StateGraph.
    """
    rag_worker = _make_rag_worker()
    github_worker = _make_github_worker(checkpointer)
    google_worker = _make_google_worker(checkpointer)
    reflection_node = _make_reflection_node(rag_worker, github_worker, google_worker)

    builder = StateGraph(SupervisorState)
    builder.add_node("classify", _classify_node)
    builder.add_node("rag_agent", rag_worker)
    builder.add_node("github_agent", github_worker)
    builder.add_node("google_agent", google_worker)
    builder.add_node("aggregate", _aggregate_node)
    builder.add_node("reflection", reflection_node)

    builder.add_edge(START, "classify")
    builder.add_conditional_edges(
        "classify",
        route,
        {
            "rag_agent": "rag_agent",
            "github_agent": "github_agent",
            "google_agent": "google_agent",
            END: END,
        },
    )
    builder.add_edge("rag_agent", "aggregate")
    builder.add_edge("github_agent", "aggregate")
    builder.add_edge("google_agent", "aggregate")
    builder.add_conditional_edges(
        "aggregate",
        _route_after_aggregate,
        {"reflection": "reflection", END: END},
    )
    builder.add_edge("reflection", END)
    if checkpointer is not None:
        return builder.compile(checkpointer=checkpointer)
    return builder.compile()


@entrypoint("makpa.supervisor")  # type: ignore[untyped-decorator]
def run_supervisor(question: str) -> dict[str, Any]:
    """Run the supervisor once without a checkpointer (read-only helper)."""
    from langchain_core.messages import HumanMessage

    graph = create_supervisor_graph()
    result = graph.invoke({"messages": [HumanMessage(content=question)]})
    return dict(result)


__all__ = [
    "aggregate_results",
    "create_supervisor_graph",
    "extract_structured",
    "run_supervisor",
]
