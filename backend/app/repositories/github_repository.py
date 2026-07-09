"""
GitHub Repository
Middle layer between the router and the GitHub service.
"""

from app.services.github_service import GitHubService


class GitHubRepository:
    """Repository layer for GitHub-related data operations."""

    def __init__(self, github_service: GitHubService) -> None:
        """
        Args:
            github_service: Injected GitHubService instance (via FastAPI Depends).
        """
        self.github = github_service

    async def get_repo(self, owner: str, repo: str) -> dict:
        """
        Returns:
            dict: Raw repository data from GitHub API.
        """
        return await self.github.get_repository(owner, repo)