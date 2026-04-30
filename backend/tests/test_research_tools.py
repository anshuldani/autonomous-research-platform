"""
Tests for ResearchTools module
"""
import pytest
import os
from unittest.mock import patch, MagicMock


def test_research_tools_init_success():
    """Test successful initialization with valid API key."""
    from research_tools import ResearchTools
    
    # Should initialize without errors
    tools = ResearchTools()
    
    # Should have tavily client
    assert hasattr(tools, 'tavily')
    assert tools.tavily is not None


def test_research_tools_init_missing_key():
    """Test initialization fails gracefully without API key."""
    from research_tools import ResearchTools
    
    # Temporarily remove API key
    with patch.dict(os.environ, {'TAVILY_API_KEY': ''}):
        with pytest.raises(ValueError) as exc_info:
            tools = ResearchTools()
        
        # Check error message is helpful
        assert "TAVILY_API_KEY not found" in str(exc_info.value)


@patch.dict(os.environ, {'TAVILY_API_KEY': 'test_key'})
def test_search_web_success():
    """Test successful web search returns formatted results."""
    from research_tools import ResearchTools

    # Mock Tavily response
    mock_response = {
        'results': [
            {
                'title': 'Test Article',
                'url': 'https://example.com/test',
                'content': 'Test content here',
                'score': 0.95
            },
            {
                'title': 'Another Article',
                'url': 'https://example.com/test2',
                'content': 'More test content',
                'score': 0.87
            }
        ]
    }
    
    tools = ResearchTools()
    
    # Mock the tavily.search method
    tools.tavily.search = MagicMock(return_value=mock_response)
    
    # Execute search
    results = tools.search_web("test query", max_results=2)
    
    # Verify results
    assert len(results) == 2
    assert results[0]['title'] == 'Test Article'
    assert results[0]['url'] == 'https://example.com/test'
    assert results[0]['score'] == 0.95
    
    # Verify API was called correctly
    tools.tavily.search.assert_called_once()


@patch.dict(os.environ, {'TAVILY_API_KEY': 'test_key'})
def test_search_web_api_error():
    """Test search_web handles API errors gracefully."""
    from research_tools import ResearchTools

    tools = ResearchTools()
    
    # Mock API to raise an exception
    tools.tavily.search = MagicMock(side_effect=Exception("API Error"))
    
    # Should not crash, should return empty list
    results = tools.search_web("test query")
    
    assert results == []
    assert isinstance(results, list)


@patch.dict(os.environ, {'TAVILY_API_KEY': 'test_key'})
def test_search_web_empty_results():
    """Test search_web handles empty results from API."""
    from research_tools import ResearchTools

    tools = ResearchTools()
    
    # Mock empty response
    tools.tavily.search = MagicMock(return_value={'results': []})
    
    results = tools.search_web("test query")
    
    assert results == []
    assert isinstance(results, list)
