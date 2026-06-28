"""Statement request/response schemas (DTOs)."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StatementCreate(BaseModel):
    """Input to record a parsed statement (used by seeding and the ingestion pipeline)."""

    card_id: UUID | None = None
    account_id: UUID | None = None
    bank: str = Field(min_length=2, max_length=40)
    card_name: str = Field(min_length=1, max_length=200)
    last4: str = Field(min_length=4, max_length=4, pattern=r"^[0-9]{4}$")
    statement_date: date | None = None
    period_start: date | None = None
    period_end: date | None = None
    bill_date: date | None = None
    due_date: date | None = None
    total_due: float | None = Field(default=None, ge=0)
    minimum_due: float | None = Field(default=None, ge=0)
    reward_points_credited: int | None = None
    reward_points_redeemed: int | None = None
    reward_points_expired: int | None = None
    reward_points_closing: int | None = None
    cashback_earned: float | None = Field(default=None, ge=0)
    reward_type: str | None = Field(default=None, max_length=40)
    reward_parse_status: str = "NOT_FOUND"
    reward_confidence: float = Field(default=0.0, ge=0, le=1)
    reward_parse_reason: str | None = Field(default=None, max_length=200)
    manual_review_flag: bool = False
    parse_confidence: float = Field(default=0.0, ge=0, le=1)
    evidence_snippet: str | None = None


class StatementRead(BaseModel):
    """A statement as returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    card_id: UUID | None
    account_id: UUID | None
    bank: str
    card_name: str
    last4: str
    statement_date: date | None
    period_start: date | None
    period_end: date | None
    bill_date: date | None
    due_date: date | None
    total_due: float | None
    minimum_due: float | None
    reward_points_credited: int | None
    reward_points_redeemed: int | None
    reward_points_expired: int | None
    reward_points_closing: int | None
    cashback_earned: float | None
    reward_type: str | None
    reward_parse_status: str
    reward_confidence: float
    reward_parse_reason: str | None
    manual_review_flag: bool
    parse_confidence: float
    evidence_snippet: str | None
