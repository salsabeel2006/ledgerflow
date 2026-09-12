import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from apps.api.src.core.database import Base


class User(Base):
    """
    User entity representing registered system users.
    """

    __tablename__ = "users"

    # Primary Key: UUID guarantees globally unique IDs without exposing sequential row counts
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Unique email field with index for fast login query performance
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )

    # Stores the secure hashed password (NEVER plain text passwords)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # User state flags
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )