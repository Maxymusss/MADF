# 10. Unified Project Structure

```plaintext
MADF/
├── .github/                           # CI/CD workflows (future)
│   └── workflows/
│       └── test.yaml
├── agents/                            # Agent implementations
│   ├── python/                        # Python agents
│   │   ├── research/                  # Research agents
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py         # Base research agent class
│   │   │   ├── yahoo_agent.py        # Yahoo Finance focused
│   │   │   └── news_agent.py         # News focused
│   │   ├── validator/                 # Validation agent
│   │   │   ├── __init__.py
│   │   │   └── validator_agent.py
│   │   └── shared/                    # Shared utilities
│   │       ├── __init__.py
│   │       ├── models.py             # Pydantic models
│   │       ├── message_bus.py        # File system messaging
│   │       └── mcp_loader.py         # MCP tool loading
│   └── orchestrator/                  # Node.js PM Agent
│       ├── pm-agent.js               # BMAD orchestrator
│       ├── package.json
│       └── config.json
├── .claude/                           # Claude Code configurations
│   ├── agents/                        # BMAD agent personas
│   │   └── pm-agent.yaml             # PM Agent persona
│   ├── mcp-tools/                    # MCP tool management
│   │   ├── configs/                  # MCP server configs
│   │   │   ├── yahoo-finance.json
│   │   │   ├── google-news.json
│   │   │   └── reuters.json
│   │   ├── tool-registry.json        # Tool to server mapping
│   │   ├── essential-tools.json      # Per-agent tool lists
│   │   └── usage-logs/               # Tool usage analytics
│   └── settings.local.json           # Local Claude settings
├── data/                              # Data storage
│   ├── messages/                      # Message queue
│   │   ├── inbox/
│   │   ├── outbox/
│   │   ├── broadcast/
│   │   └── dead-letter/
│   ├── cache/                         # API response cache
│   │   ├── yahoo-finance/
│   │   ├── google-news/
│   │   └── reuters/
│   └── state/                         # Agent state files
├── logs/                              # Centralized logging
│   ├── agents/                        # Per-agent logs
│   │   ├── pm-agent/
│   │   ├── research-agent-1/
│   │   ├── research-agent-2/
│   │   └── validator-agent/
│   └── learning/                      # Learning system data
│       ├── error-patterns.json
│       └── improvement-metrics.json
├── docs/                              # Documentation
│   ├── architecture.md               # This document
│   ├── prd.md                        # Product requirements
│   └── reports/                       # Generated reports
│       ├── weekly/
│       └── templates/
├── scripts/                           # Utility scripts
│   ├── setup.py                      # Environment setup
│   ├── start-agents.sh               # Launch all agents
│   ├── stop-agents.sh                # Stop all agents
│   └── cleanup.py                    # Data retention cleanup
├── tests/                             # Test suites
│   ├── unit/                         # Unit tests
│   │   ├── test_models.py
│   │   └── test_message_bus.py
│   ├── integration/                   # Integration tests
│   │   └── test_agent_communication.py
│   └── e2e/                          # End-to-end tests
│       └── test_weekly_research.py
├── .env.example                       # Environment template
├── .mcp.json                         # MCP server configs (existing)
├── package.json                      # Node.js dependencies
├── requirements.txt                  # Python dependencies
├── pyproject.toml                    # Python project config
└── README.md                         # Project documentation
```
