"""Card portfolio request/response schemas (DTOs)."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CardCreate(BaseModel):
    """Input to add a card (network variant) to the portfolio."""

    bank: str = Field(min_length=2, max_length=40)
    card_name: str = Field(min_length=1, max_length=200)
    last4: str = Field(min_length=4, max_length=4, pattern=r"^[0-9]{4}$")
    network: str | None = Field(default=None, max_length=20)
    registry_key: str | None = Field(default=None, max_length=120)
    account_id: UUID | None = None
    reward_format: str | None = Field(default=None, max_length=40)
    is_primary: bool = False


class CardAccountCreate(BaseModel):
    """Input to create a card billing account that groups companion variants."""

    bank: str = Field(min_length=2, max_length=40)
    display_name: str = Field(min_length=1, max_length=200)
    last4_primary: str | None = Field(default=None, min_length=4, max_length=4, pattern=r"^[0-9]{4}$")
    credit_limit: float | None = Field(default=None, ge=0)
    statement_day: int | None = Field(default=None, ge=1, le=31)


class CardRead(BaseModel):
    """A card (network variant) as returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    account_id: UUID | None
    bank: str
    card_name: str
    last4: str
    network: str | None
    registry_key: str | None
    reward_format: str | None
    is_primary: bool
    status: str


class CardAccountRead(BaseModel):
    """A card billing account that groups companion network variants (one statement, one due)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    bank: str
    display_name: str
    last4_primary: str | None
    credit_limit: float | None
    statement_day: int | None
    status: str


class CardAccountDetail(BaseModel):
    """A billing account together with its companion card variants."""

    account: CardAccountRead
    variants: list[CardRead]


class CardSummary(BaseModel):
    """A card plus derived portfolio metrics computed from its latest statement."""

    model_config = ConfigDict(from_attributes=True)

    card: CardRead
    statement_count: int
    latest_due_date: date | None
    latest_total_due: float | None
    reward_points_closing: int | None
