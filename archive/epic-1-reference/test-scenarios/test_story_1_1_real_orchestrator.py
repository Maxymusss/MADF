"""
Story 1.1: Real Orchestrator Agent Tests
NO MOCKS - Tests with real GitHub and Tavily MCP connections
"""

import pytest
import os
from pathlib import Path

# Real MCP client imports (requires mcp-use or direct MCP SDK)
# Following Story 1.3 pattern for real integrations


@pytest.fixture
async def real_orchestrator_agent():
    """Initialize Orchestrator with real MCP clients"""
    from src.agents.orchestrator_agent import OrchestratorAgent

    # Verify environment variables exist
    assert os.getenv("GITHUB_TOKEN"), "GITHUB_TOKEN required for real tests"
    assert os.getenv("TAVILY_API_KEY"), "TAVILY_API_KEY required for real tests"

    agent = OrchestratorAgent()
    await agent.initialize_real_mcp_clients()

    yield agent

    # Cleanup
    await agent.cleanup()


class TestRealOrchestratorGitHub:
    """Real GitHub MCP integration tests"""

    @pytest.mark.asyncio
    async def test_github_client_initialization(self, real_orchestrator_agent):
        """REAL TEST: Verify GitHub MCP client initializes"""
        assert real_orchestrator_agent.github_client is not None
        assert real_orchestrator_agent.github_client._initialized

    @pytest.mark.asyncio
    async def test_search_github_repos_real(self, real_orchestrator_agent):
        """REAL TEST: Search GitHub repositories via MCP"""
        result = await real_orchestrator_agent.search_github_repos(
            query="langgraph python",
            limit=5
        )

        # Verify real API response
        assert isinstance(result, list)
        assert len(result) > 0

        # Validate response structure
        first_repo = result[0]
        assert "name" in first_repo
        assert "full_name" in first_repo
        assert "url" in first_repo
        assert "description" in first_repo

    @pytest.mark.asyncio
    async def test_get_repo_info_real(self, real_orchestrator_agent):
        """REAL TEST: Get repository information via GitHub MCP"""
        result = await real_orchestrator_agent.get_repo_info(
            owner="langchain-ai",
            repo="langgraph"
        )

        # Verify actual repo data
        assert result["name"] == "langgraph"
        assert result["owner"]["login"] == "langchain-ai"
        assert "description" in result
        assert "stars" in result or "stargazers_count" in result

    @pytest.mark.asyncio
    async def test_list_repo_files_real(self, real_orchestrator_agent):
        """REAL TEST: List repository files via GitHub MCP"""
        result = await real_orchestrator_agent.list_repo_files(
            owner="langchain-ai",
            repo="langgraph",
            path="langgraph"
        )

        # Verify file listing
        assert isinstance(result, list)
        assert len(result) > 0
        assert any(f["name"] == "graph.py" for f in result if isinstance(f, dict))


class TestRealOrchestratorTavily:
    """Real Tavily MCP integration tests"""

    @pytest.mark.asyncio
    async def test_tavily_client_initialization(self, real_orchestrator_agent):
        """REAL TEST: Verify Tavily MCP client initializes"""
        assert real_orchestrator_agent.tavily_client is not None
        assert real_orchestrator_agent.tavily_client._initialized

    @pytest.mark.asyncio
    async def test_web_search_real(self, real_orchestrator_agent):
        """REAL TEST: Execute web search via Tavily MCP"""
        result = await real_orchestrator_agent.web_search(
            query="LangGraph multi-agent systems",
            max_results=5
        )

        # Verify real search results
        assert isinstance(result, list)
        assert len(result) > 0

        # Validate result structure
        first_result = result[0]
        assert "title" in first_result
        assert "url" in first_result
        assert "content" in first_result

    @pytest.mark.asyncio
    async def test_deep_search_real(self, real_orchestrator_agent):
        """REAL TEST: Execute deep web search with content extraction"""
        result = await real_orchestrator_agent.web_search(
            query="LangGraph StateGraph documentation",
            max_results=3,
            search_depth="advanced"
        )

        # Verify deep search returns detailed content
        assert isinstance(result, list)
        assert len(result) > 0

        # Advanced search should have more detailed content
        first_result = result[0]
        assert len(first_result.get("content", "")) > 100


class TestRealOrchestratorWorkflow:
    """Real workflow coordination tests"""

    @pytest.mark.asyncio
    async def test_research_task_coordination_real(self, real_orchestrator_agent):
        """REAL TEST: Coordinate research using GitHub + Tavily"""
        # Step 1: Search GitHub for relevant repositories
        github_results = await real_orchestrator_agent.search_github_repos(
            query="langgraph examples",
            limit=3
        )

        assert len(github_results) > 0
        repo_name = github_results[0]["name"]

        # Step 2: Search web for documentation
        web_results = await real_orchestrator_agent.web_search(
            query=f"{repo_name} documentation tutorial",
            max_results=3
        )

        assert len(web_results) > 0

        # Step 3: Coordinate results
        coordination_result = await real_orchestrator_agent.coordinate_research(
            github_data=github_results,
            web_data=web_results,
            task="Find LangGraph implementation examples"
        )

        # Verify coordination output
        assert coordination_result["github_repos_found"] == len(github_results)
        assert coordination_result["web_results_found"] == len(web_results)
        assert "recommendations" in coordination_result

    @pytest.mark.asyncio
    async def test_delegate_to_analyst_real(self, real_orchestrator_agent):
        """REAL TEST: Orchestrator delegates to Analyst agent"""
        # Gather research data
        github_results = await real_orchestrator_agent.search_github_repos(
            query="langgraph",
            limit=1
        )

        # Create delegation context
        delegation = await real_orchestrator_agent.delegate_to_agent(
            target_agent="analyst",
            task="Analyze LangGraph repository structure",
            context={
                "repo_url": github_results[0]["url"],
                "repo_name": github_results[0]["name"]
            }
        )

        # Verify delegation
        assert delegation["target_agent"] == "analyst"
        assert delegation["status"] == "delegated"
        assert "context" in delegation


class TestRealOrchestratorErrorHandling:
    """Real error handling and recovery tests"""

    @pytest.mark.asyncio
    async def test_github_rate_limit_handling(self, real_orchestrator_agent):
        """REAL TEST: Handle GitHub API rate limits"""
        # This test may fail if rate limit is exceeded
        try:
            result = await real_orchestrator_agent.search_github_repos(
                query="python",
                limit=100  # Large request
            )
            assert isinstance(result, list)
        except Exception as e:
            # Should handle rate limit gracefully
            assert "rate limit" in str(e).lower() or "403" in str(e)

    @pytest.mark.asyncio
    async def test_invalid_repo_handling(self, real_orchestrator_agent):
        """REAL TEST: Handle invalid repository requests"""
        with pytest.raises(Exception) as exc_info:
            await real_orchestrator_agent.get_repo_info(
                owner="nonexistent_owner_12345",
                repo="nonexistent_repo_67890"
            )

        # Verify appropriate error (404 or similar)
        assert "404" in str(exc_info.value) or "not found" in str(exc_info.value).lower()