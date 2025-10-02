"""
Pydantic State Models for Agent State Management

Provides structured state passing between agents in the LangGraph workflow
"""

from typing import Dict, List, Any, Literal
from pydantic import BaseModel, Field, field_validator


class AgentState(BaseModel):
    """Core state model for multiagent coordination"""

    current_agent: Literal["orchestrator", "analyst", "knowledge", "developer", "validator"] = Field(
        description="Currently active agent in the workflow"
    )

    task_description: str = Field(
        description="Description of the current task being processed"
    )

    messages: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Message history between agents"
    )

    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Shared context data between agents"
    )

    tools_available: List[str] = Field(
        default_factory=list,
        description="List of available tools for current agent"
    )

    workflow_stage: Literal[
        "planning", "analysis", "implementation", "validation",
        "completed", "ready_for_validation", "analysis_required"
    ] = Field(
        description="Current stage in the workflow process"
    )

    @field_validator('current_agent')
    @classmethod
    def validate_agent_name(cls, v):
        """Validate that agent name is one of the 5 specialized agents"""
        valid_agents = {"orchestrator", "analyst", "knowledge", "developer", "validator"}
        if v not in valid_agents:
            raise ValueError(f"Invalid agent name: {v}. Must be one of {valid_agents}")
        return v

    def add_message(self, role: str, content: str):
        """Add a message to the message history"""
        self.messages.append({"role": role, "content": content})

    def update_context(self, key: str, value: Any):
        """Update context with new key-value pair"""
        self.context[key] = value

    def transition_to_agent(self, agent_name: str, reason: str = ""):
        """Transition workflow to different agent"""
        self.current_agent = agent_name
        if reason:
            self.add_message("system", f"Transitioning to {agent_name}: {reason}")


class WorkflowResult(BaseModel):
    """Result model for completed workflows"""

    success: bool = Field(description="Whether workflow completed successfully")
    final_agent: str = Field(description="Agent that completed the workflow")
    output: Dict[str, Any] = Field(description="Final workflow output")
    execution_time: float = Field(description="Total execution time in seconds")
    agent_transitions: List[str] = Field(description="Sequence of agent transitions")
    error_message: str = Field(default="", description="Error message if workflow failed")