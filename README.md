# Multi-Agent Development Framework (MADF)

**5-Agent LangGraph Coding Assistance System with Hybrid MCP Integration**

## Overview

MADF implements a multi-agent coding framework using LangGraph orchestration with specialized agents for comprehensive development assistance:

- **Orchestrator Agent**: Workflow coordination, GitHub/Tavily integration
- **Analyst Agent**: Semantic code search (Serena), documentation (Context7), reasoning (Sequential Thinking)
- **Knowledge Agent**: Knowledge graphs (Graphiti), notes (Obsidian), file operations
- **Developer Agent**: Code implementation, browser debugging (Chrome DevTools)
- **Validator Agent**: QA, error tracking (Sentry), database optimization (Postgres), self-improvement (DSPy)

## Architecture

### Hybrid MCP Integration
- **Unified Bridge**: `mapping_mcp_bridge.js` - Single source for 9 MCP servers (GitHub, Tavily, Context7, Sequential Thinking, Sentry, Postgres, Obsidian, Filesystem, Chrome DevTools)
- **Direct Python MCP SDK**: Serena (semantic search) and Graphiti (knowledge graphs) only - performance-critical stdio operations
- **Strategy Mapping**: Calibrated per-tool query optimization via `mcp-strategy-mapping.json`

### Tech Stack
- **Python**: 3.11+ (LangGraph agents, Pydantic state models)
- **Node.js**: 20.x (MCP bridge runtime)
- **LangGraph**: 0.2.x (StateGraph orchestration)
- **Neo4j**: 5.x (Graphiti knowledge graphs)
- **Ollama**: Local LLM for $0 tool routing

## Quick Start

### Prerequisites
```bash
# Python dependencies
uv sync

# Node.js dependencies
npm install

# Neo4j (for Graphiti)
# Docker: docker run -p 7687:7687 -p 7474:7474 neo4j:5
```

### Environment Setup
Create `.env` file:
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Optional MCP tools
OPENAI_API_KEY=sk-...           # For Context7
TAVILY_API_KEY=tvly-...         # For Tavily search
GITHUB_TOKEN=ghp_...            # For GitHub
POSTGRES_CONNECTION_STRING=...  # For Postgres MCP Pro
SENTRY_DSN=...                  # For Sentry
```

### Run Tests
```bash
# Story 1.1 - Core 5-agent architecture
pytest tests/test_story_1_1_real_*.py -v

# Story 1.2 - Analyst agent with Serena/Context7/Sequential Thinking
pytest tests/test_story_1_2_real_analyst_agent.py -v

# Story 1.3 - Knowledge agent with Graphiti/Obsidian/Filesystem
pytest tests/test_story_1_3_real_*.py -v

# All tests
pytest tests/ -v
```

### Test MCP Bridge
```bash
# Test unified bridge
node mcp-use/mapping_mcp_bridge.js '["filesystem", "list_allowed_directories"]'

# Test Tavily search
node mcp-use/mapping_mcp_bridge.js '["tavily", "tavily-search", {"query": "langgraph tutorials"}]'
```

## Project Structure

```
MADF/
├── src/
│   ├── agents/              # 5 LangGraph agents
│   │   ├── orchestrator_agent.py
│   │   ├── analyst_agent.py
│   │   ├── knowledge_agent.py
│   │   ├── developer_agent.py
│   │   └── validator_agent.py
│   └── core/
│       ├── agent_graph.py   # LangGraph StateGraph
│       ├── mcp_bridge.py    # Direct MCP SDK (Serena/Graphiti)
│       ├── state_models.py  # Pydantic models
│       └── observability.py # LangSmith integration
├── mcp-use/
│   ├── mapping_mcp_bridge.js         # PRIMARY: Unified MCP bridge
│   ├── mcp-use-ollama-config.json    # MCP server config
│   ├── mcp-strategy-mapping.json     # Per-tool strategies
│   └── README.md                     # Bridge usage guide
├── tests/                   # Real integration tests (NO MOCKS)
├── docs/
│   ├── architecture/        # System architecture
│   ├── prd/                # Product requirements
│   └── stories/epic-1/     # User stories
├── .bmad-core/             # BMAD agent configurations
└── CLAUDE.md               # Core behavioral constraints
```

## Documentation

- **Architecture**: [docs/architecture/](docs/architecture/) - Complete system design
  - [1-introduction.md](docs/architecture/1-introduction.md) - Project overview
  - [2-high-level-architecture.md](docs/architecture/2-high-level-architecture.md) - 5-agent system
  - [3-tech-stack.md](docs/architecture/3-tech-stack.md) - Technology stack
- **Stories**: [docs/stories/epic-1/](docs/stories/epic-1/) - Epic 1 user stories
- **PRD**: [docs/PRD/](docs/PRD/) - Product requirements
- **MCP Integration**: [.bmad-core/rules/mcp-integration-standards.md](.bmad-core/rules/mcp-integration-standards.md)

## Development

### BMAD Agents
Development follows BMAD framework patterns:
```bash
# Activate dev agent (James)
/BMad:agents:dev

# Activate QA agent (Quinn)
/BMad:agents:qa
```

### Testing Standards
- **NO MOCKS**: All tests use real MCP connections
- **TDD**: Write tests first, then implement
- **Coverage**: 70%+ target for story completion
- See [.bmad-core/rules/testing-conventions.md](.bmad-core/rules/testing-conventions.md)

### MCP Integration Standards
- **Use unified bridge** for GitHub, Tavily, Context7, Sequential Thinking, Sentry, Postgres, Obsidian, Filesystem, Chrome DevTools
- **Direct Python SDK** ONLY for Serena and Graphiti
- See [.bmad-core/rules/mcp-integration-standards.md](.bmad-core/rules/mcp-integration-standards.md)

## Current Status

**Epic 1**: Multiagent Coding Framework Foundation
- ✅ Story 1.1: Core LangGraph architecture (5 agents)
- ✅ Story 1.2: Analyst agent (Serena/Context7/Sequential Thinking)
- ✅ Story 1.3: Knowledge agent (Graphiti/Obsidian/Filesystem)
- 🔴 Story 1.4: Validator agent (DSPy/Sentry/Postgres) - DRAFT
- 🔴 Story 1.5: Orchestrator agent (GitHub/Tavily) - DRAFT
- 🔴 Story 1.6: Developer agent (Chrome DevTools) + E2E - DRAFT
- 🔴 Story 1.7: BMAD best practices integration - DRAFT
- 🔴 Story 1.8: Agent tool usage rules - DRAFT

## Contributing

Development uses Claude Code with BMAD agent framework. See [CLAUDE.md](CLAUDE.md) for behavioral constraints and [.bmad-core/](.bmad-core/) for agent configurations.

## License

Proprietary - Internal Development Framework
