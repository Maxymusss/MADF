"""
PostgresManager - Direct psycopg3 integration for MADF logging
Story 1.4 Task 1 Phase 2 - Postgres Analysis Engine
Follows Story 1.3 pattern: Direct library for performance + optional MCP helpers
"""

import os
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
import psycopg
from psycopg.rows import dict_row


class PostgresManager:
    """
    Direct PostgreSQL manager for MADF logging infrastructure

    Primary operations use direct psycopg3 for performance
    Optional MCP helpers available via mcp_bridge.py for advanced analysis
    """

    def __init__(
        self,
        connection_string: Optional[str] = None
    ):
        """
        Initialize Postgres manager with direct connection

        Args:
            connection_string: PostgreSQL connection string (default: from env)
        """
        self.connection_string = connection_string or os.getenv(
            "POSTGRES_CONNECTION_STRING",
            "postgresql://localhost:5432/madf_logs"
        )
        self._conn: Optional[psycopg.AsyncConnection] = None
        self._initialized = False

    async def initialize(self):
        """Initialize connection and create schema"""
        if self._initialized:
            return

        # Create async connection
        self._conn = await psycopg.AsyncConnection.connect(
            self.connection_string,
            row_factory=dict_row
        )

        # Create schema if not exists
        await self.create_schema()
        self._initialized = True

    async def create_schema(self):
        """Create MADF logging events table schema"""
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

        async with self._conn.cursor() as cur:
            await cur.execute(schema_sql)
            await self._conn.commit()

    async def import_jsonl_file(self, jsonl_path: Path) -> Dict[str, Any]:
        """
        Import JSONL log file to Postgres

        Args:
            jsonl_path: Path to JSONL file

        Returns:
            Dict with import statistics
        """
        if not self._initialized:
            await self.initialize()

        imported = 0
        errors = 0
        start_time = None

        with open(jsonl_path, 'r', encoding='utf-8') as f:
            async with self._conn.cursor() as cur:
                for line_num, line in enumerate(f, 1):
                    try:
                        event = json.loads(line.strip())

                        # Extract fields matching schema
                        insert_sql = """
                            INSERT INTO madf_events (
                                timestamp, event_type, category, session_id, story_id,
                                agent_name, workflow_id, thread_id, trace_id,
                                duration_ms, tokens_used, context_percent, success,
                                confidence_score, impact_score, time_saved_or_wasted_ms,
                                user_satisfaction_delta, created_rule, pattern_detected,
                                needs_review, details
                            ) VALUES (
                                %(timestamp)s, %(event_type)s, %(category)s, %(session_id)s,
                                %(story_id)s, %(agent_name)s, %(workflow_id)s, %(thread_id)s,
                                %(trace_id)s, %(duration_ms)s, %(tokens_used)s, %(context_percent)s,
                                %(success)s, %(confidence_score)s, %(impact_score)s,
                                %(time_saved_or_wasted_ms)s, %(user_satisfaction_delta)s,
                                %(created_rule)s, %(pattern_detected)s, %(needs_review)s,
                                %(details)s::jsonb
                            )
                            """

                        # Build parameters with defaults
                        params = {
                            "timestamp": event.get("timestamp"),
                            "event_type": event.get("event_type"),
                            "category": event.get("category"),
                            "session_id": event.get("session_id"),
                            "story_id": event.get("story_id"),
                            "agent_name": event.get("agent_name"),
                            "workflow_id": event.get("workflow_id"),
                            "thread_id": event.get("thread_id"),
                            "trace_id": event.get("trace_id"),
                            "duration_ms": event.get("duration_ms", 0),
                            "tokens_used": event.get("tokens_used", 0),
                            "context_percent": event.get("context_percent", 0.0),
                            "success": event.get("success", True),
                            "confidence_score": event.get("confidence_score", 0.0),
                            "impact_score": event.get("impact_score", 0.0),
                            "time_saved_or_wasted_ms": event.get("time_saved_or_wasted_ms", 0),
                            "user_satisfaction_delta": event.get("user_satisfaction_delta", 0.0),
                            "created_rule": event.get("created_rule", False),
                            "pattern_detected": event.get("pattern_detected", False),
                            "needs_review": event.get("needs_review", False),
                            "details": json.dumps(event.get("details", {}))
                        }

                        await cur.execute(insert_sql, params)
                        imported += 1

                    except Exception as e:
                        errors += 1
                        print(f"Error importing line {line_num}: {e}")
                        continue

                await self._conn.commit()

        return {
            "imported": imported,
            "errors": errors,
            "file": str(jsonl_path)
        }

    async def execute_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute SQL query with optional parameters

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of result rows as dictionaries
        """
        if not self._initialized:
            await self.initialize()

        async with self._conn.cursor() as cur:
            await cur.execute(query, params or {})
            results = await cur.fetchall()
            return results

    async def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a specific session"""
        query = """
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
        WHERE session_id = %(session_id)s
        """

        results = await self.execute_query(query, {"session_id": session_id})
        return results[0] if results else {}

    async def get_story_comparison(
        self,
        story_id_1: str,
        story_id_2: str
    ) -> Dict[str, Any]:
        """Compare metrics between two stories"""
        query = """
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
        WHERE story_id IN (%(story_1)s, %(story_2)s)
        GROUP BY story_id
        ORDER BY story_id
        """

        results = await self.execute_query(query, {
            "story_1": story_id_1,
            "story_2": story_id_2
        })
        return {
            "story_1": results[0] if len(results) > 0 else {},
            "story_2": results[1] if len(results) > 1 else {}
        }

    async def find_error_patterns(
        self,
        min_occurrences: int = 3
    ) -> List[Dict[str, Any]]:
        """Find recurring error patterns"""
        query = """
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
        HAVING COUNT(*) >= %(min_count)s
        ORDER BY occurrence_count DESC
        """

        return await self.execute_query(query, {"min_count": min_occurrences})

    async def close(self):
        """Close database connection"""
        if self._conn:
            await self._conn.close()
            self._initialized = False
