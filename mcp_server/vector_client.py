"""
Lazy VectorStore Singleton
===========================

VectorStore.__init__ connects to Pinecone and may create/wait on an index
(several seconds). We initialise it on the first RAG tool call — not at
server startup — so the server boots quickly even when Pinecone keys are
missing or only the research tool is being used.

Mirrors the pattern in backend/main.py's get_vector_store().
"""

import threading
import sys
import os

_vs = None
_vs_lock = threading.Lock()


def get_vector_store():
    """Return the shared VectorStore instance, initialising it on first call."""
    global _vs
    if _vs is None:
        with _vs_lock:
            if _vs is None:
                # backend/ must already be on sys.path (set by server.py)
                from vector_store import VectorStore
                _vs = VectorStore()
    return _vs
