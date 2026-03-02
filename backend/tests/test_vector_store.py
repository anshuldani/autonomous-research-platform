"""
Unit tests for VectorStore module
"""
import pytest
from unittest.mock import Mock, patch, MagicMock


def test_vector_store_initialization():
    """Test VectorStore initializes correctly."""
    from vector_store import VectorStore
    
    store = VectorStore()
    
    assert store.index_name == "research-platform"
    assert store.dimension == 1024
    assert hasattr(store, 'pc')
    assert hasattr(store, 'voyage')
    assert hasattr(store, 'index')


def test_chunk_text():
    """Test text chunking algorithm."""
    from vector_store import VectorStore
    
    store = VectorStore()
    
    # Short text - no chunking
    short_text = "This is a short text"
    chunks = store.chunk_text(short_text, chunk_size=500)
    assert len(chunks) == 1
    
    # Long text - should chunk
    long_text = " ".join(["word"] * 1000)
    chunks = store.chunk_text(long_text, chunk_size=500, overlap=50)
    assert len(chunks) >= 2
    
    # Verify overlap
    assert len(chunks[0].split()) == 500
    # Second chunk should have some words from first chunk (overlap)


def test_embed_texts():
    """Test embedding generation."""
    from vector_store import VectorStore
    
    store = VectorStore()
    
    texts = ["Hello world", "AI is amazing"]
    embeddings = store.embed_texts(texts)
    
    # Should return list of embeddings
    assert len(embeddings) == 2
    
    # Each embedding should be 1024-dimensional
    assert len(embeddings[0]) == 1024
    assert len(embeddings[1]) == 1024
    
    # Embeddings should be list of floats
    assert isinstance(embeddings[0][0], float)


def test_store_and_search():
    """Test document storage and retrieval."""
    from vector_store import VectorStore
    import uuid
    
    store = VectorStore()
    research_id = f"test_{uuid.uuid4().hex[:8]}"
    
    # Store documents
    texts = [
        "Artificial intelligence is transforming healthcare.",
        "Quantum computing uses quantum mechanics principles."
    ]
    metadata = [
        {"title": "AI in Healthcare", "source": "test"},
        {"title": "Quantum Computing", "source": "test"}
    ]
    
    store.store_documents(texts, metadata, research_id)
    
    # Search
    results = store.search(
        query="artificial intelligence in medicine",
        research_id=research_id,
        top_k=2
    )
    
    # Should return results
    assert len(results) > 0
    
    # Results should have required fields
    assert 'text' in results[0]
    assert 'score' in results[0]
    assert 'metadata' in results[0]
    
    # Score should be between 0 and 1
    assert 0 <= results[0]['score'] <= 1


def test_semantic_search_quality():
    """Test that semantic search finds relevant content."""
    from vector_store import VectorStore
    import uuid
    
    store = VectorStore()
    research_id = f"test_{uuid.uuid4().hex[:8]}"
    
    # Store diverse documents
    texts = [
        "Machine learning models require large amounts of training data.",
        "The Eiffel Tower is located in Paris, France.",
        "Deep neural networks have revolutionized computer vision."
    ]
    metadata = [
        {"title": "ML Training", "id": 1},
        {"title": "Paris Landmark", "id": 2},
        {"title": "Neural Networks", "id": 3}
    ]
    
    store.store_documents(texts, metadata, research_id)
    
    # Search for AI-related content
    results = store.search(
        query="artificial intelligence and neural networks",
        research_id=research_id,
        top_k=2
    )
    
    # Top results should be AI-related (not Eiffel Tower)
    top_titles = [r['metadata']['title'] for r in results]
    assert "Paris Landmark" not in top_titles[:2]
    
    # Should find ML or Neural Network docs
    assert any(title in ["ML Training", "Neural Networks"] for title in top_titles)


def test_chunking_preserves_context():
    """Test that chunking maintains context at boundaries."""
    from vector_store import VectorStore
    
    store = VectorStore()
    
    # Create text with identifiable sections
    text = " ".join([f"section{i}" for i in range(1000)])
    
    chunks = store.chunk_text(text, chunk_size=500, overlap=50)
    
    # Should have multiple chunks
    assert len(chunks) >= 2
    
    # Check overlap exists
    # Last 50 words of chunk 1 should appear in first words of chunk 2
    chunk1_words = chunks[0].split()
    chunk2_words = chunks[1].split()
    
    # At least some overlap should exist
    overlap_words = set(chunk1_words[-50:]) & set(chunk2_words[:50])
    assert len(overlap_words) > 0
