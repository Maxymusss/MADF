"""
Test Tavily MCP server through mcp-use
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

async def test_tavily_mcp():
    """Test Tavily search via MCP"""

    print("=" * 60)
    print("Testing Tavily MCP via mcp-use")
    print("=" * 60)

    # Using subprocess to test MCP stdio communication
    import subprocess
    import json

    # Start Tavily MCP server
    env = os.environ.copy()
    env['TAVILY_API_KEY'] = os.getenv('TAVILY_API_KEY')

    print("\n[1] Starting Tavily MCP server...")
    proc = subprocess.Popen(
        ['C:\\Program Files\\nodejs\\npx.cmd', '-y', 'tavily-mcp'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
        shell=True
    )

    # Send MCP initialize request
    print("[2] Sending initialize request...")
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }

    proc.stdin.write(json.dumps(init_request) + "\n")
    proc.stdin.flush()

    # Read response
    response = proc.stdout.readline()
    print(f"[3] Initialize response: {response[:100]}...")

    # List tools
    print("\n[4] Requesting available tools...")
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    }

    proc.stdin.write(json.dumps(tools_request) + "\n")
    proc.stdin.flush()

    response = proc.stdout.readline()
    print(f"[5] Tools response:")
    try:
        tools_data = json.loads(response)
        if 'result' in tools_data and 'tools' in tools_data['result']:
            for tool in tools_data['result']['tools']:
                print(f"    - {tool.get('name')}: {tool.get('description', 'N/A')[:60]}")
    except:
        print(f"    Raw: {response[:200]}")

    # Call search tool
    print("\n[6] Calling tavily_search tool...")
    search_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "tavily_search",
            "arguments": {
                "query": "LangGraph multi-agent framework"
            }
        }
    }

    proc.stdin.write(json.dumps(search_request) + "\n")
    proc.stdin.flush()

    response = proc.stdout.readline()
    print(f"[7] Search results:")
    try:
        search_data = json.loads(response)
        if 'result' in search_data:
            result = search_data['result']
            if isinstance(result, dict) and 'content' in result:
                for item in result['content'][:2]:  # Show first 2 results
                    if isinstance(item, dict):
                        print(f"\n  Title: {item.get('title', 'N/A')}")
                        print(f"  URL: {item.get('url', 'N/A')}")
                        print(f"  Snippet: {item.get('content', 'N/A')[:100]}...")
    except Exception as e:
        print(f"    Error parsing: {e}")
        print(f"    Raw: {response[:300]}")

    # Cleanup
    proc.terminate()
    proc.wait(timeout=2)

    print("\n" + "=" * 60)
    print("[OK] Tavily MCP test complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_tavily_mcp())