"""Read-model persistence for the dashboard. Per-user isolation is enforced in every query here."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.bank_accounts.models import BankAccount, DebitCard
from app.cards.models import Card, CardAccount
from app.statements.models import Statement


class DashboardRepository:
    """Cross-module aggregation queries for a single user's portfolio."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def _count(self, model: Any, user_id: UUID) -> int:
        return int(
            self._db.execute(select(func.count()).select_from(model).where(model.user_id == user_id)).scalar_one()
        )

    def counts(self, user_id: UUID) -> dict[str, int]:
        """Return row counts for each portfolio entity owned by the user."""
        return {
            "cards": self._count(Card, user_id),
            "card_accounts": self._count(CardAccount, user_id),
            "bank_accounts": self._count(BankAccount, user_id),
            "debit_cards": self._count(DebitCard, user_id),
            "statements": self._count(Statement, user_id),
        }

    def statements(self, user_id: UUID) -> list[Statement]:
        """Return all of the user's statements, newest first (for grouping and trend rules)."""
        rows = (
            self._db.execute(
                select(Statement)
                .where(Statement.user_id == user_id)
                .order_by(Statement.statement_date.desc(), Statement.created_at.desc())
            )
            .scalars()
            .all()
        )
        return list(rows)

    def credit_limit_by_account(self, user_id: UUID) -> dict[UUID, float]:
        """Return a map of card account id to its credit limit, where a limit is set."""
        rows = self._db.execute(
            select(CardAccount.id, CardAccount.credit_limit).where(CardAccount.user_id == user_id)
        ).all()
        return {row[0]: float(row[1]) for row in rows if row[1] is not None}

    def card_to_account(self, user_id: UUID) -> dict[UUID, UUID]:
        """Return a map of card id to its billing account id, for cards that belong to an account."""
        rows = self._db.execute(
            select(Card.id, Card.account_id).where(Card.user_id == user_id, Card.account_id.is_not(None))
        ).all()
        return {row[0]: row[1] for row in rows if row[1] is not None}
