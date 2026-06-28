"""Persistence for cards. Per-user isolation is enforced in every query here."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.cards.models import Card, CardAccount
from app.cards.schemas import CardAccountCreate, CardCreate


class CardRepository:
    """Data-access methods for :class:`Card`, always scoped to a user id."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list_for_user(self, user_id: UUID, offset: int, limit: int) -> tuple[list[Card], int]:
        """Return a page of the user's cards and the total count."""
        total = self._db.execute(
            select(func.count()).select_from(Card).where(Card.user_id == user_id)
        ).scalar_one()
        rows = (
            self._db.execute(
                select(Card)
                .where(Card.user_id == user_id)
                .order_by(Card.bank, Card.card_name)
                .offset(offset)
                .limit(limit)
            )
            .scalars()
            .all()
        )
        return list(rows), int(total)

    def get_for_user(self, user_id: UUID, card_id: UUID) -> Card | None:
        """Return the user's card with the given id, or None."""
        return self._db.execute(
            select(Card).where(Card.id == card_id, Card.user_id == user_id)
        ).scalar_one_or_none()

    def create(self, user_id: UUID, data: CardCreate) -> Card:
        """Insert a new card owned by the user."""
        card = Card(user_id=user_id, **data.model_dump())
        self._db.add(card)
        self._db.commit()
        self._db.refresh(card)
        return card

    def list_accounts_for_user(
        self, user_id: UUID, offset: int, limit: int
    ) -> tuple[list[CardAccount], int]:
        """Return a page of the user's card billing accounts and the total count."""
        total = self._db.execute(
            select(func.count()).select_from(CardAccount).where(CardAccount.user_id == user_id)
        ).scalar_one()
        rows = (
            self._db.execute(
                select(CardAccount)
                .where(CardAccount.user_id == user_id)
                .order_by(CardAccount.bank, CardAccount.display_name)
                .offset(offset)
                .limit(limit)
            )
            .scalars()
            .all()
        )
        return list(rows), int(total)

    def get_account_for_user(self, user_id: UUID, account_id: UUID) -> CardAccount | None:
        """Return the user's card billing account with the given id, or None."""
        return self._db.execute(
            select(CardAccount).where(
                CardAccount.id == account_id, CardAccount.user_id == user_id
            )
        ).scalar_one_or_none()

    def list_variants_for_account(self, user_id: UUID, account_id: UUID) -> list[Card]:
        """Return the user's card variants belonging to the given billing account."""
        rows = (
            self._db.execute(
                select(Card)
                .where(Card.user_id == user_id, Card.account_id == account_id)
                .order_by(Card.is_primary.desc(), Card.network)
            )
            .scalars()
            .all()
        )
        return list(rows)

    def create_account(self, user_id: UUID, data: CardAccountCreate) -> CardAccount:
        """Insert a new card billing account owned by the user."""
        account = CardAccount(user_id=user_id, **data.model_dump())
        self._db.add(account)
        self._db.commit()
        self._db.refresh(account)
        return account
