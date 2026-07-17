import pytest
import respx
import httpx
from fastapi import HTTPException
from app.services.github_service import GitHubService
from app.core.config import settings

# Import fixtures explicitly
from tests.fixtures.github import (
    github_repo_data,
    github_contributors_data,
    github_commits_data,
    github_languages_data,
    github_pulls_data,
    github_issues_data,
    respx_mock_github,
)


@pytest.fixture
async def github_service():
    """Initializes GitHubService with a standard client."""
    async with httpx.AsyncClient() as client:
        yield GitHubService(client=client)


@pytest.mark.anyio
async def test_get_repository_success(
    github_service, respx_mock_github, github_repo_data
):
    """Test successful retrieval of repository metadata."""
    repo = await github_service.get_repository("test-owner", "test-repo")
    assert repo == github_repo_data
    assert repo["name"] == "test-repo"


@pytest.mark.anyio
async def test_get_contributors_success(
    github_service, respx_mock_github, github_contributors_data
):
    """Test successful retrieval of contributors with pagination parsing."""
    respx_mock_github["get_contributors"].mock(
        return_value=httpx.Response(
            200,
            json=github_contributors_data,
            headers={
                "Link": '<https://api.github.com/repos/test-owner/test-repo/contributors?page=2>; rel="next", <https://api.github.com/repos/test-owner/test-repo/contributors?page=5>; rel="last"'
            },
        )
    )

    contribs, total_pages = await github_service.get_contributors(
        "test-owner", "test-repo", page=1
    )
    assert contribs == github_contributors_data
    assert total_pages == 5


@pytest.mark.anyio
async def test_get_commits_success(
    github_service, respx_mock_github, github_commits_data
):
    """Test successful retrieval of commits."""
    commits, total_pages = await github_service.get_commits("test-owner", "test-repo")
    assert commits == github_commits_data
    assert total_pages == 1


@pytest.mark.anyio
async def test_get_languages_success(
    github_service, respx_mock_github, github_languages_data
):
    """Test successful retrieval of repository languages."""
    languages = await github_service.get_languages("test-owner", "test-repo")
    assert languages == github_languages_data


@pytest.mark.anyio
async def test_get_pull_requests_success(
    github_service, respx_mock_github, github_pulls_data
):
    """Test successful retrieval of pull requests."""
    prs, total_pages = await github_service.get_pull_requests("test-owner", "test-repo")
    assert prs == github_pulls_data
    assert total_pages == 1


@pytest.mark.anyio
async def test_get_issues_success_filters_pulls(
    github_service, respx_mock_github, github_issues_data
):
    """Test that retrieving issues successfully filters out pull requests."""
    # When hitting /issues, it returns both PRs and true issues. Our mock returns 1 issue, 2 PRs (total 3).
    issues, total_pages = await github_service.get_issues("test-owner", "test-repo")

    # We should only get the 1 true issue (not the pull requests)
    assert len(issues) == 1
    assert issues[0]["title"] == "Bug: Cache miss on repo details"
    assert total_pages == 1


@pytest.mark.anyio
async def test_handle_errors_404(github_service, respx_mock_github):
    """Test that a 404 from GitHub raises a FastAPI 404 HTTPException."""
    respx_mock_github["get_repo"].mock(return_value=httpx.Response(404))

    with pytest.raises(HTTPException) as exc_info:
        await github_service.get_repository("test-owner", "test-repo")
    assert exc_info.value.status_code == 404
    assert "not found on GitHub" in exc_info.value.detail


@pytest.mark.anyio
async def test_handle_errors_401(github_service, respx_mock_github):
    """Test that a 401 from GitHub raises a FastAPI 401 HTTPException."""
    respx_mock_github["get_repo"].mock(return_value=httpx.Response(401))

    with pytest.raises(HTTPException) as exc_info:
        await github_service.get_repository("test-owner", "test-repo")
    assert exc_info.value.status_code == 401
    assert "Invalid GitHub token" in exc_info.value.detail


@pytest.mark.anyio
async def test_handle_errors_403(github_service, respx_mock_github):
    """Test that a 403 from GitHub raises a FastAPI 403 HTTPException."""
    respx_mock_github["get_repo"].mock(return_value=httpx.Response(403))

    with pytest.raises(HTTPException) as exc_info:
        await github_service.get_repository("test-owner", "test-repo")
    assert exc_info.value.status_code == 403
    assert "rate limit exceeded" in exc_info.value.detail


@pytest.mark.anyio
async def test_handle_errors_500(github_service, respx_mock_github):
    """Test that a 500 from GitHub raises a FastAPI 502 Bad Gateway HTTPException."""
    respx_mock_github["get_repo"].mock(return_value=httpx.Response(500))

    with pytest.raises(HTTPException) as exc_info:
        await github_service.get_repository("test-owner", "test-repo")
    assert exc_info.value.status_code == 502
    assert "GitHub API returned an error" in exc_info.value.detail


@pytest.mark.anyio
async def test_connection_failure(github_service, respx_mock_github):
    """Test that connection failure to GitHub raises a FastAPI 502 Bad Gateway HTTPException."""
    respx_mock_github["get_repo"].mock(
        side_effect=httpx.ConnectError("Connection timed out")
    )

    with pytest.raises(HTTPException) as exc_info:
        await github_service.get_repository("test-owner", "test-repo")
    assert exc_info.value.status_code == 502
    assert "Could not connect to GitHub API" in exc_info.value.detail
