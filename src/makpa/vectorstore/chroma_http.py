"""Chroma HTTP vector store implementation for MAKPA."""

from __future__ import annotations

import logging
from typing import Any

from langchain_chroma import Chroma
from langchain_core.documents import Document

from .factory import VectorStore

logger = logging.getLogger(__name__)


class ChromaHTTPVectorStore(VectorStore):
    """Chroma HTTP vector store implementation."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8000,
        collection_name: str = "makpa-rag",
    ) -> None:
        """Initialize Chroma HTTP vector store.

        Args:
            host: Chroma server host.
            port: Chroma server port.
            collection_name: Name of the collection.
        """
        self._host = host
        self._port = port
        self._collection_name = collection_name
        self._vectorstore = None
        self._embeddings = None

    def _get_vectorstore(self) -> Chroma:
        """Get or create the LangChain Chroma vector store."""
        if self._vectorstore is None:
            from makpa.vectorstore import get_embeddings

            self._embeddings = get_embeddings()
            self._vectorstore = Chroma(
                collection_name=self._collection_name,
                embedding_function=self._embeddings,
                client_settings={
                    "chroma_client_type": "http",
                    "chroma_server_host": self._host,
                    "chroma_server_port": self._port,
                },
            )
        return self._vectorstore

    def add_documents(
        self, documents: list[Document], ids: list[str] | None = None
    ) -> list[str]:
        """Add documents to Chroma HTTP."""
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
        """Search with MMR using Chroma HTTP."""
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
        """Delete the Chroma collection."""
        try:
            vectorstore = self._get_vectorstore()
            vectorstore.delete_collection()
            logger.info("Deleted Chroma collection: %s", self._collection_name)
            self._vectorstore = None
        except Exception as e:
            logger.warning("Failed to delete Chroma collection: %s", e)
            raise

    def collection_info(self) -> dict[str, Any]:
        """Get Chroma collection info."""
        try:
            vectorstore = self._get_vectorstore()
            count = vectorstore._collection.count()
            return {
                "type": "chroma_http",
                "collection_name": self._collection_name,
                "host": self._host,
                "port": self._port,
                "total_vectors": count,
            }
        except Exception as e:
            logger.warning("Failed to get Chroma collection info: %s", e)
            return {
                "type": "chroma_http",
                "collection_name": self._collection_name,
                "host": self._host,
                "port": self._port,
                "error": str(e),
            }
