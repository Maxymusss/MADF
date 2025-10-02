"""
mcp-use with Ollama via Python

Alternative approach: Use Python MCP SDK with Ollama directly
Requires: pip install mcp ollama
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List

try:
    import ollama
    from mcp.client import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("   pip install mcp ollama")
    exit(1)


class OllamaMCPClient:
    """MCP client using Ollama as LLM backend"""

    def __init__(self, model: str = "qwen2.5:7b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.ollama_client = ollama.Client(host=base_url)
        self.mcp_sessions: Dict[str, ClientSession] = {}

    async def connect_mcp_server(
        self,
        server_name: str,
        command: str,
        args: List[str],
        env: Dict[str, str] = None
    ):
        """Connect to MCP server"""
        print(f"🔌 Connecting to {server_name} MCP server...")

        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env or {}
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                self.mcp_sessions[server_name] = session

                # List available tools
                tools_result = await session.list_tools()
                print(f"✅ {server_name}: {len(tools_result.tools)} tools available")

                for tool in tools_result.tools:
                    print(f"   - {tool.name}: {tool.description}")

                return session

    def chat_with_tools(self, prompt: str, tools: List[Dict[str, Any]]) -> str:
        """Chat with Ollama using tool calling"""
        print(f"\n🤖 Ollama ({self.model}) processing: {prompt}\n")

        # Format tools for Ollama
        ollama_tools = []
        for tool in tools:
            ollama_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("inputSchema", {})
                }
            })

        # Call Ollama with tools
        response = self.ollama_client.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            tools=ollama_tools,
            options={
                "temperature": 0.7,
                "num_predict": 4096
            }
        )

        return response["message"]["content"]

    async def run_agent(self, task: str):
        """Run agent task with Ollama + MCP tools"""
        print(f"🎯 Task: {task}\n")

        # Connect to filesystem MCP server
        filesystem_session = await self.connect_mcp_server(
            server_name="filesystem",
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-filesystem",
                str(Path.cwd())
            ],
            env={"ALLOWED_DIRECTORIES": str(Path.cwd())}
        )

        # Get tools from MCP server
        tools_result = await filesystem_session.list_tools()
        tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
            }
            for tool in tools_result.tools
        ]

        # Execute task with Ollama
        result = self.chat_with_tools(task, tools)

        print("\n📊 Result:")
        print(result)

        return result


async def main():
    """Main execution"""
    print("🚀 Starting Ollama + MCP Integration\n")

    # Check if Ollama is running
    try:
        client = ollama.Client()
        models = client.list()
        print(f"✅ Ollama running with {len(models['models'])} models")

        # Check if qwen2.5:7b is available
        model_names = [m["name"] for m in models["models"]]
        if "qwen2.5:7b" not in model_names:
            print("⚠️  Model qwen2.5:7b not found. Pulling model...")
            ollama.pull("qwen2.5:7b")
            print("✅ Model pulled successfully")

    except Exception as e:
        print(f"❌ Ollama not running: {e}")
        print("   Start Ollama with: ollama serve")
        return

    # Create Ollama MCP client
    ollama_mcp = OllamaMCPClient(model="qwen2.5:7b")

    # Run example task
    await ollama_mcp.run_agent(
        task="List the files in the current directory and count how many Python files exist"
    )

    print("\n✅ Complete")


if __name__ == "__main__":
    asyncio.run(main())