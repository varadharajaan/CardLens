"""Bank account and debit card business logic."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.bank_accounts.models import BankAccount, DebitCard
from app.bank_accounts.repository import BankAccountRepository
from app.bank_accounts.schemas import BankAccountCreate, DebitCardCreate
from app.shared.errors.exceptions import NotFoundError
from app.shared.logging.context import get_logger

_logger = get_logger("cardlens.bank_accounts")


class BankAccountService:
    """Coordinates bank account and debit card reads and writes for a single user."""

    def __init__(self, db: Session) -> None:
        self._repo = BankAccountRepository(db)

    def list_accounts(
        self, user_id: UUID, offset: int, limit: int
    ) -> tuple[list[BankAccount], int]:
        """Return a page of the user's bank accounts and the total count."""
        return self._repo.list_accounts_for_user(user_id, offset, limit)

    def get_account_detail(
        self, user_id: UUID, account_id: UUID
    ) -> tuple[BankAccount, list[DebitCard]]:
        """Return a bank account and its debit cards, or raise :class:`NotFoundError`."""
        account = self._repo.get_account_for_user(user_id, account_id)
        if account is None:
            raise NotFoundError("Bank account not found.")
        debit_cards = self._repo.list_debit_cards_for_account(user_id, account_id)
        return account, debit_cards

    def add_account(self, user_id: UUID, data: BankAccountCreate) -> BankAccount:
        """Create a bank account for the user."""
        account = self._repo.create_account(user_id, data)
        _logger.info("bank_account.added", account_id=str(account.id), bank=account.bank)
        return account

    def list_debit_cards(
        self, user_id: UUID, offset: int, limit: int
    ) -> tuple[list[DebitCard], int]:
        """Return a page of the user's debit cards and the total count."""
        return self._repo.list_debit_cards_for_user(user_id, offset, limit)

    def add_debit_card(self, user_id: UUID, data: DebitCardCreate) -> DebitCard:
        """Add a debit card to one of the user's bank accounts.

        The target account must belong to the requesting user; otherwise a :class:`NotFoundError` is
        raised so a client can never attach a card to another user's account.
        """
        if self._repo.get_account_for_user(user_id, data.bank_account_id) is None:
            raise NotFoundError("Bank account not found.")
        card = self._repo.create_debit_card(user_id, data)
        _logger.info(
            "debit_card.added",
            debit_card_id=str(card.id),
            bank_account_id=str(card.bank_account_id),
            last4=card.last4,
        )
        return card
