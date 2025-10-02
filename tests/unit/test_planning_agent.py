"""
Unit tests for Planning Agent
Test outputs saved to D:\\BT\\madf\\unit\\
"""

import pytest
import json
from datetime import datetime
from pathlib import Path

from langgraph_core.agents.planning import planning_agent
from langgraph_core.models.state import WorkflowState

# Test output directory
TEST_OUTPUT_DIR = Path("D:/BT/madf/unit")
TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class TestPlanningAgent:
    """Comprehensive unit tests for Planning Agent"""

    def test_basic_planning_agent_execution(self):
        """Test basic planning agent functionality"""
        initial_state = WorkflowState(
            workflow_id="test_planning_123",
            current_agent="init"
        )

        result_state = planning_agent(initial_state)

        # Verify agent transition
        assert result_state.current_agent == "research"
        assert result_state.workflow_id == "test_planning_123"

        # Verify plan creation
        assert result_state.plan is not None
        assert isinstance(result_state.plan, dict)

    def test_plan_structure_validation(self):
        """Test generated plan structure"""
        state = WorkflowState(workflow_id="test_plan_structure", current_agent="planning")

        result = planning_agent(state)

        plan = result.plan
        required_fields = ["plan_id", "title", "objective", "geographic_coverage", "data_sources"]

        for field in required_fields:
            assert field in plan, f"Missing required field: {field}"

        # Verify field types
        assert isinstance(plan["plan_id"], str)
        assert isinstance(plan["title"], str)
        assert isinstance(plan["objective"], str)
        assert isinstance(plan["geographic_coverage"], list)
        assert isinstance(plan["data_sources"], list)

    def test_plan_approval_logic(self):
        """Test plan approval logic"""
        state = WorkflowState(workflow_id="test_approval", current_agent="planning")

        # Test with default approved plan
        result = planning_agent(state)
        assert result.plan_approved is True
        assert len(result.errors) == 0

        # Test with pre-existing unapproved plan
        state_unapproved = WorkflowState(workflow_id="test_unapproved", current_agent="planning")
        state_unapproved.plan = {
            "plan_id": "test",
            "title": "Test",
            "objective": "Test",
            "geographic_coverage": ["US"],
            "data_sources": ["Test"],
            "approved": False
        }

        result_unapproved = planning_agent(state_unapproved)
        assert result_unapproved.plan_approved is False
        assert len(result_unapproved.errors) > 0
        assert "not approved" in result_unapproved.errors[0].lower()

    def test_missing_plan_fields_validation(self):
        """Test validation of missing required plan fields"""
        state = WorkflowState(workflow_id="test_invalid_plan", current_agent="planning")

        # Set incomplete plan
        state.plan = {
            "plan_id": "incomplete",
            "title": "Incomplete Plan"
            # Missing required fields
        }

        result = planning_agent(state)

        # Should have errors for missing fields
        assert len(result.errors) > 0
        error_text = " ".join(result.errors).lower()
        assert "missing" in error_text

    def test_state_preservation(self):
        """Test that original state is preserved where appropriate"""
        original_timestamp = datetime.utcnow()
        state = WorkflowState(
            workflow_id="test_preservation",
            current_agent="planning",
            timestamp=original_timestamp
        )
        state.metadata["original_key"] = "original_value"

        result = planning_agent(state)

        # Workflow ID should be preserved
        assert result.workflow_id == state.workflow_id

        # Original metadata should be preserved
        assert "original_key" in result.metadata
        assert result.metadata["original_key"] == "original_value"

        # Timestamp should be updated (allowing for small differences due to execution time)
        time_diff = (result.timestamp - original_timestamp).total_seconds()
        assert time_diff >= 0  # Should be same or later

    def test_metadata_updates(self):
        """Test metadata updates during planning"""
        state = WorkflowState(workflow_id="test_metadata", current_agent="planning")

        result = planning_agent(state)

        # Check planning-specific metadata
        assert "planning_complete" in result.metadata
        assert result.metadata["planning_complete"] is True
        assert "plan_id" in result.metadata
        assert "geographic_coverage" in result.metadata
        assert "data_sources" in result.metadata
        assert "planning_timestamp" in result.metadata

    def test_error_handling(self):
        """Test error handling in planning agent"""
        # This test depends on the specific error conditions in the agent
        # For now, test the basic error handling structure

        state = WorkflowState(workflow_id="test_error", current_agent="planning")

        # The planning agent should handle its own errors gracefully
        result = planning_agent(state)

        # Should not raise exceptions, even if there are errors
        assert isinstance(result, WorkflowState)
        assert result.workflow_id == "test_error"

    def test_geographic_coverage_content(self):
        """Test geographic coverage includes expected regions"""
        state = WorkflowState(workflow_id="test_geo", current_agent="planning")

        result = planning_agent(state)
        geographic_coverage = result.plan["geographic_coverage"]

        # Check for key regions
        expected_regions = ["CN", "TW", "KR", "HK", "SG", "US"]
        for region in expected_regions:
            assert region in geographic_coverage, f"Missing region: {region}"

    def test_data_sources_content(self):
        """Test data sources include expected APIs"""
        state = WorkflowState(workflow_id="test_data_sources", current_agent="planning")

        result = planning_agent(state)
        data_sources = result.plan["data_sources"]

        # Check for expected data sources
        expected_sources = ["NewsAPI", "Yahoo Finance", "Alpha Vantage"]
        for source in expected_sources:
            assert source in data_sources, f"Missing data source: {source}"

    def test_pre_existing_plan_handling(self):
        """Test handling of pre-existing plans"""
        existing_plan = {
            "plan_id": "existing_plan",
            "title": "Pre-existing Plan",
            "objective": "Test existing",
            "geographic_coverage": ["TEST"],
            "market_types": ["test"],
            "data_sources": ["TestAPI"],
            "approved": True
        }

        state = WorkflowState(workflow_id="test_existing", current_agent="planning")
        state.plan = existing_plan

        result = planning_agent(state)

        # Should use existing plan if valid
        assert result.plan == existing_plan
        assert result.plan_approved is True
        assert len(result.errors) == 0

    def test_agent_logging(self):
        """Test that agent logging doesn't cause errors"""
        state = WorkflowState(workflow_id="test_logging", current_agent="planning")

        # Should not raise any logging-related exceptions
        result = planning_agent(state)

        assert isinstance(result, WorkflowState)
        assert result.workflow_id == "test_logging"

    @pytest.fixture(autouse=True)
    def save_test_results(self, request):
        """Save test results to D:/BT/madf/unit/"""
        yield  # Run the test

        test_name = request.node.name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        result_file = TEST_OUTPUT_DIR / f"planning_agent_{test_name}_{timestamp}.json"

        test_result = {
            "test_name": test_name,
            "timestamp": datetime.now().isoformat(),
            "status": "passed" if not hasattr(request.node, "rep_call") or request.node.rep_call.passed else "failed",
            "module": __name__
        }

        with open(result_file, 'w') as f:
            json.dump(test_result, f, indent=2)

def pytest_runtest_makereport(item, call):
    """Hook to capture test results"""
    if call.when == "call":
        setattr(item, "rep_" + call.when, call)