# Tool Efficiency Research - Test Plan

**Version**: 2.0 (REVISED - Function-Level Testing)
**Date**: 2025-10-02
**Author**: BMAD PM Agent (John)
**Purpose**: Define function-level comparative test scenarios for ~165 commonly used tools

## Executive Summary

BMAD agents will conduct **function-level comparative testing** (not tool-level) focusing on **~165 commonly used tools** (not all 390+). Tests compare direct Python libraries vs MCP servers vs Claude Code built-in tools across 12 use case categories, measuring latency, token usage, accuracy, cost, and reliability.

**Key Change from v1.0**: Focused scope based on research findings:
- Direct Python Libraries: ~50 methods (PyGithub, tavily, graphiti_core, DSPy, psycopg)
- MCP Servers: ~20-25 tools (Serena, Context7, Filesystem, Obsidian, Chrome DevTools)
- Claude Code Built-in: ~95 tools (Read, Write, Edit, Glob, Grep, Bash, git, gh, etc.)

**Research Sources**:
- [library-analysis/](./library-analysis/) - Direct Python library common methods
- [mcp-analysis/](./mcp-analysis/) - MCP server common tools

## Test Objectives

1. **Function-level comparison** (not tool-level) across alternatives for each use case
2. **Validate performance claims** (e.g., "3x faster" graphiti_core from Story 1.3)
3. **Focus on commonly used operations** (20-25 high-priority tools per category)
4. **Document trade-offs** per function (speed vs accuracy vs cost vs ease of use)
5. **Provide use case recommendations** (when to use which tool)

**Example Function-Level Test**:
- Use Case: "Create GitHub Pull Request"
- Tools: PyGithub.create_pull() vs gh CLI vs GitHub MCP (if available)
- Metrics: Latency, ease of use, type safety, error handling
- Winner: PyGithub (type safety, Python integration) vs gh CLI (scripting)

## Test Scope

### LangGraph Agents Under Test

| Agent | Primary Responsibility | Current Tools | High-Priority Tool Count | Test Scenarios |
|-------|----------------------|---------------|------------------------|----------------|
| Orchestrator | Workflow coordination | PyGithub (18 methods), tavily-python (4 methods) | ~25 methods | 3 scenarios |
| Analyst | Code analysis | Serena MCP (10 tools), Context7 MCP (2 tools) | ~13 tools | 3 scenarios |
| Knowledge | Knowledge graphs | graphiti_core (5 methods), Obsidian MCP (6 tools) | ~11 tools | 3 scenarios |
| Developer | Implementation | Chrome DevTools MCP (6 tools), Claude Code built-in | ~15 tools | 3 scenarios |
| Validator | QA & optimization | DSPy (5 modules), psycopg (15 methods), Sentry MCP (3 tools) | ~23 methods | 3 scenarios |

**Total Test Coverage**: 15 scenarios, ~60 tool comparisons across 12 use case categories

### In Scope

- Function-level comparative tests (GitHub PR creation, file read, semantic search, etc.)
- Commonly used tools only (80% of use cases)
- Use case groupings (file ops, code search, web research, etc.)
- Performance characteristics from research documentation

### Out of Scope

- Uncommon/rarely used tools (eliminated 80% of tool inventory)
- Tool-level comprehensive testing (e.g., all 50+ PyGithub methods)
- Performance tuning of individual tools
- Custom tool development
- Production deployment optimization

## Benchmark Metrics

### 1. Latency Metrics

**Measurements**:
- Time to first response (TTFR)
- Total execution time
- Percentiles: p50, p90, p99

**Thresholds**:
- Excellent: < 100ms
- Good: 100-500ms
- Acceptable: 500-1000ms
- Poor: > 1000ms

**Collection Method**: Python `time.perf_counter()` before/after tool calls

### 2. Token Usage Metrics

**Measurements**:
- Input tokens per operation
- Output tokens per operation
- Total tokens per 1000 operations
- Estimated cost (if API-based)

**Thresholds**:
- Excellent: 0 tokens (direct library)
- Good: < 500 tokens/operation
- Acceptable: 500-2000 tokens/operation
- Poor: > 2000 tokens/operation

**Collection Method**: LangChain token counting, MCP response metadata

### 3. Accuracy Metrics

**Measurements**:
- Task completion rate (%)
- Error rate (%)
- Quality score (1-10, human evaluation for sample)

**Thresholds**:
- Excellent: > 95% completion, < 5% errors
- Good: 85-95% completion, 5-15% errors
- Acceptable: 70-85% completion, 15-30% errors
- Poor: < 70% completion, > 30% errors

**Collection Method**: Automated success/failure detection, manual quality review

### 4. Cost Metrics

**Measurements**:
- API call costs (if applicable)
- Infrastructure costs
- Cost per 1000 operations
- Total cost of ownership

**Thresholds**:
- Excellent: $0 (local/direct)
- Good: < $0.01 per 1000 ops
- Acceptable: $0.01-$0.10 per 1000 ops
- Poor: > $0.10 per 1000 ops

**Collection Method**: API pricing tables, infrastructure cost estimates

### 5. Reliability Metrics

**Measurements**:
- Success rate (%)
- Common error types
- Fallback behavior effectiveness
- Recovery time from failures

**Thresholds**:
- Excellent: > 99% success rate
- Good: 95-99% success rate
- Acceptable: 90-95% success rate
- Poor: < 90% success rate

**Collection Method**: Error tracking, retry logic testing

## Test Scenarios by Agent

### Orchestrator Agent Tests

**Test 1: GitHub Repository Search**
- **Scenario**: Search for 100 repositories using query "python machine learning"
- **Tools**: PyGithub (direct) vs GitHub MCP (via langchain-mcp-adapters)
- **Metrics**: Latency, accuracy (result relevance), cost
- **Success Criteria**: < 5 seconds total, > 90% relevant results
- **Sample Size**: 100 repos across 5 queries (20 each)

**Test 2: Web Research**
- **Scenario**: Execute 10 web search queries on technical topics
- **Tools**: tavily-python (direct) vs Tavily MCP (via langchain-mcp-adapters)
- **Metrics**: Latency, search quality, cost per query
- **Success Criteria**: < 2 seconds per query, > 85% quality score
- **Sample Size**: 10 queries, 3 runs each (30 total)

**Test 3: File Operations**
- **Scenario**: Read 100 text files from project directory
- **Tools**: Python open/read vs Filesystem MCP
- **Metrics**: Latency, success rate, overhead
- **Success Criteria**: < 1 second for 100 files, 100% success rate
- **Sample Size**: 100 files, 3 runs (300 operations)

### Analyst Agent Tests

**Test 1: Semantic Code Search**
- **Scenario**: Find 50 symbols (classes, functions) in MADF codebase
- **Tools**: Serena MCP (direct SDK) vs filesystem grep/ripgrep
- **Metrics**: Accuracy (symbol detection), latency, token usage
- **Success Criteria**: > 95% accuracy, < 2 seconds per search
- **Sample Size**: 50 symbols across agent files

**Test 2: Documentation Retrieval**
- **Scenario**: Retrieve documentation for 20 Python libraries
- **Tools**: Context7 MCP vs web search (DuckDuckGo)
- **Metrics**: Doc quality, latency, cost
- **Success Criteria**: > 90% correct docs, < 3 seconds per library
- **Sample Size**: 20 libraries (langgraph, pydantic, pytest, etc.)

**Test 3: Complex Reasoning**
- **Scenario**: Perform 10 multi-step code analyses
- **Tools**: Sequential Thinking MCP vs manual chain-of-thought prompting
- **Metrics**: Reasoning quality, token usage, latency
- **Success Criteria**: > 85% quality score, comparable or better tokens
- **Sample Size**: 10 analysis tasks

### Knowledge Agent Tests

**Test 1: Knowledge Graph Operations**
- **Scenario**: Store 100 episodes and retrieve 50
- **Tools**: graphiti_core (direct) vs Graphiti MCP
- **Metrics**: Latency, success rate, storage efficiency
- **Success Criteria**: Validate "3x faster" claim, 100% success rate
- **Sample Size**: 100 writes + 50 reads, 3 runs (450 ops)

**Test 2: Note Management**
- **Scenario**: Create, read, update 50 markdown notes
- **Tools**: Obsidian MCP vs Filesystem MCP
- **Metrics**: Latency, feature richness, reliability
- **Success Criteria**: < 500ms per operation, support metadata
- **Sample Size**: 50 notes, full CRUD cycle

**Test 3: Knowledge Retrieval**
- **Scenario**: Execute 20 semantic searches across knowledge base
- **Tools**: Graphiti search vs Obsidian search
- **Metrics**: Relevance (semantic vs keyword), latency
- **Success Criteria**: > 80% relevant results, < 2 seconds per search
- **Sample Size**: 20 queries, 3 runs (60 searches)

### Developer Agent Tests

**Test 1: Browser Automation**
- **Scenario**: Launch browser and navigate to 20 URLs
- **Tools**: Chrome DevTools MCP vs Playwright MCP
- **Metrics**: Reliability, latency, feature availability
- **Success Criteria**: > 95% success rate, < 3 seconds per page load
- **Sample Size**: 20 URLs, 3 runs (60 navigations)

**Test 2: DOM Inspection**
- **Scenario**: Take 30 page snapshots and analyze DOM
- **Tools**: Chrome DevTools snapshot vs Playwright page content
- **Metrics**: Detail level, performance, usefulness
- **Success Criteria**: Complete DOM tree, < 2 seconds per snapshot
- **Sample Size**: 30 diverse pages (forms, dashboards, etc.)

**Test 3: Console Debugging**
- **Scenario**: Capture console messages from 15 test scenarios
- **Tools**: Chrome DevTools console vs Playwright console
- **Metrics**: Error detection accuracy, message completeness
- **Success Criteria**: 100% error capture, all message types
- **Sample Size**: 15 scenarios with intentional errors

### Validator Agent Tests

**Test 1: Error Tracking**
- **Scenario**: Capture and log 50 intentional errors
- **Tools**: Sentry MCP vs custom Python logging
- **Metrics**: Error detail, aggregation quality, latency
- **Success Criteria**: Complete stack traces, < 100ms overhead
- **Sample Size**: 50 errors across 10 error types

**Test 2: Database Query Optimization**
- **Scenario**: Analyze 20 Postgres queries for optimization
- **Tools**: Postgres MCP Pro vs direct psycopg + EXPLAIN
- **Metrics**: Analysis depth, recommendations quality, latency
- **Success Criteria**: Actionable recommendations, < 5 seconds per query
- **Sample Size**: 20 queries of varying complexity

**Test 3: Test Optimization**
- **Scenario**: Optimize 10 test suites using DSPy
- **Tools**: DSPy optimize() vs manual refinement
- **Metrics**: Improvement rate, automation level, time saved
- **Success Criteria**: > 10% improvement, < 50% manual effort
- **Sample Size**: 10 test suites from existing codebase

## Test Execution Plan

### Phase 1: Setup (1 hour)
1. BMAD Dev creates test infrastructure
2. Install required dependencies (all MCP servers, libraries)
3. Verify environment configuration
4. Create test data fixtures

### Phase 2: Orchestrator Tests (1 hour)
1. Run GitHub search tests (30 min)
2. Run web research tests (20 min)
3. Run file operation tests (10 min)

### Phase 3: Analyst Tests (1.5 hours)
1. Run semantic code search tests (40 min)
2. Run documentation retrieval tests (30 min)
3. Run complex reasoning tests (20 min)

### Phase 4: Knowledge Tests (1.5 hours)
1. Run knowledge graph tests (45 min)
2. Run note management tests (30 min)
3. Run knowledge retrieval tests (15 min)

### Phase 5: Developer Tests (1 hour)
1. Run browser automation tests (30 min)
2. Run DOM inspection tests (20 min)
3. Run console debugging tests (10 min)

### Phase 6: Validator Tests (1 hour)
1. Run error tracking tests (20 min)
2. Run database optimization tests (25 min)
3. Run test optimization tests (15 min)

**Total Execution Time**: ~6 hours (includes setup, data collection, breaks)

## Success Criteria

### Overall Success
- [ ] All 15 test scenarios executed successfully (3 per agent)
- [ ] Quantitative data collected for all 5 metrics
- [ ] Minimum 30 data points per test scenario
- [ ] Results reproducible across 3 runs
- [ ] No test infrastructure failures

### Data Quality
- [ ] < 5% variance between test runs
- [ ] Complete metric coverage (no missing data)
- [ ] Human quality validation on 20% sample
- [ ] Documented edge cases and anomalies

### Deliverables
- [ ] Raw test results (JSON/CSV)
- [ ] Aggregated metrics per tool
- [ ] Comparative analysis tables
- [ ] Performance visualization charts

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| MCP server unavailable | Medium | High | Test direct library fallback, document workarounds |
| Inconsistent test results | Medium | Medium | Run 3+ iterations, calculate variance |
| Tool integration issues | High | Medium | Allocate buffer time, document failures |
| Insufficient test data | Low | High | Prepare diverse test fixtures upfront |
| API rate limits | Medium | Low | Use test accounts, implement backoff |

## Test Data Requirements

### Fixtures Needed
- 100 markdown files (various sizes)
- 20 Python library names
- 50 code symbols (classes, functions)
- 20 web URLs (technical content)
- 100 knowledge graph episodes
- 50 markdown notes
- 20 Postgres queries
- 50 error scenarios

### Environment Setup
- Neo4j database (for Graphiti)
- Postgres database (for optimization tests)
- MCP servers configured and running
- API keys: GITHUB_TOKEN, TAVILY_API_KEY, ANTHROPIC_API_KEY
- Browser installed (Chrome for DevTools tests)

## Reporting Requirements

### Raw Data Format
```json
{
  "test_id": "orchestrator_github_search_001",
  "agent": "orchestrator",
  "tool": "PyGithub",
  "scenario": "github_repo_search",
  "timestamp": "2025-10-02T10:30:00Z",
  "metrics": {
    "latency_ms": 234,
    "tokens_input": 0,
    "tokens_output": 0,
    "accuracy_pct": 92,
    "cost_usd": 0,
    "success": true
  },
  "run_number": 1
}
```

### Aggregated Report Format
```markdown
## Orchestrator Agent - GitHub Search

**Tools Compared**: PyGithub vs GitHub MCP

| Metric | PyGithub | GitHub MCP | Winner |
|--------|----------|------------|--------|
| Latency (p50) | 234ms | 567ms | PyGithub |
| Tokens/op | 0 | 1234 | PyGithub |
| Accuracy | 92% | 89% | PyGithub |
| Cost/1000 ops | $0 | $0.23 | PyGithub |
| Success Rate | 98% | 94% | PyGithub |

**Recommendation**: Use PyGithub for GitHub operations (3x faster, 0 cost)
```

## Next Steps

1. **Dev Agent**: Implement test infrastructure based on this plan
2. **Dev Agent**: Execute all tests, collect results
3. **QA Agent**: Validate results, verify test coverage
4. **PM Agent**: Analyze findings, create recommendations
5. **PM Agent**: Document implementation guide for LangGraph agents

## Approval

**PM Agent**: Ready for Dev implementation
**Target Start**: Immediate
**Expected Completion**: 6-8 hours total execution time
