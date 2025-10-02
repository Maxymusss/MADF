"""
GitHub Client - Direct PyGithub integration for repository operations

Uses PyGithub library for 3x performance over MCP bridge (per ADR-001)
"""

import os
from typing import List, Dict, Any, Optional
from github import Github, Auth, GithubException
from github.Repository import Repository
from github.PullRequest import PullRequest
from github.Issue import Issue


class GitHubClient:
    """Direct GitHub integration via PyGithub library"""

    def __init__(self, token: Optional[str] = None, read_only: bool = True):
        """
        Initialize GitHub client

        Args:
            token: GitHub personal access token (defaults to GITHUB_TOKEN env var)
            read_only: Enable read-only mode for safety (default: True)
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GitHub token required (GITHUB_TOKEN env var or token parameter)")

        self.read_only = read_only
        auth = Auth.Token(self.token)
        self.client = Github(auth=auth)
        self._rate_limit_checked = False

    def close(self):
        """Close GitHub client connection"""
        if self.client:
            self.client.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    def check_rate_limit(self) -> Dict[str, Any]:
        """
        Check GitHub API rate limit status

        Returns:
            Dict with rate limit info (limit, remaining, reset_time)
        """
        rate_limit = self.client.get_rate_limit()

        # PyGithub returns RateLimit.Rate object, access via resources.core
        core = rate_limit.core if hasattr(rate_limit, 'core') else rate_limit.resources.core

        return {
            "limit": core.limit,
            "remaining": core.remaining,
            "reset": core.reset.isoformat(),
            "used": core.limit - core.remaining
        }

    def _check_write_permission(self, operation: str):
        """Validate write operations against read-only mode"""
        if self.read_only:
            raise PermissionError(
                f"Operation '{operation}' blocked: Client in read-only mode. "
                "Set read_only=False to enable write operations."
            )

    # Repository Operations

    def get_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get repository information

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Dict with repository details
        """
        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            return self._format_repo(repository)
        except GithubException as e:
            return {"error": str(e), "status": e.status}

    def list_repos(self, username: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List user repositories

        Args:
            username: GitHub username (defaults to authenticated user)
            limit: Maximum repositories to return

        Returns:
            List of repository dicts
        """
        try:
            if username:
                user = self.client.get_user(username)
            else:
                user = self.client.get_user()

            repos = user.get_repos()
            return [self._format_repo(repo) for repo in repos[:limit]]
        except GithubException as e:
            return [{"error": str(e), "status": e.status}]

    def search_repos(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search GitHub repositories

        Args:
            query: Search query string
            limit: Maximum results to return

        Returns:
            List of matching repository dicts
        """
        try:
            repos = self.client.search_repositories(query=query)
            return [self._format_repo(repo) for repo in repos[:limit]]
        except GithubException as e:
            return [{"error": str(e), "status": e.status}]

    def get_repo_contents(self, owner: str, repo: str, path: str = "") -> List[Dict[str, Any]]:
        """
        List repository contents at path

        Args:
            owner: Repository owner
            repo: Repository name
            path: Path within repository (default: root)

        Returns:
            List of file/directory dicts
        """
        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            contents = repository.get_contents(path)

            # Handle single file vs directory
            if not isinstance(contents, list):
                contents = [contents]

            return [
                {
                    "name": item.name,
                    "path": item.path,
                    "type": item.type,
                    "size": item.size,
                    "sha": item.sha,
                    "url": item.html_url
                }
                for item in contents
            ]
        except GithubException as e:
            return [{"error": str(e), "status": e.status}]

    # Pull Request Operations

    def get_pr(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """
        Get pull request details

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number

        Returns:
            Dict with PR details
        """
        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            pr = repository.get_pull(pr_number)
            return self._format_pr(pr)
        except GithubException as e:
            return {"error": str(e), "status": e.status}

    def list_prs(self, owner: str, repo: str, state: str = "open", limit: int = 10) -> List[Dict[str, Any]]:
        """
        List pull requests

        Args:
            owner: Repository owner
            repo: Repository name
            state: PR state (open/closed/all)
            limit: Maximum PRs to return

        Returns:
            List of PR dicts
        """
        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            prs = repository.get_pulls(state=state)
            return [self._format_pr(pr) for pr in prs[:limit]]
        except GithubException as e:
            return [{"error": str(e), "status": e.status}]

    def create_pr(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str,
        body: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create pull request

        Args:
            owner: Repository owner
            repo: Repository name
            title: PR title
            head: Head branch
            base: Base branch
            body: PR description

        Returns:
            Dict with created PR details
        """
        self._check_write_permission("create_pr")

        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            pr = repository.create_pull(
                title=title,
                body=body or "",
                head=head,
                base=base
            )
            return self._format_pr(pr)
        except GithubException as e:
            return {"error": str(e), "status": e.status}

    def merge_pr(self, owner: str, repo: str, pr_number: int, commit_message: Optional[str] = None) -> Dict[str, Any]:
        """
        Merge pull request

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            commit_message: Optional merge commit message

        Returns:
            Dict with merge result
        """
        self._check_write_permission("merge_pr")

        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            pr = repository.get_pull(pr_number)
            result = pr.merge(commit_message=commit_message)

            return {
                "merged": result.merged,
                "sha": result.sha,
                "message": result.message
            }
        except GithubException as e:
            return {"error": str(e), "status": e.status}

    # Issue Operations

    def get_issue(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        """
        Get issue details

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number

        Returns:
            Dict with issue details
        """
        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            issue = repository.get_issue(issue_number)
            return self._format_issue(issue)
        except GithubException as e:
            return {"error": str(e), "status": e.status}

    def list_issues(self, owner: str, repo: str, state: str = "open", limit: int = 10) -> List[Dict[str, Any]]:
        """
        List repository issues

        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state (open/closed/all)
            limit: Maximum issues to return

        Returns:
            List of issue dicts
        """
        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            issues = repository.get_issues(state=state)
            return [self._format_issue(issue) for issue in issues[:limit]]
        except GithubException as e:
            return [{"error": str(e), "status": e.status}]

    def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: Optional[str] = None,
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create issue

        Args:
            owner: Repository owner
            repo: Repository name
            title: Issue title
            body: Issue description
            labels: List of label names

        Returns:
            Dict with created issue details
        """
        self._check_write_permission("create_issue")

        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            issue = repository.create_issue(
                title=title,
                body=body or "",
                labels=labels or []
            )
            return self._format_issue(issue)
        except GithubException as e:
            return {"error": str(e), "status": e.status}

    def update_issue(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        state: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update issue

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number
            title: New title (optional)
            body: New body (optional)
            state: New state (open/closed, optional)

        Returns:
            Dict with updated issue details
        """
        self._check_write_permission("update_issue")

        try:
            repository = self.client.get_repo(f"{owner}/{repo}")
            issue = repository.get_issue(issue_number)

            if title is not None:
                issue.edit(title=title)
            if body is not None:
                issue.edit(body=body)
            if state is not None:
                issue.edit(state=state)

            return self._format_issue(issue)
        except GithubException as e:
            return {"error": str(e), "status": e.status}

    # Formatting Helpers

    @staticmethod
    def _format_repo(repo: Repository) -> Dict[str, Any]:
        """Format repository object to dict"""
        return {
            "name": repo.name,
            "full_name": repo.full_name,
            "owner": repo.owner.login,
            "description": repo.description,
            "url": repo.html_url,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "language": repo.language,
            "created_at": repo.created_at.isoformat() if repo.created_at else None,
            "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
            "private": repo.private
        }

    @staticmethod
    def _format_pr(pr: PullRequest) -> Dict[str, Any]:
        """Format pull request object to dict"""
        return {
            "number": pr.number,
            "title": pr.title,
            "body": pr.body,
            "state": pr.state,
            "user": pr.user.login,
            "head": pr.head.ref,
            "base": pr.base.ref,
            "url": pr.html_url,
            "created_at": pr.created_at.isoformat() if pr.created_at else None,
            "updated_at": pr.updated_at.isoformat() if pr.updated_at else None,
            "merged": pr.merged,
            "mergeable": pr.mergeable
        }

    @staticmethod
    def _format_issue(issue: Issue) -> Dict[str, Any]:
        """Format issue object to dict"""
        return {
            "number": issue.number,
            "title": issue.title,
            "body": issue.body,
            "state": issue.state,
            "user": issue.user.login,
            "labels": [label.name for label in issue.labels],
            "url": issue.html_url,
            "created_at": issue.created_at.isoformat() if issue.created_at else None,
            "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
            "closed_at": issue.closed_at.isoformat() if issue.closed_at else None
        }
