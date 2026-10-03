"""Live-server harness for the web gate (D3).

Starts the thin FastAPI adapter on :8001 with a fully deterministic
mock-backed stack: mock LLM (blank provider keys), mock GitHub/Calendar/Gmail
MCP, attendee verification bypassed for the composite flow. Real HTTP servers,
real SSE, real supervisor/graph/MCP subprocesses — no mocked routes.

Child-process env only: the repo `.env` file is never modified. Overrides are
applied with os.environ here (not inherited) because detached launches do not
reliably inherit session env on all hosts.
"""

from __future__ import annotations

import os

# Deterministic mock stack (harness-owned, documented in REVIEW.md).
os.environ["MAKPA_MODE"] = "demo"
os.environ["GEMINI_API_KEY"] = ""
os.environ["GROQ_API_KEY"] = ""
os.environ["GITHUB_MCP_PAT"] = ""
os.environ["GITHUB_MCP_MODE"] = "mock"
os.environ["GOOGLE_MCP_MODE"] = "mock"
os.environ["GOOGLE_CALENDAR_ATTENDEE_MODE"] = "all"

# Keep large caches off small system drives.
os.environ.setdefault("HF_HOME", r"D:\hf-cache")
os.environ.setdefault("HUGGINGFACE_HUB_CACHE", r"D:\hf-cache\hub")
os.environ.setdefault("TMP", r"D:\temp")
os.environ.setdefault("TEMP", r"D:\temp")

import uvicorn  # noqa: E402


def main() -> None:
    uvicorn.run("makpa.api.server:app", host="127.0.0.1", port=8001, workers=1)


if __name__ == "__main__":
    main()
