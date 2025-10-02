"""Test what tools are available from Obsidian MCP server"""

import sys
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.mcp_bridge import MCPBridge
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

async def list_obsidian_tools():
    bridge = MCPBridge()
    server_config = bridge.wrapped_mcp_servers["obsidian"]

    server_params = StdioServerParameters(
        command=server_config["command"],
        args=server_config["args"]
    )

    print("Connecting to Obsidian MCP server...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            tools_result = await session.list_tools()
            print(f"\nAvailable Obsidian MCP tools ({len(tools_result.tools)}):")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")

if __name__ == "__main__":
    asyncio.run(list_obsidian_tools())
