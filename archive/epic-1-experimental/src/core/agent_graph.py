"""
LangGraph StateGraph Implementation with 5 Specialized Agent Nodes

Creates the core orchestration system for multiagent workflows
"""

from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from .state_models import AgentState


def orchestrator_node(state: AgentState) -> AgentState:
    """
    Orchestrator Agent - Workflow coordination and task delegation
    Tools: MCP GitHub, MCP Tavily, workflow control
    """
    state.tools_available = ['mcp_github', 'mcp_tavily', 'workflow_control']

    # Basic orchestrator logic
    if state.workflow_stage == "planning":
        state.workflow_stage = "analysis_required"
        state.add_message("orchestrator", "Task analyzed, delegating to analyst for code analysis")
        return state

    state.add_message("orchestrator", "Orchestrator processing complete")
    return state


def analyst_node(state: AgentState) -> AgentState:
    """
    Analyst Agent - Semantic code search and analysis
    Tools: Serena MCP, Context7 MCP, Sequential Thinking MCP
    """
    state.tools_available = ['serena_mcp', 'context7_mcp', 'sequential_thinking_mcp']

    if state.workflow_stage == "analysis_required":
        state.workflow_stage = "analysis"
        state.add_message("analyst", "Performing code analysis using semantic search")

    state.add_message("analyst", "Code analysis complete")
    return state


def knowledge_node(state: AgentState) -> AgentState:
    """
    Knowledge Agent - Persistent knowledge graphs and documentation
    Tools: Graphiti MCP, Obsidian MCP, Filesystem MCP
    """
    state.tools_available = ['graphiti_mcp', 'obsidian_mcp', 'filesystem_mcp']

    state.add_message("knowledge", "Knowledge persistence and graph operations complete")
    return state


def developer_node(state: AgentState) -> AgentState:
    """
    Developer Agent - Code implementation and debugging
    Tools: Chrome DevTools MCP, code execution, file operations
    """
    state.tools_available = ['chrome_devtools_mcp', 'code_execution', 'file_operations']

    if state.workflow_stage == "analysis":
        state.workflow_stage = "implementation"

    state.add_message("developer", "Development implementation complete")
    return state


def validator_node(state: AgentState) -> AgentState:
    """
    Validator Agent - Testing, optimization, and quality assurance
    Tools: DSPy framework, Sentry MCP, Postgres MCP, test execution
    """
    state.tools_available = ['dspy_framework', 'sentry_mcp', 'postgres_mcp', 'test_execution']

    if state.workflow_stage == "implementation":
        state.workflow_stage = "validation"

    state.add_message("validator", "Validation and quality assurance complete")
    state.workflow_stage = "completed"
    return state


def router(state: AgentState) -> Literal["orchestrator", "analyst", "knowledge", "developer", "validator", END]:
    """
    Router function to determine next agent based on current state
    """
    current = state.current_agent
    stage = state.workflow_stage

    # Define routing logic based on workflow stage and context
    if stage == "planning" and current == "orchestrator":
        return "orchestrator"
    elif stage == "analysis_required" and "handoff_target" in state.context:
        return state.context["handoff_target"]
    elif stage == "analysis_required":
        return "analyst"
    elif stage == "analysis":
        return "developer"
    elif stage == "implementation":
        return "validator"
    elif stage == "completed":
        return END

    # Default routing
    agent_sequence = {
        "orchestrator": "analyst",
        "analyst": "knowledge",
        "knowledge": "developer",
        "developer": "validator",
        "validator": END
    }

    return agent_sequence.get(current, END)


def create_agent_graph() -> StateGraph:
    """
    Create and configure the 5-agent LangGraph StateGraph

    Returns:
        StateGraph: Compiled graph with checkpointing enabled
    """
    # Create StateGraph with AgentState
    graph = StateGraph(AgentState)

    # Add all 5 specialized agent nodes
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("knowledge", knowledge_node)
    graph.add_node("developer", developer_node)
    graph.add_node("validator", validator_node)

    # Define edges between agents
    graph.add_edge(START, "orchestrator")

    # Add conditional edges based on router logic
    graph.add_conditional_edges(
        "orchestrator",
        router,
        ["orchestrator", "analyst", "knowledge", "developer", "validator", END]
    )

    graph.add_conditional_edges(
        "analyst",
        router,
        ["analyst", "knowledge", "developer", "validator", END]
    )

    graph.add_conditional_edges(
        "knowledge",
        router,
        ["knowledge", "developer", "validator", END]
    )

    graph.add_conditional_edges(
        "developer",
        router,
        ["developer", "validator", END]
    )

    graph.add_conditional_edges(
        "validator",
        router,
        [END]
    )

    # Configure checkpointing for workflow recovery
    checkpointer = MemorySaver()

    return graph.compile(checkpointer=checkpointer)