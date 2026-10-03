"""Pinecone vector store implementation for MAKPA."""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore as LangChainPineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from .factory import VectorStore

logger = logging.getLogger(__name__)


class PineconeVectorStore(VectorStore):
    """Pinecone vector store implementation using serverless indexes."""

    def __init__(
        self,
        api_key: str,
        index_name: str,
        environment: str = "us-east-1",
        cloud: str = "aws",
        region: str = "us-east-1",
    ) -> None:
        """Initialize Pinecone vector store.

        Args:
            api_key: Pinecone API key.
            index_name: Name of the index.
            environment: Pinecone environment (deprecated, kept for compat).
            cloud: Cloud provider (aws, gcp, azure).
            region: Cloud region.
        """
        self._api_key = api_key
        self._index_name = index_name
        self._cloud = cloud
        self._region = region
        self._pc = Pinecone(api_key=api_key)
        self._embeddings = None
        self._vectorstore = None
        self._ensure_index_exists()

    def _ensure_index_exists(self) -> None:
        """Create the index if it doesn't exist."""
        existing_indexes = [idx.name for idx in self._pc.list_indexes()]

        if self._index_name not in existing_indexes:
            logger.info("Creating Pinecone index: %s", self._index_name)
            # Default dimension for MiniLM
            dimension = 384

            self._pc.create_index(
                name=self._index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud=self._cloud, region=self._region),
            )
            logger.info("Pinecone index created: %s", self._index_name)
        else:
            logger.info("Pinecone index already exists: %s", self._index_name)

    def _get_vectorstore(self) -> LangChainPineconeVectorStore:
        """Get or create the LangChain PineconeVectorStore."""
        if self._vectorstore is None:
            from makpa.vectorstore import get_embeddings

            self._embeddings = get_embeddings()
            self._vectorstore = LangChainPineconeVectorStore(
                index_name=self._index_name,
                embedding=self._embeddings,
                pinecone_api_key=self._api_key,
            )
        return self._vectorstore

    def add_documents(
        self, documents: list[Document], ids: list[str] | None = None
    ) -> list[str]:
        """Add documents to Pinecone."""
        vectorstore = self._get_vectorstore()
        return vectorstore.add_documents(documents, ids=ids)  # type: ignore

    def similarity_search_with_mmr(
        self,
        query: str,
        k: int = 5,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        filter: dict[str, Any] | None = None,
    ) -> list[tuple[Document, float]]:
        """Search with MMR using Pinecone."""
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
        """Delete the Pinecone index."""
        try:
            self._pc.delete_index(self._index_name)
            logger.info("Deleted Pinecone index: %s", self._index_name)
            self._vectorstore = None
        except Exception as e:
            logger.warning("Failed to delete Pinecone index: %s", e)
            raise

    def collection_info(self) -> dict[str, Any]:
        """Get Pinecone index info."""
        try:
            index = self._pc.Index(self._index_name)
            stats = index.describe_index_stats()
            return {
                "type": "pinecone",
                "index_name": self._index_name,
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "cloud": self._cloud,
                "region": self._region,
            }
        except Exception as e:
            logger.warning("Failed to get Pinecone index info: %s", e)
            return {"type": "pinecone", "index_name": self._index_name, "error": str(e)}
