"""Shared fixtures for the mock GitHub MCP server and contract tests.

The fixtures describe a small fake repository (``octo-demo/hello-world``)
so the full GitHub flow runs with zero keys in demo mode.
"""

from __future__ import annotations

from typing import Any

MOCK_OWNER = "octo-demo"
MOCK_REPO_NAME = "hello-world"
MOCK_REPO = f"{MOCK_OWNER}/{MOCK_REPO_NAME}"

FIXTURE_REPOS: list[dict[str, Any]] = [
    {
        "full_name": MOCK_REPO,
        "description": "Demo repository for MAKPA zero-key GitHub flow",
        "private": False,
        "stars": 42,
        "default_branch": "main",
    },
    {
        "full_name": f"{MOCK_OWNER}/docs",
        "description": "Documentation repository",
        "private": False,
        "stars": 7,
        "default_branch": "main",
    },
]

FIXTURE_PRS: list[dict[str, Any]] = [
    {
        "number": 7,
        "title": "Add RAG subgraph",
        "state": "open",
        "author": "octo-demo",
        "files": ["src/makpa/rag/graph.py"],
        "comments": 3,
    },
    {
        "number": 6,
        "title": "Fix MMR score join",
        "state": "closed",
        "author": "octo-demo",
        "files": ["src/makpa/rag/retriever.py"],
        "comments": 5,
    },
]

FIXTURE_ISSUES: list[dict[str, Any]] = [
    {
        "number": 12,
        "title": "Coverage below gate on vectorstore factory",
        "state": "open",
        "labels": ["testing"],
    },
    {
        "number": 11,
        "title": "Sample PDF has only one chunk",
        "state": "closed",
        "labels": ["rag", "data"],
    },
]

FIXTURE_COMMITS: list[dict[str, Any]] = [
    {"sha": "a1b2c3d", "message": "Implement GitHub subgraph", "author": "octo-demo"},
    {"sha": "e4f5g6h", "message": "Add confirmation gate", "author": "octo-demo"},
]

FIXTURE_FILES: dict[str, str] = {
    "README.md": "# hello-world\n\nDemo repository for MAKPA.\n",
    "src/main.py": "def main() -> None:\n    print('hello-world')\n",
}

FIXTURE_CODE_SEARCH: list[dict[str, Any]] = [
    {"path": "src/main.py", "repo": MOCK_REPO, "snippet": "def main() -> None:"},
    {"path": "src/makpa/rag/graph.py", "repo": MOCK_REPO, "snippet": "def create_rag_graph():"},
]

__all__ = [
    "FIXTURE_CODE_SEARCH",
    "FIXTURE_COMMITS",
    "FIXTURE_FILES",
    "FIXTURE_ISSUES",
    "FIXTURE_PRS",
    "FIXTURE_REPOS",
    "MOCK_OWNER",
    "MOCK_REPO",
    "MOCK_REPO_NAME",
]
