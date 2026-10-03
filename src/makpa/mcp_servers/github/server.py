"""Mock GitHub MCP server for MAKPA.

Speaks MCP over STDIO and exposes the same eight tools as the real
GitHub MCP server, backed by in-repo fixtures. Used automatically when
``GITHUB_MCP_MODE=mock`` or when no PAT is configured in demo mode.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .fixtures import (
    FIXTURE_CODE_SEARCH,
    FIXTURE_COMMITS,
    FIXTURE_FILES,
    FIXTURE_ISSUES,
    FIXTURE_PRS,
    FIXTURE_REPOS,
    MOCK_REPO,
)

logger = logging.getLogger(__name__)


def _tool(name: str, description: str, properties: dict[str, Any], required: list[str]) -> Tool:
    return Tool(
        name=name,
        description=description,
        inputSchema={
            "type": "object",
            "properties": properties,
            "required": required,
        },
    )


TOOL_DEFS: list[Tool] = [
    _tool(
        "list_repos",
        "List repositories for a user or org",
        {"owner": {"type": "string"}, "limit": {"type": "integer", "default": 10}},
        ["owner"],
    ),
    _tool(
        "list_prs",
        "List pull requests by state",
        {
            "repo": {"type": "string"},
            "state": {"type": "string", "default": "open"},
            "limit": {"type": "integer", "default": 10},
        },
        ["repo"],
    ),
    _tool(
        "get_pr",
        "Get pull request details, files, and comments",
        {"repo": {"type": "string"}, "number": {"type": "integer"}},
        ["repo", "number"],
    ),
    _tool(
        "list_issues",
        "List issues by state and label",
        {
            "repo": {"type": "string"},
            "state": {"type": "string", "default": "open"},
            "labels": {"type": "array", "items": {"type": "string"}},
            "limit": {"type": "integer", "default": 10},
        },
        ["repo"],
    ),
    _tool(
        "create_issue",
        "Create an issue (mutating; requires confirmation)",
        {
            "repo": {"type": "string"},
            "title": {"type": "string"},
            "body": {"type": "string", "default": ""},
            "labels": {"type": "array", "items": {"type": "string"}},
        },
        ["repo", "title"],
    ),
    _tool(
        "search_code",
        "Search code across repositories",
        {
            "query": {"type": "string"},
            "repo": {"type": "string"},
            "limit": {"type": "integer", "default": 10},
        },
        ["query"],
    ),
    _tool(
        "get_commits",
        "Commit history for a branch",
        {
            "repo": {"type": "string"},
            "branch": {"type": "string", "default": "main"},
            "limit": {"type": "integer", "default": 10},
        },
        ["repo"],
    ),
    _tool(
        "read_file",
        "Read file content at a ref",
        {
            "repo": {"type": "string"},
            "path": {"type": "string"},
            "ref": {"type": "string", "default": "main"},
        },
        ["repo", "path"],
    ),
]

TOOL_NAMES = [t.name for t in TOOL_DEFS]


def handle_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute a mock tool call and return a JSON-serializable payload."""
    if name not in TOOL_NAMES:
        return {"status": "error", "message": f"Unknown tool: {name}"}
    if name == "list_repos":
        if not arguments.get("owner"):
            return {"status": "error", "message": "owner is required"}
        limit = int(arguments.get("limit") or 10)
        repos = FIXTURE_REPOS[:limit]
        return {"status": "ok", "repos": repos, "count": len(repos)}
    if name == "list_prs":
        if not arguments.get("repo"):
            return {"status": "error", "message": "repo is required"}
        state = arguments.get("state") or "open"
        limit = int(arguments.get("limit") or 10)
        prs = [p for p in FIXTURE_PRS if p["state"] == state][:limit]
        return {"status": "ok", "prs": prs, "count": len(prs)}
    if name == "get_pr":
        if not arguments.get("repo") or arguments.get("number") is None:
            return {"status": "error", "message": "repo and number are required"}
        number = int(arguments["number"])
        for pr in FIXTURE_PRS:
            if pr["number"] == number:
                return {"status": "ok", "pr": pr}
        return {"status": "error", "message": f"PR #{number} not found"}
    if name == "list_issues":
        if not arguments.get("repo"):
            return {"status": "error", "message": "repo is required"}
        state = arguments.get("state") or "open"
        labels = arguments.get("labels") or []
        limit = int(arguments.get("limit") or 10)
        issues = [i for i in FIXTURE_ISSUES if i["state"] == state]
        if labels:
            issues = [i for i in issues if any(lb in i["labels"] for lb in labels)]
        issues = issues[:limit]
        return {"status": "ok", "issues": issues, "count": len(issues)}
    if name == "create_issue":
        if not arguments.get("repo") or not arguments.get("title"):
            return {"status": "error", "message": "repo and title are required"}
        return {
            "status": "ok",
            "issue": {
                "number": 99,
                "repo": arguments["repo"],
                "title": arguments["title"],
                "body": arguments.get("body", ""),
                "labels": arguments.get("labels", []),
                "state": "open",
                "mock": True,
            },
        }
    if name == "search_code":
        if not arguments.get("query"):
            return {"status": "error", "message": "query is required"}
        limit = int(arguments.get("limit") or 10)
        results = FIXTURE_CODE_SEARCH[:limit]
        return {"status": "ok", "results": results, "count": len(results)}
    if name == "get_commits":
        if not arguments.get("repo"):
            return {"status": "error", "message": "repo is required"}
        limit = int(arguments.get("limit") or 10)
        commits = FIXTURE_COMMITS[:limit]
        return {
            "status": "ok",
            "commits": commits,
            "branch": arguments.get("branch") or "main",
            "count": len(commits),
        }
    if name == "read_file":
        if not arguments.get("repo") or not arguments.get("path"):
            return {"status": "error", "message": "repo and path are required"}
        content = FIXTURE_FILES.get(arguments["path"])
        if content is None:
            return {"status": "error", "message": f"file not found: {arguments['path']}"}
        return {
            "status": "ok",
            "repo": arguments.get("repo", MOCK_REPO),
            "path": arguments["path"],
            "ref": arguments.get("ref") or "main",
            "content": content,
        }
    return {"status": "error", "message": f"Unhandled tool: {name}"}  # pragma: no cover


async def list_github_tools() -> list[Tool]:
    """Return the eight mock GitHub tool definitions."""
    return TOOL_DEFS


async def call_github_tool(
    name: str, arguments: dict[str, Any]
) -> list[TextContent]:
    """Execute one mock GitHub tool and wrap the payload."""
    try:
        payload = handle_tool(name, arguments or {})
    except Exception as e:
        logger.warning("mock github tool %s failed: %s", name, e)
        payload = {"status": "error", "message": str(e)}
    return [TextContent(type="text", text=json.dumps(payload))]


class GitHubMockMCPServer:
    """Mock GitHub MCP server speaking MCP over STDIO."""

    def __init__(self) -> None:
        self.server = Server("github-mock-mcp")
        self._register_tools()

    def _register_tools(self) -> None:
        self.server.list_tools()(list_github_tools)
        self.server.call_tool()(call_github_tool)

    async def run(self) -> None:
        """Run the mock server over STDIO."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


async def main() -> None:
    """Entry point for the mock GitHub MCP server."""
    server = GitHubMockMCPServer()
    await server.run()


if __name__ == "__main__":  # pragma: no cover
    import asyncio

    asyncio.run(main())
