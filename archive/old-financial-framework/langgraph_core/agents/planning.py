"""
Planning Agent - BMAD plan integration and workflow initialization
"""

import logging
from typing import Dict, Any
from ..models.state import WorkflowState

logger = logging.getLogger(__name__)


async def planning_agent(state: WorkflowState) -> WorkflowState:
    """
    Planning Agent LangGraph node - Loads and validates BMAD-generated plans

    Responsibilities:
    - Load approved BMAD research plan
    - Validate plan structure and requirements
    - Initialize workflow state with plan data
    - Set up task queue for execution

    Args:
        state: Current workflow state

    Returns:
        Updated workflow state ready for research agent
    """
    try:
        logger.info(f"Planning agent starting for workflow {state.workflow_id}")

        # Update current agent
        state.set_current_agent("planning")

        # TODO: In Story 1.2, implement actual BMAD plan loading
        # For now, create a basic plan structure for testing
        if state.plan is None:
            state.plan = {
                "plan_id": f"research_plan_{state.workflow_id}",
                "title": "Weekly EM Asia + US FX/Rates Commentary",
                "objective": "Generate 50-80 word summaries of major market movements",
                "geographic_coverage": ["CN", "TW", "KR", "HK", "SG", "TH", "MY", "PH", "ID", "IN", "US"],
                "market_types": ["fx", "rates"],
                "data_sources": ["NewsAPI", "Yahoo Finance", "Alpha Vantage", "Google News"],
                "output_format": "weekly_commentary",
                "approved": True
            }

        # Validate plan structure
        required_fields = ["plan_id", "title", "objective", "geographic_coverage", "data_sources"]
        missing_fields = [field for field in required_fields if field not in state.plan]

        if missing_fields:
            error_msg = f"Plan missing required fields: {missing_fields}"
            state.add_error(error_msg)
            logger.error(error_msg)
            return state

        # Mark plan as approved (manual approval in Story 1.2)
        state.plan_approved = state.plan.get("approved", False)

        if not state.plan_approved:
            error_msg = "Plan not approved - human approval required"
            state.add_error(error_msg)
            logger.warning(error_msg)
            return state

        # Initialize metadata for tracking
        state.metadata.update({
            "planning_complete": True,
            "plan_id": state.plan["plan_id"],
            "geographic_coverage": state.plan["geographic_coverage"],
            "data_sources": state.plan["data_sources"],
            "planning_timestamp": state.timestamp.isoformat()
        })

        # Set next agent
        state.set_current_agent("research")

        logger.info(f"Planning agent completed for workflow {state.workflow_id}")
        return state

    except Exception as e:
        error_msg = f"Planning agent error: {str(e)}"
        state.add_error(error_msg)
        logger.error(error_msg, exc_info=True)
        return state