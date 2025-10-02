# Tool Options Analysis for LangGraph Agents

**Version**: 1.0
**Date**: 2025-10-02
**Author**: BMAD PM Agent (John)
**Purpose**: Document available tool options for each LangGraph agent

## Overview

This document catalogs all available tool options for LangGraph agents, comparing direct Python libraries vs MCP server integrations. Each section includes tool capabilities, integration methods, and expected use cases.

## Integration Methods

### Method 1: Direct Python Library
- **Pattern**: `import library; client = Library()`
- **Pros**: Fastest (no protocol overhead), full API access, type safety
- **Cons**: Requires Python bindings, direct dependency management
- **Cost**: $0 (no LLM routing)
- **Example**: PyGithub, tavily-python, graphiti_core, dspy-ai

### Method 2: MCP via langchain-mcp-adapters
- **Pattern**: LangChain tool wrapping MCP server
- **Pros**: Standardized interface, works with any MCP server
- **Cons**: Additional latency, token overhead for routing
- **Cost**: Depends on routing LLM (can be $0 with local Ollama)
- **Example**: All MCP servers via LangChain integration

### Method 3: Direct MCP SDK (stdio)
- **Pattern**: Python MCP SDK with stdio transport
- **Pros**: Native MCP protocol, persistent sessions
- **Cons**: More complex setup, async required
- **Cost**: $0 (no routing LLM)
- **Example**: Serena MCP (currently used by Analyst)

---

## Orchestrator Agent

**Primary Responsibility**: Workflow coordination, task delegation

### Tool Option 1: GitHub Operations

**Option A: PyGithub (Direct Library)** ⭐ CURRENT
- **Package**: `PyGithub`
- **Integration**: Direct Python import
- **Capabilities**:
  - Repository search and retrieval
  - PR listing, creation, updating
  - Issue management
  - Commit history
  - File operations
- **Performance**: High (direct API calls)
- **Cost**: $0
- **Limitations**: Requires GITHUB_TOKEN

**Option B: GitHub MCP**
- **Package**: `@gongrzhe/server-github` (MCP server)
- **Integration**: langchain-mcp-adapters
- **Capabilities**: Similar to PyGithub
- **Performance**: Lower (MCP protocol overhead)
- **Cost**: Token overhead for routing
- **Limitations**: Requires MCP server running

**Test Plan**: Compare latency, ease of use for repo search and PR listing

### Tool Option 2: Web Research

**Option A: tavily-python (Direct Library)** ⭐ CURRENT
- **Package**: `tavily-python`
- **Integration**: Direct Python import
- **Capabilities**:
  - Web search (basic, advanced)
  - Content extraction
  - Site crawling
  - Site mapping
- **Performance**: High (direct API)
- **Cost**: Tavily API pricing only
- **Limitations**: Requires TAVILY_API_KEY

**Option B: Tavily MCP**
- **Package**: `tavily-mcp` (MCP server)
- **Integration**: langchain-mcp-adapters
- **Capabilities**: Same as tavily-python
- **Performance**: Lower (MCP overhead)
- **Cost**: Tavily API + token routing overhead
- **Limitations**: Requires MCP server

**Test Plan**: Compare search quality and latency for 10 queries

### Tool Option 3: File Operations

**Option A: Python Built-in**
- **Package**: Built-in `open()`, `pathlib`
- **Integration**: Native Python
- **Capabilities**: Read, write, list files
- **Performance**: Highest (no overhead)
- **Cost**: $0
- **Limitations**: Manual error handling

**Option B: Filesystem MCP**
- **Package**: `@modelcontextprotocol/server-filesystem`
- **Integration**: langchain-mcp-adapters
- **Capabilities**: Enhanced file ops with metadata
- **Performance**: Lower (MCP overhead)
- **Cost**: Token overhead
- **Limitations**: Requires allowed directories config

**Test Plan**: Compare performance for 100 file reads

---

## Analyst Agent

**Primary Responsibility**: Code analysis, semantic search

### Tool Option 1: Semantic Code Search

**Option A: Serena MCP (Direct SDK)** ⭐ CURRENT
- **Package**: Serena MCP server
- **Integration**: Direct Python MCP SDK (stdio)
- **Capabilities**:
  - Symbol search (classes, functions)
  - Find definitions and references
  - File outline
  - Semantic code understanding
- **Performance**: Medium (stdio overhead)
- **Cost**: $0 (local LSP)
- **Limitations**: Requires project indexing

**Option B: Filesystem grep/ripgrep**
- **Package**: Python `subprocess` + ripgrep
- **Integration**: Shell command wrapper
- **Capabilities**:
  - Text search
  - Regex patterns
  - Fast file scanning
- **Performance**: High for simple searches
- **Cost**: $0
- **Limitations**: No semantic understanding

**Test Plan**: Compare accuracy for 50 symbol searches

### Tool Option 2: Documentation Retrieval

**Option A: Context7 MCP**
- **Package**: `@upstash/context7-mcp`
- **Integration**: langchain-mcp-adapters
- **Capabilities**:
  - Resolve library IDs
  - Fetch library documentation
  - Real-time doc updates
- **Performance**: Medium (MCP + API)
- **Cost**: Context7 API pricing + tokens
- **Limitations**: Requires API key

**Option B: Web Search Fallback**
- **Package**: DuckDuckGo search or tavily-python
- **Integration**: Direct or MCP
- **Capabilities**: General web search
- **Performance**: Variable
- **Cost**: Depends on provider
- **Limitations**: Less targeted than Context7

**Test Plan**: Compare doc quality for 20 Python libraries

### Tool Option 3: Complex Reasoning

**Option A: Sequential Thinking MCP**
- **Package**: `@modelcontextprotocol/server-sequential-thinking`
- **Integration**: langchain-mcp-adapters
- **Capabilities**:
  - Structured multi-step reasoning
  - Thought chain tracking
  - Intermediate result storage
- **Performance**: Medium (depends on reasoning depth)
- **Cost**: Token usage for thinking
- **Limitations**: May over-think simple problems

**Option B: Manual Chain-of-Thought**
- **Package**: Custom prompting
- **Integration**: LangChain prompt templates
- **Capabilities**: User-defined reasoning steps
- **Performance**: Comparable
- **Cost**: Similar token usage
- **Limitations**: Manual prompt engineering

**Test Plan**: Compare reasoning quality for 10 multi-step analyses

---

## Knowledge Agent

**Primary Responsibility**: Knowledge graphs, documentation management

### Tool Option 1: Knowledge Graph Operations

**Option A: graphiti_core (Direct Library)** ⭐ CURRENT
- **Package**: `graphiti-core`
- **Integration**: Direct Python import
- **Capabilities**:
  - Add episodes (temporal knowledge)
  - Search nodes, facts, episodes
  - Graph queries
  - Bi-temporal tracking
- **Performance**: High (Story 1.3 showed 3x faster than MCP)
- **Cost**: Neo4j hosting only
- **Limitations**: Requires Neo4j database

**Option B: Graphiti MCP**
- **Package**: Graphiti MCP server
- **Integration**: langchain-mcp-adapters or direct SDK
- **Capabilities**: Same as graphiti_core
- **Performance**: Lower (MCP protocol overhead)
- **Cost**: Neo4j + token overhead
- **Limitations**: Additional MCP server process

**Test Plan**: Validate "3x faster" claim with 100 episode operations

### Tool Option 2: Note Management

**Option A: Obsidian MCP**
- **Package**: `@modelcontextprotocol/server-obsidian`
- **Integration**: langchain-mcp-adapters
- **Capabilities**:
  - List notes in vault
  - Read/write notes
  - Search notes
  - Patch/append content
  - Note metadata
- **Performance**: Medium (MCP overhead)
- **Cost**: Token overhead
- **Limitations**: Requires Obsidian vault path

**Option B: Filesystem MCP (Markdown)**
- **Package**: `@modelcontextprotocol/server-filesystem`
- **Integration**: langchain-mcp-adapters
- **Capabilities**:
  - Read/write markdown files
  - Directory operations
  - File search
- **Performance**: Medium (MCP overhead)
- **Cost**: Token overhead
- **Limitations**: No note-specific features

**Test Plan**: Compare for 50 note CRUD operations

### Tool Option 3: Knowledge Retrieval

**Option A: Graphiti Search**
- **Package**: graphiti_core
- **Integration**: Direct library
- **Capabilities**:
  - Semantic search
  - Temporal queries
  - Graph traversal
- **Performance**: High
- **Cost**: Neo4j only
- **Limitations**: Requires graph data

**Option B: Obsidian Search**
- **Package**: Obsidian MCP
- **Integration**: langchain-mcp-adapters
- **Capabilities**:
  - Keyword search
  - Tag search
  - Full-text search
- **Performance**: Medium
- **Cost**: Token overhead
- **Limitations**: Keyword-based (not semantic)

**Test Plan**: Compare 20 semantic vs keyword searches

---

## Developer Agent

**Primary Responsibility**: Code implementation, browser testing

### Tool Option 1: Browser Automation

**Option A: Chrome DevTools MCP** ⭐ CURRENT (Story 1.6)
- **Package**: `@upstash/chrome-devtools-mcp`
- **Integration**: langchain-mcp-adapters
- **Capabilities**:
  - Launch browser, navigate pages
  - Take snapshots
  - Console messages
  - Screenshot capture
  - Execute JavaScript
- **Performance**: Medium (MCP overhead)
- **Cost**: Token overhead
- **Limitations**: Chrome-specific

**Option B: Playwright MCP**
- **Package**: `mcp-playwright` (if available)
- **Integration**: langchain-mcp-adapters
- **Capabilities**:
  - Multi-browser support
  - Advanced automation
  - Network interception
  - Trace recording
- **Performance**: Medium (MCP overhead)
- **Cost**: Token overhead
- **Limitations**: More complex setup

**Test Plan**: Compare reliability for 20 page loads

### Tool Option 2: DOM Inspection

**Option A: Chrome DevTools Snapshot**
- **Package**: Chrome DevTools MCP
- **Integration**: langchain-mcp-adapters
- **Capabilities**:
  - Full DOM tree
  - Element properties
  - Style information
- **Performance**: Fast
- **Cost**: Token overhead
- **Limitations**: Static snapshot

**Option B: Playwright Page Content**
- **Package**: Playwright MCP
- **Integration**: langchain-mcp-adapters
- **Capabilities**:
  - Live DOM access
  - Element queries
  - Dynamic state
- **Performance**: Fast
- **Cost**: Token overhead
- **Limitations**: Requires active browser

**Test Plan**: Compare detail for 30 page snapshots

### Tool Option 3: Console Debugging

**Option A: Chrome DevTools Console**
- **Package**: Chrome DevTools MCP
- **Integration**: langchain-mcp-adapters
- **Capabilities**:
  - Console log capture
  - Error messages
  - Warning detection
- **Performance**: Fast
- **Cost**: Token overhead
- **Limitations**: Chrome-specific

**Option B: Playwright Console**
- **Package**: Playwright MCP
- **Integration**: langchain-mcp-adapters
- **Capabilities**:
  - Multi-browser console
  - Event listeners
  - Message filtering
- **Performance**: Fast
- **Cost**: Token overhead
- **Limitations**: More complex API

**Test Plan**: Compare error capture for 15 test scenarios

---

## Validator Agent

**Primary Responsibility**: QA, optimization, error tracking

### Tool Option 1: Error Tracking

**Option A: Sentry MCP**
- **Package**: `@upstash/sentry-mcp`
- **Integration**: langchain-mcp-adapters
- **Capabilities**:
  - Capture errors
  - List issues
  - Issue details
  - Error aggregation
- **Performance**: Medium (MCP + API)
- **Cost**: Sentry pricing + tokens
- **Limitations**: Requires Sentry account

**Option B: Custom Python Logging**
- **Package**: Python `logging` module
- **Integration**: Native Python
- **Capabilities**:
  - Log errors
  - Stack traces
  - Custom formatting
- **Performance**: High
- **Cost**: $0
- **Limitations**: No aggregation/UI

**Test Plan**: Compare error detail for 50 error captures

### Tool Option 2: Database Query Optimization

**Option A: Postgres MCP Pro**
- **Package**: `@upstash/postgres-mcp-pro`
- **Integration**: langchain-mcp-adapters
- **Capabilities**:
  - Execute queries
  - Analyze performance
  - Get schema
  - Optimization recommendations
- **Performance**: Medium (MCP + DB)
- **Cost**: Token overhead
- **Limitations**: Requires Postgres connection

**Option B: Direct psycopg + EXPLAIN**
- **Package**: `psycopg` (psycopg3)
- **Integration**: Direct Python
- **Capabilities**:
  - Direct query execution
  - EXPLAIN ANALYZE
  - Full Postgres API
- **Performance**: High
- **Cost**: $0
- **Limitations**: Manual optimization

**Test Plan**: Compare analysis depth for 20 queries

### Tool Option 3: Test Optimization

**Option A: DSPy optimize()** ⭐ CURRENT (partial)
- **Package**: `dspy-ai`
- **Integration**: Direct Python import
- **Capabilities**:
  - Signature optimization
  - Test suite refinement
  - Automated improvement
  - Feedback loop
- **Performance**: Variable (depends on optimization)
- **Cost**: LLM API for optimization
- **Limitations**: Requires training data

**Option B: Manual Test Refinement**
- **Package**: Custom Python scripts
- **Integration**: Native
- **Capabilities**:
  - User-defined improvements
  - Manual test writing
  - Coverage analysis
- **Performance**: Slow (human-driven)
- **Cost**: Developer time
- **Limitations**: Not automated

**Test Plan**: Compare improvement rate for 10 test suites

---

## Summary: Tool Comparison Matrix

| Agent | Tool Area | Direct Library | MCP Server | Expected Winner |
|-------|-----------|---------------|------------|-----------------|
| Orchestrator | GitHub | PyGithub ⭐ | GitHub MCP | Direct (faster, 0 cost) |
| Orchestrator | Web Search | tavily-python ⭐ | Tavily MCP | Direct (proven) |
| Orchestrator | File Ops | Python built-in | Filesystem MCP | Direct (simplicity) |
| Analyst | Code Search | N/A | Serena MCP ⭐ | Serena (semantic) |
| Analyst | Docs | N/A | Context7 MCP | Context7 (specialized) |
| Analyst | Reasoning | Manual prompts | Sequential Thinking | TBD (test needed) |
| Knowledge | Graph | graphiti_core ⭐ | Graphiti MCP | Direct (3x faster) |
| Knowledge | Notes | N/A | Obsidian vs Filesystem | TBD (feature comparison) |
| Knowledge | Retrieval | Graphiti | Obsidian | Graphiti (semantic) |
| Developer | Browser | N/A | Chrome DevTools ⭐ vs Playwright | TBD (reliability test) |
| Developer | DOM | N/A | Chrome vs Playwright | TBD (detail comparison) |
| Developer | Console | N/A | Chrome vs Playwright | TBD (capture test) |
| Validator | Errors | Python logging | Sentry MCP | TBD (aggregation value) |
| Validator | DB Optimize | psycopg | Postgres MCP | TBD (recommendation quality) |
| Validator | Test Optimize | DSPy ⭐ | N/A | DSPy (automation) |

⭐ = Currently implemented in LangGraph agents

## Next Steps

1. **Dev Agent**: Use this matrix to guide test implementation priorities
2. **Focus Areas**: Test scenarios marked "TBD" require empirical data
3. **Validation**: Confirm "Expected Winner" predictions with real tests
4. **Documentation**: Update recommendations based on test results
