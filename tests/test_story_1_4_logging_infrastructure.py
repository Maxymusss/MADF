"""
Unit tests for Story 1.4 Task 1 Phase 1: QuickLogger and MADF Logger
Tests thread safety, schema validation, decorators, and context tracking
"""

import pytest
import os
import json
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import patch

from src.core.quick_logger import QuickLogger, UniversalEventSchema, get_logger
from src.core.madf_logger import MADFLogger, log_agent_execution, get_madf_logger


class TestUniversalEventSchema:
    """Test universal event schema validation"""

    def test_valid_event_schema(self):
        """Test valid event passes schema validation"""
        event = {
            "timestamp": "2025-10-01T10:00:00+00:00",
            "event_type": "agent_action",
            "category": "execution",
            "session_id": "story_1.4_20251001_100000",
            "story_id": "1.4"
        }
        schema = UniversalEventSchema(**event)
        assert schema.event_type == "agent_action"
        assert schema.category == "execution"
        assert schema.success is True  # default

    def test_invalid_event_type_fails(self):
        """Test invalid event_type fails validation"""
        event = {
            "timestamp": "2025-10-01T10:00:00+00:00",
            "event_type": "invalid_type",
            "category": "execution",
            "session_id": "test",
            "story_id": "1.4"
        }
        with pytest.raises(Exception):
            UniversalEventSchema(**event)

    def test_invalid_category_fails(self):
        """Test invalid category fails validation"""
        event = {
            "timestamp": "2025-10-01T10:00:00+00:00",
            "event_type": "agent_action",
            "category": "invalid_category",
            "session_id": "test",
            "story_id": "1.4"
        }
        with pytest.raises(Exception):
            UniversalEventSchema(**event)

    def test_optional_fields_have_defaults(self):
        """Test optional fields have sensible defaults"""
        event = {
            "timestamp": "2025-10-01T10:00:00+00:00",
            "event_type": "tool_call",
            "category": "execution",
            "session_id": "test",
            "story_id": "1.4"
        }
        schema = UniversalEventSchema(**event)
        assert schema.duration_ms == 0
        assert schema.tokens_used == 0
        assert schema.success is True
        assert schema.created_rule is False


class TestQuickLogger:
    """Test QuickLogger implementation"""

    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def logger(self, temp_log_dir):
        """Create QuickLogger with temp directory"""
        with patch.dict(os.environ, {"MADF_LOG_PATH": temp_log_dir}):
            logger = QuickLogger(story_id="test", validate_schema=True)
            yield logger
            logger.close()

    def test_logger_initialization(self, logger, temp_log_dir):
        """Test logger creates directory and file"""
        assert logger.story_id == "test"
        assert Path(logger.log_file).parent == Path(temp_log_dir)
        assert Path(logger.log_file).exists()

    def test_thread_safe_logging(self, logger):
        """Test concurrent logging from multiple threads"""
        def log_events(thread_id: int, count: int):
            for i in range(count):
                logger.log("tool_call", "execution",
                          thread=thread_id, iteration=i)

        threads = []
        events_per_thread = 100
        num_threads = 10

        # Start threads
        for t in range(num_threads):
            thread = threading.Thread(target=log_events, args=(t, events_per_thread))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Verify all events logged
        with open(logger.log_file, 'r') as f:
            lines = f.readlines()
            # +1 for session_start, +1 for expected close
            assert len(lines) >= num_threads * events_per_thread

    def test_context_tracking(self, logger):
        """Test context is properly tracked"""
        logger.set_context(agent_name="analyst", workflow_id="test-workflow")
        logger.log("tool_call", "execution", tool="test")

        # Read last logged event
        with open(logger.log_file, 'r') as f:
            lines = f.readlines()
            last_event = json.loads(lines[-1])

        assert last_event["agent_name"] == "analyst"
        assert last_event["workflow_id"] == "test-workflow"

    def test_error_logging(self, logger):
        """Test error logging captures exception details"""
        try:
            raise ValueError("Test error")
        except Exception as e:
            logger.log_error(e, {"context": "test"})

        with open(logger.log_file, 'r') as f:
            lines = f.readlines()
            error_event = json.loads(lines[-1])

        assert error_event["event_type"] == "error"
        assert error_event["category"] == "error"
        assert "ValueError" in error_event["error_type"]
        assert "Test error" in error_event["error_message"]

    def test_schema_validation_enabled(self, logger):
        """Test schema validation when enabled"""
        # Valid log should work
        logger.log("agent_action", "execution")

        # Invalid log should add validation error field
        logger.log("invalid_type", "execution")

        with open(logger.log_file, 'r') as f:
            lines = f.readlines()
            invalid_event = json.loads(lines[-1])

        assert "schema_validation_error" in invalid_event

    def test_zero_performance_impact(self, logger):
        """Test logging has minimal performance impact (<1ms per event)"""
        iterations = 100
        start_time = time.time()

        for i in range(iterations):
            logger.log("tool_call", "execution", iteration=i)

        duration_ms = (time.time() - start_time) * 1000
        avg_per_log = duration_ms / iterations

        # Each log should take <1ms on average
        assert avg_per_log < 1.0


class TestMADFLogger:
    """Test MADF Logger wrapper and decorators"""

    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def madf_logger(self, temp_log_dir):
        """Create MADF logger with temp directory"""
        # Reset global logger instances
        import src.core.quick_logger as ql
        import src.core.madf_logger as ml
        ql._logger_instance = None
        ml._madf_logger = None

        with patch.dict(os.environ, {"MADF_LOG_PATH": temp_log_dir}):
            logger = MADFLogger(story_id="test")
            yield logger

            # Cleanup
            ql._logger_instance = None
            ml._madf_logger = None

    def test_workflow_context_setting(self, madf_logger):
        """Test workflow context is properly set"""
        madf_logger.set_workflow_context(
            workflow_id="test-wf",
            agent_name="analyst",
            thread_id="thread-123",
            trace_id="trace-456"
        )

        # Context should be propagated to underlying logger
        assert madf_logger.logger.workflow_id == "test-wf"
        assert madf_logger.logger.current_agent == "analyst"

    def test_workflow_start_end_logging(self, madf_logger):
        """Test workflow lifecycle logging"""
        madf_logger.log_workflow_start(
            workflow_id="test-wf",
            task_description="Test task"
        )

        madf_logger.log_workflow_end(
            workflow_id="test-wf",
            success=True,
            duration_ms=1500
        )

        with open(madf_logger.logger.log_file, 'r') as f:
            lines = f.readlines()
            events = [json.loads(line) for line in lines]

        start_events = [e for e in events if e["event_type"] == "workflow_start"]
        end_events = [e for e in events if e["event_type"] == "workflow_end"]

        assert len(start_events) >= 1
        assert len(end_events) >= 1

    def test_agent_transition_logging(self, madf_logger):
        """Test agent handoff logging"""
        madf_logger.log_agent_transition(
            from_agent="orchestrator",
            to_agent="analyst",
            reason="Code analysis required"
        )

        with open(madf_logger.logger.log_file, 'r') as f:
            lines = f.readlines()
            last_event = json.loads(lines[-1])

        assert last_event["event_type"] == "agent_transition"
        assert last_event["from_agent"] == "orchestrator"
        assert last_event["to_agent"] == "analyst"

    def test_decision_logging(self, madf_logger):
        """Test decision point logging"""
        madf_logger.log_decision(
            decision_point="tool_selection",
            options_considered=["grep", "semantic_search"],
            choice_made="semantic_search",
            rationale="More accurate for this query"
        )

        with open(madf_logger.logger.log_file, 'r') as f:
            lines = f.readlines()
            last_event = json.loads(lines[-1])

        assert last_event["event_type"] == "decision"
        assert last_event["category"] == "decision"


class TestLogAgentExecutionDecorator:
    """Test @log_agent_execution decorator"""

    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_decorator_on_sync_function(self, temp_log_dir):
        """Test decorator works on synchronous functions"""
        # Reset global logger instances
        import src.core.quick_logger as ql
        ql._logger_instance = None

        with patch.dict(os.environ, {"MADF_LOG_PATH": temp_log_dir}):
            @log_agent_execution(agent_name="test_agent")
            def sync_function():
                return "result"

            result = sync_function()
            assert result == "result"

            # Check logs were created
            logger = get_logger("1.4")
            with open(logger.log_file, 'r') as f:
                lines = f.readlines()
                events = [json.loads(line) for line in lines]

            action_events = [e for e in events if e.get("action") == "sync_function"]
            assert len(action_events) >= 2  # start and end

            # Cleanup
            ql._logger_instance = None

    @pytest.mark.asyncio
    async def test_decorator_on_async_function(self, temp_log_dir):
        """Test decorator works on async functions"""
        # Reset global logger instances
        import src.core.quick_logger as ql
        ql._logger_instance = None

        with patch.dict(os.environ, {"MADF_LOG_PATH": temp_log_dir}):
            @log_agent_execution(agent_name="test_agent")
            async def async_function():
                return "async_result"

            result = await async_function()
            assert result == "async_result"

            # Check logs were created
            logger = get_logger("1.4")
            with open(logger.log_file, 'r') as f:
                lines = f.readlines()
                events = [json.loads(line) for line in lines]

            action_events = [e for e in events if e.get("action") == "async_function"]
            assert len(action_events) >= 2  # start and end

            # Cleanup
            ql._logger_instance = None

    def test_decorator_logs_exceptions(self, temp_log_dir):
        """Test decorator logs exceptions properly"""
        # Reset global logger instances
        import src.core.quick_logger as ql
        ql._logger_instance = None

        with patch.dict(os.environ, {"MADF_LOG_PATH": temp_log_dir}):
            @log_agent_execution(agent_name="test_agent")
            def failing_function():
                raise ValueError("Test exception")

            with pytest.raises(ValueError):
                failing_function()

            # Check error was logged
            logger = get_logger("1.4")
            with open(logger.log_file, 'r') as f:
                lines = f.readlines()
                events = [json.loads(line) for line in lines]

            error_events = [e for e in events if e.get("success") is False]
            assert len(error_events) >= 1
            assert "Test exception" in str(error_events[-1])

            # Cleanup
            ql._logger_instance = None

    def test_decorator_measures_duration(self, temp_log_dir):
        """Test decorator measures execution duration"""
        # Reset global logger instances
        import src.core.quick_logger as ql
        ql._logger_instance = None

        with patch.dict(os.environ, {"MADF_LOG_PATH": temp_log_dir}):
            @log_agent_execution(agent_name="test_agent")
            def slow_function():
                time.sleep(0.1)  # 100ms
                return "done"

            slow_function()

            # Check duration was logged
            logger = get_logger("1.4")
            with open(logger.log_file, 'r') as f:
                lines = f.readlines()
                events = [json.loads(line) for line in lines]

            duration_events = [e for e in events if e.get("duration_ms", 0) > 0]
            assert len(duration_events) >= 1
            assert duration_events[-1]["duration_ms"] >= 100

            # Cleanup
            ql._logger_instance = None


class TestIntegration:
    """Integration tests for complete logging system"""

    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_full_workflow_logging(self, temp_log_dir):
        """Test complete workflow logging scenario"""
        # Reset global logger instances
        import src.core.quick_logger as ql
        import src.core.madf_logger as ml
        ql._logger_instance = None
        ml._madf_logger = None

        with patch.dict(os.environ, {"MADF_LOG_PATH": temp_log_dir}):
            madf_logger = get_madf_logger("test")

            # Simulate workflow
            madf_logger.set_workflow_context(
                workflow_id="integration-test",
                agent_name="orchestrator"
            )

            madf_logger.log_workflow_start(
                workflow_id="integration-test",
                task_description="Integration test"
            )

            madf_logger.log_agent_transition(
                from_agent="orchestrator",
                to_agent="analyst",
                reason="Code analysis needed"
            )

            madf_logger.log_decision(
                decision_point="analysis_method",
                options_considered=["static", "semantic"],
                choice_made="semantic",
                rationale="Better context"
            )

            madf_logger.log_workflow_end(
                workflow_id="integration-test",
                success=True,
                duration_ms=2000
            )

            # Verify all events logged
            logger = madf_logger.logger
            with open(logger.log_file, 'r') as f:
                lines = f.readlines()
                events = [json.loads(line) for line in lines]

            assert any(e["event_type"] == "workflow_start" for e in events)
            assert any(e["event_type"] == "agent_transition" for e in events)
            assert any(e["event_type"] == "decision" for e in events)
            assert any(e["event_type"] == "workflow_end" for e in events)

            # Cleanup
            ql._logger_instance = None
            ml._madf_logger = None
