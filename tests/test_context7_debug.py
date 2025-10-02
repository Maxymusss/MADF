"""
Debug Context7 MCP integration to understand why tools aren't callable
"""
import sys
from pathlib import Path
import asyncio

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.mcp_bridge import MCPBridge
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def debug_context7():
    print("Debugging Context7 MCP Server...")

    # Connect directly with MCP SDK
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@upstash/context7-mcp"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List tools
            print("\n1. Listing tools...")
            tools_result = await session.list_tools()
            print(f"   Tools: {[t.name for t in tools_result.tools]}")

            # Get first tool details
            if tools_result.tools:
                tool = tools_result.tools[0]
                print(f"\n2. Tool details for '{tool.name}':")
                print(f"   Description: {tool.description}")
                print(f"   Input schema: {tool.inputSchema}")

                # Try calling with minimal params
                print(f"\n3. Attempting to call '{tool.name}'...")
                try:
                    result = await session.call_tool(tool.name, {"query": "test"})
                    print(f"   Success!")
                    print(f"   Result: {result.content}")
                except Exception as e:
                    print(f"   Error: {e}")
                    import traceback
                    traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_context7())
