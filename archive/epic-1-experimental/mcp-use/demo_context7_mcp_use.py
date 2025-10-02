"""
Demo: Context7 MCP Tool Call via MCP-use Wrapper

Shows how Analyst Agent uses Context7 for real-time documentation
"""

from src.agents.analyst_agent import AnalystAgent


def demo_context7_integration():
    """Demonstrate Context7 MCP-use tool integration"""

    print("=" * 60)
    print("Context7 MCP-use Integration Demo")
    print("=" * 60)
    print()

    # Initialize Analyst Agent (contains MCPBridge with Context7)
    agent = AnalystAgent()

    # Example 1: Get LangGraph documentation
    print("[Example 1] Getting LangGraph v0.2.0 documentation...")
    print("-" * 60)

    result1 = agent.get_documentation(
        package="langgraph",
        version="0.2.0"
    )

    print(f"Tool Used: {result1['tool_used']}")
    print(f"Package: {result1['package']} v{result1['version']}")
    print(f"Retrieved: {result1['documentation_retrieved']}")
    print(f"Cached: {result1['cached']}")

    if result1['documentation']:
        doc = result1['documentation']
        print(f"\nDescription: {doc['description']}")
        print(f"API Reference: {doc['api_reference']}")
        print(f"Examples: {doc['examples']}")

    print()

    # Example 2: Same call should return cached result
    print("[Example 2] Requesting same documentation (should be cached)...")
    print("-" * 60)

    result2 = agent.get_documentation(
        package="langgraph",
        version="0.2.0"
    )

    print(f"Tool Used: {result2['tool_used']}")
    print(f"Package: {result2['package']} v{result2['version']}")
    print(f"Retrieved: {result2['documentation_retrieved']}")
    print(f"Cached: {result2['cached']} [CACHE HIT]")

    print()

    # Example 3: Different package
    print("[Example 3] Getting Pydantic v2.0 documentation...")
    print("-" * 60)

    result3 = agent.get_documentation(
        package="pydantic",
        version="2.0"
    )

    print(f"Tool Used: {result3['tool_used']}")
    print(f"Package: {result3['package']} v{result3['version']}")
    print(f"Retrieved: {result3['documentation_retrieved']}")
    print(f"Cached: {result3['cached']}")

    print()
    print("=" * 60)
    print("Context7 MCP Configuration Details")
    print("=" * 60)
    print()

    # Show MCP bridge configuration
    bridge = agent.mcp_bridge

    print(f"MCP Server Type: {bridge.wrapped_mcp_servers['context7']['type']}")
    print(f"NPM Package: {bridge.wrapped_mcp_servers['context7']['package']}")
    print()

    # Show available tools
    context7_tools = bridge.load_mcp_tools("context7")
    print("Available Context7 Tools:")
    for tool_name, description in context7_tools.items():
        print(f"  - {tool_name}: {description}")

    print()
    print("=" * 60)
    print("Direct MCP Bridge Call Example")
    print("=" * 60)
    print()

    # Example 4: Direct bridge call (lower-level API)
    print("[Example 4] Direct call to Context7 via MCPBridge...")
    print("-" * 60)

    direct_result = bridge.call_context7_tool(
        "get_package_docs",
        {
            "package_name": "fastapi",
            "version": "0.100.0"
        }
    )

    print(f"Success: {direct_result['success']}")
    print(f"Cached: {direct_result['cached']}")

    if direct_result['success']:
        doc = direct_result['documentation']
        print(f"Package: {doc['package']} v{doc['version']}")
        print(f"Description: {doc['description']}")

    print()
    print("=" * 60)
    print("Cache Demonstration")
    print("=" * 60)
    print()

    # Show cache state
    print(f"Current cache size: {len(bridge._context7_cache)} entries")
    print()
    print("Cache keys:")
    for i, key in enumerate(bridge._context7_cache.keys(), 1):
        print(f"  {i}. {key}")

    print()
    print("Demo complete!")


if __name__ == "__main__":
    demo_context7_integration()