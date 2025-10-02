"""
Pattern Extractor - Error pattern detection and analysis
Story 1.4 Task 1 Phase 2 - Postgres Analysis Engine

Identifies recurring patterns in execution logs for DSPy training
Extracts actionable insights from error patterns
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .postgres_manager import PostgresManager


class PatternExtractor:
    """
    Extract patterns from MADF execution logs for learning and optimization

    Focuses on:
    - Error patterns that can be prevented
    - Performance bottlenecks that can be optimized
    - Successful patterns that can be replicated
    """

    def __init__(self, postgres_manager: Optional[PostgresManager] = None):
        """
        Initialize pattern extractor

        Args:
            postgres_manager: PostgresManager instance (creates new if None)
        """
        self.pg = postgres_manager or PostgresManager()

    async def initialize(self):
        """Initialize Postgres connection"""
        await self.pg.initialize()

    async def find_error_patterns(
        self,
        min_occurrences: int = 3,
        time_window_hours: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Find recurring error patterns

        Args:
            min_occurrences: Minimum times error must occur to be considered a pattern
            time_window_hours: Only consider errors in last N hours (None = all time)

        Returns:
            List of error patterns with metadata
        """
        time_filter = ""
        if time_window_hours:
            cutoff = datetime.now() - timedelta(hours=time_window_hours)
            time_filter = f"AND timestamp >= '{cutoff.isoformat()}'"

        query = f"""
        SELECT
            details->>'error' as error_message,
            details->>'error_type' as error_type,
            COUNT(*) as occurrence_count,
            array_agg(DISTINCT agent_name) as affected_agents,
            array_agg(DISTINCT event_type) as event_types,
            MIN(timestamp) as first_seen,
            MAX(timestamp) as last_seen,
            AVG(duration_ms) as avg_duration_before_error,
            COUNT(DISTINCT session_id) as affected_sessions
        FROM madf_events
        WHERE success = false
          AND details->>'error' IS NOT NULL
          {time_filter}
        GROUP BY details->>'error', details->>'error_type'
        HAVING COUNT(*) >= {min_occurrences}
        ORDER BY occurrence_count DESC
        """

        return await self.pg.execute_query(query)

    async def find_slow_operations(
        self,
        duration_threshold_ms: int = 1000,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find operations that consistently take too long

        Args:
            duration_threshold_ms: Duration threshold in milliseconds
            limit: Maximum patterns to return

        Returns:
            List of slow operation patterns
        """
        query = f"""
        SELECT
            agent_name,
            event_type,
            details->>'action' as action,
            COUNT(*) as occurrence_count,
            AVG(duration_ms) as avg_duration_ms,
            MAX(duration_ms) as max_duration_ms,
            MIN(duration_ms) as min_duration_ms,
            PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_ms) as p95_duration_ms
        FROM madf_events
        WHERE duration_ms >= {duration_threshold_ms}
        GROUP BY agent_name, event_type, details->>'action'
        HAVING COUNT(*) >= 3
        ORDER BY avg_duration_ms DESC
        LIMIT {limit}
        """

        return await self.pg.execute_query(query)

    async def find_success_patterns(
        self,
        min_confidence: float = 0.8,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find patterns associated with successful execution

        Args:
            min_confidence: Minimum confidence score threshold
            limit: Maximum patterns to return

        Returns:
            List of successful execution patterns
        """
        query = f"""
        SELECT
            agent_name,
            event_type,
            COUNT(*) as occurrence_count,
            AVG(confidence_score) as avg_confidence,
            AVG(duration_ms) as avg_duration_ms,
            AVG(tokens_used) as avg_tokens_used,
            AVG(impact_score) as avg_impact_score,
            COUNT(*) FILTER (WHERE success = true) as success_count,
            COUNT(*) FILTER (WHERE success = false) as failure_count
        FROM madf_events
        WHERE confidence_score >= {min_confidence}
          AND success = true
        GROUP BY agent_name, event_type
        HAVING COUNT(*) >= 5
        ORDER BY avg_confidence DESC, occurrence_count DESC
        LIMIT {limit}
        """

        return await self.pg.execute_query(query)

    async def find_agent_handoff_patterns(self) -> List[Dict[str, Any]]:
        """
        Find common agent transition patterns

        Returns:
            List of agent handoff patterns with frequency
        """
        query = """
        SELECT
            details->>'from_agent' as from_agent,
            details->>'to_agent' as to_agent,
            details->>'reason' as reason,
            COUNT(*) as transition_count,
            AVG(duration_ms) as avg_handoff_duration_ms,
            COUNT(*) FILTER (WHERE success = true) as successful_handoffs,
            COUNT(*) FILTER (WHERE success = false) as failed_handoffs
        FROM madf_events
        WHERE event_type = 'agent_transition'
          AND details->>'from_agent' IS NOT NULL
          AND details->>'to_agent' IS NOT NULL
        GROUP BY details->>'from_agent', details->>'to_agent', details->>'reason'
        HAVING COUNT(*) >= 2
        ORDER BY transition_count DESC
        """

        return await self.pg.execute_query(query)

    async def find_token_inefficiency_patterns(
        self,
        high_token_threshold: int = 2000,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find patterns where token usage is inefficient

        Args:
            high_token_threshold: Token count threshold
            limit: Maximum patterns to return

        Returns:
            List of token inefficiency patterns
        """
        query = f"""
        SELECT
            agent_name,
            event_type,
            details->>'tool' as tool_name,
            COUNT(*) as occurrence_count,
            AVG(tokens_used) as avg_tokens,
            AVG(context_percent) as avg_context_percent,
            AVG(duration_ms) as avg_duration_ms,
            AVG(tokens_used / NULLIF(duration_ms, 0)) as tokens_per_ms
        FROM madf_events
        WHERE tokens_used >= {high_token_threshold}
        GROUP BY agent_name, event_type, details->>'tool'
        HAVING COUNT(*) >= 3
        ORDER BY avg_tokens DESC
        LIMIT {limit}
        """

        return await self.pg.execute_query(query)

    async def find_decision_patterns(self) -> List[Dict[str, Any]]:
        """
        Find patterns in decision-making events

        Returns:
            List of decision patterns with outcomes
        """
        query = """
        SELECT
            agent_name,
            details->>'decision_point' as decision_point,
            details->>'choice_made' as choice_made,
            COUNT(*) as decision_count,
            AVG(confidence_score) as avg_confidence,
            COUNT(*) FILTER (WHERE success = true) as successful_outcomes,
            COUNT(*) FILTER (WHERE success = false) as failed_outcomes,
            AVG(duration_ms) as avg_decision_time_ms
        FROM madf_events
        WHERE event_type = 'decision'
          AND details->>'decision_point' IS NOT NULL
        GROUP BY agent_name, details->>'decision_point', details->>'choice_made'
        HAVING COUNT(*) >= 2
        ORDER BY decision_count DESC
        """

        return await self.pg.execute_query(query)

    async def extract_training_examples(
        self,
        pattern_type: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Extract specific examples for DSPy training

        Args:
            pattern_type: Type of pattern to extract (success/failure/slow)
            limit: Maximum examples to return

        Returns:
            List of training examples with full context
        """
        filters = {
            "success": "WHERE success = true AND confidence_score >= 0.8",
            "failure": "WHERE success = false",
            "slow": "WHERE duration_ms > 1000"
        }

        filter_clause = filters.get(pattern_type, "")

        query = f"""
        SELECT
            session_id,
            story_id,
            agent_name,
            event_type,
            timestamp,
            duration_ms,
            tokens_used,
            context_percent,
            success,
            confidence_score,
            details
        FROM madf_events
        {filter_clause}
        ORDER BY timestamp DESC
        LIMIT {limit}
        """

        return await self.pg.execute_query(query)

    async def generate_pattern_report(self) -> str:
        """
        Generate comprehensive pattern analysis report

        Returns:
            Human-readable pattern report (<500 tokens)
        """
        error_patterns = await self.find_error_patterns(min_occurrences=2)
        slow_ops = await self.find_slow_operations(limit=5)
        success_patterns = await self.find_success_patterns(limit=5)

        report = "MADF Pattern Analysis Report\n"
        report += "=" * 50 + "\n\n"

        # Error patterns
        report += f"Error Patterns ({len(error_patterns)} found):\n"
        for i, pattern in enumerate(error_patterns[:5], 1):
            report += f"  {i}. {pattern['error_message']}\n"
            report += f"     Occurrences: {pattern['occurrence_count']}\n"
            report += f"     Agents: {', '.join(pattern.get('affected_agents', []))}\n\n"

        # Slow operations
        report += f"\nSlow Operations ({len(slow_ops)} found):\n"
        for i, op in enumerate(slow_ops[:5], 1):
            report += f"  {i}. {op['agent_name']} - {op['event_type']}\n"
            report += f"     Avg: {op['avg_duration_ms']:.0f}ms, Max: {op['max_duration_ms']:.0f}ms\n\n"

        # Success patterns
        report += f"\nSuccess Patterns ({len(success_patterns)} found):\n"
        for i, pattern in enumerate(success_patterns[:5], 1):
            report += f"  {i}. {pattern['agent_name']} - {pattern['event_type']}\n"
            report += f"     Confidence: {pattern['avg_confidence']:.2f}, Count: {pattern['occurrence_count']}\n\n"

        return report.strip()

    async def close(self):
        """Close Postgres connection"""
        await self.pg.close()
