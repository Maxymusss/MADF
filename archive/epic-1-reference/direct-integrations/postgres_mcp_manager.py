"""
PostgresMCPManager - Postgres MCP Pro integration for MADF logging
Story 1.4 Task 1 Phase 2 - MCP-based approach for comparison

This implementation uses Postgres MCP Pro via mcp_bridge.py
Performance will be compared against direct psycopg3 (postgres_manager.py)
"""

import os
import json
from typing import Optional, Dict, Any, List
from pathlib import Path


class PostgresMCPManager:
    """
    Postgres manager using MCP protocol via mcp_bridge.py

    Comparison approach to direct psycopg3 implementation
    """

    def __init__(self, mcp_bridge=None):
        """
        Initialize Postgres MCP manager

        Args:
            mcp_bridge: MCPBridge instance (will create if None)
        """
        self.mcp_bridge = mcp_bridge
        self._initialized = False

    async def initialize(self):
        """Initialize MCP bridge and create schema"""
        if self._initialized:
            return

        # Lazy import to avoid circular dependency
        if self.mcp_bridge is None:
            from core.mcp_bridge import MCPBridge
            self.mcp_bridge = MCPBridge()

        # Create schema if not exists
        await self.create_schema()
        self._initialized = True

    async def create_schema(self):
        """Create MADF logging events table schema via MCP"""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS madf_events (
            id BIGSERIAL PRIMARY KEY,
            timestamp TIMESTAMPTZ NOT NULL,
            event_type VARCHAR(50) NOT NULL,
            category VARCHAR(50) NOT NULL,
            session_id VARCHAR(100) NOT NULL,
            story_id VARCHAR(20) NOT NULL,
            agent_name VARCHAR(50),
            workflow_id VARCHAR(100),
            thread_id VARCHAR(100),
            trace_id VARCHAR(100),
            duration_ms INTEGER DEFAULT 0,
            tokens_used INTEGER DEFAULT 0,
            context_percent FLOAT DEFAULT 0.0,
            success BOOLEAN DEFAULT TRUE,
            confidence_score FLOAT DEFAULT 0.0,
            impact_score FLOAT DEFAULT 0.0,
            time_saved_or_wasted_ms INTEGER DEFAULT 0,
            user_satisfaction_delta FLOAT DEFAULT 0.0,
            created_rule BOOLEAN DEFAULT FALSE,
            pattern_detected BOOLEAN DEFAULT FALSE,
            needs_review BOOLEAN DEFAULT FALSE,
            details JSONB DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );

        -- Indexes for common queries
        CREATE INDEX IF NOT EXISTS idx_madf_events_timestamp ON madf_events(timestamp);
        CREATE INDEX IF NOT EXISTS idx_madf_events_event_type ON madf_events(event_type);
        CREATE INDEX IF NOT EXISTS idx_madf_events_session_id ON madf_events(session_id);
        CREATE INDEX IF NOT EXISTS idx_madf_events_story_id ON madf_events(story_id);
        CREATE INDEX IF NOT EXISTS idx_madf_events_agent_name ON madf_events(agent_name);
        CREATE INDEX IF NOT EXISTS idx_madf_events_success ON madf_events(success);
        CREATE INDEX IF NOT EXISTS idx_madf_events_details ON madf_events USING gin(details);
        """

        # Execute via MCP
        result = await self.mcp_bridge.call_mcp_tool(
            server_name="postgres",
            tool_name="execute_sql",
            parameters={"query": schema_sql}
        )

        if not result.get("success"):
            raise Exception(f"Failed to create schema: {result.get('error')}")

    async def import_jsonl_file(self, jsonl_path: Path) -> Dict[str, Any]:
        """
        Import JSONL log file to Postgres via MCP

        Args:
            jsonl_path: Path to JSONL file

        Returns:
            Dict with import statistics
        """
        if not self._initialized:
            await self.initialize()

        imported = 0
        errors = 0

        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    event = json.loads(line.strip())

                    # Build INSERT statement
                    insert_sql = """
                    INSERT INTO madf_events (
                        timestamp, event_type, category, session_id, story_id,
                        agent_name, workflow_id, thread_id, trace_id,
                        duration_ms, tokens_used, context_percent, success,
                        confidence_score, impact_score, time_saved_or_wasted_ms,
                        user_satisfaction_delta, created_rule, pattern_detected,
                        needs_review, details
                    ) VALUES (
                        '{timestamp}', '{event_type}', '{category}', '{session_id}',
                        '{story_id}', {agent_name}, {workflow_id}, {thread_id},
                        {trace_id}, {duration_ms}, {tokens_used}, {context_percent},
                        {success}, {confidence_score}, {impact_score},
                        {time_saved_or_wasted_ms}, {user_satisfaction_delta},
                        {created_rule}, {pattern_detected}, {needs_review},
                        '{details}'::jsonb
                    )
                    """.format(
                        timestamp=event.get("timestamp"),
                        event_type=event.get("event_type"),
                        category=event.get("category"),
                        session_id=event.get("session_id"),
                        story_id=event.get("story_id"),
                        agent_name=f"'{event.get('agent_name')}'" if event.get('agent_name') else "NULL",
                        workflow_id=f"'{event.get('workflow_id')}'" if event.get('workflow_id') else "NULL",
                        thread_id=f"'{event.get('thread_id')}'" if event.get('thread_id') else "NULL",
                        trace_id=f"'{event.get('trace_id')}'" if event.get('trace_id') else "NULL",
                        duration_ms=event.get("duration_ms", 0),
                        tokens_used=event.get("tokens_used", 0),
                        context_percent=event.get("context_percent", 0.0),
                        success=str(event.get("success", True)).lower(),
                        confidence_score=event.get("confidence_score", 0.0),
                        impact_score=event.get("impact_score", 0.0),
                        time_saved_or_wasted_ms=event.get("time_saved_or_wasted_ms", 0),
                        user_satisfaction_delta=event.get("user_satisfaction_delta", 0.0),
                        created_rule=str(event.get("created_rule", False)).lower(),
                        pattern_detected=str(event.get("pattern_detected", False)).lower(),
                        needs_review=str(event.get("needs_review", False)).lower(),
                        details=json.dumps(event.get("details", {}))
                    )

                    # Execute via MCP
                    result = await self.mcp_bridge.call_mcp_tool(
                        server_name="postgres",
                        tool_name="execute_sql",
                        parameters={"query": insert_sql}
                    )

                    if result.get("success"):
                        imported += 1
                    else:
                        errors += 1

                except Exception as e:
                    errors += 1
                    print(f"Error importing line {line_num}: {e}")
                    continue

        return {
            "imported": imported,
            "errors": errors,
            "file": str(jsonl_path)
        }

    async def execute_query(
        self,
        query: str
    ) -> List[Dict[str, Any]]:
        """
        Execute SQL query via MCP

        Args:
            query: SQL query string

        Returns:
            List of result rows as dictionaries
        """
        if not self._initialized:
            await self.initialize()

        result = await self.mcp_bridge.call_mcp_tool(
            server_name="postgres",
            tool_name="execute_sql",
            parameters={"query": query}
        )

        if not result.get("success"):
            raise Exception(f"Query failed: {result.get('error')}")

        # Parse MCP result - structure depends on Postgres MCP Pro response format
        return result.get("result", [])

    async def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a specific session"""
        query = f"""
        SELECT
            COUNT(*) as total_events,
            COUNT(DISTINCT event_type) as event_types,
            COUNT(DISTINCT agent_name) as agents_used,
            SUM(duration_ms) as total_duration_ms,
            SUM(tokens_used) as total_tokens,
            AVG(context_percent) as avg_context_percent,
            COUNT(*) FILTER (WHERE success = false) as failures,
            MIN(timestamp) as session_start,
            MAX(timestamp) as session_end
        FROM madf_events
        WHERE session_id = '{session_id}'
        """

        results = await self.execute_query(query)
        return results[0] if results else {}

    async def get_story_comparison(
        self,
        story_id_1: str,
        story_id_2: str
    ) -> Dict[str, Any]:
        """Compare metrics between two stories"""
        query = f"""
        SELECT
            story_id,
            COUNT(*) as total_events,
            SUM(duration_ms) as total_duration_ms,
            SUM(tokens_used) as total_tokens,
            AVG(duration_ms) as avg_duration_ms,
            AVG(tokens_used) as avg_tokens,
            COUNT(*) FILTER (WHERE success = false) as failures,
            COUNT(*) FILTER (WHERE pattern_detected = true) as patterns_detected
        FROM madf_events
        WHERE story_id IN ('{story_id_1}', '{story_id_2}')
        GROUP BY story_id
        ORDER BY story_id
        """

        results = await self.execute_query(query)
        return {
            "story_1": results[0] if len(results) > 0 else {},
            "story_2": results[1] if len(results) > 1 else {}
        }

    async def find_error_patterns(
        self,
        min_occurrences: int = 3
    ) -> List[Dict[str, Any]]:
        """Find recurring error patterns"""
        query = f"""
        SELECT
            details->>'error' as error_message,
            COUNT(*) as occurrence_count,
            array_agg(DISTINCT agent_name) as affected_agents,
            MIN(timestamp) as first_seen,
            MAX(timestamp) as last_seen
        FROM madf_events
        WHERE success = false
          AND details->>'error' IS NOT NULL
        GROUP BY details->>'error'
        HAVING COUNT(*) >= {min_occurrences}
        ORDER BY occurrence_count DESC
        """

        return await self.execute_query(query)
