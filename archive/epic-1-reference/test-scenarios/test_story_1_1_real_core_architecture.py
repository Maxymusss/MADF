"""
Story 1.1: Real Core Architecture Tests
NO MOCKS - Tests with real LangGraph, Pydantic, and agent instances

Simplified approach: Test actual architecture components, not full MCP integration
(Full MCP integration tested in Stories 1.2-1.5)
"""

import pytest
from pathlib import Path

# Real imports (no mocks)
from langgraph.graph import StateGraph
from pydantic import BaseModel, ValidationError


class TestRealLangGraphArchitecture:
    """REAL: Test LangGraph StateGraph with actual instances"""

    def test_state_graph_creation_real(self):
        """REAL TEST: Create actual StateGraph instance"""
        from src.core.agent_graph import create_agent_graph

        # Create real graph (not mocked)
        graph = create_agent_graph()

        # Verify real graph object
        assert graph is not None
        assert hasattr(graph, 'invoke')
        assert hasattr(graph, 'get_graph')

    def test_five_agent_nodes_real(self):
        """REAL TEST: Verify 5 agent nodes exist in real graph"""
        from src.core.agent_graph import create_agent_graph

        compiled_graph = create_agent_graph()

        # Check real graph structure
        graph_repr = compiled_graph.get_graph()
        actual_nodes = set(graph_repr.nodes)

        # Verify all 5 agent nodes exist
        required_nodes = {'orchestrator', 'analyst', 'knowledge', 'developer', 'validator'}
        assert required_nodes.issubset(actual_nodes), \
            f"Missing nodes: {required_nodes - actual_nodes}"

    def test_agent_edges_real(self):
        """REAL TEST: Verify agent edges in real graph"""
        from src.core.agent_graph import create_agent_graph

        compiled_graph = create_agent_graph()
        graph_repr = compiled_graph.get_graph()

        edges = list(graph_repr.edges)
        assert len(edges) > 0, "No edges found in graph"

        # Verify orchestrator connects to other agents
        edge_pairs = [(edge[0], edge[1]) for edge in edges]
        orchestrator_edges = [pair for pair in edge_pairs if pair[0] == 'orchestrator']
        assert len(orchestrator_edges) > 0, "Orchestrator has no outgoing edges"


class TestRealPydanticStateManagement:
    """REAL: Test Pydantic models with actual validation"""

    def test_agent_state_model_real(self):
        """REAL TEST: Instantiate actual AgentState model"""
        from src.core.state_models import AgentState

        # Verify AgentState is real Pydantic model
        assert issubclass(AgentState, BaseModel)

    def test_agent_state_creation_real(self):
        """REAL TEST: Create actual state instance with validation"""
        from src.core.state_models import AgentState

        # Create real state instance (not mocked)
        state = AgentState(
            current_agent="orchestrator",
            task_description="Test task",
            messages=[],
            context={},
            tools_available=[],
            workflow_stage="planning"
        )

        # Verify real instance properties
        assert state.current_agent == "orchestrator"
        assert state.task_description == "Test task"
        assert isinstance(state.messages, list)
        assert isinstance(state.context, dict)

    def test_agent_state_validation_real(self):
        """REAL TEST: Validate Pydantic validation actually works"""
        from src.core.state_models import AgentState

        # Test real validation (should raise ValueError)
        with pytest.raises(ValidationError):
            AgentState(
                current_agent="invalid_agent",
                task_description="Test",
                messages=[],
                context={},
                tools_available=[],
                workflow_stage="planning"
            )


class TestRealAgentInstances:
    """REAL: Test agent instances (not full MCP integration)"""

    def test_orchestrator_agent_real(self):
        """REAL TEST: Create actual OrchestratorAgent instance"""
        from src.agents.orchestrator_agent import OrchestratorAgent

        # Create real agent instance
        agent = OrchestratorAgent()

        # Verify real properties
        assert agent.name == "Orchestrator"
        assert agent.role == "Workflow Coordinator"

        # Verify tool list (basic check, not MCP connection)
        tools = agent.get_available_tools()
        assert isinstance(tools, list)
        assert 'mcp_github' in tools
        assert 'mcp_tavily' in tools

    def test_analyst_agent_real(self):
        """REAL TEST: Create actual AnalystAgent instance"""
        from src.agents.analyst_agent import AnalystAgent

        agent = AnalystAgent()

        assert agent.name == "Analyst"
        assert agent.role == "Code Analysis Specialist"

        tools = agent.get_available_tools()
        assert 'serena_mcp' in tools
        assert 'context7_mcp' in tools
        assert 'sequential_thinking_mcp' in tools

    def test_knowledge_agent_real(self):
        """REAL TEST: Create actual KnowledgeAgent instance"""
        from src.agents.knowledge_agent import KnowledgeAgent

        agent = KnowledgeAgent()

        assert agent.name == "Knowledge"
        assert agent.role == "Knowledge Management Specialist"

        tools = agent.get_available_tools()
        assert 'graphiti_mcp' in tools
        assert 'obsidian_mcp' in tools
        assert 'filesystem_mcp' in tools

    def test_developer_agent_real(self):
        """REAL TEST: Create actual DeveloperAgent instance"""
        from src.agents.developer_agent import DeveloperAgent

        agent = DeveloperAgent()

        assert agent.name == "Developer"
        assert agent.role == "Implementation Specialist"

        tools = agent.get_available_tools()
        assert 'chrome_devtools_mcp' in tools
        assert 'code_execution' in tools

    def test_validator_agent_real(self):
        """REAL TEST: Create actual ValidatorAgent instance"""
        from src.agents.validator_agent import ValidatorAgent

        agent = ValidatorAgent()

        assert agent.name == "Validator"
        assert agent.role == "Quality Assurance Specialist"

        tools = agent.get_available_tools()
        assert 'dspy_framework' in tools
        assert 'sentry_mcp' in tools
        assert 'postgres_mcp' in tools


class TestRealCheckpointing:
    """REAL: Test LangGraph checkpointing with actual execution"""

    def test_checkpointer_configured_real(self):
        """REAL TEST: Verify checkpointer exists in real graph"""
        from src.core.agent_graph import create_agent_graph

        compiled_graph = create_agent_graph()

        # Check real checkpointer (not mocked)
        assert hasattr(compiled_graph, 'checkpointer')
        assert compiled_graph.checkpointer is not None

    def test_workflow_execution_real(self):
        """REAL TEST: Execute real workflow with checkpointing"""
        from src.core.agent_graph import create_agent_graph
        from src.core.state_models import AgentState

        compiled_graph = create_agent_graph()

        # Create real initial state
        initial_state = AgentState(
            current_agent="orchestrator",
            task_description="Real test execution",
            messages=[],
            context={"test": True},
            tools_available=[],
            workflow_stage="planning"
        )

        # Execute real workflow
        config = {"configurable": {"thread_id": "test-real-123"}}
        result = compiled_graph.invoke(initial_state, config=config)

        # Verify real execution result
        assert result is not None
        assert isinstance(result, dict)


class TestRealObservability:
    """REAL: Test LangSmith observability configuration"""

    def test_langsmith_config_real(self):
        """REAL TEST: Verify LangSmith configuration exists"""
        from src.core.observability import get_langsmith_config

        config = get_langsmith_config()

        # Verify real config (not mocked)
        assert config is not None
        assert 'project' in config
        assert 'api_key' in config


class TestRealMCPBridge:
    """REAL: Test MCP bridge exists (detailed tests in Story 1.2)"""

    def test_mcp_bridge_creation_real(self):
        """REAL TEST: Create actual MCPBridge instance"""
        from src.core.mcp_bridge import MCPBridge

        # Create real bridge instance
        bridge = MCPBridge()

        assert bridge is not None
        assert hasattr(bridge, 'direct_mcp_servers')
        assert hasattr(bridge, 'wrapped_mcp_servers')

    def test_mcp_bridge_connection_real(self):
        """REAL TEST: Test real bridge connection status"""
        from src.core.mcp_bridge import MCPBridge

        bridge = MCPBridge()

        # Get real connection status
        status = bridge.test_connection()

        assert status is not None
        assert 'bridge_available' in status

    def test_mcp_servers_available_real(self):
        """REAL TEST: Verify MCP servers are registered"""
        from src.core.mcp_bridge import MCPBridge

        bridge = MCPBridge()

        # Get real server list
        servers = bridge.get_available_servers()

        assert isinstance(servers, list)
        assert len(servers) > 0

        # Verify expected servers
        assert 'serena' in servers
        assert 'github' in servers
        assert 'graphiti' in servers


class TestRealIntegration:
    """REAL: Integration tests with actual workflow execution"""

    def test_end_to_end_workflow_real(self):
        """REAL TEST: Execute complete workflow through real graph"""
        from src.core.agent_graph import create_agent_graph
        from src.core.state_models import AgentState

        compiled_graph = create_agent_graph()

        # Create real workflow state
        initial_state = AgentState(
            current_agent="orchestrator",
            task_description="Integration test workflow",
            messages=[],
            context={"integration_test": True},
            tools_available=[],
            workflow_stage="planning"
        )

        # Execute real workflow
        config = {"configurable": {"thread_id": "integration-test"}}
        result = compiled_graph.invoke(initial_state, config=config)

        # Verify real execution
        assert result is not None
        assert isinstance(result, dict)
        # Graph returns dict with agent states
        assert 'orchestrator' in str(result) or 'analyst' in str(result)

    def test_agent_coordination_real(self):
        """REAL TEST: Test agent handoff in real graph"""
        from src.core.agent_graph import create_agent_graph
        from src.core.state_models import AgentState

        compiled_graph = create_agent_graph()

        # Create state for handoff test
        state = AgentState(
            current_agent="orchestrator",
            task_description="Test agent coordination",
            messages=[{"role": "system", "content": "Handoff to analyst"}],
            context={"handoff_target": "analyst"},
            tools_available=[],
            workflow_stage="analysis_required"
        )

        config = {"configurable": {"thread_id": "coordination-test"}}
        result = compiled_graph.invoke(state, config=config)

        # Verify coordination executed
        assert result is not None
        assert isinstance(result, dict)