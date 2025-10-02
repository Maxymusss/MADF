"""
Sentry Integration - Story 1.4 Task 3
Direct Sentry SDK for error tracking and alerting

Provides:
- Automatic error capture and reporting
- Context enrichment with agent metadata
- Performance monitoring
- Custom error grouping by agent/story
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from pathlib import Path

from .quick_logger import QuickLogger


class SentryManager:
    """
    Direct Sentry SDK integration for MADF error tracking

    Captures errors with rich context from agent execution
    Integrates with existing logging infrastructure
    """

    def __init__(
        self,
        dsn: Optional[str] = None,
        environment: str = "development",
        enable_tracing: bool = True,
        traces_sample_rate: float = 0.1
    ):
        """
        Initialize Sentry integration

        Args:
            dsn: Sentry DSN (default from env SENTRY_DSN)
            environment: Environment name (dev/staging/production)
            enable_tracing: Enable performance tracing
            traces_sample_rate: Percentage of transactions to trace (0.0-1.0)
        """
        self.dsn = dsn or os.getenv("SENTRY_DSN")
        self.environment = environment
        self.enable_tracing = enable_tracing
        self.traces_sample_rate = traces_sample_rate
        self._initialized = False
        self.logger = QuickLogger()

    def initialize(self):
        """Initialize Sentry SDK with MADF-specific configuration"""
        if self._initialized:
            return

        if not self.dsn:
            # Sentry disabled if no DSN provided
            self.logger.log(
                event_type="decision",
                category="error",
                agent_name="sentry_manager",
                success=False,
                details={
                    "action": "initialize_sentry",
                    "result": "disabled",
                    "reason": "no_dsn_provided"
                }
            )
            return

        # Configure logging integration
        logging_integration = LoggingIntegration(
            level=None,  # Don't capture logs automatically
            event_level=None  # Only capture explicitly sent events
        )

        # Initialize Sentry SDK
        sentry_sdk.init(
            dsn=self.dsn,
            environment=self.environment,
            traces_sample_rate=self.traces_sample_rate if self.enable_tracing else 0.0,
            integrations=[logging_integration],

            # Custom configuration for MADF
            before_send=self._before_send_hook,
            release=self._get_release_version(),

            # Error sampling (capture all errors)
            sample_rate=1.0,

            # Enable debug mode in development
            debug=(self.environment == "development"),

            # Attach stacktrace to messages
            attach_stacktrace=True,

            # Set max breadcrumbs
            max_breadcrumbs=50
        )

        self._initialized = True

        self.logger.log(
            event_type="decision",
            category="execution",
            agent_name="sentry_manager",
            success=True,
            details={
                "action": "initialize_sentry",
                "environment": self.environment,
                "tracing_enabled": self.enable_tracing,
                "sample_rate": self.traces_sample_rate
            }
        )

    def _get_release_version(self) -> str:
        """Get release version from git or package"""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                return f"madf@{result.stdout.strip()}"
        except Exception:
            pass

        return "madf@unknown"

    def _before_send_hook(self, event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Pre-process events before sending to Sentry

        Add MADF-specific context and filtering
        """
        # Add custom tags for better grouping
        if 'tags' not in event:
            event['tags'] = {}

        # Tag with MADF project
        event['tags']['project'] = 'madf'

        # Filter out test errors in production
        if self.environment == "production":
            if 'exception' in event:
                for exception in event['exception'].get('values', []):
                    if 'test' in exception.get('type', '').lower():
                        return None  # Don't send test errors

        return event

    def capture_error(
        self,
        error: Exception,
        agent_name: Optional[str] = None,
        story_id: Optional[str] = None,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Capture error with MADF context

        Args:
            error: Exception to capture
            agent_name: Agent that encountered the error
            story_id: Story being executed
            session_id: Session identifier
            context: Additional context dictionary
        """
        if not self._initialized:
            return

        # Set context tags
        with sentry_sdk.push_scope() as scope:
            if agent_name:
                scope.set_tag("agent", agent_name)
            if story_id:
                scope.set_tag("story", story_id)
            if session_id:
                scope.set_context("session", {"session_id": session_id})

            # Add custom context
            if context:
                scope.set_context("madf", context)

            # Capture exception
            event_id = sentry_sdk.capture_exception(error)

        # Log to JSONL as well
        self.logger.log(
            event_type="error",
            category="error",
            agent_name=agent_name or "unknown",
            success=False,
            details={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "sentry_event_id": event_id,
                "story_id": story_id,
                "session_id": session_id,
                "context": context or {}
            }
        )

        return event_id

    def capture_message(
        self,
        message: str,
        level: str = "info",
        agent_name: Optional[str] = None,
        story_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Capture custom message/event

        Args:
            message: Message to capture
            level: Severity level (debug/info/warning/error/fatal)
            agent_name: Agent sending message
            story_id: Story being executed
            context: Additional context
        """
        if not self._initialized:
            return

        with sentry_sdk.push_scope() as scope:
            if agent_name:
                scope.set_tag("agent", agent_name)
            if story_id:
                scope.set_tag("story", story_id)
            if context:
                scope.set_context("madf", context)

            event_id = sentry_sdk.capture_message(message, level=level)

        return event_id

    def start_transaction(
        self,
        name: str,
        op: str = "agent.execution",
        agent_name: Optional[str] = None,
        story_id: Optional[str] = None
    ) -> sentry_sdk.tracing.Transaction:
        """
        Start performance transaction

        Args:
            name: Transaction name
            op: Operation type
            agent_name: Agent name
            story_id: Story ID

        Returns:
            Sentry transaction object
        """
        if not self._initialized or not self.enable_tracing:
            # Return dummy transaction if tracing disabled
            return DummyTransaction()

        transaction = sentry_sdk.start_transaction(
            name=name,
            op=op
        )

        if agent_name:
            transaction.set_tag("agent", agent_name)
        if story_id:
            transaction.set_tag("story", story_id)

        return transaction

    def add_breadcrumb(
        self,
        message: str,
        category: str = "default",
        level: str = "info",
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Add breadcrumb for error context

        Args:
            message: Breadcrumb message
            category: Breadcrumb category
            level: Severity level
            data: Additional data
        """
        if not self._initialized:
            return

        sentry_sdk.add_breadcrumb(
            message=message,
            category=category,
            level=level,
            data=data or {}
        )

    def set_user(
        self,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        email: Optional[str] = None
    ):
        """
        Set user context for error tracking

        Args:
            user_id: User identifier
            username: Username
            email: User email
        """
        if not self._initialized:
            return

        sentry_sdk.set_user({
            "id": user_id,
            "username": username,
            "email": email
        })

    def close(self):
        """Flush pending events and close Sentry client"""
        if self._initialized:
            sentry_sdk.flush(timeout=2.0)


class DummyTransaction:
    """Dummy transaction for when tracing is disabled"""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def set_tag(self, key, value):
        pass

    def finish(self):
        pass


# ============================================================================
# DECORATOR FOR AGENT ERROR TRACKING
# ============================================================================

def track_errors(
    agent_name: str,
    story_id: Optional[str] = None
):
    """
    Decorator to automatically track errors in agent functions

    Args:
        agent_name: Name of agent
        story_id: Story being executed

    Example:
        @track_errors(agent_name="planning_agent", story_id="1.4")
        def plan_task(user_requirement):
            # Implementation
            pass
    """
    def decorator(func):
        import functools
        import inspect

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            sentry = SentryManager()
            sentry.initialize()

            # Start transaction
            transaction = sentry.start_transaction(
                name=f"{agent_name}.{func.__name__}",
                op="agent.execution",
                agent_name=agent_name,
                story_id=story_id
            )

            try:
                with transaction:
                    result = await func(*args, **kwargs)
                    return result
            except Exception as e:
                # Capture error with context
                sentry.capture_error(
                    error=e,
                    agent_name=agent_name,
                    story_id=story_id,
                    context={
                        "function": func.__name__,
                        "args": str(args)[:200],  # Truncate for privacy
                        "kwargs": str(kwargs)[:200]
                    }
                )
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            sentry = SentryManager()
            sentry.initialize()

            transaction = sentry.start_transaction(
                name=f"{agent_name}.{func.__name__}",
                op="agent.execution",
                agent_name=agent_name,
                story_id=story_id
            )

            try:
                with transaction:
                    result = func(*args, **kwargs)
                    return result
            except Exception as e:
                sentry.capture_error(
                    error=e,
                    agent_name=agent_name,
                    story_id=story_id,
                    context={
                        "function": func.__name__,
                        "args": str(args)[:200],
                        "kwargs": str(kwargs)[:200]
                    }
                )
                raise

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Global singleton instance
_sentry_manager: Optional[SentryManager] = None


def get_sentry_manager() -> SentryManager:
    """Get or create global Sentry manager"""
    global _sentry_manager

    if _sentry_manager is None:
        _sentry_manager = SentryManager()
        _sentry_manager.initialize()

    return _sentry_manager
