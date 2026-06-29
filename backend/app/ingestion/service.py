"""Ingestion orchestration: dedup, store, parse, and persist a statement. Wraps the S3 parser."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.ingestion.dedup import content_hash
from app.ingestion.storage import get_storage
from app.parsers.pdf import CardholderHints
from app.parsers.schemas import ParsedStatement
from app.parsers.service import ParserService
from app.statements.schemas import StatementCreate
from app.statements.service import StatementService
from app.shared.logging.context import get_logger

_logger = get_logger("cardlens.ingestion")


class IngestionService:
    """Stores raw content (deduped by hash), parses it, and records the resulting statement."""

    def __init__(self, db: Session) -> None:
        self._parser = ParserService()
        self._statements = StatementService(db)
        self._store = get_storage()

    def _persist(self, user_id: UUID, parsed: ParsedStatement) -> tuple[str, bool]:
        create = StatementCreate(
            bank=parsed.bank,
            card_name=parsed.card_name or "Unknown",
            last4=parsed.last4 or "0000",
            statement_date=parsed.statement_date,
            due_date=parsed.due_date,
            total_due=parsed.total_due,
            minimum_due=parsed.minimum_due,
            reward_points_closing=parsed.reward_points_closing,
            cashback_earned=parsed.cashback_earned,
            reward_type=parsed.reward_type,
            reward_parse_status=parsed.reward_parse_status,
            reward_confidence=parsed.reward_confidence,
        )
        stmt = self._statements.record(user_id, create)
        return str(stmt.id), True

    def ingest_text(self, user_id: UUID, bank: str | None, text: str) -> tuple[str, bool]:
        """Dedup + store raw text, parse, and persist a statement. Returns (statement_id, created)."""
        key = f"{bank or 'unknown'}/{content_hash(text.encode())}.txt"
        if self._store.exists(key):
            _logger.info("ingestion.duplicate", key=key)
            return key, False
        self._store.put(key, text.encode())
        return self._persist(user_id, self._parser.parse_text(bank, text))

    def ingest_pdf(self, user_id: UUID, content: bytes, bank: str | None, hints: CardholderHints) -> tuple[str, bool]:
        """Dedup + store raw PDF, parse, and persist a statement. Returns (statement_id, created)."""
        key = f"{bank or 'unknown'}/{content_hash(content)}.pdf"
        if self._store.exists(key):
            _logger.info("ingestion.duplicate", key=key)
            return key, False
        self._store.put(key, content)
        return self._persist(user_id, self._parser.parse_pdf(content, bank, hints))
