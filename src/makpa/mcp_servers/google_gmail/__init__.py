"""Local Gmail MCP server package (real Gmail v1 wrapper)."""

from .mock import MOCK_DRAFTS, MOCK_MESSAGES, MockGmailMCPServer, handle_mock_gmail_tool
from .server import (
    GMAIL_TOOL_DEFS,
    GMAIL_TOOL_NAMES,
    GmailMCPServer,
    build_rfc2822,
    call_gmail_tool,
    handle_gmail_tool,
    list_gmail_tools,
    main,
    validate_recipients,
)

__all__ = [
    "GMAIL_TOOL_DEFS",
    "GMAIL_TOOL_NAMES",
    "MOCK_DRAFTS",
    "MOCK_MESSAGES",
    "GmailMCPServer",
    "MockGmailMCPServer",
    "handle_mock_gmail_tool",
    "build_rfc2822",
    "call_gmail_tool",
    "handle_gmail_tool",
    "list_gmail_tools",
    "main",
    "validate_recipients",
]
