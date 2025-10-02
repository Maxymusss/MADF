"""Benchmark framework for Story 1.8 tool efficiency research

This module provides benchmarking utilities for comparing direct Python libraries,
MCP servers, and Claude Code built-in tools across ~165 commonly used operations.
"""

import time
import json
from typing import Callable, Any, Dict, List
from pathlib import Path


class ToolBenchmark:
    """Benchmark individual tool operations

    Measures latency, success rate, and collects statistics for a single tool.

    Example:
        >>> benchmark = ToolBenchmark("pygithub.get_repo", "github")
        >>> result = benchmark.measure(github.get_repo, "owner/repo")
        >>> stats = benchmark.get_stats()
    """

    def __init__(self, tool_name: str, category: str):
        """Initialize benchmark for a tool

        Args:
            tool_name: Identifier for the tool being benchmarked
            category: Category (e.g., 'github', 'search', 'database')
        """
        self.tool_name = tool_name
        self.category = category
        self.measurements: List[Dict] = []

    def measure(self, operation: Callable, *args, **kwargs) -> Any:
        """Measure single operation execution

        Args:
            operation: Callable to benchmark
            *args: Positional arguments for operation
            **kwargs: Keyword arguments for operation

        Returns:
            Result from operation (if successful)
        """
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
        """Measure batch operations with multiple runs

        Args:
            operation: Callable to benchmark
            inputs: List of input arguments (each can be tuple for multiple args)
            runs: Number of times to repeat the batch (default: 3)

        Returns:
            List of results from all operations
        """
        results = []
        for _ in range(runs):
            for input_data in inputs:
                if isinstance(input_data, (list, tuple)):
                    result = self.measure(operation, *input_data)
                else:
                    result = self.measure(operation, input_data)
                results.append(result)
        return results

    def get_stats(self) -> Dict:
        """Calculate statistics from measurements

        Returns:
            Dictionary with aggregated statistics:
            - total_runs: Number of measurements
            - success_rate: Percentage of successful operations
            - latency_p50/p90/p99: Percentile latencies in ms
            - latency_mean/min/max: Aggregate latencies in ms
        """
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
        """Calculate percentile from sorted data

        Args:
            data: List of numeric values
            percentile: Percentile to calculate (0-100)

        Returns:
            Percentile value
        """
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


class ComparisonRunner:
    """Run A/B comparisons between multiple tools

    Manages multiple ToolBenchmark instances to compare alternatives
    for the same operation (e.g., PyGithub vs gh CLI).

    Example:
        >>> runner = ComparisonRunner("github_repo_access")
        >>> pygithub = runner.add_tool("pygithub", "library")
        >>> gh_cli = runner.add_tool("gh_cli", "cli")
        >>> # Run benchmarks...
        >>> results = runner.compare()
        >>> runner.export_json(Path("results"))
    """

    def __init__(self, comparison_name: str):
        """Initialize comparison runner

        Args:
            comparison_name: Identifier for this comparison
        """
        self.comparison_name = comparison_name
        self.benchmarks: Dict[str, ToolBenchmark] = {}

    def add_tool(self, tool_name: str, category: str) -> ToolBenchmark:
        """Add tool to comparison

        Args:
            tool_name: Identifier for the tool
            category: Category (e.g., 'library', 'cli', 'mcp')

        Returns:
            ToolBenchmark instance for this tool
        """
        benchmark = ToolBenchmark(tool_name, category)
        self.benchmarks[tool_name] = benchmark
        return benchmark

    def compare(self) -> Dict:
        """Generate comparison report

        Returns:
            Dictionary with comparison results:
            - comparison: Name of comparison
            - tools: Stats for each tool
            - winner: Tool with lowest p50 latency
        """
        results = {
            "comparison": self.comparison_name,
            "tools": {},
            "winner": None
        }

        for tool_name, benchmark in self.benchmarks.items():
            results["tools"][tool_name] = benchmark.get_stats()

        # Determine winner based on latency_p50
        if results["tools"]:
            winner = min(
                results["tools"].items(),
                key=lambda x: x[1].get("latency_p50", float('inf'))
            )
            results["winner"] = winner[0]

        return results

    def export_json(self, output_dir: Path):
        """Export comparison results to JSON

        Args:
            output_dir: Directory to write JSON file
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{self.comparison_name}.json"
        with open(output_path, 'w') as f:
            json.dump(self.compare(), f, indent=2)

    def export_csv(self, output_dir: Path):
        """Export comparison results to CSV

        Args:
            output_dir: Directory to write CSV file
        """
        import csv

        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{self.comparison_name}.csv"
        comparison = self.compare()

        with open(output_path, 'w', newline='') as f:
            fieldnames = [
                "tool", "success_rate", "latency_p50", "latency_p90",
                "latency_p99", "latency_mean"
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            for tool_name, stats in comparison["tools"].items():
                row = {"tool": tool_name}
                row.update({k: stats.get(k, 0) for k in fieldnames[1:]})
                writer.writerow(row)
