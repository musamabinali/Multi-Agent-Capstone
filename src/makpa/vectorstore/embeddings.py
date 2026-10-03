"""Embedding provider factory for MAKPA.

Provides a unified interface for creating embedding models from different providers
(HuggingFace, Gemini) based on configuration.
"""

from __future__ import annotations

import logging

from langchain_core.embeddings import Embeddings

from makpa.config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingFactory:
    """Factory for creating embedding model instances."""

    _instance: EmbeddingFactory | None = None
    _cached_model: Embeddings | None = None
    _cached_provider: str | None = None

    def __new__(cls) -> EmbeddingFactory:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_initialized"):
            self._settings = get_settings()
            self._initialized = True

    def _create_huggingface_embeddings(self) -> Embeddings:
        """Create HuggingFace embeddings model."""
        try:
            from langchain_huggingface import HuggingFaceEmbeddings

            model = HuggingFaceEmbeddings(
                model_name=self._settings.hf_embedding_model,
                model_kwargs={"device": "cpu"},
                encode_kwargs={
                    "batch_size": self._settings.embedding_batch_size,
                    "normalize_embeddings": True,
                },
            )
            logger.info(
                "Created HuggingFace embeddings: %s", self._settings.hf_embedding_model
            )
            return model
        except Exception as e:
            logger.warning("Failed to create HuggingFace embeddings: %s", e)
            raise

    def _create_gemini_embeddings(self) -> Embeddings | None:
        """Create Gemini embeddings model if API key is available."""
        if not self._settings.gemini_api_key:
            return None

        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings

            model = GoogleGenerativeAIEmbeddings(
                model=self._settings.gemini_embedding_model,
                google_api_key=self._settings.gemini_api_key,
            )
            logger.info(
                "Created Gemini embeddings: %s", self._settings.gemini_embedding_model
            )
            return model
        except Exception as e:
            logger.warning("Failed to create Gemini embeddings: %s", e)
            return None

    def get_embeddings(self, provider: str | None = None) -> Embeddings:
        """Get an embeddings instance, using cache if available.

        Args:
            provider: Optional explicit provider override. If not provided,
                     uses the provider from settings.

        Returns:
            An Embeddings instance.
        """
        target_provider = provider or self._settings.embedding_provider.value

        # Return cached model if provider matches
        if self._cached_model is not None and self._cached_provider == target_provider:
            return self._cached_model

        model = None

        if target_provider == "gemini":
            model = self._create_gemini_embeddings()
            if model is None:
                logger.warning("Gemini embeddings unavailable, falling back to HuggingFace")
                model = self._create_huggingface_embeddings()
        else:  # huggingface or any other
            model = self._create_huggingface_embeddings()

        self._cached_model = model
        self._cached_provider = target_provider
        return model

    def get_embeddings_with_fallback(self) -> Embeddings:
        """Get embeddings with automatic fallback: Gemini -> HuggingFace."""
        # Priority: Gemini (if configured) > HuggingFace
        if self._settings.embedding_provider.value == "gemini":
            model = self._create_gemini_embeddings()
            if model is not None:
                logger.info("Embedding provider resolved: gemini")
                return model
            logger.warning("Gemini embeddings failed, falling back to HuggingFace")

        model = self._create_huggingface_embeddings()
        logger.info("Embedding provider resolved: huggingface")
        return model

    def clear_cache(self) -> None:
        """Clear the cached model (useful for testing)."""
        self._cached_model = None
        self._cached_provider = None


# Module-level singleton instance
_factory = EmbeddingFactory()


def get_embeddings() -> Embeddings:
    """Get the default embeddings instance with fallback.

    This is the primary accessor for the rest of the application.
    """
    return _factory.get_embeddings_with_fallback()


def get_embeddings_for_provider(provider: str) -> Embeddings:
    """Get an embeddings instance for a specific provider (no fallback)."""
    return _factory.get_embeddings(provider)


def clear_embeddings_cache() -> None:
    """Clear the embeddings factory cache."""
    _factory.clear_cache()


__all__ = [
    "get_embeddings",
    "get_embeddings_for_provider",
    "clear_embeddings_cache",
    "EmbeddingFactory",
]
