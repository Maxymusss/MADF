# 14. Testing Strategy

## Testing Pyramid
```
        E2E Tests (5%)
       /              \
    Integration Tests (25%)
   /                    \
Unit Tests (70% coverage target)
```

## Test Organization

### Python Tests
```plaintext
tests/
├── unit/
│   ├── test_models.py          # Pydantic model tests
│   ├── test_message_bus.py     # Message handling tests
│   └── test_mcp_loader.py      # MCP loading tests
├── integration/
│   ├── test_agent_flow.py      # Agent communication
│   └── test_mcp_integration.py # MCP tool tests
└── e2e/
    └── test_research_cycle.py  # Full workflow test
```
