"""Card registry business logic: file loading, upsert with schema validation, and matching."""

from __future__ import annotations

from jsonschema.exceptions import ValidationError as SchemaValidationError
from sqlalchemy.orm import Session

from app.registry.loader import RegistryLoader
from app.registry.matcher import best_match
from app.registry.models import CardRegistryEntry
from app.registry.repository import CardRegistryRepository
from app.registry.schemas import RegistryEntryRead, RegistryEntryUpsert, RegistryMatchResult
from app.shared.errors.exceptions import DomainValidationError, NotFoundError
from app.shared.logging.context import get_logger

_logger = get_logger("cardlens.registry")

_MATCH_THRESHOLD = 0.5


class RegistryService:
    """Coordinates registry persistence, file loading, schema validation, and matching."""

    def __init__(self, db: Session) -> None:
        self._repo = CardRegistryRepository(db)
        self._loader = RegistryLoader()

    def load_from_files(self) -> int:
        """Load and upsert every registry file. Returns the number of entries processed."""
        count = 0
        for entry in self._loader.load_files():
            self._repo.upsert(entry)
            count += 1
        _logger.info("registry.synced", count=count)
        return count

    def upsert(self, data: RegistryEntryUpsert) -> CardRegistryEntry:
        """Validate against the JSON schema, then upsert the entry."""
        try:
            self._loader.validate_data(data.model_dump(mode="json"))
        except SchemaValidationError as exc:
            raise DomainValidationError(f"Registry entry failed schema validation: {exc.message}") from exc
        return self._repo.upsert(data)

    def list_entries(self, offset: int, limit: int) -> tuple[list[CardRegistryEntry], int]:
        """Return a page of registry entries and the total count."""
        return self._repo.list(offset, limit)

    def get(self, key: str) -> CardRegistryEntry:
        """Return an entry by key or raise :class:`NotFoundError`."""
        entry = self._repo.get_by_key(key)
        if entry is None:
            raise NotFoundError("Registry entry not found.")
        return entry

    def match(self, bank: str | None, card_name: str | None, last4: str | None = None) -> RegistryMatchResult:
        """Match a detected card against the registry."""
        entries = self._repo.all()
        best, score = best_match(bank, card_name, entries)
        if best is not None and score >= _MATCH_THRESHOLD:
            return RegistryMatchResult(
                matched=True,
                key=best.key,
                confidence=score,
                entry=RegistryEntryRead.model_validate(best),
            )
        return RegistryMatchResult(matched=False, key=None, confidence=score, entry=None)
