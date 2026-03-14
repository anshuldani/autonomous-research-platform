"""Unit tests for the in-process session registry."""

import threading
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mcp_server import session_store


def _make_state(rid: str, topic: str = "Test topic", score: float = 8.0) -> dict:
    return {
        "research_id": rid,
        "topic": topic,
        "summary": "A test summary.",
        "quality_history": [{"iteration": 1, "overall": score, "scores": {}}],
        "sources": [{"title": "Src", "url": "https://example.com", "score": 0.9}],
        "iteration": 1,
        "improvement_history": [],
        "stored_chunks": 3,
    }


def setup_function():
    """Reset registry before each test."""
    with session_store._lock:
        session_store._sessions.clear()


def test_save_and_get():
    state = _make_state("rid_001")
    session_store.save_session("rid_001", state)
    record = session_store.get_session("rid_001")
    assert record is not None
    assert record["research_id"] == "rid_001"
    assert record["topic"] == "Test topic"
    assert record["stored_chunks"] == 3


def test_get_missing_returns_none():
    assert session_store.get_session("nonexistent") is None


def test_list_all_empty():
    result = session_store.list_all()
    assert result == []


def test_list_all_populated():
    session_store.save_session("rid_a", _make_state("rid_a", "Topic A", 7.0))
    session_store.save_session("rid_b", _make_state("rid_b", "Topic B", 9.0))
    listing = session_store.list_all()
    ids = {s["research_id"] for s in listing}
    assert {"rid_a", "rid_b"} == ids
    scores = {s["research_id"]: s["final_score"] for s in listing}
    assert scores["rid_a"] == 7.0
    assert scores["rid_b"] == 9.0


def test_count():
    assert session_store.count() == 0
    session_store.save_session("rid_c", _make_state("rid_c"))
    assert session_store.count() == 1


def test_overwrite():
    session_store.save_session("rid_x", _make_state("rid_x", "Old topic"))
    state2 = _make_state("rid_x", "New topic")
    session_store.save_session("rid_x", state2)
    record = session_store.get_session("rid_x")
    assert record["topic"] == "New topic"
    assert session_store.count() == 1


def test_thread_safety():
    """Concurrent saves should not raise or lose data."""
    errors = []

    def save(i):
        try:
            session_store.save_session(f"rid_{i}", _make_state(f"rid_{i}"))
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=save, args=(i,)) for i in range(50)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
    assert session_store.count() == 50
