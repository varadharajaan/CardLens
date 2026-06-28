"""Bank account and debit card request/response schemas (DTOs)."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BankAccountCreate(BaseModel):
    """Input to create a bank (deposit) account that groups debit-card variants."""

    bank: str = Field(min_length=2, max_length=40)
    account_type: str = Field(default="SAVINGS", max_length=20)
    display_name: str = Field(min_length=1, max_length=200)
    last4: str | None = Field(default=None, min_length=4, max_length=4, pattern=r"^[0-9]{4}$")
    ifsc: str | None = Field(default=None, max_length=11)
    balance: float | None = Field(default=None)


class DebitCardCreate(BaseModel):
    """Input to add a debit card (network variant) to a bank account."""

    bank_account_id: UUID
    card_name: str = Field(min_length=1, max_length=200)
    last4: str = Field(min_length=4, max_length=4, pattern=r"^[0-9]{4}$")
    network: str | None = Field(default=None, max_length=20)
    reward_format: str | None = Field(default=None, max_length=40)
    is_primary: bool = False


class BankAccountRead(BaseModel):
    """A bank (deposit) account as returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    bank: str
    account_type: str
    display_name: str
    last4: str | None
    ifsc: str | None
    balance: float | None
    status: str


class DebitCardRead(BaseModel):
    """A debit card (network variant) as returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    bank_account_id: UUID
    card_name: str
    last4: str
    network: str | None
    reward_format: str | None
    is_primary: bool
    status: str


class BankAccountDetail(BaseModel):
    """A bank account together with its debit-card variants."""

    account: BankAccountRead
    debit_cards: list[DebitCardRead]
