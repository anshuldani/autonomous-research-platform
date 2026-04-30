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
import os
import queue
import sys
import threading
from typing import AsyncGenerator, List, Optional

from anthropic import Anthropic
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from iterative_research import run_iterative_research

app = FastAPI(title="Autonomous Research Platform API", version="1.0.0")

_CORS_ORIGINS = [
    "http://localhost:3000",  # local dev
    "https://autonomous-research-platform.vercel.app",  # production
]

# Allow all origins in Railway preview deployments via env var
_extra_origin = os.getenv("CORS_ORIGIN")
if _extra_origin:
    _CORS_ORIGINS.append(_extra_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Lazy singleton — initialized on first /api/chat request so the
# research endpoint still works even if Pinecone keys are missing.
_vector_store = None
_vector_store_lock = threading.Lock()


def get_vector_store():
    global _vector_store
    if _vector_store is None:
        with _vector_store_lock:
            if _vector_store is None:
                from vector_store import VectorStore
                _vector_store = VectorStore()
    return _vector_store


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class ResearchRequest(BaseModel):
    topic: str = Field(..., min_length=3, description="Research topic to investigate")
    quality_threshold: float = Field(7.5, ge=1.0, le=10.0, description="Minimum quality score (1-10)")
    max_iterations: int = Field(2, ge=1, le=5, description="Maximum improvement iterations")


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    research_id: str
    messages: List[ChatMessage]


# ---------------------------------------------------------------------------
# Research endpoint helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Research SSE endpoint
# ---------------------------------------------------------------------------

@app.post("/api/research")
async def research_stream(request: ResearchRequest):
    """
    Run iterative research and stream progress + final result via SSE.

    SSE event types:
      - progress  {"type": "progress", "message": "..."}   live stdout lines
      - result    {"type": "result", "summary": "...", "quality_history": [...], "iterations": N,
                   "sources": [...], "research_id": "..."}
      - error     {"type": "error", "message": "..."}
    """

    msg_queue: queue.Queue = queue.Queue()

    def run_in_thread():
        original_stdout = sys.stdout
        sys.stdout = QueueWriter(msg_queue)
        try:
            def on_synthesis_token(text):
                if text is None:
                    msg_queue.put({"type": "synthesis_start"})
                else:
                    msg_queue.put({"type": "synthesis_token", "text": text})

            state = run_iterative_research(
                topic=request.topic,
                quality_threshold=request.quality_threshold,
                max_iterations=request.max_iterations,
                on_synthesis_token=on_synthesis_token,
            )
            msg_queue.put({
                "type": "result",
                "summary": state["summary"],
                "quality_history": state["quality_history"],
                "iterations": state["iteration"],
                "improvement_history": state["improvement_history"],
                "sources": state["sources"],
                "research_id": state["research_id"],
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


# ---------------------------------------------------------------------------
# Chat follow-up endpoint
# ---------------------------------------------------------------------------

def retrieve_chat_context(research_id: str, query: str, top_k: int = 10) -> str:
    """Embed query and retrieve top-k chunks from Pinecone for research_id."""
    vs = get_vector_store()
    results = vs.search_with_filters(
        query=query,
        research_id=research_id,
        top_k=top_k,
    )
    if not results:
        return ""
    parts = []
    for i, r in enumerate(results, 1):
        title = r["metadata"].get("title", "Source")
        url = r["metadata"].get("url", "")
        text = r["text"]
        source_line = f"[{i}] {title}" + (f" ({url})" if url else "")
        parts.append(f"{source_line}\n{text}")
    return "\n\n---\n\n".join(parts)


async def generate_chat(request: ChatRequest) -> AsyncGenerator:
    """Async generator that streams Claude tokens for a follow-up chat."""
    if not request.messages:
        yield {"data": json.dumps({"type": "error", "message": "No messages provided"})}
        return

    last_user_msg = next(
        (m.content for m in reversed(request.messages) if m.role == "user"),
        None,
    )
    if not last_user_msg:
        yield {"data": json.dumps({"type": "error", "message": "No user message found"})}
        return

    # Retrieve RAG context in a thread (Pinecone calls are blocking)
    try:
        loop = asyncio.get_running_loop()
        context = await loop.run_in_executor(
            None,
            retrieve_chat_context,
            request.research_id,
            last_user_msg,
        )
    except Exception as exc:
        yield {"data": json.dumps({"type": "error", "message": f"Context retrieval failed: {exc}"})}
        return

    system_prompt = (
        "You are a knowledgeable research assistant. "
        "Answer the user's question based on the research context below. "
        "Be concise, accurate, and cite specific details from the context when relevant. "
        "If the context does not contain enough information, say so and provide your best general answer.\n\n"
    )
    if context:
        system_prompt += f"## Research Context\n\n{context}"
    else:
        system_prompt += (
            "No stored research chunks were found for this session. "
            "Answer based on your general knowledge."
        )

    # Build messages list for Claude (exclude system from messages array)
    claude_messages = [
        {"role": m.role, "content": m.content}
        for m in request.messages
    ]

    # Stream tokens from Claude
    try:
        with anthropic_client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=system_prompt,
            messages=claude_messages,
        ) as stream:
            for text in stream.text_stream:
                yield {"data": json.dumps({"type": "token", "text": text})}
                await asyncio.sleep(0)  # yield control to event loop
    except Exception as exc:
        yield {"data": json.dumps({"type": "error", "message": str(exc)})}
        return

    yield {"data": json.dumps({"type": "done"})}


@app.post("/api/chat")
async def chat_stream(request: ChatRequest):
    """
    Stream Claude follow-up chat grounded in the stored Pinecone research.

    SSE event types:
      - token   {"type": "token", "text": "..."}
      - done    {"type": "done"}
      - error   {"type": "error", "message": "..."}
    """
    if not request.research_id:
        raise HTTPException(status_code=400, detail="research_id is required")

    return EventSourceResponse(generate_chat(request))
