"""
Quick test: Can Python mcp_bridge spawn and communicate with Serena MCP server?
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.mcp_bridge import MCPBridge

def test_serena_connection():
    """Test basic Serena MCP connection via bridge"""
    print("Initializing MCPBridge...")
    bridge = MCPBridge()

    print("\nTesting Serena tool loading...")
    tools = bridge.load_mcp_tools("serena")
    print(f"Available tools: {list(tools.keys())}")

    print("\nTesting find_symbol on real file (project auto-activated via --project flag)...")
    result = bridge.call_serena_tool(
        "find_symbol",
        {
            "name_path": "MCPBridge",
            "relative_path": "src/core/mcp_bridge.py",
            "include_body": False
        }
    )

    print(f"\nResult success: {result.get('success')}")
    print(f"Full result: {result}")

    if result.get('success'):
        if 'symbol_info' in result:
            print(f"Symbol found: {result.get('symbol_info', {}).get('name')}")
            print(f"File: {result.get('symbol_info', {}).get('file')}")
        else:
            print(f"Result keys: {list(result.keys())}")
    else:
        print(f"Error: {result.get('error')}")

    return result

if __name__ == "__main__":
    test_serena_connection()
