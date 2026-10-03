"""RAG sub-agent as a LangGraph StateGraph with ReAct-style loop."""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.documents import Document
from langgraph.graph import END, START, StateGraph

from makpa.rag.retriever import (
    NO_DOCS_MESSAGE,
    format_citations,
    grounded_answer,
    retrieve_documents,
    validate_answer,
)
from makpa.state import RAGState
from makpa.utils.tracing import entrypoint

logger = logging.getLogger(__name__)


def retrieval_node(state: RAGState) -> dict[str, Any]:
    """Retrieve chunks for the query."""
    query = state.get("query", "")
    if not query:
        return {
            "retrieved_chunks": [],
            "citations": [],
            "status": "error",
            "answer": "empty query",
        }
    try:
        results = retrieve_documents(query)
        docs = [doc for doc, _ in results]
        citations = format_citations(results)
        status = "ok" if docs else "empty"
        return {
            "retrieved_chunks": docs,
            "citations": citations,
            "status": status,
        }
    except Exception as e:
        logger.warning("Retrieval node failed: %s", e)
        return {
            "retrieved_chunks": [],
            "citations": [],
            "status": "error",
            "answer": f"retrieval error: {e}",
        }


def generation_node(state: RAGState) -> dict[str, Any]:
    """Generate a grounded answer from retrieved chunks."""
    query = state.get("query", "")
    docs: list[Document] = state.get("retrieved_chunks", [])
    if not docs:
        return {"answer": NO_DOCS_MESSAGE, "status": "empty"}
    try:
        answer = grounded_answer(query, docs)
        return {"answer": answer, "status": "ok"}
    except Exception as e:
        logger.warning("Generation node failed: %s", e)
        return {"answer": f"generation error: {e}", "status": "error"}


def validation_node(state: RAGState) -> dict[str, Any]:
    """Enforce the faithfulness guard."""
    answer = state.get("answer", "")
    docs: list[Document] = state.get("retrieved_chunks", [])
    try:
        validated = validate_answer(answer, docs)
        status = state.get("status", "ok")
        if not docs and NO_DOCS_MESSAGE in validated.lower():
            status = "empty"
        return {"answer": validated, "status": status}
    except Exception as e:
        logger.warning("Validation node failed: %s", e)
        return {"answer": f"validation error: {e}", "status": "error"}


def short_circuit_node(state: RAGState) -> dict[str, Any]:
    """Handle the zero-chunks path."""
    return {"answer": NO_DOCS_MESSAGE, "status": "empty", "citations": []}


def route_after_retrieval(state: RAGState) -> str:
    """Route to short-circuit when retrieval returns zero chunks."""
    docs = state.get("retrieved_chunks", [])
    status = state.get("status", "ok")
    if status == "error":
        return "validation"
    if not docs:
        return "short_circuit"
    return "generation"


def create_rag_graph() -> Any:
    """Create the RAG subgraph.

    The graph is invokable directly and can later be wrapped as a
    subgraph by the supervisor without modification.

    Returns:
        Compiled StateGraph.
    """
    builder = StateGraph(RAGState)
    builder.add_node("retrieval", retrieval_node)
    builder.add_node("generation", generation_node)
    builder.add_node("validation", validation_node)
    builder.add_node("short_circuit", short_circuit_node)

    builder.add_edge(START, "retrieval")
    builder.add_conditional_edges(
        "retrieval",
        route_after_retrieval,
        {
            "generation": "generation",
            "short_circuit": "short_circuit",
            "validation": "validation",
        },
    )
    builder.add_edge("generation", "validation")
    builder.add_edge("validation", END)
    builder.add_edge("short_circuit", END)
    return builder.compile()


@entrypoint("makpa.rag")  # type: ignore[untyped-decorator]
def run_rag(query: str) -> dict[str, Any]:
    """Convenience helper to run the RAG graph for one query."""
    graph = create_rag_graph()
    result = graph.invoke({"query": query})
    return dict(result)


__all__ = [
    "create_rag_graph",
    "run_rag",
    "retrieval_node",
    "generation_node",
    "validation_node",
    "short_circuit_node",
]
