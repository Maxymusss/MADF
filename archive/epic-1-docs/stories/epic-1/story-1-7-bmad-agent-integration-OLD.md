# Story 1.7: BMAD Agent Best Practices Integration

As a **multiagent system developer**,
I want **LangGraph agents to adopt proven best practices from BMAD agent implementations**,
so that **the multiagent framework benefits from battle-tested patterns, workflows, and quality standards**.

## Acceptance Criteria

1. **Agent Persona Patterns**: Implement BMAD persona structure (role, style, identity, focus, core principles) in LangGraph agents
2. **Command Structure**: Adopt BMAD command-driven interaction patterns with numbered options
3. **Task Workflow Integration**: Implement BMAD task execution patterns (activation instructions, dependencies, checklists)
4. **Quality Standards**: Integrate BMAD quality practices (TDD-first, story file permissions, gate governance)
5. **Documentation Patterns**: Adopt BMAD self-contained configuration approach (YAML-based agent definitions)
6. **Interactive Protocols**: Implement BMAD elicitation and user interaction patterns

## Tasks / Subtasks

- [ ] Task 1: Extract BMAD Agent Best Practices (AC: 1-6)
  - [ ] Analyze Dev Agent (James) TDD-first workflow and story file permissions
  - [ ] Analyze QA Agent (Quinn) gate governance and requirements traceability
  - [ ] Analyze Analyst Agent (Mary) elicitation and numbered options protocol
  - [ ] Analyze Architect Agent (Winston) holistic system thinking and cross-stack patterns
  - [ ] Analyze PM Agent (John) task workflow management and template systems
  - [ ] Document extractable patterns per agent role
  - [ ] Create mapping: BMAD Agent → LangGraph Agent equivalents

- [ ] Task 2: Implement Agent Persona Enhancement (AC: 1)
  - [ ] Extend LangGraph agent base class with persona structure
  - [ ] Add role, style, identity, focus, core_principles fields
  - [ ] Implement persona-driven prompt engineering
  - [ ] Update all 5 agents (Orchestrator, Analyst, Knowledge, Developer, Validator)
  - [ ] Write tests for persona consistency

- [ ] Task 3: Integrate Command-Driven Interaction Pattern (AC: 2)
  - [ ] Implement command registry system for agents
  - [ ] Add numbered options presentation protocol
  - [ ] Build command execution workflow
  - [ ] Implement *help command for all agents
  - [ ] Add command validation and error handling
  - [ ] Write tests for command system

- [ ] Task 4: Adopt Task Workflow Management (AC: 3)
  - [ ] Implement activation instruction protocol
  - [ ] Add dependency management system (tasks, templates, checklists)
  - [ ] Build task execution engine
  - [ ] Implement file resolution patterns (.bmad-core → agent tasks)
  - [ ] Add elicit=true workflow support
  - [ ] Write tests for task workflows

- [ ] Task 5: Integrate Quality Standards (AC: 4)
  - [ ] Implement TDD-first enforcement in Developer Agent
  - [ ] Add story file permission system (section-level editing control)
  - [ ] Build QA gate governance workflow
  - [ ] Implement requirements traceability (Given-When-Then mapping)
  - [ ] Add test report generation to tests/reports/
  - [ ] Write tests for quality gates

- [ ] Task 6: Create YAML-Based Agent Configuration System (AC: 5)
  - [ ] Design unified agent configuration schema
  - [ ] Implement YAML config loader for agents
  - [ ] Migrate agent definitions to YAML format
  - [ ] Add hot-reload capability for agent configs
  - [ ] Implement config validation
  - [ ] Write tests for config system

- [ ] Task 7: End-to-End BMAD Pattern Validation (AC: 1-6)
  - [ ] Test complete workflow with enhanced agents
  - [ ] Validate TDD-first enforcement
  - [ ] Test QA gate governance
  - [ ] Validate command-driven interactions
  - [ ] Test persona consistency across agents
  - [ ] Document usage patterns and examples

## Dev Notes

### BMAD Agent Mapping to LangGraph Agents

**Dev Agent (James)** → **Developer Agent**:
- TDD-first workflow (write tests BEFORE implementation)
- Story file permissions (only Dev Agent Record sections)
- develop-story-tdd command with RED→GREEN→REFACTOR cycle
- Test report generation to tests/reports/
- Blocking conditions (3 failures, missing config)
- Core principle: Story has ALL info needed

**QA Agent (Quinn)** → **Validator Agent**:
- Gate governance (PASS/CONCERNS/FAIL/WAIVED decisions)
- Requirements traceability (Given-When-Then mapping)
- Risk-based testing (probability × impact)
- Quality attribute validation (NFRs)
- Advisory authority without blocking
- Story file permissions (only QA Results section)

**Analyst Agent (Mary)** → **Analyst Agent** (existing):
- Numbered options protocol for selections
- Elicitation patterns (advanced-elicitation task)
- Research planning workflows
- Facilitation techniques
- Strategic contextualization
- Curiosity-driven inquiry

**Architect Agent (Winston)** → **Knowledge Agent**:
- Holistic system thinking
- Cross-stack optimization
- Living architecture (design for change)
- Data-centric design
- Progressive complexity patterns
- Developer experience focus

**PM Agent (John)** → **Orchestrator Agent**:
- Task workflow management
- Template-driven document creation
- Elicitation with exact format
- Ruthless prioritization
- Data-informed decisions
- Collaborative iteration

### Key BMAD Patterns to Adopt

#### 1. Activation Instructions Protocol
```yaml
activation-instructions:
  - STEP 1: Read THIS ENTIRE FILE
  - STEP 2: Adopt persona
  - STEP 3: Load core-config.yaml
  - STEP 4: Greet + auto-run *help
  - STAY IN CHARACTER!
```

#### 2. Persona Structure
```yaml
persona:
  role: Expert description
  style: Behavioral attributes
  identity: Self-concept
  focus: Primary objectives
  core_principles:
    - Principle 1
    - Principle 2
```

#### 3. Command-Driven Interaction
```yaml
commands:
  - help: Show numbered list
  - command-name: Description with task mapping
  - exit: Abandon persona
```

#### 4. Dependency Management
```yaml
dependencies:
  checklists:
    - checklist-name.md
  tasks:
    - task-name.md
  templates:
    - template-name.yaml
```

#### 5. Story File Permissions
```yaml
story-file-permissions:
  - CRITICAL: ONLY authorized sections
  - CRITICAL: DO NOT modify other sections
  - List specific allowed sections
```

### Previous Story Insights (Story 1.1)
- MCP bridge architecture established in `src/core/mcp_bridge.py` [Source: Story 1.1 Completion Notes]
- All 5 agents operational within LangGraph StateGraph [Source: Story 1.1 Completion Notes]
- Agent base classes follow pattern in `src/agents/base_agent.py` [Source: Story 1.1 File List]
- Testing strategy: TDD with comprehensive test coverage [Source: Story 1.1 Approach]

### Technology Stack
- **Python**: 3.11+ [Source: architecture/3-tech-stack.md#Technology Stack Table]
- **LangGraph**: StateGraph orchestration [Source: Story 1.1 File List]
- **PyYAML**: 6.x for agent configuration loading
- **Pydantic**: 2.x for config validation [Source: architecture/3-tech-stack.md#Additional Stack Components]
- **Testing**: pytest 7.x [Source: architecture/3-tech-stack.md#Technology Stack Table]

### File Locations

**Core Implementation**:
- **Base Agent**: `src/agents/base_agent.py` (existing, enhance with BMAD patterns) [Source: Story 1.1 File List]
- **All 5 Agents**: `src/agents/{agent}_agent.py` (existing, add persona/commands) [Source: Story 1.1 File List]
- **Agent Graph**: `src/core/agent_graph.py` (existing, integrate command system) [Source: Story 1.1 File List]
- **State Models**: `src/core/state_models.py` (existing, extend if needed) [Source: Story 1.1 File List]

**New BMAD Integration**:
- **Persona System**: `src/core/persona_system.py` (new) - Persona structure and prompt engineering
- **Command Registry**: `src/core/command_registry.py` (new) - Command-driven interaction
- **Task Workflow**: `src/core/task_workflow.py` (new) - BMAD task execution engine
- **Config Loader**: `src/core/config_loader.py` (new) - YAML agent configuration
- **Quality Gates**: `src/core/quality_gates.py` (new) - QA gate governance
- **Story Permissions**: `src/core/story_permissions.py` (new) - Section-level editing control

**Agent Configurations**:
- **Agent Configs**: `config/agents/{agent}_config.yaml` (new) - YAML-based agent definitions

**Tests**:
- **Tests**: `tests/test_story_1_7_bmad_integration.py` (new) [Source: architecture/14-testing-strategy.md#Test Organization]
- **Tests**: `tests/test_story_1_7_persona_system.py` (new) - Test persona consistency
- **Tests**: `tests/test_story_1_7_command_registry.py` (new) - Test command system
- **Tests**: `tests/test_story_1_7_quality_gates.py` (new) - Test QA governance

### Environment Variables Required
None - BMAD patterns are code-level improvements

### BMAD Best Practices by Category

#### **Developer Excellence (from Dev Agent James)**:
- TDD-FIRST: Write tests before implementation (RED→GREEN→REFACTOR)
- Minimal context overhead: Story contains ALL needed information
- Story file discipline: Only update authorized sections
- Test report generation: Save to tests/reports/
- Blocking awareness: 3 failures = HALT and ask for help
- Numbered options for choices

#### **Quality Governance (from QA Agent Quinn)**:
- Gate decisions: PASS/CONCERNS/FAIL/WAIVED with rationale
- Requirements traceability: Map stories to tests (Given-When-Then)
- Risk-based prioritization: probability × impact
- Advisory authority: Educate without blocking
- Testability assessment: controllability, observability, debuggability
- Story file discipline: Only update QA Results section

#### **Strategic Analysis (from Analyst Agent Mary)**:
- Numbered options protocol for all selections
- Advanced elicitation techniques
- Curiosity-driven inquiry ("why" questions)
- Objective & evidence-based analysis
- Action-oriented outputs
- Collaborative partnership iteration

#### **Architectural Thinking (from Architect Agent Winston)**:
- Holistic system thinking: Every component in context
- User experience drives architecture
- Pragmatic technology selection
- Progressive complexity (simple start, scale later)
- Developer experience as first-class concern
- Living architecture for change

#### **Product Management (from PM Agent John)**:
- Task workflow management
- Template-driven efficiency
- Elicitation with exact format (elicit=true)
- Ruthless prioritization & MVP focus
- Data-informed decisions
- Proactive risk identification

### Testing

#### Testing Strategy
- **TDD Approach**: BMAD patterns enforce TDD-first [Source: Dev Agent]
- **Test Coverage**: 70% unit test coverage target [Source: architecture/14-testing-strategy.md#Testing Pyramid]
- **Test Types**: Unit (70%), Integration (25%), E2E (5%) [Source: architecture/14-testing-strategy.md#Testing Pyramid]

#### Test File Location
- `tests/test_story_1_7_bmad_integration.py` [Source: architecture/14-testing-strategy.md#Python Tests]

#### Test Requirements
- Test persona system integration across all 5 agents
- Test command registry with numbered options
- Test task workflow execution engine
- Test YAML config loading and validation
- Test quality gate governance workflow
- Test story file permissions enforcement
- Test TDD-first enforcement in Developer Agent
- Test requirements traceability mapping
- Validate agent behavior consistency with personas

#### Testing Frameworks
- pytest 7.x [Source: architecture/3-tech-stack.md#Technology Stack Table]
- PyYAML for config validation
- Pydantic validation testing [Source: architecture/15-coding-standards.md#Critical Fullstack Rules]

### Coding Standards
- **Type Safety**: All messages use Pydantic models for validation [Source: architecture/15-coding-standards.md#Critical Fullstack Rules]
- **Error Handling**: All agents implement try-catch with error logging [Source: architecture/15-coding-standards.md#Critical Fullstack Rules]
- **Python Classes**: PascalCase (e.g., PersonaSystem) [Source: architecture/15-coding-standards.md#Naming Conventions]
- **Python Functions**: snake_case (e.g., load_agent_config) [Source: architecture/15-coding-standards.md#Naming Conventions]
- **Python Files**: snake_case (e.g., persona_system.py) [Source: architecture/15-coding-standards.md#Naming Conventions]

### Technical Constraints
- Python 3.11+ required [Source: architecture/3-tech-stack.md#Technology Stack Table]
- All Stories 1.1-1.6 must be complete before implementing Story 1.7
- BMAD patterns must not break existing agent functionality
- Backward compatibility with Stories 1.1-1.6 required

## Status

🟢 **APPROVED** - Ready for developer implementation (prerequisites Stories 1.1-1.6 complete)

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-09-30 | 1.0 | Story created with BMAD best practices extraction | PM Agent (John) |
| 2025-10-01 | 1.1 | Story approved - prerequisite Stories 1.1-1.6 complete | PM Agent (John) |

## Dev Agent Record

_This section will be populated during implementation by the development agent._

### Agent Model Used

_To be recorded during implementation_

### Debug Log References

_To be recorded during implementation_

### Completion Notes

_To be recorded during implementation_

### File List

_To be recorded during implementation_

## QA Results

_To be populated by QA Agent after story completion_