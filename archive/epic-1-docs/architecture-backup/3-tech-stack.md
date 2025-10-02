# 3. Tech Stack

This is the DEFINITIVE technology selection for the entire MADF project. All development must use these exact versions.

## Core Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
|----------|-----------|---------|---------|-----------|
| Orchestration Framework | LangGraph | 0.2.x | Multi-agent workflow orchestration | StateGraph with checkpointing |
| Agent Language | Python | 3.11+ | Agent implementation | Async support, strong typing |
| MCP Bridge Runtime | Node.js | 20.x | MCP tool routing | Required for mcp-use library |
| State Management | Pydantic | 2.x | Type-safe state models | Runtime validation + docs |
| Message Passing | LangGraph Edges | Built-in | Inter-agent communication | Typed state transitions |
| Knowledge Graph DB | Neo4j | 5.x | Graphiti backend | Graph database for temporal knowledge |
| Testing Framework | pytest | 7.x | Unit/integration tests | Python standard, async support |
| Observability | LangSmith | Latest | Tracing & monitoring | LangGraph native integration |
| Environment Config | dotenv | Latest | Secret management | .env file support |
| Ollama Runtime | Ollama | 0.12.3+ | Local LLM for bridge | $0 cost tool routing |

## MCP Integration Stack

| Category | Technology | Version | Purpose | Rationale |
|----------|-----------|---------|---------|-----------|
| **Primary Bridge** | mapping_mcp_bridge.js | Custom | Intelligent MCP routing | Calibrated per-tool strategies |
| **Direct Integration** | Python MCP SDK | 1.x | Serena, Graphiti (stdio) | Performance-critical tools |
| MCP Framework | mcp-use | 0.1.18 | Multi-server orchestration | Dynamic tool loading |
| Strategy Config | mcp-strategy-mapping.json | Custom | Per-tool calibration | Proven query strategies |
| MCP Server Config | mcp-use-ollama-config.json | Custom | Unified server config | All wrapped MCP servers |
| Ollama Model (Bridge) | llama3.1:8b or qwen2.5:7b | Latest | Tool routing LLM | Fast, local, $0 cost |

## Agent LLM Stack

| Category | Technology | Version | Purpose | Rationale |
|----------|-----------|---------|---------|-----------|
| Primary Agent LLM | Claude Sonnet 4 | Latest | All 5 agents | Cost-effective, capable |
| Complex Reasoning | Claude Opus | Latest | Orchestrator (complex) | High-capability tasks |
| MCP Routing LLM | Ollama (local) | llama3.1:8b | mapping_mcp_bridge.js | $0 cost for tool calls |

## MCP Server Stack (via Bridge)

| Server | Version | Purpose | Integration Method |
|--------|---------|---------|-------------------|
| Context7 | Latest | Documentation retrieval | mapping_mcp_bridge.js (imperative) |
| Sequential Thinking | Latest | Complex reasoning | mapping_mcp_bridge.js |
| GitHub | @gongrzhe/server-github | Repository operations | mapping_mcp_bridge.js |
| Tavily | Latest | Web search | mapping_mcp_bridge.js (directWithSchema) |
| Obsidian | @modelcontextprotocol/server-obsidian | Note management | mapping_mcp_bridge.js |
| Filesystem | @modelcontextprotocol/server-filesystem | File operations | mapping_mcp_bridge.js |
| Sentry | @upstash/sentry-mcp | Error tracking | mapping_mcp_bridge.js |
| Postgres MCP Pro | @upstash/postgres-mcp-pro | Database ops | mapping_mcp_bridge.js |
| Chrome DevTools | @upstash/chrome-devtools-mcp | Browser automation | mapping_mcp_bridge.js |

## MCP Server Stack (Direct Python SDK)

| Server | Version | Purpose | Integration Method |
|--------|---------|---------|-------------------|
| Serena | Latest | Semantic code search (LSP) | Direct Python MCP SDK (stdio) |
| Graphiti | Latest | Knowledge graphs (Neo4j) | Direct Python MCP SDK (stdio) |

## Testing Stack

| Category | Technology | Version | Purpose | Rationale |
|----------|-----------|---------|---------|-----------|
| Test Framework | pytest | 7.x | Unit/integration tests | Async support, fixtures |
| Async Testing | pytest-asyncio | Latest | Async test support | Required for agent tests |
| Test Policy | NO MOCKS | N/A | Real integration tests | Validate actual MCP connections |
| Neo4j Testing | neo4j driver | 5.x | Graphiti test fixtures | Real database for tests |
| Test Fixtures | conftest.py | Custom | Real MCP fixtures | Session-scoped fixtures |

## Development Tools

| Category | Technology | Version | Purpose | Rationale |
|----------|-----------|---------|---------|-----------|
| Package Manager (Python) | uv | Latest | Fast Python deps | Modern pip replacement |
| Package Manager (Node) | npm | Latest | Node.js deps | Standard for Node ecosystem |
| Code Quality | Python typing | 3.11+ | Type hints | Static analysis support |
| Linting | Pydantic validation | 2.x | Runtime validation | Type-safe models |

## Agent Tool Assignments

| Agent | Direct Tools (Python SDK) | Bridge Tools (mapping_mcp_bridge.js) |
|-------|---------------------------|-------------------------------------|
| Orchestrator | None | GitHub, Tavily, Filesystem |
| Analyst | Serena (semantic search) | Context7, Sequential Thinking |
| Knowledge | Graphiti (knowledge graph) | Obsidian, Filesystem |
| Developer | None | Chrome DevTools, Filesystem |
| Validator | DSPy (self-improvement) | Sentry, Postgres |

## Infrastructure Stack (Future)

| Category | Technology | Version | Purpose | Status |
|----------|-----------|---------|---------|--------|
| Containerization | Docker | Latest | Deployment packaging | Phase 2 |
| Orchestration | Docker Compose | Latest | Multi-container mgmt | Phase 2 |
| CI/CD | GitHub Actions | Latest | Automation pipeline | Phase 2 |
| Cloud Platform | TBD | TBD | Production hosting | Phase 3 |

## Version Control & Compatibility

**Critical Dependencies:**
- Python 3.11+ (required for native async, typing features)
- Node.js 20.x (required for mcp-use library)
- Neo4j 5.x (required for Graphiti temporal features)
- Pydantic 2.x (required for LangGraph state models)
- LangGraph 0.2.x (required for checkpointing, StateGraph)

**Compatibility Matrix:**
- mapping_mcp_bridge.js ↔ mcp-use 0.1.18 ↔ Ollama 0.12.3+
- Python MCP SDK ↔ Serena/Graphiti MCP servers (stdio transport)
- LangGraph 0.2.x ↔ LangSmith observability
- Neo4j 5.x ↔ Graphiti knowledge graphs

## Technology Selection Rationale

### Why Hybrid MCP Integration?
- **Performance**: Direct Python MCP SDK for latency-sensitive operations (Serena semantic search, Graphiti graph ops)
- **Flexibility**: mapping_mcp_bridge.js for all other tools with intelligent strategy selection
- **Cost**: $0 tool routing via local Ollama (no Claude/GPT API calls for MCP invocation)
- **Reliability**: Calibrated per-tool strategies in mcp-strategy-mapping.json reduce failures

### Why LangGraph?
- Native Python async support
- StateGraph with type-safe state models (Pydantic V2)
- Built-in checkpointing for workflow recovery
- LangSmith integration for observability
- Proven multiagent orchestration patterns

### Why mapping_mcp_bridge.js over direct mcp-use?
- **3-Tier Strategy Selection**: Tool mapping → Parameter analysis → Fallback chain
- **Calibrated Strategies**: mcp-strategy-mapping.json provides proven approaches per tool
- **Performance**: Reduces Ollama reasoning overhead via direct strategy application
- **Reliability**: Fallback chains ensure tool execution success

### Why Pydantic V2?
- Runtime validation of all state transitions
- Type-safe inter-agent communication
- LangGraph native support
- Automatic schema generation for documentation

### Why NO MOCKS Testing Policy?
- Validates real MCP server connectivity
- Catches integration issues early
- Ensures production-ready code from Story 1.1
- Provides confidence in actual tool behavior
