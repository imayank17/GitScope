from fastapi import APIRouter

from app.repositories.github_repository import GitHubRepository

router = APIRouter(prefix="/github", tags=["GitHub"])

repository = GitHubRepository()


@router.get("/{owner}/{repo}")
async def repository_details(owner: str, repo: str):

    data = await repository.get_repo(owner, repo)

    return {
        "name": data["name"],
        "full_name": data["full_name"],
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "open_issues": data["open_issues_count"],
        "watchers": data["watchers_count"],
        "language": data["language"],
    }