"""
MADF Logging System

Quick and comprehensive logging for the Multi-Agent Development Framework.
Designed for Story 1.2 and beyond.

Usage:
    from logger import log_event, log_error, log_tool_call
    from logger.madf_integration import log_agent_execution, madf_logger

    # Quick logging
    log_event("planning_complete", "execution", agent="planning_agent")
    log_error(Exception("Something went wrong"))

    # Decorator usage
    @log_agent_execution("research_agent")
    async def research_task(state):
        # Your agent code here
        return updated_state

    # MADF workflow integration
    madf_logger.set_workflow_context("workflow_123", "planning_agent")
"""

from .quick_logger import (
    QuickLogger,
    get_logger,
    log_error,
    log_tool_call,
    log_event
)

from .madf_integration import (
    MADFLogger,
    log_agent_execution,
    log_tool_usage,
    log_bmad_integration_event,
    log_performance_metric,
    log_user_prompt_analysis,
    madf_logger
)

__all__ = [
    # Core logging
    'QuickLogger',
    'get_logger',
    'log_error',
    'log_tool_call',
    'log_event',

    # MADF integration
    'MADFLogger',
    'log_agent_execution',
    'log_tool_usage',
    'log_bmad_integration_event',
    'log_performance_metric',
    'log_user_prompt_analysis',
    'madf_logger'
]

# Auto-start logging for current session
_default_logger = get_logger("1.2")