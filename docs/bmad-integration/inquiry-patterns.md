# Inquiry Patterns & Clarification Protocols

**BMAD Pattern**: Ask questions before execution to prevent premature action

## Overview

Inquiry patterns are structured questions that agents ask when context is incomplete. This prevents agents from making assumptions and ensures all necessary information is gathered before execution.

## How It Works

### 1. Agent Receives Task

```python
agent.clarify_task(
    task="create PRD for new feature",
    context={}  # Empty or incomplete context
)
```

### 2. Agent Matches Capability

Agent identifies which capability the task requires (e.g., "create_prd"):

```yaml
capabilities:
  - name: "create_prd"
    description: "Generate Product Requirements Document"
    inquiry_patterns:
      - "What is the core user problem being solved?"
      - "What are must-have vs nice-to-have features?"
      - "Who are the target users?"
      - "What are the success metrics?"
```

### 3. Agent Checks Context

For each inquiry pattern, agent checks if context provides an answer:

```python
for pattern in capability.inquiry_patterns:
    if not self._has_context_for_pattern(pattern, context):
        questions.append(pattern)
```

### 4. Agent Returns Clarification Request

If questions exist, agent pauses:

```python
{
    "clear": False,
    "questions": [
        "What is the core user problem being solved?",
        "What are must-have vs nice-to-have features?",
        "Who are the target users?"
    ],
    "capability": "create_prd"
}
```

### 5. Context Provided, Agent Proceeds

Once context is complete:

```python
agent.clarify_task(
    task="create PRD for new feature",
    context={
        "user_problem": "Users need to export data quickly",
        "features": ["CSV export", "JSON export"],
        "target_users": "Data analysts",
        "success_metrics": "Export time < 1 second"
    }
)

# Result:
{
    "clear": True,
    "questions": [],
    "capability": "create_prd"
}
```

## Inquiry Pattern Design

### Good Inquiry Patterns

✓ Specific and actionable:
```yaml
inquiry_patterns:
  - "What is the core user problem being solved?"
  - "Who are the primary and secondary users?"
  - "What are the technical constraints?"
```

✓ Open-ended (avoid yes/no):
```yaml
inquiry_patterns:
  - "What are the acceptance criteria?"  # Good
  - "Are there acceptance criteria?"    # Bad (yes/no)
```

✓ Domain-specific keywords:
```yaml
inquiry_patterns:
  - "What scope to analyze? (file/module/system)"
  - "What depth level? (surface/detailed/comprehensive)"
```

### Poor Inquiry Patterns

✗ Too vague:
```yaml
inquiry_patterns:
  - "What do you want?"  # Too general
  - "Any other information?"  # Not specific enough
```

✗ Assumption-laden:
```yaml
inquiry_patterns:
  - "Should we use React or Vue?"  # Assumes frontend framework needed
  - "What color theme?"  # Assumes UI work
```

## Keyword Extraction

Context validation uses sophisticated keyword extraction:

```python
from src.core.context_keyword_extractor import ContextKeywordExtractor

pattern = "What is the core user problem being solved?"

# Extract keywords with domain mappings
keywords = ContextKeywordExtractor.extract_keywords(pattern)
# Returns: {"user", "problem", "user_problem", "core_problem"}

# Check context
has_context = ContextKeywordExtractor.has_context_for_pattern(
    pattern,
    context={"user_problem": "Users need fast data export"}
)
# Returns: True (keyword "user_problem" found in context)
```

### Domain Mappings

Keywords are expanded using domain knowledge:

```python
DOMAIN_MAPPINGS = {
    "user": ["user", "users", "target_user", "audience"],
    "requirement": ["requirement", "requirements", "criteria"],
    "feature": ["feature", "features", "functionality"],
    "metric": ["metric", "metrics", "success_metrics", "kpi"]
}

# Pattern: "What are the success metrics?"
# Keywords: {"success", "metrics", "success_metrics", "kpi"}
```

## Agent-Specific Inquiry Patterns

### Orchestrator

```yaml
capabilities:
  - name: "create_prd"
    inquiry_patterns:
      - "What is the core user problem being solved?"
      - "What are must-have vs nice-to-have features?"
      - "Who are the target users?"
      - "What are the success metrics?"

  - name: "decompose_epic"
    inquiry_patterns:
      - "What are the acceptance criteria for this epic?"
      - "What are the technical dependencies between stories?"
      - "What is the priority order for implementation?"
```

### Analyst

```yaml
capabilities:
  - name: "elicit_requirements"
    inquiry_patterns:
      - "What problem does this solve for users?"
      - "Who are the primary and secondary users?"
      - "What are the technical constraints?"
      - "What are we NOT building (scope boundaries)?"

  - name: "analyze_codebase"
    inquiry_patterns:
      - "What scope to analyze? (file/module/system)"
      - "What depth level? (surface/detailed/comprehensive)"
      - "What specific patterns or issues to look for?"
```

### Knowledge

```yaml
capabilities:
  - name: "generate_architecture"
    inquiry_patterns:
      - "What system components exist?"
      - "What integration points?"
      - "What scalability requirements?"

  - name: "store_episode"
    inquiry_patterns:
      - "What type of knowledge? (nodes/facts/episodes)"
      - "What is the source agent?"
      - "What metadata should be attached?"
```

### Developer

```yaml
capabilities:
  - name: "implement_story"
    inquiry_patterns:
      - "What are the acceptance criteria?"
      - "What test cases are needed?"
      - "What story file sections can I edit?"

  - name: "debug_issue"
    inquiry_patterns:
      - "What is the error message?"
      - "What are the reproduction steps?"
      - "What browser/environment?"
```

### Validator

```yaml
capabilities:
  - name: "validate_story"
    inquiry_patterns:
      - "What test scope? (story-specific/full regression)"
      - "What acceptance criteria to verify?"
      - "What risk level? (low/medium/high/critical)"

  - name: "optimize_performance"
    inquiry_patterns:
      - "What optimizer type? (bootstrap/mipro)"
      - "What evaluation metric?"
      - "What dataset to use?"
```

## LangGraph Integration

### Clarification Interrupts

When agent needs clarification, workflow pauses:

```python
from langgraph_core.workflow_enhanced import (
    create_bmad_enhanced_workflow,
    BMADWorkflowState
)

# Create workflow with clarification support
workflow = create_bmad_enhanced_workflow(agent_functions)

# Execute workflow
result = await workflow.ainvoke(initial_state, config=config)

# Check for clarification request
if result.get("status") == "clarifying":
    request = result["clarification_request"]
    print(f"Agent {request.agent_id} needs clarification:")
    for question in request.questions:
        print(f"  - {question}")
```

### Providing Clarifications

```python
from langgraph_core.workflow_enhanced import (
    update_state_with_clarifications
)

# Collect answers
answers = {
    "user_problem": "Users need to export data quickly",
    "features": ["CSV export", "JSON export"],
    "target_users": "Data analysts",
    "success_metrics": "Export time < 1 second"
}

# Update state and resume
updated_state = update_state_with_clarifications(result, answers)
result = await workflow.ainvoke(updated_state, config=config)
```

## Testing Inquiry Patterns

```python
def test_orchestrator_clarify_task():
    \"\"\"Test Orchestrator inquiry protocol\"\"\"
    agent = OrchestratorAgent()

    # Empty context triggers clarification
    result = agent.clarify_task(
        task="create_prd for new feature",
        context={}
    )

    assert result["clear"] == False
    assert len(result["questions"]) > 0
    assert "user problem" in result["questions"][0].lower()

    # Complete context passes clarification
    result = agent.clarify_task(
        task="create_prd for new feature",
        context={
            "user_problem": "Users need fast export",
            "features": ["CSV", "JSON"],
            "target_users": "Analysts",
            "success_metrics": "< 1 sec"
        }
    )

    assert result["clear"] == True
    assert len(result["questions"]) == 0
```

## Benefits

1. **Prevents Assumptions**: Agents don't guess missing information
2. **Explicit Context**: All requirements explicitly stated
3. **Better Requirements**: Forces clarity upfront
4. **Audit Trail**: Questions and answers tracked in workflow state
5. **Interrupts Execution**: Workflow pauses until clarification provided

## Common Patterns

### Progressive Clarification

Agent asks high-level questions first, then drills down:

```python
# Round 1: High-level questions
questions = [
    "What is the core user problem?",
    "Who are the target users?"
]

# Round 2 (after Round 1 answers): Detailed questions
questions = [
    "What specific data formats to support?",
    "What is the max export size?"
]
```

### Conditional Questions

Some questions only asked if certain context exists:

```python
if context.get("has_authentication"):
    questions.append("What authentication method?")

if context.get("has_database"):
    questions.append("What database schema?")
```

### Alternative Suggestions

Agent suggests alternatives in questions:

```yaml
inquiry_patterns:
  - "What scope to analyze? (file/module/system)"
  - "What depth level? (surface/detailed/comprehensive)"
  - "What authentication method? (OAuth/JWT/session-based)"
```

## Related Documentation

- [persona-system.md](persona-system.md) - Personas that drive inquiry behavior
- [agent-capabilities.md](agent-capabilities.md) - Full capability definitions
- [langgraph-orchestration.md](langgraph-orchestration.md) - LangGraph workflow integration
