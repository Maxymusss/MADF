# MADF Logging System Design

## Overview

The Multi-Agent Development Framework (MADF) logging system provides comprehensive, token-efficient tracking of all development activities, errors, and patterns for continuous self-improvement.

## Architecture

```
Application Code
       ↓
┌─────────────────────────────────────┐
│         QuickLogger                 │
│ • Thread-safe JSONL writing        │
│ • Zero-performance-impact capture  │
│ • Auto-context tracking            │
└────────┬─────────────────────┬──────┘
         │                     │
         ▼                     ▼
   JSONL Files              SQLite Index
   (Full Events)            (Analysis)
         │                     │
         ▼                     ▼
   D:\Logs\MADF\          Token-Efficient
   Raw Event Data         Query Results
```

## Quick Start

### Basic Usage
```python
from logger import log_event, log_error, log_tool_call

# Log any event
log_event("planning_complete", "execution", agent="planning_agent")

# Log errors with context
log_error(Exception("Something failed"), {"file": "workflow.py"})

# Log tool usage
log_tool_call("Read", duration_ms=45, tokens_used=120)
```

### MADF Integration
```python
from logger.madf_integration import log_agent_execution, madf_logger

# Automatic agent logging
@log_agent_execution("research_agent")
async def research_task(state):
    return updated_state

# Workflow context
madf_logger.set_workflow_context("workflow_123", "planning_agent")
madf_logger.log_agent_transition("planning", "research", 2048, "plan_complete")
```

## Event Schema

### Universal Event Structure
All events use a single, flexible schema:

```json
{
  "timestamp": "2025-09-23T14:10:23.908242+00:00",
  "event_type": "agent_action",
  "category": "execution",
  "session_id": "story_1.2_20250923_141023",
  "story_id": "1.2",
  "agent_name": "planning_agent",
  "workflow_id": "workflow_123",
  "duration_ms": 101,
  "tokens_used": 120,
  "context_percent": 23.5,
  "success": true,
  // Event-specific details...
}
```

### Event Categories
1. **execution**: Tool calls, agent actions, workflow steps
2. **error**: Exceptions, failures, timeouts, recovery
3. **interaction**: Human prompts, clarifications, approvals
4. **performance**: Bottlenecks, optimizations, resource usage
5. **learning**: Patterns detected, assumptions validated
6. **decision**: Strategy choices, delegations, planning

## Multi-Agent Specific Tracking

### Agent Attribution
Every event tracks:
- `agent_name`: Which agent performed the action
- `workflow_id`: Which workflow the action belongs to
- `session_id`: Unique session identifier

### Agent Handoffs
```python
madf_logger.log_agent_transition(
    from_agent="planning_agent",
    to_agent="research_agent",
    state_size=2048,
    reason="plan_complete_need_research"
)
```

### Human Interactions
```python
madf_logger.log_human_clarification_needed(
    agent="research_agent",
    reason="api_documentation_unclear",
    context={"api": "bloomberg", "endpoint": "/market_data"}
)
```

## Storage Strategy

### Data Lifecycle
| Age | Storage | Format | Location |
|-----|---------|--------|----------|
| 0-7 days | Hot | JSONL | `D:\Logs\MADF\` |
| 1-4 weeks | Warm | SQLite | `D:\Logs\MADF\events.db` |
| 1-3 months | Cold | Compressed | `D:\BT\archive\` |
| >3 months | Frozen | Summary only | `D:\BT\summaries\` |

### File Structure
```
D:\Logs\MADF\
├── story_1.2_20250923.jsonl     # Today's events
├── story_1.2_20250922.jsonl     # Yesterday's events
├── events_index.db              # SQLite for analysis
└── config.json                  # Logger configuration

D:\BT\archive\
├── 2025_week_38.jsonl.gz        # Weekly archives
└── summary_2025_q3.json         # Quarterly summaries
```

## Analysis & Queries

### Token-Efficient Analysis
All analysis queries return <500 tokens:

```python
from logger.analyzer import LogAnalyzer

analyzer = LogAnalyzer()

# Get error summary (< 200 tokens)
errors = analyzer.get_error_summary()
# Returns: [('UnicodeError', 8), ('PathError', 6)]

# Get performance metrics (< 100 tokens)
perf = analyzer.get_performance_metrics()
# Returns: {'avg_duration': 234, 'peak_context': 85.6}
```

### Weekly Revision Process
Every Sunday night:

```python
class WeeklyRevision:
    def run_revision(self):
        # 1. Extract patterns (5 min)
        patterns = self.extract_patterns()

        # 2. Generate insights (2 min)
        insights = self.analyze_week()

        # 3. Create improvements (1 min)
        improvements = self.generate_rules(patterns)

        # 4. Update CLAUDE.md (automated)
        self.apply_improvements(improvements)

        # 5. Archive old data (1 min)
        self.archive_old_events()
```

## Implementation Timeline

### Phase 1: QuickLogger ✅ COMPLETE
- Basic JSONL logging
- MADF integration hooks
- Thread-safe operation
- Ready for Story 1.2

### Phase 2: SQLite Analysis (Week 1)
- Universal event schema
- Token-efficient queries
- Performance analysis
- Error pattern detection

### Phase 3: Weekly Revision (Week 2)
- Automated pattern extraction
- Rule generation
- CLAUDE.md updates
- Archive management

## Integration with MADF Workflow

### Workflow.py Integration
```python
from logger.madf_integration import madf_logger

class WorkflowOrchestrator:
    async def execute_node(self, node_name: str, state: WorkflowState):
        # Auto-log agent context
        madf_logger.set_workflow_context(state.workflow_id, node_name)

        try:
            result = await self.nodes[node_name](state)
            # Success automatically logged by decorator
            return result
        except Exception as e:
            # Error automatically logged
            raise
```

### Agent Decorators
```python
@log_agent_execution("planning_agent")
async def planning_agent(state: WorkflowState):
    # All execution metrics automatically captured:
    # - Start/end times
    # - Success/failure
    # - Duration
    # - Context size
    # - Errors with full stack traces

    return updated_state
```

## Benefits

### For Development
- **Zero overhead**: Logging doesn't slow down development
- **Automatic capture**: No manual documentation needed
- **Full context**: Every error has complete surrounding context
- **Pattern detection**: Automatically find recurring issues

### For Analysis
- **Token efficient**: <500 tokens for any analysis query
- **Weekly insights**: Patterns emerge from weekly data review
- **Self-improvement**: Automatic rule generation and CLAUDE.md updates
- **Trend tracking**: Compare performance across stories

### For Quality
- **Error prevention**: Rules prevent known error patterns
- **Performance optimization**: Bottleneck detection and resolution
- **User experience**: Track clarification needs and frustration points
- **Continuous learning**: Every session improves the system

## Configuration

### config.json
```json
{
  "logging": {
    "base_path": "D:\\Logs\\MADF",
    "current_story": "1.2",
    "thread_safe": true
  },
  "revision": {
    "schedule": "weekly",
    "day": "sunday",
    "auto_run": false
  },
  "analysis": {
    "max_tokens_per_query": 500,
    "batch_size": 1000
  }
}
```

## Success Metrics

### Story 1.2 Goals
- ✅ All errors automatically captured (not manual)
- ✅ Zero performance impact on development
- ⏳ <500 tokens to query any analysis
- ⏳ Weekly revision identifies recurring patterns

### Long-term Goals
- 50% reduction in repeated errors across stories
- 90% of bottlenecks automatically detected
- 80% of user frustrations identified and resolved
- 95% token efficiency improvement for analysis

## Next Steps

1. **This Week**: Use QuickLogger for all Story 1.2 development
2. **Week 1**: Build SQLite analysis layer
3. **Week 2**: Implement weekly revision automation
4. **Week 3**: Compare Story 1.2 vs 1.1 error patterns
5. **Month 1**: Full self-improvement cycle operational

This logging system transforms every development session into a learning opportunity, enabling continuous improvement based on real data rather than assumptions.