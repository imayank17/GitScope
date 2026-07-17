import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Float,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Language(Base):
    """SQLAlchemy model representing a programming language used in a repository."""

    __tablename__ = "languages"

    # Enforce unique language name per repository
    __table_args__ = (
        UniqueConstraint(
            "repository_id",
            "name",
            name="uq_language_repo_name",
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

    # Language Identity
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Internal Database Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationship back to Repository
    repository: Mapped["Repository"] = relationship(
        "Repository",
        back_populates="languages",
    )

    def __repr__(self) -> str:
        return f"<Language {self.name} ({self.percentage}%) in Repository {self.repository_id}>"
