"""
Test Obsidian and Filesystem MCP tools (Story 1.3)
Skip Graphiti due to Windows neo4j compatibility issues
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.mcp_bridge import MCPBridge


def test_filesystem_tools():
    """Test all Filesystem MCP tools"""
    print("\n" + "="*80)
    print("TESTING FILESYSTEM MCP TOOLS")
    print("="*80)

    bridge = MCPBridge()

    # Create test directory structure
    test_dir = Path(__file__).parent / "test_filesystem_validation"
    test_dir.mkdir(exist_ok=True)

    # Test 1: list_allowed_directories
    print("\n[1/7] Testing list_allowed_directories...")
    try:
        result = bridge.call_filesystem_tool("list_allowed_directories", {})
        print(f"Result keys: {result.keys()}")
        if result.get("success"):
            dirs = result.get("directories", [])
            print(f"OK - list_allowed_directories successful - {len(dirs)} allowed directories")
        else:
            print(f"WARN - list_allowed_directories failed: {result.get('error')}")
    except Exception as e:
        print(f"ERROR - list_allowed_directories exception: {e}")

    # Test 2: create_directory
    print("\n[2/7] Testing create_directory...")
    test_subdir = test_dir / "subdir"
    try:
        result = bridge.call_filesystem_tool("create_directory", {
            "path": str(test_subdir)
        })
        print(f"Result: {result}")
        if result.get("success"):
            print(f"OK - create_directory successful")
        else:
            print(f"WARN - create_directory failed: {result.get('error')}")
    except Exception as e:
        print(f"ERROR - create_directory exception: {e}")

    # Test 3: write_file
    print("\n[3/7] Testing write_file...")
    test_file = test_dir / "test_file.txt"
    try:
        result = bridge.call_filesystem_tool("write_file", {
            "path": str(test_file),
            "content": "Story 1.3 filesystem validation test"
        })
        print(f"Result: {result}")
        if result.get("success"):
            print(f"OK - write_file successful")
        else:
            print(f"WARN - write_file failed: {result.get('error')}")
    except Exception as e:
        print(f"ERROR - write_file exception: {e}")

    # Test 4: read_file
    print("\n[4/7] Testing read_file...")
    try:
        result = bridge.call_filesystem_tool("read_file", {
            "path": str(test_file)
        })
        print(f"Result keys: {result.keys() if isinstance(result, dict) else 'not dict'}")
        if result.get("success"):
            content = result.get("content", "")
            print(f"OK - read_file successful - content length: {len(content)}")
        else:
            print(f"WARN - read_file failed: {result.get('error')}")
    except Exception as e:
        print(f"ERROR - read_file exception: {e}")

    # Test 5: list_directory
    print("\n[5/7] Testing list_directory...")
    try:
        result = bridge.call_filesystem_tool("list_directory", {
            "path": str(test_dir)
        })
        print(f"Result keys: {result.keys() if isinstance(result, dict) else 'not dict'}")
        if result.get("success"):
            entries = result.get("entries", [])
            print(f"OK - list_directory successful - {len(entries)} entries")
        else:
            print(f"WARN - list_directory failed: {result.get('error')}")
    except Exception as e:
        print(f"ERROR - list_directory exception: {e}")

    # Test 6: get_file_info
    print("\n[6/7] Testing get_file_info...")
    try:
        result = bridge.call_filesystem_tool("get_file_info", {
            "path": str(test_file)
        })
        print(f"Result keys: {result.keys() if isinstance(result, dict) else 'not dict'}")
        if result.get("success"):
            info = result.get("info", {})
            print(f"OK - get_file_info successful - size: {info.get('size', 'unknown')} bytes")
        else:
            print(f"WARN - get_file_info failed: {result.get('error')}")
    except Exception as e:
        print(f"ERROR - get_file_info exception: {e}")

    # Test 7: search_files
    print("\n[7/7] Testing search_files...")
    try:
        result = bridge.call_filesystem_tool("search_files", {
            "path": str(test_dir),
            "pattern": "*.txt"
        })
        print(f"Result keys: {result.keys() if isinstance(result, dict) else 'not dict'}")
        if result.get("success"):
            matches = result.get("matches", [])
            print(f"OK - search_files successful - {len(matches)} matches")
        else:
            print(f"WARN - search_files failed: {result.get('error')}")
    except Exception as e:
        print(f"ERROR - search_files exception: {e}")

    # Cleanup
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)

    print("\n" + "="*80)
    print("FILESYSTEM TOOLS TEST COMPLETE")
    print("="*80)


def test_obsidian_tools():
    """Test all Obsidian MCP tools"""
    print("\n" + "="*80)
    print("TESTING OBSIDIAN MCP TOOLS")
    print("="*80)

    bridge = MCPBridge()

    # Test 1: list_files_in_vault
    print("\n[1/3] Testing list_files_in_vault...")
    try:
        result = bridge.call_obsidian_tool("list_files_in_vault", {})
        print(f"Result keys: {result.keys() if isinstance(result, dict) else 'not dict'}")
        if result.get("success"):
            files = result.get("files", [])
            print(f"OK - list_files_in_vault successful - {len(files)} files")
        else:
            print(f"WARN - list_files_in_vault failed: {result.get('error')}")
            print("(Obsidian may not be running or REST API plugin not configured)")
            return  # Skip remaining tests
    except Exception as e:
        print(f"ERROR - list_files_in_vault exception: {e}")
        print("(Obsidian may not be running or REST API plugin not configured)")
        return  # Skip remaining tests

    # Test 2: search
    print("\n[2/3] Testing search...")
    try:
        result = bridge.call_obsidian_tool("search", {
            "query": "test"
        })
        print(f"Result keys: {result.keys() if isinstance(result, dict) else 'not dict'}")
        if result.get("success"):
            results = result.get("results", [])
            print(f"OK - search successful - {len(results)} results")
        else:
            print(f"WARN - search failed: {result.get('error')}")
    except Exception as e:
        print(f"ERROR - search exception: {e}")

    # Test 3: get_file_contents (only if vault has files)
    print("\n[3/3] Testing get_file_contents...")
    try:
        # Try to get first file from vault
        result = bridge.call_obsidian_tool("list_files_in_vault", {})
        if result.get("success") and result.get("files"):
            first_file = result.get("files")[0]
            result = bridge.call_obsidian_tool("get_file_contents", {
                "file_path": first_file
            })
            print(f"Result keys: {result.keys() if isinstance(result, dict) else 'not dict'}")
            if result.get("success"):
                content = result.get("content", "")
                print(f"OK - get_file_contents successful - content length: {len(content)}")
            else:
                print(f"WARN - get_file_contents failed: {result.get('error')}")
        else:
            print("SKIP - No files in vault to test get_file_contents")
    except Exception as e:
        print(f"ERROR - get_file_contents exception: {e}")

    print("\n" + "="*80)
    print("OBSIDIAN TOOLS TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    print("\n" + "="*80)
    print("STORY 1.3 MCP TOOLS TEST (OBSIDIAN + FILESYSTEM)")
    print("Testing direct mcp_bridge helper methods")
    print("Skipping Graphiti due to Windows neo4j compatibility")
    print("="*80)

    try:
        # Test Filesystem tools
        test_filesystem_tools()

        # Test Obsidian tools
        test_obsidian_tools()

        print("\n" + "="*80)
        print("ALL TESTS COMPLETE")
        print("="*80)

    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
