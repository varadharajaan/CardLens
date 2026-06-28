"""Seed the card registry table from versioned JSON files.

Idempotent: re-running upserts by key. Invoke via ``python -m app.registry.seed`` or the
``scripts/seed_registry.ps1`` wrapper, which applies migrations first.
"""

from __future__ import annotations

from app.config import settings
from app.registry.service import RegistryService
from app.shared.database.session import session_scope
from app.shared.logging.context import get_logger
from app.shared.logging.setup import configure_logging


def main() -> int:
    """Load and upsert every registry file; return the number of entries processed."""
    configure_logging(settings)
    logger = get_logger("cardlens.registry.seed")
    with session_scope() as db:
        count = RegistryService(db).load_from_files()
    logger.info("registry.seed_complete", count=count)
    return count


if __name__ == "__main__":
    main()
