"""
Integration smoke tests for the MCP server tools.

All backend calls (run_iterative_research, VectorStore, etc.) are mocked
so no real API keys or network access are needed.
"""

import asyncio
import json
import sys
import os
from types import ModuleType
from unittest.mock import MagicMock, patch

# ── Ensure project root is on path ───────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# ── Stub out heavy backend modules before server.py imports them ─────────────
def _make_stub(name: str, **attrs) -> ModuleType:
    mod = ModuleType(name)
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules[name] = mod
    return mod

# Stub every backend module that server.py might import transitively
_make_stub("tavily")
_make_stub("pinecone")
_make_stub("voyageai")
_make_stub("cohere")
_make_stub("langgraph")
_make_stub("langgraph.graph", StateGraph=MagicMock(), END=object())

_iter_stub = _make_stub("iterative_research")
_iter_stub.run_iterative_research = MagicMock()

_make_stub("research_tools", ResearchTools=MagicMock())
_make_stub("vector_store", VectorStore=MagicMock())
_make_stub("quality_scorer", score_research_quality=MagicMock(), _extract_json=MagicMock())
_make_stub("critique_agent", critique_research=MagicMock())
_make_stub("day3_advanced_rag_agent", planning_agent=MagicMock(), AdvancedResearchState=dict)

from mcp_server import session_store


# ── Fixtures ─────────────────────────────────────────────────────────────────

MOCK_STATE = {
    "research_id": "iter_test1234",
    "topic": "CRISPR applications",
    "summary": "CRISPR is a gene editing tool with many applications...",
    "quality_history": [
        {"iteration": 1, "overall": 8.2, "scores": {"depth": 8.0, "relevance": 8.5}},
    ],
    "sources": [{"title": "Nature article", "url": "https://nature.com/crispr", "score": 0.95}],
    "iteration": 1,
    "improvement_history": [],
    "stored_chunks": 12,
    "previous_summary": "",
    "research_questions": ["What is CRISPR?", "What are its applications?"],
    "search_results": {},
    "retrieval_method": "hybrid",
    "rag_context": "",
    "rerank_scores": [],
    "quality_metrics": {},
    "current_step": "complete",
    "max_iterations": 2,
    "quality_threshold": 7.5,
    "needs_more_research": False,
    "current_critique": {},
}


def setup_function():
    """Reset registry before each test."""
    with session_store._lock:
        session_store._sessions.clear()


# ── run_research tool ─────────────────────────────────────────────────────────

def test_run_research_returns_valid_json():
    """run_research returns JSON with expected keys when pipeline succeeds."""
    _iter_stub.run_iterative_research = MagicMock(return_value=MOCK_STATE)
    from mcp_server.server import run_research
    result = asyncio.run(run_research("CRISPR applications"))
    data = json.loads(result)
    assert data["research_id"] == "iter_test1234"
    assert data["topic"] == "CRISPR applications"
    assert "summary" in data
    assert "quality_history" in data
    assert "sources" in data
    assert isinstance(data["iterations"], int)
    assert data["final_score"] == 8.2


def test_run_research_saves_to_session_store():
    """run_research persists the state so follow-up tools can find it."""
    _iter_stub.run_iterative_research = MagicMock(return_value=MOCK_STATE)
    from mcp_server.server import run_research
    asyncio.run(run_research("CRISPR applications"))
    assert session_store.count() == 1
    session = session_store.get_session("iter_test1234")
    assert session is not None
    assert session["topic"] == "CRISPR applications"


def test_run_research_empty_topic_returns_error():
    """run_research rejects empty topic without calling the backend."""
    from mcp_server.server import run_research
    result = asyncio.run(run_research(""))
    assert result.startswith("ERROR")


def test_run_research_pipeline_exception_returns_error():
    """run_research surfaces backend exceptions as ERROR strings."""
    _iter_stub.run_iterative_research = MagicMock(side_effect=RuntimeError("API down"))
    from mcp_server.server import run_research
    result = asyncio.run(run_research("some topic"))
    assert "ERROR" in result
    assert "API down" in result


# ── session management tools ──────────────────────────────────────────────────

def test_list_sessions_empty():
    from mcp_server.server import list_sessions
    result = list_sessions()
    data = json.loads(result)
    assert "sessions" in data or isinstance(data, list)


def test_get_session_report_found():
    session_store.save_session("iter_test1234", MOCK_STATE)
    from mcp_server.server import get_session_report
    result = get_session_report("iter_test1234")
    data = json.loads(result)
    assert data["research_id"] == "iter_test1234"


def test_get_session_report_not_found():
    from mcp_server.server import get_session_report
    result = get_session_report("nonexistent_id")
    assert result.startswith("ERROR")


# ── ping ──────────────────────────────────────────────────────────────────────

def test_ping():
    from mcp_server.server import ping
    assert ping() == "pong"
