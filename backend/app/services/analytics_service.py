import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.snapshot import RepositorySnapshot


class AnalyticsService:
    """Service dedicated to reading analytical data directly from the database."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Args:
            db: Injected database AsyncSession.
        """
        self.db = db

    async def get_metrics_history(self, repository_id: uuid.UUID) -> List[RepositorySnapshot]:
        """
        Retrieve all daily historical metrics snapshots for a given repository ID,
        ordered chronologically.
        """
        stmt = (
            select(RepositorySnapshot)
            .where(RepositorySnapshot.repository_id == repository_id)
            .order_by(RepositorySnapshot.date.asc(), RepositorySnapshot.created_at.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
