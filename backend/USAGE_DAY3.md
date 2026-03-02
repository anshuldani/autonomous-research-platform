# Day 3: RAG Usage Guide

Complete guide to using the RAG-enhanced research platform.

## Quick Start

### Basic RAG
```python
from day3_rag_agent import run_research

result = run_research("Advances in quantum computing")

print(f"Summary: {result['summary']}")
print(f"Chunks stored: {result['stored_chunks']}")
```

### Advanced RAG (Recommended)
```python
from day3_advanced_rag_agent import run_advanced_research

result = run_advanced_research("Climate change mitigation strategies")

print(f"Quality score: {result['quality_metrics']['avg_rerank_score']:.3f}")
print(f"Method: {result['retrieval_method']}")
```

## Vector Store Direct Usage

### Store Documents
```python
from vector_store import VectorStore

store = VectorStore()

texts = [
    "Long article about AI...",
    "Research paper on ML..."
]
metadata = [
    {"title": "AI Article", "url": "https://..."},
    {"title": "ML Paper", "url": "https://..."}
]

store.store_documents(texts, metadata, research_id="my_research")
```

### Semantic Search
```python
# Simple semantic search
results = store.search(
    query="machine learning applications",
    research_id="my_research",
    top_k=5
)

for r in results:
    print(f"{r['score']:.3f}: {r['text'][:100]}...")
```

### Hybrid Search
```python
# Better retrieval quality
results = store.hybrid_search(
    query="deep learning neural networks",
    research_id="my_research",
    top_k=10,
    alpha=0.7  # 70% semantic, 30% keyword
)
```

### With Reranking
```python
# Best quality (requires Cohere API key)
candidates = store.hybrid_search(query, research_id="my_research", top_k=20)
best_results = store.rerank_results(query, candidates, top_n=5)

for r in best_results:
    print(f"Rerank score: {r['rerank_score']:.3f}")
    print(f"Title: {r['metadata']['title']}")
```

## Advanced Features

### Metadata Filtering
```python
# Filter by source type
results = store.search_with_filters(
    query="quantum computing",
    research_id="my_research",
    filters={"source_type": "academic", "score": {"$gte": 0.9}}
)
```

### Batch Processing
```python
# For large document sets
store.store_documents_batch(
    texts=large_text_list,
    metadata=large_metadata_list,
    research_id="big_research",
    batch_size=10  # Process 10 at a time
)
```

### Index Statistics
```python
# Monitor your vector database
stats = store.get_index_stats()
count = store.count_research_documents("my_research")

print(f"Total vectors: {stats['total_vector_count']}")
print(f"This research: {count} chunks")
```

## Configuration

### Chunking Strategy
```python
# Customize chunk size
store.chunk_text(
    text=long_document,
    chunk_size=1000,  # Words per chunk
    overlap=100       # Overlap between chunks
)
```

### Search Parameters
```python
# Fine-tune hybrid search
results = store.hybrid_search(
    query="your query",
    alpha=0.5,  # 50-50 semantic/keyword
    top_k=15
)
```

## Best Practices

### 1. Research Session Management
Always use unique research_ids:
```python
import uuid

research_id = f"research_{uuid.uuid4().hex[:8]}"
```

### 2. Error Handling
```python
try:
    results = store.search(query, research_id=research_id)
except Exception as e:
    print(f"Search failed: {e}")
    # Fallback logic
```

### 3. Quality Monitoring
Track rerank scores:
```python
if result.get('rerank_scores'):
    avg_score = sum(result['rerank_scores']) / len(result['rerank_scores'])
    if avg_score < 0.5:
        print("⚠️ Low quality retrieval, consider refining query")
```

### 4. Batch Size Tuning
For rate limits:
```python
# Slower but safer
store.store_documents_batch(texts, metadata, research_id, batch_size=5)

# Faster (if rate limits allow)
store.store_documents_batch(texts, metadata, research_id, batch_size=20)
```

## Troubleshooting

### Rate Limit Errors
- Add payment method to Voyage AI for 300 RPM
- Use `vector_store_retry.py` for automatic retries
- Reduce batch sizes

### Low Quality Results
1. Try hybrid search instead of pure semantic
2. Add reranking
3. Increase top_k to get more candidates
4. Check if documents are properly chunked

### Slow Performance
- Use batch processing for large uploads
- Enable reranking only when quality is critical
- Monitor Pinecone index size

## Example Workflows

### Research Pipeline
```python
# 1. Research topic
result = run_advanced_research("AI in healthcare")

# 2. Query stored knowledge
store = VectorStore()
followup = store.hybrid_search(
    "What about diagnostic applications?",
    research_id=result['research_id']
)

# 3. Get specific info
best = store.rerank_results(
    "FDA approved AI diagnostic tools",
    followup,
    top_n=3
)
```

### Document Q&A
```python
# Store documents
store.store_documents(
    texts=pdf_contents,
    metadata=pdf_metadata,
    research_id="company_docs"
)

# Ask questions
answer_chunks = store.hybrid_search(
    "What is our refund policy?",
    research_id="company_docs",
    alpha=0.8
)
```

## Performance Tips

1. **Pre-filter with metadata** before semantic search
2. **Use hybrid search** for production (better recall)
3. **Rerank only top candidates** (not all results)
4. **Batch embed** when possible (faster than one-by-one)
5. **Monitor quality metrics** to tune parameters

## API Reference

See inline documentation in:
- `vector_store.py` - All vector operations
- `day3_rag_agent.py` - Basic RAG workflow
- `day3_advanced_rag_agent.py` - Production RAG

---

**Questions?** Check the test files for more examples!
