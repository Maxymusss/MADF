# 5. Epic 1: Multi-Agent Development Framework MVP

**Epic Goal**: Develop and validate a 4-agent LangGraph system (Planning + Research + Dev + PM) with Pydantic state management, demonstrating prototype multi-agent coordination for research commentary generation.

**Data Integration**: HTTP bridge integration with free news APIs (NewsAPI, Yahoo Finance, Alpha Vantage, Google News) via mcp-use for financial data access, with simple error handling and basic fallback mechanisms.

**Prototype Infrastructure**: Agents implemented as LangGraph nodes with Pydantic state management, manual BMAD planning workflow, and free news API integration.

## Story 1.1: Basic LangGraph Setup and State Management

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

## Story 1.2: Manual BMAD Planning Integration

As a **multi-agent development system operator**,
I want **a manual workflow for BMAD planning that integrates with LangGraph execution**,
so that **human-generated plans can be structured for agent execution**.

**Acceptance Criteria:**
1. **BMAD Chat Workflow**: Establish process for human to chat with BMAD agent for planning
2. **Plan Structuring**: Convert BMAD output into structured format (JSON/YAML) for LangGraph
3. **Planning Agent Node**: Create LangGraph node that loads and validates BMAD plans
4. **Task Dependencies**: Ensure plan includes agent assignments and task sequencing
5. **Research Commentary Focus**: Plan specifically for free news API FX/rates research commentary
6. **Manual Validation**: Human review and approval of generated plans before execution

**Planning Requirements:**
- PR1: BMAD generates research commentary workflow with agent assignments
- PR2: Plan includes acceptance criteria and deliverable specifications
- PR3: Planning Agent validates plan completeness before agent execution
- PR4: Clear handoff points between Planning, Research, Dev, and PM agents

## Story 1.3: Free News API Integration via mcp-use

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

## Story 1.4: Weekly Market Commentary Generation

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

## Story 1.5: End-to-End Workflow Integration

As a **multi-agent development system operator**,
I want **complete workflow integration from BMAD planning through research commentary delivery**,
so that **the prototype demonstrates full multi-agent coordination capabilities**.

**Acceptance Criteria:**
1. **Complete Workflow**: Execute full workflow from BMAD plan → Free news API data → commentary generation → file delivery
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

## Story 1.6: Claude Code Integration and User Interface

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
