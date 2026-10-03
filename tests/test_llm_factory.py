"""Unit tests for the LLM provider factory (all three branches)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessage

from makpa.llm import clear_llm_cache, get_llm, get_llm_for_provider


def _reset():
    clear_llm_cache()


def test_mock_branch():
    _reset()
    model = get_llm_for_provider("mock")
    assert model is not None
    resp = model.invoke("What is RAG?")
    assert isinstance(resp, AIMessage)
    assert resp.content


def test_gemini_branch_with_mock():
    _reset()
    fake = MagicMock()
    fake.invoke.return_value = AIMessage(content="gemini answer")
    with patch("makpa.llm.factory.LLMFactory._create_gemini_model", return_value=fake):
        model = get_llm_for_provider("gemini")
        assert model is fake


def test_groq_branch_with_mock():
    _reset()
    fake = MagicMock()
    fake.invoke.return_value = AIMessage(content="groq answer")
    with patch("makpa.llm.factory.LLMFactory._create_groq_model", return_value=fake):
        model = get_llm_for_provider("groq")
        assert model is fake


def test_fallback_chain_returns_working_model():
    _reset()
    model = get_llm()
    assert model is not None
    resp = model.invoke("test")
    assert resp.content


def test_mock_canned_rag_response():
    _reset()
    model = get_llm_for_provider("mock")
    resp = model.invoke("search the PDF context about agents")
    assert "sample.pdf" in resp.content or "context" in resp.content.lower()


def test_mock_citation_response():
    _reset()
    model = get_llm_for_provider("mock")
    resp = model.invoke("give me citations from context")
    assert "[" in resp.content and "]" in resp.content


def test_mock_empty_response():
    _reset()
    model = get_llm_for_provider("mock")
    resp = model.invoke("No context was retrieved. Question: xyz?")
    assert "no relevant documents found" in resp.content.lower()
