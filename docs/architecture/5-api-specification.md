# 5. API Specification

Based on the file-based messaging architecture, this section defines the "API" as the file system message protocol between agents.

## File-Based Message Protocol

**Message Directory Structure:**
```yaml
messages/
├── inbox/                      # Incoming messages for agents
│   ├── pm-agent/              # PM Agent inbox
│   ├── research-agent-1/      # Research Agent 1 inbox
│   ├── research-agent-2/      # Research Agent 2 inbox
│   └── validator-agent/       # Validator inbox
├── outbox/                    # Processed messages (archive)
│   └── {date}/               # Daily archives
├── broadcast/                 # Broadcast messages to all agents
└── dead-letter/              # Failed messages for retry
```

**Message File Format:**
```yaml
# Filename: {timestamp}_{from_agent}_{to_agent}_{message_id}.json
# Example: 20250921_143022_pm-agent_research-agent-1_uuid123.json
```

## Message Type Specifications

**Task Assignment Message:**
```python
class TaskAssignmentMessage(BaseModel):
    message_id: str
    timestamp: datetime
    from_agent: Literal["pm-agent"]
    to_agent: str  # Target research or validator agent
    message_type: Literal["task_assignment"]
    priority: int = Field(ge=1, le=5)
    correlation_id: Optional[str] = None
    payload: TaskAssignment
```

**Research Result Message:**
```python
class ResearchResultMessage(BaseModel):
    message_id: str
    timestamp: datetime
    from_agent: str  # Research agent ID
    to_agent: Literal["pm-agent"]
    message_type: Literal["result"]
    priority: int = Field(ge=1, le=5)
    correlation_id: str  # References original task
    payload: ResearchResult
```

## Message Flow Sequences

```mermaid
sequenceDiagram
    participant PM as PM Agent
    participant FS as File System
    participant R1 as Research Agent 1
    participant R2 as Research Agent 2
    participant V as Validator Agent

    PM->>FS: Write task_assignment to R1 inbox
    PM->>FS: Write task_assignment to R2 inbox

    R1->>FS: Poll inbox
    FS->>R1: Read task_assignment
    R1->>R1: Execute research with MCP tools
    R1->>FS: Write result to PM inbox

    R2->>FS: Poll inbox
    FS->>R2: Read task_assignment
    R2->>R2: Execute research with MCP tools
    R2->>FS: Write result to PM inbox

    PM->>FS: Poll inbox for results
    FS->>PM: Read R1 result
    FS->>PM: Read R2 result

    PM->>FS: Write validation task to V inbox
    V->>FS: Poll inbox
    FS->>V: Read validation task
    V->>V: Validate with Reuters MCP
    V->>FS: Write validation result to PM inbox

    PM->>FS: Poll inbox
    FS->>PM: Read validation result
    PM->>PM: Compile final report
```
