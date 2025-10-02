# Agentic Flow — Personal Use PRD

**Version:** 1.0  
**Date:** October 2, 2025  
**User:** Personal development tool (not mass adoption)  
**Focus:** LangGraph orchestration + LangSmith evaluations/improvements

---

## Executive Summary

Build a **personal agent orchestration framework** by forking three key LangChain components:

1. **LangGraph** - Multi-agent orchestration patterns
2. **LangSmith** - Evaluation, testing, and continuous improvement
3. **LangChain checkpointers** - Persistence layer

All adapted for **Claude Agent SDK** with **MCP integration**. This is for your personal use first—optimized for rapid iteration and self-improvement through LangSmith's evaluation capabilities.

**Key Insight:** LangSmith already handles agent improvement through:
- Dataset collection from production traces
- Evaluation runs (LLM-as-judge, human feedback)
- Prompt optimization experiments
- A/B testing different configurations

---

## 1. What You're Actually Building

### The Three Forks

```
┌─────────────────────────────────────────────────┐
│           Your Personal Framework               │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  LangGraph (Fork)                        │  │
│  │  • StateGraph orchestration              │  │
│  │  • Multi-agent patterns                  │  │
│  │  • Conditional routing                   │  │
│  │  • Remove: LangChain deps                │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  LangSmith (Fork)                        │  │
│  │  • Trace collection                      │  │
│  │  • Dataset creation                      │  │
│  │  • Evaluation runs                       │  │
│  │  • Prompt optimization                   │  │
│  │  • A/B testing                           │  │
│  │  • Remove: LangChain hooks               │  │
│  │  • Add: Claude SDK instrumentation       │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  PostgreSQL Checkpointer (Fork)          │  │
│  │  • State persistence                     │  │
│  │  • Keep: All code                        │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  NEW: MCP Integration                    │  │
│  │  • Graphiti, Serena, Sequential Thinking │  │
│  │  • Your innovation                       │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### Why Fork LangSmith?

**LangSmith provides the self-improvement capabilities:**

1. **Trace Collection**
   - Every execution automatically traced
   - Full input/output capture
   - Token usage, latency, costs

2. **Dataset Creation**
   - Save production traces as test cases
   - Curate edge cases
   - Build evaluation datasets

3. **Evaluation Framework**
   - LLM-as-Judge evaluators
   - Human feedback collection
   - Custom scoring functions
   - Regression detection

4. **Prompt Optimization**
   - Playground for testing variations
   - A/B test different prompts
   - Track performance over versions
   - Automatic prompt improvement

5. **Continuous Improvement**
   - Monitor metrics over time
   - Detect quality degradation
   - Compare configuration changes
   - Optimize based on real usage

---

## 2. Core Architecture

### How The Pieces Fit Together

```python
from agentic_flow import StateGraph, START, END
from agentic_flow.checkpoint.postgres import PostgresSaver
from agentic_flow.langsmith import LangSmithTracer
from agentic_flow.mcp import MCPRegistry

# 1. Setup LangSmith tracing (forked SDK)
tracer = LangSmithTracer(
    project="my-agent-system",
    auto_collect_datasets=True  # Save traces for eval
)

# 2. Setup MCP servers
mcp = MCPRegistry([
    {"name": "graphiti", "command": "npx", "args": ["-y", "@graphiti/mcp-server"]},
    {"name": "serena", "command": "npx", "args": ["-y", "@serena/mcp-server"]},
])

# 3. Build graph with Claude SDK
class CodeReviewAgent(ClaudeGraphNode):
    def __init__(self):
        super().__init__(model="claude-sonnet-4-5-20250929")
    
    def get_tools(self):
        return [
            *mcp.get_claude_tools("serena"),
            # ... custom tools
        ]

builder = StateGraph(AgentState)
builder.add_node("reviewer", CodeReviewAgent())
builder.add_edge(START, "reviewer")
builder.add_edge("reviewer", END)

# 4. Compile with persistence and tracing
graph = builder.compile(
    checkpointer=PostgresSaver(DB_URI),
    tracer=tracer  # Auto-traces to LangSmith
)

# 5. Execute - automatically traced
result = graph.invoke({"pr_url": "..."}, config)

# 6. Evaluate and improve (LangSmith web UI)
# - View trace in LangSmith dashboard
# - Save interesting traces to dataset
# - Run evaluations against dataset
# - Test prompt variations in playground
# - Deploy improved version
```

### Self-Improvement Workflow

**Day-to-Day Usage:**

```
1. Run agents on real tasks
   ↓
2. LangSmith auto-captures traces
   ↓
3. Review traces in web UI
   ↓
4. Save good/bad examples to datasets
   ↓
5. Run evaluations on datasets
   ↓
6. Experiment with improvements in playground
   ↓
7. A/B test new prompts/configs
   ↓
8. Deploy winner
   ↓
(Repeat)
```

**Concrete Example:**

```python
# Week 1: Initial agent
agent = CodeReviewAgent(
    system_prompt="Review code for bugs",
    temperature=0.7
)

# LangSmith captures 100 executions
# You notice: agent misses security issues

# Week 2: Iterate in LangSmith playground
# Test variations:
# - "Review code for bugs and security vulnerabilities"
# - "Review code with focus on security, then bugs"
# - temperature=0.3 vs 0.7

# Run evaluations on saved dataset
evaluator = LLMAsJudge(criteria="security_thoroughness")
results = evaluator.run(dataset="code-reviews-week1")

# Results show: Second prompt + temp=0.3 performs 30% better

# Week 3: Deploy improved agent
agent = CodeReviewAgent(
    system_prompt="Review code with focus on security, then bugs",
    temperature=0.3
)

# Continue monitoring in LangSmith
```

---

## 3. What You're Forking (Detailed)

### Fork 1: LangGraph

**Source:** `github.com/langchain-ai/langgraph`  
**License:** MIT  
**What to keep:** 90%  
**What to modify:** 10% (remove LangChain)

**Changes:**
```python
# Remove these imports
- from langchain_core.messages import BaseMessage
- from langchain_core.runnables import Runnable

# Replace with
+ Message = dict  # {role: str, content: str}
+ # Plain Python functions (no Runnable interface)
```

### Fork 2: LangSmith SDK

**Source:** `github.com/langchain-ai/langsmith-sdk`  
**License:** MIT  
**What to keep:** 80%  
**What to modify:** 20%

**Keep:**
- Trace collection client
- Dataset management
- Evaluation framework
- Feedback collection
- API schemas

**Modify:**
- Remove LangChain-specific instrumentations
- Add Claude Agent SDK hooks
- Add MCP tool tracing

**Example - Before (LangChain):**
```python
# langsmith/run_helpers.py
from langchain_core.tracers import LangChainTracer

def trace_chain(chain, inputs):
    tracer = LangChainTracer()
    # LangChain-specific tracing
```

**Example - After (Your Fork):**
```python
# agentic_flow/langsmith/tracing.py
from anthropic.agents import AgentExecutor

def trace_agent(agent: AgentExecutor, inputs):
    tracer = ClaudeTracer()
    # Claude SDK-specific tracing
```

### Fork 3: PostgreSQL Checkpointer

**Source:** `langgraph-checkpoint-postgres`  
**License:** MIT  
**What to keep:** 100%  
**What to modify:** 0% (just update imports)

---

## 4. Core Features for Personal Use

### Feature 1: Multi-Agent Orchestration (LangGraph)

**What you get:**
- StateGraph for complex workflows
- Conditional routing
- Human-in-the-loop
- Parallel execution
- Subgraphs

**Example - Research Assistant:**
```python
builder = StateGraph(ResearchState)

# Sequential agents
builder.add_node("searcher", SearchAgent())
builder.add_node("analyzer", AnalyzerAgent())
builder.add_node("writer", WriterAgent())

# Conditional routing
def needs_more_sources(state):
    return "searcher" if len(state["sources"]) < 5 else "analyzer"

builder.add_conditional_edges("searcher", needs_more_sources)

# Human approval before writing
builder.add_edge("analyzer", "human_review")
builder.add_edge("human_review", "writer")
```

### Feature 2: Continuous Improvement (LangSmith)

**What you get:**
- Automatic trace collection
- Dataset curation
- Evaluation framework
- Prompt playground
- A/B testing

**Example - Improve Over Time:**

```python
# Month 1: Baseline
# Run 100 code reviews
# LangSmith captures all traces

# Analyze in LangSmith UI
# Find pattern: Agent misses edge cases in async code

# Create dataset from failures
dataset = tracer.create_dataset(
    name="async-code-reviews",
    filter=lambda trace: "async" in trace.inputs["code"] 
                      and trace.outputs["rating"] < 3
)

# Test improved prompt
evaluator = LLMAsJudge(
    criteria=["correctness", "thoroughness", "async_safety"]
)

results = evaluator.evaluate(
    dataset="async-code-reviews",
    experiments=[
        {"prompt": "Original", "temperature": 0.7},
        {"prompt": "Enhanced with async focus", "temperature": 0.7},
        {"prompt": "Enhanced with async focus", "temperature": 0.3},
    ]
)

# Deploy winner
# Month 2: 40% improvement on async code reviews
```

### Feature 3: Full Claude Features (Direct SDK)

**What you get:**
- Thinking blocks for complex reasoning
- Subagents for parallel tasks
- Context compaction
- Prompt caching
- Streaming responses

**Example:**
```python
class DeepAnalysisAgent(ClaudeGraphNode):
    def __init__(self):
        super().__init__(
            model="claude-sonnet-4-5-20250929",
            thinking={"type": "enabled", "budget_tokens": 3000},
            max_tokens=8192
        )
    
    async def __call__(self, state):
        # Thinking blocks automatically used for complex analysis
        # Subagents spawned for parallel sub-tasks
        result = await self.executor.run(...)
        
        return {
            "analysis": result.content,
            "reasoning": result.thinking_blocks  # Access thinking
        }
```

### Feature 4: MCP Integration (Your Addition)

**What you get:**
- Graphiti for knowledge graphs
- Serena for code analysis
- Sequential Thinking for reasoning
- PostgreSQL for data access

**Example - Knowledge Graph Agent:**
```python
class ResearchAgent(ClaudeGraphNode):
    def __init__(self, mcp):
        super().__init__(model="claude-sonnet-4-5-20250929")
        self.mcp = mcp
    
    def get_tools(self):
        return [
            *self.mcp.get_claude_tools("graphiti"),  # Knowledge storage
            *self.mcp.get_claude_tools("sequential_thinking"),  # Reasoning
        ]

# Agent automatically:
# 1. Uses Sequential Thinking for complex analysis
# 2. Stores findings in Graphiti knowledge graph
# 3. Queries graph for related information
# 4. Builds connected knowledge over time
```

---

## 5. Personal Use Workflow

### Setup (One Time)

```bash
# 1. Fork repositories
git clone your-fork/agentic-flow

# 2. Setup environment
createdb agentic_flow
export DATABASE_URL=postgresql://localhost/agentic_flow
export ANTHROPIC_API_KEY=your-key

# 3. Install (your forked code)
cd agentic-flow
pip install -e .

# 4. Initialize
agentic-flow init --with-langsmith

# 5. Start MCP servers (auto-managed)
# Done automatically when you run agents
```

### Daily Development Loop

```python
# 1. Define/update agent
# my_agents/code_reviewer.py

from agentic_flow import StateGraph, ClaudeGraphNode
from agentic_flow.langsmith import traced

@traced(project="code-review")  # Auto-trace to LangSmith
def review_pr(pr_url: str):
    graph = build_code_review_graph()
    result = graph.invoke({"pr_url": pr_url})
    return result

# 2. Run on real tasks
result = review_pr("https://github.com/...")

# 3. Check LangSmith dashboard
# - View full trace
# - See: prompt used, tools called, costs, latency
# - Add feedback (👍 or 👎)

# 4. When you find issues:
# - Save trace to dataset
# - Test improvements in playground
# - Run evaluations
# - Deploy improved version

# 5. Monitor over time
# - LangSmith charts show quality trends
# - Detect regressions
# - Compare different approaches
```

### Weekend: Improve Your Agents

```python
# Saturday: Review week's traces in LangSmith

# 1. Create dataset from best/worst examples
dataset = langsmith.create_dataset(
    name="code-reviews-week",
    description="Week of code reviews with ratings"
)

# Add examples
for trace in langsmith.get_traces(
    project="code-review",
    filter="this_week"
):
    dataset.add_example(
        inputs=trace.inputs,
        outputs=trace.outputs,
        metadata={"rating": trace.feedback_score}
    )

# 2. Define evaluators
evaluators = [
    LLMAsJudge("correctness"),
    LLMAsJudge("thoroughness"),
    LLMAsJudge("actionability"),
    CustomEvaluator("catches_security_issues"),
]

# 3. Test variations
experiments = [
    {"name": "current", "prompt": current_prompt, "temp": 0.7},
    {"name": "detailed", "prompt": detailed_prompt, "temp": 0.7},
    {"name": "detailed-low-temp", "prompt": detailed_prompt, "temp": 0.3},
    {"name": "with-checklist", "prompt": checklist_prompt, "temp": 0.5},
]

results = langsmith.evaluate(
    dataset="code-reviews-week",
    experiments=experiments,
    evaluators=evaluators
)

# 4. Analyze results
# Results show: "with-checklist" + temp=0.5 wins
# - 25% better correctness
# - 40% better security issue detection
# - 10% slower but acceptable

# 5. Deploy winner
# Update your agent code with winning configuration
```

---

## 6. Implementation Plan (For You)

### Week 1-2: Fork & Setup

- [ ] Fork LangGraph repository
- [ ] Fork LangSmith SDK repository  
- [ ] Fork langgraph-checkpoint-postgres
- [ ] Remove LangChain from LangGraph
- [ ] Remove LangChain from LangSmith SDK
- [ ] Add Claude SDK instrumentation
- [ ] Verify tests pass (90%+)

### Week 3-4: MCP Integration

- [ ] Build MCPRegistry
- [ ] Connect Graphiti MCP
- [ ] Connect Serena MCP
- [ ] Connect Sequential Thinking MCP
- [ ] Connect PostgreSQL MCP
- [ ] Test all tools work

### Week 5-6: Personal Agents

- [ ] Build first real agent (code reviewer)
- [ ] Run on real tasks
- [ ] Collect traces in LangSmith
- [ ] Create first dataset
- [ ] Run first evaluations
- [ ] Iterate and improve

### Week 7-8: Refine & Expand

- [ ] Build 2-3 more agents
- [ ] Establish evaluation workflow
- [ ] Document learnings
- [ ] Polish rough edges

**Total: 2 months to fully functional personal system**

---

## 7. Success Criteria (Personal Use)

### Week 8 Goals

✅ **Working System:**
- All 3 forks functional (LangGraph, LangSmith, Checkpointer)
- 0 LangChain dependencies
- 4 MCP servers integrated
- Direct Claude SDK access

✅ **Production Usage:**
- 3+ agents in daily use
- 100+ traces collected
- 2+ datasets curated
- Measurable improvements from evaluations

✅ **Self-Improvement Working:**
- Can run evaluations on datasets
- Can A/B test prompt variations
- Can deploy improved versions
- Quality metrics trending up

### Month 6 Vision

- 10+ specialized agents
- 1,000+ traces collected
- 10+ curated datasets
- Established evaluation workflow
- Agents significantly better than initial versions
- You're confident in your agent development process

---

## 8. Why This Approach Works

### LangSmith Handles the Hard Parts

**You don't need to build:**
- ❌ Custom evaluation framework
- ❌ Dataset management system
- ❌ Prompt optimization engine
- ❌ A/B testing infrastructure
- ❌ Metrics dashboard

**LangSmith provides:**
- ✅ Production-grade evaluation framework
- ✅ Dataset management with tagging/filtering
- ✅ Playground for prompt experiments
- ✅ Built-in evaluators (LLM-as-Judge)
- ✅ Charts and monitoring
- ✅ Feedback collection

### You Focus On

1. **Building agents** for your specific use cases
2. **Curating datasets** from real usage
3. **Defining evaluation criteria** for your domain
4. **Iterating based on data** from LangSmith

### The Flywheel

```
Build Agent
    ↓
Use in Production
    ↓
LangSmith Captures Traces
    ↓
Review & Curate Dataset
    ↓
Run Evaluations
    ↓
Find Improvements
    ↓
Deploy Better Agent
    ↓
(Repeat - Each cycle agent gets better)
```

---

## 9. Technical Details

### LangSmith Fork Specifics

**What to keep from LangSmith SDK:**

```python
# langsmith/client.py - KEEP
class Client:
    def create_dataset(...)
    def create_example(...)
    def read_dataset(...)
    def create_run(...)  # Modify for Claude SDK
    def evaluate(...)

# langsmith/evaluation/ - KEEP ALL
- evaluators.py  # LLM-as-Judge, custom evaluators
- evaluation.py  # Evaluation runner
- criteria.py    # Built-in criteria

# langsmith/schemas.py - KEEP
# All data models

# langsmith/run_helpers.py - MODIFY
# Remove: LangChain tracers
# Add: Claude SDK tracers
```

**What to modify:**

```python
# Before (langsmith/run_helpers.py)
from langchain_core.tracers import LangChainTracer

def traceable(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        tracer = LangChainTracer()
        # ... LangChain-specific logic

# After (agentic_flow/langsmith/tracing.py)
from anthropic.agents import AgentExecutor

def traced(project: str):
    """Decorator to auto-trace Claude agents to LangSmith"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            tracer = ClaudeTracer(project=project)
            
            # Start trace
            run_id = tracer.start_trace(
                name=func.__name__,
                inputs={"args": args, "kwargs": kwargs}
            )
            
            try:
                # Execute
                result = await func(*args, **kwargs)
                
                # End trace
                tracer.end_trace(
                    run_id=run_id,
                    outputs=result,
                    success=True
                )
                
                return result
            except Exception as e:
                tracer.end_trace(
                    run_id=run_id,
                    error=str(e),
                    success=False
                )
                raise
        
        return wrapper
    return decorator
```

### Integration Example

```python
from agentic_flow import StateGraph, ClaudeGraphNode
from agentic_flow.langsmith import traced, create_dataset, evaluate
from agentic_flow.langsmith.evaluators import LLMAsJudge

# Define agent with tracing
@traced(project="research-assistant")
async def research_query(query: str):
    graph = build_research_graph()
    result = await graph.ainvoke({"query": query})
    return result

# Use it
result = await research_query("Explain quantum computing")

# Later: Create dataset from traces
dataset = create_dataset(
    name="research-queries",
    description="Week of research queries"
)

# Add examples from LangSmith traces
for trace in get_traces(project="research-assistant"):
    dataset.add_example(
        inputs={"query": trace.inputs["query"]},
        outputs=trace.outputs,
        metadata={"quality": trace.feedback_score}
    )

# Run evaluations
evaluator = LLMAsJudge(criteria=[
    "accuracy",
    "completeness", 
    "clarity"
])

results = evaluate(
    dataset="research-queries",
    agent=research_query,
    evaluators=[evaluator]
)

# Analyze and improve
print(results.summary())
# Average accuracy: 0.85
# Average completeness: 0.78
# Average clarity: 0.92

# Find weak areas and iterate
```

---

## 10. Conclusion

### What You're Actually Building

1. **Fork LangGraph** - Get proven multi-agent orchestration
2. **Fork LangSmith** - Get production-grade evaluation & improvement
3. **Fork PostgreSQL Checkpointer** - Get persistence
4. **Add MCP Integration** - Get tool ecosystem
5. **Remove LangChain** - Get direct Claude SDK access

### The Result

A **personal agent framework** that:
- Has all of LangGraph's orchestration power
- Has all of LangSmith's improvement capabilities  
- Works directly with Claude Agent SDK (no wrappers)
- Supports full MCP ecosystem
- Lets YOU iterate and improve your agents based on real usage data

### Why This Works for Personal Use

- **Not optimized for others** - Just works for your workflow
- **Fast iteration** - Fork working code, adapt for Claude
- **Data-driven improvement** - LangSmith shows you what works
- **Full Claude features** - Direct SDK = thinking blocks, subagents, MCP
- **Proven patterns** - LangGraph battle-tested at scale

### Next Steps

1. **Week 1:** Fork repos, remove LangChain
2. **Week 2:** Add Claude SDK hooks
3. **Week 3:** MCP integration
4. **Week 4:** Build first agent, start using
5. **Week 5-8:** Iterate based on LangSmith data

By Week 8, you'll have a fully functional personal agent system that improves itself through data-driven evaluation. 🚀