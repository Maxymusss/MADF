# LangGraph Orchestration with BMAD Clarification Interrupts

**BMAD Pattern**: StateGraph workflow coordination with clarification protocol

## Overview

LangGraph provides StateGraph orchestration for multiagent workflows. Story 1.7 extends LangGraph with BMAD clarification interrupts, allowing agents to pause workflows and gather missing context before execution.

## Architecture

### Standard LangGraph Workflow (Before BMAD)

```python
from langgraph.graph import StateGraph, END
from .models.state import WorkflowState

# Create workflow
workflow = StateGraph(WorkflowState)

# Add agent nodes
workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("knowledge", knowledge_node)
workflow.add_node("developer", developer_node)
workflow.add_node("validator", validator_node)

# Define linear edges
workflow.add_edge("orchestrator", "analyst")
workflow.add_edge("analyst", "knowledge")
workflow.add_edge("knowledge", "developer")
workflow.add_edge("developer", "validator")
workflow.add_edge("validator", END)

# Set entry point and compile
workflow.set_entry_point("orchestrator")
compiled = workflow.compile()

# Execute workflow
result = await compiled.ainvoke(initial_state, config=config)
```

**Problem**: Agents execute immediately without clarification, leading to:
- Assumptions about incomplete context
- Rework when context is wrong
- Poor decisions from missing information

### BMAD-Enhanced Workflow (After Story 1.7)

```python
from langgraph_core.workflow_enhanced import (
    create_bmad_enhanced_workflow,
    BMADWorkflowState
)

# Create agent functions dictionary
agent_functions = {
    "orchestrator": orchestrator_node,
    "analyst": analyst_node,
    "knowledge": knowledge_node,
    "developer": developer_node,
    "validator": validator_node
}

# Create BMAD-enhanced workflow with clarification support
workflow = create_bmad_enhanced_workflow(
    agent_functions=agent_functions,
    enable_clarification=True  # Enable inquiry protocol
)

# Execute workflow
initial_state = BMADWorkflowState(
    workflow_id="project_x",
    current_agent="orchestrator"
)

result = await workflow.ainvoke(initial_state, config=config)

# Check if clarification needed
if result.get("status") == "clarifying":
    clarification_request = result["clarification_request"]
    print(f"Agent {clarification_request.agent_id} needs clarification:")
    for question in clarification_request.questions:
        print(f"  - {question}")

    # Collect answers
    answers = {
        "user_problem": "Users need faster data export",
        "features": ["CSV export", "JSON export"],
        "target_users": "Data analysts"
    }

    # Update state and resume
    updated_state = update_state_with_clarifications(result, answers)
    result = await workflow.ainvoke(updated_state, config=config)
```

**Benefits**:
- Agents ask questions before execution
- No assumptions about incomplete context
- Better decisions from complete information
- Workflow pauses/resumes seamlessly

## BMAD Workflow Components

### 1. BMADWorkflowState

Extended WorkflowState with clarification tracking:

```python
from langgraph_core.workflow_enhanced import BMADWorkflowState

class BMADWorkflowState(WorkflowState):
    # Standard WorkflowState fields
    workflow_id: str
    current_agent: str
    timestamp: datetime
    plan: Optional[Dict[str, Any]]
    # ... other fields

    # BMAD clarification fields
    status: str  # "pending", "clarifying", "executing", "complete"
    clarification_request: Optional[ClarificationRequest]
    clarification_context: Dict[str, Any]  # Accumulated context
    agent_capabilities: Dict[str, List[str]]  # Agent capabilities registry

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

    def provide_clarifications(self, answers: Dict[str, Any]) -> None:
        """Provide clarification answers and resume workflow"""
        self.clarification_context.update(answers)
        self.clarification_request = None
        self.status = "executing"

    def is_clarifying(self) -> bool:
        """Check if workflow is waiting for clarification"""
        return self.status == "clarifying" and self.clarification_request is not None
```

### 2. ClarificationRequest

Structured clarification request from agent:

```python
from pydantic import BaseModel, Field

class ClarificationRequest(BaseModel):
    agent_id: str  # Agent requesting clarification
    capability: str  # Capability being executed
    questions: List[str]  # Questions to ask
    task_description: str  # Task description
    context: Dict[str, Any]  # Current context

# Example usage
request = ClarificationRequest(
    agent_id="orchestrator",
    capability="create_prd",
    questions=[
        "What is the core user problem being solved?",
        "What are must-have vs nice-to-have features?",
        "Who are the target users?"
    ],
    task_description="Create PRD for data export feature",
    context={"project": "project_x"}
)
```

### 3. BMAD Agent Wrapper

Wraps agent functions with clarification protocol:

```python
def create_bmad_agent_wrapper(agent_func, agent_id: str):
    """Wrap agent function with BMAD clarify_task() protocol"""
    async def wrapped_agent(state: BMADWorkflowState) -> Dict[str, Any]:
        # Check if resuming from clarification
        if state.is_clarifying() and state.clarification_request.agent_id == agent_id:
            # Pause execution - return state with clarification request
            return {
                "status": "clarifying",
                "current_agent": agent_id,
                "clarification_request": state.clarification_request
            }

        # Import agent class dynamically
        if agent_id == "orchestrator":
            from src.agents.orchestrator_agent import OrchestratorAgent
            agent = OrchestratorAgent()
        # ... other agents

        # Extract task from state
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

            # Request clarification - pause workflow
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
        state.status = "executing"
        result = await agent_func(state)

        return {
            **result,
            "status": "executing",
            "clarification_context": state.clarification_context
        }

    return wrapped_agent
```

## Workflow Execution Patterns

### Pattern 1: No Clarification Needed

```python
# All context provided upfront
initial_state = BMADWorkflowState(
    workflow_id="project_x",
    current_agent="orchestrator",
    clarification_context={
        "user_problem": "Users need faster data export",
        "features": ["CSV export", "JSON export"],
        "target_users": "Data analysts",
        "success_metrics": "50% faster exports"
    }
)

result = await workflow.ainvoke(initial_state, config=config)

# Workflow executes all agents without interruption
assert result["status"] == "complete"
```

### Pattern 2: Single Clarification

```python
# Incomplete context
initial_state = BMADWorkflowState(
    workflow_id="project_x",
    current_agent="orchestrator",
    clarification_context={}  # Empty context
)

# First execution - agent requests clarification
result = await workflow.ainvoke(initial_state, config=config)

assert result["status"] == "clarifying"
assert result["clarification_request"].agent_id == "orchestrator"

# Provide answers
answers = {
    "user_problem": "Users need faster data export",
    "features": ["CSV export", "JSON export"],
    "target_users": "Data analysts",
    "success_metrics": "50% faster exports"
}

updated_state = update_state_with_clarifications(result, answers)

# Resume execution - workflow continues
result = await workflow.ainvoke(updated_state, config=config)

assert result["status"] == "complete"
```

### Pattern 3: Multiple Clarifications

```python
# Multiple agents need clarification
initial_state = BMADWorkflowState(
    workflow_id="project_x",
    current_agent="orchestrator"
)

# Execute workflow with clarification handler
async def clarification_handler(request: ClarificationRequest):
    print(f"Agent {request.agent_id} needs clarification:")
    for question in request.questions:
        print(f"  - {question}")

    # Collect answers (in real implementation, this would be interactive)
    return collect_answers(request)

result = await execute_workflow_with_clarifications(
    workflow,
    initial_state,
    config,
    clarification_handler=clarification_handler
)

# Workflow handles multiple clarification rounds automatically
assert result["status"] == "complete"
assert result["clarification_rounds"] >= 1
```

### Pattern 4: Clarification Timeout

```python
# Prevent infinite clarification loops
result = await execute_workflow_with_clarifications(
    workflow,
    initial_state,
    config,
    clarification_handler=clarification_handler
)

# If max clarification rounds exceeded (default: 5)
if result["status"] == "error":
    assert "Max clarification rounds" in result["error"]
```

## Conditional Edges for Clarification

Workflow uses conditional edges to route based on clarification status:

```python
workflow = StateGraph(BMADWorkflowState)

# Add nodes
workflow.add_node("orchestrator", wrapped_orchestrator)
workflow.add_node("analyst", wrapped_analyst)
workflow.add_node("knowledge", wrapped_knowledge)
workflow.add_node("developer", wrapped_developer)
workflow.add_node("validator", wrapped_validator)

# Define conditional edges
agent_sequence = ["orchestrator", "analyst", "knowledge", "developer", "validator"]

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
```

## Interrupt Support

LangGraph interrupts enable human-in-the-loop debugging:

```python
# Compile with interrupt support
workflow = create_bmad_enhanced_workflow(
    agent_functions=agent_functions,
    enable_clarification=True
)

# Interrupts enabled for all agent nodes
# Workflow pauses before each agent if interrupt_before specified
compiled = workflow.compile(
    interrupt_before=["orchestrator", "analyst", "knowledge", "developer", "validator"]
)
```

## State Persistence

LangGraph checkpoints enable workflow recovery:

```python
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

# Create checkpointer
async with AsyncSqliteSaver.from_conn_string("workflow_checkpoints.db") as checkpointer:
    # Compile workflow with checkpointing
    workflow = workflow.compile(checkpointer=checkpointer)

    # Execute workflow - state saved at each step
    config = {"configurable": {"thread_id": "project_x"}}
    result = await workflow.ainvoke(initial_state, config=config)

    # Resume workflow from checkpoint
    if result["status"] == "clarifying":
        # Provide clarifications
        updated_state = update_state_with_clarifications(result, answers)

        # Resume from checkpoint
        result = await workflow.ainvoke(updated_state, config=config)
```

## Integration with Existing Workflow

BMAD clarification protocol integrates with existing Story 1.1-1.6 workflow:

```python
# langgraph_core/workflow.py (Story 1.1)
from langgraph_core.workflow import create_weekly_research_workflow

# Standard workflow without clarifications
workflow = create_weekly_research_workflow(enable_interrupts=False)

# langgraph_core/workflow_enhanced.py (Story 1.7)
from langgraph_core.workflow_enhanced import create_bmad_enhanced_workflow

# BMAD-enhanced workflow with clarifications
agent_functions = {
    "planning": planning_agent,
    "research": research_agent,
    "dev": dev_agent,
    "pm": pm_agent
}

workflow = create_bmad_enhanced_workflow(
    agent_functions=agent_functions,
    enable_clarification=True
)

# Both workflows use same StateGraph orchestration
# BMAD adds clarification layer on top
```

## Testing Clarification Interrupts

```python
# tests/test_story_1_7_langgraph_integration.py

@pytest.mark.asyncio
async def test_workflow_pauses_for_clarification():
    """
    Given: Workflow with incomplete context
    When: Agent needs clarification
    Then: Workflow pauses with clarification request
    """
    # Create mock agent that requests clarification
    async def mock_agent(state):
        return {
            "status": "clarifying",
            "clarification_request": ClarificationRequest(
                agent_id="orchestrator",
                capability="create_prd",
                questions=["What is the user problem?"],
                task_description="Create PRD",
                context={}
            )
        }

    agent_functions = {"orchestrator": mock_agent}
    workflow = create_bmad_enhanced_workflow(agent_functions)

    initial_state = BMADWorkflowState(
        workflow_id="test",
        current_agent="orchestrator"
    )

    result = await workflow.ainvoke(initial_state)

    assert result["status"] == "clarifying"
    assert result["clarification_request"] is not None
    assert len(result["clarification_request"].questions) == 1
```

## Performance Considerations

### Clarification Overhead

- **Minimal**: Clarification check adds <10ms per agent
- **Keyword Extraction**: Domain-aware extraction optimized for speed
- **Tool Loading**: Tools loaded once at init, not per clarification

### When to Disable Clarifications

```python
# Disable for performance-critical workflows
workflow = create_bmad_enhanced_workflow(
    agent_functions=agent_functions,
    enable_clarification=False  # Skip clarify_task() checks
)

# Or provide complete context upfront
initial_state = BMADWorkflowState(
    workflow_id="batch_job",
    current_agent="orchestrator",
    clarification_context={
        # All required context provided
        "user_problem": "...",
        "features": [...],
        # ... complete context
    }
)
```

## References

- **Workflow Implementation**: [langgraph_core/workflow_enhanced.py](../../langgraph_core/workflow_enhanced.py)
- **WorkflowState Model**: [langgraph_core/models/state.py](../../langgraph_core/models/state.py)
- **LangGraph Integration Tests**: [tests/test_story_1_7_langgraph_integration.py](../../tests/test_story_1_7_langgraph_integration.py)
- **Story 1.7**: [story-1-7-bmad-agent-integration.md](../stories/epic-1/story-1-7-bmad-agent-integration.md)
- **LangGraph Docs**: [.claude/docs-cache/langgraph-docs.md](../../.claude/docs-cache/langgraph-docs.md)
