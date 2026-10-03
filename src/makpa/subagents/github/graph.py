"""GitHub sub-agent as an isolated LangGraph StateGraph.

Nodes: ``plan`` → ``gate`` (conditional) → ``confirm`` (``interrupt()``)
→ ``execute`` → ``synthesize``, plus a ``short_circuit`` exit for empty
plans. Mutating tools can never execute without an explicit
``{"confirm": True}`` resume payload *and* a ``confirmed`` state flag.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from makpa.config import get_settings
from makpa.state import GitHubState
from makpa.utils.tracing import entrypoint

from .tools import GITHUB_TOOLS, MUTATING_TOOLS

logger = logging.getLogger(__name__)

TOOLS_BY_NAME = {t.name: t for t in GITHUB_TOOLS}

REPO_RE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
PR_NUMBER_RE = re.compile(r"#(\d+)")
OWNER_RE = re.compile(r"(?:org|user|owner)\s+([A-Za-z0-9_.-]+)", re.IGNORECASE)


def _default_owner() -> str:
    """Default owner for owner-less questions (mock fixture owner)."""
    if get_settings().resolved_github_mcp_path == "mock":
        return "octo-demo"
    return ""


def extract_repo(question: str) -> str:
    """Extract the first ``owner/name`` slug from a question, else ``""``."""
    match = REPO_RE.search(question)
    return str(match.group(0)) if match else ""


def heuristic_plan(question: str) -> list[dict[str, Any]]:
    """Keyword fallback planner used when the LLM output is unparseable.

    Assumes the mock fixture repo owner (``octo-demo``) when the question
    names no explicit owner and the GitHub path is mock.
    """
    q = question.lower()
    repo = extract_repo(question)
    plan: list[dict[str, Any]] = []

    create_markers = (
        "create an issue",
        "new issue",
        "file an issue",
        "open an issue",
        "create issue",
    )
    if any(k in q for k in create_markers):
        title_match = re.search(r"title\s*[:=]\s*(.+)", question, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else question[:120]
        plan.append(
            {
                "tool": "github_create_issue",
                "args": {"repo": repo, "title": title, "body": question},
            }
        )
        return plan
    if "pull request" in q or re.search(r"\bprs?\b", q):
        number = PR_NUMBER_RE.search(question)
        if number and repo:
            plan.append(
                {"tool": "github_get_pr", "args": {"repo": repo, "number": int(number.group(1))}}
            )
        elif repo:
            state = "closed" if "closed" in q else "open"
            plan.append({"tool": "github_list_prs", "args": {"repo": repo, "state": state}})
        return plan
    if "issue" in q:
        if repo:
            plan.append({"tool": "github_list_issues", "args": {"repo": repo, "state": "open"}})
        return plan
    if "commit" in q:
        if repo:
            plan.append({"tool": "github_get_commits", "args": {"repo": repo, "branch": "main"}})
        return plan
    if "search" in q or "code" in q or "find" in q:
        plan.append(
            {
                "tool": "github_search_code",
                "args": {"query": question, "repo": repo or None},
            }
        )
        return plan
    if "read" in q or "file" in q or "show" in q:
        path_match = re.search(r"[\w\-./]+\.\w+", question)
        if repo and path_match:
            plan.append(
                {"tool": "github_read_file", "args": {"repo": repo, "path": path_match.group(0)}}
            )
        return plan
    if "repo" in q:
        owner_match = OWNER_RE.search(question)
        if owner_match:
            owner = str(owner_match.group(1))
        elif repo:
            owner = repo.split("/")[0]
        else:
            owner = _default_owner()
        if owner:
            plan.append({"tool": "github_list_repos", "args": {"owner": owner}})
        return plan
    if repo:
        plan.append({"tool": "github_list_prs", "args": {"repo": repo, "state": "open"}})
    return plan


def _llm_plan(question: str) -> list[dict[str, Any]] | None:
    """Ask the LLM to pick tools; return None when unparseable."""
    from makpa.llm import get_llm

    catalog = "\n".join(f"- {t.name}: {t.description}" for t in GITHUB_TOOLS)
    prompt = (
        "Pick GitHub tools for the question. Reply with ONLY a JSON list of "
        '{"tool": name, "args": {...}} objects.\n'
        "Copy repository slugs verbatim as 'owner/name' "
        "(e.g. octo-demo/hello-world); never truncate to the bare name. "
        "Copy PR numbers from #N markers.\n"
        f"Tools:\n{catalog}\nQuestion: {question}\nJSON:"
    )
    try:
        response = get_llm().invoke(prompt)
        content = getattr(response, "content", str(response))
        text = content if isinstance(content, str) else str(content)
        start, end = text.find("["), text.rfind("]")
        if start == -1 or end == -1:
            return None
        parsed = json.loads(text[start : end + 1])
        steps: list[dict[str, Any]] = []
        for item in parsed:
            if isinstance(item, dict) and item.get("tool") in TOOLS_BY_NAME:
                steps.append({"tool": item["tool"], "args": dict(item.get("args", {}))})
        return steps or None
    except Exception as e:
        logger.warning("LLM planning failed, using heuristic: %s", e)
        return None


def plan_node(state: GitHubState) -> dict[str, Any]:
    """Pick one or more tools for the question."""
    question = state.get("question", "")
    if not question.strip():
        return {"plan": [], "tool_results": [], "status": "error", "answer": "empty question"}
    steps = _llm_plan(question) or heuristic_plan(question)
    # Drop steps the catalog does not know.
    steps = [s for s in steps if s.get("tool") in TOOLS_BY_NAME]
    steps = [_repair_step(question, step) for step in steps]
    needs_confirmation = any(s["tool"] in MUTATING_TOOLS for s in steps)
    return {"plan": steps, "needs_confirmation": needs_confirmation, "status": "ok"}


REPO_TOOLS: frozenset[str] = frozenset(
    {
        "github_list_prs",
        "github_get_pr",
        "github_list_issues",
        "github_create_issue",
        "github_get_commits",
        "github_read_file",
    }
)


def _repair_step(question: str, step: dict[str, Any]) -> dict[str, Any]:
    """Repair LLM sloppiness: split owner/repo args and truncated slugs.

    Real LLMs frequently emit ``{"owner": "o", "repo": "r"}`` or a bare
    repo name; both fail tool validation. Rejoin from parts or recover
    the verbatim slug from the question before validation runs.
    """
    from .tools import validate_repo

    name = str(step.get("tool", ""))
    args = dict(step.get("args", {}))
    if name in REPO_TOOLS:
        repo = str(args.get("repo", "") or "")
        owner = str(args.get("owner", "") or "")
        try:
            validate_repo(repo)
        except ValueError:
            if owner and repo and "/" not in repo:
                args["repo"] = f"{owner}/{repo}"
                args.pop("owner", None)
            else:
                slug = extract_repo(question)
                if slug:
                    args["repo"] = slug
                args.pop("owner", None)
    return {"tool": name, "args": args}


def route_after_plan(state: GitHubState) -> str:
    """Gate: route to confirm when a mutating tool is planned."""
    if not state.get("plan"):
        return "short_circuit"
    if state.get("needs_confirmation"):
        return "confirm"
    return "execute"


def confirm_node(state: GitHubState) -> dict[str, Any]:
    """Interrupt gate showing the full mutating payload preview."""
    plan = state.get("plan", [])
    mutating = [s for s in plan if s.get("tool") in MUTATING_TOOLS]
    preview = {
        "payload_preview": mutating,
        "question": state.get("question", ""),
        "hint": 'Resume with {"confirm": true} to proceed, anything else cancels.',
    }
    response = interrupt(preview)
    if isinstance(response, dict) and response.get("confirm") is True:
        return {"confirmed": True, "status": "ok"}
    return {
        "confirmed": False,
        "status": "confirmation_required",
        "answer": "Write operation cancelled: confirmation not granted.",
    }


def route_after_confirm(state: GitHubState) -> str:
    """Proceed to execute only when confirmation was granted."""
    if state.get("confirmed") is True and state.get("status") != "confirmation_required":
        return "execute"
    return str(END)


def execute_node(state: GitHubState) -> dict[str, Any]:
    """Run the planned tools via their LangChain wrappers."""
    plan = state.get("plan", [])
    confirmed = state.get("confirmed") is True
    results: list[dict[str, Any]] = []
    for step in plan:
        name = str(step.get("tool", ""))
        args = dict(step.get("args", {}))
        if name in MUTATING_TOOLS and not confirmed:
            results.append(
                {
                    "tool": name,
                    "status": "blocked",
                    "message": (
                        "Mutating tool blocked: resume with "
                        '{"confirm": true} to execute.'
                    ),
                }
            )
            continue
        tool_obj = TOOLS_BY_NAME.get(name)
        if tool_obj is None:
            results.append({"tool": name, "status": "error", "message": "unknown tool"})
            continue
        try:
            output = tool_obj.invoke(args)
            if isinstance(output, dict):
                payload = dict(output)
            else:
                payload = {"status": "ok", "text": str(output)}
        except Exception as e:
            payload = {"status": "error", "message": str(e)}
        payload["tool"] = name
        results.append(payload)
    ok = [r for r in results if r.get("status") == "ok"]
    status = "ok" if ok else ("error" if results else "empty")
    if any(r.get("status") == "blocked" for r in results) and not ok:
        status = "confirmation_required"
    return {"tool_results": results, "status": status}


def _format_results(results: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for r in results:
        name = r.get("tool", "?")
        if r.get("status") == "ok":
            summary = {k: v for k, v in r.items() if k not in ("tool", "status")}
            lines.append(f"- {name}: {json.dumps(summary)[:500]}")
        else:
            lines.append(f"- {name} [{r.get('status')}]: {r.get('message', '')}")
    return "\n".join(lines) if lines else "(no results)"


def synthesize_node(state: GitHubState) -> dict[str, Any]:
    """Turn tool results into a natural-language answer via the LLM."""
    from makpa.llm import get_llm

    question = state.get("question", "")
    results = state.get("tool_results", [])
    summary = _format_results(results)
    prompt = (
        "Answer the GitHub question from these tool results. "
        "Keep every repo name, number, and title exactly.\n"
        f"Question: {question}\nResults:\n{summary}\nAnswer:"
    )
    try:
        response = get_llm().invoke(prompt)
        content = getattr(response, "content", str(response))
        text = content if isinstance(content, str) else str(content)
    except Exception as e:
        logger.warning("Synthesize LLM failed: %s", e)
        text = summary
    if not text.strip():
        text = summary
    # Always ground the answer with the verbatim result summary.
    if summary not in text:
        text = f"{text.rstrip()}\nDetails:\n{summary}"
    return {"answer": text, "status": state.get("status", "ok")}


def short_circuit_node(state: GitHubState) -> dict[str, Any]:
    """Clean exit when the plan is empty or tools return nothing."""
    question = state.get("question", "")
    if state.get("status") == "error":
        return {"answer": state.get("answer", "empty question"), "status": "error"}
    if not state.get("plan") and question.strip():
        repo_hint = extract_repo(question)
        hint = (
            f" for '{repo_hint}'" if repo_hint else " (try naming an 'owner/repo' slug)"
        )
        return {
            "answer": f"I could not map your request{hint} to a GitHub tool.",
            "status": "empty",
        }
    return {"answer": "No GitHub results found.", "status": "empty"}


def create_github_graph(checkpointer: Any = None) -> Any:
    """Create the GitHub subgraph.

    Args:
        checkpointer: Optional LangGraph checkpointer. Required for
            ``interrupt()`` resume flows (the CLI passes MemorySaver).

    Returns:
        Compiled StateGraph, directly invokable and wrappable by the
        Phase 4 supervisor without modification.
    """
    builder = StateGraph(GitHubState)
    builder.add_node("plan", plan_node)
    builder.add_node("confirm", confirm_node)
    builder.add_node("execute", execute_node)
    builder.add_node("synthesize", synthesize_node)
    builder.add_node("short_circuit", short_circuit_node)

    builder.add_edge(START, "plan")
    builder.add_conditional_edges(
        "plan",
        route_after_plan,
        {"execute": "execute", "confirm": "confirm", "short_circuit": "short_circuit"},
    )
    builder.add_conditional_edges(
        "confirm", route_after_confirm, {"execute": "execute", END: END}
    )
    builder.add_edge("execute", "synthesize")
    builder.add_edge("synthesize", END)
    builder.add_edge("short_circuit", END)
    if checkpointer is not None:
        return builder.compile(checkpointer=checkpointer)
    return builder.compile()


@entrypoint("makpa.github")  # type: ignore[untyped-decorator]
def run_github(question: str) -> dict[str, Any]:
    """Run the GitHub graph once (read-only convenience helper).

    Mutating plans cannot complete without a checkpointer resume, so an
    unconfirmed run returns ``confirmation_required`` instead of executing.
    """
    from langgraph.errors import GraphInterrupt

    from makpa.utils.interrupts import detect_interrupt

    graph = create_github_graph()
    try:
        result = graph.invoke({"question": question})
        pending = detect_interrupt(result) is not None or (
            result.get("needs_confirmation") is True
            and not result.get("tool_results")
        )
        if pending:
            raise GraphInterrupt("confirmation required")
        return dict(result)
    except GraphInterrupt as e:
        logger.info("run_github interrupted (confirmation required): %s", e)
        return {
            "question": question,
            "plan": [],
            "tool_results": [],
            "answer": "Write operation needs confirmation; use the CLI to approve.",
            "needs_confirmation": True,
            "status": "confirmation_required",
        }


__all__ = [
    "TOOLS_BY_NAME",
    "confirm_node",
    "create_github_graph",
    "execute_node",
    "extract_repo",
    "heuristic_plan",
    "plan_node",
    "route_after_confirm",
    "route_after_plan",
    "run_github",
    "short_circuit_node",
    "synthesize_node",
]
