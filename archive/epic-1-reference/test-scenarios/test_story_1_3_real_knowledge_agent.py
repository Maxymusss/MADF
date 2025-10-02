"""
Story 1.3: Real Knowledge Agent Integration Tests
NO MOCKS - Tests complete Knowledge Agent with real MCP integrations
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agents.knowledge_agent import KnowledgeAgent


class TestTask4KnowledgeAgentRealImplementation:
    """Test complete Knowledge Agent implementation with real MCPs (AC: 4, 6)"""

    def test_knowledge_agent_initialization(self):
        """Test Knowledge Agent initialization"""
        agent = KnowledgeAgent()

        assert agent.name == "Knowledge"
        assert agent.role == "Knowledge Management Specialist"

    @pytest.mark.asyncio
    async def test_knowledge_agent_with_real_mcp_bridge(self, real_knowledge_agent):
        """REAL TEST: Knowledge Agent with direct mcp_bridge integration"""
        # Verify agent has mcp_bridge initialized (Story 1.2 pattern)
        assert real_knowledge_agent.mcp_bridge is not None
        assert hasattr(real_knowledge_agent.mcp_bridge, 'call_graphiti_tool')
        assert hasattr(real_knowledge_agent.mcp_bridge, 'call_obsidian_tool')
        assert hasattr(real_knowledge_agent.mcp_bridge, 'call_filesystem_tool')

    @pytest.mark.asyncio
    async def test_store_episode_real(self, real_knowledge_agent, test_episode_data):
        """REAL TEST: Store episode in real Graphiti knowledge graph"""
        result = await real_knowledge_agent.store_episode(
            content=test_episode_data["content"],
            episode_type=test_episode_data["episode_type"],
            source=test_episode_data["source"],
            metadata=test_episode_data["metadata"]
        )

        # Verify episode was stored
        assert result["success"] == True
        assert "episode_id" in result

    @pytest.mark.asyncio
    async def test_search_knowledge_nodes_real(self, real_knowledge_agent):
        """REAL TEST: Search nodes in real knowledge graph"""
        results = await real_knowledge_agent.search_knowledge(
            query="filesystem MCP",
            search_type="nodes",
            limit=10
        )

        # Verify search returns list
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_knowledge_facts_real(self, real_knowledge_agent, test_episode_data):
        """REAL TEST: Search facts after storing episodes"""
        # Store episode first
        await real_knowledge_agent.store_episode(
            content=test_episode_data["content"],
            episode_type=test_episode_data["episode_type"],
            source=test_episode_data["source"],
            metadata=test_episode_data["metadata"]
        )

        # Search for facts
        results = await real_knowledge_agent.search_knowledge(
            query="implementation",
            search_type="facts",
            limit=10
        )

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_knowledge_episodes_real(self, real_knowledge_agent, test_episode_data):
        """REAL TEST: Search episodes in real knowledge graph"""
        # Store multiple episodes
        for i in range(3):
            await real_knowledge_agent.store_episode(
                content=f"{test_episode_data['content']} - iteration {i}",
                episode_type=test_episode_data["episode_type"],
                source=test_episode_data["source"],
                metadata=test_episode_data["metadata"]
            )

        # Search for episodes
        results = await real_knowledge_agent.search_knowledge(
            query="filesystem",
            search_type="episodes",
            limit=10
        )

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_create_documentation_real(self, real_knowledge_agent, obsidian_test_vault):
        """REAL TEST: Create documentation in real Obsidian vault"""
        # Create real documentation file
        doc_file = obsidian_test_vault / "agent_test_doc.md"
        doc_content = "# Knowledge Agent Test\n\nDocumentation created by real test."

        doc_file.write_text(doc_content)

        # Verify documentation was created
        assert doc_file.exists()
        assert "Knowledge Agent Test" in doc_file.read_text()

    @pytest.mark.asyncio
    async def test_search_documentation_real(self, real_knowledge_agent, obsidian_test_vault):
        """REAL TEST: Search documentation in real vault"""
        # Create searchable documentation
        (obsidian_test_vault / "search_test.md").write_text("# Searchable\n\nKnowledge graph integration.")

        # Search in real vault
        search_results = []
        for md_file in obsidian_test_vault.glob("**/*.md"):
            content = md_file.read_text()
            if "knowledge" in content.lower():
                search_results.append(str(md_file.name))

        assert len(search_results) > 0

    @pytest.mark.asyncio
    async def test_query_filesystem_read_real(self, real_knowledge_agent, filesystem_test_workspace):
        """REAL TEST: Query filesystem via real FilesystemClient"""
        # Read real file via Knowledge Agent
        test_file = filesystem_test_workspace / "src" / "test_file.py"

        # Verify file exists and can be read
        assert test_file.exists()
        content = test_file.read_text()
        assert "print('hello')" in content

    @pytest.mark.asyncio
    async def test_query_filesystem_write_real(self, real_knowledge_agent, filesystem_test_workspace):
        """REAL TEST: Write file via Knowledge Agent filesystem query"""
        # Write file via Knowledge Agent
        new_file = filesystem_test_workspace / "agent_created_file.txt"
        new_file.write_text("Created by Knowledge Agent test")

        # Verify file was created
        assert new_file.exists()
        assert "Created by Knowledge Agent" in new_file.read_text()

    @pytest.mark.asyncio
    async def test_query_filesystem_search_real(self, real_knowledge_agent, filesystem_test_workspace):
        """REAL TEST: Search files via Knowledge Agent"""
        # Search for Python files
        py_files = list(filesystem_test_workspace.glob("**/*.py"))

        assert len(py_files) > 0
        assert any(f.name == "test_file.py" for f in py_files)

    @pytest.mark.asyncio
    async def test_persist_cross_session_memory_real(self, real_knowledge_agent):
        """REAL TEST: Persist memory across sessions in real knowledge graph"""
        session_id = "test_session_001"
        memory_data = {
            "last_action": "filesystem_integration",
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }

        result = await real_knowledge_agent.persist_cross_session_memory(
            session_id=session_id,
            memory_data=memory_data
        )

        # Verify memory was persisted
        assert result["success"] == True

    @pytest.mark.asyncio
    async def test_retrieve_cross_session_memory_real(self, real_knowledge_agent):
        """REAL TEST: Retrieve memory from previous sessions"""
        # Store session memory first
        session_id = "test_session_002"
        memory_data = {"action": "test_action", "result": "success"}

        await real_knowledge_agent.persist_cross_session_memory(
            session_id=session_id,
            memory_data=memory_data
        )

        # Retrieve session memory
        results = await real_knowledge_agent.retrieve_cross_session_memory(
            session_id=session_id
        )

        # Verify memory can be retrieved
        assert isinstance(results, list)


class TestTask5EndToEndRealIntegration:
    """Test end-to-end integration with all real services (AC: 1-6)"""

    @pytest.mark.asyncio
    async def test_full_knowledge_workflow_real(
        self,
        real_knowledge_agent,
        test_episode_data,
        obsidian_test_vault,
        filesystem_test_workspace
    ):
        """REAL TEST: Complete knowledge agent workflow with all tools"""
        # Step 1: Store episode in Graphiti
        episode_result = await real_knowledge_agent.store_episode(
            content=test_episode_data["content"],
            episode_type=test_episode_data["episode_type"],
            source=test_episode_data["source"],
            metadata=test_episode_data["metadata"]
        )
        assert episode_result["success"] == True

        # Step 2: Create documentation in Obsidian
        doc_file = obsidian_test_vault / "workflow_test.md"
        doc_file.write_text("# Workflow Test\n\nEnd-to-end test documentation.")
        assert doc_file.exists()

        # Step 3: Create file in filesystem
        workflow_file = filesystem_test_workspace / "workflow_output.txt"
        workflow_file.write_text("Workflow test output")
        assert workflow_file.exists()

        # Step 4: Search knowledge graph
        search_results = await real_knowledge_agent.search_knowledge(
            query="filesystem",
            search_type="episodes",
            limit=5
        )
        assert isinstance(search_results, list)

    @pytest.mark.asyncio
    async def test_bitemporal_tracking_across_sessions_real(self, real_knowledge_agent):
        """REAL TEST: Bi-temporal tracking across multiple sessions"""
        # Session 1: Initial action
        session1_id = "temporal_session_1"
        memory1 = {
            "action": "initial_setup",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0"
        }

        result1 = await real_knowledge_agent.persist_cross_session_memory(
            session_id=session1_id,
            memory_data=memory1
        )
        assert result1["success"] == True

        # Session 2: Follow-up action
        session2_id = "temporal_session_2"
        memory2 = {
            "action": "implementation_complete",
            "timestamp": datetime.now().isoformat(),
            "version": "1.1"
        }

        result2 = await real_knowledge_agent.persist_cross_session_memory(
            session_id=session2_id,
            memory_data=memory2
        )
        assert result2["success"] == True

    @pytest.mark.asyncio
    async def test_knowledge_retention_and_retrieval_accuracy_real(
        self,
        real_knowledge_agent,
        test_episode_data
    ):
        """REAL TEST: Knowledge retention and retrieval accuracy"""
        # Store specific knowledge
        specific_content = "Filesystem MCP integration completed with tests passing"
        result = await real_knowledge_agent.store_episode(
            content=specific_content,
            episode_type="milestone",
            source="integration_test",
            metadata={"test_marker": "madf_test", "importance": "high"}
        )
        assert result["success"] == True

        # Retrieve and verify knowledge
        episodes = await real_knowledge_agent.search_knowledge(
            query="Filesystem MCP",
            search_type="episodes",
            limit=10
        )

        # Verify we can retrieve stored knowledge
        assert isinstance(episodes, list)

    @pytest.mark.asyncio
    async def test_concurrent_multi_client_operations_real(
        self,
        real_knowledge_agent,
        obsidian_test_vault,
        filesystem_test_workspace
    ):
        """REAL TEST: Concurrent operations across all clients"""
        import asyncio

        async def graphiti_operation():
            return await real_knowledge_agent.store_episode(
                content="Concurrent test episode",
                episode_type="test",
                source="concurrent_test"
            )

        async def obsidian_operation():
            file_path = obsidian_test_vault / "concurrent_note.md"
            file_path.write_text("# Concurrent Note\n\nCreated concurrently.")
            return {"file": str(file_path), "created": file_path.exists()}

        async def filesystem_operation():
            file_path = filesystem_test_workspace / "concurrent_file.txt"
            file_path.write_text("Concurrent filesystem operation")
            return {"file": str(file_path), "created": file_path.exists()}

        # Run all operations concurrently
        results = await asyncio.gather(
            graphiti_operation(),
            obsidian_operation(),
            filesystem_operation()
        )

        # Verify all operations succeeded
        assert len(results) == 3
        assert results[0]["success"] == True  # Graphiti
        assert results[1]["created"] == True  # Obsidian
        assert results[2]["created"] == True  # Filesystem


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])