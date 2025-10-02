# ADR-001: Direct Library Integration Priority Over MCP Bridge

**Date**: 2025-10-01
**Status**: Accepted
**Context**: Epic 1 Stories 1.3 and 1.4 implementation

## Decision

**Prioritize direct Python library integration over MCP bridge wrappers for all tools where native Python libraries exist.**

## Context

During Story 1.3 (Graphiti + Obsidian + Filesystem) and Story 1.4 (DSPy + Sentry + Postgres) implementation, we tested both MCP bridge and direct library approaches and measured significant performance differences.

### Performance Comparison

**Story 1.3 Findings**:
- Direct `graphiti_core` library: **3x faster** than MCP wrapper
- Full API access (not limited to MCP-exposed tools)
- Type safety with IDE autocomplete
- Zero subprocess overhead

**Story 1.4 Implementation**:
- Direct `sentry-sdk`: Real-time error tracking with full SDK features
- Direct `psycopg3`: High-performance SQL operations, synchronous for Windows compatibility
- Direct `dspy`: Native framework integration with full optimizer access

### Original PRD Specification

PRD initially specified MCP-use wrappers for all tools:
- Story 1.3: Graphiti via MCP
- Story 1.4: Sentry/Postgres via MCP

### Implementation Reality

Dev agents chose direct libraries based on performance testing, creating a gap between PRD and implementation.

## Decision Criteria

Use **Direct Library Integration** when:
1. Native Python library available (PyPI, conda-forge, direct install)
2. Performance-critical operations (database queries, graph operations, error tracking)
3. Full API access required (beyond MCP-exposed subset)
4. Type safety important for developer experience
5. Frequent operation calls (high overhead from subprocess invocation)

Use **MCP Bridge Integration** when:
1. External service without native Python library (GitHub API, Tavily search)
2. Node.js-only server implementation (Chrome DevTools Protocol)
3. Cross-language integration required
4. Dynamic tool discovery beneficial
5. Infrequent operation calls (low overhead impact)

## Implementation Pattern

### Direct Library Pattern (PRIMARY)

```python
# Import native Python library
from graphiti_core import Graphiti
from sentry_sdk import init as sentry_init
import psycopg

# Instantiate and use directly
graphiti = Graphiti(uri=neo4j_uri, user=user, password=password)
result = await graphiti.add_episode(content=content, episode_type="code_change")

# Full type safety
sentry_init(dsn=dsn, traces_sample_rate=1.0)
conn = psycopg.connect(connection_string)
```

**Benefits**:
- 3x performance improvement
- Full API access
- Type hints and IDE autocomplete
- No subprocess overhead
- Direct error handling

### MCP Bridge Pattern (SECONDARY)

```python
# Use MCP bridge for external services
import subprocess
import json

result = subprocess.run([
    'node', 'mcp-use/mapping_mcp_bridge.js',
    json.dumps(["github", "create_pull_request", {
        "title": "Feature X",
        "body": "Implementation details"
    }])
], capture_output=True, text=True)
```

**Use cases**:
- GitHub repository operations (external API)
- Tavily web search (external service)
- Chrome DevTools (Node.js CDP library)
- Context7/Sequential Thinking (Node.js servers)
- Obsidian/Filesystem (utility operations)

## Consequences

### Positive

1. **Performance**: 3x faster for performance-critical operations
2. **Type Safety**: Full IDE support with autocomplete and type checking
3. **API Access**: Not limited to MCP-exposed tool subset
4. **Reliability**: Direct Python error handling, no subprocess failures
5. **Developer Experience**: Standard Python patterns, easier debugging

### Negative

1. **Dependency Management**: More Python dependencies to maintain
2. **Documentation Gap**: PRD specifications need updates to match reality
3. **Mixed Patterns**: Two integration approaches to understand
4. **Platform Constraints**: Some libraries have Windows compatibility issues (async psycopg)

### Neutral

1. **MCP Still Valuable**: External services require MCP bridge
2. **Hybrid Architecture**: Both patterns coexist based on use case
3. **Optional MCP Helpers**: Can add MCP wrappers for advanced features

## Updated Architecture

### Story 1.3: Graphiti + Obsidian + Filesystem
- **Graphiti**: Direct `graphiti_core` library ✓ (3x performance)
- **Obsidian**: MCP bridge ✓ (external Node.js server)
- **Filesystem**: MCP bridge ✓ (utility operations)

### Story 1.4: DSPy + Sentry + Postgres
- **DSPy**: Direct Python library ✓ (native framework)
- **Sentry**: Direct `sentry-sdk` library ✓ (real-time tracking)
- **Postgres**: Direct `psycopg3` library ✓ (high-performance SQL)

### Story 1.5: GitHub + Tavily
- **GitHub**: MCP bridge ✓ (external GitHub API)
- **Tavily**: MCP bridge ✓ (external search service)

### Story 1.6: Chrome DevTools
- **Chrome DevTools**: MCP bridge ✓ (Node.js CDP library)

## Related Documents

- [CLAUDE.md](../../CLAUDE.md) - Updated with integration architecture priority
- [Story 1.3](../stories/epic-1/story-1-3-graphiti-mcp-obsidian-filesystem.md) - Graphiti direct library pattern
- [Story 1.4](../stories/epic-1/story-1-4-dspy-sentry-postgres-integration.md) - DSPy/Sentry/Postgres direct library pattern
- [PRD Epic 1](../PRD/5-epic-1-multiagent-coding-framework-foundation.md) - Updated acceptance criteria
- [STORY_1_3_ARCHITECTURE_REFACTORING_COMPLETE.md](../../STORY_1_3_ARCHITECTURE_REFACTORING_COMPLETE.md) - Story 1.3 pattern details

## Decision Authority

This ADR documents the architectural pattern established during Stories 1.3 and 1.4 implementation based on performance testing and developer experience optimization. The pattern is now codified for future stories.

## Review and Updates

This ADR should be reviewed when:
- New MCP servers become available with improved performance
- Direct Python libraries become unavailable or unsupported
- Cross-language integration requirements change
- Performance characteristics of MCP-use improve significantly
