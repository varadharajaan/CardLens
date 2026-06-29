"""Persistence for statements. Per-user isolation is enforced in every query here."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.statements.models import Statement
from app.statements.schemas import StatementCreate


class StatementRepository:
    """Data-access methods for :class:`Statement`, always scoped to a user id."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list_for_user(
        self, user_id: UUID, card_id: UUID | None, offset: int, limit: int
    ) -> tuple[list[Statement], int]:
        """Return a page of the user's statements, optionally filtered by card."""
        conditions = [Statement.user_id == user_id]
        if card_id is not None:
            conditions.append(Statement.card_id == card_id)
        total = self._db.execute(select(func.count()).select_from(Statement).where(*conditions)).scalar_one()
        rows = (
            self._db.execute(
                select(Statement)
                .where(*conditions)
                .order_by(Statement.statement_date.desc(), Statement.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            .scalars()
            .all()
        )
        return list(rows), int(total)

    def get_for_user(self, user_id: UUID, statement_id: UUID) -> Statement | None:
        """Return the user's statement with the given id, or None."""
        return self._db.execute(
            select(Statement).where(Statement.id == statement_id, Statement.user_id == user_id)
        ).scalar_one_or_none()

    def create(self, user_id: UUID, data: StatementCreate) -> Statement:
        """Insert a new statement owned by the user."""
        statement = Statement(user_id=user_id, **data.model_dump())
        self._db.add(statement)
        self._db.commit()
        self._db.refresh(statement)
        return statement
