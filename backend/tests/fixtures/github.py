import re
import pytest
import respx
from httpx import Response
from app.core.config import settings


@pytest.fixture
def github_repo_data():
    return {
        "id": 123456789,
        "name": "test-repo",
        "full_name": "test-owner/test-repo",
        "description": "A test repository for GitScope",
        "owner": {
            "login": "test-owner",
            "avatar_url": "https://avatars.githubusercontent.com/u/9919?v=4",
        },
        "html_url": "https://github.com/test-owner/test-repo",
        "clone_url": "https://github.com/test-owner/test-repo.git",
        "language": "Python",
        "default_branch": "main",
        "visibility": "public",
        "stargazers_count": 42,
        "forks_count": 10,
        "open_issues_count": 5,
        "watchers_count": 42,
        "topics": ["fastapi", "sqlalchemy", "pytest"],
        "created_at": "2026-01-01T12:00:00Z",
        "updated_at": "2026-07-01T12:00:00Z",
    }


@pytest.fixture
def github_contributors_data():
    return [
        {
            "id": 101,
            "login": "contrib-1",
            "avatar_url": "https://avatars.githubusercontent.com/u/101?v=4",
            "html_url": "https://github.com/contrib-1",
            "contributions": 100,
        },
        {
            "id": 102,
            "login": "contrib-2",
            "avatar_url": "https://avatars.githubusercontent.com/u/102?v=4",
            "html_url": "https://github.com/contrib-2",
            "contributions": 50,
        },
    ]


@pytest.fixture
def github_commits_data():
    return [
        {
            "sha": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
            "commit": {
                "message": "Initial commit",
                "author": {
                    "name": "Developer One",
                    "email": "dev1@example.com",
                    "date": "2026-06-15T09:00:00Z",
                },
                "committer": {"name": "Developer One"},
            },
            "html_url": "https://github.com/test-owner/test-repo/commit/a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
        },
        {
            "sha": "b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0a1",
            "commit": {
                "message": "Add test structure",
                "author": {
                    "name": "Developer Two",
                    "email": "dev2@example.com",
                    "date": "2026-06-20T10:00:00Z",
                },
                "committer": {"name": "Developer Two"},
            },
            "html_url": "https://github.com/test-owner/test-repo/commit/b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0a1",
        },
    ]


@pytest.fixture
def github_languages_data():
    return {"Python": 80000, "HTML": 15000, "CSS": 5000}


@pytest.fixture
def github_pulls_data():
    return [
        {
            "number": 1,
            "title": "Feature: Add Database layer",
            "state": "closed",
            "user": {"login": "developer-one"},
            "created_at": "2026-06-16T08:00:00Z",
            "updated_at": "2026-06-17T09:00:00Z",
            "html_url": "https://github.com/test-owner/test-repo/pull/1",
            "labels": [{"name": "enhancement"}],
            "merged_at": "2026-06-17T09:00:00Z",
            "draft": False,
            "pull_request": {
                "html_url": "https://github.com/test-owner/test-repo/pull/1"
            },
        },
        {
            "number": 2,
            "title": "WIP: Add caching service",
            "state": "open",
            "user": {"login": "developer-two"},
            "created_at": "2026-07-01T10:00:00Z",
            "updated_at": "2026-07-02T11:00:00Z",
            "html_url": "https://github.com/test-owner/test-repo/pull/2",
            "labels": [{"name": "bug"}, {"name": "help wanted"}],
            "merged_at": None,
            "draft": True,
            "pull_request": {
                "html_url": "https://github.com/test-owner/test-repo/pull/2"
            },
        },
    ]


@pytest.fixture
def github_issues_data():
    return [
        {
            "number": 3,
            "title": "Bug: Cache miss on repo details",
            "state": "open",
            "user": {"login": "user-bug"},
            "created_at": "2026-07-03T15:00:00Z",
            "updated_at": "2026-07-04T16:00:00Z",
            "html_url": "https://github.com/test-owner/test-repo/issues/3",
            "labels": [{"name": "bug"}],
            "comments": 3,
        }
    ]


@pytest.fixture
def respx_mock_github(
    github_repo_data,
    github_contributors_data,
    github_commits_data,
    github_languages_data,
    github_pulls_data,
    github_issues_data,
):
    """
    A respx mock context fixture configured with named generic regex responses for GitHub API endpoints.
    Allows testing components that talk to the GitHub API without hitting the real network.
    """
    with respx.mock(
        assert_all_called=False, base_url=settings.GITHUB_API_BASE_URL
    ) as mock:
        # Mock Repo metadata
        mock.get(re.compile(r"/repos/[^/]+/[^/]+(\?.*)?$"), name="get_repo").mock(
            return_value=Response(200, json=github_repo_data)
        )

        # Mock Contributors
        mock.get(
            re.compile(r"/repos/[^/]+/[^/]+/contributors(\?.*)?$"),
            name="get_contributors",
        ).mock(
            return_value=Response(
                200, json=github_contributors_data, headers={"Link": ""}
            )
        )

        # Mock Commits
        mock.get(
            re.compile(r"/repos/[^/]+/[^/]+/commits(\?.*)?$"), name="get_commits"
        ).mock(
            return_value=Response(200, json=github_commits_data, headers={"Link": ""})
        )

        # Mock Languages
        mock.get(
            re.compile(r"/repos/[^/]+/[^/]+/languages(\?.*)?$"), name="get_languages"
        ).mock(return_value=Response(200, json=github_languages_data))

        # Mock Pull Requests
        mock.get(
            re.compile(r"/repos/[^/]+/[^/]+/pulls(\?.*)?$"), name="get_pulls"
        ).mock(return_value=Response(200, json=github_pulls_data, headers={"Link": ""}))

        # Mock Issues (which returns pulls + issues in GitHub API)
        # In our tests, we will mock it returning both pulls and issues, since we filter out pulls
        all_issues_mock = github_issues_data + github_pulls_data
        mock.get(
            re.compile(r"/repos/[^/]+/[^/]+/issues(\?.*)?$"), name="get_issues"
        ).mock(return_value=Response(200, json=all_issues_mock, headers={"Link": ""}))

        yield mock
