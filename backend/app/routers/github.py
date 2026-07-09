from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_github_repository
from app.repositories.github_repository import GitHubRepository
from app.schemas.github import RepositoryAnalyzeRequest, RepositoryResponse


router = APIRouter(tags=["GitHub"])


# Helper — parse "owner/repo" from various input formats

def _parse_repo_url(repo_url: str) -> tuple[str, str]:
   
    # Strip whitespace and trailing slashes
    url = repo_url.strip().rstrip("/")

    # Full URL format — extract the path portion
    if "github.com" in url:
        # Split on "github.com/" and take everything after
        parts = url.split("github.com/")
        if len(parts) == 2:
            url = parts[1]

    # Now we should have "owner/repo"
    segments = url.split("/")

    if len(segments) != 2 or not segments[0] or not segments[1]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid repository format: '{repo_url}'. "
                   f"Use 'owner/repo' or 'https://github.com/owner/repo'.",
        )

    return segments[0], segments[1]



# Helper — map raw GitHub API data → RepositoryResponse schema


def _build_response(data: dict) -> RepositoryResponse:
    """
    Map GitHub's raw JSON to our clean RepositoryResponse schema.

    This keeps the mapping logic in one place — both endpoints reuse it.
    """
    return RepositoryResponse(
        name=data["name"],
        full_name=data["full_name"],
        description=data.get("description"),
        language=data.get("language"),
        stars=data["stargazers_count"],
        forks=data["forks_count"],
        open_issues=data["open_issues_count"],
        watchers=data["watchers_count"],
        topics=data.get("topics", []),
        visibility=data.get("visibility", "public"),
        default_branch=data.get("default_branch", "main"),
        created_at=data["created_at"],
        updated_at=data["updated_at"],
        html_url=data["html_url"],
        clone_url=data["clone_url"],
        owner_login=data["owner"]["login"],
        owner_avatar_url=data["owner"]["avatar_url"],
    )


# Endpoints


@router.post(
    "/repositories/analyze",
    response_model=RepositoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze a GitHub repository",
    description="Accepts a GitHub repo URL or 'owner/repo' string, "
                "fetches metadata from GitHub, and returns a clean JSON response.",
)
async def analyze_repository(
    request: RepositoryAnalyzeRequest,
    repository: GitHubRepository = Depends(get_github_repository),
) -> RepositoryResponse:
    
    owner, repo = _parse_repo_url(request.repo_url)
    data = await repository.get_repo(owner, repo)
    return _build_response(data)


@router.get(
    "/github/{owner}/{repo}",
    response_model=RepositoryResponse,
    summary="Get repository details",
    description="Fetch repository metadata by owner and repo name.",
)
async def repository_details(
    owner: str,
    repo: str,
    repository: GitHubRepository = Depends(get_github_repository),
) -> RepositoryResponse:
    """
    Quick lookup endpoint — owner and repo as path parameters.
    """
    data = await repository.get_repo(owner, repo)
    return _build_response(data)