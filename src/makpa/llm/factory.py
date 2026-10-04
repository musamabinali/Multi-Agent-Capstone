"""LLM provider factory for MAKPA.

Provides a unified interface for creating chat models from different providers
(Gemini, Groq, Mock) based on configuration with fallback chain support.
"""

from __future__ import annotations

import logging

from langchain_core.language_models.chat_models import BaseChatModel

from makpa.config import get_settings
from makpa.utils.mock import create_mock_model

logger = logging.getLogger(__name__)


class LLMFactory:
    """Factory for creating LLM instances with fallback support."""

    _instance: LLMFactory | None = None
    _cached_model: BaseChatModel | None = None
    _cached_provider: str | None = None

    def __new__(cls) -> LLMFactory:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_initialized"):
            self._settings = get_settings()
            self._fallback_resolved = False
            self._initialized = True

    def _create_gemini_model(self) -> BaseChatModel | None:
        """Create a Gemini chat model if API key is available."""
        if not self._settings.gemini_api_key:
            return None

        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            model = ChatGoogleGenerativeAI(
                model=self._settings.gemini_chat_model,
                google_api_key=self._settings.gemini_api_key,
                temperature=self._settings.llm_temperature,
                max_output_tokens=self._settings.llm_max_tokens,
            )
            logger.debug("Created Gemini model: %s", self._settings.gemini_chat_model)
            return model
        except Exception as e:
            logger.debug("Failed to create Gemini model: %s", e)
            return None

    def _create_groq_model(self) -> BaseChatModel | None:
        """Create a Groq chat model if API key is available."""
        if not self._settings.groq_api_key:
            return None

        try:
            from langchain_groq import ChatGroq

            model = ChatGroq(
                model=self._settings.groq_chat_model,
                groq_api_key=self._settings.groq_api_key,
                temperature=self._settings.llm_temperature,
                max_tokens=self._settings.llm_max_tokens,
            )
            logger.debug("Created Groq model: %s", self._settings.groq_chat_model)
            return model
        except Exception as e:
            logger.debug("Failed to create Groq model: %s", e)
            return None

    def _create_mock_model(self) -> BaseChatModel:
        """Create a mock chat model for demo mode."""
        logger.debug("Created Mock model (demo mode)")
        return create_mock_model()

    def get_model(self, provider: str | None = None) -> BaseChatModel:
        """Get a chat model instance, using cache if available.

        Args:
            provider: Optional explicit provider override. If not provided,
                     uses the resolved provider from settings.

        Returns:
            A BaseChatModel instance.
        """
        target_provider = provider or self._settings.resolved_llm_provider.value

        # Return cached model if provider matches
        if self._cached_model is not None and self._cached_provider == target_provider:
            return self._cached_model

        model = None

        if target_provider == "gemini":
            model = self._create_gemini_model()
            if model is None:
                # First fallback notice is user-facing; repeats stay at debug.
                logger.debug("Gemini unavailable, trying Groq")
                model = self._create_groq_model()
            if model is None:
                logger.debug("Groq unavailable, falling back to Mock")
                model = self._create_mock_model()

        elif target_provider == "groq":
            model = self._create_groq_model()
            if model is None:
                logger.debug("Groq unavailable, falling back to Mock")
                model = self._create_mock_model()

        else:  # mock or any other
            model = self._create_mock_model()

        self._cached_model = model
        self._cached_provider = target_provider
        return model

    def get_model_with_fallback(self) -> BaseChatModel:
        """Get a model with automatic fallback chain: Gemini -> Groq -> Mock.

        This is the primary accessor that implements the full fallback logic.
        The resolved provider is cached per session so the test invoke (and
        any 403 fallback warning) runs once, not on every LLM call.
        """
        # Fast path: a resolved fallback model is already warm for this session.
        if self._cached_model is not None and self._cached_provider in (
            "gemini",
            "groq",
            "mock",
        ):
            if getattr(self, "_fallback_resolved", False):
                return self._cached_model
        # Priority order: Gemini > Groq > Mock
        for provider in ["gemini", "groq", "mock"]:
            model = self.get_model(provider)
            if model is not None:
                # Verify the model works by doing a test invoke
                try:
                    test_response = model.invoke("test")
                    if test_response and test_response.content:
                        logger.debug("LLM provider resolved: %s", provider)
                        self._fallback_resolved = True
                        return model
                except Exception as e:
                    logger.debug("Provider %s failed test invoke: %s", provider, e)
                    # Clear cache to force retry with next provider
                    self._cached_model = None
                    self._cached_provider = None
                    continue

        # Should never reach here since mock always works
        self._fallback_resolved = True
        return self._create_mock_model()

    def clear_cache(self) -> None:
        """Clear the cached model (useful for testing)."""
        self._cached_model = None
        self._cached_provider = None
        self._fallback_resolved = False


# Module-level singleton instance
_factory = LLMFactory()


def get_llm() -> BaseChatModel:
    """Get the default LLM instance with full fallback chain.

    This is the primary accessor for the rest of the application.
    """
    return _factory.get_model_with_fallback()


def get_llm_for_provider(provider: str) -> BaseChatModel:
    """Get an LLM instance for a specific provider (no fallback)."""
    return _factory.get_model(provider)


def clear_llm_cache() -> None:
    """Clear the LLM factory cache."""
    _factory.clear_cache()


__all__ = [
    "get_llm",
    "get_llm_for_provider",
    "clear_llm_cache",
    "LLMFactory",
]
