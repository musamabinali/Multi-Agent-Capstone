"""Qdrant vector store implementation for MAKPA."""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore as LangChainQdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from .factory import VectorStore

logger = logging.getLogger(__name__)


class QdrantVectorStore(VectorStore):
    """Qdrant Cloud vector store implementation."""

    def __init__(
        self,
        url: str,
        api_key: str,
        collection_name: str = "makpa-rag",
    ) -> None:
        """Initialize Qdrant vector store.

        Args:
            url: Qdrant server URL.
            api_key: Qdrant API key.
            collection_name: Name of the collection.
        """
        self._url = url
        self._api_key = api_key
        self._collection_name = collection_name
        self._client = QdrantClient(url=url, api_key=api_key)
        self._vectorstore = None
        self._embeddings = None
        self._ensure_collection_exists()

    def _ensure_collection_exists(self) -> None:
        """Create the collection if it doesn't exist."""
        try:
            collections = self._client.get_collections().collections
            existing_names = [c.name for c in collections]

            if self._collection_name not in existing_names:
                # Default dimension for MiniLM
                dimension = 384

                logger.info("Creating Qdrant collection: %s", self._collection_name)
                self._client.create_collection(
                    collection_name=self._collection_name,
                    vectors_config=VectorParams(
                        size=dimension,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info("Qdrant collection created: %s", self._collection_name)
            else:
                logger.info("Qdrant collection already exists: %s", self._collection_name)
        except Exception as e:
            logger.warning("Failed to ensure Qdrant collection: %s", e)
            raise

    def _get_vectorstore(self) -> LangChainQdrantVectorStore:
        """Get or create the LangChain QdrantVectorStore."""
        if self._vectorstore is None:
            from makpa.vectorstore import get_embeddings

            self._embeddings = get_embeddings()
            self._vectorstore = LangChainQdrantVectorStore(
                client=self._client,
                collection_name=self._collection_name,
                embedding=self._embeddings,
            )
        return self._vectorstore

    def add_documents(
        self, documents: list[Document], ids: list[str] | None = None
    ) -> list[str]:
        """Add documents to Qdrant."""
        vectorstore = self._get_vectorstore()
        return vectorstore.add_documents(documents, ids=ids)  # type: ignore[no-any-return]

    def similarity_search_with_mmr(
        self,
        query: str,
        k: int = 5,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        filter: dict[str, Any] | None = None,
    ) -> list[tuple[Document, float]]:
        """Search with MMR using Qdrant."""
        vectorstore = self._get_vectorstore()
        docs = vectorstore.max_marginal_relevance_search(
            query=query,
            k=k,
            fetch_k=fetch_k,
            lambda_mult=lambda_mult,
            filter=filter,
        )
        try:
            scored = vectorstore.similarity_search_with_score(
                query=query, k=fetch_k, filter=filter,
            )
            scores = {d.page_content: s for d, s in scored}
        except Exception:
            scores = {}
        return [(d, float(scores.get(d.page_content, 0.0))) for d in docs]

    def delete_collection(self) -> None:
        """Delete the Qdrant collection."""
        try:
            self._client.delete_collection(self._collection_name)
            logger.info("Deleted Qdrant collection: %s", self._collection_name)
            self._vectorstore = None
        except Exception as e:
            logger.warning("Failed to delete Qdrant collection: %s", e)
            raise

    def collection_info(self) -> dict[str, Any]:
        """Get Qdrant collection info."""
        try:
            info = self._client.get_collection(self._collection_name)
            return {
                "type": "qdrant",
                "collection_name": self._collection_name,
                "url": self._url,
                "total_vectors": info.points_count,
                "dimension": info.config.params.vectors.size,
            }
        except Exception as e:
            logger.warning("Failed to get Qdrant collection info: %s", e)
            return {
                "type": "qdrant",
                "collection_name": self._collection_name,
                "url": self._url,
                "error": str(e),
            }
