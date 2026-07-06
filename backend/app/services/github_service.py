import httpx
from app.core.config import settings


class GitHubService:

    BASE_URL = "https://api.github.com"

    headers = {
        "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }

    async def get_repository(self, owner: str, repo: str):

        async with httpx.AsyncClient(follow_redirects=True) as client:

            response = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}",
                headers=self.headers,
            )

            response.raise_for_status()

            return response.json()