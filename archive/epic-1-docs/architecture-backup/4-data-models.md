# 4. Data Models

Define the core data models/entities that will be shared between frontend and backend for agent communication and coordination.

## AgentMessage

**Purpose:** Core message format for all inter-agent communication via file system

**Key Attributes:**
- `message_id`: str (UUID) - Unique message identifier
- `timestamp`: datetime - ISO 8601 timestamp with timezone
- `from_agent`: str - Sending agent identifier
- `to_agent`: str - Target agent identifier or "broadcast"
- `message_type`: str - "task_assignment", "result", "error", "status"
- `payload`: Dict[str, Any] - Message-specific content
- `correlation_id`: Optional[str] - Links related messages
- `priority`: int - Message priority (1-5)

**TypeScript Interface:**
```typescript
interface AgentMessage {
  message_id: string;
  timestamp: string;
  from_agent: string;
  to_agent: string;
  message_type: "task_assignment" | "result" | "error" | "status";
  payload: Record<string, any>;
  correlation_id?: string;
  priority: number;
}
```

**Relationships:**
- Parent of: TaskAssignment, ResearchResult, ValidationResult
- References: AgentError (via correlation_id)

## TaskAssignment

**Purpose:** Specific task assigned by PM Agent to research/validation agents

**Key Attributes:**
- `task_id`: str (UUID) - Unique task identifier
- `task_type`: str - "research_fx", "research_rates", "validate"
- `target_market`: str - "Asia", "G10", specific currency pair
- `time_window`: TimeWindow - Date range for research
- `mcp_tools`: List[str] - Suggested MCP tools to use
- `deadline`: datetime - Task completion deadline
- `retry_count`: int - Number of retry attempts
- `context`: Dict[str, Any] - Additional task context

## ResearchResult

**Purpose:** Research findings from research agents

**Key Attributes:**
- `result_id`: str (UUID) - Unique result identifier
- `task_id`: str - Original task identifier
- `agent_id`: str - Reporting agent identifier
- `market_data`: List[MarketEvent] - Discovered market events
- `sources`: List[DataSource] - MCP tools and queries used
- `confidence_score`: float - 0.0-1.0 confidence in findings
- `processing_time`: float - Seconds taken to complete
- `errors_encountered`: List[str] - Non-fatal errors during research

## MarketEvent

**Purpose:** Individual market event or data point discovered during research

**Key Attributes:**
- `event_type`: str - "fx_movement", "rate_decision", "economic_data"
- `currency_pair`: Optional[str] - e.g., "USD/JPY"
- `central_bank`: Optional[str] - e.g., "BOJ", "Fed"
- `event_date`: datetime - When event occurred
- `description`: str - Event description
- `impact`: str - "high", "medium", "low"
- `source_url`: Optional[str] - Original source link
- `raw_data`: Dict[str, Any] - Original MCP tool response

## ValidationResult

**Purpose:** Validation findings comparing multiple research results

**Key Attributes:**
- `validation_id`: str (UUID) - Unique validation identifier
- `research_results`: List[str] - Result IDs being validated
- `conflicts`: List[ConflictRecord] - Detected conflicts
- `verified_events`: List[str] - Event IDs confirmed valid
- `authoritative_sources`: List[DataSource] - Reuters/AP sources used
- `recommendation`: str - Final recommendation on conflicts

## AgentError

**Purpose:** Standardized error tracking for learning system

**Key Attributes:**
- `error_id`: str (UUID) - Unique error identifier
- `timestamp`: datetime - When error occurred
- `agent_id`: str - Agent that encountered error
- `error_type`: str - Error categorization
- `error_message`: str - Detailed error description
- `mcp_tool`: Optional[str] - Tool that caused error
- `recovery_action`: Optional[str] - How agent recovered
- `impact`: str - "high", "medium", "low"
- `context`: Dict[str, Any] - Task context during error
