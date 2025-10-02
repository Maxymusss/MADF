"""
Enhanced Validator Agent Tests
Tests for validator_agent_enhanced.py with Story 1.4 integrations
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.agents.validator_agent_enhanced import ValidatorAgentEnhanced


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_story_components():
    """Mock Story 1.4 components"""
    with patch('src.agents.validator_agent_enhanced.SentryManager') as mock_sentry, \
         patch('src.agents.validator_agent_enhanced.MADFOptimizer') as mock_dspy, \
         patch('src.agents.validator_agent_enhanced.PostgresManager') as mock_pg, \
         patch('src.agents.validator_agent_enhanced.LogAnalyzer') as mock_analyzer, \
         patch('src.agents.validator_agent_enhanced.PatternExtractor') as mock_extractor, \
         patch('src.core.sentry_integration.sentry_sdk'):  # Mock sentry_sdk globally

        # Configure mocks
        mock_sentry.return_value.initialize = Mock()
        mock_sentry.return_value._initialized = True
        mock_dspy.return_value.initialize = Mock()
        mock_pg.return_value.initialize = Mock()
        mock_analyzer.return_value.initialize = Mock()
        mock_extractor.return_value.initialize = Mock()

        yield {
            'sentry': mock_sentry,
            'dspy': mock_dspy,
            'postgres': mock_pg,
            'analyzer': mock_analyzer,
            'extractor': mock_extractor
        }


@pytest.fixture
def validator_agent(mock_story_components):
    """Create enhanced validator agent with mocked components"""
    agent = ValidatorAgentEnhanced(
        enable_sentry=True,
        enable_dspy=True,
        enable_postgres=True
    )

    yield agent

    agent.close()


@pytest.fixture
def validator_agent_minimal():
    """Create validator agent with minimal components (all disabled)"""
    agent = ValidatorAgentEnhanced(
        enable_sentry=False,
        enable_dspy=False,
        enable_postgres=False
    )

    yield agent


# ============================================================================
# TEST: Initialization
# ============================================================================

class TestInitialization:
    """Test agent initialization"""

    def test_agent_creation(self, validator_agent):
        """Test agent can be created"""
        assert validator_agent is not None
        assert validator_agent.name == "Validator"

    def test_tools_available(self, validator_agent):
        """Test validator tools are available"""
        tools = validator_agent.get_available_tools()

        assert 'pytest_execution' in tools
        assert 'dspy_optimization' in tools
        assert 'sentry_monitoring' in tools
        assert 'postgres_analysis' in tools

    def test_components_initialized(self, validator_agent):
        """Test Story 1.4 components initialized"""
        assert validator_agent.sentry is not None
        assert validator_agent.dspy_optimizer is not None
        assert validator_agent.postgres is not None
        assert validator_agent.log_analyzer is not None
        assert validator_agent.pattern_extractor is not None

    def test_minimal_initialization(self, validator_agent_minimal):
        """Test agent works with disabled components"""
        assert validator_agent_minimal.sentry is None
        assert validator_agent_minimal.dspy_optimizer is None
        assert validator_agent_minimal.postgres is None


# ============================================================================
# TEST: Test Execution
# ============================================================================

class TestTestExecution:
    """Test pytest execution functionality"""

    @patch('src.agents.validator_agent_enhanced.subprocess.run')
    def test_run_tests_success(self, mock_run, validator_agent):
        """Test successful test execution"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="All tests passed",
            stderr=""
        )

        result = validator_agent.run_tests(test_path="tests/test_example.py")

        assert result['success'] is True
        assert result['exit_code'] == 0
        # subprocess.run called at least once for pytest
        assert mock_run.call_count >= 1

    @patch('src.agents.validator_agent_enhanced.subprocess.run')
    def test_run_tests_failure(self, mock_run, validator_agent):
        """Test failed test execution"""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="Test failed"
        )

        result = validator_agent.run_tests(test_path="tests/test_example.py")

        assert result['success'] is False
        assert result['exit_code'] == 1

    @patch('src.agents.validator_agent_enhanced.subprocess.run')
    def test_run_tests_timeout(self, mock_run, validator_agent):
        """Test test execution timeout"""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("pytest", 300)

        result = validator_agent.run_tests()

        assert result['success'] is False
        assert 'timeout' in result['error'].lower()


# ============================================================================
# TEST: Performance Analysis
# ============================================================================

class TestPerformanceAnalysis:
    """Test performance analysis functionality"""

    def test_analyze_performance_session(self, validator_agent):
        """Test session performance analysis"""
        # Mock log_analyzer
        validator_agent.log_analyzer.get_session_summary = Mock(
            return_value="Session summary: 5 events, 100ms total"
        )

        result = validator_agent.analyze_performance(session_id="test_session")

        assert result['analysis_type'] == 'session'
        assert result['session_id'] == 'test_session'
        assert 'summary' in result

    def test_analyze_performance_story(self, validator_agent):
        """Test story performance analysis"""
        # Mock postgres query
        validator_agent.postgres.execute_query = Mock(
            return_value=[
                {'session_id': 'session1'},
                {'session_id': 'session2'}
            ]
        )

        validator_agent.log_analyzer.get_session_summary = Mock(
            return_value="Summary"
        )

        result = validator_agent.analyze_performance(story_id="1.4")

        assert result['analysis_type'] == 'story'
        assert result['story_id'] == '1.4'
        assert result['sessions_analyzed'] == 2

    def test_analyze_performance_disabled(self, validator_agent_minimal):
        """Test analysis when Postgres disabled"""
        result = validator_agent_minimal.analyze_performance(session_id="test")

        assert 'error' in result
        assert 'disabled' in result['error'].lower()


# ============================================================================
# TEST: Error Pattern Extraction
# ============================================================================

class TestErrorPatterns:
    """Test error pattern extraction"""

    def test_extract_error_patterns(self, validator_agent):
        """Test error pattern extraction"""
        # Mock pattern extractor
        validator_agent.pattern_extractor.find_error_patterns = Mock(
            return_value=[
                {'error_type': 'ValueError', 'occurrence_count': 5},
                {'error_type': 'KeyError', 'occurrence_count': 3}
            ]
        )

        patterns = validator_agent.extract_error_patterns(min_occurrences=2)

        assert len(patterns) == 2
        assert patterns[0]['error_type'] == 'ValueError'

    def test_extract_error_patterns_disabled(self, validator_agent_minimal):
        """Test error extraction when disabled"""
        patterns = validator_agent_minimal.extract_error_patterns()

        assert patterns == []


# ============================================================================
# TEST: DSPy Optimization
# ============================================================================

class TestDSPyOptimization:
    """Test DSPy agent optimization"""

    def test_optimize_with_dspy_success(self, validator_agent):
        """Test successful agent optimization"""
        # Mock optimizer
        validator_agent.dspy_optimizer.optimize_agent = Mock(
            return_value=(
                Mock(),  # optimized_module
                {
                    'baseline_score': 0.7,
                    'optimized_score': 0.85,
                    'improvement': 0.15
                }
            )
        )

        validator_agent.dspy_optimizer.save_optimized_module = Mock(
            return_value=Path("optimized/qa_agent.json")
        )

        result = validator_agent.optimize_with_dspy(target_agent="qa_agent")

        assert result['success'] is True
        assert result['metrics']['improvement'] == 0.15

    def test_optimize_with_dspy_insufficient_data(self, validator_agent):
        """Test optimization with insufficient training data"""
        validator_agent.dspy_optimizer.optimize_agent = Mock(
            side_effect=ValueError("Insufficient training examples")
        )

        result = validator_agent.optimize_with_dspy()

        assert result['success'] is False
        assert 'insufficient' in result['error'].lower()

    def test_optimize_disabled(self, validator_agent_minimal):
        """Test optimization when DSPy disabled"""
        result = validator_agent_minimal.optimize_with_dspy()

        assert 'error' in result
        assert 'disabled' in result['error'].lower()


# ============================================================================
# TEST: Implementation Validation
# ============================================================================

class TestValidation:
    """Test implementation validation"""

    def test_validate_with_dspy(self, validator_agent):
        """Test validation using DSPy QA module"""
        # Mock QA module prediction
        mock_prediction = Mock()
        mock_prediction.validation_result = "PASS"
        mock_prediction.issues_found = []
        mock_prediction.confidence = 0.95

        with patch('src.agents.validator_agent_enhanced.MADFQAModule') as mock_qa:
            mock_qa.return_value.forward = Mock(return_value=mock_prediction)

            result = validator_agent.validate_implementation(
                implementation="def test(): pass",
                acceptance_criteria="Function should exist",
                test_results={"success": True}
            )

            assert result['validated'] is True
            assert result['validation_result'] == "PASS"
            assert result['confidence'] == 0.95

    def test_validate_simple_fallback(self, validator_agent_minimal):
        """Test simple validation fallback"""
        result = validator_agent_minimal.validate_implementation(
            implementation="code",
            acceptance_criteria="criteria",
            test_results={"success": True}
        )

        assert result['validated'] is True
        assert result['method'] == "simple_heuristic"


# ============================================================================
# TEST: QA Report Generation
# ============================================================================

class TestQAReport:
    """Test QA report generation"""

    @patch('src.agents.validator_agent_enhanced.subprocess.run')
    def test_generate_qa_report(self, mock_run, validator_agent):
        """Test comprehensive QA report generation"""
        # Mock test execution
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        # Mock components
        validator_agent.log_analyzer.get_session_summary = Mock(
            return_value="Performance: Good"
        )
        validator_agent.pattern_extractor.find_error_patterns = Mock(
            return_value=[]
        )

        report = validator_agent.generate_qa_report(story_id="1.4")

        assert "# QA Report - Story 1.4" in report
        assert "Test Execution Results" in report
        assert "Performance Analysis" in report


# ============================================================================
# TEST: Task Processing
# ============================================================================

class TestTaskProcessing:
    """Test process_task dispatcher"""

    @patch('src.agents.validator_agent_enhanced.subprocess.run')
    def test_process_test_task(self, mock_run, validator_agent):
        """Test processing test execution task"""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        result = validator_agent.process_task(
            "Run tests for story 1.4",
            {"story_id": "1.4"}
        )

        assert 'success' in result or 'exit_code' in result

    def test_process_performance_task(self, validator_agent):
        """Test processing performance analysis task"""
        validator_agent.postgres.execute_query = Mock(return_value=[])
        validator_agent.log_analyzer.get_session_summary = Mock(return_value="")

        result = validator_agent.process_task(
            "Analyze performance for story 1.4",
            {"story_id": "1.4"}
        )

        assert 'analysis_type' in result or 'error' in result


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
