# Follow-up tickets

Open these manually when ready — each is real backlog, not made-up scope.

## 1. Backend README still references `day3_advanced_rag_agent.py`

`backend/README.md` lists `day3_advanced_rag_agent.py` in its key-files
table. The file was renamed to `planning_agent.py` (commit `3d6e76d`) and
all imports/tests were updated, but the README's table didn't get touched.
One-line fix.

## 2. Module-level Anthropic / Pinecone clients defeat lazy import

`iterative_research.py`, `research_tools.py`, and `vector_store.py` each
instantiate API clients at import time:

```python
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
tools = ResearchTools()
vector_store = VectorStore()
```

Importing the module without env vars raises immediately. That breaks
unit-testing anything that touches these modules (the tests currently
work around it by monkey-patching env). Move client construction into
the functions that use them, or pass them in via dependency injection.

## 3. SSE pipeline has no client-disconnect handling

`main.py`'s SSE generators run to completion even if the browser tab is
closed. On a 90-second pipeline that's a real waste of API budget.
Wrap the generator with `if await request.is_disconnected(): break`
checks at each pipeline step.

## 4. Pinecone metadata cap is now 1500 chars, but no truncation guard

Commit `cc13854` raised the per-chunk metadata length from 200 to 1500
chars. Pinecone's hard cap is 40 KB per record total. If a chunk is
>1500 chars (e.g. a single long sentence from a 10-K), it's silently
truncated. Add a `len(text) > 1500` guard and split chunks instead of
truncating mid-sentence.

## 5. Hybrid-search alpha is hardcoded

`vector_store.py` uses a fixed alpha to blend dense vs. sparse scores.
The README calls this out as "tunable" but there's no actual knob — the
value is a constant in code. Either expose it via the API request body
or read from env. Even just a config dict at the top of the module
would be a step up.
