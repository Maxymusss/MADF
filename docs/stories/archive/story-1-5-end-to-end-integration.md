# Story 1.5: End-to-End Workflow Integration

**Epic**: Epic 1 - Multi-Agent Development Framework MVP
**Sprint**: Phase 1 (Week 3)
**Estimated Effort**: 2-3 days
**Dependencies**: All previous stories (1.1-1.4)

## User Story

As a **multi-agent development system operator**,
I want **complete workflow integration from BMAD planning through research commentary delivery**,
so that **the prototype demonstrates full multi-agent coordination capabilities**.

## Acceptance Criteria

### AC1: Complete Workflow Execution
- [ ] Execute full workflow: BMAD plan → Free news APIs → Commentary generation → File delivery
- [ ] Test workflow with real free news API data (not Bloomberg Terminal)
- [ ] Validate end-to-end execution time (<30 minutes for weekly collection)
- [ ] Confirm data flows correctly between all agent nodes

### AC2: Agent Coordination Validation
- [ ] Validate that all 4 agents (Planning, Research, Dev, PM) work together correctly
- [ ] Test agent handoffs with proper state management
- [ ] Verify error propagation and recovery across agents
- [ ] Confirm LangGraph orchestration manages agent sequence

### AC3: State Management Integrity
- [ ] Ensure LangGraph state properly passes between agents without data loss
- [ ] Test Pydantic model validation at each handoff point
- [ ] Verify state persistence through workflow interruptions
- [ ] Validate state filtering preserves required data only

### AC4: Error Recovery and Resilience
- [ ] Test workflow resilience with LangGraph checkpointing
- [ ] Simulate agent failures and validate recovery mechanisms
- [ ] Test partial data collection scenarios (some APIs unavailable)
- [ ] Verify graceful degradation maintains workflow completion

### AC5: Performance Monitoring and Observability
- [ ] Use LangSmith to track execution time, costs, and success rates
- [ ] Monitor token usage and API call efficiency
- [ ] Track memory usage throughout workflow execution
- [ ] Generate performance reports for optimization

### AC6: Manual Validation and Quality Assurance
- [ ] Human review confirms commentary quality and delivery accuracy
- [ ] Validate geographic coverage matches requirements (EM Asia + US)
- [ ] Confirm output format meets 50-80 word summary standards
- [ ] Test multiple workflow executions for consistency

## Integration Validation Features

### IV1: Real Free News API Data Processing
- [ ] Full workflow completes successfully with NewsAPI, Yahoo Finance, Alpha Vantage
- [ ] Remove all Bloomberg Terminal API references and dependencies
- [ ] Test with actual API rate limits and quota constraints
- [ ] Validate data quality sufficient for commentary generation

### IV2: Commentary Quality Standards
- [ ] Generated weekly commentary meets 50-80 word format standards
- [ ] Content demonstrates market insight and professional analysis
- [ ] Geographic coverage includes required EM Asia markets + US
- [ ] Time period coverage accurate (7-day weekly cycle)

### IV3: Workflow Persistence and Recovery
- [ ] LangGraph persistence enables workflow recovery after interruption
- [ ] Checkpoint system allows restart from any agent node
- [ ] State reconstruction maintains data integrity
- [ ] Error logs provide sufficient debugging information

### IV4: Agent Handoff Reliability
- [ ] Agent handoffs work reliably with proper state filtering
- [ ] No data loss occurs during state transitions
- [ ] Pydantic validation catches state corruption early
- [ ] Conditional routing works correctly based on state content

### IV5: Output Integration
- [ ] Reference attribution properly separated from commentary content
- [ ] File delivery to hedgemonkey project maintains structure
- [ ] Metadata files generated with workflow tracking information
- [ ] Archive system preserves historical workflow execution data

## Technical Implementation Details

### Workflow Orchestration Script
```python
# langgraph_core/workflows/weekly_research.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from ..agents.planning import planning_agent
from ..agents.research import research_agent
from ..agents.dev import dev_agent
from ..agents.pm import pm_agent
from ..models.state import WorkflowState

def create_weekly_research_workflow() -> StateGraph:
    """
    Create complete weekly research workflow with 4-agent coordination
    """

    # Initialize workflow with checkpointing
    memory = SqliteSaver.from_conn_string("data/checkpoints.db")

    workflow = StateGraph(WorkflowState)

    # Add agent nodes
    workflow.add_node("planning", planning_agent)
    workflow.add_node("research", research_agent)
    workflow.add_node("dev", dev_agent)
    workflow.add_node("pm", pm_agent)

    # Define workflow edges
    workflow.add_edge("planning", "research")
    workflow.add_edge("research", "dev")
    workflow.add_edge("dev", "pm")
    workflow.add_edge("pm", END)

    # Set entry point
    workflow.set_entry_point("planning")

    # Compile with memory
    return workflow.compile(checkpointer=memory)

async def execute_weekly_research(workflow_id: str) -> Dict[str, Any]:
    """
    Execute complete weekly research workflow
    """
    workflow = create_weekly_research_workflow()

    # Initialize state
    initial_state = WorkflowState(
        workflow_id=workflow_id,
        current_agent="planning",
        metadata={
            "execution_start": datetime.utcnow().isoformat(),
            "target_regions": ["CN", "TW", "KR", "HK", "SG", "TH", "MY", "PH", "ID", "IN", "US"],
            "target_markets": ["fx", "rates"],
            "output_format": "weekly_commentary"
        }
    )

    # Execute workflow
    config = {"configurable": {"thread_id": workflow_id}}

    try:
        result = await workflow.ainvoke(initial_state, config=config)
        return {
            "success": True,
            "workflow_id": workflow_id,
            "final_state": result,
            "execution_time": calculate_execution_time(result),
            "performance_metrics": extract_performance_metrics(result)
        }
    except Exception as e:
        return {
            "success": False,
            "workflow_id": workflow_id,
            "error": str(e),
            "last_checkpoint": await get_last_checkpoint(workflow, config)
        }
```

### Integration Test Suite
```python
# tests/integration/test_end_to_end_workflow.py
import pytest
import asyncio
from datetime import datetime, timedelta
from langgraph_core.workflows.weekly_research import execute_weekly_research

class TestEndToEndWorkflow:

    @pytest.mark.asyncio
    async def test_complete_workflow_execution(self):
        """Test complete workflow with real API data"""
        workflow_id = f"test_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        result = await execute_weekly_research(workflow_id)

        assert result["success"] is True
        assert "final_state" in result
        assert result["final_state"].validation_status == "approved"
        assert len(result["final_state"].errors) == 0

    @pytest.mark.asyncio
    async def test_workflow_resilience(self):
        """Test workflow recovery from interruption"""
        workflow_id = f"resilience_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Start workflow
        workflow = create_weekly_research_workflow()
        config = {"configurable": {"thread_id": workflow_id}}

        # Execute partially (simulate interruption after research agent)
        initial_state = create_test_state(workflow_id)
        partial_result = await workflow.ainvoke(initial_state, config=config)

        # Simulate restart - workflow should resume from checkpoint
        resume_result = await workflow.ainvoke(None, config=config)

        assert resume_result["success"] is True
        assert resume_result["final_state"].current_agent == "pm"

    @pytest.mark.asyncio
    async def test_api_fallback_scenarios(self):
        """Test workflow with API failures and fallbacks"""
        workflow_id = f"fallback_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Configure API client to simulate NewsAPI failure
        with mock_newsapi_failure():
            result = await execute_weekly_research(workflow_id)

        # Workflow should complete using backup sources
        assert result["success"] is True
        assert "yahoo_finance" in result["final_state"].research_data["sources_used"]
        assert result["final_state"].research_data["collection_summary"]["total_items"] > 0

    @pytest.mark.asyncio
    async def test_performance_requirements(self):
        """Test workflow meets performance requirements"""
        workflow_id = f"perf_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        start_time = datetime.utcnow()
        result = await execute_weekly_research(workflow_id)
        execution_time = (datetime.utcnow() - start_time).total_seconds()

        # Should complete within 30 minutes
        assert execution_time < 1800
        assert result["success"] is True

        # Token usage should be reasonable (<$5 per workflow)
        metrics = result["performance_metrics"]
        assert metrics["estimated_cost"] < 5.0
        assert metrics["total_tokens"] < 50000
```

### Performance Monitoring Integration
```python
# langgraph_core/utils/monitoring.py
from langsmith import Client
import json
from typing import Dict, Any

class WorkflowMonitor:
    def __init__(self):
        self.langsmith_client = Client()

    async def track_workflow_execution(self, workflow_id: str, state: WorkflowState) -> None:
        """Track workflow execution metrics in LangSmith"""

        # Create execution trace
        trace_data = {
            "workflow_id": workflow_id,
            "current_agent": state.current_agent,
            "timestamp": datetime.utcnow().isoformat(),
            "state_size": len(json.dumps(state.model_dump())),
            "errors": state.errors,
            "metadata": state.metadata
        }

        # Log to LangSmith
        self.langsmith_client.create_run(
            name=f"weekly_research_{workflow_id}",
            run_type="chain",
            inputs={"workflow_id": workflow_id},
            outputs=trace_data
        )

    def generate_performance_report(self, workflow_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate performance analysis report"""

        successful_runs = [r for r in workflow_results if r["success"]]
        failed_runs = [r for r in workflow_results if not r["success"]]

        if not workflow_results:
            return {"error": "No workflow results to analyze"}

        return {
            "total_workflows": len(workflow_results),
            "success_rate": len(successful_runs) / len(workflow_results),
            "average_execution_time": sum(r.get("execution_time", 0) for r in successful_runs) / len(successful_runs) if successful_runs else 0,
            "average_cost": sum(r.get("performance_metrics", {}).get("estimated_cost", 0) for r in successful_runs) / len(successful_runs) if successful_runs else 0,
            "common_errors": self._analyze_common_errors(failed_runs),
            "recommendations": self._generate_optimization_recommendations(successful_runs)
        }
```

## File Structure Additions
```
langgraph_core/
├── workflows/
│   ├── __init__.py
│   └── weekly_research.py     # Main workflow orchestration
├── utils/
│   ├── monitoring.py          # Performance monitoring
│   └── integration_helpers.py # Integration utilities
└── data/
    ├── checkpoints.db         # SQLite checkpoints
    └── execution_logs/        # Workflow execution logs

tests/
├── integration/
│   ├── test_end_to_end_workflow.py
│   ├── test_api_integration.py
│   └── test_performance.py
└── fixtures/
    ├── sample_news_data.json
    └── mock_api_responses.json
```

## Manual Validation Checklist

### Pre-Execution Validation
- [ ] All API keys configured and tested
- [ ] MCP bridge service operational
- [ ] LangSmith project configured
- [ ] Hedgemonkey project directory accessible
- [ ] BMAD agent available for planning session

### During Execution Monitoring
- [ ] Planning agent successfully loads approved plan
- [ ] Research agent collects data from multiple sources
- [ ] Dev agent generates content within word limits
- [ ] PM agent validates and delivers output
- [ ] All checkpoints saved successfully

### Post-Execution Validation
- [ ] Commentary file created in hedgemonkey project
- [ ] Content quality meets professional standards
- [ ] Geographic coverage complete for required regions
- [ ] Performance metrics within acceptable ranges
- [ ] Error logs clear of critical issues

## Performance Benchmarks

### Execution Time Targets
- **Total Workflow**: <30 minutes
- **Planning Agent**: <2 minutes
- **Research Agent**: <20 minutes (API collection time)
- **Dev Agent**: <5 minutes (content generation)
- **PM Agent**: <3 minutes (validation and delivery)

### Quality Metrics
- **Geographic Coverage**: 100% of required regions
- **Content Quality**: Human review score >80%
- **Workflow Success Rate**: >90% in normal conditions
- **Error Recovery Rate**: >95% for transient failures

### Cost Efficiency
- **Token Usage**: <50,000 tokens per workflow
- **API Costs**: <$5 per weekly commentary
- **Resource Usage**: <4GB memory peak
- **Storage**: <100MB per workflow execution


## Testing Status 🧪

- [ ] **TESTED** - Testing pending
  - **Test Results**: TBD
  - **Unit Tests**: TBD
  - **Integration Tests**: TBD
  - **Test Date**: TBD

## Definition of Done

- [ ] All acceptance criteria completed and tested
- [ ] Complete workflow executes successfully end-to-end
- [ ] Integration tests pass for all scenarios
- [ ] Performance meets or exceeds benchmark targets
- [ ] Manual validation confirms output quality
- [ ] Ready for Story 1.6 (Claude Code Integration)

## Risk Mitigation

**Risk**: End-to-end workflow too complex for reliable execution
**Mitigation**: Comprehensive error handling, fallback mechanisms, checkpoint recovery

**Risk**: Performance degradation with real API data
**Mitigation**: Optimize API calls, implement caching, parallel processing where possible

**Risk**: Integration points fail under production conditions
**Mitigation**: Extensive integration testing, monitoring and alerting systems

## Success Criteria

- Complete 4-agent workflow operational and reliable
- End-to-end execution demonstrates multi-agent coordination
- Performance meets efficiency and cost targets
- Output quality validates prototype approach
- Foundation ready for Claude Code user interface (Story 1.6)