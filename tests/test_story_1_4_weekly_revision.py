"""
Story 1.4 Phase 3 Tests - Weekly Revision Automation
Tests for weekly_revision.py

Test Categories:
1. WeeklyRevision: Report generation, statistics, recommendations
2. Report formatting: Markdown and JSON output
3. Integration: Full weekly workflow
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta, timezone
import json
import tempfile

from src.core.postgres_manager_sync import PostgresManager
from src.core.weekly_revision import WeeklyRevision


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_postgres_db():
    """Create temporary Postgres database for testing"""
    conn_string = "host=localhost port=5433 user=madf password=test_password dbname=madf_logs"

    pg = PostgresManager(connection_string=conn_string)
    pg.initialize()

    yield pg

    pg.close()


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory for reports"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_week_events(temp_postgres_db):
    """Insert sample events for a week"""
    pg = temp_postgres_db

    # Create events for last week
    week_start = datetime.now(timezone.utc) - timedelta(days=7)

    events = []
    for day in range(7):
        for event_num in range(10):
            timestamp = week_start + timedelta(days=day, hours=event_num)

            event = {
                "timestamp": timestamp.isoformat(),
                "event_type": "agent_action",
                "category": "execution",
                "session_id": f"test_session_{day}",
                "story_id": "1.4",
                "agent_name": "planning_agent" if event_num % 2 == 0 else "dev_agent",
                "duration_ms": 100 + (event_num * 50),
                "tokens_used": 1000 + (event_num * 100),
                "context_percent": 20.0 + (event_num * 2),
                "success": event_num % 5 != 0,  # 20% failure rate
                "confidence_score": 0.8 + (event_num * 0.02),
                "details": {"test": "data"}
            }
            events.append(event)

    # Import events via JSONL
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False, encoding='utf-8') as f:
        for event in events:
            f.write(json.dumps(event, ensure_ascii=True) + '\n')
        temp_path = Path(f.name)

    pg.import_jsonl_file(temp_path)
    temp_path.unlink()

    return events


# ============================================================================
# TEST: WeeklyRevision
# ============================================================================

class TestWeeklyRevision:
    """Test weekly revision report generation"""

    def test_initialize(self, temp_postgres_db, temp_output_dir):
        """Test WeeklyRevision initialization"""
        revision = WeeklyRevision(
            postgres_manager=temp_postgres_db,
            output_dir=temp_output_dir
        )

        revision.initialize()

        assert revision.pg._initialized
        assert temp_output_dir.exists()

        revision.close()

    def test_generate_weekly_report_structure(self, temp_postgres_db, temp_output_dir, sample_week_events):
        """Test weekly report structure"""
        revision = WeeklyRevision(
            postgres_manager=temp_postgres_db,
            output_dir=temp_output_dir
        )
        revision.initialize()

        # Generate report for last week
        week_start = datetime.now(timezone.utc) - timedelta(days=7)
        week_end = week_start + timedelta(days=7)

        report = revision.generate_weekly_report(week_start, week_end)

        # Verify structure
        assert 'period' in report
        assert 'overview' in report
        assert 'error_patterns' in report
        assert 'slow_operations' in report
        assert 'success_patterns' in report
        assert 'recommendations' in report

        # Verify period data
        assert report['period']['week_number'] > 0
        assert report['period']['start']
        assert report['period']['end']

        revision.close()

    def test_week_statistics(self, temp_postgres_db, temp_output_dir, sample_week_events):
        """Test weekly statistics calculation"""
        revision = WeeklyRevision(
            postgres_manager=temp_postgres_db,
            output_dir=temp_output_dir
        )
        revision.initialize()

        week_start = datetime.now(timezone.utc) - timedelta(days=7)
        week_end = week_start + timedelta(days=7)

        stats = revision._get_week_statistics(week_start, week_end)

        assert stats['total_events'] >= 70  # 7 days * 10 events
        assert stats['total_sessions'] >= 7
        assert stats['stories_worked'] >= 1
        assert stats['successful_events'] > 0
        assert stats['failed_events'] > 0

        revision.close()

    def test_generate_recommendations(self, temp_postgres_db, temp_output_dir):
        """Test recommendation generation logic"""
        revision = WeeklyRevision(
            postgres_manager=temp_postgres_db,
            output_dir=temp_output_dir
        )

        # Test high error rate scenario
        stats = {
            'total_events': 100,
            'failed_events': 15,  # 15% error rate
            'avg_tokens_used': 2000,
            'avg_context_percent': 50.0
        }

        recommendations = revision._generate_recommendations(stats, [], [])

        assert len(recommendations) > 0
        assert any("[HIGH]" in rec for rec in recommendations)

        # Test high token usage scenario
        stats['failed_events'] = 5  # Low error rate
        stats['avg_tokens_used'] = 4000  # High tokens

        recommendations = revision._generate_recommendations(stats, [], [])

        assert any("token" in rec.lower() for rec in recommendations)

        revision.close()

    def test_save_json_report(self, temp_postgres_db, temp_output_dir, sample_week_events):
        """Test saving report as JSON"""
        revision = WeeklyRevision(
            postgres_manager=temp_postgres_db,
            output_dir=temp_output_dir
        )
        revision.initialize()

        week_start = datetime.now(timezone.utc) - timedelta(days=7)
        report = revision.generate_weekly_report(week_start)

        json_path = revision.save_report(report, format="json")

        assert json_path.exists()
        assert json_path.suffix == ".json"

        # Verify JSON is valid
        with open(json_path, 'r', encoding='utf-8') as f:
            loaded = json.load(f)

        assert loaded['period'] == report['period']
        # Overview will have floats instead of Decimals after JSON round-trip
        assert loaded['overview']['total_events'] == report['overview']['total_events']
        assert loaded['overview']['total_sessions'] == report['overview']['total_sessions']

        revision.close()

    def test_save_markdown_report(self, temp_postgres_db, temp_output_dir, sample_week_events):
        """Test saving report as Markdown"""
        revision = WeeklyRevision(
            postgres_manager=temp_postgres_db,
            output_dir=temp_output_dir
        )
        revision.initialize()

        week_start = datetime.now(timezone.utc) - timedelta(days=7)
        report = revision.generate_weekly_report(week_start)

        md_path = revision.save_report(report, format="markdown")

        assert md_path.exists()
        assert md_path.suffix == ".md"

        # Verify markdown content
        content = md_path.read_text(encoding='utf-8')

        assert "# MADF Weekly Revision Report" in content
        assert "## Executive Summary" in content
        assert "## Performance Metrics" in content
        assert "## Recommendations" in content

        revision.close()

    def test_markdown_format_token_limit(self, temp_postgres_db, temp_output_dir, sample_week_events):
        """Test that markdown report is reasonably sized"""
        revision = WeeklyRevision(
            postgres_manager=temp_postgres_db,
            output_dir=temp_output_dir
        )
        revision.initialize()

        week_start = datetime.now(timezone.utc) - timedelta(days=7)
        report = revision.generate_weekly_report(week_start)

        md_content = revision._format_markdown_report(report)

        # Rough token estimate (~0.75 tokens/word)
        word_count = len(md_content.split())
        estimated_tokens = word_count * 0.75

        # Should be under 2000 tokens for weekly report
        assert estimated_tokens < 2000, f"Report too long: ~{estimated_tokens} tokens"

        revision.close()


# ============================================================================
# TEST: Integration
# ============================================================================

class TestWeeklyWorkflow:
    """Test complete weekly revision workflow"""

    def test_run_weekly_revision(self, temp_postgres_db, temp_output_dir, sample_week_events):
        """Test full weekly revision workflow"""
        revision = WeeklyRevision(
            postgres_manager=temp_postgres_db,
            output_dir=temp_output_dir
        )

        md_path = revision.run_weekly_revision()

        # Verify both files created
        assert md_path.exists()

        json_path = md_path.with_suffix('.json')
        assert json_path.exists()

        # Verify content
        md_content = md_path.read_text(encoding='utf-8')
        assert "MADF Weekly Revision Report" in md_content

        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        assert 'overview' in json_data
        assert 'recommendations' in json_data

        revision.close()

    def test_multiple_weeks_different_files(self, temp_postgres_db, temp_output_dir, sample_week_events):
        """Test that different weeks create separate files"""
        revision = WeeklyRevision(
            postgres_manager=temp_postgres_db,
            output_dir=temp_output_dir
        )
        revision.initialize()

        # Generate report for this week
        week1_start = datetime.now(timezone.utc) - timedelta(days=7)
        report1 = revision.generate_weekly_report(week1_start)
        path1 = revision.save_report(report1, format="markdown")

        # Generate report for last week
        week2_start = datetime.now(timezone.utc) - timedelta(days=14)
        report2 = revision.generate_weekly_report(week2_start)
        path2 = revision.save_report(report2, format="markdown")

        # Verify different files (different week numbers)
        assert path1 != path2

        revision.close()


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
