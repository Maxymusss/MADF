"""
MADF Logger - Agent execution decorators and workflow context management
Story 1.4 Task 1 Phase 1 implementation
"""

import time
import functools
import inspect
from typing import Optional, Callable, Any
from .quick_logger import get_logger, QuickLogger


class MADFLogger:
    """High-level MADF logging interface with decorators"""

    def __init__(self, story_id: str = "1.4"):
        self.logger = get_logger(story_id)

    def set_workflow_context(
        self,
        workflow_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        thread_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ):
        """Set workflow context for all subsequent logging"""
        self.logger.set_context(
            agent_name=agent_name,
            workflow_id=workflow_id,
            thread_id=thread_id,
            trace_id=trace_id
        )

    def log_agent_execution(
        self,
        agent_name: str,
        action: str,
        **kwargs
    ):
        """Log agent execution event"""
        self.logger.log_agent_action(agent_name, action, **kwargs)

    def log_workflow_start(
        self,
        workflow_id: str,
        task_description: str,
        **kwargs
    ):
        """Log workflow start event"""
        self.logger.log("workflow_start", "execution",
                       workflow_id=workflow_id,
                       task_description=task_description,
                       **kwargs)

    def log_workflow_end(
        self,
        workflow_id: str,
        success: bool,
        duration_ms: int,
        **kwargs
    ):
        """Log workflow end event"""
        self.logger.log("workflow_end", "execution",
                       workflow_id=workflow_id,
                       success=success,
                       duration_ms=duration_ms,
                       **kwargs)

    def log_agent_transition(
        self,
        from_agent: str,
        to_agent: str,
        reason: str,
        **kwargs
    ):
        """Log agent handoff/transition"""
        self.logger.log("agent_transition", "execution",
                       from_agent=from_agent,
                       to_agent=to_agent,
                       details={"reason": reason, **kwargs})

    def log_decision(
        self,
        decision_point: str,
        options_considered: list,
        choice_made: str,
        rationale: str,
        **kwargs
    ):
        """Log decision point"""
        self.logger.log("decision", "decision",
                       decision_point=decision_point,
                       details={
                           "options_considered": options_considered,
                           "choice_made": choice_made,
                           "rationale": rationale,
                           **kwargs
                       })


# Decorator for automatic agent execution logging
def log_agent_execution(agent_name: Optional[str] = None):
    """
    Decorator to automatically log agent execution with timing

    Usage:
        @log_agent_execution(agent_name="analyst")
        async def analyze_code(self, code: str):
            # Agent logic here
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            logger = get_logger()

            # Extract agent name from args if not provided
            actual_agent_name = agent_name
            if not actual_agent_name and args and hasattr(args[0], '__class__'):
                actual_agent_name = args[0].__class__.__name__

            # Set agent context
            if actual_agent_name:
                logger.set_context(agent_name=actual_agent_name)

            # Log execution start
            logger.log("agent_action", "execution",
                      agent=actual_agent_name,
                      action=func.__name__,
                      status="start")

            try:
                result = await func(*args, **kwargs)
                duration_ms = int((time.time() - start_time) * 1000)

                # Log successful execution
                logger.log("agent_action", "execution",
                          agent=actual_agent_name,
                          action=func.__name__,
                          duration_ms=duration_ms,
                          success=True)

                return result

            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)

                # Log failed execution
                logger.log("agent_action", "error",
                          agent=actual_agent_name,
                          action=func.__name__,
                          duration_ms=duration_ms,
                          success=False,
                          details={"error": str(e)})

                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            logger = get_logger()

            # Extract agent name from args if not provided
            actual_agent_name = agent_name
            if not actual_agent_name and args and hasattr(args[0], '__class__'):
                actual_agent_name = args[0].__class__.__name__

            # Set agent context
            if actual_agent_name:
                logger.set_context(agent_name=actual_agent_name)

            # Log execution start
            logger.log("agent_action", "execution",
                      agent=actual_agent_name,
                      action=func.__name__,
                      status="start")

            try:
                result = func(*args, **kwargs)
                duration_ms = int((time.time() - start_time) * 1000)

                # Log successful execution
                logger.log("agent_action", "execution",
                          agent=actual_agent_name,
                          action=func.__name__,
                          duration_ms=duration_ms,
                          success=True)

                return result

            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)

                # Log failed execution
                logger.log("agent_action", "error",
                          agent=actual_agent_name,
                          action=func.__name__,
                          duration_ms=duration_ms,
                          success=False,
                          details={"error": str(e)})

                raise

        # Return async or sync wrapper based on function type
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Global MADF logger instance
_madf_logger = None

def get_madf_logger(story_id: str = "1.4") -> MADFLogger:
    """Get or create global MADF logger instance"""
    global _madf_logger
    if _madf_logger is None:
        _madf_logger = MADFLogger(story_id)
    return _madf_logger
