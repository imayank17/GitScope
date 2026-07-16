import uuid
from datetime import datetime
from typing import Dict, List, Set

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import AsyncSessionLocal
from app.models.commit import Commit
from app.models.contributor import Contributor
from app.models.issue import Issue
from app.models.language import Language
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.snapshot import RepositorySnapshot
from app.services.github_service import GitHubService
from app.core.logging import get_logger

logger = get_logger("app.services.sync_service")


class SynchronizationService:
    """Service to handle background repository updates, upserts, and daily snapshots."""

    def __init__(self, github_service: GitHubService) -> None:
        """
        Args:
            github_service: Injected GitHubService instance.
        """
        self.github = github_service

    async def sync_repository(self, repository: Repository, db: AsyncSession) -> None:
        """
        Runs the actual update queries against GitHub, merges changes into the ORM objects,
        inserts a daily metrics snapshot, and commits the transaction.
        """
        owner = repository.owner_login
        repo_name = repository.name
        
        logger.info(f"Sync started for repository: {repository.full_name}")

        # 1. Fetch latest metadata and sub-resources from GitHub API (up to 100 items for sync batch)
        repo_data = await self.github.get_repository(owner, repo_name)
        
        try:
            contributors_data, _ = await self.github.get_contributors(owner, repo_name, page=1, per_page=100)
        except Exception as e:
            logger.warning(f"Failed to fetch contributors during sync for {repository.full_name}: {e}")
            contributors_data = []

        try:
            commits_data, _ = await self.github.get_commits(owner, repo_name, page=1, per_page=100)
        except Exception as e:
            logger.warning(f"Failed to fetch commits during sync for {repository.full_name}: {e}")
            commits_data = []

        try:
            languages_data = await self.github.get_languages(owner, repo_name)
        except Exception as e:
            logger.warning(f"Failed to fetch languages during sync for {repository.full_name}: {e}")
            languages_data = {}

        try:
            pulls_data, _ = await self.github.get_pull_requests(owner, repo_name, state="all", page=1, per_page=100)
        except Exception as e:
            logger.warning(f"Failed to fetch pull requests during sync for {repository.full_name}: {e}")
            pulls_data = []

        try:
            issues_data, _ = await self.github.get_issues(owner, repo_name, state="all", page=1, per_page=100)
        except Exception as e:
            logger.warning(f"Failed to fetch issues during sync for {repository.full_name}: {e}")
            issues_data = []

        # 2. Update Repository fields
        repository.name = repo_data["name"]
        repository.full_name = repo_data["full_name"]
        repository.description = repo_data.get("description")
        repository.owner_login = repo_data["owner"]["login"]
        repository.owner_avatar_url = repo_data["owner"]["avatar_url"]
        repository.html_url = repo_data["html_url"]
        repository.clone_url = repo_data["clone_url"]
        repository.language = repo_data.get("language")
        repository.default_branch = repo_data.get("default_branch", "main")
        repository.visibility = repo_data.get("visibility", "public")
        repository.stars = repo_data["stargazers_count"]
        repository.forks = repo_data["forks_count"]
        repository.open_issues = repo_data["open_issues_count"]
        repository.watchers = repo_data["watchers_count"]
        repository.topics = repo_data.get("topics", [])
        repository.github_updated_at = repo_data["updated_at"]

        # 3. Upsert Contributors (in-place updates to avoid duplicates or key violations)
        existing_contributors_stmt = select(Contributor).where(Contributor.repository_id == repository.id)
        existing_contributors_res = await db.execute(existing_contributors_stmt)
        existing_contribs_map: Dict[int, Contributor] = {
            c.github_id: c for c in existing_contributors_res.scalars().all()
        }

        for c_data in contributors_data:
            c_github_id = c_data["id"]
            if c_github_id in existing_contribs_map:
                # Update existing contributor
                contrib = existing_contribs_map[c_github_id]
                contrib.login = c_data["login"]
                contrib.avatar_url = c_data["avatar_url"]
                contrib.html_url = c_data["html_url"]
                contrib.contributions = c_data["contributions"]
            else:
                # Add new contributor
                new_contrib = Contributor(
                    repository_id=repository.id,
                    github_id=c_github_id,
                    login=c_data["login"],
                    avatar_url=c_data["avatar_url"],
                    html_url=c_data["html_url"],
                    contributions=c_data["contributions"],
                )
                db.add(new_contrib)

        # 4. Insert new Commits only (SHAs are globally unique and commits are immutable)
        incoming_shas = [commit["sha"] for commit in commits_data]
        existing_shas: Set[str] = set()
        if incoming_shas:
            existing_shas_stmt = select(Commit.sha).where(Commit.sha.in_(incoming_shas))
            existing_shas_res = await db.execute(existing_shas_stmt)
            existing_shas = set(existing_shas_res.scalars().all())

        for c_data in commits_data:
            sha = c_data["sha"]
            if sha not in existing_shas:
                new_commit = Commit(
                    repository_id=repository.id,
                    sha=sha,
                    message=c_data["commit"]["message"],
                    author_name=c_data["commit"]["author"]["name"],
                    author_email=c_data["commit"]["author"]["email"],
                    author_date=c_data["commit"]["author"]["date"],
                    committer_name=c_data["commit"]["committer"]["name"],
                    html_url=c_data["html_url"],
                )
                db.add(new_commit)

        # 5. Upsert Issues (in-place updates on number)
        existing_issues_stmt = select(Issue).where(Issue.repository_id == repository.id)
        existing_issues_res = await db.execute(existing_issues_stmt)
        existing_issues_map: Dict[int, Issue] = {
            issue.number: issue for issue in existing_issues_res.scalars().all()
        }

        for issue_data in issues_data:
            num = issue_data["number"]
            if num in existing_issues_map:
                issue = existing_issues_map[num]
                issue.title = issue_data["title"]
                issue.state = issue_data["state"]
                issue.user_login = issue_data["user"]["login"]
                issue.labels = [label["name"] for label in issue_data.get("labels", [])]
                issue.comments = issue_data.get("comments", 0)
                issue.html_url = issue_data["html_url"]
                issue.github_updated_at = issue_data["updated_at"]
            else:
                new_issue = Issue(
                    repository_id=repository.id,
                    number=num,
                    title=issue_data["title"],
                    state=issue_data["state"],
                    user_login=issue_data["user"]["login"],
                    labels=[label["name"] for label in issue_data.get("labels", [])],
                    comments=issue_data.get("comments", 0),
                    html_url=issue_data["html_url"],
                    github_created_at=issue_data["created_at"],
                    github_updated_at=issue_data["updated_at"],
                )
                db.add(new_issue)

        # 6. Upsert Pull Requests (in-place updates on number)
        existing_prs_stmt = select(PullRequest).where(PullRequest.repository_id == repository.id)
        existing_prs_res = await db.execute(existing_prs_stmt)
        existing_prs_map: Dict[int, PullRequest] = {
            pr.number: pr for pr in existing_prs_res.scalars().all()
        }

        for pr_data in pulls_data:
            num = pr_data["number"]
            if num in existing_prs_map:
                pr = existing_prs_map[num]
                pr.title = pr_data["title"]
                pr.state = pr_data["state"]
                pr.user_login = pr_data["user"]["login"]
                pr.labels = [label["name"] for label in pr_data.get("labels", [])]
                pr.draft = pr_data.get("draft", False)
                pr.merged_at = pr_data.get("merged_at")
                pr.html_url = pr_data["html_url"]
                pr.github_updated_at = pr_data["updated_at"]
            else:
                new_pr = PullRequest(
                    repository_id=repository.id,
                    number=num,
                    title=pr_data["title"],
                    state=pr_data["state"],
                    user_login=pr_data["user"]["login"],
                    labels=[label["name"] for label in pr_data.get("labels", [])],
                    draft=pr_data.get("draft", False),
                    merged_at=pr_data.get("merged_at"),
                    html_url=pr_data["html_url"],
                    github_created_at=pr_data["created_at"],
                    github_updated_at=pr_data["updated_at"],
                )
                db.add(new_pr)

        # 7. Update Languages: delete existing language entries and rewrite
        delete_langs_stmt = delete(Language).where(Language.repository_id == repository.id)
        await db.execute(delete_langs_stmt)

        total_bytes = sum(languages_data.values())
        for lang_name, bytes_count in languages_data.items():
            new_lang = Language(
                repository_id=repository.id,
                name=lang_name,
                bytes=bytes_count,
                percentage=round((bytes_count / total_bytes) * 100, 2) if total_bytes > 0 else 0.0,
            )
            db.add(new_lang)

        # Flush database changes so counts reflect all new insertions
        await db.flush()

        # 8. Create historical snapshot record
        commit_count_stmt = select(func.count(Commit.id)).where(Commit.repository_id == repository.id)
        pull_count_stmt = select(func.count(PullRequest.id)).where(PullRequest.repository_id == repository.id)
        
        commit_count = (await db.execute(commit_count_stmt)).scalar() or 0
        pull_count = (await db.execute(pull_count_stmt)).scalar() or 0

        snapshot = RepositorySnapshot(
            repository_id=repository.id,
            date=datetime.utcnow().date(),
            stars=repository.stars,
            forks=repository.forks,
            open_issues=repository.open_issues,
            watchers=repository.watchers,
            commit_count=commit_count,
            pull_request_count=pull_count,
        )
        db.add(snapshot)
        logger.info(f"Historical snapshot created for {repository.full_name} on date {snapshot.date}")

        # 9. Mark status as completed
        repository.sync_status = "COMPLETED"
        repository.last_synced_at = datetime.utcnow()
        repository.sync_error = None
        logger.info(f"Sync completed successfully for repository: {repository.full_name}")

    async def sync_repository_task(self, repository_id: uuid.UUID) -> None:
        """
        Background task executor running on a separate database session context.
        """
        logger.info(f"Starting background synchronization for repository ID {repository_id}")
        async with AsyncSessionLocal() as db:
            # Query the repository instance
            stmt = select(Repository).where(Repository.id == repository_id)
            repository = (await db.execute(stmt)).scalars().first()

            if not repository:
                logger.error(f"Synchronization failed: Repository ID {repository_id} not found in database.")
                return

            try:
                await self.sync_repository(repository, db)
                await db.commit()
                logger.info(f"Background synchronization completed successfully for {repository.full_name}")
            except Exception as e:
                logger.exception(f"Error during background synchronization for {repository.full_name}: {e}")
                # Re-fetch repo inside error context if session is rolled back
                try:
                    await db.rollback()
                    repository.sync_status = "FAILED"
                    repository.sync_error = str(e)
                    await db.commit()
                except Exception as db_err:
                    logger.error(f"Failed to record sync error status to database: {db_err}")
