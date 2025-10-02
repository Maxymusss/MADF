# Deprecated Client Wrapper Classes

**Date Deprecated**: 2025-10-01

## Files
- `graphiti_client.py` - Graphiti MCP wrapper (replaced by mcp_bridge.call_graphiti_tool)
- `obsidian_client.py` - Obsidian MCP wrapper (replaced by mcp_bridge.call_obsidian_tool)
- `filesystem_client.py` - Filesystem MCP wrapper (replaced by mcp_bridge.call_filesystem_tool)

## Reason for Deprecation
Story 1.3 refactoring to follow Story 1.2 architectural pattern:
- Agents now call `mcp_bridge` helper methods **directly**
- No intermediate client wrapper layer needed
- Consistent with AnalystAgent pattern (Story 1.2)

## Migration Path
**OLD (Deprecated)**:
```python
self.graphiti_client = GraphitiClient(mcp_bridge=self.mcp_bridge)
result = await self.graphiti_client.add_episode(content, episode_type, source, metadata)
```

**NEW (Story 1.2 Pattern)**:
```python
# No client instantiation needed
result = self.mcp_bridge.call_graphiti_tool("add_episode", {
    "content": content,
    "episode_type": episode_type,
    "source": source,
    "metadata": metadata
})
```

## Impact
- **KnowledgeAgent**: Fully migrated to direct mcp_bridge calls
- **Tests**: Need updating to match new pattern
- **Documentation**: Story 1.3 docs updated to reflect architecture change

## Removal Timeline
These files can be safely deleted after:
1. All Story 1.3 tests pass with new pattern
2. Documentation fully updated
3. No remaining references in codebase
