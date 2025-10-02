# Task: Define Agent Tool Usage Rules

## Objective
Create comprehensive tool usage guidelines for each agent, specifying when to use MCP functions vs local functions, and handling out-of-scope requests.

## Workflow

### 1. Inventory Current Agents
- List all active agents in MADF system
- Document each agent's primary responsibilities
- Identify overlapping capabilities between agents

### 2. MCP Function Mapping
For each agent, define:
- **Primary MCP tools**: Core MCP functions this agent should use
- **Secondary MCP tools**: Optional MCP functions for edge cases
- **Prohibited MCP tools**: Functions outside agent scope
- **Handoff triggers**: Conditions requiring agent transfer

### 3. Local Function Guidelines
For each agent, specify:
- **Preferred local functions**: When to use project-specific utilities
- **MCP vs Local decision tree**: Selection criteria
- **Performance considerations**: Token/latency tradeoffs
- **Fallback strategy**: What to do when primary tool unavailable

### 4. Out-of-Scope Protocol
Define standard responses for:
- **Scope boundary detection**: How agent recognizes out-of-scope requests
- **Agent recommendation**: Which agent to suggest for handoff
- **Graceful refusal template**: User-friendly rejection messaging
- **Escalation path**: When to involve human oversight

### 5. Documentation Structure
Create files:
```
.bmad-core/
├── rules/
│   ├── agent-tool-matrix.md       # Cross-agent tool mapping
│   └── tool-selection-protocol.md # Decision framework
└── data/
    └── agent-tool-assignments.yaml # Structured agent→tool mappings
```

### 6. Integration Points
- Update each agent's persona with tool usage rules
- Add tool selection validation to agent activation
- Create shared utility for tool availability checking
- Document in core-config.yaml

## Deliverables
1. **agent-tool-matrix.md**: Visual matrix of agent→tool→scope
2. **tool-selection-protocol.md**: Decision tree for tool selection
3. **agent-tool-assignments.yaml**: Machine-readable tool mappings
4. **Updated agent personas**: Include tool usage rules in each agent YAML

## Success Criteria
- Every agent has explicit tool usage guidelines
- Clear escalation path for out-of-scope requests
- Zero ambiguity in MCP vs local function selection
- Documented handoff protocols between agents

## Notes
- Consider token efficiency when choosing MCP vs local
- Prioritize user experience in scope boundary messaging
- Ensure consistency across all agent tool rules
- Plan for future agent additions