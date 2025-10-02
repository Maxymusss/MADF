# Agent Capabilities Matrix

**BMAD Pattern**: Structured capability definitions with inquiry patterns and tool assignments

## Overview

Agent capabilities define what each agent can do, how they ask clarifying questions, and which tools they use. Capabilities are defined in YAML configs and loaded at agent initialization with Pydantic validation.

## Capability Structure

### YAML Format

```yaml
capabilities:
  - name: "create_prd"
    description: "Generate Product Requirements Document"
    inquiry_patterns:
      - "What is the core user problem being solved?"
      - "What are must-have vs nice-to-have features?"
      - "Who are the target users?"
      - "What are the success metrics?"
    tools:
      - "obsidian_client"
      - "tavily_client"
    workflow:
      - "Elicit user problem and goals"
      - "Research existing solutions"
      - "Define acceptance criteria"
      - "Generate PRD document"
```

### Python Model

```python
from src.core.agent_config import AgentCapability

class AgentCapability(BaseModel):
    name: str  # Capability identifier
    description: str  # What the capability does
    inquiry_patterns: List[str]  # Questions to ask for clarification
    tools: List[str]  # Tool IDs required
    workflow: Optional[List[str]]  # Execution steps (optional)
```

## Agent Capabilities by Role

### Orchestrator (PM Agent)

**Primary Responsibilities**: PRD creation, epic/story decomposition, task planning

```yaml
# config/agents/orchestrator_config.yaml
capabilities:
  - name: "create_prd"
    description: "Generate Product Requirements Document"
    inquiry_patterns:
      - "What is the core user problem being solved?"
      - "What are must-have vs nice-to-have features?"
      - "Who are the target users?"
      - "What are the success metrics?"
    tools:
      - "obsidian_client"
      - "tavily_client"
    workflow:
      - "Elicit user problem and goals"
      - "Research existing solutions"
      - "Define acceptance criteria"
      - "Generate PRD document"

  - name: "decompose_epic"
    description: "Break epic into implementable user stories"
    inquiry_patterns:
      - "What is the epic scope and boundaries?"
      - "Are there dependencies between stories?"
      - "What is the MVP vs nice-to-have split?"
    tools:
      - "obsidian_client"
    workflow:
      - "Analyze epic scope"
      - "Identify story boundaries"
      - "Define acceptance criteria per story"
      - "Sequence stories by dependencies"

  - name: "create_story"
    description: "Create detailed user story with tasks"
    inquiry_patterns:
      - "What acceptance criteria define 'done'?"
      - "Are there technical constraints?"
      - "What is the estimated complexity?"
    tools:
      - "obsidian_client"
    workflow:
      - "Define story title and description"
      - "Write acceptance criteria"
      - "Break down into tasks"
      - "Generate story file"

  - name: "prioritize_backlog"
    description: "Prioritize stories by business value and risk"
    inquiry_patterns:
      - "What is the business priority?"
      - "What are technical dependencies?"
      - "What is the user impact?"
    tools:
      - "obsidian_client"
```

### Analyst (Research Agent)

**Primary Responsibilities**: Requirements elicitation, analysis, brainstorming

```yaml
# config/agents/analyst_config.yaml
capabilities:
  - name: "analyze_codebase"
    description: "Analyze codebase for patterns and opportunities"
    inquiry_patterns:
      - "What scope to analyze? (file/module/system)"
      - "What depth level? (surface/detailed/comprehensive)"
      - "What specific aspects? (architecture/performance/security)"
    tools:
      - "context7_client"
      - "filesystem_client"
      - "sequential_thinking_client"
    workflow:
      - "Identify analysis scope"
      - "Collect code artifacts"
      - "Apply analysis framework"
      - "Generate insights report"

  - name: "elicit_requirements"
    description: "Extract requirements through strategic questioning"
    inquiry_patterns:
      - "What is the user's current workflow?"
      - "What pain points exist in current process?"
      - "What would success look like?"
      - "What constraints must be respected?"
    tools:
      - "sequential_thinking_client"
      - "tavily_client"
    workflow:
      - "Ask open-ended 'why' questions"
      - "Probe for root causes"
      - "Identify implicit requirements"
      - "Document findings"

  - name: "brainstorm_solutions"
    description: "Generate solution alternatives with pros/cons"
    inquiry_patterns:
      - "What constraints apply?"
      - "What existing solutions exist?"
      - "What is the risk tolerance?"
    tools:
      - "sequential_thinking_client"
      - "tavily_client"
    workflow:
      - "Research existing solutions"
      - "Generate 3+ alternatives"
      - "Assess pros/cons for each"
      - "Recommend solution with rationale"

  - name: "facilitate_discussion"
    description: "Guide team discussions with structured facilitation"
    inquiry_patterns:
      - "What is the decision to be made?"
      - "Who are the stakeholders?"
      - "What is the time constraint?"
    tools:
      - "sequential_thinking_client"
```

### Knowledge (Architecture Agent)

**Primary Responsibilities**: Architecture design, knowledge persistence, system optimization

```yaml
# config/agents/knowledge_config.yaml
capabilities:
  - name: "design_architecture"
    description: "Create system architecture with cross-stack optimization"
    inquiry_patterns:
      - "What are the non-functional requirements?"
      - "What is the expected scale (users/data/throughput)?"
      - "What existing systems must integrate?"
      - "What are the technology constraints?"
    tools:
      - "graphiti_client"
      - "obsidian_client"
      - "sequential_thinking_client"
    workflow:
      - "Analyze requirements and constraints"
      - "Design high-level architecture"
      - "Define component interfaces"
      - "Document architecture decisions"

  - name: "persist_knowledge"
    description: "Store design decisions and context in knowledge graph"
    inquiry_patterns:
      - "What entities and relationships exist?"
      - "What context is important for future reference?"
      - "How should this knowledge be indexed?"
    tools:
      - "graphiti_client"
      - "obsidian_client"
    workflow:
      - "Extract entities and relationships"
      - "Store in knowledge graph"
      - "Create cross-references"
      - "Generate retrieval metadata"

  - name: "optimize_system"
    description: "Optimize system for performance, security, and maintainability"
    inquiry_patterns:
      - "What performance bottlenecks exist?"
      - "What security risks are present?"
      - "What technical debt needs addressing?"
    tools:
      - "graphiti_client"
      - "context7_client"
      - "sequential_thinking_client"
    workflow:
      - "Identify optimization opportunities"
      - "Assess impact and effort"
      - "Recommend improvements"
      - "Document optimization strategy"

  - name: "generate_adr"
    description: "Create Architecture Decision Record"
    inquiry_patterns:
      - "What decision needs documentation?"
      - "What alternatives were considered?"
      - "What are the consequences?"
    tools:
      - "obsidian_client"
```

### Developer (Implementation Agent)

**Primary Responsibilities**: TDD implementation, code generation, story execution

```yaml
# config/agents/developer_config.yaml
capabilities:
  - name: "implement_story"
    description: "Implement story with TDD workflow (RED→GREEN→REFACTOR)"
    inquiry_patterns:
      - "What are the acceptance criteria?"
      - "What existing code needs modification?"
      - "What edge cases must be handled?"
    tools:
      - "filesystem_client"
      - "github_client"
    workflow:
      - "Write failing test (RED)"
      - "Write minimal code to pass (GREEN)"
      - "Refactor for quality"
      - "Run full test suite"

  - name: "write_tests"
    description: "Write comprehensive test suite (unit, integration, e2e)"
    inquiry_patterns:
      - "What is the test scope?"
      - "What test level? (unit/integration/e2e)"
      - "What edge cases exist?"
    tools:
      - "filesystem_client"
    workflow:
      - "Identify test scenarios"
      - "Write Given-When-Then tests"
      - "Implement test logic"
      - "Verify coverage"

  - name: "refactor_code"
    description: "Improve code quality without changing behavior"
    inquiry_patterns:
      - "What quality issues exist?"
      - "What is the refactoring scope?"
      - "What tests exist to protect against regressions?"
    tools:
      - "filesystem_client"
    workflow:
      - "Identify refactoring opportunities"
      - "Ensure tests exist"
      - "Apply refactoring"
      - "Verify tests still pass"

  - name: "fix_bug"
    description: "Debug and fix code issues"
    inquiry_patterns:
      - "What is the bug reproduction scenario?"
      - "What is the expected vs actual behavior?"
      - "What is the root cause?"
    tools:
      - "filesystem_client"
      - "context7_client"
    workflow:
      - "Reproduce bug"
      - "Write failing test"
      - "Identify root cause"
      - "Fix bug"
      - "Verify fix"
```

### Validator (QA Agent)

**Primary Responsibilities**: QA gate governance, validation, quality assessment

```yaml
# config/agents/validator_config.yaml
capabilities:
  - name: "review_story"
    description: "Comprehensive story review with gate decision"
    inquiry_patterns:
      - "What acceptance criteria must be met?"
      - "What quality standards apply?"
      - "What risk level is this story?"
    tools:
      - "filesystem_client"
      - "obsidian_client"
    workflow:
      - "Perform risk assessment"
      - "Verify acceptance criteria"
      - "Check test coverage"
      - "Assess code quality"
      - "Validate NFRs"
      - "Make gate decision"

  - name: "validate_requirements"
    description: "Verify requirements traceability and coverage"
    inquiry_patterns:
      - "What are the acceptance criteria?"
      - "What tests exist?"
      - "What coverage gaps exist?"
    tools:
      - "filesystem_client"
    workflow:
      - "Parse acceptance criteria"
      - "Map tests to ACs"
      - "Calculate coverage"
      - "Generate traceability report"

  - name: "assess_quality"
    description: "Evaluate code quality and make improvement recommendations"
    inquiry_patterns:
      - "What quality metrics matter?"
      - "What are the quality thresholds?"
      - "What is the risk tolerance?"
    tools:
      - "filesystem_client"
      - "context7_client"
    workflow:
      - "Analyze code structure"
      - "Check coding standards"
      - "Verify test coverage"
      - "Assess security posture"
      - "Generate quality score"

  - name: "make_gate_decision"
    description: "Apply deterministic gate criteria (PASS/CONCERNS/FAIL/WAIVED)"
    inquiry_patterns:
      - "What issues were found?"
      - "What is the issue severity?"
      - "Are waivers being requested?"
    tools:
      - "obsidian_client"
    workflow:
      - "Collect evidence"
      - "Assess risks and NFRs"
      - "Apply gate rules"
      - "Calculate quality score"
      - "Generate gate file"
```

## Tool Assignment Matrix

| Tool | Orchestrator | Analyst | Knowledge | Developer | Validator |
|------|--------------|---------|-----------|-----------|-----------|
| **github_client** | ✓ | - | - | ✓ | - |
| **tavily_client** | ✓ | ✓ | - | - | - |
| **context7_client** | - | ✓ | ✓ | ✓ | ✓ |
| **sequential_thinking_client** | - | ✓ | ✓ | - | - |
| **graphiti_client** | - | - | ✓ | - | - |
| **obsidian_client** | ✓ | - | ✓ | - | ✓ |
| **filesystem_client** | - | ✓ | - | ✓ | ✓ |

### Tool Integration Pattern

```python
from src.agents.orchestrator_agent import OrchestratorAgent

# Agent loads tools at initialization based on config
agent = OrchestratorAgent()

# Tools accessible via agent._tools dictionary
agent._tools["github_client"].create_issue(...)
agent._tools["tavily_client"].search(...)
agent._tools["obsidian_client"].create_note(...)

# Tools are initialized with proper authentication
assert agent._tools["github_client"].authenticated is True
```

## Capability Discovery

### Runtime Capability Query

```python
# List agent capabilities
agent = AnalystAgent()

capabilities = agent.get_capabilities()
# Returns:
# [
#   {
#     "name": "analyze_codebase",
#     "description": "Analyze codebase for patterns and opportunities",
#     "inquiry_patterns": [...]
#   },
#   {
#     "name": "elicit_requirements",
#     "description": "Extract requirements through strategic questioning",
#     "inquiry_patterns": [...]
#   },
#   ...
# ]

# Check if capability exists
has_analyze = agent.has_capability("analyze_codebase")  # True
has_deploy = agent.has_capability("deploy_code")  # False
```

### Capability Matching

```python
# Match task to capability
agent = OrchestratorAgent()

capability = agent._match_capability("create PRD for new feature")
# Returns: "create_prd"

capability = agent._match_capability("break epic into stories")
# Returns: "decompose_epic"

capability = agent._match_capability("invalid task")
# Returns: None
```

## Adding New Capabilities

### 1. Define Capability in YAML

```yaml
# config/agents/my_agent_config.yaml
capabilities:
  - name: "new_capability"
    description: "Description of what it does"
    inquiry_patterns:
      - "Question 1?"
      - "Question 2?"
    tools:
      - "tool_client_1"
      - "tool_client_2"
    workflow:
      - "Step 1"
      - "Step 2"
```

### 2. Implement Capability Method

```python
class MyAgent(BaseAgent):
    def new_capability(self, task: str, context: Dict[str, Any]) -> Result:
        # Clarification phase
        clarification = self.clarify_task(task, context)
        if not clarification["clear"]:
            return {"status": "needs_clarification", "questions": clarification["questions"]}

        # Execution phase
        tool1 = self._tools["tool_client_1"]
        tool2 = self._tools["tool_client_2"]

        # Implement workflow
        result = self._execute_workflow(tool1, tool2, context)

        return {"status": "complete", "result": result}
```

### 3. Write Tests

```python
def test_new_capability():
    """
    Given: Agent with new_capability
    When: Capability invoked with valid context
    Then: Returns expected result
    """
    agent = MyAgent()

    result = agent.new_capability(
        task="test task",
        context={"param": "value"}
    )

    assert result["status"] == "complete"
```

## Capability Validation

Pydantic validates capability structure at initialization:

```python
from src.core.agent_config import AgentConfig

# Valid config loads successfully
config = AgentConfig.from_yaml("config/agents/orchestrator_config.yaml")

# Invalid config raises ValidationError
config = AgentConfig.from_yaml("config/agents/invalid_config.yaml")
# ValidationError: inquiry_patterns must be list of strings
```

## References

- **Agent Config Loader**: [src/core/agent_config.py](../../src/core/agent_config.py)
- **BaseAgent**: [src/agents/base_agent.py](../../src/agents/base_agent.py)
- **Tool Selection Guide**: [.claude/tools/tool-selection-guide.md](../../.claude/tools/tool-selection-guide.md)
- **Story 1.7**: [story-1-7-bmad-agent-integration.md](../stories/epic-1/story-1-7-bmad-agent-integration.md)
