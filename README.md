# Autonomous Research Platform

Give it a topic. In 30–90 seconds it plans targeted search queries, searches the live web in parallel, synthesises a 600+ word structured report, scores the quality on four dimensions, and self-critiques and reruns if the score is below threshold — all without any human input.

When research finishes, the full source set is embedded and stored in Pinecone. You can then ask follow-up questions answered directly from that knowledge base via RAG.

**Live demo:** [autonomous-research-platform.vercel.app](https://autonomous-research-platform.vercel.app)

---

## Why this is hard

Getting a research agent to produce a genuinely useful report — not just a padded summary — requires solving three separate problems at once.

**Quality control without ground truth.** There's no reference answer to compare against. The solution here is a Claude-based quality scorer that evaluates depth, relevance, clarity, and coverage independently (0–10 each), then feeds low scores back into a critique agent that generates specific follow-up questions. This loop converges in 1–2 iterations on most topics without manual intervention.

**RAG retrieval that actually works.** Pure semantic search fails on factual queries where exact terms matter — "what was the ROIC in Q3" retrieves irrelevant chunks if the query and the chunk use different phrasing. The fix is hybrid search: dense vector similarity plus sparse keyword matching with a tunable alpha, plus a Cohere reranker as a final pass. Each piece contributes independently; together they make follow-up answers meaningfully better.

**Streaming a 30–90 second pipeline.** The user can't stare at a spinner for 90 seconds. Server-Sent Events stream progress updates at each pipeline step (planning: 1.4s, searching: 3.2s…). Pinecone embedding runs in a background thread during synthesis so the vector index is ready before the user finishes reading the report.

---

## How it works

```
User enters topic
      │
      ▼
Planning Agent (Haiku)
  └─ generates 3 targeted research questions
      │
      ▼
Parallel Web Search (Tavily × 3 simultaneous)
  └─ basic search + AI-synthesised answer per query
      │
      ├──────────────────────────────────────────────┐
      ▼                                              ▼
Synthesis (Sonnet 4.6)                    Background: embed + store in
  └─ 600+ word structured report               Pinecone via Voyage AI
       grounded in raw search results          (for follow-up RAG chat)
      │
      ▼
Quality Scoring (Sonnet 4.6)
  └─ scores depth / relevance / clarity / coverage (0–10)
      │
      ├── score ≥ 7.5 ──► deliver report
      │
      └── score < 7.5 ──► Critique Agent (Haiku)
                               └─ generates follow-up questions
                                    └─ repeat (max 2 iterations total)
```

Once research is complete, the **follow-up chat** queries Pinecone with the user's question, retrieves the top-10 most relevant chunks, and streams a Claude answer grounded in that context.

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16 (App Router), Tailwind CSS v4, shadcn/ui |
| Backend | Python 3.12, FastAPI, SSE streaming |
| Research LLM | Claude Sonnet 4.6 (synthesis + scoring) |
| Planning / Critique | Claude Haiku 4.5 (faster, structured tasks) |
| Web search | Tavily (basic depth, parallel queries) |
| Vector DB | Pinecone serverless |
| Embeddings | Voyage AI (voyage-3, 1024-dim) |
| Reranking | Cohere (optional — improves follow-up chat) |
| Frontend deploy | Vercel |
| Backend deploy | Railway |

---

## Deployment

| Service | URL |
|---|---|
| Frontend (Vercel) | [autonomous-research-platform.vercel.app](https://autonomous-research-platform.vercel.app) |
| Backend (Railway) | Set `BACKEND_URL` env var in Vercel to your Railway service URL |

### Environment variables

**Backend (Railway)**
```env
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...
PINECONE_API_KEY=pcsk_...
VOYAGE_API_KEY=pa-...
COHERE_API_KEY=           # optional
```

**Frontend (Vercel)**
```env
BACKEND_URL=https://your-railway-service.up.railway.app
```

---

## MCP Server (Claude Desktop)

Run the research pipeline directly inside Claude Desktop — no web UI required.

### Install

```bash
# From the project root, using the same venv as the backend
pip install "mcp>=1.0.0"
```

### Configure Claude Desktop

Merge the following into `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "autonomous-research": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/path/to/autonomous-research-platform",
      "env": {
        "ANTHROPIC_API_KEY": "...",
        "TAVILY_API_KEY": "...",
        "PINECONE_API_KEY": "...",
        "VOYAGE_API_KEY": "...",
        "COHERE_API_KEY": ""
      }
    }
  }
}
```

A ready-to-edit copy lives at `mcp_server/claude_desktop_config.json`.

### Available tools

| Tool | Description |
|---|---|
| `ping` | Health check — returns `"pong"` |
| `run_research` | Full pipeline: plan → search → synthesise → critique loop. Returns `research_id` + report JSON. |
| `search_research` | Semantic search over a stored session via Pinecone |
| `hybrid_search_research` | Hybrid semantic + keyword search (tunable `alpha`) |
| `score_research` | Claude-based quality scorer (0-10) on any summary |
| `list_sessions` | List all research sessions in the current process |
| `get_session_report` | Full stored report for a `research_id` |
| `get_session_stats` | Chunk count + Pinecone index size for a session |

### Available resources

| URI | Description |
|---|---|
| `research://sessions` | All in-process sessions (JSON) |
| `research://{id}/report` | Markdown report for a session |
| `research://{id}/sources` | Top sources JSON |
| `research://{id}/quality` | Quality history across iterations |

### Available prompts

| Prompt | Description |
|---|---|
| `research_briefing` | Primes a conversation with a stored report for RAG Q&A |
| `research_planning` | Generates targeted research questions for a topic |
| `research_critique` | Structured critique of any summary |

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- API keys for: Anthropic, Tavily, Pinecone, Voyage AI
- A Pinecone **serverless index** named `research-platform` (dimension: 1024, metric: cosine)

---

## Setup

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copy the env template and fill in your keys:

```bash
cp .env.example .env
```

```env
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...
PINECONE_API_KEY=pcsk_...
VOYAGE_API_KEY=pa-...
COHERE_API_KEY=           # optional — leave blank to skip reranking
```

Start the API server:

```bash
uvicorn main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000/chat](http://localhost:3000/chat).

> The frontend proxies API calls to `http://localhost:8000`. If your backend runs on a different port, set `NEXT_PUBLIC_API_URL` in `frontend/.env.local`.

---

## Usage

1. Open the app and enter a research topic (or click an example card)
2. The agent searches, synthesises, and scores — typically **30–90 seconds**
3. The full report appears in the chat thread with source citations
4. Click **"Chat about this"** to open the follow-up chat panel
5. Ask any question — answers are grounded in the stored research via RAG
6. Click **"+ New research"** in the header to start over

---

## Project structure

```
autonomous-research-platform/
│
├── backend/
│   ├── main.py                     # FastAPI server — /api/research and /api/chat SSE endpoints
│   ├── iterative_research.py       # Core research loop (plan → search → synthesise → score → refine)
│   ├── planning_agent.py           # Planning agent (Haiku) — generates 3 targeted research questions
│   ├── research_tools.py           # Tavily web search wrapper
│   ├── vector_store.py             # Pinecone + Voyage AI — chunk, embed, store, hybrid search
│   ├── quality_scorer.py           # Claude-based quality scoring (0–10 across 4 dimensions)
│   ├── critique_agent.py           # Self-critique — identifies gaps, generates follow-up questions
│   ├── requirements.txt
│   ├── .env.example
│   └── tests/
│       ├── test_research_tools.py  # Unit tests (no real APIs required)
│       └── test_iterative.py       # Unit tests (no real APIs required)
│
└── frontend/
    ├── app/
    │   ├── chat/page.tsx           # Main chat page
    │   ├── api/research/route.ts   # SSE proxy → FastAPI /api/research
    │   └── api/chat/route.ts       # SSE proxy → FastAPI /api/chat
    ├── components/
    │   ├── chat-interface.tsx      # Top-level layout — research vs chat mode switching
    │   ├── message-list.tsx        # Landing page + scrollable message thread
    │   ├── message-item.tsx        # Individual message bubble (user / assistant report)
    │   ├── chat-input.tsx          # Topic input bar
    │   ├── pinned-research.tsx     # Collapsible research card shown in chat mode
    │   ├── follow-up-panel.tsx     # Follow-up chat panel (uses useChat hook)
    │   ├── chat-thread.tsx         # Scrollable list of follow-up bubbles
    │   ├── chat-bubble.tsx         # Individual follow-up message bubble
    │   ├── follow-up-input.tsx     # Follow-up question input
    │   ├── citation-card.tsx       # Single source card (favicon + domain + title)
    │   └── citation-list.tsx       # Expandable source list below each report
    ├── hooks/
    │   ├── use-research.ts         # SSE streaming hook for research pipeline
    │   └── use-chat.ts             # SSE streaming hook for follow-up chat
    └── lib/
        └── types.ts                # Shared TypeScript types
```

---

## API reference

### `POST /api/research`

Run iterative research and stream progress + result.

**Request body:**
```json
{
  "topic": "CRISPR applications in medicine",
  "quality_threshold": 7.5,
  "max_iterations": 2
}
```

**SSE event stream:**
```
data: {"type": "progress", "message": "⏱  planning:  1.4s"}
data: {"type": "result", "summary": "...", "quality_history": [...], "iterations": 1, "sources": [...], "research_id": "iter_abc123"}
data: {"type": "error", "message": "..."}
```

### `POST /api/chat`

Stream a follow-up answer grounded in stored Pinecone research.

**Request body:**
```json
{
  "research_id": "iter_abc123",
  "messages": [
    {"role": "user", "content": "What were the main side effects mentioned?"}
  ]
}
```

**SSE event stream:**
```
data: {"type": "token", "text": "The main "}
data: {"type": "token", "text": "side effects..."}
data: {"type": "done"}
```

### `GET /health`

Returns `{"status": "ok"}`.

---

## Running tests

```bash
cd backend
source venv/bin/activate
pytest tests/test_research_tools.py tests/test_iterative.py -v
```

The unit tests mock all external APIs and run without any API keys.

---

## Results

| Metric | Observed |
|---|---|
| End-to-end research time | 30–90 seconds (depends on topic breadth) |
| Report length | 600–900 words, structured with headers |
| Typical quality score (first pass) | 6.5–8.2 / 10 |
| Iteration rate | ~35% of requests trigger a second pass |
| Follow-up answer latency | 3–6 seconds (includes Pinecone retrieval + reranking) |
| Unit test coverage | 10 tests, 0 real API calls required |

Quality scores above 7.5 are delivered immediately. Topics with ambiguous scope or sparse web coverage are most likely to trigger a critique loop.

---

## Engineering decisions

**Single-responsibility agents over monolithic pipeline.** Each step (plan, search, synthesise, score, critique) is an independent module with no knowledge of the others. This made the quality scorer trivially replaceable and let me test each stage in isolation with mocked dependencies.

**Model tiering for cost and latency.** Haiku handles all structured, deterministic tasks — planning and critique — where speed matters more than reasoning depth. Sonnet handles synthesis and scoring where output quality is load-bearing. This roughly halves per-request cost without a noticeable quality drop.

**Chunking strategy beats embedding model choice for RAG quality.** Overlapping fixed-size chunks with consistent boundaries outperform sentence-splitting approaches for this use case, where queries land mid-topic. The embedding model barely moved the needle once chunk boundaries were fixed.

**Hybrid search + reranking as the retrieval stack.** Dense vector search alone misses factual queries with exact-term dependencies. Adding sparse keyword matching (tunable alpha) and a Cohere reranker as a final pass produces consistently better follow-up answers. The reranker is an optional dependency — disabling it degrades quality but doesn't break anything.

**SSE over WebSockets for streaming.** SSE is simpler, works natively in browsers without special infrastructure, and survives proxy timeouts with keepalive pings. The only limitation — no client-to-server streaming — isn't needed here. For one-way server push, WebSockets add complexity with no benefit.

**Background embedding during synthesis.** Pinecone is populated while the synthesis LLM writes the report, not after it completes. The vector index is ready before the user finishes reading — no perceptible lag before the first follow-up question.

---

## Notes

**Pinecone index setup** — must be created before first run:
```
Name: research-platform | Dimensions: 1024 | Metric: cosine | Type: Serverless
```
Create it in the Pinecone console or via the API. Any serverless region works.

**Follow-up chat timing** — Pinecone is populated in a background thread during synthesis. If you ask a follow-up within the first 2–3 seconds after the report appears, the first answer may have limited context. Wait for the "Indexed N chunks" status message.

**Quality threshold tuning** — default is 7.5. Set lower (e.g. `6.0`) for faster delivery on broad topics; set higher (e.g. `9.0`) to force multiple refinement passes. Pass as `quality_threshold` in the API request body.
