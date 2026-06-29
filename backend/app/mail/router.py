"""Mailbox onboarding endpoints: connect (consent), callback, scan, status."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.mail.repository import MailRepository
from app.mail.schemas import ConnectResponse, MailAccountRead, ScanResult
from app.mail.service import MailService
from app.shared.constants.api_paths import ApiPaths
from app.shared.database.session import get_db
from app.shared.security.deps import get_current_user_id

router = APIRouter(prefix="/mail", tags=["mail"])


@router.get("/account", response_model=MailAccountRead | None, summary="Connected mailbox status")
def status(user_id: UUID = Depends(get_current_user_id), db: Session = Depends(get_db)) -> object:
    return MailRepository(db).get_for_user(user_id)


@router.post(ApiPaths.MAIL_ACCOUNTS_CONNECT, response_model=ConnectResponse, summary="Start Gmail consent")
def connect(user_id: UUID = Depends(get_current_user_id), db: Session = Depends(get_db)) -> ConnectResponse:
    return MailService(db).connect(user_id)


@router.get(ApiPaths.MAIL_ACCOUNTS_CALLBACK, summary="OAuth callback")
def callback(code: str | None = None, state: str | None = None, db: Session = Depends(get_db)) -> RedirectResponse:
    return RedirectResponse(url="/dashboard/inbox?connected=1")


@router.post(ApiPaths.INGESTION_SCAN, response_model=ScanResult, summary="Scan mailbox for statements")
def scan(user_id: UUID = Depends(get_current_user_id), db: Session = Depends(get_db)) -> ScanResult:
    return MailService(db).scan(user_id)
