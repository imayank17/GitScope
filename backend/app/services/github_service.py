"""
GitHub API Service
"""

import re

import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class GitHubService:
    """Async wrapper around the GitHub REST API."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        
        self.client = client
        self.base_url = settings.GITHUB_API_BASE_URL

        # Build headers — token is optional
        self.headers: dict[str, str] = {
            "Accept": "application/vnd.github+json",
        }
        if settings.GITHUB_TOKEN:
            self.headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"


    # Private helpers


    def _handle_error(self, exc: httpx.HTTPStatusError, context: str) -> None:
       
        status_code = exc.response.status_code

        if status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{context} not found on GitHub.",
            )
        elif status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid GitHub token. Check your GITHUB_TOKEN in .env.",
            )
        elif status_code == 403:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="GitHub API rate limit exceeded or access denied. "
                       "Add a GITHUB_TOKEN to .env for higher limits.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"GitHub API returned an error (HTTP {status_code}).",
            )

    def _parse_total_pages(self, link_header: str | None) -> int:
        """
        Parse GitHub's Link header to extract total page count.

        GitHub returns headers like:
          Link: <...?page=2>; rel="next", <...?page=5>; rel="last"
        """
        if not link_header:
            return 1

        # Look for rel="last" and extract the page number
        match = re.search(r'[?&]page=(\d+)[^>]*>;\s*rel="last"', link_header)
        if match:
            return int(match.group(1))

        return 1

    async def _get_paginated(
        self,
        url: str,
        page: int,
        per_page: int,
        context: str,
        extra_params: dict | None = None,
    ) -> tuple[list[dict], int]:
        """
        Generic paginated GET request to GitHub API.

        Args:
            url:          Full API URL (e.g. https://api.github.com/repos/x/y/commits)
            page:         Page number (1-indexed).
            per_page:     Results per page (max 100).
            context:      Human-readable context for error messages.
            extra_params: Additional query params (e.g. {"state": "open"}).

        Returns:
            tuple: (list_of_items, total_pages)
        """
        params: dict = {"page": page, "per_page": per_page}
        if extra_params:
            params.update(extra_params)

        try:
            response = await self.client.get(
                url, headers=self.headers, params=params,
            )
            response.raise_for_status()

            items = response.json()
            total_pages = self._parse_total_pages(
                response.headers.get("Link")
            )

            return items, total_pages

        except httpx.HTTPStatusError as exc:
            self._handle_error(exc, context)

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Could not connect to GitHub API: {str(exc)}",
            )

  
    # Public API methods

    async def get_repository(self, owner: str, repo: str) -> dict:
        """Fetch repository metadata."""
        url = f"{self.base_url}/repos/{owner}/{repo}"

        try:
            response = await self.client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as exc:
            self._handle_error(exc, f"Repository '{owner}/{repo}'")

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Could not connect to GitHub API: {str(exc)}",
            )

    async def get_contributors(
        self, owner: str, repo: str, page: int = 1, per_page: int = 30,
    ) -> tuple[list[dict], int]:
        """
        Fetch repository contributors (sorted by number of contributions).

        Returns:
            tuple: (list_of_contributors, total_pages)
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/contributors"
        return await self._get_paginated(
            url, page, per_page, f"Contributors for '{owner}/{repo}'",
        )

    async def get_commits(
        self, owner: str, repo: str, page: int = 1, per_page: int = 30,
    ) -> tuple[list[dict], int]:
        """
        Fetch repository commits (most recent first).

        Returns:
            tuple: (list_of_commits, total_pages)
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        return await self._get_paginated(
            url, page, per_page, f"Commits for '{owner}/{repo}'",
        )

    async def get_languages(self, owner: str, repo: str) -> dict:
        """
        Fetch repository language breakdown.

        GitHub returns a dict of {language_name: bytes_of_code}.
        No pagination — GitHub always returns all languages in one response.

        Returns:
            dict: e.g. {"Python": 150234, "JavaScript": 48012, "Shell": 3201}
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/languages"

        try:
            response = await self.client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as exc:
            self._handle_error(exc, f"Languages for '{owner}/{repo}'")

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Could not connect to GitHub API: {str(exc)}",
            )

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

        Args:
            state: Filter by state — "open", "closed", or "all".

        Returns:
            tuple: (list_of_pull_requests, total_pages)
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        return await self._get_paginated(
            url, page, per_page,
            f"Pull requests for '{owner}/{repo}'",
            extra_params={"state": state},
        )

    async def get_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        page: int = 1,
        per_page: int = 30,
    ) -> tuple[list[dict], int]:
        """
        Fetch repository issues (excluding pull requests).

        GitHub's Issues API returns both issues AND pull requests.
        We filter out PRs (they have a "pull_request" key) so this
        endpoint returns only true issues.

        Args:
            state: Filter by state — "open", "closed", or "all".

        Returns:
            tuple: (list_of_issues, total_pages)

        Note:
            Because we filter client-side, the actual count per page may
            be less than per_page. total_pages reflects GitHub's pagination
            (which includes PRs), so it's an upper bound.
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        items, total_pages = await self._get_paginated(
            url, page, per_page,
            f"Issues for '{owner}/{repo}'",
            extra_params={"state": state},
        )

        # Filter out pull requests — they have a "pull_request" key
        issues_only = [
            item for item in items if "pull_request" not in item
        ]

        return issues_only, total_pages