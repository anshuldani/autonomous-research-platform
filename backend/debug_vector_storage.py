"""
Debug vector storage issues
"""

from vector_store import VectorStore
import time

store = VectorStore()

# Simple test without stats
research_id = "test_debug"

print("\n=== STORING TEST DOCS ===")
texts = ["CRISPR is used in medicine", "Gene editing treats diseases"]
metadata = [{"title": "Doc 1"}, {"title": "Doc 2"}]

store.store_documents(texts, metadata, research_id)

print("\n=== WAITING FOR INDEX (3 seconds)... ===")
time.sleep(3)

print("\n=== SEARCHING AFTER WAIT ===")
results = store.search("CRISPR medicine", research_id=research_id, top_k=5)

print(f"Found {len(results)} results")
for r in results:
    print(f"  - {r['text'][:50]}... (score: {r['score']:.3f})")

print("\n=== HYBRID SEARCH ===")
hybrid = store.hybrid_search("CRISPR medicine", research_id=research_id, top_k=5)
print(f"Found {len(hybrid)} results")
for r in hybrid:
    print(f"  - {r['text'][:50]}... (hybrid: {r.get('hybrid_score', 0):.3f})")

print("\n=== CONCLUSION ===")
if len(results) > 0:
    print("✅ Vectors are searchable after 3s wait")
else:
    print("❌ Still no results - deeper issue")
