"""Web search functionality for retrieving up-to-date information."""

import logging
import os
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Try to import Tavily
try:
    from tavily import TavilyClient
    _HAS_TAVILY = True
except ImportError:
    TavilyClient = None  # type: ignore
    _HAS_TAVILY = False


class WebSearcher:
    """Web search client for retrieving relevant information from the web."""
    
    def __init__(self, provider: str = "tavily", api_key: Optional[str] = None):
        """
        Initialize web searcher.
        
        Args:
            provider: Search provider ("tavily" or "serper")
            api_key: API key for the search provider (if None, tries to get from env)
        """
        self.provider = provider.lower()
        self.api_key = api_key
        self._client = None
        
        if self.provider == "tavily":
            self._init_tavily()
        elif self.provider == "serper":
            raise NotImplementedError("Serper provider not yet implemented")
        else:
            raise ValueError(f"Unknown provider: {provider}. Supported: 'tavily', 'serper'")
    
    def _init_tavily(self):
        """Initialize Tavily client."""
        if not _HAS_TAVILY:
            logger.warning("Tavily not installed. Install with: pip install tavily-python")
            return
        
        api_key = self.api_key or os.getenv("TAVILY_API_KEY")
        if not api_key:
            logger.warning("TAVILY_API_KEY not found. Web search will be disabled.")
            return
        
        try:
            self._client = TavilyClient(api_key=api_key)
            logger.info("Tavily web search client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Tavily client: {e}")
            self._client = None
    
    def search(self, query: str, max_results: int = 3, min_relevance: float = 0.5) -> List[Dict]:
        """
        Perform web search and return relevant results.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            min_relevance: Minimum relevance score threshold (0.0-1.0)
            
        Returns:
            List of result dictionaries with keys: title, url, content, relevance_score
        """
        if not query or not query.strip():
            logger.warning("Empty search query. Returning empty results.")
            return []
        
        if self.provider == "tavily":
            return self._search_tavily(query, max_results, min_relevance)
        else:
            logger.error(f"Unsupported provider: {self.provider}")
            return []
    
    def _search_tavily(self, query: str, max_results: int, min_relevance: float) -> List[Dict]:
        """
        Search using Tavily API.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            min_relevance: Minimum relevance threshold
            
        Returns:
            List of formatted result dictionaries
        """
        if not self._client:
            logger.warning("Tavily client not initialized. Web search unavailable.")
            return []
        
        try:
            # Perform search
            response = self._client.search(
                query=query,
                max_results=max_results,
                search_depth="basic"  # Can be "basic" or "advanced"
            )
            
            # Format results
            results = []
            for result in response.get("results", []):
                # Tavily returns relevance score, filter if below threshold
                score = result.get("score", 0.0)
                if score < min_relevance:
                    continue
                
                formatted_result = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "relevance_score": float(score)
                }
                results.append(formatted_result)
            
            logger.info(f"Web search returned {len(results)} results for query: {query[:50]}...")
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"Tavily search failed: {e}. Returning empty results.")
            return []
    
    def is_available(self) -> bool:
        """Check if web search is available (client initialized and API key present)."""
        return self._client is not None

