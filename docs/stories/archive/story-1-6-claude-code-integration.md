# Story 1.6: Claude Code Integration and User Interface

**Epic**: Epic 1 - Multi-Agent Development Framework MVP
**Sprint**: Phase 1 (Week 3)
**Estimated Effort**: 2-3 days
**Dependencies**: Story 1.5 (End-to-End Integration)

## User Story

As a **MADF user**,
I want **seamless integration between Claude Code and the LangGraph multi-agent system**,
so that **I can trigger research commentary generation through familiar Claude Code interface**.

## Acceptance Criteria

### AC1: Claude Code Entry Point
- [ ] Create `claude_interface.py` that accepts user requests and initializes LangGraph
- [ ] Integrate with existing Claude Code command structure
- [ ] Provide clear command syntax for triggering research workflows
- [ ] Handle user input validation and error messaging

### AC2: Task Integration
- [ ] Integrate with existing Claude Code task system for research commentary requests
- [ ] Support parameterized requests (date ranges, specific markets)
- [ ] Enable both immediate execution and scheduled workflow triggers
- [ ] Maintain compatibility with existing MADF task infrastructure

### AC3: Progress Reporting
- [ ] Provide real-time updates to user on agent execution progress
- [ ] Show current agent status and workflow stage
- [ ] Display estimated completion time and progress percentage
- [ ] Handle long-running operations gracefully with user feedback

### AC4: Result Delivery
- [ ] Return formatted research commentary to user with execution summary
- [ ] Display key metrics (data sources used, coverage, execution time)
- [ ] Provide links to generated files in hedgemonkey project
- [ ] Include quality scores and validation results

### AC5: Error Communication
- [ ] Clear error messages when workflow fails with recovery suggestions
- [ ] Distinguish between user errors and system errors
- [ ] Provide actionable guidance for resolving issues
- [ ] Maintain error logs accessible through Claude Code interface

### AC6: Cost Reporting
- [ ] Show API costs and execution time for budget awareness
- [ ] Track token usage across LLM calls
- [ ] Display cumulative costs for multiple workflow executions
- [ ] Provide cost optimization recommendations

## Integration Success Criteria

### CI1: User Command Interface
- [ ] User can request "Generate FX research commentary" through Claude Code
- [ ] Support variations: "Generate weekly EM Asia FX update", "Create market summary"
- [ ] Handle date-specific requests: "Generate commentary for week ending Jan 27"
- [ ] Provide help and command documentation

### CI2: Progress and Status Updates
- [ ] System provides progress updates during multi-agent execution
- [ ] User sees current agent activity and estimated time remaining
- [ ] Long operations don't appear frozen or unresponsive
- [ ] Option to cancel or interrupt workflow execution

### CI3: Result Presentation
- [ ] Results delivered in user-friendly format with hedgemonkey project integration
- [ ] Commentary displayed in Claude Code interface with formatting
- [ ] File paths and locations clearly communicated
- [ ] Option to regenerate or modify output

### CI4: Error Handling and Recovery
- [ ] Error handling provides actionable feedback without technical details
- [ ] Suggest specific actions: "Check API keys", "Retry with different date range"
- [ ] Distinguish between temporary and permanent failures
- [ ] Provide workflow restart options for recoverable errors

### CI5: Performance and Cost Transparency
- [ ] Performance metrics help user understand system efficiency
- [ ] Cost tracking enables budget-conscious usage
- [ ] Optimization suggestions for reducing costs
- [ ] Historical usage analysis and trends

## Technical Implementation Details

### Claude Code Command Integration
```python
# claude_interface.py - Main Claude Code interface
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from langgraph_core.workflows.weekly_research import execute_weekly_research

class MADFResearchInterface:
    """Claude Code interface for MADF research workflows"""

    def __init__(self):
        self.active_workflows = {}
        self.cost_tracker = CostTracker()

    async def handle_research_request(
        self,
        user_input: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle research commentary requests from Claude Code
        """
        try:
            # Parse user request
            request = self.parse_research_request(user_input, parameters)

            # Validate request parameters
            validation_result = self.validate_request(request)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"],
                    "suggestions": validation_result["suggestions"]
                }

            # Generate workflow ID
            workflow_id = f"claude_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Start workflow with progress tracking
            return await self.execute_research_workflow(workflow_id, request)

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to process research request: {str(e)}",
                "suggestions": ["Check request format", "Verify API keys", "Try again"]
            }

    async def execute_research_workflow(
        self,
        workflow_id: str,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute research workflow with progress tracking
        """
        # Register workflow for progress tracking
        self.active_workflows[workflow_id] = {
            "status": "starting",
            "current_agent": "planning",
            "progress": 0.0,
            "start_time": datetime.utcnow()
        }

        try:
            # Execute workflow with progress callback
            result = await execute_weekly_research(
                workflow_id,
                progress_callback=lambda status: self.update_progress(workflow_id, status)
            )

            # Track costs
            cost_info = self.cost_tracker.calculate_workflow_cost(result)

            # Format response for Claude Code
            return self.format_success_response(result, cost_info)

        except Exception as e:
            return self.format_error_response(workflow_id, e)

        finally:
            # Clean up tracking
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]

    def parse_research_request(
        self,
        user_input: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Parse user input into structured request
        """
        request = {
            "type": "weekly_commentary",
            "regions": ["EM_Asia", "US"],
            "markets": ["fx", "rates"],
            "date_range": self.calculate_default_date_range(),
            "output_format": "50_80_word_summaries"
        }

        # Parse user input for specific requirements
        if "asia" in user_input.lower():
            request["regions"] = ["EM_Asia"]
        if "us" in user_input.lower() and "asia" not in user_input.lower():
            request["regions"] = ["US"]
        if "equity" in user_input.lower():
            request["markets"].append("equity")

        # Handle date-specific requests
        date_match = self.extract_date_from_input(user_input)
        if date_match:
            request["date_range"] = self.calculate_date_range_from_date(date_match)

        # Override with explicit parameters
        if parameters:
            request.update(parameters)

        return request
```

### Progress Tracking System
```python
# claude_interface.py - Progress tracking
class ProgressTracker:
    def __init__(self):
        self.callbacks = {}

    def update_progress(self, workflow_id: str, status: Dict[str, Any]) -> None:
        """Update workflow progress and notify user"""
        if workflow_id not in self.active_workflows:
            return

        workflow = self.active_workflows[workflow_id]
        workflow.update(status)

        # Calculate overall progress
        agent_progress = {
            "planning": 0.1,
            "research": 0.6,  # Research takes longest
            "dev": 0.3,
            "pm": 0.1
        }

        total_progress = sum(
            agent_progress.get(agent, 0) * (1.0 if status.get(f"{agent}_complete") else 0.5)
            for agent in agent_progress.keys()
        )

        workflow["progress"] = min(total_progress, 0.95)  # Never show 100% until complete

        # Format user message
        message = self.format_progress_message(workflow_id, workflow)
        self.send_progress_update(message)

    def format_progress_message(self, workflow_id: str, workflow: Dict[str, Any]) -> str:
        """Format progress message for user display"""
        current_agent = workflow["current_agent"]
        progress_pct = int(workflow["progress"] * 100)

        agent_descriptions = {
            "planning": "Loading research plan and validating requirements",
            "research": "Collecting news data from multiple sources",
            "dev": "Generating weekly commentary content",
            "pm": "Validating quality and preparing delivery"
        }

        return (
            f"🔄 Research workflow progress: {progress_pct}%\n"
            f"📍 Current stage: {current_agent.title()} Agent\n"
            f"⚡ {agent_descriptions.get(current_agent, 'Processing...')}"
        )
```

### Cost Tracking Integration
```python
# claude_interface.py - Cost tracking
class CostTracker:
    def __init__(self):
        self.cost_history = []

    def calculate_workflow_cost(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive workflow costs"""
        cost_info = {
            "llm_costs": self.calculate_llm_costs(result),
            "api_costs": self.calculate_api_costs(result),
            "total_cost": 0.0,
            "token_usage": self.extract_token_usage(result),
            "efficiency_score": 0.0
        }

        cost_info["total_cost"] = cost_info["llm_costs"] + cost_info["api_costs"]
        cost_info["efficiency_score"] = self.calculate_efficiency_score(cost_info, result)

        # Store for historical analysis
        self.cost_history.append({
            "timestamp": datetime.utcnow(),
            "workflow_id": result.get("workflow_id"),
            "costs": cost_info
        })

        return cost_info

    def calculate_llm_costs(self, result: Dict[str, Any]) -> float:
        """Calculate LLM API costs (Claude)"""
        performance_metrics = result.get("performance_metrics", {})
        token_usage = performance_metrics.get("total_tokens", 0)

        # Claude Sonnet pricing (approximate)
        input_tokens = performance_metrics.get("input_tokens", token_usage * 0.7)
        output_tokens = performance_metrics.get("output_tokens", token_usage * 0.3)

        cost = (input_tokens * 0.000003) + (output_tokens * 0.000015)  # $3/$15 per 1M tokens
        return round(cost, 4)

    def generate_cost_report(self, workflow_id: str, cost_info: Dict[str, Any]) -> str:
        """Generate user-friendly cost report"""
        return f"""
💰 Workflow Cost Summary
├─ LLM Costs: ${cost_info['llm_costs']:.4f}
├─ API Costs: ${cost_info['api_costs']:.4f}
├─ Total Cost: ${cost_info['total_cost']:.4f}
├─ Tokens Used: {cost_info['token_usage']:,}
└─ Efficiency: {cost_info['efficiency_score']:.1f}/10

📊 Historical Average: ${self.get_average_cost():.4f}
💡 Cost Optimization: {self.get_optimization_tip(cost_info)}
        """
```

## Integration Verification

### IV1: Report Generation Integration
- [ ] Generated reports integrate with existing MADF documentation structure in `docs/` directory
- [ ] Commentary files placed correctly in hedgemonkey project structure
- [ ] File naming follows established conventions
- [ ] Metadata preserved for future reference

### IV2: System Compatibility
- [ ] Report output does not conflict with existing system outputs or analytics files
- [ ] Claude Code command system remains responsive during workflow execution
- [ ] Existing MCP servers and tool analytics continue functioning
- [ ] Memory usage stays within acceptable limits

### IV3: Documentation Standards
- [ ] Generated reports maintain consistent formatting with existing MADF documentation standards
- [ ] Error messages follow Claude Code interface conventions
- [ ] Help text and command documentation integrated with existing system
- [ ] Performance logs compatible with existing analytics structure

## Command Interface Design

### Basic Commands
```bash
# Generate current week commentary
Generate weekly FX research commentary

# Specific region focus
Generate EM Asia FX update for this week

# Custom date range
Generate market commentary for week ending January 27, 2025

# Include additional markets
Generate FX and equity commentary for EM Asia

# Check workflow status
Show research workflow status

# Display cost summary
Show research workflow costs and usage
```

### Advanced Parameters
```python
# Python API for programmatic access
from claude_interface import MADFResearchInterface

interface = MADFResearchInterface()

result = await interface.handle_research_request(
    user_input="Generate weekly commentary",
    parameters={
        "regions": ["CN", "TW", "KR"],  # Specific countries
        "markets": ["fx", "rates"],
        "word_limit": 60,              # Custom word limit
        "include_forward_looking": True,
        "detail_level": "high"
    }
)
```

## Testing Requirements

### Unit Tests
- Test request parsing and validation
- Test progress tracking updates
- Test cost calculation accuracy
- Test error message formatting

### Integration Tests
- Test complete Claude Code to LangGraph integration
- Test file delivery to hedgemonkey project
- Test progress updates during real workflow execution
- Test error handling and recovery workflows

### User Experience Tests
- Test command interface with various user inputs
- Validate progress messages are clear and helpful
- Test cost reporting accuracy and usefulness
- Verify error messages provide actionable guidance


## Testing Status 🧪

- [ ] **TESTED** - Testing pending
  - **Test Results**: TBD
  - **Unit Tests**: TBD
  - **Integration Tests**: TBD
  - **Test Date**: TBD

## Definition of Done

- [ ] All acceptance criteria completed and tested
- [ ] Claude Code interface operational and user-friendly
- [ ] Progress tracking provides meaningful user feedback
- [ ] Cost tracking enables budget awareness
- [ ] Error handling guides users to resolution
- [ ] Integration complete with existing MADF infrastructure
- [ ] Epic 1 MVP fully operational end-to-end

## Risk Mitigation

**Risk**: Claude Code interface becomes unresponsive during long workflows
**Mitigation**: Async execution, progress callbacks, user cancellation options

**Risk**: Cost tracking inaccurate leading to budget overruns
**Mitigation**: Conservative estimates, real-time tracking, user alerts

**Risk**: Error messages too technical for end users
**Mitigation**: User-friendly error translation, clear action items

## Success Criteria

- Seamless Claude Code integration operational
- User can trigger and monitor research workflows easily
- Cost and performance transparency enables informed usage
- Error handling provides clear guidance and recovery options
- Epic 1 MVP demonstrates complete 4-agent system functionality
- Foundation ready for Phase 2 sophistication enhancements