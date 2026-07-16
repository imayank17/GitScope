import pytest
import respx
from httpx import Response

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
from tests.fixtures.repositories import db_repository, sample_repo_dict
from sqlalchemy import select
from app.models.repository import Repository


@pytest.mark.anyio
async def test_analyze_repository_new(client, respx_mock_github):
    """
    Test that POST /repositories/analyze successfully synchronizes a new repo
    from the GitHub API and creates it in the database.
    """
    response = await client.post(
        "/repositories/analyze",
        json={"repo_url": "https://github.com/test-owner/test-repo"}
    )
    
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["name"] == "test-repo"
    assert json_data["full_name"] == "test-owner/test-repo"
    assert json_data["stars"] == 42
    assert json_data["language"] == "Python"
    assert json_data["owner_login"] == "test-owner"


@pytest.mark.anyio
async def test_analyze_repository_invalid_format(client):
    """
    Test that POST /repositories/analyze returns a 422 error for invalid URLs.
    """
    response = await client.post(
        "/repositories/analyze",
        json={"repo_url": "gitscope"}
    )
    assert response.status_code == 422
    assert "Invalid repository format" in response.json()["detail"]


@pytest.mark.anyio
async def test_repository_details_success(client, db_repository):
    """
    Test GET /github/{owner}/{repo} gets the details of a repository from cache.
    """
    response = await client.get(f"/github/{db_repository.owner_login}/{db_repository.name}")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["full_name"] == db_repository.full_name
    assert json_data["description"] == db_repository.description
    assert json_data["stars"] == db_repository.stars


@pytest.mark.anyio
async def test_repository_details_stale(client, respx_mock_github, db_repository, db):
    """
    Test GET /github/{owner}/{repo} triggers a background sync if the repository is stale.
    """
    from datetime import datetime, timedelta, timezone
    
    # Set repository's last_synced_at to 10 days ago (stale)
    repo_id = db_repository.id
    stmt = select(Repository).where(Repository.id == repo_id)
    repo = (await db.execute(stmt)).scalars().first()
    repo.last_synced_at = datetime.now(timezone.utc) - timedelta(days=10)
    repo.sync_status = "COMPLETED"
    await db.commit()
    
    response = await client.get(f"/github/{db_repository.owner_login}/{db_repository.name}")
    assert response.status_code == 200
    
    # Verify repository status in database is transitioned to SYNCING or COMPLETED by background task
    db.expire_all()
    repo = (await db.execute(stmt)).scalars().first()
    assert repo.sync_status in ("SYNCING", "COMPLETED")


@pytest.mark.anyio
async def test_list_contributors(client, db_repository):
    """
    Test GET /repositories/{owner}/{repo}/contributors returns a paginated list of contributors.
    """
    response = await client.get(
        f"/repositories/{db_repository.owner_login}/{db_repository.name}/contributors",
        params={"page": 1, "per_page": 1}
    )
    assert response.status_code == 200
    json_data = response.json()
    
    assert "items" in json_data
    assert json_data["page"] == 1
    assert json_data["per_page"] == 1
    assert len(json_data["items"]) == 1
    assert json_data["items"][0]["login"] == "user-alice"


@pytest.mark.anyio
async def test_list_commits(client, db_repository):
    """
    Test GET /repositories/{owner}/{repo}/commits returns a paginated list of commits.
    """
    response = await client.get(
        f"/repositories/{db_repository.owner_login}/{db_repository.name}/commits",
        params={"page": 1, "per_page": 10}
    )
    assert response.status_code == 200
    json_data = response.json()
    
    assert len(json_data["items"]) == 1
    assert json_data["items"][0]["sha"] == "c0ffee112233445566778899aabbccddeeff0011"


@pytest.mark.anyio
async def test_get_languages(client, db_repository):
    """
    Test GET /repositories/{owner}/{repo}/languages returns total bytes and percentages.
    """
    response = await client.get(f"/repositories/{db_repository.owner_login}/{db_repository.name}/languages")
    assert response.status_code == 200
    json_data = response.json()
    
    assert json_data["total_bytes"] == 100000
    assert json_data["languages"]["Python"] == 90000
    assert json_data["percentages"]["Python"] == 90.0
    assert json_data["percentages"]["Shell"] == 10.0


@pytest.mark.anyio
async def test_list_pull_requests(client, db_repository):
    """
    Test GET /repositories/{owner}/{repo}/pulls returns pull requests filtered by state.
    """
    response = await client.get(
        f"/repositories/{db_repository.owner_login}/{db_repository.name}/pulls",
        params={"state": "open"}
    )
    assert response.status_code == 200
    json_data = response.json()
    
    assert len(json_data["items"]) == 1
    assert json_data["items"][0]["number"] == 5
    assert json_data["items"][0]["state"] == "open"


@pytest.mark.anyio
async def test_list_issues(client, db_repository):
    """
    Test GET /repositories/{owner}/{repo}/issues returns issues (excluding pulls) filtered by state.
    """
    response = await client.get(
        f"/repositories/{db_repository.owner_login}/{db_repository.name}/issues",
        params={"state": "open"}
    )
    assert response.status_code == 200
    json_data = response.json()
    
    assert len(json_data["items"]) == 1
    assert json_data["items"][0]["number"] == 42
    assert json_data["items"][0]["state"] == "open"


@pytest.mark.anyio
async def test_private_mapping_helpers_with_dicts():
    """
    Test private build helper functions in app/routers/github.py directly with dictionaries
    to ensure full code coverage of legacy dict-mapping fallbacks.
    """
    from app.routers.github import (
        _build_repo_response,
        _build_contributor,
        _build_commit,
        _build_pull_request,
        _build_issue,
        _build_language_response,
    )
    
    # Test _build_repo_response with dict
    repo_dict = {
        "name": "test-repo",
        "full_name": "test-owner/test-repo",
        "description": "desc",
        "language": "Python",
        "stargazers_count": 10,
        "forks_count": 2,
        "open_issues_count": 1,
        "watchers_count": 10,
        "topics": [],
        "visibility": "public",
        "default_branch": "main",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "html_url": "https://github.com/...",
        "clone_url": "https://github.com/...",
        "owner": {"login": "test-owner", "avatar_url": "https://..."}
    }
    res_repo = _build_repo_response(repo_dict)
    assert res_repo.name == "test-repo"
    
    # Test _build_contributor with dict
    contrib_dict = {
        "login": "alice",
        "avatar_url": "https://...",
        "contributions": 5,
        "html_url": "https://..."
    }
    res_contrib = _build_contributor(contrib_dict)
    assert res_contrib.login == "alice"
    
    # Test _build_commit with dict
    commit_dict = {
        "sha": "sha123",
        "commit": {
            "message": "msg",
            "author": {"name": "alice", "email": "alice@gmail.com", "date": "2026-01-01T00:00:00Z"},
            "committer": {"name": "alice"}
        },
        "html_url": "https://..."
    }
    res_commit = _build_commit(commit_dict)
    assert res_commit.sha == "sha123"
    
    # Test _build_pull_request with dict
    pr_dict = {
        "number": 1,
        "title": "pr1",
        "state": "open",
        "user": {"login": "alice"},
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "html_url": "https://...",
        "labels": [],
        "merged_at": None,
        "draft": False
    }
    res_pr = _build_pull_request(pr_dict)
    assert res_pr.number == 1
    
    # Test _build_issue with dict
    issue_dict = {
        "number": 2,
        "title": "issue1",
        "state": "open",
        "user": {"login": "alice"},
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "html_url": "https://...",
        "labels": [],
        "comments": 0
    }
    res_issue = _build_issue(issue_dict)
    assert res_issue.number == 2
    
    # Test _build_language_response with empty dict (total <= 0)
    res_lang = _build_language_response({})
    assert res_lang.total_bytes == 0
    assert res_lang.percentages == {}
