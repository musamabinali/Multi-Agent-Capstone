"""Mock chat model for zero-key demo mode.

Returns realistic canned responses keyed by intent so that every Phase 1 demo
path works with zero keys.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import RunnableConfig


class MockChatModel:
    """Mock chat model that returns canned responses based on prompt content."""

    def __init__(self) -> None:
        self._call_count = 0

    def _get_response(self, prompt: str) -> str:
        """Generate a canned response based on prompt content."""
        prompt_lower = prompt.lower()
        self._call_count += 1

        # Empty-context marker used by the grounded prompt builder
        if "no context was retrieved" in prompt_lower:
            return "No relevant documents found."
        # Grounded prompts contain [chunk ...] context blocks
        if "[chunk" in prompt_lower:
            return (
                "Based on the retrieved context, the document covers important topics "
                "including implementation details and best practices. "
                "[source: sample.pdf, page: 1, chunk_id: 0]"
            )
        # RAG query about PDF content
        rag_keywords = ["rag", "retrieve", "search", "context", "document", "pdf"]
        if any(keyword in prompt_lower for keyword in rag_keywords):
            if "citation" in prompt_lower:
                return (
                    "Based on the provided context, the document discusses key concepts. "
                    "[source: sample.pdf, page: 1, chunk_id: 0]"
                )
            return (
                "Based on the retrieved context, the document covers important topics "
                "including implementation details and best practices. "
                "[source: sample.pdf, page: 1, chunk_id: 0]"
            )

        # General question answering
        if "?" in prompt:
            return "This is a mock response. In demo mode, no real LLM is available."

        # Fallback
        return "Mock response generated for demo mode."

    def invoke(
        self,
        input: str | list[BaseMessage],
        config: RunnableConfig | None = None,
        **kwargs: Any,
    ) -> AIMessage:
        """Invoke the mock model."""
        if isinstance(input, list):
            prompt = " ".join(msg.content for msg in input if hasattr(msg, "content"))
        else:
            prompt = input

        response_text = self._get_response(prompt)
        return AIMessage(content=response_text)

    async def ainvoke(
        self,
        input: str | list[BaseMessage],
        config: RunnableConfig | None = None,
        **kwargs: Any,
    ) -> AIMessage:
        """Async invoke (delegates to sync)."""
        return self.invoke(input, config, **kwargs)

    def stream(
        self,
        input: str | list[BaseMessage],
        config: RunnableConfig | None = None,
        **kwargs: Any,
    ) -> Iterator[AIMessage]:
        """Stream the mock response."""
        if isinstance(input, list):
            prompt = " ".join(msg.content for msg in input if hasattr(msg, "content"))
        else:
            prompt = input

        response_text = self._get_response(prompt)
        # Simulate streaming by yielding chunks
        words = response_text.split()
        for i, word in enumerate(words):
            if i == 0:
                yield AIMessage(content=word)
            else:
                yield AIMessage(content=" " + word)

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a chat result (for compatibility)."""
        prompt = " ".join(msg.content for msg in messages if hasattr(msg, "content"))
        response_text = self._get_response(prompt)
        message = AIMessage(content=response_text)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        return "mock"


def create_mock_model() -> MockChatModel:
    """Create a mock chat model instance."""
    return MockChatModel()
