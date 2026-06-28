"""Declarative base and common entity mixins.

Every entity gets a UUID primary key and audit timestamps. Defaults are computed in Python so they
work identically on SQLite (local/test) and PostgreSQL (prod) without database-specific SQL.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _utcnow() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(UTC)


class Base(DeclarativeBase):
    """Declarative base for all CardLens ORM entities."""


class UUIDPrimaryKeyMixin:
    """Adds a UUID primary key generated application-side."""

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)


class TimestampMixin:
    """Adds created/updated audit timestamps maintained application-side."""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
