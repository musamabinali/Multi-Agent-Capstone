"""Thin HTTP + SSE adapter over the MAKPA supervisor (frontend contract).

No business logic lives here — routing, tools, gates, and aggregation
all belong to the LangGraph supervisor and sub-agents. This package only
serializes state, manages deterministic thread ids, and streams events.
"""

from .server import app, create_app

__all__ = ["app", "create_app"]
