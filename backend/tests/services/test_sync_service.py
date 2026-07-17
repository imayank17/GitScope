import pytest
import respx
import httpx
import uuid
from httpx import Response
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.services.sync_service import SynchronizationService
from app.services.github_service import GitHubService
from app.models.repository import Repository
from app.models.contributor import Contributor
from app.models.commit import Commit
from app.models.issue import Issue
from app.models.pull_request import PullRequest
from app.models.language import Language
from app.models.snapshot import RepositorySnapshot

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


@pytest.fixture
async def sync_service():
    """Initializes SynchronizationService with a standard client."""
    async with httpx.AsyncClient() as client:
        service = GitHubService(client=client)
        yield SynchronizationService(github_service=service)


@pytest.mark.anyio
async def test_sync_repository_success(
    sync_service, respx_mock_github, db_repository, db
):
    """
    Test that sync_repository correctly updates a repository's metadata,
    upserts all child models (contributors, commits, PRs, issues, languages),
    creates a snapshot, and marks the status as COMPLETED.
    """
    # Store ID in local variable to avoid lazy-loading issues after bulk deletes
    repo_id = db_repository.id

    # 1. Verify pre-sync counts on db_repository
    # Ensure relationships are loaded
    stmt = (
        select(Repository)
        .where(Repository.id == repo_id)
        .options(
            selectinload(Repository.contributors),
            selectinload(Repository.commits),
            selectinload(Repository.languages),
            selectinload(Repository.pull_requests),
            selectinload(Repository.issues),
            selectinload(Repository.snapshots),
        )
    )
    repo = (await db.execute(stmt)).scalars().first()

    assert len(repo.contributors) == 2
    assert len(repo.commits) == 1
    assert len(repo.languages) == 2
    assert len(repo.pull_requests) == 1
    assert len(repo.issues) == 1
    assert len(repo.snapshots) == 1

    # 2. Modify mock responses to simulate incoming updates using named routes
    respx_mock_github["get_repo"].mock(
        return_value=Response(
            200,
            json={
                "id": repo.github_id,
                "name": repo.name,
                "full_name": repo.full_name,
                "description": "Updated Description!",
                "owner": {
                    "login": repo.owner_login,
                    "avatar_url": repo.owner_avatar_url,
                },
                "html_url": repo.html_url,
                "clone_url": repo.clone_url,
                "language": "Python",
                "default_branch": "develop",
                "visibility": "public",
                "stargazers_count": 150,  # +50 stars
                "forks_count": 30,
                "open_issues_count": 8,
                "watchers_count": 150,
                "topics": ["metrics", "analytics"],
                "created_at": "2026-02-15T08:00:00Z",
                "updated_at": "2026-07-15T12:00:00Z",
            },
        )
    )

    respx_mock_github["get_contributors"].mock(
        return_value=Response(
            200,
            json=[
                # Update contributions for Alice
                {
                    "id": 901,
                    "login": "user-alice",
                    "avatar_url": "https://...",
                    "html_url": "https://...",
                    "contributions": 150,
                },
                # Add a brand new contributor
                {
                    "id": 903,
                    "login": "user-charlie",
                    "avatar_url": "https://...",
                    "html_url": "https://...",
                    "contributions": 10,
                },
            ],
        )
    )

    respx_mock_github["get_commits"].mock(
        return_value=Response(
            200,
            json=[
                # Existing commit
                {
                    "sha": "c0ffee112233445566778899aabbccddeeff0011",
                    "commit": {
                        "message": "xyz",
                        "author": {
                            "name": "a",
                            "email": "e",
                            "date": "2026-07-01T10:00:00Z",
                        },
                        "committer": {"name": "c"},
                    },
                    "html_url": "http://...",
                },
                # New commit
                {
                    "sha": "newcommitsha12345678901234567890123456",
                    "commit": {
                        "message": "Fix bug",
                        "author": {
                            "name": "Bob",
                            "email": "b",
                            "date": "2026-07-05T10:00:00Z",
                        },
                        "committer": {"name": "Bob"},
                    },
                    "html_url": "http://...",
                },
            ],
        )
    )

    # 3. Trigger direct sync
    await sync_service.sync_repository(repo, db)
    await db.commit()

    # Expire cache to force a fresh SELECT with selectinloads
    db.expire_all()

    # Re-fetch and verify updates
    stmt = (
        select(Repository)
        .where(Repository.id == repo_id)
        .options(
            selectinload(Repository.contributors),
            selectinload(Repository.commits),
            selectinload(Repository.languages),
            selectinload(Repository.pull_requests),
            selectinload(Repository.issues),
            selectinload(Repository.snapshots),
        )
    )
    repo = (await db.execute(stmt)).scalars().first()

    # Metadata updated
    assert repo.description == "Updated Description!"
    assert repo.stars == 150
    assert repo.sync_status == "COMPLETED"

    # Child relationships merged correctly
    # Charlie was added, Alice was updated, Bob was kept, so we have 3 contributors now
    assert len(repo.contributors) == 3
    # 1 new commit added -> total 2 commits
    assert len(repo.commits) == 2
    # Snapshot history now has 2 entries (initial + post-sync)
    assert len(repo.snapshots) == 2


@pytest.mark.anyio
async def test_sync_repository_task_success(
    sync_service, respx_mock_github, db_repository, db
):
    """
    Test that the background task executor runs successfully, queries the repository,
    coordinates the update session, and commits changes.
    """
    repo_id = db_repository.id

    # Set up mocks for the repo in db_repository (gitscope-org/gitscope-core) using named route
    respx_mock_github["get_repo"].mock(
        return_value=Response(
            200,
            json={
                "id": db_repository.github_id,
                "name": db_repository.name,
                "full_name": db_repository.full_name,
                "owner": {
                    "login": db_repository.owner_login,
                    "avatar_url": db_repository.owner_avatar_url,
                },
                "html_url": db_repository.html_url,
                "clone_url": db_repository.clone_url,
                "stargazers_count": 200,
                "forks_count": 30,
                "open_issues_count": 5,
                "watchers_count": 200,
                "created_at": "2026-02-15T08:00:00Z",
                "updated_at": "2026-07-15T12:00:00Z",
            },
        )
    )

    # Run the background task
    await sync_service.sync_repository_task(repo_id)

    # Expire cache to force reload from DB
    db.expire_all()

    # Verify changes were committed and status is COMPLETED
    stmt = select(Repository).where(Repository.id == repo_id)
    repo = (await db.execute(stmt)).scalars().first()
    assert repo.sync_status == "COMPLETED"
    assert repo.stars == 200
    assert repo.sync_error is None


@pytest.mark.anyio
async def test_sync_repository_task_failure(
    sync_service, respx_mock_github, db_repository, db
):
    """
    Test that if an exception occurs during the background task, the task
    handles it, rolls back the session, marks status as FAILED, and writes the sync_error.
    """
    repo_id = db_repository.id

    # Simulate a GitHub API 500 error by overriding named route
    respx_mock_github["get_repo"].mock(return_value=Response(500))

    # Run the background task
    await sync_service.sync_repository_task(repo_id)

    # Refresh DB session context
    db.expire_all()

    # Verify repository status in database is FAILED and sync_error is populated
    stmt = select(Repository).where(Repository.id == repo_id)
    repo = (await db.execute(stmt)).scalars().first()
    assert repo.sync_status == "FAILED"
    assert repo.sync_error is not None
    assert "GitHub API returned an error" in repo.sync_error


@pytest.mark.anyio
async def test_sync_repository_partial_failures(
    sync_service, respx_mock_github, db_repository, db
):
    """
    Test that if optional GitHub endpoints fail (e.g. issues or languages),
    sync_repository still succeeds with partial empty data.
    """
    repo_id = db_repository.id
    stmt = select(Repository).where(Repository.id == repo_id)
    repo = (await db.execute(stmt)).scalars().first()

    respx_mock_github["get_contributors"].mock(return_value=Response(500))
    respx_mock_github["get_commits"].mock(return_value=Response(500))
    respx_mock_github["get_languages"].mock(return_value=Response(500))
    respx_mock_github["get_pulls"].mock(return_value=Response(500))
    respx_mock_github["get_issues"].mock(return_value=Response(500))

    await sync_service.sync_repository(repo, db)
    await db.commit()

    db.expire_all()
    stmt = (
        select(Repository)
        .where(Repository.id == repo_id)
        .options(
            selectinload(Repository.contributors),
            selectinload(Repository.languages),
        )
    )
    repo = (await db.execute(stmt)).scalars().first()
    assert repo.sync_status == "COMPLETED"


@pytest.mark.anyio
async def test_sync_repository_upsert_existing(
    sync_service, respx_mock_github, db_repository, db
):
    """
    Test that if pull requests and issues already exist in the database,
    sync_repository updates them in-place rather than duplicating them.
    """
    repo_id = db_repository.id
    stmt = select(Repository).where(Repository.id == repo_id)
    repo = (await db.execute(stmt)).scalars().first()

    # Mock get_issues to return issue 42 (with an updated title)
    respx_mock_github["get_issues"].mock(
        return_value=Response(
            200,
            json=[
                {
                    "number": 42,
                    "title": "Super updated issue title!",
                    "state": "closed",
                    "user": {"login": "user-bob"},
                    "created_at": "2026-07-02T11:00:00Z",
                    "updated_at": "2026-07-06T13:00:00Z",
                    "html_url": "https://github.com/gitscope-org/gitscope-core/issues/42",
                    "comments": 10,
                }
            ],
        )
    )

    # Mock get_pulls to return PR 5 (with an updated title)
    respx_mock_github["get_pulls"].mock(
        return_value=Response(
            200,
            json=[
                {
                    "number": 5,
                    "title": "Super updated PR title!",
                    "state": "closed",
                    "user": {"login": "user-alice"},
                    "created_at": "2026-07-03T09:00:00Z",
                    "updated_at": "2026-07-06T10:00:00Z",
                    "html_url": "https://github.com/gitscope-org/gitscope-core/pull/5",
                    "draft": False,
                    "merged_at": "2026-07-06T10:00:00Z",
                }
            ],
        )
    )

    await sync_service.sync_repository(repo, db)
    await db.commit()

    db.expire_all()
    stmt = (
        select(Repository)
        .where(Repository.id == repo_id)
        .options(
            selectinload(Repository.pull_requests),
            selectinload(Repository.issues),
        )
    )
    repo = (await db.execute(stmt)).scalars().first()

    assert len(repo.issues) == 1
    assert repo.issues[0].title == "Super updated issue title!"
    assert repo.issues[0].state == "closed"

    assert len(repo.pull_requests) == 1
    assert repo.pull_requests[0].title == "Super updated PR title!"
    assert repo.pull_requests[0].state == "closed"


@pytest.mark.anyio
async def test_sync_repository_task_not_found(sync_service):
    """
    Test that sync_repository_task logs an error and returns gracefully
    if the repository ID is not found.
    """
    random_id = uuid.uuid4()
    await sync_service.sync_repository_task(random_id)


@pytest.mark.anyio
async def test_sync_repository_task_db_commit_error(
    sync_service, respx_mock_github, db_repository, monkeypatch
):
    """
    Test that if a database commit error happens when saving the sync failure details,
    the background task logs the secondary error and exits gracefully.
    """
    repo_id = db_repository.id

    # Trigger 500 error from GitHub to force sync_repository_task into the except block
    respx_mock_github["get_repo"].mock(return_value=Response(500))

    # Monkeypatch AsyncSession.commit to always raise an exception
    from sqlalchemy.ext.asyncio import AsyncSession

    async def mock_commit(self):
        raise Exception("Database transaction commit failed on rollback status save")

    monkeypatch.setattr(AsyncSession, "commit", mock_commit)

    # Run background task - should catch database commit error and return gracefully
    await sync_service.sync_repository_task(repo_id)
