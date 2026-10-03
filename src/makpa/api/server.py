"""FastAPI thin adapter for the MAKPA web frontend.

Endpoints (see Frontend Build §9.1):
    POST   /api/threads            -> {thread_id}
    GET    /api/threads            -> thread list
    GET    /api/threads/{id}       -> full thread state + history
    DELETE /api/threads/{id}       -> forget thread
    POST   /api/threads/{id}/invoke -> one-shot query (no streaming)
    POST   /api/threads/{id}/stream -> SSE stream of agent events
    POST   /api/threads/{id}/resume -> resume after interrupt()
    GET    /api/health             -> mode + MCP reachability
    POST   /api/ingest             -> trigger PDF ingestion

Thread ids are deterministic: ``{prefix}-web-{counter:04d}``. No random UUIDs.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App factory (single shared graph + checkpointer; thread isolation via config)
# ---------------------------------------------------------------------------

_graph: Any = None
_checkpointer: Any = None
_graph_lock = threading.Lock()
_thread_counter = 0
_thread_counter_lock = threading.Lock()
_thread_meta: dict[str, dict[str, Any]] = {}


def _get_graph() -> Any:
    """Lazily build the shared supervisor graph (one MemorySaver, many threads)."""
    global _graph, _checkpointer
    if _graph is not None:
        return _graph
    with _graph_lock:
        if _graph is not None:
            return _graph
        from langgraph.checkpoint.memory import MemorySaver

        from makpa.supervisor import create_supervisor_graph

        _checkpointer = MemorySaver()
        _graph = create_supervisor_graph(checkpointer=_checkpointer)
        return _graph


def _config_for(thread_id: str) -> dict[str, Any]:
    return {"configurable": {"thread_id": thread_id}}


def _new_thread_id() -> str:
    from makpa.config import get_settings

    global _thread_counter
    with _thread_counter_lock:
        _thread_counter += 1
        n = _thread_counter
    prefix = get_settings().thread_id_prefix
    return f"{prefix}-web-{n:04d}"


# ---------------------------------------------------------------------------
# Serialization helpers (no business logic)
# ---------------------------------------------------------------------------

AGENT_NAMES = ("rag_agent", "github_agent", "google_agent")


def _serialize_message(msg: Any) -> dict[str, Any]:
    if isinstance(msg, HumanMessage):
        role = "user"
    elif isinstance(msg, AIMessage):
        role = "assistant"
    else:
        role = str(getattr(msg, "type", "unknown"))
    content = getattr(msg, "content", msg)
    if not isinstance(content, str):
        content = str(content)
    return {"role": role, "content": content}


def _parse_agent_outputs(raw: Any) -> dict[str, Any]:
    """Parse the supervisor's JSON-encoded agent_outputs into plain dicts."""
    parsed: dict[str, Any] = {}
    if not isinstance(raw, dict):
        return parsed
    for name, blob in raw.items():
        try:
            data = json.loads(blob) if isinstance(blob, str) else dict(blob)
        except (ValueError, TypeError):
            data = {"agent": name, "status": "error", "answer": str(blob)}
        if not isinstance(data, dict):
            data = {"agent": name, "status": "error", "answer": str(data)}
        data.setdefault("agent", name)
        data.setdefault("status", "error")
        data.setdefault("answer", "")
        parsed[name] = data
    return parsed


def _pending_preview(graph: Any, config: dict[str, Any]) -> dict[str, Any] | None:
    """Extract the interrupt() payload preview from a paused graph."""
    try:
        snapshot = graph.get_state(config)
    except Exception:
        return None
    for task in getattr(snapshot, "tasks", []):
        for interrupt_obj in getattr(task, "interrupts", []):
            value = getattr(interrupt_obj, "value", None)
            if isinstance(value, dict):
                return dict(value)
    return None


def _is_paused(graph: Any, config: dict[str, Any]) -> bool:
    try:
        return bool(graph.get_state(config).next)
    except Exception:
        return False


def _attribute_agent(preview: dict[str, Any]) -> str:
    blob = json.dumps(preview, default=str)
    if "gmail_" in blob:
        return "google_agent"
    if "calendar_" in blob:
        return "google_agent"
    if "github_" in blob:
        return "github_agent"
    return "google_agent"


def _interrupt_kind(preview: dict[str, Any]) -> str:
    """Derive a stable gate kind for the frontend contract.

    Composite gates carry ``gate: 1 | 2``; single mutating gates carry only
    ``payload_preview`` (a plan list), so the kind falls back to the first
    planned tool name (e.g. ``calendar_create_event``), else ``confirm``.
    """
    if "action" in preview:
        return str(preview["action"])
    if "gate" in preview:
        return str(preview["gate"])
    plans = preview.get("payload_preview", [])
    if isinstance(plans, list) and plans:
        first = plans[0]
        if isinstance(first, dict) and first.get("tool"):
            return str(first["tool"])
    return "confirm"


def _sse(kind: str, payload: dict[str, Any]) -> str:
    """Format one SSE event block (single place for the wire format)."""
    return f"event: {kind}\ndata: {json.dumps(payload, default=str)}\n\n"


def _thread_state(thread_id: str, result: dict[str, Any]) -> dict[str, Any]:
    """Normalize a supervisor invoke result into the frontend contract."""
    graph = _get_graph()
    config = _config_for(thread_id)
    preview = _pending_preview(graph, config)
    paused = preview is not None or _is_paused(graph, config)
    messages = result.get("messages", [])
    # Fall back to checkpointer snapshot when invoke returned only __interrupt__.
    if not messages:
        try:
            snapshot = graph.get_state(config)
            values = getattr(snapshot, "values", {}) or {}
            if isinstance(values, dict) and values.get("messages"):
                messages = values["messages"]
        except Exception:
            messages = []
    outputs = _parse_agent_outputs(result.get("agent_outputs", {}))
    if not outputs:
        try:
            snapshot = graph.get_state(config)
            values = getattr(snapshot, "values", {}) or {}
            if isinstance(values, dict):
                outputs = _parse_agent_outputs(values.get("agent_outputs", {}))
        except Exception:
            pass
    agents = list(result.get("next", []))
    if not agents:
        try:
            snapshot = graph.get_state(config)
            values = getattr(snapshot, "values", {}) or {}
            if isinstance(values, dict) and isinstance(values.get("next"), list):
                agents = list(values["next"])
        except Exception:
            agents = []
    status = str(result.get("status", ""))
    if paused and status not in ("cancelled", "error"):
        status = "confirmation_required"
    if not status:
        try:
            snapshot = graph.get_state(config)
            values = getattr(snapshot, "values", {}) or {}
            if isinstance(values, dict) and values.get("status"):
                status = str(values["status"])
        except Exception:
            status = ""
    interrupt_payload: dict[str, Any] | None = None
    if preview is not None:
        interrupt_payload = {
            "agent": _attribute_agent(preview),
            "kind": _interrupt_kind(preview),
            "payload": preview,
        }
    return {
        "thread_id": thread_id,
        "agents": agents,
        "agent_outputs": outputs,
        "status": status or ("confirmation_required" if paused else "ok"),
        "messages": [_serialize_message(m) for m in messages],
        "pending_interrupt": interrupt_payload,
        "paused": paused,
    }


def _invoke_new_message(thread_id: str, message: str) -> dict[str, Any]:
    """Append a user message to the thread history and invoke the supervisor."""
    from langgraph.errors import GraphInterrupt

    graph = _get_graph()
    config = _config_for(thread_id)
    try:
        snapshot = graph.get_state(config)
        existing = list((getattr(snapshot, "values", {}) or {}).get("messages", []))
    except Exception:
        existing = []
    new_messages = [*existing, HumanMessage(content=message)]
    try:
        result = graph.invoke({"messages": new_messages}, config)
    except GraphInterrupt:
        result = {"__interrupt__": [True]}
    if not isinstance(result, dict):
        result = {"answer": str(result)}
    return dict(result)


def _resume_thread(thread_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Resume a paused thread with {"confirm": bool} or {"rollback": True}."""
    from langgraph.errors import GraphInterrupt

    from makpa.utils.interrupts import resume_with

    graph = _get_graph()
    config = _config_for(thread_id)
    if not _is_paused(graph, config):
        raise HTTPException(status_code=409, detail="thread is not paused at a gate")
    try:
        result = resume_with(graph, config, payload)
    except GraphInterrupt:
        result = {"__interrupt__": [True]}
    except Exception as e:
        logger.warning("resume failed for %s: %s", thread_id, e)
        raise HTTPException(status_code=500, detail=str(e))
    return dict(result)


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------


class InvokeRequest(BaseModel):  # type: ignore[misc]
    message: str = Field(min_length=1, description="Natural-language query")


class ResumeRequest(BaseModel):  # type: ignore[misc]
    confirm: bool | None = Field(default=None)
    rollback: bool | None = Field(default=None)


class IngestRequest(BaseModel):  # type: ignore[misc]
    path: str | None = Field(default=None, description="PDF path or URL")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    app = FastAPI(title="MAKPA adapter", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")  # type: ignore[untyped-decorator]
    def health() -> dict[str, Any]:
        from makpa.config import get_settings

        settings = get_settings()
        probe: dict[str, Any] = {}
        try:
            from makpa.llm import probe_llm

            result = probe_llm()
            probe = {
                "provider": result.provider,
                "model": result.model,
                "ok": result.ok,
                "warnings": result.warnings,
            }
        except RuntimeError as e:
            probe = {"ok": False, "error": str(e)}
        except Exception as e:
            probe = {"ok": False, "error": str(e)}
        return {
            "mode": settings.resolved_mode.value,
            "requested_mode": settings.makpa_mode.value,
            "llm_provider": settings.resolved_llm_provider.value,
            "vector_store": settings.resolved_vector_store.value,
            "embedding_provider": settings.embedding_provider.value,
            "github_path": settings.resolved_github_mcp_path,
            "google_path": settings.resolved_google_mcp_mode.value,
            "oauth_state": settings.resolved_google_oauth_state,
            "downgrades": list(settings.downgrade_reasons),
            "probe": probe,
            "time": datetime.now(timezone.utc).isoformat(),
        }

    @app.post("/api/threads")  # type: ignore[untyped-decorator]
    def create_thread() -> dict[str, Any]:
        thread_id = _new_thread_id()
        _thread_meta[thread_id] = {
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return {"thread_id": thread_id}

    @app.get("/api/threads")  # type: ignore[untyped-decorator]
    def list_threads() -> dict[str, Any]:
        return {
            "threads": [
                {"thread_id": tid, **meta} for tid, meta in _thread_meta.items()
            ]
        }

    @app.get("/api/threads/{thread_id}")  # type: ignore[untyped-decorator]
    def get_thread(thread_id: str) -> dict[str, Any]:
        graph = _get_graph()
        config = _config_for(thread_id)
        try:
            snapshot = graph.get_state(config)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"unknown thread: {e}")
        values = getattr(snapshot, "values", {}) or {}
        if not values and thread_id not in _thread_meta:
            raise HTTPException(status_code=404, detail="unknown thread")
        state = _thread_state(thread_id, dict(values) if isinstance(values, dict) else {})
        state["created_at"] = _thread_meta.get(thread_id, {}).get("created_at")
        return state

    @app.delete("/api/threads/{thread_id}")  # type: ignore[untyped-decorator]
    def delete_thread(thread_id: str) -> dict[str, Any]:
        _thread_meta.pop(thread_id, None)
        return {"thread_id": thread_id, "deleted": True}

    @app.post("/api/threads/{thread_id}/invoke")  # type: ignore[untyped-decorator]
    def invoke(thread_id: str, req: InvokeRequest) -> dict[str, Any]:
        _thread_meta.setdefault(
            thread_id, {"created_at": datetime.now(timezone.utc).isoformat()}
        )
        try:
            result = _invoke_new_message(thread_id, req.message)
        except Exception as e:
            logger.warning("invoke failed for %s: %s", thread_id, e)
            raise HTTPException(status_code=500, detail=str(e))
        return _thread_state(thread_id, result)

    @app.post("/api/threads/{thread_id}/resume")  # type: ignore[untyped-decorator]
    def resume(thread_id: str, req: ResumeRequest) -> dict[str, Any]:
        if req.rollback:
            payload = {"rollback": True}
        elif req.confirm is True:
            payload = {"confirm": True}
        elif req.confirm is False:
            payload = {"confirm": False}
        else:
            raise HTTPException(
                status_code=422, detail="provide confirm:true/false or rollback:true"
            )
        result = _resume_thread(thread_id, payload)
        return _thread_state(thread_id, result)

    @app.post("/api/threads/{thread_id}/stream")  # type: ignore[untyped-decorator]
    def stream(thread_id: str, req: InvokeRequest) -> StreamingResponse:
        _thread_meta.setdefault(
            thread_id, {"created_at": datetime.now(timezone.utc).isoformat()}
        )

        def event_stream() -> Any:
            from makpa.supervisor.router import classify_intent

            started = time.monotonic()
            # 1. routing (structured LLM first, heuristic fallback — same as graph)
            try:
                decision = classify_intent([HumanMessage(content=req.message)])
                agents = [a for a in decision.agents if a in AGENT_NAMES]
                reasoning = decision.reasoning
            except Exception as e:
                yield _sse("error", {"message": str(e), "retryable": True})
                yield _sse("done", {})
                return
            yield _sse("routing", {"agents": agents, "reasoning": reasoning})
            now = datetime.now(timezone.utc).isoformat()
            for agent in agents:
                yield _sse("agent_start", {"agent": agent, "started_at": now})
            # 2. invoke (single supervisor call; token deltas chunk the final answer)
            try:
                result = _invoke_new_message(thread_id, req.message)
            except Exception as e:
                payload = {"agent": "supervisor", "message": str(e), "retryable": True}
                yield _sse("error", payload)
                yield _sse("done", {})
                return
            state = _thread_state(thread_id, result)
            elapsed = int((time.monotonic() - started) * 1000)
            for agent, output in state["agent_outputs"].items():
                answer = str(output.get("answer", ""))
                # Chunked deltas keep scroll stable; frontend appends in place.
                for i in range(0, len(answer), 400):
                    yield _sse("agent_token", {"agent": agent, "delta": answer[i : i + 400]})
                for tool in output.get("tools", []) or []:
                    info = {"agent": agent, "tool": tool.get("tool")}
                    info["status"] = tool.get("status", "ok")
                    yield _sse("agent_tool", info)
                end = {"agent": agent, "status": output.get("status", "error")}
                end["duration_ms"] = elapsed
                end["citations"] = output.get("citations", [])
                end["structured"] = output.get("structured", {})
                yield _sse("agent_end", end)
            pending = state.get("pending_interrupt")
            if pending is not None:
                yield _sse("interrupt", pending)
            else:
                agg = {"status": state.get("status", "error"), "duration_ms": elapsed}
                yield _sse("aggregate", agg)
            yield _sse("done", {})

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    @app.post("/api/ingest")  # type: ignore[untyped-decorator]
    def ingest(req: IngestRequest) -> dict[str, Any]:
        import os

        from makpa.config import get_settings
        from makpa.rag.ingestion import ingest_pdf

        settings = get_settings()
        pdf_path = (req.path or settings.sample_pdf_path or "./data/sample.pdf").strip()
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail=f"PDF not found: {pdf_path}")
        started = time.monotonic()
        try:
            result = ingest_pdf(pdf_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        return {
            "path": pdf_path,
            "chunks_created": result.chunks_created,
            "chunks_skipped": result.chunks_skipped,
            "backend": result.backend,
            "duration_ms": int((time.monotonic() - started) * 1000),
        }

    return app


app = create_app()


def main() -> None:
    """Run the adapter with uvicorn (dev default :8001 to avoid Chroma :8000)."""
    import uvicorn

    uvicorn.run("makpa.api.server:app", host="127.0.0.1", port=8001, reload=False)


if __name__ == "__main__":
    main()
