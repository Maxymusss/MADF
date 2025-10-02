# On-Demand Agents

These agents are loaded only when explicitly called to reduce initial context usage.

## Available Agents

### task-orchestrator
- **Purpose**: Coordinates Task Master workflows, analyzes dependencies, deploys parallel executors
- **Usage**: `Task(subagent_type="task-orchestrator", ...)`
- **When to use**: Complex multi-task features, parallel execution coordination

### task-executor
- **Purpose**: Implements and completes specific Task Master tasks
- **Usage**: `Task(subagent_type="task-executor", ...)`
- **When to use**: Specific task implementation after orchestrator planning

### task-checker
- **Purpose**: Verifies tasks marked as 'review' for quality assurance
- **Usage**: `Task(subagent_type="task-checker", ...)`
- **When to use**: QA validation of completed tasks

## Context Savings
- Reduces initial context by ~900 tokens
- Agents loaded only when needed during execution
- Better performance for simple operations