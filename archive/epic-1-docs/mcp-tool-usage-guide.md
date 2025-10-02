# MCP Tool Usage Guide

**Multi-Agent Development Framework (MADF)**
**Version:** 1.0
**Last Updated:** 2025-09-30

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [Direct MCP Usage](#direct-mcp-usage)
5. [Agent-Based Usage](#agent-based-usage)
6. [Available MCP Servers](#available-mcp-servers)
7. [Tool Lifecycle Management](#tool-lifecycle-management)
8. [Best Practices](#best-practices)
9. [Performance Optimization](#performance-optimization)
10. [Troubleshooting](#troubleshooting)

---

## Overview

MADF implements a hybrid MCP (Model Context Protocol) architecture that combines:

- **Direct MCP Integration**: Performance-critical tools (Serena, Graphiti)
- **MCP-use Wrapped Integration**: External services (Context7, Sequential Thinking, etc.)

### Key Benefits

- **Token Efficient**: Semantic search vs full file reads (30%+ savings)
- **Shared Resources**: Single bridge instance across all agents
- **Persistent Tools**: Load once, use everywhere
- **Intelligent Caching**: Automatic deduplication for API calls

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      MADF Application                        │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐ │
│  │ Analyst   │  │ Knowledge │  │ Developer │  │Validator │ │
│  │  Agent    │  │   Agent   │  │   Agent   │  │  Agent   │ │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └────┬─────┘ │
│        └────────────────┴──────────────┴─────────────┘       │
│                           │                                  │
│                    ┌──────▼──────┐                          │
│                    │  MCPBridge  │  (Singleton)             │
│                    │  (Shared)   │                          │
│                    └──────┬──────┘                          │
│                           │                                  │
│        ┌──────────────────┴──────────────────┐              │
│        │                                      │              │
│  ┌─────▼──────┐                    ┌────────▼────────┐     │
│  │   Direct   │                    │   MCP-use       │     │
│  │    MCP     │                    │   Wrapped       │     │
│  └─────┬──────┘                    └────────┬────────┘     │
└────────┼─────────────────────────────────────┼──────────────┘
         │                                      │
    ┌────▼────┐                        ┌───────▼────────┐
    │ Serena  │                        │   Context7     │
    │Graphiti │                        │Sequential Think│
    └─────────┘                        │    Tavily      │
                                       │   GitHub       │
                                       │    Sentry      │
                                       │   Postgres     │
                                       │   Obsidian     │
                                       │Chrome DevTools │
                                       └────────────────┘
```

### Component Roles

- **MCPBridge**: Central hub for all MCP communication
- **Agents**: High-level interfaces for specific workflows
- **Direct MCP**: Native Python protocol (performance critical)
- **MCP-use Wrapped**: Node.js packages via wrapper (external services)

---

## Quick Start

### Method 1: Direct MCP Usage (No Agent Required)

```python
from src.core.mcp_bridge import MCPBridge

# Initialize bridge directly
bridge = MCPBridge()

# Call Serena for semantic code search
result = bridge.call_serena_tool(
    "find_symbol",
    {
        "name_path": "AnalystAgent",
        "relative_path": "src/agents/analyst_agent.py",
        "include_body": True
    }
)

# Call Context7 for documentation
docs = bridge.call_context7_tool(
    "get_package_docs",
    {
        "package_name": "langgraph",
        "version": "0.2.0"
    }
)

# Call Sequential Thinking for reasoning
reasoning = bridge.call_sequential_thinking_tool(
    "reason",
    {"query": "How should we architect this feature?"}
)
```

### Method 2: Agent-Based Usage (Recommended)

```python
from src.agents.analyst_agent import AnalystAgent

# Initialize agent (includes MCPBridge)
agent = AnalystAgent()

# High-level semantic search
analysis = agent.analyze_code_structure(
    target="src/agents/analyst_agent.py",
    analysis_type="semantic_search",
    track_tokens=True
)

# Get documentation
docs = agent.get_documentation(
    package="langgraph",
    version="0.2.0"
)

# Complex reasoning
reasoning = agent.reason_about_architecture(
    question="How do agents communicate in MADF?"
)
```

### Method 3: Singleton Pattern (Production)

```python
class MCPManager:
    """Shared bridge across entire application"""

    _instance = None
    _bridge = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._bridge = MCPBridge()
        return cls._instance

    @classmethod
    def get_bridge(cls):
        if cls._bridge is None:
            cls._bridge = MCPBridge()
        return cls._bridge

# Use throughout application
manager = MCPManager()
bridge = manager.get_bridge()

# All agents share same bridge
analyst = AnalystAgent()
knowledge = KnowledgeAgent()
# Both use same MCPBridge instance
```

---

## Direct MCP Usage

### Serena MCP (Semantic Code Search)

**Purpose**: LSP-based semantic code analysis (20+ languages)

**Available Tools**:
- `find_symbol`: Find symbols by name/path
- `find_referencing_symbols`: Find references to a symbol
- `search_for_pattern`: Regex pattern search
- `get_symbols_overview`: Get top-level symbols in file
- `list_dir`: List directory contents
- `find_file`: Find files by name/pattern

**Examples**:

```python
# Find a class definition
result = bridge.call_serena_tool(
    "find_symbol",
    {
        "name_path": "AnalystAgent",
        "relative_path": "src/agents/analyst_agent.py",
        "include_body": True
    }
)
# Returns: symbol info with line numbers and body

# Find all references to a symbol
refs = bridge.call_serena_tool(
    "find_referencing_symbols",
    {
        "name_path": "BaseAgent",
        "relative_path": "src/agents/base_agent.py"
    }
)
# Returns: list of files and line numbers referencing BaseAgent

# Search for pattern
matches = bridge.call_serena_tool(
    "search_for_pattern",
    {
        "substring_pattern": "class.*Agent",
        "relative_path": "src/agents"
    }
)
# Returns: all files matching pattern

# Get file overview
symbols = bridge.call_serena_tool(
    "get_symbols_overview",
    {"relative_path": "src/core/mcp_bridge.py"}
)
# Returns: list of top-level classes, functions, methods
```

**Token Efficiency**:
- Traditional file read: ~2,000 tokens (full file)
- Serena semantic search: ~600 tokens (symbols only)
- **Savings: 70%**

### Graphiti MCP (Knowledge Graph)

**Purpose**: Temporal knowledge graph for relationships

**Available Tools**:
- `create_graph`: Create nodes in knowledge graph
- `query_graph`: Query relationships
- `temporal_tracking`: Track changes over time

---

## Agent-Based Usage

### Analyst Agent

**Specialization**: Code analysis, semantic search, documentation

**Tools Available**:
- Serena MCP (direct)
- Context7 MCP (wrapped)
- Sequential Thinking MCP (wrapped)

**Usage Examples**:

```python
from src.agents.analyst_agent import AnalystAgent

agent = AnalystAgent()

# 1. Analyze code structure
analysis = agent.analyze_code_structure(
    target="src/agents/analyst_agent.py",
    analysis_type="semantic_search",
    track_tokens=True
)

print(f"Symbols found: {len(analysis['symbols_found'])}")
print(f"Tokens used: {analysis['token_metrics']['tokens_used']}")

# 2. Get real-time documentation
docs = agent.get_documentation(
    package="langgraph",
    version="0.2.0"
)

print(f"Documentation: {docs['documentation']['description']}")
print(f"Cached: {docs['cached']}")  # Second call = True

# 3. Complex architectural reasoning
reasoning = agent.reason_about_architecture(
    question="Should we use microservices or monolith?"
)

for step in reasoning['reasoning_steps']:
    print(f"Step {step['step']}: {step['reasoning']}")

print(f"Conclusion: {reasoning['conclusion']}")

# 4. Get tool usage guidance
patterns = agent.get_tool_usage_patterns()

for tool, pattern in patterns.items():
    print(f"{tool}:")
    print(f"  - {pattern['description']}")
    print(f"  - When to use: {pattern['when_to_use']}")
```

---

## Available MCP Servers

### Direct MCP (Performance Critical)

#### 1. Serena
- **Type**: Direct Python MCP
- **Purpose**: Semantic code search via LSP
- **Languages**: Python, TypeScript, JavaScript, Go, Rust, Java, C++, etc. (20+)
- **Performance**: High (native protocol)
- **Caching**: Stateless (no cache needed)

#### 2. Graphiti
- **Type**: Direct Python MCP
- **Purpose**: Knowledge graph with temporal tracking
- **Use Case**: Entity relationships, temporal analysis
- **Performance**: High (native protocol)
- **Caching**: Internal graph database

### MCP-use Wrapped (External Services)

#### 3. Context7
- **Package**: `@upstash/context7-mcp`
- **Purpose**: Real-time library/framework documentation
- **Features**: Version-specific docs, API reference
- **Caching**: Built-in (bridge._context7_cache)
- **Rate Limiting**: Handled via cache

**Tools**:
```python
# Get package documentation
bridge.call_context7_tool(
    "get_package_docs",
    {"package_name": "fastapi", "version": "0.100.0"}
)

# Search documentation
bridge.call_context7_tool(
    "search_docs",
    {"query": "async database connections"}
)
```

#### 4. Sequential Thinking
- **Package**: `@modelcontextprotocol/server-sequential-thinking`
- **Purpose**: Multi-step reasoning chains
- **Use Case**: Architectural decisions, debugging workflows
- **Caching**: Stateless (no cache needed)

**Tools**:
```python
# Execute reasoning chain
bridge.call_sequential_thinking_tool(
    "reason",
    {"query": "Why is the API slow?"}
)

# Analyze complex problem
bridge.call_sequential_thinking_tool(
    "analyze_complex_problem",
    {
        "problem": "Choose database: SQL vs NoSQL",
        "context": {"scale": "high", "consistency": "required"}
    }
)
```

#### 5. GitHub
- **Package**: `@gongrzhe/server-github`
- **Purpose**: Repository management, PRs, issues
- **Integration**: Via mcp-use wrapper

#### 6. Tavily
- **Package**: `tavily-mcp`
- **Purpose**: Web search for technical information
- **Use Case**: Research, documentation lookup

#### 7. Sentry
- **Package**: `sentry-mcp`
- **Purpose**: Error tracking and analysis
- **Use Case**: Debugging, issue management

#### 8. Postgres
- **Package**: `postgres-mcp`
- **Purpose**: Database health, query optimization
- **Use Case**: Performance analysis

#### 9. Obsidian
- **Package**: `obsidian-mcp`
- **Purpose**: Note management, vault search
- **Use Case**: Knowledge management

#### 10. Chrome DevTools
- **Package**: `chrome-devtools-mcp`
- **Purpose**: Browser debugging, performance analysis
- **Use Case**: Frontend debugging

---

## Tool Lifecycle Management

### Loading Tools

```python
# Method 1: Implicit loading (agents handle it)
agent = AnalystAgent()  # Loads Serena, Context7, Sequential Thinking

# Method 2: Explicit loading
bridge = MCPBridge()
tools = bridge.load_mcp_tools("context7")
print(tools)  # {'search_docs': '...', 'get_package_docs': '...'}

# Method 3: Load all at startup (recommended)
class MCPManager:
    def _load_all_tools(self):
        for server in self.bridge.get_available_servers():
            self.bridge.load_mcp_tools(server)
```

### Unloading Tools (Rarely Needed)

```python
class MCPManager:
    @classmethod
    def unload_tools(cls, server_name: str):
        """
        Unload tools - clears:
        1. Tool definitions from _loaded_tools
        2. Context7 cache (if server_name == 'context7')

        Does NOT clear:
        - LLM context window
        - Other server caches
        """
        if server_name in cls._loaded_tools:
            del cls._loaded_tools[server_name]

        # Clear Context7 cache
        bridge = cls.get_bridge()
        if server_name == "context7":
            bridge._context7_cache.clear()
```

### When to Unload (Rare Cases)

1. **Memory Pressure**: Python process >8GB RAM, cache >10,000 entries
2. **Force Fresh Data**: Need latest docs, bypass cache
3. **Long Sessions**: 24+ hour daemons, periodic cleanup

**For 99% of usage: KEEP TOOLS LOADED**

---

## Best Practices

### 1. Load Once, Use Everywhere

```python
# ✓ GOOD: Load at session start
manager = MCPManager()
bridge = manager.get_bridge()

# Use across all agents
analyst.analyze_code()
knowledge.research()
developer.implement()
# All share same loaded tools

# ✗ BAD: Load/unload repeatedly
agent.use_context7()
unload_tools("context7")  # Clears cache!
agent.use_context7()      # Cache miss, API call again
```

### 2. Use Singleton Pattern

```python
# ✓ GOOD: Single bridge instance
class MCPManager:
    _instance = None
    _bridge = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._bridge = MCPBridge()
        return cls._instance

# ✗ BAD: Multiple bridge instances
bridge1 = MCPBridge()  # No cache sharing
bridge2 = MCPBridge()  # Duplicate API calls
```

### 3. Leverage Caching

```python
# ✓ GOOD: Cache benefits preserved
result1 = bridge.call_context7_tool("get_package_docs", {...})
# ... other operations ...
result2 = bridge.call_context7_tool("get_package_docs", {...})
# result2['cached'] == True (instant!)

# ✗ BAD: Cache cleared unnecessarily
result1 = bridge.call_context7_tool("get_package_docs", {...})
unload_tools("context7")  # Clears cache
result2 = bridge.call_context7_tool("get_package_docs", {...})
# result2['cached'] == False (API call again)
```

### 4. Use Semantic Search

```python
# ✓ GOOD: Serena semantic search (~600 tokens)
symbols = bridge.call_serena_tool(
    "get_symbols_overview",
    {"relative_path": "src/core/mcp_bridge.py"}
)
# Only symbol definitions, not full file

# ✗ BAD: Read entire file (~2,000 tokens)
with open("src/core/mcp_bridge.py") as f:
    content = f.read()  # Full file content
```

### 5. Agent-Specific Tool Selection

```python
# ✓ GOOD: Match tools to agent specialization
class AnalystAgent:
    _tools = ['serena_mcp', 'context7_mcp', 'sequential_thinking_mcp']

class KnowledgeAgent:
    _tools = ['graphiti_mcp', 'tavily_mcp', 'obsidian_mcp']

# ✗ BAD: All agents have all tools
class Agent:
    _tools = [...all 10 tools...]  # Unnecessary overhead
```

---

## Performance Optimization

### Token Efficiency

| Operation | Traditional | Serena MCP | Savings |
|-----------|------------|------------|---------|
| Find class definition | 2,000 tokens | 600 tokens | 70% |
| Get function signature | 2,000 tokens | 200 tokens | 90% |
| Find references | 10,000 tokens | 1,500 tokens | 85% |

### Cache Performance

```python
# Context7 cache effectiveness
calls_made = 100
cache_hits = 75
cache_miss = 25

efficiency = cache_hits / calls_made  # 75%
api_calls_saved = cache_hits  # 75 calls avoided
```

### Agent Switch Performance

```python
# With persistent tools (recommended)
switch_overhead = 0 ms  # Zero overhead
tools_reloaded = 0      # No reloading

# With unload/reload (not recommended)
switch_overhead = 20 ms  # Loading delay
tools_reloaded = 3       # Redundant work
```

---

## Troubleshooting

### Issue 1: Cache Not Working

**Symptom**: Every call to Context7 hits API (cached=False)

**Causes**:
1. Tools being unloaded between calls
2. Different MCPBridge instances
3. Parameters changing (cache key mismatch)

**Solution**:
```python
# Use singleton pattern
manager = MCPManager()
bridge = manager.get_bridge()

# Same parameters = cache hit
result1 = bridge.call_context7_tool("get_package_docs",
    {"package_name": "fastapi", "version": "0.100.0"})

result2 = bridge.call_context7_tool("get_package_docs",
    {"package_name": "fastapi", "version": "0.100.0"})

assert result2['cached'] == True
```

### Issue 2: Memory Growth

**Symptom**: Python process memory growing continuously

**Causes**:
1. Context7 cache accumulating (many unique queries)
2. Long-running session

**Solution**:
```python
# Check cache size
print(len(bridge._context7_cache))  # If >1000, consider cleanup

# Periodic cleanup (long sessions only)
if len(bridge._context7_cache) > 1000:
    bridge._context7_cache.clear()
```

### Issue 3: Context Window Full

**Symptom**: API errors about context limit

**Causes**:
- Large tool results in conversation history
- Many tool calls accumulating

**Solution**:
```python
# NOT SOLVED BY: unload_tools() - doesn't affect context
# ONLY SOLUTION: Start new conversation

# Prevention: Request minimal data
result = bridge.call_serena_tool(
    "find_symbol",
    {
        "name_path": "AnalystAgent",
        "relative_path": "src/agents/analyst_agent.py",
        "include_body": False  # Don't include full body
    }
)
```

### Issue 4: Serena LSP Errors

**Symptom**: Serena returns no symbols or errors

**Causes**:
1. Invalid file path
2. File not in project
3. LSP not initialized for language

**Solution**:
```python
# Verify file exists
import os
assert os.path.exists("src/agents/analyst_agent.py")

# Check file has content
result = bridge.call_serena_tool(
    "get_symbols_overview",
    {"relative_path": "src/agents/analyst_agent.py"}
)

if not result['success']:
    print(f"Error: {result['error']}")
```

---

## Context Window vs Application Memory

### Critical Distinction

**Context Window** (LLM Memory):
- Conversation history sent to Claude
- Tool call results
- Cannot be cleared mid-conversation
- 200,000 token limit

**Application Memory** (Python Cache):
- bridge._context7_cache dictionary
- Cached tool results
- CAN be cleared with unload_tools()
- Does NOT affect context window

### What unload_tools() Actually Does

```python
unload_tools("context7")

# ✓ Clears: Python cache (bridge._context7_cache)
# ✓ Clears: Tool definitions (_loaded_tools)
# ✗ Does NOT clear: LLM context window
# ✗ Does NOT reduce: Token count
```

### Example

```
Step 1: Call Context7
  Context Window: 2,100 tokens (tool result visible to Claude)
  Python Cache: 1 entry

Step 2: unload_tools('context7')
  Context Window: 2,100 tokens (UNCHANGED!)
  Python Cache: 0 entries (cleared)
```

**Key Insight**: Tool results already in conversation history cannot be removed. Only way to clear context: start new conversation.

---

## Testing

### Unit Tests

```python
# Test Serena integration
def test_serena_find_symbol():
    bridge = MCPBridge()
    result = bridge.call_serena_tool(
        "find_symbol",
        {"name_path": "AnalystAgent",
         "relative_path": "src/agents/analyst_agent.py"}
    )
    assert result['success'] == True
    assert 'symbol_info' in result

# Test Context7 caching
def test_context7_caching():
    bridge = MCPBridge()

    result1 = bridge.call_context7_tool(
        "get_package_docs",
        {"package_name": "test", "version": "1.0"}
    )
    assert result1['cached'] == False

    result2 = bridge.call_context7_tool(
        "get_package_docs",
        {"package_name": "test", "version": "1.0"}
    )
    assert result2['cached'] == True
```

### Integration Tests

See `tests/test_story_1_2_analyst_agent.py` for comprehensive test suite.

---

## Summary

### Key Takeaways

1. **Load Once**: Keep tools loaded throughout session
2. **Singleton Pattern**: Share bridge across all agents
3. **Leverage Cache**: Don't unload tools unnecessarily
4. **Token Efficiency**: Use Serena semantic search over file reads
5. **Agent Specialization**: Match tools to agent workflows

### Quick Reference

```python
# Initialize (once)
manager = MCPManager()
bridge = manager.get_bridge()

# Direct usage
bridge.call_serena_tool(tool_name, params)
bridge.call_context7_tool(tool_name, params)
bridge.call_sequential_thinking_tool(tool_name, params)

# Agent usage
agent = AnalystAgent()
agent.analyze_code_structure(target, analysis_type)
agent.get_documentation(package, version)
agent.reason_about_architecture(question)

# Load tools
bridge.load_mcp_tools(server_name)

# Unload (rare)
manager.unload_tools(server_name)  # Only if memory pressure
```

### Getting Help

- **Tests**: `tests/test_story_1_2_analyst_agent.py`
- **Examples**: `demo_*.py` files in project root
- **Architecture**: `docs/PRD/5-epic-1-multiagent-coding-framework-foundation.md`

---

**Document Version**: 1.0
**Last Updated**: 2025-09-30
**Author**: Dev Agent (James)
**Story**: 1.2 - Serena MCP + Context7 + Sequential Thinking Integration