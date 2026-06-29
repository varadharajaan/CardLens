"""Persistence for bank accounts and debit cards. Per-user isolation is enforced in every query."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.bank_accounts.models import BankAccount, DebitCard
from app.bank_accounts.schemas import BankAccountCreate, DebitCardCreate


class BankAccountRepository:
    """Data-access methods for bank accounts and debit cards, always scoped to a user id."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list_accounts_for_user(self, user_id: UUID, offset: int, limit: int) -> tuple[list[BankAccount], int]:
        """Return a page of the user's bank accounts and the total count."""
        total = self._db.execute(
            select(func.count()).select_from(BankAccount).where(BankAccount.user_id == user_id)
        ).scalar_one()
        rows = (
            self._db.execute(
                select(BankAccount)
                .where(BankAccount.user_id == user_id)
                .order_by(BankAccount.bank, BankAccount.display_name)
                .offset(offset)
                .limit(limit)
            )
            .scalars()
            .all()
        )
        return list(rows), int(total)

    def get_account_for_user(self, user_id: UUID, account_id: UUID) -> BankAccount | None:
        """Return the user's bank account with the given id, or None."""
        return self._db.execute(
            select(BankAccount).where(BankAccount.id == account_id, BankAccount.user_id == user_id)
        ).scalar_one_or_none()

    def list_debit_cards_for_account(self, user_id: UUID, account_id: UUID) -> list[DebitCard]:
        """Return the user's debit cards belonging to the given bank account, primary first."""
        rows = (
            self._db.execute(
                select(DebitCard)
                .where(DebitCard.user_id == user_id, DebitCard.bank_account_id == account_id)
                .order_by(DebitCard.is_primary.desc(), DebitCard.network)
            )
            .scalars()
            .all()
        )
        return list(rows)

    def list_debit_cards_for_user(self, user_id: UUID, offset: int, limit: int) -> tuple[list[DebitCard], int]:
        """Return a page of the user's debit cards and the total count."""
        total = self._db.execute(
            select(func.count()).select_from(DebitCard).where(DebitCard.user_id == user_id)
        ).scalar_one()
        rows = (
            self._db.execute(
                select(DebitCard)
                .where(DebitCard.user_id == user_id)
                .order_by(DebitCard.is_primary.desc(), DebitCard.card_name)
                .offset(offset)
                .limit(limit)
            )
            .scalars()
            .all()
        )
        return list(rows), int(total)

    def create_account(self, user_id: UUID, data: BankAccountCreate) -> BankAccount:
        """Insert a new bank account owned by the user."""
        account = BankAccount(user_id=user_id, **data.model_dump())
        self._db.add(account)
        self._db.commit()
        self._db.refresh(account)
        return account

    def create_debit_card(self, user_id: UUID, data: DebitCardCreate) -> DebitCard:
        """Insert a new debit card owned by the user."""
        card = DebitCard(user_id=user_id, **data.model_dump())
        self._db.add(card)
        self._db.commit()
        self._db.refresh(card)
        return card
