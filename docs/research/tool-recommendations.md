# Tool Recommendations for LangGraph Agents

**Date**: 2025-10-02
**Research Team**: BMAD Dev Agent (James)
**Based On**: [Tool Efficiency Analysis](tool-efficiency-analysis.md)
**Status**: Phase 3 Complete

---

## Executive Summary

Data-driven recommendations for tool selection per LangGraph agent, based on empirical benchmarking from Story 1.8 research. Each recommendation includes specific use cases, performance expectations, and implementation guidance.

### Decision Framework

```
┌─────────────────────────────────────────┐
│  1. Is there a direct Python library?  │
│     └─> YES: Use direct (3x faster)    │
│     └─> NO: Continue to step 2         │
└─────────────────────────────────────────┘
                   │
┌─────────────────────────────────────────┐
│  2. Is performance critical?            │
│     └─> YES: Use CLI if available      │
│     └─> NO: Continue to step 3          │
└─────────────────────────────────────────┘
                   │
┌─────────────────────────────────────────┐
│  3. Does MCP server exist?              │
│     └─> YES: Use MCP                    │
│     └─> NO: Use Claude Code built-in    │
└─────────────────────────────────────────┘
```

---

## Orchestrator Agent Recommendations

**Agent**: [src/agents/orchestrator_agent.py](../../src/agents/orchestrator_agent.py)
**Responsibilities**: Workflow coordination, GitHub operations, web research, file operations

### Recommended Tools

#### 1. GitHub Operations

**HIGH PRIORITY: Use `gh CLI` for latency-sensitive operations**

```python
# RECOMMENDED: gh CLI (25% faster)
import subprocess

result = subprocess.run(
    ["gh", "repo", "view", "owner/repo", "--json", "name,description"],
    capture_output=True, text=True
)
data = json.loads(result.stdout)

# Performance: 504ms p50 (vs PyGithub 688ms)
# Best for: List issues, search repos, get PRs
```

**MEDIUM PRIORITY: Use `PyGithub` for complex workflows**

```python
# USE FOR: Type-safe complex operations
from github import Github, Auth

auth = Auth.Token(github_token)
gh = Github(auth=auth)
repo = gh.get_repo("owner/repo")

# Create PR with full typing
pr = repo.create_pull(
    title="Feature X",
    body="Description",
    head="feature-branch",
    base="main"
)

# Performance: 688ms p50
# Best for: Create PR, update issues, multi-step operations
```

**Tool Selection Decision Tree**:

| Operation | Use | Rationale |
|-----------|-----|-----------|
| Get repo metadata | **gh CLI** | Latency-sensitive (25% faster) |
| List issues/PRs | **gh CLI** | High-frequency, latency matters |
| Search repositories | **gh CLI** | Batch operations, speed critical |
| Create/update PR | **PyGithub** | Complex workflow, needs typing |
| Multi-step operations | **PyGithub** | Error handling, transaction-like |

---

#### 2. Web Research

**RECOMMENDATION: Use `tavily-python` direct library** (pending benchmark validation)

```python
# RECOMMENDED: Direct Python library
from tavily import TavilyClient

client = TavilyClient(api_key=tavily_key)
results = client.search(
    query="LangGraph best practices",
    search_depth="advanced"
)

# Expected: Sub-second latency, structured results
# Best for: Multi-source research, RAG context
```

**ALTERNATIVE: `WebSearch` (Claude Code built-in)** for US-only simple searches

**Trade-offs**:
- **tavily-python**: Better search depth, cost tracking, programmatic control
- **WebSearch**: Simpler integration, no API key management, US-only

---

#### 3. File Operations

**RECOMMENDATION: Use Claude Code built-in tools**

```python
# File read: Use Read tool (direct, 0.05ms baseline)
# File write: Use Write tool (direct, 0.23ms baseline)
# File edit: Use Edit tool (exact string matching)
# File search: Use Glob tool (314ms for large codebase)
# File grep: Use Grep tool (regex search)
```

**Performance Expectations** (from benchmarks):
- Read: ~0.05ms per file
- Write: ~0.23ms per file
- Glob: ~314ms for recursive search (1000+ files)

**When to use alternatives**:
- **Filesystem MCP**: When sandboxing required, directory restrictions needed
- **Serena MCP**: When semantic code understanding needed (symbols, definitions)

---

### Orchestrator Summary

| Tool Category | Primary Recommendation | Performance | Use Cases |
|---------------|------------------------|-------------|-----------|
| **GitHub** | gh CLI + PyGithub hybrid | 504ms (CLI), 688ms (lib) | CLI for speed, lib for complex ops |
| **Web Research** | tavily-python | <1s (expected) | Multi-source research |
| **File Ops** | Claude Code built-in | 0.05-314ms | Read/write/search/grep |

---

## Analyst Agent Recommendations

**Agent**: [src/agents/analyst_agent.py](../../src/agents/analyst_agent.py)
**Responsibilities**: Code analysis, semantic search, documentation retrieval

### Recommended Tools

#### 1. Semantic Code Search

**HIGH PRIORITY: Use `Serena MCP` (direct SDK)** - Currently implemented in Story 1.2

```python
# RECOMMENDED: Serena MCP via direct SDK (performance-critical)
from mcp_bridge import MCPBridge

bridge = MCPBridge()
results = await bridge.call_tool(
    "serena",
    "search_symbol",
    {"query": "ToolBenchmark", "symbol_type": "class"}
)

# Expected: Sub-500ms for semantic search
# Best for: Symbol search, definitions, references
```

**Serena Tool Priority** (10 HIGH priority tools):
1. **search_symbol** - Find code symbols semantically
2. **find_symbol** - Locate symbol definitions
3. **find_referencing_symbols** - Find usages
4. **get_symbols_overview** - Project structure
5. **read_file** - File content with LSP context

**ALTERNATIVE: Claude Code Grep** for simple regex searches

**Trade-offs**:
- **Serena MCP**: Semantic understanding, LSP-powered, context-aware
- **Grep**: Faster for simple patterns, no semantic overhead

---

#### 2. Documentation Retrieval

**RECOMMENDATION: Use `Context7 MCP` for library documentation**

```python
# For fresh library docs (vs docs-cache files)
results = await bridge.call_tool(
    "context7",
    "get-library-docs",
    {"library": "langgraph", "version": "latest"}
)

# Expected: <2s for doc retrieval
# Best for: Up-to-date API docs, version-specific info
```

**ALTERNATIVE: `.claude/docs-cache/` files** for cached project docs

**Trade-offs**:
- **Context7 MCP**: Fresh docs, version-specific
- **docs-cache**: Faster, offline, curated

---

#### 3. Reasoning Support

**RECOMMENDATION: Use `Sequential Thinking MCP` for complex multi-step analysis**

```python
# For complex problem decomposition
result = await bridge.call_tool(
    "sequential_thinking",
    "sequentialthinking",
    {"problem": "How to optimize benchmark framework?"}
)

# Expected: 3-10s for multi-step reasoning
# Best for: Architectural decisions, trade-off analysis
```

**ALTERNATIVE: Manual chain-of-thought prompting** for simple analysis

---

### Analyst Summary

| Tool Category | Primary Recommendation | Expected Perf | Use Cases |
|---------------|------------------------|---------------|-----------|
| **Code Search** | Serena MCP | <500ms | Semantic symbol search |
| **Docs** | Context7 MCP + docs-cache | <2s | Library documentation |
| **Reasoning** | Sequential Thinking MCP | 3-10s | Complex analysis |

---

## Knowledge Agent Recommendations

**Agent**: [src/agents/knowledge_agent.py](../../src/agents/knowledge_agent.py)
**Responsibilities**: Episodic memory, knowledge graphs, note management

### Recommended Tools

#### 1. Knowledge Graph Operations

**HIGH PRIORITY: Use `graphiti_core` direct library** - Currently implemented in Story 1.3

```python
# RECOMMENDED: Direct library (3x faster than MCP per Story 1.3)
from graphiti_core import Graphiti

async with Graphiti(neo4j_uri, neo4j_user, neo4j_password) as client:
    # Add episode
    await client.add_episode(
        name="benchmark_session",
        content="Benchmark test results...",
        timestamp=datetime.now()
    )

    # Search knowledge
    results = await client.search(
        query="benchmark framework patterns"
    )

# Performance: <10ms overhead, <300ms Neo4j queries
# Best for: Episodic memory, semantic search, temporal queries
```

**Graphiti Tool Priority** (5 HIGH priority methods):
1. **add_episode()** - Store episodic memory
2. **search()** - Semantic knowledge retrieval
3. **search_nodes()** - Graph traversal
4. **search_facts()** - Fact extraction
5. **get_episode()** - Episode retrieval

**AVOID: Graphiti MCP** (3x slower per Story 1.3 benchmarks)

---

#### 2. Note Management

**RECOMMENDATION: Use `Obsidian MCP` for structured notes**

```python
# For markdown-based knowledge base
results = await bridge.call_tool(
    "obsidian",
    "search",
    {"query": "benchmark framework", "folder": "research"}
)

# Expected: <1s for note search
# Best for: Documentation, meeting notes, structured knowledge
```

**Obsidian Tool Priority** (6 commonly used tools):
1. **search** - Full-text note search
2. **get_file_contents** - Read note
3. **create_file** - New note
4. **patch_content** - Edit note
5. **get_backlinks** - Link analysis
6. **get_tags** - Tag-based retrieval

**ALTERNATIVE: Filesystem MCP** for unstructured file storage

**Trade-offs**:
- **Obsidian MCP**: Structured notes, backlinks, tags, markdown parsing
- **Filesystem MCP**: Simple file storage, no metadata overhead

---

#### 3. Hybrid Search Strategy

**RECOMMENDATION: Combine Graphiti + Obsidian + Context7**

```python
# Three-pillar knowledge retrieval
async def hybrid_search(query: str):
    # 1. Graphiti: Episodic memory (temporal, graph)
    graphiti_results = await graphiti.search(query)

    # 2. Obsidian: Documentation notes
    obsidian_results = await bridge.call_tool(
        "obsidian", "search", {"query": query}
    )

    # 3. Context7: External library docs (if needed)
    context7_results = await bridge.call_tool(
        "context7", "get-library-docs", {"library": query}
    )

    return merge_and_rank(graphiti_results, obsidian_results, context7_results)

# Expected: <3s for comprehensive search
# Best for: Comprehensive knowledge retrieval
```

---

### Knowledge Summary

| Tool Category | Primary Recommendation | Performance | Use Cases |
|---------------|------------------------|-------------|-----------|
| **Knowledge Graph** | graphiti_core direct | <10ms + Neo4j | Episodic memory, temporal queries |
| **Notes** | Obsidian MCP | <1s | Structured markdown notes |
| **Hybrid Search** | Graphiti + Obsidian + Context7 | <3s | Comprehensive retrieval |

---

## Developer Agent Recommendations

**Agent**: [src/agents/developer_agent.py](../../src/agents/developer_agent.py)
**Responsibilities**: Code generation, browser automation, debugging

### Recommended Tools

#### 1. Browser Automation

**RECOMMENDATION: Use `Chrome DevTools MCP`** - Currently implemented in Story 1.6

```python
# For end-to-end browser automation
await bridge.call_tool(
    "chrome_devtools",
    "navigate_to",
    {"url": "https://example.com"}
)

snapshot = await bridge.call_tool(
    "chrome_devtools",
    "take_snapshot",
    {}
)

# Expected: <2s for page load + snapshot
# Best for: E2E testing, UI debugging, DOM inspection
```

**Chrome DevTools Tool Priority** (6 commonly used tools):
1. **navigate_to** - Load page
2. **take_snapshot** - Capture DOM
3. **execute_javascript** - Run JS
4. **list_console_messages** - Debug logs
5. **new_page** - Create tab
6. **close_page** - Cleanup

**ALTERNATIVE: Playwright** for complex automation (not benchmarked)

---

#### 2. Code Generation

**RECOMMENDATION: Use Claude Code built-in tools**

```python
# File operations for code generation
# Write: Create new file (0.23ms baseline)
# Edit: Modify existing file (exact string match)
# Read: Verify generated code (0.05ms baseline)
```

**Best Practices**:
- Use **Write** for new files
- Use **Edit** for targeted modifications
- Use **Read** to verify changes
- Use **Glob** + **Grep** for code discovery before generation

---

#### 3. Debugging Support

**RECOMMENDATION: Use Chrome DevTools for client-side debugging**

```python
# Capture console errors
logs = await bridge.call_tool(
    "chrome_devtools",
    "list_console_messages",
    {}
)

# Best for: JavaScript errors, network failures, DOM issues
```

**ALTERNATIVE: Sentry MCP** for server-side error tracking (Validator agent)

---

### Developer Summary

| Tool Category | Primary Recommendation | Expected Perf | Use Cases |
|---------------|------------------------|---------------|-----------|
| **Browser** | Chrome DevTools MCP | <2s | E2E testing, debugging |
| **Code Gen** | Claude Code built-in | 0.05-0.23ms | File write/edit/read |
| **Debugging** | Chrome DevTools | <1s | Client-side errors |

---

## Validator Agent Recommendations

**Agent**: [src/agents/validator_agent.py](../../src/agents/validator_agent.py)
**Responsibilities**: Error tracking, database optimization, test improvement

### Recommended Tools

#### 1. Database Operations

**HIGH PRIORITY: Use `psycopg` direct library** (synchronous)

```python
# RECOMMENDED: Direct library for performance
import psycopg

with psycopg.connect(conn_string) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM benchmarks WHERE id = %s", (1,))
        result = cur.fetchone()

# Expected: <50ms for simple queries
# Best for: Query execution, bulk operations, connection pooling
```

**psycopg Tool Priority** (15 HIGH priority methods):
1. **connect()** - Database connection
2. **execute()** - Query execution
3. **executemany()** - Batch operations
4. **fetchone()/fetchall()** - Result retrieval
5. **commit()** - Transaction commit

**ALTERNATIVE: Postgres MCP Pro** for query analysis (not performance-critical)

**Trade-offs**:
- **psycopg direct**: Faster, full control, connection pooling
- **Postgres MCP Pro**: Query analysis, explain plans, schema inspection

---

#### 2. Error Tracking

**RECOMMENDATION: Use `Sentry MCP` for real-time error tracking**

```python
# For production error monitoring
await bridge.call_tool(
    "sentry",
    "capture_error",
    {
        "exception": str(error),
        "context": {"agent": "validator", "workflow": "benchmark"}
    }
)

# Expected: <100ms async capture
# Best for: Error aggregation, real-time alerts, issue tracking
```

**Sentry Tool Priority** (3 commonly used tools):
1. **capture_error** - Log exceptions
2. **list_issues** - Review errors
3. **get_issue_details** - Debug information

**ALTERNATIVE: Python logging** for simple error tracking

---

#### 3. Self-Improvement (DSPy)

**RECOMMENDATION: Use `dspy-ai` direct library for prompt optimization**

```python
# For automated prompt improvement
import dspy

# Compile optimizer
optimizer = dspy.BootstrapFewShot(metric=accuracy)
compiled_predictor = optimizer.compile(predictor, trainset=examples)

# Expected: 10-60s for optimization
# Best for: Test generation, validation rules, quality scoring
```

**DSPy Tool Priority** (5 commonly used modules):
1. **Predict** - Basic LLM prompting
2. **ChainOfThought** - Reasoning
3. **ReAct** - Tool-augmented reasoning
4. **BootstrapFewShot** - Optimization
5. **Evaluate** - Quality measurement

---

### Validator Summary

| Tool Category | Primary Recommendation | Expected Perf | Use Cases |
|---------------|------------------------|---------------|-----------|
| **Database** | psycopg direct | <50ms | Query execution, bulk ops |
| **Error Tracking** | Sentry MCP | <100ms | Real-time monitoring |
| **Self-Improvement** | dspy-ai direct | 10-60s | Prompt optimization |

---

## Cross-Agent Tool Selection Guide

### Priority Hierarchy (from Story 1.8 architecture)

```
1. Direct Python Library (if available)
   └─> 3x faster, full API access, type safety
   └─> Examples: graphiti_core, psycopg, dspy-ai, PyGithub

2. CLI Tool (if performance-critical)
   └─> 25% faster than libraries (gh CLI example)
   └─> Examples: gh, git, npm, docker

3. MCP Server (if no library or external service)
   └─> Standardized interface, cross-language
   └─> Examples: Serena, Chrome DevTools, Obsidian

4. Claude Code Built-in (file operations, search)
   └─> Fastest for basic operations
   └─> Examples: Read, Write, Edit, Glob, Grep
```

---

## Implementation Guidance

### Step 1: Audit Current Agent Tools

For each LangGraph agent:
1. List current tool assignments
2. Check against recommendations above
3. Identify misalignments (e.g., using MCP when direct library available)

### Step 2: Migrate to Recommended Tools

**Example: Orchestrator GitHub operations**

```python
# BEFORE: PyGithub only
from github import Github
gh = Github(token)
repo = gh.get_repo("owner/repo")  # 688ms

# AFTER: Hybrid approach
import subprocess
import json

# Fast path: gh CLI for metadata
result = subprocess.run(
    ["gh", "repo", "view", "owner/repo", "--json", "name,stars"],
    capture_output=True, text=True
)
metadata = json.loads(result.stdout)  # 504ms

# Complex path: PyGithub for PR creation
if need_create_pr:
    gh = Github(auth=Auth.Token(token))
    repo = gh.get_repo("owner/repo")
    pr = repo.create_pull(...)  # Type-safe
```

### Step 3: Measure Performance

Use Story 1.8.1 benchmark framework:

```python
from tests.research.tool_benchmark import ToolBenchmark

benchmark = ToolBenchmark("my_operation", "category")
result = benchmark.measure(my_function, *args)
stats = benchmark.get_stats()

# Compare against benchmarks in tool-efficiency-analysis.md
```

### Step 4: Update Agent Code

Implement recommendations in production agent files:
- [src/agents/orchestrator_agent.py](../../src/agents/orchestrator_agent.py)
- [src/agents/analyst_agent.py](../../src/agents/analyst_agent.py)
- [src/agents/knowledge_agent.py](../../src/agents/knowledge_agent.py)
- [src/agents/developer_agent.py](../../src/agents/developer_agent.py)
- [src/agents/validator_agent.py](../../src/agents/validator_agent.py)

---

## Performance Expectations

### Per-Agent Latency Budget

| Agent | Average Tool Call | Budget | Critical Tools |
|-------|-------------------|--------|----------------|
| **Orchestrator** | 400ms | <1s per operation | gh CLI (504ms), file ops (0.05ms) |
| **Analyst** | 300ms | <500ms per search | Serena semantic search |
| **Knowledge** | 200ms | <300ms per query | Graphiti Neo4j queries |
| **Developer** | 1500ms | <2s per action | Chrome DevTools automation |
| **Validator** | 100ms | <200ms per check | psycopg queries, error capture |

---

## Next Steps

1. **Implement recommendations** in LangGraph agent code (Story 1.9 or separate story)
2. **Validate performance** using production workloads
3. **Monitor metrics** via LangSmith
4. **Iterate** based on real usage patterns

---

## References

- [Tool Efficiency Analysis](tool-efficiency-analysis.md) - Benchmark results
- [Story 1.8: Tool Efficiency Research](../stories/epic-1/story-1-8-agent-tool-usage-rules.md)
- [Architecture: Tech Stack](../architecture/3-tech-stack.md)
- [Story 1.3: Graphiti Performance Data](../stories/epic-1/story-1-3-graphiti-mcp-obsidian-filesystem.md)

---

**Recommendations Prepared By**: BMAD Dev Agent (James)
**Recommendations Date**: 2025-10-02
**Based On**: 6 empirical benchmarks + Story 1.3 findings
**Status**: ✅ Complete - Ready for LangGraph Agent Implementation
