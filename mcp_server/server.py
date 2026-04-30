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
from mcp.types import PromptMessage, TextContent

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

    loop = asyncio.get_running_loop()
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

    loop = asyncio.get_running_loop()
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


@mcp.tool()
async def hybrid_search_research(
    research_id: str,
    query: str,
    top_k: int = 10,
    alpha: float = 0.7,
) -> str:
    """
    Hybrid semantic + keyword search over a specific research session.

    Combines dense (Voyage AI) and sparse (BM25-style) retrieval for better
    precision on queries with distinctive keywords.

    Args:
        research_id: ID returned by run_research.
        query: Natural-language question or keyword phrase.
        top_k: Number of chunks to return. Default 10, max 20.
        alpha: Weight for semantic vs keyword retrieval.
               1.0 = fully semantic, 0.0 = fully keyword. Default 0.7.

    Returns:
        JSON array of chunks: [{text, hybrid_score, score, metadata}]
    """
    if not research_id or not query:
        return "ERROR: research_id and query are required"

    top_k = min(top_k, 20)
    alpha = max(0.0, min(1.0, alpha))
    log(f"hybrid_search — research_id={research_id}, alpha={alpha}, top_k={top_k}")

    loop = asyncio.get_running_loop()
    try:
        vs = get_vector_store()
        results = await loop.run_in_executor(
            None,
            functools.partial(
                vs.hybrid_search,
                query=query,
                research_id=research_id,
                top_k=top_k,
                alpha=alpha,
            ),
        )
    except Exception as exc:
        log(f"hybrid_search_research failed: {exc}")
        return f"ERROR: {exc}"

    return json.dumps(
        [
            {
                "text": r["text"],
                "hybrid_score": round(r.get("hybrid_score", r.get("score", 0)), 4),
                "score": round(r.get("score", 0), 4),
                "metadata": r.get("metadata", {}),
            }
            for r in results
        ],
        indent=2,
    )


# ── Quality scoring tool ──────────────────────────────────────────────────────

@mcp.tool()
async def score_research(
    topic: str,
    summary: str,
    questions: list,
    sources_count: int = 0,
) -> str:
    """
    Score any research summary using the same Claude-based rubric as the pipeline.

    Evaluates on depth, relevance, clarity, and coverage (each 0-10) and
    returns weaknesses and improvement suggestions. Useful for evaluating
    externally generated content without running a full research job.

    Args:
        topic: Research topic the summary addresses.
        summary: The research summary text to evaluate.
        questions: List of research questions the summary should answer.
        sources_count: Number of sources used (for metadata context).

    Returns:
        JSON object with overall_score, depth_score, relevance_score,
        clarity_score, coverage_score, weaknesses, and suggestions.
    """
    if not topic or not summary:
        return "ERROR: topic and summary are required"

    log(f"score_research — topic: {topic!r}")

    from quality_scorer import score_research_quality

    fn = functools.partial(
        score_research_quality,
        topic=topic,
        questions=questions,
        summary=summary,
        sources_count=sources_count,
    )

    loop = asyncio.get_running_loop()
    try:
        with redirect_stdout_to_stderr():
            scores = await loop.run_in_executor(None, fn)
    except Exception as exc:
        log(f"score_research failed: {exc}")
        return f"ERROR: {exc}"

    return json.dumps(scores, indent=2)


# ── Session management tools ──────────────────────────────────────────────────

@mcp.tool()
def list_sessions() -> str:
    """
    List all research sessions completed in this MCP server process.

    Sessions are held in memory and reset on server restart.

    Returns:
        JSON array of session summaries: [{research_id, topic, iterations,
        final_score, source_count, stored_chunks, timestamp}]
    """
    sessions = session_store.list_all()
    if not sessions:
        return json.dumps({"message": "No research sessions in this process yet.", "sessions": []})
    return json.dumps(sessions, indent=2)


@mcp.tool()
def get_session_report(research_id: str) -> str:
    """
    Retrieve the full report for a previously completed research session.

    Args:
        research_id: ID returned by run_research.

    Returns:
        JSON object with research_id, topic, summary, quality_history,
        sources, iterations, improvement_history, stored_chunks, timestamp.
        Returns an ERROR string if research_id is not found.
    """
    if not research_id:
        return "ERROR: research_id is required"

    session = session_store.get_session(research_id)
    if not session:
        return f"ERROR: research_id '{research_id}' not found. Run run_research first or check list_sessions."

    return json.dumps(session, indent=2)


@mcp.tool()
async def get_session_stats(research_id: str) -> str:
    """
    Return storage stats for a research session: in-memory chunk count
    and live Pinecone index total vector count.

    Args:
        research_id: ID returned by run_research.

    Returns:
        JSON object with research_id, stored_chunks, index_total_vectors.
    """
    if not research_id:
        return "ERROR: research_id is required"

    session = session_store.get_session(research_id)
    if not session:
        return f"ERROR: research_id '{research_id}' not found."

    log(f"get_session_stats — research_id={research_id}")

    index_total = None
    try:
        vs = get_vector_store()
        loop = asyncio.get_running_loop()
        stats = await loop.run_in_executor(None, vs.get_index_stats)
        index_total = stats.get("total_vector_count") if isinstance(stats, dict) else None
    except Exception as exc:
        log(f"get_session_stats: Pinecone stats unavailable — {exc}")

    return json.dumps(
        {
            "research_id": research_id,
            "topic": session["topic"],
            "stored_chunks": session["stored_chunks"],
            "index_total_vectors": index_total,
        },
        indent=2,
    )


# ── MCP Resources ────────────────────────────────────────────────────────────

@mcp.resource("research://sessions")
def resource_sessions() -> str:
    """All in-process research sessions (JSON array of summaries)."""
    sessions = session_store.list_all()
    return json.dumps(sessions, indent=2)


@mcp.resource("research://{research_id}/report")
def resource_report(research_id: str) -> str:
    """Full markdown-formatted research report for a session."""
    session = session_store.get_session(research_id)
    if not session:
        return f"No session found for research_id: {research_id}"

    scores = session["quality_history"]
    score_lines = "\n".join(
        f"- Iteration {s['iteration']}: {s['overall']:.1f}/10"
        for s in scores
    )
    sources = "\n".join(
        f"- [{s['title']}]({s['url']})" for s in session["sources"][:10]
    )

    return f"""# Research Report: {session['topic']}

**Research ID:** `{research_id}`
**Iterations:** {session['iterations']}
**Timestamp:** {session['timestamp']}

## Quality Progression
{score_lines}

## Report

{session['summary']}

## Sources
{sources}
"""


@mcp.resource("research://{research_id}/sources")
def resource_sources(research_id: str) -> str:
    """Top sources (by Tavily relevance score) for a session as JSON."""
    session = session_store.get_session(research_id)
    if not session:
        return json.dumps({"error": f"No session found for {research_id}"})
    return json.dumps(session["sources"], indent=2)


@mcp.resource("research://{research_id}/quality")
def resource_quality(research_id: str) -> str:
    """Quality history across iterations for a session as JSON."""
    session = session_store.get_session(research_id)
    if not session:
        return json.dumps({"error": f"No session found for {research_id}"})
    return json.dumps(session["quality_history"], indent=2)


# ── MCP Prompts ───────────────────────────────────────────────────────────────

@mcp.prompt()
def research_briefing(research_id: str) -> list:
    """
    Prime a conversation with the full research report as context.

    Generates a system + user message pair that loads the stored report for
    research_id into the conversation, instructing Claude to answer follow-up
    questions accurately and cite sources. Mirrors what /api/chat does in the
    FastAPI backend, but packaged for direct MCP use.

    Args:
        research_id: ID returned by run_research.
    """
    session = session_store.get_session(research_id)
    if not session:
        system_text = "No research session found for the given ID."
        user_text = f"research_id '{research_id}' was not found. Please run run_research first."
    else:
        sources_text = "\n".join(
            f"- {s['title']} ({s['url']})" for s in session["sources"][:10]
        )
        system_text = (
            f"You are a knowledgeable research assistant. Answer questions based on "
            f"the research report below. Be concise and accurate; cite specific details "
            f"and source titles inline when relevant.\n\n"
            f"## Research Report: {session['topic']}\n\n"
            f"{session['summary']}\n\n"
            f"## Sources\n{sources_text}"
        )
        user_text = "I'm ready for your questions about the research."

    return [
        PromptMessage(role="user", content=TextContent(type="text", text=system_text)),
        PromptMessage(role="assistant", content=TextContent(type="text", text=user_text)),
    ]


@mcp.prompt()
def research_planning(topic: str) -> list:
    """
    Generate targeted research questions for a topic.

    Produces the same planning prompt the pipeline uses internally so you can
    preview or customise questions before running a full research job.

    Args:
        topic: The research topic to plan for.
    """
    user_text = (
        f"Generate 3 specific, searchable research questions for the following topic.\n\n"
        f"Topic: {topic}\n\n"
        f"Return ONLY a JSON array:\n"
        f'["Question 1?", "Question 2?", "Question 3?"]'
    )
    return [
        PromptMessage(role="user", content=TextContent(type="text", text=user_text)),
    ]


@mcp.prompt()
def research_critique(topic: str, summary: str) -> list:
    """
    Critique a research summary on depth, relevance, clarity, and coverage.

    Useful for evaluating summaries without running the full quality scorer tool.

    Args:
        topic: The research topic the summary addresses.
        summary: The summary text to critique.
    """
    user_text = (
        f"Critique the following research summary on these four dimensions, "
        f"each scored 0-10:\n"
        f"1. Depth — how thorough is the coverage?\n"
        f"2. Relevance — does it stay on topic?\n"
        f"3. Clarity — is it well-written and easy to follow?\n"
        f"4. Coverage — are all important aspects addressed?\n\n"
        f"Topic: {topic}\n\n"
        f"Summary:\n{summary}\n\n"
        f"List specific weaknesses and actionable improvement suggestions."
    )
    return [
        PromptMessage(role="user", content=TextContent(type="text", text=user_text)),
    ]


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
