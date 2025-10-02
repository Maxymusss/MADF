#!/usr/bin/env python3
r"""
Story 1.1 Test Runner - Execute all tests and generate comprehensive reports
All outputs saved to D:\BT\madf\
"""

import asyncio
import subprocess
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Test output directory
TEST_OUTPUT_DIR = Path("D:/BT/madf")
LOGS_DIR = TEST_OUTPUT_DIR / "logs"

# Ensure directories exist
TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

async def main():
    """Main test execution function"""
    print("Starting Story 1.1 Comprehensive Test Suite")
    print(f"All outputs saved to: {TEST_OUTPUT_DIR}")
    print("="*60)

    start_time = time.time()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    test_results = {
        "timestamp": datetime.now().isoformat(),
        "test_suite": "Story 1.1 LangGraph Setup and State Management",
        "phases": {}
    }

    try:
        # Phase 1: Verification Script
        print("\nPhase 1: Running Verification Script")
        print("-" * 40)

        verification_result = await run_verification_script()
        test_results["phases"]["verification"] = verification_result

        # Phase 2: Unit Tests
        print("\nPhase 2: Running Unit Tests")
        print("-" * 40)

        unit_test_result = await run_unit_tests()
        test_results["phases"]["unit_tests"] = unit_test_result

        # Phase 3: Integration Tests
        print("\nPhase 3: Running Integration Tests")
        print("-" * 40)

        integration_test_result = await run_integration_tests()
        test_results["phases"]["integration_tests"] = integration_test_result

        # Phase 4: Generate Final Report
        print("\nPhase 4: Generating Final Report")
        print("-" * 40)

        await generate_final_report(test_results, timestamp)

    except Exception as e:
        print(f"Test suite failed: {str(e)}")
        test_results["error"] = str(e)

    # Calculate total time
    total_time = time.time() - start_time
    test_results["total_execution_time"] = total_time

    print(f"\nTest Suite Complete ({total_time:.2f}s)")
    print(f"Results saved to: {TEST_OUTPUT_DIR}")

    return test_results

async def run_verification_script():
    """Run the main verification script"""
    print("Running Story 1.1 verification script...")

    try:
        # Run verification script
        result = subprocess.run([
            sys.executable, "verify_story_1_1.py"
        ], capture_output=True, text=True, timeout=300)

        success = result.returncode == 0

        print(f"Verification script completed (exit code: {result.returncode})")
        if result.stdout:
            print("Output preview:")
            print(result.stdout[-500:])  # Last 500 chars

        return {
            "success": success,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "execution_method": "subprocess"
        }

    except subprocess.TimeoutExpired:
        print("Verification script timed out")
        return {"success": False, "error": "timeout"}
    except Exception as e:
        print(f"Verification script failed: {str(e)}")
        return {"success": False, "error": str(e)}

async def run_unit_tests():
    """Run unit tests with pytest"""
    print("Running unit tests with pytest...")

    try:
        # Run unit tests
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/unit/",
            "-v",
            "--tb=short",
            f"--junit-xml={TEST_OUTPUT_DIR}/unit/junit_results.xml"
        ], capture_output=True, text=True, timeout=180)

        success = result.returncode == 0

        print(f"Unit tests completed (exit code: {result.returncode})")
        if result.stdout:
            print("Output preview:")
            print(result.stdout[-500:])

        return {
            "success": success,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "junit_xml": f"{TEST_OUTPUT_DIR}/unit/junit_results.xml"
        }

    except subprocess.TimeoutExpired:
        print("Unit tests timed out")
        return {"success": False, "error": "timeout"}
    except Exception as e:
        print(f"Unit tests failed: {str(e)}")
        return {"success": False, "error": str(e)}

async def run_integration_tests():
    """Run integration tests with pytest"""
    print("Running integration tests with pytest...")

    try:
        # Run integration tests
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/integration/",
            "-v",
            "--tb=short",
            f"--junit-xml={TEST_OUTPUT_DIR}/integration/junit_results.xml"
        ], capture_output=True, text=True, timeout=300)

        success = result.returncode == 0

        print(f"Integration tests completed (exit code: {result.returncode})")
        if result.stdout:
            print("Output preview:")
            print(result.stdout[-500:])

        return {
            "success": success,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "junit_xml": f"{TEST_OUTPUT_DIR}/integration/junit_results.xml"
        }

    except subprocess.TimeoutExpired:
        print("Integration tests timed out")
        return {"success": False, "error": "timeout"}
    except Exception as e:
        print(f"Integration tests failed: {str(e)}")
        return {"success": False, "error": str(e)}

async def generate_final_report(test_results, timestamp):
    """Generate comprehensive final report"""
    print("Generating final test report...")

    # Calculate summary statistics
    phases = test_results["phases"]
    total_phases = len(phases)
    successful_phases = sum(1 for phase in phases.values() if phase.get("success", False))

    summary = {
        "overall_success": successful_phases == total_phases,
        "success_rate": f"{(successful_phases/total_phases)*100:.1f}%" if total_phases > 0 else "0%",
        "total_phases": total_phases,
        "successful_phases": successful_phases,
        "failed_phases": total_phases - successful_phases
    }

    test_results["summary"] = summary

    # Save detailed JSON report
    json_report_file = TEST_OUTPUT_DIR / f"story_1_1_final_report_{timestamp}.json"
    with open(json_report_file, 'w') as f:
        json.dump(test_results, f, indent=2, default=str)

    # Generate human-readable report
    text_report_file = TEST_OUTPUT_DIR / f"story_1_1_final_report_{timestamp}.txt"
    with open(text_report_file, 'w') as f:
        f.write("="*60 + "\n")
        f.write("STORY 1.1 COMPREHENSIVE TEST REPORT\n")
        f.write("="*60 + "\n\n")

        f.write(f"Timestamp: {test_results['timestamp']}\n")
        f.write(f"Test Suite: {test_results['test_suite']}\n")
        f.write(f"Total Execution Time: {test_results.get('total_execution_time', 0):.2f}s\n\n")

        f.write("SUMMARY\n")
        f.write("-" * 20 + "\n")
        f.write(f"Overall Success: {'PASS' if summary['overall_success'] else 'FAIL'}\n")
        f.write(f"Success Rate: {summary['success_rate']}\n")
        f.write(f"Phases: {summary['successful_phases']}/{summary['total_phases']} successful\n\n")

        f.write("PHASE RESULTS\n")
        f.write("-" * 20 + "\n")
        for phase_name, phase_result in phases.items():
            status = "PASS" if phase_result.get("success", False) else "FAIL"
            f.write(f"{phase_name.upper()}: {status}\n")

            if "error" in phase_result:
                f.write(f"  Error: {phase_result['error']}\n")

            if "exit_code" in phase_result:
                f.write(f"  Exit Code: {phase_result['exit_code']}\n")

        f.write(f"\nDETAILED RESULTS\n")
        f.write("-" * 20 + "\n")
        f.write(f"Full results saved to: {json_report_file}\n")
        f.write(f"Test outputs directory: {TEST_OUTPUT_DIR}\n")

    print(f"Final report generated:")
    print(f"   Human-readable: {text_report_file}")
    print(f"   JSON detailed: {json_report_file}")

    # Print summary to console
    print(f"\nFINAL SUMMARY")
    print(f"Overall Status: {'PASS' if summary['overall_success'] else 'FAIL'}")
    print(f"Success Rate: {summary['success_rate']}")
    print(f"Phases: {summary['successful_phases']}/{summary['total_phases']} successful")

if __name__ == "__main__":
    asyncio.run(main())