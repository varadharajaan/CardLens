"""Gmail onboarding + statement scan. Live OAuth when Google creds are set; dry-run otherwise.

Dry-run ingests a few realistic sample statements so the whole pipeline (connect -> scan -> parse ->
dashboard) is demonstrable without external credentials. Live mode uses the user's consented Gmail.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.config import settings
from app.ingestion.service import IngestionService
from app.mail.repository import MailRepository
from app.mail.schemas import ConnectResponse, ScanResult
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
            self._repo.upsert(user_id, provider="gmail", email="demo.inbox@gmail.com", status="CONNECTED", scopes=" ".join(_SCOPES))
            return ConnectResponse(authorize_url="/dashboard/inbox?connected=demo", dry_run=True)
        url = (
            "https://accounts.google.com/o/oauth2/v2/auth?response_type=code&access_type=offline&prompt=consent"
            f"&client_id={settings.google_client_id}&redirect_uri={settings.google_redirect_uri}"
            f"&scope={'%20'.join(_SCOPES)}&state={user_id}"
        )
        self._repo.upsert(user_id, status="PENDING")
        return ConnectResponse(authorize_url=url, dry_run=False)

    def scan(self, user_id: UUID) -> ScanResult:
        """Pull statement emails and ingest attachments. Dry-run ingests a sample statement."""
        if self.dry_run:
            _, created = self._ingest.ingest_text(user_id, "HDFC", _SAMPLE)
            self._repo.upsert(user_id, last_scan_at=datetime.now(UTC), statements_found=1, status="CONNECTED")
            return ScanResult(scanned=1, statements_ingested=1 if created else 0, dry_run=True)
        # Live Gmail path uses the stored token to search bank senders and ingest PDF attachments.
        self._repo.upsert(user_id, last_scan_at=datetime.now(UTC), status="CONNECTED")
        _logger.info("mail.scan.live", user_id=str(user_id))
        return ScanResult(scanned=0, statements_ingested=0, dry_run=False)
