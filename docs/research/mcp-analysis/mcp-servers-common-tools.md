# MCP Servers - Commonly Used Tools Summary

**Purpose**: Consolidated overview of most commonly used MCP server tools
**Total MCP Servers**: 8 servers, ~85 tools
**Integration**: MCP Bridge (mapping_mcp_bridge.js) + Direct MCP SDK (Serena only)

---

## 1. Serena MCP (26 tools) - Direct Python MCP SDK

**Integration**: Direct Python MCP SDK via stdio (highest performance)
**Priority**: HIGH - Most comprehensive toolset
**See**: [serena-mcp-tools.md](../tool-inventory/serena-mcp-tools.md) for complete details

### Most Commonly Used (10 tools):

#### File Operations (3 tools)
1. **read_file** - Read file contents with path
2. **search_for_pattern** - Ripgrep-based pattern search
3. **list_dir** - List directory contents

#### LSP Symbol Operations (4 tools)
4. **get_symbols_overview** - Get all symbols in file/directory
5. **find_symbol** - Find symbol definition by name
6. **find_referencing_symbols** - Find all references to symbol
7. **replace_symbol_body** - Replace function/class body

#### Memory Management (2 tools)
8. **write_memory** - Store persistent memory
9. **read_memory** - Retrieve memory by ID

#### System Operations (1 tool)
10. **execute_shell_command** - Run shell commands

**Usage Priority**: HIGH
**Performance**: Fast (direct stdio communication)
**Best For**: Code analysis, symbol search, file operations

---

## 2. Context7 MCP (2 tools) - MCP Bridge

**Integration**: MCP Bridge (mapping_mcp_bridge.js)
**Priority**: HIGH - Documentation retrieval
**See**: [.claude/docs-cache/mcp-obsidian-docs.md](../../.claude/docs-cache/mcp-obsidian-docs.md)

### All Tools (2):

1. **resolve-library-id** - Convert library name to Context7 ID
   - Input: "nextjs" → Output: "/vercel/next.js"
   - **Usage**: Required before get-library-docs

2. **get-library-docs** - Fetch library documentation
   - Parameters: libraryID (required), topic (optional), tokens (default 5000)
   - **Usage**: Get up-to-date framework docs

**Usage Priority**: HIGH
**Performance**: Medium (external API call)
**Best For**: Framework documentation, API references, code examples

---

## 3. Sequential Thinking MCP (1 tool) - MCP Bridge

**Integration**: MCP Bridge (mapping_mcp_bridge.js)
**Priority**: MEDIUM - Complex reasoning
**See**: Integrated in MCP Bridge

### Single Tool:

1. **sequentialthinking** - Multi-step reasoning chain
   - Input: Question/task description
   - Output: Reasoning chain with intermediate steps
   - **Usage**: Complex analysis, problem decomposition

**Usage Priority**: MEDIUM
**Performance**: Slow (multiple LLM calls)
**Best For**: Complex multi-step analysis, structured problem decomposition

---

## 4. Filesystem MCP (13 tools) - MCP Bridge

**Integration**: MCP Bridge (mapping_mcp_bridge.js)
**Priority**: MEDIUM - File operations alternative
**See**: [01-filesystem-mcp-tools.md](../tool-inventory/01-filesystem-mcp-tools.md)

### Most Commonly Used (6 tools):

#### Read Operations (2 tools)
1. **read_text_file** - Read text file contents
2. **read_multiple_files** - Batch read multiple files

#### Write Operations (2 tools)
3. **write_file** - Create/overwrite file
4. **edit_file** - Search-replace editing

#### Directory Operations (1 tool)
5. **directory_tree** - Recursive directory structure

#### Search (1 tool)
6. **search_files** - Search files by name pattern

**Usage Priority**: MEDIUM (Claude Code built-in tools preferred)
**Performance**: Medium (MCP overhead)
**Best For**: MCP-only workflows, batch operations

---

## 5. Obsidian MCP (10+ tools estimated) - MCP Bridge

**Integration**: MCP Bridge (mapping_mcp_bridge.js)
**Priority**: MEDIUM - Note management
**See**: [.claude/docs-cache/mcp-obsidian-docs.md](../../.claude/docs-cache/mcp-obsidian-docs.md)

### Commonly Used Tools (estimated 6):

1. **list_files_in_dir** - List notes in vault directory
2. **get_file_contents** - Read note contents
3. **search** - Search notes by content/title
4. **patch_content** - Update note with diff
5. **append_content** - Add to note end
6. **create_file** - Create new note

**Usage Priority**: MEDIUM
**Performance**: Fast (local vault access)
**Best For**: Note-taking, knowledge base, markdown files

---

## 6. Chrome DevTools MCP (8+ tools estimated) - MCP Bridge

**Integration**: MCP Bridge (mapping_mcp_bridge.js)
**Priority**: MEDIUM - Browser automation
**See**: Story 1.6 usage

### Commonly Used Tools (estimated 6):

1. **new_page** - Launch browser page/tab
2. **navigate_to** - Navigate to URL
3. **take_snapshot** - DOM snapshot
4. **execute_javascript** - Run JS in page context
5. **list_console_messages** - Get console logs
6. **close_page** - Close page/tab

**Usage Priority**: MEDIUM (Story 1.6 specific)
**Performance**: Medium (browser automation overhead)
**Best For**: E2E testing, browser automation, DOM inspection

---

## 7. Sentry MCP (5+ tools estimated) - MCP Bridge

**Integration**: MCP Bridge (mapping_mcp_bridge.js)
**Priority**: LOW - Error tracking
**See**: Story 1.4 integration

### Commonly Used Tools (estimated 3):

1. **capture_error** - Log error to Sentry
2. **list_issues** - Get error list
3. **get_issue_details** - Error details and stack trace

**Usage Priority**: LOW (monitoring/logging)
**Performance**: Medium (external API)
**Best For**: Production error tracking, debugging

---

## 8. Postgres MCP Pro (10+ tools estimated) - MCP Bridge

**Integration**: MCP Bridge (mapping_mcp_bridge.js)
**Priority**: LOW - Database analysis
**See**: Story 1.4 comparison

### Commonly Used Tools (estimated 4):

1. **execute_query** - Run SQL query
2. **analyze_performance** - Query performance analysis
3. **get_schema** - Table structure
4. **explain_plan** - EXPLAIN output

**Usage Priority**: LOW (psycopg direct library preferred)
**Performance**: Medium (MCP overhead)
**Best For**: Query optimization, performance analysis

---

## Tool Usage Priority Matrix

| MCP Server | Tools | Priority | Performance | Use When |
|------------|-------|----------|-------------|----------|
| Serena | 26 | HIGH | Fast | Code analysis, symbol search |
| Context7 | 2 | HIGH | Medium | Framework docs, API refs |
| Sequential Thinking | 1 | MEDIUM | Slow | Complex reasoning |
| Filesystem | 13 | MEDIUM | Medium | MCP workflows only |
| Obsidian | 10+ | MEDIUM | Fast | Note management |
| Chrome DevTools | 8+ | MEDIUM | Medium | Browser automation |
| Sentry | 5+ | LOW | Medium | Error monitoring |
| Postgres MCP | 10+ | LOW | Medium | Query optimization |

---

## Integration Methods Comparison

### Direct Python MCP SDK (Serena only)
- **Speed**: Fastest (stdio)
- **Overhead**: Minimal
- **Setup**: Complex (MCP SDK)
- **Use**: Performance-critical operations

### MCP Bridge (All others)
- **Speed**: Medium (Node.js bridge)
- **Overhead**: Bridge + server startup
- **Setup**: Simpler (unified config)
- **Use**: Standard MCP integration

### Direct Python Libraries (Preferred)
- **Speed**: Fastest (no MCP)
- **Overhead**: None
- **Setup**: Simple (pip install)
- **Use**: Always preferred when available

---

## Recommended Tool Selection

### File Operations
1. **Claude Code Read/Write/Edit** (PREFERRED - fastest)
2. **Serena read_file** (code analysis context)
3. **Filesystem MCP** (MCP-only workflows)

### Code Search
1. **Claude Code Grep** (PREFERRED - ripgrep)
2. **Serena search_for_pattern** (LSP context)
3. **Serena find_symbol** (symbol-specific)

### Documentation
1. **docs-cache files** (PREFERRED - local, fast)
2. **Context7 get-library-docs** (up-to-date external docs)
3. **Claude Code WebFetch** (specific URLs)

### Web Search
1. **tavily-python** (PREFERRED - comprehensive research)
2. **Claude Code WebSearch** (quick lookups)
3. **Claude Code WebFetch** (single URL extraction)

### Database Operations
1. **psycopg** (PREFERRED - direct, fast)
2. **Postgres MCP** (query optimization analysis)

### GitHub Operations
1. **PyGithub** (PREFERRED - Python integration)
2. **gh CLI** (bulk operations, JSON output)
3. **git CLI** (repository operations)

### Knowledge Graph
1. **graphiti_core** (PREFERRED - direct library)
2. **Graphiti MCP** (if MCP workflow required)
3. **Obsidian MCP** (simple note linking)

---

## Testing Recommendations

### HIGH Priority MCP Tools (must test):
1. **Serena**: get_symbols_overview, find_symbol, search_for_pattern
2. **Context7**: resolve-library-id, get-library-docs
3. **Filesystem**: read_text_file, search_files, directory_tree

### MEDIUM Priority:
1. **Obsidian**: search, get_file_contents
2. **Chrome DevTools**: new_page, navigate_to, take_snapshot
3. **Sequential Thinking**: sequentialthinking

### LOW Priority:
1. **Sentry**: capture_error, list_issues
2. **Postgres MCP**: execute_query, analyze_performance

---

## Common Patterns

### Pattern 1: Code Analysis Workflow
```
1. Serena get_symbols_overview → Get file structure
2. Serena find_symbol → Locate specific definition
3. Serena find_referencing_symbols → Find usage
4. Serena replace_symbol_body → Update implementation
```

### Pattern 2: Documentation Research
```
1. docs-cache files → Check local docs first
2. Context7 resolve-library-id → Get library ID
3. Context7 get-library-docs → Fetch external docs
4. Serena write_memory → Store for future use
```

### Pattern 3: Knowledge Storage
```
1. tavily-python search → Research topic
2. graphiti_core add_episode → Store knowledge
3. graphiti_core search → Retrieve related knowledge
4. Serena write_memory → Cache frequently used
```

### Pattern 4: File Operations
```
1. Claude Code Glob → Find files by pattern
2. Claude Code Read → Read file contents
3. Claude Code Edit → Modify file
4. git CLI → Commit changes
```

---

## Performance Comparison

| Operation | Fastest | Medium | Slowest |
|-----------|---------|--------|---------|
| File read | Claude Code | Serena | Filesystem MCP |
| File search | Claude Code Grep | Serena search | Filesystem MCP |
| Code analysis | Serena symbols | Claude Code Grep | Manual grep |
| Documentation | docs-cache | Context7 | WebFetch |
| Web search | Claude Code | tavily basic | tavily advanced |
| Database | psycopg | - | Postgres MCP |
| GitHub | PyGithub | gh CLI | git CLI |

---

## Cost Comparison

| Tool Category | Free (Built-in) | Paid API | Infrastructure |
|---------------|----------------|----------|----------------|
| File operations | Claude Code | - | - |
| Code search | Claude Code, Serena | - | - |
| Documentation | docs-cache | Context7 | - |
| Web search | Claude Code | tavily-python | - |
| Database | psycopg | - | PostgreSQL |
| GitHub | git CLI, gh CLI | PyGithub API | - |
| Knowledge graph | - | graphiti_core LLM | Neo4j |
| Browser | - | - | Chrome |

---

## Summary

**Total MCP Tools**: ~85 across 8 servers
**Commonly Used**: 20-25 tools (80% of use cases)
**Preferred Approach**: Direct Python libraries > Claude Code built-in > MCP Bridge > External APIs

**Key Insight**: Most tasks can be accomplished with:
- 5 direct Python library methods (PyGithub, tavily, graphiti, psycopg, DSPy)
- 10 Claude Code built-in tools (Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch, git, gh)
- 5 high-priority MCP tools (Serena symbols, Context7 docs, Sequential Thinking)

**Recommendation**: Focus testing on 20-25 commonly used tools rather than all 390+ tools/commands.
