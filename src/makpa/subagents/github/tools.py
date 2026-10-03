"""GitHub tool catalog for MAKPA Phase 2.

Wraps each GitHub MCP tool with a LangChain ``@tool`` that enforces a
strict Pydantic argument schema, validates the ``repo`` argument, and
returns a normalized payload. Mutating tools carry
``requires_confirmation=True`` in their metadata and are listed in
:data:`MUTATING_TOOLS`.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from .client import get_github_client

logger = logging.getLogger(__name__)

REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")

#: Tools that mutate shared GitHub state and require interrupt() confirmation.
MUTATING_TOOLS: frozenset[str] = frozenset({"github_create_issue"})


def validate_repo(repo: str) -> str:
    """Validate that ``repo`` is a well-formed ``owner/name`` slug.

    Raises:
        ValueError: If the slug is missing or malformed.
    """
    if not repo or not REPO_PATTERN.match(repo.strip()):
        raise ValueError(
            f"Invalid repo {repo!r}: expected 'owner/name' "
            "(letters, digits, '.', '-', '_')"
        )
    return repo.strip()


def _normalized(status: str, **fields: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"status": status}
    payload.update(fields)
    return payload


class ListReposArgs(BaseModel):  # type: ignore[misc]
    """Arguments for listing repositories."""

    owner: str = Field(description="GitHub user or organization login")
    limit: int = Field(default=10, ge=1, le=100)


class ListPRsArgs(BaseModel):  # type: ignore[misc]
    """Arguments for listing pull requests."""

    repo: str = Field(description="Repository slug 'owner/name'")
    state: str = Field(default="open", description="open | closed | all")
    limit: int = Field(default=10, ge=1, le=100)


class GetPRArgs(BaseModel):  # type: ignore[misc]
    """Arguments for getting a pull request."""

    repo: str = Field(description="Repository slug 'owner/name'")
    number: int = Field(ge=1)


class ListIssuesArgs(BaseModel):  # type: ignore[misc]
    """Arguments for listing issues."""

    repo: str = Field(description="Repository slug 'owner/name'")
    state: str = Field(default="open", description="open | closed | all")
    labels: list[str] = Field(default_factory=list)
    limit: int = Field(default=10, ge=1, le=100)


class CreateIssueArgs(BaseModel):  # type: ignore[misc]
    """Arguments for creating an issue (mutating)."""

    repo: str = Field(description="Repository slug 'owner/name'")
    title: str = Field(min_length=1)
    body: str = Field(default="")
    labels: list[str] = Field(default_factory=list)


class SearchCodeArgs(BaseModel):  # type: ignore[misc]
    """Arguments for code search."""

    query: str = Field(min_length=1)
    repo: str | None = Field(default=None, description="Optional 'owner/name' scope")
    limit: int = Field(default=10, ge=1, le=100)


class GetCommitsArgs(BaseModel):  # type: ignore[misc]
    """Arguments for commit history."""

    repo: str = Field(description="Repository slug 'owner/name'")
    branch: str = Field(default="main")
    limit: int = Field(default=10, ge=1, le=100)


class ReadFileArgs(BaseModel):  # type: ignore[misc]
    """Arguments for reading a file."""

    repo: str = Field(description="Repository slug 'owner/name'")
    path: str = Field(min_length=1)
    ref: str = Field(default="main")


def _mark(tool_obj: Any, *, mutating: bool) -> Any:
    existing = dict(tool_obj.metadata) if tool_obj.metadata else {}
    existing["requires_confirmation"] = mutating
    tool_obj.metadata = existing
    return tool_obj


@tool("github_list_repos", args_schema=ListReposArgs)  # type: ignore[untyped-decorator]
def github_list_repos(owner: str, limit: int = 10) -> dict[str, Any]:
    """List repositories for a user or org."""
    client = get_github_client()
    return client.call_tool("list_repos", {"owner": owner, "limit": limit})


@tool("github_list_prs", args_schema=ListPRsArgs)  # type: ignore[untyped-decorator]
def github_list_prs(repo: str, state: str = "open", limit: int = 10) -> dict[str, Any]:
    """List pull requests by state."""
    validate_repo(repo)
    client = get_github_client()
    return client.call_tool("list_prs", {"repo": repo, "state": state, "limit": limit})


@tool("github_get_pr", args_schema=GetPRArgs)  # type: ignore[untyped-decorator]
def github_get_pr(repo: str, number: int) -> dict[str, Any]:
    """Get PR details, files, and comments."""
    validate_repo(repo)
    client = get_github_client()
    return client.call_tool("get_pr", {"repo": repo, "number": number})


@tool("github_list_issues", args_schema=ListIssuesArgs)  # type: ignore[untyped-decorator]
def github_list_issues(
    repo: str, state: str = "open", labels: list[str] | None = None, limit: int = 10
) -> dict[str, Any]:
    """List issues by state and label."""
    validate_repo(repo)
    client = get_github_client()
    return client.call_tool(
        "list_issues",
        {"repo": repo, "state": state, "labels": labels or [], "limit": limit},
    )


@tool("github_create_issue", args_schema=CreateIssueArgs)  # type: ignore[untyped-decorator]
def github_create_issue(
    repo: str, title: str, body: str = "", labels: list[str] | None = None
) -> dict[str, Any]:
    """Create an issue. MUTATING: requires human confirmation."""
    validate_repo(repo)
    if not title.strip():
        return _normalized("error", message="title must not be empty")
    client = get_github_client()
    return client.call_tool(
        "create_issue",
        {"repo": repo, "title": title, "body": body, "labels": labels or []},
    )


@tool("github_search_code", args_schema=SearchCodeArgs)  # type: ignore[untyped-decorator]
def github_search_code(
    query: str, repo: str | None = None, limit: int = 10
) -> dict[str, Any]:
    """Search code across repos."""
    if repo is not None:
        validate_repo(repo)
    client = get_github_client()
    args: dict[str, Any] = {"query": query, "limit": limit}
    if repo:
        args["repo"] = repo
    return client.call_tool("search_code", args)


@tool("github_get_commits", args_schema=GetCommitsArgs)  # type: ignore[untyped-decorator]
def github_get_commits(repo: str, branch: str = "main", limit: int = 10) -> dict[str, Any]:
    """Commit history for a branch."""
    validate_repo(repo)
    client = get_github_client()
    return client.call_tool(
        "get_commits", {"repo": repo, "branch": branch, "limit": limit}
    )


@tool("github_read_file", args_schema=ReadFileArgs)  # type: ignore[untyped-decorator]
def github_read_file(repo: str, path: str, ref: str = "main") -> dict[str, Any]:
    """Read file content at a ref."""
    validate_repo(repo)
    if not path.strip():
        return _normalized("error", message="path must not be empty")
    client = get_github_client()
    return client.call_tool("read_file", {"repo": repo, "path": path, "ref": ref})


GITHUB_TOOLS = [
    github_list_repos,
    github_list_prs,
    github_get_pr,
    github_list_issues,
    github_create_issue,
    github_search_code,
    github_get_commits,
    github_read_file,
]

for _t in GITHUB_TOOLS:
    _mark(_t, mutating=_t.name in MUTATING_TOOLS)

__all__ = [
    "GITHUB_TOOLS",
    "MUTATING_TOOLS",
    "REPO_PATTERN",
    "github_create_issue",
    "github_get_commits",
    "github_get_pr",
    "github_list_issues",
    "github_list_prs",
    "github_list_repos",
    "github_read_file",
    "github_search_code",
    "validate_repo",
]
