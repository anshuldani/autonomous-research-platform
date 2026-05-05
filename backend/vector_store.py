"""
Vector Store Module
===================

Manages vector database operations for semantic search.

This module provides:
- Embedding generation with Voyage AI
- Vector storage in Pinecone
- Semantic search retrieval
- Hybrid search (semantic + keyword)
- Reranking with Cohere
- Metadata filtering
- Text chunking for optimal retrieval

Example usage:
    store = VectorStore()
    store.store_documents(texts, metadata, research_id="session_001")
    results = store.search(query, top_k=5)
"""

from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import voyageai
import time
import hashlib

load_dotenv()


class VectorStore:
    """
    Manages vector database operations for semantic search.

    Uses Pinecone for vector storage and Voyage AI for generating
    high-quality embeddings optimized for retrieval tasks.

    Attributes:
        pc (Pinecone): Pinecone client
        voyage (voyageai.Client): Voyage AI client for embeddings
        index_name (str): Name of the Pinecone index
        dimension (int): Embedding dimension (1024 for Voyage-3)
        index: Connected Pinecone index
    """

    def __init__(self, index_name: str = "research-platform") -> None:
        """Initialize vector store with Pinecone and Voyage AI clients."""
        print("Initializing VectorStore...")

        self.index_name = index_name
        self.dimension = 1024  # Voyage-3 embedding size

        pinecone_key = os.getenv("PINECONE_API_KEY")
        if not pinecone_key:
            raise ValueError("PINECONE_API_KEY not found in environment")

        self.pc = Pinecone(api_key=pinecone_key)

        voyage_key = os.getenv("VOYAGE_API_KEY")
        if not voyage_key:
            raise ValueError("VOYAGE_API_KEY not found in environment")

        self.voyage = voyageai.Client(api_key=voyage_key)

        self._setup_index()

        print("✅ VectorStore initialized")

    def _setup_index(self) -> None:
        """Create the Pinecone index if missing and connect ``self.index``.

        Index is serverless on AWS us-east-1, cosine similarity, with the
        dimension declared in ``self.dimension`` (1024 for Voyage-3).
        Blocks until the index reports ``ready``.
        """
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]

        if self.index_name not in existing_indexes:
            print(f"Creating new Pinecone index: {self.index_name}")

            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )

            print("Waiting for index to be ready...")
            while not self.pc.describe_index(self.index_name).status['ready']:
                time.sleep(1)

            print("✅ Index created and ready!")
        else:
            print(f"Using existing index: {self.index_name}")

        self.index = self.pc.Index(self.index_name)

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks for better retrieval.

        Args:
            text: Long text to chunk
            chunk_size: Target words per chunk (default: 500)
            overlap: Words to overlap between chunks (default: 50)

        Returns:
            List of text chunks
        """
        words = text.split()

        if len(words) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(words):
            end = start + chunk_size
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            chunks.append(chunk_text)

            start = end - overlap

            if start >= len(words):
                break

        return chunks

    def embed_texts(self, texts: List[str], input_type: str = "document") -> List[List[float]]:
        """
        Generate embeddings for a list of texts using Voyage AI.

        Args:
            texts: List of text strings to embed
            input_type: Either "document" (for storage) or "query" (for search)

        Returns:
            List of embedding vectors (each is a list of 1024 floats)
        """
        print(f"🧮 Generating embeddings for {len(texts)} texts...")

        result = self.voyage.embed(
            texts=texts,
            model="voyage-3",
            input_type=input_type
        )

        embeddings = result.embeddings

        print(f"✅ Generated {len(embeddings)} embeddings")

        return embeddings

    def store_documents(
        self,
        texts: List[str],
        metadata: List[Dict],
        research_id: str,
        auto_chunk: bool = True,
    ) -> None:
        """Store documents in Pinecone with Voyage embeddings.

        ``metadata`` must be the same length as ``texts``. When
        ``auto_chunk`` is True, texts longer than 500 words are split via
        ``chunk_text`` before embedding; metadata is duplicated per chunk
        with ``chunk_index`` / ``total_chunks`` fields and the first
        1500 chars of the chunk text echoed under ``"text"``.
        """
        print(f"📦 Storing {len(texts)} documents...")

        all_chunks = []
        all_metadata = []

        for text, meta in zip(texts, metadata):
            if auto_chunk and len(text.split()) > 500:
                chunks = self.chunk_text(text)
                print(f"   Chunked '{meta.get('title', 'doc')[:40]}...' into {len(chunks)} chunks")
            else:
                chunks = [text]

            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)

                chunk_meta = meta.copy()
                chunk_meta.update({
                    'research_id': research_id,
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'text': chunk[:1500]
                })
                all_metadata.append(chunk_meta)

        embeddings = self.embed_texts(all_chunks, input_type="document")

        vectors = []
        for i, (chunk, embedding, meta) in enumerate(zip(all_chunks, embeddings, all_metadata)):
            doc_id = hashlib.md5(chunk.encode()).hexdigest()

            vectors.append({
                "id": f"{research_id}_{doc_id}_{i}",
                "values": embedding,
                "metadata": meta
            })

        self.index.upsert(vectors=vectors)

        print(f"✅ Stored {len(vectors)} vectors in Pinecone")

    def store_documents_batch(
        self,
        texts: List[str],
        metadata: List[Dict],
        research_id: str,
        batch_size: int = 10,
    ) -> None:
        """Wrap ``store_documents`` to batch large sets with a 1s sleep
        between batches, avoiding Pinecone / Voyage rate limits."""
        total = len(texts)
        print(f"📦 Batch storing {total} documents (batch_size={batch_size})...")

        for i in range(0, total, batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_metadata = metadata[i:i + batch_size]

            print(f"   Processing batch {i//batch_size + 1}/{(total + batch_size - 1)//batch_size}")

            self.store_documents(
                texts=batch_texts,
                metadata=batch_metadata,
                research_id=research_id,
                auto_chunk=True
            )

            if i + batch_size < total:
                time.sleep(1)

        print(f"✅ Batch storage complete: {total} documents")

    def search(
        self,
        query: str,
        research_id: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Semantic search for most relevant documents.

        Args:
            query: Search query text
            research_id: Optional filter to specific research session
            top_k: Number of results to return

        Returns:
            List of dicts with: text, score, metadata, id
        """
        print(f"🔍 Searching for: '{query}'")

        query_embedding = self.embed_texts([query], input_type="query")[0]

        filter_dict = {}
        if research_id:
            filter_dict = {"research_id": {"$eq": research_id}}

        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            filter=filter_dict if filter_dict else None,
            include_metadata=True
        )

        formatted = []
        for match in results['matches']:
            formatted.append({
                'text': match['metadata'].get('text', ''),
                'score': match['score'],
                'metadata': match['metadata'],
                'id': match['id']
            })

        print(f"✅ Found {len(formatted)} results")

        return formatted

    def hybrid_search(
        self,
        query: str,
        research_id: Optional[str] = None,
        top_k: int = 10,
        alpha: float = 0.7
    ) -> List[Dict]:
        """
        Hybrid search: semantic (vector) + keyword scoring.

        Args:
            query: Search query
            research_id: Optional filter by research session
            top_k: Number of results
            alpha: Weight for semantic vs keyword (0=keyword only, 1=semantic only)

        Returns:
            Combined and re-ranked results with hybrid_score and keyword_score fields
        """
        print(f"🔍 Hybrid search for: '{query}' (alpha={alpha})")

        semantic_results = self.search(
            query=query,
            research_id=research_id,
            top_k=top_k * 2
        )

        query_terms = set(query.lower().split())

        hybrid_results = []
        for result in semantic_results:
            text_terms = set(result['text'].lower().split())
            keyword_score = len(query_terms & text_terms) / max(len(query_terms), 1)
            hybrid_score = (alpha * result['score']) + ((1 - alpha) * keyword_score)

            result['hybrid_score'] = hybrid_score
            result['keyword_score'] = keyword_score
            hybrid_results.append(result)

        hybrid_results.sort(key=lambda x: x['hybrid_score'], reverse=True)

        print(f"✅ Hybrid search complete")

        return hybrid_results[:top_k]

    def search_with_filters(
        self,
        query: str,
        research_id: Optional[str] = None,
        filters: Optional[Dict] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Advanced search with metadata filtering.

        Args:
            query: Search query
            research_id: Research session ID
            filters: Additional metadata filters
                Example: {"source_type": "academic", "score": {"$gte": 0.8}}
            top_k: Number of results

        Returns:
            Filtered search results
        """
        print(f"🔍 Filtered search for: '{query}'")

        combined_filter = {}

        if research_id:
            combined_filter["research_id"] = {"$eq": research_id}

        if filters:
            combined_filter.update(filters)

        query_embedding = self.embed_texts([query], input_type="query")[0]

        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            filter=combined_filter if combined_filter else None,
            include_metadata=True
        )

        formatted = []
        for match in results['matches']:
            formatted.append({
                'text': match['metadata'].get('text', ''),
                'score': match['score'],
                'metadata': match['metadata'],
                'id': match['id']
            })

        print(f"✅ Found {len(formatted)} results matching filters")

        return formatted

    def rerank_results(
        self,
        query: str,
        results: List[Dict],
        top_n: int = 5
    ) -> List[Dict]:
        """
        Rerank results using Cohere's reranking model.

        Gracefully falls back to returning top_n original results if
        Cohere is unavailable or COHERE_API_KEY is not set.

        Args:
            query: Original search query
            results: Initial search results
            top_n: Number of top results to return after reranking

        Returns:
            Reranked results with rerank_score field added
        """
        try:
            import cohere

            cohere_key = os.getenv("COHERE_API_KEY")
            if not cohere_key:
                print("⚠️  COHERE_API_KEY not found, skipping reranking")
                return results[:top_n]

            print(f"🎯 Reranking {len(results)} results...")

            co = cohere.Client(cohere_key)

            texts = [r['text'] for r in results]

            rerank_response = co.rerank(
                model="rerank-english-v3.0",
                query=query,
                documents=texts,
                top_n=top_n,
                return_documents=True
            )

            reranked = []
            for item in rerank_response.results:
                original = results[item.index].copy()
                original['rerank_score'] = item.relevance_score
                original['original_rank'] = item.index
                reranked.append(original)

            print(f"✅ Reranked to top {len(reranked)} results")
            print(f"   Best score: {reranked[0]['rerank_score']:.3f}")

            return reranked

        except ImportError:
            print("⚠️  Cohere not installed, skipping reranking")
            return results[:top_n]
        except Exception as e:
            print(f"⚠️  Reranking failed: {e}, returning original results")
            return results[:top_n]

    def get_index_stats(self) -> Dict:
        """
        Get statistics about the Pinecone index.

        Returns:
            Dictionary with index statistics
        """
        stats = self.index.describe_index_stats()

        print("\n" + "="*60)
        print("📊 INDEX STATISTICS")
        print("="*60)
        print(f"Total vectors: {stats.get('total_vector_count', 0):,}")
        print(f"Dimension: {stats.get('dimension', self.dimension)}")

        if stats.get('namespaces'):
            print(f"\nNamespaces:")
            for ns, info in stats['namespaces'].items():
                print(f"  {ns}: {info.get('vector_count', 0):,} vectors")

        print("="*60 + "\n")

        return stats

    def count_research_documents(self, research_id: str) -> int:
        """
        Count how many document chunks are stored for a research session.

        Args:
            research_id: Research session ID

        Returns:
            Number of stored chunks for this research
        """
        results = self.index.query(
            vector=[0.0] * self.dimension,
            top_k=10000,
            filter={"research_id": {"$eq": research_id}},
            include_metadata=False
        )

        count = len(results.get('matches', []))

        print(f"📊 Research '{research_id}': {count} chunks stored")

        return count


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTING VECTOR STORE MODULE")
    print("="*60 + "\n")

    print("Test 1: Initialization")
    store = VectorStore()
    print("✅ Passed\n")

    print("Test 2: Embedding Generation")
    test_texts = ["Hello world", "AI is transforming research"]
    embeddings = store.embed_texts(test_texts)
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 1024
    print(f"✅ Passed - Generated {len(embeddings)} embeddings of dimension {len(embeddings[0])}\n")

    print("Test 3: Text Chunking")
    long_text = " ".join(["word"] * 1000)
    chunks = store.chunk_text(long_text, chunk_size=500)
    print(f"✅ Passed - Chunked 1000 words into {len(chunks)} chunks\n")

    print("Test 4: Document Storage")
    test_docs = [
        "Artificial intelligence is revolutionizing healthcare through machine learning.",
        "Quantum computing promises exponential speedups for certain algorithms."
    ]
    test_metadata = [
        {"title": "AI in Healthcare", "source": "test"},
        {"title": "Quantum Computing", "source": "test"}
    ]
    store.store_documents(test_docs, test_metadata, research_id="test_001")
    print("✅ Passed\n")

    print("Test 5: Semantic Search")
    results = store.search("artificial intelligence in medicine", research_id="test_001", top_k=2)
    assert len(results) > 0
    print(f"✅ Passed - Found {len(results)} results")
    print(f"   Top result score: {results[0]['score']:.3f}\n")

    print("Test 6: Hybrid Search")
    hybrid = store.hybrid_search("artificial intelligence", research_id="test_001", alpha=0.7)
    assert len(hybrid) > 0
    assert 'hybrid_score' in hybrid[0]
    print(f"✅ Passed - Hybrid search found {len(hybrid)} results\n")

    print("Test 7: Index Stats")
    store.get_index_stats()
    print("✅ Passed\n")

    print("="*60)
    print("ALL TESTS PASSED! ✅")
    print("="*60)
