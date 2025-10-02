"""
Log Analyzer - Token-efficient log analysis with <500 tokens per query
Story 1.4 Task 1 Phase 2 - Postgres Analysis Engine

Provides high-level analysis methods that return concise summaries
Perfect for LLM consumption without exceeding token limits
"""

from typing import Dict, Any, List, Optional
from .postgres_manager import PostgresManager


class LogAnalyzer:
    """
    Token-efficient log analyzer for MADF execution traces

    All queries designed to return <500 tokens of text output
    Focuses on aggregated metrics rather than raw event dumps
    """

    def __init__(self, postgres_manager: Optional[PostgresManager] = None):
        """
        Initialize log analyzer

        Args:
            postgres_manager: PostgresManager instance (creates new if None)
        """
        self.pg = postgres_manager or PostgresManager()

    async def initialize(self):
        """Initialize Postgres connection"""
        await self.pg.initialize()

    async def get_session_summary(self, session_id: str) -> str:
        """
        Get concise session summary (<200 tokens)

        Returns human-readable summary of session execution
        """
        stats = await self.pg.get_session_stats(session_id)

        if not stats:
            return f"No data found for session: {session_id}"

        summary = f"""Session: {session_id}
Story: {stats.get('story_id', 'Unknown')}
Duration: {stats.get('total_duration_ms', 0) / 1000:.1f}s
Events: {stats.get('total_events', 0)} total
Agents: {stats.get('agents_used', 0)} used
Tokens: {stats.get('total_tokens', 0)} total
Failures: {stats.get('failures', 0)} errors
Context: {stats.get('avg_context_percent', 0):.1f}% avg
"""
        return summary.strip()

    async def compare_stories(self, story_id_1: str, story_id_2: str) -> str:
        """
        Compare two stories (<300 tokens)

        Returns side-by-side comparison with key metrics
        """
        comparison = await self.pg.get_story_comparison(story_id_1, story_id_2)

        s1 = comparison.get("story_1", {})
        s2 = comparison.get("story_2", {})

        if not s1 and not s2:
            return f"No data found for stories: {story_id_1}, {story_id_2}"

        result = f"""Story Comparison: {story_id_1} vs {story_id_2}

Metric               | {story_id_1:>10} | {story_id_2:>10} | Change
---------------------|------------|------------|--------
Events               | {s1.get('total_events', 0):>10} | {s2.get('total_events', 0):>10} | {self._calc_change(s1.get('total_events', 0), s2.get('total_events', 0))}
Duration (ms)        | {s1.get('total_duration_ms', 0):>10} | {s2.get('total_duration_ms', 0):>10} | {self._calc_change(s1.get('total_duration_ms', 0), s2.get('total_duration_ms', 0))}
Tokens               | {s1.get('total_tokens', 0):>10} | {s2.get('total_tokens', 0):>10} | {self._calc_change(s1.get('total_tokens', 0), s2.get('total_tokens', 0))}
Failures             | {s1.get('failures', 0):>10} | {s2.get('failures', 0):>10} | {self._calc_change(s1.get('failures', 0), s2.get('failures', 0))}
Patterns Detected    | {s1.get('patterns_detected', 0):>10} | {s2.get('patterns_detected', 0):>10} | {self._calc_change(s1.get('patterns_detected', 0), s2.get('patterns_detected', 0))}

Avg Duration/Event   | {s1.get('avg_duration_ms', 0):>10.1f} | {s2.get('avg_duration_ms', 0):>10.1f} | {self._calc_change(s1.get('avg_duration_ms', 0), s2.get('avg_duration_ms', 0))}
Avg Tokens/Event     | {s1.get('avg_tokens', 0):>10.1f} | {s2.get('avg_tokens', 0):>10.1f} | {self._calc_change(s1.get('avg_tokens', 0), s2.get('avg_tokens', 0))}
"""
        return result.strip()

    async def get_top_errors(self, limit: int = 5) -> str:
        """
        Get top recurring errors (<250 tokens)

        Returns most common error patterns with occurrence counts
        """
        patterns = await self.pg.find_error_patterns(min_occurrences=2)

        if not patterns:
            return "No recurring error patterns found."

        result = "Top Recurring Errors:\n\n"
        for i, pattern in enumerate(patterns[:limit], 1):
            result += f"{i}. {pattern['error_message']}\n"
            result += f"   Occurrences: {pattern['occurrence_count']}\n"
            result += f"   Agents: {', '.join(pattern.get('affected_agents', []))}\n"
            result += f"   First: {pattern['first_seen']}\n"
            result += f"   Last: {pattern['last_seen']}\n\n"

        return result.strip()

    async def get_agent_performance(self, agent_name: str) -> str:
        """
        Get agent performance summary (<200 tokens)

        Returns key metrics for specific agent
        """
        query = """
        SELECT
            COUNT(*) as total_actions,
            AVG(duration_ms) as avg_duration_ms,
            SUM(tokens_used) as total_tokens,
            AVG(tokens_used) as avg_tokens,
            COUNT(*) FILTER (WHERE success = false) as failures,
            AVG(confidence_score) as avg_confidence,
            COUNT(DISTINCT session_id) as sessions
        FROM madf_events
        WHERE agent_name = %(agent_name)s
        """

        results = await self.pg.execute_query(query, {"agent_name": agent_name})

        if not results:
            return f"No data found for agent: {agent_name}"

        stats = results[0]
        summary = f"""Agent: {agent_name}
Actions: {stats.get('total_actions', 0)} total
Sessions: {stats.get('sessions', 0)} unique
Avg Duration: {stats.get('avg_duration_ms', 0):.1f}ms
Avg Tokens: {stats.get('avg_tokens', 0):.1f}
Total Tokens: {stats.get('total_tokens', 0)}
Failures: {stats.get('failures', 0)}
Avg Confidence: {stats.get('avg_confidence', 0):.2f}
"""
        return summary.strip()

    async def get_workflow_insights(self, workflow_id: str) -> str:
        """
        Get workflow execution insights (<300 tokens)

        Returns agent transitions, timing, and outcome
        """
        query = """
        SELECT
            event_type,
            agent_name,
            timestamp,
            duration_ms,
            success,
            details
        FROM madf_events
        WHERE workflow_id = %(workflow_id)s
        ORDER BY timestamp
        LIMIT 20
        """

        results = await self.pg.execute_query(query, {"workflow_id": workflow_id})

        if not results:
            return f"No data found for workflow: {workflow_id}"

        summary = f"Workflow: {workflow_id}\n"
        summary += f"Events: {len(results)}\n\n"

        transitions = []
        for event in results:
            if event['event_type'] == 'agent_transition':
                from_agent = event.get('details', {}).get('from_agent', 'unknown')
                to_agent = event.get('details', {}).get('to_agent', 'unknown')
                transitions.append(f"{from_agent} → {to_agent}")

        if transitions:
            summary += "Agent Flow:\n"
            summary += " → ".join(transitions) + "\n\n"

        total_duration = sum(e.get('duration_ms', 0) for e in results)
        failures = sum(1 for e in results if not e.get('success', True))

        summary += f"Total Duration: {total_duration / 1000:.1f}s\n"
        summary += f"Failures: {failures}\n"

        return summary.strip()

    async def get_token_usage_report(self, story_id: str) -> str:
        """
        Get token usage breakdown (<200 tokens)

        Returns token consumption by agent and operation type
        """
        query = """
        SELECT
            agent_name,
            event_type,
            COUNT(*) as event_count,
            SUM(tokens_used) as total_tokens,
            AVG(tokens_used) as avg_tokens
        FROM madf_events
        WHERE story_id = %(story_id)s
          AND tokens_used > 0
        GROUP BY agent_name, event_type
        ORDER BY total_tokens DESC
        LIMIT 10
        """

        results = await self.pg.execute_query(query, {"story_id": story_id})

        if not results:
            return f"No token usage data for story: {story_id}"

        summary = f"Token Usage Report: {story_id}\n\n"
        total_tokens = sum(r['total_tokens'] for r in results)
        summary += f"Total Tokens: {total_tokens}\n\n"
        summary += "Top Consumers:\n"

        for r in results:
            summary += f"  {r['agent_name']:15} | {r['event_type']:15} | {r['total_tokens']:6} tokens ({r['event_count']} events)\n"

        return summary.strip()

    def _calc_change(self, old_val: float, new_val: float) -> str:
        """Calculate percentage change with formatting"""
        if old_val == 0:
            return "+∞" if new_val > 0 else "0%"

        change = ((new_val - old_val) / old_val) * 100
        sign = "+" if change > 0 else ""
        return f"{sign}{change:.1f}%"

    async def close(self):
        """Close Postgres connection"""
        await self.pg.close()
