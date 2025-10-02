# Claude Code Built-in Tools

**Source**: Claude Code VSCode Extension (Native Tools)
**Total Tools**: 14 core tools + specialized agents

## Core File Operations (6 tools)

### 1. Read
- **Purpose**: Read files from filesystem
- **Key Parameters**:
  - `file_path` (string): Absolute path to file
  - `offset` (number, optional): Line number to start from
  - `limit` (number, optional): Number of lines to read
- **Features**:
  - Reads up to 2000 lines by default
  - Supports images (PNG, JPG), PDFs, Jupyter notebooks
  - Returns cat -n format with line numbers
  - Multimodal (can read and display images)
- **Use Cases**: Read source code, config files, images, PDFs, notebooks
- **Performance**: Direct filesystem access, very fast

### 2. Write
- **Purpose**: Create new files or overwrite existing
- **Key Parameters**:
  - `file_path` (string): Absolute path to file
  - `content` (string): File content
- **Features**:
  - Overwrites existing files
  - Requires prior Read for existing files
- **Use Cases**: Create new source files, config files
- **Performance**: Direct filesystem write

### 3. Edit
- **Purpose**: Exact string replacement in files
- **Key Parameters**:
  - `file_path` (string): File to modify
  - `old_string` (string): Text to replace
  - `new_string` (string): Replacement text
  - `replace_all` (boolean): Replace all occurrences
- **Features**:
  - Requires exact match
  - Preserves indentation
  - Must use Read before Edit
  - Fails if old_string not unique (unless replace_all)
- **Use Cases**: Code refactoring, bug fixes, updates
- **Performance**: Direct filesystem, pattern matching

### 4. Glob
- **Purpose**: Fast file pattern matching
- **Key Parameters**:
  - `pattern` (string): Glob pattern (e.g., "**/*.py")
  - `path` (string, optional): Directory to search
- **Features**:
  - Works with any codebase size
  - Returns sorted by modification time
  - Supports glob patterns
- **Use Cases**: Find files by name pattern
- **Performance**: Very fast, optimized for large codebases

### 5. Grep
- **Purpose**: Powerful search built on ripgrep
- **Key Parameters**:
  - `pattern` (string): Regex pattern
  - `path` (string, optional): File/directory to search
  - `glob` (string, optional): Filter files
  - `type` (string, optional): File type filter
  - `output_mode` (enum): "content" | "files_with_matches" | "count"
  - `-i` (boolean): Case insensitive
  - `-n` (boolean): Show line numbers
  - `-A`, `-B`, `-C` (number): Context lines
  - `multiline` (boolean): Cross-line patterns
- **Features**:
  - Full regex syntax
  - Context lines support
  - Multiple output modes
  - Multiline matching
- **Use Cases**: Code search, symbol finding, pattern matching
- **Performance**: Very fast (ripgrep-based)

### 6. NotebookEdit
- **Purpose**: Edit Jupyter notebook cells
- **Key Parameters**:
  - `notebook_path` (string): Absolute path to .ipynb
  - `cell_id` (string): Cell ID to edit
  - `new_source` (string): New cell content
  - `cell_type` (enum): "code" | "markdown"
  - `edit_mode` (enum): "replace" | "insert" | "delete"
- **Features**:
  - Cell-level editing
  - Insert/delete cells
  - Supports code and markdown cells
- **Use Cases**: Update Jupyter notebooks programmatically
- **Performance**: Direct .ipynb file manipulation

## Command Execution (1 tool)

### 7. Bash
- **Purpose**: Execute shell commands in persistent session
- **Key Parameters**:
  - `command` (string): Command to execute
  - `description` (string): 5-10 word description
  - `timeout` (number, optional): Max 600000ms (10 min)
  - `run_in_background` (boolean): Background execution
- **Features**:
  - Persistent shell session
  - 2-minute default timeout
  - Background execution support
  - Output limited to 30000 chars
- **Use Cases**: git, npm, docker, pytest, system commands
- **Performance**: Native shell execution
- **Security**: Proper quoting for paths with spaces

## Web Access (2 tools)

### 8. WebSearch
- **Purpose**: Search web and return formatted results
- **Key Parameters**:
  - `query` (string): Search query
  - `allowed_domains` (string[]): Domain whitelist
  - `blocked_domains` (string[]): Domain blacklist
- **Features**:
  - Returns search result blocks
  - Domain filtering
  - US-only availability
- **Use Cases**: Find current documentation, research libraries
- **Performance**: Single API call

### 9. WebFetch
- **Purpose**: Fetch and analyze web content
- **Key Parameters**:
  - `url` (string): URL to fetch
  - `prompt` (string): What to extract
- **Features**:
  - HTML to markdown conversion
  - AI-powered content extraction
  - 15-minute cache
  - Handles redirects
- **Use Cases**: Read documentation, extract specific info from pages
- **Performance**: Cached for repeated access

## Agent Execution (1 tool)

### 10. Task
- **Purpose**: Launch specialized agents for complex tasks
- **Key Parameters**:
  - `subagent_type` (string): Agent type to launch
  - `prompt` (string): Task for agent
  - `description` (string): 3-5 word task summary
- **Available Agents**:
  - `general-purpose`: Research, code search, multi-step tasks (all tools)
  - `statusline-setup`: Configure status line (Read, Edit)
  - `output-style-setup`: Create output style (Read, Write, Edit, Glob, Grep)
- **Features**:
  - Stateless execution
  - Single result message
  - Can launch multiple agents in parallel
- **Use Cases**: Complex research, multi-step workflows, open-ended search
- **Performance**: Parallel execution support

## Task Management (1 tool)

### 11. TodoWrite
- **Purpose**: Create and manage structured task lists
- **Key Parameters**:
  - `todos` (array): List of todo items
    - `content` (string): Task description (imperative)
    - `status` (enum): "pending" | "in_progress" | "completed"
    - `activeForm` (string): Present continuous form
- **Features**:
  - Real-time task tracking
  - EXACTLY ONE task in_progress at a time
  - User-visible progress
- **Use Cases**: Multi-step tasks (3+ steps), complex workflows
- **Performance**: Instant state updates

## Git Integration (2 tools)

### 12. SlashCommand
- **Purpose**: Execute VSCode slash commands
- **Key Parameters**:
  - `command` (string): Command with arguments (e.g., "/review-pr 123")
- **Features**:
  - Access to available slash commands
  - Command validation
- **Use Cases**: PR reviews, custom workflow commands
- **Performance**: Direct VSCode integration

### 13. BashOutput
- **Purpose**: Retrieve output from background bash shells
- **Key Parameters**:
  - `bash_id` (string): Shell ID to monitor
  - `filter` (string, optional): Regex to filter lines
- **Features**:
  - Returns only new output since last check
  - Regex filtering
  - Monitor long-running processes
- **Use Cases**: Monitor builds, long tests, background processes
- **Performance**: Efficient incremental reads

### 14. KillShell
- **Purpose**: Terminate background bash shells
- **Key Parameters**:
  - `shell_id` (string): Shell to kill
- **Features**:
  - Clean termination
  - Success/failure status
- **Use Cases**: Stop runaway processes, cleanup
- **Performance**: Immediate termination

## Plan Mode Tool

### 15. ExitPlanMode
- **Purpose**: Exit plan mode after presenting implementation plan
- **Key Parameters**:
  - `plan` (string): Implementation plan (markdown)
- **Features**:
  - Only for code implementation planning (not research)
  - Prompts user to exit plan mode
- **Use Cases**: Present implementation plans before coding
- **Performance**: N/A (mode transition)

## Git CLI Commands (via Bash tool)

**Available via**: `Bash` tool
**Total Commands**: 30+ common commands

### Repository Setup
- `git init` - Create empty repository
- `git clone <url>` - Clone repository

### Working Area
- `git add <files>` - Stage files
- `git mv <source> <dest>` - Move/rename files
- `git restore <file>` - Restore working tree files
- `git rm <file>` - Remove files

### History & State
- `git status` - Show working tree status
- `git diff [options]` - Show changes
- `git log [options]` - Show commit logs
- `git show <object>` - Show object details
- `git grep <pattern>` - Search repository
- `git bisect` - Binary search for bug

### Branches & Tags
- `git branch [options]` - List/create/delete branches
- `git switch <branch>` - Switch branches
- `git checkout <branch>` - Switch branches (legacy)
- `git tag <name>` - Create/list tags

### Commits & History
- `git commit [options]` - Record changes
- `git merge <branch>` - Merge branches
- `git rebase <base>` - Reapply commits
- `git reset [options]` - Reset HEAD
- `git stash [options]` - Stash changes

### Collaboration
- `git fetch [remote]` - Download objects/refs
- `git pull [remote]` - Fetch and integrate
- `git push [remote]` - Update remote refs

### Advanced
- `git cherry-pick <commit>` - Apply commit
- `git revert <commit>` - Revert commit
- `git backfill` - Download missing objects (partial clone)

## GitHub CLI (gh) Commands (via Bash tool)

**Available via**: `Bash` tool
**Total Commands**: 50+ commands across 15 categories

### Core Commands
- `gh auth login/logout/status` - Authenticate
- `gh browse [options]` - Open in browser
- `gh repo create/clone/list/view/delete` - Manage repositories
- `gh pr create/list/view/checkout/merge/close` - Manage pull requests
- `gh issue create/list/view/close` - Manage issues
- `gh release create/list/view/delete` - Manage releases
- `gh gist create/list/view` - Manage gists
- `gh org list/view` - Manage organizations
- `gh project list/view` - Work with GitHub Projects
- `gh codespace create/list/ssh` - Manage codespaces

### GitHub Actions
- `gh run list/view/watch/cancel` - View workflow runs
- `gh workflow list/view/run/enable/disable` - Manage workflows
- `gh cache list/delete` - Manage Actions caches

### Additional Commands
- `gh api <endpoint>` - Make authenticated API requests
- `gh search repos/issues/prs` - Search GitHub
- `gh secret list/set/remove` - Manage secrets
- `gh variable list/set/remove` - Manage variables
- `gh label create/list/delete` - Manage labels
- `gh gpg-key list/add/delete` - Manage GPG keys
- `gh ssh-key list/add/delete` - Manage SSH keys
- `gh alias list/set/delete` - Create command shortcuts
- `gh extension install/list/remove` - Manage extensions
- `gh ruleset list/view` - View repo rulesets
- `gh attestation verify` - Work with artifact attestations

### Key Features
- **Authenticated Requests**: `gh api repos/{owner}/{repo}/pulls`
- **Bulk Operations**: `gh pr list --state all --limit 100`
- **JSON Output**: `gh pr view --json title,body,state`
- **Interactive Mode**: `gh pr create` (interactive prompts)
- **Browser Integration**: `gh pr view --web`

## Tool Comparison Notes

### File Reading
- **Claude Code Read**: Best for source code, images, PDFs, notebooks (multimodal)
- **Bash cat**: Best for simple text files, piping
- **Filesystem MCP read_text_file**: Alternative for MCP-based workflows

### File Search
- **Claude Code Glob**: Best for name-based file finding (fastest)
- **Claude Code Grep**: Best for content-based search (ripgrep)
- **Bash find**: Best for complex criteria (size, date, permissions)
- **Filesystem MCP search_files**: Alternative for MCP workflows

### Web Research
- **Claude Code WebSearch**: Best for quick searches, current info
- **Claude Code WebFetch**: Best for targeted content extraction
- **tavily-python**: Best for comprehensive research, multiple sources

### GitHub Operations
- **PyGithub**: Best for programmatic API access (Python)
- **gh CLI**: Best for bulk operations, JSON output, interactive workflows
- **git CLI**: Best for repository operations (commits, branches, merges)

### Command Execution
- **Bash**: Only option for shell commands
- **Bash (background)**: Best for long-running processes
- **BashOutput**: Monitor background processes

## Performance Characteristics

| Tool | Access Method | Speed | Token Efficiency |
|------|--------------|-------|------------------|
| Read | Direct filesystem | Very fast | High (reads only needed lines) |
| Write | Direct filesystem | Very fast | High (single write) |
| Edit | Direct filesystem | Fast | High (only changes) |
| Glob | Direct filesystem | Very fast | High (returns paths only) |
| Grep | Ripgrep | Very fast | Configurable (content/files/count) |
| Bash | Shell execution | Fast | Low (streams full output) |
| WebSearch | API call | Medium | Medium (formatted results) |
| WebFetch | HTTP + cache | Medium-Fast | Medium (cached 15min) |
| Task | Agent spawn | Slow | Low (full agent context) |
| TodoWrite | State update | Instant | Very low (minimal JSON) |
| git CLI | Shell execution | Fast | Low (full git output) |
| gh CLI | GitHub API | Medium | Configurable (--json flag) |
| SlashCommand | VSCode | Fast | N/A |

## Tool Selection Priority

**For file operations**:
1. Read/Write/Edit (built-in) - Always prefer for direct file access
2. Glob/Grep (built-in) - Always prefer for search
3. Filesystem MCP - Only when MCP workflow required
4. Bash cat/find - Only for specific shell needs

**For web research**:
1. WebSearch (built-in) - Quick lookups
2. WebFetch (built-in) - Targeted extraction
3. tavily-python - Comprehensive research

**For GitHub**:
1. PyGithub - Programmatic Python code
2. gh CLI - Bulk operations, JSON output
3. git CLI - Repository operations

**For complex tasks**:
1. Direct implementation - Always try first
2. Task agent - Only for open-ended research, multi-round search

## Total Tool Count

- **Core Claude Code Tools**: 15 (Read, Write, Edit, Glob, Grep, NotebookEdit, Bash, WebSearch, WebFetch, Task, TodoWrite, SlashCommand, BashOutput, KillShell, ExitPlanMode)
- **git CLI Commands**: ~30 commonly used
- **gh CLI Commands**: ~50 across all categories
- **TOTAL**: ~95 built-in tools/commands

**Note**: git and gh commands are executed via the Bash tool, so they count as extensions of the Bash tool's capabilities rather than separate tools in Claude Code's tool registry.
