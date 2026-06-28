"""Card portfolio business logic."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.cards.models import Card, CardAccount
from app.cards.repository import CardRepository
from app.cards.schemas import CardAccountCreate, CardCreate
from app.shared.errors.exceptions import NotFoundError
from app.shared.logging.context import get_logger

_logger = get_logger("cardlens.cards")


class CardService:
    """Coordinates card portfolio reads and writes for a single user."""

    def __init__(self, db: Session) -> None:
        self._repo = CardRepository(db)

    def list_cards(self, user_id: UUID, offset: int, limit: int) -> tuple[list[Card], int]:
        """Return a page of the user's cards and the total count."""
        return self._repo.list_for_user(user_id, offset, limit)

    def get_card(self, user_id: UUID, card_id: UUID) -> Card:
        """Return the user's card or raise :class:`NotFoundError`."""
        card = self._repo.get_for_user(user_id, card_id)
        if card is None:
            raise NotFoundError("Card not found.")
        return card

    def add_card(self, user_id: UUID, data: CardCreate) -> Card:
        """Add a card to the user's portfolio."""
        card = self._repo.create(user_id, data)
        _logger.info("card.added", card_id=str(card.id), bank=card.bank, last4=card.last4)
        return card

    def list_accounts(
        self, user_id: UUID, offset: int, limit: int
    ) -> tuple[list[CardAccount], int]:
        """Return a page of the user's card billing accounts and the total count."""
        return self._repo.list_accounts_for_user(user_id, offset, limit)

    def get_account_detail(
        self, user_id: UUID, account_id: UUID
    ) -> tuple[CardAccount, list[Card]]:
        """Return a billing account and its companion variants, or raise :class:`NotFoundError`."""
        account = self._repo.get_account_for_user(user_id, account_id)
        if account is None:
            raise NotFoundError("Card account not found.")
        variants = self._repo.list_variants_for_account(user_id, account_id)
        return account, variants

    def add_account(self, user_id: UUID, data: CardAccountCreate) -> CardAccount:
        """Create a card billing account (companion-card group) for the user."""
        account = self._repo.create_account(user_id, data)
        _logger.info("card_account.added", account_id=str(account.id), bank=account.bank)
        return account
