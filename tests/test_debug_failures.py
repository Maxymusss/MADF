"""
Debug failing tools to understand parameter requirements
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.mcp_bridge import MCPBridge

def debug_serena_get_symbols_overview():
    """Debug get_symbols_overview"""
    print("\n" + "="*60)
    print("DEBUG: Serena get_symbols_overview")
    print("="*60)

    bridge = MCPBridge()

    # Get tool schema
    tools = bridge.load_mcp_tools("serena")
    tool = tools.get("get_symbols_overview")

    if tool:
        print(f"\nTool: {tool.name}")
        print(f"Description: {tool.description[:200]}...")
        print(f"Required params: {tool.inputSchema.get('required', [])}")
        print(f"All params: {list(tool.inputSchema.get('properties', {}).keys())}")

    print("\nAttempting call...")
    try:
        result = bridge.call_serena_tool("get_symbols_overview", {
            "relative_path": "src/core/mcp_bridge.py"
        })
        print(f"Success: {result.get('success')}")
        if not result.get('success'):
            print(f"Error: {result.get('error')}")
            if 'traceback' in result:
                print(f"Traceback:\n{result['traceback']}")
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()

def debug_context7_get_library_docs():
    """Debug get-library-docs"""
    print("\n" + "="*60)
    print("DEBUG: Context7 get-library-docs")
    print("="*60)

    bridge = MCPBridge()

    # Get tool schema
    tools = bridge.load_mcp_tools("context7")
    tool = tools.get("get-library-docs")

    if tool:
        print(f"\nTool: {tool.name}")
        print(f"Description: {tool.description[:200]}...")
        print(f"Required params: {tool.inputSchema.get('required', [])}")
        print(f"All params: {list(tool.inputSchema.get('properties', {}).keys())}")

    print("\nAttempting call...")
    try:
        result = bridge.call_context7_tool("get-library-docs", {
            "context7CompatibleLibraryID": "/npm/react",
            "topic": "hooks",
            "tokens": 500
        })
        print(f"Success: {result.get('success')}")
        if not result.get('success'):
            print(f"Error: {result.get('error')}")
            if 'traceback' in result:
                print(f"Traceback:\n{result['traceback'][-500:]}")
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_serena_get_symbols_overview()
    debug_context7_get_library_docs()
