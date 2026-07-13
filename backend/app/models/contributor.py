import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Contributor(Base):
    """SQLAlchemy model representing a contributor to a repository."""

    __tablename__ = "contributors"

    # Enforce unique contributor per repository
    __table_args__ = (
        UniqueConstraint(
            "repository_id",
            "github_id",
            name="uq_contributor_repo_github_id",
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

    # Contributor Identity (from GitHub)
    github_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    login: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str] = mapped_column(String(500), nullable=False)
    html_url: Mapped[str] = mapped_column(String(500), nullable=False)

    # Number of contributions to this specific repository
    contributions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Internal Database Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationship back to Repository
    repository: Mapped["Repository"] = relationship(
        "Repository",
        back_populates="contributors",
    )

    def __repr__(self) -> str:
        return f"<Contributor {self.login} in Repository {self.repository_id}>"
