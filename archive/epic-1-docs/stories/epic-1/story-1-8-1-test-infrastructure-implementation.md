# Story 1.8.1: Test Infrastructure Implementation for Tool Efficiency Research

As a **BMAD Dev agent**,
I want **test infrastructure for function-level comparative testing of ~165 commonly used tools**,
so that **Story 1.8 research can execute benchmarks and collect empirical performance data**.

## Overview

Implement test infrastructure required by [Story 1.8](story-1-8-agent-tool-usage-rules.md) Phase 2 (Test Implementation). Create benchmark framework, metrics collection, and 5 agent-specific test files to compare direct Python libraries vs MCP servers vs Claude Code built-in tools.

**Gap Analysis**: Story 1.8 Phase 2 references `tests/research/tool_benchmark.py` and test files that don't exist yet.

**Scope**: Infrastructure only (framework + test scaffolding), not full test execution.

---

## Objective

**BMAD Dev Agent Tasks**:
1. Create `tests/research/` directory structure
2. Implement benchmark framework (`tool_benchmark.py`)
3. Implement metrics collection (`metrics.py`)
4. Create 5 agent-specific test files with scaffolding
5. Implement master test runner (`run_all_research.py`)

**LangGraph Agents**: No involvement (Story 1.8 is BMAD-driven research)

---

## Current State

### Existing Research Documentation ✅

**Completed by PM Agent (Story 1.8 Task 1.1)**:
- [docs/research/library-analysis/](../../research/library-analysis/) - 5 files
  - [pygithub-common-methods.md](../../research/library-analysis/pygithub-common-methods.md) (20-25 methods)
  - [tavily-python-common-methods.md](../../research/library-analysis/tavily-python-common-methods.md) (4 methods)
  - [graphiti-core-common-methods.md](../../research/library-analysis/graphiti-core-common-methods.md) (5 methods)
  - [dspy-common-modules.md](../../research/library-analysis/dspy-common-modules.md) (5 modules)
  - [psycopg-common-methods.md](../../research/library-analysis/psycopg-common-methods.md) (15 methods)
- [docs/research/mcp-analysis/mcp-servers-common-tools.md](../../research/mcp-analysis/mcp-servers-common-tools.md) (20-25 tools)
- [docs/research/test-plan.md](../../research/test-plan.md) - v2.0 (function-level testing)

### Missing Infrastructure ❌

**Not Created Yet**:
- `tests/research/` directory
- `tests/research/tool_benchmark.py` - Benchmark framework
- `tests/research/metrics.py` - Metrics collection classes
- `tests/research/test_orchestrator_tools.py` - Orchestrator tests
- `tests/research/test_analyst_tools.py` - Analyst tests
- `tests/research/test_knowledge_tools.py` - Knowledge tests
- `tests/research/test_developer_tools.py` - Developer tests
- `tests/research/test_validator_tools.py` - Validator tests
- `tests/research/run_all_research.py` - Master test runner
- `tests/research/results/` - Results directory

---

## Task Breakdown

### Task 1: Create Directory Structure (15 minutes)

```bash
# Create directories
mkdir -p tests/research/results
mkdir -p tests/research/fixtures
```

**Deliverables**:
- [ ] `tests/research/` directory
- [ ] `tests/research/results/` subdirectory (for JSON/CSV outputs)
- [ ] `tests/research/fixtures/` subdirectory (for test data)

---

### Task 2: Implement Benchmark Framework (1 hour)

**File**: `tests/research/tool_benchmark.py`

**Requirements**:
- `ToolBenchmark` class - Measure latency, tokens, success rate
- `ComparisonRunner` class - A/B test tools
- Integration with metrics collection
- Results export (JSON/CSV)

**Implementation Pattern**:

```python
import time
import json
from typing import Callable, Any, Dict, List
from pathlib import Path

class ToolBenchmark:
    """Benchmark individual tool operations"""

    def __init__(self, tool_name: str, category: str):
        self.tool_name = tool_name
        self.category = category
        self.measurements: List[Dict] = []

    def measure(self, operation: Callable, *args, **kwargs) -> Any:
        """Measure single operation execution"""
        start = time.perf_counter()
        success = True
        error = None
        result = None

        try:
            result = operation(*args, **kwargs)
        except Exception as e:
            success = False
            error = str(e)

        end = time.perf_counter()
        latency_ms = (end - start) * 1000

        self.measurements.append({
            "latency_ms": latency_ms,
            "success": success,
            "error": error,
            "timestamp": time.time()
        })

        return result

    def measure_batch(self, operation: Callable, inputs: List, runs: int = 3) -> List[Any]:
        """Measure batch operations with multiple runs"""
        results = []
        for _ in range(runs):
            for input_data in inputs:
                result = self.measure(operation, input_data)
                results.append(result)
        return results

    def get_stats(self) -> Dict:
        """Calculate statistics from measurements"""
        if not self.measurements:
            return {}

        latencies = [m["latency_ms"] for m in self.measurements]
        successes = [m["success"] for m in self.measurements]

        return {
            "tool": self.tool_name,
            "category": self.category,
            "total_runs": len(self.measurements),
            "success_rate": sum(successes) / len(successes) if successes else 0,
            "latency_p50": self._percentile(latencies, 50),
            "latency_p90": self._percentile(latencies, 90),
            "latency_p99": self._percentile(latencies, 99),
            "latency_mean": sum(latencies) / len(latencies) if latencies else 0,
            "latency_min": min(latencies) if latencies else 0,
            "latency_max": max(latencies) if latencies else 0,
        }

    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


class ComparisonRunner:
    """Run A/B comparisons between multiple tools"""

    def __init__(self, comparison_name: str):
        self.comparison_name = comparison_name
        self.benchmarks: Dict[str, ToolBenchmark] = {}

    def add_tool(self, tool_name: str, category: str) -> ToolBenchmark:
        """Add tool to comparison"""
        benchmark = ToolBenchmark(tool_name, category)
        self.benchmarks[tool_name] = benchmark
        return benchmark

    def compare(self) -> Dict:
        """Generate comparison report"""
        results = {
            "comparison": self.comparison_name,
            "tools": {},
            "winner": None
        }

        for tool_name, benchmark in self.benchmarks.items():
            results["tools"][tool_name] = benchmark.get_stats()

        # Determine winner based on latency_p50
        if results["tools"]:
            winner = min(results["tools"].items(), key=lambda x: x[1].get("latency_p50", float('inf')))
            results["winner"] = winner[0]

        return results

    def export_json(self, output_dir: Path):
        """Export comparison results to JSON"""
        output_path = output_dir / f"{self.comparison_name}.json"
        with open(output_path, 'w') as f:
            json.dump(self.compare(), f, indent=2)

    def export_csv(self, output_dir: Path):
        """Export comparison results to CSV"""
        import csv

        output_path = output_dir / f"{self.comparison_name}.csv"
        comparison = self.compare()

        with open(output_path, 'w', newline='') as f:
            fieldnames = ["tool", "success_rate", "latency_p50", "latency_p90", "latency_p99", "latency_mean"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            for tool_name, stats in comparison["tools"].items():
                row = {"tool": tool_name}
                row.update({k: stats.get(k, 0) for k in fieldnames[1:]})
                writer.writerow(row)
```

**Deliverables**:
- [ ] `ToolBenchmark` class implemented
- [ ] `ComparisonRunner` class implemented
- [ ] Statistics calculation (p50, p90, p99, mean, min, max)
- [ ] JSON/CSV export functionality
- [ ] Unit tests for benchmark framework

---

### Task 3: Implement Metrics Collection (45 minutes)

**File**: `tests/research/metrics.py`

**Requirements**:
- `LatencyTracker` - Percentile calculations
- `TokenTracker` - Token counting and cost estimation
- `AccuracyScorer` - Precision, recall, F1 score
- `CostEstimator` - Per 1000 operations
- `ReliabilityTracker` - Success rate, error types

**Implementation Pattern** (from [test-plan.md](../../research/test-plan.md)):

```python
import numpy as np
from typing import Dict, List, Optional

class LatencyTracker:
    """Track latency measurements"""

    def __init__(self):
        self.measurements: List[float] = []

    def measure(self, func, *args, **kwargs):
        """Measure function execution time"""
        import time
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        latency = (end - start) * 1000  # milliseconds
        self.measurements.append(latency)
        return result

    def stats(self) -> Dict:
        """Calculate statistics"""
        if not self.measurements:
            return {}
        return {
            "p50": np.percentile(self.measurements, 50),
            "p90": np.percentile(self.measurements, 90),
            "p99": np.percentile(self.measurements, 99),
            "mean": np.mean(self.measurements),
            "min": np.min(self.measurements),
            "max": np.max(self.measurements)
        }


class TokenTracker:
    """Track token usage and estimate costs"""

    def __init__(self, model: str = "gpt-4"):
        self.model = model
        self.input_tokens = 0
        self.output_tokens = 0
        self.pricing = {
            "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015}
        }

    def track(self, input_tokens: int, output_tokens: int):
        """Record token usage"""
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens

    def cost(self) -> float:
        """Calculate total cost"""
        prices = self.pricing.get(self.model, {"input": 0, "output": 0})
        input_cost = (self.input_tokens / 1000) * prices["input"]
        output_cost = (self.output_tokens / 1000) * prices["output"]
        return input_cost + output_cost

    def per_1000_ops(self, operations: int) -> float:
        """Cost per 1000 operations"""
        if operations == 0:
            return 0.0
        avg_cost = self.cost() / operations
        return avg_cost * 1000


class AccuracyScorer:
    """Score search/analysis accuracy"""

    def __init__(self):
        self.results: List[Dict] = []

    def score_search(self, retrieved: List, ground_truth: List) -> Dict:
        """Score search results (precision, recall, F1)"""
        relevant = set(retrieved) & set(ground_truth)
        precision = len(relevant) / len(retrieved) if retrieved else 0
        recall = len(relevant) / len(ground_truth) if ground_truth else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        result = {"precision": precision, "recall": recall, "f1": f1}
        self.results.append(result)
        return result

    def average_scores(self) -> Dict:
        """Average scores across all results"""
        if not self.results:
            return {}
        return {
            "avg_precision": np.mean([r["precision"] for r in self.results]),
            "avg_recall": np.mean([r["recall"] for r in self.results]),
            "avg_f1": np.mean([r["f1"] for r in self.results])
        }


class CostEstimator:
    """Estimate operation costs"""

    def __init__(self):
        self.api_calls = 0
        self.token_tracker = TokenTracker()

    def track_call(self, input_tokens: int = 0, output_tokens: int = 0):
        """Track API call"""
        self.api_calls += 1
        self.token_tracker.track(input_tokens, output_tokens)

    def per_1000_ops(self) -> float:
        """Cost per 1000 operations"""
        return self.token_tracker.per_1000_ops(self.api_calls)


class ReliabilityTracker:
    """Track reliability metrics"""

    def __init__(self):
        self.total = 0
        self.successes = 0
        self.errors: Dict[str, int] = {}

    def track_call(self, success: bool, error_type: Optional[str] = None):
        """Track call result"""
        self.total += 1
        if success:
            self.successes += 1
        elif error_type:
            self.errors[error_type] = self.errors.get(error_type, 0) + 1

    def stats(self) -> Dict:
        """Calculate reliability statistics"""
        return {
            "success_rate": self.successes / self.total if self.total > 0 else 0,
            "error_rate": (self.total - self.successes) / self.total if self.total > 0 else 0,
            "error_types": self.errors,
            "total_calls": self.total
        }
```

**Deliverables**:
- [ ] All 5 metrics classes implemented
- [ ] Unit tests for metrics collection
- [ ] Integration with `ToolBenchmark`

---

### Task 4: Create Agent-Specific Test Files (2 hours)

Create 5 test files with scaffolding (empty test functions with docstrings).

#### 4.1: `test_orchestrator_tools.py`

**Tests** (from Story 1.8 Task 2.2):
1. GitHub operations (5 HIGH priority methods)
2. Web research (3 HIGH priority methods)
3. File operations (Claude Code vs Serena vs Filesystem MCP)

**Scaffolding**:

```python
import pytest
from tests.research.tool_benchmark import ToolBenchmark, ComparisonRunner

class TestOrchestratorGitHubTools:
    """Test GitHub operations: PyGithub vs gh CLI"""

    def test_github_get_repo(self):
        """Compare PyGithub.get_repo() vs gh CLI for repository access"""
        # TODO: Implement PyGithub test
        # TODO: Implement gh CLI test
        # TODO: Compare latency, ease of use
        pass

    def test_github_create_pull_request(self):
        """Compare PyGithub.create_pull() vs gh pr create"""
        # TODO: Implement PyGithub test
        # TODO: Implement gh CLI test
        # TODO: Compare type safety, error handling
        pass

    # Add 3 more tests for list_issues, search_repositories, get_contents


class TestOrchestratorWebResearch:
    """Test web research: tavily-python vs Claude Code WebSearch"""

    def test_web_search_comprehensive(self):
        """Compare tavily.search() vs WebSearch for multi-source research"""
        # TODO: Implement tavily test
        # TODO: Implement WebSearch test
        # TODO: Compare search quality, speed, cost
        pass

    def test_qna_search(self):
        """Test tavily.qna_search() for quick answers"""
        # TODO: Implement test
        pass

    def test_get_search_context(self):
        """Test tavily.get_search_context() for RAG context"""
        # TODO: Implement test
        pass


class TestOrchestratorFileOperations:
    """Test file operations: Claude Code vs Serena vs Filesystem MCP"""

    def test_file_read_performance(self):
        """Compare Read (Claude Code) vs Serena.read_file vs Filesystem.read_text_file"""
        # TODO: Test Claude Code Read tool
        # TODO: Test Serena read_file
        # TODO: Test Filesystem MCP read_text_file
        # TODO: Compare latency, batch operations
        pass

    # Add tests for Write, Edit, Glob, Grep
```

**Deliverables**:
- [ ] `test_orchestrator_tools.py` with 3 test classes, ~10 test functions

#### 4.2: `test_analyst_tools.py`

**Tests** (from Story 1.8 Task 2.3):
1. Serena MCP tool performance (10 HIGH priority tools)
2. Context7 MCP (2 tools)
3. Sequential Thinking MCP (1 tool)

**Scaffolding** (similar pattern to above)

**Deliverables**:
- [ ] `test_analyst_tools.py` with 3 test classes, ~13 test functions

#### 4.3: `test_knowledge_tools.py`

**Tests** (from Story 1.8 Task 2.4):
1. graphiti_core direct library (5 HIGH priority methods)
2. Obsidian MCP (6 commonly used tools)
3. Knowledge retrieval comparison

**Deliverables**:
- [ ] `test_knowledge_tools.py` with 3 test classes, ~11 test functions

#### 4.4: `test_developer_tools.py`

**Tests** (from Story 1.8 Task 2.5):
1. Chrome DevTools MCP (6 commonly used tools)
2. File operations for code generation
3. Debugging and inspection

**Deliverables**:
- [ ] `test_developer_tools.py` with 3 test classes, ~9 test functions

#### 4.5: `test_validator_tools.py`

**Tests** (from Story 1.8 Task 2.6):
1. DSPy modules (5 commonly used)
2. psycopg direct library (15 HIGH priority methods)
3. Sentry MCP (3 commonly used tools)

**Deliverables**:
- [ ] `test_validator_tools.py` with 3 test classes, ~11 test functions

---

### Task 5: Implement Master Test Runner (30 minutes)

**File**: `tests/research/run_all_research.py`

**Requirements**:
- Run all 5 agent test files
- Collect results in `tests/research/results/`
- Generate summary report
- Export JSON/CSV

**Implementation**:

```python
#!/usr/bin/env python3
"""Master test runner for Story 1.8 tool efficiency research"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

def run_all_tests():
    """Run all agent-specific tests"""
    test_files = [
        "tests/research/test_orchestrator_tools.py",
        "tests/research/test_analyst_tools.py",
        "tests/research/test_knowledge_tools.py",
        "tests/research/test_developer_tools.py",
        "tests/research/test_validator_tools.py"
    ]

    results_dir = Path("tests/research/results")
    results_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary = {
        "timestamp": timestamp,
        "test_files": [],
        "total_tests": 0,
        "passed": 0,
        "failed": 0
    }

    for test_file in test_files:
        print(f"\n{'='*80}")
        print(f"Running: {test_file}")
        print('='*80)

        result = subprocess.run(
            ["uv", "run", "python", "-m", "pytest", test_file, "-v", "--tb=short"],
            capture_output=True,
            text=True
        )

        # Parse pytest output (simplified)
        test_result = {
            "file": test_file,
            "exit_code": result.returncode,
            "output": result.stdout
        }
        summary["test_files"].append(test_result)

        if result.returncode == 0:
            summary["passed"] += 1
        else:
            summary["failed"] += 1

    # Export summary
    summary_path = results_dir / f"summary_{timestamp}.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'='*80}")
    print(f"Test Summary:")
    print(f"  Total Test Files: {len(test_files)}")
    print(f"  Passed: {summary['passed']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Results: {summary_path}")
    print('='*80)

if __name__ == "__main__":
    run_all_tests()
```

**Deliverables**:
- [ ] `run_all_research.py` implemented
- [ ] Summary report generation
- [ ] Results export to JSON

---

## Testing Strategy

### Unit Tests

**File**: `tests/research/test_tool_benchmark.py`

Test the test infrastructure:
- [ ] `ToolBenchmark` class functionality
- [ ] `ComparisonRunner` class functionality
- [ ] Metrics calculation accuracy
- [ ] JSON/CSV export

### Integration Tests

Run `run_all_research.py` with minimal test data:
- [ ] All 5 test files execute without errors
- [ ] Results export to `tests/research/results/`
- [ ] Summary report generated

---

## Deliverables

### Test Infrastructure (New Files)

1. **`tests/research/tool_benchmark.py`** - Benchmark framework
   - `ToolBenchmark` class
   - `ComparisonRunner` class
   - Statistics and export functions

2. **`tests/research/metrics.py`** - Metrics collection
   - `LatencyTracker`
   - `TokenTracker`
   - `AccuracyScorer`
   - `CostEstimator`
   - `ReliabilityTracker`

3. **Agent Test Files** (5 files with scaffolding):
   - `test_orchestrator_tools.py` (~10 test functions)
   - `test_analyst_tools.py` (~13 test functions)
   - `test_knowledge_tools.py` (~11 test functions)
   - `test_developer_tools.py` (~9 test functions)
   - `test_validator_tools.py` (~11 test functions)

4. **`tests/research/run_all_research.py`** - Master test runner

5. **`tests/research/results/`** - Results directory (empty initially)

6. **`tests/research/fixtures/`** - Test data directory (empty initially)

---

## Success Criteria

**Infrastructure Complete**:
- [ ] All 9 files created (`tool_benchmark.py`, `metrics.py`, 5 test files, `run_all_research.py`, `README.md`)
- [ ] `ToolBenchmark` and `ComparisonRunner` classes functional
- [ ] All 5 metrics classes implemented
- [ ] Test scaffolding created (~54 test functions across 5 files)
- [ ] Master test runner executes all tests

**Quality**:
- [ ] Unit tests pass for `tool_benchmark.py` and `metrics.py`
- [ ] `run_all_research.py` generates summary report
- [ ] Results export to JSON/CSV

**Documentation**:
- [ ] README.md in `tests/research/` explaining structure
- [ ] Inline docstrings for all classes and functions
- [ ] Example usage in README

---

## Dependencies

**Story Prerequisites**:
- Story 1.8 Task 1.1 ✅ COMPLETE (research documentation)
- Story 1.8 Task 1.2 ✅ COMPLETE (tool options analysis)
- [test-plan.md](../../research/test-plan.md) ✅ CREATED

**Python Dependencies** (add to `pyproject.toml`):
```toml
[tool.uv.dependencies]
numpy = "^2.0.0"  # For percentile calculations
pytest = "^8.0.0"
```

**Environment Setup**:
- Neo4j database (for Graphiti tests)
- Postgres database (for psycopg tests)
- MCP servers configured (for MCP tests)
- API keys: GITHUB_TOKEN, TAVILY_API_KEY, ANTHROPIC_API_KEY

---

## Estimated Effort

**Total**: 4-5 hours (BMAD Dev Agent)

- Task 1: Directory structure (15 min)
- Task 2: Benchmark framework (1 hour)
- Task 3: Metrics collection (45 min)
- Task 4: Agent test files (2 hours)
- Task 5: Master test runner (30 min)
- Testing and debugging (30-45 min)

---

## Notes

### Division of Labor

**BMAD Dev Agent (Story 1.8.1)**:
- Implements test infrastructure (this story)
- Creates test scaffolding
- No full test execution yet

**BMAD Dev Agent (Story 1.8 Phase 2 continuation)**:
- Implements actual test logic in scaffolding
- Executes tests
- Collects benchmark data

**BMAD PM + QA (Story 1.8 Phase 3)**:
- Analyzes test results
- Creates recommendations

### Infrastructure-First Approach

This story creates the **testing skeleton** to unblock Story 1.8 Phase 2. Full test implementation happens in Story 1.8 continuation.

**Why Separate**:
- Infrastructure is reusable across all tests
- Enables parallel work (multiple tests can be implemented simultaneously)
- Clear separation of concerns (framework vs tests)

---

## Follow-up Tasks

1. **Story 1.8 Phase 2 (continuation)**: Implement test logic in scaffolding
2. **Story 1.8 Phase 3**: Execute tests, analyze results
3. **Future**: Continuous benchmarking automation

---

## Related Documents

- [Story 1.8](story-1-8-agent-tool-usage-rules.md) - Parent story
- [test-plan.md](../../research/test-plan.md) - Test scenarios and metrics
- [library-analysis/](../../research/library-analysis/) - Direct library research
- [mcp-analysis/mcp-servers-common-tools.md](../../research/mcp-analysis/mcp-servers-common-tools.md) - MCP tool research
