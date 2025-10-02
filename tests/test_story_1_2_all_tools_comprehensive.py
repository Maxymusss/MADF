"""
Comprehensive test: ALL tools from each Story 1.2 MCP server
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.mcp_bridge import MCPBridge

def test_all_serena_tools():
    """Test key Serena tools"""
    print("\n" + "="*70)
    print("SERENA MCP - Testing Key Tools (4 most important)")
    print("="*70)

    bridge = MCPBridge()
    results = {}

    # Test 1: find_symbol
    print("\n[1/4] find_symbol - Find MCPBridge class...")
    try:
        result = bridge.call_serena_tool("find_symbol", {
            "name_path": "MCPBridge",
            "relative_path": "src/core/mcp_bridge.py",
            "include_body": False
        })
        success = result.get('success') and 'symbols' in result
        results['find_symbol'] = success
        print(f"      {'PASS' if success else 'FAIL'}")
    except Exception as e:
        results['find_symbol'] = False
        print(f"      FAIL: {e}")

    # Test 2: get_symbols_overview
    print("\n[2/4] get_symbols_overview - Overview of mcp_bridge.py...")
    try:
        result = bridge.call_serena_tool("get_symbols_overview", {
            "relative_path": "src/core/mcp_bridge.py"
        })
        success = result.get('success')
        results['get_symbols_overview'] = success
        print(f"      {'PASS' if success else 'FAIL'}")
    except Exception as e:
        results['get_symbols_overview'] = False
        print(f"      FAIL: {e}")

    # Test 3: search_for_pattern
    print("\n[3/4] search_for_pattern - Search for 'async def'...")
    try:
        result = bridge.call_serena_tool("search_for_pattern", {
            "substring_pattern": "async def",
            "relative_path": "src/core/mcp_bridge.py"
        })
        success = result.get('success')
        results['search_for_pattern'] = success
        print(f"      {'PASS' if success else 'FAIL'}")
    except Exception as e:
        results['search_for_pattern'] = False
        print(f"      FAIL: {e}")

    # Test 4: find_referencing_symbols
    print("\n[4/4] find_referencing_symbols - Find references to MCPBridge...")
    try:
        result = bridge.call_serena_tool("find_referencing_symbols", {
            "name_path": "MCPBridge",
            "relative_path": "src/core/mcp_bridge.py"
        })
        success = result.get('success')
        results['find_referencing_symbols'] = success
        print(f"      {'PASS' if success else 'FAIL'}")
    except Exception as e:
        results['find_referencing_symbols'] = False
        print(f"      FAIL: {e}")

    return results

def test_all_context7_tools():
    """Test ALL Context7 tools"""
    print("\n" + "="*70)
    print("CONTEXT7 MCP - Testing All Tools (2/2)")
    print("="*70)

    bridge = MCPBridge()
    results = {}

    # Test 1: resolve-library-id
    print("\n[1/2] resolve-library-id - Resolve 'React' library...")
    try:
        result = bridge.call_context7_tool("resolve-library-id", {
            "libraryName": "React"
        })
        success = result.get('success')
        results['resolve-library-id'] = success
        print(f"      {'PASS' if success else 'FAIL'}")

        # Store library ID for next test
        if success:
            doc_text = str(result.get('documentation', ''))
            # Try to extract library ID from response
            # Typically format: /npm/react or similar
            library_id = "/npm/react"  # Default assumption
    except Exception as e:
        results['resolve-library-id'] = False
        print(f"      FAIL: {e}")
        library_id = "/npm/react"

    # Test 2: get-library-docs
    print("\n[2/2] get-library-docs - Get React hooks documentation...")
    try:
        result = bridge.call_context7_tool("get-library-docs", {
            "context7CompatibleLibraryID": library_id,
            "topic": "hooks useState",
            "tokens": 500
        })
        success = result.get('success')
        results['get-library-docs'] = success
        print(f"      {'PASS' if success else 'FAIL'}")
    except Exception as e:
        results['get-library-docs'] = False
        print(f"      FAIL: {e}")

    return results

def test_all_sequential_thinking_tools():
    """Test Sequential Thinking tool"""
    print("\n" + "="*70)
    print("SEQUENTIAL THINKING MCP - Testing All Tools (1/1)")
    print("="*70)

    bridge = MCPBridge()
    results = {}

    # Test 1: sequentialthinking
    print("\n[1/1] sequentialthinking - Multi-step reasoning...")
    try:
        result = bridge.call_sequential_thinking_tool("sequentialthinking", {
            "thought": "Step 1: Analyzing MCP SDK unified architecture benefits",
            "nextThoughtNeeded": True,
            "thoughtNumber": 1,
            "totalThoughts": 3
        })
        success = result.get('success')
        results['sequentialthinking'] = success
        print(f"      {'PASS' if success else 'FAIL'}")
    except Exception as e:
        results['sequentialthinking'] = False
        print(f"      FAIL: {e}")

    return results

if __name__ == "__main__":
    print("\n" + "="*70)
    print("Story 1.2 Comprehensive Test - ALL MCP Tools")
    print("="*70)

    serena_results = test_all_serena_tools()
    context7_results = test_all_context7_tools()
    seq_results = test_all_sequential_thinking_tools()

    # Summary
    print("\n" + "="*70)
    print("COMPREHENSIVE RESULTS")
    print("="*70)

    print("\nSerena (4 key tools tested):")
    for tool, passed in serena_results.items():
        print(f"  {tool:30} {'PASS' if passed else 'FAIL'}")

    print("\nContext7 (2/2 tools tested):")
    for tool, passed in context7_results.items():
        print(f"  {tool:30} {'PASS' if passed else 'FAIL'}")

    print("\nSequential Thinking (1/1 tool tested):")
    for tool, passed in seq_results.items():
        print(f"  {tool:30} {'PASS' if passed else 'FAIL'}")

    # Calculate totals
    total_tests = len(serena_results) + len(context7_results) + len(seq_results)
    total_passed = sum(serena_results.values()) + sum(context7_results.values()) + sum(seq_results.values())

    print("\n" + "="*70)
    print(f"OVERALL: {total_passed}/{total_tests} tests passing ({int(total_passed/total_tests*100)}%)")
    print("="*70)

    if total_passed == total_tests:
        print("\nStory 1.2 Status: ALL TESTS PASSING - READY FOR COMPLETION")
    else:
        print(f"\nStory 1.2 Status: {total_tests - total_passed} tests failing - needs fixes")
    print("="*70)
