"""
GitHub API Service
"""

import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class GitHubService:
    """Async wrapper around the GitHub REST API."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        """
        Args:
            client: A shared httpx.AsyncClient — created once at app startup
                    and closed at shutdown (managed via FastAPI lifespan).
        """
        self.client = client
        self.base_url = settings.GITHUB_API_BASE_URL

        # Build headers — token is optional
        self.headers: dict[str, str] = {
            "Accept": "application/vnd.github+json",
        }
        if settings.GITHUB_TOKEN:
            self.headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"

    async def get_repository(self, owner: str, repo: str) -> dict:
       
        url = f"{self.base_url}/repos/{owner}/{repo}"

        try:
            response = await self.client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as exc:
            # Map GitHub HTTP errors to meaningful FastAPI responses
            status_code = exc.response.status_code

            if status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Repository '{owner}/{repo}' not found on GitHub.",
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

        except httpx.RequestError as exc:
            # Network-level failures (DNS, timeout, connection refused, etc.)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Could not connect to GitHub API: {str(exc)}",
            )