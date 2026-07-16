import pytest
import uuid
from httpx import Response
from sqlalchemy import select
from app.models.repository import Repository

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


@pytest.mark.anyio
async def test_refresh_repository_success(client, respx_mock_github, db_repository, db):
    """
    Test that POST /repositories/{id}/refresh triggers a background sync,
    sets the repository status to SYNCING/COMPLETED, and returns 202 Accepted.
    """
    repo_id = db_repository.id
    
    response = await client.post(f"/repositories/{repo_id}/refresh")
    assert response.status_code == 202
    json_data = response.json()
    assert json_data["repository_id"] == str(repo_id)
    assert json_data["status"] == "SYNCING"
    
    # Verify DB state was updated (it may transition all the way to COMPLETED during background task execution)
    db.expire_all()
    stmt = select(Repository).where(Repository.id == repo_id)
    repo = (await db.execute(stmt)).scalars().first()
    assert repo.sync_status in ("SYNCING", "COMPLETED")
    assert repo.sync_error is None


@pytest.mark.anyio
async def test_refresh_repository_not_found(client):
    """
    Test that POST /repositories/{id}/refresh returns 404 for non-existent repositories.
    """
    random_id = uuid.uuid4()
    response = await client.post(f"/repositories/{random_id}/refresh")
    assert response.status_code == 404
    assert response.json()["detail"] == "Repository not found"


@pytest.mark.anyio
async def test_get_sync_status_success(client, db_repository):
    """
    Test GET /repositories/{id}/sync-status returns the correct status and sync fields.
    """
    repo_id = db_repository.id
    response = await client.get(f"/repositories/{repo_id}/sync-status")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["repository_id"] == str(repo_id)
    assert json_data["status"] == "COMPLETED"
    assert json_data["error"] is None
    assert json_data["last_synced_at"] is not None


@pytest.mark.anyio
async def test_get_sync_status_not_found(client):
    """
    Test GET /repositories/{id}/sync-status returns 404 for non-existent repositories.
    """
    random_id = uuid.uuid4()
    response = await client.get(f"/repositories/{random_id}/sync-status")
    assert response.status_code == 404
    assert response.json()["detail"] == "Repository not found"


@pytest.mark.anyio
async def test_get_metrics_history_success(client, db_repository):
    """
    Test GET /repositories/{id}/metrics/history returns historical snapshot series.
    """
    repo_id = db_repository.id
    response = await client.get(f"/repositories/{repo_id}/metrics/history")
    assert response.status_code == 200
    json_data = response.json()
    
    assert isinstance(json_data, list)
    assert len(json_data) == 1
    assert json_data[0]["stars"] == 100
    assert json_data[0]["forks"] == 25
    assert json_data[0]["open_issues"] == 10
    assert json_data[0]["commit_count"] == 1
    assert json_data[0]["pull_request_count"] == 1


@pytest.mark.anyio
async def test_get_metrics_history_not_found(client):
    """
    Test GET /repositories/{id}/metrics/history returns 404 for non-existent repositories.
    """
    random_id = uuid.uuid4()
    response = await client.get(f"/repositories/{random_id}/metrics/history")
    assert response.status_code == 404
    assert response.json()["detail"] == "Repository not found"
