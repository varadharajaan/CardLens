"""Statement intelligence business logic."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.shared.errors.exceptions import NotFoundError
from app.shared.logging.context import get_logger
from app.statements.models import Statement
from app.statements.repository import StatementRepository
from app.statements.schemas import StatementCreate

_logger = get_logger("cardlens.statements")


class StatementService:
    """Coordinates statement reads and writes for a single user."""

    def __init__(self, db: Session) -> None:
        self._repo = StatementRepository(db)

    def list_statements(
        self, user_id: UUID, card_id: UUID | None, offset: int, limit: int
    ) -> tuple[list[Statement], int]:
        """Return a page of the user's statements, optionally filtered by card."""
        return self._repo.list_for_user(user_id, card_id, offset, limit)

    def get_statement(self, user_id: UUID, statement_id: UUID) -> Statement:
        """Return the user's statement or raise :class:`NotFoundError`."""
        statement = self._repo.get_for_user(user_id, statement_id)
        if statement is None:
            raise NotFoundError("Statement not found.")
        return statement

    def record(self, user_id: UUID, data: StatementCreate) -> Statement:
        """Record a parsed statement for the user."""
        statement = self._repo.create(user_id, data)
        _logger.info(
            "statement.recorded",
            statement_id=str(statement.id),
            bank=statement.bank,
            last4=statement.last4,
            reward_parse_status=statement.reward_parse_status,
        )
        return statement
