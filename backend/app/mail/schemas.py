"""Mail onboarding DTOs."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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


class PasswordHintsRequest(BaseModel):
    """Encrypted-at-rest hints used to unlock bank/card statement PDFs from Gmail."""

    name: str | None = Field(default=None, max_length=120)
    dob_ddmm: str | None = Field(default=None, pattern=r"^\d{4}$")
    dob_ddmmyy: str | None = Field(default=None, pattern=r"^\d{6}$")
    card_last4: str | None = Field(default=None, pattern=r"^\d{4}$")
    card_last6: str | None = Field(default=None, pattern=r"^\d{6}$")
    crn: str | None = Field(default=None, max_length=40)


class ScanResult(BaseModel):
    """Outcome of a mailbox scan."""

    scanned: int
    statements_ingested: int
    dry_run: bool
