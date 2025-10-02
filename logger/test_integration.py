"""
Test MADF logging integration
"""

import asyncio
import time
from logger import log_event, log_error, madf_logger
from logger.madf_integration import log_agent_execution, log_tool_usage


# Example: Decorated agent function
@log_agent_execution("planning_agent")
async def planning_agent_task(state):
    """Example planning agent with automatic logging"""
    madf_logger.logger.log("planning_start", "execution",
                          task="create_development_plan",
                          state_size=len(str(state)))

    # Simulate some work
    await asyncio.sleep(0.1)

    # Simulate a decision point
    madf_logger.logger.log("decision_made", "decision",
                          decision="use_parallel_execution",
                          confidence=0.85,
                          alternatives=["sequential", "hybrid"])

    return {"plan": "created", "agents": ["research", "dev", "pm"]}


# Example: Decorated tool function
@log_tool_usage("Read")
def read_file_simulation(file_path):
    """Example tool usage with automatic logging"""
    time.sleep(0.05)  # Simulate file read
    return f"Content of {file_path}"


async def test_workflow():
    """Test a complete workflow with logging"""

    # Start workflow
    workflow_id = "test_workflow_123"
    initial_state = {"task": "implement_feature", "files": ["a.py", "b.py"]}

    madf_logger.log_workflow_start(workflow_id, initial_state)
    madf_logger.set_workflow_context(workflow_id, "planning_agent")

    try:
        # Planning phase
        planning_result = await planning_agent_task(initial_state)

        # Agent transition
        madf_logger.log_agent_transition("planning_agent", "research_agent",
                                        len(str(planning_result)),
                                        "plan_complete_need_research")

        # Tool usage
        madf_logger.set_workflow_context(workflow_id, "research_agent")
        file_content = read_file_simulation("requirements.txt")

        # Simulate an error
        try:
            raise ValueError("Example error for testing")
        except ValueError as e:
            log_error(e, {"phase": "research", "file": "requirements.txt"})

        # Performance issue
        expected_time = 50
        actual_time = 200
        madf_logger.logger.log_performance_issue("api_call", expected_time, actual_time, "slow_network")

        # Human interaction
        madf_logger.log_human_clarification_needed("research_agent",
                                                  "api_documentation_unclear",
                                                  {"api": "bloomberg", "endpoint": "/market_data"})

        print("Test workflow completed successfully!")

    except Exception as e:
        log_error(e, {"workflow_id": workflow_id})

    finally:
        # Close session
        madf_logger.logger.close()


if __name__ == "__main__":
    # Run test
    print("Testing MADF logging integration...")
    asyncio.run(test_workflow())

    # Show log file location
    from logger import get_logger
    logger = get_logger()
    print(f"Logs written to: {logger.get_log_file_path()}")