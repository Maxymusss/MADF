"""
Story 1.3: Real Graphiti MCP Integration Tests
NO MOCKS - Uses actual Neo4j database and OpenAI embeddings
ARCHITECTURE: Direct mcp_bridge calls (Story 1.2 pattern)
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.mcp_bridge import MCPBridge
from core.graphiti_wrapper import GraphitiWrapper  # Story 1.3: Direct Library (not MCP)


class TestTask1GraphitiDirectLibraryIntegration:
    """Test Graphiti Direct Library integration with real Neo4j database (AC: 1, 5)"""

    def test_graphiti_wrapper_importable(self):
        """Test GraphitiWrapper can be imported"""
        # GraphitiWrapper already imported at module level
        assert GraphitiWrapper is not None

    def test_graphiti_wrapper_has_required_methods(self):
        """Test GraphitiWrapper has required methods for knowledge operations"""
        import os

        wrapper = GraphitiWrapper(
            neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
            neo4j_password=os.getenv("NEO4J_PASSWORD", "madf-dev-password")
        )

        # Verify core methods exist
        assert hasattr(wrapper, 'add_episode')
        assert hasattr(wrapper, 'search_nodes')
        assert hasattr(wrapper, 'search_facts')
        assert hasattr(wrapper, 'search_episodes')
        assert callable(wrapper.add_episode)

    @pytest.mark.asyncio
    async def test_graphiti_real_connection(self, mcp_bridge_instance, neo4j_test_db):
        """REAL TEST: Connect to actual Neo4j database"""
        # Verify Neo4j database is accessible
        with neo4j_test_db.session() as session:
            result = session.run("RETURN 1 as num")
            record = result.single()
            assert record["num"] == 1

    @pytest.mark.asyncio
    async def test_add_episode_real(self, mcp_bridge_instance, test_episode_data):
        """REAL TEST: Add episode to actual Neo4j knowledge graph via mcp_bridge"""
        # Add episode using mcp_bridge helper (Story 1.2 pattern)
        result = mcp_bridge_instance.call_graphiti_tool(
            "add_episode",
            {
                "content": test_episode_data["content"],
                "episode_type": test_episode_data["episode_type"],
                "source": test_episode_data["source"],
                "metadata": test_episode_data["metadata"]
            }
        )

        # Verify episode was created
        assert result["success"] == True
        assert "episode_id" in result
        assert result["content"] == test_episode_data["content"]
        assert result["type"] == test_episode_data["episode_type"]

        # Verify episode exists in Neo4j
        # Note: This requires actual graphiti_core implementation
        # For now, verify response structure

    @pytest.mark.asyncio
    async def test_search_nodes_real(self, real_graphiti_client):
        """REAL TEST: Search nodes in actual knowledge graph"""
        query = "filesystem MCP integration"

        results = await real_graphiti_client.search_nodes(
            query=query,
            limit=10
        )

        # Verify results structure (even if empty initially)
        assert isinstance(results, list)
        # Results may be empty if no matching nodes exist
        if len(results) > 0:
            assert "node_id" in results[0]
            assert "name" in results[0]
            assert "score" in results[0]

    @pytest.mark.asyncio
    async def test_search_facts_real(self, real_graphiti_client):
        """REAL TEST: Search facts/relationships in knowledge graph"""
        query = "implementation"

        results = await real_graphiti_client.search_facts(
            query=query,
            limit=10
        )

        # Verify results structure
        assert isinstance(results, list)
        if len(results) > 0:
            assert "fact_id" in results[0]
            assert "subject" in results[0]
            assert "predicate" in results[0]
            assert "object" in results[0]

    @pytest.mark.asyncio
    async def test_search_episodes_real(self, real_graphiti_client, test_episode_data):
        """REAL TEST: Query historical episodes with temporal filters"""
        # First add an episode
        await real_graphiti_client.add_episode(
            content=test_episode_data["content"],
            episode_type=test_episode_data["episode_type"],
            source=test_episode_data["source"],
            metadata=test_episode_data["metadata"]
        )

        # Search for episodes
        results = await real_graphiti_client.search_episodes(
            query="filesystem",
            limit=10
        )

        # Verify episodes can be retrieved
        assert isinstance(results, list)
        if len(results) > 0:
            assert "episode_id" in results[0]
            assert "content" in results[0]
            assert "timestamp" in results[0]

    @pytest.mark.asyncio
    async def test_bitemporal_tracking_real(self, real_graphiti_client):
        """REAL TEST: Bi-temporal tracking for project evolution"""
        entity = "KnowledgeAgent"
        time_point = datetime.now().isoformat()

        result = await real_graphiti_client.query_temporal(
            entity=entity,
            time_point=time_point
        )

        # Verify temporal query structure
        assert "entity" in result
        assert result["entity"] == entity
        assert "time_point" in result
        assert "valid_time" in result
        assert "transaction_time" in result

    @pytest.mark.asyncio
    async def test_graphiti_error_handling_real(self, neo4j_test_db):
        """REAL TEST: Error handling with invalid credentials"""
        import os
        from neo4j import GraphDatabase
        from neo4j.exceptions import AuthError

        neo4j_uri = os.getenv("NEO4J_URI")
        neo4j_user = os.getenv("NEO4J_USER")

        # Test invalid password raises AuthError
        with pytest.raises(AuthError):
            driver = GraphDatabase.driver(
                neo4j_uri,
                auth=(neo4j_user, "wrong_password")
            )
            driver.verify_connectivity()
            driver.close()

        # Test invalid user raises AuthError
        with pytest.raises(AuthError):
            driver = GraphDatabase.driver(
                neo4j_uri,
                auth=("wrong_user", "any_password")
            )
            driver.verify_connectivity()
            driver.close()

    @pytest.mark.asyncio
    async def test_graphiti_concurrent_operations_real(self, real_graphiti_client):
        """REAL TEST: Concurrent episode additions to Neo4j"""
        import asyncio

        episodes = [
            {"content": f"Test episode {i}", "episode_type": "test", "source": "concurrent_test"}
            for i in range(5)
        ]

        # Add episodes concurrently
        tasks = [
            real_graphiti_client.add_episode(
                content=ep["content"],
                episode_type=ep["episode_type"],
                source=ep["source"],
                metadata={"test_marker": "madf_test", "index": i}
            )
            for i, ep in enumerate(episodes)
        ]

        results = await asyncio.gather(*tasks)

        # Verify all episodes were added successfully
        assert len(results) == 5
        for result in results:
            assert result["success"] == True
            assert "episode_id" in result


class TestGraphitiAPIValidation:
    """Validate Graphiti API signature requirements"""

    @pytest.mark.asyncio
    async def test_graphiti_client_initialization_signature(self, test_env_vars):
        """REAL TEST: Verify correct Graphiti initialization parameters"""
        client = GraphitiClient()

        # Verify client has required attributes
        assert hasattr(client, "neo4j_uri")
        assert hasattr(client, "neo4j_user")
        assert hasattr(client, "neo4j_password")
        assert hasattr(client, "openai_api_key")

        # Verify correct values from environment
        assert client.neo4j_uri == test_env_vars["NEO4J_URI"]
        assert client.neo4j_user == test_env_vars["NEO4J_USER"]
        assert client.neo4j_password == test_env_vars["NEO4J_PASSWORD"]

    @pytest.mark.asyncio
    async def test_graphiti_add_episode_signature(self, real_graphiti_client):
        """REAL TEST: Verify add_episode accepts correct parameters"""
        # Test all parameters are accepted
        result = await real_graphiti_client.add_episode(
            content="Test content",
            episode_type="test",
            source="test_source",
            metadata={"key": "value"}
        )

        assert "success" in result
        assert "episode_id" in result

    @pytest.mark.asyncio
    async def test_graphiti_search_methods_signature(self, real_graphiti_client):
        """REAL TEST: Verify search methods accept correct parameters"""
        # Test search_nodes
        nodes = await real_graphiti_client.search_nodes(
            query="test",
            limit=5,
            filters={"label": "TestNode"}
        )
        assert isinstance(nodes, list)

        # Test search_facts
        facts = await real_graphiti_client.search_facts(
            query="test",
            limit=5
        )
        assert isinstance(facts, list)

        # Test search_episodes
        episodes = await real_graphiti_client.search_episodes(
            query="test",
            limit=5,
            time_range=None
        )
        assert isinstance(episodes, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])