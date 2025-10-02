"""
QuickLogger - Thread-safe JSONL logging with universal event schema
Zero-performance-impact structured logging for MADF framework
Story 1.4 Task 1 Phase 1 implementation
"""

import json
import datetime
import threading
import os
from pathlib import Path
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict


# Universal Event Schema (Story 1.4 specification)
class UniversalEventSchema(BaseModel):
    """Universal event schema for MADF logging (Story 1.4)"""
    timestamp: str
    event_type: Literal[
        "agent_action", "tool_call", "agent_transition",
        "workflow_start", "workflow_end", "error", "decision",
        "session_start", "session_end", "human_interaction", "performance_issue"
    ]
    category: Literal["execution", "error", "interaction", "performance", "learning", "decision"]
    session_id: str
    story_id: str
    agent_name: Optional[str] = None
    workflow_id: Optional[str] = None
    thread_id: Optional[str] = None
    trace_id: Optional[str] = None
    duration_ms: int = 0
    tokens_used: int = 0
    context_percent: float = 0.0
    success: bool = True
    confidence_score: float = 0.0
    impact_score: float = 0.0
    time_saved_or_wasted_ms: int = 0
    user_satisfaction_delta: float = 0.0
    created_rule: bool = False
    pattern_detected: bool = False
    needs_review: bool = False
    details: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")  # Allow additional fields for extensibility


class QuickLogger:
    """Minimal logger for immediate use - captures everything, analyzes later"""

    def __init__(self, story_id: str = "1.4", validate_schema: bool = True):
        self.story_id = story_id
        self.start_time = datetime.datetime.now(datetime.timezone.utc)
        self.session_id = f"story_{story_id}_{self.start_time:%Y%m%d_%H%M%S}"
        self.validate_schema = validate_schema

        # Create log directory (configurable via env var)
        self.base_path = Path(os.getenv("MADF_LOG_PATH", "D:/Logs/MADF"))
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Create today's log file
        today = datetime.date.today()
        self.log_file = self.base_path / f"story_{story_id}_{today:%Y%m%d}.jsonl"

        # Thread-safe file writing
        self._lock = threading.Lock()

        # Track current context
        self.current_agent = None
        self.workflow_id = None
        self.thread_id = None
        self.trace_id = None

        # Auto-log session start
        self.log("session_start", "execution",
                session_id=self.session_id,
                story_id=story_id)

    def log(self, event_type: str, category: str, **kwargs):
        """Log any event with automatic timestamp and context"""

        event = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "event_type": event_type,
            "category": category,
            "session_id": self.session_id,
            "story_id": self.story_id,
            "agent_name": self.current_agent,
            "workflow_id": self.workflow_id,
            "thread_id": self.thread_id,
            "trace_id": self.trace_id,
            **kwargs
        }

        # Validate against universal schema if enabled
        if self.validate_schema:
            try:
                UniversalEventSchema(**event)
            except Exception as e:
                # Log validation error but don't block logging
                event["schema_validation_error"] = str(e)

        # Thread-safe write to JSONL
        with self._lock:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=True) + "\n")

    def log_error(self, error: Exception, context: Optional[Dict] = None):
        """Log errors with full context"""
        self.log("error", "error",
                error_type=type(error).__name__,
                error_message=str(error),
                context=context or {},
                priority="high")

    def log_tool_call(self, tool_name: str, duration_ms: int,
                     tokens_used: Optional[int] = None,
                     context_percent: Optional[float] = None,
                     success: bool = True):
        """Log Claude tool calls"""
        self.log("tool_call", "execution",
                tool=tool_name,
                duration_ms=duration_ms,
                tokens_used=tokens_used,
                context_percent=context_percent,
                success=success)

    def log_agent_action(self, agent_name: str, action: str,
                        duration_ms: Optional[int] = None,
                        success: bool = True):
        """Log multi-agent actions"""
        self.log("agent_action", "execution",
                agent=agent_name,
                action=action,
                duration_ms=duration_ms,
                success=success)

    def log_human_interaction(self, interaction_type: str,
                            trigger_reason: Optional[str] = None,
                            response_time_ms: Optional[int] = None):
        """Log human clarifications and interventions"""
        self.log("human_interaction", "interaction",
                interaction_type=interaction_type,
                trigger_reason=trigger_reason,
                response_time_ms=response_time_ms,
                triggering_agent=self.current_agent)

    def log_performance_issue(self, operation: str,
                            expected_ms: int, actual_ms: int,
                            bottleneck_cause: Optional[str] = None):
        """Log performance bottlenecks"""
        self.log("performance_issue", "performance",
                operation=operation,
                expected_ms=expected_ms,
                actual_ms=actual_ms,
                slowdown_factor=actual_ms / expected_ms if expected_ms > 0 else 1,
                bottleneck_cause=bottleneck_cause)

    def set_context(self, agent_name: Optional[str] = None,
                   workflow_id: Optional[str] = None,
                   thread_id: Optional[str] = None,
                   trace_id: Optional[str] = None):
        """Update current context for subsequent logs"""
        if agent_name is not None:
            self.current_agent = agent_name
        if workflow_id is not None:
            self.workflow_id = workflow_id
        if thread_id is not None:
            self.thread_id = thread_id
        if trace_id is not None:
            self.trace_id = trace_id

    def get_log_file_path(self) -> str:
        """Return current log file path for external tools"""
        return str(self.log_file)

    def close(self):
        """Log session end"""
        end_time = datetime.datetime.now(datetime.timezone.utc)
        duration_minutes = (end_time - self.start_time).total_seconds() / 60
        self.log("session_end", "execution",
                session_duration_minutes=round(duration_minutes, 2))


# Global logger instance for easy importing
_logger_instance = None

def get_logger(story_id: str = "1.4") -> QuickLogger:
    """Get or create global logger instance"""
    global _logger_instance
    if _logger_instance is None:
        # Use env var for current story if set
        story_id = os.getenv("MADF_CURRENT_STORY", story_id)
        _logger_instance = QuickLogger(story_id)
    return _logger_instance

def log_error(error: Exception, context: Optional[Dict] = None):
    """Quick error logging function"""
    get_logger().log_error(error, context)

def log_tool_call(tool_name: str, duration_ms: int, **kwargs):
    """Quick tool call logging function"""
    get_logger().log_tool_call(tool_name, duration_ms, **kwargs)

def log_event(event_type: str, category: str, **kwargs):
    """Quick event logging function"""
    get_logger().log(event_type, category, **kwargs)


if __name__ == "__main__":
    # Test the logger
    logger = QuickLogger("test")

    # Test different log types
    logger.log_tool_call("Read", 45, tokens_used=120, context_percent=23.5)
    logger.log_error(Exception("Test error"), {"file": "test.py"})
    logger.log_agent_action("planning_agent", "create_plan", 1500)
    logger.log_human_interaction("clarification", "ambiguous_requirement", 5000)
    logger.log_performance_issue("file_read", 100, 1500, "slow_disk")

    logger.close()
    print(f"Test logs written to: {logger.get_log_file_path()}")