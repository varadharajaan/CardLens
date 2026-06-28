"""Card registry HTTP endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.registry.schemas import (
    CardMatchQuery,
    RegistryEntryRead,
    RegistryEntryUpsert,
    RegistryMatchResult,
)
from app.registry.service import RegistryService
from app.shared.constants.api_paths import ApiPaths
from app.shared.database.session import get_db
from app.shared.pagination import Page, PageParams
from app.shared.security.deps import get_current_user_id

router = APIRouter(prefix=ApiPaths.REGISTRY_CARDS, tags=["registry"])


def get_registry_service(db: Session = Depends(get_db)) -> RegistryService:
    """Provide a request-scoped :class:`RegistryService`."""
    return RegistryService(db)


@router.get("", response_model=Page[RegistryEntryRead], summary="List card registry entries")
def list_cards(
    params: PageParams = Depends(),
    service: RegistryService = Depends(get_registry_service),
) -> Page[RegistryEntryRead]:
    """Return a page of card registry entries."""
    rows, total = service.list_entries(params.offset, params.limit)
    return Page.create([RegistryEntryRead.model_validate(row) for row in rows], total, params)


@router.post("/match", response_model=RegistryMatchResult, summary="Match a card to the registry")
def match_card(
    body: CardMatchQuery,
    service: RegistryService = Depends(get_registry_service),
) -> RegistryMatchResult:
    """Match a detected card (bank, name, last4) against the registry."""
    return service.match(body.bank, body.card_name, body.last4)


@router.get("/{key}", response_model=RegistryEntryRead, summary="Get a registry entry by key")
def get_card(
    key: str,
    service: RegistryService = Depends(get_registry_service),
) -> RegistryEntryRead:
    """Return a single registry entry by its key."""
    return RegistryEntryRead.model_validate(service.get(key))


@router.post(
    "",
    response_model=RegistryEntryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create or update a registry entry",
    dependencies=[Depends(get_current_user_id)],
)
def upsert_card(
    body: RegistryEntryUpsert,
    service: RegistryService = Depends(get_registry_service),
) -> RegistryEntryRead:
    """Validate and upsert a registry entry (authenticated)."""
    return RegistryEntryRead.model_validate(service.upsert(body))
