"""
Knowledge Agent - Persistent knowledge graphs and documentation

Responsibilities:
- Knowledge graph operations via Graphiti (direct library - Story 1.2 pattern)
- Note and documentation management via Obsidian MCP
- Filesystem operations via Filesystem MCP
- Cross-session knowledge persistence and bi-temporal tracking
"""

from typing import List, Dict, Any, Optional
import logging
from agents.base_agent import BaseAgent
from core.mcp_bridge import MCPBridge
from core.graphiti_wrapper import GraphitiWrapper

logger = logging.getLogger(__name__)


class KnowledgeAgent(BaseAgent):
    """Knowledge agent for persistent knowledge graphs and documentation"""

    def __init__(self):
        super().__init__("Knowledge", "Knowledge Management Specialist", agent_id="knowledge")
        self.mcp_bridge = MCPBridge()

        # Graphiti: Direct library integration (like Serena in Story 1.2)
        self.graphiti = GraphitiWrapper()
        if self.graphiti.is_mock:
            logger.warning("KnowledgeAgent using mock Graphiti (requires Linux/WSL/Docker for real implementation)")



    def get_available_tools(self) -> List[str]:
        """Return knowledge persistence and graph tools"""
        return self._tools.copy()

    async def store_episode(
        self,
        content: str,
        episode_type: str = "observation",
        source: str = "knowledge_agent",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store episodic knowledge in graph

        Args:
            content: Episode content
            episode_type: Type of episode
            source: Source agent
            metadata: Additional metadata

        Returns:
            Dict containing storage result
        """
        try:
            # Direct Graphiti library call (Story 1.2 pattern)
            result = await self.graphiti.add_episode(
                content=content,
                episode_type=episode_type,
                source=source,
                metadata=metadata
            )
            logger.info(f"Episode stored: {result.get('episode_id')}")
            return result
        except Exception as e:
            logger.error(f"Failed to store episode: {e}")
            return {"success": False, "error": str(e)}

    async def search_knowledge(
        self,
        query: str,
        search_type: str = "nodes",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge graph

        Args:
            query: Search query
            search_type: Type of search (nodes, facts, episodes)
            limit: Maximum results

        Returns:
            List of matching results
        """
        try:
            # Direct Graphiti library calls (Story 1.2 pattern)
            if search_type == "nodes":
                results = await self.graphiti.search_nodes(query, limit)
            elif search_type == "facts":
                results = await self.graphiti.search_facts(query, limit)
            elif search_type == "episodes":
                results = await self.graphiti.search_episodes(query, limit)
            else:
                logger.warning(f"Unknown search type: {search_type}")
                return []

            logger.info(f"Found {len(results)} results for query: {query}")
            return results
        except Exception as e:
            logger.error(f"Failed to search knowledge: {e}")
            return []

    async def create_documentation(
        self,
        file_path: str,
        content: str,
        operation: str = "append"
    ) -> Dict[str, Any]:
        """
        Create or update documentation in Obsidian

        Args:
            file_path: Path to documentation file
            content: Content to add
            operation: Operation type (append, patch)

        Returns:
            Dict containing operation result
        """
        try:
            if operation == "append":
                result = self.mcp_bridge.call_obsidian_tool(
                    "append_content",
                    {"file_path": file_path, "content": content}
                )
            elif operation == "patch":
                result = self.mcp_bridge.call_obsidian_tool(
                    "patch_content",
                    {"file_path": file_path, "content": content}
                )
            else:
                logger.warning(f"Unknown operation: {operation}")
                result = {"success": False, "error": f"Unknown operation: {operation}"}

            logger.info(f"Documentation {operation} result: {result.get('success')}")
            return result
        except Exception as e:
            logger.error(f"Failed to create documentation: {e}")
            return {"success": False, "error": str(e)}

    async def search_documentation(self, query: str) -> List[Dict[str, Any]]:
        """
        Search documentation in Obsidian vault

        Args:
            query: Search query

        Returns:
            List of matching documents
        """
        try:
            result = self.mcp_bridge.call_obsidian_tool(
                "search",
                {"query": query}
            )
            results = result.get("results", []) if result.get("success") else []
            logger.info(f"Found {len(results)} documentation matches")
            return results
        except Exception as e:
            logger.error(f"Failed to search documentation: {e}")
            return []

    async def query_filesystem(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Query filesystem via Filesystem MCP

        Args:
            tool_name: Filesystem tool to use
            parameters: Tool parameters

        Returns:
            Dict containing filesystem query results
        """
        try:
            result = self.mcp_bridge.call_filesystem_tool(tool_name, parameters)
            logger.info(f"Filesystem query {tool_name} completed")
            return result
        except Exception as e:
            logger.error(f"Failed to query filesystem: {e}")
            return {"success": False, "error": str(e)}

    async def query_serena(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Query semantic code search via Serena MCP (separate from filesystem operations)

        Args:
            tool_name: Serena tool to use (find_symbol, find_referencing_symbols, etc.)
            parameters: Tool parameters

        Returns:
            Dict containing Serena query results
        """
        try:
            result = self.mcp_bridge.call_serena_tool(tool_name, parameters)
            logger.info(f"Serena query {tool_name} completed")
            return result
        except Exception as e:
            logger.error(f"Failed to query Serena: {e}")
            return {"success": False, "error": str(e)}

    async def persist_cross_session_memory(
        self,
        session_id: str,
        memory_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Persist memory across sessions using knowledge graph

        Args:
            session_id: Session identifier
            memory_data: Memory data to persist

        Returns:
            Dict containing persistence result
        """
        try:
            # Store session memory as episode
            episode_content = f"Session {session_id}: {memory_data}"
            result = await self.store_episode(
                content=str(episode_content),
                episode_type="session_memory",
                source="knowledge_agent",
                metadata={"session_id": session_id, **memory_data}
            )

            logger.info(f"Cross-session memory persisted for {session_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to persist cross-session memory: {e}")
            return {"success": False, "error": str(e)}

    async def retrieve_cross_session_memory(
        self,
        session_id: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memory from previous sessions

        Args:
            session_id: Session identifier to retrieve

        Returns:
            List of memory items from session
        """
        try:
            # Search for session memory episodes
            results = await self.search_knowledge(
                query=f"session {session_id}",
                search_type="episodes",
                limit=50
            )

            logger.info(f"Retrieved {len(results)} memory items for {session_id}")
            return results
        except Exception as e:
            logger.error(f"Failed to retrieve cross-session memory: {e}")
            return []

    def process_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process knowledge management tasks (sync wrapper for async operations)

        Args:
            task_description: Description of knowledge task
            context: Current knowledge context

        Returns:
            Dict containing knowledge operations results
        """
        return {
            "agent": "knowledge",
            "task_processed": task_description,
            "tools_used": self._tools,
            "knowledge_stored": True,
            "graph_operations": [],
            "documents_created": [],
            "filesystem_operations": []
        }

    async def close(self):
        """Close Graphiti and MCP bridge connections"""
        await self.graphiti.close()
        logger.info("Knowledge Agent closed")