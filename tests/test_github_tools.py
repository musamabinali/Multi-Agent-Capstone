"""Phase 2: GitHub tool catalog unit tests (validation, shape, flags)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


def _fake_client():
    fake = MagicMock()
    fake.call_tool.return_value = {"status": "ok"}
    return fake


def test_validate_repo():
    from makpa.subagents.github.tools import validate_repo

    assert validate_repo("octo-demo/hello-world") == "octo-demo/hello-world"
    for bad in ("", "no-slash", "/x", "a/", "a/b/c", "a b/c"):
        with pytest.raises(ValueError, match="Invalid repo"):
            validate_repo(bad)


def test_all_tools_call_client_with_normalized_shape():
    from makpa.subagents.github import tools as tools_mod

    cases = [
        (
            "github_list_repos",
            {"owner": "octo-demo"},
            ("list_repos", {"owner": "octo-demo", "limit": 10}),
        ),
        (
            "github_list_prs",
            {"repo": "o/r"},
            ("list_prs", {"repo": "o/r", "state": "open", "limit": 10}),
        ),
        (
            "github_get_pr",
            {"repo": "o/r", "number": 7},
            ("get_pr", {"repo": "o/r", "number": 7}),
        ),
        (
            "github_list_issues",
            {"repo": "o/r"},
            ("list_issues", {"repo": "o/r", "state": "open", "labels": [], "limit": 10}),
        ),
        (
            "github_create_issue",
            {"repo": "o/r", "title": "T"},
            ("create_issue", {"repo": "o/r", "title": "T", "body": "", "labels": []}),
        ),
        ("github_search_code", {"query": "q"}, ("search_code", {"query": "q", "limit": 10})),
        (
            "github_get_commits",
            {"repo": "o/r"},
            ("get_commits", {"repo": "o/r", "branch": "main", "limit": 10}),
        ),
        (
            "github_read_file",
            {"repo": "o/r", "path": "README.md"},
            ("read_file", {"repo": "o/r", "path": "README.md", "ref": "main"}),
        ),
    ]
    by_name = {t.name: t for t in tools_mod.GITHUB_TOOLS}
    assert len(by_name) == 8
    for name, args, (expect_tool, expect_args) in cases:
        fake = _fake_client()
        with patch.object(tools_mod, "get_github_client", return_value=fake):
            out = by_name[name].invoke(args)
        assert out == {"status": "ok"}
        fake.call_tool.assert_called_once_with(expect_tool, expect_args)


def test_search_code_with_repo_scope():
    from makpa.subagents.github import tools as tools_mod

    by_name = {t.name: t for t in tools_mod.GITHUB_TOOLS}
    fake = MagicMock()
    fake.call_tool.return_value = {"status": "ok", "results": []}
    with patch.object(tools_mod, "get_github_client", return_value=fake):
        out = by_name["github_search_code"].invoke({"query": "q", "repo": "o/r"})
    assert out == {"status": "ok", "results": []}
    fake.call_tool.assert_called_once_with(
        "search_code", {"query": "q", "limit": 10, "repo": "o/r"}
    )


def test_tools_reject_bad_repo():
    from makpa.subagents.github import tools as tools_mod

    by_name = {t.name: t for t in tools_mod.GITHUB_TOOLS}
    with pytest.raises(Exception, match="Invalid repo"):
        by_name["github_list_prs"].invoke({"repo": "bad"})
    with pytest.raises(Exception, match="Invalid repo"):
        by_name["github_search_code"].invoke({"query": "q", "repo": "bad"})


def test_create_issue_empty_title_and_read_file_empty_path():
    from makpa.subagents.github import tools as tools_mod

    by_name = {t.name: t for t in tools_mod.GITHUB_TOOLS}
    fake = _fake_client()
    with patch.object(tools_mod, "get_github_client", return_value=fake):
        out = by_name["github_create_issue"].invoke({"repo": "o/r", "title": "  "})
        assert out["status"] == "error"
        out = by_name["github_read_file"].invoke({"repo": "o/r", "path": "  "})
        assert out["status"] == "error"
    fake.call_tool.assert_not_called()


def test_requires_confirmation_flags():
    from makpa.subagents.github.tools import GITHUB_TOOLS, MUTATING_TOOLS

    assert MUTATING_TOOLS == frozenset({"github_create_issue"})
    for tool_obj in GITHUB_TOOLS:
        expect = tool_obj.name in MUTATING_TOOLS
        assert tool_obj.metadata["requires_confirmation"] is expect
