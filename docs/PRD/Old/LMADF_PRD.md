# LMADF: LangGraph Multi-Agent Development Framework – PRD

**Problem:** Manual task routing and inconsistent agent utilization in development workflows.
**Objective:** Automated multi-agent task routing via LangGraph StateGraph with Claude Code + Task Master integration.
**Stakeholders:** Human In-the-loop (HI)

## Functional Requirements

1. **LangGraph StateGraph:** Multi-agent orchestration with 13 specialized agents (PM, HR, HI, DA, SR, JR, JC, SC, TA, QA, DAA, SA, UX) and dynamic task routing through intake → component check → research → agent activation + context provision → implementation → validation → feedback → improve workflow 
2. **Task Classification:** Auto-routing by keywords (frontend/backend/qa/research/ux), complexity analysis (simple/medium/complex), dependency detection
3. **Agent Integration:** Leverage `.claude/agents/*.json` configs with specialized prompts and optimal agent/rule/hooks/commands/mcp setup
4. **Task Master Bridge:** Monitor `.taskmaster/state.json`, execute workflows, sync status
5. **Project Context:** Alphaseek-specific handling (80k LOC) with context injection
6. **Confidence Scoring:** Performance tracking with workflow transparency
7. **Persistence & Logging:** JSON state management with agent-categorized error logs for debugging
8. **CLI Interface:** Direct submission and real-time monitoring
9. **Workflow Transparency:** Complete agent history and error logging
10. **Self-Improvement:** Critical/repeated errors trigger research and agent configuration improvements

## Non-Functional Requirements

- **Simplicity:** File-based persistence, minimal infrastructure
- **Performance:** <5s task routing, optimized execution
- **Reliability:** Retry logic, graceful fallbacks, state recovery
- **Integration:** Claude Code + Task Master compatibility, MCP support
- **Debugging:** Transparent JSON state files, comprehensive logging
- **Expandability:** Modular design for future agents/features  

**Agent-Specific Implementations:**

- **PM (Project Manager):** Creates `pm_context` package, analyzes complexity, sets routing decisions, propose agents number/type
- **HR (Human Resources):** Updates `hr_metrics`, manages agent activation in `active_agent`, tracks performance (different metrics for agents)
- **HI (Human In-the-loop):** Reviews proposals, populates `hi_decisions` with approval/rejection outcomes
- **DA (Doc Agent):** Populates `da_cache` with reusable component findings
- **SR (Senior Research):** Fills `sr_findings` with comprehensive solution approaches and architecture
- **JR (Junior Research):** Populates `jr_findings` with standard solution summaries
- **JC (Junior Coder):** Generates basic implementation in `jc_output` for simple tasks
- **SC (Senior Coder):** Generates complex architecture and implementation in `sc_output`
- **TA (Test Agent):** Validates implementations and populates `ta_results` with quality metrics
- **QA (Quant Agent):** Creates financial models and analysis in `qa_models` for alphaseek tasks
- **DAA (Data Agent):** Builds data processing pipelines in `daa_pipelines`
- **SA (Security Agent):** Performs security assessments and populates `sa_assessments`
- **UX (User Experience Agent):** Designs interfaces and user flows, populates `ux_designs` with wireframes and usability guidelines

## User Workflows

- **Task Submission:** PM generates tasks from PRD using Task Master and sequential thinking
- **Workflow Execution:**
  1. **PM** receives and classifies task (frontend/backend/qa/research/quant/data/security/ux)
  2. **DA** checks dictionary for reusable components
  3. If no reuse → **SR/JR** finds solutions and approaches (based on complexity)
  4. **PM** analyzes complexity/dependencies, creates context package
  5. **HR** activates appropriate implementation agents (JC/SC/QA/DAA/SA/UX)
  6. **PM** provides context/tools to activated agent
  7. **Active IA Agent** (JC/SC/QA/DAA/SA/UX) delivers solution
  8. **TA** validates with state tracking and metrics
- **Task Master Integration:** Batch processing with `.taskmaster/state.json` monitoring
- **Progress Monitoring:** Real-time status via LangGraph state management
- **Error Handling:** Auto-retry with manual fallback, agent-categorized error logging in state
- **Self-Improvement:**
  1. **HR** reviews performance every 20-call cycles
  2. Identifies critical/repeated errors in `hr_metrics`
  3. Triggers **SR** for improvement analysis
  4. **HI** reviews and approves/rejects improvement proposals
- **Research Workflows:**
  1. **Project-triggered:** PM requests research → SR/JR investigates → PM summarizes
  2. **HR-triggered:** HR identifies error patterns → SR analyzes → HR receives recommendations
  3. **Complexity-based:** PM analyzes task → HR activates SR/JR → Research provides context
- **Specialist Workflows:**
  1. **Financial Tasks:** PM → QA for alphaseek trading/modeling → TA validates financial logic
  2. **Data Tasks:** PM → DAA for ETL/analysis → TA validates data integrity
  3. **Security Tasks:** PM → SA for audits/implementation → TA validates security measures

## Dependencies & Constraints

- **Technical Stack:** LangGraph StateGraph, Claude API, Claude Code + Task Master, MCPs, rules, hooks, commands
- **File System:** JSON state persistence, `.claude/agents/` configs
- **Integration:** `.taskmaster/state.json` monitoring, MCP compatibility
- **Focus:** Alphaseek project testing (80k LOC)
- **Timeline:** 3-week MVP with immediate validation
- **Testing:** Real tasks, integration validation, performance benchmarks  

## Technical Architecture

**Agent Node Pattern:**
1. Load `.claude/agents/*.json` configuration
2. Build role-specific prompt with task context
3. Execute Claude API call with project context
4. Extract actionable results
5. Update state with results and confidence score
6. Handle errors with retry/fallback logic

### Technical Implementation

**Storage:** JSON file persistence for state/debugging
**Integration:** Task Master `.taskmaster/state.json` monitoring
**Agent Configs:** Existing `.claude/agents/*.json` reuse
**APIs:** Claude API with role-specific prompts

## Implementation Timeline

**Total Project Duration:** 3 weeks
**Approach:** LangGraph-centric MVP with immediate validation and agent-by-agent testing refinement

## Agent Testing & Refinement Plan

**Core Setup Phase (Week 1):**
1. **PM Agent** - Test task classification, context creation, routing decisions
2. **HR Agent** - Test agent activation, performance tracking, metrics management
3. **HI Agent** - Test approval workflows, decision capture, human oversight

**Research & Implementation Phase (Week 2):**
4. **DA Agent** - Test component discovery, cache population, reuse identification
5. **SR Agent** - Test complex research, architecture findings, solution approaches
6. **JR Agent** - Test standard research, basic findings, solution summaries
7. **JC Agent** - Test simple implementations, basic code generation
8. **SC Agent** - Test complex implementations, architecture decisions
9. **TA Agent** - Test validation workflows, quality metrics, results capture

**Specialist Phase (Week 3):**
10. **DAA Agent** - Test data pipeline creation, ETL workflows, data processing
11. **QA Agent** - Test financial modeling, quantitative analysis, alphaseek integration
12. **SA Agent** - Test security assessments, audit workflows, vulnerability analysis
13. **UX Agent** - Test interface design, wireframe creation, usability guidelines

**Testing Methodology per Agent:**
- Hooks integration and trigger testing
- Commands execution and workflow validation
- MCPs connectivity and data exchange
- Rules compliance and constraint checking
- Performance metrics and error handling
- State management and handoff protocols

### Week 1: LangGraph Foundation & Core Agents
**Primary Deliverable:** `madf_langgraph.py` + Core Agent Testing

**Core Components:**
- StateGraph with 4 nodes (TaskIntake, Research, Implementation, QualityAssurance)
- Keyword-based task classification
- `.claude/agents/*.json` integration
- Role-specific Claude API calls
- State schema with confidence scoring and error handling
- Agent history tracking

**Core Agent Implementation & Testing:**
- **PM Agent**: Task intake, classification, context distribution, routing decisions
- **HR Agent**: Agent lifecycle management, performance monitoring, activation control
- **HI Agent**: Human approval gates, decision workflows, oversight protocols

**Success Criteria:**
- Functional 4-node StateGraph
- Working task classification/routing
- Claude API + agent config integration
- State management and error handling operational
- PM/HR/HI agents fully tested with hooks/commands/MCPs/rules integration

### Week 2: Research & Implementation Agents + Task Master Integration
**Primary Deliverable:** `taskmaster_integration.py` + Research/Implementation Agent Testing

**Integration Points:**
- Monitor `.taskmaster/state.json` for pending tasks
- Convert Task Master format to LMADF compatibility
- Sync Task Master with workflow progress
- Store LMADF results in Task Master
- Generate performance metrics and reports

**Research & Implementation Agent Testing:**
- **DA Agent**: Component discovery, cache management, reuse identification
- **SR Agent**: Complex research workflows, architecture analysis, advanced solutions
- **JR Agent**: Standard research patterns, basic findings, routine analysis
- **JC Agent**: Simple implementation tasks, basic code generation, routine changes
- **SC Agent**: Complex implementations, architecture decisions, advanced solutions
- **TA Agent**: Validation workflows, quality metrics, test execution

**CLI Commands:**
```bash
python taskmaster_integration.py list           # Show pending tasks
python taskmaster_integration.py process <id>   # Process specific task
python taskmaster_integration.py process-all    # Process all suitable tasks
python taskmaster_integration.py report         # Performance metrics
```

**Success Criteria:**
- Complete Task Master integration with status sync
- Working format conversion and workflow execution
- Functional performance metrics/reporting
- Alphaseek context injection operational
- DA/SR/JR/JC/SC/TA agents fully tested with hooks/commands/MCPs/rules integration

### Week 3: Specialist Agents + CLI Interface & Real-World Testing
**Primary Deliverable:** `madf_cli.py` + Specialist Agent Testing

**Specialist Agent Testing (Priority Order):**
- **DAA Agent**: Data pipeline creation, ETL workflows, data processing validation
- **QA Agent**: Financial modeling, quantitative analysis, alphaseek integration testing
- **SA Agent**: Security assessments, audit workflows, vulnerability analysis
- **UX Agent**: Interface design, wireframe creation, usability guidelines

**User Interface Features:**
- Simple task submission: `python madf_cli.py submit "Implement user authentication"`
- Real-time progress monitoring
- Agent workflow visualization/debugging
- MCP infrastructure integration
- Performance dashboards

**Testing & Validation:**
- Real alphaseek tasks (80k LOC codebase)
- Performance benchmarking/optimization
- CI/CD integration validation
- Error scenario testing/recovery
- End-to-end workflow validation

**Success Criteria:**
- Fully functional CLI for submission/monitoring
- Successful alphaseek task processing
- Completed performance validation/optimization
- Documentation and examples delivered
- DAA/QA/SA/UX agents fully tested with hooks/commands/MCPs/rules integration

## Success Metrics

**Performance:** <100ms critical context, <500ms full context, <5s sync lag, 95%+ accuracy, 99.9% availability
**Coordination:** 95% SLA compliance, 80%+ agent utilization, 90%+ context-driven decisions, 40%+ duplicate work reduction
**Cost/ROI:** <5% overhead, track coordination savings, 100% budget compliance, measure ROI contribution

## Acceptance Criteria

| Criterion | Target |
|-----------|--------|
| **Task Success Rate** | ≥80% per specialist (20-task cycle) |
| **Error Rate** | ≤20% failures per cycle |
| **Auto Specialist Creation** | When >5 similar tasks appear |
| **Trust Autonomy** | 80% of agents maintain ≥60 trust |
| **ROI (Month 3)** | ≥100% cumulative ROI |
| **Budget Compliance** | Throttle at 70%/85%/95% thresholds |
| **Routing SLAs** | 95% meet targets (<4h High, <1h Critical) |
| **Gate Adherence** | 100% high-risk tasks invoke human gate |
| **System Reliability** | 99% uptime, 90% fallback success |
| **Context Performance** | <100ms critical, <500ms full, <5s sync |
| **Context Overhead** | <5% operational costs |

## Key Implementation Advantages

### LangGraph Benefits:
- Built-in state management/orchestration
- Leverages Claude Code + Task Master infrastructure
- Reliable JSON file persistence
- 3-week MVP with immediate validation
- Real alphaseek testing
- Usage-based iterative expansion

### Asset Utilization:
- Reuses `.claude/agents/*.json` configs
- Integrates with operational Task Master
- Builds on existing LangGraph setup
- Leverages configured MCP servers
- Maintains alphaseek focus/context

### Risk Mitigation:
- **Technical:** Simple workflow reduces LangGraph complexity
- **Integration:** Non-invasive approach preserves functionality
- **Performance:** File persistence adequate for MVP
- **Project:** Clear timeline with defined deliverables

## Agent Definitions

### Core Agents (CA)

**1. PM Agent (PM)**
- **Role:** Task coordinator and context distributor
- **Responsibilities:**
  - Analyze task complexity and dependencies
  - Distribute context to appropriate agents
  - Track progress and manage blockers
  - Identify specialist requirements
- **Activation:** Triggered after task intake
- **Tools:** Task Master MCP, Sequential Thinking MCP, Context management
- **Outputs:** Task assignments, complexity assessments, context packages

**2. HR Agent (HR)**
- **Role:** Agent lifecycle and performance manager
- **Responsibilities:**
  - Monitor agent performance (20-call cycles)
  - Activate/deactivate agent instances
  - Identify critical/repeated errors
  - Trigger research for improvements
  - Propose specialist agent creation
- **Activation:** Periodic review cycles and on-demand by PM
- **Tools:** Performance metrics, agent configuration management
- **Outputs:** Performance reports, agent recommendations, improvement proposals

**3. Human In-the-loop (HI)**
- **Role:** Human oversight and decision maker
- **Responsibilities:**
  - Review agent recommendations
  - Approve/reject improvement proposals
  - Handle escalations and edge cases
  - Provide strategic guidance
- **Activation:** On HR recommendations or critical decisions
- **Tools:** Review dashboards, decision interfaces
- **Outputs:** Approval decisions, strategic direction, feedback

### Implementation Agents (IA)

**4. Doc Agent (DA)**
- **Role:** Component reuse and documentation checker
- **Responsibilities:**
  - Check documentation dictionary for existing solutions
  - Identify reusable components
  - Maintain component registry
  - Suggest existing implementations
- **Activation:** After task intake, before research
- **Tools:** Documentation search, component registry access
- **Outputs:** Reusability assessment, component suggestions

**5. Senior Research (SR)**
- **Role:** Complex research and technical investigation
- **Responsibilities:**
  - Research advanced technical solutions
  - Analyze complex codebase patterns
  - Investigate cutting-edge best practices
  - Provide architectural guidance
- **Activation:** For complex research tasks (complexity score >7)
- **Tools:** WebSearch, WebFetch, Grep, Glob, Read, advanced analysis tools
- **Outputs:** Comprehensive solution recommendations, technical analysis, architecture proposals

**6. Junior Research (JR)**
- **Role:** Basic research and information gathering
- **Responsibilities:**
  - Research standard solutions
  - Gather documentation and examples
  - Perform routine analysis tasks
  - Support Senior Research efforts
- **Activation:** For simple research tasks (complexity score <4)
- **Tools:** WebSearch, WebFetch, basic analysis tools
- **Outputs:** Standard solution recommendations, documentation summaries

**7. Junior Coder (JC)**
- **Role:** Basic implementation specialist
- **Responsibilities:**
  - Handle simple, well-defined tasks
  - Implement routine changes
  - Follow established patterns
  - Apply standard solutions
- **Activation:** For simple coding tasks (complexity score <4)
- **Tools:** Edit, Write, basic development tools
- **Outputs:** Basic implementations, routine updates

**8. Senior Coder (SC)**
- **Role:** Complex implementation specialist
- **Responsibilities:**
  - Handle complex multi-file changes
  - Make architecture decisions
  - Solve advanced technical problems
  - Mentor junior implementations
- **Activation:** For complex coding tasks (complexity score >7)
- **Tools:** Full development tool suite with elevated permissions
- **Outputs:** Complex implementations, architecture decisions, technical guidance

**9. Test Agent (TA)**
- **Role:** Quality assurance and validation
- **Responsibilities:**
  - Validate implemented solutions
  - Maintain state tracking
  - Run test suites
  - Verify requirements compliance
- **Activation:** After implementation completion
- **Tools:** Test runners, validation frameworks, state management
- **Outputs:** Test results, validation reports, quality metrics

### Specialist Agents (SPA)

**10. Quant Agent (QA)**
- **Role:** Quantitative analysis and financial modeling
- **Responsibilities:**
  - Perform financial calculations and modeling
  - Analyze market data and trading strategies
  - Implement quantitative algorithms
  - Validate financial logic
- **Activation:** For alphaseek financial/trading tasks
- **Tools:** Mathematical libraries, financial APIs, data analysis tools
- **Outputs:** Financial models, quantitative analysis, trading algorithms

**11. Data Agent (DAA)**
- **Role:** Data processing and analysis specialist
- **Responsibilities:**
  - Handle large-scale data processing
  - Implement data pipelines and ETL
  - Perform data analysis and visualization
  - Optimize data storage and retrieval
- **Activation:** For data-intensive tasks
- **Tools:** Data processing frameworks, databases, visualization tools
- **Outputs:** Data pipelines, analysis reports, optimized data structures

**12. Security Agent (SA)**
- **Role:** Security analysis and implementation
- **Responsibilities:**
  - Perform security audits and reviews
  - Implement security measures
  - Analyze vulnerabilities and threats
  - Ensure compliance requirements
- **Activation:** For security-related tasks or periodic reviews
- **Tools:** Security scanning tools, audit frameworks, compliance checkers
- **Outputs:** Security assessments, vulnerability reports, security implementations

**13. UX Agent (UX)**
- **Role:** User experience design and interface optimization
- **Responsibilities:**
  - Design user interfaces and user flows
  - Create wireframes and prototypes
  - Conduct usability analysis
  - Implement accessibility standards
  - Optimize user interaction patterns
- **Activation:** For frontend/UI tasks or user experience requirements
- **Tools:** Design tools, accessibility checkers, user testing frameworks
- **Outputs:** UI designs, wireframes, usability reports, accessibility guidelines

### Agent Interaction Patterns

**Workflow Handoffs:**
1. PM → DA: Check for reusable components
2. DA → SR/JR: If no reusable solution found (complexity-based routing)
3. SR/JR → PM: Solution findings and recommendations
4. PM → HR: Request agent activation based on task type and complexity
5. HR → JC/SC/QA/DAA/SA: Activate appropriate implementation agent
6. PM → Active IA: Provide context and tools
7. Active IA → TA: Deliver solution for validation
8. TA → PM: Validation results and metrics

**Performance Feedback Loop:**
1. All Agents → HR: Performance metrics every 20 calls
2. HR → SR: Trigger improvement research on critical errors
3. SR → HR: Improvement recommendations
4. HR → HI: Present improvement proposals for human approval
5. HI → HR: Approval/rejection decisions

**Specialist Agent Activation:**
1. PM identifies task type (financial/data/security)
2. HR activates specialist (QA/DAA/SA) based on PM analysis
3. Specialist agent receives PM context and project-specific tools
4. TA validates specialist output with domain-specific criteria