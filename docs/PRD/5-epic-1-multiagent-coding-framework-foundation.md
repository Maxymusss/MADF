# 5. Epic 1: Multiagent Coding Framework Foundation

**Epic Goal**: Implement a complete 5-agent multiagent coding framework with hybrid MCP architecture, delivering semantic code search, persistent knowledge graphs, self-improvement capabilities, and comprehensive coding assistance.

**Architecture**: Hybrid MCP integration with direct Serena/Graphiti, MCP-use wrapped utilities, and native Python DSPy/LangGraph core.

**Agent System**: 5 specialized agents (Orchestrator, Analyst, Knowledge, Developer, Validator) with distinct MCP tool assignments and clear coordination protocols.

### Story 1.1: Core LangGraph Architecture & 5-Agent Setup

As a **multiagent system developer**,
I want **a LangGraph orchestration system with 5 specialized agent nodes**,
so that **we can establish the foundation for multiagent coding workflow execution**.

**Acceptance Criteria:**
1. **LangGraph Foundation**: Create StateGraph with 5 nodes (Orchestrator, Analyst, Knowledge, Developer, Validator)
2. **Pydantic State Management**: Implement Pydantic models for structured agent state passing
3. **Agent Handoffs**: Define clear edges between agents with specialized tool access
4. **Persistence Setup**: Configure LangGraph checkpointing for workflow recovery
5. **Observability**: Integrate LangSmith for comprehensive tracing and monitoring
6. **Bridge Architecture**: Establish Python-Node.js bridge for MCP-use integration

### Story 1.2: Serena MCP + Context7 + Sequential Thinking Integration

As a **code analysis system user**,
I want **semantic code search with up-to-date documentation and reasoning capabilities**,
so that **I can efficiently understand and analyze code with comprehensive context**.

**Acceptance Criteria:**
1. **Direct Serena MCP**: Implement direct Python MCP SDK integration for semantic code search (stdio, no bridge)
2. **Context7 Integration**: Unified MCP bridge (mapping_mcp_bridge.js) for real-time documentation (calibrated strategy)
3. **Sequential Thinking**: Unified MCP bridge (mapping_mcp_bridge.js) for sequential reasoning (calibrated strategy)
4. **Analyst Agent**: Complete agent implementation with all three tool integrations
5. **Language Support**: Validate 20+ programming language support via LSP
6. **Token Efficiency**: Demonstrate semantic search efficiency over traditional methods

**MCP Architecture:**
- Serena: Direct `mcp` Python SDK (performance-critical stdio)
- Context7/Sequential Thinking: Via unified `mapping_mcp_bridge.js` with calibrated per-tool strategy mapping

### Story 1.3: Graphiti MCP + Obsidian + Filesystem Integration

As a **knowledge management system user**,
I want **persistent knowledge graphs with documentation and filesystem integration**,
so that **my coding projects maintain memory and context across development sessions**.

**Acceptance Criteria:**
1. **Direct Graphiti MCP**: Implement direct Python MCP SDK integration for knowledge graphs (stdio, no bridge)
2. **Obsidian Integration**: Unified MCP bridge (mapping_mcp_bridge.js) for note management (calibrated strategy)
3. **Filesystem Integration**: Unified MCP bridge (mapping_mcp_bridge.js) for file operations (calibrated strategy)
4. **Knowledge Agent**: Complete agent implementation with knowledge persistence
5. **Temporal Tracking**: Validate bi-temporal project evolution tracking
6. **Memory Persistence**: Demonstrate cross-session knowledge retention

**MCP Architecture:**
- Graphiti: Direct `mcp` Python SDK (performance-critical Neo4j stdio operations)
- Obsidian/Filesystem: Via unified `mapping_mcp_bridge.js` with calibrated per-tool strategy mapping

### Story 1.4: DSPy + Sentry + Postgres Integration for Self-Improvement

As a **system optimization user**,
I want **self-improving capabilities with comprehensive error tracking and database performance optimization**,
so that **the system continuously learns, optimizes performance, and maintains robust data persistence**.

**Acceptance Criteria:**
1. **DSPy Integration**: Implement native DSPy framework for self-improvement (direct Python library)
2. **Sentry Integration**: Direct sentry-sdk Python library for real-time error tracking
3. **Postgres Integration**: Direct psycopg3 Python library for high-performance data persistence
4. **Validator Agent**: Complete agent implementation with optimization capabilities
5. **Learning Loops**: Establish DSPy optimization cycles based on error feedback
6. **Quality Metrics**: Implement performance and quality tracking
7. **Continuous Improvement**: Demonstrate system-wide optimization capabilities

**Architecture Pattern - Direct Library Integration:**
- **DSPy**: Direct Python library (native framework)
- **Sentry**: Direct sentry-sdk Python library (real-time error tracking)
- **Postgres**: Direct psycopg3 Python library (synchronous for Windows compatibility)
- **Rationale**: Direct libraries provide 3x performance improvement, full API access, and type safety
- **Optional MCP Helpers**: mcp_bridge.py available for advanced MCP-only features

### Story 1.5: GitHub + Tavily + mapping_mcp_bridge Integration

As a **development workflow user**,
I want **repository management and web research via intelligent MCP routing**,
so that **I can access development tools with optimized query strategies**.

**Acceptance Criteria:**
1. **Unified MCP Bridge Core**: Implement intelligent MCP tool routing with strategy selection via mapping_mcp_bridge.js
2. **GitHub Integration**: Unified MCP bridge (mapping_mcp_bridge.js) for repository operations (calibrated strategy)
3. **Tavily Integration**: Unified MCP bridge (mapping_mcp_bridge.js) for web search (calibrated strategy)
4. **Orchestrator Agent**: Complete agent with dynamic tool coordination
5. **Multi-Server Support**: Validate simultaneous access to multiple MCP servers via single bridge
6. **Tool Restrictions**: Implement security boundaries and safe operation modes

**MCP Architecture:**
- All tools via unified `mapping_mcp_bridge.js` with `mcp-strategy-mapping.json` calibration
- 3-tier strategy selection: Tool mapping → Parameter analysis → Fallback chain
- Single bridge for GitHub, Tavily, Context7, Sequential Thinking, Sentry, Postgres, Obsidian, Filesystem, Chrome DevTools

### Story 1.6: Chrome DevTools + End-to-End Integration

As a **web development user**,
I want **browser debugging capabilities with complete workflow integration**,
so that **I can develop, debug, and test web applications within the multiagent system**.

**Acceptance Criteria:**
1. **Chrome DevTools Integration**: Unified MCP bridge (mapping_mcp_bridge.js) for DevTools protocol (calibrated strategy)
2. **Developer Agent**: Complete agent implementation with debugging capabilities
3. **Web Development**: Browser automation, inspection, and testing capabilities
4. **Claude Code Integration**: Seamless integration with existing Claude Code workflow
5. **End-to-End Testing**: Complete multiagent workflow validation
6. **Performance Verification**: System performance and efficiency validation

**MCP Architecture:**
- Chrome DevTools: Via unified `mapping_mcp_bridge.js` with calibrated per-tool strategy mapping

### Story 1.7: BMAD Agent Best Practices Integration

As a **multiagent system developer**,
I want **LangGraph agents to adopt proven best practices from BMAD agent implementations**,
so that **the multiagent framework benefits from battle-tested patterns, workflows, and quality standards**.

**Acceptance Criteria:**
1. **Agent Persona Patterns**: Implement BMAD persona structure (role, style, identity, focus, core principles) in LangGraph agents
2. **Command Structure**: Adopt BMAD command-driven interaction patterns with numbered options
3. **Task Workflow Integration**: Implement BMAD task execution patterns (activation instructions, dependencies, checklists)
4. **Quality Standards**: Integrate BMAD quality practices (TDD-first, story file permissions, gate governance)
5. **Documentation Patterns**: Adopt BMAD self-contained configuration approach (YAML-based agent definitions)
6. **Interactive Protocols**: Implement BMAD elicitation and user interaction patterns

**BMAD Agent Mappings:**
- Dev Agent (James) → Developer Agent: TDD-first workflow, story file permissions, test report generation
- QA Agent (Quinn) → Validator Agent: Gate governance, requirements traceability, risk-based testing
- Analyst Agent (Mary) → Analyst Agent: Numbered options, elicitation patterns, curiosity-driven inquiry
- Architect Agent (Winston) → Knowledge Agent: Holistic thinking, cross-stack optimization, living architecture
- PM Agent (John) → Orchestrator Agent: Task workflow management, template-driven efficiency, prioritization

### Story 1.8: Agent Tool Usage Rules & Boundaries

As a **multiagent system developer**,
I want **comprehensive tool usage guidelines for all 5 LangGraph agents**,
so that **tool selection is clear, scope boundaries prevent conflicts, and MCP integration is efficient**.

**Acceptance Criteria:**
1. **Agent Tool Matrix**: Document all agents with assigned MCP tools, primary vs secondary usage
2. **Tool Selection Protocol**: Define decision tree for MCP vs local function selection with performance criteria
3. **Scope Boundaries**: Implement runtime validation preventing agents from using out-of-scope tools
4. **Handoff Triggers**: Define clear conditions when agents should route to different specialists
5. **Out-of-Scope Handling**: Create graceful refusal templates and escalation paths
6. **Runtime Validation**: Implement tool usage validation with boundary violation logging

**Tool Boundary Examples:**
- Serena MCP: Analyst (semantic search) vs Knowledge (filesystem ops) - separate usage contexts
- Context7 MCP: Analyst-only for documentation retrieval
- Sequential Thinking MCP: Analyst-only for complex architectural reasoning
- Graphiti MCP: Knowledge-only for persistent knowledge graphs
- DSPy: Developer/Validator for self-improvement loops

---
