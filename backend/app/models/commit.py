import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Commit(Base):
    """SQLAlchemy model representing a commit in a repository."""

    __tablename__ = "commits"

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

    # Commit Identity
    sha: Mapped[str] = mapped_column(
        String(40),
        unique=True,
        nullable=False,
        index=True,
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)

    # Author details (flattened from GitHub commit payload)
    author_name: Mapped[str] = mapped_column(String(255), nullable=False)
    author_email: Mapped[str] = mapped_column(String(255), nullable=False)
    author_date: Mapped[str] = mapped_column(String(50), nullable=False)

    # Committer details
    committer_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # URL
    html_url: Mapped[str] = mapped_column(String(500), nullable=False)

    # Internal Database Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationship back to Repository
    repository: Mapped["Repository"] = relationship(
        "Repository",
        back_populates="commits",
    )

    def __repr__(self) -> str:
        return f"<Commit {self.sha[:7]} in Repository {self.repository_id}>"
