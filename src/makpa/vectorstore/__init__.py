"""Vector store factory for MAKPA.

Provides a unified interface for different vector store backends
(Pinecone, Chroma HTTP, Chroma Local, Qdrant) with a common interface.
"""

from .embeddings import (
    EmbeddingFactory,
    clear_embeddings_cache,
    get_embeddings,
    get_embeddings_for_provider,
)
from .factory import (
    VectorStore,
    VectorStoreFactory,
    clear_vector_store_cache,
    create_vector_store,
)

__all__ = [
    "VectorStore",
    "VectorStoreFactory",
    "create_vector_store",
    "clear_vector_store_cache",
    "PineconeVectorStore",
    "ChromaHTTPVectorStore",
    "ChromaLocalVectorStore",
    "QdrantVectorStore",
    "get_embeddings",
    "get_embeddings_for_provider",
    "clear_embeddings_cache",
    "EmbeddingFactory",
]
