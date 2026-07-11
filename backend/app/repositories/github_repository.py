"""
GitHub Repository
-----------------
Middle layer between the router and the GitHub service.

Currently a thin pass-through, but this is where you'll add:
  • Caching (avoid hitting GitHub for the same data repeatedly)
  • Database persistence (save results for analytics)
  • Data transformation / enrichment

Receives GitHubService via constructor — dependency injection.
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

    # Repository details 

    async def get_repo(self, owner: str, repo: str) -> dict:
        """Fetch repository metadata."""
        return await self.github.get_repository(owner, repo)

    # Contributors 

    async def get_contributors(
        self, owner: str, repo: str, page: int = 1, per_page: int = 30,
    ) -> tuple[list[dict], int]:
        """
        Fetch repository contributors.

        Returns:
            tuple: (list_of_contributors, total_pages)
        """
        return await self.github.get_contributors(owner, repo, page, per_page)

    # Commits 

    async def get_commits(
        self, owner: str, repo: str, page: int = 1, per_page: int = 30,
    ) -> tuple[list[dict], int]:
        """
        Fetch repository commits (most recent first).

        Returns:
            tuple: (list_of_commits, total_pages)
        """
        return await self.github.get_commits(owner, repo, page, per_page)

    # Languages 

    async def get_languages(self, owner: str, repo: str) -> dict:
        """
        Fetch repository language breakdown.

        Returns:
            dict: {language_name: bytes_of_code}
        """
        return await self.github.get_languages(owner, repo)

    # Pull Requests 

    async def get_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        page: int = 1,
        per_page: int = 30,
    ) -> tuple[list[dict], int]:
        """
        Fetch repository pull requests.

        Returns:
            tuple: (list_of_pull_requests, total_pages)
        """
        return await self.github.get_pull_requests(
            owner, repo, state, page, per_page,
        )

    # Issues 

    async def get_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        page: int = 1,
        per_page: int = 30,
    ) -> tuple[list[dict], int]:
        """
        Fetch repository issues (PRs filtered out by the service layer).

        Returns:
            tuple: (list_of_issues, total_pages)
        """
        return await self.github.get_issues(
            owner, repo, state, page, per_page,
        )