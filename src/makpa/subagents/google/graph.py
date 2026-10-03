"""Google Workspace sub-agent as an isolated LangGraph StateGraph.

Single sub-agent, two services (calendar/gmail), one composite
scheduling flow with exactly two ``interrupt()`` gates. All interrupt
handling goes through the shared ``makpa.utils.interrupts`` helpers.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from makpa.state import GoogleState
from makpa.utils.tracing import entrypoint

from .tools import GOOGLE_TOOLS, MUTATING_TOOLS

logger = logging.getLogger(__name__)

TOOLS_BY_NAME = {t.name: t for t in GOOGLE_TOOLS}

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
ISO_RE = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:?\d{2})?")

COMPOSITE_MARKERS = ("schedule", "set up", "set-up", "organise", "organize")


def extract_emails(question: str) -> list[str]:
    """Extract email addresses from a question."""
    return list(dict.fromkeys(EMAIL_RE.findall(question)))


def extract_isos(question: str) -> list[str]:
    """Extract ISO 8601 timestamps from a question."""
    return ISO_RE.findall(question)


def is_composite_request(question: str) -> bool:
    """Detect the 'schedule a meeting with X at Y' pattern."""
    lowered = question.lower()
    return any(m in lowered for m in COMPOSITE_MARKERS) and any(
        w in lowered for w in ("meeting", "call", "event", "appointment")
    )


def heuristic_plan(question: str) -> tuple[str, list[dict[str, Any]], str]:
    """Keyword fallback planner.

    Returns:
        Tuple of (service, plan steps, action).
    """
    lowered = question.lower()
    emails = extract_emails(question)
    isos = extract_isos(question)
    plan: list[dict[str, Any]] = []

    if is_composite_request(question):
        if len(isos) >= 2 and emails:
            return (
                "both",
                [{"tool": "__composite__", "args": {}}],
                "schedule_meeting",
            )
        return "both", [], "schedule_meeting"
    if "availability" in lowered or "free" in lowered or "busy" in lowered:
        if len(isos) >= 2:
            plan.append(
                {
                    "tool": "calendar_check_availability",
                    "args": {"time_min": isos[0], "time_max": isos[1], "attendees": emails},
                }
            )
        return "calendar", plan, "check_availability"
    if "update" in lowered or "reschedule" in lowered or "move" in lowered:
        match = re.search(r"(evt-[\w-]+|event\s+([\w-]+))", lowered)
        event_id = match.group(1) if match else ""
        args: dict[str, Any] = {"event_id": event_id}
        if isos:
            args["start"] = isos[0]
            if len(isos) > 1:
                args["end"] = isos[1]
        if event_id:
            plan.append({"tool": "calendar_update_event", "args": args})
        return "calendar", plan, "update_event"
    if "create" in lowered or "new event" in lowered or "add event" in lowered:
        if len(isos) >= 2:
            plan.append(
                {
                    "tool": "calendar_create_event",
                    "args": {
                        "summary": question[:120],
                        "start": isos[0],
                        "end": isos[1],
                        "attendees": emails,
                    },
                }
            )
        return "calendar", plan, "create_event"
    if "event" in lowered or "calendar" in lowered or "agenda" in lowered:
        if len(isos) >= 2:
            plan.append(
                {
                    "tool": "calendar_list_events",
                    "args": {"time_min": isos[0], "time_max": isos[1]},
                }
            )
        return "calendar", plan, "list_events"
    if "draft" in lowered or "compose" in lowered:
        if emails:
            plan.append(
                {"tool": "gmail_draft_message", "args": {"to": emails, "subject": question[:120]}}
            )
        return "gmail", plan, "draft_message"
    if "send" in lowered or "email to" in lowered or "mail to" in lowered:
        if emails:
            plan.append(
                {"tool": "gmail_send_message", "args": {"to": emails, "subject": question[:120]}}
            )
        return "gmail", plan, "send_message"
    if "read" in lowered or "open" in lowered or "show" in lowered:
        match = re.search(r"(msg-[\w-]+)", lowered)
        if match:
            plan.append({"tool": "gmail_read_message", "args": {"message_id": match.group(1)}})
        return "gmail", plan, "read_message"
    if "search" in lowered or "find" in lowered or "inbox" in lowered or "mail" in lowered:
        plan.append({"tool": "gmail_search_messages", "args": {"query": question}})
        return "gmail", plan, "search_messages"
    return "calendar", [], "unknown"


def _llm_plan(question: str) -> tuple[str, list[dict[str, Any]], str] | None:
    """Ask the LLM to pick service and tools; None when unparseable."""
    from makpa.llm import get_llm

    catalog = "\n".join(f"- {t.name}: {t.description}" for t in GOOGLE_TOOLS)
    prompt = (
        "Pick Google Workspace tools for the question. Reply with ONLY JSON: "
        '{"service": "calendar|gmail|both", "action": name, '
        '"plan": [{"tool": name, "args": {...}}]}.\n'
        "Copy email addresses and ISO 8601 timestamps verbatim from the "
        "question; never invent them.\n"
        f"Tools:\n{catalog}\nQuestion: {question}\nJSON:"
    )
    try:
        response = get_llm().invoke(prompt)
        content = getattr(response, "content", str(response))
        text = content if isinstance(content, str) else str(content)
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end == -1:
            return None
        parsed = json.loads(text[start : end + 1])
        steps: list[dict[str, Any]] = []
        for item in parsed.get("plan", []):
            if isinstance(item, dict) and item.get("tool") in TOOLS_BY_NAME:
                steps.append({"tool": item["tool"], "args": dict(item.get("args", {}))})
        service = str(parsed.get("service", "calendar"))
        if service not in ("calendar", "gmail", "both"):
            service = "calendar"
        action = str(parsed.get("action", "unknown"))
        return service, steps, action
    except Exception as e:
        logger.warning("LLM planning failed, using heuristic: %s", e)
        return None


def plan_node(state: GoogleState) -> dict[str, Any]:
    """Pick service, action, and tool steps for the question."""
    question = state.get("question", "")
    if not question.strip():
        return {
            "plan": [],
            "tool_results": [],
            "service": "calendar",
            "action": "unknown",
            "status": "error",
            "answer": "empty question",
        }
    if is_composite_request(question):
        service, steps, action = heuristic_plan(question)
    else:
        llm_result = _llm_plan(question)
        if llm_result is None:
            service, steps, action = heuristic_plan(question)
        else:
            service, steps, action = llm_result
    steps = [s for s in steps if s.get("tool") in TOOLS_BY_NAME or s.get("tool") == "__composite__"]
    needs_confirmation = any(s["tool"] in MUTATING_TOOLS for s in steps)
    update: dict[str, Any] = {
        "service": service,
        "action": action,
        "plan": steps,
        "needs_confirmation": needs_confirmation,
        "status": "ok",
    }
    if action == "schedule_meeting":
        update["composite_stage"] = "check"
    return update


def route_after_plan(state: GoogleState) -> str:
    """Gate: composite, confirm, execute, or short-circuit."""
    if not state.get("plan"):
        return "short_circuit"
    if state.get("action") == "schedule_meeting" and any(
        s.get("tool") == "__composite__" for s in state.get("plan", [])
    ):
        return "composite_check"
    if state.get("needs_confirmation"):
        return "confirm"
    return "execute"


def confirm_node(state: GoogleState) -> dict[str, Any]:
    """Interrupt gate for single mutating plans."""
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
        "status": "cancelled",
        "answer": "Operation cancelled: confirmation not granted; no changes were made.",
    }


def route_after_confirm(state: GoogleState) -> str:
    """Proceed to execute only when confirmation was granted."""
    if state.get("confirmed") is True and state.get("status") != "cancelled":
        return "execute"
    return str(END)


def execute_node(state: GoogleState) -> dict[str, Any]:
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
                    "message": 'Mutating tool blocked: resume with {"confirm": true} to execute.',
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


def _run_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    """Run one catalog tool synchronously, normalizing failures."""
    tool_obj = TOOLS_BY_NAME.get(name)
    if tool_obj is None:
        return {"tool": name, "status": "error", "message": "unknown tool"}
    try:
        output = tool_obj.invoke(args)
        if isinstance(output, dict):
            payload = dict(output)
        else:
            payload = {"status": "ok", "text": str(output)}
    except Exception as e:
        payload = {"status": "error", "message": str(e)}
    payload["tool"] = name
    return payload


def composite_check_node(state: GoogleState) -> dict[str, Any]:
    """Step 1 of the composite flow: availability for the requested window."""
    question = state.get("question", "")
    isos = extract_isos(question)
    emails = extract_emails(question)
    result = _run_tool(
        "calendar_check_availability",
        {"time_min": isos[0], "time_max": isos[1], "attendees": emails},
    )
    return {
        "tool_results": [result],
        "payload": {"time_min": isos[0], "time_max": isos[1], "attendees": emails},
        "composite_stage": "checked",
        "status": "ok" if result.get("status") == "ok" else "error",
    }


def route_after_check(state: GoogleState) -> str:
    """Busy or partial slots propose alternatives; verified-free plans the event."""
    results = state.get("tool_results", [])
    if not results or results[0].get("status") != "ok":
        return "synthesize"
    if results[0].get("partial") is True:
        return "synthesize"
    if results[0].get("free") is True:
        return "composite_plan_event"
    return "synthesize"


def composite_plan_event_node(state: GoogleState) -> dict[str, Any]:
    """Step 3: build the calendar_create_event payload."""
    question = state.get("question", "")
    stored = state.get("payload", {})
    summary = question[:120]
    title_match = re.search(
        r"(?:meeting|call|event)\s+(?:about|re:?)\s*(.+?)(?:\s+with|\s+from|$)",
        question,
        re.IGNORECASE,
    )
    if title_match:
        summary = title_match.group(1).strip()[:120]
    plan = [
        {
            "tool": "calendar_create_event",
            "args": {
                "summary": summary,
                "start": stored.get("time_min", ""),
                "end": stored.get("time_max", ""),
                "attendees": stored.get("attendees", []),
                "description": f"Scheduled via MAKPA: {question[:200]}",
            },
        }
    ]
    return {"plan": plan, "needs_confirmation": True, "composite_stage": "event_planned"}


def confirm_event_node(state: GoogleState) -> dict[str, Any]:
    """Gate 1: boxed event preview before creating."""
    preview = {
        "gate": 1,
        "payload_preview": state.get("plan", []),
        "question": state.get("question", ""),
        "hint": 'Resume with {"confirm": true} to create the event, anything else cancels.',
    }
    response = interrupt(preview)
    if isinstance(response, dict) and response.get("confirm") is True:
        return {"confirmed": True, "status": "ok", "composite_stage": "event_confirmed"}
    return {
        "confirmed": False,
        "status": "cancelled",
        "composite_stage": "event_cancelled",
        "answer": "Scheduling cancelled at gate 1: no event was created and no email was sent.",
    }


def route_after_confirm_event(state: GoogleState) -> str:
    """Create the event only when gate 1 was confirmed."""
    if state.get("confirmed") is True and state.get("status") != "cancelled":
        return "composite_create"
    return str(END)


def composite_create_node(state: GoogleState) -> dict[str, Any]:
    """Step 5: create the event (gate 1 already confirmed)."""
    if state.get("confirmed") is not True:
        blocked = {
            "tool": "calendar_create_event",
            "status": "blocked",
            "message": 'Gate 1 not confirmed; event was not created.',
        }
        return {
            "tool_results": [*state.get("tool_results", []), blocked],
            "status": "cancelled",
        }
    created = _run_tool(
        "calendar_create_event", dict(state.get("plan", [{}])[0].get("args", {}))
    )
    return {
        "tool_results": [*state.get("tool_results", []), created],
        "composite_stage": "event_created",
        "status": "ok" if created.get("status") == "ok" else "error",
    }


def composite_plan_email_node(state: GoogleState) -> dict[str, Any]:
    """Step 6: draft the meeting email from the created event (safe)."""
    results = state.get("tool_results", [])
    created = next(
        (
            r
            for r in results
            if r.get("tool") == "calendar_create_event" and r.get("status") == "ok"
        ),
        None,
    )
    event = (created or {}).get("event", {})
    stored = state.get("payload", {})
    attendees = stored.get("attendees", [])
    subject = f"Meeting scheduled: {event.get('summary', 'your meeting')}"
    body = (
        f"Your meeting is scheduled.\nWhen: {event.get('start', '')} to {event.get('end', '')}\n"
        f"Link: {event.get('html_link', '')}\n"
    )
    drafted = _run_tool(
        "gmail_draft_message", {"to": attendees, "subject": subject, "body": body}
    )
    draft_id = ""
    if drafted.get("status") == "ok":
        draft_id = str(drafted.get("draft", {}).get("id", ""))
    send_plan = [
        {
            "tool": "gmail_send_message",
            "args": {"to": attendees, "subject": subject, "body": body, "draft_id": draft_id},
        }
    ]
    return {
        "tool_results": [*results, drafted],
        "plan": send_plan,
        "needs_confirmation": True,
        "composite_stage": "email_planned",
        "status": "ok",
    }


def confirm_email_node(state: GoogleState) -> dict[str, Any]:
    """Gate 2: boxed email preview before sending (supports rollback)."""
    preview = {
        "gate": 2,
        "payload_preview": state.get("plan", []),
        "question": state.get("question", ""),
        "note": "Declining keeps the created calendar event; only the email is skipped.",
        "hint": 'Resume with {"confirm": true} to send, {"rollback": true} '
        "to cancel the event too, anything else cancels.",
    }
    response = interrupt(preview)
    if isinstance(response, dict) and response.get("confirm") is True:
        return {"confirmed": True, "status": "ok", "composite_stage": "email_confirmed"}
    if isinstance(response, dict) and response.get("rollback") is True:
        return {
            "confirmed": False,
            "status": "rollback_requested",
            "composite_stage": "rollback_requested",
        }
    return {
        "confirmed": False,
        "status": "cancelled",
        "composite_stage": "email_cancelled",
        "answer": (
            "Email cancelled at gate 2: the calendar event stays as created; "
            "no email was sent."
        ),
    }


def route_after_confirm_email(state: GoogleState) -> str:
    """Send on confirm, roll back on rollback, end otherwise."""
    if state.get("confirmed") is True and state.get("status") != "cancelled":
        return "composite_send"
    if state.get("status") == "rollback_requested":
        return "composite_rollback"
    return str(END)


def composite_send_node(state: GoogleState) -> dict[str, Any]:
    """Step 8: send the email (gate 2 already confirmed)."""
    if state.get("confirmed") is not True:
        blocked = {
            "tool": "gmail_send_message",
            "status": "blocked",
            "message": "Gate 2 not confirmed; email was not sent.",
        }
        return {
            "tool_results": [*state.get("tool_results", []), blocked],
            "status": "cancelled",
        }
    sent = _run_tool("gmail_send_message", dict(state.get("plan", [{}])[0].get("args", {})))
    return {
        "tool_results": [*state.get("tool_results", []), sent],
        "composite_stage": "email_sent",
        "status": "ok" if sent.get("status") == "ok" else "error",
    }


def composite_rollback_node(state: GoogleState) -> dict[str, Any]:
    """Gate-2 rollback: cancel the created event, then report."""
    created = next(
        (
            r
            for r in state.get("tool_results", [])
            if r.get("tool") == "calendar_create_event" and r.get("status") == "ok"
        ),
        None,
    )
    event_id = str((created or {}).get("event", {}).get("id", ""))
    if not event_id:
        blocked = {
            "tool": "calendar_update_event",
            "status": "error",
            "message": "Rollback failed: no created event id found.",
        }
        return {
            "tool_results": [*state.get("tool_results", []), blocked],
            "status": "error",
        }
    cancelled = _run_tool(
        "calendar_update_event", {"event_id": event_id, "status": "cancelled"}
    )
    ok = cancelled.get("status") == "ok"
    answer = (
        "Rolled back at gate 2: the calendar event "
        f"{event_id} was cancelled and no email was sent."
        if ok
        else f"Rollback failed for event {event_id}: {cancelled.get('message', '')}"
    )
    return {
        "tool_results": [*state.get("tool_results", []), cancelled],
        "composite_stage": "rolled_back",
        "status": "rolled_back" if ok else "error",
        "answer": answer,
    }


def _format_results(results: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for item in results:
        name = item.get("tool", "?")
        if item.get("status") == "ok":
            summary = {k: v for k, v in item.items() if k not in ("tool", "status")}
            lines.append(f"- {name}: {json.dumps(summary)[:500]}")
        else:
            lines.append(f"- {name} [{item.get('status')}]: {item.get('message', '')}")
    return "\n".join(lines) if lines else "(no results)"


def synthesize_node(state: GoogleState) -> dict[str, Any]:
    """Turn tool results into a natural-language answer via the LLM."""
    from makpa.llm import get_llm

    question = state.get("question", "")
    results = state.get("tool_results", [])
    summary = _format_results(results)
    if state.get("action") == "schedule_meeting" and results:
        first = results[0]
        if first.get("tool") == "calendar_check_availability" and first.get("status") == "ok":
            if first.get("partial") is True:
                summary = (
                    "Availability is PARTIAL (own calendar only; attendee "
                    "calendars were not verified). Auto-create is refused "
                    "with external attendees present. Either confirm the "
                    "attendees manually or re-run with "
                    "GOOGLE_CALENDAR_ATTENDEE_MODE=all. Known results:\n" + summary
                )
            elif first.get("free") is not True:
                summary = (
                    "The requested slot is busy. Busy blocks: "
                    f"{json.dumps(first.get('busy', []))}. "
                    "Please propose two alternative windows. Known results:\n" + summary
                )
    prompt = (
        "Answer the Google Workspace question from these tool results. "
        "Keep every id, link, and timestamp exactly.\n"
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
    if summary not in text:
        text = f"{text.rstrip()}\nDetails:\n{summary}"
    return {"answer": text, "status": state.get("status", "ok")}


def short_circuit_node(state: GoogleState) -> dict[str, Any]:
    """Clean exit for empty plans and cancellations."""
    if state.get("status") in ("cancelled", "error"):
        return {
            "answer": state.get("answer", "No changes were made."),
            "status": state.get("status", "empty"),
        }
    question = state.get("question", "")
    if state.get("action") == "schedule_meeting":
        return {
            "answer": (
                "To schedule a meeting I need attendee emails and an ISO time window, "
                'e.g. "schedule a meeting with a@example.com from '
                '2026-10-02T15:00:00Z to 2026-10-02T16:00:00Z".'
            ),
            "status": "empty",
        }
    if question.strip():
        return {
            "answer": "I could not map your request to a Calendar or Gmail tool.",
            "status": "empty",
        }
    return {"answer": "No Google results found.", "status": "empty"}


def create_google_graph(checkpointer: Any = None) -> Any:
    """Create the Google Workspace subgraph.

    Args:
        checkpointer: Optional LangGraph checkpointer. Required for
            ``interrupt()`` resume flows (the CLI passes MemorySaver).

    Returns:
        Compiled StateGraph, directly invokable and wrappable by the
        Phase 4 supervisor without modification.
    """
    builder = StateGraph(GoogleState)
    builder.add_node("plan", plan_node)
    builder.add_node("confirm", confirm_node)
    builder.add_node("execute", execute_node)
    builder.add_node("synthesize", synthesize_node)
    builder.add_node("short_circuit", short_circuit_node)
    builder.add_node("composite_check", composite_check_node)
    builder.add_node("composite_plan_event", composite_plan_event_node)
    builder.add_node("confirm_event", confirm_event_node)
    builder.add_node("composite_create", composite_create_node)
    builder.add_node("composite_plan_email", composite_plan_email_node)
    builder.add_node("confirm_email", confirm_email_node)
    builder.add_node("composite_send", composite_send_node)
    builder.add_node("composite_rollback", composite_rollback_node)

    builder.add_edge(START, "plan")
    builder.add_conditional_edges(
        "plan",
        route_after_plan,
        {
            "execute": "execute",
            "confirm": "confirm",
            "short_circuit": "short_circuit",
            "composite_check": "composite_check",
        },
    )
    builder.add_conditional_edges(
        "confirm", route_after_confirm, {"execute": "execute", END: END}
    )
    builder.add_conditional_edges(
        "composite_check",
        route_after_check,
        {"composite_plan_event": "composite_plan_event", "synthesize": "synthesize"},
    )
    builder.add_edge("composite_plan_event", "confirm_event")
    builder.add_conditional_edges(
        "confirm_event",
        route_after_confirm_event,
        {"composite_create": "composite_create", END: END},
    )
    builder.add_edge("composite_create", "composite_plan_email")
    builder.add_edge("composite_plan_email", "confirm_email")
    builder.add_conditional_edges(
        "confirm_email",
        route_after_confirm_email,
        {
            "composite_send": "composite_send",
            "composite_rollback": "composite_rollback",
            END: END,
        },
    )
    builder.add_edge("composite_send", "synthesize")
    builder.add_edge("composite_rollback", "synthesize")
    builder.add_edge("execute", "synthesize")
    builder.add_edge("synthesize", END)
    builder.add_edge("short_circuit", END)
    if checkpointer is not None:
        return builder.compile(checkpointer=checkpointer)
    return builder.compile()


@entrypoint("makpa.google")  # type: ignore[untyped-decorator]
def run_google(question: str) -> dict[str, Any]:
    """Run the Google graph once (read-only convenience helper).

    Plans needing confirmation cannot complete without a checkpointer
    resume, so they return ``confirmation_required`` instead of executing.
    """
    from langgraph.errors import GraphInterrupt

    from makpa.utils.interrupts import detect_interrupt

    graph = create_google_graph()
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
        logger.info("run_google interrupted (confirmation required): %s", e)
        return {
            "question": question,
            "service": "calendar",
            "action": "unknown",
            "plan": [],
            "tool_results": [],
            "answer": "Write operation needs confirmation; use the CLI to approve.",
            "needs_confirmation": True,
            "status": "confirmation_required",
        }


__all__ = [
    "TOOLS_BY_NAME",
    "composite_check_node",
    "composite_create_node",
    "composite_plan_email_node",
    "composite_plan_event_node",
    "composite_rollback_node",
    "composite_send_node",
    "confirm_email_node",
    "confirm_event_node",
    "confirm_node",
    "create_google_graph",
    "execute_node",
    "extract_emails",
    "extract_isos",
    "heuristic_plan",
    "is_composite_request",
    "plan_node",
    "route_after_check",
    "route_after_confirm",
    "route_after_confirm_email",
    "route_after_confirm_event",
    "route_after_plan",
    "run_google",
    "short_circuit_node",
    "synthesize_node",
]
