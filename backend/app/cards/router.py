"""Card portfolio HTTP endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.cards.schemas import (
    CardAccountCreate,
    CardAccountDetail,
    CardAccountRead,
    CardCreate,
    CardRead,
)
from app.cards.service import CardService
from app.shared.constants.api_paths import ApiPaths
from app.shared.database.session import get_db
from app.shared.pagination import Page, PageParams
from app.shared.security.deps import get_current_user_id

router = APIRouter(prefix=ApiPaths.CARDS, tags=["cards"])


def get_card_service(db: Session = Depends(get_db)) -> CardService:
    """Provide a request-scoped :class:`CardService`."""
    return CardService(db)


@router.get("", response_model=Page[CardRead], summary="List cards in the portfolio")
def list_cards(
    params: PageParams = Depends(),
    user_id: UUID = Depends(get_current_user_id),
    service: CardService = Depends(get_card_service),
) -> Page[CardRead]:
    """Return a page of the authenticated user's cards."""
    rows, total = service.list_cards(user_id, params.offset, params.limit)
    return Page.create([CardRead.model_validate(row) for row in rows], total, params)


@router.post("", response_model=CardRead, status_code=status.HTTP_201_CREATED, summary="Add a card")
def add_card(
    body: CardCreate,
    user_id: UUID = Depends(get_current_user_id),
    service: CardService = Depends(get_card_service),
) -> CardRead:
    """Add a card to the authenticated user's portfolio."""
    return CardRead.model_validate(service.add_card(user_id, body))


@router.get("/{card_id}", response_model=CardRead, summary="Get a card by id")
def get_card(
    card_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: CardService = Depends(get_card_service),
) -> CardRead:
    """Return one of the authenticated user's cards by id."""
    return CardRead.model_validate(service.get_card(user_id, card_id))


accounts_router = APIRouter(prefix=ApiPaths.CARD_ACCOUNTS, tags=["card-accounts"])


@accounts_router.get("", response_model=Page[CardAccountRead], summary="List card billing accounts")
def list_card_accounts(
    params: PageParams = Depends(),
    user_id: UUID = Depends(get_current_user_id),
    service: CardService = Depends(get_card_service),
) -> Page[CardAccountRead]:
    """Return a page of the user's card billing accounts (companion-card groups)."""
    rows, total = service.list_accounts(user_id, params.offset, params.limit)
    return Page.create([CardAccountRead.model_validate(row) for row in rows], total, params)


@accounts_router.get(
    "/{account_id}",
    response_model=CardAccountDetail,
    summary="Get a billing account with its variants",
)
def get_card_account(
    account_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: CardService = Depends(get_card_service),
) -> CardAccountDetail:
    """Return one of the user's billing accounts and its companion card variants."""
    account, variants = service.get_account_detail(user_id, account_id)
    return CardAccountDetail(
        account=CardAccountRead.model_validate(account),
        variants=[CardRead.model_validate(v) for v in variants],
    )


@accounts_router.post(
    "",
    response_model=CardAccountRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a billing account",
)
def create_card_account(
    body: CardAccountCreate,
    user_id: UUID = Depends(get_current_user_id),
    service: CardService = Depends(get_card_service),
) -> CardAccountRead:
    """Create a card billing account (companion-card group) for the authenticated user."""
    return CardAccountRead.model_validate(service.add_account(user_id, body))
