"""
Test all Story 1.2 MCP tools via unified SDK approach
Tests: Serena, Context7, Sequential Thinking
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.mcp_bridge import MCPBridge

def test_serena_tools():
    """Test Serena MCP tools"""
    print("\n" + "="*60)
    print("TESTING SERENA MCP (Semantic Code Search)")
    print("="*60)

    bridge = MCPBridge()

    # Test 1: find_symbol
    print("\n1. Testing find_symbol...")
    result = bridge.call_serena_tool("find_symbol", {
        "name_path": "MCPBridge",
        "relative_path": "src/core/mcp_bridge.py",
        "include_body": False
    })
    print(f"   Success: {result.get('success')}")
    if result.get('success') and 'symbols' in result:
        print(f"   Found {len(result['symbols'])} symbol(s)")
        print(f"   Symbol: {result['symbols'][0].get('name_path')}")
    elif result.get('success'):
        print(f"   Result keys: {list(result.keys())}")
    else:
        print(f"   Error: {result.get('error')}")

    # Test 2: search_for_pattern
    print("\n2. Testing search_for_pattern...")
    result2 = bridge.call_serena_tool("search_for_pattern", {
        "pattern": "def __init__",
        "relative_path": "src/core/mcp_bridge.py"
    })
    print(f"   Success: {result2.get('success')}")
    if result2.get('success'):
        print(f"   Result: {str(result2)[:100]}...")
    else:
        print(f"   Error: {result2.get('error')}")

    return result

def test_context7_tools():
    """Test Context7 MCP tools"""
    print("\n" + "="*60)
    print("TESTING CONTEXT7 MCP (Real-time Documentation)")
    print("="*60)

    bridge = MCPBridge()

    # Test: search (or available tool)
    print("\n1. Listing available Context7 tools...")
    tools = bridge.load_mcp_tools("context7")
    print(f"   Available tools: {list(tools.keys())}")

    # Try first available tool
    if tools:
        tool_name = list(tools.keys())[0]
        print(f"\n2. Testing {tool_name}...")

        # Attempt tool call with minimal params
        result = bridge.call_context7_tool(tool_name, {
            "query": "React hooks"
        })
        print(f"   Success: {result.get('success')}")
        if result.get('success'):
            print(f"   Result keys: {list(result.keys())}")
            if 'documentation' in result:
                doc = str(result['documentation'])
                print(f"   Documentation: {doc[:100]}...")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')[:200]}")
            if 'traceback' in result:
                print(f"   Traceback snippet: {result['traceback'][-300:]}")

    return result if tools else {"success": False, "error": "No tools available"}

def test_sequential_thinking_tools():
    """Test Sequential Thinking MCP tools"""
    print("\n" + "="*60)
    print("TESTING SEQUENTIAL THINKING MCP (Reasoning)")
    print("="*60)

    bridge = MCPBridge()

    # Test: sequential_thinking (correct tool name)
    print("\n1. Listing available Sequential Thinking tools...")
    tools = bridge.load_mcp_tools("sequential_thinking")
    print(f"   Available tools: {list(tools.keys())}")

    if "reason" in tools:
        print("\n2. Testing reason tool...")
        result = bridge.call_sequential_thinking_tool("reason", {
            "query": "What are the benefits of using MCP SDK?"
        })
        print(f"   Success: {result.get('success')}")
        if result.get('success'):
            print(f"   Result keys: {list(result.keys())}")
            if 'reasoning' in result:
                print(f"   Reasoning: {str(result['reasoning'])[:150]}...")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')[:200]}")
            if 'traceback' in result:
                print(f"   Traceback snippet: {result['traceback'][-300:]}")
    else:
        print(f"   Tool 'sequential_thinking' not found in available tools")
        result = {"success": False, "error": "Tool not found"}

    return result

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Story 1.2: Testing All MCP Tools via Unified SDK")
    print("MCP SDK Version: 1.15.0")
    print("="*60)

    # Test all three tools
    serena_result = test_serena_tools()
    context7_result = test_context7_tools()
    seq_think_result = test_sequential_thinking_tools()

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Serena:              {'PASS' if serena_result.get('success') else 'FAIL'}")
    print(f"Context7:            {'PASS' if context7_result.get('success') else 'FAIL'}")
    print(f"Sequential Thinking: {'PASS' if seq_think_result.get('success') else 'FAIL'}")
    print("="*60)
