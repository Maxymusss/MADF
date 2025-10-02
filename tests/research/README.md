# Story 1.8 Tool Efficiency Research - Test Infrastructure

Test infrastructure for comparing ~165 commonly used tools across direct Python libraries, MCP servers, and Claude Code built-in tools.

## Overview

This directory contains benchmark framework, metrics collection, and agent-specific test files for [Story 1.8: Agent Tool Usage Rules](../../docs/stories/epic-1/story-1-8-agent-tool-usage-rules.md).

**Purpose**: Collect empirical performance data to inform tool selection guidelines.

## Directory Structure

```
tests/research/
├── tool_benchmark.py          # Benchmark framework (ToolBenchmark, ComparisonRunner)
├── metrics.py                 # Metrics collection (Latency, Token, Accuracy, Cost, Reliability)
├── run_all_research.py        # Master test runner
├── test_orchestrator_tools.py # Orchestrator agent tests (~10 tests)
├── test_analyst_tools.py      # Analyst agent tests (~13 tests)
├── test_knowledge_tools.py    # Knowledge agent tests (~11 tests)
├── test_developer_tools.py    # Developer agent tests (~9 tests)
├── test_validator_tools.py    # Validator agent tests (~11 tests)
├── results/                   # Test results (JSON/CSV)
├── fixtures/                  # Test data
└── README.md                  # This file
```

## Quick Start

### Run All Tests

```bash
# Run all agent tests
uv run python tests/research/run_all_research.py

# Results saved to: tests/research/results/summary_<timestamp>.json
```

### Run Agent-Specific Tests

```bash
# Run orchestrator tests only
uv run python tests/research/run_all_research.py --agent orchestrator

# Run analyst tests only
uv run python tests/research/run_all_research.py --agent analyst

# List available tests
uv run python tests/research/run_all_research.py --list
```

### Run Individual Test Files

```bash
# Run pytest directly
uv run python -m pytest tests/research/test_orchestrator_tools.py -v

# Run specific test class
uv run python -m pytest tests/research/test_orchestrator_tools.py::TestOrchestratorGitHubTools -v

# Run specific test function
uv run python -m pytest tests/research/test_orchestrator_tools.py::TestOrchestratorGitHubTools::test_github_get_repo -v
```

## Benchmark Framework

### ToolBenchmark Class

Measures latency, success rate, and statistics for individual tools.

```python
from tests.research.tool_benchmark import ToolBenchmark

# Create benchmark
benchmark = ToolBenchmark("pygithub.get_repo", "github")

# Measure single operation
result = benchmark.measure(github.get_repo, "owner/repo")

# Get statistics
stats = benchmark.get_stats()
# Returns: {latency_p50, latency_p90, latency_p99, success_rate, ...}
```

### ComparisonRunner Class

Runs A/B comparisons between multiple tools.

```python
from tests.research.tool_benchmark import ComparisonRunner
from pathlib import Path

# Create comparison
runner = ComparisonRunner("github_repo_access")

# Add tools
pygithub_bench = runner.add_tool("pygithub", "library")
gh_cli_bench = runner.add_tool("gh_cli", "cli")

# Run benchmarks (your test code here)
# pygithub_bench.measure(github.get_repo, "owner/repo")
# gh_cli_bench.measure(run_gh_cli, "repo view owner/repo")

# Generate comparison
results = runner.compare()
# Returns: {comparison, tools: {pygithub: {...}, gh_cli: {...}}, winner}

# Export results
runner.export_json(Path("tests/research/results"))
runner.export_csv(Path("tests/research/results"))
```

## Metrics Collection

### Available Metrics Classes

1. **LatencyTracker** - Percentile calculations (p50, p90, p99)
2. **TokenTracker** - Token usage and cost estimation
3. **AccuracyScorer** - Precision, recall, F1 score
4. **CostEstimator** - Cost per 1000 operations
5. **ReliabilityTracker** - Success rate and error types

### Example Usage

```python
from tests.research.metrics import LatencyTracker, TokenTracker, AccuracyScorer

# Latency tracking
latency = LatencyTracker()
result = latency.measure(some_function, arg1, arg2)
stats = latency.stats()  # {p50, p90, p99, mean, min, max}

# Token tracking
tokens = TokenTracker(model="gpt-4")
tokens.track(input_tokens=100, output_tokens=50)
cost = tokens.cost()  # Total cost in USD
cost_per_1k = tokens.per_1000_ops(10)  # Cost per 1000 operations

# Accuracy scoring
accuracy = AccuracyScorer()
result = accuracy.score_search(
    retrieved=["doc1", "doc2", "doc3"],
    ground_truth=["doc1", "doc2", "doc4"]
)
# Returns: {precision, recall, f1}
avg_scores = accuracy.average_scores()
```

## Test Files

### Orchestrator Agent Tests
[test_orchestrator_tools.py](test_orchestrator_tools.py)

- GitHub operations: PyGithub vs gh CLI (5 tests)
- Web research: tavily-python vs WebSearch (3 tests)
- File operations: Claude Code vs Serena vs Filesystem MCP (5 tests)

**Total**: ~10 test functions

### Analyst Agent Tests
[test_analyst_tools.py](test_analyst_tools.py)

- Serena MCP semantic search (10 tests)
- Context7 MCP context management (2 tests)
- Sequential Thinking MCP reasoning (1 test)

**Total**: ~13 test functions

### Knowledge Agent Tests
[test_knowledge_tools.py](test_knowledge_tools.py)

- graphiti_core direct library (5 tests)
- Obsidian MCP markdown knowledge base (6 tests)
- Knowledge retrieval comparison (4 tests)

**Total**: ~11 test functions

### Developer Agent Tests
[test_developer_tools.py](test_developer_tools.py)

- Chrome DevTools MCP browser automation (6 tests)
- File operations for code generation (3 tests)
- Debugging and inspection (3 tests)

**Total**: ~9 test functions

### Validator Agent Tests
[test_validator_tools.py](test_validator_tools.py)

- DSPy modules self-improvement (5 tests)
- psycopg direct library Postgres operations (15 tests)
- Sentry MCP error tracking (3 tests)

**Total**: ~11 test functions

## Environment Setup

### Required Dependencies

```bash
# Install Python dependencies
uv sync

# Required packages (already in pyproject.toml):
# - numpy (for percentile calculations)
# - pytest (for test execution)
```

### Required Environment Variables

```bash
# GitHub API
export GITHUB_TOKEN="ghp_..."

# Tavily API
export TAVILY_API_KEY="tvly-..."

# Anthropic API (for WebSearch)
export ANTHROPIC_API_KEY="sk-ant-..."

# Postgres connection (for psycopg tests)
export POSTGRES_CONNECTION_STRING="postgresql://user:pass@localhost:5432/madf"

# Neo4j connection (for Graphiti tests)
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"
```

### Required Services

1. **Neo4j database** (for Graphiti tests)
   ```bash
   docker run -d -p 7687:7687 -p 7474:7474 \
     -e NEO4J_AUTH=neo4j/password \
     neo4j:5.15
   ```

2. **Postgres database** (for psycopg tests)
   ```bash
   docker run -d -p 5432:5432 \
     -e POSTGRES_PASSWORD=password \
     -e POSTGRES_DB=madf \
     postgres:16
   ```

3. **MCP servers** (configured in `.claude/mcp-servers.json`)
   - Serena (semantic code search)
   - Context7 (context management)
   - Sequential Thinking (reasoning)
   - Obsidian (markdown knowledge base)
   - Filesystem (file operations)
   - Chrome DevTools (browser automation)
   - Sentry (error tracking)

## Results Format

### JSON Output

Results are saved to `tests/research/results/<comparison_name>.json`:

```json
{
  "comparison": "github_repo_access",
  "tools": {
    "pygithub": {
      "tool": "pygithub",
      "category": "library",
      "total_runs": 10,
      "success_rate": 1.0,
      "latency_p50": 245.3,
      "latency_p90": 312.7,
      "latency_p99": 389.2,
      "latency_mean": 258.4,
      "latency_min": 198.1,
      "latency_max": 389.2
    },
    "gh_cli": {
      "tool": "gh_cli",
      "category": "cli",
      "total_runs": 10,
      "success_rate": 1.0,
      "latency_p50": 512.8,
      "latency_p90": 623.4,
      "latency_p99": 701.2,
      "latency_mean": 534.6,
      "latency_min": 445.3,
      "latency_max": 701.2
    }
  },
  "winner": "pygithub"
}
```

### CSV Output

Results are also saved to `tests/research/results/<comparison_name>.csv`:

```csv
tool,success_rate,latency_p50,latency_p90,latency_p99,latency_mean
pygithub,1.0,245.3,312.7,389.2,258.4
gh_cli,1.0,512.8,623.4,701.2,534.6
```

## Next Steps

### Story 1.8.1 Status

✅ **Infrastructure Complete** (this story)
- Benchmark framework implemented
- Metrics collection implemented
- Test scaffolding created (~54 test functions)
- Master test runner implemented

### Story 1.8 Phase 2 (Next)

🔲 **Implement Test Logic**
- Fill in TODO sections in test files
- Execute benchmarks
- Collect real performance data

### Story 1.8 Phase 3 (Final)

🔲 **Analyze Results**
- Generate tool selection recommendations
- Update `.bmad-core/rules/tool-selection-guide.md`
- Create performance comparison reports

## Related Documents

- [Story 1.8: Agent Tool Usage Rules](../../docs/stories/epic-1/story-1-8-agent-tool-usage-rules.md) - Parent story
- [Story 1.8.1: Test Infrastructure Implementation](../../docs/stories/epic-1/story-1-8-1-test-infrastructure-implementation.md) - This story
- [test-plan.md](../../docs/research/test-plan.md) - Test scenarios and metrics
- [library-analysis/](../../docs/research/library-analysis/) - Direct library research
- [mcp-analysis/mcp-servers-common-tools.md](../../docs/research/mcp-analysis/mcp-servers-common-tools.md) - MCP tool research

## Contributing

When adding new test implementations:

1. Follow existing test patterns in scaffolding
2. Use `ToolBenchmark` and `ComparisonRunner` classes
3. Measure all relevant metrics (latency, accuracy, cost, reliability)
4. Export results to JSON/CSV
5. Add docstrings explaining test purpose and metrics

## Support

For questions or issues:
- Review test scaffolding comments (TODO sections)
- Check [test-plan.md](../../docs/research/test-plan.md) for methodology
- See [Story 1.8](../../docs/stories/epic-1/story-1-8-agent-tool-usage-rules.md) for context
