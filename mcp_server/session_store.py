"""
In-Process Session Registry
============================

Holds completed research sessions for the lifetime of the MCP server process.
Sessions do not persist across server restarts — restart = clean slate.

Thread safety: all mutations are protected by a Lock because tool calls run
inside executor threads while the FastMCP event loop reads from async handlers.
"""

import threading
from datetime import datetime
from typing import Dict, Optional


_lock = threading.Lock()
_sessions: Dict[str, dict] = {}


def save_session(research_id: str, state: dict) -> None:
    """Persist a completed research state keyed by research_id."""
    record = {
        "research_id": research_id,
        "topic": state.get("topic", ""),
        "summary": state.get("summary", ""),
        "quality_history": state.get("quality_history", []),
        "sources": state.get("sources", []),
        "iterations": state.get("iteration", 1),
        "improvement_history": state.get("improvement_history", []),
        "stored_chunks": state.get("stored_chunks", 0),
        "timestamp": datetime.now().isoformat(),
    }
    with _lock:
        _sessions[research_id] = record


def get_session(research_id: str) -> Optional[dict]:
    """Return session record or None if not found."""
    with _lock:
        return _sessions.get(research_id)


def list_all() -> list:
    """Return a summary list of all sessions (lightweight, no full summaries)."""
    with _lock:
        return [
            {
                "research_id": s["research_id"],
                "topic": s["topic"],
                "iterations": s["iterations"],
                "final_score": (
                    s["quality_history"][-1]["overall"]
                    if s["quality_history"]
                    else None
                ),
                "source_count": len(s["sources"]),
                "stored_chunks": s["stored_chunks"],
                "timestamp": s["timestamp"],
            }
            for s in _sessions.values()
        ]


def count() -> int:
    """Return number of sessions in the registry."""
    with _lock:
        return len(_sessions)
