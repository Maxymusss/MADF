"""
Weekly Revision Automation - Story 1.4 Task 1 Phase 3

Automated weekly analysis of execution patterns and performance trends
Generates concise reports for continuous improvement and learning
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
from decimal import Decimal
import json

from .postgres_manager_sync import PostgresManager
from .log_analyzer_sync import LogAnalyzer
from .pattern_extractor_sync import PatternExtractor


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal and datetime objects from Postgres"""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class WeeklyRevision:
    """
    Automated weekly revision and analysis system

    Generates comprehensive weekly reports covering:
    - Performance trends across stories
    - Error pattern evolution
    - Agent efficiency metrics
    - Token usage optimization opportunities
    - Success pattern reinforcement
    """

    def __init__(
        self,
        postgres_manager: Optional[PostgresManager] = None,
        output_dir: Optional[Path] = None
    ):
        """
        Initialize weekly revision system

        Args:
            postgres_manager: PostgresManager instance (creates new if None)
            output_dir: Directory for weekly reports (default: docs/qa/weekly-reports/)
        """
        self.pg = postgres_manager or PostgresManager()
        self.analyzer = LogAnalyzer(postgres_manager=self.pg)
        self.extractor = PatternExtractor(postgres_manager=self.pg)

        self.output_dir = output_dir or Path("docs/qa/weekly-reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def initialize(self):
        """Initialize all components"""
        self.pg.initialize()
        self.analyzer.initialize()
        self.extractor.initialize()

    def generate_weekly_report(
        self,
        week_start: Optional[datetime] = None,
        week_end: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive weekly report

        Args:
            week_start: Start of week (default: last Monday)
            week_end: End of week (default: last Sunday)

        Returns:
            Report data dictionary
        """
        if not week_start:
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday() + 7)  # Last Monday
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

        if not week_end:
            week_end = week_start + timedelta(days=7)  # Following Sunday

        # Collect weekly statistics
        stats = self._get_week_statistics(week_start, week_end)

        # Extract patterns
        error_patterns = self.extractor.find_error_patterns(min_occurrences=2)
        slow_operations = self.extractor.find_slow_operations(duration_threshold_ms=1000)
        success_patterns = self.extractor.find_success_patterns(min_confidence=0.85)

        # Generate report sections
        report = {
            "period": {
                "start": week_start.isoformat(),
                "end": week_end.isoformat(),
                "week_number": week_start.isocalendar()[1]
            },
            "overview": stats,
            "error_patterns": error_patterns[:10],  # Top 10 errors
            "slow_operations": slow_operations[:10],  # Top 10 slowest
            "success_patterns": success_patterns[:5],  # Top 5 successes
            "recommendations": self._generate_recommendations(stats, error_patterns, slow_operations)
        }

        return report

    def _get_week_statistics(
        self,
        week_start: datetime,
        week_end: datetime
    ) -> Dict[str, Any]:
        """
        Get aggregated statistics for the week

        Args:
            week_start: Week start timestamp
            week_end: Week end timestamp

        Returns:
            Weekly statistics dictionary
        """
        query = """
        SELECT
            COUNT(*) as total_events,
            COUNT(DISTINCT session_id) as total_sessions,
            COUNT(DISTINCT story_id) as stories_worked,
            SUM(duration_ms) as total_duration_ms,
            AVG(duration_ms) as avg_duration_ms,
            SUM(tokens_used) as total_tokens_used,
            AVG(tokens_used) as avg_tokens_used,
            AVG(context_percent) as avg_context_percent,
            COUNT(*) FILTER (WHERE success = true) as successful_events,
            COUNT(*) FILTER (WHERE success = false) as failed_events,
            COUNT(DISTINCT agent_name) as agents_used
        FROM madf_events
        WHERE timestamp >= %s AND timestamp < %s
        """

        results = self.pg.execute_query(query, (week_start, week_end))

        if results:
            return results[0]
        return {}

    def _generate_recommendations(
        self,
        stats: Dict[str, Any],
        error_patterns: List[Dict[str, Any]],
        slow_operations: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate actionable recommendations based on patterns

        Args:
            stats: Weekly statistics
            error_patterns: Detected error patterns
            slow_operations: Slow operation patterns

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Error rate recommendations
        if stats.get('failed_events', 0) > 0:
            error_rate = stats['failed_events'] / stats.get('total_events', 1)
            if error_rate > 0.1:  # >10% error rate
                recommendations.append(
                    f"[HIGH] Error rate at {error_rate*100:.1f}% - Review top error patterns"
                )

        # Token efficiency recommendations
        avg_tokens = stats.get('avg_tokens_used', 0)
        if avg_tokens > 3000:
            recommendations.append(
                f"[MEDIUM] Average token usage high ({avg_tokens:.0f}) - Optimize prompts"
            )

        # Context usage recommendations
        avg_context = stats.get('avg_context_percent', 0)
        if avg_context > 70:
            recommendations.append(
                f"[MEDIUM] Context usage at {avg_context:.1f}% - Consider summarization"
            )

        # Performance recommendations
        if slow_operations:
            slowest = slow_operations[0]
            recommendations.append(
                f"[LOW] Slowest operation: {slowest.get('event_type', 'unknown')} "
                f"({slowest.get('avg_duration_ms', 0):.0f}ms avg)"
            )

        # Success pattern reinforcement
        if not recommendations:
            recommendations.append("[INFO] No critical issues - Continue current approach")

        return recommendations

    def save_report(
        self,
        report: Dict[str, Any],
        format: str = "markdown"
    ) -> Path:
        """
        Save weekly report to file

        Args:
            report: Report data dictionary
            format: Output format ("markdown" or "json")

        Returns:
            Path to saved report file
        """
        week_num = report['period']['week_number']
        year = datetime.fromisoformat(report['period']['start']).year

        if format == "json":
            filename = f"week_{year}_w{week_num:02d}.json"
            filepath = self.output_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, cls=DecimalEncoder)

        elif format == "markdown":
            filename = f"week_{year}_w{week_num:02d}.md"
            filepath = self.output_dir / filename

            content = self._format_markdown_report(report)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

        else:
            raise ValueError(f"Unsupported format: {format}")

        return filepath

    def _format_markdown_report(self, report: Dict[str, Any]) -> str:
        """
        Format report as markdown document

        Args:
            report: Report data dictionary

        Returns:
            Markdown-formatted report string
        """
        week_num = report['period']['week_number']
        year = datetime.fromisoformat(report['period']['start']).year
        start = datetime.fromisoformat(report['period']['start']).strftime('%Y-%m-%d')
        end = datetime.fromisoformat(report['period']['end']).strftime('%Y-%m-%d')

        overview = report.get('overview', {})

        md = f"""# MADF Weekly Revision Report - Week {week_num}, {year}

**Period**: {start} to {end}

## Executive Summary

- **Total Events**: {overview.get('total_events', 0):,}
- **Sessions**: {overview.get('total_sessions', 0)}
- **Stories Worked**: {overview.get('stories_worked', 0)}
- **Agents Used**: {overview.get('agents_used', 0)}
- **Success Rate**: {(overview.get('successful_events', 0) / max(overview.get('total_events', 1), 1) * 100):.1f}%

## Performance Metrics

- **Total Execution Time**: {overview.get('total_duration_ms', 0) / 1000:.1f}s
- **Average Event Duration**: {overview.get('avg_duration_ms', 0):.0f}ms
- **Total Tokens Used**: {overview.get('total_tokens_used', 0):,}
- **Average Tokens/Event**: {overview.get('avg_tokens_used', 0):.0f}
- **Average Context Usage**: {overview.get('avg_context_percent', 0):.1f}%

## Top Error Patterns

"""
        error_patterns = report.get('error_patterns', [])
        if error_patterns:
            for i, pattern in enumerate(error_patterns[:5], 1):
                md += f"{i}. **{pattern.get('error_type', 'Unknown')}**: {pattern.get('occurrence_count', 0)} occurrences\n"
                if pattern.get('sample_message'):
                    md += f"   - Sample: `{pattern['sample_message'][:100]}`\n"
        else:
            md += "*No recurring error patterns detected*\n"

        md += "\n## Performance Bottlenecks\n\n"

        slow_ops = report.get('slow_operations', [])
        if slow_ops:
            for i, op in enumerate(slow_ops[:5], 1):
                md += f"{i}. **{op.get('event_type', 'Unknown')}** by {op.get('agent_name', 'Unknown')}: {op.get('avg_duration_ms', 0):.0f}ms avg ({op.get('occurrence_count', 0)} times)\n"
        else:
            md += "*No significant performance bottlenecks detected*\n"

        md += "\n## Success Patterns\n\n"

        success = report.get('success_patterns', [])
        if success:
            for i, pattern in enumerate(success[:5], 1):
                md += f"{i}. **{pattern.get('event_type', 'Unknown')}** by {pattern.get('agent_name', 'Unknown')}: {pattern.get('avg_confidence', 0):.2f} confidence ({pattern.get('occurrence_count', 0)} times)\n"
        else:
            md += "*Not enough data for success pattern analysis*\n"

        md += "\n## Recommendations\n\n"

        recommendations = report.get('recommendations', [])
        for rec in recommendations:
            md += f"- {rec}\n"

        md += f"\n---\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        return md

    def run_weekly_revision(self) -> Path:
        """
        Run complete weekly revision workflow

        Returns:
            Path to generated markdown report
        """
        self.initialize()

        # Generate report for last week
        report = self.generate_weekly_report()

        # Save both formats
        json_path = self.save_report(report, format="json")
        md_path = self.save_report(report, format="markdown")

        print(f"Weekly revision complete:")
        print(f"  JSON: {json_path}")
        print(f"  Markdown: {md_path}")

        return md_path

    def close(self):
        """Close all connections"""
        self.pg.close()
        self.analyzer.close()
        self.extractor.close()


def main():
    """CLI entry point for weekly revision"""
    import argparse

    parser = argparse.ArgumentParser(description="MADF Weekly Revision Automation")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("docs/qa/weekly-reports"),
        help="Output directory for reports"
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json", "both"],
        default="both",
        help="Output format"
    )

    args = parser.parse_args()

    revision = WeeklyRevision(output_dir=args.output_dir)

    try:
        report_path = revision.run_weekly_revision()
        print(f"\n[OK] Weekly report generated: {report_path}")
    finally:
        revision.close()


if __name__ == "__main__":
    main()
