# Autonomous Research Platform

An AI agent that takes a research topic, searches the live web, builds a private vector knowledge base, writes a structured report, self-critiques it, and iteratively improves the quality — all fully automated.

After research completes you can ask unlimited follow-up questions answered by Claude grounded in the stored knowledge base via RAG.

**Live demo:** [autonomous-research-platform.vercel.app](https://autonomous-research-platform.vercel.app)

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

## Notes

- **Pinecone index**: must be created manually before first run. Name: `research-platform`, dimensions: `1024`, metric: `cosine`, cloud: any serverless region.
- **Follow-up chat context**: Pinecone is populated in a background thread during research. If you ask a follow-up question immediately after research completes, the first answer may have limited context — wait a few seconds.
- **Quality threshold**: the pipeline retries until the score meets the threshold or `max_iterations` is exhausted. Lowering the threshold (e.g. `6.0`) speeds up delivery; raising it (e.g. `9.0`) forces more refinement passes.
