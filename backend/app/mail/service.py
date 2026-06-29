"""Gmail onboarding + statement scan. Live OAuth when Google creds are set; dry-run otherwise.

Dry-run ingests a few realistic sample statements so the whole pipeline (connect -> scan -> parse ->
dashboard) is demonstrable without external credentials. Live mode uses the user's consented Gmail.
"""

from __future__ import annotations

import base64
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import httpx
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from app.config import settings
from app.ingestion.service import IngestionService
from app.mail.repository import MailRepository
from app.mail.schemas import ConnectResponse, ScanResult
from app.parsers.pdf import CardholderHints
from app.shared.errors.exceptions import DomainValidationError
from app.shared.security.crypto import decrypt_text, encrypt_text
from app.shared.logging.context import get_logger

_logger = get_logger("cardlens.mail")
_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "email"]

_SAMPLE = """HDFC Bank Credit Card Statement
Product: HDFC Infinia
Card Number: XXXXXXXXXXXX1234
Statement Date: 02-06-2026
Payment Due Date: 22-06-2026
Total Amount Due: INR 25,000.00
Minimum Amount Due: INR 1,250.00
Reward Points Earned: 1,200
Closing Reward Points: 48,000
"""


class MailService:
    def __init__(self, db: Session) -> None:
        self._repo = MailRepository(db)
        self._ingest = IngestionService(db)

    @property
    def dry_run(self) -> bool:
        return settings.gmail_dry_run or not (settings.google_client_id and settings.google_client_secret)

    def connect(self, user_id: UUID) -> ConnectResponse:
        """Begin Gmail consent. Returns Google's authorize URL, or a dry-run sentinel."""
        if self.dry_run:
            self._repo.upsert(
                user_id, provider="gmail", email="demo.inbox@gmail.com", status="CONNECTED", scopes=" ".join(_SCOPES)
            )
            return ConnectResponse(authorize_url="/dashboard/inbox?connected=demo", dry_run=True)
        url = (
            "https://accounts.google.com/o/oauth2/v2/auth?response_type=code&access_type=offline&prompt=consent"
            f"&client_id={settings.google_client_id}&redirect_uri={settings.google_redirect_uri}"
            f"&scope={'%20'.join(_SCOPES)}&state={user_id}"
        )
        self._repo.upsert(user_id, status="PENDING")
        return ConnectResponse(authorize_url=url, dry_run=False)

    def complete_oauth(self, user_id: UUID, code: str) -> None:
        """Exchange an OAuth code for encrypted tokens and mark Gmail connected."""
        token = httpx.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
            timeout=30,
        )
        token.raise_for_status()
        payload = token.json()
        access_token = payload["access_token"]
        refresh_token = payload.get("refresh_token", "")
        userinfo = httpx.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30,
        )
        email = userinfo.json().get("email") if userinfo.status_code == 200 else None
        self._repo.upsert(
            user_id,
            provider="gmail",
            email=email,
            status="CONNECTED",
            access_token_enc=encrypt_text(access_token),
            refresh_token_enc=encrypt_text(refresh_token) if refresh_token else None,
            scopes=payload.get("scope", " ".join(_SCOPES)),
        )

    def scan(self, user_id: UUID) -> ScanResult:
        """Pull statement emails and ingest attachments. Dry-run ingests a sample statement."""
        if self.dry_run:
            sample = f"{_SAMPLE}\nDryRunUser: {user_id}\n"
            _, created = self._ingest.ingest_text(user_id, "HDFC", sample)
            self._repo.upsert(user_id, last_scan_at=datetime.now(UTC), statements_found=1, status="CONNECTED")
            return ScanResult(scanned=1, statements_ingested=1 if created else 0, dry_run=True)

        account = self._repo.get_for_user(user_id)
        if account is None or not account.access_token_enc:
            raise DomainValidationError("Gmail is not connected for this user.")
        token = decrypt_text(account.access_token_enc)
        refresh = decrypt_text(account.refresh_token_enc) if account.refresh_token_enc else None
        creds = Credentials(
            token=token,
            refresh_token=refresh,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            scopes=_SCOPES,
        )
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            if creds.token:
                self._repo.upsert(user_id, access_token_enc=encrypt_text(creds.token))
        service = build("gmail", "v1", credentials=creds, cache_discovery=False)
        query = f'newer_than:{settings.gmail_scan_lookback_hours}h (filename:pdf OR statement OR "credit card")'
        found = service.users().messages().list(userId="me", q=query, maxResults=25).execute()
        messages: list[dict[str, Any]] = found.get("messages", [])
        ingested = 0
        for msg in messages:
            full = service.users().messages().get(userId="me", id=msg["id"], format="full").execute()
            for attachment_id in _pdf_attachment_ids(full.get("payload", {})):
                attachment = (
                    service.users()
                    .messages()
                    .attachments()
                    .get(userId="me", messageId=msg["id"], id=attachment_id)
                    .execute()
                )
                raw = base64.urlsafe_b64decode(attachment["data"].encode("utf-8"))
                try:
                    _, created = self._ingest.ingest_pdf(user_id, raw, None, CardholderHints())
                    if created:
                        ingested += 1
                except Exception as exc:  # noqa: BLE001 - keep scanning other attachments
                    _logger.warning("mail.attachment_parse_failed", reason=exc.__class__.__name__)
        self._repo.upsert(
            user_id,
            last_scan_at=datetime.now(UTC),
            statements_found=(account.statements_found or 0) + ingested,
            status="CONNECTED",
        )
        return ScanResult(scanned=len(messages), statements_ingested=ingested, dry_run=False)


def _pdf_attachment_ids(payload: dict[str, Any]) -> list[str]:
    """Return Gmail attachment IDs for PDF parts anywhere in the MIME tree."""
    ids: list[str] = []
    parts = payload.get("parts") or []
    if payload.get("filename", "").lower().endswith(".pdf"):
        attachment_id = payload.get("body", {}).get("attachmentId")
        if attachment_id:
            ids.append(attachment_id)
    for part in parts:
        ids.extend(_pdf_attachment_ids(part))
    return ids
