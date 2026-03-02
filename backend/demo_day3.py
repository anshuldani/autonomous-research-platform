"""
Day 3 Quick Demo
================

Quick demonstration of RAG capabilities.
"""

from day3_advanced_rag_agent import run_advanced_research
from vector_store import VectorStore
import time


def demo_rag_features():
    """Demonstrate RAG features step by step."""
    
    print("\n" + "="*70)
    print("DAY 3 RAG FEATURES DEMO")
    print("="*70)
    
    topic = "Breakthroughs in battery technology for electric vehicles"
    
    print(f"\n📚 Topic: {topic}")
    print("\nThis demo will show:")
    print("  1. Web search + Vector storage")
    print("  2. Hybrid semantic search")
    print("  3. Reranking for quality")
    print("  4. Claude synthesis")
    
    input("\nPress Enter to start...")
    
    # Run research
    print("\n" + "─"*70)
    print("STEP 1: Running Advanced RAG Research")
    print("─"*70)
    
    start = time.time()
    result = run_advanced_research(topic)
    elapsed = time.time() - start
    
    print(f"\n✅ Research complete in {elapsed:.1f}s")
    
    # Show results
    print("\n" + "─"*70)
    print("STEP 2: Research Results")
    print("─"*70)
    
    print(f"\nResearch ID: {result['research_id']}")
    print(f"\nQuestions generated: {len(result['research_questions'])}")
    for i, q in enumerate(result['research_questions'], 1):
        print(f"  {i}. {q}")
    
    print(f"\nChunks stored in vector DB: {result['stored_chunks']}")
    print(f"Retrieval method: {result['retrieval_method']}")
    
    if result.get('rerank_scores'):
        avg_score = result['quality_metrics']['avg_rerank_score']
        print(f"Average rerank score: {avg_score:.3f} (higher = better)")
    
    print("\n" + "─"*70)
    print("STEP 3: Query the Knowledge Base")
    print("─"*70)
    
    # Demonstrate querying
    store = VectorStore()
    
    followup_query = "What are the latest solid-state battery developments?"
    print(f"\nFollowup query: {followup_query}")
    
    print("\nSearching stored knowledge...")
    results = store.hybrid_search(
        followup_query,
        research_id=result['research_id'],
        alpha=0.7
    )
    
    print(f"\nFound {len(results)} relevant chunks:")
    for i, r in enumerate(results[:3], 1):
        print(f"\n  {i}. Score: {r['hybrid_score']:.3f}")
        print(f"     {r['text'][:100]}...")
    
    print("\n" + "─"*70)
    print("STEP 4: Generated Summary")
    print("─"*70)
    
    print(f"\n{result['summary']}\n")
    
    print("="*70)
    print("DEMO COMPLETE! 🎉")
    print("="*70)
    
    print("\n💡 Key Takeaways:")
    print("  ✅ RAG stores knowledge for future queries")
    print("  ✅ Hybrid search improves retrieval quality")
    print("  ✅ Reranking ensures best chunks are used")
    print("  ✅ Can query stored knowledge anytime")
    
    print(f"\n📊 Your research is saved as: {result['research_id']}")
    print("   You can query it again anytime!\n")


if __name__ == "__main__":
    demo_rag_features()
