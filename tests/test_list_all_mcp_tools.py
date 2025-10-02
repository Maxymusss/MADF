"""
List all available tools from each MCP server to get correct tool names
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.mcp_bridge import MCPBridge

def list_tools_for_server(server_name):
    """List all tools for a given MCP server"""
    print(f"\n{'='*60}")
    print(f"MCP Server: {server_name}")
    print('='*60)

    bridge = MCPBridge()

    try:
        tools = bridge.load_mcp_tools(server_name)
        print(f"Total tools: {len(tools)}")
        print("\nTool details:")
        for tool_name, tool_info in tools.items():
            print(f"\n  {tool_name}:")
            if hasattr(tool_info, 'description'):
                print(f"    Description: {tool_info.description[:100]}...")
            if hasattr(tool_info, 'inputSchema'):
                schema = tool_info.inputSchema
                if 'properties' in schema:
                    print(f"    Parameters: {list(schema['properties'].keys())}")
        return tools
    except Exception as e:
        print(f"Error loading tools: {e}")
        import traceback
        traceback.print_exc()
        return {}

if __name__ == "__main__":
    print("\n" + "="*60)
    print("MCP Server Tool Discovery")
    print("="*60)

    # Test each Story 1.2 MCP server
    serena_tools = list_tools_for_server("serena")
    context7_tools = list_tools_for_server("context7")
    seq_tools = list_tools_for_server("sequential_thinking")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Serena tools:              {len(serena_tools)}")
    print(f"Context7 tools:            {len(context7_tools)}")
    print(f"Sequential Thinking tools: {len(seq_tools)}")
    print("="*60)
