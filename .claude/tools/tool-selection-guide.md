# Tool Selection Guide

## Streaming Tools

**Tool Selection Matrix - Native vs MCP Tools**:

| Operation Type | When to Use | Best Function | Source | Frequency | Reason |
|---------------|-------------|---------------|--------|-----------|---------|
| **File Reading** | Reading single files, code analysis | `Read` | Claude Code | 5 | lowest token cost |
| **Bulk File Reading** | Multiple files simultaneously | `read_multiple_files` | filesystem MCP | 4 | atomic operations |
| **File Writing** | Creating/overwriting files | `Write` | Claude Code | 4 | validation built-in |
| **File Editing** | Selective modifications | `Edit/MultiEdit` | Claude Code | 5 | precise control |
| **Directory Operations** | Creating/listing directories | `Bash` (mkdir/ls) | Claude Code | 3 | performance |
| **File Search** | Finding files by pattern | `Glob/Grep` | Claude Code | 4 | flexibility |
| **Symbol Search** | Finding code symbols semantically | `find_symbol` | serena MCP | 4 | precise symbol targeting |
| **Code Analysis** | Symbol dependencies/references | `find_referencing_symbols` | serena MCP | 3 | automated cross-reference |
| **Semantic Editing** | Symbol-aware code insertion | `insert_after_symbol` | serena MCP | 3 | context-aware modifications |
| **Multi-Language Support** | Universal language analysis | `LSP integration` | serena MCP | 4 | 20+ language support |
| **Local Git Status** | Check working directory | `git_status` | git MCP | 5 | structured output |
| **Local Git Commits** | Development commits | `Bash` (git commit) | Claude Code | 5 | direct control |
| **Local Git Branches** | Branch management | `git_create_branch/git_checkout` | git MCP | 4 | workflow integration |
| **Local Git Diffs** | Code changes analysis | `git_diff_unstaged/git_diff_staged` | git MCP | 4 | structured parsing |
| **GitHub Repository Creation** | New repo setup | `Bash` (gh repo create) | Claude Code | 2 | simpler execution |
| **GitHub Issues** | Issue management | `Bash` (gh issue) | Claude Code | 3 | lower overhead |
| **GitHub Pull Requests** | PR workflows | `Bash` (gh pr create) | Claude Code | 4 | direct control |
| **GitHub Repository Search** | Finding repositories | `search_repositories` | github MCP | 2 | AI integration |
| **Remote Git Operations** | Push/pull/fetch | `Bash` (git push/pull) | Claude Code | 4 | direct control |
| **GitHub API Operations** | Complex GitHub tasks | `github MCP` | github MCP | 3 | structured responses |
| **File System Security** | Permission validation | `list_allowed_directories` | filesystem MCP | 2 | safety features |



| **Cross-platform Operations** | OS-agnostic tasks | `filesystem MCP` | filesystem MCP | 3 | portability |
| **Performance Critical** | High-frequency operations | `Bash` | Claude Code | 4 | fastest execution |
| **AI-Integrated Workflows** | Natural language ops | `MCP tools` | MCP | 3 | AI consumption optimized |
| **Simple Automation** | Basic scripting | `Bash` | Claude Code | 5 | simplicity |
| **Structured Data Processing** | JSON responses needed | `MCP tools` | MCP | 3 | data consistency |
| **State Management** | Multi-step operations | `MCP tools` | MCP | 2 | operation tracking |
| **Development Debugging** | Local troubleshooting | `Bash` | Claude Code | 4 | direct access |
| **Team Collaboration** | Shared workflows | `github MCP` | github MCP | 3 | integration features |

**Decision Framework**:
1. **Start Native**: Use built-in tools for single operations
2. **Scale to MCP**: Switch when batch operations or advanced features needed
3. **IDE Context**: Always use MCP tools for IDE-integrated operations
4. **Semantic Operations**: Use serena MCP for symbol-level code understanding
5. **Research Tasks**: Prefer context7 MCP for structured analysis workflows

## Serena MCP Integration Guidelines
**When to Use Serena**:
- Large codebases (>10k LOC) requiring semantic navigation
- Multi-language projects needing unified analysis
- Symbol-level refactoring operations
- Cross-reference dependency analysis
- IDE-like code understanding without IDE

**When to Skip Serena**:
- Simple text-based operations
- Single file basic edits
- Performance-critical file operations
- Basic CRUD tasks

**Hybrid Approach**: Combine serena semantic tools with native file operations for optimal workflow.

## Sequential Thinking Tool Selection

| Scenario | Use Sequential Thinking | Skip Sequential Thinking | Reason |
|----------|------------------------|--------------------------|---------|
| **Complex feature planning** | ✅ | ❌ | Multi-step analysis prevents rework |
| **Architecture decisions** | ✅ | ❌ | Trade-off evaluation critical |
| **Debugging (unknown cause)** | ✅ | ❌ | Systematic root cause analysis |
| **Performance optimization** | ✅ | ❌ | Multiple bottleneck factors |
| **Security analysis** | ✅ | ❌ | Threat modeling required |
| **Simple CRUD operations** | ❌ | ✅ | Overhead not justified |
| **Bug fixes (obvious cause)** | ❌ | ✅ | Direct action preferred |
| **Following existing patterns** | ❌ | ✅ | Template approach faster |

**Triggered by Keywords**: "How should I approach...", "What's the best way to...", "This is complex...", "Multiple options...", "Trade-offs between..."

## Integration with 7-Parallel-Task Workflow
1. User requests complex feature → Use sequential thinking to analyze approach
2. Generate optimal task breakdown from analysis → Launch 7 parallel tasks
3. During task execution: If complexity increases → Use sequential thinking

**Performance Impact**: 30-60 seconds thinking time vs potential hours of rework from suboptimal approaches

## Terminal Management Protocol

**When to Use Multiple Panels/Windows**:
- **Multi-Agent Execution**: Planning + Research + Dev + PM agents running simultaneously
- **Long-Running Processes**: Bloomberg data streams + LangGraph execution + log monitoring
- **Development Workflows**: Tests running + build processes + error monitoring
- **Debugging Sessions**: Multiple log files + runtime state + configuration checks

**Auto-Trigger Scenarios** (Claude suggests panels):
- User requests "run multi-agent workflow"
- Complex development tasks with >3 concurrent processes
- Bloomberg integration testing (API + data + logs)

**Contextual Labeling Approach**:
- Label commands by context: "Bloomberg Monitor:", "Agent Execution:", "Build Process:"
- Humans organize panels around Claude's contextual labels
- No mandatory panel management - suggestion only

## MCP Integration

### Primary Method - mcp-use Library
- **Usage**: Create custom agents that connect any LLM to tools from multiple MCP servers
- **Architecture**: TypeScript/JavaScript library for programmatic MCP integration
- **Documentation**: agent check `.claude/docs-cache/mcp-use-docs.md` before going external using context7 mcp

### Secondary Method - Claude Code Native
- Use `claude mcp add` for direct Claude Code MCP server integration
- Limited to single-server contexts

## Essential Tools List
**Dynamic Tool Prioritization**: The framework maintains a essential list for each agent of most-used tools from different servers. Log usage for different tools and bi-weekly review to suggest tools to be included into essential list. Use internet to research and propose the best new tools or technology.