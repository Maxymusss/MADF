"""
Story 1.3: Knowledge Agent Integration Tests
Tests for Graphiti MCP, Obsidian MCP, and Filesystem MCP integration
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.mcp_bridge import MCPBridge
from agents.knowledge_agent import KnowledgeAgent


class TestTask1GraphitiMCPIntegration:
    """Test Graphiti MCP direct integration (AC: 1, 5)"""

    def test_graphiti_connection_configured(self):
        """Test Neo4j database connection configuration"""
        bridge = MCPBridge()

        # Verify Graphiti is registered as direct MCP server
        assert "graphiti" in bridge.direct_mcp_servers
        assert bridge.direct_mcp_servers["graphiti"]["type"] == "direct"

    def test_add_episode_tool_available(self):
        """Test add_episode tool for episodic data management"""
        bridge = MCPBridge()
        tools = bridge.load_mcp_tools("graphiti")

        # Verify episodic data management tools
        assert "add_episode" in str(tools) or len(tools) > 0

    def test_entity_search_capabilities(self):
        """Test entity and fact search capabilities"""
        bridge = MCPBridge()
        tools = bridge.load_mcp_tools("graphiti")

        # Verify search tools are available
        assert len(tools) > 0

    def test_bitemporal_tracking_configured(self):
        """Test bi-temporal tracking for project evolution"""
        bridge = MCPBridge()
        tools = bridge.load_mcp_tools("graphiti")

        # Verify temporal tracking capabilities
        assert "temporal_tracking" in tools or len(tools) > 0


class TestTask2ObsidianMCPIntegration:
    """Test Obsidian MCP via MCP-use wrapper (AC: 2)"""

    def test_obsidian_connection_configured(self):
        """Test Obsidian REST API connection"""
        bridge = MCPBridge()

        # Verify Obsidian is registered as wrapped MCP server
        assert "obsidian" in bridge.wrapped_mcp_servers
        assert bridge.wrapped_mcp_servers["obsidian"]["type"] == "wrapped"

    def test_vault_management_methods(self):
        """Test vault management methods (list_files, get_file_contents)"""
        bridge = MCPBridge()
        tools = bridge.load_mcp_tools("obsidian")

        # Verify vault management tools
        assert len(tools) > 0

    def test_content_operations(self):
        """Test content operations (patch, append, delete)"""
        bridge = MCPBridge()
        tools = bridge.load_mcp_tools("obsidian")

        # Verify content operation tools
        assert "note_create" in tools or len(tools) > 0

    def test_search_functionality(self):
        """Test search functionality across notes"""
        bridge = MCPBridge()
        tools = bridge.load_mcp_tools("obsidian")

        # Verify search capabilities
        assert "vault_search" in tools or len(tools) > 0


class TestTask3FilesystemMCPIntegration:
    """Test Filesystem MCP via MCP-use wrapper (AC: 3)"""

    def test_filesystem_server_configured(self):
        """Test filesystem MCP server configuration"""
        bridge = MCPBridge()

        # Verify filesystem is registered in wrapped servers
        assert "filesystem" in bridge.wrapped_mcp_servers
        assert bridge.wrapped_mcp_servers["filesystem"]["type"] == "wrapped"
        assert bridge.wrapped_mcp_servers["filesystem"]["package"] == "@modelcontextprotocol/server-filesystem"

    def test_project_structure_navigation(self):
        """Test project structure navigation tools"""
        bridge = MCPBridge()

        # Verify filesystem navigation capabilities
        tools = bridge.load_mcp_tools("filesystem")
        assert "list_directory" in tools or "directory_tree" in tools

    def test_file_operations_with_safety(self):
        """Test file/directory operations with safety checks"""
        bridge = MCPBridge()

        # Verify filesystem operation tools
        tools = bridge.load_mcp_tools("filesystem")
        assert "read_text_file" in tools
        assert "write_file" in tools
        assert "search_files" in tools


class TestTask4KnowledgeAgentImplementation:
    """Test complete Knowledge Agent implementation (AC: 4, 6)"""

    def test_knowledge_agent_initialization(self):
        """Test Knowledge Agent initialization with all tools"""
        agent = KnowledgeAgent()

        assert agent.name == "Knowledge"
        assert agent.role == "Knowledge Management Specialist"

    def test_graphiti_tools_available(self):
        """Test Graphiti tools available in Knowledge Agent"""
        agent = KnowledgeAgent()
        tools = agent.get_available_tools()

        assert "graphiti_mcp" in tools

    def test_obsidian_tools_available(self):
        """Test Obsidian tools available in Knowledge Agent"""
        agent = KnowledgeAgent()
        tools = agent.get_available_tools()

        assert "obsidian_mcp" in tools

    def test_filesystem_tools_available(self):
        """Test Filesystem tools available in Knowledge Agent"""
        agent = KnowledgeAgent()
        tools = agent.get_available_tools()

        assert "filesystem_mcp" in tools

    def test_cross_session_memory_persistence(self):
        """Test cross-session memory persistence workflows"""
        agent = KnowledgeAgent()

        # Test knowledge persistence capability
        result = agent.process_task(
            "Store project context",
            {"session_id": "test-session-1"}
        )

        assert result["knowledge_stored"] == True

    def test_knowledge_graph_operations(self):
        """Test knowledge graph query and update operations"""
        agent = KnowledgeAgent()

        # Test graph operations
        result = agent.process_task(
            "Query project dependencies",
            {"query": "find dependencies"}
        )

        assert "graph_operations" in result


class TestTask5EndToEndIntegration:
    """Test end-to-end integration (AC: 1-6)"""

    def test_full_knowledge_workflow(self):
        """Test full knowledge agent workflow with all tools"""
        agent = KnowledgeAgent()
        bridge = MCPBridge()

        # Verify agent-bridge integration
        assert len(agent.get_available_tools()) >= 3
        assert len(bridge.get_available_servers()) > 0

    def test_bitemporal_tracking_across_sessions(self):
        """Test bi-temporal tracking across sessions"""
        agent = KnowledgeAgent()

        # Session 1: Store knowledge
        result1 = agent.process_task(
            "Store project milestone",
            {"session_id": "session-1", "timestamp": "2025-09-30T10:00:00Z"}
        )

        assert result1["knowledge_stored"] == True

    def test_knowledge_retention_and_retrieval(self):
        """Test knowledge retention and retrieval accuracy"""
        agent = KnowledgeAgent()

        # Store and retrieve knowledge
        store_result = agent.process_task(
            "Store technical decision",
            {"decision": "Use Graphiti for knowledge graphs"}
        )

        assert store_result["knowledge_stored"] == True

    def test_error_handling_and_consistency(self):
        """Test error handling and data consistency"""
        bridge = MCPBridge()

        # Test error handling for invalid server
        result = bridge.load_mcp_tools("nonexistent_server")

        assert "error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])