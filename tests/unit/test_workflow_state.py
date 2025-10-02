"""
Unit tests for WorkflowState Pydantic model
Test outputs saved to D:\\BT\\madf\\unit\\
"""

import pytest
import json
from datetime import datetime
from pathlib import Path

from langgraph_core.models.state import WorkflowState

# Test output directory
TEST_OUTPUT_DIR = Path("D:/BT/madf/unit")
TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class TestWorkflowState:
    """Comprehensive unit tests for WorkflowState"""

    def test_valid_state_creation(self):
        """Test valid WorkflowState creation"""
        state = WorkflowState(
            workflow_id="test_123",
            current_agent="planning"
        )

        assert state.workflow_id == "test_123"
        assert state.current_agent == "planning"
        assert isinstance(state.timestamp, datetime)
        assert state.plan is None
        assert state.errors == []
        assert state.retry_count == 0

    def test_required_fields_validation(self):
        """Test Pydantic validation for required fields"""
        with pytest.raises(ValueError):
            WorkflowState()  # Missing required fields

        with pytest.raises(ValueError):
            WorkflowState(workflow_id="test")  # Missing current_agent

    def test_add_error_method(self):
        """Test error addition functionality"""
        state = WorkflowState(workflow_id="test", current_agent="planning")

        state.add_error("Test error message")

        assert len(state.errors) == 1
        assert "Test error message" in state.errors[0]
        assert datetime.utcnow().isoformat()[:10] in state.errors[0]  # Date check

    def test_set_current_agent_method(self):
        """Test agent setting functionality"""
        state = WorkflowState(workflow_id="test", current_agent="planning")
        original_timestamp = state.timestamp

        # Wait a tiny bit to ensure timestamp difference
        import time
        time.sleep(0.001)

        state.set_current_agent("research")

        assert state.current_agent == "research"
        assert state.timestamp > original_timestamp

    def test_is_complete_method(self):
        """Test workflow completion logic"""
        state = WorkflowState(workflow_id="test", current_agent="planning")

        # Initially incomplete
        assert not state.is_complete()

        # Still incomplete with partial completion
        state.validation_status = "approved"
        assert not state.is_complete()

        state.output_path = "/test/path"
        # The state starts with empty errors list, so this should be complete now
        assert state.is_complete()

        # Complete when all conditions met
        state.errors = []
        assert state.is_complete()

        # Incomplete again with errors
        state.add_error("New error")
        assert not state.is_complete()

    def test_get_execution_summary(self):
        """Test execution summary generation"""
        state = WorkflowState(
            workflow_id="test_summary",
            current_agent="planning"
        )
        state.add_error("Test error")
        state.metadata["test_key"] = "test_value"

        summary = state.get_execution_summary()

        assert summary["workflow_id"] == "test_summary"
        assert summary["current_agent"] == "planning"
        assert summary["errors_count"] == 1
        assert summary["retry_count"] == 0
        assert "test_key" in summary["metadata"]
        assert isinstance(summary["timestamp"], str)
        assert summary["is_complete"] is False

    def test_json_serialization(self):
        """Test JSON serialization with datetime encoding"""
        state = WorkflowState(
            workflow_id="test_json",
            current_agent="planning"
        )
        state.plan = {"test": "data"}
        state.metadata = {"key": "value"}

        # Test model_dump
        state_dict = state.model_dump()
        assert isinstance(state_dict, dict)
        assert state_dict["workflow_id"] == "test_json"

        # Test JSON serialization mode
        state_dict_json = state.model_dump(mode='json')
        assert isinstance(state_dict_json["timestamp"], str)  # Datetime should be serialized in JSON mode

        # Test JSON roundtrip using JSON-serialized version
        json_str = json.dumps(state_dict_json)
        loaded_dict = json.loads(json_str)
        assert loaded_dict["workflow_id"] == "test_json"

    def test_state_field_types(self):
        """Test field type validation"""
        state = WorkflowState(workflow_id="test", current_agent="planning")

        # Test optional fields can be None
        assert state.plan is None
        assert state.research_data is None
        assert state.generated_content is None
        assert state.validation_status is None
        assert state.output_path is None

        # Test default values
        assert isinstance(state.errors, list)
        assert len(state.errors) == 0
        assert isinstance(state.metadata, dict)
        assert len(state.metadata) == 0
        assert state.retry_count == 0
        assert state.word_count == 0
        assert state.plan_approved is False

    def test_state_field_assignment(self):
        """Test field assignment and type handling"""
        state = WorkflowState(workflow_id="test", current_agent="planning")

        # Test dict assignments
        test_plan = {"plan_id": "test", "title": "Test Plan"}
        state.plan = test_plan
        assert state.plan == test_plan

        test_research = {"data": "test_data"}
        state.research_data = test_research
        assert state.research_data == test_research

        test_content = {"content": "Generated text", "word_count": 100}
        state.generated_content = test_content
        assert state.generated_content == test_content

        # Test string assignments
        state.validation_status = "approved"
        assert state.validation_status == "approved"

        state.output_path = "/test/output/file.txt"
        assert state.output_path == "/test/output/file.txt"

        # Test boolean assignment
        state.plan_approved = True
        assert state.plan_approved is True

        # Test integer assignments
        state.retry_count = 3
        assert state.retry_count == 3

        state.word_count = 500
        assert state.word_count == 500

    def test_config_class(self):
        """Test Pydantic Config settings"""
        state = WorkflowState(workflow_id="test", current_agent="planning")

        # Test datetime encoding in model_dump - in Pydantic v2, datetime is not auto-serialized
        state_dict = state.model_dump()
        timestamp_obj = state_dict["timestamp"]

        # In Pydantic v2, datetime remains as datetime object unless explicitly serialized
        assert isinstance(timestamp_obj, datetime)

        # Test explicit serialization
        state_dict_serialized = state.model_dump(mode='json')
        timestamp_str = state_dict_serialized["timestamp"]
        assert isinstance(timestamp_str, str)
        assert "T" in timestamp_str  # ISO format has T separator

        # Should be able to parse back to datetime
        parsed_dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        assert isinstance(parsed_dt, datetime)

    @pytest.fixture(autouse=True)
    def save_test_results(self, request):
        """Save test results to D:/BT/madf/unit/"""
        yield  # Run the test

        # Save test result
        test_name = request.node.name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        result_file = TEST_OUTPUT_DIR / f"workflow_state_{test_name}_{timestamp}.json"

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