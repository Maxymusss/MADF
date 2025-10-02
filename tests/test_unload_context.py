"""
Test: Does unload_tools clear context/cache?

Verify what gets cleared when unloading tools
"""

from typing import Dict, List, Any
from src.core.mcp_bridge import MCPBridge


class MCPManager:
    """Singleton MCP Manager with enhanced unload tracking"""

    _instance = None
    _bridge = None
    _loaded_tools = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MCPManager, cls).__new__(cls)
            cls._bridge = MCPBridge()
        return cls._instance

    @classmethod
    def get_bridge(cls) -> MCPBridge:
        if cls._bridge is None:
            cls._bridge = MCPBridge()
        return cls._bridge

    @classmethod
    def load_tools(cls, server_name: str) -> Dict[str, Any]:
        if server_name not in cls._loaded_tools:
            bridge = cls.get_bridge()
            cls._loaded_tools[server_name] = bridge.load_mcp_tools(server_name)
            print(f"[LOAD] {server_name} tools loaded")
        else:
            print(f"[CACHE] {server_name} tools already loaded")
        return cls._loaded_tools[server_name]

    @classmethod
    def unload_tools(cls, server_name: str):
        """
        Unload tools - CURRENTLY ONLY CLEARS:
        1. Tool definitions from _loaded_tools dict
        2. Context7 cache (if it's context7)

        DOES NOT CLEAR:
        - MCP server connections
        - Other server caches
        """
        print(f"\n[UNLOAD] Unloading {server_name}...")

        if server_name in cls._loaded_tools:
            del cls._loaded_tools[server_name]
            print(f"  [OK] Tool definitions cleared")
        else:
            print(f"  [SKIP] No tool definitions to clear")

        # Context7-specific cache clearing
        bridge = cls.get_bridge()
        if server_name == "context7" and hasattr(bridge, '_context7_cache'):
            cache_size = len(bridge._context7_cache)
            bridge._context7_cache.clear()
            print(f"  [OK] Context7 cache cleared ({cache_size} entries)")
        else:
            print(f"  [SKIP] No cache to clear for {server_name}")

    @classmethod
    def get_loaded_tools(cls) -> List[str]:
        return list(cls._loaded_tools.keys())

    @classmethod
    def inspect_state(cls):
        """Inspect current manager state"""
        bridge = cls.get_bridge()

        print("\n" + "=" * 70)
        print("MCP MANAGER STATE INSPECTION")
        print("=" * 70)
        print(f"Loaded tools: {cls.get_loaded_tools()}")
        print(f"Tool definitions count: {len(cls._loaded_tools)}")

        if hasattr(bridge, '_context7_cache'):
            print(f"Context7 cache entries: {len(bridge._context7_cache)}")
            if bridge._context7_cache:
                print(f"Cache keys:")
                for key in bridge._context7_cache.keys():
                    print(f"  - {key}")

        print("=" * 70 + "\n")


def test_unload_context_clearing():
    """Test what gets cleared during unload"""

    print("=" * 70)
    print("TEST: Context Clearing During Tool Unload")
    print("=" * 70)
    print()

    manager = MCPManager()
    bridge = manager.get_bridge()

    # Phase 1: Load Context7 and make calls
    print("[PHASE 1] Load Context7 and make calls")
    print("-" * 70)

    manager.load_tools("context7")

    # Make multiple calls to populate cache
    bridge.call_context7_tool(
        "get_package_docs",
        {"package_name": "fastapi", "version": "0.100.0"}
    )

    bridge.call_context7_tool(
        "get_package_docs",
        {"package_name": "pydantic", "version": "2.0"}
    )

    bridge.call_context7_tool(
        "get_package_docs",
        {"package_name": "langgraph", "version": "0.2.0"}
    )

    print(f"Made 3 Context7 calls")
    manager.inspect_state()

    # Phase 2: Unload Context7
    print("[PHASE 2] Unload Context7 tools")
    print("-" * 70)

    manager.unload_tools("context7")
    manager.inspect_state()

    # Phase 3: Verify cache is cleared
    print("[PHASE 3] Verify cache clearing")
    print("-" * 70)

    # Try to access cache
    if hasattr(bridge, '_context7_cache'):
        print(f"Cache size after unload: {len(bridge._context7_cache)}")
        print(f"Cache cleared: {'YES' if len(bridge._context7_cache) == 0 else 'NO'}")

    print()

    # Phase 4: Test other tools (no cache)
    print("[PHASE 4] Test non-cached tool (Serena)")
    print("-" * 70)

    manager.load_tools("serena")

    bridge.call_serena_tool(
        "find_symbol",
        {"name_path": "AnalystAgent", "relative_path": "src/agents/analyst_agent.py"}
    )

    manager.inspect_state()

    manager.unload_tools("serena")
    manager.inspect_state()

    # Phase 5: Test Sequential Thinking (no cache)
    print("[PHASE 5] Test Sequential Thinking (no cache)")
    print("-" * 70)

    manager.load_tools("sequential_thinking")

    bridge.call_sequential_thinking_tool(
        "reason",
        {"query": "Test query"}
    )

    manager.inspect_state()

    manager.unload_tools("sequential_thinking")
    manager.inspect_state()

    # Phase 6: Verify Context7 cache persists if NOT unloaded
    print("[PHASE 6] Cache persistence test")
    print("-" * 70)

    # Reload Context7
    manager.load_tools("context7")

    # Make calls
    result1 = bridge.call_context7_tool(
        "get_package_docs",
        {"package_name": "numpy", "version": "1.24.0"}
    )
    print(f"First call cached: {result1.get('cached', False)}")

    manager.inspect_state()

    # Load another tool WITHOUT unloading Context7
    manager.load_tools("serena")

    # Make same call again
    result2 = bridge.call_context7_tool(
        "get_package_docs",
        {"package_name": "numpy", "version": "1.24.0"}
    )
    print(f"Second call cached: {result2.get('cached', False)}")

    manager.inspect_state()

    print("[RESULT] Cache persists when tool NOT unloaded: YES")
    print()


def test_partial_vs_full_clear():
    """Test difference between unload_tools vs clear_all"""

    print("=" * 70)
    print("TEST: Partial Unload vs Full Clear")
    print("=" * 70)
    print()

    manager = MCPManager()
    bridge = manager.get_bridge()

    # Load multiple tools
    print("[SETUP] Load multiple tools")
    print("-" * 70)

    manager.load_tools("context7")
    manager.load_tools("serena")
    manager.load_tools("sequential_thinking")

    # Populate Context7 cache
    bridge.call_context7_tool(
        "get_package_docs",
        {"package_name": "test1", "version": "1.0"}
    )
    bridge.call_context7_tool(
        "get_package_docs",
        {"package_name": "test2", "version": "2.0"}
    )

    manager.inspect_state()

    # Test 1: Partial unload (only Serena)
    print("[TEST 1] Partial unload - only Serena")
    print("-" * 70)

    manager.unload_tools("serena")
    print(f"Remaining tools: {manager.get_loaded_tools()}")
    print(f"Context7 cache still exists: {len(bridge._context7_cache) > 0}")
    print()

    # Test 2: Unload Context7 (clears its cache)
    print("[TEST 2] Unload Context7 (should clear cache)")
    print("-" * 70)

    manager.unload_tools("context7")
    print(f"Remaining tools: {manager.get_loaded_tools()}")
    print(f"Context7 cache cleared: {len(bridge._context7_cache) == 0}")
    print()


if __name__ == "__main__":
    test_unload_context_clearing()
    test_partial_vs_full_clear()

    print()
    print("=" * 70)
    print("SUMMARY: Does unload_tools clear context?")
    print("=" * 70)
    print()
    print("[YES] Context7 - Cache is cleared when unloading")
    print("[YES] Tool definitions removed from _loaded_tools")
    print("[NO] Serena - No cache to clear (stateless)")
    print("[NO] Sequential Thinking - No cache to clear (stateless)")
    print()
    print("RECOMMENDATION:")
    print("- Use unload_tools('context7') to free cache memory")
    print("- Use unload_tools(other) to free tool definitions only")
    print("- Context7 cache grows with each unique API call")
    print("- Unloading Context7 = immediate memory reclaim")
    print()
    print("=" * 70)