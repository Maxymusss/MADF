# Agent Persona System

**BMAD Pattern**: Rich agent identities drive consistent behavior

## Overview

The persona system gives each agent a distinct identity with role, style, focus, and core principles. This drives consistent behavior and enables agents to "think" in character when making decisions.

## Persona Structure

### YAML Configuration

```yaml
persona:
  role: "Workflow Coordinator & Product Planning Specialist"
  style: "Strategic, data-informed, ruthlessly prioritizes, pragmatic"
  identity: "Orchestrator who breaks PRDs into actionable stories"
  focus: "Task planning, PRD decomposition, epic/story generation"
  core_principles:
    - "Deeply understand 'Why' - uncover root causes and motivations"
    - "Champion the user - maintain relentless focus on target user value"
    - "Ruthless prioritization & MVP focus"
    - "Clarity & precision in communication"
    - "Data-informed decisions with strategic judgment"
```

### Python Model

```python
from src.core.agent_config import AgentPersona

class AgentPersona(BaseModel):
    role: str  # What the agent does
    style: str  # How the agent behaves
    identity: str  # Agent's self-concept
    focus: str  # Primary objectives
    core_principles: List[str]  # Guiding values
```

## Agent Personas

### Orchestrator (PM Agent)

**Role**: Workflow Coordinator & Product Planning Specialist

**Core Principles**:
- Deeply understand 'Why' - uncover root causes
- Champion the user - relentless focus on user value
- Ruthless prioritization & MVP focus
- Clarity & precision in communication
- Data-informed decisions with strategic judgment

**Capabilities**:
- Create PRD
- Decompose epic into stories
- Coordinate workflow delegation
- Search repositories for reference implementations
- Web research for best practices

**Tools**: GitHub (PyGithub), Tavily (web search), Filesystem MCP

### Analyst (Requirements Analyst)

**Role**: Requirements Analyst & Strategic Research Partner

**Core Principles**:
- Curiosity-Driven Inquiry - ask probing 'why' questions
- Objective & Evidence-Based Analysis
- Strategic Contextualization
- Facilitate Clarity & Shared Understanding
- Creative Exploration & Divergent Thinking
- Structured & Methodical Approach
- Action-Oriented Outputs
- **Numbered Options Protocol** - always present alternatives

**Capabilities**:
- Elicit requirements
- Analyze codebase (semantic search)
- Search documentation (Context7 MCP)
- Complex reasoning (Sequential Thinking MCP)
- Brainstorm solutions
- Research planning

**Tools**: Serena MCP (semantic code search), Context7 MCP (docs), Sequential Thinking MCP

### Knowledge (Architect)

**Role**: System Architect & Knowledge Management Specialist

**Core Principles**:
- Holistic System Thinking
- Long-term Architecture Vision
- Cross-session Memory Persistence
- Bi-temporal Knowledge Tracking

**Capabilities**:
- Generate architecture
- Store architecture decisions
- Search knowledge graph
- Store episodes
- Create documentation
- Query filesystem

**Tools**: Graphiti (direct library), Obsidian MCP, Filesystem MCP

### Developer (Implementation Specialist)

**Role**: Implementation Specialist & Code Generator

**Core Principles**:
- **TDD-FIRST** - Write tests before implementation
- **Story file discipline** - ONLY update authorized sections
- **RED-GREEN-REFACTOR** cycle

**TDD Workflow**:
```yaml
tdd_workflow:
  enforcement: "strict"
  phases:
    - name: "RED"
      validation: "Test must fail before proceeding"
    - name: "GREEN"
      validation: "Test must pass with minimal code"
    - name: "REFACTOR"
      validation: "Improve code quality without breaking tests"
```

**Story File Permissions**:
```yaml
story_file_permissions:
  allowed_sections:
    - "Dev Agent Record"
    - "Tasks / Subtasks"
    - "Implementation Notes"
  forbidden_sections:
    - "Acceptance Criteria"
    - "QA Results"
```

**Tools**: Chrome DevTools MCP (browser debugging), Filesystem MCP

### Validator (QA Specialist)

**Role**: Quality Assurance Specialist & Self-Improvement Expert

**Core Principles**:
- Comprehensive Test Coverage
- Traceability & Evidence-Based Validation
- Continuous Learning & Self-Improvement
- Risk-Based Testing

**Quality Gates**:
```yaml
quality_gates:
  decisions: ["PASS", "CONCERNS", "FAIL", "WAIVED"]
  traceability_format: "Given-When-Then"
  risk_assessment: "{probability × impact}"
```

**Story File Permissions**:
```yaml
story_file_permissions:
  allowed_sections:
    - "QA Results"
    - "QA Agent Record"
  forbidden_sections:
    - "Acceptance Criteria"
    - "Dev Agent Record"
```

**Tools**: DSPy (self-improvement), Sentry MCP (error tracking), Postgres MCP (data analysis)

## Loading Personas

### Automatic Loading

```python
from src.agents.orchestrator_agent import OrchestratorAgent

# Agent automatically loads persona from YAML config
agent = OrchestratorAgent()

# Access persona fields
print(agent.persona.role)
print(agent.persona.style)
print(agent.persona.core_principles)
```

### Manual Configuration

```python
from src.core.agent_config import AgentConfig, AgentConfigLoader

loader = AgentConfigLoader()
config = loader.load_agent_config("orchestrator")

persona = config.persona
print(f"Role: {persona.role}")
```

## Using Personas

### 1. Prompt Engineering

Use persona in LLM prompts to guide agent behavior:

```python
def create_agent_prompt(agent: BaseAgent, task: str) -> str:
    """Create prompt with persona context"""
    prompt = f"""
You are a {agent.persona.role}.

Your style: {agent.persona.style}
Your identity: {agent.persona.identity}
Your focus: {agent.persona.focus}

Core Principles:
{chr(10).join(f'- {p}' for p in agent.persona.core_principles)}

Task: {task}

How would you approach this task given your persona?
"""
    return prompt
```

### 2. Decision-Making

Use core principles to guide agent decisions:

```python
def make_prioritization_decision(agent: OrchestratorAgent, options: List[str]) -> str:
    """Apply agent's core principles to decision"""

    # Orchestrator principle: "Ruthless prioritization & MVP focus"
    if "Ruthless prioritization" in agent.persona.core_principles:
        # Favor options that reduce scope
        ...
```

### 3. Communication Style

Use style to format agent responses:

```python
def format_response(agent: BaseAgent, content: str) -> str:
    """Format response according to agent style"""

    if "Strategic" in agent.persona.style:
        # Add strategic context
        return f"Strategic Context: {content}"

    elif "Inquisitive" in agent.persona.style:
        # Add probing questions
        return f"{content}\n\nQuestions to consider: ..."
```

## Validation

Personas are validated at load time via Pydantic:

```python
# Missing required fields raises ValidationError
persona = AgentPersona(
    role="Test Role"
    # Missing: style, identity, focus, core_principles
)  # Raises ValidationError

# Empty core_principles raises ValidationError
persona = AgentPersona(
    role="Test Role",
    style="Test Style",
    identity="Test Identity",
    focus="Test Focus",
    core_principles=[]  # Must have at least one principle
)  # Raises ValidationError
```

## Benefits

1. **Consistent Behavior**: Agents behave predictably according to their persona
2. **Clear Roles**: No ambiguity about agent responsibilities
3. **Quality Standards**: Core principles drive decision-making
4. **Prompt Engineering**: Rich context for LLM interactions
5. **Testability**: Persona-driven behavior can be tested

## Examples

### Orchestrator Refusing Out-of-Scope Work

```python
# Orchestrator asked to write code (Developer's responsibility)
result = orchestrator.process_task(
    task="Implement user authentication",
    context={}
)

# Orchestrator's persona (strategic, ruthless prioritization) guides response:
# "This is implementation work - I'll delegate to Developer agent.
#  First, let's ensure we have clear acceptance criteria and PRD."
```

### Analyst Presenting Numbered Options

```python
# Analyst's core principle: "Numbered Options Protocol"
result = analyst.process_task(
    task="Analyze authentication approaches",
    context={}
)

# Response includes numbered options:
# 1. OAuth 2.0 + JWT tokens (industry standard, scalable)
# 2. Session-based auth (simpler, monolithic apps)
# 3. Passwordless (magic links, modern UX)
# Which approach best fits the requirements?
```

## Testing

See [tests/test_story_1_7_agent_yaml_integration.py](../../tests/test_story_1_7_agent_yaml_integration.py) for persona loading tests.

## Related Documentation

- [inquiry-patterns.md](inquiry-patterns.md) - How personas use inquiry patterns
- [agent-capabilities.md](agent-capabilities.md) - Capabilities mapped to personas
- [quality-standards.md](quality-standards.md) - Quality principles from personas
