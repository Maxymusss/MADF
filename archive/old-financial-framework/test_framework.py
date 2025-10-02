"""
Quick test script to verify the multi-agent framework setup
Tests basic functionality without requiring full MCP-use integration
"""

import asyncio
import json
import os
from pathlib import Path
from datetime import datetime, timedelta

from agents.product_manager_agent import ProductManagerAgent
from agents.research_agent import ResearchAgent
from agents.validator_agent import ValidatorAgent


def test_product_manager_agent():
    """Test Product Manager Agent basic functionality"""
    print("Testing Product Manager Agent...")

    pm = ProductManagerAgent("test_workspace")

    # Test timeframe calculation
    start, end = pm.get_week_timeframe()
    assert start <= end
    assert (end - start).days >= 7
    print(f"+ Timeframe calculation: {start.date()} to {end.date()}")

    # Test task creation
    task_spec = pm.create_research_task("test_task", ["G10"], ["currencies"])
    assert task_spec["task_id"] == "test_task"
    assert "G10" in task_spec["scope"]["regions"]
    print("✓ Task creation successful")

    # Test agent deployment
    agent_ids = pm.deploy_research_agents("test_task", num_agents=2)
    assert len(agent_ids) == 2
    print(f"✓ Research agents deployed: {agent_ids}")

    # Test validator deployment
    validator_id = pm.deploy_validator_agent("test_task", agent_ids)
    assert validator_id.startswith("validator_")
    print(f"✓ Validator agent deployed: {validator_id}")

    print("Product Manager Agent: PASSED\n")
    return True


def create_mock_research_results():
    """Create mock research results for testing"""
    mock_result = {
        "agent_id": "research_agent_1_test_task",
        "task_id": "test_task",
        "status": "completed",
        "completed_at": datetime.now().isoformat(),
        "strategy_used": "comprehensive_search",
        "findings": {
            "currency_movements": [
                {
                    "type": "currency_movement",
                    "currency_pairs": ["EUR/USD"],
                    "movement_description": "rises 0.3%",
                    "source": "https://reuters.com/example",
                    "title": "EUR/USD gains on ECB dovish signals"
                }
            ],
            "interest_rate_changes": [
                {
                    "type": "interest_rate",
                    "rate_info": ["0.25%"],
                    "action_info": ["raises", "25 basis points"],
                    "source": "https://bloomberg.com/example",
                    "title": "Fed raises rates by 25bp as expected"
                }
            ],
            "central_bank_actions": [
                {
                    "type": "central_bank_action",
                    "bank": "Federal Reserve",
                    "actions": ["announces", "signals"],
                    "source": "https://federalreserve.gov/example",
                    "title": "Fed signals gradual rate normalization"
                }
            ],
            "sources": [
                {"domain": "reuters.com", "url": "https://reuters.com/example"},
                {"domain": "bloomberg.com", "url": "https://bloomberg.com/example"}
            ]
        },
        "quality_metrics": {
            "total_sources": 2,
            "events_found": 3,
            "avg_source_reliability": 0.9,
            "queries_executed": 5
        }
    }

    # Save mock result
    os.makedirs("test_workspace/results", exist_ok=True)
    with open("test_workspace/results/research_agent_1_test_task_result.json", 'w') as f:
        json.dump(mock_result, f, indent=2)

    return mock_result


def test_research_agent():
    """Test Research Agent basic functionality"""
    print("Testing Research Agent...")

    agent = ResearchAgent("research_agent_test", "test_workspace")

    # Test timeframe parsing
    start_str = "2024-01-01T00:00:00"
    end_str = "2024-01-07T23:59:59"
    start, end = agent.parse_timeframe(start_str, end_str)
    assert start.year == 2024
    assert start.month == 1
    print("✓ Timeframe parsing successful")

    # Test search query building
    queries = agent.build_search_queries(
        ["G10"], ["currencies"], start, end
    )
    assert len(queries) > 0
    assert any("EUR/USD" in q for q in queries)
    print(f"✓ Search queries built: {len(queries)} queries")

    # Test claim extraction with mock data
    mock_results = [
        {
            "title": "EUR/USD rises 0.5% on ECB comments",
            "content": "The euro strengthened against the dollar today...",
            "url": "https://reuters.com/test",
            "published_date": "2024-01-03"
        }
    ]

    events = agent.extract_financial_events(mock_results, start, end)
    assert "currency_movements" in events
    assert "sources" in events
    print("✓ Event extraction successful")

    print("Research Agent: PASSED\n")
    return True


async def test_validator_agent():
    """Test Validator Agent basic functionality"""
    print("Testing Validator Agent...")

    validator = ValidatorAgent("validator_test", "test_workspace")

    # Create mock research results
    mock_research = create_mock_research_results()

    # Test claim extraction
    claims = validator.extract_claims_from_research(mock_research)
    assert len(claims) > 0
    assert any(claim["type"] == "currency_movement" for claim in claims)
    print(f"✓ Claim extraction: {len(claims)} claims found")

    # Test conflict detection with multiple agents
    research_results = {
        "agent1": mock_research,
        "agent2": {
            "status": "completed",
            "findings": {
                "currency_movements": [
                    {
                        "type": "currency_movement",
                        "currency_pairs": ["EUR/USD"],
                        "movement_description": "falls 0.2%",  # Conflicting direction
                        "source": "https://wsj.com/example",
                        "title": "EUR/USD drops on inflation concerns"
                    }
                ]
            }
        }
    }

    conflicts = validator.detect_claim_conflicts(research_results)
    print(f"✓ Conflict detection: {len(conflicts)} conflicts found")

    # Test similarity calculation
    similarity = validator.calculate_claim_similarity(
        "EUR/USD rises 0.3%",
        "EUR/USD gains 0.3%"
    )
    assert similarity > 0.5
    print(f"✓ Similarity calculation: {similarity:.2f}")

    print("Validator Agent: PASSED\n")
    return True


def test_error_logging():
    """Test error logging functionality"""
    print("Testing Error Logging...")

    pm = ProductManagerAgent("test_workspace")
    pm.log_error("test_error", "This is a test error", {"test": True})

    error_file = Path("test_workspace/logs/product_manager_errors.json")
    assert error_file.exists()

    with open(error_file, 'r') as f:
        errors = json.load(f)
        assert len(errors) > 0
        assert errors[-1]["error_type"] == "test_error"

    print("✓ Error logging successful")
    print("Error Logging: PASSED\n")
    return True


def test_shared_file_communication():
    """Test shared file system communication"""
    print("Testing Shared File Communication...")

    # Test task file creation and reading
    pm = ProductManagerAgent("test_workspace")
    task_spec = pm.create_research_task("comm_test", ["Asia"], ["currencies"])

    task_file = Path("test_workspace/tasks/comm_test.json")
    assert task_file.exists()

    # Verify another agent can read the task
    with open(task_file, 'r') as f:
        loaded_task = json.load(f)
        assert loaded_task["task_id"] == "comm_test"

    print("✓ Task file communication successful")

    # Test result file creation
    test_result = {
        "agent_id": "test_agent",
        "status": "completed",
        "data": "test_data"
    }

    result_file = Path("test_workspace/results/test_agent_result.json")
    with open(result_file, 'w') as f:
        json.dump(test_result, f)

    # Verify PM can read results
    status = pm.check_agent_status("test_agent")
    assert status["status"] == "completed"
    print("✓ Result file communication successful")

    print("Shared File Communication: PASSED\n")
    return True


def cleanup_test_files():
    """Clean up test workspace"""
    import shutil
    if Path("test_workspace").exists():
        shutil.rmtree("test_workspace")
    print("✓ Test files cleaned up")


async def run_all_tests():
    """Run all framework tests"""
    print("=" * 60)
    print("MULTI-AGENT FRAMEWORK TEST SUITE")
    print("=" * 60)
    print()

    tests_passed = 0
    total_tests = 6

    try:
        # Test individual components
        if test_product_manager_agent():
            tests_passed += 1

        if test_research_agent():
            tests_passed += 1

        if await test_validator_agent():
            tests_passed += 1

        if test_error_logging():
            tests_passed += 1

        if test_shared_file_communication():
            tests_passed += 1

        # Test overall framework status
        from run_multi_agent_framework import MultiAgentFramework
        framework = MultiAgentFramework("test_workspace")
        status = framework.get_framework_status()
        assert status["framework_ready"] == True
        print("Testing Framework Status...")
        print("✓ Framework initialization successful")
        print("Framework Status: PASSED\n")
        tests_passed += 1

    except Exception as e:
        print(f"❌ Test failed with error: {e}")

    finally:
        # Cleanup
        cleanup_test_files()

    # Results
    print("=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Success Rate: {tests_passed/total_tests*100:.1f}%")

    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Framework is ready for deployment.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

    print("\nFramework Components:")
    print("✓ Product Manager Agent - Orchestration and task management")
    print("✓ Research Agent - MCP-use integration for data collection")
    print("✓ Validator Agent - Cross-reference and fact-checking")
    print("✓ Shared File System - Agent communication")
    print("✓ Error Tracking - Learning and improvement")
    print("✓ Framework Status - Health monitoring")


if __name__ == "__main__":
    asyncio.run(run_all_tests())