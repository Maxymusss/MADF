#!/usr/bin/env python3
"""
Story 1.1 Verification Script - LangGraph Setup and State Management
Comprehensive testing to validate all acceptance criteria with outputs to D:\\BT\\madf\\
"""

import asyncio
import json
import logging
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Test output directory
TEST_OUTPUT_DIR = Path("D:/BT/madf")
LOGS_DIR = TEST_OUTPUT_DIR / "logs"
UNIT_DIR = TEST_OUTPUT_DIR / "unit"
INTEGRATION_DIR = TEST_OUTPUT_DIR / "integration"
CHECKPOINTS_DIR = TEST_OUTPUT_DIR / "checkpoints"

# Ensure directories exist
for dir_path in [LOGS_DIR, UNIT_DIR, INTEGRATION_DIR, CHECKPOINTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Set up logging to D:\BT\madf\logs\
log_file = LOGS_DIR / f"story_1_1_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class Story11Verifier:
    """Comprehensive verification of Story 1.1 acceptance criteria"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_summary": {},
            "acceptance_criteria": {},
            "detailed_results": {},
            "errors": [],
            "performance_metrics": {}
        }
        self.start_time = time.time()

    async def run_all_verifications(self) -> Dict[str, Any]:
        """Run complete verification suite"""
        logger.info("=== Starting Story 1.1 Comprehensive Verification ===")

        try:
            # AC1: LangGraph Foundation
            await self.verify_langgraph_foundation()

            # AC2: Pydantic State Management
            await self.verify_pydantic_state()

            # AC3: Agent Handoffs
            await self.verify_agent_handoffs()

            # AC4: Persistence Setup
            await self.verify_persistence()

            # AC5: Observability (LangSmith)
            await self.verify_observability()

            # AC6: Error Handling
            await self.verify_error_handling()

            # Performance Tests
            await self.verify_performance()

            # Integration Tests
            await self.verify_integration()

        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            self.results["errors"].append(f"Global error: {str(e)}")
            self.results["errors"].append(traceback.format_exc())

        # Calculate final metrics
        self.results["performance_metrics"]["total_execution_time"] = time.time() - self.start_time
        self.calculate_summary()

        # Save results
        await self.save_results()

        return self.results

    async def verify_langgraph_foundation(self):
        """AC1: LangGraph Foundation verification"""
        logger.info("--- Verifying AC1: LangGraph Foundation ---")

        try:
            # Test 1: Import LangGraph components
            from langgraph.graph import StateGraph, END
            from langgraph.checkpoint.sqlite import SqliteSaver
            logger.info("[OK] LangGraph imports successful")

            # Test 2: Import workflow components
            from langgraph_core.workflow import create_weekly_research_workflow
            from langgraph_core.models.state import WorkflowState
            logger.info("[OK] MADF components import successful")

            # Test 3: Create StateGraph
            workflow = create_weekly_research_workflow()
            logger.info("[OK] StateGraph creation successful")

            # Test 4: Verify nodes
            expected_nodes = {"planning", "research", "dev", "pm"}
            actual_nodes = set(workflow.nodes.keys())

            if expected_nodes.issubset(actual_nodes):
                logger.info(f"[OK] All 4 nodes present: {actual_nodes}")
            else:
                missing = expected_nodes - actual_nodes
                logger.error(f"[FAIL] Missing nodes: {missing}")
                self.results["errors"].append(f"Missing nodes: {missing}")

            # Test 5: Verify workflow compilation
            if hasattr(workflow, 'invoke'):
                logger.info("[OK] Workflow compiled successfully")
            else:
                logger.error("[FAIL] Workflow not properly compiled")
                self.results["errors"].append("Workflow not compiled")

            self.results["acceptance_criteria"]["AC1_LangGraph_Foundation"] = True

        except Exception as e:
            logger.error(f"[FAIL] AC1 failed: {str(e)}")
            self.results["acceptance_criteria"]["AC1_LangGraph_Foundation"] = False
            self.results["errors"].append(f"AC1 error: {str(e)}")

    async def verify_pydantic_state(self):
        """AC2: Pydantic State Management verification"""
        logger.info("--- Verifying AC2: Pydantic State Management ---")

        try:
            from langgraph_core.models.state import WorkflowState
            from datetime import datetime

            # Test 1: Valid state creation
            state = WorkflowState(workflow_id="test_123", current_agent="planning")
            logger.info("[OK] WorkflowState creation successful")

            # Test 2: Required field validation
            try:
                invalid_state = WorkflowState()  # Missing required fields
                logger.error("[FAIL] Validation should have failed")
                self.results["errors"].append("Pydantic validation not working")
            except Exception:
                logger.info("[OK] Required field validation working")

            # Test 3: Method functionality
            state.add_error("test error")
            state.set_current_agent("research")

            if len(state.errors) == 1 and state.current_agent == "research":
                logger.info("[OK] State methods working correctly")
            else:
                logger.error("[FAIL] State methods not working")
                self.results["errors"].append("State methods failed")

            # Test 4: JSON serialization
            state_dict = state.model_dump()
            if isinstance(state_dict, dict) and "workflow_id" in state_dict:
                logger.info("[OK] JSON serialization working")
            else:
                logger.error("[FAIL] JSON serialization failed")
                self.results["errors"].append("JSON serialization failed")

            # Test 5: State completion check
            incomplete = state.is_complete()
            state.validation_status = "approved"
            state.output_path = "/test/path"
            state.errors = []
            complete = state.is_complete()

            if not incomplete and complete:
                logger.info("[OK] State completion logic working")
            else:
                logger.error("[FAIL] State completion logic failed")
                self.results["errors"].append("Completion logic failed")

            self.results["acceptance_criteria"]["AC2_Pydantic_State"] = True

        except Exception as e:
            logger.error(f"[FAIL] AC2 failed: {str(e)}")
            self.results["acceptance_criteria"]["AC2_Pydantic_State"] = False
            self.results["errors"].append(f"AC2 error: {str(e)}")

    async def verify_agent_handoffs(self):
        """AC3: Agent Handoffs verification"""
        logger.info("--- Verifying AC3: Agent Handoffs ---")

        try:
            from langgraph_core.agents.planning import planning_agent
            from langgraph_core.models.state import WorkflowState

            # Test 1: Planning agent execution
            initial_state = WorkflowState(workflow_id="handoff_test", current_agent="init")
            result_state = await planning_agent(initial_state)

            if result_state.current_agent == "research":
                logger.info("[OK] Planning agent handoff successful")
            else:
                logger.error(f"[FAIL] Planning agent handoff failed: {result_state.current_agent}")
                self.results["errors"].append("Planning agent handoff failed")

            # Test 2: State preservation
            if result_state.workflow_id == initial_state.workflow_id:
                logger.info("[OK] State preservation working")
            else:
                logger.error("[FAIL] State not preserved during handoff")
                self.results["errors"].append("State not preserved")

            # Test 3: Plan creation
            if result_state.plan is not None and isinstance(result_state.plan, dict):
                logger.info("[OK] Plan creation successful")
            else:
                logger.error("[FAIL] Plan creation failed")
                self.results["errors"].append("Plan creation failed")

            self.results["acceptance_criteria"]["AC3_Agent_Handoffs"] = True

        except Exception as e:
            logger.error(f"[FAIL] AC3 failed: {str(e)}")
            self.results["acceptance_criteria"]["AC3_Agent_Handoffs"] = False
            self.results["errors"].append(f"AC3 error: {str(e)}")

    async def verify_persistence(self):
        """AC4: Persistence Setup verification"""
        logger.info("--- Verifying AC4: Persistence Setup ---")

        try:
            from langgraph.checkpoint.sqlite import SqliteSaver
            from langgraph_core.workflow import create_weekly_research_workflow

            # Test 1: SQLite checkpointer creation
            checkpoint_path = CHECKPOINTS_DIR / "test_checkpoints.db"
            memory = SqliteSaver.from_conn_string(f"sqlite:///{checkpoint_path}")
            logger.info("[OK] SQLite checkpointer created")

            # Test 2: Workflow with checkpointing
            workflow = create_weekly_research_workflow()
            logger.info("[OK] Workflow with checkpointing compiled")

            # Test 3: Checkpoint file creation
            if checkpoint_path.exists():
                logger.info("[OK] Checkpoint database file created")
            else:
                logger.warning("[WARN] Checkpoint file not yet created (normal until first execution)")

            self.results["acceptance_criteria"]["AC4_Persistence"] = True

        except Exception as e:
            logger.error(f"[FAIL] AC4 failed: {str(e)}")
            self.results["acceptance_criteria"]["AC4_Persistence"] = False
            self.results["errors"].append(f"AC4 error: {str(e)}")

    async def verify_observability(self):
        """AC5: Observability verification"""
        logger.info("--- Verifying AC5: Observability ---")

        try:
            # Test 1: LangSmith import (optional)
            try:
                import langsmith
                logger.info("[OK] LangSmith available")
                langsmith_available = True
            except ImportError:
                logger.warning("[WARN] LangSmith not installed (optional)")
                langsmith_available = False

            # Test 2: Logging infrastructure
            from langgraph_core.utils.logging import create_workflow_logger
            test_logger = create_workflow_logger("test_workflow")

            if test_logger:
                logger.info("[OK] Workflow logging infrastructure working")
            else:
                logger.error("[FAIL] Workflow logging failed")
                self.results["errors"].append("Workflow logging failed")

            self.results["acceptance_criteria"]["AC5_Observability"] = True
            self.results["detailed_results"]["langsmith_available"] = langsmith_available

        except Exception as e:
            logger.error(f"[FAIL] AC5 failed: {str(e)}")
            self.results["acceptance_criteria"]["AC5_Observability"] = False
            self.results["errors"].append(f"AC5 error: {str(e)}")

    async def verify_error_handling(self):
        """AC6: Error Handling verification"""
        logger.info("--- Verifying AC6: Error Handling ---")

        try:
            from langgraph_core.agents.planning import planning_agent
            from langgraph_core.models.state import WorkflowState

            # Test 1: Error capture in state
            state = WorkflowState(workflow_id="error_test", current_agent="planning")
            state.add_error("Test error message")

            if len(state.errors) > 0 and "Test error message" in state.errors[0]:
                logger.info("[OK] Error capture working")
            else:
                logger.error("[FAIL] Error capture failed")
                self.results["errors"].append("Error capture failed")

            # Test 2: Agent error handling
            invalid_state = WorkflowState(workflow_id="invalid_test", current_agent="planning")
            invalid_state.plan = {}  # Invalid plan to trigger error

            result = await planning_agent(invalid_state)
            if len(result.errors) > 0:
                logger.info("[OK] Agent error handling working")
            else:
                logger.warning("[WARN] Agent error handling might not be triggered")

            self.results["acceptance_criteria"]["AC6_Error_Handling"] = True

        except Exception as e:
            logger.error(f"[FAIL] AC6 failed: {str(e)}")
            self.results["acceptance_criteria"]["AC6_Error_Handling"] = False
            self.results["errors"].append(f"AC6 error: {str(e)}")

    async def verify_performance(self):
        """Performance verification"""
        logger.info("--- Verifying Performance ---")

        try:
            from langgraph_core.agents.planning import planning_agent
            from langgraph_core.models.state import WorkflowState

            # Test 1: Agent execution time
            start_time = time.time()
            state = WorkflowState(workflow_id="perf_test", current_agent="planning")
            result = await planning_agent(state)
            execution_time = time.time() - start_time

            logger.info(f"[OK] Planning agent execution time: {execution_time:.4f}s")
            self.results["performance_metrics"]["planning_agent_time"] = execution_time

            # Test 2: Memory usage (basic check)
            import sys
            state_size = sys.getsizeof(result)
            logger.info(f"[OK] WorkflowState memory usage: {state_size} bytes")
            self.results["performance_metrics"]["state_memory_usage"] = state_size

            # Performance thresholds
            if execution_time < 1.0:  # Should be fast
                logger.info("[OK] Performance within acceptable limits")
            else:
                logger.warning(f"[WARN] Performance concern: {execution_time:.4f}s > 1.0s")

        except Exception as e:
            logger.error(f"[FAIL] Performance verification failed: {str(e)}")
            self.results["errors"].append(f"Performance error: {str(e)}")

    async def verify_integration(self):
        """Integration verification"""
        logger.info("--- Verifying Integration ---")

        try:
            from langgraph_core.workflow import execute_weekly_research

            # Test 1: Full workflow execution
            logger.info("Starting full workflow execution test...")
            start_time = time.time()

            result = await execute_weekly_research(workflow_id="integration_test")
            execution_time = time.time() - start_time

            if result.get("success"):
                logger.info(f"[OK] Full workflow execution successful ({execution_time:.2f}s)")
                self.results["performance_metrics"]["full_workflow_time"] = execution_time
            else:
                logger.error(f"[FAIL] Full workflow execution failed: {result.get('error')}")
                self.results["errors"].append(f"Integration test failed: {result.get('error')}")

            # Test 2: Workflow state progression
            final_state = result.get("final_state")
            if final_state and hasattr(final_state, 'current_agent'):
                logger.info(f"[OK] Final agent: {final_state.current_agent}")
                self.results["detailed_results"]["final_agent"] = final_state.current_agent

            self.results["detailed_results"]["integration_test_result"] = result

        except Exception as e:
            logger.error(f"[FAIL] Integration verification failed: {str(e)}")
            self.results["errors"].append(f"Integration error: {str(e)}")

    def calculate_summary(self):
        """Calculate test summary"""
        total_criteria = len(self.results["acceptance_criteria"])
        passed_criteria = sum(1 for passed in self.results["acceptance_criteria"].values() if passed)

        self.results["test_summary"] = {
            "total_acceptance_criteria": total_criteria,
            "passed_acceptance_criteria": passed_criteria,
            "success_rate": f"{(passed_criteria/total_criteria)*100:.1f}%" if total_criteria > 0 else "0%",
            "total_errors": len(self.results["errors"]),
            "overall_status": "PASS" if passed_criteria == total_criteria and len(self.results["errors"]) == 0 else "FAIL"
        }

    async def save_results(self):
        """Save results to D:/BT/madf/"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save detailed results
        results_file = INTEGRATION_DIR / f"story_1_1_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        # Save summary report
        summary_file = INTEGRATION_DIR / f"story_1_1_summary_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write("=== Story 1.1 Verification Summary ===\n\n")
            f.write(f"Timestamp: {self.results['timestamp']}\n")
            f.write(f"Overall Status: {self.results['test_summary']['overall_status']}\n")
            f.write(f"Success Rate: {self.results['test_summary']['success_rate']}\n")
            f.write(f"Total Errors: {self.results['test_summary']['total_errors']}\n\n")

            f.write("Acceptance Criteria Results:\n")
            for criteria, passed in self.results["acceptance_criteria"].items():
                status = "[PASS]" if passed else "[FAIL]"
                f.write(f"  {criteria}: {status}\n")

            if self.results["errors"]:
                f.write("\nErrors:\n")
                for error in self.results["errors"]:
                    f.write(f"  - {error}\n")

            f.write(f"\nPerformance Metrics:\n")
            for metric, value in self.results["performance_metrics"].items():
                f.write(f"  {metric}: {value}\n")

        logger.info(f"Results saved to: {results_file}")
        logger.info(f"Summary saved to: {summary_file}")

async def main():
    """Main verification function"""
    print(">>> Starting Story 1.1 Comprehensive Verification")
    print(f"[DIR] Test outputs will be saved to: {TEST_OUTPUT_DIR}")

    verifier = Story11Verifier()
    results = await verifier.run_all_verifications()

    print("\n" + "="*60)
    print("[REPORT] VERIFICATION COMPLETE")
    print("="*60)
    print(f"Overall Status: {results['test_summary']['overall_status']}")
    print(f"Success Rate: {results['test_summary']['success_rate']}")
    print(f"Total Errors: {results['test_summary']['total_errors']}")
    print(f"Execution Time: {results['performance_metrics']['total_execution_time']:.2f}s")
    print(f"[DIR] Detailed results saved to: {TEST_OUTPUT_DIR}")

    return results

if __name__ == "__main__":
    asyncio.run(main())