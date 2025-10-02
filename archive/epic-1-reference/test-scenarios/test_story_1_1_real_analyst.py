"""
Story 1.1: Real Analyst Agent Tests
NO MOCKS - Tests with real Context7, Serena, Sequential Thinking MCP connections
"""

import pytest
import os
from pathlib import Path


@pytest.fixture
async def real_analyst_agent():
    """Initialize Analyst with real MCP clients"""
    from src.agents.analyst_agent import AnalystAgent

    # Verify environment variables
    assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY required for real tests"

    agent = AnalystAgent()
    await agent.initialize_real_mcp_clients()

    yield agent

    await agent.cleanup()


class TestRealAnalystContext7:
    """Real Context7 MCP integration tests"""

    @pytest.mark.asyncio
    async def test_context7_client_initialization(self, real_analyst_agent):
        """REAL TEST: Verify Context7 MCP client initializes"""
        assert real_analyst_agent.context7_client is not None
        assert real_analyst_agent.context7_client._initialized

    @pytest.mark.asyncio
    async def test_store_context_real(self, real_analyst_agent):
        """REAL TEST: Store code context via Context7 MCP"""
        context_data = {
            "file_path": "src/core/agent_graph.py",
            "content": "LangGraph StateGraph implementation",
            "tags": ["langgraph", "architecture", "story-1.1"],
            "metadata": {
                "story": "1.1",
                "component": "core"
            }
        }

        result = await real_analyst_agent.store_context(context_data)

        # Verify context stored successfully
        assert result["success"] == True
        assert "context_id" in result

    @pytest.mark.asyncio
    async def test_retrieve_context_real(self, real_analyst_agent):
        """REAL TEST: Retrieve stored context via Context7 MCP"""
        # First store context
        context_data = {
            "file_path": "src/agents/analyst_agent.py",
            "content": "Analyst agent for semantic code search",
            "tags": ["analyst", "agent"],
            "metadata": {"type": "agent"}
        }

        store_result = await real_analyst_agent.store_context(context_data)
        context_id = store_result["context_id"]

        # Now retrieve it
        retrieved = await real_analyst_agent.retrieve_context(context_id)

        # Verify retrieved data matches
        assert retrieved["context_id"] == context_id
        assert "content" in retrieved
        assert "analyst" in str(retrieved).lower()

    @pytest.mark.asyncio
    async def test_semantic_search_real(self, real_analyst_agent):
        """REAL TEST: Semantic search across stored contexts"""
        # Store multiple contexts first
        contexts = [
            {
                "file_path": "src/core/state_models.py",
                "content": "Pydantic models for agent state management",
                "tags": ["pydantic", "state"]
            },
            {
                "file_path": "src/core/agent_graph.py",
                "content": "LangGraph StateGraph orchestration",
                "tags": ["langgraph", "orchestration"]
            }
        ]

        for ctx in contexts:
            await real_analyst_agent.store_context(ctx)

        # Execute semantic search
        results = await real_analyst_agent.semantic_search(
            query="Pydantic state management",
            limit=5
        )

        # Verify search returns relevant results
        assert isinstance(results, list)
        assert len(results) > 0
        assert any("pydantic" in str(r).lower() for r in results)


class TestRealAnalystSequentialThinking:
    """Real Sequential Thinking MCP integration tests"""

    @pytest.mark.asyncio
    async def test_sequential_thinking_client_initialization(self, real_analyst_agent):
        """REAL TEST: Verify Sequential Thinking MCP client initializes"""
        assert real_analyst_agent.sequential_thinking_client is not None
        assert real_analyst_agent.sequential_thinking_client._initialized

    @pytest.mark.asyncio
    async def test_analyze_code_structure_real(self, real_analyst_agent):
        """REAL TEST: Analyze code structure with sequential thinking"""
        code_snippet = """
from langgraph.graph import StateGraph, START, END
from .state_models import AgentState

def create_agent_graph():
    graph = StateGraph(AgentState)
    graph.add_node("orchestrator", orchestrator_node)
    return graph
"""

        result = await real_analyst_agent.analyze_code_with_thinking(
            code=code_snippet,
            analysis_type="structure"
        )

        # Verify analysis completed
        assert result["success"] == True
        assert "thinking_steps" in result
        assert "analysis" in result
        assert len(result["thinking_steps"]) > 0

    @pytest.mark.asyncio
    async def test_plan_refactoring_real(self, real_analyst_agent):
        """REAL TEST: Generate refactoring plan with sequential thinking"""
        refactoring_task = {
            "file": "src/core/agent_graph.py",
            "current_structure": "Function-based agent nodes",
            "desired_structure": "Class-based agent nodes with inheritance",
            "reason": "Better code organization and reusability"
        }

        result = await real_analyst_agent.plan_refactoring_with_thinking(
            task=refactoring_task
        )

        # Verify planning output
        assert result["success"] == True
        assert "plan_steps" in result
        assert "reasoning" in result
        assert len(result["plan_steps"]) > 0


class TestRealAnalystSerena:
    """Real Serena MCP integration tests"""

    @pytest.mark.asyncio
    async def test_serena_client_initialization(self, real_analyst_agent):
        """REAL TEST: Verify Serena MCP client initializes"""
        assert real_analyst_agent.serena_client is not None
        assert real_analyst_agent.serena_client._initialized

    @pytest.mark.asyncio
    async def test_search_codebase_real(self, real_analyst_agent):
        """REAL TEST: Search codebase via Serena MCP"""
        result = await real_analyst_agent.search_codebase(
            query="AgentState",
            search_type="symbol"
        )

        # Verify search results
        assert isinstance(result, list)
        assert len(result) > 0

        # Check result structure
        first_result = result[0]
        assert "file_path" in first_result
        assert "line_number" in first_result
        assert "match" in first_result

    @pytest.mark.asyncio
    async def test_find_references_real(self, real_analyst_agent):
        """REAL TEST: Find symbol references via Serena MCP"""
        result = await real_analyst_agent.find_references(
            symbol="create_agent_graph",
            file_path="src/core/agent_graph.py"
        )

        # Verify references found
        assert isinstance(result, list)
        # May be empty if not imported elsewhere, but should return list
        assert isinstance(result, list)


class TestRealAnalystWorkflow:
    """Real analysis workflow integration tests"""

    @pytest.mark.asyncio
    async def test_comprehensive_code_analysis_real(self, real_analyst_agent):
        """REAL TEST: Complete code analysis workflow"""
        analysis_request = {
            "target": "src/core/agent_graph.py",
            "analysis_types": ["structure", "dependencies", "complexity"]
        }

        # Step 1: Search for file
        search_result = await real_analyst_agent.search_codebase(
            query="agent_graph.py",
            search_type="file"
        )
        assert len(search_result) > 0

        # Step 2: Analyze structure with sequential thinking
        structure_analysis = await real_analyst_agent.analyze_code_with_thinking(
            code=search_result[0]["content"],
            analysis_type="structure"
        )
        assert structure_analysis["success"]

        # Step 3: Store analysis in context
        context_result = await real_analyst_agent.store_context({
            "file_path": "src/core/agent_graph.py",
            "content": structure_analysis["analysis"],
            "tags": ["analysis", "architecture"],
            "metadata": {
                "analyzed_at": "2025-09-30",
                "story": "1.1"
            }
        })
        assert context_result["success"]

        # Verify complete workflow
        assert search_result is not None
        assert structure_analysis["success"]
        assert context_result["success"]

    @pytest.mark.asyncio
    async def test_delegate_to_knowledge_agent_real(self, real_analyst_agent):
        """REAL TEST: Analyst delegates findings to Knowledge agent"""
        # Analyze code
        analysis = await real_analyst_agent.analyze_code_with_thinking(
            code="from langgraph.graph import StateGraph",
            analysis_type="imports"
        )

        # Delegate to Knowledge for persistence
        delegation = await real_analyst_agent.delegate_to_agent(
            target_agent="knowledge",
            task="Store code analysis in knowledge graph",
            context={
                "analysis": analysis["analysis"],
                "file": "src/core/agent_graph.py"
            }
        )

        # Verify delegation
        assert delegation["target_agent"] == "knowledge"
        assert delegation["status"] == "delegated"
        assert "context" in delegation


class TestRealAnalystErrorHandling:
    """Real error handling tests"""

    @pytest.mark.asyncio
    async def test_invalid_code_analysis_handling(self, real_analyst_agent):
        """REAL TEST: Handle malformed code gracefully"""
        malformed_code = "def incomplete_function("

        result = await real_analyst_agent.analyze_code_with_thinking(
            code=malformed_code,
            analysis_type="structure"
        )

        # Should handle gracefully with error indication
        assert result["success"] == False or "error" in result

    @pytest.mark.asyncio
    async def test_nonexistent_file_search_handling(self, real_analyst_agent):
        """REAL TEST: Handle search for non-existent files"""
        result = await real_analyst_agent.search_codebase(
            query="nonexistent_file_12345.py",
            search_type="file"
        )

        # Should return empty list, not raise error
        assert isinstance(result, list)
        assert len(result) == 0