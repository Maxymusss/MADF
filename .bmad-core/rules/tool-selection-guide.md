# Tool Selection Guide for LangGraph Agents

**Date**: 2025-10-02
**Research Basis**: Story 1.8 Tool Efficiency Research
**Source**: [Tool Recommendations](../../docs/research/tool-recommendations.md)
**Status**: v1.0 - Initial Release

---

## Purpose

This guide provides data-driven tool selection criteria for LangGraph agents based on empirical benchmarking from Story 1.8. Use this guide when implementing tool assignments in [src/agents/](../../src/agents/) files.

---

## Quick Decision Tree

```
START: Need to call a tool from LangGraph agent
  │
  ├─> Is there a direct Python library?
  │   └─> YES: Use direct library (3x faster)
  │       └─> Examples: graphiti_core, psycopg, dspy-ai, PyGithub
  │
  ├─> Is performance critical (<500ms required)?
  │   └─> YES: Use CLI tool if available
  │       └─> Example: gh CLI (25% faster than PyGithub)
  │
  ├─> Does MCP server exist?
  │   └─> YES: Use MCP for external services
  │       └─> Examples: Serena, Chrome DevTools, Obsidian
  │
  └─> Use Claude Code built-in tools
      └─> Examples: Read, Write, Edit, Glob, Grep
```

---

## Tool Priority Hierarchy

From Story 1.8 architecture and benchmarks:

### 1. Direct Python Library (HIGHEST PRIORITY)

**When to use:**
- ✅ Native Python async support available
- ✅ Performance-critical operations (3x faster than MCP per Story 1.3)
- ✅ Type safety required for complex workflows
- ✅ IDE autocomplete beneficial for development

**Examples:**
- `graphiti_core` - Knowledge graph operations (<10ms overhead)
- `psycopg` - Database operations (<50ms queries)
- `dspy-ai` - Self-improvement framework
- `PyGithub` - Complex GitHub workflows (688ms p50)
- `tavily-python` - Web research

**Performance Characteristics:**
- Latency: Lowest overhead, direct API calls
- Token cost: 50-100 tokens per call
- Reliability: High (native Python error handling)

---

### 2. CLI Tool (HIGH PRIORITY for latency-sensitive ops)

**When to use:**
- ✅ Latency-sensitive operations (<500ms required)
- ✅ Stable command interface (gh, git, npm)
- ✅ Human-readable output acceptable (JSON parsing)
- ✅ Benchmarks show faster than library alternative

**Examples:**
- `gh CLI` - GitHub operations (504ms p50, **25% faster than PyGithub**)
- `git` - Version control operations
- `npm` - Package management
- `docker` - Container operations

**Performance Characteristics:**
- Latency: Faster for specific operations (gh CLI: 504ms vs PyGithub: 688ms)
- Token cost: 100-200 tokens (command string + JSON parsing)
- Reliability: High (stable interfaces, exit codes)

**Trade-offs:**
- ❌ No type safety (JSON parsing required)
- ❌ Error handling via stderr parsing
- ❌ No IDE autocomplete

---

### 3. MCP Server (MEDIUM PRIORITY for external services)

**When to use:**
- ✅ No native Python library exists
- ✅ External service integration required
- ✅ Cross-language tool reuse needed
- ✅ Standardized tool interface beneficial

**Examples:**
- `Serena MCP` - Semantic code search (<500ms expected)
- `Chrome DevTools MCP` - Browser automation (<2s)
- `Obsidian MCP` - Note management (<1s)
- `Context7 MCP` - Documentation retrieval (<2s)
- `Sequential Thinking MCP` - Complex reasoning (3-10s)
- `Sentry MCP` - Error tracking (<100ms)

**Performance Characteristics:**
- Latency: Higher overhead (JSON-RPC protocol)
- Token cost: 200-300 tokens (protocol + params)
- Reliability: Depends on MCP server implementation

**Trade-offs:**
- ❌ ~3x slower than direct libraries (Story 1.3 finding)
- ❌ Protocol overhead
- ✅ Standardized interface across languages

---

### 4. Claude Code Built-in (BASELINE for basic operations)

**When to use:**
- ✅ File operations (read, write, edit)
- ✅ Code search (glob, grep)
- ✅ Web operations (WebSearch, WebFetch)
- ✅ Bash commands
- ✅ No specialized tool available

**Examples:**
- `Read` - File read (0.05ms p50 baseline)
- `Write` - File write (0.23ms p50 baseline)
- `Edit` - File edit (exact string matching)
- `Glob` - File search (314ms p50 for 1000+ files)
- `Grep` - Content search (regex)
- `Bash` - Shell commands

**Performance Characteristics:**
- Latency: Extremely fast for file ops (<1ms), moderate for search (~300ms)
- Token cost: Minimal (direct tool calls)
- Reliability: Very high (built-in, well-tested)

---

## Per-Agent Tool Assignments

Based on [Tool Recommendations](../../docs/research/tool-recommendations.md):

### Orchestrator Agent

**File**: [src/agents/orchestrator_agent.py](../../src/agents/orchestrator_agent.py)

| Operation | Recommended Tool | Priority | Expected Latency |
|-----------|------------------|----------|------------------|
| GitHub repo access | **gh CLI** | 1 (CLI) | 504ms p50 |
| GitHub complex ops | PyGithub | 2 (Library) | 688ms p50 |
| Web research | tavily-python | 2 (Library) | <1s |
| File read | Read (built-in) | 4 (Built-in) | 0.05ms |
| File write | Write (built-in) | 4 (Built-in) | 0.23ms |
| File search | Glob (built-in) | 4 (Built-in) | 314ms |

**Decision Logic:**
```python
# Latency-sensitive GitHub operations
if operation in ["get_repo", "list_issues", "search_repos"]:
    use_gh_cli()  # 25% faster
else:
    use_pygithub()  # Type-safe complex ops
```

---

### Analyst Agent

**File**: [src/agents/analyst_agent.py](../../src/agents/analyst_agent.py)

| Operation | Recommended Tool | Priority | Expected Latency |
|-----------|------------------|----------|------------------|
| Semantic code search | **Serena MCP** | 3 (MCP) | <500ms |
| Documentation | Context7 MCP | 3 (MCP) | <2s |
| Complex reasoning | Sequential Thinking MCP | 3 (MCP) | 3-10s |
| Simple regex search | Grep (built-in) | 4 (Built-in) | <100ms |

**Decision Logic:**
```python
# Semantic understanding vs regex
if need_semantic_context:
    use_serena_mcp()  # LSP-powered, context-aware
else:
    use_grep()  # Fast regex search
```

---

### Knowledge Agent

**File**: [src/agents/knowledge_agent.py](../../src/agents/knowledge_agent.py)

| Operation | Recommended Tool | Priority | Expected Latency |
|-----------|------------------|----------|------------------|
| Knowledge graph | **graphiti_core** | 1 (Library) | <10ms + Neo4j |
| Note management | Obsidian MCP | 3 (MCP) | <1s |
| File storage | Filesystem MCP | 3 (MCP) | Similar to built-in |
| Documentation | Context7 MCP | 3 (MCP) | <2s |

**Decision Logic:**
```python
# ALWAYS use direct library for Graphiti (3x faster)
if operation in ["add_episode", "search", "graph_query"]:
    use_graphiti_core()  # Direct library, NOT MCP
elif need_structured_notes:
    use_obsidian_mcp()  # Backlinks, tags
else:
    use_filesystem_mcp()  # Simple file storage
```

**CRITICAL**: Never use Graphiti MCP (3x slower per Story 1.3)

---

### Developer Agent

**File**: [src/agents/developer_agent.py](../../src/agents/developer_agent.py)

| Operation | Recommended Tool | Priority | Expected Latency |
|-----------|------------------|----------|------------------|
| Browser automation | **Chrome DevTools MCP** | 3 (MCP) | <2s |
| Code generation | Write (built-in) | 4 (Built-in) | 0.23ms |
| Code editing | Edit (built-in) | 4 (Built-in) | <1ms |
| File reading | Read (built-in) | 4 (Built-in) | 0.05ms |

**Decision Logic:**
```python
# Code generation workflow
if creating_new_file:
    use_write()  # Fast, direct
elif modifying_existing:
    use_edit()  # Exact string matching
else:
    use_read()  # Verify changes
```

---

### Validator Agent

**File**: [src/agents/validator_agent.py](../../src/agents/validator_agent.py)

| Operation | Recommended Tool | Priority | Expected Latency |
|-----------|------------------|----------|------------------|
| Database queries | **psycopg** | 1 (Library) | <50ms |
| Error tracking | Sentry MCP | 3 (MCP) | <100ms |
| Self-improvement | dspy-ai | 1 (Library) | 10-60s |
| Query analysis | Postgres MCP Pro | 3 (MCP) | <1s |

**Decision Logic:**
```python
# Performance-critical DB operations
if operation in ["execute", "fetchone", "executemany"]:
    use_psycopg()  # Direct library, fast
elif need_query_analysis:
    use_postgres_mcp_pro()  # EXPLAIN plans, schema
```

---

## Performance Benchmarks Reference

From Story 1.8 empirical testing:

| Tool | Category | p50 Latency | Winner | Use Case |
|------|----------|-------------|--------|----------|
| **gh CLI** | CLI | 504ms | ✅ | GitHub repo access |
| PyGithub | Library | 688ms | - | GitHub complex ops |
| python_builtin (read) | Baseline | 0.05ms | ✅ | File read |
| python_builtin (write) | Baseline | 0.23ms | ✅ | File write |
| python_glob | Baseline | 314ms | ✅ | Large codebase search |
| graphiti_core | Library | <10ms | ✅ | Episode creation |

**Key Finding**: gh CLI is **25% faster** than PyGithub for repository access operations.

---

## Token Cost Estimation

| Tool Type | Estimated Tokens | Rationale |
|-----------|------------------|-----------|
| **Direct Python Library** | 50-100 | Function signature + params |
| **CLI Tool** | 100-200 | Command string + JSON parsing |
| **MCP Server** | 200-300 | JSON-RPC protocol + params |
| **Claude Code Built-in** | 50-100 | Direct tool call |

**Optimization**: Direct libraries have lowest token overhead for LLM tool calling.

---

## Implementation Pattern

### Template for Tool Selection in Agent Code

```python
from typing import Literal, Union
from dataclasses import dataclass

@dataclass
class ToolCall:
    """Tool call with performance characteristics"""
    name: str
    category: Literal["library", "cli", "mcp", "builtin"]
    expected_latency_ms: float
    token_overhead: int

class AgentToolSelector:
    """Select optimal tool based on operation requirements"""

    def select_github_tool(self, operation: str) -> ToolCall:
        """Select GitHub tool based on operation type"""
        if operation in ["get_repo", "list_issues", "search_repos"]:
            # Latency-sensitive: use gh CLI (25% faster)
            return ToolCall(
                name="gh_cli",
                category="cli",
                expected_latency_ms=504,
                token_overhead=150
            )
        else:
            # Complex ops: use PyGithub (type-safe)
            return ToolCall(
                name="pygithub",
                category="library",
                expected_latency_ms=688,
                token_overhead=100
            )

    def select_file_tool(self, operation: str) -> ToolCall:
        """Select file operation tool"""
        # Always use built-in for basic file ops (fastest)
        ops_map = {
            "read": ToolCall("read", "builtin", 0.05, 50),
            "write": ToolCall("write", "builtin", 0.23, 50),
            "glob": ToolCall("glob", "builtin", 314, 50),
        }
        return ops_map.get(operation)

    def select_knowledge_tool(self, operation: str) -> ToolCall:
        """Select knowledge management tool"""
        if operation in ["add_episode", "search", "graph_query"]:
            # ALWAYS use direct library (3x faster than MCP)
            return ToolCall(
                name="graphiti_core",
                category="library",
                expected_latency_ms=10,
                token_overhead=100
            )
        elif operation == "structured_notes":
            return ToolCall(
                name="obsidian_mcp",
                category="mcp",
                expected_latency_ms=1000,
                token_overhead=250
            )
```

---

## Validation Checklist

Before deploying LangGraph agent with tool assignments:

- [ ] **Performance**: Check expected latency against agent budget
  - Orchestrator: <1s per operation
  - Analyst: <500ms per search
  - Knowledge: <300ms per query
  - Developer: <2s per action
  - Validator: <200ms per check

- [ ] **Tool Priority**: Verify using correct priority (direct > CLI > MCP > built-in)

- [ ] **Critical Paths**: Ensure direct libraries used for performance-critical operations:
  - ✅ graphiti_core (NOT Graphiti MCP)
  - ✅ psycopg (NOT Postgres MCP for queries)
  - ✅ gh CLI (NOT PyGithub for simple ops)

- [ ] **Benchmarks**: Compare actual performance against Story 1.8 benchmarks

- [ ] **Token Budget**: Estimate token cost for tool calling

---

## Monitoring and Optimization

### LangSmith Integration

Track tool performance in production:

```python
from langsmith import traceable

@traceable
def orchestrator_github_call(operation: str):
    """Track GitHub tool call performance"""
    tool = tool_selector.select_github_tool(operation)
    result = call_tool(tool)
    # LangSmith automatically tracks latency, tokens
    return result
```

### Performance Alerts

Set alerts for tool calls exceeding benchmarks:

```python
if actual_latency > expected_latency * 1.5:
    log_warning(
        f"Tool {tool.name} took {actual_latency}ms "
        f"(expected {tool.expected_latency_ms}ms)"
    )
```

---

## References

- [Tool Recommendations](../../docs/research/tool-recommendations.md) - Per-agent guidance
- [Tool Efficiency Analysis](../../docs/research/tool-efficiency-analysis.md) - Benchmark results
- [Story 1.8: Tool Efficiency Research](../../docs/stories/epic-1/story-1-8-agent-tool-usage-rules.md)
- [Architecture: Tech Stack](../../docs/architecture/3-tech-stack.md)

---

## Version History

- **v1.0 (2025-10-02)**: Initial release based on Story 1.8 research
  - 6 empirical benchmarks
  - Per-agent recommendations
  - Decision tree and priority hierarchy

---

**Guide Prepared By**: BMAD Dev Agent (James)
**Guide Date**: 2025-10-02
**Research Basis**: Story 1.8 Phase 2 & 3
**Status**: ✅ Complete - Ready for LangGraph Agent Implementation
