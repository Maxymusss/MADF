# Tool Selection Optimization Rules

**Reference**: For detailed MCP function documentation, see `.claude/docs/mcp-functions-reference.md`

## Quick Reference Matrix

| Operation | File Count | Condition | Tool Choice | Reasoning |
|-----------|------------|-----------|-------------|-----------|
| **Read** | 1 | Any size | `Read` | Fastest, direct execution |
| **Read** | 2-3 | <2k lines each | `Read` (multiple calls) | Simple, predictable |
| **Read** | 2-3 | >2k lines or unknown | `mcp__filesystem__read_multiple_files` | Batch efficiency |
| **Read** | 4+ | Any size | `mcp__filesystem__read_multiple_files` | Always more efficient |
| **Edit** | 1 | Single replacement | `Edit` | Simple, fast |
| **Edit** | 1 | Multiple changes | `mcp__filesystem__edit_file` | Git-style diffs, preview |
| **Edit** | Multiple | Cross-file changes | `MultiEdit` or batch MCP | Depends on complexity |
| **Search** | - | Name patterns | `Glob` | Fast file discovery |
| **Search** | - | Content search | `Grep` | Optimized for content |
| **Search** | - | Complex filters/excludes | `mcp__filesystem__search_files` | Advanced capabilities |
| **Directory** | - | Simple listing | `Bash(ls)` or built-in | Quick overview |
| **Directory** | - | Structured analysis | `mcp__filesystem__directory_tree` | JSON hierarchy |
| **Metadata** | - | File info needed | `mcp__filesystem__get_file_info` | Detailed stats |

## Detailed Decision Trees

### File Reading Operations

```
Need to read files?
├── 1 file
│   └── Use: Read
├── 2-3 files
│   ├── All small (<2k lines) → Use: Read (multiple calls)
│   ├── Large or unknown size → Use: mcp__filesystem__read_multiple_files
│   └── Need metadata first → Use: mcp__filesystem__get_file_info, then decide
└── 4+ files
    └── Use: mcp__filesystem__read_multiple_files
```

### File Editing Operations

```
Need to edit files?
├── Single file
│   ├── One simple replacement → Use: Edit
│   ├── Multiple changes → Use: mcp__filesystem__edit_file (with dryRun)
│   └── Complex refactoring → Use: mcp__filesystem__edit_file
├── Multiple files
│   ├── Same pattern across files → Use: MultiEdit
│   ├── Different changes per file → Use: batch mcp__filesystem__edit_file
│   └── Cross-file dependencies → Use: MultiEdit with careful ordering
└── New file creation
    └── Use: Write (unless part of batch operation)
```

### Search Operations

```
Need to find files/content?
├── Find files by name
│   ├── Simple patterns (*.js, src/**) → Use: Glob
│   └── Complex patterns with excludes → Use: mcp__filesystem__search_files
├── Find content in files
│   ├── Simple text search → Use: Grep
│   ├── Regex patterns → Use: Grep
│   └── Search with file type filters → Use: mcp__filesystem__search_files
└── Directory exploration
    ├── Quick overview → Use: Bash(ls) or built-in
    └── Structured analysis → Use: mcp__filesystem__directory_tree
```

## Performance Benchmarks

### API Call Efficiency

| Scenario | Built-in Tools | MCP Tools | Efficiency Gain |
|----------|----------------|-----------|-----------------|
| Read 1 file | 1 call | 1 call | 0% |
| Read 5 files | 5 calls | 1 call | 80% |
| Edit 3 changes in 1 file | 3 calls | 1 call | 67% |
| Search + read results | 2+ calls | 1-2 calls | 25-50% |

### Context Token Usage

| Operation | Built-in | MCP | Notes |
|-----------|----------|-----|-------|
| Single file read | Lower | Higher | MCP has verbose function names |
| Multiple file read | Higher | Lower | Batch operations save context |
| Complex search | Higher | Lower | Single call vs multiple operations |

### Speed Considerations

- **Built-in tools**: Faster for simple, single operations
- **MCP tools**: Faster for batch operations (fewer round trips)
- **Break-even point**: ~2-3 operations favor MCP tools
- **Network latency**: MCP tools reduce total latency for multi-step operations

## Context Efficiency Guidelines

### When to Prefer Built-in Tools
- Single file operations
- Simple, well-defined tasks
- When function name verbosity matters
- Quick exploratory operations

### When to Prefer MCP Tools
- Multi-file operations
- Complex search requirements
- When you need structured output (JSON)
- Batch operations with preview capability
- When file metadata is important

### Token Optimization Strategies
1. **Batch related operations** - Group file reads, searches, edits
2. **Use preview modes** - `dryRun` for edits to verify before applying
3. **Structure output** - JSON responses are more parseable than text
4. **Reduce round trips** - One complex MCP call vs multiple simple calls

## Integration with Workflows

### Feature Implementation (7-Parallel-Task Method)

**Task Assignment with Tool Optimization:**
1. **Component Task**: Use built-in tools for single file creation
2. **Styles Task**: Use MCP if updating multiple CSS files
3. **Tests Task**: Use MCP for batch test file creation
4. **Types Task**: Use built-in for single type files
5. **Hooks Task**: Use built-in for individual utility files
6. **Integration Task**: Use MCP for multi-file updates (routes, imports)
7. **Remaining Task**: Use MCP for batch config/doc updates

### Agent Tool Preferences

**Senior Development Agent:**
- Prefers MCP tools for complex multi-file operations
- Uses built-in tools for focused, single-file changes
- Always uses `dryRun` mode for edit previews

**Performance Optimization Agent:**
- Heavily favors MCP batch operations
- Uses `mcp__filesystem__get_file_info` for size analysis
- Prefers `mcp__filesystem__search_files` for pattern analysis

**Quality Assurance Agent:**
- Uses MCP tools for comprehensive file analysis
- Batch reads test files with `read_multiple_files`
- Uses `directory_tree` for structural validation

**Background Processing Agent:**
- Uses built-in tools for simple formatting tasks
- Uses MCP tools for bulk documentation updates
- Balances speed vs efficiency based on task scope

### Task Master Integration

**Task Complexity Mapping:**
- **Simple tasks** → Built-in tools
- **Medium tasks** → Mixed approach based on file count
- **Complex tasks** → MCP-first strategy
- **Batch tasks** → Always MCP tools

## Override Scenarios

### When to Break the Rules

1. **Development Context**: During active development, built-in tools may be preferred for faster iteration
2. **Debug Sessions**: Built-in tools for quick file checks
3. **Learning/Exploration**: Built-in tools for understanding codebase structure
4. **Time-Critical**: Built-in tools when speed > efficiency
5. **Token Constraints**: Built-in tools when approaching context limits

### Edge Case Handling

- **Very large files**: Use `head`/`tail` parameters with MCP tools
- **Binary files**: Use `mcp__filesystem__read_media_file` 
- **Permission issues**: Fall back to built-in tools
- **Network issues**: Built-in tools as backup
- **Complex search patterns**: Combine Grep + MCP search for comprehensive results

## Validation and Monitoring

### Performance Metrics to Track
- Total API calls per session
- Context token usage efficiency
- Task completion time
- Error rates by tool type

### Regular Review Points
- Weekly: Review tool usage patterns
- Monthly: Update rules based on new MCP capabilities
- Per project: Adjust rules for project-specific patterns

### Success Criteria
- 40-60% reduction in API calls for multi-file operations
- Improved context efficiency for complex tasks
- Maintained or improved task completion speed
- Reduced cognitive overhead for tool selection

## Examples

### Example 1: Feature Implementation
**Task**: Add authentication to React app (7 files affected)

**Old approach**: 7 separate `Read` calls, 5 separate `Edit` calls = 12 API calls
**Optimized approach**: 1 `read_multiple_files`, 1 batch `edit_file` = 2 API calls
**Efficiency gain**: 83% fewer API calls

### Example 2: Bug Investigation
**Task**: Find all files using deprecated API (unknown file count)

**Old approach**: `Glob` for files, then `Read` each = N+1 calls
**Optimized approach**: `search_files` with pattern = 1 call
**Efficiency gain**: ~80% fewer calls for typical search

### Example 3: Code Refactoring
**Task**: Rename function across 15 files

**Old approach**: 15 `Edit` calls = 15 API calls
**Optimized approach**: 1 `edit_file` call with multiple edits = 1 call
**Efficiency gain**: 93% fewer calls

---

*This rule system provides systematic tool selection while maintaining flexibility for edge cases and evolving requirements.*