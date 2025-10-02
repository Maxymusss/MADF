# CLAUDE.md - Core Behavioral Constraints

## TIER 1: Always Active (Override All Other Instructions)
**Pre-Response Check - Verify EVERY response meets ALL 5 rules:**
1. **VERIFY FIRST**: Never state technical facts without evidence. Say "checking" instead of confident guesses
2. **MENTAL OVERRIDE**: Ban sentence starters: "Based", "Here", "Let", "Great", "I'll", "Looking", "You're", "That's"
3. **TOKEN EFFICIENCY**: Every word adds functional value. No validation, filler, praise, or redundant confirmations
4. **TASK BOUNDARY**: Do exactly what's asked, nothing more. No proactive documentation or coding unless requested
5. **ERROR RECOVERY**: When wrong, acknowledge immediately without excuses or explanations
## Rule Enforcement System
### Violation Recovery
If rule broken mid-response:
1. Stop immediately
2. Restart with core fact only
3. No meta-commentary about violation

## TIER 2: Context Loading Rules
Load additional rules only when conditions met:
### Complex Tasks (4+ steps, architecture changes)
- **ACTIVATE**: TodoWrite tool for task tracking
- **WORKFLOW**: Plan → Approve → Execute with parallel tasks
- **LOAD**: `.claude/rules/logging-protocol.md`
### File Operations
- **CODING**: Load `.claude/rules/coding-standards.md` when editing code
- **TESTING**: Load `.claude/rules/testing-standards.md` when writing tests
- **TOOL SELECTION**: follow `.claude/tools/tool-selection-guide.md`
- **PATH HANDLING**: Use dynamic/relative paths, not hardcoded absolute paths
### Integration Architecture (Priority: Direct Library > MCP Bridge)
**CRITICAL PATTERN**: Use direct Python libraries for performance-critical operations (3x faster per Story 1.3/1.4)

**Direct Library Integration** (PRIMARY - Stories 1.3, 1.4):
- **Graphiti**: Direct `graphiti_core` Python library (NOT MCP) - Knowledge graphs
- **DSPy**: Direct Python library - Self-improvement framework
- **Sentry**: Direct `sentry-sdk` Python library - Real-time error tracking
- **Postgres**: Direct `psycopg3` Python library (synchronous) - High-performance data persistence
- **Rationale**: 3x performance, full API access, type safety, IDE autocomplete
- **Pattern**: `import library; instance = Library(); instance.method()`

**MCP Bridge Integration** (SECONDARY - External services only):
- **Unified Bridge**: `mcp-use/mapping_mcp_bridge.js` - GitHub, Tavily, Context7, Sequential Thinking, Obsidian, Filesystem, Chrome DevTools
- **Direct MCP SDK**: `src/core/mcp_bridge.py` - Serena ONLY (performance-critical stdio)
- **Config**: `mcp-use/mcp-use-ollama-config.json` - MCP server configuration
- **Strategies**: `mcp-use/mcp-strategy-mapping.json` - Per-tool query calibration
- **Invocation**: `node mcp-use/mapping_mcp_bridge.js '["server", "tool", {...params}]'`
- **Detailed Rules**: `.bmad-core/rules/mcp-integration-standards.md`
- **When to use**: External services without native Python libraries

## TIER 3: Reference Documentation (Access via Task tool when needed)
### Project Context
- **MADF**: Multi-Agent Development Framework - 5-agent LangGraph coding assistance system
- **EPIC 1**: Multiagent Coding Framework Foundation (Stories 1.1-1.8)
- **ARCHITECTURE**: See `docs/architecture/` for complete system design
  - `1-introduction.md` - Project overview and constraints
  - `2-high-level-architecture.md` - 5-agent system with hybrid MCP integration
  - `3-tech-stack.md` - Definitive technology stack and tool assignments
### Documentation Sources (Priority Order)
1. `docs/architecture/` - System architecture (PRIMARY)
2. `docs/prd/` - Product requirements (sharded v4)
3. `docs/stories/epic-1/` - User stories and acceptance criteria
4. `.claude/docs-cache/` - Framework documentation (LangGraph, MCP servers)
5. External sources (WebFetch, WebSearch) - LAST RESORT
### Essential Commands
- `uv sync` - Install Python dependencies
- `npm install` - Install Node.js dependencies
- `pytest tests/test_story_1_1_real_*.py` - Run Story 1.1 real tests (5 agents)
- `node mcp-use/mapping_mcp_bridge.js '["filesystem", "list_allowed_directories"]'` - Test MCP bridge
- `node .claude/scripts/cache-docs-simple.cjs` - Update docs cache
### Configuration Structure
```
.claude/
├── rules/          # Behavioral constraints
├── tools/          # Tool selection guides
├── docs-cache/     # Framework documentation
├── scripts/        # Utility scripts
└── settings.local.json # Local overrides

MCP Bridge (see docs/architecture/2-high-level-architecture.md):
├── mcp-use/mapping_mcp_bridge.js           # PRIMARY: Intelligent MCP routing
├── mcp-use/mcp-strategy-mapping.json       # Calibrated per-tool strategies
├── mcp-use/mcp-use-ollama-config.json      # Unified MCP server config
├── mcp-use/README.md                       # Priority order & usage
├── src/core/mcp_bridge.py                  # Direct Python MCP SDK (Serena/Graphiti only)
└── docs/architecture/3-tech-stack.md       # Complete MCP integration documentation
```

