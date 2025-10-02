"""
MADF Integration for QuickLogger
Provides seamless logging integration with the LangGraph workflow
"""

from functools import wraps
import time
from typing import Any, Dict, Optional
from .quick_logger import get_logger


class MADFLogger:
    """Integration layer between MADF workflow and logging system"""

    def __init__(self, story_id: str = "1.2"):
        self.logger = get_logger(story_id)

    def set_workflow_context(self, workflow_id: str, agent_name: str):
        """Set context for subsequent logging"""
        self.logger.set_context(agent_name=agent_name, workflow_id=workflow_id)

    def log_workflow_start(self, workflow_id: str, initial_state: Dict):
        """Log workflow initiation"""
        self.logger.log("workflow_start", "execution",
                       workflow_id=workflow_id,
                       initial_state_size=len(str(initial_state)),
                       agents_planned=initial_state.get("agents", []))

    def log_agent_transition(self, from_agent: str, to_agent: str,
                           state_size: int, reason: str = None):
        """Log agent handoffs"""
        self.logger.log("agent_handoff", "execution",
                       from_agent=from_agent,
                       to_agent=to_agent,
                       state_size_bytes=state_size,
                       handoff_reason=reason)

    def log_state_update(self, agent: str, state_before_size: int,
                        state_after_size: int, operation: str):
        """Log state modifications"""
        self.logger.log("state_update", "execution",
                       agent=agent,
                       operation=operation,
                       size_before=state_before_size,
                       size_after=state_after_size,
                       size_delta=state_after_size - state_before_size)

    def log_checkpoint_save(self, checkpoint_id: str, state_size: int):
        """Log state persistence"""
        self.logger.log("checkpoint_save", "execution",
                       checkpoint_id=checkpoint_id,
                       state_size_bytes=state_size)

    def log_human_clarification_needed(self, agent: str, reason: str,
                                     context: Dict = None):
        """Log when human intervention is required"""
        self.logger.log_human_interaction("clarification_needed",
                                         trigger_reason=reason)
        self.logger.log("workflow_blocked", "interaction",
                       blocking_agent=agent,
                       block_reason=reason,
                       context=context or {})


def log_agent_execution(agent_name: str):
    """Decorator to automatically log agent execution"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger = get_logger()
            logger.set_context(agent_name=agent_name)

            start_time = time.time()
            logger.log("agent_start", "execution",
                      agent=agent_name,
                      function=func.__name__)

            try:
                result = await func(*args, **kwargs)

                duration_ms = int((time.time() - start_time) * 1000)
                logger.log("agent_complete", "execution",
                          agent=agent_name,
                          duration_ms=duration_ms,
                          success=True)

                return result

            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                logger.log_error(e, {
                    "agent": agent_name,
                    "function": func.__name__,
                    "duration_ms": duration_ms
                })
                logger.log("agent_failed", "execution",
                          agent=agent_name,
                          duration_ms=duration_ms,
                          success=False,
                          error_type=type(e).__name__)
                raise

        return wrapper
    return decorator


def log_tool_usage(tool_name: str):
    """Decorator to automatically log Claude tool usage"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger()

            start_time = time.time()

            try:
                result = func(*args, **kwargs)

                duration_ms = int((time.time() - start_time) * 1000)

                # Estimate tokens (rough approximation)
                result_size = len(str(result)) if result else 0
                estimated_tokens = result_size // 4  # Rough token estimation

                logger.log_tool_call(tool_name, duration_ms,
                                   tokens_used=estimated_tokens,
                                   success=True)

                return result

            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                logger.log_tool_call(tool_name, duration_ms, success=False)
                logger.log_error(e, {"tool": tool_name})
                raise

        return wrapper
    return decorator


# Convenience functions for direct use
def log_bmad_integration_event(event_type: str, details: Dict):
    """Log BMAD-specific events"""
    logger = get_logger()
    logger.log(f"bmad_{event_type}", "integration", **details)

def log_performance_metric(operation: str, expected_ms: int, actual_ms: int):
    """Quick performance logging"""
    logger = get_logger()
    if actual_ms > expected_ms * 2:  # 2x slower than expected
        logger.log_performance_issue(operation, expected_ms, actual_ms,
                                    "significant_slowdown")
    else:
        logger.log("performance_ok", "performance",
                  operation=operation,
                  expected_ms=expected_ms,
                  actual_ms=actual_ms)

def log_user_prompt_analysis(prompt: str, clarity_score: float = None):
    """Log human prompt characteristics for improvement"""
    logger = get_logger()

    # Simple prompt analysis
    word_count = len(prompt.split())
    has_specifics = any(char.isdigit() for char in prompt)
    has_examples = any(word in prompt.lower() for word in ['example', 'e.g.', 'like'])

    logger.log("user_prompt", "interaction",
              word_count=word_count,
              has_specifics=has_specifics,
              has_examples=has_examples,
              clarity_score=clarity_score,
              prompt_length=len(prompt))


# Initialize MADF logger for the current story
madf_logger = MADFLogger()