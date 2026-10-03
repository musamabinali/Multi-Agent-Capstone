"""MAKPA end-to-end demo script (Phase 4).

Runs a fixed three-scenario script through the supervisor, prints the
routing decision, sub-agents invoked, tools called, answers, and timing
per scenario, and exits zero only if every scenario succeeded.

 Gates are auto-confirmed for the non-interactive demo run (each
auto-confirm is logged explicitly). Use the interactive CLI for
human-in-the-loop approvals.

Usage:
    python scripts/demo.py [--mode demo|free|live]
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("makpa.demo")


def next_tuesday_15utc(now: datetime | None = None) -> tuple[str, str]:
    """Next Tuesday 15:00-16:00 UTC as ISO strings (demo scheduling window)."""
    base = now or datetime.now(timezone.utc)
    days_ahead = (1 - base.weekday()) % 7 or 7
    day = (base + timedelta(days=days_ahead)).replace(
        hour=15, minute=0, second=0, microsecond=0
    )
    end = day + timedelta(hours=1)
    return day.isoformat(), end.isoformat()


def build_scenarios() -> list[dict[str, Any]]:
    """Build the three fixed demo scenarios."""
    start, end = next_tuesday_15utc()
    return [
        {
            "name": "RAG scenario",
            "question": "What does the sample PDF say about implementation details?",
            "auto_confirms": [],
        },
        {
            "name": "GitHub scenario",
            "question": "List open pull requests in octo-demo/hello-world.",
            "auto_confirms": [],
        },
        {
            "name": "Composite scenario",
            "question": (
                "Schedule a meeting with a@example.com "
                f"from {start} to {end} and email them the agenda."
            ),
            "auto_confirms": [{"confirm": True}, {"confirm": True}],
        },
    ]


def run_scenario(
    graph: Any, config: dict[str, Any], scenario: dict[str, Any]
) -> dict[str, Any]:
    """Run one scenario with demo auto-confirmation of gates."""
    from langchain_core.messages import HumanMessage

    from makpa.utils.interrupts import detect_interrupt, resume_with

    question = str(scenario["question"])
    confirms = list(scenario.get("auto_confirms", []))
    print(f"\n=== {scenario['name']} ===")
    print(f"Question: {question}")
    started = time.monotonic()
    agent_started: dict[str, float] = {}
    _ = agent_started
    try:
        result = graph.invoke({"messages": [HumanMessage(content=question)]}, config)
    except Exception as e:  # noqa: BLE001
        return {"name": scenario["name"], "ok": False, "error": str(e)}
    resumes = 0
    while detect_interrupt(result) is not None or _paused(graph, config):
        if resumes >= len(confirms):
            return {
                "name": scenario["name"],
                "ok": False,
                "error": "demo ran out of auto-confirms",
            }
        payload = confirms[resumes]
        resumes += 1
        print(f"[demo auto-confirm {resumes}: {payload}]")
        try:
            result = resume_with(graph, config, payload)
        except Exception as e:  # noqa: BLE001
            return {"name": scenario["name"], "ok": False, "error": str(e)}
    elapsed = time.monotonic() - started
    report = _report_result(result)
    report.update({"name": scenario["name"], "seconds": round(elapsed, 1)})
    print(f"Routing: {report.get('agents')}")
    print(f"Tools: {report.get('tools')}")
    print(f"Answer: {report.get('answer', '')[:800]}")
    print(f"Status: {report.get('status')} in {report['seconds']}s")
    report["ok"] = report.get("status") in ("ok", "partial")
    return report


def _paused(graph: Any, config: dict[str, Any]) -> bool:
    try:
        return bool(graph.get_state(config).next)
    except Exception:  # noqa: BLE001
        return False


def _report_result(result: dict[str, Any]) -> dict[str, Any]:
    """Extract routing, tools, answer, and status for the transcript."""
    agents = result.get("next", [])
    outputs = result.get("agent_outputs", {})
    tools: list[str] = []
    if isinstance(outputs, dict):
        for raw in outputs.values():
            try:
                data = json.loads(raw)
            except (ValueError, TypeError):
                continue
            for item in data.get("tools", []) if isinstance(data, dict) else []:
                if isinstance(item, dict) and item.get("tool"):
                    tools.append(str(item["tool"]))
    messages = result.get("messages", [])
    answer = ""
    if messages:
        last = messages[-1]
        answer = str(getattr(last, "content", last))
    return {
        "agents": agents,
        "tools": tools,
        "answer": answer,
        "status": result.get("status", "error"),
    }


def run_all() -> tuple[list[dict[str, Any]], int]:
    """Run all scenarios; returns (reports, exit_code)."""
    from langgraph.checkpoint.memory import MemorySaver

    from makpa.config import get_settings, print_startup_banner
    from makpa.supervisor import create_supervisor_graph

    print_startup_banner()
    settings = get_settings()
    print(f"Demo mode: {settings.resolved_mode.value}")
    graph = create_supervisor_graph(checkpointer=MemorySaver())
    reports = []
    scenarios = build_scenarios()
    for index, scenario in enumerate(scenarios):
        # Deterministic per-scenario thread: isolates state between scenarios.
        config = {"configurable": {"thread_id": f"{settings.thread_id_prefix}-demo-{index}"}}
        if scenario["name"] == "Composite scenario":
            # The flagship two-gate flow needs full attendee verification;
            # default own_only would (correctly) refuse. Logged, not hidden.
            os.environ["GOOGLE_CALENDAR_ATTENDEE_MODE"] = "all"
            if hasattr(get_settings, "cache_clear"):
                get_settings.cache_clear()
            print("[demo: GOOGLE_CALENDAR_ATTENDEE_MODE=all for the composite flow]")
        reports.append(run_scenario(graph, config, scenario))
    ok = all(report.get("ok") for report in reports)
    print("\n=== Demo summary ===")
    for report in reports:
        print(f"- {report['name']}: {'OK' if report.get('ok') else 'FAIL'}")
    return reports, 0 if ok else 1


def main() -> int:
    """Entry point (supports --mode for one run)."""
    parser = argparse.ArgumentParser(description="MAKPA end-to-end demo")
    parser.add_argument("--mode", default="", help="demo|free|live override")
    args = parser.parse_args()
    if args.mode:
        choice = args.mode.strip().lower()
        if choice not in ("demo", "free", "live"):
            print(f"Invalid mode {args.mode!r}", file=sys.stderr)
            return 1
        os.environ["MAKPA_MODE"] = choice
        from makpa.config import get_settings

        if hasattr(get_settings, "cache_clear"):
            get_settings.cache_clear()
    _, code = run_all()
    return code


if __name__ == "__main__":
    raise SystemExit(main())
