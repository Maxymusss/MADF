"""
Platform-aware Graphiti wrapper for Story 1.3

Provides direct graphiti_core.Graphiti integration following Story 1.2 Serena pattern.
Handles Windows neo4j driver incompatibility with mock implementation.
"""

import sys
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Platform detection
IS_WINDOWS = sys.platform == "win32"

if not IS_WINDOWS:
    # Real Graphiti implementation (Linux/WSL/Docker)
    try:
        from graphiti_core import Graphiti as GraphitiCore
        GRAPHITI_AVAILABLE = True
    except (ImportError, AttributeError) as e:
        logger.warning(f"Graphiti import failed: {e}")
        GRAPHITI_AVAILABLE = False
        GraphitiCore = None
else:
    # Windows: neo4j 6.0 driver incompatibility
    GRAPHITI_AVAILABLE = False
    GraphitiCore = None


class GraphitiWrapper:
    """
    Platform-aware wrapper for Graphiti knowledge graph operations

    Provides consistent API across platforms:
    - Linux/WSL/Docker: Real graphiti_core.Graphiti
    - Windows: Mock implementation for development/testing
    """

    def __init__(
        self,
        neo4j_uri: Optional[str] = None,
        neo4j_user: Optional[str] = None,
        neo4j_password: Optional[str] = None,
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize Graphiti wrapper

        Args:
            neo4j_uri: Neo4j database URI (defaults to NEO4J_URI env var)
            neo4j_user: Neo4j username (defaults to NEO4J_USER env var)
            neo4j_password: Neo4j password (defaults to NEO4J_PASSWORD env var)
            openai_api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.neo4j_uri = neo4j_uri or os.getenv("NEO4J_URI")
        self.neo4j_user = neo4j_user or os.getenv("NEO4J_USER")
        self.neo4j_password = neo4j_password or os.getenv("NEO4J_PASSWORD")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        self._client = None
        self._is_mock = False

        if GRAPHITI_AVAILABLE and GraphitiCore:
            try:
                self._client = GraphitiCore(
                    neo4j_uri=self.neo4j_uri,
                    neo4j_user=self.neo4j_user,
                    neo4j_password=self.neo4j_password
                )
                logger.info("Graphiti initialized with real graphiti_core library")
            except Exception as e:
                logger.error(f"Failed to initialize Graphiti: {e}")
                self._is_mock = True
        else:
            self._is_mock = True
            reason = "Windows platform (neo4j 6.0 incompatibility)" if IS_WINDOWS else "graphiti_core not available"
            logger.warning(f"Graphiti using mock implementation: {reason}")

    @property
    def is_mock(self) -> bool:
        """Check if using mock implementation"""
        return self._is_mock

    @property
    def is_available(self) -> bool:
        """Check if real Graphiti is available"""
        return not self._is_mock

    async def add_episode(
        self,
        content: str,
        episode_type: str = "observation",
        source: str = "knowledge_agent",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add episodic data to knowledge graph

        Args:
            content: Episode content
            episode_type: Type of episode
            source: Source identifier
            metadata: Additional metadata

        Returns:
            Dict with success status and episode_id
        """
        if self._is_mock:
            return {
                "success": True,
                "episode_id": f"mock-episode-{hash(content) % 10000}",
                "message": f"Mock: Would add episode (type={episode_type}, source={source})",
                "platform": "mock"
            }

        try:
            result = await self._client.add_episode(
                name=episode_type,
                episode_body=content,
                source_description=source,
                reference_time=datetime.now()
            )
            return {
                "success": True,
                "episode_id": str(result.episode_id) if hasattr(result, 'episode_id') else "unknown",
                "platform": "graphiti_core"
            }
        except Exception as e:
            logger.error(f"Graphiti add_episode failed: {e}")
            return {"success": False, "error": str(e)}

    async def search_nodes(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for nodes in knowledge graph

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching nodes
        """
        if self._is_mock:
            return [
                {
                    "node_id": f"mock-node-{i}",
                    "name": f"Mock Result {i} for: {query}",
                    "score": 0.9 - (i * 0.1),
                    "platform": "mock"
                }
                for i in range(min(3, limit))
            ]

        try:
            results = await self._client.search(
                query=query,
                num_results=limit
            )
            # Convert results to dict format
            return [
                {
                    "node_id": str(r.id) if hasattr(r, 'id') else "unknown",
                    "name": str(r.name) if hasattr(r, 'name') else str(r),
                    "score": float(r.score) if hasattr(r, 'score') else 0.0,
                    "platform": "graphiti_core"
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Graphiti search_nodes failed: {e}")
            return []

    async def search_facts(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for facts/relationships in knowledge graph

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching facts
        """
        if self._is_mock:
            return [
                {
                    "fact_id": f"mock-fact-{i}",
                    "subject": "Entity A",
                    "predicate": "relates to",
                    "object": "Entity B",
                    "query": query,
                    "platform": "mock"
                }
                for i in range(min(2, limit))
            ]

        try:
            # graphiti_core may have different method for facts
            # Using search as fallback
            results = await self._client.search(
                query=query,
                num_results=limit
            )
            return [{"fact": str(r), "platform": "graphiti_core"} for r in results]
        except Exception as e:
            logger.error(f"Graphiti search_facts failed: {e}")
            return []

    async def search_episodes(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for historical episodes

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching episodes
        """
        if self._is_mock:
            return [
                {
                    "episode_id": f"mock-episode-{i}",
                    "content": f"Mock episode content matching: {query}",
                    "timestamp": datetime.now().isoformat(),
                    "platform": "mock"
                }
                for i in range(min(2, limit))
            ]

        try:
            # graphiti_core search method
            results = await self._client.search(
                query=query,
                num_results=limit
            )
            return [
                {
                    "episode_id": str(r.id) if hasattr(r, 'id') else "unknown",
                    "content": str(r),
                    "platform": "graphiti_core"
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Graphiti search_episodes failed: {e}")
            return []

    async def close(self):
        """Close Graphiti connection"""
        if self._client and not self._is_mock:
            try:
                if hasattr(self._client, 'close'):
                    await self._client.close()
                logger.info("Graphiti connection closed")
            except Exception as e:
                logger.warning(f"Error closing Graphiti: {e}")
