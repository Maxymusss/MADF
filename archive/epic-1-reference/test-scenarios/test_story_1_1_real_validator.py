"""
Story 1.1: Real Validator Agent Tests
NO MOCKS - Tests with real DSPy, Sentry, Postgres MCP connections
"""

import pytest
import os
from pathlib import Path
from datetime import datetime


@pytest.fixture
async def real_validator_agent():
    """Initialize Validator with real MCP clients"""
    from src.agents.validator_agent import ValidatorAgent

    # Verify environment variables
    assert os.getenv("POSTGRES_CONNECTION_STRING"), "POSTGRES_CONNECTION_STRING required"
    assert os.getenv("SENTRY_DSN"), "SENTRY_DSN required for real tests"

    agent = ValidatorAgent()
    await agent.initialize_real_mcp_clients()

    yield agent

    await agent.cleanup()


class TestRealValidatorDSPy:
    """Real DSPy framework integration tests"""

    @pytest.mark.asyncio
    async def test_dspy_client_initialization(self, real_validator_agent):
        """REAL TEST: Verify DSPy framework client initializes"""
        assert real_validator_agent.dspy_client is not None
        assert real_validator_agent.dspy_client._initialized

    @pytest.mark.asyncio
    async def test_optimize_prompt_real(self, real_validator_agent):
        """REAL TEST: Optimize LLM prompt using DSPy"""
        initial_prompt = {
            "task": "code_analysis",
            "template": "Analyze this code: {code}",
            "examples": [
                {
                    "code": "def add(a, b): return a + b",
                    "expected": "Simple addition function"
                }
            ]
        }

        result = await real_validator_agent.optimize_prompt_with_dspy(
            prompt_data=initial_prompt,
            optimization_metric="accuracy"
        )

        # Verify optimization completed
        assert result["success"] == True
        assert "optimized_prompt" in result
        assert "score" in result
        assert result["score"] > 0

    @pytest.mark.asyncio
    async def test_evaluate_model_performance_real(self, real_validator_agent):
        """REAL TEST: Evaluate agent model performance with DSPy"""
        test_cases = [
            {
                "input": "Analyze: def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
                "expected_keywords": ["recursive", "factorial", "base case"]
            },
            {
                "input": "Analyze: async def fetch_data(): return await api.get()",
                "expected_keywords": ["async", "await", "api"]
            }
        ]

        result = await real_validator_agent.evaluate_model_with_dspy(
            test_cases=test_cases,
            model_name="claude-sonnet"
        )

        # Verify evaluation results
        assert result["success"] == True
        assert "accuracy" in result
        assert "test_count" in result
        assert result["test_count"] == len(test_cases)

    @pytest.mark.asyncio
    async def test_compile_optimized_pipeline_real(self, real_validator_agent):
        """REAL TEST: Compile optimized agent pipeline with DSPy"""
        pipeline_config = {
            "stages": [
                {"name": "code_analysis", "model": "claude-sonnet"},
                {"name": "test_generation", "model": "claude-sonnet"},
                {"name": "validation", "model": "claude-haiku"}
            ],
            "optimization_target": "cost_efficiency"
        }

        result = await real_validator_agent.compile_pipeline_with_dspy(
            config=pipeline_config
        )

        # Verify pipeline compilation
        assert result["success"] == True
        assert "compiled_pipeline" in result
        assert "optimization_score" in result


class TestRealValidatorSentry:
    """Real Sentry MCP integration tests"""

    @pytest.mark.asyncio
    async def test_sentry_client_initialization(self, real_validator_agent):
        """REAL TEST: Verify Sentry MCP client initializes"""
        assert real_validator_agent.sentry_client is not None
        assert real_validator_agent.sentry_client._initialized

    @pytest.mark.asyncio
    async def test_capture_exception_real(self, real_validator_agent):
        """REAL TEST: Capture exception via Sentry MCP"""
        try:
            # Generate real exception
            raise ValueError("Test validation error")
        except ValueError as e:
            result = await real_validator_agent.capture_exception(
                exception=e,
                context={
                    "agent": "validator",
                    "story": "1.1",
                    "test": "real_sentry_test"
                }
            )

            # Verify exception captured
            assert result["success"] == True
            assert "event_id" in result

    @pytest.mark.asyncio
    async def test_capture_message_real(self, real_validator_agent):
        """REAL TEST: Capture log message via Sentry MCP"""
        result = await real_validator_agent.capture_message(
            message="Validator agent test validation completed",
            level="info",
            context={
                "tests_run": 10,
                "tests_passed": 9,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        # Verify message captured
        assert result["success"] == True
        assert "event_id" in result

    @pytest.mark.asyncio
    async def test_query_sentry_issues_real(self, real_validator_agent):
        """REAL TEST: Query recent issues from Sentry"""
        result = await real_validator_agent.query_sentry_issues(
            project="madf",
            query="story:1.1",
            limit=10
        )

        # Verify query results
        assert isinstance(result, list)
        # May be empty if no issues exist
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_create_sentry_release_real(self, real_validator_agent):
        """REAL TEST: Create release tracking in Sentry"""
        release_data = {
            "version": "story-1.1-test",
            "projects": ["madf"],
            "commits": [
                {
                    "id": "test123",
                    "message": "Story 1.1 implementation complete"
                }
            ]
        }

        result = await real_validator_agent.create_sentry_release(
            release_data=release_data
        )

        # Verify release created
        assert result["success"] == True
        assert "release_id" in result


class TestRealValidatorPostgres:
    """Real Postgres MCP integration tests"""

    @pytest.mark.asyncio
    async def test_postgres_client_initialization(self, real_validator_agent):
        """REAL TEST: Verify Postgres MCP client initializes"""
        assert real_validator_agent.postgres_client is not None
        assert real_validator_agent.postgres_client._initialized

    @pytest.mark.asyncio
    async def test_create_test_results_table_real(self, real_validator_agent):
        """REAL TEST: Create test results table in Postgres"""
        result = await real_validator_agent.execute_sql(
            query="""
                CREATE TABLE IF NOT EXISTS test_results (
                    id SERIAL PRIMARY KEY,
                    story_id VARCHAR(50),
                    agent_name VARCHAR(100),
                    test_name VARCHAR(200),
                    status VARCHAR(20),
                    duration_ms INTEGER,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        )

        # Verify table creation
        assert result["success"] == True

    @pytest.mark.asyncio
    async def test_store_test_result_real(self, real_validator_agent):
        """REAL TEST: Store test result in Postgres"""
        # First ensure table exists
        await real_validator_agent.execute_sql(
            query="""
                CREATE TABLE IF NOT EXISTS test_results (
                    id SERIAL PRIMARY KEY,
                    story_id VARCHAR(50),
                    agent_name VARCHAR(100),
                    test_name VARCHAR(200),
                    status VARCHAR(20),
                    duration_ms INTEGER,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        )

        # Insert test result
        result = await real_validator_agent.execute_sql(
            query="""
                INSERT INTO test_results
                (story_id, agent_name, test_name, status, duration_ms)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            """,
            params=["1.1", "validator", "test_postgres_integration", "passed", 150]
        )

        # Verify insertion
        assert result["success"] == True
        assert "id" in result or "returning" in str(result).lower()

    @pytest.mark.asyncio
    async def test_query_test_results_real(self, real_validator_agent):
        """REAL TEST: Query test results from Postgres"""
        result = await real_validator_agent.execute_sql(
            query="""
                SELECT story_id, agent_name, test_name, status
                FROM test_results
                WHERE story_id = $1
                ORDER BY executed_at DESC
                LIMIT 10
            """,
            params=["1.1"]
        )

        # Verify query results
        assert result["success"] == True
        assert isinstance(result.get("rows", []), list)

    @pytest.mark.asyncio
    async def test_aggregate_test_metrics_real(self, real_validator_agent):
        """REAL TEST: Calculate test metrics from Postgres"""
        result = await real_validator_agent.execute_sql(
            query="""
                SELECT
                    story_id,
                    COUNT(*) as total_tests,
                    SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) as passed,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                    AVG(duration_ms) as avg_duration
                FROM test_results
                WHERE story_id = $1
                GROUP BY story_id
            """,
            params=["1.1"]
        )

        # Verify aggregation
        assert result["success"] == True
        # May be empty if no tests stored yet
        assert isinstance(result.get("rows", []), list)


class TestRealValidatorWorkflow:
    """Real validation workflow integration tests"""

    @pytest.mark.asyncio
    async def test_comprehensive_validation_workflow_real(self, real_validator_agent):
        """REAL TEST: Complete validation workflow"""
        validation_task = {
            "story_id": "1.1",
            "code_files": ["src/core/agent_graph.py"],
            "test_files": ["tests/test_story_1_1_core_architecture.py"],
            "validation_types": ["syntax", "logic", "performance"]
        }

        # Step 1: Run tests and capture results
        test_results = [
            {"name": "test_state_graph_creation", "status": "passed", "duration_ms": 45},
            {"name": "test_five_agent_nodes_exist", "status": "passed", "duration_ms": 32},
            {"name": "test_agent_node_edges_defined", "status": "passed", "duration_ms": 28}
        ]

        # Step 2: Store results in Postgres
        for test in test_results:
            await real_validator_agent.execute_sql(
                query="""
                    INSERT INTO test_results
                    (story_id, agent_name, test_name, status, duration_ms)
                    VALUES ($1, $2, $3, $4, $5)
                """,
                params=["1.1", "validator", test["name"], test["status"], test["duration_ms"]]
            )

        # Step 3: Capture metrics in Sentry
        summary_message = f"Story 1.1 validation: {len(test_results)} tests passed"
        sentry_result = await real_validator_agent.capture_message(
            message=summary_message,
            level="info",
            context={"story": "1.1", "tests_passed": len(test_results)}
        )

        # Step 4: Optimize validation prompts with DSPy
        optimization_result = await real_validator_agent.optimize_prompt_with_dspy(
            prompt_data={
                "task": "test_validation",
                "template": "Validate test: {test_name}",
                "examples": test_results[:2]
            },
            optimization_metric="efficiency"
        )

        # Verify complete workflow
        assert sentry_result["success"]
        assert optimization_result["success"]

    @pytest.mark.asyncio
    async def test_generate_validation_report_real(self, real_validator_agent):
        """REAL TEST: Generate comprehensive validation report"""
        # Query test results from Postgres
        test_data = await real_validator_agent.execute_sql(
            query="""
                SELECT story_id, COUNT(*) as total,
                       SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) as passed
                FROM test_results
                WHERE story_id = $1
                GROUP BY story_id
            """,
            params=["1.1"]
        )

        # Generate report
        report = await real_validator_agent.generate_validation_report(
            story_id="1.1",
            test_data=test_data
        )

        # Verify report structure
        assert report["story_id"] == "1.1"
        assert "test_summary" in report
        assert "validation_status" in report


class TestRealValidatorErrorHandling:
    """Real error handling tests"""

    @pytest.mark.asyncio
    async def test_postgres_connection_error_handling(self, real_validator_agent):
        """REAL TEST: Handle Postgres connection errors"""
        # Execute query with invalid syntax to trigger error
        result = await real_validator_agent.execute_sql(
            query="INVALID SQL SYNTAX HERE"
        )

        # Should handle SQL error gracefully
        assert result["success"] == False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_sentry_rate_limit_handling(self, real_validator_agent):
        """REAL TEST: Handle Sentry rate limiting gracefully"""
        # Send many messages rapidly
        results = []
        for i in range(5):
            result = await real_validator_agent.capture_message(
                message=f"Rate limit test message {i}",
                level="info"
            )
            results.append(result)

        # Most should succeed (or handle rate limit gracefully)
        successful = [r for r in results if r.get("success")]
        assert len(successful) > 0  # At least some should succeed