"""User request and response schemas (DTOs). These never expose the ORM entity directly."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Input for creating a user."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=200)


class UserRead(BaseModel):
    """Public user representation returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: str | None
    status: str
    created_at: datetime


class UserUpdate(BaseModel):
    """Mutable user profile fields."""

    full_name: str | None = Field(default=None, max_length=200)
