#!/usr/bin/env python3
"""Master test runner for Story 1.8 tool efficiency research

Executes all agent-specific test files and generates summary reports.
Results are exported to tests/research/results/ directory.
"""

import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List


def run_all_tests():
    """Run all agent-specific tests and generate summary report"""
    test_files = [
        "tests/research/test_orchestrator_tools.py",
        "tests/research/test_analyst_tools.py",
        "tests/research/test_knowledge_tools.py",
        "tests/research/test_developer_tools.py",
        "tests/research/test_validator_tools.py"
    ]

    # Ensure results directory exists
    results_dir = Path("tests/research/results")
    results_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary = {
        "timestamp": timestamp,
        "test_files": [],
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "errors": 0
    }

    print("="*80)
    print("Story 1.8 Tool Efficiency Research - Test Runner")
    print("="*80)
    print(f"Timestamp: {timestamp}")
    print(f"Results Directory: {results_dir}")
    print("="*80)

    for test_file in test_files:
        print(f"\n{'='*80}")
        print(f"Running: {test_file}")
        print('='*80)

        # Run pytest with verbose output
        result = subprocess.run(
            ["uv", "run", "python", "-m", "pytest", test_file, "-v", "--tb=short", "-ra"],
            capture_output=True,
            text=True
        )

        # Display output
        print(result.stdout)
        if result.stderr:
            print(f"STDERR: {result.stderr}")

        # Parse pytest output (simplified - counts from pytest summary)
        test_result = {
            "file": test_file,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "status": "passed" if result.returncode == 0 else "failed"
        }
        summary["test_files"].append(test_result)

        # Update counters (simplified - real implementation would parse pytest output)
        if result.returncode == 0:
            summary["passed"] += 1
        else:
            summary["failed"] += 1

    # Generate summary report
    summary_path = results_dir / f"summary_{timestamp}.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    # Print final summary
    print(f"\n{'='*80}")
    print("Test Execution Summary")
    print('='*80)
    print(f"Total Test Files: {len(test_files)}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Skipped: {summary['skipped']}")
    print(f"Errors: {summary['errors']}")
    print(f"\nResults saved to: {summary_path}")
    print('='*80)

    # Exit with appropriate code
    sys.exit(0 if summary['failed'] == 0 else 1)


def run_specific_agent(agent_name: str):
    """Run tests for a specific agent

    Args:
        agent_name: Agent name (orchestrator, analyst, knowledge, developer, validator)
    """
    test_file = f"tests/research/test_{agent_name}_tools.py"

    if not Path(test_file).exists():
        print(f"Error: Test file not found: {test_file}")
        sys.exit(1)

    print(f"Running tests for {agent_name} agent...")
    result = subprocess.run(
        ["uv", "run", "python", "-m", "pytest", test_file, "-v", "--tb=short"],
        capture_output=False,
        text=True
    )
    sys.exit(result.returncode)


def list_available_tests():
    """List all available test files"""
    test_files = [
        "test_orchestrator_tools.py",
        "test_analyst_tools.py",
        "test_knowledge_tools.py",
        "test_developer_tools.py",
        "test_validator_tools.py"
    ]

    print("Available test files:")
    for idx, test_file in enumerate(test_files, start=1):
        agent = test_file.replace("test_", "").replace("_tools.py", "")
        print(f"  {idx}. {agent} - {test_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Run Story 1.8 tool efficiency research tests"
    )
    parser.add_argument(
        "--agent",
        type=str,
        choices=["orchestrator", "analyst", "knowledge", "developer", "validator"],
        help="Run tests for specific agent only"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available test files"
    )

    args = parser.parse_args()

    if args.list:
        list_available_tests()
    elif args.agent:
        run_specific_agent(args.agent)
    else:
        run_all_tests()
