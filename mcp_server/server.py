"""
Autonomous Research Platform — MCP Server
==========================================

Exposes the iterative research pipeline as MCP tools, resources, and prompts
so Claude Desktop (or any MCP client) can run research, query the knowledge
base, and ask follow-up questions grounded in stored vector context.

Run with:
    python -m mcp_server.server

Or via the MCP CLI:
    mcp run mcp_server/server.py

Transport: stdio (default for Claude Desktop).
"""

import asyncio
import functools
import json
import os
import sys

# ── Put backend/ on the path before any backend imports ─────────────────────
_BACKEND = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, os.path.abspath(_BACKEND))

from dotenv import load_dotenv
load_dotenv(os.path.join(_BACKEND, ".env"))

from mcp.server.fastmcp import FastMCP

from mcp_server.utils import log, redirect_stdout_to_stderr
from mcp_server import session_store
from mcp_server.vector_client import get_vector_store

# ── FastMCP app ───────────────────────────────────────────────────────────────

mcp = FastMCP(
    "autonomous-research-platform",
    instructions=(
        "A research assistant that autonomously searches the web, synthesises "
        "a structured report, self-critiques it, and iteratively improves quality. "
        "After research completes you can query the stored knowledge base with "
        "natural-language questions grounded in retrieved context."
    ),
)


# ── Health check ─────────────────────────────────────────────────────────────

@mcp.tool()
def ping() -> str:
    """Health check. Returns 'pong' immediately. Use to verify the server is running."""
    log("ping received")
    return "pong"


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
