import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import BigInteger, DateTime, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Repository(Base):
    """SQLAlchemy model representing a GitHub repository."""

    __tablename__ = "repositories"

    # UUID Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    # Unique GitHub Repository ID
    github_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
    )

    # Repository Identity
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Owner details
    owner_login: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_avatar_url: Mapped[str] = mapped_column(String(500), nullable=False)

    # URLs
    html_url: Mapped[str] = mapped_column(String(500), nullable=False)
    clone_url: Mapped[str] = mapped_column(String(500), nullable=False)

    # Repository Metadata
    language: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    default_branch: Mapped[str] = mapped_column(
        String(100), nullable=False, default="main"
    )
    visibility: Mapped[str] = mapped_column(
        String(50), nullable=False, default="public"
    )

    # Metrics
    stars: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    forks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    open_issues: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    watchers: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Topics (List of tags, stored as JSON)
    topics: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # External GitHub Creation/Update timestamps (stored as strings to match API format)
    github_created_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    github_updated_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Internal database timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Sync fields
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    sync_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="PENDING",
    )
    sync_error: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships (Cascade deletes children if repository is deleted)
    contributors: Mapped[List["Contributor"]] = relationship(
        "Contributor",
        back_populates="repository",
        cascade="all, delete-orphan",
    )
    commits: Mapped[List["Commit"]] = relationship(
        "Commit",
        back_populates="repository",
        cascade="all, delete-orphan",
    )
    issues: Mapped[List["Issue"]] = relationship(
        "Issue",
        back_populates="repository",
        cascade="all, delete-orphan",
    )
    pull_requests: Mapped[List["PullRequest"]] = relationship(
        "PullRequest",
        back_populates="repository",
        cascade="all, delete-orphan",
    )
    languages: Mapped[List["Language"]] = relationship(
        "Language",
        back_populates="repository",
        cascade="all, delete-orphan",
    )
    snapshots: Mapped[List["RepositorySnapshot"]] = relationship(
        "RepositorySnapshot",
        back_populates="repository",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Repository {self.full_name}>"
