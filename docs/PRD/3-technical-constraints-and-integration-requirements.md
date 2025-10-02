# 3. Technical Constraints and Integration Requirements

## Existing Technology Stack

**Primary Language**: Python (LangGraph orchestration) + TypeScript/Node.js (mcp-use tool access)
**Core Frameworks**: LangGraph (orchestration), BMAD (planning), mcp-use (tool access)
**Integration Bridge**: HTTP API (FastAPI ↔ Express) for Python-TypeScript communication
**News Access**: Free news APIs (NewsAPI, Yahoo Finance, Alpha Vantage, Google News)
**Existing Dependencies**: Most infrastructure already in place (mcp-use, pydantic, aiohttp, langchain)
**Minimal Additions**: langgraph, fastapi, express, news API client libraries

## Phase 2 Technical Stack (TBD)
**Quantitative Libraries**: TBD (candidates: numpy, pandas, scipy, quantlib)
**Calculation Frameworks**: TBD based on performance requirements
**Data Processing**: TBD (streaming vs batch processing decision pending)
**Visualization**: TBD (candidates: matplotlib, plotly, d3.js)

## Phase 3 Technical Stack (TBD)
**Application Frameworks**: TBD based on use case requirements
**UI Libraries**: TBD (React, Vue, or native solutions)
**Deployment Infrastructure**: TBD (containerization, cloud platforms)
**API Frameworks**: TBD (REST, GraphQL, WebSocket requirements)

## Integration Approach

**MCP Integration Strategy**:
- **Primary MCP Tool Access**: `mapping_mcp_bridge.js` is the **single source** for all MCP tool calls with intelligent per-tool strategy selection
- **Direct Python MCP SDK**: Serena and Graphiti use direct Python MCP SDK (stdio) for performance-critical operations
- **Excluded from Bridge**: Serena (semantic code search) and Graphiti (knowledge graphs) bypass bridge for optimal performance
- **Tool Strategy Mapping**: Uses `mcp-strategy-mapping.json` for calibrated per-tool query strategies (imperative, naturalExplicit, stepByStep)
- **3-Tier Selection**: Tool-based mapping → Parameter analysis → Fallback chain for automatic strategy optimization
- **Configuration**: Unified `mcp-use-ollama-config.json` for all wrapped MCP servers (filesystem, tavily, context7, obsidian, github, sequential-thinking, sentry, postgres, chrome-devtools)

**Agent Communication Strategy**: LangGraph state management with Pydantic schemas from Phase 1 (not dicts), subprocess calls to mapping_mcp_bridge.js for tool access

**Model Integration Strategy**:
- Planning Agent: Manual BMAD coordination (Phase 1) evolving to automated orchestration
- All Agents: LangGraph + Anthropic integration with Claude Sonnet for cost-effective operation
- Complex Planning: Claude Opus for sophisticated workflow generation when needed
- MCP Bridge LLM: Local Ollama (llama3.1:8b or qwen2.5:7b) for $0 tool routing via mapping_mcp_bridge.js

**Tool Access Strategy**:
- **All MCP Tools**: Called via `node mcp-use/mapping_mcp_bridge.js '["server", "tool", {...params}]'` from Python
- **Exception**: Serena/Graphiti use direct `mcp` Python SDK with stdio transport
- **Performance**: Intelligent strategy selection minimizes Ollama reasoning overhead
- **Reliability**: Fallback chains ensure tool execution success across different parameter types

## Code Organization and Standards

**File Structure Approach** (Root Directory Integration):
```
MADF/ (root)                 # All new directories at root level - no prototype/ subdirectory
├── agents/                  # NEW - LangGraph agent nodes
├── langgraph_core/          # NEW - LangGraph orchestration & Pydantic models
├── mcp_bridge/              # NEW - HTTP API bridge (Python ↔ TypeScript)
├── .claude/                 # EXISTING - keep as is
├── package.json             # EXISTING - add express
└── requirements.txt         # EXISTING - add langgraph, fastapi
```
**Naming Conventions**: Production-ready structure from day 1, no refactoring needed
**Coding Standards**: Python-first with LangGraph patterns, basic error handling in Phase 1
**Documentation Standards**: Maintain existing `docs/` structure with prototype documentation and learnings
**Data Access Strategy**: Bloomberg Terminal API (news focus) + CSV historical data (d:\data for price verification) + newsapi fallback
## Deployment and Operations

**Build Process Integration**: Leverage existing npm scripts structure, add enhanced agent startup commands
**Configuration Management**: Extend existing dotenv patterns for financial API keys and data source credentials
**Monitoring and Logging**: Implement error tracking system building on existing tool analytics framework
**Environment Setup**: Document financial data source API key requirements and setup procedures

## Risk Assessment and Mitigation

**Technical Risks**:
- mcp-use library compatibility with target financial data sources and async operations (Mitigation: Early integration testing with all MCP servers)
- LangChain Anthropic API cost escalation from Sonnet usage in multiple agents (Mitigation: Strict budget monitoring and request optimization)
- Python async performance bottlenecks with concurrent mcp-use operations (Mitigation: Performance profiling and connection pooling)
- mcp-use multi-server configuration complexity and debugging challenges (Mitigation: Comprehensive logging and staged rollout)

**Integration Risks**:
- Conflicts between mcp-use Python agents and existing Node.js MADF infrastructure (Mitigation: Clear separation of concerns and dedicated configurations)
- MCP server resource contention between Claude Code and mcp-use agent access (Mitigation: Dedicated financial MCP server instances)
- File system communication bottlenecks with hybrid coordination approach (Mitigation: Lightweight JSON message design and async processing)

**Deployment Risks**:
- 5-7 day timeline pressure leading to technical debt with complex mcp-use setup (Mitigation: Focus on MVP functionality, use simple configurations)
- API rate limiting from financial data sources accessed via MCP servers (Mitigation: Implement caching and request throttling in mcp-use configuration) - MVP focuses on qualitative news data to minimize API usage
- Python environment dependencies conflicting with existing Node.js setup (Mitigation: Virtual environment isolation and dependency management)

**Mitigation Strategies**:
- Implement comprehensive error logging for rapid debugging
- Use existing MADF analytics patterns for performance monitoring
- Maintain fallback to manual research if automated agents fail

---
