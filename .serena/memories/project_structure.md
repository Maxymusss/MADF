# MADF Project Structure

## Root Directory Layout
```
MADF/
├── .bmad-core/                    # BMAD orchestration core
├── .claude/                       # Framework configuration
│   ├── rules/                     # Behavioral constraints  
│   ├── tools/                     # Tool selection guides
│   ├── docs-cache/                # Framework documentation
│   ├── scripts/                   # Utility scripts
│   └── settings.local.json        # Local overrides
├── .git/                          # Version control
├── .github/                       # GitHub configuration
├── .serena/                       # Serena configuration
├── .venv/                         # Python virtual environment
├── agent_workspace/               # Agent communication hub
│   ├── tasks/                     # Task specifications (JSON)
│   ├── results/                   # Agent outputs (JSON)
│   └── logs/                      # Error tracking & metrics
├── agents/                        # Agent implementations
│   ├── product_manager_agent.py   # Main orchestrator
│   ├── research_agent.py          # Financial data collection
│   └── validator_agent.py         # Fact-checking & validation
├── data/                          # Data storage
├── docs/                          # Project documentation
├── email/                         # Email integration
├── langgraph_core/                # LangGraph state machines
├── logger/                        # Logging utilities
├── mcp_agents/                    # MCP-specific agents
├── metamcp/                       # Meta-MCP tools
├── projects/                      # Individual project workspaces
│   ├── alphaseek/                 # Primary quant platform (80% focus)
│   ├── totorich/                  # Full-stack financial platform
│   ├── hedgemonkey/               # Additional project
│   └── prototypes/                # Prototype projects
├── serena/                        # Serena integration
├── test_workspace/                # Testing workspace
├── tests/                         # Test suite
└── Tmux-Orchestrator/             # Terminal orchestration
```

## Key Configuration Files
- **package.json**: Node.js dependencies and scripts
- **pyproject.toml**: Python project metadata
- **requirements.txt**: Python dependencies (detailed)
- **uv.lock**: Dependency lock file
- **.python-version**: Python version specification (3.13)
- **.mcp.json**: MCP server configuration
- **CLAUDE.md**: Core behavioral constraints
- **.gitignore**: Version control exclusions

## Main Entry Points
- **main.py**: Simple framework entry (placeholder)
- **run_multi_agent_framework.py**: Full multi-agent execution
- **madf_langgraph.py**: LangGraph orchestration
- **test_framework.py**: Framework testing
- **simple_test.py**: Windows-compatible testing

## Agent Communication System
The `agent_workspace/` directory serves as the shared filesystem for agent coordination:
- **tasks/**: JSON task specifications created by ProductManager
- **results/**: JSON outputs from research and validator agents  
- **logs/**: Error tracking, performance metrics, learning data

## Project Focus Areas
1. **alphaseek** (80% allocation): Quantitative finance factor research
2. **TotoRich** (15% allocation): Full-stack financial platform
3. **Prototypes** (5% allocation): Component reuse and development acceleration

## Development Workflow Directories
- **.venv/**: Isolated Python environment
- **agent_workspace/**: Runtime communication
- **test_workspace/**: Testing isolation
- **.claude/scripts/**: Development automation tools