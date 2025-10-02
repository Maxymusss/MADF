"""
Enhanced Validator Agent - Story 1.4 Integration
Comprehensive QA with DSPy, Sentry, and Postgres integration

Responsibilities:
- Automated test execution and validation
- Performance analysis using Postgres logs
- Error tracking and alerting via Sentry
- Self-improvement via DSPy optimization
- Quality metrics and reporting
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import subprocess
import json

from .base_agent import BaseAgent
from src.core.dspy_optimizer import MADFOptimizer, MADFQAModule
from src.core.sentry_integration import SentryManager, track_errors
from src.core.postgres_manager_sync import PostgresManager
from src.core.log_analyzer_sync import LogAnalyzer
from src.core.pattern_extractor_sync import PatternExtractor
from src.core.quick_logger import QuickLogger


class ValidatorAgentEnhanced(BaseAgent):
    """
    Enhanced Validator Agent with Story 1.4 self-improvement capabilities

    Integrates:
    - DSPy for agent optimization
    - Sentry for error tracking
    - Postgres for performance analysis
    """

    def __init__(
        self,
        enable_sentry: bool = True,
        enable_dspy: bool = True,
        enable_postgres: bool = True
    ):
        """
        Initialize enhanced validator agent

        Args:
            enable_sentry: Enable Sentry error tracking
            enable_dspy: Enable DSPy optimization
            enable_postgres: Enable Postgres analysis
        """
        super().__init__("Validator", "Quality Assurance & Self-Improvement Specialist")

        self.logger = QuickLogger()

        # Initialize Story 1.4 components
        self.sentry = SentryManager() if enable_sentry else None
        self.dspy_optimizer = MADFOptimizer() if enable_dspy else None
        self.postgres = PostgresManager() if enable_postgres else None
        self.log_analyzer = LogAnalyzer(postgres_manager=self.postgres) if enable_postgres else None
        self.pattern_extractor = PatternExtractor(postgres_manager=self.postgres) if enable_postgres else None

        self._initialize_components()
        self._initialize_tools()

    def _initialize_components(self):
        """Initialize Story 1.4 integration components"""
        if self.sentry:
            self.sentry.initialize()

        if self.dspy_optimizer:
            self.dspy_optimizer.initialize()

        if self.postgres:
            self.postgres.initialize()
            if self.log_analyzer:
                self.log_analyzer.initialize()
            if self.pattern_extractor:
                self.pattern_extractor.initialize()

    def _initialize_tools(self):
        """Initialize Validator-specific tools"""
        self._tools = [
            'pytest_execution',
            'dspy_optimization',
            'sentry_monitoring',
            'postgres_analysis',
            'performance_profiling',
            'code_quality_checks'
        ]

    def get_available_tools(self) -> List[str]:
        """Return testing and optimization tools"""
        return self._tools.copy()

    @track_errors(agent_name="validator_agent")
    def run_tests(
        self,
        test_path: Optional[str] = None,
        test_pattern: Optional[str] = None,
        story_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute pytest tests and capture results

        Args:
            test_path: Path to test file/directory
            test_pattern: Test pattern to match (e.g., "test_story_1_*")
            story_id: Story ID for logging context

        Returns:
            Test execution results with metrics
        """
        test_cmd = ["pytest"]

        if test_path:
            test_cmd.append(test_path)
        elif test_pattern:
            test_cmd.extend(["-k", test_pattern])

        # Add coverage and output options
        test_cmd.extend([
            "-v",
            "--tb=short",
            "--json-report",
            "--json-report-file=tests/reports/test_results.json"
        ])

        try:
            result = subprocess.run(
                test_cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            # Parse JSON results if available
            results_file = Path("tests/reports/test_results.json")
            test_results = {}
            if results_file.exists():
                with open(results_file, 'r') as f:
                    test_results = json.load(f)

            execution_result = {
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "test_results": test_results
            }

            # Log test execution
            self.logger.log(
                event_type="agent_action",
                category="execution",
                agent_name="validator_agent",
                story_id=story_id,
                success=execution_result["success"],
                details={
                    "action": "run_tests",
                    "test_path": test_path,
                    "exit_code": result.returncode
                }
            )

            return execution_result

        except subprocess.TimeoutExpired:
            if self.sentry:
                self.sentry.capture_message(
                    "Test execution timeout",
                    level="error",
                    agent_name="validator_agent",
                    story_id=story_id
                )

            return {
                "success": False,
                "error": "Test execution timeout (>300s)",
                "exit_code": -1
            }

        except Exception as e:
            if self.sentry:
                self.sentry.capture_error(
                    e,
                    agent_name="validator_agent",
                    story_id=story_id
                )

            return {
                "success": False,
                "error": str(e),
                "exit_code": -1
            }

    def analyze_performance(
        self,
        session_id: Optional[str] = None,
        story_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze performance metrics from Postgres logs

        Args:
            session_id: Session to analyze
            story_id: Story to analyze

        Returns:
            Performance analysis results
        """
        if not self.log_analyzer:
            return {"error": "Postgres analysis disabled"}

        try:
            if session_id:
                # Analyze specific session
                summary = self.log_analyzer.get_session_summary(session_id)
                return {
                    "analysis_type": "session",
                    "session_id": session_id,
                    "summary": summary
                }

            elif story_id:
                # Analyze story performance
                # Get all sessions for this story
                query = """
                SELECT DISTINCT session_id
                FROM madf_events
                WHERE story_id = %s
                ORDER BY timestamp DESC
                LIMIT 10
                """
                sessions = self.postgres.execute_query(query, (story_id,))

                summaries = []
                for session in sessions:
                    sid = session['session_id']
                    summaries.append(self.log_analyzer.get_session_summary(sid))

                return {
                    "analysis_type": "story",
                    "story_id": story_id,
                    "sessions_analyzed": len(summaries),
                    "summaries": summaries
                }

            else:
                return {"error": "Must provide session_id or story_id"}

        except Exception as e:
            if self.sentry:
                self.sentry.capture_error(e, agent_name="validator_agent", story_id=story_id)

            return {"error": str(e)}

    def extract_error_patterns(
        self,
        min_occurrences: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Extract recurring error patterns for optimization

        Args:
            min_occurrences: Minimum error occurrences to report

        Returns:
            List of error patterns
        """
        if not self.pattern_extractor:
            return []

        try:
            patterns = self.pattern_extractor.find_error_patterns(
                min_occurrences=min_occurrences
            )

            # Log error patterns to Sentry for alerting
            if self.sentry and patterns:
                for pattern in patterns[:5]:  # Top 5 errors
                    self.sentry.capture_message(
                        f"Recurring error: {pattern.get('error_type', 'Unknown')} "
                        f"({pattern.get('occurrence_count', 0)} times)",
                        level="warning",
                        agent_name="validator_agent",
                        context=pattern
                    )

            return patterns

        except Exception as e:
            if self.sentry:
                self.sentry.capture_error(e, agent_name="validator_agent")
            return []

    def optimize_with_dspy(
        self,
        target_agent: str = "qa_agent",
        optimizer_type: str = "bootstrap"
    ) -> Dict[str, Any]:
        """
        Optimize agent using DSPy framework

        Args:
            target_agent: Agent to optimize
            optimizer_type: "bootstrap" or "mipro"

        Returns:
            Optimization results and metrics
        """
        if not self.dspy_optimizer:
            return {"error": "DSPy optimization disabled"}

        try:
            # Extract training examples and optimize
            optimized_module, metrics = self.dspy_optimizer.optimize_agent(
                target_agent,
                optimizer_type=optimizer_type
            )

            # Save optimized module
            module_path = self.dspy_optimizer.save_optimized_module(
                optimized_module,
                target_agent
            )

            return {
                "success": True,
                "agent": target_agent,
                "metrics": metrics,
                "module_path": str(module_path)
            }

        except ValueError as e:
            # Insufficient training data
            return {
                "success": False,
                "error": str(e),
                "recommendation": "Need more execution data for training"
            }

        except Exception as e:
            if self.sentry:
                self.sentry.capture_error(e, agent_name="validator_agent")

            return {
                "success": False,
                "error": str(e)
            }

    def validate_implementation(
        self,
        implementation: str,
        acceptance_criteria: str,
        test_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate implementation against acceptance criteria using DSPy QA module

        Args:
            implementation: Code or feature implementation
            acceptance_criteria: Success criteria
            test_results: Optional test execution results

        Returns:
            Validation decision and reasoning
        """
        if not self.dspy_optimizer:
            # Fallback to simple validation
            return self._simple_validation(implementation, acceptance_criteria, test_results)

        try:
            # Use DSPy QA module
            qa_module = MADFQAModule()

            test_results_str = json.dumps(test_results) if test_results else "No automated tests run"

            prediction = qa_module.forward(
                implementation=implementation[:1000],  # Truncate for token limits
                acceptance_criteria=acceptance_criteria[:500],
                test_results=test_results_str[:500]
            )

            return {
                "validated": True,
                "validation_result": prediction.validation_result,
                "issues_found": prediction.issues_found,
                "confidence": float(prediction.confidence),
                "method": "dspy_qa_module"
            }

        except Exception as e:
            if self.sentry:
                self.sentry.capture_error(e, agent_name="validator_agent")

            return self._simple_validation(implementation, acceptance_criteria, test_results)

    def _simple_validation(
        self,
        implementation: str,
        acceptance_criteria: str,
        test_results: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Simple validation fallback"""
        # Basic heuristic validation
        tests_passing = test_results and test_results.get("success", False)

        return {
            "validated": tests_passing,
            "validation_result": "PASS" if tests_passing else "FAIL",
            "issues_found": [] if tests_passing else ["Tests not passing"],
            "confidence": 0.7 if tests_passing else 0.3,
            "method": "simple_heuristic"
        }

    def generate_qa_report(
        self,
        story_id: str,
        session_id: Optional[str] = None
    ) -> str:
        """
        Generate comprehensive QA report for story

        Args:
            story_id: Story ID to report on
            session_id: Optional specific session

        Returns:
            Markdown-formatted QA report
        """
        from datetime import datetime
        report_lines = [
            f"# QA Report - Story {story_id}",
            f"\nGenerated: {datetime.now().isoformat()}",
            "\n## Test Execution Results\n"
        ]

        # Run tests for this story
        test_results = self.run_tests(test_pattern=f"test_story_{story_id.replace('.', '_')}*")

        if test_results.get("success"):
            report_lines.append("[OK] All tests passing")
        else:
            report_lines.append(f"[FAIL] Tests failed with exit code {test_results.get('exit_code')}")

        # Performance analysis
        if self.log_analyzer:
            report_lines.append("\n## Performance Analysis\n")
            perf = self.analyze_performance(session_id=session_id, story_id=story_id)
            if "summary" in perf:
                report_lines.append(perf["summary"])
            elif "summaries" in perf:
                report_lines.append(f"Analyzed {len(perf['summaries'])} recent sessions")

        # Error patterns
        if self.pattern_extractor:
            report_lines.append("\n## Error Patterns\n")
            errors = self.extract_error_patterns()
            if errors:
                for i, err in enumerate(errors[:5], 1):
                    report_lines.append(
                        f"{i}. {err.get('error_type')}: {err.get('occurrence_count')} occurrences"
                    )
            else:
                report_lines.append("No recurring errors detected")

        report_lines.append("\n---")
        return "\n".join(report_lines)

    def process_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process validation and QA tasks

        Args:
            task_description: QA task description
            context: Task context

        Returns:
            Validation results
        """
        story_id = context.get("story_id")
        session_id = context.get("session_id")

        # Determine task type
        if "test" in task_description.lower():
            return self.run_tests(story_id=story_id)

        elif "performance" in task_description.lower() or "analyze" in task_description.lower():
            return self.analyze_performance(session_id=session_id, story_id=story_id)

        elif "optimize" in task_description.lower():
            target = context.get("target_agent", "qa_agent")
            return self.optimize_with_dspy(target_agent=target)

        elif "report" in task_description.lower():
            return {"report": self.generate_qa_report(story_id or "unknown")}

        else:
            # Default comprehensive QA
            return {
                "agent": "validator_enhanced",
                "tests": self.run_tests(story_id=story_id),
                "performance": self.analyze_performance(story_id=story_id),
                "errors": self.extract_error_patterns(),
                "report": self.generate_qa_report(story_id or "unknown")
            }

    def close(self):
        """Clean up resources"""
        if self.sentry:
            self.sentry.close()
        if self.postgres:
            self.postgres.close()
        if self.log_analyzer:
            self.log_analyzer.close()
        if self.pattern_extractor:
            self.pattern_extractor.close()
        if self.dspy_optimizer:
            self.dspy_optimizer.close()
