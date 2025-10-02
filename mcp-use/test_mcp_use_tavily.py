"""
Test Tavily search using real mcp-use library with ChatAnthropic
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

async def test_mcp_use_tavily():
    """Use mcp-use with Anthropic to search NFL scores"""

    print("=" * 60)
    print("Testing mcp-use with ChatAnthropic + Tavily")
    print("=" * 60)

    try:
        # Import mcp-use (installed in anaconda)
        sys.path.insert(0, r"D:\Programs\anaconda3\Lib\site-packages")
        from mcp_use import MCPClient, MCPAgent
        from langchain_anthropic import ChatAnthropic

        print("\n[1] Initializing ChatAnthropic...")
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20240620",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.7
        )
        print(f"    Model: {llm.model}")

        print("\n[2] Creating MCP Client with Tavily server...")
        config = {
            "mcpServers": {
                "tavily": {
                    "command": "C:\\Program Files\\nodejs\\npx.cmd",
                    "args": ["-y", "tavily-mcp"],
                    "env": {
                        "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY")
                    }
                }
            }
        }

        client = MCPClient(config=config)
        print("    MCP Client created")

        print("\n[3] Creating MCPAgent...")
        agent = MCPAgent(llm=llm, client=client)
        print("    Agent created")

        print("\n[4] Running query: 'Search for NFL scores from yesterday'...")
        print("    (This may take 30-60 seconds for LLM + tool execution)")

        result = await agent.run("Search for NFL scores from yesterday and summarize the top 3 games")

        print("\n" + "=" * 60)
        print("RESULT FROM MCP-USE + ANTHROPIC")
        print("=" * 60)
        print(result)
        print("=" * 60)

    except ImportError as e:
        print(f"\n[ERROR] Import failed: {e}")
        print("\nMissing dependencies. Install with:")
        print("  pip install mcp-use langchain-anthropic")
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    print("\n[OK] Test complete")


if __name__ == "__main__":
    asyncio.run(test_mcp_use_tavily())