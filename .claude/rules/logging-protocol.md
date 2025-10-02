# Development Logging Protocol

**CRITICAL**: ALL development activities MUST be logged using the MADF logging system

## Event Logging Requirements
- **Event Logging**: Use `D:\Logs\MADF\` for real-time event capture via QuickLogger
- **Analysis Storage**: Archive analysis and summaries to `D:\BT\` directory
- **Story Integration**: Every story MUST start with `from logger import log_event, log_error`
- **Token Efficiency**: Use SQLite queries for analysis (target <500 tokens per query)
- **Weekly Revision**: Every Sunday night, run automated pattern analysis and rule generation

## Test Output Storage
**CRITICAL**: ALL test outputs, results, logs, and temporary files MUST be saved to `D:\BT\` directory
- This includes: test reports, execution logs, checkpoint databases, generated files, benchmark results
- Use `D:\BT\madf\` as the base directory for MADF-related test outputs
- Never save test outputs in the project directory to preserve storage space
- Create subdirectories under `D:\BT\madf\` for different test types (unit, integration, performance)

## Story Development Protocol
**MANDATORY**: All stories MUST integrate comprehensive logging from Day 1:

### Story Start Requirements
- **Import logging**: Every story begins with `from logger import log_event, log_error`
- **Context setup**: Initialize `madf_logger.set_workflow_context(workflow_id, agent_name)`
- **Auto-tracking**: Use `@log_agent_execution` decorators for all agent functions
- **Real-time capture**: All development activities automatically logged to `D:\Logs\MADF\`

### During Development
- **Error logging**: All exceptions automatically captured with full context
- **Performance tracking**: Tool calls, agent transitions, and bottlenecks logged
- **Human interaction**: Clarifications and interventions automatically tracked
- **Zero overhead**: Logging runs in background without affecting development speed

## Post-Story Documentation Protocol
**MANDATORY**: After completing each story, create comprehensive lessons learned documentation:

### Error Analysis Documentation
Document all errors encountered with frequency and impact data
- **Location**: `D:\BT\madf\STORY_X.X_LESSONS_LEARNED.md`
- **Content**: Error frequency (% of test runs), absolute count, resolution time, prevention strategies
- **Cumulative Tracking**: Combine current story errors with previous stories for trend analysis
- **Format**: Include occurrence statistics, impact analysis, and cumulative frequency calculations

### Error Classification & Rule Updates
Use cumulative data to classify and propose rule updates
- **High Priority**: Frequency ≥10% OR absolute count >5 across all stories combined
- **Low Priority**: Frequency <10% AND absolute count ≤5 across all stories combined
- **Automatic Rule Addition**: High priority error prevention/resolution rules must be added to CLAUDE.md immediately

### Cumulative Error Tracking
Maintain running totals across all stories
- **Baseline Data**: Save total error count and test runs for each story
- **Combined Frequency**: Calculate `(Story1_errors + Story2_errors) / (Story1_runs + Story2_runs)`
- **Trend Analysis**: Track if error rates are decreasing over time
- **Pattern Recognition**: Add same/similar error counts together across previous and current story, then calculate cumulative frequency for priority classification

### Knowledge Transfer
Ensure lessons learned prevent similar issues in future stories
- **Team Review**: Share findings with development team
- **Rule Integration**: Update CLAUDE.md with approved prevention strategies
- **Success Metrics**: Track error rate reduction between stories

**Purpose**: Systematic learning from each story to reduce error rates and improve development efficiency through cumulative knowledge building.