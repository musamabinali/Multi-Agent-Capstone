"""Retrieval MCP server for MAKPA.

Real implementation exposing document search over STDIO.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from makpa.config import get_settings

logger = logging.getLogger(__name__)


async def list_retrieval_tools() -> list[Tool]:
    """Return the retrieval tool definitions."""
    return [
        Tool(
            name="search_documents",
            description="Search documents in the vector store",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "k": {
                        "type": "integer",
                        "description": "Number of results",
                        "default": 5,
                    },
                    "filter": {"type": "object", "description": "Metadata filter"},
                },
                "required": ["query"],
            },
        ),
    ]


async def call_search_documents(
    name: str, arguments: dict[str, Any]
) -> list[TextContent]:
    """Execute the search_documents tool and wrap the payload."""
    if name != "search_documents":
        return [
            TextContent(
                type="text",
                text=json.dumps({"status": "error", "message": f"Unknown tool: {name}"}),
            )
        ]
    query = arguments.get("query", "")
    if not query:
        return [
            TextContent(
                type="text",
                text=json.dumps({"status": "error", "message": "query is required"}),
            )
        ]
    settings = get_settings()
    k = arguments.get("k") or settings.rag_k
    filt = arguments.get("filter")
    try:
        from makpa.rag.retriever import retrieve_documents

        results = retrieve_documents(
            query,
            k=int(k),
            filter=filt,
        )
    except Exception as e:
        logger.warning("search_documents failed: %s", e)
        return [
            TextContent(
                type="text",
                text=json.dumps({"status": "error", "message": str(e)}),
            )
        ]
    if not results:
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "status": "empty",
                        "message": "no relevant documents found",
                        "chunks": [],
                        "count": 0,
                    }
                ),
            )
        ]
    chunks = []
    for doc, score in results:
        meta = doc.metadata or {}
        chunks.append(
            {
                "text": doc.page_content,
                "source": meta.get("source", "unknown"),
                "page": meta.get("page", 0),
                "chunk_id": meta.get("chunk_index", 0),
                "doc_id": meta.get("doc_id", ""),
                "score": float(score),
            }
        )
    return [
        TextContent(
            type="text",
            text=json.dumps({"status": "ok", "chunks": chunks, "count": len(chunks)}),
        )
    ]


class RetrievalMCPServer:
    """Retrieval MCP Server that exposes document search via MCP protocol."""

    def __init__(self) -> None:
        self.server = Server("retrieval-mcp")
        self._register_tools()

    def _register_tools(self) -> None:
        """Register MCP tools."""
        self.server.list_tools()(list_retrieval_tools)
        self.server.call_tool()(call_search_documents)

    async def run(self) -> None:
        """Run the MCP server over STDIO."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


async def main() -> None:
    """Entry point for the Retrieval MCP server."""
    server = RetrievalMCPServer()
    await server.run()


if __name__ == "__main__":  # pragma: no cover
    import asyncio

    asyncio.run(main())
