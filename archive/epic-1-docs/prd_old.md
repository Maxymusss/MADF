# Multi-Agent Development Framework PRD

**Version:** 4.1
**Date:** 2025-09-23
**Author:** PM Agent John

---

## 1. Intro Project Analysis and Context

### Existing Project Overview

**Analysis Source:** 3-in-1 agent architecture analysis

**Current Project State:**
The Multi-Agent Development Framework (MADF) implements a prototype-first, layered architecture for AI-driven development workflows. The framework provides:
- **LangGraph Orchestration Core**: State-based graph execution with persistence and observability
- **4-Layer Integration**: Claude Code (interface) → BMAD (planning) → LangGraph (execution) → mcp-use (tools)
- **Bloomberg Data Integration**: Real Terminal API (localhost:8194) with mock fallback for development
- **Prototype Architecture**: Simple implementations that scale to sophisticated features incrementally
- **Multi-Agent Coordination**: Planning, Research, Development, and PM agents with clear handoffs
- **Human-BMAD Integration**: Manual planning workflow that evolves to automated coordination
- Research commentary generation for Asia/G10 FX pairs and interest rates

### Available Documentation Analysis

**Available Documentation:**
- ✓ LangGraph Framework Documentation (.claude/docs-cache/langgraph-docs.md)
- ✓ BMAD Planning Methodology (.claude/docs-cache/bmad-*-docs.md)
- ✓ mcp-use Tool Integration (.claude/docs-cache/mcp-use-docs.md)
- ✓ Claude Code Integration Patterns (CLAUDE.md)
- 🔄 Prototype LangGraph Implementation (langgraph_core/ directory structure)
- 🔄 4-Layer Architecture Design (Claude Code → BMAD → LangGraph → mcp-use)
- ✗ LangGraph Agent Nodes (Planning, Research, Dev, PM agents as Python implementations)
- ✗ Bloomberg mcp-use Integration (Direct API access without complex wrappers)

**Note:** Core framework documentation available. Prototype LangGraph multi-agent implementation needs development.

### Enhancement Scope Definition

**Enhancement Type:**
- ☑️ **New Framework Implementation** (Primary)
- ☑️ **Multi-Agent Orchestration** (LangGraph state machine with 4 agents)
- ☑️ **Tool Integration Architecture** (mcp-use for Bloomberg and financial data access)

**Enhancement Description:**
Implement a prototype-first multi-agent development platform using a 4-layer architecture: Claude Code for user interface, BMAD for strategic planning, LangGraph for multi-agent execution, and mcp-use for tool integration. The system starts with simplified implementations (Pydantic state models, manual BMAD chat, HTTP bridge tool access) and evolves incrementally to sophisticated features (validation automation, HITL dashboards, advanced error handling). This approach enables rapid value delivery while establishing the foundation for production-grade capabilities.

**Core Innovation - Prototype-First Multi-Agent Architecture:**
- LangGraph state machine orchestrates 4 specialized agents with clear handoffs
- BMAD planning layer generates structured workflows through human-agent collaboration
- mcp-use tool layer provides secure, multi-server access to Bloomberg and financial data
- Incremental sophistication: Start simple, add schemas/automation/validation as proven valuable
- Claude Code integration maintains familiar user experience

**Three-Phase Evolution:**
- Phase 1: Prototype Foundation (2-3 weeks). Basic LangGraph with 4 agents, manual BMAD planning, direct mcp-use integration
- Phase 2: Sophistication Layer (4-5 weeks). Add schemas, automated validation, HITL dashboards, error handling
- Phase 3: Production Features (ongoing). Advanced analytics, application generation, deployment automation

**Bloomberg Integration Strategy:**
- Real Bloomberg Terminal API (localhost:8194) via mcp-use client for production accuracy
- Mock Bloomberg service for development environment testing
- Asia/G10 FX pairs and interest rates as research commentary focus
- HTTP bridge mcp-use integration in prototype, with sophisticated wrappers in later phases

**Impact Assessment:**
- ☑️ **Significant Enhancement** (enhanced agent infrastructure with lifecycle management)
- Integration of comprehensive data/news sources including Bloomberg Terminal API
- Implementation of 3-in-1 agent architecture with AgentBase foundation
- Migration from basic agent configurations to enhanced infrastructure system
- Multi-domain development capabilities with usage analytics

### Goals and Background Context

**Goals:**

**Phase 1 Goals (Prototype Foundation, 2-3 weeks):**
• Deploy basic LangGraph with 4-agent system: Planning + Research + Dev + PM agents
• Implement manual BMAD planning workflow (human chat with BMAD agent)
• Establish direct mcp-use integration with Bloomberg Terminal API
• Deliver first research commentary demonstrating multi-agent coordination
• Create structured state management with Pydantic models from Phase 1
• Validate core architecture pattern with minimal viable implementation
• Output research commentary to hedgemonkey project directory directory

**Phase 2 Goals (Sophistication Layer, 4-5 weeks):**
• Add Pydantic schemas for structured state management and validation
• Implement automated ValidationAgent for quality checks and acceptance criteria
• Create HITL dashboard for human oversight and approval workflows
• Add sophisticated error handling, retry logic, and replanning capabilities
• Expand HTTP bridge mcp-use integration with tool wrappers and fallback mechanisms
• Evaluate tmux integration for multi-agent session management and monitoring
• Integrate advanced analytics capabilities with existing alphaseek project

**Phase 3 Goals (Production Features, ongoing):**
• Implement quantitative analytics engine with specialized calculation agents
• Build reusable component libraries for financial analysis workflows
• Add autonomous coding capabilities with full testing and validation
• Enable application scaffolding and deployment automation
• Implement tmux-based development environment for enterprise multi-agent workflows
• Scale to enterprise-grade features based on production learnings
• Full integration with alphaseek project for advanced analytics

**Background Context:**
The current AI development landscape lacks sophisticated multi-agent coordination frameworks with proper lifecycle management and permissions. This enhancement addresses the critical need for reliable multi-agent development platforms by implementing an enhanced agent validation system. The approach leverages the existing MADF MCP infrastructure while adding comprehensive multi-agent capabilities, focusing on the concrete use case of research commentary projects where agent coordination accuracy is mission-critical for project delivery.

### Development Roadmap

**Phase 1: Prototype Foundation** (2-3 weeks)
- Basic LangGraph with 4-agent system (Planning + Research + Dev + PM)
- Manual BMAD planning workflow implementation
- Direct mcp-use Bloomberg integration
- Research commentary delivery to hedgemonkey project
- Structured state management with Pydantic models
- Sub-projects: Core graph setup, agent nodes, tool integration

**Phase 2: Sophistication Layer** (4-5 weeks)
- Add Pydantic schemas for structured state management
- Implement automated ValidationAgent and HITL dashboards
- Expand to multi-server mcp-use configuration
- Add comprehensive error handling and replanning logic
- Production-ready observability with LangSmith
- Sub-projects: Schema design, validation automation, human oversight UI

**Phase 3: Production Features** (ongoing)
- Quantitative analytics engine integration with alphaseek project
- Application scaffolding and deployment automation
- Advanced learning and optimization capabilities
- Enterprise-grade scaling and monitoring
- Sub-projects: Calculation agents, component libraries, autonomous development

**End Product:** A self-improving agentic working group that learns from each project delivery, continuously enhancing its capabilities through error tracking, validation feedback, and performance metrics.

### Change Log
| Change | Date | Version | Description | Author |
|--------|------|---------|-------------|---------|
| Initial PRD Creation | 2025-09-21 | v1.0 | Multi-agent development framework enhancement | PM Agent John |
| Major Scope Revision | 2025-09-21 | v3.1 | Revised Phase 1 to enhanced infrastructure (5-7 days), implemented AgentBase architecture, expanded to 3-agent system, added precise success metrics | Claude Code |
| Clarity Improvements | 2025-09-23 | v3.2 | Resolved all unclear sections marked with ??, standardized terminology, clarified Bloomberg integration scope, project organization, and timeline consistency | Claude Code |
| Architecture Revision | 2025-09-23 | v4.0 | Revised to prototype-first 4-layer architecture: Claude Code → BMAD → LangGraph → mcp-use, with incremental sophistication approach | Claude Code |
| Requirements Correction | 2025-09-23 | v4.1 | Corrected data sources (Bloomberg → free news APIs), output format (50-80 word weekly summaries), geographic focus (EM Asia + US) | PM Agent John |

---

## 2. Requirements

### Core Architecture Requirements

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

### Bloomberg Integration Requirements

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

### Agent-Specific Requirements

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

### Phase 2 Sophistication Requirements

**FR7:** The system shall enhance Pydantic schema-based state management
- Add advanced validation rules and custom validators to existing Pydantic models
- Implement sophisticated data validation and type safety across all agent interactions
- Enable comprehensive error handling and state recovery capabilities with schema validation

**FR8:** The system shall provide automated validation and quality assurance
- Implement ValidationAgent as LangGraph node for automatic output verification
- Add HITL dashboard for human oversight and approval workflows
- Integrate comprehensive error tracking and replanning logic

### Phase 3 Production Requirements

**FR9:** The system shall integrate advanced analytics capabilities
- Connect quantitative analysis agents with existing alphaseek project
- Implement calculation agents for factor-based analytics infrastructure
- Add reusable component libraries for financial analysis workflows

**FR10:** The system shall support enterprise-grade scaling and deployment
- Add containerization and cloud deployment capabilities
- Implement comprehensive monitoring, alerting, and performance optimization
- Enable autonomous application scaffolding and deployment automation

### Non-Functional Requirements

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

### Compatibility Requirements

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

## 3. Technical Constraints and Integration Requirements

### Existing Technology Stack

**Primary Language**: Python (LangGraph orchestration) + TypeScript/Node.js (mcp-use tool access)
**Core Frameworks**: LangGraph (orchestration), BMAD (planning), mcp-use (tool access)
**Integration Bridge**: HTTP API (FastAPI ↔ Express) for Python-TypeScript communication
**News Access**: Free news APIs (NewsAPI, Yahoo Finance, Alpha Vantage, Google News)
**Existing Dependencies**: Most infrastructure already in place (mcp-use, pydantic, aiohttp, langchain)
**Minimal Additions**: langgraph, fastapi, express, news API client libraries

### Phase 2 Technical Stack (TBD)
**Quantitative Libraries**: TBD (candidates: numpy, pandas, scipy, quantlib)
**Calculation Frameworks**: TBD based on performance requirements
**Data Processing**: TBD (streaming vs batch processing decision pending)
**Visualization**: TBD (candidates: matplotlib, plotly, d3.js)

### Phase 3 Technical Stack (TBD)
**Application Frameworks**: TBD based on use case requirements
**UI Libraries**: TBD (React, Vue, or native solutions)
**Deployment Infrastructure**: TBD (containerization, cloud platforms)
**API Frameworks**: TBD (REST, GraphQL, WebSocket requirements)

### Integration Approach

**MCP Integration Strategy**: Direct mcp-use client integration with Bloomberg Terminal API in Phase 1, expanding to multi-server configuration (Yahoo Finance, Google News, Reuters) in Phase 2

**Agent Communication Strategy**: LangGraph state management with Pydantic schemas from Phase 1 (not dicts), HTTP bridge for tool access

**Model Integration Strategy**:
- Planning Agent: Manual BMAD coordination (Phase 1) evolving to automated orchestration
- All Agents: LangGraph + Anthropic integration with Claude Sonnet for cost-effective operation
- Complex Planning: Claude Opus for sophisticated workflow generation when needed

**Tool Access Strategy**: mcp-use library enables dynamic multi-server configuration and simultaneous tool access across multiple data sources without pre-configuration complexity

### Code Organization and Standards

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
### Deployment and Operations

**Build Process Integration**: Leverage existing npm scripts structure, add enhanced agent startup commands
**Configuration Management**: Extend existing dotenv patterns for financial API keys and data source credentials
**Monitoring and Logging**: Implement error tracking system building on existing tool analytics framework
**Environment Setup**: Document financial data source API key requirements and setup procedures

### Risk Assessment and Mitigation

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

## 4. Epic and Story Structure

### Epic Approach

**Epic Structure Decision**: Three-phase epic structure aligned with platform evolution roadmap.

**Rationale**:
- Phase 1 (Epic 1): Establishes prototype foundation with basic LangGraph multi-agent system (2-3 weeks)
- Phase 2 (Epic 2): Adds sophistication layer with schemas, validation, and HITL (4-5 weeks)
- Phase 3 (Epic 3): Implements production features with advanced analytics and deployment (ongoing)

This prototype-first approach enables rapid value delivery through research commentary generation while establishing the foundation for sophisticated multi-agent capabilities. Each phase builds incrementally on proven functionality.

---

## 5. Epic 1: Multi-Agent Development Framework MVP

**Epic Goal**: Develop and validate a 4-agent LangGraph system (Planning + Research + Dev + PM) with Pydantic state management, demonstrating prototype multi-agent coordination for research commentary generation.

**Data Integration**: HTTP bridge integration with Bloomberg Terminal API via mcp-use for financial data access, with simple error handling and basic fallback mechanisms.

**Prototype Infrastructure**: Agents implemented as LangGraph nodes with Pydantic state management, manual BMAD planning workflow, and basic tool integration.

### Story 1.1: Basic LangGraph Setup and State Management

As a **multi-agent development system operator**,
I want **a basic LangGraph orchestration system with 4 agent nodes**,
so that **we can establish the foundation for multi-agent workflow execution**.

**Acceptance Criteria:**
1. **LangGraph Foundation**: Create StateGraph with 4 nodes (Planning, Research, Dev, PM)
2. **Pydantic State Management**: Implement Pydantic models for structured agent state passing
3. **Agent Handoffs**: Define clear edges between agents with Pydantic state filtering
4. **Persistence Setup**: Configure LangGraph checkpointing for workflow recovery
5. **Observability**: Integrate LangSmith for basic tracing and monitoring
6. **Error Handling**: Add basic try/catch and logging for agent operations

**Infrastructure Verification:**
- IV1: LangGraph nodes execute successfully with Pydantic state management
- IV2: Agent handoffs work correctly with structured state passing
- IV3: LangSmith tracing captures execution flow and performance

### Story 1.2: Manual BMAD Planning Integration

As a **multi-agent development system operator**,
I want **a manual workflow for BMAD planning that integrates with LangGraph execution**,
so that **human-generated plans can be structured for agent execution**.

**Acceptance Criteria:**
1. **BMAD Chat Workflow**: Establish process for human to chat with BMAD agent for planning
2. **Plan Structuring**: Convert BMAD output into structured format (JSON/YAML) for LangGraph
3. **Planning Agent Node**: Create LangGraph node that loads and validates BMAD plans
4. **Task Dependencies**: Ensure plan includes agent assignments and task sequencing
5. **Research Commentary Focus**: Plan specifically for Bloomberg FX/rates research commentary
6. **Manual Validation**: Human review and approval of generated plans before execution

**Planning Requirements:**
- PR1: BMAD generates research commentary workflow with agent assignments
- PR2: Plan includes acceptance criteria and deliverable specifications
- PR3: Planning Agent validates plan completeness before agent execution
- PR4: Clear handoff points between Planning, Research, Dev, and PM agents

### Story 1.3: Free News API Integration via mcp-use

As a **financial research system operator**,
I want **automated news collection from free APIs through mcp-use client**,
so that **research agents can gather market news for weekly commentary generation**.

**Acceptance Criteria:**
1. **mcp-use Client Setup**: Configure mcp-use to connect to free news APIs via HTTP bridge
2. **Research Agent Integration**: Implement Research Agent node with multi-source news access
3. **Geographic Coverage**: EM Asia markets (CN, TW, KR, HK, SG, TH, MY, PH, ID, IN) + US
4. **Market Coverage**: FX & rates focused, equity/commodities for outsized moves only
5. **API Integration**: NewsAPI (primary), Yahoo Finance, Alpha Vantage, Google News
6. **Basic Error Handling**: Handle API failures with retry logic and source fallback
7. **Data Formatting**: Structure news data for weekly analysis and commentary generation

### Story 1.4: Weekly Market Commentary Generation

As a **financial research system operator**,
I want **automated weekly commentary generation using multi-agent coordination**,
so that **I receive concise 50-80 word summaries of major market movements**.

**Acceptance Criteria:**
1. **Research Agent Execution**: Research Agent node collects weekly news data per BMAD plan
2. **Dev Agent Processing**: Dev Agent formats news into weekly commentary structure
3. **Content Generation**: Generate 50-80 word summaries per major movement/event
4. **Geographic Focus**: EM Asia + US markets with appropriate timezone awareness
5. **File Output Management**: Save weekly commentary to hedgemonkey project directory
6. **PM Agent Coordination**: PM Agent validates completion and manages final delivery
7. **Reference Attribution**: Append data source attribution separate from commentary text

**Weekly Commentary Features:**
- WCF1: Major FX & rates movements with driver analysis (policy, geopolitical, sentiment)
- WCF2: Brief equity/commodities mentions for outsized moves only
- WCF3: Key future events mention alongside current week analysis
- WCF4: 7-day period ending on report generation date coverage
- WCF5: Reference appendix with source attribution and data age indicators

### Story 1.5: End-to-End Workflow Integration

As a **multi-agent development system operator**,
I want **complete workflow integration from BMAD planning through research commentary delivery**,
so that **the prototype demonstrates full multi-agent coordination capabilities**.

**Acceptance Criteria:**
1. **Complete Workflow**: Execute full workflow from BMAD plan → Bloomberg data → commentary generation → file delivery
2. **Agent Coordination**: Validate that all 4 agents (Planning, Research, Dev, PM) work together correctly
3. **State Management**: Ensure LangGraph state properly passes between agents without data loss
4. **Error Recovery**: Test workflow resilience with LangGraph checkpointing and error handling
5. **Performance Monitoring**: Use LangSmith to track execution time, costs, and success rates
6. **Manual Validation**: Human review confirms commentary quality and delivery accuracy

**Integration Validation Features:**
- IV1: Full workflow completes successfully with real free news API data
- IV2: Generated weekly commentary meets 50-80 word format standards
- IV3: LangGraph persistence enables workflow recovery after interruption
- IV4: Agent handoffs work reliably with proper state filtering
- IV5: Reference attribution properly separated from commentary content

### Story 1.6: Claude Code Integration and User Interface

As a **MADF user**,
I want **seamless integration between Claude Code and the LangGraph multi-agent system**,
so that **I can trigger research commentary generation through familiar Claude Code interface**.

**Acceptance Criteria:**
1. **Claude Code Entry Point**: Create claude_interface.py that accepts user requests and initializes LangGraph
2. **Task Integration**: Integrate with existing Claude Code task system for research commentary requests
3. **Progress Reporting**: Provide real-time updates to user on agent execution progress
4. **Result Delivery**: Return formatted research commentary to user with execution summary
5. **Error Communication**: Clear error messages when workflow fails with recovery suggestions
6. **Cost Reporting**: Show API costs and execution time for budget awareness

**Integration Success Criteria:**
- CI1: User can request "Generate FX research commentary" through Claude Code
- CI2: System provides progress updates during multi-agent execution
- CI3: Results delivered in user-friendly format with hedgemonkey project integration
- CI4: Error handling provides actionable feedback without technical details
- CI5: Performance metrics help user understand system efficiency

**Integration Verification:**
- IV1: Report generation integrates with existing MADF documentation structure in `docs/` directory
- IV2: Report output does not conflict with existing system outputs or analytics files
- IV3: Generated reports maintain consistent formatting with existing MADF documentation standards

---

## 6. Epic 2: Sophistication Layer (Phase 2)

**Epic Goal**: Add sophisticated features to the proven prototype foundation: Pydantic schemas, automated validation, HITL dashboards, and enhanced error handling.

**Foundation**: Builds on proven Phase 1 prototype with 4-agent LangGraph system and successful research commentary generation.

**Estimated Stories**: 6-8 stories covering:
- Pydantic schema implementation for structured state management
- ValidationAgent development for automated quality checks
- HITL dashboard creation for human oversight workflows
- Multi-server mcp-use configuration and tool wrappers
- Advanced error handling and replanning logic
- LangSmith observability and performance monitoring

**Success Criteria**: 80% error reduction, 90% automated validation accuracy, <2 minute human review time

---

## 7. Epic 3: Production Features (Phase 3)

**Epic Goal**: Scale to production-grade capabilities with advanced analytics integration, enterprise features, and deployment automation.

**Foundation**: Builds on Phase 2 sophistication with proven schemas, validation, and human oversight capabilities.

**Estimated Stories**: 8-12 stories covering:
- Quantitative analytics integration with alphaseek project
- Calculation agents for factor-based analytics infrastructure
- Application scaffolding and deployment automation
- Enterprise monitoring, alerting, and performance optimization
- Advanced component libraries and reusable workflows
- Container orchestration and cloud deployment capabilities

**Success Criteria**: Production deployment, alphaseek integration, autonomous operation >80%

---

## 8. Success Metrics and Validation

### Phase 1 Success Criteria (Prototype Validation)
- ✓ 4-agent LangGraph system operational within 2-3 weeks (Planning + Research + Dev + PM)
- ✓ Research commentary successfully generated with Bloomberg news + price verification
- ✓ Manual BMAD planning workflow demonstrated with structured output
- ✓ HTTP bridge operational (Python LangGraph ↔ TypeScript mcp-use)
- ✓ Bloomberg Terminal API + CSV data access functional
- ✓ Agent coordination through Pydantic state management proven functional
- ✓ Factual accuracy validation + human quality check demonstrated
- ✓ Root directory structure established (no refactoring needed for production)

### Phase 2 Success Criteria (Sophistication Validation)
- ✓ Advanced Pydantic validation rules reduce state management errors by 80%
- ✓ Automated ValidationAgent catches 90% of quality issues before human review
- ✓ HITL dashboard enables efficient human oversight with <2 minute review time
- ✓ Multi-server mcp-use configuration supports 3+ data sources simultaneously
- ✓ Error handling and replanning logic resolves 80% of failures automatically
- ✓ LangSmith observability provides comprehensive workflow monitoring

### Phase 3 Success Criteria (TBD)
- TBD: Application generation time targets
- TBD: Code quality metrics
- TBD: Deployment success rates
- TBD: User satisfaction scores
- TBD: Autonomous operation percentage

### Learning Framework Metrics
- Error reduction rate per project cycle
- Agent decision accuracy improvements
- Time to complete similar tasks (learning curve)
- Human intervention frequency (autonomy measure)
- Knowledge transfer between project types

---

**Note:** This revised PRD implements a prototype-first approach with a realistic 2-3 week Phase 1 timeline, establishing a 4-layer architecture (Claude Code → BMAD → LangGraph → mcp-use) that scales incrementally. The framework starts with simple implementations and adds sophistication as proven valuable, enabling rapid research commentary delivery while building toward production-grade multi-agent capabilities.