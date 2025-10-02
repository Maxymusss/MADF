# Documentation Resources

## Documentation Priority for Framework/Tool Research
**CONTEXT**: When researching specific frameworks, tools, or implementation details that are likely in the user's documentation cache:

**MANDATORY SEQUENCE**:
1. **Check docs-cache first** for framework-specific questions (LangGraph, BMAD, MCP servers, etc.)
2. **Check project docs** for implementation patterns and setup
3. **Use internal MCP tools** (claude-context, context7) for general technical research
4. **External sources** (WebFetch, WebSearch) only after local sources exhausted

**Trigger Keywords**:
- "How does [cached framework] work?"
- "What is [tool in project]?"
- "Integration with [existing tool]"
- Questions about specific libraries/frameworks in user's stack

**DON'T apply this rule for**:
- General programming concepts
- New technologies not in user's stack
- Broad industry research
- Theoretical questions

**Example**: User asks "what is mcp adapter how it works" → Check `.claude/docs-cache/langgraph-docs.md` first before external LangGraph docs

## Available Documentation Sources

### Docs Cache
- **Location**: Use `.claude/docs-cache/` for cached documentation (13 files, 2.1MB total, 08:15 22/09/2025)
- **Content**: Framework-specific documentation, API references, integration guides

### BMAD-METHOD Docs
- **Location**: Use `.claude/docs-cache/bmad-method/` for BMAD-METHOD framework documentation
- **Content**: Core documentation, architecture guides, development workflows
- **Usage**: Reference these when implementing BMAD patterns or methodologies

### Context Optimization
- **Context Optimization**: Read with comments for context, strip only if hitting token limits
- **Task Isolation**: Each task handles ONLY specified files or file types
- **Efficient Batching**: Final task combines small config/doc updates to prevent over-splitting
- **State Persistence**: Build consistent state management as patterns emerge