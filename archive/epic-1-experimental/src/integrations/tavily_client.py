"""
Tavily Client - Direct tavily-python integration for web search

Uses tavily-python library for native SDK performance (per ADR-001)
"""

import os
from typing import List, Dict, Any, Optional
from tavily import TavilyClient as TavilySDK


class TavilyClient:
    """Direct Tavily integration via tavily-python library"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Tavily client

        Args:
            api_key: Tavily API key (defaults to TAVILY_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("Tavily API key required (TAVILY_API_KEY env var or api_key parameter)")

        self.client = TavilySDK(api_key=self.api_key)
        self._quota_used = 0

    def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
        include_answer: bool = True,
        include_raw_content: bool = False,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute web search

        Args:
            query: Search query string
            max_results: Maximum results to return (default: 5)
            search_depth: Search depth - "basic" or "advanced" (default: basic)
            include_answer: Include AI-generated answer (default: True)
            include_raw_content: Include raw HTML content (default: False)
            include_domains: List of domains to include (optional)
            exclude_domains: List of domains to exclude (optional)

        Returns:
            Dict with search results and optional answer
        """
        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                include_answer=include_answer,
                include_raw_content=include_raw_content,
                include_domains=include_domains,
                exclude_domains=exclude_domains
            )

            self._quota_used += 1

            return {
                "success": True,
                "query": query,
                "answer": response.get("answer"),
                "results": self._format_results(response.get("results", [])),
                "quota_used": self._quota_used
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }

    def qna_search(self, query: str) -> Dict[str, Any]:
        """
        Execute Q&A search (optimized for question answering)

        Args:
            query: Question to answer

        Returns:
            Dict with answer and supporting sources
        """
        try:
            response = self.client.qna_search(query=query)

            self._quota_used += 1

            return {
                "success": True,
                "query": query,
                "answer": response,
                "quota_used": self._quota_used
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }

    def get_search_context(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        """
        Get search context for RAG applications

        Args:
            query: Search query
            max_results: Maximum results to return
            search_depth: Search depth - "basic" or "advanced"
            max_tokens: Maximum tokens in context

        Returns:
            Dict with formatted context string and sources
        """
        try:
            context = self.client.get_search_context(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                max_tokens=max_tokens
            )

            self._quota_used += 1

            return {
                "success": True,
                "query": query,
                "context": context,
                "quota_used": self._quota_used
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }

    def extract(self, urls: List[str]) -> Dict[str, Any]:
        """
        Extract content from URLs (up to 20 URLs)

        Args:
            urls: List of URLs to extract content from

        Returns:
            Dict with extracted content per URL
        """
        if len(urls) > 20:
            return {
                "success": False,
                "error": "Maximum 20 URLs allowed per extraction",
                "urls_count": len(urls)
            }

        try:
            response = self.client.extract(urls=urls)

            self._quota_used += len(urls)

            return {
                "success": True,
                "results": self._format_extract_results(response.get("results", [])),
                "urls_count": len(urls),
                "quota_used": self._quota_used
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "urls_count": len(urls)
            }

    def filter_results(
        self,
        results: List[Dict[str, Any]],
        min_score: float = 0.0,
        required_keywords: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Filter search results by score and keywords

        Args:
            results: List of search result dicts
            min_score: Minimum relevance score (0.0-1.0)
            required_keywords: Keywords that must appear in title or content

        Returns:
            Filtered list of results
        """
        filtered = []

        for result in results:
            # Score filter
            if result.get("score", 0) < min_score:
                continue

            # Keyword filter
            if required_keywords:
                text = (result.get("title", "") + " " + result.get("content", "")).lower()
                if not any(keyword.lower() in text for keyword in required_keywords):
                    continue

            filtered.append(result)

        return filtered

    def get_quota_status(self) -> Dict[str, int]:
        """
        Get quota usage status

        Returns:
            Dict with quota_used counter
        """
        return {
            "quota_used": self._quota_used,
            "note": "This is a session counter. Check Tavily dashboard for actual quota limits."
        }

    @staticmethod
    def _format_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format search results to standardized structure"""
        formatted = []

        for result in results:
            formatted.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
                "score": result.get("score", 0.0),
                "raw_content": result.get("raw_content")
            })

        return formatted

    @staticmethod
    def _format_extract_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format extraction results to standardized structure"""
        formatted = []

        for result in results:
            formatted.append({
                "url": result.get("url", ""),
                "raw_content": result.get("raw_content", ""),
                "success": result.get("success", False)
            })

        return formatted
