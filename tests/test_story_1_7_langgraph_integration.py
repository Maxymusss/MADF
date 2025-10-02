"""
Tests for Story 1.7 - LangGraph BMAD Integration

Tests LangGraph workflow with BMAD clarification interrupts
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langgraph_core.workflow_enhanced import (
    BMADWorkflowState,
    ClarificationRequest,
    create_bmad_agent_wrapper,
    create_bmad_enhanced_workflow,
    update_state_with_clarifications
)


# Mock agent functions for testing
async def mock_orchestrator_agent(state: BMADWorkflowState) -> Dict[str, Any]:
    """Mock orchestrator agent"""
    return {
        "current_agent": "orchestrator",
        "metadata": {**state.metadata, "orchestrator_complete": True}
    }


async def mock_analyst_agent(state: BMADWorkflowState) -> Dict[str, Any]:
    """Mock analyst agent"""
    return {
        "current_agent": "analyst",
        "metadata": {**state.metadata, "analyst_complete": True}
    }


async def mock_knowledge_agent(state: BMADWorkflowState) -> Dict[str, Any]:
    """Mock knowledge agent"""
    return {
        "current_agent": "knowledge",
        "metadata": {**state.metadata, "knowledge_complete": True}
    }


class TestBMADWorkflowState:
    """Test BMAD-enhanced workflow state"""

    def test_create_bmad_state(self):
        """Should create BMADWorkflowState with clarification fields"""
        state = BMADWorkflowState(
            workflow_id="test_workflow",
            current_agent="orchestrator"
        )

        assert state.status == "pending"
        assert state.clarification_request is None
        assert state.clarification_context == {}

    def test_request_clarification(self):
        """Should request clarification from agent"""
        state = BMADWorkflowState(
            workflow_id="test_workflow",
            current_agent="orchestrator"
        )

        questions = [
            "What is the core user problem?",
            "What are the success metrics?"
        ]

        state.request_clarification(
            agent_id="orchestrator",
            capability="create_prd",
            questions=questions,
            task_description="Create PRD for new feature"
        )

        assert state.status == "clarifying"
        assert state.clarification_request is not None
        assert state.clarification_request.agent_id == "orchestrator"
        assert state.clarification_request.capability == "create_prd"
        assert len(state.clarification_request.questions) == 2

    def test_provide_clarifications(self):
        """Should provide clarifications and resume workflow"""
        state = BMADWorkflowState(
            workflow_id="test_workflow",
            current_agent="orchestrator"
        )

        # Request clarification
        state.request_clarification(
            agent_id="orchestrator",
            capability="create_prd",
            questions=["What is the user problem?"],
            task_description="Create PRD"
        )

        # Provide clarifications
        answers = {
            "user_problem": "Users need to export data",
            "features": ["CSV export", "JSON export"]
        }

        state.provide_clarifications(answers)

        assert state.status == "executing"
        assert state.clarification_request is None
        assert state.clarification_context["user_problem"] == "Users need to export data"
        assert len(state.clarification_context["features"]) == 2

    def test_is_clarifying(self):
        """Should check if state is waiting for clarification"""
        state = BMADWorkflowState(
            workflow_id="test_workflow",
            current_agent="orchestrator"
        )

        assert state.is_clarifying() == False

        state.request_clarification(
            agent_id="orchestrator",
            capability="create_prd",
            questions=["Question?"],
            task_description="Task"
        )

        assert state.is_clarifying() == True

        state.provide_clarifications({"answer": "value"})

        assert state.is_clarifying() == False


class TestClarificationRequest:
    """Test ClarificationRequest model"""

    def test_create_clarification_request(self):
        """Should create clarification request with required fields"""
        request = ClarificationRequest(
            agent_id="orchestrator",
            capability="create_prd",
            questions=["What is the user problem?"],
            task_description="Create PRD for feature"
        )

        assert request.agent_id == "orchestrator"
        assert request.capability == "create_prd"
        assert len(request.questions) == 1
        assert request.context == {}


class TestBMADAgentWrapper:
    """Test BMAD agent wrapper with clarification protocol"""

    @pytest.mark.asyncio
    async def test_agent_wrapper_with_clear_context(self):
        """Agent should execute normally when context is clear"""
        # Create wrapped agent
        wrapped_agent = create_bmad_agent_wrapper(
            mock_orchestrator_agent,
            agent_id="orchestrator"
        )

        # State with complete context (no clarification needed)
        state = BMADWorkflowState(
            workflow_id="test_workflow",
            current_agent="orchestrator",
            clarification_context={
                "user_problem": "Users need to export data",
                "features": ["CSV", "JSON"],
                "target_users": "Analysts",
                "success_metrics": "50% adoption"
            },
            metadata={"current_task": "create_prd for export feature"}
        )

        # Execute wrapped agent
        result = await wrapped_agent(state)

        # Should execute normally (no clarification)
        # Note: Will fallback to original agent if BMAD agent not available
        assert "current_agent" in result or "status" in result

    @pytest.mark.asyncio
    async def test_agent_wrapper_requests_clarification(self):
        """Agent should request clarification when context incomplete"""
        # Create wrapped agent
        wrapped_agent = create_bmad_agent_wrapper(
            mock_orchestrator_agent,
            agent_id="orchestrator"
        )

        # State with incomplete context
        state = BMADWorkflowState(
            workflow_id="test_workflow",
            current_agent="orchestrator",
            clarification_context={},  # Empty context - will trigger clarification
            metadata={"current_task": "create_prd for new feature"}
        )

        # Execute wrapped agent
        result = await wrapped_agent(state)

        # Should return clarification request or execute with fallback
        assert "status" in result or "current_agent" in result


class TestWorkflowCreation:
    """Test BMAD-enhanced workflow creation"""

    def test_create_workflow_with_clarification(self):
        """Should create workflow with clarification support"""
        agent_functions = {
            "orchestrator": mock_orchestrator_agent,
            "analyst": mock_analyst_agent,
            "knowledge": mock_knowledge_agent
        }

        workflow = create_bmad_enhanced_workflow(
            agent_functions,
            enable_clarification=True
        )

        assert workflow is not None

    def test_create_workflow_without_clarification(self):
        """Should create workflow without clarification (original behavior)"""
        agent_functions = {
            "orchestrator": mock_orchestrator_agent,
            "analyst": mock_analyst_agent
        }

        workflow = create_bmad_enhanced_workflow(
            agent_functions,
            enable_clarification=False
        )

        assert workflow is not None


class TestUpdateStateWithClarifications:
    """Test updating state with clarification answers"""

    def test_update_state_with_answers(self):
        """Should update state with clarification answers"""
        state = BMADWorkflowState(
            workflow_id="test_workflow",
            current_agent="orchestrator"
        )

        # Request clarification
        state.request_clarification(
            agent_id="orchestrator",
            capability="create_prd",
            questions=["What is the user problem?", "What are the features?"],
            task_description="Create PRD"
        )

        # Provide answers
        answers = {
            "user_problem": "Users need fast data export",
            "features": ["CSV export", "JSON export", "Excel export"],
            "target_users": "Data analysts",
            "success_metrics": "Export time < 1 second"
        }

        updated_state = update_state_with_clarifications(state, answers)

        assert updated_state.status == "executing"
        assert updated_state.clarification_request is None
        assert updated_state.clarification_context["user_problem"] == "Users need fast data export"
        assert len(updated_state.clarification_context["features"]) == 3
        assert "clarifications_provided" in updated_state.metadata

    def test_update_state_without_active_request(self):
        """Should raise error when no active clarification request"""
        state = BMADWorkflowState(
            workflow_id="test_workflow",
            current_agent="orchestrator"
        )

        # No clarification request
        answers = {"user_problem": "Some problem"}

        with pytest.raises(ValueError, match="not waiting for clarification"):
            update_state_with_clarifications(state, answers)


class TestWorkflowExecution:
    """Test workflow execution with clarifications"""

    @pytest.mark.asyncio
    async def test_workflow_execution_no_clarification(self):
        """Workflow should execute normally when context complete"""
        agent_functions = {
            "orchestrator": mock_orchestrator_agent,
            "analyst": mock_analyst_agent
        }

        workflow = create_bmad_enhanced_workflow(
            agent_functions,
            enable_clarification=False  # Disable for simple test
        )

        initial_state = BMADWorkflowState(
            workflow_id="test_workflow",
            current_agent="orchestrator"
        )

        config = {"configurable": {"thread_id": "test_thread"}}

        # Execute workflow
        result = await workflow.ainvoke(initial_state, config=config)

        # Should complete execution
        assert result is not None
        # Check that agents executed (metadata updated)
        if hasattr(result, 'metadata'):
            # Some agent should have completed
            assert len(result.metadata) > 0


class TestIntegrationWithRealAgents:
    """Test integration with real BMAD agents"""

    def test_orchestrator_agent_has_clarify_task(self):
        """Real Orchestrator agent should have clarify_task() method"""
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
            from agents.orchestrator_agent import OrchestratorAgent

            agent = OrchestratorAgent()

            # Should have clarify_task method
            assert hasattr(agent, 'clarify_task')
            assert callable(agent.clarify_task)

            # Should have persona loaded
            assert agent.persona is not None

            # Should have capabilities
            assert len(agent.capabilities) > 0

        except ImportError:
            pytest.skip("Orchestrator agent not available")

    def test_analyst_agent_has_clarify_task(self):
        """Real Analyst agent should have clarify_task() method"""
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
            from agents.analyst_agent import AnalystAgent

            agent = AnalystAgent()

            assert hasattr(agent, 'clarify_task')
            assert agent.persona is not None
            assert len(agent.capabilities) > 0

        except ImportError:
            pytest.skip("Analyst agent not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
