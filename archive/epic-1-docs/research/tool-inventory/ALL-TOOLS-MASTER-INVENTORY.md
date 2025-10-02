# Master Tool Inventory - All Available Tools

**Purpose**: Complete inventory of all tools available for testing
**Date**: 2025-10-02
**Status**: Ready for test design

---

## Tool Categories

1. **Claude Code Built-in Tools** - Native tools in Claude Code
2. **Direct Python Libraries** - PyGithub, tavily-python, graphiti_core, dspy, psycopg
3. **MCP Servers** - Serena, Context7, Sequential Thinking, Obsidian, Filesystem, Chrome DevTools, Sentry, Postgres

---

## 1. Claude Code Built-in Tools

**Total**: 15 core tools + ~80 CLI commands (git ~30, gh ~50)
**See**: [claude-code-builtin-tools.md](claude-code-builtin-tools.md) for complete details

### Core File Operations (6 tools)
1. **Read** - Read files with line numbers, images, PDFs, notebooks
2. **Write** - Create/overwrite files
3. **Edit** - Pattern-based exact string replacement
4. **Glob** - Fast file pattern matching (glob patterns)
5. **Grep** - Powerful content search (ripgrep-based, regex, multiline)
6. **NotebookEdit** - Edit Jupyter notebook cells

### Command Execution (1 tool)
7. **Bash** - Execute shell commands in persistent session, background execution support

### Web Access (2 tools)
8. **WebSearch** - Web search with domain filtering
9. **WebFetch** - Fetch and analyze web content with AI, 15-min cache

### Agent Execution (1 tool)
10. **Task** - Launch specialized agents (general-purpose, statusline-setup, output-style-setup)

### Task Management (1 tool)
11. **TodoWrite** - Create and manage structured task lists with real-time tracking

### Git Integration (2 tools)
12. **SlashCommand** - Execute VSCode slash commands
13. **BashOutput** - Retrieve output from background shells

### Background Shell Management (1 tool)
14. **KillShell** - Terminate background bash shells

### Plan Mode (1 tool)
15. **ExitPlanMode** - Exit plan mode after presenting implementation plan

### git CLI Commands (via Bash)
**Total**: ~30 common commands
**See**: [git-cli-commands.md](git-cli-commands.md) for complete list

**Categories**:
- Repository setup: `init`, `clone`
- Working area: `add`, `mv`, `restore`, `rm`
- History & state: `status`, `diff`, `log`, `show`, `grep`, `bisect`
- Branches & tags: `branch`, `switch`, `checkout`, `tag`
- Commits: `commit`, `merge`, `rebase`, `reset`, `stash`
- Collaboration: `fetch`, `pull`, `push`, `remote`
- Advanced: `cherry-pick`, `revert`, `backfill`, `config`, `clean`, `blame`, `reflog`

### gh CLI Commands (via Bash)
**Total**: ~50 commands, 200+ total operations
**See**: [gh-cli-commands.md](gh-cli-commands.md) for complete list

**Core Commands**: `auth`, `repo`, `pr`, `issue`, `release`, `gist`, `browse`, `org`, `project`, `codespace`
**Actions**: `run`, `workflow`, `cache`
**Additional**: `api`, `search`, `secret`, `variable`, `label`, `gpg-key`, `ssh-key`, `alias`, `extension`, `ruleset`, `attestation`, `config`, `completion`, `status`

**Key Features**:
- JSON output: `--json <fields>` for structured data
- jq integration: `--jq` for filtering
- Bulk operations: `--paginate`, `--limit`
- Interactive workflows: prompts and confirmations

---

## 2. Direct Python Libraries

### PyGithub (Github class)
**Total Methods**: 50+ across multiple classes

**Main Classes**:
1. **Github**: `get_repo()`, `get_organization()`, `get_user()`, `search_repositories()`
2. **Repository**: `get_issues()`, `create_issue()`, `get_pulls()`, `create_pull()`, `get_branches()`, `get_commits()`, `get_contents()`, `create_file()`, `update_file()`
3. **PullRequest**: `get_comments()`, `create_comment()`, `get_commits()`, `edit()`, `add_to_assignees()`, `merge()`
4. **Issue**: `get_comments()`, `create_comment()`, `edit()`, `add_to_labels()`, `lock()`, `unlock()`
5. **Commit**: `get_comments()`, `create_comment()`, `get_check_runs()`
6. **User**: `get_repo()`, `get_repos()`, `get_issues()`
7. **Organization**: `get_repos()`, `create_repo()`, `get_members()`, `get_teams()`

**MADF Implementation** ([src/integrations/github_client.py](../../src/integrations/github_client.py)):
- `search_repos()`, `get_repo()`, `list_repos()`, `get_repo_contents()`
- `get_pr()`, `list_prs()`, `create_pr()`, `update_pr()`, `merge_pr()`
- `get_issue()`, `list_issues()`, `create_issue()`, `update_issue()`, `add_issue_comment()`
- `get_file_contents()`, `create_or_update_file()`, `delete_file()`
- `list_commits()`, `get_commit()`

---

### tavily-python (TavilyClient)
**Total Methods**: 5 main methods

**Methods**:
1. **search()** - Web search with advanced options
   - Parameters: query, max_results, search_depth, include_answer, include_raw_content, include_domains, exclude_domains
2. **qna_search()** - Q&A optimized search
   - Parameters: query
3. **get_search_context()** - RAG context retrieval
   - Parameters: query, max_results, search_depth, max_tokens
4. **extract()** - Content extraction from URLs
   - Parameters: urls, extract_depth, format, include_images
5. **crawl()** - Multi-page crawling
   - Parameters: url, max_depth, max_breadth, instructions

**MADF Implementation** ([src/integrations/tavily_client.py](../../src/integrations/tavily_client.py)):
- `search()`, `qna_search()`, `get_search_context()`, `extract()`

---

### graphiti_core (Graphiti class)
**Total Methods**: 10+ knowledge graph methods

**Main Methods**:
1. **add_episode()** - Store knowledge episodes
2. **search_nodes()** - Search graph nodes
3. **search_facts()** - Search facts
4. **search_episodes()** - Search episodes
5. **get_episode_by_id()** - Retrieve specific episode
6. **update_episode()** - Modify episode
7. **delete_episode()** - Remove episode
8. **get_temporal_state()** - Query at specific time
9. **traverse_graph()** - Graph traversal

**Note**: Requires Neo4j database

---

### dspy-ai (DSPy)
**Total Methods**: 20+ self-improvement methods

**Core Classes**:
1. **Signature** - Task definitions
2. **Module** - Reusable components
3. **Optimizer** - Self-improvement (`optimize()`, `evaluate()`)
4. **ChainOfThought** - Reasoning module
5. **ReAct** - Reasoning + Acting
6. **Compile** - Optimize signatures

---

### psycopg (Postgres direct)
**Total Methods**: 50+ database methods

**Main Classes**:
1. **Connection**: `execute()`, `commit()`, `rollback()`, `cursor()`
2. **Cursor**: `execute()`, `fetchone()`, `fetchall()`, `fetchmany()`
3. **Transaction management**
4. **Connection pooling**

---

## 3. MCP Servers

### Serena MCP (26 tools)
**Integration**: Direct Python MCP SDK (stdio)

**Categories**:
1. **File Operations** (6 tools):
   - `read_file`, `create_text_file`, `list_dir`, `find_file`, `replace_regex`, `search_for_pattern`

2. **LSP Symbol Operations** (6 tools):
   - `get_symbols_overview`, `find_symbol`, `find_referencing_symbols`
   - `replace_symbol_body`, `insert_after_symbol`, `insert_before_symbol`

3. **Memory Management** (4 tools):
   - `write_memory`, `read_memory`, `list_memories`, `delete_memory`

4. **System Operations** (7 tools):
   - `execute_shell_command`, `activate_project`, `switch_modes`, `get_current_config`
   - `check_onboarding_performed`, `onboarding`, `prepare_for_new_conversation`

5. **Thinking Tools** (3 tools):
   - `think_about_collected_information`, `think_about_task_adherence`, `think_about_whether_you_are_done`

**Most Used** (per MADF usage):
- `get_symbols_overview`, `find_symbol`, `find_referencing_symbols`, `search_for_pattern`, `read_file`

---

### Context7 MCP (2 tools)
**Integration**: MCP Bridge (mapping_mcp_bridge.js)

**Tools**:
1. **resolve-library-id** - Convert library name to Context7 ID
   - Parameters: libraryName (required)
   - Example: "nextjs" → "/vercel/next.js"

2. **get-library-docs** - Fetch library documentation
   - Parameters: context7CompatibleLibraryID (required), topic (optional), tokens (optional, default 5000)
   - Example: `/mongodb/docs` with topic "aggregation"

**Use Cases**:
- Fetch up-to-date library documentation
- Get API references for external packages
- Retrieve code examples from official docs

---

### Sequential Thinking MCP (1 tool)
**Integration**: MCP Bridge (mapping_mcp_bridge.js)

**Tool**:
1. **sequentialthinking** - Multi-step reasoning
   - Parameters: question/task description
   - Returns: Reasoning chain with intermediate steps

**Use Cases**:
- Complex multi-step analysis
- Structured problem decomposition
- Thought chain tracking

---

### Filesystem MCP (13 tools)
**Integration**: MCP Bridge (mapping_mcp_bridge.js)
**See**: [01-filesystem-mcp-tools.md](01-filesystem-mcp-tools.md) for complete list

**Categories**:
1. **Read** (3): `read_text_file`, `read_media_file`, `read_multiple_files`
2. **Write** (2): `write_file`, `edit_file`
3. **Directory** (4): `create_directory`, `list_directory`, `list_directory_with_sizes`, `directory_tree`
4. **File Management** (2): `move_file`, `get_file_info`
5. **Search** (1): `search_files`
6. **Access Control** (1): `list_allowed_directories`

**Most Useful**:
- `read_text_file`, `write_file`, `edit_file`, `search_files`, `directory_tree`

---

### Obsidian MCP (10+ tools - estimated)
**Integration**: MCP Bridge (mapping_mcp_bridge.js)

**Expected Tools** (based on typical Obsidian MCP):
1. `list_files_in_dir` - List notes in vault
2. `get_file_contents` - Read note
3. `search` - Search notes
4. `patch_content` - Update note
5. `append_content` - Add to note
6. `delete_file` - Remove note
7. `create_file` - New note
8. `get_metadata` - Note frontmatter
9. `list_tags` - Tag search
10. `graph_view` - Note connections

---

### Chrome DevTools MCP (8+ tools - estimated)
**Integration**: MCP Bridge (mapping_mcp_bridge.js)

**Expected Tools** (based on Story 1.6 usage):
1. `new_page` - Launch browser page
2. `navigate_to` - Navigate URL
3. `take_snapshot` - DOM snapshot
4. `take_screenshot` - Visual snapshot
5. `list_console_messages` - Console logs
6. `execute_javascript` - Run JS code
7. `get_dom_tree` - DOM structure
8. `close_page` - Close page

**Use Cases**:
- Browser automation testing
- DOM inspection
- Console debugging
- Screenshot capture

---

### Sentry MCP (5+ tools - estimated)
**Integration**: MCP Bridge (mapping_mcp_bridge.js)

**Expected Tools**:
1. `capture_error` - Log error
2. `list_issues` - Get error list
3. `get_issue_details` - Error details
4. `resolve_issue` - Mark resolved
5. `search_issues` - Search errors

---

### Postgres MCP Pro (10+ tools - estimated)
**Integration**: MCP Bridge (mapping_mcp_bridge.js)

**Expected Tools**:
1. `execute_query` - Run SQL
2. `analyze_performance` - Query analysis
3. `get_schema` - Table structure
4. `optimize_query` - Optimization suggestions
5. `explain_plan` - EXPLAIN output
6. `list_tables` - Schema tables
7. `get_table_stats` - Table statistics
8. `index_recommendations` - Index suggestions

---

## Total Tool Count

| Category | Tools | Integration Method |
|----------|-------|-------------------|
| Claude Code Built-in | 15 core tools | Native |
| git CLI | ~30 commands | Native (via Bash tool) |
| gh CLI | ~50 commands, 200+ operations | Native (via Bash tool) |
| PyGithub | 50+ methods | Direct Python |
| tavily-python | 5 methods | Direct Python |
| graphiti_core | 10+ methods | Direct Python |
| dspy-ai | 20+ methods | Direct Python |
| psycopg | 50+ methods | Direct Python |
| Serena MCP | 26 tools | Direct Python MCP SDK |
| Context7 MCP | 2 tools | MCP Bridge |
| Sequential Thinking MCP | 1 tool | MCP Bridge |
| Filesystem MCP | 13 tools | MCP Bridge |
| Obsidian MCP | 10+ tools | MCP Bridge |
| Chrome DevTools MCP | 8+ tools | MCP Bridge |
| Sentry MCP | 5+ tools | MCP Bridge |
| Postgres MCP Pro | 10+ tools | MCP Bridge |

**Grand Total**: ~390+ individual tools/functions/commands

**Breakdown**:
- Claude Code Native: 15 core + 30 git + 50 gh = 95 tools/commands
- Direct Python Libraries: ~135 methods
- MCP Servers: ~85 tools
- **Total**: 315-390 tools (conservative to high estimate)

---

## Tool Testing Priority

### High Priority (Daily Use)
1. File operations (Read, Write, Edit, Grep, Filesystem MCP, Serena file tools)
2. Code search (Grep, Serena symbol search, PyGithub code search)
3. Web search (WebSearch, tavily-python)
4. GitHub operations (PyGithub, GitHub MCP)

### Medium Priority (Frequent Use)
1. Documentation (Context7, docs-cache files, WebFetch)
2. Knowledge graphs (graphiti_core, Graphiti MCP)
3. Note management (Obsidian MCP, Filesystem MCP)
4. Browser testing (Chrome DevTools MCP)

### Low Priority (Specialized)
1. Complex reasoning (Sequential Thinking MCP)
2. Error tracking (Sentry MCP)
3. Database ops (Postgres MCP, psycopg)
4. Test optimization (DSPy)

---

## Next Steps

1. Design function-level tests for high-priority tools
2. Create comparative scenarios (e.g., Claude Code Read vs Filesystem MCP read_text_file vs Serena read_file)
3. Define metrics per tool category
4. Build test framework in `tests/research/`
5. Execute tests and collect data
