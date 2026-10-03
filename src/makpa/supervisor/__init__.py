"""Supervisor module for MAKPA.

Hub-and-spoke coordination of the three sub-agents: intent router,
supervisor graph with Send-based parallel dispatch, and aggregation.
"""

from .graph import aggregate_results, create_supervisor_graph, run_supervisor
from .router import IntentRouter, Route, classify_intent, route
from .state import SupervisorState

__all__ = [
    "IntentRouter",
    "Route",
    "SupervisorState",
    "aggregate_results",
    "classify_intent",
    "create_supervisor_graph",
    "route",
    "run_supervisor",
]
