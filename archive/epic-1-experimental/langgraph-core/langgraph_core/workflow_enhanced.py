"""
BMAD-Enhanced LangGraph Workflow with Clarification Interrupts

Extends LangGraph workflow to support BMAD inquiry protocols:
- Agents call clarify_task() before execution
- If clarification needed, workflow interrupts with questions
- Human provides context, workflow resumes with updated state
- Preserves LangGraph StateGraph orchestration (no CLI patterns)

Usage:
    workflow = create_bmad_enhanced_workflow()

    # Execute with clarification support
    result = await workflow.ainvoke(initial_state, config=config)

    # If agent needs clarification, check state:
    if result.get("status") == "needs_clarification":
        questions = result["clarification_questions"]
        # Collect answers, then resume with:
        updated_state = update_state_with_clarifications(result, answers)
        result = await workflow.ainvoke(updated_state, config=config)
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

from .models.state import WorkflowState

logger = logging.getLogger(__name__)


class ClarificationRequest(BaseModel):
    """Clarification request from agent"""
    agent_id: str
    capability: str
    questions: List[str]
    task_description: str
    context: Dict[str, Any] = Field(default_factory=dict)


class BMADWorkflowState(WorkflowState):
    """
    Extended WorkflowState with BMAD clarification support

    Extends WorkflowState with clarification tracking fields
    """
    # Clarification tracking
    status: str = Field("pending", description="Workflow status: pending, clarifying, executing, complete")
    clarification_request: Optional[ClarificationRequest] = Field(None, description="Active clarification request")
    clarification_context: Dict[str, Any] = Field(default_factory=dict, description="Accumulated clarification context")

    # Agent capabilities
    agent_capabilities: Dict[str, List[str]] = Field(default_factory=dict, description="Agent capabilities registry")

    def request_clarification(
        self,
        agent_id: str,
        capability: str,
        questions: List[str],
        task_description: str
    ) -> None:
        """Request clarification before agent execution"""
        self.status = "clarifying"
        self.clarification_request = ClarificationRequest(
            agent_id=agent_id,
            capability=capability,
            questions=questions,
            task_description=task_description,
            context=self.clarification_context.copy()
        )
        logger.info(f"Agent {agent_id} requesting clarification for capability '{capability}'")

    def provide_clarifications(self, answers: Dict[str, Any]) -> None:
        """Provide clarification answers and resume workflow"""
        if not self.clarification_request:
            raise ValueError("No active clarification request")

        # Update context with answers
        self.clarification_context.update(answers)

        # Clear clarification request
        logger.info(f"Clarifications provided for agent {self.clarification_request.agent_id}")
        self.clarification_request = None
        self.status = "executing"

    def is_clarifying(self) -> bool:
        """Check if workflow is waiting for clarification"""
        return self.status == "clarifying" and self.clarification_request is not None


def create_bmad_agent_wrapper(agent_func, agent_id: str):
    """
    Wrap agent function with BMAD clarify_task() protocol

    Args:
        agent_func: Original agent function (orchestrator, analyst, etc.)
        agent_id: Agent identifier for capability lookup

    Returns:
        Wrapped agent function with clarification support
    """
    async def wrapped_agent(state: BMADWorkflowState) -> Dict[str, Any]:
        """
        Execute agent with clarification check

        Flow:
        1. Call agent.clarify_task(task, context)
        2. If clear=False, pause with clarification request
        3. If clear=True, execute agent normally
        4. Return updated state
        """
        logger.info(f"Executing {agent_id} with BMAD clarification protocol")

        # Check if resuming from clarification
        if state.is_clarifying() and state.clarification_request.agent_id == agent_id:
            logger.info(f"{agent_id} waiting for clarification - pausing execution")
            # Don't execute agent, just return state with clarification request
            return {
                "status": "clarifying",
                "current_agent": agent_id,
                "clarification_request": state.clarification_request
            }

        # Import agent class dynamically
        try:
            if agent_id == "orchestrator":
                from src.agents.orchestrator_agent import OrchestratorAgent
                agent = OrchestratorAgent()
            elif agent_id == "analyst":
                from src.agents.analyst_agent import AnalystAgent
                agent = AnalystAgent()
            elif agent_id == "knowledge":
                from src.agents.knowledge_agent import KnowledgeAgent
                agent = KnowledgeAgent()
            elif agent_id == "developer":
                from src.agents.developer_agent import DeveloperAgent
                agent = DeveloperAgent()
            elif agent_id == "validator":
                from src.agents.validator_agent import ValidatorAgent
                agent = ValidatorAgent()
            else:
                # Fallback to original agent function if no BMAD agent available
                return await agent_func(state)
        except ImportError:
            logger.warning(f"Could not import BMAD agent {agent_id}, using original agent function")
            return await agent_func(state)

        # Extract task description from state
        task_description = state.metadata.get("current_task", f"Execute {agent_id} responsibilities")

        # Call clarify_task() with accumulated context
        clarification_result = agent.clarify_task(
            task=task_description,
            context=state.clarification_context
        )

        # Check if clarification needed
        if not clarification_result.get("clear", False):
            questions = clarification_result.get("questions", [])
            capability = clarification_result.get("capability", "unknown")

            # Request clarification
            state.request_clarification(
                agent_id=agent_id,
                capability=capability,
                questions=questions,
                task_description=task_description
            )

            return {
                "status": "clarifying",
                "current_agent": agent_id,
                "clarification_request": state.clarification_request,
                "metadata": {
                    **state.metadata,
                    "clarification_triggered": datetime.now(timezone.utc).isoformat()
                }
            }

        # Context is clear - execute agent normally
        logger.info(f"{agent_id} clarification passed - executing task")
        state.status = "executing"

        # Execute original agent function
        result = await agent_func(state)

        return {
            **result,
            "status": "executing",
            "clarification_context": state.clarification_context
        }

    return wrapped_agent


def create_bmad_enhanced_workflow(
    agent_functions: Dict[str, Any],
    enable_clarification: bool = True
) -> StateGraph:
    """
    Create LangGraph workflow with BMAD clarification interrupts

    Args:
        agent_functions: Dict mapping agent IDs to agent functions
        enable_clarification: Enable BMAD clarification protocol (default: True)

    Returns:
        Compiled StateGraph with clarification support

    Example:
        agent_functions = {
            "orchestrator": orchestrator_node,
            "analyst": analyst_node,
            "knowledge": knowledge_node,
            "developer": developer_node,
            "validator": validator_node
        }

        workflow = create_bmad_enhanced_workflow(agent_functions)
    """
    # Create StateGraph with BMAD-enhanced state
    workflow = StateGraph(BMADWorkflowState)

    # Wrap agent functions with clarification protocol
    for agent_id, agent_func in agent_functions.items():
        if enable_clarification:
            wrapped_func = create_bmad_agent_wrapper(agent_func, agent_id)
        else:
            wrapped_func = agent_func

        workflow.add_node(agent_id, wrapped_func)

    # Define workflow edges (linear flow with clarification checks)
    agent_sequence = list(agent_functions.keys())

    for i in range(len(agent_sequence) - 1):
        current_agent = agent_sequence[i]
        next_agent = agent_sequence[i + 1]

        # Add conditional edge: proceed only if not clarifying
        workflow.add_conditional_edges(
            current_agent,
            lambda state: "clarifying" if state.is_clarifying() else "proceed",
            {
                "clarifying": END,  # Pause workflow for clarification
                "proceed": next_agent
            }
        )

    # Last agent always goes to END
    workflow.add_edge(agent_sequence[-1], END)

    # Set entry point
    workflow.set_entry_point(agent_sequence[0])

    # Compile with interrupt support
    # Interrupt before each agent if clarification enabled
    if enable_clarification:
        return workflow.compile(interrupt_before=agent_sequence)
    else:
        return workflow.compile()


def update_state_with_clarifications(
    state: BMADWorkflowState,
    answers: Dict[str, Any]
) -> BMADWorkflowState:
    """
    Update workflow state with clarification answers

    Args:
        state: Current workflow state with clarification request
        answers: Dict mapping question keywords to answers

    Returns:
        Updated state ready to resume execution

    Example:
        answers = {
            "user_problem": "Users need to export data quickly",
            "features": ["CSV export", "JSON export"],
            "target_users": "Data analysts and finance teams",
            "success_metrics": "50% adoption in 3 months"
        }

        updated_state = update_state_with_clarifications(state, answers)
    """
    if not state.is_clarifying():
        raise ValueError("State is not waiting for clarification")

    # Provide clarifications
    state.provide_clarifications(answers)

    # Update metadata
    state.metadata["clarifications_provided"] = datetime.now(timezone.utc).isoformat()
    state.metadata["clarification_count"] = state.metadata.get("clarification_count", 0) + 1

    return state


async def execute_workflow_with_clarifications(
    workflow: StateGraph,
    initial_state: BMADWorkflowState,
    config: Dict[str, Any],
    clarification_handler: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Execute workflow with automatic clarification handling

    Args:
        workflow: Compiled StateGraph with BMAD clarification support
        initial_state: Initial workflow state
        config: LangGraph execution config
        clarification_handler: Optional handler for collecting clarifications

    Returns:
        Final workflow result

    Example:
        async def my_clarification_handler(request: ClarificationRequest):
            print(f"Agent {request.agent_id} needs clarification:")
            for question in request.questions:
                print(f"  - {question}")

            # Collect answers (in real implementation, this would be interactive)
            return {
                "user_problem": "...",
                "features": [...]
            }

        result = await execute_workflow_with_clarifications(
            workflow,
            initial_state,
            config,
            clarification_handler=my_clarification_handler
        )
    """
    max_clarification_rounds = 5  # Prevent infinite loops
    clarification_rounds = 0

    current_state = initial_state

    while clarification_rounds < max_clarification_rounds:
        # Execute workflow
        result = await workflow.ainvoke(current_state, config=config)

        # Check if clarification needed
        if result.get("status") == "clarifying" and result.get("clarification_request"):
            clarification_rounds += 1
            logger.info(f"Clarification round {clarification_rounds}/{max_clarification_rounds}")

            clarification_request = result["clarification_request"]

            # Use handler to collect answers (if provided)
            if clarification_handler:
                answers = await clarification_handler(clarification_request)
            else:
                # Default: return result and let caller handle clarifications
                return {
                    "status": "needs_clarification",
                    "clarification_request": clarification_request,
                    "state": result,
                    "message": f"Agent {clarification_request.agent_id} needs clarification before proceeding"
                }

            # Update state with answers
            current_state = update_state_with_clarifications(result, answers)

            # Continue execution
            continue

        # Workflow complete or error
        return {
            "status": "complete" if result.get("status") != "error" else "error",
            "result": result,
            "clarification_rounds": clarification_rounds
        }

    # Max clarification rounds exceeded
    return {
        "status": "error",
        "error": f"Max clarification rounds ({max_clarification_rounds}) exceeded",
        "last_state": current_state
    }
