"""Registry file loader and JSON Schema validation.

Reads card entry files from the registry directory and validates each against the JSON Schema that
matches the entry's declared ``schema_version``, supporting multiple schema versions side by side.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from app.config import settings
from app.registry.schemas import RegistryEntryUpsert
from app.shared.logging.context import get_logger

_logger = get_logger("cardlens.registry")


class RegistryLoader:
    """Loads and validates versioned card registry JSON files."""

    def __init__(self, registry_dir: Path | None = None) -> None:
        self._dir = registry_dir or settings.card_registry_dir
        self._validators: dict[str, Draft202012Validator] = {}

    def _validator(self, schema_version: str) -> Draft202012Validator:
        if schema_version not in self._validators:
            schema_path = self._dir / "schema" / f"v{schema_version}" / "card-feature.schema.json"
            if not schema_path.exists():
                raise FileNotFoundError(f"No registry schema for version {schema_version}: {schema_path}")
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            self._validators[schema_version] = Draft202012Validator(schema, format_checker=FormatChecker())
        return self._validators[schema_version]

    def iter_entry_files(self) -> list[Path]:
        """Return all registry entry JSON files (excludes the schema directory)."""
        india = self._dir / "india"
        if not india.exists():
            return []
        return sorted(india.rglob("*.json"))

    def validate_data(self, data: dict[str, Any]) -> None:
        """Validate a single entry dict against the schema for its declared version."""
        schema_version = str(data.get("schema_version", "1"))
        self._validator(schema_version).validate(data)

    def load_files(self) -> list[RegistryEntryUpsert]:
        """Load, validate, and parse every registry entry file into upsert DTOs."""
        entries: list[RegistryEntryUpsert] = []
        for path in self.iter_entry_files():
            data = json.loads(path.read_text(encoding="utf-8"))
            self.validate_data(data)
            entries.append(RegistryEntryUpsert(**data))
        _logger.info("registry.files_loaded", count=len(entries), registry_dir=str(self._dir))
        return entries
