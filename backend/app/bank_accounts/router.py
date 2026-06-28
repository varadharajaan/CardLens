"""Bank account and debit card HTTP endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.bank_accounts.schemas import (
    BankAccountCreate,
    BankAccountDetail,
    BankAccountRead,
    DebitCardCreate,
    DebitCardRead,
)
from app.bank_accounts.service import BankAccountService
from app.shared.constants.api_paths import ApiPaths
from app.shared.database.session import get_db
from app.shared.pagination import Page, PageParams
from app.shared.security.deps import get_current_user_id

router = APIRouter(prefix=ApiPaths.BANK_ACCOUNTS, tags=["bank-accounts"])


def get_bank_account_service(db: Session = Depends(get_db)) -> BankAccountService:
    """Provide a request-scoped :class:`BankAccountService`."""
    return BankAccountService(db)


@router.get("", response_model=Page[BankAccountRead], summary="List bank accounts")
def list_bank_accounts(
    params: PageParams = Depends(),
    user_id: UUID = Depends(get_current_user_id),
    service: BankAccountService = Depends(get_bank_account_service),
) -> Page[BankAccountRead]:
    """Return a page of the authenticated user's bank accounts."""
    rows, total = service.list_accounts(user_id, params.offset, params.limit)
    return Page.create([BankAccountRead.model_validate(row) for row in rows], total, params)


@router.post(
    "",
    response_model=BankAccountRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a bank account",
)
def create_bank_account(
    body: BankAccountCreate,
    user_id: UUID = Depends(get_current_user_id),
    service: BankAccountService = Depends(get_bank_account_service),
) -> BankAccountRead:
    """Create a bank account for the authenticated user."""
    return BankAccountRead.model_validate(service.add_account(user_id, body))


@router.get(
    "/{account_id}",
    response_model=BankAccountDetail,
    summary="Get a bank account with its debit cards",
)
def get_bank_account(
    account_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: BankAccountService = Depends(get_bank_account_service),
) -> BankAccountDetail:
    """Return one of the user's bank accounts and its debit-card variants."""
    account, debit_cards = service.get_account_detail(user_id, account_id)
    return BankAccountDetail(
        account=BankAccountRead.model_validate(account),
        debit_cards=[DebitCardRead.model_validate(c) for c in debit_cards],
    )


debit_cards_router = APIRouter(prefix=ApiPaths.DEBIT_CARDS, tags=["debit-cards"])


@debit_cards_router.get("", response_model=Page[DebitCardRead], summary="List debit cards")
def list_debit_cards(
    params: PageParams = Depends(),
    user_id: UUID = Depends(get_current_user_id),
    service: BankAccountService = Depends(get_bank_account_service),
) -> Page[DebitCardRead]:
    """Return a page of the authenticated user's debit cards."""
    rows, total = service.list_debit_cards(user_id, params.offset, params.limit)
    return Page.create([DebitCardRead.model_validate(row) for row in rows], total, params)


@debit_cards_router.post(
    "",
    response_model=DebitCardRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a debit card to a bank account",
)
def add_debit_card(
    body: DebitCardCreate,
    user_id: UUID = Depends(get_current_user_id),
    service: BankAccountService = Depends(get_bank_account_service),
) -> DebitCardRead:
    """Add a debit card (network variant) to one of the user's bank accounts."""
    return DebitCardRead.model_validate(service.add_debit_card(user_id, body))
