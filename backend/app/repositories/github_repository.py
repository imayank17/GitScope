from app.services.github_service import GitHubService


class GitHubRepository:

    def __init__(self):
        self.github = GitHubService()

    async def get_repo(self, owner, repo):

        return await self.github.get_repository(owner, repo)