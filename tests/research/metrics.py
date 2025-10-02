"""Metrics collection for Story 1.8 tool efficiency research

This module provides metrics tracking utilities for latency, token usage,
accuracy, cost estimation, and reliability across tool comparisons.
"""

import numpy as np
import time
from typing import Dict, List, Optional, Callable, Any


class LatencyTracker:
    """Track latency measurements

    Collects timing data and calculates percentile statistics.

    Example:
        >>> tracker = LatencyTracker()
        >>> result = tracker.measure(some_function, arg1, arg2)
        >>> stats = tracker.stats()
        >>> print(stats['p50'])  # Median latency in ms
    """

    def __init__(self):
        """Initialize latency tracker"""
        self.measurements: List[float] = []

    def measure(self, func: Callable, *args, **kwargs) -> Any:
        """Measure function execution time

        Args:
            func: Function to measure
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result from func
        """
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        latency = (end - start) * 1000  # milliseconds
        self.measurements.append(latency)
        return result

    def record(self, latency_ms: float):
        """Record latency measurement directly

        Args:
            latency_ms: Latency in milliseconds
        """
        self.measurements.append(latency_ms)

    def stats(self) -> Dict:
        """Calculate statistics

        Returns:
            Dictionary with percentile and aggregate statistics:
            - p50, p90, p99: Percentile latencies in ms
            - mean, min, max: Aggregate latencies in ms
            - count: Number of measurements
        """
        if not self.measurements:
            return {}
        return {
            "p50": float(np.percentile(self.measurements, 50)),
            "p90": float(np.percentile(self.measurements, 90)),
            "p99": float(np.percentile(self.measurements, 99)),
            "mean": float(np.mean(self.measurements)),
            "min": float(np.min(self.measurements)),
            "max": float(np.max(self.measurements)),
            "count": len(self.measurements)
        }


class TokenTracker:
    """Track token usage and estimate costs

    Calculates costs based on model pricing for input/output tokens.

    Example:
        >>> tracker = TokenTracker(model="gpt-4")
        >>> tracker.track(input_tokens=100, output_tokens=50)
        >>> cost = tracker.cost()
        >>> cost_per_1k = tracker.per_1000_ops(10)
    """

    def __init__(self, model: str = "gpt-4"):
        """Initialize token tracker

        Args:
            model: Model name for pricing (gpt-4, gpt-3.5-turbo, claude-3-sonnet)
        """
        self.model = model
        self.input_tokens = 0
        self.output_tokens = 0
        self.pricing = {
            "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "claude-sonnet-4-5": {"input": 0.003, "output": 0.015}
        }

    def track(self, input_tokens: int, output_tokens: int):
        """Record token usage

        Args:
            input_tokens: Number of input tokens consumed
            output_tokens: Number of output tokens generated
        """
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens

    def cost(self) -> float:
        """Calculate total cost in USD

        Returns:
            Total cost based on accumulated token usage
        """
        prices = self.pricing.get(self.model, {"input": 0, "output": 0})
        input_cost = (self.input_tokens / 1000) * prices["input"]
        output_cost = (self.output_tokens / 1000) * prices["output"]
        return input_cost + output_cost

    def per_1000_ops(self, operations: int) -> float:
        """Calculate cost per 1000 operations

        Args:
            operations: Number of operations executed

        Returns:
            Estimated cost per 1000 operations
        """
        if operations == 0:
            return 0.0
        avg_cost = self.cost() / operations
        return avg_cost * 1000

    def stats(self) -> Dict:
        """Get token usage statistics

        Returns:
            Dictionary with token counts and cost
        """
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.input_tokens + self.output_tokens,
            "cost_usd": self.cost()
        }


class AccuracyScorer:
    """Score search/analysis accuracy

    Calculates precision, recall, and F1 scores for retrieval tasks.

    Example:
        >>> scorer = AccuracyScorer()
        >>> result = scorer.score_search(
        ...     retrieved=["doc1", "doc2", "doc3"],
        ...     ground_truth=["doc1", "doc2", "doc4"]
        ... )
        >>> print(result['f1'])  # F1 score
    """

    def __init__(self):
        """Initialize accuracy scorer"""
        self.results: List[Dict] = []

    def score_search(self, retrieved: List, ground_truth: List) -> Dict:
        """Score search results (precision, recall, F1)

        Args:
            retrieved: List of retrieved items
            ground_truth: List of relevant items (gold standard)

        Returns:
            Dictionary with precision, recall, and F1 score
        """
        relevant = set(retrieved) & set(ground_truth)
        precision = len(relevant) / len(retrieved) if retrieved else 0
        recall = len(relevant) / len(ground_truth) if ground_truth else 0
        f1 = (
            2 * (precision * recall) / (precision + recall)
            if (precision + recall) > 0
            else 0
        )

        result = {"precision": precision, "recall": recall, "f1": f1}
        self.results.append(result)
        return result

    def average_scores(self) -> Dict:
        """Average scores across all results

        Returns:
            Dictionary with average precision, recall, F1
        """
        if not self.results:
            return {}
        return {
            "avg_precision": float(np.mean([r["precision"] for r in self.results])),
            "avg_recall": float(np.mean([r["recall"] for r in self.results])),
            "avg_f1": float(np.mean([r["f1"] for r in self.results]))
        }


class CostEstimator:
    """Estimate operation costs

    Combines API call counting with token tracking for cost estimation.

    Example:
        >>> estimator = CostEstimator(model="gpt-4")
        >>> estimator.track_call(input_tokens=100, output_tokens=50)
        >>> cost_per_1k = estimator.per_1000_ops()
    """

    def __init__(self, model: str = "gpt-4"):
        """Initialize cost estimator

        Args:
            model: Model name for pricing
        """
        self.api_calls = 0
        self.token_tracker = TokenTracker(model=model)

    def track_call(self, input_tokens: int = 0, output_tokens: int = 0):
        """Track API call with token usage

        Args:
            input_tokens: Number of input tokens (default: 0)
            output_tokens: Number of output tokens (default: 0)
        """
        self.api_calls += 1
        self.token_tracker.track(input_tokens, output_tokens)

    def per_1000_ops(self) -> float:
        """Calculate cost per 1000 operations

        Returns:
            Estimated cost per 1000 operations in USD
        """
        return self.token_tracker.per_1000_ops(self.api_calls)

    def stats(self) -> Dict:
        """Get cost estimation statistics

        Returns:
            Dictionary with API calls, token usage, and costs
        """
        token_stats = self.token_tracker.stats()
        return {
            "api_calls": self.api_calls,
            "total_cost_usd": token_stats["cost_usd"],
            "cost_per_1000_ops": self.per_1000_ops(),
            **token_stats
        }


class ReliabilityTracker:
    """Track reliability metrics

    Monitors success rate and error types for tool operations.

    Example:
        >>> tracker = ReliabilityTracker()
        >>> tracker.track_call(success=True)
        >>> tracker.track_call(success=False, error_type="TimeoutError")
        >>> stats = tracker.stats()
        >>> print(stats['success_rate'])
    """

    def __init__(self):
        """Initialize reliability tracker"""
        self.total = 0
        self.successes = 0
        self.errors: Dict[str, int] = {}

    def track_call(self, success: bool, error_type: Optional[str] = None):
        """Track call result

        Args:
            success: Whether operation succeeded
            error_type: Error type if failed (e.g., "TimeoutError")
        """
        self.total += 1
        if success:
            self.successes += 1
        elif error_type:
            self.errors[error_type] = self.errors.get(error_type, 0) + 1

    def stats(self) -> Dict:
        """Calculate reliability statistics

        Returns:
            Dictionary with success rate, error rate, error breakdown
        """
        success_rate = self.successes / self.total if self.total > 0 else 0
        error_rate = (self.total - self.successes) / self.total if self.total > 0 else 0
        return {
            "success_rate": success_rate,
            "error_rate": error_rate,
            "error_types": self.errors,
            "total_calls": self.total,
            "successful_calls": self.successes,
            "failed_calls": self.total - self.successes
        }
