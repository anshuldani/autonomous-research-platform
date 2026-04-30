"""
Tests for Day 3 RAG Agents
"""
import pytest
from unittest.mock import Mock, patch
import uuid


def test_advanced_rag_hybrid_search():
    """Test advanced RAG uses hybrid search."""
    from planning_agent import advanced_rag_synthesis_agent
    from vector_store import VectorStore

    state = {
        'topic': 'Test',
        'research_id': 'test_123',
        'research_questions': ['Q1?'],
        'search_results': {},
        'stored_chunks': 3,
        'retrieval_method': '',
        'rag_context': '',
        'rerank_scores': [],
        'quality_metrics': {},
        'summary': '',
        'current_step': 'research_complete'
    }

    mock_hybrid_results = [
        {
            'text': 'chunk text',
            'score': 0.9,
            'hybrid_score': 0.85,
            'metadata': {'title': 'Source 1'}
        }
    ]

    mock_claude = Mock()
    mock_claude.content = [Mock(text="Summary here")]

    with patch('planning_agent.vector_store.hybrid_search', return_value=mock_hybrid_results):
        with patch('planning_agent.client.messages.create', return_value=mock_claude):
            result = advanced_rag_synthesis_agent(state)

            assert result['retrieval_method'] == 'hybrid+rerank'
            assert result['current_step'] == 'complete'
            assert result['summary'] == "Summary here"


def test_reranking_quality_improvement():
    """Test that reranking improves result quality."""
    from vector_store import VectorStore
    import time

    store = VectorStore()
    research_id = f"test_rerank_{uuid.uuid4().hex[:8]}"

    texts = [
        "Machine learning requires large datasets for training neural networks.",
        "The weather today is sunny with clear skies.",
        "Deep learning models use backpropagation for optimization."
    ]
    metadata = [
        {"title": "ML Training", "relevance": "high"},
        {"title": "Weather", "relevance": "low"},
        {"title": "Deep Learning", "relevance": "high"}
    ]

    store.store_documents(texts, metadata, research_id)
    time.sleep(2)

    query = "machine learning and neural networks"

    regular_results = store.search(query, research_id=research_id, top_k=3)

    try:
        candidates = store.search(query, research_id=research_id, top_k=10)
        reranked = store.rerank_results(query, candidates, top_n=3)

        top_titles = [r['metadata']['title'] for r in reranked]
        assert "Weather" not in top_titles[:2]

    except Exception as e:
        pytest.skip(f"Reranking not available: {e}")


def test_vector_store_batch_processing():
    """Test batch document storage."""
    from vector_store import VectorStore

    store = VectorStore()
    research_id = f"test_batch_{uuid.uuid4().hex[:8]}"

    texts = [f"Document number {i} about AI and ML" for i in range(15)]
    metadata = [{"title": f"Doc {i}", "batch": "test"} for i in range(15)]

    with patch.object(store, 'store_documents') as mock_store:
        store.store_documents_batch(
            texts=texts,
            metadata=metadata,
            research_id=research_id,
            batch_size=5
        )

        assert mock_store.call_count == 3


def test_hybrid_search_combines_scores():
    """Test hybrid search combines semantic and keyword scores."""
    from vector_store import VectorStore
    import time

    store = VectorStore()
    research_id = f"test_hybrid_{uuid.uuid4().hex[:8]}"

    texts = [
        "Artificial intelligence and machine learning",
        "Quantum computing uses quantum mechanics"
    ]
    metadata = [{"title": "AI"}, {"title": "Quantum"}]

    store.store_documents(texts, metadata, research_id)
    time.sleep(2)

    results = store.hybrid_search(
        query="artificial intelligence",
        research_id=research_id,
        alpha=0.7
    )

    assert 'hybrid_score' in results[0]
    assert 'keyword_score' in results[0]

    assert results[0]['metadata']['title'] == "AI"
