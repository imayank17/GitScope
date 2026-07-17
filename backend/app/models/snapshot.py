import uuid
import datetime
from sqlalchemy import DateTime, Date, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class RepositorySnapshot(Base):
    """SQLAlchemy model representing a daily historical metrics snapshot for a repository."""

    __tablename__ = "repository_snapshots"

    # UUID Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    # Reference to Repository
    repository_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # The date of the snapshot (defaulting to the current database date)
    date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        default=func.current_date(),
    )

    # Historical Metrics
    stars: Mapped[int] = mapped_column(Integer, nullable=False)
    forks: Mapped[int] = mapped_column(Integer, nullable=False)
    open_issues: Mapped[int] = mapped_column(Integer, nullable=False)
    watchers: Mapped[int] = mapped_column(Integer, nullable=False)
    commit_count: Mapped[int] = mapped_column(Integer, nullable=False)
    pull_request_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Internal Database Timestamps
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationship back to Repository
    repository: Mapped["Repository"] = relationship(
        "Repository",
        back_populates="snapshots",
    )

    def __repr__(self) -> str:
        return f"<RepositorySnapshot {self.date} for Repository {self.repository_id}>"
