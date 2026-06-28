"""User ORM entity."""

from __future__ import annotations

from enum import StrEnum

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class UserStatus(StrEnum):
    """Lifecycle states for a user account."""

    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A CardLens account holder. Owns all mailboxes, cards, statements, and derived intelligence."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default=UserStatus.ACTIVE.value, nullable=False)
