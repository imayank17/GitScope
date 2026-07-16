import pytest
import respx
from httpx import AsyncClient, Response
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.repositories.github_repository import GitHubRepository
from app.services.github_service import GitHubService
from app.models.repository import Repository
from app.models.contributor import Contributor
from app.models.commit import Commit
from app.models.issue import Issue
from app.models.pull_request import PullRequest
from app.models.language import Language
from app.models.snapshot import RepositorySnapshot

# Import fixtures explicitly (pytest automatically registers them when imported or in conftest)
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
async def git_repo_layer(db):
    """Fixture that initializes the repository layer with a mocked GitHub Service."""
    # We use a standard AsyncClient inside tests to communicate with the mocked API
    async with AsyncClient() as client:
        service = GitHubService(client=client)
        yield GitHubRepository(db=db, github_service=service)


@pytest.mark.anyio
async def test_get_repo_cached_in_db(git_repo_layer, db_repository, db):
    """
    Test that if a repository already exists in the database,
    it returns the database model directly without contacting GitHub.
    """
    # Since we didn't activate respx here, if it tries to call the API it will fail/raise
    repo = await git_repo_layer.get_repo("gitscope-org", "gitscope-core")
    
    assert isinstance(repo, Repository)
    assert repo.id == db_repository.id
    assert repo.full_name == "gitscope-org/gitscope-core"


@pytest.mark.anyio
async def test_get_repo_not_cached_syncs_from_github(git_repo_layer, respx_mock_github, db):
    """
    Test that if a repository does not exist in the database,
    it is fetched from GitHub and saved along with all related models.
    """
    # Verify DB is currently empty
    stmt = select(Repository).where(Repository.full_name == "test-owner/test-repo")
    assert (await db.execute(stmt)).scalars().first() is None
    
    # Run sync from mock GitHub API
    repo = await git_repo_layer.get_repo("test-owner", "test-repo")
    
    assert isinstance(repo, Repository)
    assert repo.full_name == "test-owner/test-repo"
    assert repo.sync_status == "COMPLETED"
    
    # Query database to confirm persistence
    stmt = select(Repository).where(Repository.full_name == "test-owner/test-repo").options(
        selectinload(Repository.contributors),
        selectinload(Repository.commits),
        selectinload(Repository.languages),
        selectinload(Repository.pull_requests),
        selectinload(Repository.issues),
        selectinload(Repository.snapshots),
    )
    db_repo = (await db.execute(stmt)).scalars().first()
    assert db_repo is not None
    assert db_repo.github_id == 123456789
    
    # Verify child relations are mapped and saved
    assert len(db_repo.contributors) == 2
    assert len(db_repo.commits) == 2
    assert len(db_repo.languages) == 3
    assert len(db_repo.pull_requests) == 2
    assert len(db_repo.issues) == 1
    assert len(db_repo.snapshots) == 1
    
    # Verify commit sha uniqueness check worked
    assert db_repo.commits[0].sha == "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"


@pytest.mark.anyio
async def test_get_repo_partial_failures_handled(git_repo_layer, respx_mock_github, github_repo_data, db):
    """
    Test that if optional GitHub endpoints fail (e.g. issues or languages),
    repository synchronization still succeeds with partial data.
    """
    # Cause the languages and issues endpoints to return 500 errors
    respx_mock_github["get_languages"].mock(
        return_value=Response(500)
    )
    respx_mock_github["get_issues"].mock(
        return_value=Response(500)
    )
    
    repo = await git_repo_layer.get_repo("test-owner", "test-repo")
    
    assert repo is not None
    assert repo.sync_status == "COMPLETED"
    
    # Re-fetch from DB
    stmt = select(Repository).where(Repository.full_name == "test-owner/test-repo").options(
        selectinload(Repository.contributors),
        selectinload(Repository.commits),
        selectinload(Repository.languages),
        selectinload(Repository.pull_requests),
        selectinload(Repository.issues),
        selectinload(Repository.snapshots),
    )
    db_repo = (await db.execute(stmt)).scalars().first()
    
    assert len(db_repo.languages) == 0
    assert len(db_repo.issues) == 0
    # Contributors and commits should still be fetched
    assert len(db_repo.contributors) == 2
    assert len(db_repo.commits) == 2


@pytest.mark.anyio
async def test_get_contributors_cached_vs_live(git_repo_layer, db_repository, respx_mock_github):
    """
    Test that contributors are retrieved from the database when cached,
    or from the live API when not cached.
    """
    # Case 1: Cached in DB (returns database Contributor models)
    contribs, total_pages = await git_repo_layer.get_contributors("gitscope-org", "gitscope-core")
    assert len(contribs) == 2
    assert isinstance(contribs[0], Contributor)
    assert contribs[0].login == "user-alice"
    assert total_pages == 1
    
    # Case 2: Not Cached (calls GitHub API and returns lists of dicts)
    contribs, total_pages = await git_repo_layer.get_contributors("test-owner", "test-repo")
    assert len(contribs) == 2
    assert isinstance(contribs[0], dict)
    assert contribs[0]["login"] == "contrib-1"
    assert total_pages == 1


@pytest.mark.anyio
async def test_get_commits_cached_vs_live(git_repo_layer, db_repository, respx_mock_github):
    """
    Test that commits are retrieved from the database when cached,
    or from the live API when not cached.
    """
    # Case 1: Cached in DB
    commits, total_pages = await git_repo_layer.get_commits("gitscope-org", "gitscope-core")
    assert len(commits) == 1
    assert isinstance(commits[0], Commit)
    assert commits[0].author_name == "Alice Smith"
    
    # Case 2: Not Cached
    commits, total_pages = await git_repo_layer.get_commits("test-owner", "test-repo")
    assert len(commits) == 2
    assert isinstance(commits[0], dict)
    assert commits[0]["commit"]["message"] == "Initial commit"


@pytest.mark.anyio
async def test_get_languages_cached_vs_live(git_repo_layer, db_repository, respx_mock_github):
    """
    Test that languages are retrieved from the database when cached,
    or from the live API when not cached.
    """
    # Case 1: Cached in DB
    langs = await git_repo_layer.get_languages("gitscope-org", "gitscope-core")
    assert len(langs) == 2
    assert isinstance(langs[0], Language)
    assert langs[0].name == "Python"
    
    # Case 2: Not Cached
    langs = await git_repo_layer.get_languages("test-owner", "test-repo")
    assert isinstance(langs, dict)
    assert "Python" in langs


@pytest.mark.anyio
async def test_get_pull_requests_cached_vs_live(git_repo_layer, db_repository, respx_mock_github):
    """
    Test that pull requests are retrieved from the database when cached,
    or from the live API when not cached (with state filters).
    """
    # Case 1: Cached in DB
    prs, total_pages = await git_repo_layer.get_pull_requests("gitscope-org", "gitscope-core", state="all")
    assert len(prs) == 1
    assert isinstance(prs[0], PullRequest)
    assert prs[0].title == "Refactor: Optimize DB indices"
    
    # Case 2: Not Cached
    prs, total_pages = await git_repo_layer.get_pull_requests("test-owner", "test-repo", state="all")
    assert len(prs) == 2
    assert isinstance(prs[0], dict)
    assert prs[0]["title"] == "Feature: Add Database layer"


@pytest.mark.anyio
async def test_get_issues_cached_vs_live(git_repo_layer, db_repository, respx_mock_github):
    """
    Test that issues are retrieved from the database when cached,
    or from the live API when not cached (with state filters).
    """
    # Case 1: Cached in DB
    issues, total_pages = await git_repo_layer.get_issues("gitscope-org", "gitscope-core", state="all")
    assert len(issues) == 1
    assert isinstance(issues[0], Issue)
    assert issues[0].title == "Bug: Snapshot division by zero"
    
    # Case 2: Not Cached
    issues, total_pages = await git_repo_layer.get_issues("test-owner", "test-repo", state="all")
    # Our mock setup filters pull requests out of the issues list (total: 3 items, 1 issue, 2 PRs)
    # So we expect 1 true issue to be returned
    assert len(issues) == 1
    assert isinstance(issues[0], dict)
    assert issues[0]["title"] == "Bug: Cache miss on repo details"
