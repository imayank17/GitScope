import pytest
import uuid
from datetime import datetime, timezone
from app.models.repository import Repository
from app.models.contributor import Contributor
from app.models.commit import Commit
from app.models.issue import Issue
from app.models.pull_request import PullRequest
from app.models.language import Language
from app.models.snapshot import RepositorySnapshot

@pytest.fixture
def sample_repo_dict():
    """Returns a dict representation of a Repository for easy validation or insertion."""
    return {
        "github_id": 99887766,
        "name": "gitscope-core",
        "full_name": "gitscope-org/gitscope-core",
        "description": "GitScope Core Backend Engine",
        "owner_login": "gitscope-org",
        "owner_avatar_url": "https://avatars.githubusercontent.com/u/9988?v=4",
        "html_url": "https://github.com/gitscope-org/gitscope-core",
        "clone_url": "https://github.com/gitscope-org/gitscope-core.git",
        "language": "Python",
        "default_branch": "develop",
        "visibility": "public",
        "stars": 100,
        "forks": 25,
        "open_issues": 10,
        "watchers": 100,
        "topics": ["metrics", "analytics", "github-api"],
        "github_created_at": "2026-02-15T08:00:00Z",
        "github_updated_at": "2026-07-10T12:00:00Z"
    }

@pytest.fixture
async def db_repository(db, sample_repo_dict):
    """Inserts a Repository instance into the database and returns it."""
    repo = Repository(
        id=uuid.uuid4(),
        github_id=sample_repo_dict["github_id"],
        name=sample_repo_dict["name"],
        full_name=sample_repo_dict["full_name"],
        description=sample_repo_dict["description"],
        owner_login=sample_repo_dict["owner_login"],
        owner_avatar_url=sample_repo_dict["owner_avatar_url"],
        html_url=sample_repo_dict["html_url"],
        clone_url=sample_repo_dict["clone_url"],
        language=sample_repo_dict["language"],
        default_branch=sample_repo_dict["default_branch"],
        visibility=sample_repo_dict["visibility"],
        stars=sample_repo_dict["stars"],
        forks=sample_repo_dict["forks"],
        open_issues=sample_repo_dict["open_issues"],
        watchers=sample_repo_dict["watchers"],
        topics=sample_repo_dict["topics"],
        github_created_at=sample_repo_dict["github_created_at"],
        github_updated_at=sample_repo_dict["github_updated_at"],
        sync_status="COMPLETED",
        last_synced_at=datetime.now(timezone.utc),
    )
    
    # Add associated contributors
    repo.contributors = [
        Contributor(
            github_id=901,
            login="user-alice",
            avatar_url="https://avatars.githubusercontent.com/u/901",
            html_url="https://github.com/user-alice",
            contributions=120
        ),
        Contributor(
            github_id=902,
            login="user-bob",
            avatar_url="https://avatars.githubusercontent.com/u/902",
            html_url="https://github.com/user-bob",
            contributions=40
        )
    ]
    
    # Add commits
    repo.commits = [
        Commit(
            sha="c0ffee112233445566778899aabbccddeeff0011",
            message="Feature: Core analytics calculations",
            author_name="Alice Smith",
            author_email="alice@gitscope.org",
            author_date="2026-07-01T10:00:00Z",
            committer_name="Alice Smith",
            html_url="https://github.com/gitscope-org/gitscope-core/commit/c0ffee112233"
        )
    ]
    
    # Add issues
    repo.issues = [
        Issue(
            number=42,
            title="Bug: Snapshot division by zero",
            state="open",
            user_login="user-bob",
            labels=["bug", "high-priority"],
            comments=2,
            html_url="https://github.com/gitscope-org/gitscope-core/issues/42",
            github_created_at="2026-07-02T11:00:00Z",
            github_updated_at="2026-07-02T13:00:00Z"
        )
    ]
    
    # Add pull requests
    repo.pull_requests = [
        PullRequest(
            number=5,
            title="Refactor: Optimize DB indices",
            state="open",
            user_login="user-alice",
            labels=["performance"],
            draft=False,
            merged_at=None,
            html_url="https://github.com/gitscope-org/gitscope-core/pull/5",
            github_created_at="2026-07-03T09:00:00Z",
            github_updated_at="2026-07-04T10:00:00Z"
        )
    ]
    
    # Add languages
    repo.languages = [
        Language(name="Python", bytes=90000, percentage=90.0),
        Language(name="Shell", bytes=10000, percentage=10.0)
    ]
    
    # Add daily snapshot history
    repo.snapshots = [
        RepositorySnapshot(
            date=datetime.now(timezone.utc).date(),
            stars=100,
            forks=25,
            open_issues=10,
            watchers=100,
            commit_count=1,
            pull_request_count=1
        )
    ]
    
    db.add(repo)
    await db.commit()
    await db.refresh(repo)
    return repo
