# Story 1.3: Architecture Refactoring Complete

**Date**: 2025-10-01
**Status**: Core implementation complete, tests require updates
**Architecture Pattern**: Story 1.2 (Direct mcp_bridge calls)

## Summary

Story 1.3 has been refactored from client wrapper architecture to direct `mcp_bridge` helper method pattern, matching Story 1.2's AnalystAgent architecture.

## Changes Made

### 1. mcp_bridge.py - Added Three Helper Methods (✓ COMPLETE)

Following exact Story 1.2 pattern (`call_serena_tool`, `call_context7_tool`, `call_sequential_thinking_tool`):

```python
# Lines 645-722
def call_graphiti_tool(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]
async def _call_graphiti_tool_async(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]
def _parse_graphiti_result(tool_name: str, result: Any) -> Dict[str, Any]

# Lines 724-801
def call_obsidian_tool(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]
async def _call_obsidian_tool_async(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]
def _parse_obsidian_result(tool_name: str, result: Any) -> Dict[str, Any]

# Lines 803-877
def call_filesystem_tool(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]
async def _call_filesystem_tool_async(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]
def _parse_filesystem_result(tool_name: str, result: Any) -> Dict[str, Any]
```

**Pattern Details**:
- Sync wrapper → calls async implementation via `asyncio.run()`
- Async method → gets server config, creates temporary stdio session, calls MCP tool
- Parser → converts MCP TextContent to `{"success": True, ...}` dict format

### 2. KnowledgeAgent Refactoring (✓ COMPLETE)

**File**: `src/agents/knowledge_agent.py`

**Before** (Client Wrapper Pattern):
```python
from core.graphiti_client import GraphitiClient
from core.obsidian_client import ObsidianClient
from core.filesystem_client import FilesystemClient

def __init__(self):
    self.graphiti_client = GraphitiClient(mcp_bridge=self.mcp_bridge)
    self.obsidian_client = ObsidianClient(mcp_bridge=self.mcp_bridge)
    self.filesystem_client = FilesystemClient(mcp_bridge=self.mcp_bridge)

async def store_episode(self, content, episode_type, source, metadata):
    result = await self.graphiti_client.add_episode(...)
```

**After** (Story 1.2 Pattern):
```python
from core.mcp_bridge import MCPBridge

def __init__(self):
    self.mcp_bridge = MCPBridge()
    # No client instantiation

async def store_episode(self, content, episode_type, source, metadata):
    result = self.mcp_bridge.call_graphiti_tool("add_episode", {
        "content": content,
        "episode_type": episode_type,
        "source": source,
        "metadata": metadata or {}
    })
```

**Changes**:
- Removed imports: `GraphitiClient`, `ObsidianClient`, `FilesystemClient`
- Removed client instantiation in `__init__()`
- Updated `store_episode()` - direct `call_graphiti_tool()`
- Updated `search_knowledge()` - direct `call_graphiti_tool()` with tool name mapping
- Updated `create_documentation()` - direct `call_obsidian_tool()`
- Updated `search_documentation()` - direct `call_obsidian_tool()`
- Updated `query_filesystem()` - direct `call_filesystem_tool()`
- Updated `close()` - simplified (mcp_bridge manages own connections)

### 3. Client Wrapper Classes Deprecated (✓ COMPLETE)

**Moved to**: `src/core/deprecated/`

- `graphiti_client.py` → `src/core/deprecated/graphiti_client.py`
- `obsidian_client.py` → `src/core/deprecated/obsidian_client.py`
- `filesystem_client.py` → `src/core/deprecated/filesystem_client.py`
- Added `src/core/deprecated/README.md` with deprecation rationale and migration guide

### 4. Test Fixtures Updated (✓ PARTIAL)

**File**: `tests/conftest.py`

**Changes**:
- Removed imports: `GraphitiClient`, `ObsidianClient`, `FilesystemClient`
- Replaced `real_graphiti_client` fixture → `mcp_bridge_instance` fixture
- Removed `real_obsidian_client` and `real_filesystem_client` fixtures
- Updated `real_knowledge_agent` fixture to use `mcp_bridge_instance`

**Remaining Work**: Individual test files still reference old fixtures

### 5. Test Files Requiring Updates (⚠️ IN PROGRESS)

**Partially Updated**:
- `tests/test_story_1_3_real_knowledge_agent.py` - Main agent test updated
- `tests/test_story_1_3_real_graphiti.py` - First 3 tests updated

**Need Full Refactoring**:
- `tests/test_story_1_3_real_graphiti.py` - 11 remaining test methods
- `tests/test_story_1_3_real_obsidian.py` - All tests
- `tests/test_story_1_3_real_filesystem.py` - All tests
- `tests/test_story_1_3_knowledge_agent.py` - Mock-based tests (may be obsolete)

**Pattern to Follow**:
```python
# OLD
async def test_add_episode(real_graphiti_client):
    result = await real_graphiti_client.add_episode(...)

# NEW
async def test_add_episode(mcp_bridge_instance):
    result = mcp_bridge_instance.call_graphiti_tool("add_episode", {...})
```

## Architecture Comparison

| Aspect | OLD (Client Wrapper) | NEW (Story 1.2 Pattern) |
|--------|---------------------|------------------------|
| **Imports** | GraphitiClient, ObsidianClient, FilesystemClient | MCPBridge only |
| **Agent Init** | Instantiate 3 client objects | Single mcp_bridge |
| **Method Calls** | `await self.graphiti_client.add_episode(...)` | `self.mcp_bridge.call_graphiti_tool("add_episode", {...})` |
| **Layers** | Agent → Client → mcp_bridge → MCP | Agent → mcp_bridge → MCP |
| **Tests** | Mock/real client fixtures | mcp_bridge_instance fixture |
| **Consistency** | Different from Story 1.2 | Matches Story 1.2 exactly |

## Benefits of New Architecture

1. **Consistency**: Matches Story 1.2 (AnalystAgent) pattern exactly
2. **Simplicity**: Removes unnecessary client wrapper layer
3. **Maintainability**: Single point of MCP integration (mcp_bridge.py)
4. **Testability**: Direct testing of mcp_bridge helper methods
5. **Performance**: One less indirection layer

## Files Status

| File | Status | Notes |
|------|--------|-------|
| `src/core/mcp_bridge.py` | ✓ Complete | 3 helper methods added |
| `src/agents/knowledge_agent.py` | ✓ Complete | All methods refactored |
| `src/core/deprecated/*` | ✓ Complete | Client wrappers moved |
| `tests/conftest.py` | ✓ Complete | Fixtures updated |
| `tests/test_story_1_3_real_knowledge_agent.py` | ⚠️ Partial | 1/8 tests updated |
| `tests/test_story_1_3_real_graphiti.py` | ⚠️ Partial | 3/16 tests updated |
| `tests/test_story_1_3_real_obsidian.py` | ⚠️ Pending | Not started |
| `tests/test_story_1_3_real_filesystem.py` | ⚠️ Pending | Not started |

## Next Steps

1. **Update Remaining Test Methods** (⚠️ IN PROGRESS):
   - Systematically update all test methods in 4 test files
   - Replace `real_graphiti_client` → `mcp_bridge_instance.call_graphiti_tool()`
   - Replace `real_obsidian_client` → `mcp_bridge_instance.call_obsidian_tool()`
   - Replace `real_filesystem_client` → `mcp_bridge_instance.call_filesystem_tool()`

2. **Run Tests**:
   ```bash
   pytest tests/test_story_1_3_*.py -v
   ```

3. **Update Documentation**:
   - `docs/stories/epic-1/story-1-3-graphiti-mcp-obsidian-filesystem.md`
   - Architecture diagrams showing new pattern
   - Update acceptance criteria notes

4. **Remove Experimental Files** (Optional):
   - `experimental/demo_obsidian_mcp_client.py` uses deprecated clients
   - `experimental/demo_story_1_3_mcp.py` uses deprecated clients
   - Either update or remove these demos

## Technical Notes

### MCP Server Configuration

Both `direct_mcp_servers` and `wrapped_mcp_servers` are used:

```python
# mcp_bridge.py
self.direct_mcp_servers = {
    "graphiti": {  # Direct Python MCP SDK
        "command": "python",
        "args": ["-m", "graphiti_mcp"],
        "type": "direct"
    }
}

self.wrapped_mcp_servers = {
    "obsidian": {  # Via mcp-use wrapper
        "command": "node",
        "args": ["mcp-use/mapping_mcp_bridge.js"],
        "type": "wrapped"
    },
    "filesystem": {  # Via mcp-use wrapper
        "command": "node",
        "args": ["mcp-use/mapping_mcp_bridge.js"],
        "type": "wrapped"
    }
}
```

### Helper Method Signature

All three helpers follow identical pattern:

```python
def call_<server>_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Sync wrapper"""
    return asyncio.run(self._call_<server>_tool_async(tool_name, parameters))

async def _call_<server>_tool_async(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Async implementation"""
    server_config = self.<server_type>_mcp_servers.get("<server>")
    async with self._get_stdio_session(server_config) as session:
        result = await session.call_tool(tool_name, parameters)
        return self._parse_<server>_result(tool_name, result.content)

def _parse_<server>_result(self, tool_name: str, result: Any) -> Dict[str, Any]:
    """Parser for TextContent → dict"""
    # Extract data from TextContent objects
    return {"success": True, **result_data}
```

## References

- **Story 1.2**: `docs/stories/epic-1/story-1-2-serena-mcp-context7-sequential-thinking.md`
- **AnalystAgent**: `src/agents/analyst_agent.py` (reference implementation)
- **Architecture Docs**: `docs/architecture/2-high-level-architecture.md`
- **Tech Stack**: `docs/architecture/3-tech-stack.md`

---

**Refactoring Lead**: Claude (Sonnet 4.5)
**Pattern Source**: Story 1.2 (AnalystAgent)
**Completion**: Core implementation 100%, Tests ~20%
