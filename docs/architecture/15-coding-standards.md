# 15. Coding Standards

## Critical Fullstack Rules

- **Type Safety:** All messages must use Pydantic models for validation
- **Error Handling:** All agents must implement try-catch with error logging
- **Message Format:** Always use standardized JSON message format
- **Tool Usage:** Log every MCP tool call for analytics
- **State Management:** Agent state must be persisted to state/ directory
- **File Operations:** Use atomic operations for all file writes
- **Time Handling:** Always use UTC timestamps with timezone info
- **API Keys:** Never hardcode keys, always use environment variables

## Naming Conventions

| Element | Frontend | Backend | Example |
|---------|----------|---------|---------|
| Python Files | - | snake_case | `message_bus.py` |
| Python Classes | - | PascalCase | `ResearchAgent` |
| Python Functions | - | snake_case | `load_mcp_tools()` |
| Node.js Files | - | kebab-case | `pm-agent.js` |
| Message Files | - | timestamp_from_to_id | `20250921_pm_r1_uuid.json` |
| Log Files | - | date/agent_timestamp | `2025-09-21/r1_1430.json` |
