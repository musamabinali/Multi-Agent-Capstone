"""GitHub MCP server package for MAKPA (mock STDIO implementation)."""

from .fixtures import MOCK_REPO
from .server import GitHubMockMCPServer, main

__all__ = ["GitHubMockMCPServer", "MOCK_REPO", "main"]
