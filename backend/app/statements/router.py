"""Statement intelligence HTTP endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.shared.constants.api_paths import ApiPaths
from app.shared.database.session import get_db
from app.shared.pagination import Page, PageParams
from app.shared.security.deps import get_current_user_id
from app.statements.schemas import StatementCreate, StatementRead
from app.statements.service import StatementService

router = APIRouter(prefix=ApiPaths.STATEMENTS, tags=["statements"])


def get_statement_service(db: Session = Depends(get_db)) -> StatementService:
    """Provide a request-scoped :class:`StatementService`."""
    return StatementService(db)


@router.get("", response_model=Page[StatementRead], summary="List statements")
def list_statements(
    params: PageParams = Depends(),
    card_id: UUID | None = Query(default=None, description="filter by card id"),
    user_id: UUID = Depends(get_current_user_id),
    service: StatementService = Depends(get_statement_service),
) -> Page[StatementRead]:
    """Return a page of the authenticated user's statements, optionally filtered by card."""
    rows, total = service.list_statements(user_id, card_id, params.offset, params.limit)
    return Page.create([StatementRead.model_validate(row) for row in rows], total, params)


@router.post("", response_model=StatementRead, status_code=status.HTTP_201_CREATED, summary="Record a statement")
def record_statement(
    body: StatementCreate,
    user_id: UUID = Depends(get_current_user_id),
    service: StatementService = Depends(get_statement_service),
) -> StatementRead:
    """Record a parsed statement for the authenticated user."""
    return StatementRead.model_validate(service.record(user_id, body))


@router.get("/{statement_id}", response_model=StatementRead, summary="Get a statement by id")
def get_statement(
    statement_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: StatementService = Depends(get_statement_service),
) -> StatementRead:
    """Return one of the authenticated user's statements by id."""
    return StatementRead.model_validate(service.get_statement(user_id, statement_id))
