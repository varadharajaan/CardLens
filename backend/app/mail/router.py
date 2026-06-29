"""Mailbox onboarding endpoints: connect (consent), callback, scan, status."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.mail.repository import MailRepository
from app.mail.schemas import ConnectResponse, MailAccountRead, PasswordHintsRequest, ScanResult
from app.mail.service import MailService
from app.config import settings
from app.shared.constants.api_paths import ApiPaths
from app.shared.database.session import get_db
from app.shared.security.deps import get_current_user_id

router = APIRouter(tags=["mail"])


@router.get(ApiPaths.MAIL_ACCOUNTS, response_model=MailAccountRead | None, summary="Connected mailbox status")
def status(user_id: UUID = Depends(get_current_user_id), db: Session = Depends(get_db)) -> object:
    return MailRepository(db).get_for_user(user_id)


@router.post(ApiPaths.MAIL_ACCOUNTS_CONNECT, response_model=ConnectResponse, summary="Start Gmail consent")
def connect(user_id: UUID = Depends(get_current_user_id), db: Session = Depends(get_db)) -> ConnectResponse:
    return MailService(db).connect(user_id)


@router.put("/mail/accounts/password-hints", status_code=204, summary="Save encrypted PDF password hints")
def save_password_hints(
    body: PasswordHintsRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> None:
    MailService(db).save_password_hints(user_id, body)


@router.get(ApiPaths.MAIL_ACCOUNTS_CALLBACK, summary="OAuth callback")
def callback(code: str | None = None, state: str | None = None, db: Session = Depends(get_db)) -> RedirectResponse:
    if code and state:
        MailService(db).complete_oauth(UUID(state), code)
    return RedirectResponse(url=f"{settings.frontend_base_url}/dashboard/inbox?connected=1")


@router.post(ApiPaths.INGESTION_SCAN, response_model=ScanResult, summary="Scan mailbox for statements")
def scan(user_id: UUID = Depends(get_current_user_id), db: Session = Depends(get_db)) -> ScanResult:
    return MailService(db).scan(user_id)
