# BMAD Integration Documentation

**Story 1.7 Implementation - BMAD Best Practices Integrated into LangGraph Agents**

This directory contains documentation for BMAD (Best Multiagent Development) patterns integrated into the MADF LangGraph multiagent system.

## Overview

BMAD is a CLI-based agent system with rich personas, inquiry protocols, and quality standards. Story 1.7 adapts BMAD's programmatic best practices for LangGraph StateGraph orchestration **without** adopting CLI-specific patterns.

### What We Adopted ✓

- **Persona Structure**: Rich agent identities (role, style, focus, core_principles)
- **Inquiry Protocols**: `clarify_task()` method asks questions before execution
- **Capabilities Registry**: Structured agent capabilities with inquiry patterns
- **Quality Standards**: TDD workflow (Developer), QA gates (Validator)
- **Story File Permissions**: Section-level edit controls
- **Requirements Traceability**: Given-When-Then test mapping

### What We Rejected ✗

- **Slash Commands**: LangGraph agents use programmatic APIs, not CLI commands
- **Activation Instructions**: Agents instantiated programmatically, not CLI steps
- **User-Facing Numbered Options**: Agents coordinate via StateGraph, not user menus
- **elicit=true Workflows**: LangGraph uses StateGraph interrupts instead

## Documentation Files

1. **[persona-system.md](persona-system.md)** - Agent persona structure and configuration
2. **[inquiry-patterns.md](inquiry-patterns.md)** - Clarification protocols and inquiry patterns
3. **[quality-standards.md](quality-standards.md)** - TDD workflow and QA governance
4. **[agent-capabilities.md](agent-capabilities.md)** - Capability definitions and tool assignments
5. **[langgraph-orchestration.md](langgraph-orchestration.md)** - LangGraph workflow with BMAD clarification interrupts

## Quick Start

### 1. Create Agent with BMAD Persona

```python
from src.agents.orchestrator_agent import OrchestratorAgent

# Agent loads persona, capabilities, and tools from YAML config
agent = OrchestratorAgent()

print(agent.persona.role)  # "Workflow Coordinator & Product Planning Specialist"
print(agent.capabilities)  # [create_prd, decompose_epic, ...]
print(agent._tools)  # ['github_client', 'tavily_client', ...]
```

### 2. Use Inquiry Protocol

```python
# Agent asks questions when context is incomplete
result = agent.clarify_task(
    task="create PRD for new feature",
    context={}  # Empty context triggers clarification
)

if not result["clear"]:
    print("Agent needs clarification:")
    for question in result["questions"]:
        print(f"  - {question}")
    # Questions:
    #   - What is the core user problem being solved?
    #   - What are must-have vs nice-to-have features?
    #   - Who are the target users?
```

### 3. Execute LangGraph Workflow with Clarifications

```python
from langgraph_core.workflow_enhanced import (
    create_bmad_enhanced_workflow,
    BMADWorkflowState
)

# Create workflow with clarification support
agent_functions = {
    "orchestrator": orchestrator_node,
    "analyst": analyst_node,
    "knowledge": knowledge_node,
    "developer": developer_node,
    "validator": validator_node
}

workflow = create_bmad_enhanced_workflow(agent_functions)

# Execute workflow
initial_state = BMADWorkflowState(
    workflow_id="project_x",
    current_agent="orchestrator"
)

result = await workflow.ainvoke(initial_state, config=config)

# Check if clarification needed
if result.get("status") == "clarifying":
    questions = result["clarification_request"].questions
    # Collect answers, then resume workflow
```

### 4. Enforce Story File Permissions

```python
from src.core.story_file_manager import StoryFileManager

manager = StoryFileManager()

# Validate edit permission
permission = manager.validate_edit(
    agent_id="developer",
    section_name="Dev Agent Record"
)

if permission.allowed:
    # Apply edit
    manager.apply_edit(
        agent_id="developer",
        file_path=story_file,
        section_name="Dev Agent Record",
        new_content="Implementation complete"
    )
```

### 5. Track Requirements Traceability

```python
from src.core.requirements_tracer import RequirementsTracer

tracer = RequirementsTracer()

# Parse story and tests
tracer.parse_acceptance_criteria(story_file)
tracer.parse_test_file(test_file)

# Generate traceability report
report = tracer.calculate_coverage()

print(f"Coverage: {report.coverage_percentage:.1f}%")
print(f"Missing tests: {report.missing_tests}")
```

## Architecture

### Agent Layer
- **BaseAgent** (enhanced): `clarify_task()`, persona, capabilities
- **5 Specialized Agents**: Orchestrator, Analyst, Knowledge, Developer, Validator
- **YAML Configs**: `config/agents/*.yaml` define persona, capabilities, tools

### Core Layer
- **agent_config.py**: Pydantic validation for YAML configs
- **context_keyword_extractor.py**: Domain-aware keyword extraction
- **story_file_manager.py**: Section-level permission enforcement
- **requirements_tracer.py**: Given-When-Then traceability

### Workflow Layer
- **workflow_enhanced.py**: LangGraph with clarification interrupts
- **BMADWorkflowState**: Extended state with clarification tracking
- **Clarification Protocol**: Agents pause workflow, collect context, resume

## Test Coverage

**69 passing tests** across 4 test files:

- **test_story_1_7_agent_yaml_integration.py** (16 tests): YAML config loading, inquiry protocols, tool sync
- **test_story_1_7_story_permissions.py** (18 tests): Story file permission enforcement
- **test_story_1_7_requirements_tracer.py** (15 tests): Given-When-Then traceability
- **test_story_1_7_langgraph_integration.py** (14 tests): LangGraph clarification interrupts
- **test_tool_assignment_sync.py** (6 tests): Tool assignment synchronization

## Files Created

### Configuration
- `config/agents/orchestrator_config.yaml`
- `config/agents/analyst_config.yaml`
- `config/agents/knowledge_config.yaml`
- `config/agents/developer_config.yaml`
- `config/agents/validator_config.yaml`

### Core Infrastructure
- `src/core/agent_config.py`
- `src/core/context_keyword_extractor.py`
- `src/core/story_file_manager.py`
- `src/core/requirements_tracer.py`

### Workflow
- `langgraph_core/workflow_enhanced.py`

### Tests
- `tests/test_story_1_7_agent_yaml_integration.py`
- `tests/test_story_1_7_story_permissions.py`
- `tests/test_story_1_7_requirements_tracer.py`
- `tests/test_story_1_7_langgraph_integration.py`
- `tests/test_tool_assignment_sync.py`

## Key Benefits

1. **Rich Agent Personalities**: Agents have clear roles, styles, and core principles
2. **Proactive Clarification**: Agents ask questions before premature execution
3. **Quality Governance**: TDD workflow, QA gates with traceability
4. **Permission Enforcement**: Developer/Validator can only edit authorized sections
5. **Requirements Coverage**: Track AC-to-test traceability automatically
6. **LangGraph Orchestration**: StateGraph coordination preserved throughout

## Next Steps

- Read [persona-system.md](persona-system.md) to understand agent identities
- Read [inquiry-patterns.md](inquiry-patterns.md) to implement clarification logic
- Read [quality-standards.md](quality-standards.md) for TDD and QA gate patterns
- Read [langgraph-orchestration.md](langgraph-orchestration.md) for workflow integration

## References

- **Story 1.7**: [docs/stories/epic-1/story-1-7-bmad-agent-integration.md](../stories/epic-1/story-1-7-bmad-agent-integration.md)
- **Architecture**: [docs/architecture/2-high-level-architecture.md](../architecture/2-high-level-architecture.md)
- **Tech Stack**: [docs/architecture/3-tech-stack.md](../architecture/3-tech-stack.md)
