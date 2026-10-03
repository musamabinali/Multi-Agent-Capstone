"""Chroma Local vector store implementation for MAKPA."""

from __future__ import annotations

import logging
import os
from typing import Any

from langchain_chroma import Chroma
from langchain_core.documents import Document

from makpa.config import get_settings

from .factory import VectorStore

logger = logging.getLogger(__name__)


class ChromaLocalVectorStore(VectorStore):
    """Chroma Local (in-process) vector store implementation."""

    def __init__(
        self,
        persist_directory: str | None = None,
        collection_name: str = "makpa-rag",
    ) -> None:
        """Initialize Chroma Local vector store.

        Args:
            persist_directory: Directory to persist the database.
            collection_name: Name of the collection.
        """
        settings = get_settings()
        self._persist_directory = persist_directory or os.path.join(
            os.path.dirname(settings.sample_pdf_path), "chroma_db"
        )
        self._collection_name = collection_name
        self._vectorstore = None
        self._embeddings = None

        # Ensure persist directory exists
        os.makedirs(self._persist_directory, exist_ok=True)

    def _get_vectorstore(self) -> Chroma:
        """Get or create the LangChain Chroma vector store."""
        if self._vectorstore is None:
            from makpa.vectorstore import get_embeddings

            self._embeddings = get_embeddings()
            self._vectorstore = Chroma(
                collection_name=self._collection_name,
                embedding_function=self._embeddings,
                persist_directory=self._persist_directory,
            )
        return self._vectorstore

    def add_documents(
        self, documents: list[Document], ids: list[str] | None = None
    ) -> list[str]:
        """Add documents to Chroma Local."""
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
        """Search with MMR using Chroma Local."""
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
            logger.info("Deleted Chroma local collection: %s", self._collection_name)
            self._vectorstore = None
        except Exception as e:
            logger.warning("Failed to delete Chroma local collection: %s", e)
            raise

    def collection_info(self) -> dict[str, Any]:
        """Get Chroma local collection info."""
        try:
            vectorstore = self._get_vectorstore()
            count = vectorstore._collection.count()
            return {
                "type": "chroma_local",
                "collection_name": self._collection_name,
                "persist_directory": self._persist_directory,
                "total_vectors": count,
            }
        except Exception as e:
            logger.warning("Failed to get Chroma local collection info: %s", e)
            return {
                "type": "chroma_local",
                "collection_name": self._collection_name,
                "persist_directory": self._persist_directory,
                "error": str(e),
            }
