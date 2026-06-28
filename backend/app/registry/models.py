"""Card registry ORM entity."""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import JSON, Date, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CardRegistryEntry(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A validated card-feature registry entry loaded from a versioned JSON file or upserted via API."""

    __tablename__ = "card_registry_entries"

    key: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    bank: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    card_name: Mapped[str] = mapped_column(String(200), nullable=False)
    network: Mapped[str] = mapped_column(String(20), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(10), default="1", nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    source_confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_verified_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    features: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    official_links: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    community_links: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
