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
│   ├── day3_advanced_rag_agent.py  # Planning agent (Haiku) — generates 3 research questions
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

## Key learnings

### Multi-agent architecture
- Breaking a complex pipeline into **small, single-responsibility agents** (plan → search → synthesise → score → critique) makes each step independently testable and replaceable. The quality scorer doesn't need to know how synthesis works.
- **Model tiering** matters: using Haiku for structured, deterministic tasks (planning, critique) and Sonnet only for open-ended generation cuts latency and cost significantly without hurting output quality.

### Retrieval-Augmented Generation (RAG)
- **Chunking strategy** has a bigger impact on retrieval quality than embedding model choice. Overlapping chunks with a consistent size prevent context being split at awkward boundaries.
- **Hybrid search** (dense vector + sparse keyword) consistently outperforms pure semantic search on factual queries where exact terms matter.
- **Reranking** (Cohere) as a final pass over retrieved chunks noticeably improves the coherence of follow-up answers — it's a cheap quality boost worth adding.
- Storing embeddings in Pinecone **in a background thread** during research means the vector index is ready by the time the user asks their first follow-up question.

### Streaming and perceived performance
- The biggest UX win wasn't making the pipeline faster — it was **streaming progress updates** to the user so the 30–90 second wait felt active rather than frozen. Real latency and perceived latency are very different problems.
- SSE (Server-Sent Events) is significantly simpler than WebSockets for one-way server-to-client streaming. It works natively in browsers, survives proxy timeouts with keepalive pings, and needs no special infrastructure.
- The **"washing machine" UX principle**: users tolerate slow processes when they can see meaningful progress. Showing step names and timings (planning: 1.4s, searching: 3.2s…) is more reassuring than a generic spinner.

### API design and cost
- Parallelising web searches increases throughput but scales cost **linearly** — N parallel searches = N× API spend. For a production system, staying sequential unless there's a hard latency requirement is the operationally safer default.
- **Never bake runtime config into build artefacts.** The `BACKEND_URL` must be resolved at request time (via `process.env` in a route handler), not at `next build` time — otherwise every environment change requires a redeploy.

### Deployment
- FastAPI + Railway + Vercel is a clean separation: Railway handles the long-running Python process (with SSE keepalive), Vercel handles the static Next.js frontend. The only connection between them is the `BACKEND_URL` env var.
- CORS must explicitly allow the production Vercel origin — `*` doesn't work with credentialed requests, and missing this causes silent failures that look like backend errors.
- Vercel's hobby plan has a **300-second function timeout** — critical for SSE endpoints that can run 90+ seconds per research job.

### Testing strategy
- Mocking at the API-client level (patching `anthropic.Anthropic`, `TavilyClient`, etc.) gives fast, reliable unit tests with no API keys required. Integration tests with real APIs are reserved for pre-deploy smoke tests.
- 10 unit tests covering the research loop and tool wrappers caught multiple regressions during refactoring at zero cost.

---

## Notes

- **Pinecone index**: must be created manually before first run. Name: `research-platform`, dimensions: `1024`, metric: `cosine`, cloud: any serverless region.
- **Follow-up chat context**: Pinecone is populated in a background thread during research. If you ask a follow-up question immediately after research completes, the first answer may have limited context — wait a few seconds.
- **Quality threshold**: the pipeline retries until the score meets the threshold or `max_iterations` is exhausted. Lowering the threshold (e.g. `6.0`) speeds up delivery; raising it (e.g. `9.0`) forces more refinement passes.
