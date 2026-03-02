"""
FastAPI Server
==============

Exposes the iterative research pipeline over HTTP with Server-Sent Events (SSE)
so the Next.js frontend can stream live progress updates and the final report.

Run with:
    uvicorn main:app --reload --port 8000
"""

import asyncio
import json
import queue
import sys
import threading
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from iterative_research import run_iterative_research

app = FastAPI(title="Autonomous Research Platform API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResearchRequest(BaseModel):
    topic: str = Field(..., min_length=3, description="Research topic to investigate")
    quality_threshold: float = Field(7.5, ge=1.0, le=10.0, description="Minimum quality score (1-10)")
    max_iterations: int = Field(3, ge=1, le=5, description="Maximum improvement iterations")


class QueueWriter:
    """Captures stdout and routes it to a queue as SSE progress events."""

    def __init__(self, msg_queue: queue.Queue):
        self._queue = msg_queue

    def write(self, text: str):
        text = text.strip()
        if text:
            self._queue.put({"type": "progress", "message": text})

    def flush(self):
        pass


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/research")
async def research_stream(request: ResearchRequest):
    """
    Run iterative research and stream progress + final result via SSE.

    SSE event types:
      - progress  {"type": "progress", "message": "..."}   live stdout lines
      - result    {"type": "result", "summary": "...", "quality_history": [...], "iterations": N}
      - error     {"type": "error", "message": "..."}
    """

    msg_queue: queue.Queue = queue.Queue()

    def run_in_thread():
        original_stdout = sys.stdout
        sys.stdout = QueueWriter(msg_queue)
        try:
            state = run_iterative_research(
                topic=request.topic,
                quality_threshold=request.quality_threshold,
                max_iterations=request.max_iterations,
            )
            msg_queue.put({
                "type": "result",
                "summary": state["summary"],
                "quality_history": state["quality_history"],
                "iterations": state["iteration"],
                "improvement_history": state["improvement_history"],
            })
        except Exception as exc:
            msg_queue.put({"type": "error", "message": str(exc)})
        finally:
            sys.stdout = original_stdout
            msg_queue.put(None)  # sentinel — signals stream end

    async def generate() -> AsyncGenerator:
        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()

        while True:
            try:
                item = msg_queue.get_nowait()
            except queue.Empty:
                await asyncio.sleep(0.05)
                continue

            if item is None:
                break

            yield {"data": json.dumps(item)}

        thread.join(timeout=5)

    return EventSourceResponse(generate())
