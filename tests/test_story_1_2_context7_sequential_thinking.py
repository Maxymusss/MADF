"""
Test Context7 and Sequential Thinking MCP integration via Python bridge
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.mcp_bridge import MCPBridge

def test_context7_integration():
    """Test Context7 MCP for real-time documentation"""
    print("=" * 60)
    print("Testing Context7 MCP Integration")
    print("=" * 60)

    bridge = MCPBridge()

    print("\n1. Loading Context7 tools...")
    tools = bridge.load_mcp_tools("context7")
    print(f"   Available tools: {list(tools.keys())}")

    print("\n2. Testing documentation retrieval...")
    # Note: Context7 uses HTTP transport, not stdio
    result = bridge.call_context7_tool(
        "search_docs",
        {
            "query": "React useState hook"
        }
    )

    print(f"\n   Result success: {result.get('success')}")
    print(f"   Result keys: {list(result.keys())}")
    if result.get('success'):
        print(f"   Documentation retrieved: {result.get('documentation', 'N/A')[:100]}...")
    else:
        print(f"   Error: {result.get('error')}")

    return result

def test_sequential_thinking_integration():
    """Test Sequential Thinking MCP for complex reasoning"""
    print("\n" + "=" * 60)
    print("Testing Sequential Thinking MCP Integration")
    print("=" * 60)

    bridge = MCPBridge()

    print("\n1. Loading Sequential Thinking tools...")
    tools = bridge.load_mcp_tools("sequential_thinking")
    print(f"   Available tools: {list(tools.keys())}")

    print("\n2. Testing reasoning workflow...")
    result = bridge.call_sequential_thinking_tool(
        "reason",
        {
            "problem": "What are the key benefits of using MCP for agent tool integration?"
        }
    )

    print(f"\n   Result success: {result.get('success')}")
    print(f"   Result keys: {list(result.keys())}")
    if result.get('success'):
        print(f"   Reasoning output: {result.get('reasoning', result)}")
    else:
        print(f"   Error: {result.get('error')}")

    return result

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Story 1.2: Testing Context7 & Sequential Thinking MCP")
    print("=" * 60)

    context7_result = test_context7_integration()
    seq_think_result = test_sequential_thinking_integration()

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Context7: {'✅ PASS' if context7_result.get('success') else '❌ FAIL'}")
    print(f"Sequential Thinking: {'✅ PASS' if seq_think_result.get('success') else '❌ FAIL'}")
    print("=" * 60)
