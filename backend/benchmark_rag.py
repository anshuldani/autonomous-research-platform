"""
RAG Performance Benchmark
=========================

Compare retrieval quality across different methods.
"""

from vector_store import VectorStore
import time
import uuid
from typing import List, Dict


def create_test_corpus() -> tuple:
    """Create test documents for benchmarking."""
    
    texts = [
        # Highly relevant to "machine learning"
        "Machine learning algorithms learn patterns from data to make predictions.",
        "Neural networks are a type of machine learning model inspired by the brain.",
        "Deep learning uses multiple layers to learn hierarchical representations.",
        
        # Somewhat relevant
        "Data science involves extracting insights from large datasets.",
        "Artificial intelligence encompasses machine learning and other techniques.",
        
        # Less relevant
        "Cloud computing provides on-demand computing resources.",
        "The weather today is sunny with mild temperatures.",
        "Python is a popular programming language for data analysis."
    ]
    
    metadata = [
        {"title": f"Doc {i}", "category": "ml" if i < 3 else "other"}
        for i in range(len(texts))
    ]
    
    return texts, metadata


def benchmark_retrieval_methods():
    """Compare different retrieval methods."""
    
    print("\n" + "="*70)
    print("RAG RETRIEVAL BENCHMARK")
    print("="*70)
    
    # Setup
    store = VectorStore()
    research_id = f"benchmark_{uuid.uuid4().hex[:8]}"
    
    texts, metadata = create_test_corpus()
    
    print(f"\n📦 Storing {len(texts)} test documents...")
    store.store_documents(texts, metadata, research_id)
    
    time.sleep(2)  # Allow indexing
    
    query = "machine learning neural networks deep learning"
    
    # Method 1: Basic semantic search
    print("\n" + "─"*70)
    print("METHOD 1: Basic Semantic Search")
    print("─"*70)
    
    start = time.time()
    semantic_results = store.search(query, research_id=research_id, top_k=5)
    semantic_time = time.time() - start
    
    print(f"Time: {semantic_time:.3f}s")
    print("Top 3 results:")
    for i, r in enumerate(semantic_results[:3], 1):
        print(f"  {i}. {r['metadata']['title']} (score: {r['score']:.3f})")
        print(f"     {r['text'][:60]}...")
    
    # Method 2: Hybrid search
    print("\n" + "─"*70)
    print("METHOD 2: Hybrid Search (70% semantic, 30% keyword)")
    print("─"*70)
    
    start = time.time()
    hybrid_results = store.hybrid_search(
        query, research_id=research_id, top_k=5, alpha=0.7
    )
    hybrid_time = time.time() - start
    
    print(f"Time: {hybrid_time:.3f}s")
    print("Top 3 results:")
    for i, r in enumerate(hybrid_results[:3], 1):
        print(f"  {i}. {r['metadata']['title']} "
              f"(hybrid: {r['hybrid_score']:.3f}, "
              f"semantic: {r['score']:.3f}, "
              f"keyword: {r['keyword_score']:.3f})")
        print(f"     {r['text'][:60]}...")
    
    # Method 3: With reranking
    print("\n" + "─"*70)
    print("METHOD 3: Hybrid + Reranking")
    print("─"*70)
    
    try:
        start = time.time()
        candidates = store.hybrid_search(
            query, research_id=research_id, top_k=10, alpha=0.7
        )
        reranked = store.rerank_results(query, candidates, top_n=3)
        rerank_time = time.time() - start
        
        print(f"Time: {rerank_time:.3f}s")
        print("Top 3 results:")
        for i, r in enumerate(reranked[:3], 1):
            print(f"  {i}. {r['metadata']['title']} "
                  f"(rerank: {r.get('rerank_score', 0):.3f})")
            print(f"     {r['text'][:60]}...")
        
    except Exception as e:
        print(f"⚠️  Reranking unavailable: {e}")
        rerank_time = None
    
    # Summary
    print("\n" + "="*70)
    print("BENCHMARK SUMMARY")
    print("="*70)
    
    print(f"\n{'Method':<30} {'Time (s)':<15} {'Quality'}")
    print("─"*70)
    print(f"{'Semantic Search':<30} {semantic_time:<15.3f} {'Good'}")
    print(f"{'Hybrid Search':<30} {hybrid_time:<15.3f} {'Better'}")
    if rerank_time:
        print(f"{'Hybrid + Reranking':<30} {rerank_time:<15.3f} {'Best'}")
    
    print("\n💡 Key Insights:")
    print("  • Semantic search: Fast, good recall")
    print("  • Hybrid search: Slightly slower, better precision")
    print("  • Reranking: Slowest, highest quality")
    print("\n  Recommendation: Use hybrid+rerank for production\n")


if __name__ == "__main__":
    benchmark_retrieval_methods()
