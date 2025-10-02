# 2. Requirements

## Core Architecture Requirements

**AR1:** The system shall implement the 4-Layer Prototype-First Architecture
- **Claude Code Layer**: User interface and task orchestration with familiar interaction patterns
- **BMAD Planning Layer**: Strategic workflow planning through human-agent collaboration (manual in Phase 1, automated in Phase 2)
- **LangGraph Execution Layer**: Multi-agent state machine orchestration with persistence and observability
- **mcp-use Tool Layer**: Secure multi-server tool access with Bloomberg Terminal API integration
- **Incremental Sophistication**: Start with simple implementations (Pydantic state models, manual processes) and add complexity as proven valuable
- **Agent Coordination**: 4-agent system (Planning, Research, Dev, PM) with clear handoffs and state management

**AR2:** The system shall implement LangGraph State Management Foundation
- **State Architecture**: Pydantic schema structure from Phase 1 for robust state management and type safety
- **Agent Nodes**: Each agent (Planning, Research, Dev, PM) implemented as LangGraph nodes with clear inputs/outputs
- **Persistence**: LangGraph checkpointing for workflow resumption and debugging
- **Error Handling**: Basic error handling in Phase 1, sophisticated retry/replanning logic in Phase 2
- **Observability**: LangSmith integration for tracing and performance monitoring
- **Human Integration**: Manual validation points evolving to automated HITL dashboards

## Bloomberg Integration Requirements

**BR1:** The system shall integrate free news data sources for EM Asia markets
- Free news API access (NewsAPI, Yahoo Finance, Alpha Vantage, Google News)
- Geographic focus: EM Asia (CN, TW, KR, HK, SG, TH, MY, PH, ID, IN) + US markets
- Market focus: FX & rates with overview of equity and commodities
- Phase 1: Automated weekly news collection with basic error handling

**BR2:** The system shall implement automated news data handling
- Phase 1: Pydantic models for structured news data (NewsItem, MarketEvent, Commentary)
- Market Focus: FX & rates focused, with brief mention of equity and commodities for outsized moves
- Weekly Processing: Automated collection → analysis → commentary generation
- Research Output: 50-80 word summaries per major market movement/event
- Data Sources: NewsAPI (primary) + Yahoo Finance + Alpha Vantage + Google News

**BR3:** The system shall maintain weekly commentary accuracy and timing
- Weekly data collection cycle for news aggregation and analysis
- "This week" defined clearly: 7-day period ending on report generation date + key future events mention
- Asia timezone awareness for EM market events and timing
- Clear data source attribution and age indicators as reference appendix (not within commentary text)

## Agent-Specific Requirements

**AG1:** Planning Agent - BMAD Integration & Workflow Orchestration (Phase 1)
- Facilitates human-BMAD planning conversations to generate project workflows
- Provides workflow suggestions to humans based on BMAD methodology and project context
- Coordinates with humans for plan approval, modifications, and strategic guidance
- Translates BMAD outputs into structured LangGraph state (Pydantic models)
- Manages technical workflow structure, agent handoffs, and task dependencies
- Handles research commentary project delivery workflow coordination

**AG2:** Research Agent - Data Collection & Analysis (Phase 1)
- Implements LangGraph node for financial data gathering via mcp-use
- Accesses Bloomberg Terminal API and other financial data sources
- Focuses on Asia/G10 FX pairs and interest rate analysis
- Processes data for research commentary generation with basic error handling

**AG3:** Dev Agent - Output Generation & File Management (Phase 1)
- Implements LangGraph node for generating research commentary documents
- Handles file operations and output formatting for hedgemonkey project
- Manages code generation and testing for research tools
- Integrates with project file structure and version control

**AG4:** PM Agent - Coordination & Quality Management (Phase 1)
- Implements LangGraph node for overall project coordination
- Manages task completion verification and quality checks (manual in Phase 1)
- Coordinates between Planning, Research, and Dev agents
- Handles final output validation and delivery confirmation

## Phase 2 Sophistication Requirements

**FR7:** The system shall enhance Pydantic schema-based state management
- Add advanced validation rules and custom validators to existing Pydantic models
- Implement sophisticated data validation and type safety across all agent interactions
- Enable comprehensive error handling and state recovery capabilities with schema validation

**FR8:** The system shall provide automated validation and quality assurance
- Implement ValidationAgent as LangGraph node for automatic output verification
- Add HITL dashboard for human oversight and approval workflows
- Integrate comprehensive error tracking and replanning logic

## Phase 3 Production Requirements

**FR9:** The system shall integrate advanced analytics capabilities
- Connect quantitative analysis agents with existing alphaseek project
- Implement calculation agents for factor-based analytics infrastructure
- Add reusable component libraries for financial analysis workflows

**FR10:** The system shall support enterprise-grade scaling and deployment
- Add containerization and cloud deployment capabilities
- Implement comprehensive monitoring, alerting, and performance optimization
- Enable autonomous application scaffolding and deployment automation

## Non-Functional Requirements

**NFR1:** The system must maintain existing MADF performance characteristics without exceeding current memory usage by more than 20% (target guideline)
- Resource monitoring required during 5-7 day implementation timeline
- Agent processes must be lightweight and efficient

**NFR2:** The system shall implement prototype-first phased delivery:
- Phase 1: 2-3 weeks prototype foundation
  - Week 1: Basic LangGraph setup with 4-agent nodes and Pydantic state models
  - Week 2: Manual BMAD integration, mcp-use Bloomberg connection, first research commentary
  - Week 3: Refinement, testing, and documentation of prototype learnings
- Phase 2: 4-5 weeks sophistication layer (schemas, validation, HITL dashboards)
- Phase 3: Ongoing production features (advanced analytics, automation, deployment)

**NFR3:** The system must implement cost-effective model strategy for LangGraph agent execution
- Use Claude Sonnet for most agent operations with Opus for complex planning tasks
- LangGraph + Anthropic integration for efficient token usage and cost tracking
- Budget monitoring built into LangSmith observability for sustainable operations

**NFR4:** The system shall maintain crash resilience through LangGraph persistence
- LangGraph checkpointing ensures agent states recoverable after system interruptions
- LangSmith tracing provides comprehensive debug information and execution visibility
- File-based outputs maintain accessibility for manual inspection and debugging

**NFR5:** The system must support rapid scaling to additional research agent variants
- Communication protocol must accommodate N research agents without architectural changes
- Agent addition/removal must not require system restart

## Compatibility Requirements

**CR1:** Enhancement must maintain compatibility with existing MCP server infrastructure
- All existing `.mcp.json` configurations must remain functional (currently none defined)
- New MCP servers (news and data sources) must integrate without conflicts (managed through agents via mcp-use)

**CR2:** Enhancement must preserve existing Claude Code tool compatibility
- Current tool loading and analytics systems must continue functioning
- Essential tools list must remain accessible alongside new financial agents

**CR3:** Enhancement must maintain file system structure consistency
- New agent files must follow existing `.claude/` directory conventions
- Configuration files must use dynamic/relative paths for portability

**CR4:** Enhancement must integrate with existing environment management
- Dotenv integration must support new API keys for financial data sources
- Environment variable patterns must follow established MADF conventions

---
