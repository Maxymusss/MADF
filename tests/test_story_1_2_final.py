"""
Final test: All Story 1.2 MCP tools with correct names via unified SDK
Tests: Serena, Context7, Sequential Thinking
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.mcp_bridge import MCPBridge

def test_serena():
    """Test Serena - find_symbol"""
    print("\n" + "="*60)
    print("SERENA MCP - Semantic Code Search")
    print("="*60)

    bridge = MCPBridge()

    print("\n[TEST] find_symbol for MCPBridge class...")
    result = bridge.call_serena_tool("find_symbol", {
        "name_path": "MCPBridge",
        "relative_path": "src/core/mcp_bridge.py",
        "include_body": False
    })

    success = result.get('success', False)
    print(f"Result: {'PASS' if success else 'FAIL'}")
    if success and 'symbols' in result:
        print(f"Found: {result['symbols'][0].get('name_path')} at line {result['symbols'][0].get('body_location', {}).get('start_line')}")
    elif not success:
        print(f"Error: {result.get('error', 'Unknown')}")

    return success

def test_context7():
    """Test Context7 - resolve-library-id"""
    print("\n" + "="*60)
    print("CONTEXT7 MCP - Real-time Documentation")
    print("="*60)

    bridge = MCPBridge()

    print("\n[TEST] resolve-library-id for React...")
    result = bridge.call_context7_tool("resolve-library-id", {
        "libraryName": "React"
    })

    success = result.get('success', False)
    print(f"Result: {'PASS' if success else 'FAIL'}")
    if success:
        doc = result.get('documentation', result.get('result', ''))
        print(f"Response: {str(doc)[:100]}...")
    else:
        print(f"Error: {result.get('error', 'Unknown')[:150]}")

    return success

def test_sequential_thinking():
    """Test Sequential Thinking - sequentialthinking"""
    print("\n" + "="*60)
    print("SEQUENTIAL THINKING MCP - Complex Reasoning")
    print("="*60)

    bridge = MCPBridge()

    print("\n[TEST] sequentialthinking for MCP SDK analysis...")
    result = bridge.call_sequential_thinking_tool("sequentialthinking", {
        "thought": "Analyzing the benefits of unified MCP SDK approach",
        "nextThoughtNeeded": True,
        "thoughtNumber": 1,
        "totalThoughts": 2
    })

    success = result.get('success', False)
    print(f"Result: {'PASS' if success else 'FAIL'}")
    if success:
        reasoning = result.get('reasoning', {})
        print(f"Reasoning: {str(reasoning)[:100]}...")
    else:
        print(f"Error: {result.get('error', 'Unknown')[:150]}")

    return success

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Story 1.2 Final Test - Unified MCP SDK")
    print("MCP SDK v1.15.0 | Sonnet 4.5")
    print("="*60)

    serena_pass = test_serena()
    context7_pass = test_context7()
    seq_think_pass = test_sequential_thinking()

    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    print(f"Serena (Semantic Search):      {'PASS' if serena_pass else 'FAIL'}")
    print(f"Context7 (Documentation):      {'PASS' if context7_pass else 'FAIL'}")
    print(f"Sequential Thinking (Reason):  {'PASS' if seq_think_pass else 'FAIL'}")
    print("="*60)

    all_pass = serena_pass and context7_pass and seq_think_pass
    print(f"\nStory 1.2 Status: {'ALL TESTS PASSING' if all_pass else 'NEEDS FIXES'}")
    print("="*60)
