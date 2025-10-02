"""
Story 1.5: Real Integration Tests for Orchestrator Agent with GitHub + Tavily

Tests direct PyGithub and tavily-python integrations (NO MOCKS)
"""

import os
import pytest
from dotenv import load_dotenv
from src.agents.orchestrator_agent import OrchestratorAgent

# Load test environment
load_dotenv(".env.test")
load_dotenv(".env")  # Fallback to main .env

# Skip markers for missing credentials
skip_github = pytest.mark.skipif(
    not os.getenv("GITHUB_TOKEN"),
    reason="GITHUB_TOKEN not configured - add to .env file"
)
skip_tavily = pytest.mark.skipif(
    not os.getenv("TAVILY_API_KEY"),
    reason="TAVILY_API_KEY not configured - add to .env file"
)


@skip_github
class TestTask1GitHubIntegration:
    """Task 1: GitHub Integration via PyGithub"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator agent with read-only mode"""
        agent = OrchestratorAgent(read_only=True)
        agent.initialize()
        yield agent
        agent.cleanup()

    def test_github_client_initialization(self, orchestrator):
        """Test GitHub client initializes correctly"""
        assert orchestrator.github_client is not None
        assert orchestrator.github_client.read_only is True
        assert orchestrator._initialized is True

    def test_search_repos(self, orchestrator):
        """Test GitHub repository search"""
        results = orchestrator.search_repos(query="langgraph", limit=3)

        assert isinstance(results, list)
        assert len(results) > 0
        assert len(results) <= 3

        # Validate result structure
        first_result = results[0]
        assert "name" in first_result
        assert "full_name" in first_result
        assert "owner" in first_result
        assert "stars" in first_result
        assert "url" in first_result

    def test_get_repo(self, orchestrator):
        """Test get repository information"""
        result = orchestrator.get_repo(owner="langchain-ai", repo="langgraph")

        assert isinstance(result, dict)
        assert result.get("name") == "langgraph"
        assert result.get("owner") == "langchain-ai"
        assert "stars" in result
        assert "url" in result

    def test_list_prs(self, orchestrator):
        """Test list pull requests"""
        results = orchestrator.list_prs(
            owner="langchain-ai",
            repo="langgraph",
            state="closed",
            limit=3
        )

        assert isinstance(results, list)
        # May be empty if no PRs, but should be a list
        if len(results) > 0:
            first_pr = results[0]
            assert "number" in first_pr
            assert "title" in first_pr
            assert "state" in first_pr
            assert "url" in first_pr

    def test_list_issues(self, orchestrator):
        """Test list repository issues"""
        results = orchestrator.list_issues(
            owner="langchain-ai",
            repo="langgraph",
            state="closed",
            limit=3
        )

        assert isinstance(results, list)
        if len(results) > 0:
            first_issue = results[0]
            assert "number" in first_issue
            assert "title" in first_issue
            assert "state" in first_issue
            assert "url" in first_issue

    def test_check_rate_limit(self, orchestrator):
        """Test GitHub rate limit checking"""
        result = orchestrator.check_github_rate_limit()

        assert isinstance(result, dict)
        assert "limit" in result
        assert "remaining" in result
        assert "used" in result
        assert result["limit"] > 0
        assert result["remaining"] >= 0

    def test_read_only_mode_blocks_writes(self, orchestrator):
        """Test read-only mode prevents write operations"""
        with pytest.raises(PermissionError, match="read-only mode"):
            orchestrator.create_issue(
                owner="test",
                repo="test",
                title="Test Issue"
            )

        with pytest.raises(PermissionError, match="read-only mode"):
            orchestrator.create_pr(
                owner="test",
                repo="test",
                title="Test PR",
                head="test",
                base="main"
            )


@skip_tavily
class TestTask2TavilyIntegration:
    """Task 2: Tavily Integration via tavily-python"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator agent"""
        agent = OrchestratorAgent()
        agent.initialize()
        yield agent
        agent.cleanup()

    def test_tavily_client_initialization(self, orchestrator):
        """Test Tavily client initializes correctly"""
        assert orchestrator.tavily_client is not None
        assert orchestrator._initialized is True

    def test_web_search(self, orchestrator):
        """Test Tavily web search"""
        result = orchestrator.web_search(
            query="langgraph multi-agent framework",
            max_results=3,
            include_answer=True
        )

        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "results" in result
        assert len(result["results"]) > 0

        # Validate result structure
        first_result = result["results"][0]
        assert "title" in first_result
        assert "url" in first_result
        assert "content" in first_result
        assert "score" in first_result

        # Check if answer included
        if result.get("answer"):
            assert isinstance(result["answer"], str)
            assert len(result["answer"]) > 0

    def test_qna_search(self, orchestrator):
        """Test Tavily Q&A search"""
        result = orchestrator.qna_search(query="What is LangGraph used for?")

        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "answer" in result
        assert isinstance(result["answer"], str)
        assert len(result["answer"]) > 0

    def test_get_search_context(self, orchestrator):
        """Test Tavily search context for RAG"""
        result = orchestrator.get_search_context(
            query="langgraph agent patterns",
            max_results=3,
            max_tokens=1000
        )

        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "context" in result
        assert isinstance(result["context"], str)
        assert len(result["context"]) > 0

    def test_extract_from_urls(self, orchestrator):
        """Test Tavily URL content extraction"""
        urls = [
            "https://github.com/langchain-ai/langgraph",
        ]

        result = orchestrator.extract_from_urls(urls=urls)

        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "results" in result
        assert len(result["results"]) == len(urls)

        # Validate extraction result structure
        first_result = result["results"][0]
        assert "url" in first_result
        assert "raw_content" in first_result


@pytest.mark.skipif(
    not (os.getenv("GITHUB_TOKEN") and os.getenv("TAVILY_API_KEY")),
    reason="Requires both GITHUB_TOKEN and TAVILY_API_KEY"
)
class TestTask3OrchestratorCoordination:
    """Task 3: Orchestrator Agent Coordination"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator agent"""
        agent = OrchestratorAgent(read_only=True)
        agent.initialize()
        yield agent
        agent.cleanup()

    def test_coordinate_research_github_only(self, orchestrator):
        """Test research coordination with GitHub only"""
        result = orchestrator.coordinate_research(
            github_query="langgraph",
            max_results=3
        )

        assert isinstance(result, dict)
        assert result.get("coordinated") is True
        assert "github_results" in result
        assert len(result["github_results"]) > 0
        assert len(result["web_results"]) == 0

    def test_coordinate_research_web_only(self, orchestrator):
        """Test research coordination with web search only"""
        result = orchestrator.coordinate_research(
            web_query="langgraph tutorials",
            max_results=3
        )

        assert isinstance(result, dict)
        assert result.get("coordinated") is True
        assert "web_results" in result
        assert len(result["web_results"]) > 0
        assert len(result["github_results"]) == 0

    def test_coordinate_research_both_sources(self, orchestrator):
        """Test research coordination with both GitHub and web"""
        result = orchestrator.coordinate_research(
            github_query="langgraph",
            web_query="langgraph multi-agent tutorials",
            max_results=3
        )

        assert isinstance(result, dict)
        assert result.get("coordinated") is True
        assert "github_results" in result
        assert "web_results" in result
        assert len(result["github_results"]) > 0
        assert len(result["web_results"]) > 0

        # Check for web answer
        if "web_answer" in result:
            assert isinstance(result["web_answer"], str)

    def test_delegate_to_agent(self, orchestrator):
        """Test agent delegation"""
        result = orchestrator.delegate_to_agent(
            target_agent="analyst",
            task="Analyze repository structure",
            context={"repo": "langchain-ai/langgraph"}
        )

        assert isinstance(result, dict)
        assert result.get("target_agent") == "analyst"
        assert result.get("task") == "Analyze repository structure"
        assert result.get("status") == "delegated"

    def test_get_available_tools(self, orchestrator):
        """Test tool listing"""
        tools = orchestrator.get_available_tools()

        assert isinstance(tools, list)
        assert "github_repos" in tools
        assert "github_prs" in tools
        assert "github_issues" in tools
        assert "tavily_search" in tools
        assert "tavily_extract" in tools
        assert "workflow_control" in tools


@pytest.mark.skipif(
    not (os.getenv("GITHUB_TOKEN") and os.getenv("TAVILY_API_KEY")),
    reason="Requires both GITHUB_TOKEN and TAVILY_API_KEY"
)
class TestTask4EndToEndIntegration:
    """Task 4: End-to-End Integration Testing"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator agent"""
        agent = OrchestratorAgent(read_only=True)
        agent.initialize()
        yield agent
        agent.cleanup()

    def test_full_research_workflow(self, orchestrator):
        """Test complete research workflow"""
        # Step 1: Search GitHub for repositories
        github_results = orchestrator.search_repos(query="pytest", limit=2)
        assert len(github_results) > 0

        # Step 2: Get detailed info on first repo
        first_repo = github_results[0]
        owner, repo_name = first_repo["full_name"].split("/")
        repo_details = orchestrator.get_repo(owner=owner, repo=repo_name)
        assert repo_details.get("name") == repo_name

        # Step 3: Search web for related information
        web_results = orchestrator.web_search(
            query=f"{repo_name} documentation",
            max_results=3
        )
        assert web_results.get("success") is True

        # Step 4: Coordinate all results
        coordinated = orchestrator.coordinate_research(
            github_query="pytest",
            web_query="pytest best practices",
            max_results=2
        )
        assert coordinated.get("coordinated") is True

    def test_error_handling_invalid_repo(self, orchestrator):
        """Test error handling for invalid repository"""
        result = orchestrator.get_repo(
            owner="nonexistent-owner-12345",
            repo="nonexistent-repo-67890"
        )

        # Should return error in result dict, not raise exception
        assert isinstance(result, dict)
        assert "error" in result or result.get("name") is None

    def test_error_handling_uninitialized_client(self):
        """Test error handling when client not initialized"""
        agent = OrchestratorAgent()
        # Don't initialize

        with pytest.raises(RuntimeError, match="not initialized"):
            agent.search_repos(query="test")

        with pytest.raises(RuntimeError, match="not initialized"):
            agent.web_search(query="test")

    def test_performance_direct_vs_mcp(self, orchestrator):
        """Test performance of direct library vs MCP bridge approach"""
        import time

        # Measure direct library performance
        start = time.time()
        orchestrator.search_repos(query="python", limit=5)
        direct_time = time.time() - start

        # Direct library should be reasonably fast (< 2 seconds)
        assert direct_time < 2.0

        print(f"\nDirect library search time: {direct_time:.3f}s")

    def test_security_boundaries(self, orchestrator):
        """Test security boundary enforcement"""
        # Read-only mode should be enforced
        assert orchestrator.read_only is True

        # Write operations should fail
        with pytest.raises(PermissionError):
            orchestrator.github_client.create_issue(
                owner="test",
                repo="test",
                title="Test"
            )

    def test_rate_limit_awareness(self, orchestrator):
        """Test rate limit monitoring"""
        # Check rate limit before operations
        initial_limit = orchestrator.check_github_rate_limit()

        # Perform operation
        orchestrator.search_repos(query="test", limit=1)

        # Check rate limit after
        after_limit = orchestrator.check_github_rate_limit()

        # Remaining should decrease (or stay same if cached)
        assert after_limit["remaining"] <= initial_limit["remaining"]
