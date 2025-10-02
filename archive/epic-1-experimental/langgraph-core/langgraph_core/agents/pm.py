"""
PM Agent - Quality validation and workflow completion
"""

import logging
from typing import Dict, Any
from ..models.state import WorkflowState

logger = logging.getLogger(__name__)


async def pm_agent(state: WorkflowState) -> WorkflowState:
    """
    PM Agent LangGraph node - Validates and completes workflow

    Responsibilities:
    - Validate generated content quality
    - Check format and word count requirements
    - Confirm file delivery completion
    - Finalize workflow execution

    Args:
        state: Current workflow state with generated content

    Returns:
        Final workflow state with validation results
    """
    try:
        logger.info(f"PM agent starting for workflow {state.workflow_id}")

        # Update current agent
        state.set_current_agent("pm")

        # Validate generated content exists
        if not state.generated_content:
            error_msg = "PM agent requires generated content from dev agent"
            state.add_error(error_msg)
            logger.error(error_msg)
            return state

        # Extract content for validation
        content_data = state.generated_content
        commentary = content_data.get("commentary", {})
        word_count = content_data.get("word_count", 0)

        logger.info(f"Validating commentary with {word_count} words")

        # Quality validation checks
        validation_results = perform_quality_validation(commentary, word_count, state)

        if validation_results["passed"]:
            # Workflow completed successfully
            state.validation_status = "approved"
            logger.info(f"Workflow {state.workflow_id} approved - validation passed")

            # Final delivery confirmation (mock)
            state.metadata.update({
                "delivery_confirmed": True,
                "final_word_count": word_count,
                "quality_score": validation_results["quality_score"],
                "validation_timestamp": state.timestamp.isoformat()
            })

        else:
            # Quality issues identified
            state.validation_status = "rejected"
            state.errors.extend(validation_results["issues"])
            logger.warning(f"Workflow {state.workflow_id} rejected - validation failed")

        # Archive workflow completion
        state.metadata.update({
            "pm_complete": True,
            "pm_timestamp": state.timestamp.isoformat(),
            "validation_status": state.validation_status,
            "workflow_complete": validation_results["passed"]
        })

        # Set final agent status
        state.set_current_agent("completed")

        logger.info(f"PM agent completed - status: {state.validation_status}")
        return state

    except Exception as e:
        error_msg = f"PM agent error: {str(e)}"
        state.add_error(error_msg)
        logger.error(error_msg, exc_info=True)
        return state


def perform_quality_validation(
    commentary: Dict[str, Any],
    word_count: int,
    state: WorkflowState
) -> Dict[str, Any]:
    """
    Validate commentary meets quality standards

    Args:
        commentary: Generated commentary content
        word_count: Total word count
        state: Current workflow state

    Returns:
        Validation results with pass/fail and issues
    """
    issues = []
    quality_score = 1.0

    # Word count validation (target: 50-80 words per section, 4 sections = 200-320 total)
    if word_count < 150:
        issues.append(f"Word count too low: {word_count} words (minimum 150)")
        quality_score -= 0.3
    elif word_count > 400:
        issues.append(f"Word count too high: {word_count} words (maximum 400)")
        quality_score -= 0.2

    # Content completeness validation
    required_sections = ["fx_highlights", "rates_highlights", "cross_market_themes", "week_ahead"]
    missing_sections = [section for section in required_sections if not commentary.get(section)]

    if missing_sections:
        issues.append(f"Missing required sections: {missing_sections}")
        quality_score -= 0.4

    # Geographic coverage validation
    plan_coverage = state.plan.get("geographic_coverage", [])
    if len(plan_coverage) < 2:  # Should cover at least CN + US
        issues.append("Insufficient geographic coverage in plan")
        quality_score -= 0.2

    # Research data validation
    if not state.research_data or state.research_data.get("total_items", 0) < 5:
        issues.append("Insufficient research data for quality commentary")
        quality_score -= 0.3

    # Ensure quality score doesn't go negative
    quality_score = max(quality_score, 0.0)

    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "quality_score": quality_score,
        "word_count": word_count,
        "sections_complete": len(required_sections) - len(missing_sections)
    }