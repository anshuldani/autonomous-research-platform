"""
MCP Server Utilities
====================

Two critical concerns:
  1. All logging must go to stderr — MCP uses stdout for JSON-RPC wire protocol.
     Any stray print() to stdout corrupts the session.
  2. The backend is heavily instrumented with print() calls. Every tool call
     must redirect stdout to stderr for the duration of the backend invocation.
"""

import sys
import contextlib
from datetime import datetime


def log(msg: str) -> None:
    """Write a timestamped message to stderr (safe during MCP sessions)."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}", file=sys.stderr, flush=True)


class _StderrWriter:
    """Shim that forwards write() calls to stderr."""

    def write(self, text: str) -> None:
        text = text.strip()
        if text:
            print(f"[backend] {text}", file=sys.stderr, flush=True)

    def flush(self) -> None:
        pass


@contextlib.contextmanager
def redirect_stdout_to_stderr():
    """
    Context manager that routes all stdout from backend code to stderr.

    Usage::

        with redirect_stdout_to_stderr():
            run_iterative_research(...)
    """
    original = sys.stdout
    sys.stdout = _StderrWriter()
    try:
        yield
    finally:
        sys.stdout = original
