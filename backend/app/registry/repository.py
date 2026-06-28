"""Persistence for card registry entries."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.registry.models import CardRegistryEntry
from app.registry.schemas import RegistryEntryUpsert


class CardRegistryRepository:
    """Data-access methods for :class:`CardRegistryEntry`."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_key(self, key: str) -> CardRegistryEntry | None:
        """Return the entry with the given key, or None."""
        return self._db.execute(
            select(CardRegistryEntry).where(CardRegistryEntry.key == key)
        ).scalar_one_or_none()

    def all(self) -> list[CardRegistryEntry]:
        """Return every registry entry (used for matching)."""
        return list(self._db.execute(select(CardRegistryEntry)).scalars().all())

    def list(self, offset: int, limit: int) -> tuple[list[CardRegistryEntry], int]:
        """Return a page of entries and the total count."""
        total = self._db.execute(
            select(func.count()).select_from(CardRegistryEntry)
        ).scalar_one()
        rows = (
            self._db.execute(
                select(CardRegistryEntry).order_by(CardRegistryEntry.bank, CardRegistryEntry.card_name)
                .offset(offset)
                .limit(limit)
            )
            .scalars()
            .all()
        )
        return list(rows), int(total)

    def upsert(self, data: RegistryEntryUpsert) -> CardRegistryEntry:
        """Insert a new entry or update the existing one with the same key."""
        existing = self.get_by_key(data.key)
        if existing is not None:
            for field, value in data.model_dump().items():
                setattr(existing, field, value)
            self._db.commit()
            self._db.refresh(existing)
            return existing
        entry = CardRegistryEntry(**data.model_dump())
        self._db.add(entry)
        self._db.commit()
        self._db.refresh(entry)
        return entry
