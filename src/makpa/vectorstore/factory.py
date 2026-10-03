"""Vector store interface and factory for MAKPA.

Provides a unified interface for different vector store backends
(Pinecone, Chroma HTTP, Chroma Local, Qdrant) with a common interface.
"""

from __future__ import annotations

import importlib
import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from langchain_core.documents import Document

from makpa.config import get_settings

logger = logging.getLogger(__name__)


class VectorStore(ABC):
    """Abstract interface for vector store backends."""

    @abstractmethod
    def add_documents(
        self, documents: list[Document], ids: list[str] | None = None
    ) -> list[str]:
        """Add documents to the vector store.

        Args:
            documents: List of documents to add.
            ids: Optional list of IDs for the documents.

        Returns:
            List of document IDs.
        """
        pass

    @abstractmethod
    def similarity_search_with_mmr(
        self,
        query: str,
        k: int = 5,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        filter: dict[str, Any] | None = None,
    ) -> list[tuple[Document, float]]:
        """Search for similar documents using Maximum Marginal Relevance.

        Args:
            query: Search query string.
            k: Number of documents to return.
            fetch_k: Number of documents to fetch before MMR.
            lambda_mult: Diversity parameter (0 = max diversity, 1 = min diversity).
            filter: Optional metadata filter.

        Returns:
            List of (Document, score) tuples.
        """
        pass

    @abstractmethod
    def delete_collection(self) -> None:
        """Delete the entire collection/index."""
        pass

    @abstractmethod
    def collection_info(self) -> dict[str, Any]:
        """Get information about the collection.

        Returns:
            Dictionary with collection metadata (name, count, etc.)
        """
        pass


def _optional_import(module_suffix: str, class_name: str) -> Any:
    """Import a backend class, returning None when its deps are missing."""
    try:
        module = importlib.import_module(f".{module_suffix}", __package__)
        return getattr(module, class_name)
    except ImportError:
        logger.warning("%s backend unavailable (import failed)", class_name)
        return None


# Import implementations
if TYPE_CHECKING:
    from .chroma_http import ChromaHTTPVectorStore
    from .chroma_local import ChromaLocalVectorStore
    from .pinecone import PineconeVectorStore
    from .qdrant import QdrantVectorStore
else:
    PineconeVectorStore = _optional_import("pinecone", "PineconeVectorStore")
    ChromaHTTPVectorStore = _optional_import("chroma_http", "ChromaHTTPVectorStore")
    ChromaLocalVectorStore = _optional_import("chroma_local", "ChromaLocalVectorStore")
    QdrantVectorStore = _optional_import("qdrant", "QdrantVectorStore")


class VectorStoreFactory:
    """Factory for creating vector store instances."""

    _instance: VectorStoreFactory | None = None
    _cached_store: VectorStore | None = None
    _cached_type: str | None = None

    def __new__(cls) -> VectorStoreFactory:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_initialized"):
            self._settings = get_settings()
            self._initialized = True

    def _create_pinecone_store(self) -> VectorStore | None:
        """Create a Pinecone vector store."""
        if not self._settings.pinecone_api_key:
            return None
        if PineconeVectorStore is None:
            logger.warning("PineconeVectorStore not available (import failed)")
            return None

        try:
            store = PineconeVectorStore(
                api_key=self._settings.pinecone_api_key,
                index_name=self._settings.pinecone_index_name,
                environment=self._settings.pinecone_environment,
                cloud=self._settings.pinecone_cloud,
                region=self._settings.pinecone_region,
            )
            logger.info("Created Pinecone vector store: %s", self._settings.pinecone_index_name)
            return store
        except Exception as e:
            logger.warning("Failed to create Pinecone vector store: %s", e)
            return None

    def _create_chroma_http_store(self) -> VectorStore | None:
        """Create a Chroma HTTP vector store."""
        if ChromaHTTPVectorStore is None:
            logger.warning("ChromaHTTPVectorStore not available (import failed)")
            return None

        try:
            store = ChromaHTTPVectorStore(
                host=self._settings.chroma_host,
                port=self._settings.chroma_port,
            )
            logger.info(
                "Created Chroma HTTP vector store: %s:%s",
                self._settings.chroma_host,
                self._settings.chroma_port,
            )
            return store
        except Exception as e:
            logger.warning("Failed to create Chroma HTTP vector store: %s", e)
            return None

    def _create_chroma_local_store(self) -> VectorStore | None:
        """Create a local Chroma vector store."""
        if ChromaLocalVectorStore is None:
            logger.warning("ChromaLocalVectorStore not available (import failed)")
            return None

        try:
            store = ChromaLocalVectorStore()
            logger.info("Created Chroma local vector store")
            return store
        except Exception as e:
            logger.warning("Failed to create Chroma local vector store: %s", e)
            return None

    def _create_qdrant_store(self) -> VectorStore | None:
        """Create a Qdrant vector store."""
        if not self._settings.qdrant_url or not self._settings.qdrant_api_key:
            return None
        if QdrantVectorStore is None:
            logger.warning("QdrantVectorStore not available (import failed)")
            return None

        try:
            store = QdrantVectorStore(
                url=self._settings.qdrant_url,
                api_key=self._settings.qdrant_api_key,
                collection_name=self._settings.qdrant_collection_name,
            )
            logger.info("Created Qdrant vector store: %s", self._settings.qdrant_collection_name)
            return store
        except Exception as e:
            logger.warning("Failed to create Qdrant vector store: %s", e)
            return None

    def get_store(self, store_type: str | None = None) -> VectorStore:
        """Get a vector store instance, using cache if available.

        Args:
            store_type: Optional explicit store type override.

        Returns:
            A VectorStore instance.
        """
        target_type = store_type or self._settings.resolved_vector_store.value

        # Return cached store if type matches
        if self._cached_store is not None and self._cached_type == target_type:
            return self._cached_store

        store = None

        if target_type == "pinecone":
            store = self._create_pinecone_store()
        elif target_type == "chroma_http":
            store = self._create_chroma_http_store()
        elif target_type == "chroma_local":
            store = self._create_chroma_local_store()
        elif target_type == "qdrant":
            store = self._create_qdrant_store()

        # Fallback chain if requested store unavailable
        if store is None:
            logger.warning("Vector store %s unavailable, trying fallback chain", target_type)

            # Try Pinecone
            store = self._create_pinecone_store()
            if store is not None:
                logger.info("Falling back to Pinecone")
                return store

            # Try Chroma HTTP
            store = self._create_chroma_http_store()
            if store is not None:
                logger.info("Falling back to Chroma HTTP")
                return store

            # Try Chroma Local (always available in demo)
            store = self._create_chroma_local_store()
            if store is not None:
                logger.info("Falling back to Chroma Local")
                return store

            # Try Qdrant
            store = self._create_qdrant_store()
            if store is not None:
                logger.info("Falling back to Qdrant")
                return store

        if store is None:
            raise RuntimeError("No vector store backend available")

        self._cached_store = store
        self._cached_type = target_type
        return store

    def clear_cache(self) -> None:
        """Clear the cached store (useful for testing)."""
        self._cached_store = None
        self._cached_type = None


# Module-level singleton instance
_factory = VectorStoreFactory()


def create_vector_store(store_type: str | None = None) -> VectorStore:
    """Create a vector store instance.

    This is the primary accessor for the rest of the application.
    """
    return _factory.get_store(store_type)


def clear_vector_store_cache() -> None:
    """Clear the vector store factory cache."""
    _factory.clear_cache()


__all__ = [
    "VectorStore",
    "create_vector_store",
    "clear_vector_store_cache",
    "VectorStoreFactory",
    "PineconeVectorStore",
    "ChromaHTTPVectorStore",
    "ChromaLocalVectorStore",
    "QdrantVectorStore",
]
