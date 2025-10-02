# Story 1.9: Context Engineering Infrastructure

As a **multiagent system developer**,
I want **production-ready context management with sliding windows, PostgreSQL persistence, and observability**,
so that **agents maintain optimal context window utilization and provide consistent performance across sessions**.

## Context & Research Foundation

**Context Engineering Definition**: "Building dynamic systems to provide the right information and tools in the right format such that the LLM can plausibly accomplish the task" (LangChain Blog, 2024)

**Research Findings**:
- Optimal context window utilization: 70-85% (not 100%) - arxiv.org/html/2407.19794v2
- Sliding window memory reduces token costs by 40-60% while maintaining quality
- PostgresSaver enables production-grade persistence (used in LangGraph Platform)
- Token usage monitoring critical for optimization and cost control

**Dependencies**: Story 1.1 (Core LangGraph Architecture) must be completed

## Acceptance Criteria

### 1. PostgreSQL Checkpointer (Production Persistence)

**Requirement**: Replace InMemorySaver with PostgresSaver for production-ready checkpointing

**Implementation**:
- Configure PostgresSaver with connection pooling
- Create checkpoint schema in PostgreSQL database
- Enable thread ID management for multi-session support
- Configure checkpoint retention policies (TTL: 30 days default)
- Test checkpoint recovery across service restarts

**Success Metrics**:
- Checkpoint write latency < 100ms (P95)
- Checkpoint read latency < 50ms (P95)
- Zero data loss during service restart
- Support for 100+ concurrent threads

**References**:
- [LangGraph Persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [PostgresSaver Production Setup](https://redis.io/blog/langgraph-redis-build-smarter-ai-agents-with-memory-persistence/)

---

### 2. Sliding Window Memory Management

**Requirement**: Implement automatic message pruning to maintain optimal context window utilization

**Implementation**:
- Add `trim_messages` utility to all agent workflows
- Configure sliding window size: 15 messages (default), configurable per agent
- Preserve system messages and critical tool outputs
- Implement token-based trimming (max 8K tokens per agent step)
- Add message summarization for pruned history (optional)

**Trimming Strategy**:
```yaml
Strategy:
  - Always keep: System messages, last 3 human messages, last 2 AI messages
  - Conditional keep: Tool messages from last 5 steps
  - Summarize: Messages 16+ (if enabled)
  - Hard limit: 8K tokens per agent invocation
```

**Success Metrics**:
- Context window utilization: 70-85% average
- Token cost reduction: 40-60% vs unlimited history
- No quality degradation in agent responses

**References**:
- [LangGraph Message Trimming](https://python.langchain.com/docs/how_to/trim_messages/)
- [Sliding Window Tutorial](https://aiproduct.engineer/tutorials/langgraph-tutorial-message-history-management-with-sliding-windows-unit-12-exercise-3)

---

### 3. Context Window Utilization (CWU) Monitoring

**Requirement**: Track and optimize context window usage per agent and per step

**Metrics to Track**:
1. **Per-Agent CWU**:
   - Tokens used / Max context window (%)
   - Average CWU over 100 runs
   - P50, P95, P99 percentiles

2. **Per-Step CWU**:
   - Input tokens (state + messages)
   - Output tokens (response)
   - Total tokens per step

3. **Cost Metrics**:
   - Total tokens per workflow
   - Estimated cost per agent invocation
   - Cost reduction from trimming

**Implementation**:
- Add CWU tracking to observability.py
- Log CWU metrics to LangSmith
- Create dashboard for CWU visualization
- Alert when CWU > 90% (risk of truncation)

**Success Metrics**:
- CWU tracking for 100% of agent invocations
- Real-time alerts for high CWU
- Historical CWU trends available in LangSmith

**References**:
- [Context Window Utilization Research](https://arxiv.org/html/2407.19794v2)
- [LangChain Token Usage Tracking](https://python.langchain.com/docs/how_to/chat_token_usage_tracking/)

---

### 4. Token Usage Observability

**Requirement**: Comprehensive token tracking for optimization and cost control

**Observability Stack**:
1. **LangSmith Integration**:
   - Track tokens per agent step
   - Track tokens per tool call (MCP servers)
   - Track cumulative workflow tokens

2. **Custom Metrics**:
   - Add token tracking to all agent classes
   - Export metrics to Prometheus (optional)
   - Store aggregated metrics in PostgreSQL

3. **Cost Estimation**:
   - Calculate cost per agent (Claude Sonnet 4: $3/$15 per M tokens)
   - Track MCP tool token costs (Ollama: $0, Claude API: paid)
   - Generate cost reports per workflow

**Implementation**:
```python
# Add to base_agent.py
class BaseAgent:
    async def track_tokens(self, input_tokens: int, output_tokens: int):
        # Log to LangSmith
        self.langsmith_client.track_tokens(...)
        # Update metrics
        self.total_tokens += input_tokens + output_tokens
```

**Success Metrics**:
- 100% of agent invocations tracked
- Cost reports available per workflow
- Token usage trends visible in dashboards

**References**:
- [LangSmith Tracing](https://python.langchain.com/docs/concepts/tracing/)
- [LangChain Callbacks](https://python.langchain.com/docs/concepts/callbacks/)

---

### 5. Context Engineering Evaluation Framework

**Requirement**: A/B testing framework for evaluating context engineering strategies

**Test Scenarios**:
1. **Sliding Window Size**:
   - Test: 10 messages vs 15 messages vs 20 messages
   - Metric: Response quality (human eval) vs token cost

2. **Trimming Strategy**:
   - Test: Token-based vs message-count-based
   - Metric: Context relevance vs performance

3. **Summarization**:
   - Test: With summarization vs without
   - Metric: Information retention vs latency

**Evaluation Metrics**:
- **Quality**: LLM-as-judge scoring (1-5) for response relevance
- **Cost**: Total tokens per workflow
- **Latency**: Time to first token, total response time
- **Accuracy**: Task completion rate (for benchmark tasks)

**Implementation**:
- Create evaluation dataset (20 benchmark tasks)
- Use LangSmith evaluations framework
- Run A/B tests for each strategy
- Document winning strategy in architecture docs

**Success Metrics**:
- 5+ A/B tests completed
- Optimal strategy documented with benchmarks
- Framework reusable for future optimizations

**References**:
- [LangSmith Evaluation](https://python.langchain.com/docs/concepts/evaluation/)
- [Context Engineering for Agents](https://blog.langchain.com/context-engineering-for-agents/)

---

## Implementation Architecture

### Component Updates

#### 1. `src/core/state_models.py`
```python
from pydantic import BaseModel, Field
from typing import List

class AgentState(BaseModel):
    messages: List[BaseMessage] = Field(default_factory=list)
    max_messages: int = 15  # Sliding window size
    max_tokens: int = 8000  # Token limit per step
    token_usage: dict = Field(default_factory=dict)  # Track usage
```

#### 2. `src/core/checkpointing.py` (NEW)
```python
from langgraph.checkpoint.postgres import PostgresSaver

class ProductionCheckpointer:
    def __init__(self, connection_string: str):
        self.saver = PostgresSaver.from_conn_string(connection_string)

    async def get_checkpoint(self, thread_id: str) -> dict:
        # Retrieve checkpoint
        pass

    async def save_checkpoint(self, thread_id: str, state: dict):
        # Save checkpoint
        pass
```

#### 3. `src/core/context_manager.py` (NEW)
```python
from langchain_core.messages import trim_messages

class ContextManager:
    def __init__(self, max_messages: int = 15, max_tokens: int = 8000):
        self.max_messages = max_messages
        self.max_tokens = max_tokens

    async def trim_history(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        return trim_messages(
            messages,
            max_tokens=self.max_tokens,
            strategy="last",
            token_counter=self._count_tokens
        )

    def calculate_cwu(self, messages: List[BaseMessage]) -> float:
        tokens = self._count_tokens(messages)
        return (tokens / self.max_tokens) * 100
```

#### 4. `src/core/observability.py` (MODIFY)
```python
# Add CWU tracking
class ObservabilityManager:
    async def track_cwu(self, agent_name: str, cwu_percentage: float):
        await self.langsmith_client.log_metric(
            metric_name="context_window_utilization",
            value=cwu_percentage,
            tags={"agent": agent_name}
        )

    async def track_token_usage(self, agent_name: str, input_tokens: int, output_tokens: int):
        # Track tokens per agent
        pass
```

---

## Testing Requirements

### Unit Tests

**File**: `tests/test_story_1_9_context_engineering.py`

**Test Cases**:
1. ✅ PostgresSaver initialization and connection
2. ✅ Checkpoint save/retrieve with thread IDs
3. ✅ Checkpoint recovery after simulated restart
4. ✅ Sliding window message trimming (15 message limit)
5. ✅ Token-based trimming (8K token limit)
6. ✅ CWU calculation for various message histories
7. ✅ Token usage tracking per agent
8. ✅ LangSmith metric export
9. ✅ Evaluation framework setup and execution

### Integration Tests

**Test Scenarios**:
1. Multi-agent workflow with checkpointing (Orchestrator → Analyst → Developer)
2. Long conversation (50+ messages) with sliding window trimming
3. Context window utilization monitoring across 100 agent invocations
4. Checkpoint recovery after service restart
5. A/B test comparing 10-message vs 15-message sliding window

---

## Configuration

### Environment Variables

```bash
# PostgreSQL Checkpointer
POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost:5432/madf_checkpoints

# Context Management
SLIDING_WINDOW_SIZE=15
MAX_TOKENS_PER_STEP=8000
CONTEXT_SUMMARIZATION_ENABLED=false

# Observability
LANGSMITH_API_KEY=your_api_key
LANGSMITH_PROJECT=madf-context-engineering
TRACK_TOKEN_USAGE=true
```

### Database Schema

```sql
-- PostgresSaver schema (auto-created by LangGraph)
CREATE TABLE IF NOT EXISTS checkpoints (
    thread_id TEXT NOT NULL,
    checkpoint_id TEXT NOT NULL,
    parent_id TEXT,
    checkpoint JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (thread_id, checkpoint_id)
);

CREATE INDEX idx_checkpoints_thread ON checkpoints(thread_id);
CREATE INDEX idx_checkpoints_created ON checkpoints(created_at);
```

---

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Checkpoint write latency | < 100ms (P95) | LangSmith traces |
| Checkpoint read latency | < 50ms (P95) | LangSmith traces |
| Context window utilization | 70-85% average | Custom metrics |
| Token cost reduction | 40-60% vs baseline | Cost analysis |
| Concurrent threads supported | 100+ | Load testing |
| Zero data loss | 100% uptime | Checkpoint recovery tests |

---

## Success Criteria

The story is complete when:

1. ✅ PostgresSaver configured and operational with < 100ms write latency
2. ✅ Sliding window trimming reduces token usage by 40%+ with no quality loss
3. ✅ CWU monitoring operational with real-time alerts
4. ✅ Token usage tracking integrated with LangSmith
5. ✅ Evaluation framework validates context engineering strategies
6. ✅ All tests passing (unit + integration)
7. ✅ Documentation updated with context engineering best practices

---

## Dependencies

### Prerequisite Stories
- ✅ Story 1.1: Core LangGraph Architecture (provides base checkpointing infrastructure)

### Follow-Up Stories
- Story 1.10: Hybrid Memory Architecture (builds on this foundation)
- Story 1.11: Multi-Source Context Fusion (leverages CWU optimization)

### External Dependencies
- PostgreSQL 14+ (for PostgresSaver)
- LangSmith account (for observability)
- `langgraph` >= 0.2.0 (for PostgresSaver support)
- `langchain-core` >= 0.3.0 (for trim_messages utility)

---

## References & Citations

### Research Papers
1. [Context Window Utilization for RAG](https://arxiv.org/html/2407.19794v2) - 2024
2. [Introducing CWU Hyper-parameter](https://arxiv.org/abs/2407.19794) - 2024

### Documentation
3. [LangGraph Persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/)
4. [LangChain Message Trimming](https://python.langchain.com/docs/how_to/trim_messages/)
5. [LangSmith Tracing](https://python.langchain.com/docs/concepts/tracing/)

### Blog Posts
6. [Context Engineering for Agents](https://blog.langchain.com/context-engineering-for-agents/) - LangChain, 2024
7. [Redis + LangGraph for Persistent Memory](https://redis.io/blog/langgraph-redis-build-smarter-ai-agents-with-memory-persistence/) - 2024

### Tutorials
8. [Sliding Window Memory Management](https://aiproduct.engineer/tutorials/langgraph-tutorial-message-history-management-with-sliding-windows-unit-12-exercise-3)

---

## Status

**Priority**: P0 (Critical - Required for production)

**Estimated Effort**: 3-5 days

**Complexity**: Medium

**Current Status**: 📝 **DRAFT** - Ready for dev team review

---

## Notes

- This story provides the foundation for all context engineering improvements
- Performance targets based on LangGraph Platform production benchmarks
- Evaluation framework enables data-driven optimization decisions
- PostgresSaver migration is breaking change (requires database setup)