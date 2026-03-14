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


# ── Core research tool ────────────────────────────────────────────────────────

@mcp.tool()
async def run_research(
    topic: str,
    quality_threshold: float = 7.5,
    max_iterations: int = 2,
) -> str:
    """
    Run the full iterative research pipeline on a topic.

    Executes: planning (Haiku) → parallel web search (Tavily) → synthesis
    (Sonnet) → quality scoring → critique → improvement loop.

    This is a long-running call (1-5 minutes). Progress is logged to stderr.

    Args:
        topic: The research topic to investigate.
        quality_threshold: Minimum quality score (1-10) to accept the report.
                           Default 7.5.
        max_iterations: Maximum improvement iterations. Default 2.

    Returns:
        JSON string with keys: research_id, topic, summary, quality_history,
        iterations, improvement_history, sources.
        Use research_id with the search_research tool for follow-up queries.
    """
    if not topic or not topic.strip():
        return "ERROR: topic must be a non-empty string"

    log(f"run_research starting — topic: {topic!r}")

    from iterative_research import run_iterative_research

    # Accumulate synthesis tokens so we can log progress without streaming
    _token_buf: list[str] = []

    def on_token(text):
        if text is None:
            log("Synthesis in progress...")
            _token_buf.clear()
        else:
            _token_buf.append(text)
            # Log a progress dot every ~200 chars so stderr shows activity
            joined = "".join(_token_buf)
            if len(joined) % 200 < len(text):
                log(f"  synthesising... ({len(joined)} chars so far)")

    fn = functools.partial(
        run_iterative_research,
        topic=topic,
        quality_threshold=quality_threshold,
        max_iterations=max_iterations,
        on_synthesis_token=on_token,
    )

    loop = asyncio.get_event_loop()
    try:
        with redirect_stdout_to_stderr():
            state = await loop.run_in_executor(None, fn)
    except Exception as exc:
        log(f"run_research failed: {exc}")
        return f"ERROR: {exc}"

    session_store.save_session(state["research_id"], state)
    log(f"run_research complete — research_id: {state['research_id']}")

    final_score = (
        state["quality_history"][-1]["overall"] if state["quality_history"] else None
    )

    return json.dumps(
        {
            "research_id": state["research_id"],
            "topic": state["topic"],
            "summary": state["summary"],
            "quality_history": state["quality_history"],
            "iterations": state["iteration"],
            "improvement_history": state["improvement_history"],
            "sources": state["sources"],
            "final_score": final_score,
        },
        indent=2,
    )


# ── RAG search tools ─────────────────────────────────────────────────────────

@mcp.tool()
async def search_research(
    research_id: str,
    query: str,
    top_k: int = 5,
) -> str:
    """
    Semantic search over a specific research session stored in Pinecone.

    Embeds the query with Voyage AI and retrieves the most relevant chunks
    from the vector store, filtered to the given research_id.

    Args:
        research_id: ID returned by run_research.
        query: Natural-language question or keyword phrase.
        top_k: Number of chunks to return. Default 5, max 20.

    Returns:
        JSON array of chunks: [{text, score, metadata: {title, url, question}}]
        or an ERROR string if Pinecone is unreachable.
    """
    if not research_id or not query:
        return "ERROR: research_id and query are required"

    top_k = min(top_k, 20)
    log(f"search_research — research_id={research_id}, query={query!r}, top_k={top_k}")

    loop = asyncio.get_event_loop()
    try:
        vs = get_vector_store()
        results = await loop.run_in_executor(
            None,
            functools.partial(
                vs.search_with_filters,
                query=query,
                research_id=research_id,
                top_k=top_k,
            ),
        )
    except Exception as exc:
        log(f"search_research failed: {exc}")
        return f"ERROR: {exc}"

    return json.dumps(
        [
            {
                "text": r["text"],
                "score": round(r.get("score", 0), 4),
                "metadata": r.get("metadata", {}),
            }
            for r in results
        ],
        indent=2,
    )


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
