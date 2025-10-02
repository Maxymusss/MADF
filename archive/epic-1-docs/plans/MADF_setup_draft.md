# MADF Technical Implementation Draft
## Detailed Code Examples and Setup Instructions

This document contains the detailed technical implementation code extracted from the main MADF structure plan.

## Layer 1: LangGraph Implementation Details

### PM Agent Code
```python
# orchestration/agents/pm_agent.py
class PMAgent:
    """
    Summarizes research results, coordinates task planning, and manages human interactions
    """
    def __init__(self):
        self.model = ChatAnthropic(model="claude-3-5-sonnet-20241022")
        self.taskmaster = TaskMasterIntegration()
        self.summary_threshold = 0.7  # Confidence threshold for human review

    async def summarize_research_results(self, research_outputs):
        """Aggregate and summarize results from multiple research agents"""
        summary = {
            "key_findings": await self.extract_key_findings(research_outputs),
            "consensus_points": await self.identify_consensus(research_outputs),
            "conflicting_info": await self.identify_conflicts(research_outputs),
            "confidence_score": await self.calculate_confidence(research_outputs),
            "recommendations": await self.generate_recommendations(research_outputs)
        }

        # Determine if human review needed
        if summary["confidence_score"] < self.summary_threshold:
            summary["requires_human_review"] = True
            summary["review_reason"] = "Low confidence in research findings"

        return summary

    async def create_execution_plan(self, summarized_research):
        """Convert summarized research into actionable tasks"""
        plan = {
            "tasks": await self.decompose_requirements(summarized_research),
            "dependencies": await self.map_dependencies(),
            "specialist_needs": await self.identify_specialists(),
            "parallel_opportunities": await self.find_parallelism(),
            "human_checkpoints": await self.identify_human_gates(),
            "risk_assessment": await self.assess_risks(summarized_research)
        }
        return plan

    async def coordinate_research_agents(self, query, num_agents=3):
        """Dispatch query to multiple research agents for diverse perspectives"""
        research_tasks = []
        for i in range(num_agents):
            task = {
                "agent_id": f"research_agent_{i}",
                "query": query,
                "focus_area": self.assign_focus_area(i),
                "timeout": 30
            }
            research_tasks.append(task)

        return await self.dispatch_to_layer2(research_tasks)

    async def route_to_specialists(self, task, available_agents):
        """Determine which Layer 2 agent should handle task"""
        task_type = await self.classify_task(task)
        return self.select_best_agent(task_type, available_agents)
```

### HR Agent Code
```python
# orchestration/agents/hr_agent.py
class HRAgent:
    """
    Dynamic specialist management and performance monitoring
    """
    def __init__(self):
        self.evaluation_cycles = 15
        self.performance_thresholds = {
            "success_rate": 0.80,
            "error_rate": 0.20,
            "efficiency_gain": 0.15
        }

    async def evaluate_specialist_need(self, task_patterns):
        """Determine if new specialists are needed"""
        analysis = {
            "database_tasks": self.count_database_patterns(task_patterns),
            "api_tasks": self.count_api_patterns(task_patterns),
            "frontend_tasks": self.count_frontend_patterns(task_patterns)
        }

        recommendations = []
        for task_type, count in analysis.items():
            if count > 5 and not self.has_specialist(task_type):
                recommendations.append(self.create_specialist_spec(task_type))

        return recommendations

    async def performance_review(self, agent_id, metrics):
        """Make hire/fire decisions based on performance"""
        if metrics["task_count"] < self.evaluation_cycles:
            return {"decision": "continue", "reason": "insufficient data"}

        scores = self.calculate_performance_scores(metrics)

        if self.meets_thresholds(scores):
            return {"decision": "keep", "confidence": scores["overall"]}
        else:
            return {
                "decision": "improve_or_retire",
                "improvement_plan": await self.generate_improvement_plan(scores),
                "requires_human_approval": True
            }
```

### Human Interaction Manager
```python
# orchestration/human_interaction.py
class HumanInteractionManager:
    """
    Manages all human-in-the-loop interactions
    """
    def __init__(self):
        self.interaction_points = {
            "research_validation": {"priority": "medium", "timeout": 3600},
            "plan_approval": {"priority": "high", "timeout": 1800},
            "critical_decisions": {"priority": "critical", "timeout": 900},
            "quality_gates": {"priority": "medium", "timeout": 3600},
            "error_escalation": {"priority": "high", "timeout": 1200}
        }

    async def request_human_input(self, interaction_type, context):
        """Request human input with timeout and fallback"""
        config = self.interaction_points[interaction_type]

        request = {
            "type": interaction_type,
            "priority": config["priority"],
            "context": context,
            "options": await self.generate_options(context),
            "default_action": await self.determine_default(context),
            "timeout": config["timeout"]
        }

        # Send notification to human
        await self.notify_human(request)

        # Wait for response with timeout
        response = await self.wait_for_response(request)

        if response is None:
            # Timeout - use default action
            return self.apply_default_action(request)

        return response

    async def human_review_gate(self, state):
        """Gate for human review of plans and decisions"""
        if state["confidence_score"] < 0.7 or state["risk_level"] == "high":
            review_needed = True
        else:
            review_needed = False

        if review_needed:
            human_decision = await self.request_human_input(
                "plan_approval",
                {
                    "plan": state["execution_plan"],
                    "risks": state["risk_assessment"],
                    "alternatives": state["alternative_approaches"]
                }
            )
            state["human_decision"] = human_decision
            state["human_reviewed"] = True

        return state
```

### LangGraph Orchestration Graph
```python
# orchestration/graphs/main_supervisor.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint import MemorySaver
from typing import TypedDict, Annotated, List
from langchain_core.messages import AnyMessage, add_messages

class MADFState(TypedDict):
    """Global state for MADF orchestration"""
    messages: Annotated[List[AnyMessage], add_messages]
    project_type: str  # alphaseek, totorich, prototype
    current_phase: str  # research, planning, execution, feedback
    research_results: List[dict]  # Multiple research agent outputs
    summarized_research: dict  # PM agent summary
    execution_plan: dict
    specialist_agents: List[str]
    performance_metrics: dict
    human_approval_needed: bool
    human_decisions: List[dict]  # Track human inputs
    confidence_score: float
    risk_level: str
    artifacts: List[dict]
    errors: List[dict]
    improvements_applied: List[dict]

def create_madf_orchestrator():
    workflow = StateGraph(MADFState)

    # Add Layer 1 nodes
    workflow.add_node("pm_coordinator", pm_coordinator_node)
    workflow.add_node("research_dispatch", research_dispatch_node)
    workflow.add_node("research_summary", research_summary_node)
    workflow.add_node("human_review_research", human_review_research_node)
    workflow.add_node("planning", planning_node)
    workflow.add_node("human_review_plan", human_review_plan_node)
    workflow.add_node("hr_evaluation", hr_evaluation_node)
    workflow.add_node("specialist_creation", specialist_creation_node)
    workflow.add_node("task_routing", task_routing_node)

    # Add Layer 2 execution subgraph
    workflow.add_node("layer2_execution", layer2_execution_subgraph)

    # Add feedback and improvement nodes
    workflow.add_node("human_quality_gate", human_quality_gate_node)
    workflow.add_node("performance_monitoring", performance_monitoring_node)
    workflow.add_node("error_analysis", error_analysis_node)
    workflow.add_node("human_error_review", human_error_review_node)
    workflow.add_node("improvement_application", improvement_application_node)

    # Define conditional routing
    def route_after_research_summary(state):
        if state["confidence_score"] < 0.7:
            return "human_review_research"
        else:
            return "planning"

    def route_after_planning(state):
        if state["human_approval_needed"] or state["risk_level"] == "high":
            return "human_review_plan"
        else:
            return "hr_evaluation"

    def route_after_hr(state):
        if state["specialist_agents"]:
            return "task_routing"
        else:
            return "specialist_creation"

    def route_after_execution(state):
        if state["errors"] and len(state["errors"]) > 3:
            return "human_error_review"
        elif state["errors"]:
            return "error_analysis"
        else:
            return "human_quality_gate"

    def route_after_quality_gate(state):
        if state["quality_approved"]:
            return "performance_monitoring"
        else:
            return "improvement_application"

    # Connect the graph
    workflow.add_edge("pm_coordinator", "research_dispatch")
    workflow.add_edge("research_dispatch", "research_summary")
    workflow.add_conditional_edges("research_summary", route_after_research_summary)
    workflow.add_edge("human_review_research", "planning")
    workflow.add_conditional_edges("planning", route_after_planning)
    workflow.add_edge("human_review_plan", "hr_evaluation")
    workflow.add_conditional_edges("hr_evaluation", route_after_hr)
    workflow.add_edge("specialist_creation", "task_routing")
    workflow.add_edge("task_routing", "layer2_execution")
    workflow.add_conditional_edges("layer2_execution", route_after_execution)
    workflow.add_edge("human_error_review", "improvement_application")
    workflow.add_edge("error_analysis", "improvement_application")
    workflow.add_conditional_edges("human_quality_gate", route_after_quality_gate)
    workflow.add_edge("performance_monitoring", "improvement_application")
    workflow.add_conditional_edges(
        "improvement_application",
        lambda x: END if x["current_phase"] == "complete" else "task_routing"
    )

    # Set entry point
    workflow.set_entry_point("pm_coordinator")

    # Compile with persistence and human-in-the-loop
    checkpointer = MemorySaver()
    return workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_review_research", "human_review_plan", "human_quality_gate", "human_error_review"]
    )
```

## Research Coordination Workflow
```python
# orchestration/workflows/research_coordination.py
class ResearchCoordinator:
    """
    Coordinates multiple Layer 2 research agents and summarizes results
    """

    async def coordinate_research_phase(self, query, project_type):
        """
        1. PM Agent dispatches research to multiple Claude Code Research Agents
        2. Research Agents work in parallel on different focus areas
        3. PM Agent summarizes and synthesizes results
        4. Human review gate based on confidence score
        """

        # Step 1: Dispatch to multiple research agents
        research_tasks = self.create_research_tasks(query, project_type)

        # Step 2: Execute research in parallel
        research_results = await asyncio.gather(*[
            self.dispatch_to_research_agent(task) for task in research_tasks
        ])

        # Step 3: PM Agent synthesizes results
        summary = await self.pm_agent.summarize_research_results(research_results)

        # Step 4: Human review if needed
        if summary["confidence_score"] < 0.7:
            summary = await self.request_human_review(summary)

        return summary

    def create_research_tasks(self, query, project_type):
        """Create focused research tasks for different agents"""
        if project_type == "alphaseek":
            return [
                {"focus": "quant_patterns", "query": f"{query} quantitative finance patterns"},
                {"focus": "performance", "query": f"{query} performance optimization techniques"},
                {"focus": "testing", "query": f"{query} financial testing strategies"}
            ]
        elif project_type == "totorich":
            return [
                {"focus": "fullstack", "query": f"{query} full-stack architecture patterns"},
                {"focus": "api_design", "query": f"{query} API best practices"},
                {"focus": "ui_ux", "query": f"{query} modern UI/UX approaches"}
            ]
        else:  # prototype
            return [
                {"focus": "simple_patterns", "query": f"{query} simple implementation approaches"},
                {"focus": "documentation", "query": f"{query} documentation standards"}
            ]
```

## Human Decision Gates
```python
# orchestration/human_gates.py
class HumanDecisionGates:
    """
    Defines specific human interaction points with clear criteria
    """

    def __init__(self):
        self.gates = {
            "research_validation": {
                "trigger": "confidence_score < 0.7 OR conflicting_info > 2",
                "timeout": 3600,  # 1 hour
                "options": ["approve", "request_more_research", "provide_guidance"],
                "default": "approve"
            },
            "plan_approval": {
                "trigger": "risk_level == 'high' OR budget_impact > 1000",
                "timeout": 1800,  # 30 minutes
                "options": ["approve", "modify", "reject"],
                "default": "approve"
            },
            "quality_gate": {
                "trigger": "test_coverage < 80% OR critical_bugs > 0",
                "timeout": 3600,  # 1 hour
                "options": ["approve", "fix_required", "accept_risk"],
                "default": "fix_required"
            },
            "error_escalation": {
                "trigger": "error_count > 3 OR agent_failure_rate > 20%",
                "timeout": 1200,  # 20 minutes
                "options": ["retry", "reassign", "human_takeover"],
                "default": "retry"
            },
            "specialist_creation": {
                "trigger": "new_agent_request OR performance_below_threshold",
                "timeout": 2400,  # 40 minutes
                "options": ["create", "retrain_existing", "delay"],
                "default": "create"
            }
        }

    async def evaluate_gate(self, gate_type, context):
        """Evaluate if human intervention is needed"""
        gate_config = self.gates[gate_type]

        # Check trigger conditions
        if self.evaluate_trigger(gate_config["trigger"], context):
            return await self.request_human_decision(gate_type, context)
        else:
            return {"decision": "proceed", "automated": True}
```

## Layer 2 Agent Configurations

### Research Agent
```json
// .claude/agents/research.json
{
  "name": "Research Agent",
  "role": "Information gathering and analysis execution",
  "system_prompt": "You are a research specialist. Gather comprehensive information and provide detailed analysis with confidence scores.",
  "tools": [
    "WebSearch",
    "WebFetch",
    "mcp__context7__*",
    "mcp__github__search_*",
    "mcp__langgraph-docs-mcp__*",
    "Grep",
    "Read",
    "Glob"
  ],
  "research_focus_areas": [
    "codebase_analysis",
    "best_practices",
    "technical_patterns",
    "dependency_mapping",
    "security_considerations"
  ],
  "output_requirements": {
    "confidence_score": "required",
    "source_citations": "required",
    "alternative_approaches": "required",
    "risk_assessment": "required"
  },
  "success_criteria": {
    "completeness": ">90%",
    "accuracy": ">95%",
    "response_time": "<60s"
  }
}
```

### Implementation Agent
```json
// .claude/agents/implementation.json
{
  "name": "Implementation Agent",
  "role": "Code generation and development",
  "system_prompt": "You are a senior software engineer focused on clean, maintainable code. Follow TDD principles.",
  "tools": [
    "Edit",
    "Write",
    "MultiEdit",
    "Read",
    "Bash",
    "mcp__task-master-ai__*"
  ],
  "rules": [
    "rules/code_quality.md",
    "rules/testing_first.md"
  ],
  "success_criteria": {
    "code_compiles": true,
    "tests_pass": true,
    "coverage_threshold": 0.80
  }
}
```

## MCP Bridge Implementation
```python
# orchestration/mcp_bridge.py
import asyncio
from typing import Dict, Any
import subprocess
import json

class MCPBridge:
    """
    Bridges Layer 1 LangGraph with Layer 2 Claude Code agents
    """

    def __init__(self):
        self.sessions = {}
        self.mcp_servers = {
            "task_master": {
                "command": "npx",
                "args": ["-y", "task-master-ai"],
                "env": {"ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY")}
            },
            "claude_executor": {
                "command": "python",
                "args": ["mcp_servers/claude_executor.py"]
            }
        }

    async def dispatch_to_claude(self, agent_profile: str, task: Dict[str, Any], context: Dict[str, Any]):
        """
        Dispatch task from LangGraph to Claude Code agent
        """
        # Create or reuse session
        session_id = f"{agent_profile}_{task['id']}"

        if session_id not in self.sessions:
            self.sessions[session_id] = await self.create_claude_session(
                agent_profile=agent_profile,
                context_files=context.get("files", []),
                project_root=context.get("project_root", ".")
            )

        # Execute task through MCP
        result = await self.execute_via_mcp(
            session_id=session_id,
            command="execute_task",
            params={
                "task": task,
                "tools_allowed": self.get_tools_for_agent(agent_profile),
                "max_iterations": 5
            }
        )

        return self.parse_claude_result(result)

    async def create_claude_session(self, agent_profile: str, context_files: list, project_root: str):
        """
        Initialize a Claude Code session with proper context
        """
        session_config = {
            "profile": f".claude/agents/{agent_profile}.json",
            "context": {
                "files": context_files,
                "project_root": project_root,
                "rules": self.load_agent_rules(agent_profile)
            },
            "mcp_servers": self.get_mcp_servers_for_agent(agent_profile)
        }

        # Launch Claude Code in headless mode
        process = await asyncio.create_subprocess_exec(
            "claude",
            "--headless",
            "--config", json.dumps(session_config),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        return {
            "process": process,
            "config": session_config,
            "created_at": asyncio.get_event_loop().time()
        }
```

## Specialist Manager
```python
# orchestration/specialist_manager.py
class SpecialistManager:
    """Manages Layer 2 specialist lifecycle"""

    def __init__(self):
        self.active_specialists = {}
        self.specialist_templates = {
            "database": DatabaseAgent,
            "api": APIAgent,
            "frontend": FrontendAgent,
            "testing": TestingAgent,
            "security": SecurityAgent,
            "documentation": DocumentationAgent
        }

    async def create_specialist(self, specialist_type, job_description):
        """Instantiate a new specialist based on needs"""
        if specialist_type not in self.specialist_templates:
            specialist_type = await self.find_closest_match(specialist_type)

        specialist = self.specialist_templates[specialist_type](
            job_description=job_description,
            evaluation_period=15,
            performance_thresholds=self.get_thresholds(specialist_type)
        )

        self.active_specialists[specialist.id] = specialist
        return specialist

    async def retire_specialist(self, specialist_id, reason):
        """Remove underperforming specialist"""
        specialist = self.active_specialists[specialist_id]

        # Archive performance data for learning
        await self.archive_performance(specialist)

        # Reassign pending tasks
        await self.reassign_tasks(specialist.pending_tasks)

        del self.active_specialists[specialist_id]

        return {
            "retired": specialist_id,
            "reason": reason,
            "tasks_reassigned": len(specialist.pending_tasks)
        }
```

## Installation & Setup Commands

### Phase 1: Infrastructure Setup
```bash
# Install LangGraph and dependencies
pip install langgraph langchain langsmith langchain-anthropic langchain-openai

# Setup Redis for state management
docker run -d -p 6379:6379 redis:alpine

# Create project structure
mkdir -p orchestration/{agents,graphs,workflows,state,config}
mkdir -p .claude/{agents,commands,hooks,rules}
mkdir -p monitoring
```

### Phase 2: MCP Configuration
```json
// .mcp.json
{
  "mcpServers": {
    "orchestrator": {
      "command": "python",
      "args": ["orchestration/mcp_server.py"],
      "env": {
        "LANGSMITH_API_KEY": "${LANGSMITH_API_KEY}",
        "LANGCHAIN_TRACING_V2": "true"
      }
    }
  }
}
```

### Phase 3: Agent Configuration Files
All the JSON configurations for Layer 2 agents would be placed in their respective files as shown above.

### Phase 4: Testing Framework
```python
# tests/test_orchestration.py
async def test_full_workflow():
    orchestrator = create_madf_orchestrator()

    # Test research phase
    result = await orchestrator.ainvoke({
        "messages": [HumanMessage("Research authentication patterns")],
        "current_task": "auth_implementation"
    })

    assert result["research_complete"] == True
    assert len(result["plan"]["tasks"]) > 0
```

### LangGraph StateGraph Design

**Core State Schema:**
```python
class LMADFState(TypedDict):
    task: Dict              # Original task details
    task_type: str          # Classification (frontend/backend/qa/research)
    agent_history: List     # Agent handoff chain with timestamps
    results: Dict           # Accumulated results from each agent
    confidence_score: float # Overall workflow confidence
    status: str            # Current workflow status
    errors: List           # Error tracking and retry logic
    project_context: Dict  # Project-specific context (alphaseek focus)
    created_at: str        # Timestamps for tracking
    updated_at: str        # Last modification time

    # Agent-specific state fields
    active_agent: str       # Currently active agent ID (PM/HR/HI/DA/SR/JR/JC/SC/TA/QA/DAA/SA)
    agent_states: Dict      # Per-agent state tracking for all 12 agents
    pm_context: Dict        # PM-distributed context package
    hr_metrics: Dict        # HR performance tracking data
    hi_decisions: Dict      # Human-in-the-loop approval decisions
    da_cache: Dict          # Doc Agent reusable component findings
    sr_findings: Dict       # Senior Research discoveries
    jr_findings: Dict       # Junior Research summaries
    jc_output: Dict         # Junior Coder implementation details
    sc_output: Dict         # Senior Coder architecture and complex code
    ta_results: Dict        # Test Agent validation outcomes
    qa_models: Dict         # Quant Agent financial models
    daa_pipelines: Dict     # Data Agent processing results
    sa_assessments: Dict    # Security Agent audit findings
```