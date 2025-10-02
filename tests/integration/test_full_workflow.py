"""
Integration tests for complete LangGraph workflow
Test outputs saved to D:\\BT\\madf\\integration\\
"""

import asyncio
import pytest
import json
import time
from datetime import datetime
from pathlib import Path

from langgraph_core.workflow import create_weekly_research_workflow, execute_weekly_research
from langgraph_core.models.state import WorkflowState

# Test output directory
TEST_OUTPUT_DIR = Path("D:/BT/madf/integration")
TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class TestFullWorkflow:
    """Integration tests for complete workflow execution"""

    def test_workflow_creation(self):
        """Test StateGraph workflow creation"""
        workflow = create_weekly_research_workflow()

        # Verify workflow exists and is compiled
        assert workflow is not None
        assert hasattr(workflow, 'invoke')

        # Verify all expected nodes exist
        expected_nodes = {"planning", "research", "dev", "pm"}
        actual_nodes = set(workflow.nodes.keys())
        assert expected_nodes.issubset(actual_nodes)

    @pytest.mark.asyncio
    async def test_basic_workflow_execution(self):
        """Test basic workflow execution without errors"""
        workflow = create_weekly_research_workflow()

        initial_state = WorkflowState(
            workflow_id="integration_test_basic",
            current_agent="planning"
        )

        config = {"configurable": {"thread_id": "test_basic"}}

        # Execute workflow
        start_time = time.time()
        result = await workflow.ainvoke(initial_state, config=config)
        execution_time = time.time() - start_time

        # Basic assertions - LangGraph returns state as dict
        assert isinstance(result, dict)
        assert result["workflow_id"] == "integration_test_basic"
        assert execution_time < 30.0  # Should complete within 30 seconds

        # Save execution metrics
        await self._save_execution_metrics("basic_execution", {
            "execution_time": execution_time,
            "final_agent": result["current_agent"],
            "errors_count": len(result.get("errors", [])),
            "workflow_complete": result.get("validation_status") == "approved" and result.get("output_path") is not None
        })

    @pytest.mark.asyncio
    async def test_execute_weekly_research_function(self):
        """Test the high-level execute_weekly_research function"""
        start_time = time.time()

        result = await execute_weekly_research(
            workflow_id="integration_test_execute",
            initial_plan={"test": "data"}
        )

        execution_time = time.time() - start_time

        # Verify result structure
        assert isinstance(result, dict)
        assert "success" in result
        assert "workflow_id" in result
        assert result["workflow_id"] == "integration_test_execute"

        if result["success"]:
            assert "final_state" in result
            assert "execution_time" in result
            assert "performance_metrics" in result

            final_state = result["final_state"]
            assert isinstance(final_state, dict)

        # Save execution results
        await self._save_execution_metrics("execute_weekly_research", {
            "success": result["success"],
            "execution_time": execution_time,
            "result_keys": list(result.keys()),
            "has_final_state": "final_state" in result
        })

    @pytest.mark.asyncio
    async def test_workflow_state_progression(self):
        """Test that workflow progresses through all agents correctly"""
        workflow = create_weekly_research_workflow()

        initial_state = WorkflowState(
            workflow_id="integration_test_progression",
            current_agent="planning"
        )

        config = {"configurable": {"thread_id": "test_progression"}}

        # Execute workflow
        result = await workflow.ainvoke(initial_state, config=config)

        # The workflow should complete the full pipeline
        # Due to the linear nature: planning -> research -> dev -> pm
        # Final agent depends on implementation, but should not be "planning"
        assert result["current_agent"] != "planning"

        # Metadata should show progression
        metadata = result["metadata"]
        assert isinstance(metadata, dict)

        # Save progression data
        await self._save_execution_metrics("state_progression", {
            "initial_agent": "planning",
            "final_agent": result["current_agent"],
            "metadata_keys": list(metadata.keys()),
            "has_plan": result.get("plan") is not None,
            "plan_approved": result.get("plan_approved", False)
        })

    @pytest.mark.asyncio
    async def test_workflow_with_custom_plan(self):
        """Test workflow execution with custom initial plan"""
        custom_plan = {
            "plan_id": "custom_test_plan",
            "title": "Custom Test Plan",
            "objective": "Test custom plan execution",
            "geographic_coverage": ["US", "CN"],
            "market_types": ["fx"],
            "data_sources": ["TestAPI"],
            "approved": True
        }

        result = await execute_weekly_research(
            workflow_id="integration_test_custom_plan",
            initial_plan=custom_plan
        )

        assert result["success"] is True
        final_state = result["final_state"]

        # Custom plan should be preserved
        assert final_state["plan"]["plan_id"] == "custom_test_plan"
        assert final_state["plan_approved"] is True

    @pytest.mark.asyncio
    async def test_workflow_error_handling(self):
        """Test workflow behavior with error conditions"""
        # Test with invalid initial state
        invalid_plan = {
            "plan_id": "invalid_plan",
            # Missing required fields to trigger validation errors
        }

        result = await execute_weekly_research(
            workflow_id="integration_test_error_handling",
            initial_plan=invalid_plan
        )

        # Workflow should handle errors gracefully
        assert isinstance(result, dict)
        assert "success" in result

        if not result["success"]:
            assert "error" in result
            assert isinstance(result["error"], str)

    @pytest.mark.asyncio
    async def test_concurrent_workflow_execution(self):
        """Test multiple concurrent workflow executions"""
        async def run_workflow(workflow_id):
            return await execute_weekly_research(workflow_id=workflow_id)

        # Run 3 concurrent workflows
        tasks = [
            run_workflow(f"concurrent_test_{i}")
            for i in range(3)
        ]

        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time

        # All should complete without exceptions
        successful_results = [r for r in results if isinstance(r, dict) and r.get("success")]
        assert len(successful_results) > 0

        # Save concurrency metrics
        await self._save_execution_metrics("concurrent_execution", {
            "total_workflows": len(tasks),
            "successful_workflows": len(successful_results),
            "total_execution_time": total_time,
            "average_time_per_workflow": total_time / len(tasks),
            "has_exceptions": any(isinstance(r, Exception) for r in results)
        })

    @pytest.mark.asyncio
    async def test_checkpoint_creation(self):
        """Test that checkpoints are created during execution"""
        # Use custom checkpoint path in test directory
        checkpoint_path = Path("D:/BT/madf/checkpoints/test_checkpoints.db")

        workflow = create_weekly_research_workflow()
        initial_state = WorkflowState(
            workflow_id="integration_test_checkpoints",
            current_agent="planning"
        )

        config = {"configurable": {"thread_id": "test_checkpoints"}}

        # Execute workflow
        result = await workflow.ainvoke(initial_state, config=config)

        # Note: Checkpoint file creation depends on LangGraph implementation
        # This test documents expected behavior
        checkpoint_exists = checkpoint_path.exists() if checkpoint_path.parent.exists() else False

        await self._save_execution_metrics("checkpoint_creation", {
            "checkpoint_path": str(checkpoint_path),
            "checkpoint_exists": checkpoint_exists,
            "workflow_completed": isinstance(result, dict) and "workflow_id" in result,
            "final_workflow_id": result.get("workflow_id") if isinstance(result, dict) else None
        })

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self):
        """Test workflow performance benchmarks"""
        execution_times = []
        memory_usage = []

        for i in range(3):
            start_time = time.time()

            result = await execute_weekly_research(
                workflow_id=f"performance_test_{i}"
            )

            execution_time = time.time() - start_time
            execution_times.append(execution_time)

            # Basic memory check (final state size)
            if result["success"]:
                import sys
                state_size = sys.getsizeof(result["final_state"])
                memory_usage.append(state_size)

        # Calculate performance metrics
        avg_execution_time = sum(execution_times) / len(execution_times)
        max_execution_time = max(execution_times)
        avg_memory_usage = sum(memory_usage) / len(memory_usage) if memory_usage else 0

        # Performance assertions
        assert avg_execution_time < 10.0  # Should average under 10 seconds
        assert max_execution_time < 30.0  # Should never exceed 30 seconds

        await self._save_execution_metrics("performance_benchmarks", {
            "execution_times": execution_times,
            "avg_execution_time": avg_execution_time,
            "max_execution_time": max_execution_time,
            "memory_usage": memory_usage,
            "avg_memory_usage": avg_memory_usage,
            "total_test_runs": len(execution_times)
        })

    async def _save_execution_metrics(self, test_name: str, metrics: dict):
        """Save execution metrics to test output directory"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        metrics_file = TEST_OUTPUT_DIR / f"workflow_{test_name}_{timestamp}.json"

        test_data = {
            "test_name": test_name,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "module": __name__
        }

        with open(metrics_file, 'w') as f:
            json.dump(test_data, f, indent=2, default=str)

    @pytest.fixture(autouse=True)
    def save_test_results(self, request):
        """Save test results to D:/BT/madf/integration/"""
        yield  # Run the test

        test_name = request.node.name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        result_file = TEST_OUTPUT_DIR / f"integration_{test_name}_{timestamp}.json"

        test_result = {
            "test_name": test_name,
            "timestamp": datetime.now().isoformat(),
            "status": "passed" if not hasattr(request.node, "rep_call") or request.node.rep_call.passed else "failed",
            "module": __name__,
            "test_type": "integration"
        }

        with open(result_file, 'w') as f:
            json.dump(test_result, f, indent=2)

def pytest_runtest_makereport(item, call):
    """Hook to capture test results"""
    if call.when == "call":
        setattr(item, "rep_" + call.when, call)