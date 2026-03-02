# Autonomous Research Platform

An AI-powered research platform that autonomously searches the web, builds a vector knowledge base, and iteratively improves its own research reports using self-critique.

## Architecture

```
browser  →  Next.js (frontend/)  →  FastAPI (backend/)
                  ↓                        ↓
            /api/research           Tavily · Pinecone
            (SSE proxy)             Voyage AI · Claude
```

**Flow:** User enters a topic → Claude generates research questions → Tavily searches the web → content is chunked and stored in Pinecone (Voyage AI embeddings) → hybrid search retrieves relevant chunks → Claude synthesises a report → Claude scores the report → if quality < 7.5/10, the critique agent generates follow-up questions and the loop repeats (up to 3 iterations).

## Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 (App Router), shadcn/ui, Tailwind CSS |
| Backend | Python, FastAPI, SSE streaming |
| LLM | Anthropic Claude (claude-sonnet-4-20250514) |
| Web search | Tavily |
| Vector DB | Pinecone (serverless) |
| Embeddings | Voyage AI (voyage-3, 1024d) |
| Reranking | Cohere (optional) |

## Setup

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your API keys:

```
ANTHROPIC_API_KEY=...
TAVILY_API_KEY=...
PINECONE_API_KEY=...
VOYAGE_API_KEY=...
COHERE_API_KEY=...   # optional — enables reranking
```

Start the API server:

```bash
uvicorn main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local   # edit if backend is not on :8000
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Usage

1. Type a research topic in the chat input and press **Enter** or click **Research**
2. Watch live progress as the AI searches and builds the knowledge base
3. Receive a structured markdown report with a quality score (0–10) and iteration history
4. Start a new research session with the **New research** button

## Project Structure

```
autonomous-research-platform/
├── backend/
│   ├── main.py                    # FastAPI server (entry point)
│   ├── iterative_research.py      # Main research loop
│   ├── research_tools.py          # Tavily web search
│   ├── vector_store.py            # Pinecone + Voyage AI
│   ├── quality_scorer.py          # Claude-based quality scoring
│   ├── critique_agent.py          # Self-critique + follow-up questions
│   ├── day3_advanced_rag_agent.py # Planning agent + advanced RAG
│   └── requirements.txt
└── frontend/
    ├── app/
    │   ├── chat/page.tsx          # Chat page
    │   └── api/research/route.ts  # SSE proxy to FastAPI
    ├── components/
    │   ├── chat-interface.tsx     # Top-level layout
    │   ├── chat-input.tsx         # Input bar
    │   ├── message-list.tsx       # Scrollable message list
    │   ├── message-item.tsx       # Individual message bubble
    │   ├── research-progress.tsx  # Live progress terminal
    │   └── quality-badge.tsx      # Score + iteration display
    ├── hooks/
    │   └── use-research.ts        # SSE streaming hook
    └── lib/
        └── types.ts               # TypeScript types
```
