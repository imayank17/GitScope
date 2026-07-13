import math
from datetime import datetime
from typing import Dict, List, Tuple, Union

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commit import Commit
from app.models.contributor import Contributor
from app.models.issue import Issue
from app.models.language import Language
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.snapshot import RepositorySnapshot
from app.services.github_service import GitHubService


class GitHubRepository:
    """Repository layer for GitScope handling database persistence and GitHub API access."""

    def __init__(self, db: AsyncSession, github_service: GitHubService) -> None:
        """
        Args:
            db: Injected AsyncSession instance for database operations.
            github_service: Injected GitHubService instance for external API access.
        """
        self.db = db
        self.github = github_service

    async def _get_db_repo_by_name(self, owner: str, repo: str) -> Union[Repository, None]:
        """Helper to lookup a repository in the database by full_name (case-insensitive)."""
        full_name = f"{owner}/{repo}"
        stmt = select(Repository).where(func.lower(Repository.full_name) == full_name.lower())
        result = await self.db.execute(stmt)
        return result.scalars().first()

    # Repository details 

    async def get_repo(self, owner: str, repo: str) -> Union[Repository, dict]:
        """
        Retrieve repository metadata. Checks the database first.
        If it exists, returns the database Repository model.
        If not, fetches all data from GitHub API and saves it.
        """
        db_repo = await self._get_db_repo_by_name(owner, repo)
        if db_repo:
            return db_repo

        # Repository does not exist in DB: fetch all components from GitHub API
        # We fetch up to 100 items per list for initial sync batch
        repo_data = await self.github.get_repository(owner, repo)
        
        # Catch and ignore errors for optional sub-resources to guarantee robust analysis
        try:
            contributors_data, _ = await self.github.get_contributors(owner, repo, page=1, per_page=100)
        except Exception:
            contributors_data = []

        try:
            commits_data, _ = await self.github.get_commits(owner, repo, page=1, per_page=100)
        except Exception:
            commits_data = []

        try:
            languages_data = await self.github.get_languages(owner, repo)
        except Exception:
            languages_data = {}

        try:
            pulls_data, _ = await self.github.get_pull_requests(owner, repo, state="all", page=1, per_page=100)
        except Exception:
            pulls_data = []

        try:
            issues_data, _ = await self.github.get_issues(owner, repo, state="all", page=1, per_page=100)
        except Exception:
            issues_data = []

        # Start a new transaction/savepoint to persist repository and all child collections
        new_repo = Repository(
            github_id=repo_data["id"],
            name=repo_data["name"],
            full_name=repo_data["full_name"],
            description=repo_data.get("description"),
            owner_login=repo_data["owner"]["login"],
            owner_avatar_url=repo_data["owner"]["avatar_url"],
            html_url=repo_data["html_url"],
            clone_url=repo_data["clone_url"],
            language=repo_data.get("language"),
            default_branch=repo_data.get("default_branch", "main"),
            visibility=repo_data.get("visibility", "public"),
            stars=repo_data["stargazers_count"],
            forks=repo_data["forks_count"],
            open_issues=repo_data["open_issues_count"],
            watchers=repo_data["watchers_count"],
            topics=repo_data.get("topics", []),
            github_created_at=repo_data["created_at"],
            github_updated_at=repo_data["updated_at"],
            sync_status="COMPLETED",
            last_synced_at=datetime.utcnow(),
        )

        # Build child objects via SQLAlchemy relationship back-populates
        new_repo.contributors = [
            Contributor(
                github_id=c["id"],
                login=c["login"],
                avatar_url=c["avatar_url"],
                html_url=c["html_url"],
                contributions=c["contributions"],
            )
            for c in contributors_data
        ]

        # Prevent duplicate inserts on Commit.sha (globally unique constraint)
        shas = [c["sha"] for c in commits_data]
        existing_shas = set()
        if shas:
            stmt = select(Commit.sha).where(Commit.sha.in_(shas))
            res = await self.db.execute(stmt)
            existing_shas = set(res.scalars().all())

        new_repo.commits = [
            Commit(
                sha=c["sha"],
                message=c["commit"]["message"],
                author_name=c["commit"]["author"]["name"],
                author_email=c["commit"]["author"]["email"],
                author_date=c["commit"]["author"]["date"],
                committer_name=c["commit"]["committer"]["name"],
                html_url=c["html_url"],
            )
            for c in commits_data
            if c["sha"] not in existing_shas
        ]

        new_repo.issues = [
            Issue(
                number=issue["number"],
                title=issue["title"],
                state=issue["state"],
                user_login=issue["user"]["login"],
                labels=[label["name"] for label in issue.get("labels", [])],
                comments=issue.get("comments", 0),
                html_url=issue["html_url"],
                github_created_at=issue["created_at"],
                github_updated_at=issue["updated_at"],
            )
            for issue in issues_data
        ]

        new_repo.pull_requests = [
            PullRequest(
                number=pr["number"],
                title=pr["title"],
                state=pr["state"],
                user_login=pr["user"]["login"],
                labels=[label["name"] for label in pr.get("labels", [])],
                draft=pr.get("draft", False),
                merged_at=pr.get("merged_at"),
                html_url=pr["html_url"],
                github_created_at=pr["created_at"],
                github_updated_at=pr["updated_at"],
            )
            for pr in pulls_data
        ]

        total_bytes = sum(languages_data.values())
        new_repo.languages = [
            Language(
                name=lang,
                bytes=bytes_count,
                percentage=round((bytes_count / total_bytes) * 100, 2) if total_bytes > 0 else 0.0,
            )
            for lang, bytes_count in languages_data.items()
        ]

        # Add initial daily metrics snapshot
        new_repo.snapshots = [
            RepositorySnapshot(
                date=datetime.utcnow().date(),
                stars=new_repo.stars,
                forks=new_repo.forks,
                open_issues=new_repo.open_issues,
                watchers=new_repo.watchers,
                commit_count=len(new_repo.commits),
                pull_request_count=len(new_repo.pull_requests),
            )
        ]

        self.db.add(new_repo)
        await self.db.commit()
        await self.db.refresh(new_repo)
        return new_repo

    # Contributors 

    async def get_contributors(
        self, owner: str, repo: str, page: int = 1, per_page: int = 30,
    ) -> Tuple[List[Union[Contributor, dict]], int]:
        """
        Fetch repository contributors. Queries database if the repo exists.
        Falls back to GitHub API if not analyzed.
        """
        db_repo = await self._get_db_repo_by_name(owner, repo)
        if db_repo:
            # Count contributors in database
            count_stmt = select(func.count(Contributor.id)).where(Contributor.repository_id == db_repo.id)
            total_count = (await self.db.execute(count_stmt)).scalar() or 0
            total_pages = math.ceil(total_count / per_page) if total_count > 0 else 1

            # Fetch contributors page
            select_stmt = (
                select(Contributor)
                .where(Contributor.repository_id == db_repo.id)
                .order_by(Contributor.contributions.desc())
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
            result = await self.db.execute(select_stmt)
            return result.scalars().all(), total_pages

        return await self.github.get_contributors(owner, repo, page, per_page)

    # Commits 

    async def get_commits(
        self, owner: str, repo: str, page: int = 1, per_page: int = 30,
    ) -> Tuple[List[Union[Commit, dict]], int]:
        """
        Fetch repository commits. Queries database if the repo exists.
        Falls back to GitHub API if not analyzed.
        """
        db_repo = await self._get_db_repo_by_name(owner, repo)
        if db_repo:
            count_stmt = select(func.count(Commit.id)).where(Commit.repository_id == db_repo.id)
            total_count = (await self.db.execute(count_stmt)).scalar() or 0
            total_pages = math.ceil(total_count / per_page) if total_count > 0 else 1

            select_stmt = (
                select(Commit)
                .where(Commit.repository_id == db_repo.id)
                .order_by(Commit.author_date.desc())
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
            result = await self.db.execute(select_stmt)
            return result.scalars().all(), total_pages

        return await self.github.get_commits(owner, repo, page, per_page)

    # Languages 

    async def get_languages(self, owner: str, repo: str) -> Union[List[Language], dict]:
        """
        Fetch repository language breakdown. Queries database if the repo exists.
        Falls back to GitHub API if not analyzed.
        """
        db_repo = await self._get_db_repo_by_name(owner, repo)
        if db_repo:
            select_stmt = select(Language).where(Language.repository_id == db_repo.id).order_by(Language.bytes.desc())
            result = await self.db.execute(select_stmt)
            return result.scalars().all()

        return await self.github.get_languages(owner, repo)

    # Pull Requests 

    async def get_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        page: int = 1,
        per_page: int = 30,
    ) -> Tuple[List[Union[PullRequest, dict]], int]:
        """
        Fetch repository pull requests. Queries database if the repo exists.
        Falls back to GitHub API if not analyzed.
        """
        db_repo = await self._get_db_repo_by_name(owner, repo)
        if db_repo:
            query = select(PullRequest).where(PullRequest.repository_id == db_repo.id)
            if state != "all":
                query = query.where(PullRequest.state == state)

            count_stmt = select(func.count()).select_from(query.subquery())
            total_count = (await self.db.execute(count_stmt)).scalar() or 0
            total_pages = math.ceil(total_count / per_page) if total_count > 0 else 1

            select_stmt = query.order_by(PullRequest.number.desc()).offset((page - 1) * per_page).limit(per_page)
            result = await self.db.execute(select_stmt)
            return result.scalars().all(), total_pages

        return await self.github.get_pull_requests(owner, repo, state, page, per_page)

    # Issues 

    async def get_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        page: int = 1,
        per_page: int = 30,
    ) -> Tuple[List[Union[Issue, dict]], int]:
        """
        Fetch repository issues (excluding PRs). Queries database if the repo exists.
        Falls back to GitHub API if not analyzed.
        """
        db_repo = await self._get_db_repo_by_name(owner, repo)
        if db_repo:
            query = select(Issue).where(Issue.repository_id == db_repo.id)
            if state != "all":
                query = query.where(Issue.state == state)

            count_stmt = select(func.count()).select_from(query.subquery())
            total_count = (await self.db.execute(count_stmt)).scalar() or 0
            total_pages = math.ceil(total_count / per_page) if total_count > 0 else 1

            select_stmt = query.order_by(Issue.number.desc()).offset((page - 1) * per_page).limit(per_page)
            result = await self.db.execute(select_stmt)
            return result.scalars().all(), total_pages

        return await self.github.get_issues(owner, repo, state, page, per_page)