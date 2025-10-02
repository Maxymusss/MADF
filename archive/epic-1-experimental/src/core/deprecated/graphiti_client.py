"""
Graphiti MCP Client - MCP Bridge Integration

Provides temporally-aware knowledge graph operations via mcp_bridge.py MCPBridge class.
Uses @upstash/graphiti-mcp MCP server via Python MCP SDK.
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from core.mcp_bridge import MCPBridge

logger = logging.getLogger(__name__)


class GraphitiClient:
    """Client for Graphiti knowledge graph operations via MCP bridge"""

    def __init__(self, mcp_bridge: Optional[MCPBridge] = None):
        """
        Initialize Graphiti client with MCP bridge

        Args:
            mcp_bridge: Optional MCPBridge instance (creates new if not provided)

        Environment variables required:
            - NEO4J_URI: Neo4j connection URI
            - NEO4J_USER: Neo4j username
            - NEO4J_PASSWORD: Neo4j password
            - OPENAI_API_KEY: OpenAI API key for embeddings
        """
        self.mcp_bridge = mcp_bridge or MCPBridge()
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        self._validate_config()
        self._initialized = False

    def _validate_config(self):
        """Validate required configuration is present"""
        if not self.neo4j_password:
            logger.warning("NEO4J_PASSWORD not set - Graphiti MCP may not function")
        if not self.openai_api_key or self.openai_api_key == "your_openai_api_key_here":
            logger.warning("OPENAI_API_KEY not set or is placeholder - Graphiti MCP may not function")

    async def initialize(self):
        """Initialize Graphiti connection (lazy initialization)"""
        if self._initialized:
            return

        try:
            # MCP server initialization handled by mcp_bridge
            self._initialized = True
            logger.info("Graphiti client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Graphiti: {e}")
            raise

    async def add_episode(
        self,
        content: str,
        episode_type: str = "observation",
        source: str = "madf_agent",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add episodic data to knowledge graph with temporal tracking

        Args:
            content: Text content of the episode
            episode_type: Type of episode (observation, action, decision, etc.)
            source: Source agent or system
            metadata: Additional metadata

        Returns:
            Dict containing episode ID and creation metadata
        """
        if not self._initialized:
            await self.initialize()

        try:
            # Prepare parameters for Graphiti MCP
            parameters = {
                "name": content[:50] if len(content) > 50 else content,
                "episode_body": content,
                "source_description": source,
                "reference_time": datetime.now().isoformat(),
                "source": "message"  # EpisodeType.message
            }

            result = await self.mcp_bridge.call_mcp_tool(
                server_name="graphiti",
                tool_name="add_episode",
                parameters=parameters
            )

            if result.get("success"):
                # Parse MCP result
                mcp_result = result.get("result", {})

                # Handle TextContent objects
                if isinstance(mcp_result, list) and len(mcp_result) > 0:
                    content_obj = mcp_result[0]
                    if hasattr(content_obj, 'text'):
                        import json
                        parsed_result = json.loads(content_obj.text)
                    elif isinstance(content_obj, dict):
                        parsed_result = content_obj
                    else:
                        parsed_result = {}
                else:
                    parsed_result = mcp_result

                return {
                    "success": True,
                    "episode_id": parsed_result.get("episode_id", parsed_result.get("uuid", "unknown")),
                    "content": content,
                    "type": episode_type,
                    "source": source,
                    "timestamp": parsed_result.get("created_at", datetime.now().isoformat()),
                    "metadata": metadata or {},
                    "nodes_created": parsed_result.get("nodes_created", 0),
                    "edges_created": parsed_result.get("edges_created", 0)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error")
                }

        except Exception as e:
            logger.error(f"Failed to add episode: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def search_nodes(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for specific entities/nodes in knowledge graph

        Args:
            query: Search query text
            limit: Maximum number of results
            filters: Optional filters (labels, properties, etc.)

        Returns:
            List of matching nodes with metadata
        """
        if not self._initialized:
            await self.initialize()

        try:
            parameters = {
                "query": query,
                "limit": limit
            }
            if filters:
                parameters.update(filters)

            result = await self.mcp_bridge.call_mcp_tool(
                server_name="graphiti",
                tool_name="search_nodes",
                parameters=parameters
            )

            if result.get("success"):
                # Parse MCP result
                mcp_result = result.get("result", {})

                if isinstance(mcp_result, list) and len(mcp_result) > 0:
                    content_obj = mcp_result[0]
                    if hasattr(content_obj, 'text'):
                        import json
                        nodes = json.loads(content_obj.text)
                    elif isinstance(content_obj, dict):
                        nodes = content_obj.get("nodes", [])
                    else:
                        nodes = []
                else:
                    nodes = []

                return nodes
            else:
                logger.error(f"Failed to search nodes: {result.get('error')}")
                return []

        except Exception as e:
            logger.error(f"Failed to search nodes: {e}")
            return []

    async def search_facts(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for factual relationships in knowledge graph

        Args:
            query: Search query text
            limit: Maximum number of results
            filters: Optional filters

        Returns:
            List of matching facts/edges with metadata
        """
        if not self._initialized:
            await self.initialize()

        try:
            parameters = {
                "query": query,
                "limit": limit
            }
            if filters:
                parameters.update(filters)

            result = await self.mcp_bridge.call_mcp_tool(
                server_name="graphiti",
                tool_name="search_facts",
                parameters=parameters
            )

            if result.get("success"):
                # Parse MCP result
                mcp_result = result.get("result", {})

                if isinstance(mcp_result, list) and len(mcp_result) > 0:
                    content_obj = mcp_result[0]
                    if hasattr(content_obj, 'text'):
                        import json
                        facts = json.loads(content_obj.text)
                    elif isinstance(content_obj, dict):
                        facts = content_obj.get("facts", [])
                    else:
                        facts = []
                else:
                    facts = []

                return facts
            else:
                logger.error(f"Failed to search facts: {result.get('error')}")
                return []

        except Exception as e:
            logger.error(f"Failed to search facts: {e}")
            return []

    async def search_episodes(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query historical episodes with temporal awareness

        Args:
            query: Search query text
            limit: Maximum number of results
            filters: Optional temporal or metadata filters

        Returns:
            List of matching episodes with temporal metadata
        """
        if not self._initialized:
            await self.initialize()

        try:
            parameters = {
                "query": query,
                "limit": limit
            }
            if filters:
                parameters.update(filters)

            result = await self.mcp_bridge.call_mcp_tool(
                server_name="graphiti",
                tool_name="search_episodes",
                parameters=parameters
            )

            if result.get("success"):
                # Parse MCP result
                mcp_result = result.get("result", {})

                if isinstance(mcp_result, list) and len(mcp_result) > 0:
                    content_obj = mcp_result[0]
                    if hasattr(content_obj, 'text'):
                        import json
                        episodes = json.loads(content_obj.text)
                    elif isinstance(content_obj, dict):
                        episodes = content_obj.get("episodes", [])
                    else:
                        episodes = []
                else:
                    episodes = []

                return episodes
            else:
                logger.error(f"Failed to search episodes: {result.get('error')}")
                return []

        except Exception as e:
            logger.error(f"Failed to search episodes: {e}")
            return []

    async def query_temporal(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        entity_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query knowledge graph with temporal constraints

        Args:
            start_time: Start of time range
            end_time: End of time range
            entity_types: Filter by entity types

        Returns:
            List of entities/facts within temporal range
        """
        if not self._initialized:
            await self.initialize()

        try:
            # Build temporal query using search_nodes with filters
            parameters = {
                "query": "*",  # Match all
                "limit": 100
            }

            filters = {}
            if start_time:
                filters["start_time"] = start_time.isoformat()
            if end_time:
                filters["end_time"] = end_time.isoformat()
            if entity_types:
                filters["entity_types"] = entity_types

            if filters:
                parameters["filters"] = filters

            result = await self.mcp_bridge.call_mcp_tool(
                server_name="graphiti",
                tool_name="search_nodes",
                parameters=parameters
            )

            if result.get("success"):
                mcp_result = result.get("result", {})

                if isinstance(mcp_result, list) and len(mcp_result) > 0:
                    content_obj = mcp_result[0]
                    if hasattr(content_obj, 'text'):
                        import json
                        return json.loads(content_obj.text)
                    elif isinstance(content_obj, dict):
                        return content_obj.get("nodes", [])
                return []
            else:
                logger.error(f"Failed temporal query: {result.get('error')}")
                return []

        except Exception as e:
            logger.error(f"Failed temporal query: {e}")
            return []

    async def close(self):
        """Close Graphiti connection"""
        self._initialized = False
        logger.info("Graphiti client closed")
