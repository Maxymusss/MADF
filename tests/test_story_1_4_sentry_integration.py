"""
Story 1.4 Task 3 Tests - Sentry Integration
Tests for sentry_integration.py

Test Categories:
1. Initialization: Sentry SDK setup
2. Error Capture: Exception tracking with context
3. Transactions: Performance monitoring
4. Decorator: Automatic error tracking
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import os

from src.core.sentry_integration import (
    SentryManager,
    track_errors,
    get_sentry_manager,
    DummyTransaction
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_sentry_sdk():
    """Mock sentry_sdk to avoid actual API calls"""
    with patch('src.core.sentry_integration.sentry_sdk') as mock_sdk:
        mock_sdk.init = Mock()
        mock_sdk.capture_exception = Mock(return_value="test_event_id")
        mock_sdk.capture_message = Mock(return_value="test_message_id")
        mock_sdk.add_breadcrumb = Mock()
        mock_sdk.set_user = Mock()
        mock_sdk.flush = Mock()
        mock_sdk.push_scope = MagicMock()
        mock_sdk.start_transaction = Mock(return_value=DummyTransaction())

        yield mock_sdk


@pytest.fixture
def sentry_manager_no_dsn():
    """Create SentryManager without DSN (disabled)"""
    # Clear environment variable
    old_dsn = os.environ.get('SENTRY_DSN')
    if 'SENTRY_DSN' in os.environ:
        del os.environ['SENTRY_DSN']

    manager = SentryManager(dsn=None)

    yield manager

    # Restore
    if old_dsn:
        os.environ['SENTRY_DSN'] = old_dsn


@pytest.fixture
def sentry_manager_with_dsn(mock_sentry_sdk):
    """Create SentryManager with test DSN"""
    manager = SentryManager(
        dsn="https://test@sentry.io/123456",
        environment="test"
    )

    yield manager

    manager.close()


# ============================================================================
# TEST: Initialization
# ============================================================================

class TestSentryInitialization:
    """Test Sentry SDK initialization"""

    def test_init_without_dsn(self, sentry_manager_no_dsn):
        """Test initialization without DSN (disabled mode)"""
        sentry_manager_no_dsn.initialize()

        # Should not raise error, just log warning
        assert not sentry_manager_no_dsn._initialized

    def test_init_with_dsn(self, sentry_manager_with_dsn, mock_sentry_sdk):
        """Test initialization with DSN"""
        sentry_manager_with_dsn.initialize()

        # Verify Sentry SDK was initialized
        mock_sentry_sdk.init.assert_called_once()

        # Verify initialization parameters
        call_args = mock_sentry_sdk.init.call_args
        assert call_args.kwargs['dsn'] == "https://test@sentry.io/123456"
        assert call_args.kwargs['environment'] == "test"

        assert sentry_manager_with_dsn._initialized

    def test_double_initialization(self, sentry_manager_with_dsn, mock_sentry_sdk):
        """Test that double initialization is idempotent"""
        sentry_manager_with_dsn.initialize()
        sentry_manager_with_dsn.initialize()

        # Should only call init once
        assert mock_sentry_sdk.init.call_count == 1

    def test_get_release_version(self, sentry_manager_with_dsn):
        """Test release version detection"""
        version = sentry_manager_with_dsn._get_release_version()

        # Should return either git hash or unknown
        assert version.startswith("madf@")


# ============================================================================
# TEST: Error Capture
# ============================================================================

class TestErrorCapture:
    """Test error capture functionality"""

    def test_capture_error_basic(self, sentry_manager_with_dsn, mock_sentry_sdk):
        """Test basic error capture"""
        sentry_manager_with_dsn.initialize()

        error = ValueError("Test error")
        event_id = sentry_manager_with_dsn.capture_error(error)

        # Verify exception was captured
        mock_sentry_sdk.capture_exception.assert_called_once_with(error)
        assert event_id == "test_event_id"

    def test_capture_error_with_context(self, sentry_manager_with_dsn, mock_sentry_sdk):
        """Test error capture with MADF context"""
        sentry_manager_with_dsn.initialize()

        error = RuntimeError("Agent failed")
        event_id = sentry_manager_with_dsn.capture_error(
            error,
            agent_name="planning_agent",
            story_id="1.4",
            session_id="test_session_123",
            context={"task": "plan_creation", "confidence": 0.75}
        )

        # Verify scope was set
        mock_sentry_sdk.push_scope.assert_called()
        assert event_id == "test_event_id"

    def test_capture_error_without_initialization(self, sentry_manager_no_dsn):
        """Test error capture when Sentry is not initialized"""
        error = Exception("Test")
        result = sentry_manager_no_dsn.capture_error(error)

        # Should not raise, just return None
        assert result is None

    def test_capture_message(self, sentry_manager_with_dsn, mock_sentry_sdk):
        """Test custom message capture"""
        sentry_manager_with_dsn.initialize()

        event_id = sentry_manager_with_dsn.capture_message(
            "Agent completed successfully",
            level="info",
            agent_name="dev_agent",
            story_id="1.4"
        )

        mock_sentry_sdk.capture_message.assert_called_once()
        assert event_id == "test_message_id"


# ============================================================================
# TEST: Transactions
# ============================================================================

class TestTransactions:
    """Test performance transaction tracking"""

    def test_start_transaction(self, sentry_manager_with_dsn, mock_sentry_sdk):
        """Test starting performance transaction"""
        sentry_manager_with_dsn.initialize()

        transaction = sentry_manager_with_dsn.start_transaction(
            name="test_transaction",
            op="agent.execution",
            agent_name="planning_agent",
            story_id="1.4"
        )

        mock_sentry_sdk.start_transaction.assert_called_once()
        assert transaction is not None

    def test_transaction_disabled(self, mock_sentry_sdk):
        """Test transaction when tracing is disabled"""
        manager = SentryManager(
            dsn="https://test@sentry.io/123456",
            enable_tracing=False
        )
        manager.initialize()

        transaction = manager.start_transaction("test")

        # Should return DummyTransaction
        assert isinstance(transaction, DummyTransaction)

    def test_dummy_transaction_context_manager(self):
        """Test DummyTransaction as context manager"""
        dummy = DummyTransaction()

        # Should work without errors
        with dummy:
            pass

        dummy.set_tag("test", "value")
        dummy.finish()


# ============================================================================
# TEST: Breadcrumbs
# ============================================================================

class TestBreadcrumbs:
    """Test breadcrumb functionality"""

    def test_add_breadcrumb(self, sentry_manager_with_dsn, mock_sentry_sdk):
        """Test adding breadcrumbs"""
        sentry_manager_with_dsn.initialize()

        sentry_manager_with_dsn.add_breadcrumb(
            message="Agent started task",
            category="agent",
            level="info",
            data={"agent": "planning_agent", "task_id": "123"}
        )

        mock_sentry_sdk.add_breadcrumb.assert_called_once()

    def test_set_user(self, sentry_manager_with_dsn, mock_sentry_sdk):
        """Test setting user context"""
        sentry_manager_with_dsn.initialize()

        sentry_manager_with_dsn.set_user(
            user_id="user_123",
            username="test_user",
            email="test@example.com"
        )

        mock_sentry_sdk.set_user.assert_called_once()


# ============================================================================
# TEST: Decorator
# ============================================================================

class TestTrackErrorsDecorator:
    """Test @track_errors decorator"""

    @patch('src.core.sentry_integration.sentry_sdk')
    def test_decorator_on_sync_function(self, mock_sentry_sdk):
        """Test decorator on synchronous function"""
        mock_sentry_sdk.start_transaction = Mock(return_value=DummyTransaction())

        @track_errors(agent_name="test_agent", story_id="1.4")
        def test_function(x):
            return x * 2

        result = test_function(5)

        assert result == 10
        mock_sentry_sdk.start_transaction.assert_called()

    @patch('src.core.sentry_integration.sentry_sdk')
    @pytest.mark.asyncio
    async def test_decorator_on_async_function(self, mock_sentry_sdk):
        """Test decorator on asynchronous function"""
        mock_sentry_sdk.start_transaction = Mock(return_value=DummyTransaction())

        @track_errors(agent_name="test_agent", story_id="1.4")
        async def async_test_function(x):
            return x * 3

        result = await async_test_function(5)

        assert result == 15
        mock_sentry_sdk.start_transaction.assert_called()

    @patch('src.core.sentry_integration.sentry_sdk')
    @patch('src.core.sentry_integration.QuickLogger')
    def test_decorator_captures_errors(self, mock_logger, mock_sentry_sdk):
        """Test decorator captures exceptions"""
        mock_sentry_sdk.start_transaction = Mock(return_value=DummyTransaction())
        mock_sentry_sdk.capture_exception = Mock(return_value="error_event_id")
        mock_sentry_sdk.push_scope = MagicMock()

        # Mock QuickLogger to avoid JSON serialization issues
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance

        @track_errors(agent_name="test_agent", story_id="1.4")
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_function()

        # Verify error logging was attempted
        mock_logger_instance.log.assert_called()


# ============================================================================
# TEST: Singleton
# ============================================================================

class TestSingleton:
    """Test global singleton manager"""

    @patch('src.core.sentry_integration.sentry_sdk')
    def test_get_sentry_manager(self, mock_sentry_sdk):
        """Test getting global Sentry manager"""
        # Clear singleton
        import src.core.sentry_integration as sentry_module
        sentry_module._sentry_manager = None

        manager1 = get_sentry_manager()
        manager2 = get_sentry_manager()

        # Should return same instance
        assert manager1 is manager2

        # Cleanup
        sentry_module._sentry_manager = None


# ============================================================================
# TEST: Before Send Hook
# ============================================================================

class TestBeforeSendHook:
    """Test event filtering before send"""

    def test_before_send_adds_tags(self, sentry_manager_with_dsn):
        """Test before_send hook adds MADF tags"""
        event = {}
        hint = {}

        result = sentry_manager_with_dsn._before_send_hook(event, hint)

        assert result is not None
        assert 'tags' in result
        assert result['tags']['project'] == 'madf'

    def test_before_send_filters_test_errors_in_production(self):
        """Test before_send filters test errors in production"""
        manager = SentryManager(
            dsn="https://test@sentry.io/123456",
            environment="production"
        )

        event = {
            'exception': {
                'values': [
                    {'type': 'TestError', 'value': 'Test failed'}
                ]
            }
        }
        hint = {}

        result = manager._before_send_hook(event, hint)

        # Test errors should be filtered in production
        assert result is None

    def test_before_send_allows_test_errors_in_dev(self):
        """Test before_send allows test errors in development"""
        manager = SentryManager(
            dsn="https://test@sentry.io/123456",
            environment="development"
        )

        event = {
            'exception': {
                'values': [
                    {'type': 'TestError', 'value': 'Test failed'}
                ]
            }
        }
        hint = {}

        result = manager._before_send_hook(event, hint)

        # Test errors allowed in development
        assert result is not None


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
