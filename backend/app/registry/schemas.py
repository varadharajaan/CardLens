"""Card registry request/response schemas (DTOs)."""

from __future__ import annotations

from datetime import date
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RegistryEntryUpsert(BaseModel):
    """Input to create or update a registry entry. Mirrors the versioned JSON schema."""

    schema_version: str = "1"
    key: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    bank: str
    card_name: str
    network: str
    version: int = Field(default=1, ge=1)
    source_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    last_verified_at: date | None = None
    features: dict[str, Any] = Field(default_factory=dict)
    official_links: list[str] = Field(default_factory=list)
    community_links: list[str] = Field(default_factory=list)


class RegistryEntryRead(BaseModel):
    """Registry entry as returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    key: str
    bank: str
    card_name: str
    network: str
    schema_version: str
    version: int
    source_confidence: float
    last_verified_at: date | None
    features: dict[str, Any]
    official_links: list[str]
    community_links: list[str]


class CardMatchQuery(BaseModel):
    """Query to match a detected card against the registry."""

    bank: str | None = None
    card_name: str | None = None
    last4: str | None = Field(default=None, max_length=4)


class RegistryMatchResult(BaseModel):
    """Outcome of a registry match attempt."""

    matched: bool
    key: str | None = None
    confidence: float = 0.0
    entry: RegistryEntryRead | None = None
