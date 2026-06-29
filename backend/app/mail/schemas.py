"""Mail onboarding DTOs."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MailAccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    provider: str
    email: str | None
    status: str
    last_scan_at: datetime | None
    statements_found: int


class ConnectResponse(BaseModel):
    """Where the UI should send the user to grant consent (or a dry-run notice)."""

    authorize_url: str
    dry_run: bool


class ScanResult(BaseModel):
    """Outcome of a mailbox scan."""

    scanned: int
    statements_ingested: int
    dry_run: bool
