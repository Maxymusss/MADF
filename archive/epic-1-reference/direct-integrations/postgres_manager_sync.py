"""
Postgres Manager (Sync) - Windows-compatible direct library integration
Story 1.4 Task 1 Phase 2 - Postgres Analysis Engine

Synchronous implementation for Windows compatibility
(psycopg AsyncConnection doesn't work with Windows ProactorEventLoop)
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

    Synchronous implementation (Windows compatible)
    Primary operations use direct psycopg3 for performance
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
            "host=localhost port=5433 user=madf password=test_password dbname=madf_logs"
        )
        self._conn: Optional[psycopg.Connection] = None
        self._initialized = False

    def initialize(self):
        """Initialize connection and create schema"""
        if self._initialized:
            return

        # Create sync connection (Windows compatible)
        self._conn = psycopg.connect(
            self.connection_string,
            row_factory=dict_row
        )

        # Create schema if not exists
        self.create_schema()
        self._initialized = True

    def create_schema(self):
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
            context_percent REAL DEFAULT 0.0,
            success BOOLEAN DEFAULT true,
            confidence_score REAL,
            impact_score REAL,
            details JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );

        -- Indexes for common queries
        CREATE INDEX IF NOT EXISTS idx_madf_session_id ON madf_events(session_id);
        CREATE INDEX IF NOT EXISTS idx_madf_story_id ON madf_events(story_id);
        CREATE INDEX IF NOT EXISTS idx_madf_agent_name ON madf_events(agent_name);
        CREATE INDEX IF NOT EXISTS idx_madf_event_type ON madf_events(event_type);
        CREATE INDEX IF NOT EXISTS idx_madf_timestamp ON madf_events(timestamp DESC);
        CREATE INDEX IF NOT EXISTS idx_madf_success ON madf_events(success) WHERE success = false;
        """

        with self._conn.cursor() as cur:
            cur.execute(schema_sql)
            self._conn.commit()

    def import_jsonl_file(self, jsonl_path: Path) -> Dict[str, Any]:
        """
        Import JSONL log file to Postgres

        Args:
            jsonl_path: Path to JSONL log file

        Returns:
            Import statistics
        """
        if not self._initialized:
            self.initialize()

        total_events = 0
        successful_imports = 0
        failed_imports = 0

        with open(jsonl_path, 'r', encoding='utf-8') as f:
            with self._conn.cursor() as cur:
                for line_num, line in enumerate(f, 1):
                    total_events += 1
                    try:
                        event = json.loads(line.strip())

                        # Extract fields
                        insert_sql = """
                        INSERT INTO madf_events (
                            timestamp, event_type, category, session_id, story_id,
                            agent_name, workflow_id, thread_id, trace_id,
                            duration_ms, tokens_used, context_percent,
                            success, confidence_score, impact_score, details
                        ) VALUES (
                            %(timestamp)s, %(event_type)s, %(category)s, %(session_id)s, %(story_id)s,
                            %(agent_name)s, %(workflow_id)s, %(thread_id)s, %(trace_id)s,
                            %(duration_ms)s, %(tokens_used)s, %(context_percent)s,
                            %(success)s, %(confidence_score)s, %(impact_score)s, %(details)s
                        )
                        """

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
                            "confidence_score": event.get("confidence_score"),
                            "impact_score": event.get("impact_score"),
                            "details": json.dumps(event.get("details", {}))
                        }

                        cur.execute(insert_sql, params)
                        successful_imports += 1

                    except Exception as e:
                        failed_imports += 1
                        print(f"Line {line_num} import failed: {e}")

                self._conn.commit()

        return {
            "total_events": total_events,
            "successful_imports": successful_imports,
            "failed_imports": failed_imports,
            "file_path": str(jsonl_path)
        }

    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """
        Get summary statistics for a session

        Args:
            session_id: Session identifier

        Returns:
            Session statistics dictionary
        """
        if not self._initialized:
            self.initialize()

        query = """
        SELECT
            session_id,
            story_id,
            COUNT(*) as total_events,
            SUM(duration_ms) as total_duration_ms,
            AVG(duration_ms) as avg_duration_ms,
            SUM(tokens_used) as total_tokens_used,
            AVG(context_percent) as avg_context_percent,
            COUNT(*) FILTER (WHERE success = true) as successful_events,
            COUNT(*) FILTER (WHERE success = false) as failed_events,
            MIN(timestamp) as start_time,
            MAX(timestamp) as end_time
        FROM madf_events
        WHERE session_id = %s
        GROUP BY session_id, story_id
        """

        with self._conn.cursor() as cur:
            cur.execute(query, (session_id,))
            result = cur.fetchone()
            return result or {}

    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Execute arbitrary SQL query

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of result dictionaries
        """
        if not self._initialized:
            self.initialize()

        with self._conn.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchall()

    def close(self):
        """Close Postgres connection"""
        if self._conn:
            self._conn.close()
            self._conn = None
            self._initialized = False
