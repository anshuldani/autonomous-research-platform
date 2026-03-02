"""
Research Tools Module
=====================

Handles external research tools like web search.

Example usage:
    tools = ResearchTools()
    results = tools.search_web("AI research", max_results=5)

Testing:
    Run tests with: pytest tests/test_research_tools.py -v
    
    Manual testing:
    >>> from research_tools import ResearchTools
    >>> tools = ResearchTools()
    >>> results = tools.search_web("test query", max_results=2)
    >>> assert len(results) <= 2
"""

from tavily import TavilyClient
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()


class ResearchTools:
    """
    Manages external research tools and APIs.
    
    This class provides a unified interface for various research tools,
    starting with web search via Tavily. Future additions may include
    academic paper search, news APIs, etc.
    
    Attributes:
        tavily (TavilyClient): Client for Tavily web search API
    
    Example:
        >>> tools = ResearchTools()
        >>> results = tools.search_web("quantum computing")
        >>> print(results[0]['title'])
    """
    
    def __init__(self):
        """
        Initialize research tools and API clients.
        
        Raises:
            ValueError: If required API keys are not found in environment
        """
        # Get API key from environment
        api_key = os.getenv("TAVILY_API_KEY")
        
        # Validate API key exists
        if not api_key:
            raise ValueError(
                "TAVILY_API_KEY not found in environment variables. "
                "Please add it to your .env file."
            )
        
        # Initialize Tavily client
        self.tavily = TavilyClient(api_key=api_key)
        
        print("✅ ResearchTools initialized")
    
    
    def _format_search_result(self, item: Dict) -> Dict:
        """
        Format a single search result into standard structure.
        
        Args:
            item: Raw result from Tavily API
        
        Returns:
            Formatted dictionary with standard keys
        """
        return {
            'title': item.get('title', 'Untitled'),
            'url': item.get('url', ''),
            'content': item.get('content', ''),
            'score': item.get('score', 0.0)
        }
    
    
    def search_web(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search the web and return clean results.
        
        Uses Tavily's advanced search to find high-quality, relevant
        content with extracted text ready for LLM processing.
        
        Args:
            query: Search query string (e.g., "latest AI breakthroughs")
            max_results: Maximum number of results to return (default: 5)
        
        Returns:
            List of dictionaries containing search results with keys:
            - title (str): Page title
            - url (str): Page URL
            - content (str): Extracted text content (cleaned)
            - score (float): Relevance score between 0 and 1
            
            Returns empty list if search fails.
        
        Example:
            >>> tools = ResearchTools()
            >>> results = tools.search_web("CRISPR gene editing", max_results=3)
            >>> for result in results:
            ...     print(f"{result['title']}: {result['score']}")
            CRISPR Breakthrough 2024: 0.95
            Gene Editing Ethics: 0.88
            CRISPR Applications: 0.82
        
        Raises:
            No exceptions raised - errors are logged and empty list returned.
        """
        print(f"🔍 Searching web: '{query}'")
        print(f"   Requesting {max_results} results...")
        
        try:
            # Call Tavily API
            response = self.tavily.search(
                query=query,
                max_results=max_results,
                search_depth="advanced",
                include_raw_content=False
            )
            
            # Process results using helper method
            results = [
                self._format_search_result(item)
                for item in response.get('results', [])
            ]
            
            print(f"✅ Found {len(results)} results\n")
            
            return results
            
        except Exception as e:
            print(f"❌ Search failed: {str(e)}")
            return []  # Return empty list on error


# Module-level test when run directly
if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTING RESEARCH TOOLS MODULE")
    print("="*60 + "\n")
    
    # Test initialization
    print("Test 1: Initialization")
    tools = ResearchTools()
    print("✅ Passed\n")
    
    # Test search
    print("Test 2: Web Search")
    results = tools.search_web("artificial intelligence", max_results=2)
    
    if results:
        print(f"✅ Passed - Got {len(results)} results")
        print(f"   Sample: {results[0]['title'][:60]}...")
    else:
        print("❌ Failed - No results returned")
    
    print("\n" + "="*60)
    print("Run full test suite: pytest tests/test_research_tools.py -v")
    print("="*60 + "\n")
