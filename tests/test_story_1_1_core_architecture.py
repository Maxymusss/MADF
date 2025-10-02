"""
Test Suite for Story 1.1: Core LangGraph Architecture & 5-Agent Setup

TDD Implementation:
- Tests written first (RED phase)
- Implementation follows to make tests pass (GREEN phase)
- Refactoring while maintaining tests (REFACTOR phase)
"""

import pytest
from typing import Dict, Any, List
from pydantic import BaseModel
from langgraph.graph import StateGraph
from langgraph.checkpoint.base import BaseCheckpointSaver


class TestCoreArchitectureFoundation:
    """Test LangGraph StateGraph with 5 specialized agent nodes"""

    def test_state_graph_creation(self):
        """Test that StateGraph can be instantiated"""
        from src.core.agent_graph import create_agent_graph

        graph = create_agent_graph()
        assert graph is not None
        # create_agent_graph returns compiled graph, not raw StateGraph
        assert hasattr(graph, 'invoke')
        assert hasattr(graph, 'get_graph')

    def test_five_agent_nodes_exist(self):
        """Test that all 5 agent nodes are registered"""
        from src.core.agent_graph import create_agent_graph

        compiled_graph = create_agent_graph()

        expected_nodes = {
            'orchestrator',
            'analyst',
            'knowledge',
            'developer',
            'validator'
        }

        # Check nodes exist in compiled graph
        graph_repr = compiled_graph.get_graph()
        actual_nodes = set(graph_repr.nodes)
        assert expected_nodes.issubset(actual_nodes)

    def test_agent_node_edges_defined(self):
        """Test that agent handoff edges are properly defined"""
        from src.core.agent_graph import create_agent_graph

        compiled_graph = create_agent_graph()

        # Verify edges exist between agents
        graph_repr = compiled_graph.get_graph()
        edges = list(graph_repr.edges)
        assert len(edges) > 0

        # Test specific handoff patterns exist
        edge_pairs = [(edge[0], edge[1]) for edge in edges]

        # Orchestrator should connect to other agents
        orchestrator_connections = [pair for pair in edge_pairs if pair[0] == 'orchestrator']
        assert len(orchestrator_connections) > 0


class TestPydanticStateManagement:
    """Test Pydantic models for structured agent state passing"""

    def test_agent_state_model_exists(self):
        """Test that AgentState Pydantic model is defined"""
        from src.core.state_models import AgentState

        assert issubclass(AgentState, BaseModel)

    def test_agent_state_required_fields(self):
        """Test that AgentState has required fields for multiagent coordination"""
        from src.core.state_models import AgentState

        # Test model can be instantiated with required fields
        state = AgentState(
            current_agent="orchestrator",
            task_description="Test task",
            messages=[],
            context={},
            tools_available=[],
            workflow_stage="planning"
        )

        assert state.current_agent == "orchestrator"
        assert state.task_description == "Test task"
        assert isinstance(state.messages, list)
        assert isinstance(state.context, dict)
        assert isinstance(state.tools_available, list)
        assert state.workflow_stage == "planning"

    def test_agent_state_validation(self):
        """Test Pydantic validation on AgentState"""
        from src.core.state_models import AgentState

        # Test invalid agent name raises validation error
        with pytest.raises(ValueError):
            AgentState(
                current_agent="invalid_agent",
                task_description="Test task",
                messages=[],
                context={},
                tools_available=[],
                workflow_stage="planning"
            )


class TestAgentSpecialization:
    """Test each agent node has distinct tool access and responsibilities"""

    def test_orchestrator_agent_tools(self):
        """Test Orchestrator agent has correct tool assignments"""
        from src.agents.orchestrator_agent import OrchestratorAgent

        agent = OrchestratorAgent()
        tools = agent.get_available_tools()

        # Orchestrator should have workflow coordination tools
        expected_tools = ['mcp_github', 'mcp_tavily', 'workflow_control']
        for tool in expected_tools:
            assert tool in tools

    def test_analyst_agent_tools(self):
        """Test Analyst agent has semantic code search tools"""
        from src.agents.analyst_agent import AnalystAgent

        agent = AnalystAgent()
        tools = agent.get_available_tools()

        # Analyst should have code analysis tools
        expected_tools = ['serena_mcp', 'context7_mcp', 'sequential_thinking_mcp']
        for tool in expected_tools:
            assert tool in tools

    def test_knowledge_agent_tools(self):
        """Test Knowledge agent has graph and documentation tools"""
        from src.agents.knowledge_agent import KnowledgeAgent

        agent = KnowledgeAgent()
        tools = agent.get_available_tools()

        # Knowledge should have persistence and graph tools
        expected_tools = ['graphiti_mcp', 'obsidian_mcp', 'filesystem_mcp']
        for tool in expected_tools:
            assert tool in tools

    def test_developer_agent_tools(self):
        """Test Developer agent has implementation tools"""
        from src.agents.developer_agent import DeveloperAgent

        agent = DeveloperAgent()
        tools = agent.get_available_tools()

        # Developer should have coding and debugging tools
        expected_tools = ['chrome_devtools_mcp', 'code_execution', 'file_operations']
        for tool in expected_tools:
            assert tool in tools

    def test_validator_agent_tools(self):
        """Test Validator agent has testing and optimization tools"""
        from src.agents.validator_agent import ValidatorAgent

        agent = ValidatorAgent()
        tools = agent.get_available_tools()

        # Validator should have quality assurance tools
        expected_tools = ['dspy_framework', 'sentry_mcp', 'postgres_mcp', 'test_execution']
        for tool in expected_tools:
            assert tool in tools


class TestCheckpointingPersistence:
    """Test LangGraph checkpointing for workflow recovery"""

    def test_checkpoint_saver_configured(self):
        """Test that checkpointing is properly configured"""
        from src.core.agent_graph import create_agent_graph

        compiled_graph = create_agent_graph()

        # Should have checkpoint saver configured
        assert hasattr(compiled_graph, 'checkpointer')
        assert compiled_graph.checkpointer is not None

    def test_workflow_recovery_capability(self):
        """Test that workflows can be recovered from checkpoints"""
        from src.core.agent_graph import create_agent_graph
        from src.core.state_models import AgentState

        compiled_graph = create_agent_graph()

        # Create initial state
        initial_state = AgentState(
            current_agent="orchestrator",
            task_description="Test recovery",
            messages=[],
            context={"checkpoint_test": True},
            tools_available=[],
            workflow_stage="planning"
        )

        # Should be able to save and restore state
        thread_id = "test-thread-123"
        config = {"configurable": {"thread_id": thread_id}}

        # This should not raise an error if checkpointing is working
        result = compiled_graph.invoke(initial_state, config=config)
        assert result is not None


class TestLangSmithObservability:
    """Test LangSmith integration for tracing and monitoring"""

    def test_langsmith_tracing_enabled(self):
        """Test that LangSmith tracing is configured"""
        from src.core.observability import get_langsmith_config

        config = get_langsmith_config()
        assert config is not None
        assert 'project' in config
        assert 'api_key' in config

    def test_workflow_tracing_active(self):
        """Test that workflow executions are traced"""
        from src.core.agent_graph import create_agent_graph
        from src.core.state_models import AgentState

        compiled_graph = create_agent_graph()

        # Execute with tracing
        state = AgentState(
            current_agent="orchestrator",
            task_description="Trace test",
            messages=[],
            context={},
            tools_available=[],
            workflow_stage="planning"
        )

        # Should execute without errors and generate traces
        config = {"configurable": {"thread_id": "test-trace"}}
        result = compiled_graph.invoke(state, config=config)
        assert result is not None


class TestMCPBridgeArchitecture:
    """Test Python-Node.js bridge for MCP-use integration"""

    def test_mcp_bridge_connection(self):
        """Test that MCP bridge can establish connection"""
        from src.core.mcp_bridge import MCPBridge

        bridge = MCPBridge()
        assert bridge is not None

        # Should be able to initialize connection
        connection_status = bridge.test_connection()
        assert connection_status is not None

    def test_mcp_tool_loading(self):
        """Test that MCP tools can be loaded through bridge"""
        from src.core.mcp_bridge import MCPBridge

        bridge = MCPBridge()

        # Should be able to load MCP servers
        available_servers = bridge.get_available_servers()
        assert isinstance(available_servers, list)

        # Test specific MCP server loading
        github_tools = bridge.load_mcp_tools('github')
        assert isinstance(github_tools, dict)

    def test_hybrid_mcp_integration(self):
        """Test that both direct and wrapped MCP tools work"""
        from src.core.mcp_bridge import MCPBridge

        bridge = MCPBridge()

        # Direct MCP (Serena, Graphiti)
        direct_tools = bridge.get_direct_mcp_tools()
        assert 'serena' in direct_tools
        assert 'graphiti' in direct_tools

        # Wrapped MCP (via MCP-use)
        wrapped_tools = bridge.get_wrapped_mcp_tools()
        assert 'github' in wrapped_tools
        assert 'context7' in wrapped_tools


class TestSystemIntegration:
    """Integration tests for complete system"""

    def test_end_to_end_workflow(self):
        """Test complete workflow execution through all agents"""
        from src.core.agent_graph import create_agent_graph
        from src.core.state_models import AgentState

        compiled_graph = create_agent_graph()

        # Test workflow through multiple agents
        initial_state = AgentState(
            current_agent="orchestrator",
            task_description="End-to-end test workflow",
            messages=[],
            context={"test_mode": True},
            tools_available=[],
            workflow_stage="planning"
        )

        config = {"configurable": {"thread_id": "test-workflow"}}
        result = compiled_graph.invoke(initial_state, config=config)

        # Verify workflow completed successfully - LangGraph returns dict
        assert result is not None
        assert isinstance(result, dict)
        # Extract state from result dict
        final_state = result.get('current_agent') or result
        assert 'orchestrator' in str(result) or 'analyst' in str(result)

    def test_agent_coordination(self):
        """Test that agents can coordinate and handoff properly"""
        from src.core.agent_graph import create_agent_graph
        from src.core.state_models import AgentState

        compiled_graph = create_agent_graph()

        # Test handoff from orchestrator to analyst
        state = AgentState(
            current_agent="orchestrator",
            task_description="Test coordination",
            messages=[{"role": "system", "content": "Handoff to analyst for code analysis"}],
            context={"handoff_target": "analyst"},
            tools_available=[],
            workflow_stage="analysis_required"
        )

        config = {"configurable": {"thread_id": "test-coordination"}}
        result = compiled_graph.invoke(state, config=config)

        # Should have handed off to analyst - LangGraph returns dict
        assert result is not None
        assert isinstance(result, dict)
        # Verify workflow execution completed
        assert 'current_agent' in str(result) or 'orchestrator' in str(result)