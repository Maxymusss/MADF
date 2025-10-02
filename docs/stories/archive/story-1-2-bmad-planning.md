# Story 1.2: Manual BMAD Planning Integration

**Epic**: Epic 1 - Multi-Agent Development Framework MVP
**Sprint**: Phase 1 (Week 1-2)
**Estimated Effort**: 2-3 days
**Dependencies**: Story 1.1 (LangGraph Setup)

## User Story

As a **multi-agent development system operator**,
I want **a manual workflow for BMAD planning that integrates with LangGraph execution**,
so that **human-generated plans can be structured for agent execution**.

## Acceptance Criteria

### AC1: BMAD Chat Workflow
- [ ] Establish process for human to chat with BMAD agent for planning
- [ ] Create interaction script for research commentary planning
- [ ] Document workflow steps for generating research plans
- [ ] Test workflow with sample research commentary request

### AC2: Plan Structuring
- [ ] Convert BMAD output into structured format (JSON/YAML) for LangGraph
- [ ] Define plan schema with agent assignments and task details
- [ ] Implement plan validation logic
- [ ] Create plan template for research commentary workflows

### AC3: Planning Agent Node
- [ ] Create LangGraph node that loads and validates BMAD plans
- [ ] Implement plan parsing and state initialization
- [ ] Add plan validation with error reporting
- [ ] Integrate with existing state management from Story 1.1

### AC4: Task Dependencies
- [ ] Ensure plan includes agent assignments and task sequencing
- [ ] Define dependency validation rules
- [ ] Implement task ordering logic
- [ ] Add conflict detection for overlapping assignments

### AC5: Research Commentary Focus
- [ ] Plan specifically for free news API research commentary
- [ ] Define market coverage requirements (EM Asia + US)
- [ ] Specify data source requirements (NewsAPI, Yahoo Finance, etc.)
- [ ] Include output format specifications (50-80 word summaries)

### AC6: Manual Validation
- [ ] Human review and approval of generated plans before execution
- [ ] Create approval workflow interface
- [ ] Implement plan modification capabilities
- [ ] Add approval tracking and audit log

## Technical Implementation Details

### Plan Schema Definition
```python
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum

class AgentType(str, Enum):
    PLANNING = "planning"
    RESEARCH = "research"
    DEV = "dev"
    PM = "pm"

class TaskSpec(BaseModel):
    task_id: str = Field(..., description="Unique task identifier")
    assigned_agent: AgentType = Field(..., description="Agent responsible for task")
    description: str = Field(..., description="Task description")
    dependencies: List[str] = Field(default_factory=list, description="Task dependencies")
    deliverables: List[str] = Field(..., description="Expected outputs")
    acceptance_criteria: List[str] = Field(..., description="Success criteria")

class ResearchPlan(BaseModel):
    plan_id: str = Field(..., description="Unique plan identifier")
    title: str = Field(..., description="Research topic/title")
    objective: str = Field(..., description="Research objective")
    tasks: List[TaskSpec] = Field(..., description="Ordered task list")
    data_sources: List[str] = Field(..., description="Required data sources")
    output_format: str = Field(..., description="Expected output format")
    timeline: str = Field(..., description="Execution timeline")
    approved: bool = Field(default=False, description="Human approval status")
```

### BMAD Interaction Process
1. **Human initiates planning chat with BMAD agent**
2. **BMAD generates structured research plan**
3. **Plan converted to ResearchPlan Pydantic model**
4. **Human reviews and approves/modifies plan**
5. **Approved plan loaded into LangGraph workflow**

### Planning Agent Implementation
```python
def planning_agent(state: WorkflowState) -> WorkflowState:
    """
    Planning Agent Node - Loads and validates BMAD-generated plans
    """
    try:
        # Load plan from manual BMAD workflow
        plan_data = load_approved_plan(state.workflow_id)

        # Validate plan structure
        research_plan = ResearchPlan.model_validate(plan_data)

        # Initialize workflow state with plan
        state.plan = research_plan.model_dump()
        state.current_agent = "research"

        # Set up task queue for execution
        state.metadata["task_queue"] = [task.task_id for task in research_plan.tasks]

        return state

    except Exception as e:
        state.errors.append(f"Planning agent error: {str(e)}")
        raise
```

## Planning Requirements

### PR1: BMAD Research Commentary Workflow
- Generate workflow with clear agent assignments
- Include data collection, analysis, and output generation phases
- Specify news source requirements and coverage areas
- Define quality criteria and validation checkpoints

### PR2: Plan Acceptance Criteria
- Each task must have measurable acceptance criteria
- Deliverables must be clearly specified with formats
- Success metrics must be quantifiable
- Timeline must be realistic for 2-3 week Phase 1

### PR3: Planning Agent Validation
- Validate plan completeness before agent execution
- Check task dependencies for circular references
- Verify agent assignments match available capabilities
- Ensure data source requirements are available

### PR4: Agent Handoff Points
- Clear handoff between Planning → Research
- Clear handoff between Research → Dev
- Clear handoff between Dev → PM
- State filtering preserves required information only

## File Structure
```
langgraph_core/
├── agents/
│   └── planning.py      # Enhanced with BMAD integration
├── models/
│   └── plan.py         # ResearchPlan and TaskSpec models
└── bmad_integration/
    ├── __init__.py
    ├── plan_loader.py   # Load plans from BMAD workflow
    ├── validator.py     # Plan validation logic
    └── templates/
        └── research_commentary.yaml  # Plan template
```

## Manual Workflow Process

### Step 1: BMAD Planning Session
```bash
# Human initiates chat with BMAD agent
/BMad:agents:architect  # or appropriate BMAD agent
> "Create research plan for weekly EM Asia + US FX/rates commentary using free news APIs"
```

### Step 2: Plan Structuring
```yaml
# Generated plan template (research_commentary.yaml)
plan_id: "weekly_research_001"
title: "Weekly EM Asia + US FX/Rates Commentary"
objective: "Generate 50-80 word summaries of major market movements"
tasks:
  - task_id: "research_data_collection"
    assigned_agent: "research"
    description: "Collect news from NewsAPI, Yahoo Finance, Alpha Vantage"
    dependencies: []
    deliverables: ["structured_news_data.json"]
    acceptance_criteria:
      - "Covers EM Asia markets: CN, TW, KR, HK, SG, TH, MY, PH, ID, IN"
      - "Covers US markets with appropriate timezone awareness"
      - "7-day period ending on report generation date"
```

### Step 3: Human Approval
- Review generated plan for completeness
- Modify requirements as needed
- Approve plan for LangGraph execution
- Plan file saved to `langgraph_core/plans/approved/`

## Testing Requirements

### Unit Tests
- Test ResearchPlan model validation
- Test planning agent with valid/invalid plans
- Test plan loading and parsing logic

### Integration Tests
- Test full BMAD → LangGraph integration
- Test plan approval workflow
- Test error handling for malformed plans

### Manual Tests
- Execute complete BMAD planning session
- Verify plan quality and completeness
- Test human approval/modification workflow

## Testing Status 🧪

- [ ] **TESTED** - Testing pending
  - **Test Results**: TBD
  - **Unit Tests**: TBD
  - **Integration Tests**: TBD
  - **Test Date**: TBD

## Definition of Done

- [ ] All acceptance criteria completed and tested
- [ ] BMAD integration workflow documented and proven
- [ ] Plan schema validated with real BMAD output
- [ ] Human approval process tested and functional
- [ ] Planning agent integrates with Story 1.1 foundation
- [ ] Ready for Story 1.3 (Free News API Integration)

## Risk Mitigation

**Risk**: BMAD output format incompatible with plan schema
**Mitigation**: Iterative schema refinement based on actual BMAD sessions

**Risk**: Manual approval process creates bottleneck
**Mitigation**: Streamlined approval interface, clear validation criteria

**Risk**: Plan validation too strict for practical use
**Mitigation**: Configurable validation rules, warning vs error distinction

## Success Criteria

- Manual BMAD planning workflow operational
- Plans successfully load into LangGraph execution
- Human approval process efficient and clear
- Foundation ready for free news API integration (Story 1.3)