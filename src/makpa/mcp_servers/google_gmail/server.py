"""Local Gmail MCP server for MAKPA (real Gmail v1 wrapper).

Speaks MCP over STDIO. Encodes RFC 2822 messages as UTF-8 base64url.
Every handler degrades to a structured error envelope on auth,
recipient, or quota failures.
"""

from __future__ import annotations

import base64
import json
import logging
import re
from email.message import EmailMessage
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

logger = logging.getLogger(__name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _get_service() -> Any:
    """Build the Gmail v1 service from cached OAuth credentials."""
    from googleapiclient.discovery import build

    from makpa.google.oauth import get_google_credentials

    return build("gmail", "v1", credentials=get_google_credentials())


def validate_recipients(values: list[str], field: str = "to") -> list[str]:
    """Validate email recipients.

    Raises:
        ValueError: On empty lists or malformed addresses.
    """
    cleaned = [v.strip() for v in values if v and v.strip()]
    if not cleaned:
        raise ValueError(f"{field} must contain at least one recipient")
    for address in cleaned:
        if not EMAIL_RE.match(address):
            raise ValueError(f"Invalid email address in {field}: {address!r}")
    return cleaned


def _optional_recipients(values: Any, field: str) -> list[str]:
    """Validate an optional cc/bcc list (empty when absent)."""
    if not values:
        return []
    return validate_recipients(values, field=field)


def build_rfc2822(
    to: list[str],
    subject: str,
    body: str,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
) -> str:
    """Build a base64url-encoded RFC 2822 message (UTF-8)."""
    message = EmailMessage()
    message["To"] = ", ".join(to)
    if cc:
        message["Cc"] = ", ".join(cc)
    if bcc:
        message["Bcc"] = ", ".join(bcc)
    message["Subject"] = subject
    message.set_content(body or "")
    raw = message.as_bytes()
    return base64.urlsafe_b64encode(raw).decode()


def _message_to_payload(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item.get("id", ""),
        "thread_id": item.get("threadId", ""),
        "label_ids": item.get("labelIds", []),
        "snippet": item.get("snippet", ""),
    }


def handle_gmail_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute a Gmail tool against the v1 API."""
    if name == "gmail_search_messages":
        if not arguments.get("query"):
            return {"status": "error", "message": "query is required"}
        max_results = int(arguments.get("max_results") or 10)
        try:
            service = _get_service()
            response = (
                service.users()
                .messages()
                .list(userId="me", q=arguments["query"], maxResults=max_results)
                .execute()
            )
        except Exception as e:
            logger.warning("gmail_search_messages failed: %s", type(e).__name__)
            return {"status": "error", "message": f"Gmail API error: {e}"}
        messages = response.get("messages", [])
        return {
            "status": "ok",
            "messages": [_message_to_payload(m) for m in messages],
            "count": len(messages),
        }
    if name == "gmail_read_message":
        if not arguments.get("message_id"):
            return {"status": "error", "message": "message_id is required"}
        try:
            service = _get_service()
            item = (
                service.users()
                .messages()
                .get(userId="me", id=arguments["message_id"], format="full")
                .execute()
            )
        except Exception as e:
            logger.warning("gmail_read_message failed: %s", type(e).__name__)
            return {"status": "error", "message": f"Gmail API error: {e}"}
        payload = _message_to_payload(item)
        headers = {
            h.get("name", ""): h.get("value", "")
            for h in item.get("payload", {}).get("headers", [])
        }
        payload["subject"] = headers.get("Subject", "")
        payload["from"] = headers.get("From", "")
        return {"status": "ok", "message": payload}
    if name == "gmail_draft_message":
        try:
            to = validate_recipients(arguments.get("to") or [], field="to")
            cc = _optional_recipients(arguments.get("cc"), field="cc")
            bcc = _optional_recipients(arguments.get("bcc"), field="bcc")
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        if not arguments.get("subject"):
            return {"status": "error", "message": "subject is required"}
        raw = build_rfc2822(
            to, str(arguments["subject"]), str(arguments.get("body", "")), cc, bcc
        )
        try:
            service = _get_service()
            draft = (
                service.users()
                .drafts()
                .create(userId="me", body={"message": {"raw": raw}})
                .execute()
            )
        except Exception as e:
            logger.warning("gmail_draft_message failed: %s", type(e).__name__)
            return {"status": "error", "message": f"Gmail API error: {e}"}
        return {
            "status": "ok",
            "draft": {
                "id": draft.get("id", ""),
                "message_id": draft.get("message", {}).get("id", ""),
            },
        }
    if name == "gmail_send_message":
        try:
            to = validate_recipients(arguments.get("to") or [], field="to")
            cc = _optional_recipients(arguments.get("cc"), field="cc")
            bcc = _optional_recipients(arguments.get("bcc"), field="bcc")
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        if not arguments.get("subject"):
            return {"status": "error", "message": "subject is required"}
        draft_id = arguments.get("draft_id")
        try:
            service = _get_service()
            if draft_id:
                sent = (
                    service.users()
                    .drafts()
                    .send(userId="me", body={"id": draft_id})
                    .execute()
                )
            else:
                raw = build_rfc2822(
                    to, str(arguments["subject"]), str(arguments.get("body", "")), cc, bcc
                )
                sent = (
                    service.users()
                    .messages()
                    .send(userId="me", body={"raw": raw})
                    .execute()
                )
        except Exception as e:
            logger.warning("gmail_send_message failed: %s", type(e).__name__)
            return {"status": "error", "message": f"Gmail API error: {e}"}
        return {
            "status": "ok",
            "sent": {
                "id": sent.get("id", ""),
                "thread_id": sent.get("threadId", ""),
                "label_ids": sent.get("labelIds", []),
            },
        }
    return {"status": "error", "message": f"Unknown tool: {name}"}


GMAIL_TOOL_DEFS: list[Tool] = [
    Tool(
        name="gmail_search_messages",
        description="Search Gmail messages",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "max_results": {"type": "integer", "default": 10},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="gmail_read_message",
        description="Read a Gmail message by id",
        inputSchema={
            "type": "object",
            "properties": {"message_id": {"type": "string"}},
            "required": ["message_id"],
        },
    ),
    Tool(
        name="gmail_draft_message",
        description="Create a Gmail draft (safe, no gate)",
        inputSchema={
            "type": "object",
            "properties": {
                "to": {"type": "array", "items": {"type": "string"}},
                "subject": {"type": "string"},
                "body": {"type": "string"},
                "cc": {"type": "array", "items": {"type": "string"}},
                "bcc": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["to", "subject"],
        },
    ),
    Tool(
        name="gmail_send_message",
        description="Send an email, optionally from a draft (mutating)",
        inputSchema={
            "type": "object",
            "properties": {
                "to": {"type": "array", "items": {"type": "string"}},
                "subject": {"type": "string"},
                "body": {"type": "string"},
                "cc": {"type": "array", "items": {"type": "string"}},
                "bcc": {"type": "array", "items": {"type": "string"}},
                "draft_id": {"type": "string"},
            },
            "required": ["to", "subject"],
        },
    ),
]

GMAIL_TOOL_NAMES = [t.name for t in GMAIL_TOOL_DEFS]


async def list_gmail_tools() -> list[Tool]:
    """Return the Gmail tool definitions."""
    return GMAIL_TOOL_DEFS


async def call_gmail_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute one Gmail tool and wrap the payload."""
    try:
        payload = handle_gmail_tool(name, arguments or {})
    except Exception as e:
        logger.warning("gmail tool %s failed: %s", name, type(e).__name__)
        payload = {"status": "error", "message": str(e)}
    return [TextContent(type="text", text=json.dumps(payload))]


class GmailMCPServer:
    """Local Gmail MCP server speaking MCP over STDIO."""

    def __init__(self) -> None:
        self.server = Server("gmail-mcp")
        self.server.list_tools()(list_gmail_tools)
        self.server.call_tool()(call_gmail_tool)

    async def run(self) -> None:
        """Run the server over STDIO."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


async def main() -> None:
    """Entry point for the local Gmail MCP server."""
    server = GmailMCPServer()
    await server.run()


if __name__ == "__main__":  # pragma: no cover
    import asyncio

    asyncio.run(main())
