"""
Performance Comparison Test: Direct psycopg3 vs Postgres MCP
Story 1.4 Task 1 Phase 2 - Measure actual performance difference

This test imports 100 events using both approaches and measures:
- Total import time
- Events per second
- Connection overhead
"""

import pytest
import time
import json
import tempfile
import os
from pathlib import Path
from datetime import datetime, timezone

# Skip if no Postgres available
pytest_plugins = ('pytest_asyncio',)

pytestmark = pytest.mark.skipif(
    not os.getenv("POSTGRES_CONNECTION_STRING"),
    reason="Postgres not configured (set POSTGRES_CONNECTION_STRING)"
)


@pytest.fixture
def sample_jsonl_file():
    """Create sample JSONL file with 100 events"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        for i in range(100):
            event = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": "tool_call" if i % 2 == 0 else "agent_action",
                "category": "execution",
                "session_id": "perf_test_session",
                "story_id": "perf_test",
                "agent_name": f"agent_{i % 5}",
                "workflow_id": f"workflow_{i % 10}",
                "thread_id": None,
                "trace_id": None,
                "duration_ms": 100 + (i % 500),
                "tokens_used": 50 + (i % 200),
                "context_percent": 0.1 + (i % 50) / 100.0,
                "success": i % 10 != 0,  # 10% failure rate
                "confidence_score": 0.8 + (i % 20) / 100.0,
                "impact_score": 0.5 + (i % 50) / 100.0,
                "time_saved_or_wasted_ms": (i % 1000) - 500,
                "user_satisfaction_delta": (i % 20) / 100.0 - 0.1,
                "created_rule": i % 100 == 0,
                "pattern_detected": i % 50 == 0,
                "needs_review": i % 30 == 0,
                "details": {"iteration": i, "test": "performance"}
            }
            f.write(json.dumps(event) + '\n')

        temp_path = f.name

    yield Path(temp_path)

    # Cleanup
    os.unlink(temp_path)


@pytest.mark.asyncio
async def test_direct_psycopg3_import_performance(sample_jsonl_file):
    """Test direct psycopg3 import performance"""
    from src.core.postgres_manager import PostgresManager

    manager = PostgresManager()

    # Measure initialization time
    init_start = time.time()
    await manager.initialize()
    init_time = time.time() - init_start

    # Clean table
    await manager.execute_query("TRUNCATE TABLE madf_events")

    # Measure import time
    import_start = time.time()
    result = await manager.import_jsonl_file(sample_jsonl_file)
    import_time = time.time() - import_start

    await manager.close()

    # Calculate metrics
    events_per_second = result["imported"] / import_time if import_time > 0 else 0

    print("\n" + "="*60)
    print("DIRECT PSYCOPG3 PERFORMANCE")
    print("="*60)
    print(f"Initialization time: {init_time:.3f}s")
    print(f"Import time: {import_time:.3f}s")
    print(f"Events imported: {result['imported']}")
    print(f"Events per second: {events_per_second:.2f}")
    print(f"Errors: {result['errors']}")
    print("="*60)

    assert result["imported"] == 100
    assert result["errors"] == 0

    return {
        "approach": "direct_psycopg3",
        "init_time": init_time,
        "import_time": import_time,
        "events_per_second": events_per_second
    }


@pytest.mark.asyncio
async def test_postgres_mcp_import_performance(sample_jsonl_file):
    """Test Postgres MCP import performance"""
    from src.core.postgres_mcp_manager import PostgresMCPManager

    manager = PostgresMCPManager()

    # Measure initialization time
    init_start = time.time()
    await manager.initialize()
    init_time = time.time() - init_start

    # Clean table
    await manager.execute_query("TRUNCATE TABLE madf_events")

    # Measure import time
    import_start = time.time()
    result = await manager.import_jsonl_file(sample_jsonl_file)
    import_time = time.time() - import_start

    # Calculate metrics
    events_per_second = result["imported"] / import_time if import_time > 0 else 0

    print("\n" + "="*60)
    print("POSTGRES MCP PERFORMANCE")
    print("="*60)
    print(f"Initialization time: {init_time:.3f}s")
    print(f"Import time: {import_time:.3f}s")
    print(f"Events imported: {result['imported']}")
    print(f"Events per second: {events_per_second:.2f}")
    print(f"Errors: {result['errors']}")
    print("="*60)

    assert result["imported"] == 100
    assert result["errors"] == 0

    return {
        "approach": "postgres_mcp",
        "init_time": init_time,
        "import_time": import_time,
        "events_per_second": events_per_second
    }


@pytest.mark.asyncio
async def test_performance_comparison(sample_jsonl_file):
    """
    Run both approaches and compare performance

    This test will show actual speed difference between:
    - Direct psycopg3 with connection pooling
    - Postgres MCP via mcp_bridge.py
    """

    # Test direct approach
    direct_result = await test_direct_psycopg3_import_performance(sample_jsonl_file)

    # Small delay between tests
    time.sleep(2)

    # Test MCP approach
    mcp_result = await test_postgres_mcp_import_performance(sample_jsonl_file)

    # Calculate comparison
    speedup = mcp_result["import_time"] / direct_result["import_time"]

    print("\n" + "="*60)
    print("PERFORMANCE COMPARISON SUMMARY")
    print("="*60)
    print(f"Direct psycopg3 time: {direct_result['import_time']:.3f}s")
    print(f"Postgres MCP time: {mcp_result['import_time']:.3f}s")
    print(f"Speed ratio: {speedup:.2f}x")
    if speedup > 1:
        print(f"✓ Direct psycopg3 is {speedup:.2f}x FASTER")
    else:
        print(f"✓ Postgres MCP is {1/speedup:.2f}x FASTER")
    print("="*60)
    print("\nRECOMMENDATION:")
    if speedup > 2:
        print("Use direct psycopg3 - significantly faster for bulk operations")
    elif speedup > 1.2:
        print("Use direct psycopg3 - moderately faster")
    elif speedup < 0.8:
        print("Use Postgres MCP - faster than direct")
    else:
        print("Performance similar - choose based on other factors (type safety, API)")
    print("="*60)

    # Document findings
    with open("tests/reports/postgres_performance_comparison.md", "w") as f:
        f.write("# Postgres Performance Comparison\n\n")
        f.write(f"**Test Date**: {datetime.now().isoformat()}\n\n")
        f.write("## Test Conditions\n")
        f.write("- Events: 100\n")
        f.write("- Environment: " + os.getenv("POSTGRES_CONNECTION_STRING", "local").split("@")[0] + "\n\n")
        f.write("## Results\n\n")
        f.write("| Approach | Import Time | Events/sec | Speed Ratio |\n")
        f.write("|----------|-------------|------------|-------------|\n")
        f.write(f"| Direct psycopg3 | {direct_result['import_time']:.3f}s | {direct_result['events_per_second']:.2f} | 1.00x (baseline) |\n")
        f.write(f"| Postgres MCP | {mcp_result['import_time']:.3f}s | {mcp_result['events_per_second']:.2f} | {speedup:.2f}x |\n\n")
        f.write("## Recommendation\n\n")
        if speedup > 1.5:
            f.write("**Use direct psycopg3** - Significantly faster for bulk operations.\n")
        elif speedup < 0.9:
            f.write("**Use Postgres MCP** - Faster than direct implementation.\n")
        else:
            f.write("**Performance similar** - Choose based on other factors.\n")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
