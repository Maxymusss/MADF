"""
Main LangGraph workflow orchestration for MADF multi-agent system
"""

import logging
import sqlite3
import os
import aiosqlite
from datetime import datetime
from typing import Dict, Any
from uuid import uuid4

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from .models.state import WorkflowState
from .agents import planning_agent, research_agent, dev_agent, pm_agent
from .utils.logging import create_workflow_logger

logger = logging.getLogger(__name__)


def create_weekly_research_workflow(enable_interrupts: bool = False) -> StateGraph:
    """
    Create complete weekly research workflow with 4-agent coordination

    Args:
        enable_interrupts: Enable breakpoint interrupts for human-in-the-loop

    Returns:
        Compiled StateGraph with checkpointing enabled
    """
    # Create StateGraph
    workflow = StateGraph(WorkflowState)

    # Add agent nodes
    workflow.add_node("planning", planning_agent)
    workflow.add_node("research", research_agent)
    workflow.add_node("dev", dev_agent)
    workflow.add_node("pm", pm_agent)

    # Define linear workflow edges
    workflow.add_edge("planning", "research")
    workflow.add_edge("research", "dev")
    workflow.add_edge("dev", "pm")
    workflow.add_edge("pm", END)

    # Set entry point
    workflow.set_entry_point("planning")

    # Compile workflow with async checkpointing and optional interrupts
    # AsyncSqliteSaver returns context manager, not direct instance
    if enable_interrupts:
        # Enable breakpoints for human-in-the-loop debugging
        interrupt_before = ["planning", "research", "dev", "pm"]
        return workflow.compile(interrupt_before=interrupt_before)
    else:
        return workflow.compile()


async def execute_weekly_research(
    workflow_id: str = None,
    initial_plan: Dict[str, Any] = None,
    enable_interrupts: bool = False
) -> Dict[str, Any]:
    """
    Execute complete weekly research workflow

    Args:
        workflow_id: Optional workflow ID (generated if not provided)
        initial_plan: Optional initial BMAD plan data
        enable_interrupts: Enable breakpoint interrupts for debugging

    Returns:
        Workflow execution results
    """
    # Generate workflow ID if not provided
    if not workflow_id:
        workflow_id = f"weekly_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid4())[:8]}"

    # Set up workflow logging
    workflow_logger = create_workflow_logger(workflow_id)
    workflow_logger.info(f"Starting weekly research workflow: {workflow_id}")

    try:
        # Create workflow with interrupt support
        workflow = create_weekly_research_workflow(enable_interrupts)

        # Initialize state
        initial_state = WorkflowState(
            workflow_id=workflow_id,
            current_agent="planning",
            plan=initial_plan,
            metadata={
                "execution_start": datetime.utcnow().isoformat(),
                "target_regions": ["CN", "TW", "KR", "HK", "SG", "TH", "MY", "PH", "ID", "IN", "US"],
                "target_markets": ["fx", "rates"],
                "output_format": "weekly_commentary"
            }
        )

        # Execute workflow
        config = {"configurable": {"thread_id": workflow_id}}

        workflow_logger.info("Executing LangGraph workflow")
        result = await workflow.ainvoke(initial_state, config=config)

        # Calculate execution metrics
        execution_time = calculate_execution_time(result)
        performance_metrics = extract_performance_metrics(result)

        workflow_logger.info(f"Workflow completed successfully in {execution_time}s")

        return {
            "success": True,
            "workflow_id": workflow_id,
            "final_state": result,
            "execution_time": execution_time,
            "performance_metrics": performance_metrics,
            "execution_summary": get_execution_summary_from_result(result)
        }

    except Exception as e:
        error_msg = f"Workflow execution failed: {str(e)}"
        workflow_logger.error(error_msg, exc_info=True)

        # Try to get last checkpoint for recovery
        try:
            workflow = create_weekly_research_workflow()
            config = {"configurable": {"thread_id": workflow_id}}
            last_checkpoint = await get_last_checkpoint(workflow, config)
        except Exception:
            last_checkpoint = None

        return {
            "success": False,
            "workflow_id": workflow_id,
            "error": error_msg,
            "last_checkpoint": last_checkpoint
        }


def calculate_execution_time(result) -> float:
    """
    Calculate workflow execution time from metadata

    Args:
        result: Final workflow state (dict or WorkflowState)

    Returns:
        Execution time in seconds
    """
    try:
        # Handle both dict and WorkflowState objects
        if isinstance(result, dict):
            metadata = result.get('metadata', {})
            timestamp = result.get('timestamp')
        else:
            metadata = result.metadata
            timestamp = result.timestamp

        start_time_str = metadata.get("execution_start")
        if not start_time_str:
            return 0.0

        start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))

        # Handle timestamp as string or datetime object
        if isinstance(timestamp, str):
            end_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        elif isinstance(timestamp, datetime):
            end_time = timestamp
        else:
            return 0.0

        return (end_time - start_time).total_seconds()

    except Exception:
        return 0.0


def extract_performance_metrics(result) -> Dict[str, Any]:
    """
    Extract performance metrics from workflow execution

    Args:
        result: Final workflow state (dict or WorkflowState)

    Returns:
        Performance metrics dictionary
    """
    # Handle both dict and WorkflowState objects
    if isinstance(result, dict):
        metadata = result.get('metadata', {})
        errors = result.get('errors', [])
        retry_count = result.get('retry_count', 0)
        word_count = result.get('word_count', 0)
        validation_status = result.get('validation_status')
        output_path = result.get('output_path')
        is_complete = result.get('validation_status') == 'approved' and result.get('output_path') is not None and len(result.get('errors', [])) == 0
    else:
        metadata = result.metadata
        errors = result.errors
        retry_count = result.retry_count
        word_count = result.word_count
        validation_status = result.validation_status
        output_path = result.output_path
        is_complete = result.is_complete()

    return {
        "agents_completed": sum(1 for key in metadata.keys() if key.endswith("_complete")),
        "total_errors": len(errors),
        "retry_count": retry_count,
        "word_count": word_count,
        "validation_status": validation_status,
        "output_generated": output_path is not None,
        "workflow_complete": is_complete,
        "quality_score": metadata.get("quality_score", 0.0),
        "research_items": metadata.get("items_collected", 0),
        "data_sources_used": len(metadata.get("data_sources_used", []))
    }


async def get_last_checkpoint(workflow: StateGraph, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get last checkpoint for workflow recovery

    Args:
        workflow: Compiled StateGraph
        config: Workflow configuration

    Returns:
        Last checkpoint data or None
    """
    try:
        # This would implement checkpoint retrieval
        # For now, return placeholder
        return {
            "checkpoint_available": False,
            "last_agent": "unknown",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception:
        return None


def get_execution_summary_from_result(result) -> Dict[str, Any]:
    """
    Get workflow execution summary from result

    Args:
        result: Final workflow state (dict or WorkflowState)

    Returns:
        Execution summary dictionary
    """
    # Handle both dict and WorkflowState objects
    if isinstance(result, dict):
        return {
            "workflow_id": result.get('workflow_id', 'unknown'),
            "current_agent": result.get('current_agent', 'unknown'),
            "timestamp": result.get('timestamp', datetime.utcnow().isoformat()) if isinstance(result.get('timestamp'), str) else result.get('timestamp', datetime.utcnow()).isoformat(),
            "errors_count": len(result.get('errors', [])),
            "retry_count": result.get('retry_count', 0),
            "validation_status": result.get('validation_status'),
            "is_complete": result.get('validation_status') == 'approved' and result.get('output_path') is not None and len(result.get('errors', [])) == 0,
            "metadata": result.get('metadata', {})
        }
    else:
        # WorkflowState object - use its method
        return result.get_execution_summary()