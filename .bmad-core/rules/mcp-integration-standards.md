# MCP Integration Standards for MADF

**Version**: 2.0 (Updated 2025-10-01)
**Authority**: MANDATORY for all MCP client implementations

## Critical MCP Architecture Rules

### Python MCP SDK Pattern (PRIMARY)

**ABSOLUTE RULE**: Use `src/core/mcp_bridge.py` MCPBridge class for ALL MCP tool integrations.

### Integration Approach

**ALL MCP Tools**: Python MCP SDK via MCPBridge
- **File**: `src/core/mcp_bridge.py`
- **Method**: `await mcp_bridge.call_mcp_tool(server_name, tool_name, parameters)`
- **Servers**: Serena, Graphiti, Context7, Sequential Thinking, GitHub, Tavily, Obsidian, Filesystem, Chrome DevTools, Sentry, Postgres
- **Transport**: stdio via Python MCP SDK
- **Session Management**: Persistent sessions for performance
- **Usage**:
  ```python
  from core.mcp_bridge import MCPBridge

  class MyClient:
      def __init__(self, mcp_bridge: Optional[MCPBridge] = None):
          self.mcp_bridge = mcp_bridge or MCPBridge()

      async def my_operation(self, param: str) -> Dict[str, Any]:
          result = await self.mcp_bridge.call_mcp_tool(
              server_name="filesystem",
              tool_name="read_text_file",
              parameters={"path": param}
          )

          if result.get("success"):
              return result["result"]
          else:
              return {"error": result.get("error")}
  ```

**Server-Specific Helpers** (optional convenience methods):
- `mcp_bridge.call_serena_tool(tool_name, parameters)` - Serena semantic search
- `mcp_bridge.call_context7_tool(tool_name, parameters)` - Context7 documentation
- `mcp_bridge.call_sequential_thinking_tool(tool_name, parameters)` - Sequential reasoning

## Configuration

### MCP Server Registration

**File**: `src/core/mcp_bridge.py`

All MCP servers configured in MCPBridge class:
- `direct_mcp_servers`: Performance-critical (Serena, Graphiti, Context7, Sequential Thinking)
- `wrapped_mcp_servers`: General tools (GitHub, Tavily, Obsidian, Filesystem, Chrome DevTools, Sentry, Postgres)

Both use stdio transport via Python MCP SDK.

### Environment Variables

Set required API keys and credentials:
```bash
# Neo4j (for Graphiti)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# OpenAI (for Graphiti embeddings, Context7)
OPENAI_API_KEY=sk-...

# Other services
OBSIDIAN_API_KEY=your_key
GITHUB_TOKEN=ghp_...
TAVILY_API_KEY=tvly-...
POSTGRES_CONNECTION_STRING=postgresql://...
```

## Agent Tool Assignments

### By Agent
| Agent | MCP Tools (all via mcp_bridge.py) |
|-------|----------------------------------|
| Orchestrator | GitHub, Tavily, Filesystem |
| Analyst | Serena, Context7, Sequential Thinking |
| Knowledge | Graphiti, Obsidian, Filesystem |
| Developer | Chrome DevTools, Filesystem |
| Validator | DSPy, Sentry, Postgres |

### Tool Boundaries
- **Serena**: Analyst ONLY (no other agents)
- **Graphiti**: Knowledge ONLY (no other agents)
- **Filesystem**: Shared (Orchestrator, Knowledge, Developer)
- All tools accessed via `mcp_bridge.call_mcp_tool()` or server-specific helpers

## Testing Requirements

### Real MCP Integration Tests
**CRITICAL**: NO MOCKS - All tests use real MCP connections

```python
# tests/test_story_1_2_real_analyst_agent.py
async def test_serena_find_symbol_real():
    """Test real Serena MCP connection via direct Python SDK"""
    # Uses actual Serena MCP server, not mocks

async def test_context7_resolve_library_real():
    """Test real Context7 via mapping_mcp_bridge.js"""
    # Calls actual bridge subprocess, not mocks
```

### Test Environment
```bash
# .env.test
NEO4J_TEST_URI=bolt://localhost:7687  # For Graphiti
OPENAI_API_KEY=sk-...                 # For Context7
TAVILY_API_KEY=tvly-...               # For Tavily
GITHUB_TOKEN=ghp_...                  # For GitHub
POSTGRES_CONNECTION_STRING=postgresql://... # For Postgres MCP Pro
```

## Implementation Patterns

### Pattern 1: Client with MCP Bridge Integration ✅

```python
from core.mcp_bridge import MCPBridge
from typing import Optional, Dict, Any

class FilesystemClient:
    """Client for filesystem operations via MCP bridge"""

    def __init__(self, mcp_bridge: Optional[MCPBridge] = None):
        self.mcp_bridge = mcp_bridge or MCPBridge()
        self._initialized = False

    async def read_file(self, path: str) -> Dict[str, Any]:
        """Read file via filesystem MCP server"""
        if not self._initialized:
            await self.initialize()

        result = await self.mcp_bridge.call_mcp_tool(
            server_name="filesystem",
            tool_name="read_text_file",
            parameters={"path": path}
        )

        if result.get("success"):
            # Parse MCP result (TextContent objects)
            mcp_result = result.get("result", {})
            return self._parse_mcp_result(mcp_result)
        else:
            return {"error": result.get("error")}
```

### Pattern 2: Agent with Shared MCP Bridge ✅

```python
from core.mcp_bridge import MCPBridge
from core.graphiti_client import GraphitiClient
from core.filesystem_client import FilesystemClient

class KnowledgeAgent(BaseAgent):
    def __init__(self):
        super().__init__("Knowledge", "Knowledge Management")

        # Create single MCPBridge instance
        self.mcp_bridge = MCPBridge()

        # Share with all clients
        self.graphiti_client = GraphitiClient(mcp_bridge=self.mcp_bridge)
        self.filesystem_client = FilesystemClient(mcp_bridge=self.mcp_bridge)
```

## Prohibited Practices

### ❌ DO NOT
- Use direct library imports (e.g., `from graphiti_core import Graphiti`)
- Make direct REST API calls (e.g., `aiohttp.ClientSession().get()`)
- Use subprocess calls to MCP servers directly (use mcp_bridge.py)
- Create mock implementations with hardcoded returns
- Use mocks in MCP integration tests

### ✅ DO
- Use `mcp_bridge.call_mcp_tool()` for ALL MCP operations
- Share single MCPBridge instance across clients in same agent
- Write real integration tests with actual MCP servers
- Follow agent tool boundaries strictly
- Parse MCP TextContent objects correctly

## Architecture References

- **MCP Bridge**: [src/core/mcp_bridge.py](../../src/core/mcp_bridge.py)
- **Architecture**: [docs/architecture/2-high-level-architecture.md](../../docs/architecture/2-high-level-architecture.md)
- **Tech Stack**: [docs/architecture/3-tech-stack.md](../../docs/architecture/3-tech-stack.md)
- **Story 1.3 Refactoring**: [docs/stories/epic-1/STORY_1_3_REFACTORING_REQUIRED.md](../../docs/stories/epic-1/STORY_1_3_REFACTORING_REQUIRED.md)
- **Phase 1 Complete**: [docs/stories/epic-1/STORY_1_3_PHASE_1_COMPLETE.md](../../docs/stories/epic-1/STORY_1_3_PHASE_1_COMPLETE.md)

## Reference Implementations

### ✅ Correct (MCP Bridge Integration)
- **FilesystemClient**: [src/core/filesystem_client.py](../../src/core/filesystem_client.py) - Phase 1 complete
- **AnalystAgent**: [src/agents/analyst_agent.py](../../src/agents/analyst_agent.py) - Uses server-specific helpers

### ❌ Requires Refactoring
- **GraphitiClient**: [src/core/graphiti_client.py](../../src/core/graphiti_client.py) - Uses direct graphiti_core library
- **ObsidianClient**: [src/core/obsidian_client.py](../../src/core/obsidian_client.py) - Uses direct REST API

## Enforcement

- **Dev Agent**: Auto-loads this file during activation
- **Code Review**: Rejects MCP protocol bypassing
- **Testing**: Fails tests using mocks for MCP integration
- **CI/CD**: Validates MCP architecture compliance

---

**Last Updated**: 2025-10-01
**Version**: 2.0 (Python MCP SDK Primary)
**Status**: Active - Enforced in all Epic 1 development
