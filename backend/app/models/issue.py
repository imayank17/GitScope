import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Issue(Base):
    """SQLAlchemy model representing an issue in a repository."""

    __tablename__ = "issues"

    # Enforce unique issue number per repository
    __table_args__ = (
        UniqueConstraint(
            "repository_id",
            "number",
            name="uq_issue_repo_number",
        ),
    )

    # UUID Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    # Reference to Repository
    repository_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Issue Identity
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    state: Mapped[str] = mapped_column(String(20), nullable=False)

    # Submitter login
    user_login: Mapped[str] = mapped_column(String(255), nullable=False)

    # Labels (stored as JSON array of strings)
    labels: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Comment count
    comments: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # URL
    html_url: Mapped[str] = mapped_column(String(500), nullable=False)

    # GitHub Creation/Update timestamps (stored as strings to match API format)
    github_created_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    github_updated_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Internal Database Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationship back to Repository
    repository: Mapped["Repository"] = relationship(
        "Repository",
        back_populates="issues",
    )

    def __repr__(self) -> str:
        return (
            f"<Issue #{self.number} ({self.state}) in Repository {self.repository_id}>"
        )
