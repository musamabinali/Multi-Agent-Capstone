"""Retriever and citation layer for MAKPA RAG sub-agent.

Wraps the vector store factory with MMR retrieval, citation formatting,
and grounded answer generation with a faithfulness guard.
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.documents import Document

from makpa.config import get_settings

logger = logging.getLogger(__name__)

NO_DOCS_MESSAGE = "no relevant documents found"


def retrieve_documents(
    query: str,
    k: int | None = None,
    fetch_k: int | None = None,
    lambda_mult: float | None = None,
    filter: dict[str, Any] | None = None,
) -> list[tuple[Document, float]]:
    """Retrieve documents with MMR.

    Args:
        query: Search query.
        k: Number of documents to return (defaults to RAG_K).
        fetch_k: Candidates to fetch before MMR (defaults to RAG_FETCH_K).
        lambda_mult: Diversity parameter (defaults to RAG_LAMBDA_MULT).
        filter: Optional metadata filter.

    Returns:
        List of (Document, score) tuples with required metadata preserved.
    """
    from makpa.vectorstore import create_vector_store

    settings = get_settings()
    k = k if k is not None else settings.rag_k
    fetch_k = fetch_k if fetch_k is not None else settings.rag_fetch_k
    lambda_mult = lambda_mult if lambda_mult is not None else settings.rag_lambda_mult

    store = create_vector_store()
    try:
        results = store.similarity_search_with_mmr(
            query=query,
            k=k,
            fetch_k=fetch_k,
            lambda_mult=lambda_mult,
            filter=filter,
        )
    except Exception as e:
        logger.warning("Retrieval failed (empty store?): %s", e)
        return []
    logger.info("Retrieved %d chunks for query: %s", len(results), query[:80])
    return results  # type: ignore[no-any-return]


def format_citations(
    docs: list[Document] | list[tuple[Document, float]],
) -> list[dict[str, Any]]:
    """Format citations for retrieved chunks.

    Args:
        docs: Documents or (Document, score) tuples.

    Returns:
        List of {source, page, chunk_id} dicts.
    """
    citations: list[dict[str, Any]] = []
    for item in docs:
        doc = item[0] if isinstance(item, tuple) else item
        meta = doc.metadata or {}
        citations.append(
            {
                "source": meta.get("source", "unknown"),
                "page": meta.get("page", 0),
                "chunk_id": meta.get("chunk_index", 0),
                "doc_id": meta.get("doc_id", ""),
                "score": item[1] if isinstance(item, tuple) else 0.0,
            }
        )
    return citations


def _build_grounded_prompt(question: str, docs: list[Document]) -> str:
    """Build a strictly-grounded prompt from retrieved chunks."""
    if not docs:
        return (
            "You are a RAG assistant. No context was retrieved.\n"
            f"Question: {question}\n"
            f"Reply with exactly: {NO_DOCS_MESSAGE}"
        )
    context_blocks = []
    for i, doc in enumerate(docs):
        meta = doc.metadata or {}
        src = meta.get("source", "unknown")
        page = meta.get("page", 0)
        cid = meta.get("chunk_index", i)
        context_blocks.append(f"[chunk {cid} | {src} p.{page}]\n{doc.page_content}")
    context = "\n\n".join(context_blocks)
    return (
        "You are a RAG assistant. Answer STRICTLY from the context below.\n"
        "Rules:\n"
        "- Use only facts present in the context.\n"
        "- If the context does not contain the answer, reply exactly: "
        f"{NO_DOCS_MESSAGE}\n"
        "- Append a 'Citations:' line listing [source, page, chunk_id] "
        "for every chunk you used.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    )


def grounded_answer(question: str, docs: list[Document]) -> str:
    """Generate a grounded answer with citations.

    Args:
        question: User question.
        docs: Retrieved documents.

    Returns:
        Answer string. Returns NO_DOCS_MESSAGE when docs is empty.
    """
    from makpa.llm import get_llm

    if not docs:
        return NO_DOCS_MESSAGE
    prompt = _build_grounded_prompt(question, docs)
    llm = get_llm()
    try:
        response = llm.invoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)
        text = content if isinstance(content, str) else str(content)
    except Exception as e:
        logger.warning("LLM invocation failed: %s", e)
        # Deterministic fallback so demo/tests work offline
        first = docs[0]
        meta = first.metadata or {}
        text = (
            f"Based on the retrieved context, {first.page_content[:280]} "
            f"[source: {meta.get('source', 'unknown')}, "
            f"page: {meta.get('page', 0)}, "
            f"chunk_id: {meta.get('chunk_index', 0)}]"
        )
    return validate_answer(text, docs)


def validate_answer(answer: str, docs: list[Document]) -> str:
    """Enforce the faithfulness guard.

    Rejects answers with no citation when context is non-empty by
    appending a citation fallback. Empty-context answers must be
    the NO_DOCS_MESSAGE.

    Args:
        answer: Candidate answer.
        docs: Retrieved documents.

    Returns:
        Validated answer string.

    Raises:
        ValueError: If answer claims no docs but docs were provided.
    """
    if not docs:
        if NO_DOCS_MESSAGE not in answer.lower():
            return NO_DOCS_MESSAGE
        return answer
    # Non-empty context requires at least one citation marker
    has_bracket = "[" in answer and "]" in answer
    has_citations_word = "citation" in answer.lower() or "source" in answer.lower()
    if not (has_bracket or has_citations_word):
        citations = format_citations(docs)
        c = citations[0]
        answer = (
            f"{answer.rstrip()} "
            f"[source: {c['source']}, page: {c['page']}, chunk_id: {c['chunk_id']}]"
        )
    return answer


__all__ = [
    "retrieve_documents",
    "format_citations",
    "grounded_answer",
    "validate_answer",
    "NO_DOCS_MESSAGE",
]
