"""
GitHub Router
-------------
HTTP endpoints for GitHub repository operations.
  POST /repositories/analyze              — Analyze a repo (URL or owner/repo)
  GET  /github/{owner}/{repo}             — Quick lookup by owner and repo
  GET  /repositories/{owner}/{repo}/contributors  — List contributors
  GET  /repositories/{owner}/{repo}/commits       — List commits
  GET  /repositories/{owner}/{repo}/languages     — Language breakdown
  GET  /repositories/{owner}/{repo}/pulls         — List pull requests
  GET  /repositories/{owner}/{repo}/issues        — List issues
"""

from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.dependencies import get_github_repository
from app.repositories.github_repository import GitHubRepository
from app.schemas.github import (
    CommitResponse,
    ContributorResponse,
    IssueResponse,
    LanguageResponse,
    PaginatedResponse,
    PullRequestResponse,
    RepositoryAnalyzeRequest,
    RepositoryResponse,
)


router = APIRouter(tags=["GitHub"])


# Enums for query parameters

class StateFilter(str, Enum):
    """Valid states for filtering pull requests and issues."""
    open = "open"
    closed = "closed"
    all = "all"


# Private helpers — URL parsing & response building

def _parse_repo_url(repo_url: str) -> tuple[str, str]:
    """
    Extract (owner, repo) from a user-provided string.

    Supports:
      • "fastapi/fastapi"
      • "https://github.com/fastapi/fastapi"
      • "https://github.com/fastapi/fastapi/" (trailing slash)
      • "github.com/fastapi/fastapi"

    Raises:
        HTTPException 422: If the string can't be parsed into owner/repo.
    """
    url = repo_url.strip().rstrip("/")

    if "github.com" in url:
        parts = url.split("github.com/")
        if len(parts) == 2:
            url = parts[1]

    segments = url.split("/")

    if len(segments) != 2 or not segments[0] or not segments[1]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid repository format: '{repo_url}'. "
                   f"Use 'owner/repo' or 'https://github.com/owner/repo'.",
        )

    return segments[0], segments[1]


def _build_repo_response(data) -> RepositoryResponse:
    """Map either GitHub's raw repo JSON or database Repository model → RepositoryResponse."""
    if isinstance(data, dict):
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
    else:
        return RepositoryResponse(
            name=data.name,
            full_name=data.full_name,
            description=data.description,
            language=data.language,
            stars=data.stars,
            forks=data.forks,
            open_issues=data.open_issues,
            watchers=data.watchers,
            topics=data.topics or [],
            visibility=data.visibility,
            default_branch=data.default_branch,
            created_at=data.github_created_at or data.created_at.isoformat(),
            updated_at=data.github_updated_at or data.updated_at.isoformat(),
            html_url=data.html_url,
            clone_url=data.clone_url,
            owner_login=data.owner_login,
            owner_avatar_url=data.owner_avatar_url,
        )


def _build_contributor(data) -> ContributorResponse:
    """Map either GitHub contributor dict or Contributor model → ContributorResponse."""
    if isinstance(data, dict):
        return ContributorResponse(
            login=data["login"],
            avatar_url=data["avatar_url"],
            contributions=data["contributions"],
            html_url=data["html_url"],
        )
    else:
        return ContributorResponse(
            login=data.login,
            avatar_url=data.avatar_url,
            contributions=data.contributions,
            html_url=data.html_url,
        )


def _build_commit(data) -> CommitResponse:
    """Map either GitHub commit dict or Commit model → CommitResponse."""
    if isinstance(data, dict):
        commit_data = data["commit"]
        return CommitResponse(
            sha=data["sha"],
            message=commit_data["message"],
            author_name=commit_data["author"]["name"],
            author_email=commit_data["author"]["email"],
            author_date=commit_data["author"]["date"],
            committer_name=commit_data["committer"]["name"],
            html_url=data["html_url"],
        )
    else:
        return CommitResponse(
            sha=data.sha,
            message=data.message,
            author_name=data.author_name,
            author_email=data.author_email,
            author_date=data.author_date,
            committer_name=data.committer_name,
            html_url=data.html_url,
        )


def _build_language_response(raw_languages: dict) -> LanguageResponse:
    """
    Build a LanguageResponse from raw language dict.
    GitHub returns: {"Python": 150234, "JavaScript": 48012}
    We add:
      total_bytes  = 198246
      percentages  = {"Python": 75.77, "JavaScript": 24.23}
    """
    total = sum(raw_languages.values()) if raw_languages else 0

    percentages = {}
    if total > 0:
        percentages = {
            lang: round((byte_count / total) * 100, 2)
            for lang, byte_count in raw_languages.items()
        }

    return LanguageResponse(
        languages=raw_languages,
        total_bytes=total,
        percentages=percentages,
    )


def _build_pull_request(data) -> PullRequestResponse:
    """Map either GitHub PR dict or PullRequest model → PullRequestResponse."""
    if isinstance(data, dict):
        return PullRequestResponse(
            number=data["number"],
            title=data["title"],
            state=data["state"],
            user_login=data["user"]["login"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            html_url=data["html_url"],
            labels=[label["name"] for label in data.get("labels", [])],
            merged_at=data.get("merged_at"),
            draft=data.get("draft", False),
        )
    else:
        return PullRequestResponse(
            number=data.number,
            title=data.title,
            state=data.state,
            user_login=data.user_login,
            created_at=data.github_created_at or data.created_at.isoformat(),
            updated_at=data.github_updated_at or data.created_at.isoformat(),
            html_url=data.html_url,
            labels=data.labels or [],
            merged_at=data.merged_at,
            draft=data.draft,
        )


def _build_issue(data) -> IssueResponse:
    """Map either GitHub issue dict or Issue model → IssueResponse."""
    if isinstance(data, dict):
        return IssueResponse(
            number=data["number"],
            title=data["title"],
            state=data["state"],
            user_login=data["user"]["login"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            html_url=data["html_url"],
            labels=[label["name"] for label in data.get("labels", [])],
            comments=data.get("comments", 0),
        )
    else:
        return IssueResponse(
            number=data.number,
            title=data.title,
            state=data.state,
            user_login=data.user_login,
            created_at=data.github_created_at or data.created_at.isoformat(),
            updated_at=data.github_updated_at or data.created_at.isoformat(),
            html_url=data.html_url,
            labels=data.labels or [],
            comments=data.comments,
        )


#  Endpoints (unchanged)

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
    return _build_repo_response(data)


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
    data = await repository.get_repo(owner, repo)
    return _build_repo_response(data)


#  Endpoints — Contributors

@router.get(
    "/repositories/{owner}/{repo}/contributors",
    response_model=PaginatedResponse,
    summary="List repository contributors",
    description="Fetch contributors sorted by number of contributions. "
                "Supports pagination via page and per_page query params.",
)
async def list_contributors(
    owner: str,
    repo: str,
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)."),
    per_page: int = Query(
        default=30, ge=1, le=100,
        description="Results per page (max 100).",
    ),
    repository: GitHubRepository = Depends(get_github_repository),
) -> PaginatedResponse:
    items, total_pages = await repository.get_contributors(
        owner, repo, page, per_page,
    )

    return PaginatedResponse(
        items=[_build_contributor(c) for c in items],
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


#Endpoints — Commits

@router.get(
    "/repositories/{owner}/{repo}/commits",
    response_model=PaginatedResponse,
    summary="List repository commits",
    description="Fetch commits ordered by date (most recent first). "
                "Supports pagination via page and per_page query params.",
)
async def list_commits(
    owner: str,
    repo: str,
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)."),
    per_page: int = Query(
        default=30, ge=1, le=100,
        description="Results per page (max 100).",
    ),
    repository: GitHubRepository = Depends(get_github_repository),
) -> PaginatedResponse:
    items, total_pages = await repository.get_commits(
        owner, repo, page, per_page,
    )

    return PaginatedResponse(
        items=[_build_commit(c) for c in items],
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


# Endpoints — Languages

@router.get(
    "/repositories/{owner}/{repo}/languages",
    response_model=LanguageResponse,
    summary="Get repository language breakdown",
    description="Fetch the language composition of a repository. "
                "Returns raw byte counts and calculated percentages.",
)
async def get_languages(
    owner: str,
    repo: str,
    repository: GitHubRepository = Depends(get_github_repository),
) -> LanguageResponse:
    raw_languages = await repository.get_languages(owner, repo)
    if isinstance(raw_languages, list):
        raw_languages = {lang.name: lang.bytes for lang in raw_languages}
    return _build_language_response(raw_languages)


#  Endpoints — Pull Requests

@router.get(
    "/repositories/{owner}/{repo}/pulls",
    response_model=PaginatedResponse,
    summary="List repository pull requests",
    description="Fetch pull requests filtered by state. "
                "Supports pagination via page and per_page query params.",
)
async def list_pull_requests(
    owner: str,
    repo: str,
    state: StateFilter = Query(
        default=StateFilter.open,
        description="Filter by PR state: 'open', 'closed', or 'all'.",
    ),
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)."),
    per_page: int = Query(
        default=30, ge=1, le=100,
        description="Results per page (max 100).",
    ),
    repository: GitHubRepository = Depends(get_github_repository),
) -> PaginatedResponse:
    items, total_pages = await repository.get_pull_requests(
        owner, repo, state.value, page, per_page,
    )

    return PaginatedResponse(
        items=[_build_pull_request(pr) for pr in items],
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


# Endpoints — Issues

@router.get(
    "/repositories/{owner}/{repo}/issues",
    response_model=PaginatedResponse,
    summary="List repository issues",
    description="Fetch issues (excluding pull requests) filtered by state. "
                "Supports pagination via page and per_page query params.",
)
async def list_issues(
    owner: str,
    repo: str,
    state: StateFilter = Query(
        default=StateFilter.open,
        description="Filter by issue state: 'open', 'closed', or 'all'.",
    ),
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)."),
    per_page: int = Query(
        default=30, ge=1, le=100,
        description="Results per page (max 100).",
    ),
    repository: GitHubRepository = Depends(get_github_repository),
) -> PaginatedResponse:
    items, total_pages = await repository.get_issues(
        owner, repo, state.value, page, per_page,
    )

    return PaginatedResponse(
        items=[_build_issue(issue) for issue in items],
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )