# Backend

FastAPI server for the Autonomous Research Platform.

See the [root README](../README.md) for full setup instructions, architecture overview, and API reference.

## Quick start

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in API keys
uvicorn main:app --reload --port 8000
```

## Key files

| File | Purpose |
|---|---|
| `main.py` | FastAPI app — `/api/research` and `/api/chat` SSE endpoints |
| `iterative_research.py` | Core research loop |
| `day3_advanced_rag_agent.py` | Planning agent |
| `research_tools.py` | Tavily web search |
| `vector_store.py` | Pinecone + Voyage AI |
| `quality_scorer.py` | Claude-based quality scoring |
| `critique_agent.py` | Self-critique and follow-up generation |

## Tests

```bash
pytest tests/test_research_tools.py tests/test_iterative.py -v
```
