"""Configuration module for MAKPA.

Provides Pydantic v2 settings management with mode detection,
LLM provider resolution, vector store resolution, and Google MCP mode resolution.
"""

from makpa.config.settings import (
    EmbeddingProvider,
    GitHubMCPMode,
    GoogleMCPMode,
    LLMProvider,
    Mode,
    Settings,
    VectorStoreType,
    get_settings,
    print_startup_banner,
)

__all__ = [
    "Settings",
    "Mode",
    "LLMProvider",
    "VectorStoreType",
    "GoogleMCPMode",
    "GitHubMCPMode",
    "EmbeddingProvider",
    "get_settings",
    "print_startup_banner",
]
