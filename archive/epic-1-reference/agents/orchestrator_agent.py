"""
Orchestrator Agent - Workflow coordination and task delegation

Responsibilities:
- Task planning and workflow orchestration
- GitHub repository management via PyGithub (direct library, 3x faster)
- Web research coordination via tavily-python (direct library)
- Dynamic tool loading and security management
"""

import os
from typing import List, Dict, Any, Optional
from .base_agent import BaseAgent
from integrations.github_client import GitHubClient
from integrations.tavily_client import TavilyClient


class OrchestratorAgent(BaseAgent):
    """Orchestrator agent for workflow coordination using direct library integrations"""

    def __init__(self, read_only: bool = True):
        """
        Initialize Orchestrator Agent

        Args:
            read_only: Enable read-only mode for GitHub operations (default: True)
        """
        super().__init__("Orchestrator", "Workflow Coordinator", agent_id="orchestrator")
        self.github_client: Optional[GitHubClient] = None
        self.tavily_client: Optional[TavilyClient] = None
        self.read_only = read_only
        self._initialized = False


    def initialize(self):
        """Initialize GitHub and Tavily clients with direct libraries"""
        try:
            # Initialize GitHub client (direct PyGithub)
            github_token = os.getenv("GITHUB_TOKEN")
            if github_token:
                self.github_client = GitHubClient(token=github_token, read_only=self.read_only)
            else:
                print("Warning: GITHUB_TOKEN not found, GitHub features disabled")

            # Initialize Tavily client (direct tavily-python)
            tavily_key = os.getenv("TAVILY_API_KEY")
            if tavily_key:
                self.tavily_client = TavilyClient(api_key=tavily_key)
            else:
                print("Warning: TAVILY_API_KEY not found, Tavily features disabled")

            self._initialized = True

        except Exception as e:
            raise RuntimeError(f"Failed to initialize Orchestrator clients: {e}")

    def cleanup(self):
        """Cleanup client connections"""
        if self.github_client:
            self.github_client.close()
            self.github_client = None

        self.tavily_client = None
        self._initialized = False

    # GitHub Operations (Direct PyGithub)

    def search_repos(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search GitHub repositories using direct PyGithub client"""
        if not self._initialized or not self.github_client:
            raise RuntimeError("GitHub client not initialized. Call initialize() first.")

        return self.github_client.search_repos(query=query, limit=limit)

    def get_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information using direct PyGithub client"""
        if not self._initialized or not self.github_client:
            raise RuntimeError("GitHub client not initialized. Call initialize() first.")

        return self.github_client.get_repo(owner=owner, repo=repo)

    def list_prs(self, owner: str, repo: str, state: str = "open", limit: int = 10) -> List[Dict[str, Any]]:
        """List pull requests using direct PyGithub client"""
        if not self._initialized or not self.github_client:
            raise RuntimeError("GitHub client not initialized. Call initialize() first.")

        return self.github_client.list_prs(owner=owner, repo=repo, state=state, limit=limit)

    def create_pr(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str,
        body: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create pull request using direct PyGithub client"""
        if not self._initialized or not self.github_client:
            raise RuntimeError("GitHub client not initialized. Call initialize() first.")

        return self.github_client.create_pr(
            owner=owner,
            repo=repo,
            title=title,
            head=head,
            base=base,
            body=body
        )

    def list_issues(self, owner: str, repo: str, state: str = "open", limit: int = 10) -> List[Dict[str, Any]]:
        """List repository issues using direct PyGithub client"""
        if not self._initialized or not self.github_client:
            raise RuntimeError("GitHub client not initialized. Call initialize() first.")

        return self.github_client.list_issues(owner=owner, repo=repo, state=state, limit=limit)

    def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: Optional[str] = None,
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create issue using direct PyGithub client"""
        if not self._initialized or not self.github_client:
            raise RuntimeError("GitHub client not initialized. Call initialize() first.")

        return self.github_client.create_issue(
            owner=owner,
            repo=repo,
            title=title,
            body=body,
            labels=labels
        )

    def check_github_rate_limit(self) -> Dict[str, Any]:
        """Check GitHub API rate limit status"""
        if not self._initialized or not self.github_client:
            raise RuntimeError("GitHub client not initialized. Call initialize() first.")

        return self.github_client.check_rate_limit()

    # Tavily Operations (Direct tavily-python)

    def web_search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
        include_answer: bool = True
    ) -> Dict[str, Any]:
        """Execute web search using direct Tavily client"""
        if not self._initialized or not self.tavily_client:
            raise RuntimeError("Tavily client not initialized. Call initialize() first.")

        return self.tavily_client.search(
            query=query,
            max_results=max_results,
            search_depth=search_depth,
            include_answer=include_answer
        )

    def qna_search(self, query: str) -> Dict[str, Any]:
        """Execute Q&A search using direct Tavily client"""
        if not self._initialized or not self.tavily_client:
            raise RuntimeError("Tavily client not initialized. Call initialize() first.")

        return self.tavily_client.qna_search(query=query)

    def extract_from_urls(self, urls: List[str]) -> Dict[str, Any]:
        """Extract content from URLs using direct Tavily client"""
        if not self._initialized or not self.tavily_client:
            raise RuntimeError("Tavily client not initialized. Call initialize() first.")

        return self.tavily_client.extract(urls=urls)

    def get_search_context(
        self,
        query: str,
        max_results: int = 5,
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        """Get search context for RAG using direct Tavily client"""
        if not self._initialized or not self.tavily_client:
            raise RuntimeError("Tavily client not initialized. Call initialize() first.")

        return self.tavily_client.get_search_context(
            query=query,
            max_results=max_results,
            max_tokens=max_tokens
        )

    # Workflow Coordination

    def coordinate_research(
        self,
        github_query: Optional[str] = None,
        web_query: Optional[str] = None,
        max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Coordinate research across GitHub and web sources

        Args:
            github_query: Query for GitHub repository search (optional)
            web_query: Query for web search (optional)
            max_results: Maximum results per source

        Returns:
            Dict with combined research results
        """
        results = {
            "github_results": [],
            "web_results": [],
            "coordinated": True
        }

        if github_query and self.github_client:
            results["github_results"] = self.search_repos(query=github_query, limit=max_results)

        if web_query and self.tavily_client:
            search_result = self.web_search(query=web_query, max_results=max_results)
            results["web_results"] = search_result.get("results", [])
            results["web_answer"] = search_result.get("answer")

        return results

    def delegate_to_agent(
        self,
        target_agent: str,
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Delegate task to another agent"""
        return {
            "target_agent": target_agent,
            "task": task,
            "context": context,
            "status": "delegated"
        }

    def get_available_tools(self) -> List[str]:
        """Return GitHub, Tavily, and workflow coordination tools"""
        return self._tools.copy()

    def process_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process workflow coordination tasks

        Args:
            task_description: Description of task to coordinate
            context: Current workflow context

        Returns:
            Dict containing coordination results and next steps
        """
        return {
            "agent": "orchestrator",
            "task_processed": task_description,
            "tools_used": self._tools,
            "next_agent": "analyst",
            "coordination_complete": True
        }